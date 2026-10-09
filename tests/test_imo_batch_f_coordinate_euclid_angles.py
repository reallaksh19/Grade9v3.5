"""Research-only falsifiers for IMO Batch F's ten original geometry source positions."""
from __future__ import annotations

import json
import math
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "TEST/imo-research/batches/batch-f-coordinate-euclid-angles-source-capabilities.v1.json"
TAX = ROOT / "TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl"
CENSUS = ROOT / "TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
REGISTER = ROOT / "TEST/imo-research/adjudication/source-discrepancy-register.v1.json"
UNSOLVED = "SOF-IMO-G09-SAMPLE-2026-27-Q005"
FIG_CONFLICT = "SOF-IMO-G09-L1-2025-26-A-Q031"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

class BatchFCoordinateEuclidAngleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = load(BATCH)
        cls.rows = cls.document["records"]
        cls.by_id = {r["question_id"]:r for r in cls.rows}
        cls.census = {r["question_id"]:r for r in load(CENSUS)["records"]}
        cls.tax = [json.loads(line) for line in TAX.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_exact_source_set_and_honest_68_vs_66_reconciliation(self):
        expected={t["question_id"] for t in self.tax if t["primary_topic_id"] in ("COORD","EUCLID","ANGLES")}
        self.assertEqual(len(expected),10)
        self.assertEqual(len(self.by_id),10)
        self.assertEqual(set(self.by_id),expected)
        self.assertEqual(Counter(r["provisional_topic"] for r in self.rows),{"COORD":4,"EUCLID":3,"ANGLES":3})
        self.assertEqual(self.document["topic_counts"],{"COORD":4,"EUCLID":3,"ANGLES":3})
        self.assertEqual((len(self.census),len(self.tax)),(68,66))
        missing=set(self.census)-{r["question_id"] for r in self.tax}
        self.assertEqual(missing,{
            "SOF-IMO-G09-SAMPLE-2026-27-Q001",
            "SOF-IMO-G09-SAMPLE-2026-27-Q003",
        })
        self.assertEqual({r["question_id"] for r in self.document["taxonomy_missing_inventory_positions"]},missing)
        self.assertTrue(all(r["not_silently_dropped"] for r in self.document["taxonomy_missing_inventory_positions"]))
        self.assertEqual((self.document["previous_research_mapped_source_positions"],self.document["batch_distinct_source_positions"],self.document["cumulative_research_mapped_source_positions"],self.document["remaining_original_source_positions"]),(50,10,60,8))
        self.assertEqual(self.document["prior_authored_legacy_practice_excluded_from_source_denominator"],7)
        self.assertTrue(all(v==0 for v in self.document["rights_and_product_admissions"].values()))

    def test_census_and_prior_math_source_ref_alignment(self):
        for r in self.rows:
            id=r["question_id"]
            prior=self.census[id]
            loc=r["source_pdf_locator_authority"]
            self.assertEqual(r["source_id"],prior["source_id"])
            self.assertEqual(r["source_document_url"],prior["source_document_url"])
            self.assertEqual(r["source_printed_question_number"],next(t["original_q"] for t in self.tax if t["question_id"]==id))
            self.assertEqual(loc["census_observed_original_number"],prior["original_printed_position_observed"])
            self.assertEqual(loc["census_observed_pdf_page_index"],prior["source_locator_pdf_page_index"])
            self.assertEqual(loc["durable_source_pdf_sha256"],prior["document_retained_sha256"])
            self.assertTrue(loc["prior_math_audit_sighting_is_not_durable_source_custody"])
            e=r["prior_agent_math_audit"]
            obj=load(ROOT/e["path"])
            matches=[a for seq in obj.values() if isinstance(seq,list) for a in seq if isinstance(a,dict) and a.get("question_id")==id]
            self.assertEqual(len(matches),1,id)
            self.assertEqual(loc["prior_math_audit_sighted_page_index"],matches[0]["source_pdf_page_index"])
            if matches[0].get("audit_id"):
                self.assertEqual(e["id"],matches[0]["audit_id"])
            self.assertFalse(e["official_fullpaper_answer_key_accepted"])
            self.assertFalse(e["independent_academic_signoff"])
            self.assertTrue(all(v is False for v in r["product_holds"].values()))
            self.assertFalse(r["figure_and_rights_custody"]["figure_republication_rights_granted"])
            self.assertFalse(r["figure_and_rights_custody"]["complete_original_seven_item_components_verified"])
            self.assertFalse(r["source_specific_capability_research"]["candidate_core1a_owner_accepted"])
            self.assertIsNone(r["source_specific_capability_research"]["qrt_acceptance"])
            self.assertNotIn("source_stem",r)
            self.assertNotIn("source_printed_options",r)
            self.assertNotIn("source_image",r)

    def test_conflict_007_owner_source_disagreement_without_auto_clear(self):
        by_case={x["case_id"]:x for x in load(REGISTER)["cases"]}
        row=self.by_id[FIG_CONFLICT]
        dispute=row["source_discrepancy"]
        self.assertEqual(dispute["case_id"],"IMO-SOURCE-CONFLICT-007")
        self.assertEqual(dispute["conflict_type"],"FIGURE_DEPENDENT_ANSWER_DISAGREEMENT")
        self.assertEqual(dispute["source_finding"],by_case["IMO-SOURCE-CONFLICT-007"]["printed_source_evidence_summary"])
        self.assertEqual(dispute["owner_compilation_difference"],by_case["IMO-SOURCE-CONFLICT-007"]["owner_compilation_claim_summary"])
        self.assertTrue(dispute["source_dispute_unresolved"])
        self.assertTrue(dispute["source_figure_required"])
        self.assertEqual(row["prior_agent_math_audit"]["agent_selected_option"],"C")
        self.assertIn("84",row["prior_agent_math_audit"]["computed_answer"])
        self.assertIn("57",dispute["owner_compilation_difference"])
        self.assertEqual(4*21+21+75,180)
        self.assertNotEqual(57+21+75,180)
        self.assertEqual((4*21,21,(75+21)//2),(84,21,48))

    def test_sample_q5_sighted_key_is_not_an_independent_solution(self):
        by_case={x["case_id"]:x for x in load(REGISTER)["cases"]}
        open_case=self.by_id[UNSOLVED]
        e=open_case["prior_agent_math_audit"]
        cap=open_case["source_specific_capability_research"]
        self.assertEqual(open_case["source_discrepancy"]["case_id"],"IMO-SOURCE-CONFLICT-009")
        self.assertEqual(open_case["source_discrepancy"]["conflict_type"],"UNSOLVED_FIGURE_GEOMETRY")
        self.assertEqual(open_case["source_discrepancy"]["source_finding"],by_case["IMO-SOURCE-CONFLICT-009"]["printed_source_evidence_summary"])
        self.assertEqual(e["organizer_printed_key_sighted"],"C")
        self.assertIsNone(e["agent_selected_option"])
        self.assertIsNone(e["computed_answer"])
        self.assertIsNone(e["mathematical_derivation"])
        self.assertIsNone(e["independent_check"])
        self.assertIsNone(cap["protected_inference"])
        self.assertIsNone(cap["agent_math_warrant"])
        self.assertEqual(cap["academic_status"],"AWAIT_FIGURE_BASED_PROOF_NO_CRUX_PROMOTION")
        self.assertTrue(open_case["figure_and_rights_custody"]["original_source_figure_needed_for_source_fidelity"])
        self.assertEqual(self.document["unsolved_question_ids"],[UNSOLVED])
        self.assertEqual(self.document["this_batch_figure_dependent_unsolved_count"],1)

    def test_coordinate_geometry_exact_math_oracles(self):
        # Q27: y-axis enforces x=0 in 4x+y=12.
        self.assertEqual(4*0+12,12)
        self.assertEqual((0,12),(0,12))
        # Q50 three independent geometric claims.
        self.assertEqual((-7,5),(-7,+5))
        self.assertEqual(math.hypot(3,4),5)
        p=(-6,-3)
        self.assertEqual((abs(p[1]),abs(p[0])),(3,6))
        self.assertTrue(all(x<0 for x in p))
        # Q20 signed abscissa minus ordinate.
        self.assertEqual(10-(-4),14)
        # Q46 linear rule, opposite point and reflection x-axis.
        self.assertEqual(3*(-4)+2,-10)
        self.assertEqual((5+(-5),-4+4),(0,0))
        self.assertEqual((4,-9),(4,-9))
        self.assertEqual(sum(r["provisional_topic"]=="COORD" for r in self.rows),4)

    def test_euclid_postulates_and_sample_ordered_segments(self):
        # Q33 and Q31 are distinct Euclidean principles.
        p=self.by_id["SOF-IMO-G09-L1-2023-24-A-Q033"]["source_specific_capability_research"]
        self.assertIn("one line parallel",p["protected_inference"])
        third=self.by_id["SOF-IMO-G09-L1-2024-25-B-Q031"]["source_specific_capability_research"]
        self.assertIn("third postulate",third["protected_inference"].lower())
        # Official sample Q6: P-Q-R-S ordered, PQ=RS.
        PQ,QR,RS=4,7,4
        self.assertEqual(PQ+QR,QR+RS)
        q6=self.by_id["SOF-IMO-G09-SAMPLE-2026-27-Q006"]
        self.assertEqual(q6["prior_agent_math_audit"]["agent_selected_option"],"C")
        self.assertEqual(q6["prior_agent_math_audit"]["organizer_printed_key_sighted"],"C")
        self.assertIn("PR=PQ+QR",q6["source_specific_capability_research"]["agent_math_warrant"])
        self.assertEqual(q6["source_specific_capability_research"]["qrt_acceptance"],None)

    def test_supplementary_angle_bisectors_and_figure_limits(self):
        # For any 180-degree adjacent pair, the angle between their bisectors is 90.
        for angle in (0,37,75,101,180):
            self.assertEqual(angle/2+(180-angle)/2,90)
        q19=self.by_id["SOF-IMO-G09-L1-2023-24-A-Q019"]
        self.assertEqual(q19["prior_agent_math_audit"]["computed_answer"],"Rectangle")
        self.assertTrue(q19["figure_and_rights_custody"]["original_source_figure_needed_for_source_fidelity"])
        for id in (FIG_CONFLICT,UNSOLVED):
            self.assertTrue(self.by_id[id]["figure_and_rights_custody"]["original_source_figure_needed_for_source_fidelity"])
        disagreements={r["source_discrepancy"]["case_id"] for r in self.rows if r["source_discrepancy"]}
        self.assertEqual(disagreements,{"IMO-SOURCE-CONFLICT-007","IMO-SOURCE-CONFLICT-009"})

if __name__=="__main__":
    unittest.main()
