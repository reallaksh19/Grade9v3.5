#!/usr/bin/env python3
"""Regression and falsifier tests for the GCDR runtime auditor."""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from Shared.tools import gcdr_runtime_audit


@unittest.skipUnless(shutil.which("node"), "Node runtime is required for GCDR runtime smoke tests")
class GCDRRuntimeAuditTest(unittest.TestCase):
    def test_motion2d_explorers_pass_runtime_integrity_slice(self):
        report = gcdr_runtime_audit.audit(gcdr_runtime_audit.REPO)
        self.assertTrue(report["passed"])
        rows = [row for row in report["activities"] if row["resource"].startswith("ACT-KIN-2D-")]
        self.assertEqual(len(rows), 6)
        for row in rows:
            with self.subTest(activity=row["resource"]):
                self.assertEqual(
                    row["checks"],
                    {
                        "implementation_locator": "PASS",
                        "static_syntax": "PASS",
                        "handler_and_control_integrity": "PASS",
                        "identifier_integrity": "PASS",
                        "no_placeholder_or_undefined_output": "PASS",
                        "deterministic_reset": "PASS",
                        "runtime_smoke": "PASS",
                        "accessibility_baseline": "PASS",
                    },
                )

    def _inspect(self, html: str):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(html, encoding="utf-8")
            return gcdr_runtime_audit.inspect_html(path)

    def test_duplicate_ids_are_detected(self):
        result = self._inspect(
            """<!doctype html><html><body>
            <div id="same"></div><div id="same"></div>
            <button id="reset">Reset</button>
            <script>reset.onclick=()=>{};</script>
            </body></html>"""
        )
        self.assertEqual(result["checks"]["identifier_integrity"], "FAIL")
        self.assertIn("same", result["details"]["duplicate_ids"])

    def test_dead_manipulation_is_detected(self):
        result = self._inspect(
            """<!doctype html><html><body>
            <label>Value <input id="x" type="range" min="0" max="10" value="5"></label>
            <div id="out"></div><button id="reset">Reset</button>
            <script>
            x.oninput=()=>{};
            reset.onclick=()=>{x.value=5;out.textContent='';};
            </script>
            </body></html>"""
        )
        self.assertEqual(result["checks"]["handler_and_control_integrity"], "FAIL")
        self.assertIn("x", result["details"]["no_effect_controls"])

    def test_undefined_runtime_output_is_detected(self):
        result = self._inspect(
            """<!doctype html><html><body>
            <label>Value <input id="x" type="range" min="0" max="10" value="5"></label>
            <div id="out"></div><button id="reset">Reset</button>
            <script>
            function draw(){out.textContent=undefined;}
            x.oninput=draw;
            reset.onclick=()=>{x.value=5;draw();};
            draw();
            </script>
            </body></html>"""
        )
        self.assertEqual(result["checks"]["no_placeholder_or_undefined_output"], "FAIL")
        self.assertIn("undefined", result["details"]["placeholder_hits"])

    def test_missing_control_label_is_detected(self):
        result = self._inspect(
            """<!doctype html><html><body>
            <select id="mode"><option value="a">A</option><option value="b">B</option></select>
            <div id="out"></div><button id="reset">Reset</button>
            <script>
            function draw(){out.textContent=mode.value;}
            mode.onchange=draw;
            reset.onclick=()=>{mode.value='a';draw();};
            draw();
            </script>
            </body></html>"""
        )
        self.assertEqual(result["checks"]["accessibility_baseline"], "FAIL")
        self.assertTrue(result["details"]["accessibility_problems"])

    def test_missing_reset_is_detected(self):
        result = self._inspect(
            """<!doctype html><html><body>
            <label>Value <input id="x" type="range" min="0" max="10" value="5"></label>
            <div id="out"></div>
            <script>x.oninput=()=>{out.textContent=x.value;};</script>
            </body></html>"""
        )
        self.assertEqual(result["checks"]["deterministic_reset"], "FAIL")

    def test_js_syntax_error_is_detected(self):
        result = self._inspect(
            """<!doctype html><html><body>
            <button id="reset">Reset</button>
            <script>function broken( {</script>
            </body></html>"""
        )
        self.assertEqual(result["checks"]["static_syntax"], "FAIL")
        self.assertTrue(result["details"]["syntax_errors"])


if __name__ == "__main__":
    unittest.main()
