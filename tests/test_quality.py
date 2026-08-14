import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from aigc_content_studio import FAILURE_CATEGORIES, evaluate_quality_files, evaluate_quality_fixture


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "examples" / "sample_production_package.json"
TAXONOMY = ROOT / "data" / "failure_taxonomy.json"
FIXTURE = ROOT / "data" / "quality_fixture.json"


def payloads():
    return (
        json.loads(PACKAGE.read_text(encoding="utf-8")),
        json.loads(TAXONOMY.read_text(encoding="utf-8")),
        json.loads(FIXTURE.read_text(encoding="utf-8")),
    )


class QualityFixtureTests(unittest.TestCase):
    def test_fixture_exercises_all_six_categories_without_external_calls(self):
        report = evaluate_quality_files(PACKAGE, TAXONOMY, FIXTURE)

        self.assertEqual(report["summary"]["reviewed_cases"], 7)
        self.assertEqual(report["summary"]["blocked_cases"], 6)
        self.assertEqual(report["summary"]["pass_fixture_only_cases"], 1)
        self.assertEqual(report["summary"]["taxonomy_coverage"], 1.0)
        self.assertEqual(set(report["summary"]["failure_counts"]), set(FAILURE_CATEGORIES))
        self.assertTrue(all(count == 1 for count in report["summary"]["failure_counts"].values()))
        self.assertEqual(report["external_calls_executed"], 0)

    def test_every_failure_blocks_release_and_retains_evidence(self):
        package, taxonomy, fixture = payloads()
        report = evaluate_quality_fixture(package, taxonomy, fixture)
        failures = [case for case in report["cases"] if case["failure_count"]]

        self.assertTrue(all(case["release_decision"] == "blocked" for case in failures))
        self.assertTrue(all(case["failures"][0]["evidence"] for case in failures))
        self.assertTrue(all(case["human_review_required"] for case in report["cases"]))

    def test_unknown_category_is_rejected(self):
        package, taxonomy, fixture = payloads()
        fixture["cases"][1]["failures"][0]["category"] = "looks_bad"

        with self.assertRaisesRegex(ValueError, "Unknown failure category"):
            evaluate_quality_fixture(package, taxonomy, fixture)

    def test_taxonomy_must_define_exact_controlled_set(self):
        package, taxonomy, fixture = payloads()
        taxonomy["categories"] = taxonomy["categories"][:-1]

        with self.assertRaisesRegex(ValueError, "six controlled categories"):
            evaluate_quality_fixture(package, taxonomy, fixture)

    def test_fixture_asset_must_match_package_manifest(self):
        package, taxonomy, fixture = payloads()
        fixture["cases"][0]["asset_id"] = "MISSING-ASSET"

        with self.assertRaisesRegex(ValueError, "Unknown quality fixture asset ID"):
            evaluate_quality_fixture(package, taxonomy, fixture)

    def test_real_looking_candidate_reference_is_rejected(self):
        package, taxonomy, fixture = payloads()
        fixture["cases"][0]["candidate_reference"] = "https://example.com/real-output.mp4"

        with self.assertRaisesRegex(ValueError, "synthetic-fixture"):
            evaluate_quality_fixture(package, taxonomy, fixture)

    def test_file_loader_rejects_non_object_fixture(self):
        with TemporaryDirectory() as directory:
            bad_fixture = Path(directory) / "fixture.json"
            bad_fixture.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "quality fixture must be a JSON object"):
                evaluate_quality_files(PACKAGE, TAXONOMY, bad_fixture)


if __name__ == "__main__":
    unittest.main()
