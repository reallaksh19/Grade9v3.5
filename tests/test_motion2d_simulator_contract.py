"""Regression tests for the Motion in 2D question bank and simulator teaching contract."""
from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MOTION_DIR = REPO / "public/physics/motion-in-2d/explorers/motions_in_2d"
DATA_PATH = MOTION_DIR / "jee_questions_data.js"
HTML_PATH = MOTION_DIR / "index.html"

PLACEHOLDER_ANSWERS = {
    "Direct application of projectile formulas",
    "Evaluate from coordinate kinematic equations",
    "Complementary symmetry verified",
    "Computed from asymmetric boundary kinematics",
    "River-boat kinematic decomposition",
    "Galilean vector subtraction",
    "Compare with trajectory standard form",
}


def load_bank() -> list[dict]:
    text = DATA_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.JEE_QUESTIONS_DATA\s*=\s*(\[.*\])\s*;\s*$", text, re.S)
    if not match:
        raise AssertionError("Could not parse window.JEE_QUESTIONS_DATA")
    return json.loads(match.group(1))


class Motion2DSimulatorContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = load_bank()
        cls.by_id = {row["id"]: row for row in cls.bank}
        cls.html = HTML_PATH.read_text(encoding="utf-8")

    def test_bank_has_exactly_104_unique_records(self):
        self.assertEqual(len(self.bank), 104)
        self.assertEqual(len(self.by_id), 104)

    def test_every_record_has_teaching_and_audit_fields(self):
        required = {
            "ans",
            "formula",
            "steps",
            "takeaway",
            "trap",
            "teacherCheck",
            "audit",
            "simulation",
        }
        for row in self.bank:
            with self.subTest(question=row["id"]):
                self.assertTrue(required.issubset(row))
                self.assertTrue(row["ans"].strip())
                self.assertTrue(row["formula"].strip())
                self.assertTrue(row["steps"])
                self.assertTrue(row["takeaway"].strip())
                self.assertTrue(row["trap"].strip())
                self.assertTrue(row["teacherCheck"].strip())
                self.assertIn("status", row["audit"])
                self.assertIn(
                    row["simulation"]["fidelity"],
                    {
                        "exact_question_load",
                        "constraint_faithful_demo",
                        "concept_demo",
                        "unavailable",
                    },
                )

    def test_no_known_placeholder_final_answers_remain(self):
        offenders = [
            row["id"]
            for row in self.bank
            if row.get("ans", "").strip() in PLACEHOLDER_ANSWERS
        ]
        self.assertEqual(offenders, [])

    def test_known_content_regressions_are_fixed(self):
        self.assertEqual(self.by_id["EXAM-04"]["ans"], "x = √3")
        self.assertEqual(self.by_id["EXAM-32"]["ans"], "30 ĵ cm/s²")
        self.assertIn("53.13° North of East", self.by_id["PDF-12"]["ans"])
        self.assertIn("tan φ is linear", self.by_id["PDF-04"]["ans"])
        self.assertIn("d²φ/dt² = −2k³t", self.by_id["PDF-04"]["ans"])

    def test_source_inconsistent_record_is_explicit_not_fabricated(self):
        inconsistent = [
            row["id"]
            for row in self.bank
            if row.get("audit", {}).get("status") == "source-inconsistent"
        ]
        self.assertEqual(inconsistent, ["EXAM-20"])
        self.assertEqual(
            self.by_id["EXAM-20"]["simulation"]["fidelity"],
            "unavailable",
        )

    def test_html_exposes_answers_traps_checks_and_question_chalkboard(self):
        for required_text in (
            "function openQuestionChalkboard",
            "Teacher's Chalkboard",
            "Teacher check:",
            "Trap:",
            "simulationLabel(q)",
            "validateQuestionBank()",
        ):
            self.assertIn(required_text, self.html)

    def test_html_does_not_truncate_topic_questions_or_fabricate_sim_values(self):
        self.assertNotIn("filtered.slice(0, 6)", self.html)
        self.assertNotIn(
            "If no explicit numbers were found, assign category-specific custom values",
            self.html,
        )
        self.assertNotIn("d²φ/dt² ≈ 0 · LINEAR STEADY RISE", self.html)
        self.assertIn("Apply only parameters explicitly declared", self.html)

    def test_static_dom_ids_are_unique(self):
        ids = re.findall(r'\bid="([^"]+)"', self.html)
        duplicates = sorted(k for k, n in Counter(ids).items() if n > 1)
        self.assertEqual(duplicates, [])


if __name__ == "__main__":
    unittest.main()
