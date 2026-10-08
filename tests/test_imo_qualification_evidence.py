"""Falsifiers for the immutable, non-admitting seven-question qualification overlay."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_qualification_evidence import validate_qualification  # noqa: E402


class QualificationEvidenceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.paths = {}
        originals = {
            "ledger": ROOT / "intake" / "original-practice-qualification-evidence.v1.json",
            "practice": ROOT / "original-practice" / "seven-cell-original-problems.v1.json",
            "diagnostics": ROOT / "original-practice" / "diagnostics" / "structured-checker-cases.v1.json",
            "intake": ROOT / "intake" / "original-practice-intake-contract.v1.json",
            "policy": ROOT / "governance" / "owner-independent-academic-review-waiver.v1.json",
        }
        for key, source in originals.items():
            self.paths[key] = self.root / f"{key}.json"
            shutil.copyfile(source, self.paths[key])
        self.seed = self.root / "seed"
        self.seed.mkdir()
        for name in ("questions.jsonl", "sources.json", "source_observations.json"):
            shutil.copyfile(ROOT / "seed" / name, self.seed / name)

    def verify(self):
        return validate_qualification(
            ledger=self.paths["ledger"], practice=self.paths["practice"],
            diagnostics=self.paths["diagnostics"], intake=self.paths["intake"],
            policy=self.paths["policy"], seed=self.seed,
        )

    def mutate(self, kind, fn):
        p = self.paths[kind]
        obj = json.loads(p.read_text(encoding="utf-8"))
        fn(obj)
        p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    def blocked(self, kind, fn):
        self.mutate(kind, fn)
        with self.assertRaises(SeedError):
            self.verify()

    def test_reconciles_only_research(self):
        result = self.verify()
        self.assertEqual(result["original_candidates"], 7)
        self.assertEqual(result["upstream_focused_head_receipts"], 3)
        self.assertEqual((result["structured_positive_examples"], result["misconception_probes"]),
                         (14, 18))
        self.assertEqual((result["accepted_qrt_cells"], result["product_approved"],
                          result["core_ready"], result["learner_published"]), (0, 0, 0, 0))

    def test_wrong_pr_head_fails(self):
        self.blocked("ledger", lambda d: d["upstream_receipts"][0].update(head_sha="a" * 40))

    def test_wrong_merge_commit_fails(self):
        self.blocked("ledger", lambda d: d["upstream_receipts"][1].update(merge_commit="b" * 40))

    def test_wrong_focused_ci_run_fails(self):
        self.blocked("ledger", lambda d: d["upstream_receipts"][2].update(run_id=1))

    def test_forged_ci_success_fails(self):
        self.blocked("ledger", lambda d: d["upstream_receipts"][0].update(result="OWNER_APPROVED"))

    def test_historical_intake_snapshot_is_unchanged(self):
        self.blocked("intake", lambda d: d.update(
            upstream_pr_merge_qualification="VERIFIED_NOW"))

    def test_source_content_mutation_fails(self):
        self.blocked("practice", lambda d: d["records"][0].update(
            title=d["records"][0]["title"] + " changed"))

    def test_diagnostic_sample_mutation_fails(self):
        self.blocked("diagnostics", lambda d:
                     d["records"][1]["misconception_probes"][0].update(actionable_hint="bad"))

    def test_owner_waiver_cannot_claim_peer_approval(self):
        self.blocked("policy", lambda d: d.update(original_human_signoffs_obtained=1))

    def test_owner_waiver_cannot_be_cancelled(self):
        self.blocked("ledger", lambda d: d.update(academic_peer_review="REVIEW_REQUIRED"))

    def test_fake_source_license_fails(self):
        self.blocked("ledger", lambda d: d.update(independently_licensed_source_material=True))

    def test_fake_learner_accessibility_fails(self):
        self.blocked("ledger", lambda d: d.update(reviewed_for_accessibility_with_learners=True))

    def test_historical_census_cannot_be_inflated(self):
        self.blocked("ledger", lambda d: d.update(owner_seed_positions_unchanged=68))

    def test_qrts_are_not_accepted(self):
        self.blocked("ledger", lambda d: d["records"][0].update(qrt_acceptance="APPROVED"))

    def test_product_owner_is_not_actions(self):
        self.blocked("ledger", lambda d: d["records"][3].update(
            product_owner_identity="GitHub Actions"))

    def test_core_cannot_be_admitted(self):
        self.blocked("ledger", lambda d: d["records"][4].update(core_2_ready=True))

    def test_learner_not_published(self):
        self.blocked("ledger", lambda d: d["records"][5].update(learner_published=True))

    def test_crosslinked_qrt_cannot_be_relabelled(self):
        self.blocked("ledger", lambda d: d["records"][6].update(
            provisional_qrt_cell="QRT-REPRESENT-D4"))

    def test_structured_checker_is_not_a_free_text_grader(self):
        self.blocked("ledger", lambda d: d["records"][0].update(
            diagnostic_scope="ARBITRARY_PROOF_AUTO_GRADED"))

    def test_misconception_count_cannot_be_inflated(self):
        self.blocked("ledger", lambda d: d["records"][1].update(
            checked_misconception_probes=99))

    def test_item_quality_hold_cannot_be_waived(self):
        self.blocked("ledger", lambda d: d["records"][2].update(
            learner_quality_gate="PASS"))

    def test_specific_quality_action_cannot_be_erased(self):
        self.blocked("ledger", lambda d: d["records"][3].update(
            quality_hold_action="No review required."))

    def test_unlicensed_source_field_not_allowed(self):
        self.blocked("ledger", lambda d: d["records"][0].update(
            sof_original_stem="unauthorized source text"))

    def test_seventh_item_must_not_be_deleted(self):
        self.blocked("ledger", lambda d: d["records"].pop())

    def test_input_blob_pin_cannot_be_changed(self):
        self.blocked("ledger", lambda d: d["input_git_blobs"][0].update(blob_sha="0" * 40))

    def test_boolean_is_not_a_valid_zero_counter(self):
        self.blocked("ledger", lambda d: d.update(product_approved=False))


if __name__ == "__main__":
    unittest.main()
