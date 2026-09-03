from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any


_STATUSES = {"accepted", "pending", "rejected"}


def replay_reviewer_feedback(feedback_batch: list[dict[str, Any]], current_export: dict[str, Any]) -> dict[str, Any]:
    """Replay accepted synthetic feedback as regression metadata without applying decisions."""
    if not isinstance(feedback_batch, list) or not feedback_batch:
        raise ValueError("feedback batch must be a non-empty list")
    decision_ids = {str(item.get("decision_id")) for item in current_export.get("decisions", [])}
    if not decision_ids:
        raise ValueError("current review export must contain decisions")
    seen: set[str] = set()
    dates: list[date] = []
    statuses: Counter[str] = Counter()
    replayed: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for record in feedback_batch:
        if not isinstance(record, dict):
            raise ValueError("each feedback record must be an object")
        required = {"feedback_id", "decision_id", "recorded_on", "classification", "status", "summary", "applied"}
        if required.difference(record):
            raise ValueError("feedback record is incomplete")
        feedback_id = str(record["feedback_id"]).strip()
        if not feedback_id or feedback_id in seen:
            raise ValueError("feedback IDs must be unique")
        seen.add(feedback_id)
        if str(record["decision_id"]).strip() not in decision_ids:
            raise ValueError("feedback decision_id must reference the current export")
        try:
            recorded_on = date.fromisoformat(str(record["recorded_on"]))
        except ValueError as exc:
            raise ValueError("feedback recorded_on must be ISO format") from exc
        if dates and recorded_on < dates[-1]:
            raise ValueError("feedback dates must be chronological")
        dates.append(recorded_on)
        status = str(record["status"]).strip()
        if status not in _STATUSES or not str(record["classification"]).strip() or not str(record["summary"]).strip():
            raise ValueError("feedback status or summary is invalid")
        if record["applied"] is not False:
            raise ValueError("feedback replay cannot apply decisions")
        item = {"feedback_id": feedback_id, "decision_id": str(record["decision_id"]), "status": status, "passed": True}
        statuses[status] += 1
        (replayed if status == "accepted" else excluded).append(item)
    return {
        "schema_version": "1.0",
        "record_count": len(feedback_batch),
        "status_counts": dict(sorted(statuses.items())),
        "replayed_count": len(replayed),
        "excluded_count": len(excluded),
        "replayed": replayed,
        "excluded": excluded,
        "decision_execution_executed": False,
        "asset_publication_executed": False,
        "external_calls_executed": 0,
        "boundary": "Only accepted synthetic feedback is replayed as regression metadata; no decision is applied and no asset is published.",
    }
