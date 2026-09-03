import unittest

from aigc_content_studio.feedback_replay import replay_reviewer_feedback


class FeedbackReplayTests(unittest.TestCase):
    def setUp(self):
        self.export = {"decisions": [{"decision_id": "D-1"}, {"decision_id": "D-2"}]}
        self.batch = [
            {"feedback_id": "F-1", "decision_id": "D-1", "recorded_on": "2026-08-01", "classification": "usability", "status": "accepted", "summary": "clearer", "applied": False},
            {"feedback_id": "F-2", "decision_id": "D-2", "recorded_on": "2026-08-02", "classification": "requirement", "status": "pending", "summary": "wait", "applied": False},
        ]

    def test_replays_only_accepted_feedback(self):
        result = replay_reviewer_feedback(self.batch, self.export)
        self.assertEqual(result["replayed_count"], 1)
        self.assertEqual(result["excluded_count"], 1)
        self.assertFalse(result["decision_execution_executed"])

    def test_unknown_decision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "current export"):
            replay_reviewer_feedback([dict(self.batch[0], decision_id="D-X")], self.export)

    def test_applied_feedback_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "apply decisions"):
            replay_reviewer_feedback([dict(self.batch[0], applied=True)], self.export)

    def test_dates_must_be_chronological(self):
        invalid = [dict(self.batch[0]), dict(self.batch[1], recorded_on="2026-07-01")]
        with self.assertRaisesRegex(ValueError, "chronological"):
            replay_reviewer_feedback(invalid, self.export)


if __name__ == "__main__":
    unittest.main()
