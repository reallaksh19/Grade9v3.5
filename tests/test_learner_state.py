"""Direct evidence for the renderer's protected learner and print states."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import quality_observe, render_core  # noqa: E402
from tests.test_quality_gate import complete_fixture  # noqa: E402


class LearnerState(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        bank_path = Path(m["bank_refs"][0])
        bank = json.loads(bank_path.read_text(encoding="utf-8"))
        q = bank["questions"][0]
        q["options"] = ["7/3", "2.33", "3"]
        q["extensions"]["grade9v3:source_format"] = "SINGLE_CORRECT"
        q["hints"] = [
            {"text": "Try an inverse operation.", "reveals": "CONCEPT"},
            {"text": "Remove the added 2 first.", "reveals": "METHOD"},
            {"text": "The exact result is 7/3.", "reveals": "ANSWER"},
        ]
        q["answer"]["source_key"] = {"state": "PRESENT", "value": "2.33", "card": "CARD-1"}
        q["answer"]["key_relation"] = "CONFLICTS_WITH_KEY"
        q["answer"]["key_conflict_explanation"] = "The printed decimal is rounded."
        bank_path.write_text(json.dumps(bank), encoding="utf-8")
        self.manifest = manifest
        self.out = self.tmp / "out"
        self.assertEqual(render_core.main(["build", "--manifest", str(manifest), "--out", str(self.out)]), 0)
        controls = []
        for kind in ("single_choice", "multiple_choice", "true_false", "numeric", "short_text",
                     "free_response", "multipart", "match"):
            response = {"type": kind}
            if kind == "multipart":
                response["parts"] = [{"label": "Number", "type": "numeric"}, "Reason"]
            if kind == "match":
                response.update(match_left=["Left one", "Left two"], match_right=["Right one", "Right two"])
            options = ["Choice one", "Choice two"] if kind in {"single_choice", "multiple_choice"} else None
            controls.append(f'<article data-g9-unit="{kind}">{render_core.attempt_box("Answer", response, options, kind)}'
                            f'{render_core.reveal("Answer", render_core.para("Protected " + kind), ref=kind)}</article>')
        self.controls = self.tmp / "controls.html"
        self.controls.write_text('<!doctype html><html><head><style>' + render_core.CSS + '</style></head><body>'
                                 + ''.join(controls) + '<script>' + render_core.JS + '</script></body></html>',
                                 encoding="utf-8")

    def test_r1_r4_r7_r8_raw_html_and_projection(self):
        source = (self.out / "core2.html").read_text(encoding="utf-8")
        self.assertIn('data-blueprint-slot="support"', source)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', source)
        self.assertIn('data-g9-representation="REP-MATH-NUMBER-LINE"', source)
        self.assertIn('data-g9-response-type="single_choice"', source)
        self.assertIn('<span>7/3</span>', source)
        self.assertNotIn('3x + 2 = 9 (a)', source)
        for phrase in ("Printed book key", "Mathematically verified result", "Why they differ"):
            self.assertIn(phrase, source)
            self.assertNotIn(phrase, re.sub(r"<template\b[^>]*>.*?</template>", "", source, flags=re.S))
        self.assertIn('<li data-g9-rung="1">Try an inverse operation.</li>', source)
        self.assertIn('<template data-g9-rung-payload=', source)
        self.assertNotIn('Remove the added 2 first.', re.sub(r"<template\b[^>]*>.*?</template>", "", source, flags=re.S))
        for role in render_core.ROLES:
            html = (self.out / render_core.ROLE_FILE[role]).read_text(encoding="utf-8")
            if role != "CORE1":
                self.assertIn('data-g9-payload-ref=', html)
        self.assertEqual(render_core.PROTECTION["LEARNER_PDF"], "protected-bytes-absent")

    def test_response_derivation(self):
        self.assertEqual(render_core.response_for({"response": {"type": "match"}})["type"], "match")
        self.assertEqual(render_core.response_for({"extensions": {"grade9v3:source_format": "MULTIPLE_CORRECT"}})["type"], "multiple_choice")
        self.assertEqual(render_core.response_for({"options": ["A", "B"], "answer": {"kind": "EXACT"}})["type"], "single_choice")
        self.assertEqual(render_core.response_for({"subparts": ["a", "b"]})["type"], "multipart")
        self.assertEqual(render_core.response_for({"answer": {"numeric": {"value": "1"}}})["type"], "numeric")
        self.assertEqual(render_core.response_for({})["type"], "free_response")

    def test_schema_accepts_typed_response_and_source_key(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema unavailable")
        schema = json.loads((REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))
        package = json.loads((REPO / "Mathematics/library/linear-equations.v1.json").read_text(encoding="utf-8"))
        q = package["questions"][0]
        q["response"] = {"type": "multipart", "parts": [{"label": "First", "type": "numeric"}, "Second"]}
        q["answer"].update(source_key={"state": "PRESENT", "value": "7/3", "card": "CARD-1"},
                           key_relation="MATCHES_KEY")
        self.assertEqual(list(jsonschema.Draft202012Validator(schema).iter_errors(package)), [])

    def test_all_web_modes_and_observation_follow_template_payloads(self):
        phrase = "The printed decimal is rounded."
        for mode in render_core.MODES:
            pages, gaps, _ = render_core.build(self.manifest, mode=mode)
            self.assertEqual(gaps, [])
            for name, html in pages.items():
                if name == "index.html":
                    continue
                self.assertNotIn(phrase, re.sub(r"<template\b[^>]*>.*?</template>", "", html, flags=re.S))
        source = quality_observe.parse((self.out / "core2.html").read_text(encoding="utf-8"))
        article = source.first("article", attr="data-g9-unit")
        observed = quality_observe._render_core_unit(article)
        self.assertTrue(observed["attempt"])
        self.assertTrue(any(r["gated"] and "verified_result" in r["blocks"] for r in observed["reveals"]))

    def test_no_key_is_one_note_with_verified_answer(self):
        body = render_core._source_solution({"source_key": {"state": "ABSENT"}, "summary": "x = 7/3."})
        self.assertEqual(body.count("<p>"), 1)
        self.assertIn("No printed key", body)
        self.assertIn("x = 7/3.", body)

    @unittest.skipUnless(shutil.which("node"), "Chromium browser unavailable")
    def test_r2_r3_r4_r5_chromium(self):
        result = subprocess.run(["node", str(REPO / "tests/learner_state_browser.mjs"), str(self.out / "core2.html"),
                                 str(self.out / "core1b.html"), str(self.controls)], cwd=REPO,
                                capture_output=True, text=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        evidence = json.loads(result.stdout)
        self.assertTrue(evidence["source_protected_before"])
        self.assertTrue(evidence["source_visible_after"])
        self.assertTrue(evidence["search_excludes_protected"])
        self.assertTrue(evidence["progressive_hints"])
        self.assertTrue(evidence["staged_figure"])
        self.assertEqual(evidence["typed_controls"],
                         ["single_choice", "multiple_choice", "true_false", "numeric", "short_text",
                          "free_response", "multipart", "match"])

    @unittest.skipUnless(shutil.which("node"), "Chromium PDF unavailable")
    def test_r6_pdf_text(self):
        try:
            from pypdf import PdfReader
        except ImportError:
            self.skipTest("pypdf unavailable")
        pdf = self.tmp / "pdf"
        for flag in ([], ["--key"]):
            result = subprocess.run(["node", str(REPO / "tools/print/print-product.mjs"), str(self.out),
                                     "--out", str(pdf), *flag], cwd=REPO, capture_output=True, text=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        learner = " ".join(p.extract_text() or "" for p in PdfReader(pdf / "core2.pdf").pages)
        key = " ".join(p.extract_text() or "" for p in PdfReader(pdf / "core2.key.pdf").pages)
        self.assertNotIn("Printed book key", learner)
        self.assertNotIn("The printed decimal is rounded.", learner)
        self.assertIn("Printed book key", key)
        self.assertIn("The printed decimal is rounded.", key)
        self.assertEqual(json.loads((pdf / "print-receipt.json").read_text())["mode"], "LEARNER_PDF")
        self.assertEqual(json.loads((pdf / "print-key-receipt.json").read_text())["mode"], "KEY_PDF")


if __name__ == "__main__":
    unittest.main()
