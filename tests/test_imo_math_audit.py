"""Adversarial checks for the quarantined scanned-paper maths audit."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(BASE))
from validate_seed import SeedError  # noqa: E402
from validate_math_audit import validate_audit, expected_mathematics  # noqa: E402


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for filename in ("questions.jsonl", "sources.json", "source_observations.json", "math_audit_batch01.json"):
            (self.root / filename).write_bytes((BASE / "seed" / filename).read_bytes())

    def alter(self, action):
        path = self.root / "math_audit_batch01.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        action(data)
        path.write_text(json.dumps(data))

    def test_audit_honestly_remains_unverified(self):
        report = validate_audit(self.root)
        self.assertEqual(report["worked_source_questions"], 16)
        self.assertEqual(report["choice_discrepancies"], 3)
        self.assertEqual(report["official_answer_keys_verified"], 0)
        self.assertEqual(report["core_eligible"], 0)

    def test_math_oracle_for_inverse_and_cone(self):
        oracle = expected_mathematics()
        self.assertEqual(oracle["SOF-IMO-G09-L1-2023-24-A-Q018"], "-5/12")
        self.assertEqual(oracle["SOF-IMO-G09-L1-2025-26-A-Q031"], "a=84deg,b=21deg,c=48deg")

    def test_wrong_computed_answer_fails(self):
        self.alter(lambda data: data["questions"][0].update(computed_answer="2:3"))
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_silent_inverse_identity_repair_fails(self):
        def mutate(data):
            q = next(q for q in data["questions"] if q["compilation_entry"] == 2)
            q["source_comparison"] = "MATCH_PARTIAL"
        self.alter(mutate)
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_missing_wrong_choice_evidence_fails(self):
        def mutate(data):
            q = next(q for q in data["questions"] if q["compilation_entry"] == 22)
            q["math_derived_printed_choice"] = "D"
        self.alter(mutate)
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_never_claims_official_key_verification(self):
        self.alter(lambda data: data["questions"][0].update(official_key_receipt="SOF"))
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_never_auto_promotes_question_to_core(self):
        self.alter(lambda data: data["questions"][0].update(core_eligible=True))
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_source_rebinding_fails(self):
        self.alter(lambda data: data["questions"][0].update(source_id="SOF-IMO-G09-L1-2025-26-A"))
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_printed_page_locator_is_not_optional(self):
        self.alter(lambda data: data["questions"][0].pop("source_pdf_page_index"))
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_quiet_loss_of_source_record_fails(self):
        self.alter(lambda data: data["questions"].pop())
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_section_correction_is_enforced(self):
        def mutate(data):
            q = next(q for q in data["questions"] if q["compilation_entry"] == 9)
            q["exam_section_observed"] = "ACHIEVERS_SECTION"
        self.alter(mutate)
        with self.assertRaises(SeedError): validate_audit(self.root)

    def test_cross_year_near_duplicate_stays_separate(self):
        self.alter(lambda data: data["cross_document_candidates"][0].update(source_b_seed_record=True))
        with self.assertRaises(SeedError): validate_audit(self.root)


if __name__ == "__main__":
    unittest.main()
