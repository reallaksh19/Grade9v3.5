"""Issue #125: accelerated-frame / elevator explicit-demand extension."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class AcceleratedFrameExplorerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(
            (REPO / "Physics/library/phy-nlm-first-law.v1.json").read_text(encoding="utf-8")
        )
        cls.matrix = json.loads(
            (REPO / "Physics/matrices/phy-nlm-first-law.rungs.json").read_text(encoding="utf-8")
        )
        cls.gates = json.loads(
            (REPO / "Physics/gates/foundational-relations.v1.json").read_text(encoding="utf-8")
        )
        cls.html = (
            REPO / "public/physics/nlm/explorers/accelerated-frames/index.html"
        ).read_text(encoding="utf-8")
        cls.relations = {row["id"]: row for row in cls.package["relations"]}
        cls.resources = {row["id"]: row for row in cls.package["resources"]}
        cls.representations = {row["id"]: row for row in cls.package["representations"]}
        cls.microtopics = {row["id"]: row for row in cls.package["microtopics"]}

    def test_r4_remains_nondefault_explicit_demand_extension(self):
        rung = next(row for row in self.matrix["rungs"] if row["rung"] == "R4")
        self.assertEqual(rung["microtopic_ref"], "MIC-PHY-NLM-FRAME-CHOICE")
        self.assertFalse(rung["default_entry_eligible"])
        resource = self.resources["ACT-NLM-ACCELERATED-FRAMES"]
        self.assertEqual(
            resource["extensions"]["issue125:scope_class"],
            "QUESTION_DEMAND_EXTENSION",
        )
        self.assertEqual(resource["depth"], ["ADVANCED"])

    def test_quantitative_relations_are_gate_owned(self):
        gate = next(
            row for row in self.gates["gates"]
            if row["gate_id"] == "PHY-NLM-ACCELERATING-FRAME-EXTENSION"
        )
        self.assertEqual(gate["curriculum"]["scope_class"], "OWNER_EXTENSION")
        by_id = {row["relation_id"]: row for row in gate["relations"]}
        expected = {
            "REL-NLM-ELEVATOR-SUPPORT": "N - m g = m a_y",
            "REL-NLM-PSEUDO-FORCE": "F_pseudo = -m a_frame",
            "REL-NLM-HANGING-BOB-TILT": "tan(theta) = |a_frame| / g",
        }
        self.assertEqual({k: by_id[k]["expression"] for k in expected}, expected)
        for relation_id, expression in expected.items():
            row = self.relations[relation_id]
            self.assertEqual(row["gate_relation_ref"], relation_id)
            self.assertEqual(row["expression"], expression)

    def test_microtopic_and_resource_bind_one_canonical_representation(self):
        micro = self.microtopics["MIC-PHY-NLM-FRAME-CHOICE"]
        self.assertEqual(
            micro["representation_refs"],
            ["REP-NLM-ACCELERATING-FRAME-COMPARISON"],
        )
        for relation_id in (
            "REL-NLM-ELEVATOR-SUPPORT",
            "REL-NLM-PSEUDO-FORCE",
            "REL-NLM-HANGING-BOB-TILT",
        ):
            self.assertIn(relation_id, micro["relation_refs"])
        rep = self.representations["REP-NLM-ACCELERATING-FRAME-COMPARISON"]
        self.assertEqual(
            rep["interactive_resource_refs"],
            ["ACT-NLM-ACCELERATED-FRAMES"],
        )
        self.assertIn("REL-NLM-PSEUDO-FORCE", rep["relation_refs"])

    def test_inertial_and_accelerating_frame_equations_stay_separate(self):
        self.assertIn("N - m g = m a<sub>y</sub>", self.html)
        self.assertIn("F<sub>pseudo</sub> = -m a<sub>frame</sub>", self.html)
        self.assertIn("N - mg - m a<sub>frame</sub> = 0", self.html)
        self.assertIn("Physical forces only", self.html)
        self.assertIn("Same physical interactions + frame term", self.html)

    def test_velocity_and_acceleration_are_independent_controls(self):
        self.assertIn('id="velocity"', self.html)
        self.assertIn('id="accel"', self.html)
        self.assertIn(
            "scale reading depends on acceleration, not on whether the elevator is moving up or down",
            self.html,
        )

    def test_free_fall_keeps_gravity_and_zeroes_support(self):
        self.assertIn('data-a="-9.81"', self.html)
        self.assertIn(
            "Free fall: N = 0. Gravity has not vanished",
            self.html,
        )
        self.assertIn(
            "N = 0 while mg remains nonzero",
            self.html,
        )

    def test_pseudo_force_direction_follows_frame_acceleration(self):
        self.assertIn("const pseudo=-m*a", self.html)
        self.assertIn("const pseudoDir=a>0?'downward':a<0?'upward':'zero'", self.html)
        self.assertIn(
            "pseudo-force is a frame-dependent inertial term, not a Newton-III partner",
            self.html,
        )

    def test_hanging_bob_transfer_is_bounded_and_quantitative(self):
        self.assertIn("tan(θ) = |a<sub>frame</sub>| / g", self.html)
        self.assertIn("Math.atan(ha/G)", self.html)
        self.assertIn("The bob tilts opposite the vehicle acceleration", self.html)

    def test_no_circular_motion_scope_leak(self):
        lower = self.html.lower()
        self.assertNotIn("centripetal", lower)
        self.assertNotIn("banked", lower)


if __name__ == "__main__":
    unittest.main()
