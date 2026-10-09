"""Fail-closed behavioural goldens for three separate *unapproved* Core1B practices.

The 4x7 QRT is the authoritative source; goldens cover 3 of 28 cells only.
These tests exercise contract/source/math statements, not learner mastery.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import question_review_matrix as qrt

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "tests" / "fixtures" / "core1b-goldens"
CASE_FILES = ("01-consecutive.json", "02-algebra.json", "03-motion.json")
COVERAGE = DIR / "matrix-coverage.v1.json"


def load_goldens():
    return [json.loads((DIR / filename).read_text(encoding="utf-8")) for filename in CASE_FILES]


class Core1BThreeCaseGoldens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_goldens()
        cls.matrix = json.loads(COVERAGE.read_text(encoding="utf-8"))

    def test_exactly_three_distinct_goldens_and_noncanonical_status(self):
        self.assertEqual([c["id"] for c in self.cases], ["consecutive", "algebra", "motion"])
        self.assertEqual(len({c["qrt"]["cell"] for c in self.cases}), 3)
        self.assertEqual({c["subject"] for c in self.cases}, {"Mathematics", "Physics"})
        for c in self.cases:
            self.assertEqual(c["schema"], "core1b-three-case-golden/v1")
            self.assertEqual(c["status"], "TEST_FIXTURE_NOT_CURRICULUM_ADMISSION")
            self.assertEqual(c["review_status"], "NOT_INDEPENDENTLY_APPROVED")
            self.assertEqual(c["learner_trial"], "NOT_RUN")
            self.assertFalse(c["source"]["official_exam_custody"])
            self.assertEqual(c["policy"]["automatic_grade"], "NEVER")
        self.assertEqual(self.cases[0]["source"]["origin"], "MERGED_AUTHORED_TEST_PILOT")
        for c in self.cases[1:]:
            self.assertEqual(c["source"]["origin"], "NEW_AUTHOR_DEMONSTRATION")
            self.assertFalse(c["source"]["approved_package"])

    def test_qrt_4_by_7_matrix_exact_and_25_cells_explicitly_uncovered(self):
        self.assertEqual(qrt.check_paths(), [])
        templates = qrt.compile_templates(qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH))
        actual_ids = {t["template_id"] for t in templates}
        self.assertEqual(len(actual_ids), 28)
        self.assertEqual(self.matrix["source_qrt"], qrt.MATRIX_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(self.matrix["all_qrt_cell_count"], 28)
        self.assertEqual(list(self.matrix["matrix"]), list(qrt.BANDS))
        selected = {}
        for band in qrt.BANDS:
            row = self.matrix["matrix"][band]
            self.assertEqual(list(row), list(qrt.DEMANDS))
            for demand in qrt.DEMANDS:
                entry = row[demand]
                cell = f"QRT-{demand}-{band}"
                self.assertEqual(entry["cell"], cell)
                self.assertIn(cell, actual_ids)
                if entry["fixture_id"] is not None:
                    self.assertEqual(entry["coverage"], "EXERCISED_AS_UNAPPROVED_TEST_GOLDEN")
                    selected[entry["fixture_id"]] = cell
                else:
                    self.assertEqual(entry["coverage"], "NOT_EXERCISED_BY_THREE_GOLDENS")
        self.assertEqual(len(selected), 3)
        self.assertEqual(self.matrix["exercised_cell_count"], 3)
        self.assertEqual(self.matrix["untested_cell_count"], 25)
        self.assertEqual(selected, {c["id"]: c["qrt"]["cell"] for c in self.cases})
        self.assertNotIn("D4", {c["qrt"]["band"] for c in self.cases})
        self.assertEqual(self.matrix["approval"], "NOT_GRANTED")

    def test_distinct_demand_and_band_semantics_do_not_claim_qrt_admission(self):
        intended = {
            "consecutive": ("JUSTIFY", "D3", "SYNTHESIZE"),
            "algebra": ("REPRESENT", "D2", "JUSTIFY"),
            "motion": ("MODEL", "D2", "APPLY"),
        }
        for c in self.cases:
            demand, band, secondary = intended[c["id"]]
            self.assertEqual((c["qrt"]["primary_demand"], c["qrt"]["band"]), (demand, band))
            self.assertIn(secondary, c["qrt"]["secondary_demands"])
            self.assertEqual(c["qrt"]["cell"], f"QRT-{demand}-{band}")
            self.assertGreater(len(c["qrt"]["protected_work"]), 45)
            self.assertGreater(len(c["qrt"]["reason"]), 45)
        self.assertEqual(set(self.matrix["review_asks"]), set(qrt.ASKS))
        for cell in ("S1", "S2", "S3", "P2"):
            self.assertTrue(self.matrix["review_asks"][cell].startswith("NOT_EXERCISED"))

    def test_all_three_preserve_core1b_sequence_and_encouraging_entry(self):
        for c in self.cases:
            policy, learner = c["policy"], c["learner"]
            self.assertEqual(policy["attempt"], "NONWHITESPACE_OR_EXPLICIT_PAPER")
            self.assertEqual(policy["short_nonblank_text"], "ACCEPT_UNGRADED")
            self.assertEqual(policy["whitespace_text"], "BLOCK")
            self.assertEqual(policy["paper_attempt"], "ACCEPT_UNGRADED")
            self.assertEqual(policy["first_commit_unlocks"], "DIAGNOSTIC_RECONSTRUCTION_ONLY")
            self.assertEqual(policy["repair_commit"], "REQUIRED_BEFORE_REFERENCE")
            self.assertEqual(policy["boundary_commit"], "SEPARATE_FROM_PROOF_AND_REPAIR")
            self.assertEqual(policy["boundary_reference"], "REVEAL_ONLY_AFTER_OWN_ATTEMPT")
            self.assertIn("what you think", learner["encouragement"])
            self.assertNotIn("33", learner["encouragement"])
            self.assertGreaterEqual(len(learner["diagnostics"]), 4)
            self.assertTrue(all(q.endswith("?") for q in learner["diagnostics"]))
            self.assertEqual(len(learner["warrants"]), 4)
            for key in ("situation", "question", "repair_prompt", "reference",
                        "boundary_question", "boundary_answer", "plausible_wrong_attempt",
                        "misconception"):
                self.assertTrue(learner[key].strip(), (c["id"], key))

    def test_mathematical_falsifiers_come_from_real_proofs_not_sample_scores(self):
        by_id = {c["id"]: c for c in self.cases}
        proof = by_id["consecutive"]["learner"]
        source = json.loads((ROOT / by_id["consecutive"]["source"]["source_file"]).read_text(encoding="utf-8"))
        m = next(t for t in source["microtopics"]
                 if t["id"] == by_id["consecutive"]["source"]["source_microtopic"])
        self.assertIn("three checks", m["elicitation"]["predict"]["prompt"])
        self.assertIn("t=2", m["elicitation"]["boundary_test"]["answer"])
        self.assertIn("gcd(2,3)=1", proof["reference"])
        for remainder in (0, 1, 2):
            self.assertIn(f"is {remainder}", proof["reference"])
        for n in range(1, 101):
            self.assertEqual(n*(n+1)*(n+2) % 6, 0)
        self.assertEqual(((2-1)*2)%6, 2)
        alg = by_id["algebra"]["learner"]
        self.assertIn("x²+4x+4", alg["reference"])
        self.assertIn("x=0", alg["boundary_answer"])
        for x in (-7, -1, 0, 1, 5):
            self.assertEqual((x+2)**2, x*x+4*x+4)
            self.assertEqual((x+2)**2 == x*x+4, x == 0)
        motion = by_id["motion"]["learner"]
        self.assertIn("120/40=3 m/s", motion["reference"])
        self.assertIn("0/40=0 m/s", motion["reference"])
        self.assertIn("1 m/s east", motion["boundary_answer"])
        self.assertEqual((60+60)/40, 3)
        self.assertEqual((60-60)/40, 0)
        self.assertEqual((60-30)/30, 1)

    def test_no_answers_or_status_claims_can_be_misread_as_real_student_evidence(self):
        for c in self.cases:
            self.assertEqual(c["policy"]["student_mastery"], "NOT_MEASURED")
            self.assertEqual(c["policy"]["precommit_answer_access"], "UI_HIDDEN_NOT_CRYPTOGRAPHIC")
            self.assertNotIn("PASS", c["review_status"])
            self.assertNotIn("real learner", c["source"]["origin"].lower())


if __name__ == "__main__":
    unittest.main()
