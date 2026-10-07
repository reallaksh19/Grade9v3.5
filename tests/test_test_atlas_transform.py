from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from Shared.tools import build_test_site


REPO = Path(__file__).resolve().parents[1]
TRANSFORM = REPO / "Shared/web/atlas-sandbox-transform.v1.json"


class TestTestAtlasTransform(unittest.TestCase):
    def test_transform_targets_current_canonical_atlas_and_every_swap_is_exact(self):
        contract = json.loads(TRANSFORM.read_text(encoding="utf-8"))
        self.assertEqual(contract["template"], "public/physics/nlm/atlas.html")
        source = (REPO / contract["template"]).read_text(encoding="utf-8")
        self.assertEqual(len(contract["swaps"]), 13)
        for step in contract["swaps"]:
            self.assertEqual(source.count(step["old"]), 1, step["old"][:100])
        self.assertEqual(source.count(contract["init"]["block_start"]), 1)
        self.assertEqual(source.count(contract["init"]["call"]), 1)

    def test_generated_test_atlas_has_test_breadcrumb_and_dynamic_init(self):
        page = build_test_site.atlas_page()
        match = re.search(r'<div class="breadcrumb"[^>]*>(.*?)</div>', page, re.S)
        self.assertIsNotNone(match)
        breadcrumb = match.group(1)
        self.assertIn(">TEST</a>", breadcrumb)
        self.assertIn(">Atlas</span>", breadcrumb)
        self.assertNotIn("Newton's Laws of Motion", breadcrumb)
        self.assertNotIn(">Physics</a>", breadcrumb)
        self.assertIn('data-g9-test="sandbox-draft"', page)
        self.assertIn("const matrices = ((window.GRADE9V3", page)
        self.assertIn('../../js/topic-atlas.js', page)
        self.assertIn('../../core-learning/data.js', page)

    def test_full_test_site_render_no_longer_fails_on_atlas_template_shape(self):
        rendered = build_test_site.render_all()
        self.assertEqual(
            set(rendered),
            {"index.html", "atlas/index.html", "rungs/index.html", "deployments/index.html"},
        )
        self.assertIn("No TEST rung matrix yet.", rendered["atlas/index.html"])


if __name__ == "__main__":
    unittest.main()
