"""Research-only Q26-like authored Core1A package: source safety, mathematics, renderer."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
PKG_PATH=ROOT/"TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST=ROOT/"TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.test.manifest.json"

class Q26CommonBaseCore1ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads(PKG_PATH.read_text(encoding="utf-8"))
        cls.m=json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_schema_and_canonical_reference_graph(self):
        from jsonschema import Draft202012Validator
        from Shared.library.resolve import validate_library
        schema=json.loads((ROOT/"Shared/library/package.schema.json").read_text(encoding="utf-8"))
        problems=list(Draft202012Validator(schema).iter_errors(self.d))
        self.assertEqual(problems,[],[e.message for e in problems])
        graph=validate_library([self.d])
        self.assertEqual(graph["unresolved_references"],0)

    def test_authored_material_never_reclassified_as_source_core2(self):
        d=self.d
        self.assertEqual(d["status"],"CANDIDATE")
        self.assertEqual(d["subject"],"TEST")
        self.assertEqual(len(d["resources"]),1)
        self.assertEqual(d["resources"][0]["origin"],"AUTHORED")
        self.assertEqual(d["resources"][0]["role"],["AUTHOR_CREATED"])
        self.assertEqual(d["resources"][0]["source_refs"],[])
        self.assertIsNone(d["resources"][0]["snapshot_digest"])
        self.assertIsNone(d["resources"][0]["snapshot_ref"])
        self.assertEqual(d["questions"],[])
        self.assertEqual(d["curriculum_mappings"],[])
        self.assertEqual(d["capabilities"][0]["acceptance_status"],"CANDIDATE")
        self.assertEqual(d["extensions"]["grade9v3:qrt_admitted"],False)
        self.assertEqual(d["extensions"]["grade9v3:core2_source_custody_granted"],False)
        self.assertEqual(d["extensions"]["grade9v3:learner_published"],False)
        serialized=json.dumps(d,ensure_ascii=False)
        for unsafe in ("SOF-IMO-G09","©SOF",'"origin": "SOF"', "https://sofworld.org/download/"):
            self.assertNotIn(unsafe,serialized)
        rep=d["representations"][0]
        self.assertEqual(len(rep["rendered_asset_refs"]),1)
        asset=ROOT/rep["rendered_asset_refs"][0]
        self.assertTrue(asset.is_file())
        svg=asset.read_text(encoding="utf-8")
        self.assertIn("<title>",svg)
        self.assertIn("<desc>",svg)
        self.assertIn('aria-label=',svg)
        self.assertEqual([s["id"] for s in rep["reveal_stages"]],
                         ["Q26-BASE","Q26-FACTOR","Q26-SOLVE"])
        for item in rep["reveal_stages"]:
            self.assertIn('data-g9-stage-id="'+item["id"]+'"',svg)
        self.assertNotIn("SOF-IMO-G09",svg)

    def test_exact_subject_scoped_manifest(self):
        from Shared.tools import product_manifest
        m=self.m
        self.assertEqual(m["schema"],"product-manifest/v1")
        self.assertEqual(m["subject"],"TEST")
        self.assertEqual(m["output_roles"],["CORE1A"])
        self.assertEqual(product_manifest.selected_output_roles(m),["CORE1A"])
        self.assertEqual(m["package_refs"],[PKG_PATH.relative_to(ROOT).as_posix()])
        self.assertEqual(m["bank_refs"],[])
        self.assertEqual(m["selection"]["microtopics"],[self.d["microtopics"][0]["id"]])
        for key in ("core2","core2a","core2b"):
            self.assertEqual(m["selection"][key],[])
        match=product_manifest.validate_selection(m,[self.d],[])
        self.assertEqual(len(match["microtopics"]),1)
        self.assertEqual(len(match["core2"]),0)

    def test_nontrivial_complete_construction_and_fresh_exit(self):
        m=self.d["microtopics"][0]
        steps=m["teaching_path"]
        self.assertEqual([s["id"] for s in steps],
                         ["TC-01","TC-02","TC-03","TC-04","TC-05"])
        self.assertEqual(m["construction_units"][0]["step_refs"],[s["id"] for s in steps])
        self.assertEqual(m["construction_units"][0]["misconception_indexes"],[0,1])
        for step in steps:
            self.assertGreater(len(step["action"]),50)
            self.assertGreater(len(step["why_valid"]),60)
        self.assertGreaterEqual(len(m["entry_assumptions"]),4)
        self.assertTrue(all(x["wrong_idea"] and x["repair"] and x["diagnostic_prompt"]
                            for x in m["misconceptions"]))
        self.assertIn("t>0",json.dumps(steps))
        self.assertNotEqual(m["exit_task"]["prompt"],"3^(2x+1)=9^x+162")
        answer=m["exit_task"]["answer"]
        self.assertEqual(len(answer["reasoning"]),4)
        self.assertEqual(answer["verification_status"],"CHECKED_BY_AUTHOR")

    def test_algebraic_warrants_and_domain(self):
        self.assertEqual(3**(2*2+1),9**2+162)
        self.assertEqual(2**(2*3+1),4**3+64)
        self.assertEqual(3*(3**4),3**4+162)
        self.assertEqual(2*(4**3),4**3+64)
        for x in [-3,-2,-1,0,1,2,3]:
            t=3**(2*x)
            self.assertGreater(t,0)
            self.assertAlmostEqual(3**(2*x+1),3*t,places=10)
            self.assertAlmostEqual(9**x,t,places=10)
        # A negative t from 2t=t-5 cannot equal 4**y for any real y.
        self.assertLess(-5,0)
        self.assertEqual(2*(-5),(-5)-5)

    def test_actual_renderer_projection_in_memory(self):
        from Shared.tools import render_core
        pages,gaps,digest,advisories,waived=render_core.build_report(
            MANIFEST,mode="PAGES",held_to="FLOOR"
        )
        self.assertEqual(set(pages),{"core1a.html","index.html"})
        self.assertEqual(len(digest),16)
        html=pages["core1a.html"]
        for phrase in ("3^(2x+1)=9^x+162","2^(2y+1)=4^y+64",
                       "shared positive quantity","Why valid","Model answer"):
            self.assertIn(phrase,html)
        self.assertNotIn("SOF-IMO-G09",html)
        self.assertNotIn("Original paper question",html)
        self.assertEqual(html.count('data-g9-stage-id="Q26-'),3)
        self.assertIn("data-g9-figure",html)
        self.assertEqual([], [g for g in gaps if g["duty"]=="PRODUCT_SELECTION_UNRESOLVED"])
        # A legitimate gap/advisory is not an academic rejection or a green grade.
        self.assertIsInstance(gaps,list)
        self.assertIsInstance(advisories,list)

if __name__=="__main__":
    unittest.main()
