from __future__ import annotations

from typing import Any


REVIEW_HISTORY_VERSION = "0.9"


def validate_review_history(history: list[dict[str, Any]], current_export: dict[str, Any]) -> dict[str, Any]:
    """Validate an append-only synthetic review log without applying decisions."""
    if not isinstance(history, list) or not history:
        raise ValueError("review history must be a non-empty list")
    export_ids = {str(item.get("decision_id")) for item in current_export.get("decisions", [])}
    seen_revisions: set[int] = set()
    seen_decisions: set[str] = set()
    checked: list[dict[str, Any]] = []
    for record in history:
        if not isinstance(record, dict):
            raise ValueError("each review history record must be an object")
        revision = record.get("revision")
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise ValueError("review history revision must be a positive integer")
        if revision in seen_revisions:
            raise ValueError("review history revisions must be unique")
        decision_id = record.get("decision_id")
        if not isinstance(decision_id, str) or decision_id not in export_ids:
            raise ValueError("review history decision_id must reference the current export")
        if decision_id in seen_decisions:
            raise ValueError("review history cannot duplicate a decision")
        if record.get("status") not in {"pending", "accepted", "rejected"}:
            raise ValueError("review history status is unsupported")
        if not isinstance(record.get("applied"), bool) or record["applied"]:
            raise ValueError("review history applied must remain false")
        if not isinstance(record.get("reviewer"), str) or not record["reviewer"].strip():
            raise ValueError("review history reviewer must be non-empty")
        seen_revisions.add(revision)
        seen_decisions.add(decision_id)
        checked.append({"revision": revision, "decision_id": decision_id, "passed": True})
    ordered = [item["revision"] for item in checked]
    return {
        "history_version": REVIEW_HISTORY_VERSION,
        "record_count": len(checked),
        "revisions": ordered,
        "append_only": ordered == sorted(ordered),
        "decision_execution_executed": False,
        "platform_writes_executed": 0,
        "records": checked,
        "boundary": "Synthetic review history records accountability only; it does not apply decisions or publish assets.",
    }


__all__ = ["REVIEW_HISTORY_VERSION", "validate_review_history"]
