from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .brief import SUPPORTED_DELIVERABLES
from .providers import ProviderAdapter, build_provider_request_plan


def _strict_non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a non-negative integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = int(value.strip())
        except ValueError as exc:
            raise ValueError(f"{field} must be a non-negative integer") from exc
    else:
        raise ValueError(f"{field} must be a non-negative integer")
    if parsed < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return parsed


@dataclass(frozen=True)
class RoutingPolicy:
    policy_id: str
    version: str
    max_requests_per_run: int
    max_total_cost_units: int
    cost_units_by_deliverable: dict[str, int]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "RoutingPolicy":
        allowed = {
            "policy_id",
            "version",
            "max_requests_per_run",
            "max_total_cost_units",
            "cost_units_by_deliverable",
        }
        unknown = sorted(set(value) - allowed)
        missing = sorted(allowed - set(value))
        if unknown:
            raise ValueError(f"Unknown routing policy fields: {', '.join(unknown)}")
        if missing:
            raise ValueError(f"Missing routing policy fields: {', '.join(missing)}")
        policy_id = str(value["policy_id"]).strip()
        version = str(value["version"]).strip()
        if not policy_id or not version:
            raise ValueError("policy_id and version must not be blank")
        max_requests = _strict_non_negative_int(value["max_requests_per_run"], "max_requests_per_run")
        max_cost = _strict_non_negative_int(value["max_total_cost_units"], "max_total_cost_units")
        raw_costs = value["cost_units_by_deliverable"]
        if not isinstance(raw_costs, dict) or set(raw_costs) != SUPPORTED_DELIVERABLES:
            raise ValueError("cost_units_by_deliverable must define exactly cover_image, short_video and voiceover")
        costs = {
            name: _strict_non_negative_int(raw, f"cost_units_by_deliverable.{name}")
            for name, raw in raw_costs.items()
        }
        if any(cost < 1 for cost in costs.values()):
            raise ValueError("Each deliverable cost must be at least one abstract cost unit")
        return cls(policy_id, version, max_requests, max_cost, costs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "max_requests_per_run": self.max_requests_per_run,
            "max_total_cost_units": self.max_total_cost_units,
            "cost_units_by_deliverable": dict(self.cost_units_by_deliverable),
        }


def load_routing_policy(path: Path) -> RoutingPolicy:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid routing policy JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Routing policy must contain a JSON object")
    return RoutingPolicy.from_mapping(payload)


def build_guarded_request_plan(
    package: dict[str, Any], adapter: ProviderAdapter, policy: RoutingPolicy
) -> dict[str, Any]:
    deliverables = package.get("deliverables")
    if not isinstance(deliverables, list) or not deliverables:
        raise ValueError("Production package deliverables must be a non-empty list")
    types = [str(item.get("type", "")) for item in deliverables if isinstance(item, dict)]
    if len(types) != len(deliverables) or any(item not in policy.cost_units_by_deliverable for item in types):
        raise ValueError("Every deliverable must have a supported type and abstract cost unit")
    estimated_cost = sum(policy.cost_units_by_deliverable[item] for item in types)
    reasons: list[str] = []
    if len(deliverables) > policy.max_requests_per_run:
        reasons.append(
            f"request count {len(deliverables)} exceeds policy limit {policy.max_requests_per_run}"
        )
    if estimated_cost > policy.max_total_cost_units:
        reasons.append(
            f"estimated abstract cost {estimated_cost} exceeds policy limit {policy.max_total_cost_units}"
        )
    common = {
        "campaign_id": package.get("campaign_id"),
        "provider_id": adapter.provider_id,
        "routing_policy": policy.to_dict(),
        "request_count": len(deliverables),
        "estimated_cost_units": estimated_cost,
        "cost_unit_boundary": "Abstract planning units only; not currency, tokens, provider price or a quote.",
        "external_calls_executed": 0,
        "human_approval_required": True,
    }
    if reasons:
        return {
            **common,
            "routing_status": "blocked",
            "reasons": reasons,
            "requests": [],
            "approval_gate": "Revise the package or reviewed routing policy before preparing any provider envelope.",
        }
    prepared = build_provider_request_plan(package, adapter)
    return {
        **common,
        "routing_status": "eligible_for_human_review",
        "reasons": [],
        "requests": prepared["requests"],
        "approval_gate": prepared["approval_gate"],
    }
