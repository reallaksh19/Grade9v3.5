from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools import objective_review as review  # noqa: E402


class ObjectiveReviewMatrix(unittest.TestCase):
    def test_matrix_is_exactly_four_by_seven(self):
        self.assertEqual(review.problems(), [])
        rows = review.load(review.MATRIX_FILE)["cells"]
        self.assertEqual(len(rows), 28)
        self.assertEqual(
            {(row["difficulty_band"], row["demand_family"]) for row in rows},
            {(band, demand) for band in review.BANDS for demand in review.DEMANDS},
        )

    def test_every_cell_resolves_to_agent_ready_hspm_policy(self):
        for band in review.BANDS:
            for demand in review.DEMANDS:
                policy = review.resolve(band, demand)
                self.assertEqual(policy["template_id"], f"QRT-{band}-{demand}")
                self.assertEqual(set(policy["slots"]), {"X", "Y", "Z", "W"})
                self.assertEqual(policy["attempt_first"]["protected_slot"], "W")
                self.assertEqual(policy["hint_objectives"]["REPRESENTATION"]["review_id"], "H1")
                self.assertEqual(policy["hint_objectives"]["KEY_CONCEPT"]["review_id"], "H2")
                self.assertEqual(policy["hint_objectives"]["CRUX"]["review_id"], "H3")
                self.assertEqual(set(policy["figure_policy"]["stage_objectives"]), {"S1", "S2", "S3"})
                self.assertEqual(set(policy["helper_policy"]), {"P1", "P2", "P3"})
                self.assertTrue(all(key in policy["misconception_policy"] for key in ("M1", "M2", "M3")))

    def test_difficulty_changes_posture_not_demand_identity(self):
        direct = review.resolve("D1", "MOD")
        transfer = review.resolve("D4", "MOD")
        self.assertEqual(direct["objective"], transfer["objective"])
        self.assertNotEqual(direct["difficulty_character"], transfer["difficulty_character"])
        self.assertNotEqual(direct["slots"]["W"], transfer["slots"]["W"])

    def test_demand_changes_cognitive_job_at_same_band(self):
        model = review.resolve("D3", "MOD")
        proof = review.resolve("D3", "PRF")
        self.assertNotEqual(model["objective"], proof["objective"])
        self.assertNotEqual(model["hint_objectives"]["CRUX"]["objective"], proof["hint_objectives"]["CRUX"]["objective"])

    def test_subject_overlays_cover_same_seven_demands(self):
        for subject, path in review.OVERLAYS.items():
            overlay = review.load(path)
            self.assertEqual(overlay["subject"], subject)
            self.assertEqual(set(overlay["demand_overlays"]), set(review.DEMANDS))
            self.assertNotIn("cells", overlay)

    def test_subject_packet_keeps_same_matrix_cell(self):
        packet = review.packet("D3", "MOD", "Physics")
        self.assertEqual(packet["template_ref"], "QRT-D3-MOD")
        self.assertEqual(packet["subject"], "Physics")
        self.assertIn("system or boundary choice", packet["subject_overlay"]["manifestations"])
        self.assertTrue(packet["matrix_digest"].startswith("sha256:"))


class ProtectedW(unittest.TestCase):
    def record(self):
        return {
            "schema_version": "1.0.0",
            "question_id": "Q-TEST-1",
            "difficulty_band": "D3",
            "primary_demand": "MOD",
            "secondary_demands": ["REP"],
            "matrix_template_ref": "QRT-D3-MOD",
            "slots": {
                "X": "which event condition controls the model",
                "Y": "one shared clock",
                "Z": "write the two event conditions",
                "W": {"description": "eliminate the extra unknown", "protected_move_ref": "Q-TEST-1-MOVE-3"},
            },
            "hint_bindings": [
                {"stage": "REPRESENTATION", "objective_ref": "QRT-D3-MOD#REPRESENTATION", "supports_move_ref": "Q-TEST-1-MOVE-1"},
                {"stage": "KEY_CONCEPT", "objective_ref": "QRT-D3-MOD#KEY_CONCEPT", "supports_move_ref": "Q-TEST-1-MOVE-2"},
                {"stage": "CRUX", "objective_ref": "QRT-D3-MOD#CRUX", "supports_move_ref": None},
            ],
            "figure": {"applicability": "CONDITIONAL", "reason": "event geometry helps", "representation_ref": "REP-TEST-1", "reveals_move_refs": []},
            "pre_attempt": {"move_refs_revealed": []},
            "concept_navigation": {"core1a_refs": ["MIC-TEST"]},
            "misconceptions": [],
            "validation_strategy_refs": ["ASSUMPTION_CHECK"],
            "core1a_extraction": {
                "canonical_refs": ["CAP-TEST"],
                "evidence_question_ids": ["Q-TEST-1"],
                "prerequisite_refs": [],
                "target_concept_ref": "MIC-TEST",
                "inferential_leaps": ["event condition before algebra"],
                "misconception_ids": [],
                "representation_refs": ["REP-TEST-1"],
                "model_boundaries": ["same model assumptions"],
                "transfer_conditions": [],
            },
        }

    def test_clean_binding_does_not_hand_w_over(self):
        self.assertEqual(review.question_pedagogy_problems(self.record()), [])

    def test_hint_cannot_support_protected_w(self):
        bad = self.record()
        bad["hint_bindings"][2]["supports_move_ref"] = "Q-TEST-1-MOVE-3"
        self.assertTrue(any(item.startswith("W_LEAK") for item in review.question_pedagogy_problems(bad)))

    def test_safe_figure_and_pre_attempt_panels_cannot_declare_w(self):
        for lane, key in (("figure", "reveals_move_refs"), ("pre_attempt", "move_refs_revealed")):
            bad = self.record()
            bad[lane][key] = ["Q-TEST-1-MOVE-3"]
            self.assertTrue(any(item.startswith("W_LEAK") for item in review.question_pedagogy_problems(bad)), lane)


class Schemas(unittest.TestCase):
    def test_new_schemas_are_valid_draft_2020_12(self):
        from jsonschema import Draft202012Validator
        for name in ("question-demand-matrix.schema.json", "question-pedagogy.schema.json", "concept-evidence.schema.json", "review-instance.schema.json"):
            Draft202012Validator.check_schema(review.load(review.ROOT / name))


if __name__ == "__main__":
    unittest.main()
