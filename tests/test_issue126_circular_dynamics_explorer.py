"""Issue #126: circular-dynamics force-role Owner extension."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class CircularDynamicsExplorerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(
            (REPO / "Physics/library/phy-kin-1d-motion.v1.json").read_text(encoding="utf-8")
        )
        cls.matrix = json.loads(
            (REPO / "Physics/matrices/phy-kin-1d-motion.rungs.json").read_text(encoding="utf-8")
        )
        cls.gates = json.loads(
            (REPO / "Physics/gates/foundational-relations.v1.json").read_text(encoding="utf-8")
        )
        cls.audit = (
            REPO / "docs/grade9/G9-1-MOTION-AUTHORING-AUDIT.md"
        ).read_text(encoding="utf-8")
        cls.html = (
            REPO / "public/physics/motion-1d/explorers/circular-dynamics/index.html"
        ).read_text(encoding="utf-8")
        cls.capabilities = {row["id"]: row for row in cls.package["capabilities"]}
        cls.microtopics = {row["id"]: row for row in cls.package["microtopics"]}
        cls.relations = {row["id"]: row for row in cls.package["relations"]}
        cls.resources = {row["id"]: row for row in cls.package["resources"]}
        cls.representations = {row["id"]: row for row in cls.package["representations"]}

    def test_r5_boundary_is_preserved_and_r6_is_nondefault(self):
        r5 = next(row for row in self.matrix["rungs"] if row["rung"] == "R5")
        r6 = next(row for row in self.matrix["rungs"] if row["rung"] == "R6")
        self.assertEqual(
            r5["microtopic_ref"],
            "MIC-PHY-KIN-UNIFORM-CIRCULAR-MOTION",
        )
        self.assertIn("centripetal force formula", r5["ceiling"])
        self.assertNotIn("default_entry_eligible", r5)
        self.assertEqual(
            r6["microtopic_ref"],
            "MIC-PHY-KIN-CIRCULAR-DYNAMICS-ROLE",
        )
        self.assertFalse(r6["default_entry_eligible"])
        self.assertIn("OWNER_EXTENSION", self.audit)
        self.assertIn("R5 retains its `centripetal force formula` ceiling", self.audit)

    def test_r6_composes_ucm_and_newton_second_law(self):
        cap = self.capabilities["CAP-KIN-CIRCULAR-DYNAMICS-ROLE"]
        self.assertEqual(
            cap["prerequisite_refs"],
            ["CAP-KIN-UNIFORM-CIRCULAR-MOTION", "CAP-NLM-SECOND-LAW"],
        )
        micro = self.microtopics["MIC-PHY-KIN-CIRCULAR-DYNAMICS-ROLE"]
        self.assertEqual(
            micro["representation_refs"],
            ["REP-KIN-CIRCULAR-FORCE-ROLE"],
        )
        self.assertIn("ACT-KIN-CIRCULAR-DYNAMICS", self.resources)

    def test_quantitative_relations_are_gate_owned(self):
        gate = next(
            row for row in self.gates["gates"]
            if row["gate_id"] == "PHY-KIN-CIRCULAR-DYNAMICS-EXTENSION"
        )
        self.assertEqual(gate["curriculum"]["scope_class"], "OWNER_EXTENSION")
        self.assertEqual(
            gate["prerequisites"],
            [
                "PHY-KIN-AVERAGE-RATES",
                "PHY-NEWTON-SECOND-LAW",
                "PHY-NLM-CONTACT-CONSTRAINTS",
            ],
        )
        expected = {
            "REL-CIRC-RADIAL-ACCELERATION": "a_r = v^2 / r",
            "REL-CIRC-NET-RADIAL-FORCE": "Sigma F_r = m v^2 / r",
            "REL-CIRC-VERTICAL-TOP": "T + m g = m v_top^2 / r",
            "REL-CIRC-VERTICAL-BOTTOM": "T - m g = m v_bottom^2 / r",
            "REL-CIRC-TOP-MIN-SPEED": "v_min = sqrt(g r)",
        }
        by_id = {row["relation_id"]: row for row in gate["relations"]}
        self.assertEqual({key: by_id[key]["expression"] for key in expected}, expected)
        for relation_id, expression in expected.items():
            self.assertEqual(self.relations[relation_id]["expression"], expression)
            self.assertEqual(
                self.relations[relation_id]["gate_relation_ref"],
                relation_id,
            )

    def test_flat_curve_reuses_static_friction_bound(self):
        gate = next(
            row for row in self.gates["gates"]
            if row["gate_id"] == "PHY-NLM-CONTACT-CONSTRAINTS"
        )
        bound = next(
            row for row in gate["relations"]
            if row["relation_id"] == "REL-NLM-STATIC-FRICTION-BOUND"
        )
        self.assertEqual(bound["expression"], "|f_s| <= mu_s N")
        self.assertIn("|f<sub>s</sub>| ≤ μ<sub>s</sub>N", self.html)
        self.assertIn(
            "Do not write f<sub>s</sub>=μ<sub>s</sub>N automatically",
            self.html,
        )

    def test_no_extra_centripetal_force_arrow(self):
        rep = self.representations["REP-KIN-CIRCULAR-FORCE-ROLE"]
        joined = " ".join(rep["instance_constraints"])
        self.assertIn("No inertial-frame scene may draw an additional physical force arrow", joined)
        self.assertIn(
            "centripetal is the radial resultant role",
            self.html,
        )
        self.assertIn(
            "drawing T inward and another “Fc” inward double-counts",
            self.html,
        )
        self.assertIn(
            "Do not add a second force arrow called Fc",
            self.html,
        )

    def test_velocity_reasoning_precedes_force_model(self):
        self.assertLess(
            self.html.index('id="kinematics"'),
            self.html.index('id="forces"'),
        )
        self.assertIn(
            "Start with motion, not force names",
            self.html,
        )
        self.assertIn(
            "velocity direction changes",
            self.html,
        )

    def test_radial_tangential_axis_toggle_and_scaling_are_live(self):
        self.assertIn('id="axisToggle"', self.html)
        self.assertIn("radial +", self.html)
        self.assertIn("tangent axis", self.html)
        self.assertIn("const ar=V*V/R, req=M*ar", self.html)
        self.assertIn("2v ⇒ 4× force", self.html)

    def test_cut_string_path_is_tangent(self):
        self.assertIn('id="cutButton"', self.html)
        self.assertIn("tension → 0", self.html)
        self.assertIn("instantaneous velocity remains tangent", self.html)
        self.assertIn("initial path: tangent", self.html)
        self.assertNotIn("initial path: radial outward", self.html)

    def test_vertical_circle_signs_and_boundary_are_explicit(self):
        self.assertIn("top: T + mg = m v²/r", self.html)
        self.assertIn("bottom: T - mg = m v²/r", self.html)
        self.assertIn("just-taut top boundary: T = 0", self.html)
        self.assertIn("v_min(top, T=0) = √(gr)", self.html)

    def test_rotating_frame_scope_is_not_silently_added(self):
        lower = self.html.lower()
        self.assertNotIn("centrifugal force", lower)
        self.assertNotIn("coriolis", lower)


if __name__ == "__main__":
    unittest.main()
