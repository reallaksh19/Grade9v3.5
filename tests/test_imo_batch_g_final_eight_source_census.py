"""Batch G research: final eight source positions, source rights holds and real math oracles."""
from __future__ import annotations

import itertools
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "TEST/imo-research/batches/batch-g-final-circle-logic-68-source-census.v1.json"
CENSUS = ROOT / "TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
TAXONOMY = ROOT / "TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl"
DISPUTES = ROOT / "TEST/imo-research/adjudication/source-discrepancy-register.v1.json"
SAMPLE = ROOT / "TEST/imo-research/verification/official-sample-2026-27-math-qrt-pilot.v1.json"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

class BatchGResearchOnlyEightPositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=load(REPORT)
        cls.rows=cls.report["records"]
        cls.by_id={r["question_id"]:r for r in cls.rows}
        cls.census={r["question_id"]:r for r in load(CENSUS)["records"]}
        cls.tax={json.loads(line)["question_id"]:json.loads(line) for line in TAXONOMY.read_text(encoding="utf-8").splitlines() if line.strip()}

    def test_exact_68_census_partition_across_six_unmerged_drafts_and_G(self):
        r=self.report
        self.assertEqual((len(self.census),len(self.tax)),(68,66))
        self.assertEqual((len(self.rows),len(self.by_id)),(8,8))
        self.assertEqual((r["prior_batched_unique_source_positions"],r["batch_g_source_positions"],r["programme_distinct_positions_research_mapped"],r["remaining_unmapped_original_identities"]),(60,8,68,0))
        self.assertEqual(r["G_topics"],{"CIRCLES":2,"LOGIC":6})
        prior=r["cross_batch_original_identity_check"]["prior_batches"]
        self.assertEqual([p["batch"] for p in prior],list("ABCDEF"))
        self.assertEqual([p["position_count"] for p in prior],[8,11,12,11,8,10])
        before=[q for p in prior for q in p["question_ids"]]
        self.assertEqual(len(before),60)
        self.assertEqual(len(set(before)),60)
        self.assertFalse(set(before)&set(self.by_id))
        self.assertEqual(set(before)|set(self.by_id),set(self.census))
        self.assertEqual(r["legacy_authored_practice_separate_count"],7)
        self.assertEqual(r["new_r1_authored_practice_separate_count"],1)
        self.assertTrue(all(v==0 for v in r["admissions_and_rights"].values()))

    def test_census_identity_null_taxonomy_and_source_component_holds(self):
        r=self.report
        expected={"SOF-IMO-G09-SAMPLE-2026-27-Q001","SOF-IMO-G09-SAMPLE-2026-27-Q003"}
        self.assertEqual(set(r["new_sample_census_only_ids"]),expected)
        self.assertEqual(set(self.census)-set(self.tax),expected)
        for row in self.rows:
            id=row["question_id"]
            c=self.census[id]
            self.assertEqual(row["source_id"],c["source_id"])
            self.assertEqual(row["source_document_url"],c["source_document_url"])
            self.assertEqual(row["original_position_claim"],c["original_printed_position_claim"])
            self.assertEqual(row["provisional_topic_from_68_census"],c["provisional_topic_id"])
            loc=row["source_custody"]
            self.assertEqual(loc["observed_number"],c["original_printed_position_observed"])
            self.assertEqual(loc["census_pdf_page"],c["source_locator_pdf_page_index"])
            self.assertEqual(loc["publisher_pdf_sha256_custodied"],c["document_retained_sha256"])
            self.assertTrue(loc["prior_agent_viewer_sighting_is_not_verified_source_pdf_custody"])
            self.assertEqual(row["older_66_topic_mapping"]["present"],id in self.tax)
            self.assertFalse(row["older_66_topic_mapping"]["authorized_taxonomy_change"])
            self.assertTrue(all(v is False for v in row["authority_holds"].values()))
            self.assertFalse(row["source_figure"]["original_figure_stored"])
            self.assertFalse(row["source_figure"]["publisher_figure_rights_granted"])
            self.assertFalse(row["source_figure"]["original_seven_components_verified"])
            self.assertIsNone(row["capability_proposal"]["qrt_accepted_cell"])
            self.assertFalse(row["capability_proposal"]["canonical_core1a_accepted"])
            self.assertNotIn("original_publisher_stem",row)
            self.assertNotIn("original_publisher_figure",row)
            if id in expected:
                self.assertIsNone(row["older_66_topic_mapping"]["original_subtopic"])
                self.assertIsNone(row["math_research"]["prior_audit_file"])
                self.assertIsNone(row["math_research"]["prior_agent_option"])
                self.assertEqual(row["math_research"]["basis"],"NEW_AGENT_INDEPENDENT_VISUAL_CALCULATION_2026_10_09")
                self.assertEqual(row["math_research"]["organizer_sample_key_sighted"],"B")

    def test_all_prior_agent_math_joined_to_exact_existing_audit(self):
        for row in self.rows:
            id=row["question_id"]
            if id in self.report["new_sample_census_only_ids"]:
                continue
            m=row["math_research"]
            path=ROOT/m["prior_audit_file"]
            report=load(path)
            matches=[x for seq in report.values() if isinstance(seq,list) for x in seq if isinstance(x,dict) and x.get("question_id")==id]
            self.assertEqual(len(matches),1,id)
            first=matches[0]
            if first.get("audit_id"):
                self.assertEqual(m["prior_audit_id"],first["audit_id"])
            self.assertEqual(row["source_custody"]["prior_agent_viewer_pdf_page"],first["source_pdf_page_index"])
            self.assertIsNotNone(m["prior_math_derivation"])
            self.assertIsNotNone(m["prior_computed_result"])
            self.assertIsNotNone(m["prior_agent_option"])
            self.assertFalse(m["external_academic_signoff"])
            self.assertFalse(m["official_fullpaper_key_accepted"])

    def test_historic_predecessor_conflict_001_unmodified(self):
        id="SOF-IMO-G09-L1-2023-24-A-Q013"
        row=self.by_id[id]
        conflict=next(x for x in load(DISPUTES)["cases"] if x["case_id"]=="IMO-SOURCE-CONFLICT-001")
        shown=row["source_conflict"]
        self.assertEqual(shown["case_id"],conflict["case_id"])
        self.assertEqual(shown["type"],"ANSWER_CALCULATION_DISAGREEMENT")
        self.assertEqual(shown["register_original_summary"],conflict["printed_source_evidence_summary"])
        self.assertEqual(shown["register_owner_summary"],conflict["owner_compilation_claim_summary"])
        self.assertFalse(shown["dispute_cleared"])
        transformed=[int(d)-1 for d in "5736928"]
        self.assertEqual(transformed,[4,6,2,5,8,1,7])
        self.assertEqual(sorted(transformed),[1,2,4,5,6,7,8])
        self.assertEqual(sorted(transformed)[3],5)
        self.assertNotEqual(sorted(transformed)[3],4)
        self.assertEqual(row["math_research"]["prior_agent_option"],"B")
        self.assertIn("Fourth digit = 4",shown["register_owner_summary"])

    def test_cube_q1_rotation_oracle_enumerates_only_legal_cube_rotations(self):
        normals={"U":(0,0,1),"D":(0,0,-1),"F":(0,-1,0),"B":(0,1,0),"R":(1,0,0),"L":(-1,0,0)}
        def dot(a,b):
            return sum(x*y for x,y in zip(a,b))
        def cross(a,b):
            return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
        def face_of(v):
            return next(k for k,x in normals.items() if x==v)
        orientations=[]
        for u,f in itertools.product(normals,repeat=2):
            if dot(normals[u],normals[f])==0:
                orientations.append((u,f,face_of(cross(normals[u],normals[f]))))
        self.assertEqual(len(orientations),24)
        solutions=[]
        for d,b,l in itertools.permutations([1,3,6]):
            faces={"U":2,"F":4,"R":5,"D":d,"B":b,"L":l}
            third=[o for o in orientations if tuple(faces[k] for k in o)==(5,6,1)]
            if not third:
                continue
            for mid in orientations:
                if faces[mid[0]]==6 and faces[mid[2]]==3:
                    solutions.append((faces[mid[1]],(d,b,l),mid))
        self.assertEqual(len(solutions),1,solutions)
        self.assertEqual(solutions[0][0],4)
        new=self.by_id["SOF-IMO-G09-SAMPLE-2026-27-Q001"]["math_research"]
        self.assertEqual((new["new_agent_answer"],new["new_agent_derived_option"],new["organizer_sample_key_sighted"]),("4","B","B"))
        self.assertEqual(self.report["new_agent_source_visual_math_oracles"]["valid_arrangements"],1)

    def test_missing_ring_q3_square_average_oracle(self):
        pairs=[(14,8,121),(6,12,81),(3,13,64),(5,9,49)]
        for a,b,inside in pairs:
            self.assertEqual(((a+b)//2)**2,inside)
            self.assertEqual((a+b)%2,0)
        q3=self.by_id["SOF-IMO-G09-SAMPLE-2026-27-Q003"]
        self.assertEqual((q3["math_research"]["new_agent_answer"],q3["math_research"]["new_agent_derived_option"],q3["math_research"]["organizer_sample_key_sighted"]),("49","B","B"))
        self.assertTrue(q3["source_figure"]["required_for_source_integrity"])

    def test_prior_circle_proofs_and_numeric_pattern_oracles(self):
        q47=self.by_id["SOF-IMO-G09-L1-2023-24-A-Q047"]
        self.assertEqual(q47["math_research"]["prior_agent_option"],"C")
        self.assertEqual(360-360//2,180)
        self.assertEqual((180-140,90,180-(180-140)-90),(40,90,50))
        q50=self.by_id["SOF-IMO-G09-L1-2025-26-A-Q050"]
        self.assertEqual(3*3+4*4,25)
        self.assertEqual(25-4*4,9)
        self.assertTrue(q50["source_figure"]["required_for_source_integrity"])
        self.assertIn("FIGURE-DEPENDENT",q50["capability_proposal"]["source_limit_and_provenance_boundary"])
        self.assertEqual(q50["math_research"]["prior_agent_option"],"A")
        values=[(12,148),(15,229),(14,200),(13,167)]
        offsets=[b-a*a for a,b in values]
        self.assertEqual(offsets,[4,4,4,-2])
        self.assertEqual(self.by_id["SOF-IMO-G09-L1-2023-24-A-Q003"]["math_research"]["prior_agent_option"],"D")

    def test_no_silent_clearance_of_prior_batch_f_unsolved_q5(self):
        q5=next(x for x in load(SAMPLE)["records"] if x["question_id"]=="SOF-IMO-G09-SAMPLE-2026-27-Q005")
        self.assertIsNone(q5["agent_derived_option"])
        self.assertIsNone(q5["answer_meaning"])
        self.assertIsNone(q5["source_mathematical_derivation"])
        self.assertEqual(q5["organizer_printed_key"],"C")
        held=self.report["mathematically_unsolved_earlier_position"]
        self.assertEqual(held["id"],q5["question_id"])
        self.assertEqual(held["source_dispute"],"IMO-SOURCE-CONFLICT-009")
        self.assertIsNone(held["independent_agent_solution"])
        self.assertEqual(self.report["census_source_id_count"],68)
        self.assertFalse(held.get("independent_agent_math_solution_accepted",False))

if __name__=="__main__":
    unittest.main()
