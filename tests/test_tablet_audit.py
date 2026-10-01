"""The 12.7-inch tablet promises, measured in a real browser: short identity block, columns that start together, no overflow."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from Shared.tools import render_core

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "products/physics/phy-kin-2d-motion.manifest.json"


def _browser_available() -> str | None:
    """None when a Chromium can be driven from Node here; otherwise why not."""
    node = shutil.which("node")
    if not node:
        return "node is not installed"
    probe = ("const {execSync}=require('child_process');let p;try{p=require('playwright')}catch(e){"
             "try{p=require(execSync('npm root -g').toString().trim()+'/playwright')}catch(e2){console.log('no playwright');process.exit(3)}}"
             "p.chromium.launch().then(b=>b.close()).then(()=>process.exit(0)).catch(e=>{console.log(String(e).slice(0,120));process.exit(4)})")
    run = subprocess.run([node, "-e", probe], capture_output=True, text=True, cwd=REPO, timeout=120)
    return None if run.returncode == 0 else (run.stdout.strip() or "chromium cannot be launched")


class TabletAudit(unittest.TestCase):
    def test_the_reference_product_keeps_the_blueprints_tablet_promises(self):
        why_not = _browser_available()
        if why_not:
            self.skipTest(why_not)
        pages, gaps, _digest = render_core.build(MANIFEST, mode="PAGES")
        self.assertEqual(gaps, [])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "products" / "physics" / "phy-kin-2d-motion"
            out.mkdir(parents=True)
            for name, content in pages.items():
                (out / name).write_text(content, encoding="utf-8")
            (root / "css").mkdir()
            shutil.copy2(REPO / "public/css/tablet-12-7.css", root / "css/tablet-12-7.css")
            report = root / "audit.json"
            run = subprocess.run(["node", str(REPO / "tools/site-audit/core-page-audit.mjs"), str(out), "--profile", "tablet-12.7",
                                  "--http-root", str(root), "--enforce", "--json", str(report)],
                                 capture_output=True, text=True, cwd=REPO, timeout=900)
            self.assertEqual(run.returncode, 0, run.stdout[-1500:] + run.stderr[-1500:])
            self.assertIn("tablet-12.7 enforcement: PASS", run.stdout)
            measured = json.loads(report.read_text(encoding="utf-8"))
            for file in ("core1a.html", "core2.html"):
                row = measured[file]["viewports"]["tablet-1366-landscape"]["tablet"]
                self.assertIsNotNone(row, file)
                self.assertEqual(row["supportOffsetMaxPx"], 0, file)
                self.assertLessEqual(row["identityMaxPx"], 200, file)


if __name__ == "__main__":
    unittest.main()
