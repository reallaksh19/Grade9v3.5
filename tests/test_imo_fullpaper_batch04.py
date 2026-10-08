"""Adversarial checks on complete 58/58 original SOF Grade 9 paper source-position audit."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(BASE))
from validate_seed import SeedError  # noqa: E402
from validate_fullpaper_batch04 import validate_b04, mathematical_oracles  # noqa: E402


class FullPaperB04Tests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        self.seed=root/"seed"; self.verification=root/"verification"
        self.seed.mkdir(); self.verification.mkdir()
        for fn in ("questions.jsonl","sources.json","source_observations.json","math_audit_batch01.json"):
            (self.seed/fn).write_bytes((BASE/"seed"/fn).read_bytes())
        for fn in ("fullpaper-source-math-batch02.v1.json","fullpaper-audit-b03.v1.json",
                   "fullpaper-audit-b04.v1.json"):
            (self.verification/fn).write_bytes((BASE/"verification"/fn).read_bytes())
        self.file=self.verification/"fullpaper-audit-b04.v1.json"

    def check(self):
        return validate_b04(self.seed,self.verification)

    def mutate(self,edit):
        p=json.loads(self.file.read_text(encoding="utf-8"))
        edit(p)
        self.file.write_text(json.dumps(p))

    @staticmethod
    def item(data,question_number):
        return next(x for x in data["records"] if int(x["printed_question_number"])==question_number)

    def test_58_fullpaper_seed_positions_are_worked_not_accepted(self):
        r=self.check()
        self.assertEqual(r["combined_agent_worked_fullpaper"],58)
        self.assertEqual(r["remaining_unworked_fullpaper"],0)
        self.assertEqual(r["independent_academic_accepted"],0)
        self.assertEqual(r["accepted_qrt_cells"],0)

    def test_oracles_recalculate_financial_and_composite_geometry(self):
        outcomes=mathematical_oracles()
        self.assertEqual(outcomes[44],"INR 4000 income for P")
        self.assertEqual(outcomes[48],"Only statement C is incorrect")
        self.assertEqual(outcomes[50],"Both circle statements true")
        self.assertEqual(outcomes[43],"4/5")

    def test_missing_original_paper_question_fails(self):
        self.mutate(lambda d:d["records"].pop())
        with self.assertRaises(SeedError): self.check()

    def test_duplicate_original_paper_question_fails(self):
        self.mutate(lambda d:d["records"][0].update(question_id=d["records"][1]["question_id"]))
        with self.assertRaises(SeedError): self.check()

    def test_source_page_locator_fails_if_wrong(self):
        self.mutate(lambda d:self.item(d,50).update(source_pdf_page_index=5))
        with self.assertRaises(SeedError): self.check()

    def test_source_question_order_and_section_are_protected(self):
        self.mutate(lambda d:self.item(d,46).update(printed_level1_section="EVERYDAY_MATHEMATICS"))
        with self.assertRaises(SeedError): self.check()

    def test_miscomputed_interest_or_incomes_not_accepted(self):
        self.mutate(lambda d:self.item(d,44).update(independent_agent_result="INR 5000 income for P"))
        with self.assertRaises(SeedError): self.check()

    def test_sphere_volume_incorrect_option_cannot_be_changed(self):
        self.mutate(lambda d:self.item(d,48).update(printed_choice_selected_by_math="D"))
        with self.assertRaises(SeedError): self.check()

    def test_two_circle_figure_cannot_be_claimed_as_absent(self):
        self.mutate(lambda d:self.item(d,50).update(figure_referenced=False))
        with self.assertRaises(SeedError): self.check()

    def test_two_circle_geometry_warrants_must_be_present(self):
        self.mutate(lambda d:self.item(d,50).update(mathematical_derivation="Two circles exist."*9))
        with self.assertRaises(SeedError): self.check()

    def test_no_fabricated_official_key(self):
        self.mutate(lambda d:self.item(d,40).update(printed_official_key_receipt="SIGNED"))
        with self.assertRaises(SeedError): self.check()

    def test_no_fabricated_rights(self):
        self.mutate(lambda d:self.item(d,43).update(rights_status="CLEARED"))
        with self.assertRaises(SeedError): self.check()

    def test_no_unearned_qrt_cell(self):
        self.mutate(lambda d:self.item(d,45).update(qrt_accepted_cell="QRT-APPLY-D2"))
        with self.assertRaises(SeedError): self.check()

    def test_no_core_promotion(self):
        self.mutate(lambda d:self.item(d,36).update(core_eligible=True))
        with self.assertRaises(SeedError): self.check()

    def test_republished_stem_is_not_allowed(self):
        self.mutate(lambda d:self.item(d,37).update(stem="Original full paper question"))
        with self.assertRaises(SeedError): self.check()

    def test_false_58_audit_claim_is_refused(self):
        self.mutate(lambda d:d.update(total_nonoverlapping_agent_worked_fullpaper_source_positions=57))
        with self.assertRaises(SeedError): self.check()


if __name__=="__main__":
    unittest.main()
