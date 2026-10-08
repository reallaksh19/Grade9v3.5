#!/usr/bin/env python3
"""Unit tests for Grade9V3.5 Blueprint additive transitions (UNIT-08, UNIT-09)."""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
from Shared.tools import render_core

MANIFEST_PATH = REPO / "products" / "physics" / "phy-nlm-friction.manifest.json"


class TestBlueprintTransitions(unittest.TestCase):
    def setUp(self):
        self.ctx = render_core.context(MANIFEST_PATH)

    def test_interactive_bridge_rendered_when_explorer_present(self):
        # Microtopic 1: MIC-PHY-NLM-FRICTION has friction-threshold explorer
        m_friction = next(m for m in self.ctx.selection_rows["microtopics"] if m["id"] == "MIC-PHY-NLM-FRICTION")
        bridge_html = render_core._core1a_interactive_bridge(self.ctx, m_friction)
        self.assertIn("data-g9-interactive-bridge", bridge_html)
        self.assertIn("Try it visually", bridge_html)
        self.assertIn('href="../../../physics/nlm/explorers/friction-threshold/index.html"', bridge_html)

    def test_interactive_bridge_absent_when_no_explorer(self):
        # Microtopic 2: MIC-PHY-NLM-FRICTION-QUANT has NO explorer
        m_quant = next(m for m in self.ctx.selection_rows["microtopics"] if m["id"] == "MIC-PHY-NLM-FRICTION-QUANT")
        bridge_html = render_core._core1a_interactive_bridge(self.ctx, m_quant)
        self.assertEqual(bridge_html, "", "When no explorer is bound, interactive bridge must render nothing")

    def test_learning_transitions_rendered(self):
        m_friction = next(m for m in self.ctx.selection_rows["microtopics"] if m["id"] == "MIC-PHY-NLM-FRICTION")
        transitions_html = render_core._core1a_learning_transitions(self.ctx, m_friction)
        self.assertIn("data-g9-transitions", transitions_html)
        self.assertIn("core2.html", transitions_html)
        self.assertIn("question-bank/index.html?capability=MIC-PHY-NLM-FRICTION", transitions_html)


if __name__ == "__main__":
    unittest.main()
