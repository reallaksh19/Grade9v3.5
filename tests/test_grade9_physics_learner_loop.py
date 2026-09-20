import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LIBS = {
    "MATRIX-PHY-GRAV-UNIVERSAL-LAW": ROOT / "Physics/library/phy-grav-universal-law.v1.json",
    "MATRIX-PHY-WORK-ENERGY-POWER": ROOT / "Physics/library/phy-work-energy-power.v1.json",
    "MATRIX-PHY-SOUND": ROOT / "Physics/library/phy-sound.v1.json",
    "MATRIX-PHY-SIMPLE-MACHINES": ROOT / "Physics/library/phy-simple-machines.v1.json",
}
MATRICES = {
    "MATRIX-PHY-GRAV-UNIVERSAL-LAW": ROOT / "Physics/matrices/phy-grav-universal-law.rungs.json",
    "MATRIX-PHY-WORK-ENERGY-POWER": ROOT / "Physics/matrices/phy-work-energy-power.rungs.json",
    "MATRIX-PHY-SOUND": ROOT / "Physics/matrices/phy-sound.rungs.json",
    "MATRIX-PHY-SIMPLE-MACHINES": ROOT / "Physics/matrices/phy-simple-machines.rungs.json",
}
DIRECT_GAPS = {
    "CAP-PHY-GRAV-INVERSE-SQUARE",
    "CAP-PHY-GRAV-FREE-FALL-G",
    "CAP-PHY-GRAV-MASS-WEIGHT",
    "CAP-WEP-MECH-ENERGY-CONDITION",
    "CAP-SOUND-REFLECTION",
    "CAP-MACHINE-TRADEOFF",
    "CAP-MACHINE-COMPARE",
}
EXPECTED_TRANSFER_KEYS = {
    "MATRIX-PHY-GRAV-UNIVERSAL-LAW": {0, 1, 2, 3},
    "MATRIX-PHY-WORK-ENERGY-POWER": {0, 1, 2, 3, 4, 5},
    "MATRIX-PHY-SOUND": {0, 1, 2, 3, 4},
    "MATRIX-PHY-SIMPLE-MACHINES": {0, 1, 2},
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class Grade9PhysicsLearnerLoopInventoryTest(unittest.TestCase):
    def test_direct_core2a_gaps_are_closed(self):
        primary_core2a = set()
        closure_core2a = []
        for path in LIBS.values():
            package = load(path)
            for q in package["questions"]:
                cores = {x["core"] for x in q.get("exposure", [])}
                if "CORE2A" in cores:
                    primary_core2a.add(q["primary_capability_ref"])
                    if q.get("extensions", {}).get("grade9v3:closure_ep") == "EP-TA-006":
                        closure_core2a.append(q)
        self.assertTrue(DIRECT_GAPS.issubset(primary_core2a))
        self.assertEqual(7, len(closure_core2a))
        self.assertEqual(DIRECT_GAPS, {q["primary_capability_ref"] for q in closure_core2a})

    def test_exact_core_transfer_rows_are_executable(self):
        closure = {}
        for matrix_id, path in LIBS.items():
            package = load(path)
            for q in package["questions"]:
                key = q.get("extensions", {}).get("grade9v3:matrix_transfer_key")
                if key:
                    self.assertNotIn(key, closure)
                    closure[key] = q
        self.assertEqual(18, len(closure))

        for matrix_id, indices in EXPECTED_TRANSFER_KEYS.items():
            matrix = load(MATRICES[matrix_id])
            package = load(LIBS[matrix_id])
            teaching_ids = {
                step["id"]
                for micro in package["microtopics"]
                for step in micro.get("teaching_path", [])
            }
            for idx in indices:
                row = matrix["transfer"][idx]
                key = f"{matrix_id}:{idx}"
                self.assertIn(key, closure)
                q = closure[key]
                self.assertEqual("CORE2B", q["exposure"][0]["core"])
                self.assertEqual(row["dimension"], q["transfer"]["dimension"])
                self.assertEqual(row["changed_demand"], q["transfer"]["statement"])
                self.assertEqual(
                    row["information_not_handed_over"],
                    q["extensions"]["grade9v3:information_not_handed_over"],
                )
                self.assertIn(q["repair_ref"], teaching_ids)
                self.assertEqual("AUTHORED", q["origin"])
                self.assertEqual("CANDIDATE", q["status"])
                self.assertTrue(q["transfer"]["builds_on"])
                self.assertTrue(q["answer"].get("rubric"))

        # Explicitly protect the Gravitation orbital extension rows from Grade-9 closure.
        self.assertNotIn("MATRIX-PHY-GRAV-UNIVERSAL-LAW:4", closure)
        self.assertNotIn("MATRIX-PHY-GRAV-UNIVERSAL-LAW:5", closure)

    def test_new_items_use_existing_family_and_source_refs(self):
        for path in LIBS.values():
            package = load(path)
            resource_ids = {r["id"] for r in package.get("resources", [])}
            family_ids = {f["id"] for f in package.get("question_families", [])}
            family_items = {item for f in package.get("question_families", []) for item in f.get("item_refs", [])}
            for q in package["questions"]:
                if q.get("extensions", {}).get("grade9v3:closure_ep") != "EP-TA-006":
                    continue
                self.assertIn(q["origin_ref"], resource_ids)
                self.assertEqual([q["origin_ref"]], q["source_refs"])
                self.assertIn(q["family_ref"], family_ids)
                self.assertIn(q["id"], family_items)


if __name__ == "__main__":
    unittest.main()
