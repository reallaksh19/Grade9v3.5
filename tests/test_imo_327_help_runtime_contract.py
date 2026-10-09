"""Scoped #327 TEST renderer regression: the concept-first gate and *optional* Core2A hints.

This proves emitted HTML/JS structure only; actual Chromium exercise is
tools/site-audit/imo-r1-authored-qrt-core2a-audit.mjs. A client-side formative
keyword/radio check is never academic admission or mastery evidence.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from Shared.tools import render_core

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"


class ConceptFirstRendererContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.pages, cls.gaps, _, cls.advisories, cls.waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")

    def test_renderer_retains_existing_declared_role_projection(self):
        self.assertEqual(set(self.pages), {"index.html", "core1a.html", "core2a.html"})
        self.assertEqual(self.gaps, [], self.gaps)
        self.assertEqual(self.advisories, [])
        self.assertEqual(self.waivers, [])
        self.assertNotIn('data-g9-role="CORE2"', self.pages["core2a.html"])

    def test_fixtured_core1a_gate_precedes_all_guided_content(self):
        html = self.pages["core1a.html"]
        spec = self.package["microtopics"][0]["extensions"]["grade9v3:concept_checkpoint"]
        self.assertEqual(spec["scope"], "TEST_AUTHORED_CORE1A_ONLY")
        self.assertEqual(spec["correct_value"], "FACTOR")
        self.assertIn('data-g9-concept-check', html)
        self.assertIn('data-g9-concept-correct="FACTOR"', html)
        self.assertIn('data-g9-concept-option value="FACTOR"', html)
        self.assertIn('data-g9-concept-option value="ADD"', html)
        self.assertIn('data-g9-concept-reason', html)
        self.assertIn('data-g9-concept-feedback role="status" aria-live="polite"', html)
        self.assertIn('data-g9-concept-target hidden', html)
        self.assertLess(html.index('data-g9-concept-check'), html.index('data-g9-concept-target hidden'))
        self.assertIn('Formative teaching self-check only', html)
        # Worked construction, its solutions and fresh exit are behind the
        # concept gate. A print-only override may materialise them on paper.
        self.assertRegex(html, r'data-g9-concept-target hidden>.*data-g9-block="worked_anchor"')
        self.assertIn("a.dataset.g9ConceptCheckCompleted='formative_only'", html)
        self.assertIn("reason.length<15", html)
        self.assertIn("choice!==c.dataset.g9ConceptCorrect", html)
        self.assertIn("q('[data-g9-concept-target]',article).forEach(el=>{el.hidden=false})", html)
        self.assertNotIn('data-g9-concept-check', self.pages["core2a.html"])

    def test_core2a_no_hint_is_pre_revealed_and_first_click_marks_assisted(self):
        html = self.pages["core2a.html"]
        self.assertIn('data-g9-next-rung>Show hint 1', html)
        self.assertIn('data-g9-rung-payload="CORE2A-', html)
        self.assertIn('data-g9-rung-payload="CORE2A-', html)
        self.assertIn('<ol data-g9-ladder></ol>', html)
        # Hint 1 still exists inside an inert <template> for explicit reveal;
        # its DOM text must not appear in the initially visible ladder.
        self.assertIn('data-g9-assistance-status role="status" aria-live="polite" hidden', html)
        self.assertIn('Hints viewed: assisted practice, not independent mastery.', html)
        self.assertIn("['CORE2','CORE2A'].includes(a.dataset.g9Role)", html)
        self.assertIn("markAssistance(a,'HINT_LADDER');nextRung", html)
        self.assertIn("if(state.assisted){a.dataset.g9Assisted='1'", html)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', html)
        self.assertIn('data-g9-repair-ref="TC-02"', html)

    def test_no_server_attestation_from_client_format_check(self):
        html = self.pages["core1a.html"]
        self.assertIn("A keyword/radio check is NOT a knowledge score, mastery or secure receipt.", html)
        self.assertNotIn('data-g9-mastery="independent"', html)
        self.assertIn('window.g9MaterialiseAll=()=>{q(\'[data-g9-concept-target]\')', html)


if __name__ == "__main__":
    unittest.main()
