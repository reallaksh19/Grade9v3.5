"""R4 four-row NCERT rendered-PDF observations are historical, non-promoting data."""
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

from Shared.tools import test_source_observation, test_source_custody  # noqa: E402

BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
OBS = test_source_observation.FILE


class TestFourRowOfficialPDFObservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_bank = json.loads((REPO / BANK).read_text(encoding="utf-8"))
        cls.original_observation = json.loads((REPO / OBS).read_text(encoding="utf-8"))

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.bank_file = self.repo / BANK
        self.observation_file = self.repo / OBS
        self.bank_file.parent.mkdir(parents=True)
        self.observation_file.parent.mkdir(parents=True)
        self.reset()

    def reset(self):
        self.bank = copy.deepcopy(self.original_bank)
        self.data = copy.deepcopy(self.original_observation)
        self.write()

    def write(self):
        self.bank_file.write_text(json.dumps(self.bank, ensure_ascii=False), encoding="utf-8")
        self.observation_file.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_exact_four_row_two_topic_observation_is_visual_only(self):
        for repo in (REPO, self.repo):
            result = test_source_observation.validate(repo)
            self.assertEqual(result["reviewed"], 4)
            self.assertEqual(result["ready_granted"], 0)
            self.assertFalse(result["official_pdf_bytes_available"])
            self.assertEqual(result["review_ids"],
                             [f"ncert-exemplar-g9-math-u{unit:02d}-q{i:02d}"
                              for unit in (1, 2) for i in (11, 12)])
        result = test_source_observation.validate(REPO)
        self.assertEqual(len(result["source_pending"]), 4)
        self.assertFalse(result["separately_ready"])
        custody = test_source_custody.reconcile(REPO)
        self.assertEqual((custody["ready_for_blueprint"], custody["evidence_pending"]),
                         (12, 198))

    def test_mutating_frozen_record_or_locator_is_rejected(self):
        variants = [
            ("option", lambda d: d["records"][0]["captured_options"].__setitem__(0, "(A) fake")),
            ("stem digest", lambda d: d["records"][0].__setitem__("stem_sha256", "sha256:" + "0" * 64)),
            ("key", lambda d: d["records"][0].__setitem__("official_answer_key", "(D)")),
            ("printed page", lambda d: d["records"][0]["source_locator"].__setitem__("printed_page", 5)),
            ("PDF index", lambda d: d["records"][2]["source_locator"].__setitem__("pdf_page_index", 3)),
            ("answer index", lambda d: d["records"][2].__setitem__("official_answer_pdf_page_index", 0)),
            ("note", lambda d: d["records"][0].__setitem__("comparison_note", "rewritten")),
        ]
        for label, change in variants:
            with self.subTest(label=label):
                self.reset()
                change(self.data)
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen rendered-page observation"):
                    test_source_observation.validate(self.repo)

    def test_coordinated_source_and_ledger_rewrite_still_rejected(self):
        for label in ("stem", "options", "source URL", "answer", "original identifier"):
            with self.subTest(label=label):
                self.reset()
                r = self.data["records"][2]  # Polynomials Q11
                q = next(q for q in self.bank["questions"] if q["id"] == r["source_id"])
                if label == "stem":
                    q["stem"] += " forged"
                    q["stem_sha256"] = "sha256:" + hashlib.sha256(
                        q["stem"].encode("utf-8")).hexdigest()
                    r["captured_stem"] = q["stem"]
                    r["stem_sha256"] = q["stem_sha256"]
                elif label == "options":
                    q["options"][0] = "(A) 999"
                    r["captured_options"] = list(q["options"])
                elif label == "source URL":
                    q["source_url"] = r["official_question_document_url"] = (
                        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf"
                    )
                elif label == "answer":
                    q["official_answer_text"] = q["options"][2]
                    r["official_answer_key"] = "(C)"
                    r["captured_answer"] = q["official_answer_text"]
                else:
                    q["original_identifier"] = "Unit 2 Ex 2.1 Q111"
                    r["original_identifier"] = q["original_identifier"]
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen rendered-page observation"):
                    test_source_observation.validate(self.repo)

    def test_visual_review_cannot_claim_pdf_custody_or_new_authority(self):
        variants = [
            ("PDF bytes", lambda d: d.__setitem__("official_pdf_bytes_available", True)),
            ("made-up sha", lambda d: d.__setitem__("official_pdf_sha256", "sha256:" + "f" * 64)),
            ("authenticated", lambda d: d.__setitem__("independent_custody_witness_authenticated", True)),
            ("source READY", lambda d: d.__setitem__("source_custody_promoted", True)),
            ("academic PASS", lambda d: d.__setitem__("academic_status_promoted", True)),
            ("publish", lambda d: d.__setitem__("publication_authorized", True)),
            ("row READY", lambda d: d["records"][0].__setitem__("projection_disposition", "READY_FOR_BLUEPRINT")),
            ("row academic PASS", lambda d: d["records"][0].__setitem__("academic_status_promoted", True)),
            ("silent promoted flag", lambda d: d["records"][0].__setitem__("ready_for_blueprint", True)),
        ]
        for label, change in variants:
            with self.subTest(label=label):
                self.reset()
                change(self.data)
                self.write()
                with self.assertRaisesRegex(ValueError, "observation .*|visual observation cannot"):
                    test_source_observation.validate(self.repo)

    def test_scope_cannot_be_deleted_duplicated_or_redirected(self):
        variants = [
            ("deleted", lambda d: d["records"].pop()),
            ("duplicate", lambda d: d["records"].__setitem__(1, copy.deepcopy(d["records"][0]))),
            ("untrusted URL", lambda d: d["question_documents"].__setitem__(0, "https://example.org/x.pdf")),
            ("untrusted key", lambda d: d.__setitem__("answer_document", "https://example.org/key.pdf")),
            ("changed date", lambda d: d.__setitem__("checked_on", "2026-10-09")),
            ("relabel scope", lambda d: d.__setitem__("scope", "VERIFIED")),
            ("document sha claim", lambda d: d.__setitem__("document_sha256", "x")),
        ]
        for label, change in variants:
            with self.subTest(label=label):
                self.reset()
                change(self.data)
                self.write()
                with self.assertRaises(ValueError):
                    test_source_observation.validate(self.repo)

    def test_raw_intake_cannot_be_qualified_by_observation(self):
        for field, value in [
            ("workflow_status", "READY_FOR_BLUEPRINT"),
            ("text_verification_status", "TEXT_VERIFIED_AGAINST_OFFICIAL"),
            ("wording_custody", "INDEPENDENTLY_EVIDENCED"),
        ]:
            with self.subTest(field=field):
                self.reset()
                q = next(q for q in self.bank["questions"]
                         if q["id"] == self.data["records"][0]["source_id"])
                q[field] = value
                self.write()
                with self.assertRaisesRegex(ValueError, "raw capture cannot|raw intake must not inherit"):
                    test_source_observation.validate(self.repo)


if __name__ == "__main__":
    unittest.main()
