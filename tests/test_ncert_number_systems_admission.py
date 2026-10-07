#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.library import intake
from Shared.tools import build_question_bank_web

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "Mathematics/library/number-systems.v1.json"
SOURCE = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
VALIDATION = REPO / "TEST/candidates/ncert-exemplar-g9-math-u01-q01-q10.validation.json"

CANONICAL_IDS = [f"Q-MAT-NUMSYS-NCERT9-EX11-Q{n:02d}" for n in range(1, 11)]
SOURCE_IDS = [f"ncert-exemplar-g9-math-u01-q{n:02d}" for n in range(1, 11)]


class TestNcertNumberSystemsAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
        cls.source_by_id = {row["id"]: row for row in cls.source["questions"]}
        cls.validation_by_id = {row["source_id"]: row for row in cls.validation["records"]}
        cls.package_by_id = {row["id"]: row for row in cls.package["questions"]}
        cls.browser = build_question_bank_web.build(REPO)
        cls.browser_by_id = {row["id"]: row for row in cls.browser["questions"]}

    def test_admission_is_exactly_the_ten_validation_pass_records(self):
        admitted = [
            q for q in self.package["questions"]
            if (q.get("extensions") or {}).get("grade9v3:question_bank", {}).get("include") is True
        ]
        self.assertEqual({q["id"] for q in admitted}, set(CANONICAL_IDS))

        for number, canonical_id in enumerate(CANONICAL_IDS, start=1):
            source_id = SOURCE_IDS[number - 1]
            receipt = self.validation_by_id[source_id]
            self.assertEqual(receipt["academic_validation"]["status"], "PASS")
            self.assertTrue(receipt["academic_validation"]["admission_eligible"])

            canonical = self.package_by_id[canonical_id]
            source = self.source_by_id[source_id]
            lineage = canonical["extensions"]["grade9v3:lineage"]
            custody = canonical["extensions"]["grade9v3:source_custody"]
            self.assertEqual(lineage["source_question_id"], source_id)
            self.assertEqual(lineage["validation_ref"], VALIDATION.relative_to(REPO).as_posix())
            self.assertEqual(canonical["stem"], source["stem"])
            self.assertEqual(canonical["options"], source["options"])
            self.assertEqual(canonical["answer"]["summary"], source["official_answer_text"])
            self.assertEqual(custody["text_sha256"], source["stem_sha256"])
            self.assertEqual(canonical["answer"]["verification_status"], "INDEPENDENTLY_CHECKED")
            self.assertEqual(canonical["status"], "REVIEWED")

    def test_q7_duplicate_resolution_is_preserved_without_source_custody_loss(self):
        source_q6 = self.source_by_id["ncert-exemplar-g9-math-u01-q06"]
        source_q7 = self.source_by_id["ncert-exemplar-g9-math-u01-q07"]
        self.assertEqual(source_q6["stem_sha256"], source_q7["stem_sha256"])
        self.assertNotEqual(source_q6["options"], source_q7["options"])
        self.assertEqual(source_q7["workflow_status"], "READY_FOR_BLUEPRINT")

        q7 = self.package_by_id["Q-MAT-NUMSYS-NCERT9-EX11-Q07"]
        self.assertEqual(q7["extensions"]["grade9v3:source_custody"]["text_sha256"], source_q7["stem_sha256"])
        self.assertEqual(q7["options"], source_q7["options"])

    def test_remaining_ncert_intake_is_not_admitted_by_source_identity(self):
        admitted_source_ids = {
            q["extensions"]["grade9v3:lineage"]["source_question_id"]
            for q in self.package["questions"]
            if (q.get("extensions") or {}).get("grade9v3:question_bank", {}).get("include") is True
        }
        all_ncert_ids = {q["id"] for q in self.source["questions"]}
        self.assertEqual(admitted_source_ids, set(SOURCE_IDS))
        self.assertEqual(len(all_ncert_ids - admitted_source_ids), 200)

    def test_package_stays_structurally_admissible(self):
        report = intake.check(self.package)
        self.assertTrue(report["admitted"], report["findings"])

    def test_production_question_bank_contains_all_ten_canonical_ids_only(self):
        self.assertLessEqual(set(CANONICAL_IDS), set(self.browser_by_id))
        self.assertFalse(set(SOURCE_IDS) & set(self.browser_by_id))
        for qid in CANONICAL_IDS:
            row = self.browser_by_id[qid]
            self.assertEqual(row["subject"], "Mathematics")
            self.assertEqual(row["topic"], "Number Systems")
            self.assertEqual(row["topic_ref"], "TOPIC-MATHEMATICS-NUMBER-SYSTEMS")
            self.assertEqual(row["exam"], "NCERT Exemplar")
            self.assertEqual(row["answer"]["verification_status"], "INDEPENDENTLY_CHECKED")

    def test_polynomials_and_iss55_admission_state_is_untouched(self):
        polynomials = json.loads((REPO / "Mathematics/library/polynomials.v1.json").read_text(encoding="utf-8"))
        admitted = [
            q for q in polynomials["questions"]
            if (q.get("extensions") or {}).get("grade9v3:question_bank", {}).get("include") is True
        ]
        iss55 = [q for q in polynomials["questions"] if q["id"].startswith("Q-MAT-POLY-ISS55-")]
        self.assertEqual(len(admitted), 29)
        self.assertEqual(len(iss55), 10)
        self.assertEqual(sum((q["extensions"]["grade9v3:question_bank"]["include"] is True) for q in iss55), 0)
        held = polynomials["extensions"]["grade9v3:question_bank_admission"]["excluded_source_refs"]
        self.assertEqual([row["source_question_id"] for row in held], ["ncert-exemplar-g9-math-u02-q23"])


if __name__ == "__main__":
    unittest.main()
