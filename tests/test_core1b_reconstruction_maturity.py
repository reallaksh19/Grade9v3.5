"""Core1B: truly attempt-first conceptual reconstruction, not a second Core1A.

Exercises the existing package schema, role-scoped manifest, QRT and sole renderer.
This TEST-only pilot has no original exam Core2 and no curriculum acceptance.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from Shared.tools import product_manifest, product_coverage, question_review_matrix as qrt, render_core

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
MANIFEST = ROOT / "TEST/products/core1b-authored-reconstruction-journey.manifest.json"
M = "MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS"


def fixture():
    p = json.loads(PACKAGE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return p, manifest, next(m for m in p["microtopics"] if m["id"] == M)


class Core1BReconstructionTests(unittest.TestCase):
    def test_same_concept_owns_both_teaching_and_reconstruction(self):
        p, manifest, m = fixture()
        self.assertEqual(manifest["output_roles"], ["CORE1A", "CORE1B", "CORE2A"])
        self.assertEqual(manifest["selection"]["microtopics"], [M])
        self.assertEqual(manifest["selection"]["core2"], [])
        self.assertEqual(manifest["selection"]["core2b"], [])
        self.assertEqual(manifest["bank_refs"], [])
        self.assertEqual(p["subject"], "TEST")
        self.assertEqual(p["status"], "CANDIDATE")
        self.assertFalse(p["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(p["extensions"]["grade9v3:learner_published"])
        self.assertEqual(p["questions"][1]["origin"], "AUTHORED")
        self.assertTrue(m["inferential_jump"])
        self.assertEqual([s["id"] for s in m["teaching_path"]],
                         ["TC-01", "TC-02", "TC-03", "TC-04"])
        self.assertEqual(set(m["elicitation"]),
                         {"predict", "attempt", "reconstruct", "boundary_test"})
        self.assertEqual(PACKAGE.parent.name, "pilots")
        self.assertFalse(PACKAGE in list(ROOT.glob("*/library/*.v1.json")))
        product_coverage.validate(manifest, product_manifest.derivable([p], []))
        selected = product_manifest.validate_selection(manifest, [p], [])
        self.assertEqual(len(selected["core2a"]), 1)

    def test_learner_owned_proof_and_closure_are_not_a_declarative_rewrite(self):
        p, manifest, m = fixture()
        e = m["elicitation"]
        self.assertIn("Do those three checks PROVE", e["predict"]["prompt"])
        self.assertTrue(e["predict"]["defensible_answer"].startswith("No."))
        self.assertIn("t−2", e["attempt"]["task"]["prompt"])
        self.assertEqual(e["attempt"]["closure"], "RUBRIC")
        self.assertEqual(len(e["attempt"]["rubric"]), 4)
        self.assertGreaterEqual(len(e["attempt"]["accepted"]), 2)
        self.assertGreaterEqual(len(e["attempt"]["rejected"]), 2)
        self.assertTrue(all(s["evidence_of"] for s in e["attempt"]["rubric"]))
        route = e["reconstruct"]["route"]
        self.assertGreaterEqual(len(route), 4)
        self.assertTrue(all("?" in s["ask"] and s["why_this_ask"] for s in route))
        self.assertEqual({s["from_step_ref"] for s in route if s.get("from_step_ref")},
                         {"TC-01", "TC-02", "TC-03", "TC-04"})
        self.assertNotIn("from_step_ref", route[-1])  # learner-led universal closure
        self.assertIn("Core1A directly models", e["reconstruct"]["differs_from_teaching_path"])
        self.assertIn("(t−1)t", e["boundary_test"]["prompt"])
        self.assertIn("t=2", e["boundary_test"]["answer"])
        self.assertIn("multiple-of-three", e["boundary_test"]["answer"])
        self.assertEqual(len(m["misconceptions"]), 1)
        self.assertTrue(m["misconceptions"][0]["diagnostic_prompt"])
        self.assertTrue(m["misconceptions"][0]["repair"])
        # The limiting case is mathematical falsification, not paraphrasing.
        self.assertEqual((2 - 1) * 2 % 6, 2)
        for t in range(3, 80):
            self.assertEqual((t - 2) * (t - 1) * t % 6, 0)

    def test_preattempt_visual_contains_no_decisive_proof(self):
        p, _, m = fixture()
        task = m["elicitation"]["attempt"]["task"]
        rep = next(x for x in p["representations"] if x["id"] == task["representation_ref"])
        self.assertEqual(rep["scene_instances"][0]["cores"], ["CORE1B"])
        self.assertEqual(rep["scene_instances"][0]["microtopic_ref"], M)
        self.assertEqual(task["stage_refs"], ["CORE1B-GIVEN-FACTORS"])
        path = ROOT / rep["rendered_asset_refs"][0]
        s = path.read_text(encoding="utf-8")
        for visible in ("t − 2", "t − 1"):
            self.assertIn(visible, s)
        # Accessibility description may say this is an unmarked figure, but
        # must never supply the mathematical case analysis or a model response.
        self.assertNotIn("t mod 3", s)
        self.assertNotIn("factor of 2 and", s)
        self.assertNotIn("coprime", s)
        self.assertNotIn("divisible by 6", s)
        self.assertEqual(len(rep["scene_instances"][0]["datum_refs"]), 1)

    def test_real_role_scoped_renderer_and_qrt_stay_intact(self):
        p, manifest, m = fixture()
        self.assertEqual(qrt.check_paths(), [])
        matrix, vocab = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
        compiled = qrt.generated_payload(matrix, vocab)
        self.assertEqual(len(compiled["templates"]), 28)
        pages, gaps, digest, advisories, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE"
        )
        self.assertEqual(set(pages), {"index.html", "core1a.html", "core1b.html", "core2a.html"})
        self.assertEqual(gaps, [], gaps)
        self.assertEqual(advisories, [], advisories)
        self.assertEqual(waivers, [], waivers)
        self.assertEqual(len(digest), 16)
        b = pages["core1b.html"]
        self.assertEqual(re.findall(r'<article[^>]*data-g9-role="([^"]+)"', b), ["CORE1B"])
        self.assertIn("Boundary test", b)
        self.assertIn("Reconstruct", b)
        # The Core1B self-tutor must show the author's entire closure after
        # commitment, not silently discard rubric evidence or rejected work.
        self.assertIn("Check your prediction", b)
        self.assertIn("No. Three checks are instances", b)
        self.assertIn("Evidence:", b)
        self.assertIn("Answers that do not yet satisfy the criteria", b)
        self.assertIn("I tested t=3,4,5", b)
        self.assertIn("The factor t is always divisible by 3", b)
        self.assertIn("CORE1B-GIVEN-FACTORS", b)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', b)
        self.assertNotIn("SOF-IMO-G09-L1", b)
        self.assertEqual(set(pages), set(render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE"
        )[0]))


if __name__ == "__main__":
    unittest.main()
