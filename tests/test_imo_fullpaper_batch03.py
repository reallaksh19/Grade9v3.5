"""Adversarial integrity checks for completed 2023–24 / 2024–25 seed-source audit."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(RESEARCH))
from validate_seed import SeedError  # noqa: E402
from validate_fullpaper_batch03 import validate_batch03, arithmetic_oracles  # noqa: E402


class AuditB03Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.seed, self.verify = base / "seed", base / "verification"
        self.seed.mkdir(); self.verify.mkdir()
        for name in ("questions.jsonl","sources.json","source_observations.json",
                     "math_audit_batch01.json"):
            (self.seed/name).write_bytes((RESEARCH/"seed"/name).read_bytes())
        for name in ("fullpaper-source-math-batch02.v1.json","fullpaper-audit-b03.v1.json"):
            (self.verify/name).write_bytes((RESEARCH/"verification"/name).read_bytes())
        self.audit = self.verify/"fullpaper-audit-b03.v1.json"

    def run_audit(self):
        return validate_batch03(self.seed,self.verify)

    def change(self,fn):
        doc=json.loads(self.audit.read_text(encoding="utf-8"))
        fn(doc)
        self.audit.write_text(json.dumps(doc))

    def q(self,doc,owner):
        return next(x for x in doc["records"] if x["owner_compilation_entry"]==owner)

    def test_b03_has_47_fullpaper_checks_but_no_acceptance(self):
        got=self.run_audit()
        self.assertEqual((got["new_agent_checked"],got["cumulative_fullpaper_agent_checked"],
                          got["remaining_2025_set_a"],got["qrt_cells_accepted"]),(16,47,11,0))

    def test_numeric_oracle_recomputes_unreviewed_questions(self):
        answers=arithmetic_oracles()
        self.assertEqual(answers[("SOF-IMO-G09-L1-2023-24-A",36)],"36/7 days")
        self.assertEqual(answers[("SOF-IMO-G09-L1-2024-25-B",43)],"4 days")
        self.assertEqual(answers[("SOF-IMO-G09-L1-2023-24-A",50)],"(-7,5); 5 units; (-6,-3)")

    def test_duplicate_source_question_fails(self):
        self.change(lambda d:d["records"][1].update(question_id=d["records"][0]["question_id"]))
        with self.assertRaises(SeedError):self.run_audit()

    def test_source_question_removed_fails(self):
        self.change(lambda d:d["records"].pop())
        with self.assertRaises(SeedError):self.run_audit()

    def test_wrong_pdf_page_locator_fails(self):
        self.change(lambda d:self.q(d,54).update(source_pdf_page_index=4))
        with self.assertRaises(SeedError):self.run_audit()

    def test_source_host_cannot_be_relabelled_official(self):
        self.change(lambda d:self.q(d,55).update(source_host_status="OFFICIAL_SOF_HOST"))
        with self.assertRaises(SeedError):self.run_audit()

    def test_printed_choice_swap_is_not_hidden(self):
        self.change(lambda d:self.q(d,27).update(mathematically_selected_printed_option="A"))
        with self.assertRaises(SeedError):self.run_audit()

    def test_compiler_claim_rewrite_fails(self):
        self.change(lambda d:self.q(d,53).update(attachment_claimed_option="A"))
        with self.assertRaises(SeedError):self.run_audit()

    def test_math_derivation_is_required(self):
        self.change(lambda d:self.q(d,18).update(agent_mathematical_derivation=""))
        with self.assertRaises(SeedError):self.run_audit()

    def test_alt_check_is_required(self):
        self.change(lambda d:self.q(d,49).update(alternate_verification=""))
        with self.assertRaises(SeedError):self.run_audit()

    def test_unsupported_official_answer_key_receipt_fails(self):
        self.change(lambda d:self.q(d,52).update(organizer_official_key_receipt="SOF"))
        with self.assertRaises(SeedError):self.run_audit()

    def test_promotion_to_core_is_blocked(self):
        self.change(lambda d:self.q(d,41).update(core_eligible=True))
        with self.assertRaises(SeedError):self.run_audit()

    def test_qrt_cell_is_not_accepted_without_review(self):
        self.change(lambda d:self.q(d,50).update(accepted_qrt_cell="QRT-APPLY-D1"))
        with self.assertRaises(SeedError):self.run_audit()

    def test_rights_clearance_must_not_be_invented(self):
        self.change(lambda d:self.q(d,32).update(original_figure_rights="CLEARED"))
        with self.assertRaises(SeedError):self.run_audit()

    def test_original_paper_text_cannot_be_inserted(self):
        self.change(lambda d:self.q(d,45).update(stem="Unlicensed source verbatim text"))
        with self.assertRaises(SeedError):self.run_audit()


if __name__ == "__main__":
    unittest.main()
