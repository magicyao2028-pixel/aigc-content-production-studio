import json
import unittest
from pathlib import Path

from aigc_content_studio import (
    ContentProductionWorkflow,
    OfflineProviderAdapter,
    PromptTemplateSet,
    ProviderProfile,
    build_provider_request_plan,
    load_brief,
    load_provider_profile,
    load_template_set,
)


ROOT = Path(__file__).parents[1]
BRIEF = ROOT / "data" / "sample_brief.json"
TEMPLATES = ROOT / "data" / "prompt_templates.json"
PROFILE = ROOT / "data" / "offline_provider_profile.json"


def template_payload() -> dict:
    return json.loads(TEMPLATES.read_text(encoding="utf-8"))


def provider_payload() -> dict:
    return json.loads(PROFILE.read_text(encoding="utf-8"))


class PromptTemplateTests(unittest.TestCase):
    def test_custom_templates_render_and_report_identity(self):
        templates = load_template_set(TEMPLATES)
        package = ContentProductionWorkflow(templates).run(load_brief(BRIEF))
        video = next(item for item in package["deliverables"] if item["type"] == "short_video")

        self.assertEqual(package["package_version"], "0.4")
        self.assertEqual(package["prompt_template"], {"template_set_id": "retail-content-safe-v1", "version": "1.0"})
        self.assertIn("approved call to action", video["generation_prompt"])
        self.assertIn("Jasmine Tea Gift Box", video["generation_prompt"])

    def test_every_deliverable_has_a_rendered_generation_prompt(self):
        package = ContentProductionWorkflow(load_template_set(TEMPLATES)).run(load_brief(BRIEF))
        self.assertTrue(all(item["generation_prompt"].strip() for item in package["deliverables"]))

    def test_rejects_unknown_or_unsafe_template_fields(self):
        payload = template_payload()
        payload["templates"]["short_video"] += " {api_key}"
        with self.assertRaisesRegex(ValueError, "Unknown template fields"):
            PromptTemplateSet.from_mapping(payload)

        payload = template_payload()
        payload["templates"]["short_video"] += " {product_name.__class__}"
        with self.assertRaisesRegex(ValueError, "Unsafe template field syntax"):
            PromptTemplateSet.from_mapping(payload)

    def test_rejects_missing_required_template_or_placeholder(self):
        payload = template_payload()
        del payload["templates"]["voiceover"]
        with self.assertRaisesRegex(ValueError, "define exactly"):
            PromptTemplateSet.from_mapping(payload)

        payload = template_payload()
        payload["templates"]["voiceover"] = "Read {product_name} using {approved_facts}."
        with self.assertRaisesRegex(ValueError, "Missing required template fields"):
            PromptTemplateSet.from_mapping(payload)


class ProviderAdapterTests(unittest.TestCase):
    def test_builds_reviewable_requests_without_sending(self):
        package = ContentProductionWorkflow(load_template_set(TEMPLATES)).run(load_brief(BRIEF))
        adapter = OfflineProviderAdapter(load_provider_profile(PROFILE))
        plan = build_provider_request_plan(package, adapter)

        self.assertEqual(plan["request_count"], 3)
        self.assertEqual(plan["external_calls_executed"], 0)
        self.assertEqual(plan["execution_status"], "prepared_not_sent")
        self.assertTrue(all(not item["external_call_executed"] for item in plan["requests"]))
        self.assertTrue(all(item["human_approval_required"] for item in plan["requests"]))

    def test_rejects_external_execution_profile(self):
        payload = provider_payload()
        payload["external_execution_enabled"] = True
        with self.assertRaisesRegex(ValueError, "cannot enable external execution"):
            ProviderProfile.from_mapping(payload)

    def test_rejects_unknown_profile_fields_to_avoid_embedded_secrets(self):
        payload = provider_payload()
        payload["api_key"] = "not-a-real-key"
        with self.assertRaisesRegex(ValueError, "Unknown provider profile fields"):
            ProviderProfile.from_mapping(payload)

    def test_enforces_provider_capability_limits(self):
        package = ContentProductionWorkflow(load_template_set(TEMPLATES)).run(load_brief(BRIEF))
        payload = provider_payload()
        payload["supported_deliverables"] = ["cover_image", "voiceover"]
        adapter = OfflineProviderAdapter(ProviderProfile.from_mapping(payload))
        with self.assertRaisesRegex(ValueError, "does not support deliverable type"):
            build_provider_request_plan(package, adapter)

        payload = provider_payload()
        payload["max_duration_seconds"] = 10
        adapter = OfflineProviderAdapter(ProviderProfile.from_mapping(payload))
        with self.assertRaisesRegex(ValueError, "duration limit exceeded"):
            build_provider_request_plan(package, adapter)


if __name__ == "__main__":
    unittest.main()
