"""Frozen natural-language stress prompts must keep routing through the envisaged path."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import plan_request, resolve_request  # noqa: E402


class FrozenAgentPathStressPrompts(unittest.TestCase):
    CASES = REPO / "tests/fixtures/agent_path_stress/cases.json"

    @classmethod
    def suite(cls):
        return json.loads(cls.CASES.read_text(encoding="utf-8"))

    def test_prompts_are_frozen_with_machine_projection_and_expectations(self):
        suite = self.suite()
        self.assertEqual(suite["suite_id"], "AGENT-PATH-STRESS-V1")
        self.assertGreaterEqual(len(suite["cases"]), 5)
        seen = set()
        for case in suite["cases"]:
            with self.subTest(case=case["case_id"]):
                self.assertNotIn(case["case_id"], seen)
                seen.add(case["case_id"])
                self.assertTrue(case["prompt"].startswith("Prepare "))
                self.assertEqual(case["request"]["request_id"], case["case_id"])
                self.assertIn("owner_estimate", case["request"]["learner"])
                self.assertTrue(case["expected"]["must_not"])

    def test_machine_projection_follows_expected_owner_estimate_path(self):
        for case in self.suite()["cases"]:
            report = plan_request.plan(case["request"])
            expected = case["expected"]
            with self.subTest(case=case["case_id"]):
                self.assertTrue(report["passed"], report["findings"])
                self.assertTrue(report["no_content_authored"])
                self.assertEqual(report["learner_route"]["entry"], expected["entry"])
                self.assertEqual(
                    report["learner_route"]["selected_by"],
                    expected["selected_by"],
                )
                self.assertEqual(
                    report["learner_route"]["state"],
                    expected["route_state"],
                )
                self.assertEqual(
                    report["learner_route"].get("prerequisite_checks", []),
                    expected["prerequisite_checks"],
                )
                self.assertEqual(
                    [row["id"] for row in report["required_owner_inputs"]],
                    expected["required_owner_inputs"],
                )

    def test_percentage_never_becomes_mastery_or_support_level(self):
        purposes = resolve_request.purposes()
        for case in self.suite()["cases"]:
            report = plan_request.plan(case["request"])
            expected = case["expected"]
            serialized = json.dumps(report, sort_keys=True)
            with self.subTest(case=case["case_id"]):
                self.assertNotIn('"DEMONSTRATED"', serialized)
                self.assertEqual(
                    report["learner_route"]["selected_by"],
                    "OWNER_ESTIMATE_CONSERVATIVE_FLOOR",
                )
                for core, support in expected["practice_support"].items():
                    purpose = case["request"]["practice"][core]["purpose"]
                    self.assertEqual(purposes[purpose]["support"], support)

    def test_core1a_core1b_share_one_canonical_segment(self):
        for case in self.suite()["cases"]:
            if not {"CORE1A", "CORE1B"}.issubset(case["request"]["requested_cores"]):
                continue
            report = plan_request.plan(case["request"])
            with self.subTest(case=case["case_id"]):
                self.assertEqual(
                    report["core_relationships"]["CORE1A_CORE1B"],
                    "same canonical rung segment; agency changes, target does not",
                )
                products = {row["core"]: row for row in report["products"]}
                self.assertIn("CORE1A", products)
                self.assertIn("CORE1B", products)
                self.assertEqual(products["CORE1A"]["state"], products["CORE1B"]["state"])

    def test_source_backed_practice_without_source_becomes_research(self):
        cases = [case for case in self.suite()["cases"]
                 if "RESEARCH_SOURCE_BASIS" in case["expected"].get("agent_actions", [])]
        self.assertTrue(cases)
        for case in cases:
            report = plan_request.plan(case["request"])
            with self.subTest(case=case["case_id"]):
                self.assertEqual(report["source"]["basis"], [])
                self.assertIn(
                    "RESEARCH_SOURCE_BASIS",
                    [row["id"] for row in report["agent_actions"]],
                )
                self.assertIn(
                    "RESEARCH_SOURCE_BASIS",
                    report["lifecycle"]["AUTHORING"]["duties"],
                )
                self.assertEqual(report["lifecycle"]["AUTHORING"]["state"], "READY_FOR_AUTHORING")

    def test_fixture_is_system_evidence_only(self):
        serialized = self.CASES.read_text(encoding="utf-8")
        self.assertNotIn('"LIVE_LEARNER"', serialized)
        self.assertNotIn('"profile_ref"', serialized)


if __name__ == "__main__":
    unittest.main()
