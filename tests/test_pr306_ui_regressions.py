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

    def test_question_bank_renders_only_schema_declared_math_with_katex(self):
        import json

        runtime = (REPO / "public" / "js" / "question-bank.js").read_text(encoding="utf-8")
        bank = json.loads(
            (REPO / "Physics" / "library" / "exam-bank" / "competitive-exam-question-bank.v2.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("ASCII_MATH_TOKEN", runtime)
        self.assertNotIn("renderPhysicsAsciiMath", runtime)
        self.assertIn("renderDeclaredMath", runtime)
        self.assertIn("data-qb-math-target", runtime)
        self.assertIn("katex.render(spec.tex", runtime)

        spans = [
            span
            for q in bank["questions"]
            for span in q.get("extensions", {}).get("grade9v3:math_spans", [])
        ]
        self.assertTrue(spans)
        literals = {span["literal"].lower() for span in spans}
        self.assertNotIn("sink", literals)
        self.assertNotIn("cosine", literals)
        self.assertTrue(any("sqrt(" in span["literal"] for span in spans))

        def source_text(question, target):
            if target == "stem":
                return question["stem"]
            if target == "conditions":
                return " ".join(question.get("conditions", []))
            if target == "common_wrong_route":
                return question["extensions"]["grade9v3:analysis"]["common_wrong_route"]
            if target == "answer_summary":
                return question["answer"]["summary"]
            if target == "answer_check":
                return question["answer"]["check"]
            kind, index = target.split(":", 1)
            index = int(index)
            if kind == "option":
                return question["options"][index]
            if kind == "source_hint":
                hint = question["hints"][index]
                return hint if isinstance(hint, str) else hint["text"]
            if kind == "scaffold":
                return question["scaffolds"][index]["text"]
            if kind == "answer_reasoning":
                return question["answer"]["reasoning"][index]
            self.fail(f"unknown math target {target}")

        for question in bank["questions"]:
            for span in question.get("extensions", {}).get("grade9v3:math_spans", []):
                self.assertIn(span["literal"], source_text(question, span["target"]))

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

    def test_tailwind_external_runtime_is_owned_by_pages_publication_contract(self):
        from Shared.tools import build_pages_site

        runtime = REPO / "public" / "vendor" / "tailwind" / "3.4.17" / "tailwind-play.js"
        self.assertTrue(runtime.is_file())
        self.assertEqual(
            build_pages_site.VENDOR_REWRITES["https://cdn.tailwindcss.com"],
            "vendor/tailwind/3.4.17/tailwind-play.js",
        )
        self.assertEqual(
            build_pages_site.VENDOR_REWRITES["https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"],
            "vendor/tailwind/3.4.17/tailwind-play.js",
        )

    def test_interactive_pages_do_not_disable_browser_zoom(self):
        paths = [
            "public/chemistry/bonding/explorers/chemical_bonding/index.html",
            "public/chemistry/gases/explorers/behaviour_of_gases/index.html",
            "public/chemistry/some-basic-concepts/explorers/mole_concept/index.html",
            "public/mathematics/vectors/explorers/vector_algebra/index.html",
            "public/physics/motion-1d/explorers/motion_in_1d/index.html",
            "public/physics/motion-in-2d/explorers/motions_in_2d/index.html",
            "standalone/chemistry-behaviour-of-gases-master-suite.html",
            "standalone/chemistry-chemical-bonding-master-suite.html",
            "standalone/chemistry-mole-concept-master-suite.html",
            "standalone/motion-in-1d-master-suite.html",
            "standalone/motion-in-2d-master-suite.html",
            "standalone/vector-algebra-3d-master-suite.html",
        ]
        for rel in paths:
            with self.subTest(path=rel):
                source = (REPO / rel).read_text(encoding="utf-8")
                viewport = next(
                    (line for line in source.splitlines() if 'name="viewport"' in line),
                    "",
                )
                self.assertNotIn("user-scalable=no", viewport)
                self.assertNotIn("maximum-scale=1", viewport)

    def test_tailwind_suite_typography_has_no_sub_13px_utilities(self):
        paths = [
            "public/chemistry/bonding/explorers/chemical_bonding/index.html",
            "public/chemistry/gases/explorers/behaviour_of_gases/index.html",
            "public/chemistry/redox/explorers/redox_reactions/index.html",
            "public/chemistry/some-basic-concepts/explorers/mole_concept/index.html",
            "public/mathematics/vectors/explorers/vector_algebra/index.html",
            "public/physics/motion-1d/explorers/motion_in_1d/index.html",
            "public/physics/motion-in-2d/explorers/independent_components_shared_clock/index.html",
            "public/physics/motion-in-2d/explorers/is_it_really_a_projectile/index.html",
            "public/physics/motion-in-2d/explorers/motions_in_2d/index.html",
            "public/physics/motion-in-2d/explorers/same_height_same_speed/index.html",
            "public/physics/motion-in-2d/explorers/the_apex_fallacy/index.html",
            "public/physics/motion-in-2d/explorers/the_event_clock/index.html",
            "standalone/chemistry-behaviour-of-gases-master-suite.html",
            "standalone/chemistry-chemical-bonding-master-suite.html",
            "standalone/chemistry-mole-concept-master-suite.html",
            "standalone/chemistry-redox-reactions-master-suite.html",
            "standalone/motion-in-1d-master-suite.html",
            "standalone/motion-in-2d-master-suite.html",
            "standalone/vector-algebra-3d-master-suite.html",
        ]
        micro = __import__("re").compile(r"text-\[(?:9|10|11|12|12\.5)px\]|\btext-xs\b")
        for rel in paths:
            with self.subTest(path=rel):
                source = (REPO / rel).read_text(encoding="utf-8")
                self.assertIsNone(micro.search(source))

    def test_motion_2d_deglossing_does_not_leave_orphan_keyframe_blocks(self):
        paths = [
            "public/physics/motion-in-2d/explorers/independent_components_shared_clock/index.html",
            "public/physics/motion-in-2d/explorers/motions_in_2d/index.html",
            "public/physics/motion-in-2d/explorers/same_height_same_speed/index.html",
            "standalone/motion-in-2d-master-suite.html",
        ]
        orphan = __import__("re").compile(r"(?m)^\s*(?:0%|25%|50%|75%|100%)\s*\{")
        for rel in paths:
            with self.subTest(path=rel):
                source = (REPO / rel).read_text(encoding="utf-8")
                self.assertNotIn("@keyframes", source)
                self.assertIsNone(orphan.search(source))

    def test_vector_public_orbit_uses_pointer_capture_and_responsive_canvas(self):
        source = (
            REPO / "public" / "mathematics" / "vectors" / "explorers" / "vector_algebra" / "index.html"
        ).read_text(encoding="utf-8")
        self.assertIn("canvas.addEventListener('pointerdown'", source)
        self.assertIn("canvas.addEventListener('pointermove'", source)
        self.assertIn("canvas.addEventListener('pointercancel'", source)
        self.assertIn("canvas.setPointerCapture", source)
        self.assertIn("touch-action: none", source)
        self.assertIn("canvas.dataset.logicalWidth", source)
        self.assertIn("Math.min(window.devicePixelRatio || 1, 2)", source)
        self.assertNotIn("canvas.addEventListener('mousedown'", source)
        self.assertNotIn("canvas.addEventListener('touchstart'", source)

    def test_event_clock_wall_drag_uses_pointer_capture(self):
        source = (
            REPO / "public" / "physics" / "motion-in-2d" / "explorers" / "the_event_clock" / "index.html"
        ).read_text(encoding="utf-8")
        self.assertIn('id="svgContainer" style="touch-action:none"', source)
        self.assertIn("svgContainer.addEventListener('pointerdown'", source)
        self.assertIn("svgContainer.addEventListener('pointermove'", source)
        self.assertIn("svgContainer.addEventListener('pointercancel'", source)
        self.assertIn("svgContainer.setPointerCapture", source)
        self.assertNotIn("svgContainer.addEventListener('mousedown'", source)
        self.assertNotIn("svgContainer.addEventListener('touchstart'", source)

    def test_diagram_typography_has_no_explicit_sub_13px_labels(self):
        paths = [
            "public/chemistry/bonding/explorers/chemical_bonding/index.html",
            "public/chemistry/gases/explorers/behaviour_of_gases/index.html",
            "public/chemistry/redox/explorers/redox_reactions/index.html",
            "public/chemistry/some-basic-concepts/explorers/mole_concept/index.html",
            "public/mathematics/vectors/explorers/vector_algebra/index.html",
            "public/physics/motion-1d/explorers/circular-dynamics/index.html",
            "public/physics/motion-1d/explorers/motion_in_1d/index.html",
            "public/physics/motion-2d/explorers/motion-in-a-plane/index.html",
            "public/physics/motion-in-2d/explorers/independent_components_shared_clock/index.html",
            "public/physics/motion-in-2d/explorers/is_it_really_a_projectile/index.html",
            "public/physics/motion-in-2d/explorers/motions_in_2d/index.html",
            "public/physics/motion-in-2d/explorers/same_height_same_speed/index.html",
            "public/physics/motion-in-2d/explorers/the_apex_fallacy/index.html",
            "public/physics/motion-in-2d/explorers/the_event_clock/index.html",
            "public/physics/nlm/explorers/accelerated-frames/index.html",
            "public/physics/nlm/explorers/atwood-pulleys/index.html",
            "public/physics/nlm/explorers/connected-blocks/index.html",
            "public/physics/nlm/explorers/friction-threshold/index.html",
            "standalone/chemistry-behaviour-of-gases-master-suite.html",
            "standalone/chemistry-chemical-bonding-master-suite.html",
            "standalone/chemistry-mole-concept-master-suite.html",
            "standalone/chemistry-redox-reactions-master-suite.html",
            "standalone/core2a-projectile-study.html",
            "standalone/mathematics-polynomials-and-coordinates-suite.html",
            "standalone/motion-in-1d-master-suite.html",
            "standalone/motion-in-2d-master-suite.html",
            "standalone/physics-motion-in-a-plane-interactive-suite.html",
            "standalone/vector-algebra-3d-master-suite.html",
        ]
        re_mod = __import__("re")
        svg_micro = re_mod.compile(r'font-size=["\'](?:[0-9]|1[0-2](?:\.\d+)?)["\']')
        css_micro = re_mod.compile(r"font-size\s*:\s*(?:[0-9]|1[0-2](?:\.\d+)?)px", re_mod.I)
        canvas_micro = re_mod.compile(
            r"\.font\s*=\s*[\"\'][^\"\']*?(?:[0-9]|1[0-2](?:\.\d+)?)px[^\"\']*[\"\']"
        )
        for rel in paths:
            with self.subTest(path=rel):
                source = (REPO / rel).read_text(encoding="utf-8")
                self.assertIsNone(svg_micro.search(source))
                self.assertIsNone(css_micro.search(source))
                self.assertIsNone(canvas_micro.search(source))

    def test_changed_webpage_style_blocks_have_balanced_braces(self):
        paths = [
            "public/physics/motion-in-2d/explorers/motions_in_2d/index.html",
            "public/physics/motion-in-2d/explorers/the_apex_fallacy/index.html",
            "public/physics/motion-in-2d/explorers/the_event_clock/index.html",
            "standalone/motion-in-2d-master-suite.html",
        ]
        style_re = __import__("re").compile(r"<style[^>]*>([\\s\\S]*?)</style>", __import__("re").I)
        for rel in paths:
            with self.subTest(path=rel):
                source = (REPO / rel).read_text(encoding="utf-8")
                for style in style_re.findall(source):
                    self.assertEqual(style.count("{"), style.count("}"))


if __name__ == "__main__":
    unittest.main()