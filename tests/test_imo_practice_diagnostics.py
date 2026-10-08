"""Adversarial tests for seven non-SOF original-practice structured diagnostics."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_practice_diagnostics import diagnose,validate_diagnostics  # noqa: E402


class ResearchPracticeDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        ctx=tempfile.TemporaryDirectory()
        self.addCleanup(ctx.cleanup)
        self.json=Path(ctx.name)/"diagnostics.json"
        self.json.write_bytes((ROOT/"original-practice"/"diagnostics"/
            "structured-checker-cases.v1.json").read_bytes())

    def read(self):
        return json.loads(self.json.read_text(encoding="utf-8"))

    def edit(self,fn):
        doc=self.read()
        fn(doc)
        self.json.write_text(json.dumps(doc))

    @staticmethod
    def packet(doc,n):
        return next(r for r in doc["records"] if r["candidate_id"].endswith(f"-{n:03d}"))

    def check(self):
        return validate_diagnostics(data_path=self.json)

    def test_all_seven_packets_and_18_misconception_probes(self):
        r=self.check()
        self.assertEqual((r["question_count"],r["distinct_provisional_qrt_cells"],
                          r["targeted_misconception_probes"]),(7,7,18))
        self.assertEqual((r["accepted_qrt_cells"],r["core_ready"],
                          r["learner_published"]),(0,0,0))

    def test_positive_equivalent_structured_responses(self):
        for i,p in enumerate(self.read()["records"],1):
            self.assertEqual(diagnose(i,p["accepted_illustrative_response"]),"PASS")
            self.assertEqual(diagnose(i,p["equivalent_illustrative_response"]),"PASS")

    def test_targeted_wrong_ideas_stay_detectable(self):
        for i,p in enumerate(self.read()["records"],1):
            for misconception in p["misconception_probes"]:
                self.assertEqual(diagnose(i,misconception["response"]),misconception["code"])

    def test_proof_examples_cannot_replace_universal_argument(self):
        self.assertEqual(diagnose(1,{"claim_true":True,"even_factor":True,
                         "factor_three":True,"proof_basis":"example_only"}),"EXAMPLE_ONLY")

    def test_missing_divisibility_by_three_is_reported(self):
        self.assertEqual(diagnose(1,{"claim_true":True,"even_factor":True,
                         "factor_three":False,"proof_basis":"residue_mod6"}),"MISSING_THREE_FACTOR")

    def test_coordinate_axis_swap_is_reported(self):
        self.assertEqual(diagnose(2,{"x":3,"y":-4}),"AXES_SWAPPED")

    def test_wrong_circle_ends_are_flagged(self):
        self.assertEqual(diagnose(4,{"surface_scope":"both_ends_included","area_cm2":1188}),
                         "END_CAPS_INCLUDED")

    def test_diagram_reflection_order_mistake_is_diagnosed(self):
        self.assertEqual(diagnose(7,{"vertices":{"P":[2,-1],"Q":[-3,-1],"R":[0,2]},
                    "twice_area":15,"area_preserved":True}),
                    "REFLECTION_TRANSLATION_MISORDER")

    def test_boolean_is_not_treated_as_numeric_coordinate(self):
        self.assertEqual(diagnose(2,{"x":True,"y":3}),"INVALID_STRUCTURE")

    def test_nan_not_accepted_as_area(self):
        self.assertEqual(diagnose(4,{"surface_scope":"curved_only","area_cm2":float("nan")}),
                         "INVALID_STRUCTURE")

    def test_unknown_student_prose_not_auto_graded(self):
        self.assertEqual(diagnose(1,"My proof is that the product is even"),"INVALID_STRUCTURE")

    def test_missing_response_field_not_treated_as_pass(self):
        self.assertEqual(diagnose(6,{"booklet_rupees":18,"card_rupees":29}),"INVALID_STRUCTURE")

    def test_tampered_correct_example_fails_validation(self):
        self.edit(lambda d:self.packet(d,6)["accepted_illustrative_response"].update(
                  target_total_rupees=123))
        with self.assertRaises(SeedError):self.check()

    def test_critical_error_case_cannot_be_omitted(self):
        self.edit(lambda d:self.packet(d,5)["misconception_probes"].pop())
        with self.assertRaises(SeedError):self.check()

    def test_qrt_cell_cannot_be_accepted_from_diagnostics(self):
        self.edit(lambda d:self.packet(d,3).update(qrt_acceptance="ACCEPTED"))
        with self.assertRaises(SeedError):self.check()

    def test_no_core_ready_claim_from_simulated_answers(self):
        self.edit(lambda d:self.packet(d,7).update(core_ready=True))
        with self.assertRaises(SeedError):self.check()

    def test_no_original_sof_stem_copied_into_diagnostics(self):
        self.edit(lambda d:self.packet(d,1).update(sof_stem="Original exam text"))
        with self.assertRaises(SeedError):self.check()

    def test_source_candidate_ids_must_match_merged_practice(self):
        self.edit(lambda d:self.packet(d,2).update(candidate_id="SOF-IMO-G09-SAMPLE-2026-27-Q002"))
        with self.assertRaises(SeedError):self.check()

    def test_declared_feedback_hint_must_be_actionable(self):
        self.edit(lambda d:self.packet(d,3)["misconception_probes"][0].update(actionable_hint="wrong"))
        with self.assertRaises(SeedError):self.check()

    def test_cannot_call_this_production_free_text_grader(self):
        self.edit(lambda d:d.update(scope="LIVE_FREE_TEXT_GRADED"))
        with self.assertRaises(SeedError):self.check()


if __name__=="__main__":
    unittest.main()
