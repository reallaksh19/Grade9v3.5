"""Regression guards for independently verified PR #306 UI/runtime findings."""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class Pr306UiRegressions(unittest.TestCase):
    def test_shared_search_does_not_assign_read_only_window_top(self):
        source = (REPO / "public" / "js" / "site-header.js").read_text(encoding="utf-8")
        self.assertNotIn(",top=document.createElement", source)
        self.assertIn("const top=document.createElement('div')", source)

    def test_friction_graph_uses_pointer_events_and_css_to_canvas_scaling(self):
        source = (
            REPO
            / "public"
            / "physics"
            / "nlm"
            / "explorers"
            / "friction-threshold"
            / "index.html"
        ).read_text(encoding="utf-8")
        self.assertIn("#graphCanvas {", source)
        self.assertIn("touch-action: none", source)
        self.assertIn("graphCanvas.addEventListener('pointerdown'", source)
        self.assertIn("graphCanvas.addEventListener('pointermove'", source)
        self.assertIn("graphCanvas.addEventListener('pointerup'", source)
        self.assertIn("graphCanvas.addEventListener('pointercancel'", source)
        self.assertIn("graphCanvas.width / rect.width", source)
        self.assertIn("graphCanvas.height / rect.height", source)
        self.assertNotIn("graphCanvas.addEventListener('mousedown'", source)

    def test_question_hub_is_keyboard_safe_dialog_in_public_and_standalone(self):
        paths = [
            REPO / "public" / "physics" / "motion-in-2d" / "explorers" / "motions_in_2d" / "index.html",
            REPO / "standalone" / "motion-in-2d-master-suite.html",
        ]
        for path in paths:
            with self.subTest(path=path):
                source = path.read_text(encoding="utf-8")
                self.assertIn('id="jeeHubModal" role="dialog" aria-modal="true"', source)
                self.assertIn('aria-labelledby="jeeHubTitle"', source)
                self.assertIn("event.key === 'Escape'", source)
                self.assertIn("event.key !== 'Tab'", source)
                self.assertIn("document.body.style.overflow = 'hidden'", source)
                self.assertIn("jeeHubLastFocus.focus()", source)
                self.assertIn("jeeHubFocusable(modal)", source)

    def test_question_bank_renders_current_physics_ascii_math_with_katex(self):
        runtime = (REPO / "public" / "js" / "question-bank.js").read_text(encoding="utf-8")
        data = (REPO / "public" / "data" / "question-bank-data.js").read_text(encoding="utf-8")
        self.assertIn("sqrt(", data)
        self.assertRegex(data, r"[A-Za-z]\\^[0-9]")
        self.assertIn("function asciiMathTokenToTex", runtime)
        self.assertIn("function renderPhysicsAsciiMath", runtime)
        self.assertIn("data-qb-subject", runtime)
        self.assertIn("katex.render(asciiMathTokenToTex", runtime)
        self.assertIn("renderPhysicsAsciiMath(els.results)", runtime)

    def test_katex_vendor_dependency_closure_and_no_jsdelivr_runtime(self):
        css = (REPO / "public" / "vendor" / "katex" / "0.16.8" / "katex.min.css").read_text(encoding="utf-8")
        fonts = set(
            p.name
            for p in (REPO / "public" / "vendor" / "katex" / "0.16.8" / "fonts").glob("*.woff2")
        )
        referenced = set(__import__("re").findall(r"url\\([^)]*/([^/'\")]+\\.woff2)", css))
        self.assertEqual(referenced - fonts, set())
        self.assertTrue((REPO / "public" / "vendor" / "katex" / "0.16.8" / "LICENSE").is_file())

        for root_name in ("public", "standalone"):
            for path in (REPO / root_name).rglob("*.html"):
                if "/products/" in path.as_posix():
                    continue
                source = path.read_text(encoding="utf-8")
                self.assertNotIn(
                    "cdn.jsdelivr.net/npm/katex@0.16.8",
                    source,
                    msg=f"external KaTeX runtime remains in {path.relative_to(REPO)}",
                )

    def test_tailwind_external_runtime_is_still_explicit_until_vendored(self):
        offenders = []
        for root_name in ("public", "standalone"):
            for path in (REPO / root_name).rglob("*.html"):
                source = path.read_text(encoding="utf-8")
                if "cdn.tailwindcss.com" in source or "gstatic.com/antigravity" in source:
                    offenders.append(path.relative_to(REPO).as_posix())
        self.assertTrue(offenders, "remove this sentinel once Tailwind is actually local")


if __name__ == "__main__":
    unittest.main()
