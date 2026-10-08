"""Focused regressions for the TEST-only NCERT Exemplar Question Bank projection."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
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
VALIDATION_RECEIPTS = [
    REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q01-q10.validation.json",
    REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q11-q20.validation.json",
    REPO / "TEST/candidates/ncert-exemplar-g9-math-u02-q21-q30.validation.json",
]
NUMBER_SYSTEMS_VALIDATION = REPO / "TEST/candidates/ncert-exemplar-g9-math-u01-q01-q10.validation.json"
NUMBER_SYSTEMS_VALIDATION_Q11_Q20 = REPO / "TEST/candidates/ncert-exemplar-g9-math-u01-q11-q20.validation.json"
NUMBER_SYSTEMS_VALIDATION_Q21_Q30 = REPO / "TEST/candidates/ncert-exemplar-g9-math-u01-q21-q30.validation.json"


class TestTestQuestionBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(INTAKE.read_text(encoding="utf-8"))
        cls.questions = cls.bank["questions"]
        cls.ids = {row["id"] for row in cls.questions}

    def test_projection_contains_all_210_with_per_question_validation(self):
        projection = build_test_question_bank.payload(REPO)
        rows = [q for bank in projection["banks"] for q in bank["questions"]]
        self.assertEqual(len(rows), 210)
        self.assertEqual(len({q["id"] for q in rows}), 210)
        self.assertEqual(projection["academic_validation_status"], "PER_QUESTION")
        self.assertEqual(projection["validation_counts"], {"HOLD": 1, "UNVALIDATED": 151, "VALIDATED": 58})
        self.assertTrue(all(q["workflow_status"] == "EVIDENCE_PENDING" for q in rows))
        self.assertTrue(all(q["text_verification_status"] == "CAPTURED_UNVERIFIED" for q in rows))
        self.assertTrue(all(q["wording_custody"] == "CAPTURED_UNVERIFIED" for q in rows))
        self.assertTrue(all("page" not in q and "unverified_legacy_page" in q for q in rows))
        self.assertEqual(sum(q["custody_evidence_status"] == "INDEPENDENTLY_EVIDENCED"
                             for q in rows), 12)
        self.assertEqual(sum(q["academic_validation_status"] == "VALIDATED" for q in rows), 58)
        self.assertEqual(sum(q["academic_validation_status"] == "UNVALIDATED" for q in rows), 151)
        self.assertEqual(sum(q["academic_validation_status"] == "HOLD" for q in rows), 1)
        validated = {q["id"] for q in rows if q["academic_validation_status"] == "VALIDATED"}
        expected_validated = {f"ncert-exemplar-g9-math-u02-q{number:02d}" for number in range(1, 31)}
        expected_validated.remove("ncert-exemplar-g9-math-u02-q23")
        expected_validated.remove("ncert-exemplar-g9-math-u02-q01")
        expected_validated |= {f"ncert-exemplar-g9-math-u01-q{number:02d}" for number in range(1, 31)}
        self.assertEqual(validated, expected_validated)
        held = {q["id"] for q in rows if q["academic_validation_status"] == "HOLD"}
        self.assertEqual(held, {"ncert-exemplar-g9-math-u02-q23"})
        self.assertEqual(sum(q["workflow_status"] == "DUPLICATE_REVIEW" for q in rows), 0)

    def test_custody_evidence_is_separate_from_legacy_source_and_academic_states(self):
        projection = build_test_question_bank.payload(REPO)
        self.assertEqual(projection["custody_evidence_counts"],
                         {"EVIDENCE_PENDING": 198, "INDEPENDENTLY_EVIDENCED": 12, "SOURCE_TEXT_HOLD": 0})
        rows = [q for bank in projection["banks"] for q in bank["questions"]]
        self.assertEqual(len(rows), 210)
        evidenced = [q for q in rows if q["custody_evidence_status"] == "INDEPENDENTLY_EVIDENCED"]
        self.assertEqual({q["id"] for q in evidenced},
                         {f"ncert-exemplar-g9-math-u01-q{i:02d}" for i in range(1, 7)} |
                         {f"ncert-exemplar-g9-math-u02-q{i:02d}" for i in range(1, 7)})
        for q in evidenced:
            self.assertIsNotNone(q["custody_source_locator"])
            self.assertIn("ieep20", q["custody_question_source_url"])
            self.assertIn("ieep2an.pdf", q["custody_answer_source_url"])
            self.assertTrue("#129:" in q["custody_evidence_ref"] or "#68:" in q["custody_evidence_ref"])
        pending = [q for q in rows if q["custody_evidence_status"] == "EVIDENCE_PENDING"]
        self.assertEqual(len(pending), 198)
        held = [q for q in rows if q["custody_evidence_status"] == "SOURCE_TEXT_HOLD"]
        self.assertEqual(held, [])
        self.assertTrue(all(q["custody_source_locator"] is None for q in held))
        self.assertTrue(all(q["custody_source_locator"] is None for q in pending))
        self.assertTrue(all(q["custody_evidence_ref"] is None for q in pending))
        self.assertTrue(all(q["custody_answer_source_url"] is None for q in pending))
        self.assertEqual(projection["validation_counts"], {"HOLD": 1, "UNVALIDATED": 151, "VALIDATED": 58})
        self.assertIn("independent source evidence", build_test_question_bank.render_page(REPO))
        corrected_q1 = next(q for q in rows if q["id"] == "ncert-exemplar-g9-math-u02-q01")
        self.assertEqual(corrected_q1["academic_validation_status"], "UNVALIDATED")
        self.assertIsNone(corrected_q1["academic_validation_receipt"])
        self.assertEqual(corrected_q1["custody_evidence_status"], "INDEPENDENTLY_EVIDENCED")
        self.assertIn('target="_blank" rel="noopener noreferrer"', build_test_question_bank.render_page(REPO))

    def test_shell_makes_source_and_academic_states_distinct(self):
        page = build_test_question_bank.render_page(REPO)
        self.assertIn("SOURCE VERIFIED", page)
        self.assertIn("UNVALIDATED", page)
        self.assertIn("VALIDATED", page)
        self.assertIn("DUPLICATE REVIEW", page)
        self.assertIn("questions.js", page)
        self.assertIn("Production admission is governed separately.", page)
        self.assertIn('data-g9-test="sandbox-draft"', page)
        self.assertNotRegex(page, r"https?://")

    def test_committed_public_and_pages_outputs_are_current(self):
        self.assertEqual(PUBLIC_PAGE.read_text(encoding="utf-8"), build_test_question_bank.render_page(REPO))
        self.assertEqual(PUBLIC_DATA.read_text(encoding="utf-8"), build_test_question_bank.render_data(REPO))
        self.assertEqual(DOCS_PAGE.read_bytes(), PUBLIC_PAGE.read_bytes())
        self.assertEqual(DOCS_DATA.read_bytes(), PUBLIC_DATA.read_bytes())

    def test_historical_academic_receipt_cannot_validate_a_rewritten_source_instance(self):
        receipt = json.loads(NUMBER_SYSTEMS_VALIDATION.read_text(encoding="utf-8"))
        receipt["records"] = [receipt["records"][0]]
        original = copy.deepcopy(self.questions[0])
        with tempfile.TemporaryDirectory() as folder:
            tmp = Path(folder)
            bank_dir = tmp / "TEST/question-bank/intake"
            candidates = tmp / "TEST/candidates"
            bank_dir.mkdir(parents=True)
            candidates.mkdir(parents=True)
            bank_path = bank_dir / "ncert-cbse-math-g9-pilot.json"
            receipt_path = candidates / "number-systems-q01.validation.json"
            receipt_path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")

            def projected(question):
                bank = copy.deepcopy(self.bank)
                bank["questions"] = [question]
                bank_path.write_text(json.dumps(bank, ensure_ascii=False), encoding="utf-8")
                return build_test_question_bank.payload(tmp)["banks"][0]["questions"][0]

            self.assertEqual(projected(original)["academic_validation_status"], "VALIDATED")
            options_changed = copy.deepcopy(original)
            options_changed["options"][0] = "(A) a changed natural number"
            self.assertEqual(projected(options_changed)["academic_validation_status"], "UNVALIDATED")
            answer_changed = copy.deepcopy(original)
            answer_changed["official_answer_text"] = "(A) a natural number"
            receipt["records"][0]["official_answer_text"] = answer_changed["official_answer_text"]
            receipt_path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(projected(answer_changed)["academic_validation_status"], "UNVALIDATED")

    def test_source_intake_ids_remain_out_of_production_question_bank_and_search(self):
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

    def test_polynomial_validation_receipts_are_source_bound_and_non_publishing(self):
        schema = json.loads(VALIDATION_SCHEMA.read_text(encoding="utf-8"))
        source = {row["id"]: row for row in self.questions}
        seen = []

        for index, path in enumerate(VALIDATION_RECEIPTS):
            receipt = json.loads(path.read_text(encoding="utf-8"))
            errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path))
            self.assertEqual([error.message for error in errors], [], path.name)

            start = index * 10 + 1
            expected_ids = [f"ncert-exemplar-g9-math-u02-q{number:02d}" for number in range(start, start + 10)]
            rows = receipt["records"]
            self.assertEqual([row["source_id"] for row in rows], expected_ids)
            seen.extend(expected_ids)

            for row in rows:
                original = source[row["source_id"]]
                self.assertEqual(row["original_identifier"], original["original_identifier"])
                if row["source_id"] == "ncert-exemplar-g9-math-u02-q01":
                    # Historical academic PASS still binds the superseded capture,
                    # and therefore must NOT be applied to corrected official wording.
                    self.assertNotEqual(row["stem_sha256"], original["stem_sha256"])
                else:
                    self.assertEqual(row["stem_sha256"], original["stem_sha256"])
                # The academic receipt preserves its historical capture claim;
                # the source bank is now explicitly unverified until custody is joined.
                self.assertEqual(row["source_text_verification"], "TEXT_VERIFIED_AGAINST_OFFICIAL")
                self.assertEqual(original["text_verification_status"], "CAPTURED_UNVERIFIED")
                self.assertEqual(row["official_answer_text"], original["official_answer_text"])
                self.assertEqual(row["official_answer_locator"], original["answer_key_locator"])
                validation = row["academic_validation"]
                self.assertTrue(validation["reasoning"])
                if row["source_id"] == "ncert-exemplar-g9-math-u02-q23":
                    self.assertEqual(validation["status"], "HOLD")
                    self.assertFalse(validation["admission_eligible"])
                    self.assertNotEqual(validation["independent_result"], original["official_answer_text"])
                    self.assertIn("wording/key conflict", validation["convention_note"].lower())
                else:
                    self.assertEqual(validation["status"], "PASS")
                    self.assertTrue(validation["admission_eligible"])
                    self.assertEqual(validation["independent_result"], original["official_answer_text"])

            self.assertFalse(receipt["authority_boundary"]["production_question_bank_admission"])
            self.assertFalse(receipt["authority_boundary"]["atlas_rungs_enrichment"])

        self.assertEqual(seen, [f"ncert-exemplar-g9-math-u02-q{number:02d}" for number in range(1, 31)])
        first = json.loads(VALIDATION_RECEIPTS[0].read_text(encoding="utf-8"))["records"][0]["academic_validation"]
        self.assertIn("convention_note", first)
        self.assertIn("x = 0", first["convention_note"])


    def test_number_systems_q01_q10_validation_receipt_is_source_bound_and_resolves_duplicate_review(self):
        schema = json.loads(VALIDATION_SCHEMA.read_text(encoding="utf-8"))
        receipt = json.loads(NUMBER_SYSTEMS_VALIDATION.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path))
        self.assertEqual([error.message for error in errors], [])

        expected_ids = [f"ncert-exemplar-g9-math-u01-q{number:02d}" for number in range(1, 11)]
        rows = receipt["records"]
        self.assertEqual([row["source_id"] for row in rows], expected_ids)
        source = {row["id"]: row for row in self.questions}

        for row in rows:
            original = source[row["source_id"]]
            self.assertEqual(row["original_identifier"], original["original_identifier"])
            self.assertEqual(row["stem_sha256"], original["stem_sha256"])
            # Preserve immutable academic receipt's historical claim without granting custody.
            self.assertEqual(row["source_text_verification"], "TEXT_VERIFIED_AGAINST_OFFICIAL")
            self.assertEqual(original["text_verification_status"], "CAPTURED_UNVERIFIED")
            self.assertEqual(row["official_answer_text"], original["official_answer_text"])
            self.assertEqual(row["official_answer_locator"], original["answer_key_locator"])
            validation = row["academic_validation"]
            self.assertEqual(validation["status"], "PASS")
            self.assertTrue(validation["admission_eligible"])
            self.assertEqual(validation["independent_result"], original["official_answer_text"])
            self.assertTrue(validation["reasoning"])

        q6 = source["ncert-exemplar-g9-math-u01-q06"]
        q7 = source["ncert-exemplar-g9-math-u01-q07"]
        self.assertEqual(q6["stem_sha256"], q7["stem_sha256"])
        self.assertNotEqual(q6["options"], q7["options"])
        self.assertEqual(q7["workflow_status"], "EVIDENCE_PENDING")
        q7_validation = rows[6]["academic_validation"]
        self.assertIn("stem-only digest collision", q7_validation["convention_note"])
        self.assertIn("not duplicate items", q7_validation["convention_note"])
        self.assertFalse(receipt["authority_boundary"]["production_question_bank_admission"])
        self.assertFalse(receipt["authority_boundary"]["atlas_rungs_enrichment"])

    def test_number_systems_q11_q20_validation_receipt_is_source_bound_and_non_publishing(self):
        schema = json.loads(VALIDATION_SCHEMA.read_text(encoding="utf-8"))
        receipt = json.loads(NUMBER_SYSTEMS_VALIDATION_Q11_Q20.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path))
        self.assertEqual([error.message for error in errors], [])

        expected_ids = [f"ncert-exemplar-g9-math-u01-q{number:02d}" for number in range(11, 21)]
        rows = receipt["records"]
        self.assertEqual([row["source_id"] for row in rows], expected_ids)
        source = {row["id"]: row for row in self.questions}

        for row in rows:
            original = source[row["source_id"]]
            self.assertEqual(row["original_identifier"], original["original_identifier"])
            self.assertEqual(row["stem_sha256"], original["stem_sha256"])
            # Preserve immutable academic receipt's historical claim without granting custody.
            self.assertEqual(row["source_text_verification"], "TEXT_VERIFIED_AGAINST_OFFICIAL")
            self.assertEqual(original["text_verification_status"], "CAPTURED_UNVERIFIED")
            self.assertEqual(row["official_answer_text"], original["official_answer_text"])
            self.assertEqual(row["official_answer_locator"], original["answer_key_locator"])
            validation = row["academic_validation"]
            self.assertEqual(validation["status"], "PASS")
            self.assertTrue(validation["admission_eligible"])
            self.assertEqual(validation["independent_result"], original["official_answer_text"])
            self.assertTrue(validation["reasoning"])

        self.assertFalse(receipt["authority_boundary"]["production_question_bank_admission"])
        self.assertFalse(receipt["authority_boundary"]["atlas_rungs_enrichment"])

    def test_number_systems_q21_q30_validation_receipt_is_source_bound_and_non_publishing(self):
        schema = json.loads(VALIDATION_SCHEMA.read_text(encoding="utf-8"))
        receipt = json.loads(NUMBER_SYSTEMS_VALIDATION_Q21_Q30.read_text(encoding="utf-8"))
        errors = sorted(Draft202012Validator(schema).iter_errors(receipt), key=lambda e: list(e.path))
        self.assertEqual([error.message for error in errors], [])

        expected_ids = [f"ncert-exemplar-g9-math-u01-q{number:02d}" for number in range(21, 31)]
        rows = receipt["records"]
        self.assertEqual([row["source_id"] for row in rows], expected_ids)
        source = {row["id"]: row for row in self.questions}

        for row in rows:
            original = source[row["source_id"]]
            self.assertEqual(row["original_identifier"], original["original_identifier"])
            self.assertEqual(row["stem_sha256"], original["stem_sha256"])
            # Preserve immutable academic receipt's historical claim without granting custody.
            self.assertEqual(row["source_text_verification"], "TEXT_VERIFIED_AGAINST_OFFICIAL")
            self.assertEqual(original["text_verification_status"], "CAPTURED_UNVERIFIED")
            self.assertEqual(row["official_answer_text"], original["official_answer_text"])
            self.assertEqual(row["official_answer_locator"], original["answer_key_locator"])
            validation = row["academic_validation"]
            self.assertEqual(validation["status"], "PASS")
            self.assertTrue(validation["admission_eligible"])
            self.assertEqual(validation["independent_result"], original["official_answer_text"])
            self.assertTrue(validation["reasoning"])

        q21 = rows[0]["academic_validation"]
        self.assertIn("real-domain", q21["convention_note"])
        self.assertIn("negative real x", q21["convention_note"])
        self.assertFalse(receipt["authority_boundary"]["production_question_bank_admission"])
        self.assertFalse(receipt["authority_boundary"]["atlas_rungs_enrichment"])


if __name__ == "__main__":
    unittest.main()
