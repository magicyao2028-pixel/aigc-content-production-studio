from __future__ import annotations

from datetime import date, timedelta
from typing import Any


_STATUSES = {"accepted", "pending", "rejected"}


def summarize_stale_feedback(
    review_export: dict[str, Any], feedback_batch: list[dict[str, Any]], *, as_of_date: str, stale_after_days: int = 7
) -> dict[str, Any]:
    """Expose old accepted feedback still attached to unresolved review decisions."""
    if stale_after_days < 1:
        raise ValueError("stale_after_days must be at least 1")
    try:
        as_of = date.fromisoformat(as_of_date)
    except ValueError as exc:
        raise ValueError("as_of_date must be ISO format") from exc
    decisions = {str(item.get("decision_id")): item for item in review_export.get("decisions", []) if isinstance(item, dict)}
    if not decisions:
        raise ValueError("review export must contain decisions")
    if not isinstance(feedback_batch, list) or not feedback_batch:
        raise ValueError("feedback batch must be a non-empty list")
    cutoff = as_of - timedelta(days=stale_after_days)
    seen: set[str] = set()
    accepted: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    for record in feedback_batch:
        if not isinstance(record, dict):
            raise ValueError("each feedback record must be an object")
        required = {"feedback_id", "decision_id", "recorded_on", "status", "summary", "applied"}
        if required.difference(record):
            raise ValueError("feedback record is incomplete")
        feedback_id = str(record["feedback_id"]).strip()
        if not feedback_id or feedback_id in seen:
            raise ValueError("feedback IDs must be unique")
        seen.add(feedback_id)
        decision_id = str(record["decision_id"]).strip()
        if decision_id not in decisions:
            raise ValueError("feedback decision_id must reference the current export")
        try:
            recorded_on = date.fromisoformat(str(record["recorded_on"]))
        except ValueError as exc:
            raise ValueError("feedback recorded_on must be ISO format") from exc
        status = str(record["status"]).strip()
        if status not in _STATUSES or not str(record["summary"]).strip():
            raise ValueError("feedback status or summary is invalid")
        if record["applied"] is not False:
            raise ValueError("feedback visibility cannot apply decisions")
        item = {"feedback_id": feedback_id, "decision_id": decision_id, "recorded_on": recorded_on.isoformat(), "status": status}
        if status != "accepted":
            excluded.append(item)
            continue
        accepted.append(item)
        decision_status = str(decisions[decision_id].get("status", ""))
        if recorded_on <= cutoff and decision_status.startswith("blocked"):
            stale.append({**item, "reason": "accepted_feedback_older_than_cutoff_on_unresolved_decision"})
    return {
        "schema_version": "1.0",
        "as_of_date": as_of.isoformat(),
        "cutoff_date": cutoff.isoformat(),
        "stale_after_days": stale_after_days,
        "accepted_count": len(accepted),
        "excluded_count": len(excluded),
        "stale_count": len(stale),
        "stale": stale,
        "excluded": excluded,
        "decision_execution_executed": False,
        "asset_publication_executed": False,
        "boundary": "Visibility is a review aid only; it does not reclassify decisions, publish assets or send reminders.",
    }


__all__ = ["summarize_stale_feedback"]
