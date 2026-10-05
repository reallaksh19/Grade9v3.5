from __future__ import annotations

import unittest

from Shared.tools import authoring_intake as intake


class AuthoringIntakeTests(unittest.TestCase):
    def base_intake(self):
        return {
            "schema": "minimal-authoring-intake/v1",
            "subject": "Mathematics",
            "grade": 9,
            "topic": "Surface Areas and Volumes",
            "questions": [
                {"id": f"Q{i}", "stem": f"Grade 9 surface-area/volume question number {i}."}
                for i in range(1, 11)
            ],
        }

    def capabilities(self):
        return {
            "capabilities": [
                {
                    "id": "CAP-MAT-SAV-CIRCLE",
                    "label": "circle circumference and area",
                    "reason": "Needed for cylinder, cone, sphere and hemisphere questions.",
                },
                {
                    "id": "CAP-MAT-SAV-EXPOSED",
                    "label": "identify exposed versus hidden surfaces",
                    "reason": "Needed for open and composite solids.",
                },
                {
                    "id": "CAP-MAT-SAV-UNITS",
                    "label": "area/volume units and litre conversion",
                    "reason": "Needed for unit conversion and capacity questions.",
                },
            ]
        }

    def test_minimal_prompt_first_requires_agent_capability_scan_not_owner_taxonomy_work(self):
        result = intake.clarification_plan(self.base_intake(), None)
        self.assertEqual(result["status"], "CLARIFICATION_REQUIRED")
        ids = [row["id"] for row in result["owner_questions"]]
        self.assertEqual(ids, ["PURPOSE"])
        self.assertIn("SCAN_RELEVANT_LEARNER_CAPABILITIES", [row["id"] for row in result["agent_actions"]])
        forbidden = " ".join(result["do_not_ask_owner_for"])
        self.assertIn("D1-D4", forbidden)
        self.assertIn("cognitive demand", forbidden)
        self.assertIn("QRT template", forbidden)

    def test_after_agent_scan_owner_is_asked_only_for_missing_learner_knowledge_and_purpose(self):
        result = intake.clarification_plan(self.base_intake(), self.capabilities())
        self.assertEqual(result["status"], "CLARIFICATION_REQUIRED")
        ids = [row["id"] for row in result["owner_questions"]]
        self.assertEqual(ids, ["PURPOSE", "LEARNER_KNOWLEDGE"])
        knowledge = result["owner_questions"][1]
        self.assertEqual(len(knowledge["items"]), 3)
        self.assertEqual(knowledge["allowed"], list(intake.KNOWLEDGE))

    def test_known_owner_facts_are_not_asked_again(self):
        source = self.base_intake()
        source["purpose"] = "COMPETITION"
        source["learner"] = {
            "knowledge": {
                "CAP-MAT-SAV-CIRCLE": "DEMONSTRATED",
                "CAP-MAT-SAV-EXPOSED": "UNCERTAIN",
                "CAP-MAT-SAV-UNITS": "MISSING",
            }
        }
        result = intake.clarification_plan(source, self.capabilities())
        self.assertEqual(result["status"], "READY_FOR_PERSONALIZED_QRT")
        self.assertEqual(result["owner_questions"], [])

    def test_partial_knowledge_asks_only_for_missing_items(self):
        source = self.base_intake()
        source["purpose"] = "PRACTICE"
        source["learner"] = {
            "knowledge": {"CAP-MAT-SAV-CIRCLE": "DEMONSTRATED"}
        }
        result = intake.clarification_plan(source, self.capabilities())
        self.assertEqual(result["status"], "CLARIFICATION_REQUIRED")
        self.assertEqual([row["id"] for row in result["owner_questions"]], ["LEARNER_KNOWLEDGE"])
        asked = [row["id"] for row in result["owner_questions"][0]["items"]]
        self.assertEqual(asked, ["CAP-MAT-SAV-EXPOSED", "CAP-MAT-SAV-UNITS"])

    def test_profile_materialization_bridges_to_existing_qrt_resolver_contract(self):
        source = self.base_intake()
        source["purpose"] = "COMPETITION"
        source["learner"] = {
            "profile_ref": "PROFILE-OWNER-SAV",
            "knowledge": {
                "CAP-MAT-SAV-CIRCLE": "DEMONSTRATED",
                "CAP-MAT-SAV-EXPOSED": "UNCERTAIN",
                "CAP-MAT-SAV-UNITS": "MISSING",
            },
        }
        profile = intake.materialize_profile(source, self.capabilities())
        self.assertEqual(profile["profile_id"], "PROFILE-OWNER-SAV")
        self.assertEqual(profile["provenance"], "OWNER_ESTIMATE")
        self.assertIn("actual owner events", profile["provenance_note"])
        self.assertEqual(profile["knowledge_percentage"], None)
        self.assertFalse(profile["measured_fit_claim"])
        self.assertEqual(profile["held"]["CAP-MAT-SAV-EXPOSED"], "UNCERTAIN")

    def test_no_profile_is_fabricated_when_clarification_is_missing(self):
        source = self.base_intake()
        with self.assertRaisesRegex(intake.IntakeError, "PROFILE_NOT_READY"):
            intake.materialize_profile(source, self.capabilities())

    def test_owner_supplied_questions_use_agent_custody_interpretation_not_fake_owner_reply(self):
        result = intake.clarification_plan(self.base_intake(), self.capabilities())
        source_default = result["source_default"]
        self.assertEqual(source_default["status"], "OWNER_SUPPLIED")
        self.assertEqual(source_default["provenance_kind"], "AGENT_CUSTODY_INTERPRETATION")
        self.assertIn("not an owner clarification reply", source_default["basis"])
        self.assertNotIn("SOURCE", [row["id"] for row in result["owner_questions"]])


if __name__ == "__main__":
    unittest.main()
