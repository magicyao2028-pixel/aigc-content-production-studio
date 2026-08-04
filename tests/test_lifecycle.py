import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from aigc_content_studio import AssetLedger, ContentProductionWorkflow, load_brief


ROOT = Path(__file__).parents[1]
SAMPLE = ROOT / "data" / "sample_brief.json"


def sample_ledger() -> tuple[AssetLedger, str]:
    package = ContentProductionWorkflow().run(load_brief(SAMPLE))
    asset_id = package["asset_manifest"][0]["asset_id"]
    return AssetLedger.from_manifest(package["campaign_id"], package["asset_manifest"]), asset_id


class AssetLifecycleTests(unittest.TestCase):
    def test_initializes_all_manifest_assets_with_append_only_events(self):
        package = ContentProductionWorkflow().run(load_brief(SAMPLE))
        ledger = AssetLedger.from_manifest(package["campaign_id"], package["asset_manifest"]).to_dict()

        self.assertEqual(len(ledger["assets"]), 3)
        self.assertEqual(len(ledger["events"]), 3)
        self.assertTrue(all(item["current_status"] == "planned" for item in ledger["assets"].values()))

    def test_records_valid_status_path_and_versions(self):
        ledger, asset_id = sample_ledger()

        ledger.transition(asset_id, "generated_candidate", "content-operator", "Candidate file recorded.")
        ledger.transition(asset_id, "in_review", "content-lead", "Submitted for five-gate review.")
        event = ledger.transition(asset_id, "approved_final", "business-owner", "All required gates passed.")

        state = ledger.to_dict()
        self.assertEqual(state["assets"][asset_id], {"current_status": "approved_final", "version": 4})
        self.assertEqual(event["from_status"], "in_review")
        self.assertEqual(event["version"], 4)

    def test_rejects_skipping_human_review(self):
        ledger, asset_id = sample_ledger()

        with self.assertRaisesRegex(ValueError, "planned -> approved_final"):
            ledger.transition(asset_id, "approved_final", "operator", "Skip review")

    def test_supports_changes_requested_loop(self):
        ledger, asset_id = sample_ledger()
        ledger.transition(asset_id, "generated_candidate", "operator", "Candidate v1")
        ledger.transition(asset_id, "in_review", "reviewer", "Review started")
        ledger.transition(asset_id, "changes_requested", "reviewer", "CTA text is too small")
        ledger.transition(asset_id, "generated_candidate", "operator", "Candidate v2")

        self.assertEqual(ledger.to_dict()["assets"][asset_id]["current_status"], "generated_candidate")

    def test_round_trips_local_json_without_losing_history(self):
        ledger, asset_id = sample_ledger()
        ledger.transition(asset_id, "generated_candidate", "operator", "Candidate saved")
        before = ledger.to_dict()
        with TemporaryDirectory() as directory:
            path = Path(directory) / "asset_history.json"
            ledger.save(path)
            after = AssetLedger.load(path).to_dict()

        self.assertEqual(after, before)

    def test_rejects_unknown_asset(self):
        ledger, _ = sample_ledger()

        with self.assertRaisesRegex(ValueError, "Unknown asset ID"):
            ledger.transition("MISSING", "generated_candidate", "operator", "Candidate saved")


if __name__ == "__main__":
    unittest.main()
