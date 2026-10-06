#!/usr/bin/env python3
import unittest
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO / "public"

class TestThemeAndOwnerIsolation(unittest.TestCase):
    def get_learner_html_files(self):
        html_files = []
        for root, dirs, files in os.walk(PUBLIC_DIR):
            if "test" in Path(root).parts or "owner" in Path(root).parts:
                continue
            for f in files:
                if f.endswith(".html"):
                    html_files.append(Path(root) / f)
        return html_files

    def test_only_the_owner_authorized_test_hub_link_reaches_learner_navigation(self):
        """TEST is visible only as the explicit #68 lab-tab entry; deeper sandbox/owner links stay isolated."""
        allowed = {
            "index.html": ["test/index.html"],
            "physics/index.html": ["../test/index.html"],
            "chemistry/index.html": ["../test/index.html"],
            "mathematics/index.html": ["../test/index.html"],
        }
        files = self.get_learner_html_files()
        if not files:
            return
        for filepath in files:
            content = filepath.read_text(encoding="utf-8")
            relative = filepath.relative_to(PUBLIC_DIR).as_posix()
            test_links = re.findall(r'href=["\']([^"\']*test/[^"\']*)["\']', content, re.IGNORECASE)
            self.assertEqual(test_links, allowed.get(relative, []), f"Unexpected TEST links in {filepath}: {test_links}")

            if relative in allowed:
                self.assertIn(">TEST · LAB</a>", content, f"Missing sandbox-labelled TEST navigation in {filepath}")
            else:
                self.assertNotIn(">TEST · LAB</a>", content, f"TEST lab navigation leaked into {filepath}")

            self.assertNotIn(">TEST<", content, f"Unlabelled TEST text found in {filepath}")
            self.assertNotIn(">CORE1A<", content, f"Legacy CORE1A breadcrumb found in {filepath}")
            self.assertNotIn(">CORE2<", content, f"Legacy CORE2 breadcrumb found in {filepath}")

    def test_universal_light_theme_default(self):
        """Assert that core pages and question bank do not hardcode data-theme="dark"."""
        files_to_check = [
            PUBLIC_DIR / "standalone" / "practice" / "friction" / "core1a.html",
            PUBLIC_DIR / "standalone" / "practice" / "friction" / "core2.html",
            PUBLIC_DIR / "question-bank" / "index.html"
        ]
        
        for filepath in files_to_check:
            if not filepath.exists():
                continue # May not be built yet in CI context before the build
            content = filepath.read_text(encoding="utf-8")
            self.assertNotIn('data-theme="dark"', content, f"Legacy dark theme found in {filepath}")

    def test_concept_triad_in_core_pages(self):
        """Assert core1a.html contains the top .g9-concept-triad-bar."""
        core1a = PUBLIC_DIR / "standalone" / "practice" / "friction" / "core1a.html"
        if not core1a.exists():
            self.skipTest("core1a.html not built yet")
            
        content = core1a.read_text(encoding="utf-8")
        self.assertIn('class="g9-concept-triad-bar"', content, f"Missing concept triad bar in {core1a}")
        self.assertIn('g9-btn-learn', content)
        self.assertIn('g9-btn-practice', content)

    def test_data_g9_shell_attribute(self):
        """Ensure <html lang="en" data-g9-shell> attribute is present on all outer pages."""
        files_to_check = [
            PUBLIC_DIR / "index.html",
            PUBLIC_DIR / "physics" / "index.html",
            PUBLIC_DIR / "question-bank" / "index.html",
            PUBLIC_DIR / "topics" / "nlm" / "index.html"
        ]
        
        for filepath in files_to_check:
            if not filepath.exists():
                continue
            content = filepath.read_text(encoding="utf-8")
            self.assertIn('data-g9-shell', content, f"Missing data-g9-shell in {filepath}")

if __name__ == '__main__':
    unittest.main()
