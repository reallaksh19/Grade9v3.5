"""Regression tests for #68 Stage-1 identity and layout truth.

A source-verified pilot repeating existing IDs must be reconciled as evidence,
not blindly added as another visible intake bank.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_test_question_bank, build_test_site, test_intake_registry  # noqa: E402

MAIN_BANK = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"


class TestOfficialIntakeIdentity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(MAIN_BANK.read_text(encoding="utf-8"))
        cls.q1 = cls.original["questions"][0]
        cls.q6 = cls.original["questions"][5]
        cls.q7 = cls.original["questions"][6]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.intake = self.repo / "TEST/question-bank/intake"
        self.intake.mkdir(parents=True)

    def bank(self, filename: str, questions: list[dict], **extra) -> Path:
        path = self.intake / filename
        payload = {
            "schema_version": test_intake_registry.SCHEMA,
            "bank_id": filename.removesuffix(".json"),
            "subject": self.original["subject"],
            "grade": self.original["grade"],
            "source_scope": copy.deepcopy(self.original["source_scope"]),
            "created_from": self.original["created_from"],
            "questions": copy.deepcopy(questions),
            **extra,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_current_main_has_one_unique_instance_per_210_questions(self):
        banks = test_intake_registry.load_intake_banks(REPO)
        self.assertEqual(sum(len(b["questions"]) for b in banks), 210)
        self.assertEqual(len(banks), 1)
        self.assertEqual(
            [b["bank_id"] for b in banks],
            ["ncert-cbse-math-g9-pilot"],
        )

    def test_distinct_official_q6_q7_may_share_a_verbatim_stem(self):
        self.assertEqual(self.q6["stem"], self.q7["stem"])
        self.assertNotEqual(self.q6["options"], self.q7["options"])
        self.bank("unit-one.json", [self.q6, self.q7])
        self.assertEqual(
            len(test_intake_registry.load_intake_banks(self.repo)[0]["questions"]), 2
        )

    def test_second_bank_repeating_same_question_id_fails_both_producers(self):
        self.bank("main.json", [self.q1])
        self.bank("six-record-pilot.json", [self.q1])
        with self.assertRaisesRegex(ValueError, "duplicate source id"):
            test_intake_registry.load_intake_banks(self.repo)
        with self.assertRaisesRegex(ValueError, "duplicate source id"):
            build_test_question_bank.payload(self.repo)
        with mock.patch.object(build_test_site, "REPO", self.repo):
            with self.assertRaisesRegex(ValueError, "duplicate source id"):
                build_test_site.intake_banks()

    def test_different_id_same_official_locator_is_not_a_new_question(self):
        duplicate = copy.deepcopy(self.q1)
        duplicate["id"] = "another-custody-record-for-q1"
        self.bank("main.json", [self.q1])
        self.bank("candidate.json", [duplicate])
        with self.assertRaisesRegex(ValueError, "duplicate official locator"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_structured_custody_cannot_reuse_flat_v1_schema_silently(self):
        self.bank("structured-pilot.json", [self.q1], documents=[{"id": "NCERT"}])
        with self.assertRaisesRegex(ValueError, "versioned adapter"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_malformed_source_file_fails_closed_instead_of_disappearing(self):
        (self.intake / "bad.json").write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unreadable official-source intake"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_missing_source_locator_and_hash_fail_closed(self):
        row = copy.deepcopy(self.q1)
        del row["source_url"]
        self.bank("bad-locator.json", [row])
        with self.assertRaisesRegex(ValueError, "incomplete official source identity"):
            test_intake_registry.load_intake_banks(self.repo)
        row = copy.deepcopy(self.q1)
        del row["stem_sha256"]
        self.bank("bad-locator.json", [row])
        with self.assertRaisesRegex(ValueError, "malformed source stem digest"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_unofficial_source_links_are_blocked_before_render(self):
        forged = copy.deepcopy(self.q1)
        for url in ("https://ncert.nic.in.evil.test/file.pdf",
                    "javascript:alert(1)",
                    "http://ncert.nic.in/unsafe",
                    "https://user@ncert.nic.in/file.pdf",
                    "https://ncert.nic.in:444/file.pdf",
                    "https://ncert.nic.in/file.pdf?copy=1",
                    "https://ncert.nic.in/file.pdf#page=1",
                    "https://ncert.nic.in/file%2epdf",
                    "https://ncert.nic.in/./file.pdf",
                    "https://ncert.nic.in//file.pdf",
                    "https://NCERT.NIC.IN/file.pdf"):
            with self.subTest(url=url):
                forged["source_url"] = url
                self.bank("unsafe.json", [forged])
                with self.assertRaisesRegex(ValueError, "unofficial or unsafe source URL"):
                    test_intake_registry.load_intake_banks(self.repo)

    def test_same_official_document_url_alias_cannot_be_a_second_source_instance(self):
        alias = copy.deepcopy(self.q1)
        alias["id"] = "alias-for-q1"
        alias["source_url"] += "?copy=1"
        self.bank("first.json", [self.q1])
        self.bank("second.json", [alias])
        with self.assertRaisesRegex(ValueError, "unofficial or unsafe source URL"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_missing_stage_one_metadata_or_grade_mismatch_fails_closed(self):
        fields = ("original_identifier", "document_title", "capture_method",
                  "wording_custody", "text_verification_status", "last_checked",
                  "topic_label", "question_type")
        for field in fields:
            with self.subTest(missing=field):
                invalid = copy.deepcopy(self.q1)
                invalid.pop(field)
                self.bank("bad.json", [invalid])
                with self.assertRaisesRegex(ValueError, "missing required Stage-1 metadata"):
                    test_intake_registry.load_intake_banks(self.repo)
        invalid = copy.deepcopy(self.q1)
        invalid["grade"] = 10
        self.bank("bad.json", [invalid])
        with self.assertRaisesRegex(ValueError, "bank/question subject or grade mismatch"):
            test_intake_registry.load_intake_banks(self.repo)
        self.bank("bad.json", [self.q1], source_scope=["CBSE_OFFICIAL"])
        with self.assertRaisesRegex(ValueError, "source authority outside bank scope"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_stem_digest_must_match_the_actual_captured_text(self):
        invalid = copy.deepcopy(self.q1)
        invalid["stem"] += " tampered"
        self.bank("bad.json", [invalid])
        with self.assertRaisesRegex(ValueError, "source stem digest does not match wording"):
            test_intake_registry.load_intake_banks(self.repo)

    def test_handoff_output_is_not_a_second_intake_bank(self):
        self.bank("main.json", [self.q1])
        (self.intake / "some.blueprint-handoff.json").write_text("{}", encoding="utf-8")
        banks = test_intake_registry.load_intake_banks(self.repo)
        self.assertEqual(len(banks), 1)
        self.assertEqual(build_test_question_bank.payload(self.repo)["validation_counts"], {"UNVALIDATED": 1})


if __name__ == "__main__":
    unittest.main()
