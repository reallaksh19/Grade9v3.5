"""Research-only Batch D: eleven geometric source decisions, no product authority."""
from __future__ import annotations

import json
import math
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"TEST/imo-research/batches/batch-d-geometry-mensuration-source-capabilities.v1.json"
CENSUS=ROOT/"TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
TAX=ROOT/"TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl"
REGISTER=ROOT/"TEST/imo-research/adjudication/source-discrepancy-register.v1.json"

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

class BatchDGeometrySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=load(FILE)
        cls.rows=cls.d["records"]

    def test_exact_eleven_and_68_position_source_taxonomy(self):
        self.assertEqual(len(self.rows),11)
        self.assertEqual(len({r["question_id"] for r in self.rows}),11)
        tax=[json.loads(line) for line in TAX.read_text(encoding="utf-8").splitlines() if line.strip()]
        expected={r["question_id"] for r in tax if r["primary_topic_id"] in ("MENSURATION","TRIANGLES")}
        self.assertEqual({r["question_id"] for r in self.rows},expected)
        sources={r["question_id"]:r for r in load(CENSUS)["records"]}
        self.assertEqual(len(sources),68)
        self.assertEqual(self.d["authentic_source_programme_denominator"],68)
        self.assertEqual((self.d["prior_producer_batched_source_positions"],self.d["this_batch"],self.d["cumulative_distinct_mapped_positions"],self.d["future_unmapped_positions"]),(31,11,42,26))
        self.assertEqual(self.d["topic_counts"],{"MENSURATION":6,"TRIANGLES":5})
        self.assertEqual(self.d["legacy_authored_practice_separate"],7)
        for r in self.rows:
            c=sources[r["question_id"]]
            self.assertEqual(r["source_id"],c["source_id"])
            self.assertEqual(r["source_pdf_page_index"],c["source_locator_pdf_page_index"])
            self.assertEqual(r["source_url"],c["source_document_url"])
            self.assertEqual(r["printed_question_number"],c["original_printed_position_observed"])
            self.assertEqual(r["primary_topic_id"],c["provisional_topic_id"])

    def test_exact_source_math_evidence_join_and_no_admission(self):
        for r in self.rows:
            a=r["research_math_audit"]
            self.assertIn(a["file"],(
                "TEST/imo-research/seed/math_audit_batch01.json",
                "TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json",
                "TEST/imo-research/verification/fullpaper-audit-b03.v1.json",
                "TEST/imo-research/verification/fullpaper-audit-b04.v1.json",
                "TEST/imo-research/verification/official-sample-2026-27-math-qrt-pilot.v1.json"))
            raw=load(ROOT/a["file"])
            records=[x for values in raw.values() if isinstance(values,list) for x in values if isinstance(x,dict) and x.get("question_id")==r["question_id"]]
            self.assertEqual(len(records),1,r["question_id"])
            self.assertTrue(a["agent_result"] and a["agent_original_derivation"] and a["agent_selected_printed_option"])
            self.assertFalse(r["source_capability_research"]["canonical_core1a_accepted"])
            holds=r["product_holds"]
            self.assertTrue(all(v is False for k,v in holds.items() if k!="qrt_cell_accepted"))
            self.assertIsNone(holds["qrt_cell_accepted"])
            self.assertFalse(r["figure_dependency"]["reproduce_figure"])
            self.assertNotIn("source_original_text",r)
            self.assertNotIn("source_pdf_bytes",r)
        self.assertTrue(all(v==0 for v in self.d["rights_admission_status"].values()))

    def test_preserve_distractor_conflict_002_and_sample_figure_hold(self):
        conflicts=[r for r in self.rows if r["source_discrepancy"]]
        self.assertEqual([r["question_id"] for r in conflicts],["SOF-IMO-G09-L1-2023-24-A-Q017"])
        record=conflicts[0]["source_discrepancy"]
        case=next(x for x in load(REGISTER)["cases"] if x["case_id"]=="IMO-SOURCE-CONFLICT-002")
        self.assertEqual(record["conflict_type"],case["conflict_type"])
        self.assertEqual(record["printed_vs_owner_option_summary"],case["printed_source_evidence_summary"])
        self.assertEqual(record["conflict_type"],"DISTRACTOR_OPTION_REPLACEMENT")
        self.assertEqual(conflicts[0]["research_math_audit"]["agent_result"],"4:9")
        sample=next(x for x in self.rows if x["question_id"]=="SOF-IMO-G09-SAMPLE-2026-27-Q010")
        self.assertTrue(sample["figure_dependency"]["required_for_source_fidelity"])
        self.assertFalse(sample["figure_dependency"]["reproduce_figure"])
        self.assertIn("perpendicular",sample["source_capability_research"]["source_scope_and_domain_limit"])

    def test_independent_bounded_mathematical_witnesses(self):
        # 2023 right triangle 24,32,40; separate 5,12,13 altitude test.
        self.assertEqual(24**2+32**2,40**2)
        area=F(24*32,2)
        self.assertEqual(area,384)
        self.assertEqual(2*area/24,32)
        self.assertEqual(F(2*(5*12//2),13),F(60,13))
        # 2024 constrained 13,17,20 triangle, Heron radicand.
        self.assertTrue(13+17>20)
        s=F(13+17+20,2)
        self.assertEqual(s*(s-13)*(s-17)*(s-20),12000)
        self.assertEqual(12000, (20**2)*30)
        # Scale factors/percentage gains are distinct.
        self.assertEqual(F(7**2,14**2),F(1,4))
        self.assertEqual(5**2,25)
        self.assertEqual((2**2-1)*100,300)
        # Cone volume: equal radius cancels square-radius factor.
        self.assertEqual(F(4,9),F(4*8*8,9*8*8))
        # Curved cone ratio r1*l1/(r2*l2)=2 with l2=2*l1.
        self.assertEqual(F(4*1,1*2),2)
        # Hemisphere area, square-metre conversion, rate per 100 cm2.
        pi=F(22,7)
        radius=F("17.6")/(2*pi)
        self.assertEqual(radius,F(14,5))
        hemi=2*pi*radius**2
        self.assertEqual(hemi,F("49.28"))
        self.assertEqual(hemi*10000*F(8,100),39424)
        # Tent footprint and air volume independently have different units.
        self.assertEqual(F(3*(11*20),11*4),15)
        # Three solid claims in 2025 source, not a general shape identity.
        self.assertEqual(F(3*(15**2)*4,10**2),27)
        self.assertEqual(12*F("3.14")*4**3,F("2411.52"))
        sphere=F(4,3)*F("3.14")*F(7,2)**3
        self.assertTrue(abs(float(sphere)-179.5)<0.02)
        self.assertNotEqual(sphere,F("185.76"))
        # Figured organizer item: scaled isosceles triangles can be similar but not congruent.
        self.assertEqual((3**2+4**2),5**2)
        self.assertEqual((6**2+8**2),10**2)
        self.assertNotEqual(3,6)

    def test_comparative_inference_does_not_promote_core_design(self):
        ids={r["question_id"]:r for r in self.rows}
        a=ids["SOF-IMO-G09-L1-2023-24-A-Q029"]["source_capability_research"]
        b=ids["SOF-IMO-G09-L1-2024-25-B-Q035"]["source_capability_research"]
        self.assertNotEqual(a["family"],b["family"])
        self.assertIn("right-angle",a["comparison_to_pr306_design"].lower())
        self.assertIn("linked side conditions",b["decisive_inference"])
        q=ids["SOF-IMO-G09-L1-2023-24-A-Q049"]["source_capability_research"]
        self.assertIn("300%",q["math_warrant"])
        self.assertIn("60/13",q["math_warrant"])
        self.assertEqual(self.d["this_batch_conflict_ids"],["IMO-SOURCE-CONFLICT-002"])

if __name__=="__main__":
    unittest.main()
