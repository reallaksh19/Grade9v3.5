"""IMO Batch E: eight research-only statistics/probability source positions."""
from __future__ import annotations

import itertools
import json
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT/"TEST/imo-research/batches/batch-e-statistics-probability-source-capabilities.v1.json"
CENSUS = ROOT/"TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
TAX = ROOT/"TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl"
REGISTER = ROOT/"TEST/imo-research/adjudication/source-discrepancy-register.v1.json"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

class BatchEStatisticsProbabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=read(E)
        cls.rows=cls.data["records"]
        cls.by_id={r["question_id"]:r for r in cls.rows}

    def test_eight_exact_taxonomy_and_true_68_denominator(self):
        corpus={r["question_id"]:r for r in read(CENSUS)["records"]}
        self.assertEqual(len(corpus),68)
        topic_rows=[json.loads(line) for line in TAX.read_text(encoding="utf-8").splitlines() if line.strip()]
        expected={r["question_id"] for r in topic_rows if r["primary_topic_id"] in ("STATISTICS","PROBABILITY")}
        self.assertEqual(len(expected),8)
        self.assertEqual(set(self.by_id),expected)
        self.assertEqual(len(self.rows),len(self.by_id))
        self.assertEqual(Counter(r["provisional_primary_topic"] for r in self.rows),{"STATISTICS":4,"PROBABILITY":4})
        self.assertEqual(self.data["source_denominator"],68)
        self.assertEqual((self.data["previously_producer_research_mapped"],self.data["this_batch_positions"],self.data["cumulative_source_research_mapped"],self.data["remaining_source_positions_after_this_batch"]),(42,8,50,18))
        self.assertEqual(self.data["legacy_authored_practice_positions_separate"],7)
        for r in self.rows:
            source=corpus[r["question_id"]]
            self.assertEqual(r["source_id"],source["source_id"])
            self.assertEqual(r["source_document_url"],source["source_document_url"])
            self.assertEqual(r["custody_pdf_page_index"],source["source_locator_pdf_page_index"])
            self.assertEqual(r["custody_observed_question_number"],source["original_printed_position_observed"])
            self.assertEqual(r["source_locator_status_from_custody"],source["source_locator_basis"])
            self.assertEqual(r["provisional_primary_topic"],source["provisional_topic_id"])
            if source["original_printed_position_observed"] is None:
                self.assertIsNone(r["custody_pdf_page_index"])
                self.assertIsNotNone(r["prior_agent_pdf_page_index"])
                self.assertFalse(r["figure_and_custody"]["exact_printed_locator_retained_in_custody"])

    def test_prior_agent_math_identity_and_separate_source_authority(self):
        allowed={
            "TEST/imo-research/seed/math_audit_batch01.json",
            "TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json",
            "TEST/imo-research/verification/fullpaper-audit-b03.v1.json",
            "TEST/imo-research/verification/fullpaper-audit-b04.v1.json",
        }
        for r in self.rows:
            evidence=r["source_math_research"]
            self.assertIn(evidence["audit_path"],allowed)
            audit=read(ROOT/evidence["audit_path"])
            matching=[x for arr in audit.values() if isinstance(arr,list) for x in arr if isinstance(x,dict) and x.get("question_id")==r["question_id"]]
            self.assertEqual(len(matching),1,r["question_id"])
            self.assertEqual(evidence["audit_id"],matching[0]["audit_id"])
            self.assertEqual(r["prior_agent_pdf_page_index"],matching[0]["source_pdf_page_index"])
            self.assertTrue(evidence["previous_agent_math_explanation"])
            self.assertTrue(evidence["agent_computed_result"])
            self.assertTrue(evidence["agent_mathematically_selected_option"])
            self.assertFalse(evidence["accepted_fullpaper_key_receipt"])
            self.assertFalse(evidence["independently_peer_approved"])
            self.assertTrue(all(v is False for v in r["product_and_source_holds"].values()))
            self.assertFalse(r["figure_and_custody"]["source_diagram_publication_allowed"])
            self.assertFalse(r["figure_and_custody"]["source_item_complete_component_custody"])
            self.assertIsNone(r["protected_capability_research"]["governing_qrt_cell"])
            self.assertFalse(r["protected_capability_research"]["candidate_core1a_authorized"])
            self.assertNotIn("source_stem",r)
            self.assertNotIn("source_figure_file",r)
        self.assertTrue(all(v==0 for v in self.data["rights_and_product_holds"].values()))

    def test_two_original_chart_conflicts_and_shared_figure_still_held(self):
        bycase={x["case_id"]:x for x in read(REGISTER)["cases"]}
        expected={
            "SOF-IMO-G09-L1-2024-25-B-Q016":"IMO-SOURCE-CONFLICT-004",
            "SOF-IMO-G09-L1-2025-26-A-Q032":"IMO-SOURCE-CONFLICT-008",
            "SOF-IMO-G09-L1-2025-26-A-Q033":"IMO-SOURCE-CONFLICT-008",
        }
        observed={id:r["source_discrepancy"]["case_id"] for id,r in self.by_id.items() if r["source_discrepancy"]}
        self.assertEqual(observed,expected)
        self.assertEqual(set(self.data["source_conflict_case_ids"]),{"IMO-SOURCE-CONFLICT-004","IMO-SOURCE-CONFLICT-008"})
        self.assertEqual(self.data["source_conflict_affected_distinct_positions"],3)
        for id,case in observed.items():
            row=self.by_id[id]["source_discrepancy"]
            self.assertEqual(row["conflict_type"],bycase[case]["conflict_type"])
            self.assertEqual(row["printed_finding"],bycase[case]["printed_source_evidence_summary"])
            self.assertEqual(row["owner_compilation_claim"],bycase[case]["owner_compilation_claim_summary"])
            self.assertTrue(row["source_figure_required"])
            self.assertFalse(row["source_conflict_cleared"])
            self.assertFalse(row["owner_source_edit_authorized"])
        q32,q33=(self.by_id["SOF-IMO-G09-L1-2025-26-A-Q"+i] for i in ("032","033"))
        self.assertEqual(q32["owner_compilation_entry"],q33["owner_compilation_entry"])
        self.assertEqual(q32["custody_pdf_page_index"],q33["custody_pdf_page_index"])
        self.assertNotEqual(q32["protected_capability_research"]["family"],q33["protected_capability_research"]["family"])
        self.assertTrue(self.data["printed_shared_chart_split"]["preserve_two_distinct_printed_question_identities"])

    def test_statistics_four_source_specific_math_oracles(self):
        # A count and percentage determine a common pie-chart denominator.
        total=Fraction(140,1)/Fraction(35,100)
        self.assertEqual(total,400)
        self.assertEqual(Fraction(15,100)*total,60)
        # Distinct original Q32/Q33 share a chart but ask distinct conversions.
        self.assertEqual(Fraction(70+55,360)*720,250)
        other_angle=360-sum((80,75,55,70))
        self.assertEqual(other_angle,80)
        self.assertEqual(Fraction(other_angle,360)*100,Fraction(200,9))
        # Three independently matched statistical interpretations.
        lower=2*10-15
        self.assertEqual((lower+15)/2,10)
        self.assertEqual(93-18,75)
        self.assertEqual(Fraction(4,10)*Fraction(2500,50),20)
        self.assertEqual(self.by_id["SOF-IMO-G09-L1-2025-26-A-Q047"]["source_math_research"]["agent_computed_result"],"P=(ii), Q=(iii), R=(i)")

    def test_probability_four_different_sample_spaces(self):
        self.assertEqual(Fraction(400-250,400),Fraction(3,8))
        self.assertEqual(Fraction(250,400)+Fraction(150,400),1)
        self.assertEqual(Fraction(5,3+5+4),Fraction(5,12))
        self.assertEqual(Fraction(3+5+4,12),1)
        pairs=list(itertools.product(range(1,7),repeat=2))
        hits=[(a,b) for a,b in pairs if a+b>9]
        self.assertEqual((len(pairs),len(hits)),(36,6))
        self.assertEqual(Fraction(len(hits),len(pairs)),Fraction(1,6))
        self.assertEqual(Counter(a+b for a,b in hits),{10:3,11:2,12:1})
        def prime(n):
            return n>=2 and all(n%d!=0 for d in range(2,int(n**0.5)+1))
        cards=list(range(51,101))
        primes=[x for x in cards if prime(x)]
        self.assertEqual(primes,[53,59,61,67,71,73,79,83,89,97])
        self.assertEqual((len(cards),len(primes)),(50,10))
        self.assertEqual(Fraction(len(cards)-len(primes),len(cards)),Fraction(4,5))
        self.assertEqual(Fraction(len(primes),len(cards))+Fraction(40,50),1)

    def test_inference_priorities_do_not_pretend_one_generic_qrt_lesson(self):
        families=[r["protected_capability_research"]["family"] for r in self.rows]
        self.assertEqual(len(set(families)),8)
        self.assertIn("ordered",self.by_id["SOF-IMO-G09-L1-2024-25-B-Q027"]["protected_capability_research"]["decisive_inference"].lower())
        self.assertIn("individual balls",self.by_id["SOF-IMO-G09-L1-2023-24-A-Q040"]["protected_capability_research"]["decisive_inference"])
        self.assertIn("missing",self.by_id["SOF-IMO-G09-L1-2025-26-A-Q033"]["protected_capability_research"]["decisive_inference"])
        self.assertIn("three",self.by_id["SOF-IMO-G09-L1-2025-26-A-Q047"]["protected_capability_research"]["conditions_and_limits"].lower())
        self.assertEqual(sum(1 for x in self.rows if x["figure_and_custody"]["figure_required"]),3)

if __name__=="__main__":
    unittest.main()
