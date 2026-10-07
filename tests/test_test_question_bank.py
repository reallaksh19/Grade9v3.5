"""Focused regressions for the TEST-only NCERT Exemplar Question Bank projection."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_question_bank_web, build_test_question_bank  # noqa: E402

INTAKE = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
PUBLIC_PAGE = REPO / "public/test/question-bank/index.html"
PUBLIC_DATA = REPO / "public/test/question-bank/questions.js"
DOCS_PAGE = REPO / "docs/test/question-bank/index.html"
DOCS_DATA = REPO / "docs/test/question-bank/questions.js"
VALIDATION_SCHEMA = REPO / "TEST/adapter/QuestionValidation.schema.json"
VALIDATION_RECEIPT = REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q01-q10.validation.json"


class TestTestQuestionBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(INTAKE.read_text(encoding="utf-8"))
        cls.questions = cls.bank["questions"]
        cls.ids = {row["id"] for row in cls.questions}

    def test_projection_contains_all_210_as_academically_unvalidated(self):
        projection = build_test_question_bank.payload(REPO)
        rows = [q for bank in projection["banks"] for q in bank["questions"]]
        self.assertEqual(len(rows), 210)
        self.assertEqual(len({q["id"] for q in rows}), 210)
        self.assertEqual(projection["academic_validation_status"], "UNVALIDATED")
        self.assertEqual(
            sum(q["text_verification_status"] == "TEXT_VERIFIED_AGAINST_OFFICIAL" for q in rows),
            210,
        )
        self.assertEqual(sum(q["workflow_status"] == "DUPLICATE_REVIEW" for q in rows), 1)

    def test_shell_makes_source_and_academic_states_distinct(self):
        page = build_test_question_bank.render_page(REPO)
        self.assertIn("SOURCE VERIFIED", page)
        self.assertIn("UNVALIDATED", page)
        self.assertIn("DUPLICATE REVIEW", page)
        self.assertIn("questions.js", page)
        self.assertIn("Nothing on this page is in the production Question Bank.", page)
        self.assertIn('data-g9-test="sandbox-draft"', page)
        self.assertNotRegex(page, r"https?://")

    def test_committed_public_and_pages_outputs_are_current(self):
        self.assertEqual(PUBLIC_PAGE.read_text(encoding="utf-8"), build_test_question_bank.render_page(REPO))
        self.assertEqual(PUBLIC_DATA.read_text(encoding="utf-8"), build_test_question_bank.render_data(REPO))
        self.assertEqual(DOCS_PAGE.read_bytes(), PUBLIC_PAGE.read_bytes())
        self.assertEqual(DOCS_DATA.read_bytes(), PUBLIC_DATA.read_bytes())

    def test_all_210_remain_out_of_production_question_bank_and_search(self):
        production = build_question_bank_web.build(REPO)
        production_ids = {q["id"] for q in production["questions"]}
        self.assertFalse(self.ids & production_ids)

        canonical = (REPO / "public/data/search-index.v1.json").read_text(encoding="utf-8")
        learner = (REPO / "public/data/learner-search-index.v1.json").read_text(encoding="utf-8")
        for qid in self.ids:
            self.assertNotIn(qid, canonical)
            self.assertNotIn(qid, learner)

    def test_unit_and_question_type_denominators_are_stable(self):
        by_unit: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for question in self.questions:
            by_unit[question["chapter_or_unit"]] = by_unit.get(question["chapter_or_unit"], 0) + 1
            by_type[question["question_type"]] = by_type.get(question["question_type"], 0) + 1
        self.assertEqual(sorted(by_unit.values()), [30, 30, 30, 30, 30, 30, 30])
        self.assertEqual(by_type, {"MULTIPLE_CHOICE": 125, "TRUE_FALSE": 40, "SHORT_ANSWER": 45})

    def test_first_ten_polynomial_validation_receipt_is_source_bound_and_non_publishing(self):
        schema = json.loads(VALIDATION_SCHEMA.read_text(encoding="utf-8"))
        receipt = json.loads(VALIDATION_RECEIPT.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path))
        self.assertEqual([error.message for error in errors], [])

        expected_ids = [f"ncert-exemplar-g9-math-u02-q{number:02d}" for number in range(1, 11)]
        rows = receipt["records"]
        self.assertEqual([row["source_id"] for row in rows], expected_ids)
        source = {row["id"]: row for row in self.questions}

        for row in rows:
            original = source[row["source_id"]]
            self.assertEqual(row["original_identifier"], original["original_identifier"])
            self.assertEqual(row["stem_sha256"], original["stem_sha256"])
            self.assertEqual(row["source_text_verification"], original["text_verification_status"])
            self.assertEqual(row["official_answer_text"], original["official_answer_text"])
            self.assertEqual(row["official_answer_locator"], original["answer_key_locator"])
            validation = row["academic_validation"]
            self.assertEqual(validation["status"], "PASS")
            self.assertTrue(validation["admission_eligible"])
            self.assertTrue(validation["reasoning"])
            self.assertEqual(validation["independent_result"], original["official_answer_text"])

        q1 = rows[0]["academic_validation"]
        self.assertIn("convention_note", q1)
        self.assertIn("x = 0", q1["convention_note"])
        self.assertFalse(receipt["authority_boundary"]["production_question_bank_admission"])
        self.assertFalse(receipt["authority_boundary"]["atlas_rungs_enrichment"])


if __name__ == "__main__":
    unittest.main()
