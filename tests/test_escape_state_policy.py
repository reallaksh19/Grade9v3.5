"""No agent-facing surface offers HOLD/BLOCKED/WAITING; missing learner data takes the median."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import escape_state_guard, plan_request, research_first_policy  # noqa: E402


class EscapeStatePolicy(unittest.TestCase):
    def setUp(self):
        self.workflow = research_first_policy.load_workflow()

    def test_workflow_declares_the_no_escape_invariant_first(self):
        self.assertEqual(self.workflow["invariants"][0]["id"], "no_escape_state")
        for word in ("HOLD", "FAILED", "INCOMPLETE", "BLOCKED", "WAITING"):
            self.assertIn(word, self.workflow["forbidden_outcome_states"])

    def test_escape_states_are_detected_and_duty_states_are_not(self):
        self.assertEqual(
            research_first_policy.escape_states(
                ["IDENTITY_HOLD", "BLOCKED_ASSET", "WAITING_FOR_PURPOSE", "HOLD", "INCOMPLETE"],
                self.workflow),
            ["BLOCKED_ASSET", "HOLD", "IDENTITY_HOLD", "INCOMPLETE", "WAITING_FOR_PURPOSE"],
        )
        self.assertEqual(research_first_policy.escape_states(
            ["READY", "RESEARCH_AND_AUTHOR", "READY_FOR_PLANNER", "OWNER_REVIEW",
             "RESEARCH_SOURCE_IDENTITY", "DEFAULT_ELIGIBLE", "the figure is held"], self.workflow), [])

    def test_every_former_escape_state_maps_to_a_declared_duty(self):
        for state in research_first_policy.STATE_FAMILY:
            duty = research_first_policy.duty_for(state, self.workflow)
            self.assertTrue(duty["duty"])
            self.assertTrue(duty["do"])
            self.assertEqual(research_first_policy.escape_states(duty["duty"], self.workflow), [])
        self.assertEqual(research_first_policy.duty_for("SOMETHING_NEW", self.workflow)["duty"],
                         "FIX_AND_REGATE")

    def test_default_learner_is_the_median_and_never_blocks(self):
        learner = research_first_policy.default_learner(self.workflow)
        self.assertEqual(learner["knowledge_percentage"], 50)
        self.assertEqual(learner["knowledge_basis"], "DEFAULT_MEDIAN")
        self.assertEqual(learner["support"], "full")
        self.assertFalse(learner["blocking"])

    def test_request_defaults_fill_every_input_the_planner_used_to_wait_on(self):
        request, applied = research_first_policy.apply_request_defaults(
            {"requested_cores": ["CORE2A", "CORE2B"]}, self.workflow)
        self.assertEqual(request["learner"], {"owner_estimate": {"knowledge_percentage": 50}})
        self.assertEqual(request["practice"]["CORE2A"]["purpose"], "PRACTICE")
        self.assertEqual(request["practice"]["CORE2B"]["purpose"], "PRACTICE")
        self.assertEqual(request["supplemental_question_policy"], "ALLOW_AUTHORED_CANDIDATES")
        self.assertEqual(len(applied), 4)
        owner, applied = research_first_policy.apply_request_defaults({
            "requested_cores": ["CORE2A"],
            "learner": {"owner_estimate": {"knowledge_percentage": 80}},
            "practice": {"CORE2A": {"purpose": "REVISION"}},
            "supplemental_question_policy": "SOURCE_ONLY",
        }, self.workflow)
        self.assertEqual(owner["learner"]["owner_estimate"]["knowledge_percentage"], 80)
        self.assertEqual(owner["practice"]["CORE2A"]["purpose"], "REVISION")
        self.assertEqual(applied, [])

    def test_explicit_unknown_learner_takes_the_default(self):
        request, applied = research_first_policy.apply_request_defaults(
            {"requested_cores": ["CORE1A"], "learner": {"unknown": {"by": "owner"}}}, self.workflow)
        self.assertEqual(request["learner"], {"owner_estimate": {"knowledge_percentage": 50}})
        self.assertEqual(applied[0]["basis"], "DEFAULT_MEDIAN")

    def test_planner_never_waits_on_the_owner_for_any_committed_request(self):
        for pattern in ("*.plan-request.json", "*.author-request.json"):
            for path in sorted((REPO / "Requests").glob(pattern)):
                with self.subTest(request=path.name):
                    report = plan_request.plan(json.loads(path.read_text(encoding="utf-8")))
                    self.assertEqual(report["required_owner_inputs"], [])
                    for row in report.get("products", []):
                        self.assertNotIn(row["state"], {"WAITING_FOR_LEARNER_ENTRY", "WAITING_FOR_PURPOSE"})
                        if row["state"] == "RESEARCH_AND_AUTHOR":
                            self.assertTrue(row["duty"]["duty"])

    def test_core2_gaps_are_always_source_research_never_authoring(self):
        request = json.loads((REPO / "tests/fixtures/prompt-composer/projectile-stress-set.json")
                             .read_text(encoding="utf-8"))
        report = plan_request.plan({
            "request_id": "MOTION-2D-STRESS", "subject": "Physics",
            "bucket_id": "BUCKET-PHY-KIN-2D-MOTION",
            "requested_cores": request["requested_cores"], "learner": request["learner"],
        })
        core2 = next(row for row in report["products"] if row["core"] == "CORE2")
        self.assertEqual(core2["state"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(core2["duty"]["duty"], "ACQUIRE_SOURCE")
        self.assertIn("RESEARCH_SOURCE_BASIS", [row["id"] for row in report["agent_actions"]])

    def test_guard_flags_the_old_hold_wording_and_allows_the_definition(self):
        old = ("If a composer HOLD is present, do not silently resolve it.\n"
               "A missing or incompatible blueprint is a build HOLD.\n"
               "HOLD, FAILED, INCOMPLETE, BLOCKED and WAITING are never an outcome.")
        rows = escape_state_guard._text_findings("x.md", old, self.workflow)
        self.assertEqual([row["surface"] for row in rows], ["x.md:1", "x.md:2"])

    def test_every_agent_facing_surface_is_free_of_escape_states(self):
        report = escape_state_guard.audit()
        self.assertTrue(report["passed"], report["findings"])
        self.assertGreater(report["surfaces_checked"], 10)


if __name__ == "__main__":
    unittest.main()
