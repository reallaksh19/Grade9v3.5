from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from Shared.tools import interactive_chromium_gate as gate


class InteractiveChromiumGateTests(unittest.TestCase):
    def receipt(self, html: Path):
        checks = {
            name: {"verdict": "PASS", "evidence": {}}
            for name in gate.REQUIRED_CHECKS
        }
        return {
            "schema": "interactive-chromium-audit/v1",
            "engine": "chromium",
            "html_path": html.name,
            "html_sha256": "sha256:" + hashlib.sha256(html.read_bytes()).hexdigest(),
            "audited_at": "2026-10-03T18:00:00Z",
            "viewports": [
                {"name": "tablet-landscape", "width": 1366, "height": 854},
                {"name": "tablet-portrait", "width": 854, "height": 1366},
            ],
            "checks": checks,
            "status": "PASS",
            "note": "fixture",
        }

    def test_exact_chromium_receipt_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "interactive.html"
            html.write_text("<!doctype html><main><h1>x</h1><button>go</button></main>", encoding="utf-8")
            self.assertEqual(gate.validate(html, self.receipt(html)), [])

    def test_non_chromium_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "interactive.html"
            html.write_text("<main><h1>x</h1></main>", encoding="utf-8")
            receipt = self.receipt(html)
            receipt["engine"] = "webkit"
            self.assertIn("CHROMIUM_REQUIRED", gate.validate(html, receipt))

    def test_stale_html_digest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "interactive.html"
            html.write_text("<main><h1>x</h1></main>", encoding="utf-8")
            receipt = self.receipt(html)
            html.write_text("<main><h1>changed</h1></main>", encoding="utf-8")
            self.assertIn("HTML_DIGEST_MISMATCH", gate.validate(html, receipt))

    def test_any_failed_browser_check_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = Path(tmp) / "interactive.html"
            html.write_text("<main><h1>x</h1></main>", encoding="utf-8")
            receipt = self.receipt(html)
            receipt["checks"]["touch_targets"]["verdict"] = "FAIL"
            receipt["status"] = "FAIL"
            errors = gate.validate(html, receipt)
            self.assertIn("CHROMIUM_AUDIT_NOT_PASS", errors)
            self.assertIn("CHECK_NOT_PASS:touch_targets", errors)


if __name__ == "__main__":
    unittest.main()
