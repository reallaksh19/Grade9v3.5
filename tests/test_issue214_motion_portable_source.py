from __future__ import annotations

import unittest
from pathlib import Path

from Shared.contracts import load
from Shared.library.resolve import build_index

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "Physics/library/phy-kin-2d-motion.v1.json"

REP = "REP-KIN-2D-SHARED-CLOCK"
MIC = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"
SCENE = "SCENE-KIN-2D-SHARED-CLOCK-PORTABLE-01"
T_SHARED = "DAT-KIN-2D-SHARED-T2"
T_MIXED = "DAT-KIN-2D-MIXED-T3"
PACKAGE_REF = "portable-motion-shared-clock"


class MotionSharedClockPortableSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = load(PACKAGE)
        cls.records = build_index([cls.package])
        cls.rep = cls.records[REP]
        cls.microtopic = cls.records[MIC]
        cls.scene = next(
            row for row in cls.rep["scene_instances"] if row["id"] == SCENE
        )
        cls.portable = cls.scene["scene"]["portable_workbench"]

    def test_scene_is_bound_to_canonical_microtopic_and_governed_time_datums(self):
        self.assertEqual(self.scene["microtopic_ref"], MIC)
        self.assertEqual(self.scene["cores"], ["CORE1A", "CORE1B"])
        self.assertEqual(self.scene["datum_refs"], [T_SHARED, T_MIXED])

        shared = self.records[T_SHARED]
        mixed = self.records[T_MIXED]
        self.assertEqual((shared["value"], shared["unit"]), (2, "s"))
        self.assertEqual((mixed["value"], mixed["unit"]), (3, "s"))
        self.assertEqual(shared["source_refs"], self.rep["source_refs"])
        self.assertEqual(mixed["source_refs"], self.rep["source_refs"])

    def test_portable_source_declares_one_operation_with_accept_and_reject_cases(self):
        self.assertEqual(self.portable["schema_version"], "1.0.0")
        self.assertEqual(self.portable["package_ref"], PACKAGE_REF)
        self.assertEqual(
            self.portable["target"]["operation"],
            "reconstruct-plane-state",
        )
        cases = {row["id"]: row for row in self.portable["transactions"]}
        self.assertEqual(cases["same-time"]["outcome"], "ACCEPT")
        self.assertEqual(cases["mixed-time"]["outcome"], "REJECT")
        self.assertEqual(
            cases["same-time"]["source_entity_ref"],
            "shared-clock-same-time-candidate",
        )
        self.assertEqual(
            cases["mixed-time"]["source_entity_ref"],
            "shared-clock-mixed-time-candidate",
        )
        self.assertIn("same physical state", cases["mixed-time"]["reason"])
        self.assertEqual(
            cases["same-time"]["operation"],
            cases["mixed-time"]["operation"],
        )

    def test_portable_source_preserves_canonical_shared_clock_invariant(self):
        candidates = {
            row["id"]: row
            for row in self.portable["entities"]
        }
        same = candidates["shared-clock-same-time-candidate"]
        mixed = candidates["shared-clock-mixed-time-candidate"]
        self.assertEqual(same["x_time_ref"], T_SHARED)
        self.assertEqual(same["y_time_ref"], T_SHARED)
        self.assertEqual(mixed["x_time_ref"], T_SHARED)
        self.assertEqual(mixed["y_time_ref"], T_MIXED)
        self.assertEqual(same["semantic_state"], "SIMULTANEOUS")
        self.assertEqual(mixed["semantic_state"], "NON_SIMULTANEOUS")

        invariant = self.microtopic["teaching_path"][3]
        self.assertEqual(invariant["id"], "K2D1-4")
        self.assertIn("same instant", invariant["action"])
        self.assertIn("single physical state", invariant["why_valid"])

    def test_source_is_declarative_and_does_not_embed_page_code(self):
        forbidden = {"script", "javascript", "eval", "function", "handler", "onclick"}
        stack = [self.portable]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                self.assertTrue(forbidden.isdisjoint({str(k).lower() for k in value}))
                stack.extend(value.values())
            elif isinstance(value, list):
                stack.extend(value)


if __name__ == "__main__":
    unittest.main()
