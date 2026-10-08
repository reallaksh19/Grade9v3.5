"""Negative admission tests for independently authored SOF Grade 9 style questions."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_intake_contract import validate_contract  # noqa: E402


class IntakeContractTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        root=Path(d.name)
        self.seed=root/"seed"
        self.seed.mkdir()
        for name in ("questions.jsonl","sources.json","source_observations.json"):
            (self.seed/name).write_bytes((ROOT/"seed"/name).read_bytes())
        self.contract=root/"intake.json"
        self.contract.write_bytes((ROOT/"intake"/"original-practice-intake-contract.v1.json").read_bytes())

    def valid(self):
        return validate_contract(self.seed,self.contract)

    def edit(self,change):
        d=json.loads(self.contract.read_text(encoding="utf-8"))
        change(d)
        self.contract.write_text(json.dumps(d))

    @staticmethod
    def item(data,n):
        return next(x for x in data["records"] if x["candidate_id"].endswith(f"-{n:03d}"))

    def test_seven_packets_no_product_admission(self):
        result=self.valid()
        self.assertEqual(result["source_independent_candidate_slots"],7)
        self.assertEqual(result["separate_required_gates"],6)
        self.assertFalse(result["human_academic_signoff_required"])
        self.assertEqual((result["qrt_accepted_cells"],result["core_ready"],
                          result["learner_published"]),(0,0,0))

    def test_pr270_is_not_assumed_merged(self):
        self.edit(lambda d:d.update(upstream_pr_merge_qualification="ASSUMED_MERGED"))
        with self.assertRaises(SeedError):self.valid()

    def test_no_claim_original_source_rights(self):
        self.edit(lambda d:d.update(source_paper_question_reproduction_rights="LICENSED"))
        with self.assertRaises(SeedError):self.valid()

    def test_missing_candidate_fails(self):
        self.edit(lambda d:d["records"].pop())
        with self.assertRaises(SeedError):self.valid()

    def test_candidate_id_cannot_be_replaced_with_source_id(self):
        self.edit(lambda d:self.item(d,1).update(
            candidate_id="SOF-IMO-G09-SAMPLE-2026-27-Q005"))
        with self.assertRaises(SeedError):self.valid()

    def test_cognitive_cell_does_not_equal_accepted_cell(self):
        self.edit(lambda d:self.item(d,1).update(qrt_accepted_cell="QRT-JUSTIFY-D3"))
        with self.assertRaises(SeedError):self.valid()

    def test_math_receipt_cannot_be_assumed(self):
        self.edit(lambda d:self.item(d,3).update(mathematical_oracle_ci_receipt="SUCCESS"))
        with self.assertRaises(SeedError):self.valid()

    def test_learner_accessibility_check_still_pending(self):
        self.edit(lambda d:self.item(d,4).update(accessibility_and_wording_review="APPROVED"))
        with self.assertRaises(SeedError):self.valid()

    def test_core2_admission_must_be_decided_later(self):
        self.edit(lambda d:self.item(d,5).update(core_2_approved=True))
        with self.assertRaises(SeedError):self.valid()

    def test_core1a_admission_must_be_decided_later(self):
        self.edit(lambda d:self.item(d,6).update(core_1a_approved=True))
        with self.assertRaises(SeedError):self.valid()

    def test_owner_is_not_an_inferred_ci_runner(self):
        self.edit(lambda d:self.item(d,6).update(product_owner_identity="GitHub Actions"))
        with self.assertRaises(SeedError):self.valid()

    def test_learner_publishing_needs_product_decision(self):
        self.edit(lambda d:self.item(d,2).update(learner_published=True))
        with self.assertRaises(SeedError):self.valid()

    def test_source_independence_must_be_checked(self):
        self.edit(lambda d:self.item(d,7).update(
            source_originality_boundary="SOURCE_SOF_STEM_VERBATIM"))
        with self.assertRaises(SeedError):self.valid()

    def test_cannot_claim_human_review_was_required(self):
        self.edit(lambda d:self.item(d,1).update(independent_human_academic_signoff_required=True))
        with self.assertRaises(SeedError):self.valid()

    def test_product_owner_gate_cannot_be_removed(self):
        self.edit(lambda d:d["required_gates"].pop())
        with self.assertRaises(SeedError):self.valid()

    def test_automatic_approval_from_ci_cannot_be_enabled(self):
        self.edit(lambda d:d["required_gates"][3].update(must_not_autofill_from_ci=False))
        with self.assertRaises(SeedError):self.valid()

    def test_original_sof_figure_not_allowed_in_intake(self):
        self.edit(lambda d:self.item(d,4).update(sof_figure="source PDF figure content"))
        with self.assertRaises(SeedError):self.valid()

    def test_future_evidence_list_requires_owner_decision(self):
        self.edit(lambda d:self.item(d,5)["requires_future_evidence"].pop())
        with self.assertRaises(SeedError):self.valid()


if __name__=="__main__":
    unittest.main()
