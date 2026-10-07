from __future__ import annotations

import copy
import unittest

from TEST.tools import source_intake


SOURCE_URL = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf"
ANSWER_URL = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf"


def valid_bank() -> dict:
    stem = "Every rational number is"
    return {
        "schema_version": source_intake.SCHEMA_VERSION,
        "bank_id": "ncert-g9-number-systems-pilot",
        "subject": "Mathematics",
        "grade": 9,
        "source_scope": ["NCERT_OFFICIAL"],
        "created_from": "NCERT Exemplar Class IX Mathematics, Exercise 1.1",
        "documents": [
            {
                "id": "NCERT-EXEMPLAR-G9-MATH-U01",
                "authority": "NCERT_OFFICIAL",
                "kind": "EXEMPLAR",
                "role": "QUESTION_SOURCE",
                "title": "NCERT Exemplar Problems — Mathematics Class IX, Unit 1",
                "url": SOURCE_URL,
                "verified_on": "2026-10-07",
                "verification_evidence_ref": "github:Grade9v3.5#129:6028788367",
            },
            {
                "id": "NCERT-EXEMPLAR-G9-MATH-ANSWERS",
                "authority": "NCERT_OFFICIAL",
                "kind": "EXEMPLAR",
                "role": "ANSWER_KEY",
                "title": "NCERT Exemplar Class IX Mathematics — Answers",
                "url": ANSWER_URL,
                "verified_on": "2026-10-07",
                "verification_evidence_ref": "github:Grade9v3.5#129:6028808520",
            },
        ],
        "questions": [
            {
                "id": "ncert-exemplar-g9-math-u01-q01",
                "original_identifier": "Unit 1 Ex 1.1 Q1",
                "stem": stem,
                "stem_sha256": source_intake.text_digest(stem),
                "source_document_ref": "NCERT-EXEMPLAR-G9-MATH-U01",
                "source_locator": {
                    "chapter_or_unit": "Unit 1: Number Systems",
                    "exercise_or_section": "Exercise 1.1",
                    "question_number": "1",
                    "printed_page": 2,
                    "pdf_page_index": 1,
                },
                "capture_method": "OFFICIAL_PDF_VERIFIED_TRANSCRIPTION",
                "wording_custody": "VERBATIM",
                "source_verification_status": "SOURCE_VERIFIED_OFFICIAL",
                "text_verification_status": "TEXT_VERIFIED_AGAINST_OFFICIAL",
                "verification_evidence_ref": "github:Grade9v3.5#129:6028788367",
                "subject": "Mathematics",
                "grade": 9,
                "topic_label": "Number System",
                "subtopic_label": "Rational Numbers",
                "question_type": "MULTIPLE_CHOICE",
                "options": ["(A) a natural number", "(B) an integer", "(C) a real number", "(D) a whole number"],
                "official_answer_available": True,
                "official_answer": {
                    "document_ref": "NCERT-EXEMPLAR-G9-MATH-ANSWERS",
                    "exercise_or_section": "Exercise 1.1",
                    "question_number": "1",
                    "answer_key": "(C)",
                    "verification_evidence_ref": "github:Grade9v3.5#129:6028808520",
                },
                "workflow_status": "READY_FOR_BLUEPRINT",
            }
        ],
    }


class TestTestSourceIntake(unittest.TestCase):
    def test_valid_ready_record_passes_and_handoff_is_source_only(self):
        bank = valid_bank()
        self.assertEqual(source_intake.findings(bank), [])
        rows = source_intake.handoff(bank)
        self.assertEqual([r["intake_question_ref"] for r in rows], ["ncert-exemplar-g9-math-u01-q01"])
        self.assertEqual(rows[0]["source_locator"]["printed_page"], 2)
        self.assertEqual(rows[0]["official_answer"]["answer_key"], "(C)")
        for forbidden in ("difficulty", "qrt", "capability", "crux", "accepted", "worked_solution"):
            self.assertNotIn(forbidden, rows[0])

    def test_ready_requires_verified_source_text_and_evidence(self):
        bank = valid_bank()
        q = bank["questions"][0]
        q["source_verification_status"] = "CAPTURED_UNVERIFIED"
        q["text_verification_status"] = "CAPTURED_UNVERIFIED"
        q["verification_evidence_ref"] = ""
        problems = "\n".join(source_intake.findings(bank))
        self.assertIn("requires SOURCE_VERIFIED_OFFICIAL", problems)
        self.assertIn("requires TEXT_VERIFIED_AGAINST_OFFICIAL", problems)
        self.assertIn("verification evidence", problems)

    def test_bad_stem_digest_fails(self):
        bank = valid_bank()
        bank["questions"][0]["stem"] += " changed"
        self.assertIn("stem_sha256 does not match exact stem bytes", "\n".join(source_intake.findings(bank)))

    def test_third_party_source_cannot_claim_ncert_authority(self):
        bank = valid_bank()
        bank["documents"][0]["url"] = "https://example.com/copied.pdf"
        self.assertIn("not on an allowed official NCERT_OFFICIAL host", "\n".join(source_intake.findings(bank)))

    def test_duplicate_source_instance_fails_closed(self):
        bank = valid_bank()
        duplicate = copy.deepcopy(bank["questions"][0])
        duplicate["id"] = "ncert-exemplar-g9-math-u01-q01-copy"
        bank["questions"].append(duplicate)
        self.assertIn("duplicate source instance", "\n".join(source_intake.findings(bank)))

    def test_hold_record_is_inspectable_but_excluded_from_handoff(self):
        bank = valid_bank()
        q = bank["questions"][0]
        q["source_verification_status"] = "SOURCE_HOLD"
        q["text_verification_status"] = "TEXT_HOLD"
        q["workflow_status"] = "SOURCE_HOLD"
        self.assertEqual(source_intake.findings(bank), [])
        self.assertEqual(source_intake.handoff(bank), [])

    def test_stage1_schema_rejects_academic_analysis_fields(self):
        bank = valid_bank()
        bank["questions"][0]["difficulty"] = {"band": "D2"}
        problems = "\n".join(source_intake.findings(bank))
        self.assertIn("difficulty", problems)
        self.assertIn("Additional properties are not allowed", problems)


if __name__ == "__main__":
    unittest.main()
