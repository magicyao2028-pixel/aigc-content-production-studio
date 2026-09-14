from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXECUTION_POLICY_SCHEMA_VERSION = "1.0"
MAX_CONCURRENCY_LIMIT = 16
MAX_ATTEMPTS_LIMIT = 5
MAX_BACKOFF_SECONDS = 3_600

_POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "version",
    "max_concurrency",
    "max_attempts_per_job",
    "retry_backoff_seconds",
}
_ROUTING_PLAN_FIELDS = {
    "campaign_id",
    "provider_id",
    "routing_policy",
    "request_count",
    "estimated_cost_units",
    "cost_unit_boundary",
    "external_calls_executed",
    "human_approval_required",
    "routing_status",
    "reasons",
    "requests",
    "approval_gate",
}
_REQUEST_FIELDS = {
    "request_id",
    "provider_id",
    "asset_id",
    "deliverable_type",
    "payload",
    "execution_status",
    "external_call_executed",
    "human_approval_required",
}


@dataclass(frozen=True)
class ExecutionPolicy:
    policy_id: str
    version: str
    max_concurrency: int
    max_attempts_per_job: int
    retry_backoff_seconds: tuple[int, ...]

    @classmethod
    def from_mapping(cls, value: Any) -> "ExecutionPolicy":
        if not isinstance(value, dict):
            raise ValueError("Execution policy must be a JSON object")
        _require_exact_fields(value, _POLICY_FIELDS, "Execution policy")
        if value["schema_version"] != EXECUTION_POLICY_SCHEMA_VERSION:
            raise ValueError("Execution policy schema_version must be 1.0")
        policy_id = _strict_non_blank_string(value["policy_id"], "policy_id")
        version = _strict_non_blank_string(value["version"], "version")
        max_concurrency = _strict_int(
            value["max_concurrency"],
            "max_concurrency",
            minimum=1,
            maximum=MAX_CONCURRENCY_LIMIT,
        )
        max_attempts = _strict_int(
            value["max_attempts_per_job"],
            "max_attempts_per_job",
            minimum=1,
            maximum=MAX_ATTEMPTS_LIMIT,
        )
        raw_backoff = value["retry_backoff_seconds"]
        if not isinstance(raw_backoff, list):
            raise ValueError("retry_backoff_seconds must be a list")
        backoff = tuple(
            _strict_int(
                item,
                f"retry_backoff_seconds[{index}]",
                minimum=1,
                maximum=MAX_BACKOFF_SECONDS,
            )
            for index, item in enumerate(raw_backoff)
        )
        if len(backoff) != max_attempts - 1:
            raise ValueError(
                "retry_backoff_seconds must contain exactly max_attempts_per_job - 1 entries"
            )
        if any(current < previous for previous, current in zip(backoff, backoff[1:])):
            raise ValueError("retry_backoff_seconds must be non-decreasing")
        return cls(policy_id, version, max_concurrency, max_attempts, backoff)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": EXECUTION_POLICY_SCHEMA_VERSION,
            "policy_id": self.policy_id,
            "version": self.version,
            "max_concurrency": self.max_concurrency,
            "max_attempts_per_job": self.max_attempts_per_job,
            "retry_backoff_seconds": list(self.retry_backoff_seconds),
        }


def load_execution_policy(path: Path) -> ExecutionPolicy:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid execution policy JSON: {exc.msg}") from exc
    return ExecutionPolicy.from_mapping(payload)


def build_execution_preflight(
    routing_plan: dict[str, Any], policy: ExecutionPolicy
) -> dict[str, Any]:
    """Build a deterministic zero-send schedule or atomically block duplicates."""
    campaign_id, provider_id, requests = _validate_routing_plan(routing_plan)
    fingerprints = [
        _request_fingerprint(campaign_id, provider_id, request) for request in requests
    ]
    duplicate_fingerprints = sorted(
        fingerprint
        for fingerprint, count in Counter(fingerprints).items()
        if count > 1
    )
    duplicate_request_ids = sorted(
        request_id
        for request_id, count in Counter(
            request["request_id"] for request in requests
        ).items()
        if count > 1
    )
    common = {
        "schema_version": EXECUTION_POLICY_SCHEMA_VERSION,
        "preflight_type": "offline_zero_send_execution_schedule",
        "campaign_id": campaign_id,
        "provider_id": provider_id,
        "source_routing_status": routing_plan["routing_status"],
        "source_request_count": len(requests),
        "execution_policy": policy.to_dict(),
        "execution_authorized": False,
        "human_approval_required": True,
        "attempts_executed": 0,
        "external_requests_executed": 0,
        "provider_sends_executed": 0,
        "duplicate_fingerprints": duplicate_fingerprints,
        "duplicate_request_ids": duplicate_request_ids,
    }
    if duplicate_fingerprints or duplicate_request_ids:
        reasons = []
        if duplicate_fingerprints:
            reasons.append(
                "duplicate request fingerprints detected: "
                + ", ".join(duplicate_fingerprints)
            )
        if duplicate_request_ids:
            reasons.append(
                "duplicate request IDs detected: " + ", ".join(duplicate_request_ids)
            )
        return {
            **common,
            "preflight_status": "blocked",
            "execution_status": "blocked_not_prepared",
            "reasons": reasons,
            "job_count": 0,
            "wave_count": 0,
            "jobs": [],
            "waves": [],
            "approval_gate": (
                "Remove duplicate source requests and rerun the offline preflight; "
                "no job or provider send has been created."
            ),
        }

    jobs = [
        _build_job(request, fingerprint, index, policy)
        for index, (request, fingerprint) in enumerate(
            zip(requests, fingerprints), start=1
        )
    ]
    waves = []
    for offset in range(0, len(jobs), policy.max_concurrency):
        wave_jobs = jobs[offset : offset + policy.max_concurrency]
        waves.append(
            {
                "wave_number": len(waves) + 1,
                "job_count": len(wave_jobs),
                "job_ids": [job["job_id"] for job in wave_jobs],
                "execution_status": "prepared_not_sent",
                "attempts_executed": 0,
                "external_requests_executed": 0,
                "provider_sends_executed": 0,
            }
        )
    return {
        **common,
        "preflight_status": "prepared_for_human_review",
        "execution_status": "prepared_not_sent",
        "reasons": [],
        "job_count": len(jobs),
        "wave_count": len(waves),
        "jobs": jobs,
        "waves": waves,
        "approval_gate": (
            "This schedule is review-only. A separately authorized execution service "
            "must revalidate identity, budget, rights and provider state before any send."
        ),
    }


def _validate_routing_plan(
    routing_plan: Any,
) -> tuple[str, str, list[dict[str, Any]]]:
    if not isinstance(routing_plan, dict):
        raise ValueError("Routing plan must be a JSON object")
    _require_exact_fields(routing_plan, _ROUTING_PLAN_FIELDS, "Routing plan")
    if routing_plan["routing_status"] != "eligible_for_human_review":
        raise ValueError("Execution preflight requires an eligible routing plan")
    if routing_plan["reasons"] != []:
        raise ValueError("Eligible routing plan reasons must be empty")
    if routing_plan["human_approval_required"] is not True:
        raise ValueError("Routing plan must require human approval")
    if not _is_zero_int(routing_plan["external_calls_executed"]):
        raise ValueError("Routing plan must have zero external calls")
    campaign_id = _strict_non_blank_string(routing_plan["campaign_id"], "campaign_id")
    provider_id = _strict_non_blank_string(routing_plan["provider_id"], "provider_id")
    requests = routing_plan["requests"]
    if not isinstance(requests, list) or not requests:
        raise ValueError("Eligible routing plan requests must be a non-empty list")
    request_count = routing_plan["request_count"]
    if (
        isinstance(request_count, bool)
        or not isinstance(request_count, int)
        or request_count != len(requests)
    ):
        raise ValueError("Routing plan request_count must match requests")
    for index, request in enumerate(requests):
        if not isinstance(request, dict):
            raise ValueError(f"requests[{index}] must be a JSON object")
        _require_exact_fields(request, _REQUEST_FIELDS, f"requests[{index}]")
        for field in ("request_id", "provider_id", "asset_id", "deliverable_type"):
            _strict_non_blank_string(request[field], f"requests[{index}].{field}")
        if request["provider_id"] != provider_id:
            raise ValueError(f"requests[{index}].provider_id must match the routing plan")
        if not isinstance(request["payload"], dict):
            raise ValueError(f"requests[{index}].payload must be a JSON object")
        _canonical_json(request["payload"], f"requests[{index}].payload")
        if request["execution_status"] != "prepared_not_sent":
            raise ValueError(
                f"requests[{index}].execution_status must be prepared_not_sent"
            )
        if request["external_call_executed"] is not False:
            raise ValueError(f"requests[{index}] must have zero external calls")
        if request["human_approval_required"] is not True:
            raise ValueError(f"requests[{index}] must require human approval")
    return campaign_id, provider_id, requests


def _request_fingerprint(
    campaign_id: str, provider_id: str, request: dict[str, Any]
) -> str:
    canonical = _canonical_json(
        {
            "campaign_id": campaign_id,
            "provider_id": provider_id,
            "asset_id": request["asset_id"],
            "deliverable_type": request["deliverable_type"],
            "payload": request["payload"],
        },
        "request fingerprint",
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _build_job(
    request: dict[str, Any],
    fingerprint: str,
    index: int,
    policy: ExecutionPolicy,
) -> dict[str, Any]:
    return {
        "job_id": f"job-sha256-{fingerprint}",
        "idempotency_key": f"idem-sha256-{fingerprint}",
        "request_fingerprint": fingerprint,
        "source_request_id": request["request_id"],
        "asset_id": request["asset_id"],
        "deliverable_type": request["deliverable_type"],
        "wave_number": ((index - 1) // policy.max_concurrency) + 1,
        "execution_status": "prepared_not_sent",
        "max_attempts_per_job": policy.max_attempts_per_job,
        "retry_backoff_seconds": list(policy.retry_backoff_seconds),
        "attempts_executed": 0,
        "external_requests_executed": 0,
        "provider_sends_executed": 0,
    }


def _canonical_json(value: Any, field: str) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be canonical JSON data") from exc


def _require_exact_fields(
    value: dict[Any, Any], allowed: set[str], label: str
) -> None:
    if any(not isinstance(key, str) for key in value):
        raise ValueError(f"{label} keys must be strings")
    missing = sorted(allowed.difference(value))
    unknown = sorted(set(value).difference(allowed))
    if missing or unknown:
        raise ValueError(
            f"{label} fields are invalid: missing={missing or []}, unknown={unknown or []}"
        )


def _strict_non_blank_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{field} must be a non-blank string")
    return value


def _strict_int(value: Any, field: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{field} must be between {minimum} and {maximum}")
    return value


def _is_zero_int(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, int) and value == 0


__all__ = [
    "EXECUTION_POLICY_SCHEMA_VERSION",
    "ExecutionPolicy",
    "build_execution_preflight",
    "load_execution_policy",
]
