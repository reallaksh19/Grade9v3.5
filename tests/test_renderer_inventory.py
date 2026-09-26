"""Phase-0 freeze: no learner-content renderer may exist in main unless it is inventoried."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import renderer_inventory  # noqa: E402


class RendererInventory(unittest.TestCase):
    def test_every_renderer_in_main_is_classified(self):
        report = renderer_inventory.check()
        self.assertEqual(report["findings"], [], "a new renderer needs an inventory entry; new product generators are frozen until Phase 3")

    def test_scanner_detects_a_new_html_and_pdf_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Physics/tools").mkdir(parents=True)
            (root / "Physics/tools/new_product.py").write_text('PAGE = "<!doctype html><html></html>"\n')
            (root / "Physics/tools/new_pdf.py").write_text("from reportlab.pdfgen import canvas\n")
            found = renderer_inventory.candidates(root)
        self.assertEqual(found["Physics/tools/new_product.py"], "PYTHON_HTML")
        self.assertEqual(found["Physics/tools/new_pdf.py"], "PYTHON_PDF")


if __name__ == "__main__":
    unittest.main()
