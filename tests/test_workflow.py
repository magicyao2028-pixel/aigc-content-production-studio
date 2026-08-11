import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from aigc_content_studio import CampaignBrief, ContentProductionWorkflow, load_brief


ROOT = Path(__file__).parents[1]
SAMPLE = ROOT / "data" / "sample_brief.json"


class ContentProductionWorkflowTests(unittest.TestCase):
    def test_builds_three_linked_deliverables(self):
        package = ContentProductionWorkflow().run(load_brief(SAMPLE))

        self.assertEqual(len(package["deliverables"]), 3)
        self.assertEqual(len(package["asset_manifest"]), 3)
        self.assertEqual(package["execution_status"], "planned_not_generated")
        self.assertTrue(all(item["human_approval_required"] for item in package["deliverables"]))

    def test_video_plan_uses_only_approved_facts(self):
        brief = load_brief(SAMPLE)
        package = ContentProductionWorkflow().run(brief)
        video = next(item for item in package["deliverables"] if item["type"] == "short_video")

        self.assertIn(brief.product_facts[0], video["generation_prompt"])
        self.assertIn(brief.call_to_action, video["script"]["call_to_action"])
        self.assertIn(brief.prohibited_claims[0], video["negative_constraints"])

    def test_preserves_five_review_gates_and_trace(self):
        package = ContentProductionWorkflow().run(load_brief(SAMPLE))

        self.assertEqual([item["gate"] for item in package["review_gates"]], ["FACTS", "BRAND", "CLAIMS", "RIGHTS_PRIVACY", "FINAL_RELEASE"])
        self.assertEqual(len(package["workflow_trace"]), 6)
        self.assertEqual(package["prompt_template"]["template_set_id"], "builtin-safe-default")

    def test_rejects_unsupported_deliverable(self):
        value = json.loads(SAMPLE.read_text(encoding="utf-8"))
        value["deliverables"] = [{"type": "automatic_publish", "aspect_ratio": "9:16"}]

        with self.assertRaisesRegex(ValueError, "Unsupported deliverable"):
            CampaignBrief.from_mapping(value)

    def test_load_brief_rejects_missing_product_facts(self):
        value = json.loads(SAMPLE.read_text(encoding="utf-8"))
        value["product_facts"] = []
        with TemporaryDirectory() as directory:
            path = Path(directory) / "brief.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "product_facts must not be empty"):
                load_brief(path)


if __name__ == "__main__":
    unittest.main()
