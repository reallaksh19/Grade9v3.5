from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from Shared.tools import build_pages_site, render_core


REPO = Path(__file__).resolve().parents[1]


class UiBlueprintContractTest(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(
            (REPO / "Shared" / "web" / "interactive-page-blueprints.v1.json").read_text(encoding="utf-8")
        )
        self.shell = self.registry["shell"]

    def test_shell_carries_systemic_learner_web_invariants(self):
        self.assertEqual(self.shell["typography_policy"]["minimum_learner_text_css_px"], 14)
        self.assertEqual(
            self.shell["math_policy"]["static_relation_format"],
            "RESTRICTED_PRESENTATION_MATHML",
        )
        self.assertEqual(self.shell["math_policy"]["dynamic_question_format"], "TYPED_TEX_SEGMENTS")
        self.assertEqual(self.shell["math_policy"]["dynamic_renderer"], "LOCAL_KATEX")
        self.assertEqual(self.shell["math_policy"]["runtime_text_inference"], "FORBIDDEN")
        self.assertTrue(
            self.shell["representation_accessibility_policy"][
                "instructional_visual_requires_accessible_name"
            ]
        )
        self.assertTrue(
            self.shell["representation_accessibility_policy"][
                "instructional_visual_requires_description"
            ]
        )
        self.assertEqual(
            self.shell["data_representation_policy"]["comparative_relations"],
            "TABLE_OR_MATRIX_ALLOWED",
        )
        self.assertEqual(
            self.shell["data_representation_policy"]["tag_count_as_quality_metric"],
            "FORBIDDEN",
        )
        self.assertEqual(self.shell["vendor_policy"]["publication_rewrite"], "BUILD_PIPELINE")
        self.assertEqual(self.shell["vendor_policy"]["unknown_runtime_dependency"], "FAIL_CLOSED")

    def test_shared_site_tokens_respect_blueprint_text_floor(self):
        css = (REPO / "public" / "css" / "site.css").read_text(encoding="utf-8")
        root_px = 16
        floor = self.shell["typography_policy"]["minimum_learner_text_css_px"]
        tokens = dict(re.findall(r"--(text-(?:xs|sm)):\s*([0-9.]+)rem", css))
        self.assertEqual(set(tokens), {"text-xs", "text-sm"})
        for name, value in tokens.items():
            with self.subTest(token=name):
                self.assertGreaterEqual(float(value) * root_px, floor)

    def test_renderer_and_pages_builder_implement_blueprint_authority(self):
        self.assertEqual(render_core.RENDERER_VERSION, "render_core/2")
        source = (REPO / "Shared" / "tools" / "render_core.py").read_text(encoding="utf-8")
        self.assertIn("ctx.blueprints", source)
        self.assertIn("_shared_head_assets", source)
        self.assertIn("authored SVG lacks an accessible name", source)
        self.assertEqual(build_pages_site.GENERATOR_VERSION, "1.2.0")
        self.assertTrue(build_pages_site.VENDOR_REWRITES)


if __name__ == "__main__":
    unittest.main()