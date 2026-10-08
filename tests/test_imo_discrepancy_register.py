"""Negative tests for printed-paper/source-attachment discrepancy adjudication custody."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_discrepancy_register import validate_register, mathematical_checks  # noqa: E402


class ConflictLedgerTests(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        root=Path(d.name)
        self.seed=root/"seed"; self.ver=root/"verification";self.adt=root/"adjudication"
        for x in (self.seed,self.ver,self.adt):x.mkdir()
        for fn in ("questions.jsonl","sources.json","source_observations.json","math_audit_batch01.json"):
            (self.seed/fn).write_bytes((ROOT/"seed"/fn).read_bytes())
        for fn in ("fullpaper-source-math-batch02.v1.json",
                   "official-sample-2026-27-math-qrt-pilot.v1.json"):
            (self.ver/fn).write_bytes((ROOT/"verification"/fn).read_bytes())
        self.registry=self.adt/"source-discrepancy-register.v1.json"
        self.registry.write_bytes((ROOT/"adjudication"/self.registry.name).read_bytes())

    def check(self):
        return validate_register(self.seed,self.ver,self.registry)

    def modify(self,change):
        d=json.loads(self.registry.read_text(encoding="utf-8"))
        change(d)
        self.registry.write_text(json.dumps(d))

    def case(self,d,number):
        return next(x for x in d["cases"] if x["case_id"]==f"IMO-SOURCE-CONFLICT-{number:03d}")

    def test_valid_discrepancy_census_stays_quarantined(self):
        v=self.check()
        self.assertEqual((v["cases"],v["distinct_source_positions_in_cases"],v["core_ready"]),(10,11,0))
        self.assertEqual(v["accepted_qrt_cells"],0)

    def test_math_oracles_for_compiler_answer_and_diagram(self):
        r=mathematical_checks()
        self.assertEqual(r["IMO-SOURCE-CONFLICT-001"],"5")
        self.assertEqual(r["IMO-SOURCE-CONFLICT-003"],"-5/12")
        self.assertEqual(r["IMO-SOURCE-CONFLICT-007"],"a=84°, b=21°, c=48°")
        self.assertIn("3/80",r["IMO-SOURCE-CONFLICT-010"])

    def test_source_answer_dispute_cannot_be_erased(self):
        self.modify(lambda d:self.case(d,1).update(owner_compilation_option_claim="B"))
        with self.assertRaises(SeedError):self.check()

    def test_q18_option_reorder_must_stay_visible(self):
        self.modify(lambda d:self.case(d,3).update(printed_option_selection_by_math_or_key="A"))
        with self.assertRaises(SeedError):self.check()

    def test_identity_cannot_be_replaced_with_inverse(self):
        self.modify(lambda d:self.case(d,6).update(source_finding_status="RESOLVED_INVERSE"))
        with self.assertRaises(SeedError):self.check()

    def test_source_q31_diagram_answer_cannot_be_changed(self):
        self.modify(lambda d:self.case(d,7).update(agent_mathematical_result="a=57°, b=21°, c=48°"))
        with self.assertRaises(SeedError):self.check()

    def test_2024_q44_exam_section_source_identity_is_pinned(self):
        self.modify(lambda d:self.case(d,5).update(source_pdf_page_index=7))
        with self.assertRaises(SeedError):self.check()

    def test_shared_pie_chart_two_original_positions_not_silently_joined(self):
        self.modify(lambda d:self.case(d,8).update(question_ids=self.case(d,8)["question_ids"][:1]))
        with self.assertRaises(SeedError):self.check()

    def test_original_sample_q5_remains_without_calculated_answer(self):
        self.modify(lambda d:self.case(d,9).update(agent_mathematical_result="90°−x/2"))
        with self.assertRaises(SeedError):self.check()

    def test_sample_q9_radical_result_not_fudged(self):
        self.modify(lambda d:self.case(d,10).update(agent_mathematical_result="Statement II = 0.03"))
        with self.assertRaises(SeedError):self.check()

    def test_official_sample_key_sighting_not_accepted_academically(self):
        self.modify(lambda d:self.case(d,10).update(independent_academic_acceptance=True))
        with self.assertRaises(SeedError):self.check()

    def test_source_mirror_cannot_claim_official_host(self):
        self.modify(lambda d:self.case(d,2).update(source_host_class="SOF_ORGANIZER_HOST"))
        with self.assertRaises(SeedError):self.check()

    def test_accepting_qrt_cell_without_review_fails(self):
        self.modify(lambda d:self.case(d,4).update(accepted_qrt_cell="QRT-REPRESENT-D2"))
        with self.assertRaises(SeedError):self.check()

    def test_rights_permission_cannot_be_assumed(self):
        self.modify(lambda d:self.case(d,7).update(figure_reuse_rights_status="CLEARED"))
        with self.assertRaises(SeedError):self.check()

    def test_dispute_case_cannot_disappear(self):
        self.modify(lambda d:d["cases"].pop())
        with self.assertRaises(SeedError):self.check()

    def test_no_original_scan_transcription_published(self):
        self.modify(lambda d:self.case(d,1).update(stem="Original unlicensed paper stem"))
        with self.assertRaises(SeedError):self.check()


if __name__=="__main__":
    unittest.main()
