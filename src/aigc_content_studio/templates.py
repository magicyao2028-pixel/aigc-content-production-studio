from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from string import Formatter
from typing import Any

from .brief import CampaignBrief, DeliverableRequest, SUPPORTED_DELIVERABLES


ALLOWED_FIELDS = {
    "product_name",
    "audience",
    "aspect_ratio",
    "duration_seconds",
    "brand_voice",
    "approved_facts",
    "call_to_action",
    "prohibited_claims",
}

REQUIRED_FIELDS = {
    "short_video": {"product_name", "audience", "aspect_ratio", "duration_seconds", "approved_facts"},
    "cover_image": {"product_name", "audience", "aspect_ratio", "approved_facts"},
    "voiceover": {"product_name", "duration_seconds", "approved_facts", "call_to_action"},
}


@dataclass(frozen=True)
class PromptTemplateSet:
    template_set_id: str
    version: str
    templates: dict[str, str]

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "PromptTemplateSet":
        required = {"template_set_id", "version", "templates"}
        missing = sorted(required - set(value))
        if missing:
            raise ValueError(f"Missing template fields: {', '.join(missing)}")
        template_set_id = str(value["template_set_id"]).strip()
        version = str(value["version"]).strip()
        templates = value["templates"]
        if not template_set_id or not version:
            raise ValueError("template_set_id and version must not be blank")
        if not isinstance(templates, dict):
            raise ValueError("templates must be an object")
        if set(templates) != SUPPORTED_DELIVERABLES:
            raise ValueError("templates must define exactly: cover_image, short_video, voiceover")
        cleaned: dict[str, str] = {}
        for deliverable_type, template in templates.items():
            if not isinstance(template, str) or not template.strip():
                raise ValueError(f"{deliverable_type} template must not be blank")
            if len(template) > 4000:
                raise ValueError(f"{deliverable_type} template exceeds 4000 characters")
            fields = _template_fields(template)
            unknown = sorted(fields - ALLOWED_FIELDS)
            if unknown:
                raise ValueError(f"Unknown template fields for {deliverable_type}: {', '.join(unknown)}")
            missing_fields = sorted(REQUIRED_FIELDS[deliverable_type] - fields)
            if missing_fields:
                raise ValueError(
                    f"Missing required template fields for {deliverable_type}: {', '.join(missing_fields)}"
                )
            cleaned[deliverable_type] = template.strip()
        return cls(template_set_id=template_set_id, version=version, templates=cleaned)

    def render(self, brief: CampaignBrief, request: DeliverableRequest) -> str:
        context = {
            "product_name": brief.product_name,
            "audience": brief.audience,
            "aspect_ratio": request.aspect_ratio,
            "duration_seconds": request.duration_seconds if request.duration_seconds is not None else "not_applicable",
            "brand_voice": ", ".join(brief.brand_voice),
            "approved_facts": "; ".join(brief.product_facts),
            "call_to_action": brief.call_to_action,
            "prohibited_claims": "; ".join(brief.prohibited_claims) or "none declared",
        }
        return self.templates[request.deliverable_type].format_map(context)

    def metadata(self) -> dict[str, str]:
        return {"template_set_id": self.template_set_id, "version": self.version}


def load_template_set(path: Path) -> PromptTemplateSet:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid template JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Template file must contain a JSON object")
    return PromptTemplateSet.from_mapping(payload)


def default_template_set() -> PromptTemplateSet:
    return PromptTemplateSet.from_mapping({
        "template_set_id": "builtin-safe-default",
        "version": "1.0",
        "templates": {
            "short_video": (
                "Create a {duration_seconds}-second {aspect_ratio} product video for {product_name}. "
                "Audience: {audience}. Voice: {brand_voice}. Use only these approved facts: "
                "{approved_facts}. Keep product identity stable, actions physically coherent, text readable, "
                "and leave a clean final CTA frame."
            ),
            "cover_image": (
                "Design a {aspect_ratio} short-video cover for {product_name}. Audience: {audience}. "
                "Style: {brand_voice}. Anchor the visual to these approved facts: {approved_facts}. "
                "Use one clear focal product, strong mobile hierarchy, reserved headline space, and realistic materials."
            ),
            "voiceover": (
                "Read a {duration_seconds}-second voiceover for {product_name}. Use only these approved facts: "
                "{approved_facts}. End with: {call_to_action}"
            ),
        },
    })


def _template_fields(template: str) -> set[str]:
    fields: set[str] = set()
    try:
        parsed = Formatter().parse(template)
        for _, field_name, _, _ in parsed:
            if field_name is None:
                continue
            if not field_name.replace("_", "").isalpha():
                raise ValueError(f"Unsafe template field syntax: {field_name}")
            fields.add(field_name)
    except ValueError as exc:
        raise ValueError(f"Invalid template syntax: {exc}") from exc
    return fields
