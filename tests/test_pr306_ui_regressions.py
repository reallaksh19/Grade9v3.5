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


if __name__ == "__main__":
    unittest.main()
