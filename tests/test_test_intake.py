"""Unit tests for Stage-1 NCERT/CBSE official question intake tool (Shared/tools/test_intake.py)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import test_intake

SAMPLE_BANK = {
    "schema_version": "grade9v3-test-source-question-intake-v1",
    "bank_id": "math-g9-test-fixture",
    "subject": "Mathematics",
    "grade": 9,
    "source_scope": ["NCERT_OFFICIAL", "CBSE_OFFICIAL"],
    "created_from": "NCERT Exemplar Class IX Mathematics Unit 1",
    "questions": [
        {
            "id": "Q-INTAKE-TEST-001",
            "original_identifier": "Exemplar Unit 1 Q1",
            "stem": "Every rational number is",
            "stem_sha256": test_intake.text_digest("Every rational number is"),
            "source_authority": "NCERT_OFFICIAL",
            "source_kind": "EXEMPLAR",
            "document_title": "NCERT Exemplar Problems - Mathematics Class IX",
            "edition_or_year": "2024-25",
            "source_url": "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf",
            "chapter_or_unit": "Unit 1: Number Systems",
            "exercise_or_section": "Exercise 1.1",
            "question_number": "1",
            "page": 2,
            "capture_method": "VERBATIM_EXTRACTION",
            "wording_custody": "VERBATIM",
            "text_verification_status": "TEXT_VERIFIED_AGAINST_OFFICIAL",
            "last_checked": "2026-10-06",
            "subject": "Mathematics",
            "grade": 9,
            "topic_label": "Chapter 1 : Number System",
            "question_type": "MULTIPLE_CHOICE",
            "options": [
                "(A) a natural number",
                "(B) an integer",
                "(C) a real number",
                "(D) a whole number"
            ],
            "official_answer_available": True,
            "answer_key_locator": "Answers Exercise 1.1 Q1",
            "official_answer_text": "(C)",
            "workflow_status": "READY_FOR_BLUEPRINT"
        }
    ]
}


class TestIntakeValidation(unittest.TestCase):
    def test_valid_bank_passes(self):
        problems = test_intake.check(SAMPLE_BANK)
        self.assertEqual(problems, [])

    def test_digest_mismatch_fails(self):
        bank = json.loads(json.dumps(SAMPLE_BANK))
        bank["questions"][0]["stem"] = "Every rational number is changed"
        problems = test_intake.check(bank)
        self.assertTrue(any("stem_sha256 mismatch" in p for p in problems))

    def test_deferred_academic_field_is_forbidden(self):
        for field in ("difficulty", "band", "qrt_cell", "reasoning_route", "crux_move", "scaffolds"):
            with self.subTest(field=field):
                bank = json.loads(json.dumps(SAMPLE_BANK))
                bank["questions"][0][field] = "forbidden_value"
                problems = test_intake.check(bank)
                self.assertTrue(any("is FORBIDDEN at Stage 1" in p for p in problems))

    def test_ready_for_blueprint_requires_verified_status(self):
        bank = json.loads(json.dumps(SAMPLE_BANK))
        bank["questions"][0]["text_verification_status"] = "CAPTURED_UNVERIFIED"
        problems = test_intake.check(bank)
        self.assertTrue(any("READY_FOR_BLUEPRINT requires text_verification_status" in p for p in problems))

    def test_report_generation(self):
        rep = test_intake.report(SAMPLE_BANK)
        self.assertEqual(rep["total_questions"], 1)
        self.assertEqual(rep["by_topic"]["Chapter 1 : Number System"], 1)
        self.assertEqual(rep["by_authority"]["NCERT_OFFICIAL"], 1)
        self.assertEqual(rep["by_workflow_status"]["READY_FOR_BLUEPRINT"], 1)

    def test_handoff_export(self):
        items = test_intake.handoff(SAMPLE_BANK)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["intake_question_ref"], "Q-INTAKE-TEST-001")
        self.assertEqual(item["stem_sha256"], SAMPLE_BANK["questions"][0]["stem_sha256"])
        self.assertIn("source_identity", item)
        self.assertEqual(item["source_identity"]["source_url"], SAMPLE_BANK["questions"][0]["source_url"])

    def test_duplicate_stem_protocol(self):
        bank = json.loads(json.dumps(SAMPLE_BANK))
        q2 = json.loads(json.dumps(bank["questions"][0]))
        q2["id"] = "Q-INTAKE-TEST-002"
        q2["question_number"] = "2"
        bank["questions"].append(q2)
        # Without DUPLICATE_REVIEW, duplicate stem fails
        problems = test_intake.check(bank)
        self.assertTrue(any("duplicate stem matches" in p for p in problems))

        # With DUPLICATE_REVIEW, duplicate stem is accepted as properly flagged
        q2["workflow_status"] = "DUPLICATE_REVIEW"
        problems = test_intake.check(bank)
        self.assertFalse(any("duplicate stem matches" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
