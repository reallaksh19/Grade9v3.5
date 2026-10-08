"""Negative custody, scope and PDF-source falsifiers for next R4 Q13–Q14 batch."""
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

from Shared.tools import test_source_observation_next, test_source_custody  # noqa: E402

BANK = test_source_observation_next.BANK
LEDGER = test_source_observation_next.LEDGER


class TestNextR4NCERTVisualObservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_bank = json.loads((REPO / BANK).read_text(encoding="utf-8"))
        cls.original_ledger = json.loads((REPO / LEDGER).read_text(encoding="utf-8"))

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.bank_path = self.repo / BANK
        self.ledger_path = self.repo / LEDGER
        self.bank_path.parent.mkdir(parents=True)
        self.ledger_path.parent.mkdir(parents=True)
        self.reset()

    def reset(self):
        self.bank = copy.deepcopy(self.original_bank)
        self.doc = copy.deepcopy(self.original_ledger)
        self.write()

    def write(self):
        self.bank_path.write_text(json.dumps(self.bank, ensure_ascii=False), encoding="utf-8")
        self.ledger_path.write_text(json.dumps(self.doc, ensure_ascii=False), encoding="utf-8")

    def test_exact_four_visual_only_rows_never_supply_custody(self):
        for repo in (REPO, self.repo):
            report = test_source_observation_next.validate(repo)
            self.assertEqual(report["reviewed"], 4)
            self.assertEqual(report["ready_granted"], 0)
            self.assertFalse(report["official_pdf_bytes_authenticated"])
            self.assertEqual(report["source_ids"], [
                f"ncert-exemplar-g9-math-u{unit:02d}-q{i:02d}"
                for unit in (1, 2) for i in (13, 14)
            ])
        original = test_source_custody.reconcile(REPO)
        self.assertEqual((original["ready_for_blueprint"], original["evidence_pending"]),
                         (12, 198))
        self.assertFalse(set(test_source_observation_next.FROZEN_ROWS)
                         & set(original["ready_ids"]))

    def test_reject_coordinated_bank_and_ledger_edits(self):
        for kind in ("stem", "options", "identifier", "source URL", "answer"):
            with self.subTest(kind=kind):
                self.reset()
                r = self.doc["records"][2]
                q = next(q for q in self.bank["questions"] if q["id"] == r["source_id"])
                if kind == "stem":
                    q["stem"] = r["captured_stem"] = "forged polynomial"
                    q["stem_sha256"] = r["stem_sha256"] = "sha256:" + hashlib.sha256(
                        q["stem"].encode("utf-8")).hexdigest()
                elif kind == "options":
                    q["options"][0] = "(A) forged"
                    r["captured_options"] = copy.deepcopy(q["options"])
                elif kind == "identifier":
                    q["original_identifier"] = r["original_identifier"] = "Unit 2 Ex 2.1 Q99"
                elif kind == "source URL":
                    q["source_url"] = r["official_question_document_url"] = (
                        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf"
                    )
                else:
                    q["official_answer_text"] = r["captured_answer"] = q["options"][0]
                    r["official_answer_key"] = "(A)"
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen options, locators, key"):
                    test_source_observation_next.validate(self.repo)

    def test_frozen_url_locator_key_and_math_notation_cannot_drift(self):
        changes = (
            ("question PDF page", lambda d: d["records"][0]["source_locator"].__setitem__("pdf_page_index", 99)),
            ("printed page", lambda d: d["records"][0]["source_locator"].__setitem__("printed_page", 3)),
            ("answer PDF index", lambda d: d["records"][2].__setitem__("official_answer_pdf_page_index", 0)),
            ("answer key", lambda d: d["records"][2].__setitem__("official_answer_key", "(C)")),
            ("radical option", lambda d: d["records"][0]["captured_options"].__setitem__(0, "(A) 1/2")),
            ("exponent option", lambda d: d["records"][2]["captured_options"].__setitem__(1, "(B) x^5")),
            ("review note", lambda d: d["records"][0].__setitem__("comparison_note", "edited")),
        )
        for label, mutate in changes:
            with self.subTest(label=label):
                self.reset()
                mutate(self.doc)
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen options, locators, key"):
                    test_source_observation_next.validate(self.repo)

    def test_no_visual_pdf_observation_can_assert_authority(self):
        changes = (
            ("fabricated SHA", lambda d: d.__setitem__("official_pdf_sha256", "sha256:" + "f" * 64)),
            ("pretend bytes", lambda d: d.__setitem__("official_pdf_bytes_available", True)),
            ("reviewer approval", lambda d: d.__setitem__("independent_custody_witness_authenticated", True)),
            ("READY", lambda d: d.__setitem__("source_custody_promoted", True)),
            ("academic PASS", lambda d: d.__setitem__("academic_status_promoted", True)),
            ("publish", lambda d: d.__setitem__("publication_authorized", True)),
            ("row READY", lambda d: d["records"][0].__setitem__("projection_disposition", "READY_FOR_BLUEPRINT")),
            ("row academic PASS", lambda d: d["records"][0].__setitem__("academic_status_promoted", True)),
            ("injected witness", lambda d: d["records"][0].__setitem__("authenticated", True)),
        )
        for label, mutate in changes:
            with self.subTest(label=label):
                self.reset()
                mutate(self.doc)
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen root|frozen options"):
                    test_source_observation_next.validate(self.repo)

    def test_deletion_duplication_or_redirect_rejects(self):
        changes = (
            ("missing", lambda d: d["records"].pop()),
            ("duplicate", lambda d: d["records"].__setitem__(1, copy.deepcopy(d["records"][0]))),
            ("rewritten source IDs", lambda d: d["records"][0].__setitem__("source_id", "ncert-exemplar-g9-math-u01-q01")),
            ("official answer URL", lambda d: d.__setitem__("answer_document", "https://example.org/key.pdf")),
            ("source observation date", lambda d: d.__setitem__("checked_on", "2026-10-09")),
        )
        for label, mutate in changes:
            with self.subTest(label=label):
                self.reset()
                mutate(self.doc)
                self.write()
                with self.assertRaises(ValueError):
                    test_source_observation_next.validate(self.repo)

    def test_bank_status_promotion_is_rejected_by_intake_registry(self):
        for field, value in (
            ("workflow_status", "READY_FOR_BLUEPRINT"),
            ("wording_custody", "INDEPENDENTLY_EVIDENCED"),
            ("text_verification_status", "TEXT_VERIFIED_AGAINST_OFFICIAL"),
        ):
            with self.subTest(field=field):
                self.reset()
                q = next(q for q in self.bank["questions"]
                         if q["id"] == self.doc["records"][0]["source_id"])
                q[field] = value
                self.write()
                with self.assertRaises(ValueError):
                    test_source_observation_next.validate(self.repo)


if __name__ == "__main__":
    unittest.main()
