from __future__ import annotations

import copy
import unittest

from Shared.library import compile_inputs, core1b_reconstruction


def fixture() -> dict:
    return {
        "id": "MIC-TEST",
        "title": "A test conceptual decision",
        "bucket_id": "BUCKET-TEST",
        "inferential_jump": "The learner distinguishes the governing case.",
        "teaching_path": [{
            "id": "STEP-1",
            "role": "DECLARE",
            "action": "State the two cases.",
            "why_valid": "The distinction controls the concept.",
            "inputs": [],
            "output": "Two explicit cases.",
        }],
        "misconceptions": [{
            "wrong_idea": "Treat both cases as equivalent.",
            "diagnostic_prompt": "Which observation separates the two cases?",
            "repair": "Return to the deciding observation and classify before calculating.",
        }],
        "elicitation": {
            "predict": {
                "prompt": "Which case applies here, and what observation decides it?",
                "defensible_answer": "Case A applies because the deciding observation is present.",
            },
            "attempt": {
                "produces": "A case choice plus the observation that justifies it.",
                "closure": "MODEL_RESPONSE",
                "model_response": "Case A, because the deciding observation is present.",
            },
            "reconstruct": {
                "route": [{
                    "ask": "What observation changes between the two cases?",
                    "why_this_ask": "The learner must identify the discriminator before naming the case.",
                    "from_step_ref": "STEP-1",
                }],
                "differs_from_teaching_path": "Teaching states both cases first; reconstruction begins from the discriminator.",
            },
            "boundary_test": {
                "prompt": "If the deciding observation is reversed, which case applies?",
                "answer": "Case B.",
                "confirms": "The learner is using the discriminator rather than recalling a label.",
            },
        },
    }


class Core1BReconstructionAudit(unittest.TestCase):
    def row(self, micro=None, *, a=None, b=None):
        return core1b_reconstruction.audit_microtopic(
            "Test",
            "Test/library/test.json",
            micro or fixture(),
            core1a_route_refs=["ROUTE-A"] if a is None else a,
            core1b_route_refs=["ROUTE-B"] if b is None else b,
        )

    def test_complete_cycle_has_no_structural_debt(self):
        row = self.row()
        self.assertEqual(row["finding_codes"], [])
        self.assertTrue(row["coverage_equal"])
        self.assertEqual(row["reconstruct_step_count"], 1)
        self.assertIn(
            "RECONSTRUCTION_GENUINELY_DIFFERS_FROM_TEACHING_PATH",
            row["manual_review_obligations"],
        )

    def test_unrouted_concept_is_phase4_handoff_not_core1b_elicitation_debt(self):
        micro = fixture()
        del micro["elicitation"]
        row = self.row(micro, a=[], b=[])
        self.assertEqual(row["routing_state"], "UNROUTED")
        self.assertEqual(row["finding_codes"], [])
        self.assertEqual(
            row["phase4_handoff_codes"],
            ["CROSS_CORE_ROUTING_UNRESOLVED"],
        )
        self.assertNotIn("ELICITATION_MISSING", row["finding_codes"])

    def test_core1a_coverage_cannot_disappear_from_core1b(self):
        row = self.row(b=[])
        self.assertIn("CORE1B_COVERAGE_MISSING", row["finding_codes"])
        self.assertFalse(row["coverage_equal"])

    def test_core1b_cannot_create_orphan_concept_coverage(self):
        row = self.row(a=[], b=["ROUTE-B"])
        self.assertIn("CORE1B_ORPHAN_COVERAGE", row["finding_codes"])
        self.assertFalse(row["coverage_equal"])

    def test_missing_elicitation_is_named_without_fabricating_fallback_quality(self):
        micro = fixture()
        del micro["elicitation"]
        row = self.row(micro)
        self.assertIn("ELICITATION_MISSING", row["finding_codes"])
        self.assertNotIn("quality_score", row)

    def test_prediction_requires_prompt_and_defensible_answer(self):
        micro = fixture()
        micro["elicitation"]["predict"] = {"prompt": "", "defensible_answer": ""}
        row = self.row(micro)
        self.assertIn("PREDICT_PROMPT_MISSING", row["finding_codes"])
        self.assertIn("PREDICT_DEFENSIBLE_ANSWER_MISSING", row["finding_codes"])

    def test_model_response_closure_requires_model_response(self):
        micro = fixture()
        del micro["elicitation"]["attempt"]["model_response"]
        row = self.row(micro)
        self.assertIn("ATTEMPT_MODEL_RESPONSE_MISSING", row["finding_codes"])

    def test_rubric_closure_requires_criteria_and_accepted_rejected_examples(self):
        micro = fixture()
        micro["elicitation"]["attempt"] = {
            "produces": "An open explanation.",
            "closure": "RUBRIC",
            "rubric": [{
                "criterion": "Names the deciding observation.",
                "evidence_of": "Uses the conceptual discriminator.",
            }],
        }
        row = self.row(micro)
        self.assertIn("ATTEMPT_ACCEPTED_EXAMPLES_MISSING", row["finding_codes"])
        self.assertIn("ATTEMPT_REJECTED_EXAMPLES_MISSING", row["finding_codes"])

    def test_criteria_closure_requires_rubric_but_not_example_pairs(self):
        micro = fixture()
        micro["elicitation"]["attempt"] = {
            "produces": "An explanation.",
            "closure": "CRITERIA",
            "rubric": [{
                "criterion": "Identifies the discriminator.",
                "evidence_of": "Explains why it changes the classification.",
            }],
        }
        row = self.row(micro)
        self.assertNotIn("ATTEMPT_RUBRIC_MISSING", row["finding_codes"])
        self.assertNotIn("ATTEMPT_ACCEPTED_EXAMPLES_MISSING", row["finding_codes"])
        self.assertNotIn("ATTEMPT_REJECTED_EXAMPLES_MISSING", row["finding_codes"])

    def test_reconstruction_step_reference_must_resolve_to_core1a_path(self):
        micro = fixture()
        micro["elicitation"]["reconstruct"]["route"][0]["from_step_ref"] = "STEP-UNKNOWN"
        row = self.row(micro)
        self.assertIn("RECONSTRUCT_STEP_REF_UNKNOWN", row["finding_codes"])

    def test_reconstruction_route_requires_ask_and_rationale(self):
        micro = fixture()
        micro["elicitation"]["reconstruct"]["route"] = [{"ask": "", "why_this_ask": ""}]
        row = self.row(micro)
        self.assertIn("RECONSTRUCT_ASK_MISSING", row["finding_codes"])
        self.assertIn("RECONSTRUCT_RATIONALE_MISSING", row["finding_codes"])

    def test_boundary_test_closes_without_a_tutor(self):
        micro = fixture()
        micro["elicitation"]["boundary_test"] = {"prompt": "", "answer": "", "confirms": ""}
        row = self.row(micro)
        self.assertIn("BOUNDARY_PROMPT_MISSING", row["finding_codes"])
        self.assertIn("BOUNDARY_ANSWER_MISSING", row["finding_codes"])
        self.assertIn("BOUNDARY_CONFIRMATION_MISSING", row["finding_codes"])

    def test_surface_similarity_does_not_certify_or_fail_genuine_reconstruction(self):
        micro = fixture()
        micro["elicitation"]["reconstruct"]["differs_from_teaching_path"] = "Same words."
        row = self.row(micro)
        self.assertNotIn("RECONSTRUCTION_TOO_SIMILAR", row["finding_codes"])
        self.assertIn(
            "RECONSTRUCTION_GENUINELY_DIFFERS_FROM_TEACHING_PATH",
            row["manual_review_obligations"],
        )

    def test_forward_gate_freezes_legacy_debt_without_accepting_new_debt(self):
        row = self.row()
        report = {"audit": "CORE1B_GENUINE_RECONSTRUCTION", "microtopics": [row]}
        base = core1b_reconstruction.baseline(report)
        self.assertEqual(core1b_reconstruction.forward_findings(report, base), [])

        damaged = copy.deepcopy(row)
        damaged["finding_codes"] = ["CORE1B_COVERAGE_MISSING"]
        findings = core1b_reconstruction.forward_findings({"microtopics": [damaged]}, base)
        self.assertEqual(findings[0]["code"], "CORE1B_COVERAGE_MISSING")

    def test_compiler_places_every_reveal_after_the_prompt_it_answers(self):
        micro = fixture()
        blocks = compile_inputs._elicitation_blocks(
            micro,
            "CORE1B",
            "OB-MIC-TEST",
            ["DAT-TEST"],
        )
        positions = {block["id"]: index for index, block in enumerate(blocks)}
        reveal_blocks = [block for block in blocks if block.get("reveals_block_id")]
        self.assertTrue(reveal_blocks)
        for reveal in reveal_blocks:
            self.assertLess(
                positions[reveal["reveals_block_id"]],
                positions[reveal["id"]],
            )


if __name__ == "__main__":
    unittest.main()
