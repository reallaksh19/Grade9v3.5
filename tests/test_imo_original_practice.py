"""Positive and adverse gates for seven freshly authored, non-SOF G9 practice candidates."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_original_practice import validate_original_practice, arithmetic_oracles  # noqa: E402


class OriginalPracticeTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root=Path(temp.name)
        self.seed=root/"seed"
        self.seed.mkdir()
        for name in ("questions.jsonl","sources.json","source_observations.json"):
            (self.seed/name).write_bytes((ROOT/"seed"/name).read_bytes())
        self.data=root/"original-practice.v1.json"
        self.data.write_bytes((ROOT/"original-practice"/"seven-cell-original-problems.v1.json").read_bytes())

    def check(self):
        return validate_original_practice(self.seed,self.data)

    def change(self,fn):
        obj=json.loads(self.data.read_text(encoding="utf-8"))
        fn(obj)
        self.data.write_text(json.dumps(obj))

    @staticmethod
    def item(d,n):
        return next(r for r in d["records"] if r["id"].endswith(f"-{n:03d}"))

    def test_seven_fresh_non_source_candidates_with_zero_admission(self):
        result=self.check()
        self.assertEqual((result["original_question_candidates"],
                          result["distinct_proposed_qrt_cells"]),(7,7))
        self.assertEqual((result["accepted_qrt_cells"],result["learner_published"],
                          result["core_ready"]),(0,0,0))

    def test_math_oracles_including_signed_area_and_prices(self):
        answers=arithmetic_oracles()
        self.assertEqual(answers[4],"880 square centimetres")
        self.assertEqual(answers[5],"y=-2x+5; x=7")
        self.assertEqual(answers[6],"112 rupees")
        self.assertIn("7.5 square units",answers[7])

    def test_missing_question_fails(self):
        self.change(lambda d:d["records"].pop())
        with self.assertRaises(SeedError):self.check()

    def test_duplicate_original_question_id_fails(self):
        self.change(lambda d:d["records"][0].update(id=d["records"][1]["id"]))
        with self.assertRaises(SeedError):self.check()

    def test_sof_printed_question_not_mislabeled_as_original(self):
        self.change(lambda d:self.item(d,1).update(id="SOF-IMO-G09-SAMPLE-2026-27-Q005"))
        with self.assertRaises(SeedError):self.check()

    def test_drum_wrap_must_not_include_lids(self):
        self.change(lambda d:self.item(d,4).update(expected_answer="1188 square centimetres"))
        with self.assertRaises(SeedError):self.check()

    def test_invoice_elimination_answer_cannot_change(self):
        self.change(lambda d:self.item(d,6).update(expected_answer="114 rupees"))
        with self.assertRaises(SeedError):self.check()

    def test_transformed_area_is_preserved(self):
        self.change(lambda d:self.item(d,7).update(
            expected_answer="P''=(6,-1), Q''=(1,-1), R''=(4,2); area doubled."))
        with self.assertRaises(SeedError):self.check()

    def test_non_source_origin_claim_cannot_be_swapped(self):
        self.change(lambda d:d.update(origin_claim="OFFICIAL_SOF_PAPER_CONTENT"))
        with self.assertRaises(SeedError):self.check()

    def test_no_sof_figure_assumed_publicly_reusable(self):
        self.change(lambda d:self.item(d,3)["intellectual_property_boundary"].update(
            original_sof_figure_copied=True))
        with self.assertRaises(SeedError):self.check()

    def test_global_prior_art_uniqueness_cannot_be_certified(self):
        self.change(lambda d:self.item(d,2)["intellectual_property_boundary"].update(
            external_originality_certification=True))
        with self.assertRaises(SeedError):self.check()

    def test_no_unearned_license_or_product_admission(self):
        self.change(lambda d:self.item(d,1)["intellectual_property_boundary"].update(
            publication_permission_decision="APPROVED"))
        with self.assertRaises(SeedError):self.check()

    def test_grade9_primary_demand_distinct_cells(self):
        self.change(lambda d:self.item(d,2)["qrt_proposal"].update(
            primary_demand="JUSTIFY"))
        with self.assertRaises(SeedError):self.check()

    def test_difficulty_score_factors_are_bounded(self):
        self.change(lambda d:self.item(d,6)["qrt_proposal"]["five_factor_scores"].update(
            concept_model_selection=3))
        with self.assertRaises(SeedError):self.check()

    def test_no_expert_signoff_claim_for_owner_n_a_policy(self):
        self.change(lambda d:self.item(d,7).update(
            independent_human_reviewer_was_used=True))
        with self.assertRaises(SeedError):self.check()

    def test_cannot_promote_core2_or_1a(self):
        self.change(lambda d:self.item(d,5).update(core_2_ready=True))
        with self.assertRaises(SeedError):self.check()

    def test_can_not_auto_accept_cognitive_cell(self):
        self.change(lambda d:self.item(d,4).update(
            qrt_acceptance_decision="ACCEPTED_QRT_MODEL_D2"))
        with self.assertRaises(SeedError):self.check()

    def test_full_original_stem_allowed_but_sof_source_content_not(self):
        self.change(lambda d:self.item(d,1).update(source_stem="unlicensed original SOF paper"))
        with self.assertRaises(SeedError):self.check()


if __name__=="__main__":
    unittest.main()
