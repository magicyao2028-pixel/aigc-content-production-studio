import json
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from aigc_content_studio.trial import (
    evaluate_provider_profile_diff,
    load_json_object,
    run_trial,
    validate_evidence_index,
    validate_external_intake,
    validate_feedback,
    write_trial_report,
)


ROOT = Path(__file__).parents[1]


class TrialReadinessTests(unittest.TestCase):
    def test_complete_trial_passes(self):
        report = run_trial(ROOT)
        self.assertTrue(report["overall_passed"])
        self.assertEqual(report["core_flow"]["routing_status"], "eligible_for_human_review")
        self.assertEqual(report["feedback_regression"]["routing_status"], "blocked")
        self.assertEqual(report["feedback_regression"]["prepared_requests"], 0)
        self.assertTrue(report["review_history"]["append_only"])
        self.assertFalse(report["review_history"]["decision_execution_executed"])

    def test_evidence_index_links_real_files(self):
        checked = validate_evidence_index(ROOT, load_json_object(ROOT / "evidence" / "evidence_index.json"))
        self.assertEqual(len(checked), 11)
        self.assertTrue(all(item["passed"] for item in checked))

    def test_external_intake_requires_full_commit_and_consistent_decision(self):
        payload = load_json_object(ROOT / "evidence" / "external_intake.json")
        short = deepcopy(payload)
        short["candidates"][0]["commit"] = "abc123"
        with self.assertRaisesRegex(ValueError, "full SHA"):
            validate_external_intake(short)
        inconsistent = deepcopy(payload)
        inconsistent["candidates"][0]["code_adopted"] = True
        with self.assertRaisesRegex(ValueError, "must agree"):
            validate_external_intake(inconsistent)

    def test_feedback_source_is_explicit(self):
        payload = load_json_object(ROOT / "evidence" / "feedback_case.json")
        changed = deepcopy(payload)
        changed["source_type"] = "operator"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            validate_feedback(ROOT, changed)

    def test_report_is_reproducible(self):
        with TemporaryDirectory() as directory:
            json_path = Path(directory) / "trial.json"
            md_path = Path(directory) / "trial.md"
            first = write_trial_report(ROOT, json_path, md_path)
            first_bytes = (json_path.read_bytes(), md_path.read_bytes())
            second = write_trial_report(ROOT, json_path, md_path)
            self.assertEqual(first, second)
            self.assertEqual(first_bytes, (json_path.read_bytes(), md_path.read_bytes()))
            self.assertTrue(json.loads(json_path.read_text(encoding="utf-8"))["overall_passed"])

    def test_provider_capability_diff_blocks_reduced_profile(self):
        report = evaluate_provider_profile_diff(ROOT)
        self.assertEqual(report["status"], "breaking")
        self.assertEqual(report["changes"]["removed_deliverables"], ["voiceover"])
        self.assertEqual(report["changes"]["removed_aspect_ratios"], ["16:9"])
        self.assertEqual(report["changes"]["max_duration_delta_seconds"], -15)
        self.assertTrue(report["human_review_required"])


if __name__ == "__main__":
    unittest.main()
