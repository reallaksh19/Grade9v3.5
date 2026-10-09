"""Batch B source-specific algebra crosswalk: maths witnesses and non-admissions."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IMO=ROOT/"TEST"/"imo-research"
CROSS=IMO/"batches"/"batch-b-algebra-source-capabilities.v1.json"

def read(rel):
    return json.loads((ROOT/rel).read_text(encoding="utf-8"))

class BatchBAlgebraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads(CROSS.read_text(encoding="utf-8"))
        cls.census=read("TEST/imo-research/intake/core2-source-custody-eligibility.v1.json")
        cls.topics=[json.loads(s) for s in (IMO/"taxonomy"/"seed-question-topic-map.v1.jsonl")
                    .read_text(encoding="utf-8").splitlines() if s.strip()]
        cls.audits={
            "TEST/imo-research/seed/math_audit_batch01.json":"questions",
            "TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json":"observations",
            "TEST/imo-research/verification/fullpaper-audit-b03.v1.json":"records",
            "TEST/imo-research/verification/fullpaper-audit-b04.v1.json":"records",
            "TEST/imo-research/verification/official-sample-2026-27-math-qrt-pilot.v1.json":"records"
        }
        cls.expected_result_field={
            "TEST/imo-research/seed/math_audit_batch01.json":("computed_answer","math_derived_printed_choice"),
            "TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json":("independent_agent_answer","printed_correct_choice_by_agent"),
            "TEST/imo-research/verification/fullpaper-audit-b03.v1.json":("computed_result","mathematically_selected_printed_option"),
            "TEST/imo-research/verification/fullpaper-audit-b04.v1.json":("independent_agent_result","printed_choice_selected_by_math"),
            "TEST/imo-research/verification/official-sample-2026-27-math-qrt-pilot.v1.json":("answer_meaning","agent_derived_option")
        }

    def test_inventory_exact_11_and_strict_68_denominator(self):
        d=self.doc
        self.assertEqual(len(self.census["records"]),68)
        self.assertEqual(d["programme_total_authentic_source_positions"],68)
        self.assertEqual(d["this_batch_distinct_source_positions"],11)
        self.assertEqual(d["source_positions_mapped_across_batches_a_b"],19)
        self.assertEqual(d["programme_separate_authored_practice"],7)
        self.assertEqual(len(d["records"]),11)
        declared={q["question_id"] for q in self.topics
                  if q["primary_topic_id"] in {"LIN_EQ","POLY","ALG_ID"}}
        actual={q["question_id"] for q in d["records"]}
        self.assertEqual(len(declared),11)
        self.assertEqual(actual,declared)
        self.assertEqual(len(actual),len(d["records"]))
        self.assertEqual({key:sum(r["provisional_topic_id"]==key for r in d["records"])
                          for key in ("LIN_EQ","POLY","ALG_ID")},
                         {"LIN_EQ":7,"POLY":3,"ALG_ID":1})

    def test_all_previous_audits_and_page_references_match(self):
        census={q["question_id"]:q for q in self.census["records"]}
        topics={q["question_id"]:q for q in self.topics}
        for row in self.doc["records"]:
            with self.subTest(row=row["question_id"]):
                original=census[row["question_id"]]
                meta=topics[row["question_id"]]
                self.assertEqual(row["source_id"],original["source_id"])
                self.assertEqual(row["source_url"],original["source_document_url"])
                self.assertEqual(row["source_printed_question_number"],meta["original_q"])
                self.assertEqual(row["owner_attachment_entry"],meta["attachment_entry"])
                self.assertEqual(row["provisional_subtopic_id"],meta["subtopic_id"])
                path=row["research_math_evidence"]["file"]
                self.assertIn(path,self.audits)
                audit=[x for x in read(path)[self.audits[path]]
                       if x["question_id"]==row["question_id"]]
                self.assertEqual(len(audit),1)
                item=audit[0]
                result_field,choice_field=self.expected_result_field[path]
                self.assertEqual(row["research_math_evidence"]["agent_computed_result"],
                                 item[result_field])
                self.assertEqual(row["research_math_evidence"]["agent_selected_printed_option"],
                                 item[choice_field])
                self.assertEqual(row["source_pdf_page_index"],
                                 item["source_pdf_page_index"])

    def test_discrepancy_005_is_not_lost_or_invented(self):
        conflicts=read("TEST/imo-research/adjudication/source-discrepancy-register.v1.json")
        byid={qid:case["case_id"] for case in conflicts["cases"] for qid in case["question_ids"]}
        actual=[]
        for row in self.doc["records"]:
            case=row["source_discrepancy"]
            self.assertEqual(case["case_id"] if case else None,
                             byid.get(row["question_id"]))
            if case: actual.append(case["case_id"])
        self.assertEqual(actual,["IMO-SOURCE-CONFLICT-005"])
        self.assertEqual(self.doc["known_conflict_cases_entire_programme"],10)
        self.assertEqual(self.doc["known_conflict_affected_positions_entire_programme"],11)

    def test_capability_is_source_specific_but_not_admitted(self):
        d=self.doc
        for key in ("source_key_acceptances","source_custody_eligible_core2",
                    "source_core2_admitted","canonical_core1a_admitted",
                    "qrt_cells_accepted","rights_granted"):
            self.assertEqual(d[key],0)
        for row in d["records"]:
            c=row["source_capability_proposal"]
            h=row["provenance_and_product_hold"]
            for term in ("decisive_inference","mathematical_warrant",
                         "likely_wrong_path","limits_and_domain"):
                self.assertGreater(len(c[term]),30)
            self.assertFalse(c["canonical_core1a_mapping_accepted"])
            for key in ("retained_publisher_pdf_bytes",
                        "source_component_custody_verified",
                        "source_rights_reproduction_granted",
                        "official_fullpaper_answer_key_accepted",
                        "independent_external_peer_signature",
                        "eligible_source_core2","rendered_source_core2",
                        "academic_owner_approved"):
                self.assertIs(h[key],False)
            self.assertIsNone(h["qrt_accepted_cell"])
            self.assertTrue(h["external_reference_only"])
        self.assertEqual(len({r["source_capability_proposal"]["decisive_inference"]
                              for r in d["records"]}),11)

    def test_bounded_independent_math_reversals(self):
        def q028_delta(x,y):
            return 2*x**3-5*y**4-2*x**4-15*x**2*y**2
        def q028_from(x,y):
            return 3*x**4+7*x**2*y**2+2*y**4
        def q028_to(x,y):
            return 2*x**3-3*y**4+x**4-8*x**2*y**2
        for x,y in ((0,1),(2,-1),(3,2)):
            self.assertEqual(q028_from(x,y)+q028_delta(x,y),q028_to(x,y))
        for x in (4,5,7):
            self.assertEqual(x*(x-3)*(x+4),x**3+x*x-12*x)
        self.assertEqual(4**3-4,60)  # factor theorem sample Q7
        self.assertEqual(1+2*F(-1,2)+0,0)
        self.assertEqual(-1-2*F(-1,2)+0,0)
        self.assertEqual((2*3**2+4)**2,484)
        self.assertEqual((2*2**2+4)**2-(2*2**3-11*2**2-4*2+5),
                         4*2**4-2*2**3+27*2**2+4*2+11)
        self.assertEqual(-25*2+750,700)
        self.assertEqual(9*3+12*3,63)
        self.assertEqual(5+2*5,3*5)
        self.assertEqual(15-6*2,2*2-1)
        self.assertEqual(15+(1-2*2)*6,3*(-1))
        self.assertEqual(2*(-1)-1,-3)
        self.assertEqual(2*2-1,3)
        self.assertEqual(46+14,60)
        self.assertEqual(40,5*8)
        for x,y in ((0,0),(3,2),(7,5)):
            original=F(28,5)*x-F(4,5)*y
            normalized=28*x-4*y
            self.assertEqual(5*original,normalized)
        self.assertEqual(5*800-3*800,1600)
        self.assertEqual(4*800-2*800,1600)


if __name__=="__main__":
    unittest.main()
