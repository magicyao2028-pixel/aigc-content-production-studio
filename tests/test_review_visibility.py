import unittest

from aigc_content_studio.review_visibility import summarize_stale_feedback


class ReviewVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.export = {"decisions": [
            {"decision_id": "D-1", "status": "blocked_pending_human_review"},
            {"decision_id": "D-2", "status": "blocked_pending_human_review"},
        ]}
        self.batch = [
            {"feedback_id": "F-1", "decision_id": "D-1", "recorded_on": "2026-08-20", "status": "accepted", "summary": "old", "applied": False},
            {"feedback_id": "F-2", "decision_id": "D-2", "recorded_on": "2026-09-04", "status": "pending", "summary": "new", "applied": False},
        ]

    def test_marks_old_accepted_feedback_stale(self):
        result = summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05")
        self.assertEqual(result["stale_count"], 1)
        self.assertEqual(result["excluded_count"], 1)
        self.assertFalse(result["decision_execution_executed"])

    def test_recent_feedback_is_not_stale(self):
        self.batch[0]["recorded_on"] = "2026-09-04"
        result = summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05")
        self.assertEqual(result["stale_count"], 0)

    def test_rejects_unknown_decision(self):
        self.batch[0]["decision_id"] = "D-X"
        with self.assertRaisesRegex(ValueError, "current export"):
            summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05")

    def test_rejects_duplicate_feedback(self):
        self.batch[1]["feedback_id"] = "F-1"
        with self.assertRaisesRegex(ValueError, "unique"):
            summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05")

    def test_rejects_applied_feedback(self):
        self.batch[0]["applied"] = True
        with self.assertRaisesRegex(ValueError, "apply decisions"):
            summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05")

    def test_rejects_invalid_cutoff(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05", stale_after_days=0)

    def test_rejects_invalid_status(self):
        self.batch[0]["status"] = "approved"
        with self.assertRaisesRegex(ValueError, "status"):
            summarize_stale_feedback(self.export, self.batch, as_of_date="2026-09-05")

    def test_rejects_empty_batch(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            summarize_stale_feedback(self.export, [], as_of_date="2026-09-05")


if __name__ == "__main__":
    unittest.main()
