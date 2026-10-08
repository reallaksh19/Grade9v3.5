from __future__ import annotations

import copy
import unittest

from Shared.tools import question_review_matrix as qrt


class DemandMoveBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = qrt.load(qrt.MATRIX_PATH)
        cls.vocab = qrt.load(qrt.VOCAB_PATH)

    def question(self) -> dict:
        return {
            "id": "Q-DEMAND-BINDING",
            "primary_capability_ref": "CAP-A",
            "secondary_capability_refs": [],
            "difficulty": {
                "band": "D2",
                "score": 4,
                "components": {
                    "concept_model_selection": 1,
                    "representation_translation": 0,
                    "reasoning_chain_length": 1,
                    "algebra_computational_load": 1,
                    "trap_exception_sensitivity": 1,
                },
                "basis": "One familiar model, one bridge, routine algebra and one local condition.",
            },
            "extensions": {
                "grade9v3:cognitive_demand": {
                    "primary": "APPLY",
                    "secondary": ["EXPLAIN"],
                    "basis": "The decisive act is executing the known relation after checking its condition.",
                },
                "grade9v3:analysis": {
                    "stable_crux_move": "Choose the valid relation and execute it.",
                    "common_wrong_route": "Apply a familiar relation without checking its condition.",
                },
            },
            "answer": {
                "reasoning_route": [
                    {
                        "id": "MOVE-1",
                        "kind": "DECIDE",
                        "action": "Check whether the stated condition permits the familiar relation.",
                        "why_valid": "The relation is conditional.",
                        "inputs": [],
                        "output": "relation is applicable",
                    },
                    {
                        "id": "MOVE-2",
                        "kind": "TRANSFORM",
                        "action": "Execute the familiar relation with the supplied values.",
                        "why_valid": "The applicability condition has been established.",
                        "inputs": ["relation is applicable"],
                        "output": "requested result",
                    },
                ],
                "crux_move_ref": "MOVE-2",
            },
        }

    def profile(self) -> dict:
        return {
            "profile_id": "PROFILE-DEMAND-BINDING",
            "provenance": "SYNTHETIC_TEST",
            "held": {"CAP-A": "DEMONSTRATED"},
            "knowledge_percentage": 50,
            "measured_fit_claim": False,
        }

    def test_primary_demand_is_bound_to_canonical_crux_move(self):
        result = qrt.resolve_review(self.question(), self.profile(), self.matrix, self.vocab)
        demand = result["classification"]["demand"]
        self.assertEqual(demand["primary"], "APPLY")
        self.assertEqual(demand["primary_move_ref"], "MOVE-2")
        self.assertEqual(demand["primary_move_kind"], "TRANSFORM")
        self.assertEqual(
            demand["primary_move_action"],
            "Execute the familiar relation with the supplied values.",
        )
        self.assertIn("primary_move", result["basis_digests"])

    def test_primary_move_digest_changes_when_the_canonical_crux_move_changes(self):
        one = qrt.resolve_review(self.question(), self.profile(), self.matrix, self.vocab)
        changed = self.question()
        changed["answer"]["reasoning_route"][1]["action"] = (
            "Execute the same relation after mapping each supplied quantity explicitly."
        )
        two = qrt.resolve_review(changed, self.profile(), self.matrix, self.vocab)
        self.assertNotEqual(one["basis_digests"]["primary_move"], two["basis_digests"]["primary_move"])

    def test_floating_demand_without_crux_is_rejected(self):
        question = self.question()
        del question["answer"]["crux_move_ref"]
        with self.assertRaisesRegex(qrt.QRTContractError, "COGNITIVE_DEMAND_CRUX_MOVE_MISSING"):
            qrt.resolve_review(question, self.profile(), self.matrix, self.vocab)

    def test_unresolved_crux_is_rejected(self):
        question = self.question()
        question["answer"]["crux_move_ref"] = "MOVE-DOES-NOT-EXIST"
        with self.assertRaisesRegex(qrt.QRTContractError, "COGNITIVE_DEMAND_CRUX_MOVE_UNRESOLVED"):
            qrt.resolve_review(question, self.profile(), self.matrix, self.vocab)


if __name__ == "__main__":
    unittest.main()
