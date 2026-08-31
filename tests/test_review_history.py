import unittest

from aigc_content_studio.review_history import validate_review_history


class ReviewHistoryTests(unittest.TestCase):
    def test_valid_history_is_append_only_and_non_executing(self):
        export = {"decisions": [{"decision_id": "D-1"}, {"decision_id": "D-2"}]}
        result = validate_review_history([
            {"revision": 1, "decision_id": "D-1", "status": "pending", "reviewer": "owner", "applied": False},
            {"revision": 2, "decision_id": "D-2", "status": "accepted", "reviewer": "owner", "applied": False},
        ], export)
        self.assertTrue(result["append_only"])
        self.assertFalse(result["decision_execution_executed"])
        self.assertEqual(result["platform_writes_executed"], 0)

    def test_rejects_applied_or_unknown_decisions(self):
        export = {"decisions": [{"decision_id": "D-1"}]}
        with self.assertRaisesRegex(ValueError, "applied"):
            validate_review_history([{"revision": 1, "decision_id": "D-1", "status": "accepted", "reviewer": "owner", "applied": True}], export)
        with self.assertRaisesRegex(ValueError, "current export"):
            validate_review_history([{"revision": 1, "decision_id": "D-9", "status": "pending", "reviewer": "owner", "applied": False}], export)


if __name__ == "__main__":
    unittest.main()
