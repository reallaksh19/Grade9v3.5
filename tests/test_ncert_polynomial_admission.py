#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.library import intake
from Shared.tools import build_question_bank_web

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "Mathematics/library/polynomials.v1.json"
SOURCE = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
VALIDATIONS = [
    REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q01-q10.validation.json",
    REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q11-q20.validation.json",
    REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q21-q30.validation.json",
]

CANONICAL_TO_SOURCE = {
    **{f"Q-MAT-POLY-NCERT9-EX21-Q{n:02d}": f"ncert-exemplar-g9-math-u02-q{n:02d}" for n in range(1, 22)},
    "Q-MAT-POLY-NCERT9-EX22-Q01": "ncert-exemplar-g9-math-u02-q22",
    "Q-MAT-POLY-NCERT9-EX22-Q02-II": "ncert-exemplar-g9-math-u02-q24",
    "Q-MAT-POLY-NCERT9-EX22-Q02-IV": "ncert-exemplar-g9-math-u02-q25",
    "Q-MAT-POLY-NCERT9-EX23-Q01-I": "ncert-exemplar-g9-math-u02-q26",
    "Q-MAT-POLY-NCERT9-EX23-Q01-II": "ncert-exemplar-g9-math-u02-q27",
    "Q-MAT-POLY-NCERT9-EX23-Q01-III": "ncert-exemplar-g9-math-u02-q28",
    "Q-MAT-POLY-NCERT9-EX23-Q02-I": "ncert-exemplar-g9-math-u02-q29",
    "Q-MAT-POLY-NCERT9-EX23-Q02-II": "ncert-exemplar-g9-math-u02-q30",
}
CANONICAL_IDS = list(CANONICAL_TO_SOURCE)
SOURCE_IDS = list(CANONICAL_TO_SOURCE.values())
HELD_SOURCE_ID = "ncert-exemplar-g9-math-u02-q23"


class TestNcertPolynomialQuestionBankAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.validations = [json.loads(path.read_text(encoding="utf-8")) for path in VALIDATIONS]
        cls.source_by_id = {row["id"]: row for row in cls.source["questions"]}
        cls.validation_by_id = {
            row["source_id"]: (row, path.relative_to(REPO).as_posix())
            for path, receipt in zip(VALIDATIONS, cls.validations)
            for row in receipt["records"]
        }
        cls.package_by_id = {row["id"]: row for row in cls.package["questions"]}
        cls.browser = build_question_bank_web.build(REPO)
        cls.browser_by_id = {row["id"]: row for row in cls.browser["questions"]}

    def test_admission_is_exactly_the_twenty_nine_validation_pass_records(self):
        admitted = [
            q for q in self.package["questions"]
            if (q.get("extensions") or {}).get("grade9v3:question_bank", {}).get("include") is True
        ]
        admitted_ids = {q["id"] for q in admitted}
        self.assertEqual(admitted_ids, set(CANONICAL_IDS))
        self.assertEqual(len(admitted_ids), 29)

        for canonical_id, source_id in CANONICAL_TO_SOURCE.items():
            receipt, validation_ref = self.validation_by_id[source_id]
            self.assertEqual(receipt["academic_validation"]["status"], "PASS")
            self.assertTrue(receipt["academic_validation"]["admission_eligible"])

            canonical = self.package_by_id[canonical_id]
            lineage = canonical["extensions"]["grade9v3:lineage"]
            custody = canonical["extensions"]["grade9v3:source_custody"]
            source = self.source_by_id[source_id]
            self.assertEqual(lineage["source_question_id"], source_id)
            self.assertEqual(lineage["validation_ref"], validation_ref)
            self.assertEqual(canonical["stem"], source["stem"])
            self.assertEqual(canonical["options"], source.get("options", []))
            self.assertEqual(canonical["answer"]["summary"], source["official_answer_text"])
            self.assertEqual(custody["text_sha256"], source["stem_sha256"])
            self.assertEqual(canonical["answer"]["verification_status"], "INDEPENDENTLY_CHECKED")
            self.assertEqual(canonical["status"], "REVIEWED")

    def test_q23_hold_is_explicit_and_not_admitted(self):
        receipt, validation_ref = self.validation_by_id[HELD_SOURCE_ID]
        self.assertEqual(validation_ref, "TEST/candidates/ncert-exemplar-g9-math-u02-q21-q30.validation.json")
        self.assertEqual(receipt["academic_validation"]["status"], "HOLD")
        self.assertFalse(receipt["academic_validation"]["admission_eligible"])

        admitted_source_ids = {
            q["extensions"]["grade9v3:lineage"]["source_question_id"]
            for q in self.package["questions"]
            if (q.get("extensions") or {}).get("grade9v3:question_bank", {}).get("include") is True
        }
        self.assertNotIn(HELD_SOURCE_ID, admitted_source_ids)
        excluded = self.package["extensions"]["grade9v3:question_bank_admission"]["excluded_source_refs"]
        self.assertEqual([row["source_question_id"] for row in excluded], [HELD_SOURCE_ID])
        self.assertEqual(excluded[0]["status"], "HOLD")

    def test_remaining_ncert_intake_is_not_admitted_by_source_identity(self):
        admitted_source_ids = {
            q["extensions"]["grade9v3:lineage"]["source_question_id"]
            for q in self.package["questions"]
            if (q.get("extensions") or {}).get("grade9v3:question_bank", {}).get("include") is True
        }
        all_ncert_ids = {q["id"] for q in self.source["questions"]}
        self.assertEqual(admitted_source_ids, set(SOURCE_IDS))
        self.assertEqual(len(all_ncert_ids - admitted_source_ids), 181)

    def test_iss55_owner_questions_remain_candidate_and_non_admitted(self):
        iss55 = [q for q in self.package["questions"] if q["id"].startswith("Q-MAT-POLY-ISS55-")]
        self.assertEqual(len(iss55), 10)
        for q in iss55:
            self.assertEqual(q["status"], "CANDIDATE")
            self.assertIs(q["extensions"]["grade9v3:question_bank"]["include"], False)

    def test_package_stays_structurally_admissible(self):
        report = intake.check(self.package)
        self.assertTrue(report["admitted"], report["findings"])

    def test_production_question_bank_contains_only_canonical_admission_ids(self):
        self.assertLessEqual(set(CANONICAL_IDS), set(self.browser_by_id))
        self.assertFalse(set(SOURCE_IDS) & set(self.browser_by_id))
        self.assertNotIn(HELD_SOURCE_ID, self.browser_by_id)
        for qid in CANONICAL_IDS:
            row = self.browser_by_id[qid]
            self.assertEqual(row["subject"], "Mathematics")
            self.assertEqual(row["topic"], "Polynomials")
            self.assertEqual(row["exam"], "NCERT Exemplar")
            self.assertEqual(row["answer"]["verification_status"], "INDEPENDENTLY_CHECKED")

    def test_q1_domain_caveat_survives_admission_evidence(self):
        q1 = self.package_by_id["Q-MAT-POLY-NCERT9-EX21-Q01"]
        note = q1["extensions"]["grade9v3:validation_note"]
        self.assertIn("x = 0", note)
        self.assertIn("NCERT", note)


if __name__ == "__main__":
    unittest.main()
