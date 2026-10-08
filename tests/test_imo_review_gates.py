"""Adversarial human sign-off and copyright/custody gate tests for SOF Grade 9."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_review_gates import validate_queue  # noqa: E402


class IndependentReviewGateTests(unittest.TestCase):
    def setUp(self):
        ctx=tempfile.TemporaryDirectory()
        self.addCleanup(ctx.cleanup)
        self.base=Path(ctx.name)
        self.seed=self.base/"seed"
        self.verify=self.base/"verification"
        self.adjudication=self.base/"adjudication"
        self.review=self.base/"review-gates"
        for d in (self.seed,self.verify,self.adjudication,self.review):
            d.mkdir()
        for name in ("questions.jsonl","sources.json","source_observations.json","math_audit_batch01.json"):
            (self.seed/name).write_bytes((ROOT/"seed"/name).read_bytes())
        for name in ("fullpaper-source-math-batch02.v1.json","official-sample-2026-27-math-qrt-pilot.v1.json"):
            (self.verify/name).write_bytes((ROOT/"verification"/name).read_bytes())
        self.register=self.adjudication/"source-discrepancy-register.v1.json"
        self.register.write_bytes((ROOT/"adjudication"/self.register.name).read_bytes())
        self.queue=self.review/"independent-review-queue.v1.json"
        self.queue.write_bytes((ROOT/"review-gates"/self.queue.name).read_bytes())

    def validate(self):
        return validate_queue(self.seed,self.verify,self.register,self.queue)

    def mutate(self,fn):
        data=json.loads(self.queue.read_text(encoding="utf-8"))
        fn(data)
        self.queue.write_text(json.dumps(data))

    @staticmethod
    def row(data,n):
        return next(x for x in data["records"] if x["case_id"].endswith(f"-{n:03d}"))

    def test_ten_packets_and_four_rights_holds_pass(self):
        out=self.validate()
        self.assertEqual((out["review_packets"],out["source_positions"],
                          out["distinct_source_rights_holds"],out["urgent_p0"]),(10,11,4,4))
        self.assertEqual((out["reviewer_signoffs"],out["source_reuse_grants"],
                          out["accepted_qrt_cells"],out["core_eligible"]),(0,0,0,0))

    def test_case_cannot_be_removed(self):
        self.mutate(lambda d:d["records"].pop())
        with self.assertRaises(SeedError):self.validate()

    def test_duplicate_case_cannot_be_injected(self):
        self.mutate(lambda d:d["records"][1].update(case_id=d["records"][0]["case_id"]))
        with self.assertRaises(SeedError):self.validate()

    def test_source_case_identity_cannot_be_changed(self):
        self.mutate(lambda d:self.row(d,7).update(source_document_id="SOF-IMO-G09-L1-2024-25-B"))
        with self.assertRaises(SeedError):self.validate()

    def test_priority_for_semantic_change_must_remain_p0(self):
        self.mutate(lambda d:self.row(d,6).update(priority="P2"))
        with self.assertRaises(SeedError):self.validate()

    def test_priority_count_claim_cannot_be_manipulated(self):
        self.mutate(lambda d:d["priority_counts"].update(P0=3))
        with self.assertRaises(SeedError):self.validate()

    def test_fabricated_human_review_identity_blocked(self):
        self.mutate(lambda d:self.row(d,9).update(assigned_reviewer_identity="Unverified Reader"))
        with self.assertRaises(SeedError):self.validate()

    def test_fake_mathematics_peer_signature_blocked(self):
        self.mutate(lambda d:self.row(d,10).update(signed_mathematical_receipt="fake-signature"))
        with self.assertRaises(SeedError):self.validate()

    def test_false_peer_approval_decision_blocked(self):
        self.mutate(lambda d:self.row(d,3).update(peer_approval_decision="APPROVED"))
        with self.assertRaises(SeedError):self.validate()

    def test_fake_organizer_erratum_blocked(self):
        self.mutate(lambda d:self.row(d,6).update(official_key_or_erratum_url="https://sofworld.org/fake"))
        with self.assertRaises(SeedError):self.validate()

    def test_source_mirror_is_not_rights_owner(self):
        self.mutate(lambda d:d["source_documents"][0].update(publisher_rights_holder_identity="ISWK"))
        with self.assertRaises(SeedError):self.validate()

    def test_license_must_not_be_inferred_from_public_pdf(self):
        self.mutate(lambda d:d["source_documents"][1].update(figure_and_text_reuse_authorized=True))
        with self.assertRaises(SeedError):self.validate()

    def test_organizer_sample_still_needs_reuse_permission(self):
        self.mutate(lambda d:d["source_documents"][-1].update(
            rights_review_decision="GRANTED"))
        with self.assertRaises(SeedError):self.validate()

    def test_cannot_claim_permission_request_sent(self):
        self.mutate(lambda d:d["source_documents"][0].update(permission_request_status="SENT"))
        with self.assertRaises(SeedError):self.validate()

    def test_qrts_cannot_be_accepted_by_queue(self):
        self.mutate(lambda d:self.row(d,1).update(accepted_qrt_cell="QRT-APPLY-D2"))
        with self.assertRaises(SeedError):self.validate()

    def test_core_cannot_be_promoted_by_queue(self):
        self.mutate(lambda d:self.row(d,5).update(learner_content_eligible=True))
        with self.assertRaises(SeedError):self.validate()

    def test_scanned_figures_not_redistributed_in_queue(self):
        self.mutate(lambda d:self.row(d,4).update(source_figure="<image scan>"))
        with self.assertRaises(SeedError):self.validate()

    def test_no_verbatim_stem_storage(self):
        self.mutate(lambda d:self.row(d,7).update(stem="Original question text"))
        with self.assertRaises(SeedError):self.validate()


if __name__=="__main__":
    unittest.main()
