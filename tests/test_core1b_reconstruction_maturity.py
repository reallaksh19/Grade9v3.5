"""Core1B: truly attempt-first conceptual reconstruction, not a second Core1A.

Exercises the existing package schema, role-scoped manifest, QRT and sole renderer.
This TEST-only pilot has no original exam Core2 and no curriculum acceptance.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from html.parser import HTMLParser

from Shared.tools import product_manifest, product_coverage, question_review_matrix as qrt, render_core

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json"
MANIFEST = ROOT / "TEST/products/core1b-authored-reconstruction-journey.manifest.json"
M = "MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS"


def fixture():
    p = json.loads(PACKAGE.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return p, manifest, next(m for m in p["microtopics"] if m["id"] == M)


class _FigureVisibility(HTMLParser):
    """Distinguish actual learner figures from inert answer-template markup."""
    def __init__(self):
        super().__init__()
        self.template_depth = 0
        self.figures = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "template":
            self.template_depth += 1
        if tag == "figure" and "data-g9-figure" in a:
            self.figures.append({
                "stage": a.get("data-g9-stage"),
                "representation": a.get("data-g9-representation"),
                "in_template": self.template_depth > 0,
            })

    def handle_endtag(self, tag):
        if tag == "template":
            self.template_depth -= 1


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
        self.assertIn("If using a printed handout, write on a separate sheet.", e["predict"]["prompt"])
        self.assertNotIn("same response box", e["predict"]["prompt"])
        self.assertTrue(e["attempt"]["task"]["response"]["paper_ok"])
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
        self.assertEqual(len(m["misconceptions"]), 2)
        self.assertEqual(m["construction_units"][0]["misconception_indexes"], [0, 1])
        self.assertTrue(all(w["diagnostic_prompt"] and w["repair"] for w in m["misconceptions"]))
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
        # Alt/title/desc are preattempt content too: naming the proof
        # ingredients in a negative sentence is still a learner hint.
        for hint in ("even factor", "multiples of three", "remainder", "parity"):
            self.assertNotIn(hint, s.lower())
        self.assertEqual(len(rep["scene_instances"][0]["datum_refs"]), 1)


    def test_inert_postattempt_figure_is_not_a_missing_print_figure(self):
        """Static quality counts template markup; learner print intentionally doesn't."""
        html, gaps, _, advisories, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(gaps, [], gaps)
        self.assertEqual(advisories, [], advisories)
        self.assertEqual(waivers, [], waivers)
        figures = {}
        for name in ("core1a.html", "core1b.html", "core2a.html"):
            parser = _FigureVisibility()
            parser.feed(html[name])
            self.assertEqual(parser.template_depth, 0)
            figures[name] = parser.figures
        self.assertEqual(sum(map(len, figures.values())), 4)
        self.assertEqual(sum(sum(not f["in_template"] for f in fs)
                             for fs in figures.values()), 3)
        core = figures["core1b.html"]
        self.assertEqual(len(core), 2)
        self.assertEqual([f["stage"] for f in core], ["PRE_ATTEMPT", "POST_ATTEMPT"])
        self.assertEqual([f["in_template"] for f in core], [False, True])
        # The protected second instance is the SAME unmarked authored asset,
        # not a lost fourth student-visible diagram or official source figure.
        self.assertEqual(core[0]["representation"], core[1]["representation"])
        self.assertEqual(core[0]["representation"],
                         "REP-TEST-CORE1B-ENDING-AT-T-UNMARKED")

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


    def test_each_rejected_route_has_a_distinct_governed_diagnosis_and_repair(self):
        """Example-only and fixed-factor fallacies must have different falsifiers."""
        _, _, m = fixture()
        wrong = m["misconceptions"]
        rejected = m["elicitation"]["attempt"]["rejected"]
        self.assertEqual(len(rejected), len(wrong))
        self.assertEqual(len(wrong), 2)
        self.assertIn("t=3,4,5", rejected[0])
        self.assertIn("t is always divisible by 3", rejected[1])
        self.assertIn("far larger than every sample", wrong[0]["diagnostic_prompt"])
        self.assertIn("t=4", wrong[1]["diagnostic_prompt"])
        self.assertIn("t−1", wrong[1]["diagnostic_prompt"])
        self.assertIn("t−2", wrong[1]["repair"])
        self.assertNotEqual(wrong[0]["diagnostic_prompt"], wrong[1]["diagnostic_prompt"])
        self.assertNotEqual(wrong[0]["repair"], wrong[1]["repair"])
        pages, gaps, _, _, _ = render_core.build_report(MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(gaps, [], gaps)
        protected = re.search(
            r'<template data-g9-payload="[^"]+-reconstruct">(.*?)</template>',
            pages["core1b.html"], flags=re.DOTALL,
        )
        self.assertIsNotNone(protected)
        for item in wrong:
            self.assertIn(item["diagnostic_prompt"], protected.group(1))
            self.assertIn(item["repair"], protected.group(1))
        self.assertIn("t=4", protected.group(1))

    def test_governed_mod3_warrant_fails_a_swapped_case(self):
        """Read the actual authored rubric's residue witnesses, not a test-only truth."""
        _, _, m = fixture()
        criterion = m["elicitation"]["attempt"]["rubric"][2]["criterion"]
        match = re.search(
            r"respectively (t(?:−[12])?), (t(?:−[12])?), (t(?:−[12])?) divisible by 3",
            criterion,
        )
        self.assertIsNotNone(match, "Rubric must name all three residue witnesses")
        witnesses = match.groups()

        def check_mapping(cases):
            for residue, expression in enumerate(cases):
                for t in range(3 + residue, 42, 3):
                    actual = {"t": t, "t−1": t - 1, "t−2": t - 2}[expression]
                    self.assertEqual(actual % 3, 0, (residue, expression, t))

        check_mapping(witnesses)
        with self.assertRaises(AssertionError):
            check_mapping((witnesses[1], witnesses[0], witnesses[2]))
        self.assertIn("(t−1)t", m["elicitation"]["boundary_test"]["prompt"])
        self.assertEqual((2 - 1) * 2 % 6, 2)


    def test_separate_boundary_attempt_and_protected_answer(self):
        """Main commitment cannot authorize another answer; KEY mode stays deliberate."""
        p, _, m = fixture()
        self.assertIn("boundary decision and reason", m["elicitation"]["boundary_test"]["prompt"])
        html, gaps, _, advisories, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE"
        )
        self.assertEqual((gaps, advisories, waivers), ([], [], []))
        page = html["core1b.html"]
        boxes = re.findall(r'<div class="g9-attempt" data-g9-attempt-box[^>]*>', page)
        reveals = re.findall(r'<details data-g9-reveal data-requires-attempt[^>]*>', page)
        self.assertEqual(len(boxes), 2)
        self.assertEqual(len(reveals), 2)
        self.assertNotIn('data-g9-attempt-stage="boundary"', boxes[0])
        self.assertNotIn('data-g9-attempt-stage="boundary"', reveals[0])
        self.assertIn('data-g9-attempt-stage="boundary"', boxes[1])
        self.assertIn('data-g9-attempt-stage="boundary"', reveals[1])
        self.assertIn("Your boundary decision and reason", page)
        self.assertIn("I have attempted the boundary", page)
        self.assertIn("if(!attemptedFor(a,d))return", render_core.JS)
        self.assertIn("a.dataset.g9BoundaryAttempted='1'", render_core.JS)

    def test_core1b_print_layout_is_scoped_and_preserves_complete_gates(self):
        """Role-local CSS must never change CORE1A/CORE2A or remove protected answers."""
        pages, gaps, _, _, _ = render_core.build_report(MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(gaps, [])
        for role in ("core1a.html", "core1b.html", "core2a.html"):
            self.assertIn('html[data-g9-role="CORE1B"] .g9-concept-triad-bar', pages[role])
            self.assertIn('html[data-g9-role="CORE1B"] article[data-g9-role="CORE1B"] .g9-split', pages[role])
            self.assertNotIn('html[data-g9-role="CORE1A"] .g9-concept-triad-bar', pages[role])
            self.assertNotIn('html[data-g9-role="CORE2A"] .g9-concept-triad-bar', pages[role])
        b = pages["core1b.html"]
        self.assertIn('data-g9-block="boundary_test"', b)
        self.assertIn('data-g9-block="boundary_answer"', b)
        # Count DOM elements only: inline browser JS also names this selector.
        boundary_tags = re.findall(
            r'<(?:div|details)\b[^>]*data-g9-attempt-stage="boundary"', b
        )
        self.assertEqual(len(boundary_tags), 2)

if __name__ == "__main__":
    unittest.main()
