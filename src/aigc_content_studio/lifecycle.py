from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ALLOWED_TRANSITIONS = {
    "planned": {"generated_candidate"},
    "generated_candidate": {"in_review"},
    "in_review": {"approved_final", "changes_requested"},
    "changes_requested": {"generated_candidate"},
    "approved_final": {"archived"},
    "archived": set(),
}


class AssetLedger:
    """A local append-only record of explicit asset status changes."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = deepcopy(payload)
        self._validate()

    @classmethod
    def from_manifest(cls, campaign_id: str, manifest: list[dict[str, Any]]) -> "AssetLedger":
        if not manifest:
            raise ValueError("Asset manifest must not be empty")
        assets: dict[str, dict[str, Any]] = {}
        events: list[dict[str, Any]] = []
        for item in manifest:
            asset_id = str(item.get("asset_id", "")).strip()
            if not asset_id or asset_id in assets:
                raise ValueError("Asset IDs must be present and unique")
            status = str(item.get("status", "planned"))
            if status != "planned":
                raise ValueError("New ledgers must initialize assets in planned status")
            event = {
                "event_id": f"EVT-{len(events) + 1:04d}",
                "asset_id": asset_id,
                "version": 1,
                "from_status": None,
                "to_status": "planned",
                "actor": "workflow",
                "note": "Asset registered from the production package manifest.",
            }
            events.append(event)
            assets[asset_id] = {"current_status": "planned", "version": 1}
        return cls({"ledger_version": "1.0", "campaign_id": campaign_id, "assets": assets, "events": events})

    @classmethod
    def load(cls, path: Path) -> "AssetLedger":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid asset ledger JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError("Asset ledger must be a JSON object")
        return cls(payload)

    def transition(self, asset_id: str, to_status: str, actor: str, note: str) -> dict[str, Any]:
        if asset_id not in self._payload["assets"]:
            raise ValueError(f"Unknown asset ID: {asset_id}")
        if not actor.strip() or not note.strip():
            raise ValueError("actor and note must not be blank")
        asset = self._payload["assets"][asset_id]
        from_status = asset["current_status"]
        allowed = ALLOWED_TRANSITIONS[from_status]
        if to_status not in allowed:
            choices = ", ".join(sorted(allowed)) or "none"
            raise ValueError(f"Invalid transition {from_status} -> {to_status}; allowed: {choices}")
        version = asset["version"] + 1
        event = {
            "event_id": f"EVT-{len(self._payload['events']) + 1:04d}",
            "asset_id": asset_id,
            "version": version,
            "from_status": from_status,
            "to_status": to_status,
            "actor": actor.strip(),
            "note": note.strip(),
        }
        self._payload["events"].append(event)
        asset.update({"current_status": to_status, "version": version})
        return deepcopy(event)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(self._payload)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _validate(self) -> None:
        required = {"ledger_version", "campaign_id", "assets", "events"}
        if not required.issubset(self._payload):
            raise ValueError("Asset ledger is missing required fields")
        if not isinstance(self._payload["assets"], dict) or not isinstance(self._payload["events"], list):
            raise ValueError("Asset ledger assets and events have invalid shapes")
        for asset_id, asset in self._payload["assets"].items():
            if asset.get("current_status") not in ALLOWED_TRANSITIONS:
                raise ValueError(f"Unknown current status for {asset_id}")
            if not isinstance(asset.get("version"), int) or asset["version"] < 1:
                raise ValueError(f"Invalid version for {asset_id}")


def ledger_from_package(package_path: Path) -> AssetLedger:
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid production package JSON: {exc.msg}") from exc
    if not isinstance(package, dict):
        raise ValueError("Production package must be a JSON object")
    return AssetLedger.from_manifest(str(package.get("campaign_id", "")), package.get("asset_manifest", []))
