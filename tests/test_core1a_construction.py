from __future__ import annotations

import copy
import unittest

from Shared.library import core1a_construction


def fixture() -> tuple[dict, dict, dict, dict]:
    micro = {
        "id": "MIC-TEST",
        "bucket_id": "BUCKET-TEST",
        "intrinsic_badge": "MEDIUM",
        "entry_assumptions": ["Can read the starting representation."],
        "inferential_jump": "The new concept follows from the stated bridge.",
        "teaching_path": [{
            "id": "STEP-1",
            "action": "Connect the representation to the symbolic statement.",
            "why_valid": "The correspondence is declared explicitly.",
        }],
        "relation_refs": ["REL-TEST"],
        "representation_refs": ["REP-TEST"],
        "question_family_refs": ["FAM-TEST"],
        "misconceptions": [{
            "wrong_idea": "Treat the two representations as unrelated.",
            "diagnostic_prompt": "Which visible element corresponds to the symbol?",
            "repair": "Trace the declared correspondence in both directions.",
        }],
        "exit_task": {
            "prompt": "Explain the bridge in your own words.",
            "answer": {
                "summary": "The symbol and visible element represent the same quantity.",
                "check": "Reverse the mapping and recover the original element.",
            },
        },
        "research_contribution": "Research-informed representation bridge.",
    }
    rep = {
        "id": "REP-TEST",
        "scene_instances": [{
            "id": "SCENE-TEST",
            "cores": ["CORE1A"],
            "microtopic_ref": "MIC-TEST",
            "datum_refs": ["DAT-TEST"],
            "scene": {
                "kind": "TEST",
                "frame": "test",
                "caption": "A test bridge.",
            },
        }],
        "correspondence": [{
            "symbol": "x",
            "element": "marked horizontal length",
            "in_words": "the horizontal quantity",
        }],
    }
    relation = {
        "id": "REL-TEST",
        "checks": ["Reverse the mapping and recover the same quantity."],
    }
    question = {
        "id": "Q-TEST",
        "family_ref": "FAM-TEST",
        "exposure": [{"core": "CORE1A", "role": "PLANNED_WORKED_ANCHOR"}],
        "answer": {
            "reasoning": [
                "Read the picture.",
                "Translate the marked element into x.",
                "Check the reverse correspondence.",
            ],
        },
    }
    return micro, rep, relation, question


class Core1AConstructionAudit(unittest.TestCase):
    def row(self, micro=None, rep=None, relation=None, question=None):
        base_micro, base_rep, base_relation, base_question = fixture()
        micro = micro or base_micro
        rep = rep or base_rep
        relation = relation or base_relation
        question = question or base_question
        return core1a_construction.audit_microtopic(
            "Test",
            "Test/library/test.json",
            micro,
            representations={rep["id"]: rep},
            relations={relation["id"]: relation},
            questions=[question],
        )

    def test_complete_fixture_has_no_structural_debt(self):
        row = self.row()
        self.assertEqual(row["finding_codes"], [])
        self.assertEqual(row["representation_bridge_count"], 1)
        self.assertEqual(row["core1a_scene_representation_refs"], ["REP-TEST"])
        self.assertEqual(row["worked_anchor_refs"], ["Q-TEST"])
        self.assertEqual(row["relation_check_refs"], ["REL-TEST"])
        self.assertIn(
            "TEACHING_PATH_ACTUALLY_CONSTRUCTS_INFERENTIAL_JUMP",
            row["manual_review_obligations"],
        )

    def test_missing_crux_and_route_are_named(self):
        micro, rep, relation, question = fixture()
        micro["inferential_jump"] = ""
        micro["teaching_path"] = []
        row = self.row(micro, rep, relation, question)
        self.assertIn("INFERENTIAL_JUMP_MISSING", row["finding_codes"])
        self.assertIn("TEACHING_PATH_MISSING", row["finding_codes"])

    def test_each_teaching_move_must_say_why_it_is_valid(self):
        micro, rep, relation, question = fixture()
        micro["teaching_path"][0]["why_valid"] = ""
        row = self.row(micro, rep, relation, question)
        self.assertIn("TEACHING_STEP_WHY_VALID_MISSING", row["finding_codes"])

    def test_representation_correspondence_is_semantic_not_just_a_ref(self):
        micro, rep, relation, question = fixture()
        rep["correspondence"] = []
        row = self.row(micro, rep, relation, question)
        self.assertIn("REPRESENTATION_CORRESPONDENCE_MISSING", row["finding_codes"])

    def test_representation_must_be_bound_to_this_microtopic_for_core1a(self):
        micro, rep, relation, question = fixture()
        rep["scene_instances"][0]["microtopic_ref"] = "MIC-OTHER"
        row = self.row(micro, rep, relation, question)
        self.assertIn("REPRESENTATION_SCENE_BINDING_MISSING", row["finding_codes"])

    def test_worked_anchor_requires_core1a_exposure_and_full_reasoning(self):
        micro, rep, relation, question = fixture()
        question["answer"]["reasoning"] = []
        row = self.row(micro, rep, relation, question)
        self.assertIn("WORKED_CONCEPTUAL_ANCHOR_MISSING", row["finding_codes"])

    def test_relation_owned_concept_requires_an_independent_relation_check(self):
        micro, rep, relation, question = fixture()
        relation["checks"] = []
        row = self.row(micro, rep, relation, question)
        self.assertIn("RELATION_CHECK_MISSING", row["finding_codes"])

    def test_misconception_diagnostic_repair_is_one_complete_claim(self):
        micro, rep, relation, question = fixture()
        del micro["misconceptions"][0]["repair"]
        row = self.row(micro, rep, relation, question)
        self.assertIn("MISCONCEPTION_REPAIR_INCOMPLETE", row["finding_codes"])

    def test_exit_closure_and_independent_check_are_separate(self):
        micro, rep, relation, question = fixture()
        micro["exit_task"]["answer"]["summary"] = ""
        micro["exit_task"]["answer"]["check"] = ""
        row = self.row(micro, rep, relation, question)
        self.assertIn("EXIT_CLOSURE_MISSING", row["finding_codes"])
        self.assertIn("INDEPENDENT_CHECK_MISSING", row["finding_codes"])

    def test_medium_and_hard_content_retains_research_contribution(self):
        micro, rep, relation, question = fixture()
        micro["research_contribution"] = ""
        row = self.row(micro, rep, relation, question)
        self.assertIn("RESEARCH_CONTRIBUTION_MISSING", row["finding_codes"])

    def test_forward_gate_freezes_legacy_debt_without_accepting_new_debt(self):
        row = self.row()
        report = {"audit": "CORE1A_CONCEPTUAL_CONSTRUCTION", "microtopics": [row]}
        base = core1a_construction.baseline(report)
        self.assertEqual(core1a_construction.forward_findings(report, base), [])

        damaged = copy.deepcopy(row)
        damaged["finding_codes"] = ["TEACHING_PATH_MISSING"]
        findings = core1a_construction.forward_findings({"microtopics": [damaged]}, base)
        self.assertEqual(findings[0]["code"], "TEACHING_PATH_MISSING")

    def test_no_text_length_or_keyword_quality_score_is_created(self):
        row = self.row()
        self.assertNotIn("score", row)
        self.assertNotIn("quality_score", row)


if __name__ == "__main__":
    unittest.main()
