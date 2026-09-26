"""The deployed site may only get better: no navigation finding outside the committed baseline."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import site_nav_audit  # noqa: E402


class SiteNavAudit(unittest.TestCase):
    def test_no_new_navigation_findings_beyond_the_baseline(self):
        report = site_nav_audit.audit()
        baseline = json.loads(site_nav_audit.BASELINE.read_text(encoding="utf-8"))["findings"]
        new = site_nav_audit.keys(report["findings"]) - site_nav_audit.keys(baseline)
        self.assertEqual(sorted(new), [], "fix these or, if intended, they must not exist; the baseline only shrinks")

    def test_audit_detects_each_problem_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text('<meta name="viewport" content="x"><a href="a.html">A</a>')
            (root / "a.html").write_text('<meta name="viewport" content="x"><a href="missing.html">x</a>'
                                         '<script src="https://cdn.example.com/x.js"></script>')
            (root / "orphan.html").write_text('<html data-g9-shell><meta name="viewport" content="x"></html>')
            codes = {(f["code"], f["page"]) for f in site_nav_audit.audit(root)["findings"]}
        self.assertIn(("BROKEN_LINK", "a.html"), codes)
        self.assertIn(("NO_WAY_HOME", "a.html"), codes)
        self.assertIn(("EXTERNAL_RUNTIME_DEP", "a.html"), codes)
        self.assertIn(("ORPHAN", "orphan.html"), codes)
        self.assertNotIn(("NO_SHELL", "orphan.html"), codes)
        self.assertNotIn(("NO_WAY_HOME", "orphan.html"), codes)


if __name__ == "__main__":
    unittest.main()
