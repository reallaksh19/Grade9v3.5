"""Owner no-human-peer-signoff policy and full organizer sample provisional QRT falsifiers."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_owner_sample_qrt import validate_owner_sample_qrt  # noqa: E402


class OwnerWaiverSampleQRTTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dir=Path(tmp.name)
        self.policy=dir/"owner-policy.json"
        self.overlay=dir/"qrt-proposals.json"
        self.policy.write_bytes((ROOT/"governance"/"owner-independent-academic-review-waiver.v1.json").read_bytes())
        self.overlay.write_bytes((ROOT/"verification"/"official-sample-2026-27-new-qrt-proposals.v1.json").read_bytes())

    def check(self):
        return validate_owner_sample_qrt(self.policy,self.overlay)

    def mutate_policy(self,fn):
        d=json.loads(self.policy.read_text(encoding="utf-8"))
        fn(d);self.policy.write_text(json.dumps(d))

    def mutate_qrt(self,fn):
        d=json.loads(self.overlay.read_text(encoding="utf-8"))
        fn(d);self.overlay.write_text(json.dumps(d))

    @staticmethod
    def item(d,n):
        return next(r for r in d["records"] if r["sample_original_question_number"]==n)

    def test_complete_sample_proposals_with_n_a_human_gate(self):
        r=self.check()
        self.assertEqual((r["source_sample_positions_with_proposals"],r["new_provisional_proposals"],
                          r["unique_provisional_qrt_cells"]),(10,3,7))
        self.assertFalse(r["independent_human_review_required"])
        self.assertEqual((r["qrt_accepted_cells"],r["core_ready"]),(0,0))

    def test_owner_human_waiver_cannot_be_swapped_for_fake_approval(self):
        self.mutate_policy(lambda d:d.update(approval_claim_boundary="PEER_APPROVAL_GRANTED"))
        with self.assertRaises(SeedError):self.check()

    def test_owner_authority_source_cannot_be_removed(self):
        self.mutate_policy(lambda d:d.update(owner_instruction_quoted="independent academic approved"))
        with self.assertRaises(SeedError):self.check()

    def test_publisher_rights_remain_a_gate(self):
        self.mutate_policy(lambda d:d.update(publisher_redistribution_or_figure_rights_not_waived=False))
        with self.assertRaises(SeedError):self.check()

    def test_original_question_mathematics_still_mandatory(self):
        self.mutate_policy(lambda d:d.update(computational_mathematical_evidence_still_required=False))
        with self.assertRaises(SeedError):self.check()

    def test_original_66_source_seed_unchanged(self):
        self.mutate_qrt(lambda d:d.update(original_owner_sample_seed_positions=10))
        with self.assertRaises(SeedError):self.check()

    def test_ten_source_question_numbers_must_be_complete(self):
        self.mutate_qrt(lambda d:d.update(ten_source_question_numbers=[1,2,3,4,5,6,7,8,9]))
        with self.assertRaises(SeedError):self.check()

    def test_sample_q1_original_dice_qrt_demand_locked(self):
        self.mutate_qrt(lambda d:self.item(d,1).update(primary_demand="JUSTIFY"))
        with self.assertRaises(SeedError):self.check()

    def test_sample_q3_number_pattern_math_proof_source_locked(self):
        self.mutate_qrt(lambda d:self.item(d,3).update(
            mathematical_evidence_reference="TEST/imo-research/seed/questions.jsonl"))
        with self.assertRaises(SeedError):self.check()

    def test_sample_q5_is_scored_as_justification_not_retrieval(self):
        self.mutate_qrt(lambda d:self.item(d,5).update(primary_demand="RETRIEVE"))
        with self.assertRaises(SeedError):self.check()

    def test_difficulty_factor_score_cannot_be_inflated(self):
        self.mutate_qrt(lambda d:self.item(d,5)["five_factor_scores"].update(
            reasoning_chain_length=3))
        with self.assertRaises(SeedError):self.check()

    def test_score_band_must_match_five_factor_sum(self):
        self.mutate_qrt(lambda d:self.item(d,1).update(difficulty_band="D4"))
        with self.assertRaises(SeedError):self.check()

    def test_source_figure_rights_not_inferred_from_official_key(self):
        self.mutate_qrt(lambda d:self.item(d,1).update(
            source_reproduction_rights_status="LICENSED"))
        with self.assertRaises(SeedError):self.check()

    def test_q5_previous_p0_review_is_historical_not_hidden(self):
        self.mutate_qrt(lambda d:self.item(d,5).update(
            prior_record_status="PREVIOUSLY_HUMAN_APPROVED"))
        with self.assertRaises(SeedError):self.check()

    def test_source_sample_q9_important_dispute_not_erased(self):
        self.mutate_qrt(lambda d:d.update(sample_q9_source_radical_transcription_dispute_remains=False))
        with self.assertRaises(SeedError):self.check()

    def test_acceptance_not_auto_provisioned_for_q1(self):
        self.mutate_qrt(lambda d:self.item(d,1).update(accepted_qrt_cell="QRT-REPRESENT-D3"))
        with self.assertRaises(SeedError):self.check()

    def test_core_publication_not_automatically_unlocked(self):
        self.mutate_qrt(lambda d:self.item(d,3).update(core_eligible=True))
        with self.assertRaises(SeedError):self.check()

    def test_source_stem_not_republished(self):
        self.mutate_qrt(lambda d:self.item(d,5).update(stem="Original sample paper stem"))
        with self.assertRaises(SeedError):self.check()


if __name__=="__main__":
    unittest.main()
