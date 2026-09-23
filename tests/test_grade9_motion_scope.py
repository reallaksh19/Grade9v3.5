"""Grade-9 Motion authoring scope stays narrow and reuses the current canonical spine."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class Grade9MotionScope(unittest.TestCase):
    def setUp(self):
        self.package = json.loads(
            (REPO / "Physics/library/phy-kin-1d-motion.v1.json").read_text(encoding="utf-8")
        )
        self.matrix = json.loads(
            (REPO / "Physics/matrices/phy-kin-1d-motion.rungs.json").read_text(encoding="utf-8")
        )
        self.bucket = next(
            row for row in self.package["buckets"]
            if row["id"] == "BUCKET-PHY-KIN-1D-MOTION"
        )
        self.microtopics = {row["id"]: row for row in self.package["microtopics"]}
        self.capabilities = {row["id"]: row for row in self.package["capabilities"]}

    def test_motion_does_not_pull_the_vector_addition_bucket_into_grade9_by_default(self):
        self.assertEqual(self.bucket["prerequisite_refs"], [])

    def test_every_motion_rung_reuses_a_current_canonical_microtopic_and_capability(self):
        self.assertEqual(
            {row["rung"] for row in self.matrix["rungs"]},
            {"R1", "R2", "R3", "R4G", "R4", "R5", "R6"},
        )
        r6 = next(row for row in self.matrix["rungs"] if row["rung"] == "R6")
        self.assertFalse(r6["default_entry_eligible"])
        self.assertEqual(
            r6["microtopic_ref"],
            "MIC-PHY-KIN-CIRCULAR-DYNAMICS-ROLE",
        )
        for rung in self.matrix["rungs"]:
            ref = rung.get("microtopic_ref")
            self.assertIn(ref, self.microtopics, rung["rung"])
            cap = self.microtopics[ref]["primary_capability_ref"]
            self.assertIn(cap, self.capabilities, (rung["rung"], ref))

    def test_grade9_scope_does_not_promote_curriculum_authority(self):
        self.assertEqual(self.package["status"], "CANDIDATE")
        self.assertEqual(self.package["curriculum_mappings"], [])
        self.assertEqual(self.bucket["curriculum_mappings"], [])
        self.assertEqual(
            self.bucket["extensions"].get("issue19:scope_class"),
            "OWNER_EXTENSION",
        )

    def test_matrix_contract_is_not_given_a_grade_field(self):
        forbidden = {"grade", "grade_level", "class", "syllabus_status"}
        self.assertFalse(forbidden & set(self.matrix))


if __name__ == "__main__":
    unittest.main()
