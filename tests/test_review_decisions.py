import unittest

from aigc_content_studio.review_decisions import build_human_review_export


class ReviewDecisionTests(unittest.TestCase):
    def test_export_is_pending_and_non_executing(self):
        report = build_human_review_export(
            {"cases": [{"case_id": "CASE-01", "asset_id": "ASSET-01", "release_decision": "blocked", "failures": [{"owner": "Content Lead", "category": "unreadable_text"}]}]},
            {"status": "breaking", "candidate_provider_id": "provider-candidate"},
            {"external_calls_executed": 0},
        )
        self.assertEqual(report["decision_count"], 2)
        self.assertTrue(all(item["status"] == "blocked_pending_human_review" for item in report["decisions"]))
        self.assertFalse(report["governance"]["decision_execution_executed"])
        self.assertEqual(report["governance"]["platform_writes_executed"], 0)

    def test_pass_fixture_only_case_is_not_exported(self):
        report = build_human_review_export(
            {"cases": [{"case_id": "CASE-02", "asset_id": "ASSET-02", "release_decision": "pass_fixture_only", "failures": []}]},
            {"status": "clear"},
            {},
        )
        self.assertEqual(report["decisions"], [])


if __name__ == "__main__":
    unittest.main()
