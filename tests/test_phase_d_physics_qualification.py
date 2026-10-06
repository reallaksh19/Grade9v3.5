from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
PACKAGE = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
MANIFEST = REPO / "products/physics/phy-kin-2d-motion.manifest.json"
WITNESS = "PYQ-PHY-IITJEE-2011-P2-Q33"


class PhaseDPhysicsDemandCruxQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.question = next(q for q in cls.bank["questions"] if q["id"] == WITNESS)

    def test_product_selects_witness_without_overwriting_question_primary_demand(self):
        self.assertIn(WITNESS, self.manifest["selection"]["core2"])
        self.assertEqual(
            self.question["primary_capability_ref"],
            "CAP-KIN-PROJECTILE-MODEL",
        )
        capability = next(
            c for c in self.package["capabilities"]
            if c["id"] == self.question["primary_capability_ref"]
        )
        self.assertIn("projectile", capability["action"].lower())

        microtopic = next(
            m for m in self.package["microtopics"]
            if m["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        )
        self.assertEqual(
            microtopic["primary_capability_ref"],
            self.question["primary_capability_ref"],
        )

    def test_crux_is_bound_to_one_concrete_reasoning_move(self):
        analysis = self.question["extensions"]["grade9v3:analysis"]
        answer = self.question["answer"]
        route = {move["id"]: move for move in answer["reasoning_route"]}

        self.assertEqual(
            analysis["stable_crux_move"],
            "Use the vertical projectile event to get time, then include the train's accelerated displacement in the relative x equation.",
        )
        self.assertEqual(
            answer["crux_move_ref"],
            "PYQ-PHY-IITJEE-2011-P2-Q33-MOVE-2",
        )
        crux = route[answer["crux_move_ref"]]
        self.assertEqual(crux["kind"], "CONNECT")
        self.assertIn("Relative horizontal displacement", crux["action"])
        self.assertIn("accelerating train", crux["action"])
        self.assertEqual(answer["difficult_move"], 1)

    def test_crux_support_targets_the_same_move_reference(self):
        crux_ref = self.question["answer"]["crux_move_ref"]
        supports = [
            row for row in self.question["scaffolds"]
            if row["supports_move_ref"] == crux_ref
        ]
        self.assertEqual(len(supports), 1)
        self.assertEqual(supports[0]["support_kind"], "CONNECT")
        self.assertIn("ball-minus-train horizontal displacement", supports[0]["text"])

    def test_secondary_demand_is_question_owned_not_manifest_owned(self):
        self.assertEqual(
            self.question["secondary_capability_refs"],
            [
                "CAP-KIN-2D-INDEPENDENT-COMPONENTS",
                "CAP-KIN-2D-CONSTANT-ACCELERATION",
            ],
        )
        self.assertNotIn("primary_capability_ref", self.manifest["selection"])
        self.assertNotIn("secondary_capability_refs", self.manifest["selection"])


if __name__ == "__main__":
    unittest.main()
