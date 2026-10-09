"""Batch C 12-source quantitative reasoning crosswalk: evidence, warrants, non-grants."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IMO=ROOT/"TEST"/"imo-research"
CROSS=IMO/"batches"/"batch-c-quant-source-capabilities.v1.json"

def read(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

class BatchCQuantitativeResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(CROSS.read_text(encoding="utf-8"))
        cls.census=read("TEST/imo-research/intake/core2-source-custody-eligibility.v1.json")
        cls.topics=[json.loads(line) for line in
                    (IMO/"taxonomy"/"seed-question-topic-map.v1.jsonl")
                    .read_text(encoding="utf-8").splitlines() if line.strip()]
        cls.audits={
            "TEST/imo-research/seed/math_audit_batch01.json":("questions","computed_answer","math_derived_printed_choice","independent_computation"),
            "TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json":("observations","independent_agent_answer","printed_correct_choice_by_agent","independent_mathematical_derivation"),
            "TEST/imo-research/verification/fullpaper-audit-b03.v1.json":("records","computed_result","mathematically_selected_printed_option","agent_mathematical_derivation"),
            "TEST/imo-research/verification/fullpaper-audit-b04.v1.json":("records","independent_agent_result","printed_choice_selected_by_math","mathematical_derivation"),
        }

    def test_full_denominator_and_batch_nonoverlap(self):
        d=self.doc
        self.assertEqual(len(self.census["records"]),68)
        self.assertEqual(d["programme_authentic_source_positions"],68)
        self.assertEqual(d["source_allocation_across_three_fullpapers_and_sample"],[24,12,22,10])
        self.assertEqual(d["separate_authored_practice_question_count"],7)
        self.assertEqual(d["prior_batches_a_b_mapped_count"],19)
        self.assertEqual(d["this_batch_distinct_source_positions"],12)
        self.assertEqual(d["cumulative_source_research_mapped_count"],31)
        self.assertEqual(len(d["records"]),12)
        target={q["question_id"] for q in self.topics if q["primary_topic_id"]=="QUANT"}
        actual={r["question_id"] for r in d["records"]}
        prior={q["question_id"] for q in self.topics
               if q["primary_topic_id"] in {"NS","LIN_EQ","POLY","ALG_ID"}}
        self.assertEqual(len(target),12)
        self.assertEqual(actual,target)
        self.assertEqual(len(actual),len(d["records"]))
        self.assertEqual(len(prior),19)
        self.assertFalse(actual & prior)

    def test_each_source_exact_audit_question_page_answer(self):
        original={r["question_id"]:r for r in self.census["records"]}
        topic={r["question_id"]:r for r in self.topics}
        for row in self.doc["records"]:
            with self.subTest(row=row["question_id"]):
                sid=row["question_id"]
                self.assertEqual(row["source_id"],original[sid]["source_id"])
                self.assertEqual(row["source_url"],original[sid]["source_document_url"])
                self.assertEqual(row["printed_source_question_number"],topic[sid]["original_q"])
                self.assertEqual(row["original_owner_compilation_entry"],topic[sid]["attachment_entry"])
                self.assertEqual(row["provisional_subtopic_id"],topic[sid]["subtopic_id"])
                p=row["prior_math_audit"]["path"]
                self.assertIn(p,self.audits)
                coll,val,choice,derive=self.audits[p]
                matches=[q for q in read(p)[coll] if q["question_id"]==sid]
                self.assertEqual(len(matches),1)
                x=matches[0]
                self.assertEqual(row["source_pdf_page_index"],x["source_pdf_page_index"])
                self.assertEqual(row["prior_math_audit"]["audit_id"],x["audit_id"])
                self.assertEqual(row["prior_math_audit"]["agent_result"],x[val])
                self.assertEqual(row["prior_math_audit"]["printed_option_selected_by_agent"],x[choice])
                self.assertEqual(row["prior_math_audit"]["derivation_from_prior_audit"],x[derive])

    def test_retained_holds_conflicts_and_distinct_cruxes(self):
        d=self.doc
        for k in ("original_fullpaper_official_keys_accepted","source_core2_eligible",
                  "source_core2_admitted","source_pdf_durably_custodied",
                  "independently_accepted_academic_reviews","core1a_canonical_admitted",
                  "qrt_cells_accepted","publisher_reproduction_permissions"):
            self.assertEqual(d[k],0,k)
        self.assertEqual(d["source_discrepancy_cases_entire_programme"],10)
        self.assertEqual(d["source_discrepancy_positions_entire_programme"],11)
        source=read("TEST/imo-research/adjudication/source-discrepancy-register.v1.json")
        conflicts={q for c in source["cases"] for q in c["question_ids"]}
        self.assertFalse({r["question_id"] for r in d["records"]} & conflicts)
        self.assertEqual(len({r["capability"]["decisive_model_or_inference"]
                              for r in d["records"]}),12)
        for row in d["records"]:
            self.assertIsNone(row["source_discrepancy"])
            cap=row["capability"]
            for key in ("decisive_model_or_inference","independently_recheckable_warrant",
                        "plausible_wrong_path","domain_and_source_boundary"):
                self.assertGreater(len(cap[key]),48)
            hold=row["product_holds"]
            for key,val in hold.items():
                if key=="qrt_cell_accepted":
                    self.assertIsNone(val)
                else:
                    self.assertIs(val,False,(row["question_id"],key))

    def test_independent_small_mathematical_oracles(self):
        self.assertEqual(F(20825)*F(36,49),15300)
        joint=F(1,9)+F(1,12)
        self.assertEqual(1/joint,F(36,7))
        self.assertEqual((F(45)-F(75,100)*40)/60,F(1,4)) # high-earning female fraction
        self.assertEqual(1-F(1,4),F(3,4))
        self.assertEqual(F(150+175)/((54+36)*F(5,18)),13)
        self.assertEqual(F(12000)/(1+F(16,100)*F(5,4)),10000)
        self.assertEqual(F(6*5+5,7*5+5),F(7,8))
        self.assertEqual(7*5+1,36)
        self.assertEqual(F(10,3)**2/100,F(1,9))
        m,b=F(1,100),F(1,200)
        self.assertEqual(6*m+8*b,F(1,10))
        self.assertEqual(26*m+48*b,F(1,2))
        self.assertEqual(1/(15*m+20*b),4)
        self.assertEqual(15000*((1+F(1,10))**3-1),4965)
        self.assertEqual(12*8*10,8*15*8)
        a=16000*3+11000*9
        bcap=12000*3+17000*9
        c=21000*6
        self.assertEqual((a,bcap,c),(147000,189000,126000))
        self.assertEqual(F(bcap-c,a+bcap+c)*17600,2400)
        self.assertEqual((1+F(40,100))*(1-F(10,100)),F(126,100))

if __name__=="__main__":
    unittest.main()
