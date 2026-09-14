import json
import unittest
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from aigc_content_studio import (
    ContentProductionWorkflow,
    ExecutionPolicy,
    OfflineProviderAdapter,
    __version__,
    build_execution_preflight,
    load_brief,
    load_execution_policy,
    load_provider_profile,
)
from aigc_content_studio.routing import (
    build_guarded_request_plan,
    load_routing_policy,
)


ROOT = Path(__file__).parents[1]


class ExecutionPreflightTests(unittest.TestCase):
    def setUp(self):
        package = ContentProductionWorkflow().run(
            load_brief(ROOT / "data" / "sample_brief.json")
        )
        adapter = OfflineProviderAdapter(
            load_provider_profile(ROOT / "data" / "offline_provider_profile.json")
        )
        self.routing_policy = load_routing_policy(ROOT / "data" / "routing_policy.json")
        self.routing_plan = build_guarded_request_plan(
            package, adapter, self.routing_policy
        )
        self.execution_policy = load_execution_policy(
            ROOT / "data" / "execution_policy.json"
        )
        self.package = package
        self.adapter = adapter

    def test_unique_plan_builds_deterministic_zero_send_waves(self):
        first = build_execution_preflight(self.routing_plan, self.execution_policy)
        second = build_execution_preflight(self.routing_plan, self.execution_policy)

        self.assertEqual(first, second)
        self.assertEqual(first["preflight_status"], "prepared_for_human_review")
        self.assertEqual(first["execution_status"], "prepared_not_sent")
        self.assertFalse(first["execution_authorized"])
        self.assertEqual(first["job_count"], 3)
        self.assertEqual(first["wave_count"], 2)
        self.assertEqual([job["wave_number"] for job in first["jobs"]], [1, 1, 2])
        self.assertEqual([wave["job_count"] for wave in first["waves"]], [2, 1])
        self.assertEqual(len({job["job_id"] for job in first["jobs"]}), 3)
        self.assertEqual(len({job["idempotency_key"] for job in first["jobs"]}), 3)
        self.assertTrue(
            all(job["execution_status"] == "prepared_not_sent" for job in first["jobs"])
        )
        self.assertTrue(all(job["attempts_executed"] == 0 for job in first["jobs"]))
        self.assertTrue(
            all(job["external_requests_executed"] == 0 for job in first["jobs"])
        )
        self.assertTrue(
            all(job["provider_sends_executed"] == 0 for job in first["jobs"])
        )
        self.assertEqual(first["attempts_executed"], 0)
        self.assertEqual(first["external_requests_executed"], 0)
        self.assertEqual(first["provider_sends_executed"], 0)

    def test_checked_in_sample_matches_current_preflight(self):
        routing_plan = json.loads(
            (ROOT / "examples" / "sample_routing_plan.json").read_text(
                encoding="utf-8"
            )
        )
        expected = build_execution_preflight(routing_plan, self.execution_policy)
        actual = json.loads(
            (ROOT / "examples" / "sample_execution_preflight.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(actual, expected)

    @patch("aigc_content_studio.execution_preflight._build_job")
    def test_duplicate_fingerprint_blocks_atomically_before_job_creation(
        self, build_job
    ):
        duplicate_package = deepcopy(self.package)
        duplicate_package["deliverables"].append(
            deepcopy(duplicate_package["deliverables"][0])
        )
        relaxed = replace(
            self.routing_policy,
            max_requests_per_run=10,
            max_total_cost_units=20,
        )
        duplicate_routing = build_guarded_request_plan(
            duplicate_package, self.adapter, relaxed
        )
        duplicate_routing["requests"][-1]["request_id"] += "-DUPLICATE"

        result = build_execution_preflight(duplicate_routing, self.execution_policy)

        self.assertEqual(duplicate_routing["routing_status"], "eligible_for_human_review")
        self.assertEqual(result["preflight_status"], "blocked")
        self.assertEqual(result["execution_status"], "blocked_not_prepared")
        self.assertEqual(len(result["duplicate_fingerprints"]), 1)
        self.assertEqual(result["duplicate_request_ids"], [])
        self.assertEqual(result["job_count"], 0)
        self.assertEqual(result["wave_count"], 0)
        self.assertEqual(result["jobs"], [])
        self.assertEqual(result["waves"], [])
        self.assertEqual(result["attempts_executed"], 0)
        self.assertEqual(result["external_requests_executed"], 0)
        self.assertEqual(result["provider_sends_executed"], 0)
        build_job.assert_not_called()

    def test_duplicate_request_id_blocks_even_when_payload_changes(self):
        routing_plan = deepcopy(self.routing_plan)
        duplicate = deepcopy(routing_plan["requests"][0])
        duplicate["payload"]["prompt"] += " Distinct retry payload."
        routing_plan["requests"].append(duplicate)
        routing_plan["request_count"] += 1

        result = build_execution_preflight(routing_plan, self.execution_policy)

        self.assertEqual(result["preflight_status"], "blocked")
        self.assertEqual(result["duplicate_fingerprints"], [])
        self.assertEqual(result["duplicate_request_ids"], [duplicate["request_id"]])
        self.assertEqual(result["jobs"], [])

    def test_only_eligible_zero_send_routing_plan_is_accepted(self):
        blocked = build_guarded_request_plan(
            self.package,
            self.adapter,
            replace(self.routing_policy, max_requests_per_run=2),
        )
        with self.assertRaisesRegex(ValueError, "eligible routing plan"):
            build_execution_preflight(blocked, self.execution_policy)

        tampered = deepcopy(self.routing_plan)
        tampered["requests"][0]["execution_status"] = "sent"
        with self.assertRaisesRegex(ValueError, "prepared_not_sent"):
            build_execution_preflight(tampered, self.execution_policy)

        tampered = deepcopy(self.routing_plan)
        tampered["requests"][0]["external_call_executed"] = True
        with self.assertRaisesRegex(ValueError, "zero external calls"):
            build_execution_preflight(tampered, self.execution_policy)

        tampered = deepcopy(self.routing_plan)
        tampered["human_approval_required"] = False
        with self.assertRaisesRegex(ValueError, "human approval"):
            build_execution_preflight(tampered, self.execution_policy)

    def test_routing_plan_shape_and_provider_binding_fail_closed(self):
        tampered = deepcopy(self.routing_plan)
        tampered["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "fields are invalid"):
            build_execution_preflight(tampered, self.execution_policy)

        tampered = deepcopy(self.routing_plan)
        tampered["request_count"] += 1
        with self.assertRaisesRegex(ValueError, "request_count"):
            build_execution_preflight(tampered, self.execution_policy)

        tampered = deepcopy(self.routing_plan)
        tampered["requests"][0]["provider_id"] = "another-provider"
        with self.assertRaisesRegex(ValueError, "must match"):
            build_execution_preflight(tampered, self.execution_policy)

    def test_execution_policy_is_strict_and_bounded(self):
        raw = json.loads(
            (ROOT / "data" / "execution_policy.json").read_text(encoding="utf-8")
        )
        changed = deepcopy(raw)
        changed["unexpected"] = True
        with self.assertRaisesRegex(ValueError, "fields are invalid"):
            ExecutionPolicy.from_mapping(changed)

        for field, value in (
            ("max_concurrency", True),
            ("max_concurrency", 0),
            ("max_concurrency", 17),
            ("max_attempts_per_job", "3"),
            ("max_attempts_per_job", 6),
        ):
            changed = deepcopy(raw)
            changed[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    ExecutionPolicy.from_mapping(changed)

        changed = deepcopy(raw)
        changed["retry_backoff_seconds"] = [2]
        with self.assertRaisesRegex(ValueError, "exactly"):
            ExecutionPolicy.from_mapping(changed)

        changed = deepcopy(raw)
        changed["retry_backoff_seconds"] = [5, 2]
        with self.assertRaisesRegex(ValueError, "non-decreasing"):
            ExecutionPolicy.from_mapping(changed)

        changed = deepcopy(raw)
        changed["retry_backoff_seconds"] = [2, 3_601]
        with self.assertRaisesRegex(ValueError, "between 1 and 3600"):
            ExecutionPolicy.from_mapping(changed)

    def test_policy_file_round_trip_and_release_version_are_consistent(self):
        self.assertEqual(
            self.execution_policy,
            ExecutionPolicy.from_mapping(self.execution_policy.to_dict()),
        )
        self.assertEqual(__version__, "1.1.0")
        project_metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "1.1.0"', project_metadata)


if __name__ == "__main__":
    unittest.main()
