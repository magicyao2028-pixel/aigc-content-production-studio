import json
import unittest
from dataclasses import replace
from pathlib import Path

from aigc_content_studio import ContentProductionWorkflow, OfflineProviderAdapter, load_brief, load_provider_profile
from aigc_content_studio.routing import RoutingPolicy, build_guarded_request_plan, load_routing_policy


ROOT = Path(__file__).parents[1]


class RoutingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.package = ContentProductionWorkflow().run(load_brief(ROOT / "data" / "sample_brief.json"))
        self.adapter = OfflineProviderAdapter(load_provider_profile(ROOT / "data" / "offline_provider_profile.json"))
        self.policy = load_routing_policy(ROOT / "data" / "routing_policy.json")

    def test_sample_package_is_eligible_but_never_sent(self):
        plan = build_guarded_request_plan(self.package, self.adapter, self.policy)
        self.assertEqual(plan["routing_status"], "eligible_for_human_review")
        self.assertEqual(plan["request_count"], 3)
        self.assertEqual(plan["estimated_cost_units"], 8)
        self.assertEqual(plan["external_calls_executed"], 0)
        self.assertTrue(all(not item["external_call_executed"] for item in plan["requests"]))

    def test_request_quota_blocks_atomically_without_envelopes(self):
        blocked = build_guarded_request_plan(self.package, self.adapter, replace(self.policy, max_requests_per_run=2))
        self.assertEqual(blocked["routing_status"], "blocked")
        self.assertEqual(blocked["requests"], [])
        self.assertIn("request count 3 exceeds policy limit 2", blocked["reasons"])

    def test_abstract_budget_blocks_atomically(self):
        blocked = build_guarded_request_plan(self.package, self.adapter, replace(self.policy, max_total_cost_units=7))
        self.assertEqual(blocked["routing_status"], "blocked")
        self.assertEqual(blocked["external_calls_executed"], 0)
        self.assertIn("not currency", blocked["cost_unit_boundary"])

    def test_policy_rejects_boolean_fractional_unknown_and_missing_costs(self):
        payload = json.loads((ROOT / "data" / "routing_policy.json").read_text(encoding="utf-8"))
        for value in (True, 1.5, -1):
            changed = dict(payload)
            changed["max_requests_per_run"] = value
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "non-negative integer"):
                    RoutingPolicy.from_mapping(changed)
        changed = dict(payload)
        changed["cost_units_by_deliverable"] = {"short_video": 5}
        with self.assertRaisesRegex(ValueError, "define exactly"):
            RoutingPolicy.from_mapping(changed)


if __name__ == "__main__":
    unittest.main()
