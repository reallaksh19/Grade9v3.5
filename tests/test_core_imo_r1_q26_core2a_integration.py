"""IMO-R1: one authored common-base Core2A connects to the existing Q26 Core1A."""
from __future__ import annotations
import copy
import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from Shared.tools import product_manifest, product_coverage, question_review_matrix as qrt, render_core, question_difficulty

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/"TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT/"TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
QUESTION_ID = "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01"
CAPABILITY = "CAP-TEST-IMO-G9-COMMON-EXPONENTIAL-QUANTITY"

def inputs():
    d=json.loads(PACKAGE.read_text(encoding="utf-8"))
    m=json.loads(MANIFEST.read_text(encoding="utf-8"))
    q=next(row for row in d["questions"] if row["id"]==QUESTION_ID)
    return d,m,q

class IMOOneAuthoredQRTRepair(unittest.TestCase):
    def test_authored_schema_ownership_manifest_and_repair(self):
        d,m,q=inputs()
        schema=json.loads((ROOT/"Shared/library/package.schema.json").read_text(encoding="utf-8"))
        errors=list(Draft202012Validator(schema).iter_errors(d))
        self.assertFalse(errors,[str(e) for e in errors[:6]])
        self.assertEqual(d["status"],"CANDIDATE")
        self.assertEqual(d["subject"],"TEST")
        self.assertEqual(q["origin"],"AUTHORED")
        self.assertEqual(q["exposure"],[{"core":"CORE2A","role":"SUPPORTED_PRACTICE","artifact_ref":None}])
        self.assertEqual(q["primary_capability_ref"],CAPABILITY)
        self.assertEqual(len([x for x in d["questions"] if any(e["core"]=="CORE2A" for e in x.get("exposure",[]))]),1)
        self.assertEqual(q["repair_ref"],"TC-02")
        self.assertIn(q["repair_ref"],[s["id"] for s in d["microtopics"][0]["teaching_path"]])
        self.assertEqual(m["output_roles"],["CORE1A","CORE2A"])
        self.assertEqual(m["selection"]["core2"],[])
        self.assertEqual(m["selection"]["core2b"],[])
        self.assertEqual(m["selection"]["core2a"],[QUESTION_ID])
        self.assertEqual(m["bank_refs"],[])
        selected=product_manifest.validate_selection(m,[d],[])
        self.assertEqual([row["id"] for row in selected["core2a"]],[QUESTION_ID])
        product_coverage.validate(m,product_manifest.derivable([d],[]))
        self.assertEqual(len(q["answer"]["reasoning_route"]),5)
        self.assertEqual(q["answer"]["crux_move_ref"],"MOVE-IMO-R1-FACTOR")
        self.assertTrue(all(s["why_valid"] for s in q["answer"]["reasoning_route"]))
        self.assertEqual(len(q["hint_ladder"]),3)
        self.assertEqual(q["representation_roles"]["initial_ref"],"REP-TEST-IMO-G9-R1-CORE2A-ATTEMPT-SAFE")
        self.assertEqual(q["figure_refs"],["REP-TEST-IMO-G9-R1-CORE2A-ATTEMPT-SAFE"])
        self.assertNotIn("transfer",q)
        self.assertEqual(d["extensions"]["grade9v3:qrt_admitted"],False)
        self.assertEqual(d["extensions"]["grade9v3:core2_source_custody_granted"],False)
        self.assertEqual(d["extensions"]["grade9v3:learner_published"],False)
        self.assertNotIn("SOF-IMO-G09",q["stem"])
        self.assertNotIn("SOF-IMO-G09",q["answer"]["summary"])

    def test_independent_math_including_domain_and_inverse(self):
        d,m,q=inputs()
        u=3/2
        lhs=4**(2*u+1)
        rhs=16**u+192
        self.assertEqual((lhs,rhs),(256,256))
        self.assertEqual(4**(2*u),64)
        self.assertEqual(4*64,64+192)
        self.assertEqual(64,4**3)
        self.assertEqual(u,1.5)
        self.assertGreater(4**(2*u),0)
        self.assertEqual(q["answer"]["summary"],"The unique real solution is u=3/2.")

    def test_qrt_existing_model_d3_derives_score_and_12_jobs(self):
        d,m,q=inputs()
        self.assertEqual(qrt.check_paths(),[])
        self.assertEqual(question_difficulty.derive(q["difficulty"])["band"],"D3")
        self.assertEqual(q["difficulty"]["score"],7)
        profile={"profile_id":"SYNTHETIC-UNKNOWN-IMO-R1","provenance":"SYNTHETIC_TEST_ONLY","held":{CAPABILITY:"UNCERTAIN"},"knowledge_percentage":95,"measured_fit_claim":False}
        matrix,vocab=qrt.load(qrt.MATRIX_PATH),qrt.load(qrt.VOCAB_PATH)
        out=qrt.resolve_review(q,profile,matrix,vocab)
        self.assertEqual(out["template_id"],"QRT-MODEL-D3")
        self.assertEqual(out["classification"]["difficulty_score"],7)
        self.assertEqual(out["classification"]["demand"]["primary_move_ref"],"MOVE-IMO-R1-FACTOR")
        self.assertEqual(tuple(out["review"]),qrt.ASKS)
        self.assertEqual(set(out["slots"]),{"X","Y","Z","W","wrong_idea","replacement_rule","visual_job","check_job"})
        self.assertIn("UNCERTAIN",out["slots"]["X"]["text"])
        profile["knowledge_percentage"]=10
        other=qrt.resolve_review(q,profile,matrix,vocab)
        self.assertEqual(out["template_id"],other["template_id"])
        self.assertEqual(out["slots"],other["slots"])
        invalid=copy.deepcopy(q)
        invalid["difficulty"]["band"]="D4"
        with self.assertRaisesRegex(qrt.QRTContractError,"QUESTION_DIFFICULTY_BAND_MISMATCH"):
            qrt.resolve_review(invalid,profile,matrix,vocab)
        invalid=copy.deepcopy(q)
        invalid["answer"]["crux_move_ref"]="MADE_UP"
        with self.assertRaisesRegex(qrt.QRTContractError,"COGNITIVE_DEMAND_CRUX_MOVE_UNRESOLVED"):
            qrt.resolve_review(invalid,profile,matrix,vocab)

    def test_false_source_core2_authority_rejected(self):
        d,m,q=inputs()
        wrong=copy.deepcopy(m)
        wrong["selection"]["core2"]=[QUESTION_ID]
        wrong["selection"]["core2a"]=[]
        with self.assertRaisesRegex(product_manifest.ProductSelectionError,"PRODUCT_SELECTION_WRONG_AUTHORITY"):
            product_manifest.validate_selection(wrong,[d],[])

    def test_true_renderer_produces_only_role_scoped_pages(self):
        d,m,q=inputs()
        pages,gaps,_,advice,waivers=render_core.build_report(MANIFEST,"PAGES",held_to="REFERENCE")
        self.assertEqual(set(pages),{"index.html","core1a.html","core2a.html"})
        self.assertEqual(gaps,[],gaps)
        self.assertEqual(advice,[],advice)
        self.assertEqual(waivers,[],waivers)
        a,b=pages["core1a.html"],pages["core2a.html"]
        self.assertIn("Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01",b)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"',b)
        self.assertIn('data-g9-repair-ref="TC-02"',b)
        self.assertIn("core1a.html#CU-TEST-IMO-G9-EXPONENTIAL-RELATION",b)
        self.assertIn('data-g9-role="CORE2A"',b)
        self.assertIn('data-g9-role="CORE1A"',a)
        self.assertEqual(re.findall(r'<article\b[^>]*data-g9-role="([^"]+)"',b),["CORE2A"])
        self.assertNotIn("SOF-IMO-G09",a+b)

if __name__=="__main__":
    unittest.main()
