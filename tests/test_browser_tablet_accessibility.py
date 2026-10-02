#!/usr/bin/env python3
"""Unit and accessibility tests for Grade9V3.5 tablet & browser conformance (UNIT-17)."""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PUBLIC = REPO / "public"


class TestBrowserTabletAccessibility(unittest.TestCase):
    def setUp(self):
        self.surfaces = [
            PUBLIC / "index.html",
            PUBLIC / "physics" / "index.html",
            PUBLIC / "topics" / "nlm" / "index.html",
            PUBLIC / "standalone" / "practice" / "friction" / "core1a.html",
            PUBLIC / "standalone" / "practice" / "friction" / "core2.html",
            PUBLIC / "physics" / "nlm" / "explorers" / "friction-threshold" / "index.html"
        ]

    def test_all_surfaces_exist(self):
        for p in self.surfaces:
            self.assertTrue(p.exists(), f"Surface missing: {p}")

    def test_responsive_viewport_conformance(self):
        for p in self.surfaces:
            text = p.read_text(encoding="utf-8")
            self.assertIn('name="viewport"', text, f"{p.name} missing viewport meta")
            self.assertIn("width=device-width", text, f"{p.name} missing width=device-width")
            self.assertNotIn("user-scalable=no", text, f"{p.name} forbids zoom (user-scalable=no)")
            self.assertNotIn("maximum-scale=1.0", text, f"{p.name} forbids zoom (maximum-scale=1.0)")

    def test_touch_target_policy_and_typography_floor(self):
        css_file = PUBLIC / "css" / "modern-learner.css"
        self.assertTrue(css_file.exists())
        css_text = css_file.read_text(encoding="utf-8")

        # 48px touch floor
        self.assertIn("--touch-min: 48px", css_text)
        self.assertIn("min-height: var(--touch-min)", css_text)

        # 14px typography floor
        self.assertIn("--font-floor: 14px", css_text)

    def test_offline_local_network_policy_no_unauthorized_cdns(self):
        forbidden_hosts = ["unpkg.com", "cdnjs.cloudflare.com", "cdn.jsdelivr.net", "fonts.googleapis.com"]
        for p in self.surfaces:
            text = p.read_text(encoding="utf-8")
            for host in forbidden_hosts:
                self.assertNotIn(host, text, f"{p.name} contains remote external host: {host}")

    def test_reciprocal_navigation_integrity(self):
        # 1. Topic workspace links to Core1A, Core2, Explorer, QB
        ws_text = (PUBLIC / "topics" / "nlm" / "index.html").read_text(encoding="utf-8")
        self.assertIn("core1a.html", ws_text)
        self.assertIn("core2.html", ws_text)
        self.assertIn("friction-threshold", ws_text)
        self.assertIn("question-bank/index.html?capability=MIC-PHY-NLM-FRICTION", ws_text)

        # 2. Core1A links to Core2, Explorer, QB
        c1_text = (PUBLIC / "standalone" / "practice" / "friction" / "core1a.html").read_text(encoding="utf-8")
        self.assertIn("core2.html", c1_text)
        self.assertIn("friction-threshold", c1_text)
        self.assertIn("question-bank/index.html?capability=MIC-PHY-NLM-FRICTION", c1_text)

        # 3. Core2 links to Core1A
        c2_text = (PUBLIC / "standalone" / "practice" / "friction" / "core2.html").read_text(encoding="utf-8")
        self.assertIn("core1a.html", c2_text)

        # 4. Explorer links to Core1A, Core2, QB
        exp_text = (PUBLIC / "physics" / "nlm" / "explorers" / "friction-threshold" / "index.html").read_text(encoding="utf-8")
        self.assertIn("core1a.html", exp_text)
        self.assertIn("core2.html", exp_text)
        self.assertIn("question-bank/index.html?capability=MIC-PHY-NLM-FRICTION", exp_text)


if __name__ == "__main__":
    unittest.main()
