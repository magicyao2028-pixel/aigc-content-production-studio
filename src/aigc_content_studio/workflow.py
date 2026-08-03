from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .brief import CampaignBrief, DeliverableRequest


@dataclass
class WorkflowTrace:
    steps: list[dict[str, str]] = field(default_factory=list)

    def record(self, tool: str, purpose: str, status: str = "completed") -> None:
        self.steps.append({"tool": tool, "purpose": purpose, "status": status})


class ContentProductionWorkflow:
    """Builds a reviewable production package without calling a generation model."""

    def run(self, brief: CampaignBrief) -> dict[str, Any]:
        trace = WorkflowTrace()
        trace.record("validate_brief", "Validate product facts, constraints and deliverable specifications.")

        strategy = self._build_strategy(brief)
        trace.record("plan_content_strategy", "Translate the business objective into a content direction.")

        deliverables = [self._plan_deliverable(brief, item, index) for index, item in enumerate(brief.deliverables, 1)]
        trace.record("build_multimodal_tasks", "Create provider-neutral image, video and voice production tasks.")

        manifest = self._build_asset_manifest(brief, deliverables)
        trace.record("create_asset_manifest", "Assign stable IDs and expected evidence to planned assets.")

        review_gates = self._review_gates(brief)
        trace.record("attach_review_gates", "Require factual, brand, rights, privacy and final human review.")

        return {
            "package_version": "0.1",
            "campaign_id": brief.campaign_id,
            "brief": brief.to_dict(),
            "strategy": strategy,
            "deliverables": deliverables,
            "asset_manifest": manifest,
            "review_gates": review_gates,
            "workflow_trace": trace.steps,
            "execution_status": "planned_not_generated",
            "cost_boundary": "No model API or paid service was called by this public workflow.",
            "limitations": [
                "Prompts and shot plans are deterministic planning artifacts, not generated media.",
                "Provider adapters, asset files, version history and publishing integrations are not implemented.",
                "Platform compliance and commercial claims require an authorized human reviewer.",
            ],
        }

    @staticmethod
    def _build_strategy(brief: CampaignBrief) -> dict[str, Any]:
        return {
            "objective": brief.objective,
            "audience": brief.audience,
            "channel_plan": list(brief.channels),
            "message_pillar": brief.product_facts[0],
            "supporting_facts": list(brief.product_facts[1:]),
            "brand_voice": list(brief.brand_voice),
            "call_to_action": brief.call_to_action,
            "content_hypothesis": (
                f"If {brief.audience} sees a concise demonstration anchored to approved product facts, "
                f"the content may support the objective: {brief.objective}."
            ),
            "validation_note": "This hypothesis requires platform and conversion evidence after a controlled release.",
        }

    def _plan_deliverable(
        self,
        brief: CampaignBrief,
        request: DeliverableRequest,
        index: int,
    ) -> dict[str, Any]:
        asset_id = f"{brief.campaign_id}-{index:02d}-{request.deliverable_type.upper()}"
        base = {
            "asset_id": asset_id,
            "type": request.deliverable_type,
            "aspect_ratio": request.aspect_ratio,
            "duration_seconds": request.duration_seconds,
            "status": "planned",
            "human_approval_required": True,
        }
        if request.deliverable_type == "short_video":
            base.update(self._video_plan(brief, request))
        elif request.deliverable_type == "cover_image":
            base.update(self._image_plan(brief, request))
        else:
            base.update(self._voice_plan(brief, request))
        return base

    @staticmethod
    def _video_plan(brief: CampaignBrief, request: DeliverableRequest) -> dict[str, Any]:
        duration = request.duration_seconds or 15
        return {
            "script": {
                "hook": f"A simple way to experience {brief.product_name} in a busy day.",
                "proof": " ".join(brief.product_facts[:2]),
                "call_to_action": brief.call_to_action,
            },
            "shot_plan": [
                {"beat": "hook", "time": f"0-{max(2, duration // 5)}s", "visual": f"Immediate product-context shot of {brief.product_name}.", "purpose": "Stop the scroll without an unsupported claim."},
                {"beat": "proof", "time": f"{max(2, duration // 5)}-{max(6, duration * 3 // 5)}s", "visual": f"Demonstrate the approved fact: {brief.product_facts[0]}", "purpose": "Show evidence rather than a generic beauty montage."},
                {"beat": "cta", "time": f"{max(6, duration * 3 // 5)}-{duration}s", "visual": "Clean product frame with readable call to action.", "purpose": "Close with one reviewable action."},
            ],
            "generation_prompt": (
                f"Create a {duration}-second {request.aspect_ratio} product video for {brief.product_name}. "
                f"Audience: {brief.audience}. Voice: {', '.join(brief.brand_voice)}. "
                f"Use only these approved facts: {'; '.join(brief.product_facts)}. "
                "Keep product identity stable, actions physically coherent, text readable, and leave a clean final CTA frame."
            ),
            "negative_constraints": list(brief.prohibited_claims) + [
                "no invented packaging details",
                "no unstable product appearance",
                "no unreadable overlay text",
            ],
            "quality_checks": ["product consistency", "fact accuracy", "action continuity", "text legibility", "platform-safe framing"],
        }

    @staticmethod
    def _image_plan(brief: CampaignBrief, request: DeliverableRequest) -> dict[str, Any]:
        return {
            "generation_prompt": (
                f"Design a {request.aspect_ratio} short-video cover for {brief.product_name}. "
                f"Audience: {brief.audience}. Style: {', '.join(brief.brand_voice)}. "
                f"Anchor the visual to this approved fact: {brief.product_facts[0]}. "
                "Use one clear focal product, strong mobile hierarchy, reserved headline space, and realistic materials."
            ),
            "negative_constraints": list(brief.prohibited_claims) + [
                "no duplicate product",
                "no distorted logo or packaging",
                "no dense unreadable copy",
            ],
            "quality_checks": ["product identity", "mobile readability", "brand tone", "claim compliance", "copyright review"],
        }

    @staticmethod
    def _voice_plan(brief: CampaignBrief, request: DeliverableRequest) -> dict[str, Any]:
        return {
            "voice_script": (
                f"{brief.product_name}. {brief.product_facts[0]} {brief.call_to_action}"
            ),
            "voice_direction": (
                f"Natural commercial read; {', '.join(brief.brand_voice)}; "
                f"fit within {request.duration_seconds} seconds; no synthetic celebrity imitation."
            ),
            "negative_constraints": ["no unauthorized voice clone", "no exaggerated medical or financial claim"],
            "quality_checks": ["pronunciation", "timing", "natural pacing", "claim accuracy", "voice rights"],
        }

    @staticmethod
    def _build_asset_manifest(brief: CampaignBrief, deliverables: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "asset_id": item["asset_id"],
                "campaign_id": brief.campaign_id,
                "type": item["type"],
                "status": "planned",
                "source_brief": brief.campaign_id,
                "expected_evidence": ["generation settings", "generated candidate", "review record", "approved final"],
            }
            for item in deliverables
        ]

    @staticmethod
    def _review_gates(brief: CampaignBrief) -> list[dict[str, Any]]:
        return [
            {"gate": "FACTS", "owner": "Product / Operations", "checks": list(brief.product_facts), "required": True},
            {"gate": "BRAND", "owner": "Content Lead", "checks": list(brief.brand_voice), "required": True},
            {"gate": "CLAIMS", "owner": "Business Owner", "checks": list(brief.prohibited_claims), "required": True},
            {"gate": "RIGHTS_PRIVACY", "owner": "Content Lead", "checks": ["copyright", "likeness rights", "voice rights", "personal information"], "required": True},
            {"gate": "FINAL_RELEASE", "owner": "Authorized Human", "checks": ["platform rules", "final asset", "CTA", "publishing account"], "required": True},
        ]
