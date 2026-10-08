"""Gate 1 / #68: verified evidence augments source IDs, never duplicates them."""
from __future__ import annotations

import copy
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


class TestSourceCustodyReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((REPO / BANK).read_text(encoding="utf-8"))
        cls.overlay = json.loads((REPO / OVERLAY).read_text(encoding="utf-8"))

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
        self.assertEqual(self.bank_doc["questions"][0]["page"], 1)
        self.assertEqual(first["source_locator"]["printed_page"], 2)
        self.assertEqual(first["source_locator"]["pdf_page_index"], 1)
        self.assertEqual(sixth["source_locator"]["printed_page"], 3)
        self.assertEqual(sixth["source_locator"]["pdf_page_index"], 2)
        self.assertNotIn("edition_or_year", first)
        self.assertIn("ieep2an.pdf", first["official_answer_key_ref"]["document_url"])
        self.assertEqual(self.bank_doc["questions"][0]["workflow_status"], "READY_FOR_BLUEPRINT")

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

    def test_source_bank_stem_mutation_invalidates_a_former_witness(self):
        self.bank_doc["questions"][0]["stem"] = "Changed question wording"
        self.write()
        with self.assertRaisesRegex(ValueError, "stem digest mismatch"):
            test_source_custody.reconcile(self.repo)

    def test_academic_receipts_remain_distinct_from_source_custody(self):
        result = test_source_custody.reconcile(REPO)
        projection = build_test_question_bank.payload(REPO)
        self.assertEqual((result["ready_for_blueprint"], result["evidence_pending"]), (6, 204))
        self.assertEqual(projection["validation_counts"], {"HOLD": 1, "UNVALIDATED": 150, "VALIDATED": 59})
        self.assertEqual(result["total_intake"], 210)


if __name__ == "__main__":
    unittest.main()
