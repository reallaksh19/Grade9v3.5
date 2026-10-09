"""Reject unsupported edition, forged publisher witness, or status promotion on #68."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from Shared.tools import test_source_edition_provenance  # noqa: E402


class NCERTEditionProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((REPO / test_source_edition_provenance.EVIDENCE).read_text(encoding="utf-8"))
        cls.bank = json.loads((REPO / test_source_edition_provenance.BANK_REF).read_text(encoding="utf-8"))

    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.repo = Path(workspace.name)
        self.doc = copy.deepcopy(self.evidence)
        self.questions = copy.deepcopy(self.bank)
        self.ep = self.repo / test_source_edition_provenance.EVIDENCE
        self.bp = self.repo / test_source_edition_provenance.BANK_REF
        self.ep.parent.mkdir(parents=True)
        self.bp.parent.mkdir(parents=True)
        self.write()

    def write(self):
        self.ep.write_text(json.dumps(self.doc, ensure_ascii=False), encoding="utf-8")
        self.bp.write_text(json.dumps(self.questions, ensure_ascii=False), encoding="utf-8")

    def test_all_210_raw_claims_are_unverified_but_source_counts_unchanged(self):
        for repo in (REPO, self.repo):
            result = test_source_edition_provenance.validate(repo)
            self.assertEqual(result["question_count"], 210)
            self.assertEqual(result["raw_edition_label"], "2023-24")
            self.assertIs(result["verified_publisher_edition"], False)
            self.assertEqual(result["source_ready_granted"], 0)
            self.assertEqual(result["academic_validation_granted"], 0)
            self.assertIs(result["publication_authorized"], False)

    def test_forged_publisher_provenance_claims_are_rejected(self):
        mutations = (
            ("verified edition", lambda d: d.__setitem__("publisher_edition_verified", True)),
            ("numeric false impersonation", lambda d: d.__setitem__("publisher_edition_verified", 0)),
            ("float scope count", lambda d: d.__setitem__("rows_bearing_raw_label", 210.0)),
            ("fake hash", lambda d: d.__setitem__("official_pdf_sha256", "sha256:" + "a" * 64)),
            ("downloaded official bytes", lambda d: d.__setitem__("exact_official_pdf_bytes_obtained", True)),
            ("third-party mirror promoted", lambda d: d["secondary_bibliography"].__setitem__(
                "independently_authenticated_as_official_ncert_document", True)),
            ("mirror promoted as edition", lambda d: d["secondary_bibliography"].__setitem__(
                "may_resolve_2023_24_claim", True)),
            ("fake independent reviewer", lambda d: d.__setitem__("independent_reviewer_authenticated", True)),
            ("reviewer conflict hidden", lambda d: d.__setitem__("reviewer_conflict_disclosed", False)),
            ("changed actual evidence stamp", lambda d: d["official_page_layout_date_stamps"].__setitem__(0, "2023/24")),
            ("layout stamp becomes edition", lambda d: d.__setitem__("official_layout_date_is_publisher_edition", True)),
            ("claims verified edition", lambda d: d.__setitem__("edition_claim_disposition", "PUBLISHER_AUTHENTICATED")),
            ("fabricated edition", lambda d: d.__setitem__("observed_raw_edition_label", "2018")),
            ("third-party URL masquerades", lambda d: d["secondary_bibliography"].__setitem__(
                "url", "https://ncert.nic.in/unverified/imprint.pdf")),
            ("note rewritten", lambda d: d.__setitem__("note", "certified 2023-24")),
            ("injected authority", lambda d: d.__setitem__("official_edition_attested", True)),
        )
        for name, mutation in mutations:
            with self.subTest(name=name):
                self.doc = copy.deepcopy(self.evidence)
                mutation(self.doc)
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen scope"):
                    test_source_edition_provenance.validate(self.repo)

    def test_record_ids_scope_and_raw_edition_cannot_be_rewritten(self):
        cases = (
            ("different edition", lambda q: q.__setitem__("edition_or_year", "2018")),
            ("invent authoritative label", lambda q: q.__setitem__("edition_or_year", "2023-24 VERIFIED")),
            ("changed source kind", lambda q: q.__setitem__("source_kind", "PRIVATE_GUIDE")),
            ("changed source authority", lambda q: q.__setitem__("source_authority", "THIRD_PARTY")),
            ("duplicate source ID", lambda q: q.__setitem__("id", self.questions["questions"][1]["id"])),
        )
        for name, mutation in cases:
            with self.subTest(name=name):
                self.doc = copy.deepcopy(self.evidence)
                self.questions = copy.deepcopy(self.bank)
                mutation(self.questions["questions"][0])
                self.write()
                # The existing intake identity gate may reject a forged bank before
                # the edition-specific check is reached.
                with self.assertRaises(ValueError):
                    test_source_edition_provenance.validate(self.repo)

    def test_missing_source_record_and_extra_bank_fail_closed(self):
        self.questions["questions"].pop()
        self.write()
        with self.assertRaisesRegex(ValueError, "210 original source IDs"):
            test_source_edition_provenance.validate(self.repo)
        self.questions = copy.deepcopy(self.bank)
        self.questions["questions"].append(copy.deepcopy(self.questions["questions"][0]))
        self.write()
        with self.assertRaises(ValueError):
            test_source_edition_provenance.validate(self.repo)

    def test_unchanged_prior_academic_validation_does_not_verify_book_edition(self):
        self.assertEqual(self.evidence["rows_bearing_raw_label"], 210)
        self.assertEqual(len(self.evidence["spot_checked_source_ids"]), 10)
        self.assertFalse(self.evidence["publisher_edition_verified"])
        self.assertFalse(self.evidence["independent_reviewer_authenticated"])
        self.assertEqual(self.evidence["edition_claim_disposition"], "UNVERIFIED_PUBLISHER_EDITION")
        self.assertEqual(self.evidence["official_page_layout_date_stamps"], ["16/04/18"])
        self.assertFalse(self.evidence["official_layout_date_is_publisher_edition"])

    def test_ready_academic_canonical_owner_and_publication_cannot_be_attested(self):
        for key in (
            "source_ready_promoted", "academic_validation_granted",
            "canonical_admission_authorized", "owner_acceptance_granted",
            "publication_authorized",
        ):
            with self.subTest(key=key):
                self.doc = copy.deepcopy(self.evidence)
                self.doc[key] = True
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen scope"):
                    test_source_edition_provenance.validate(self.repo)


if __name__ == "__main__":
    unittest.main()
