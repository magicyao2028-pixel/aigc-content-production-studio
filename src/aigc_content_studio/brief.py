from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SUPPORTED_DELIVERABLES = {"short_video", "cover_image", "voiceover"}


@dataclass(frozen=True)
class DeliverableRequest:
    deliverable_type: str
    aspect_ratio: str
    duration_seconds: int | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "DeliverableRequest":
        deliverable_type = str(value.get("type", "")).strip()
        if deliverable_type not in SUPPORTED_DELIVERABLES:
            raise ValueError(f"Unsupported deliverable type: {deliverable_type}")
        aspect_ratio = str(value.get("aspect_ratio", "")).strip()
        if aspect_ratio not in {"9:16", "16:9", "1:1"}:
            raise ValueError("aspect_ratio must be 9:16, 16:9 or 1:1")
        duration = value.get("duration_seconds")
        if duration is not None:
            try:
                duration = int(duration)
            except (TypeError, ValueError) as exc:
                raise ValueError("duration_seconds must be an integer") from exc
            if duration < 1 or duration > 180:
                raise ValueError("duration_seconds must be between 1 and 180")
        if deliverable_type in {"short_video", "voiceover"} and duration is None:
            raise ValueError(f"{deliverable_type} requires duration_seconds")
        return cls(deliverable_type, aspect_ratio, duration)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CampaignBrief:
    campaign_id: str
    product_name: str
    objective: str
    audience: str
    channels: tuple[str, ...]
    product_facts: tuple[str, ...]
    prohibited_claims: tuple[str, ...]
    brand_voice: tuple[str, ...]
    call_to_action: str
    deliverables: tuple[DeliverableRequest, ...]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "CampaignBrief":
        required = {
            "campaign_id", "product_name", "objective", "audience", "channels",
            "product_facts", "prohibited_claims", "brand_voice", "call_to_action", "deliverables",
        }
        missing = sorted(required.difference(value))
        if missing:
            raise ValueError(f"Missing brief fields: {', '.join(missing)}")

        channels = _string_list(value["channels"], "channels")
        facts = _string_list(value["product_facts"], "product_facts")
        prohibited = _string_list(value["prohibited_claims"], "prohibited_claims", allow_empty=True)
        voice = _string_list(value["brand_voice"], "brand_voice")
        deliverable_values = value["deliverables"]
        if not isinstance(deliverable_values, list) or not deliverable_values:
            raise ValueError("deliverables must be a non-empty list")

        brief = cls(
            campaign_id=str(value["campaign_id"]).strip(),
            product_name=str(value["product_name"]).strip(),
            objective=str(value["objective"]).strip(),
            audience=str(value["audience"]).strip(),
            channels=channels,
            product_facts=facts,
            prohibited_claims=prohibited,
            brand_voice=voice,
            call_to_action=str(value["call_to_action"]).strip(),
            deliverables=tuple(DeliverableRequest.from_mapping(item) for item in deliverable_values),
        )
        scalar_values = (
            brief.campaign_id,
            brief.product_name,
            brief.objective,
            brief.audience,
            brief.call_to_action,
        )
        if not all(scalar_values):
            raise ValueError("Brief text fields must not be blank")
        return brief

    def to_dict(self) -> dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "product_name": self.product_name,
            "objective": self.objective,
            "audience": self.audience,
            "channels": list(self.channels),
            "product_facts": list(self.product_facts),
            "prohibited_claims": list(self.prohibited_claims),
            "brand_voice": list(self.brand_voice),
            "call_to_action": self.call_to_action,
            "deliverables": [item.to_dict() for item in self.deliverables],
        }


def load_brief(path: Path) -> CampaignBrief:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid brief JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Campaign brief must be a JSON object")
    return CampaignBrief.from_mapping(payload)


def _string_list(value: Any, field: str, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    cleaned = tuple(item.strip() for item in value if item.strip())
    if not cleaned and not allow_empty:
        raise ValueError(f"{field} must not be empty")
    return cleaned
