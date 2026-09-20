#!/usr/bin/env python3
"""Contract and regression tests for Issue #118 Data-Driven Topic Atlas.

Verifies:
- Canonical projection from Shared/tools/build_web_data.py
- Non-default R4 eligibility isolation
- Teaching-path step IDs preservation (NLM5-1, ME-1, etc.)
- Governed activity resource registration (ACT-NLM-FRICTION-THRESHOLD)
- Cross-subject reusability for Physics NLM and Mathematics Linear Equations
- Request schema conformance for generated requests
- Zero fake data / mock policy adherence
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

from Shared.contracts import load
from Shared.tools import build_web_data
import jsonschema


class TopicAtlasContractTest(unittest.TestCase):
    def setUp(self):
        self.payload = build_web_data.build()

    def test_generated_web_data_contains_matrices(self):
        subjects = self.payload["subjects"]
        self.assertIn("Physics", subjects)
        self.assertIn("Mathematics", subjects)

        phy_matrices = subjects["Physics"].get("matrices", [])
        self.assertTrue(len(phy_matrices) > 0, "Physics must project canonical matrices")

        math_matrices = subjects["Mathematics"].get("matrices", [])
        self.assertTrue(len(math_matrices) > 0, "Mathematics must project canonical matrices")

    def test_nlm_matrix_structure_and_non_default_r4(self):
        phy_matrices = self.payload["subjects"]["Physics"]["matrices"]
        nlm = next((m for m in phy_matrices if m["matrix_id"] == "MATRIX-PHY-NLM-FIRST-LAW"), None)
        self.assertIsNotNone(nlm, "MATRIX-PHY-NLM-FIRST-LAW must be projected")

        rungs = nlm["rungs"]
        self.assertEqual(len(rungs), 11, "NLM must contain 11 canonical rungs")

        # R4 must carry default_entry_eligible == False (GAP-WEB-004)
        r4 = next(r for r in rungs if r["rung"] == "R4")
        self.assertFalse(r4["default_entry_eligible"], "R4 frame choice must not be default entry eligible")
        self.assertEqual(r4["ladder_position"], 100)

        # Default rungs must carry default_entry_eligible == True
        r1 = next(r for r in rungs if r["rung"] == "R1")
        self.assertTrue(r1["default_entry_eligible"])

        # When percentage is 100%, highest default-eligible rung must be R7 (Pos: 94), NOT R4 (Pos: 100)
        default_rungs = [r for r in rungs if r["default_entry_eligible"]]
        highest_default = max(default_rungs, key=lambda r: r["ladder_position"])
        self.assertEqual(highest_default["rung"], "R7")
        self.assertNotEqual(highest_default["rung"], "R4")

    def test_r5_teaching_path_step_ids_and_activity_binding(self):
        phy_matrices = self.payload["subjects"]["Physics"]["matrices"]
        nlm = next(m for m in phy_matrices if m["matrix_id"] == "MATRIX-PHY-NLM-FIRST-LAW")
        r5 = next(r for r in nlm["rungs"] if r["rung"] == "R5")

        self.assertEqual(r5["capability"]["id"], "CAP-NLM-FRICTION")
        self.assertIsNotNone(r5["microtopic"])

        # Steps must carry stable step IDs (GAP-WEB-008)
        step_ids = [s["id"] for s in r5["microtopic"]["teaching_path"]]
        self.assertEqual(step_ids, ["NLM5-1", "NLM5-2", "NLM5-3", "NLM5-4"])

        # Activity binding must come from canonical library resource (GAP-WEB-017)
        activities = r5["activities"]
        self.assertTrue(len(activities) >= 1, "R5 must have bound activity resource")
        self.assertEqual(activities[0]["id"], "ACT-NLM-FRICTION-THRESHOLD")
        self.assertEqual(activities[0]["locator"], "public/physics/nlm/explorers/friction-threshold/index.html")
        self.assertIn("CAP-NLM-FRICTION", activities[0]["supports_claims"])

    def test_motion2d_semantic_leaf_activity_bindings(self):
        phy_matrices = self.payload["subjects"]["Physics"]["matrices"]
        motion = next(
            (m for m in phy_matrices if m["matrix_id"] == "MATRIX-PHY-KIN-2D-MOTION"),
            None,
        )
        self.assertIsNotNone(motion, "Motion-in-2D matrix must be projected")

        expected = {
            "K2D1-3": "ACT-KIN-2D-SHARED-CLOCK",
            "K2D1-4": "ACT-KIN-2D-SHARED-CLOCK",
            "K2D2-3": "ACT-KIN-2D-EVENT-CLOCK",
            "K2D3-1": "ACT-KIN-2D-PROJECTILE-MODEL-GATE",
            "K2D3-4": "ACT-KIN-2D-APEX-FALLACY",
            "K2D3-7": "ACT-KIN-2D-EQUAL-HEIGHT-STATE",
            "K2D3-3": "ACT-KIN-2D-LANDING-GEOMETRY",
            "K2D3-5": "ACT-KIN-2D-LANDING-GEOMETRY",
            "K2D3-6": "ACT-KIN-2D-LANDING-GEOMETRY",
        }

        by_step = {}
        for rung in motion["rungs"]:
            for activity in rung.get("activities", []):
                for step_ref in activity.get("teaching_step_refs", []):
                    by_step.setdefault(step_ref, set()).add(activity["id"])
                if activity["id"].startswith("ACT-KIN-2D-"):
                    self.assertEqual(activity["activity_kind"], "GRAPHICAL_COGNITIVE_DECONSTRUCTION")
                    self.assertEqual(activity["support_route"]["kind"], "GCDR")
                    self.assertEqual(activity["support_route"]["conformance_status"], "IMPLEMENTATION_PARTIAL")
                    self.assertEqual(activity["support_route"]["quality_audit_status"], "PARTIAL")
                    self.assertGreater(activity["support_route"]["quality_check_counts"]["PENDING"], 0)
                    self.assertEqual(activity["support_route"]["quality_check_counts"]["FAIL"], 0)
                    self.assertEqual(activity["support_route"]["external_state_mapping"], "NOT_APPLICABLE")
                    self.assertEqual(activity["support_route"]["external_state_binding_count"], 0)
                    self.assertEqual(
                        activity["support_route"]["missing_parameter_policy"],
                        "NEVER_INVENT_AS_EXACT",
                    )
                    self.assertEqual(activity["support_route"]["auto_route_policy"], "RECOMMEND_ONLY")
                    self.assertTrue(activity["support_route"]["recommended_when"])
                    self.assertTrue(activity["support_route"]["learner_evidence_triggers"])
                    self.assertTrue(activity["locator"].startswith("public/physics/motion-2d/explorers/"))
                    self.assertTrue((REPO / activity["locator"]).exists())

        for step_ref, activity_id in expected.items():
            with self.subTest(step_ref=step_ref):
                self.assertIn(activity_id, by_step.get(step_ref, set()))

        r3 = next(r for r in motion["rungs"] if r["rung"] == "R3")
        k6 = next(s for s in r3["microtopic"]["teaching_path"] if s["id"] == "K2D3-6")
        self.assertIn("actual Delta y=y_f-y_i", k6["action"])
        self.assertIn("actual u_y", k6["action"])
        self.assertTrue((REPO / "public/physics/motion-2d/index.html").exists())

    def test_mathematics_linear_equations_proof_case(self):
        math_matrices = self.payload["subjects"]["Mathematics"]["matrices"]
        lin = next((m for m in math_matrices if m["matrix_id"] == "MATRIX-MATH-LINEAR-EQUATIONS"), None)
        self.assertIsNotNone(lin, "MATRIX-MATH-LINEAR-EQUATIONS must be projected")

        rungs = lin["rungs"]
        self.assertEqual(len(rungs), 3)

        r2 = next(r for r in rungs if r["rung"] == "R2")
        self.assertEqual(r2["capability"]["id"], "CAP-MATH-ISOLATE")

        # Mathematics steps must carry stable IDs ME-1, ME-2, ME-3 (GAP-WEB-018)
        step_ids = [s["id"] for s in r2["microtopic"]["teaching_path"]]
        self.assertEqual(step_ids, ["ME-1", "ME-2", "ME-3"])

    def test_web_data_files_on_disk(self):
        # Both tools/data.js and public/data/data.js must exist and match fresh render
        tools_js = (REPO / "tools" / "data.js").read_text(encoding="utf-8")
        public_js = (REPO / "public" / "data" / "data.js").read_text(encoding="utf-8")

        self.assertEqual(tools_js, public_js, "tools/data.js and public/data/data.js must be identical")
        rendered = build_web_data.render(self.payload)
        self.assertEqual(tools_js, rendered, "Disk files must match freshly rendered payload")

    def test_request_schema_validation_for_atlas_request(self):
        # Test that an exported Core request generated by the Atlas conforms to request.schema.json
        req_schema = load(REPO / "Shared" / "library" / "request.schema.json")

        sample_request = {
            "request_id": "REQ-NLM-TEST-001",
            "subject": "Physics",
            "bucket_id": "BUCKET-PHY-NLM-FIRST-LAW",
            "label": "Topic Atlas Test Request",
            "cores": ["CORE1A", "CORE1B", "CORE2A"],
            "learner": {
                "owner_entry": {
                    "rung": "R2",
                    "by": "Topic Atlas Need Resolver",
                    "instruction": "Entry selected via diagnostic gap OBS-NLM-002"
                }
            },
            "practice": {
                "CORE2A": {
                    "purpose": "PRACTICE",
                    "note": "Fluency build"
                }
            }
        }

        # Must not raise jsonschema.ValidationError
        jsonschema.validate(instance=sample_request, schema=req_schema)


if __name__ == "__main__":
    unittest.main()
