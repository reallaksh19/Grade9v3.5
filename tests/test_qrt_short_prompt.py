from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import qrt_short_prompt as sp


REPO = Path(__file__).resolve().parents[1]


class QRTShortPromptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = sp.load(sp.WORKFLOW_PATH)

    def minimal(self):
        return {
            "schema": "qrt-short-prompt-request/v1",
            "subject": "Mathematics",
            "grade": 9,
            "topic": "Surface Areas and Volumes",
            "questions": [
                {"text": f"Question {i}: find the requested Grade 9 mensuration quantity from the stated dimensions."}
                for i in range(1, 11)
            ],
            "requested_outputs": ["LEARNER_HTML", "QRT_EVIDENCE"],
        }

    def test_minimal_prompt_asks_only_decision_changing_owner_inputs(self):
        result = sp.plan(self.minimal(), self.workflow)
        self.assertEqual(result["state"], "OWNER_INPUT_REQUIRED")
        self.assertEqual(
            [row["id"] for row in result["owner_questions"]],
            ["LEARNER_PROFILE", "QUESTION_PROVENANCE", "PRODUCT_INTENT"],
        )
        joined = json.dumps(result["owner_questions"])
        for forbidden in ("difficulty", "cognitive demand", "QRT template", "X/Y/Z/W"):
            self.assertNotIn(forbidden, joined)

    def test_question_ids_are_generated_but_question_text_is_preserved(self):
        result = sp.plan(self.minimal(), self.workflow)
        rows = result["request"]["questions"]
        self.assertEqual([row["id"] for row in rows], [f"Q{i}" for i in range(1, 11)])
        self.assertTrue(rows[0]["text"].startswith("Question 1:"))

    def test_complete_owner_supplied_request_routes_to_core2(self):
        raw = self.minimal()
        raw["learner_input"] = {
            "mode": "PROFILE",
            "ideas": [
                {"idea": "radius versus diameter", "status": "UNCERTAIN"},
                {"idea": "substitution", "status": "DEMONSTRATED"},
            ],
        }
        raw["provenance"] = {"kind": "OWNER_SUPPLIED"}
        raw["product_intent"] = "PRESERVE_OWNER_QUESTIONS"
        result = sp.plan(raw, self.workflow)
        self.assertEqual(result["state"], "READY_TO_AUTHOR")
        self.assertEqual(result["role"], "CORE2")
        self.assertEqual(result["blueprint_ref"], "BP-CORE2-SOURCE-QUESTION@1.5.0")
        self.assertEqual(result["learner_mode"], "PERSONALISED")
        self.assertEqual(result["owner_questions"], [])

    def test_authored_practice_routes_to_core2a(self):
        raw = self.minimal()
        raw["learner_input"] = {"mode": "USE_DEFAULT_GENERIC"}
        raw["provenance"] = {"kind": "AUTHORED_PRACTICE"}
        raw["product_intent"] = "AUTHORED_PRACTICE"
        result = sp.plan(raw, self.workflow)
        self.assertEqual(result["state"], "READY_TO_AUTHOR")
        self.assertEqual(result["role"], "CORE2A")
        self.assertEqual(result["blueprint_ref"], "BP-CORE2A-SUPPORTED-APPLICATION@1.1.0")
        self.assertIn("RUN_SHORT_DIAGNOSTIC_BEFORE_MAKING_PERSONALISED_XY_CLAIMS", result["agent_duties"])

    def test_external_source_without_locator_asks_source_details(self):
        raw = self.minimal()
        raw["learner_input"] = {"mode": "USE_DEFAULT_GENERIC"}
        raw["provenance"] = {"kind": "EXTERNAL_SOURCE"}
        raw["product_intent"] = "PRESERVE_OWNER_QUESTIONS"
        result = sp.plan(raw, self.workflow)
        self.assertEqual([row["id"] for row in result["owner_questions"]], ["SOURCE_DETAILS"])

    def test_agent_derives_demand_difficulty_xyzw_and_support(self):
        raw = self.minimal()
        raw["learner_input"] = {"mode": "USE_DEFAULT_GENERIC"}
        raw["provenance"] = {"kind": "OWNER_SUPPLIED"}
        raw["product_intent"] = "PRESERVE_OWNER_QUESTIONS"
        result = sp.plan(raw, self.workflow)
        fields = " ".join(result["agent_derived_fields"])
        self.assertIn("five-component difficulty", fields)
        self.assertIn("cognitive demand", fields)
        self.assertIn("X/Y/Z/W", fields)
        self.assertIn("hints/representations/helpers/misconception repair", fields)
        self.assertNotIn("LEARNER_PROFILE", [row["id"] for row in result["owner_questions"]])

    def test_html_and_qrt_are_forced_outputs_even_if_owner_lists_one(self):
        raw = self.minimal()
        raw["requested_outputs"] = ["LEARNER_HTML"]
        result = sp.plan(raw, self.workflow)
        self.assertEqual(result["requested_outputs"], ["LEARNER_HTML", "QRT_EVIDENCE"])

    def test_authored_practice_cannot_be_promoted_to_preserved_core2(self):
        raw = self.minimal()
        raw["learner_input"] = {"mode": "USE_DEFAULT_GENERIC"}
        raw["provenance"] = {"kind": "AUTHORED_PRACTICE"}
        raw["product_intent"] = "PRESERVE_OWNER_QUESTIONS"
        with self.assertRaisesRegex(sp.ShortPromptError, "cannot be promoted"):
            sp.plan(raw, self.workflow)

    def test_workflow_contract_explicitly_forbids_silent_personalization_default(self):
        self.assertTrue(self.workflow["clarification_policy"]["no_silent_personalization_default"])
        self.assertTrue(self.workflow["clarification_policy"]["default_generic_requires_explicit_owner_choice"])



    def test_surface_areas_and_volumes_short_prompt_fixture_requires_owner_clarification(self):
        raw = json.loads(
            (REPO / "tests" / "fixtures" / "quality" / "qrt-short-prompt-surface-areas-volumes.v1.json")
            .read_text(encoding="utf-8")
        )
        result = sp.plan(raw, self.workflow)
        self.assertEqual(result["state"], "OWNER_INPUT_REQUIRED")
        self.assertEqual(len(result["request"]["questions"]), 10)
        self.assertEqual(result["request"]["topic"], "Surface Areas and Volumes")
        self.assertEqual(
            [row["id"] for row in result["owner_questions"]],
            ["LEARNER_PROFILE", "QUESTION_PROVENANCE", "PRODUCT_INTENT"],
        )
        self.assertEqual(result["requested_outputs"], ["LEARNER_HTML", "QRT_EVIDENCE"])

if __name__ == "__main__":
    unittest.main()
