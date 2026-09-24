from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Shared.library import core1_progression
from Shared.library.compile_inputs import compile_bucket
from Shared.library.resolve import build_index


REPO = Path(__file__).resolve().parents[1]


def microtopic_fixture() -> dict:
    return {
        "id": "MIC-TEST",
        "bucket_id": "BUCKET-TEST",
        "intrinsic_badge": "HARD",
        "inferential_jump": "A single canonical conceptual inference.",
        "representation_refs": ["REP-TEST"],
    }


def orientation_fixture() -> dict:
    return {
        "core1_compilable": True,
        "orientation_surfaces": ["HARD_TRANSITION_POINTERS"],
        "hard_transitions": [{
            "microtopic_ref": "MIC-TEST",
            "intrinsic_badge": "HARD",
            "badge_reason": "The concept contains a real decision.",
        }],
        "finding_codes": [],
    }


def construction_fixture() -> dict:
    return {"finding_codes": []}


def reconstruction_fixture() -> dict:
    return {
        "routing_state": "A_AND_B",
        "core1a_route_refs": ["ROUTE-A"],
        "core1b_route_refs": ["ROUTE-B"],
        "finding_codes": [],
    }


class CrossCore1Progression(unittest.TestCase):
    def row(self, micro=None, orientation=None, construction=None, reconstruction=None):
        return core1_progression.progression_row(
            micro or microtopic_fixture(),
            subject="Test",
            orientation=orientation if orientation is not None else orientation_fixture(),
            construction=construction if construction is not None else construction_fixture(),
            reconstruction=reconstruction if reconstruction is not None else reconstruction_fixture(),
        )

    def test_complete_map_construct_reconstruct_row_is_cross_coherent(self):
        row = self.row()
        self.assertTrue(row["cross_progression_coherent"])
        self.assertEqual(row["cross_progression_codes"], [])
        self.assertEqual(row["depth_authority"], "CANONICAL_MICROTOPIC")
        self.assertEqual(
            row["representation_authority"],
            "SHARED_CANONICAL_MICROTOPIC_REFS",
        )

    def test_routed_study_concept_requires_a_core1_map(self):
        orientation = orientation_fixture()
        orientation["core1_compilable"] = False
        orientation["orientation_surfaces"] = []
        row = self.row(orientation=orientation)
        self.assertIn(
            "CORE1_ORIENTATION_UNAVAILABLE_FOR_STUDY",
            row["cross_progression_codes"],
        )

    def test_unrouted_concept_is_a_cross_progression_gap(self):
        reconstruction = reconstruction_fixture()
        reconstruction.update({
            "routing_state": "UNROUTED",
            "core1a_route_refs": [],
            "core1b_route_refs": [],
        })
        row = self.row(reconstruction=reconstruction)
        self.assertIn(
            "CROSS_CORE_ROUTING_UNRESOLVED",
            row["cross_progression_codes"],
        )

    def test_a_b_route_asymmetry_is_cross_progression_drift(self):
        reconstruction = reconstruction_fixture()
        reconstruction.update({
            "routing_state": "CORE1A_ONLY",
            "core1b_route_refs": [],
        })
        row = self.row(reconstruction=reconstruction)
        self.assertIn(
            "CROSS_CORE_ROUTE_COVERAGE_MISMATCH",
            row["cross_progression_codes"],
        )

    def test_hard_concept_must_be_named_in_core1_orientation(self):
        orientation = orientation_fixture()
        orientation["hard_transitions"] = []
        row = self.row(orientation=orientation)
        self.assertIn("CORE1_HARD_POINTER_MISSING", row["cross_progression_codes"])

    def test_canonical_inferential_jump_is_single_cross_product_crux(self):
        micro = microtopic_fixture()
        micro["inferential_jump"] = ""
        row = self.row(micro=micro)
        self.assertIn(
            "CANONICAL_INFERENTIAL_JUMP_MISSING",
            row["cross_progression_codes"],
        )

    def test_local_phase2_debt_is_reported_but_not_relabelled_cross_drift(self):
        construction = {"finding_codes": ["WORKED_CONCEPTUAL_ANCHOR_MISSING"]}
        row = self.row(construction=construction)
        self.assertTrue(row["cross_progression_coherent"])
        self.assertEqual(
            row["phase2_construction_debt"],
            ["WORKED_CONCEPTUAL_ANCHOR_MISSING"],
        )

    def test_forward_gate_freezes_only_cross_progression_debt(self):
        clean = self.row()
        report = {
            "audit": "CORE1_CROSS_PROGRESSION",
            "route_findings": [],
            "microtopics": [clean],
        }
        base = core1_progression.baseline(report)
        self.assertEqual(core1_progression.forward_findings(report, base), [])

        damaged = copy.deepcopy(clean)
        damaged["cross_progression_codes"] = ["CORE1_ORIENTATION_UNAVAILABLE_FOR_STUDY"]
        findings = core1_progression.forward_findings(
            {**report, "microtopics": [damaged]},
            base,
        )
        self.assertEqual(
            findings[0]["code"],
            "CORE1_ORIENTATION_UNAVAILABLE_FOR_STUDY",
        )

    def test_real_relationless_bucket_now_compiles_a_core1_map(self):
        packages = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((REPO / "Physics/library").glob("*.json"))
        ]
        compiled = compile_bucket(
            build_index(packages),
            "BUCKET-PHY-ELEC-CURRENT-OHM",
            topic_id="PHY-ELEC-G9",
            title="Current electricity orientation",
            subject="Physics",
            practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
        )
        self.assertIn("CORE1", compiled["baseline"]["selected_cores"])
        core1 = next(
            product for product in compiled["plan"]["products"]
            if product["core"] == "CORE1"
        )
        blocks = core1["units"][0]["blocks"]
        self.assertTrue(
            any(block["id"] == "CORE1-DEMAND" for block in blocks),
            "A relationless bucket still has canonical hard-transition map content.",
        )


if __name__ == "__main__":
    unittest.main()
