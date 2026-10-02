#!/usr/bin/env python3
"""Tests for assurance projection."""
from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
import sys

# Add Shared/tools to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Shared" / "tools"))
from assurance_projection import check_completeness, check_link_integrity, check_network_policy, check_viewport

class TestAssuranceProjection(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_link_integrity_pass(self):
        p1 = self.dir_path / "index.html"
        p2 = self.dir_path / "style.css"
        p2.write_text("body {}", encoding="utf-8")
        p1.write_text('<link href="style.css" rel="stylesheet">', encoding="utf-8")
        fails = check_link_integrity([p1], self.dir_path)
        self.assertEqual(len(fails), 0)
        
    def test_link_integrity_fail_dead(self):
        p1 = self.dir_path / "index.html"
        p1.write_text('<a href="missing.html">Link</a>', encoding="utf-8")
        fails = check_link_integrity([p1], self.dir_path)
        self.assertEqual(len(fails), 1)
        
    def test_network_policy_pass(self):
        p1 = self.dir_path / "index.html"
        p1.write_text('<html><body>Local content</body></html>', encoding="utf-8")
        fails = check_network_policy([p1])
        self.assertEqual(len(fails), 0)
        
    def test_network_policy_fail_cdn(self):
        p1 = self.dir_path / "index.html"
        p1.write_text('<script src="https://www.gstatic.com/js/test.js"></script>', encoding="utf-8")
        fails = check_network_policy([p1])
        self.assertEqual(len(fails), 1)
        
    def test_viewport_pass(self):
        p1 = self.dir_path / "index.html"
        p1.write_text('<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5.0">', encoding="utf-8")
        fails = check_viewport([p1])
        self.assertEqual(len(fails), 0)
        
    def test_viewport_fail_usno(self):
        p1 = self.dir_path / "index.html"
        p1.write_text('<meta name="viewport" content="width=device-width, user-scalable=no">', encoding="utf-8")
        fails = check_viewport([p1])
        self.assertEqual(len(fails), 1)
        
    def test_viewport_fail_maxscale1(self):
        p1 = self.dir_path / "index.html"
        p1.write_text('<meta name="viewport" content="width=device-width, maximum-scale=1.0">', encoding="utf-8")
        fails = check_viewport([p1])
        self.assertEqual(len(fails), 1)

if __name__ == "__main__":
    unittest.main()
