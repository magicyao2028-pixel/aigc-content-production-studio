from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from .brief import SUPPORTED_DELIVERABLES


@dataclass(frozen=True)
class ProviderProfile:
    provider_id: str
    display_name: str
    supported_deliverables: tuple[str, ...]
    allowed_aspect_ratios: tuple[str, ...]
    max_duration_seconds: int
    external_execution_enabled: bool

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "ProviderProfile":
        allowed_keys = {
            "provider_id",
            "display_name",
            "supported_deliverables",
            "allowed_aspect_ratios",
            "max_duration_seconds",
            "external_execution_enabled",
        }
        unknown = sorted(set(value) - allowed_keys)
        if unknown:
            raise ValueError(f"Unknown provider profile fields: {', '.join(unknown)}")
        provider_id = str(value.get("provider_id", "")).strip()
        display_name = str(value.get("display_name", "")).strip()
        deliverables = _string_tuple(value.get("supported_deliverables"), "supported_deliverables")
        ratios = _string_tuple(value.get("allowed_aspect_ratios"), "allowed_aspect_ratios")
        try:
            max_duration = int(value.get("max_duration_seconds", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("max_duration_seconds must be an integer") from exc
        if not provider_id or not display_name:
            raise ValueError("provider_id and display_name must not be blank")
        unsupported = sorted(set(deliverables) - SUPPORTED_DELIVERABLES)
        if unsupported:
            raise ValueError(f"Unsupported provider deliverables: {', '.join(unsupported)}")
        if any(item not in {"9:16", "16:9", "1:1"} for item in ratios):
            raise ValueError("allowed_aspect_ratios contains an unsupported ratio")
        if max_duration < 1 or max_duration > 180:
            raise ValueError("max_duration_seconds must be between 1 and 180")
        execution_enabled = value.get("external_execution_enabled") is True
        if execution_enabled:
            raise ValueError("public provider profiles cannot enable external execution")
        return cls(provider_id, display_name, deliverables, ratios, max_duration, execution_enabled)


class ProviderAdapter(Protocol):
    @property
    def provider_id(self) -> str: ...

    def build_request(self, deliverable: dict[str, Any]) -> dict[str, Any]: ...


class OfflineProviderAdapter:
    """Builds reviewable request envelopes and never performs a network call."""

    def __init__(self, profile: ProviderProfile):
        self.profile = profile

    @property
    def provider_id(self) -> str:
        return self.profile.provider_id

    def build_request(self, deliverable: dict[str, Any]) -> dict[str, Any]:
        deliverable_type = str(deliverable.get("type", ""))
        if deliverable_type not in self.profile.supported_deliverables:
            raise ValueError(f"Provider does not support deliverable type: {deliverable_type}")
        aspect_ratio = str(deliverable.get("aspect_ratio", ""))
        if aspect_ratio not in self.profile.allowed_aspect_ratios:
            raise ValueError(f"Provider does not support aspect ratio: {aspect_ratio}")
        duration = deliverable.get("duration_seconds")
        if duration is not None and int(duration) > self.profile.max_duration_seconds:
            raise ValueError(
                f"Provider duration limit exceeded: {duration} > {self.profile.max_duration_seconds}"
            )
        prompt = str(deliverable.get("generation_prompt", "")).strip()
        if not prompt:
            raise ValueError(f"Deliverable has no generation_prompt: {deliverable.get('asset_id', 'unknown')}")
        return {
            "request_id": f"REQ-{deliverable['asset_id']}-{self.provider_id}",
            "provider_id": self.provider_id,
            "asset_id": deliverable["asset_id"],
            "deliverable_type": deliverable_type,
            "payload": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "duration_seconds": duration,
                "negative_constraints": list(deliverable.get("negative_constraints", [])),
            },
            "execution_status": "prepared_not_sent",
            "external_call_executed": False,
            "human_approval_required": True,
        }


def build_provider_request_plan(package: dict[str, Any], adapter: ProviderAdapter) -> dict[str, Any]:
    requests = [adapter.build_request(item) for item in package.get("deliverables", [])]
    return {
        "campaign_id": package.get("campaign_id"),
        "provider_id": adapter.provider_id,
        "requests": requests,
        "request_count": len(requests),
        "execution_status": "prepared_not_sent",
        "external_calls_executed": 0,
        "approval_gate": "An authorized human must approve each request before any future external adapter sends it.",
    }


def load_provider_profile(path: Path) -> ProviderProfile:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid provider profile JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Provider profile must contain a JSON object")
    return ProviderProfile.from_mapping(payload)


def _string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a non-empty list of strings")
    cleaned = tuple(item.strip() for item in value if item.strip())
    if not cleaned:
        raise ValueError(f"{field} must not be empty")
    if len(cleaned) != len(set(cleaned)):
        raise ValueError(f"{field} values must be unique")
    return cleaned
