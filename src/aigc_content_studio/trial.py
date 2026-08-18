from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import date
from pathlib import Path
from typing import Any

from .brief import load_brief
from .providers import OfflineProviderAdapter, load_provider_profile
from .quality import evaluate_quality_files
from .routing import build_guarded_request_plan, load_routing_policy
from .templates import load_template_set
from .workflow import ContentProductionWorkflow


COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
SOURCE_TYPES = {"real", "synthetic"}
FEEDBACK_CLASSES = {"defect", "requirement", "usability", "performance", "safety", "documentation"}


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def validate_evidence_index(root: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    claims = payload.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("Evidence index must contain claims")
    root = root.resolve()
    seen: set[str] = set()
    checked = []
    for claim in claims:
        if not isinstance(claim, dict) or not str(claim.get("claim_id", "")).strip() or not str(claim.get("statement", "")).strip():
            raise ValueError("Every evidence claim needs claim_id and statement")
        if claim["claim_id"] in seen:
            raise ValueError(f"Duplicate evidence claim_id: {claim['claim_id']}")
        seen.add(claim["claim_id"])
        artifacts = claim.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError(f"{claim['claim_id']} must link at least one artifact")
        paths = []
        for artifact in artifacts:
            relative = str(artifact.get("path", "")) if isinstance(artifact, dict) else ""
            target = (root / relative).resolve()
            if not isinstance(artifact, dict) or not str(artifact.get("kind", "")).strip():
                raise ValueError(f"{claim['claim_id']} has an untyped artifact")
            if not relative or not target.is_relative_to(root) or not target.is_file():
                raise ValueError(f"Missing or unsafe evidence path: {relative}")
            paths.append(relative)
        checked.append({"claim_id": claim["claim_id"], "artifact_paths": paths, "passed": True})
    return checked


def validate_external_intake(payload: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        date.fromisoformat(str(payload["reviewed_on"]))
    except (KeyError, ValueError) as exc:
        raise ValueError("External intake reviewed_on must be an ISO-8601 date") from exc
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("External intake must contain screened candidates")
    checked = []
    for item in candidates:
        required = {"repository", "version", "commit", "license", "decision", "reason", "code_adopted"}
        if not isinstance(item, dict) or required.difference(item):
            raise ValueError("External candidate metadata is incomplete")
        if any(key != "code_adopted" and not str(item[key]).strip() for key in required):
            raise ValueError("External candidate metadata must not be blank")
        if not str(item["repository"]).startswith("https://github.com/"):
            raise ValueError("External repository must use a GitHub HTTPS URL")
        if not COMMIT_PATTERN.fullmatch(str(item["commit"])):
            raise ValueError("External candidate commit must be a full SHA")
        if item["decision"] not in {"adopted", "rejected"} or not isinstance(item["code_adopted"], bool):
            raise ValueError("External candidate decision is invalid")
        if (item["decision"] == "adopted") != item["code_adopted"]:
            raise ValueError("External decision and code_adopted must agree")
        checked.append({"repository": item["repository"], "decision": item["decision"], "passed": True})
    return checked


def validate_feedback(root: Path, payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "feedback_id", "source_type", "recorded_on", "classification", "summary", "reproduction",
        "decision", "acceptance_test", "implementation", "release_result",
    }
    if required.difference(payload) or any(not str(payload[key]).strip() for key in required):
        raise ValueError("Feedback record is incomplete")
    date.fromisoformat(str(payload["recorded_on"]))
    if payload["source_type"] not in SOURCE_TYPES or payload["classification"] not in FEEDBACK_CLASSES:
        raise ValueError("Feedback source_type or classification is unsupported")
    if payload["decision"] != "accepted":
        raise ValueError("Trial feedback case must record an accepted decision")
    for key in ("acceptance_test", "implementation"):
        target = (root.resolve() / str(payload[key])).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            raise ValueError(f"Feedback {key} path is missing or unsafe")
    return {"feedback_id": payload["feedback_id"], "source_type": payload["source_type"], "passed": True}


def run_trial(root: Path) -> dict[str, Any]:
    root = root.resolve()
    manifest = load_json_object(root / "evidence" / "evidence_index.json")
    external_checks = validate_external_intake(load_json_object(root / "evidence" / "external_intake.json"))
    feedback_check = validate_feedback(root, load_json_object(root / "evidence" / "feedback_case.json"))
    evidence_checks = validate_evidence_index(root, manifest)

    package = ContentProductionWorkflow(load_template_set(root / "data" / "prompt_templates.json")).run(
        load_brief(root / "data" / "sample_brief.json")
    )
    adapter = OfflineProviderAdapter(load_provider_profile(root / "data" / "offline_provider_profile.json"))
    policy = load_routing_policy(root / "data" / "routing_policy.json")
    routing = build_guarded_request_plan(package, adapter, policy)
    quality = evaluate_quality_files(
        root / "examples" / "sample_production_package.json",
        root / "data" / "failure_taxonomy.json",
        root / "data" / "quality_fixture.json",
    )
    core_passed = (
        routing["routing_status"] == "eligible_for_human_review"
        and routing["request_count"] == 3
        and routing["estimated_cost_units"] == 8
        and routing["external_calls_executed"] == 0
        and quality["summary"]["blocked_cases"] == 6
        and quality["summary"]["taxonomy_coverage"] == 1.0
    )
    blocked = build_guarded_request_plan(package, adapter, replace(policy, max_requests_per_run=2))
    feedback_regression = {
        **feedback_check,
        "passed": blocked["routing_status"] == "blocked" and blocked["requests"] == [] and blocked["external_calls_executed"] == 0,
        "routing_status": blocked["routing_status"],
        "prepared_requests": len(blocked["requests"]),
        "reasons": blocked["reasons"],
    }
    all_checks = [
        core_passed,
        feedback_regression["passed"],
        all(item["passed"] for item in external_checks),
        all(item["passed"] for item in evidence_checks),
    ]
    return {
        "schema_version": "1.0",
        "trial_id": manifest["trial"]["trial_id"],
        "source_data": "synthetic",
        "overall_passed": all(all_checks),
        "core_flow": {
            "passed": core_passed,
            "routing_status": routing["routing_status"],
            "request_count": routing["request_count"],
            "estimated_cost_units": routing["estimated_cost_units"],
            "quality_blocked_cases": quality["summary"]["blocked_cases"],
            "external_calls_executed": 0,
        },
        "feedback_regression": feedback_regression,
        "external_intake": external_checks,
        "evidence_index": evidence_checks,
        "boundaries": manifest["boundaries"],
    }


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join([
        "# AIGC Studio Trial Readiness Report",
        "",
        "> Synthetic, offline verification. No model, media, provider call or price quote is involved.",
        "",
        f"- Overall: **{'PASS' if report['overall_passed'] else 'FAIL'}**",
        f"- End-to-end planning and routing: {'PASS' if report['core_flow']['passed'] else 'FAIL'}",
        f"- Atomic quota-block regression: {'PASS' if report['feedback_regression']['passed'] else 'FAIL'}",
        f"- Evidence claims checked: {len(report['evidence_index'])}",
        f"- External candidates screened: {len(report['external_intake'])}",
        "",
        "## Pilot boundary",
        "",
        *[f"- {item}" for item in report["boundaries"]],
        "",
    ])


def write_trial_report(root: Path, json_output: Path, markdown_output: Path) -> dict[str, Any]:
    report = run_trial(root)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")
    return report
