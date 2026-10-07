"""Focused regressions for the TEST-only NCERT Exemplar Question Bank projection."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_question_bank_web, build_test_question_bank  # noqa: E402

INTAKE = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
PUBLIC_PAGE = REPO / "public/test/question-bank/index.html"
PUBLIC_DATA = REPO / "public/test/question-bank/questions.js"
DOCS_PAGE = REPO / "docs/test/question-bank/index.html"
DOCS_DATA = REPO / "docs/test/question-bank/questions.js"


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


if __name__ == "__main__":
    unittest.main()
