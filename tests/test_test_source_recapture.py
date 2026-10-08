"""Issue #68 R4: Q7 source-notation proposal is specific and non-promoting."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import test_source_recapture, test_source_custody  # noqa: E402

BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
REVIEW = test_source_recapture.REVIEW
PROPOSAL = test_source_recapture.PROPOSAL
APPLIED = test_source_recapture.APPLIED
QID = test_source_recapture.QID


class TestNcertQ7RecaptureProposal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((REPO / BANK).read_text(encoding="utf-8"))
        cls.review = json.loads((REPO / REVIEW).read_text(encoding="utf-8"))
        cls.proposal = json.loads((REPO / PROPOSAL).read_text(encoding="utf-8"))
        cls.applied = json.loads((REPO / APPLIED).read_text(encoding="utf-8"))

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.data = copy.deepcopy(self.proposal)
        self.applied_data = copy.deepcopy(self.applied)
        for path, data in ((BANK, self.bank), (REVIEW, self.review)):
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        self.write_proposal()
        self.write_applied()

    def write_applied(self):
        path = self.repo / APPLIED
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.applied_data, ensure_ascii=False), encoding="utf-8")

    def write_proposal(self):
        path = self.repo / PROPOSAL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_current_source_notation_is_directly_reviewed_and_not_admitted(self):
        result = test_source_recapture.validate(self.repo)
        self.assertEqual(result["source_id"], QID)
        self.assertEqual(result["historical_review_rows"], 8)
        self.assertEqual(result["recapture_proposals"], 1)
        self.assertEqual(result["recaptures_applied"], 1)
        self.assertEqual(result["ready_granted"], 0)
        self.assertNotIn(QID, test_source_custody.reconcile(REPO)["ready_ids"])
        self.assertEqual(test_source_custody.reconcile(REPO)["ready_for_blueprint"], 12)
        self.assertEqual(test_source_custody.reconcile(REPO)["evidence_pending"], 198)
        self.assertEqual(self.data["proposed_tex_options"][1], "(B) 0.14\\overline{16}")
        self.assertEqual(self.data["proposed_tex_options"][2], "(C) 0.\\overline{1416}")
        self.assertEqual(self.applied_data["current_options"][1], "(B) 0.141\u03056\u0305")
        self.assertEqual(self.applied_data["current_options"][2], "(C) 0.1\u03054\u03051\u03056\u0305")

    def test_mutating_original_review_or_source_cannot_reuse_proposal(self):
        for variant in ("original options", "review options", "source stem"):
            with self.subTest(variant=variant):
                src = copy.deepcopy(self.bank)
                rev = copy.deepcopy(self.review)
                bankrow = next(r for r in src["questions"] if r["id"] == QID)
                reviewrow = next(r for r in rev["records"] if r["source_id"] == QID)
                if variant == "original options":
                    bankrow["options"][1] = "(B) silently corrected"
                elif variant == "review options":
                    reviewrow["captured_options"][1] = "(B) silently corrected"
                else:
                    bankrow["stem"] += " altered"
                (self.repo / BANK).write_text(json.dumps(src, ensure_ascii=False), encoding="utf-8")
                (self.repo / REVIEW).write_text(json.dumps(rev, ensure_ascii=False), encoding="utf-8")
                with self.assertRaises(ValueError):
                    test_source_recapture.validate(self.repo)
                (self.repo / BANK).write_text(json.dumps(self.bank, ensure_ascii=False), encoding="utf-8")
                (self.repo / REVIEW).write_text(json.dumps(self.review, ensure_ascii=False), encoding="utf-8")

    def test_proposal_cannot_forge_source_notation_locator_answer_or_approval(self):
        for field, replacement in (
            ("source_question_ref", "ncert-exemplar-g9-math-u01-q06"),
            ("source_stem_sha256", "sha256:" + "0" * 64),
            ("original_captured_options", ["(A) forged"]),
            ("proposed_tex_options", ["(A) forged"] * 4),
            ("official_question_pdf", "https://example.org/other.pdf"),
            ("official_answer_pdf_page_index", 3),
            ("official_answer_key", "(B)"),
            ("historical_review_status", "VISUAL_MATCH"),
            ("proposed_record_change_applied", True),
            ("source_custody_promoted", True),
            ("academic_status_promoted", True),
            ("publication_authorized", True),
        ):
            with self.subTest(field=field):
                self.data = copy.deepcopy(self.proposal)
                self.data[field] = replacement
                self.write_proposal()
                with self.assertRaises(ValueError):
                    test_source_recapture.validate(self.repo)

    def test_applied_version_cannot_claim_readiness_reuse_old_pass_or_change_source(self):
        for key, value in (
            ("source_id", "ncert-exemplar-g9-math-u01-q06"),
            ("previous_options", ["forged"]),
            ("current_options", ["forged"]),
            ("source_locator", {"printed_page": 99}),
            ("answer_key", "(C)"),
            ("official_pdf_bytes_digest_available", True),
            ("source_custody_status", "READY_FOR_BLUEPRINT"),
            ("academic_validation_status", "VALIDATED"),
            ("historical_academic_receipt_reused", True),
            ("accepted", True),
            ("publication_authorized", True),
            ("ready_for_blueprint", True),
        ):
            with self.subTest(key=key):
                self.applied_data = copy.deepcopy(self.applied)
                self.applied_data[key] = value
                self.write_applied()
                with self.assertRaises(ValueError):
                    test_source_recapture.validate(self.repo)

    def test_changed_pdf_coordinates_or_identity_do_not_inherit_past_review(self):
        for key, val in (("printed_page", 5), ("pdf_page_index", 6),
                         ("question_number", "6")):
            with self.subTest(key=key):
                self.data = copy.deepcopy(self.proposal)
                self.data["source_locator"][key] = val
                self.write_proposal()
                with self.assertRaisesRegex(ValueError, "locator mismatch"):
                    test_source_recapture.validate(self.repo)


if __name__ == "__main__":
    unittest.main()
