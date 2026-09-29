"""Phase-0 freeze: one renderer, plus narrow product-output scope invariants."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import product_manifest, renderer_inventory  # noqa: E402


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


class OneRenderer(unittest.TestCase):
    def test_render_core_is_the_only_renderer_class(self):
        inventory = json.loads(renderer_inventory.INVENTORY.read_text(encoding="utf-8"))
        rows = [r["path"] for r in inventory["renderers"] if r["classification"] == "RENDERER"]
        self.assertEqual(rows, [renderer_inventory.THE_RENDERER])
        self.assertEqual([f for f in renderer_inventory.check()["findings"] if f["code"] == "SECOND_RENDERER"], [])


class OutputRoleScope(unittest.TestCase):
    def test_legacy_manifest_defaults_to_all_six_roles(self):
        self.assertEqual(
            product_manifest.selected_output_roles({}),
            list(product_manifest.OUTPUT_ROLES),
        )

    def test_first_stage_manifest_may_select_core1_only(self):
        self.assertEqual(
            product_manifest.selected_output_roles({"output_roles": ["CORE1"]}),
            ["CORE1"],
        )

    def test_output_role_scope_rejects_empty_duplicate_or_unknown_roles(self):
        for value in ([], ["CORE1", "CORE1"], ["CORE7"]):
            with self.subTest(value=value):
                with self.assertRaises(product_manifest.ProductSelectionError):
                    product_manifest.selected_output_roles({"output_roles": value})

    def test_issue352_nlm_pilot_declares_core1_first_stage_scope(self):
        manifest = json.loads(
            (REPO / "products/physics/phy-nlm-momentum-transfer.manifest.json").read_text(encoding="utf-8")
        )
        package = json.loads(
            (REPO / "Physics/library/phy-nlm-momentum-transfer.v1.json").read_text(encoding="utf-8")
        )
        microtopic = next(
            row for row in package["microtopics"]
            if row["id"] == "MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE"
        )
        self.assertEqual(product_manifest.selected_output_roles(manifest), ["CORE1"])
        self.assertEqual(manifest["selection"]["core2"], [])
        self.assertEqual(manifest["selection"]["microtopics"], [microtopic["id"]])
        self.assertEqual(microtopic["intrinsic_badge"], "HARD")


if __name__ == "__main__":
    unittest.main()
