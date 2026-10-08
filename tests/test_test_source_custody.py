"""Gate 1 / #68: verified evidence augments source IDs, never duplicates them."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_test_question_bank, test_source_custody  # noqa: E402

BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
OVERLAY = "TEST/evidence/source-intake/ncert-exemplar-g9-number-systems-q1-q6.custody.v1.json"
POLY = "TEST/evidence/source-intake/ncert-exemplar-g9-polynomials-q02-q06.custody.v1.json"
Q1_CORRECTED = "TEST/evidence/source-intake/ncert-exemplar-g9-polynomials-q01.custody.v1.json"


class TestSourceCustodyReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((REPO / BANK).read_text(encoding="utf-8"))
        cls.overlay = json.loads((REPO / OVERLAY).read_text(encoding="utf-8"))
        cls.polynomials = json.loads((REPO / POLY).read_text(encoding="utf-8"))
        cls.corrected_q1 = json.loads((REPO / Q1_CORRECTED).read_text(encoding="utf-8"))

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.bank_path = self.repo / BANK
        self.overlay_path = self.repo / OVERLAY
        self.bank_path.parent.mkdir(parents=True, exist_ok=True)
        self.overlay_path.parent.mkdir(parents=True, exist_ok=True)
        self.bank_doc = copy.deepcopy(self.bank)
        self.overlay_doc = copy.deepcopy(self.overlay)
        self.write()

    def write(self):
        self.bank_path.write_text(json.dumps(self.bank_doc, ensure_ascii=False), encoding="utf-8")
        self.overlay_path.write_text(json.dumps(self.overlay_doc, ensure_ascii=False), encoding="utf-8")

    def test_verified_six_reconcile_to_existing_210_without_a_duplicate_bank(self):
        result = test_source_custody.reconcile(self.repo)
        self.assertEqual((result["total_intake"], result["ready_for_blueprint"], result["evidence_pending"]),
                         (210, 6, 204))
        self.assertEqual(result["ready_ids"],
                         [f"ncert-exemplar-g9-math-u01-q{i:02d}" for i in range(1, 7)])
        self.assertNotIn("ncert-exemplar-g9-math-u01-q07", result["ready_ids"])
        self.assertEqual(len({q["intake_question_ref"] for q in result["handoff"]}), 6)
        self.assertEqual(len(build_test_question_bank.payload(self.repo)["banks"][0]["questions"]), 210)
        self.assertEqual(result, test_source_custody.reconcile(self.repo))

    def test_corrected_printed_pdf_locators_supersede_inaccurate_legacy_page(self):
        result = test_source_custody.reconcile(self.repo)
        first = result["handoff"][0]
        sixth = result["handoff"][5]
        self.assertEqual(self.bank_doc["questions"][0]["unverified_legacy_page"], 1)
        self.assertEqual(first["source_locator"]["printed_page"], 2)
        self.assertEqual(first["source_locator"]["pdf_page_index"], 1)
        self.assertEqual(sixth["source_locator"]["printed_page"], 3)
        self.assertEqual(sixth["source_locator"]["pdf_page_index"], 2)
        self.assertNotIn("edition_or_year", first)
        self.assertIn("ieep2an.pdf", first["official_answer_key_ref"]["document_url"])
        self.assertEqual(self.bank_doc["questions"][0]["workflow_status"], "EVIDENCE_PENDING")

    def test_no_overlay_means_no_independently_evidenced_ready_records(self):
        self.overlay_path.unlink()
        result = test_source_custody.reconcile(self.repo)
        self.assertEqual(result["ready_for_blueprint"], 0)
        self.assertEqual(result["evidence_pending"], 210)
        self.assertEqual(result["handoff"], [])

    def test_bad_custody_data_fails_closed(self):
        original = copy.deepcopy(self.overlay_doc)
        alterations = (
            ("wrong digest", lambda x: x["records"][0].__setitem__("stem_sha256", "sha256:" + "0" * 64), "stem digest mismatch"),
            ("option edited", lambda x: x["records"][0]["options"].append("(E) fake"), "identifier/options mismatch"),
            ("wrong source number", lambda x: x["records"][0]["source_locator"].__setitem__("question_number", "999"), "source exercise/number mismatch"),
            ("unofficial mirror", lambda x: x["documents"][0].__setitem__("url", "https://ncert.example.com/ieep201.pdf"), "unofficial document URL"),
            ("wrong answer key", lambda x: x["records"][0]["official_answer"].__setitem__("answer_key", "(A)"), "official answer differs"),
            ("empty answer key", lambda x: x["records"][0]["official_answer"].__setitem__("answer_key", ""), "official answer differs"),
            ("partial answer key", lambda x: x["records"][0]["official_answer"].__setitem__("answer_key", "("), "official answer differs"),
            ("boolean printed page", lambda x: x["records"][0]["source_locator"].__setitem__("printed_page", True), "missing independently checked PDF/printed page"),
            ("boolean PDF page index", lambda x: x["records"][0]["source_locator"].__setitem__("pdf_page_index", True), "missing independently checked PDF/printed page"),
            ("orphan id", lambda x: x["records"][0].__setitem__("id", "not-in-the-210-bank"), "orphan source identity"),
            ("missing verified text", lambda x: x["records"][0].__setitem__("text_verification_status", "CAPTURED_UNVERIFIED"), "independent source/text evidence missing"),
            ("missing witness", lambda x: x["records"][0].pop("verification_evidence_ref"), "independent source/text evidence missing"),
            ("duplicate overlay row", lambda x: x["records"].append(copy.deepcopy(x["records"][0])), "duplicate custody evidence"),
            ("wrong target bank", lambda x: x.__setitem__("source_bank_ref", "TEST/question-bank/intake/unrelated.json"), "bank identity mismatch"),
            ("same doc for answers", lambda x: x["documents"][1].__setitem__("url", x["documents"][0]["url"]), "missing independent official answer-key witness"),
        )
        for label, change, expected in alterations:
            with self.subTest(label=label):
                self.overlay_doc = copy.deepcopy(original)
                change(self.overlay_doc)
                self.write()
                with self.assertRaisesRegex(ValueError, expected):
                    test_source_custody.reconcile(self.repo)

    def test_official_answer_key_is_optional_for_verified_question_readiness(self):
        """Stage-1 question/text readiness does not depend on answer-key publication."""
        for available in (False, True):
            with self.subTest(official_answer_available=available):
                self.overlay_doc["records"][0].pop("official_answer", None)
                first = self.bank_doc["questions"][0]
                first["official_answer_available"] = available
                if not available:
                    first.pop("official_answer_text", None)
                self.write()
                result = test_source_custody.reconcile(self.repo)
                self.assertEqual((result["ready_for_blueprint"], result["evidence_pending"]), (6, 204))
                q1 = next(q for q in result["handoff"] if q["intake_question_ref"] == first["id"])
                self.assertEqual(q1["intake_status"], "READY_FOR_BLUEPRINT")
                self.assertIsNone(q1["official_answer_key_ref"])
                self.assertEqual(q1["official_answer_custody"], "KEY_NOT_EVIDENCED")
                self.assertTrue(all(q["official_answer_key_ref"] is not None
                                    for q in result["handoff"] if q["intake_question_ref"] != first["id"]))
                self.overlay_doc = copy.deepcopy(self.overlay)
                self.bank_doc = copy.deepcopy(self.bank)

    def test_supplied_but_incomplete_answer_custody_is_not_treated_as_absent(self):
        """Partial key objects still fail closed even though omitted keys are allowed."""
        for invalid in ({}, {"answer_key": "(C)"}, {"document_ref": "NCERT-EXEMPLAR-G9-MATH-ANSWERS"}):
            with self.subTest(invalid=invalid):
                self.overlay_doc["records"][0]["official_answer"] = invalid
                self.write()
                with self.assertRaisesRegex(ValueError, "invalid answer custody|missing independent official answer-key witness"):
                    test_source_custody.reconcile(self.repo)
                self.overlay_doc = copy.deepcopy(self.overlay)

    def test_forged_well_formed_github_witness_cannot_promote_ready(self):
        """A shape-valid but nonexistent GitHub pointer is not custody evidence."""
        fake = "github:reallaksh19/Grade9v3.5#129:9999999999"
        for location in ("source_document", "question", "answer_key"):
            with self.subTest(location=location):
                self.overlay_doc = copy.deepcopy(self.overlay)
                if location == "source_document":
                    self.overlay_doc["documents"][0]["verification_evidence_ref"] = fake
                elif location == "question":
                    self.overlay_doc["records"][0]["verification_evidence_ref"] = fake
                else:
                    self.overlay_doc["records"][0]["official_answer"]["verification_evidence_ref"] = fake
                self.write()
                with self.assertRaisesRegex(ValueError, "witness|evidence missing"):
                    test_source_custody.reconcile(self.repo)

    def test_real_witness_for_q1_to_q6_cannot_be_replayed_for_q7(self):
        """Same-worded Q6/Q7 are distinct official source instances."""
        q7 = self.bank_doc["questions"][6]
        self.assertEqual(self.bank_doc["questions"][5]["stem"], q7["stem"])
        forged = copy.deepcopy(self.overlay_doc["records"][5])
        forged.update({
            "id": q7["id"],
            "original_identifier": q7["original_identifier"],
            "stem_sha256": q7["stem_sha256"],
            "options": q7["options"],
        })
        forged["source_locator"]["question_number"] = q7["question_number"]
        forged["official_answer"]["question_number"] = q7["question_number"]
        forged["official_answer"]["answer_key"] = q7["official_answer_text"].split()[0]
        self.overlay_doc["records"].append(forged)
        self.write()
        with self.assertRaisesRegex(ValueError, "question witness scope"):
            test_source_custody.reconcile(self.repo)

    def test_joint_bank_overlay_stem_rewrite_cannot_reuse_old_witness(self):
        """A self-consistent new digest cannot retrofit an older GitHub witness."""
        first = self.bank_doc["questions"][0]
        first["stem"] = "Every rational number is a different statement"
        digest = "sha256:" + hashlib.sha256(first["stem"].encode("utf-8")).hexdigest()
        first["stem_sha256"] = digest
        self.overlay_doc["records"][0]["stem_sha256"] = digest
        self.write()
        with self.assertRaisesRegex(ValueError, "question witness scope"):
            test_source_custody.reconcile(self.repo)

    def test_coordinated_bank_and_overlay_options_rewrite_cannot_reuse_old_witness(self):
        """Matching mutable copies do not constitute independent official-option evidence."""
        first = self.bank_doc["questions"][0]
        first["options"][0] = "(A) forged but structurally plausible option"
        self.overlay_doc["records"][0]["options"] = copy.deepcopy(first["options"])
        self.write()
        with self.assertRaisesRegex(ValueError, "witness options scope"):
            test_source_custody.reconcile(self.repo)

    def test_valid_shape_but_unwitnessed_printed_pdf_page_is_rejected(self):
        """Numeric page checks alone cannot authenticate an official PDF locator."""
        locator = self.overlay_doc["records"][0]["source_locator"]
        locator["printed_page"] = 999
        locator["pdf_page_index"] = 998
        self.write()
        with self.assertRaisesRegex(ValueError, "witness page scope"):
            test_source_custody.reconcile(self.repo)

    def test_source_bank_stem_mutation_invalidates_a_former_witness(self):
        self.bank_doc["questions"][0]["stem"] = "Changed question wording"
        self.write()
        # The intake identity gate rejects altered wording before custody reconciliation.
        with self.assertRaisesRegex(ValueError, "source stem digest does not match wording"):
            test_source_custody.reconcile(self.repo)

    def stage_second_topic(self):
        q1_path = self.repo / Q1_CORRECTED
        q1_path.write_text(json.dumps(self.corrected_q1, ensure_ascii=False), encoding="utf-8")
        other = self.repo / POLY
        other.write_text(json.dumps(self.polynomials, ensure_ascii=False), encoding="utf-8")

    def test_second_topic_q1_reverified_without_academic_promotion(self):
        self.stage_second_topic()
        result = test_source_custody.reconcile(self.repo)
        self.assertEqual((result["total_intake"], result["ready_for_blueprint"],
                          result["source_text_hold"], result["evidence_pending"]), (210, 12, 0, 198))
        self.assertEqual(result["hold_ids"], [])
        self.assertEqual(len([qid for qid in result["ready_ids"] if "-u02-" in qid]), 6)
        q1 = next(q for q in result["handoff"] if q["intake_question_ref"] == "ncert-exemplar-g9-math-u02-q01")
        self.assertEqual(q1["stem"], "Which one of the following is a polynomial?")
        self.assertEqual(q1["official_answer_key_ref"]["answer_key"], "(C)")
        self.assertEqual(q1["source_locator"]["printed_page"], 14)
        self.assertEqual(q1["source_locator"]["pdf_page_index"], 1)
        self.assertTrue(all(v["source_locator"]["printed_page"] == 14
                            and v["source_locator"]["pdf_page_index"] == 1
                            for v in result["handoff"] if "-u02-" in v["intake_question_ref"]))

    def test_later_overlay_cannot_duplicate_corrected_q1_ready_record(self):
        self.stage_second_topic()
        q1 = next(q for q in self.bank_doc["questions"] if q["id"] == "ncert-exemplar-g9-math-u02-q01")
        forged = copy.deepcopy(self.polynomials)
        record = copy.deepcopy(forged["records"][0])
        record.update({
            "id": q1["id"], "original_identifier": q1["original_identifier"],
            "stem_sha256": q1["stem_sha256"], "options": q1["options"],
        })
        record["source_locator"]["question_number"] = q1["question_number"]
        record["official_answer"]["question_number"] = q1["question_number"]
        record["official_answer"]["answer_key"] = "(C)"
        forged["records"], forged["holds"] = [record], []
        later = self.repo / "TEST/evidence/source-intake/zzz-illicit-custody.custody.v1.json"
        later.write_text(json.dumps(forged, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate custody evidence or source-text HOLD"):
            test_source_custody.reconcile(self.repo)

    def test_old_q1_hold_cannot_override_new_verified_source(self):
        self.stage_second_topic()
        historic_hold = {
            "id": "ncert-exemplar-g9-math-u02-q01", "disposition": "SOURCE_TEXT_HOLD",
            "reason_code": "VERBATIM_SOURCE_TEXT_MISMATCH",
            "captured_stem": "Which of the following is a polynomial?",
            "captured_stem_sha256": "sha256:e9cf2f9dd0b4ccdd828e671580c65aed68b09405a1eda4c0f54561b9e24a3175",
            "official_stem": "Which one of the following is a polynomial?",
            "source_document_ref": "NCERT-U02-QUESTION",
            "source_locator": {
                "chapter_or_unit": "Unit 2: Polynomials", "exercise_or_section": "Exercise 2.1",
                "question_number": "1", "printed_page": 14, "pdf_page_index": 1,
            },
            "verification_evidence_ref": "github:reallaksh19/Grade9v3.5#68:6050805060",
        }
        other = self.repo / POLY
        old_overlay = copy.deepcopy(self.polynomials)
        old_overlay["holds"] = [historic_hold]
        other.write_text(json.dumps(old_overlay, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate or READY source-text hold"):
            test_source_custody.reconcile(self.repo)

    def test_academic_receipts_remain_distinct_from_source_custody(self):
        result = test_source_custody.reconcile(REPO)
        projection = build_test_question_bank.payload(REPO)
        self.assertEqual((result["ready_for_blueprint"], result["source_text_hold"], result["evidence_pending"]), (12, 0, 198))
        self.assertEqual(projection["validation_counts"], {"HOLD": 1, "UNVALIDATED": 151, "VALIDATED": 58})
        self.assertEqual(result["total_intake"], 210)
        question = next(q for bank in projection["banks"] for q in bank["questions"]
                        if q["id"] == "ncert-exemplar-g9-math-u02-q01")
        self.assertEqual(question["academic_validation_status"], "UNVALIDATED")
        self.assertIsNone(question["academic_validation_receipt"])


if __name__ == "__main__":
    unittest.main()
