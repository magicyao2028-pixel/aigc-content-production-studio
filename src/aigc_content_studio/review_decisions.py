from __future__ import annotations

from typing import Any


def build_human_review_export(
    quality_report: dict[str, Any],
    capability_diff: dict[str, Any],
    routing_plan: dict[str, Any],
) -> dict[str, Any]:
    """Compile deterministic, non-executing decisions for a human review queue."""
    decisions: list[dict[str, Any]] = []
    for case in quality_report.get("cases", []):
        if case.get("release_decision") == "blocked":
            decisions.append({
                "decision_id": f"QUALITY-{case['case_id']}",
                "subject_id": case["asset_id"],
                "source": "quality_fixture",
                "status": "blocked_pending_human_review",
                "owner": sorted({item["owner"] for item in case["failures"]})[0],
                "blockers": [item["category"] for item in case["failures"]],
                "next_action": "review_failure_evidence_and_request_revision",
                "approved": False,
            })
    if capability_diff.get("status") == "breaking":
        decisions.append({
            "decision_id": "PROVIDER-CAPABILITY-001",
            "subject_id": capability_diff.get("candidate_provider_id", "candidate-profile"),
            "source": "provider_capability_diff",
            "status": "blocked_pending_human_review",
            "owner": "AI Application Operator",
            "blockers": ["breaking_provider_capability_change"],
            "next_action": "confirm_provider_profile_or_replan_request",
            "approved": False,
        })
    decisions.sort(key=lambda item: item["decision_id"])
    return {
        "export_version": "1.0",
        "decision_count": len(decisions),
        "decisions": decisions,
        "governance": {
            "human_approval_required": True,
            "external_calls_executed": int(routing_plan.get("external_calls_executed", 0)),
            "platform_writes_executed": 0,
            "decision_execution_executed": False,
        },
    }
