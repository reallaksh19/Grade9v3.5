#!/usr/bin/env python3
"""Unit tests for Grade9V3.5 Migration, Route Compatibility, and Link Integrity (UNIT-16)."""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PUBLIC = REPO / "public"


class TestMigrationAndLinks(unittest.TestCase):
    def check_links_in_file(self, rel_html_path: str):
        full_path = PUBLIC / rel_html_path
        self.assertTrue(full_path.exists(), f"Source file does not exist: {rel_html_path}")
        html_text = full_path.read_text(encoding="utf-8")
        base_dir = full_path.parent

        # Find all local hrefs (ignoring #anchors, mailto, http/https, javascript:)
        hrefs = re.findall(r'href="([^"#:]+)(?:#[^"]*)?"', html_text)
        for href in hrefs:
            # Strip query params
            clean_href = href.split("?")[0]
            target_file = (base_dir / clean_href).resolve()
            self.assertTrue(
                target_file.exists(),
                f"Dead link in {rel_html_path}: '{href}' (resolved to {target_file})"
            )

    def test_home_page_links_resolve(self):
        self.check_links_in_file("index.html")

    def test_subject_hub_links_resolve(self):
        self.check_links_in_file("physics/index.html")

    def test_topic_workspace_links_resolve(self):
        self.check_links_in_file("topics/nlm/index.html")

    def test_friction_core1a_links_resolve(self):
        self.check_links_in_file("standalone/practice/friction/core1a.html")

    def test_friction_explorer_links_resolve(self):
        self.check_links_in_file("physics/nlm/explorers/friction-threshold/index.html")

    def test_legacy_standalone_index_exists(self):
        self.assertTrue((PUBLIC / "standalone/practice/index.html").exists())

    def test_owner_surfaces_remain_at_legacy_paths(self):
        self.assertTrue((PUBLIC / "test/atlas/index.html").exists())
        self.assertTrue((PUBLIC / "test/rungs/index.html").exists())


if __name__ == "__main__":
    unittest.main()
