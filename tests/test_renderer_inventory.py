"""Phase-0 freeze: one renderer, plus narrow product-output scope invariants."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_products, product_manifest, render_core, renderer_inventory  # noqa: E402


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
    PILOT = REPO / "products/physics/phy-nlm-momentum-transfer.manifest.json"
    BANK_FIRST = REPO / "golden/units/G-CORE2-R2/manifest.json"

    def _scoped_manifest(self, source: Path, roles: list[str], tmp: str) -> Path:
        manifest = json.loads(source.read_text(encoding="utf-8"))
        manifest["output_roles"] = roles
        path = Path(tmp) / "scoped-manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

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
        for value in (None, "CORE1", {}, 1, [], ["CORE1", "CORE1"], ["CORE7"]):
            with self.subTest(value=value):
                with self.assertRaises(product_manifest.ProductSelectionError):
                    product_manifest.selected_output_roles({"output_roles": value})

    def test_product_rederive_preserves_explicit_output_scope(self):
        self.assertIn("output_roles", build_products.PRESERVED_MANIFEST_KEYS)

    def test_scoped_cross_core_links_resolve_in_pages_and_single_file(self):
        for roles in (["CORE2A"], ["CORE2B"], ["CORE1A", "CORE2A", "CORE2B"]):
            for mode in ("PAGES", "SINGLE_FILE"):
                with self.subTest(roles=roles, mode=mode), tempfile.TemporaryDirectory() as tmp:
                    path = self._scoped_manifest(self.PILOT, roles, tmp)
                    pages, _, _ = render_core.build(path, mode=mode)
                    for html in pages.values():
                        for file, anchor in re.findall(r'href="(core[12][ab]?\.html)#([^"]+)"', html):
                            self.assertIn(file, pages)
                            self.assertIn(f'id="{anchor}"', pages[file])
                        for anchor in re.findall(r'href="#(g9-CORE[^"]+)"', html):
                            self.assertIn(f'id="{anchor}"', html)
                    self.assertIn("Revisit:", "".join(pages.values()))

    def test_rerender_retires_only_receipt_owned_outputs_and_invalidates_prints(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rendered"
            path = self._scoped_manifest(self.PILOT, list(product_manifest.OUTPUT_ROLES), tmp)
            args = ["build", "--manifest", str(path), "--out", str(out), "--draft"]
            self.assertEqual(render_core.main(args), 0)
            (out / "notes.txt").write_text("keep")
            (out / "user.pdf").write_bytes(b"keep")
            for name in ("core1.pdf", "core2.key.pdf", "print-receipt.json", "print-key-receipt.json"):
                (out / name).write_text("obsolete")
            self._scoped_manifest(self.PILOT, ["CORE1"], tmp)
            self.assertEqual(render_core.main(args), 0)
            self.assertEqual({p.name for p in out.glob("*.html")}, {"core1.html", "index.html"})
            self.assertEqual({p.name for p in out.glob("*.pdf")}, {"user.pdf"})
            self.assertFalse((out / "print-receipt.json").exists())
            self.assertFalse((out / "print-key-receipt.json").exists())
            from Shared.tools.accept_product import verify_render
            verify_render(out)
            self.assertEqual(render_core.main(args + ["--mode", "SINGLE_FILE"]), 0)
            self.assertEqual({p.name for p in out.glob("*.html")}, {"product.html"})
            self.assertEqual((out / "notes.txt").read_text(), "keep")
            self.assertEqual(render_core.main(args), 0)
            verify_render(out)

    def test_issue352_nlm_pilot_declares_complete_core1_first_stage_scope(self):
        manifest = json.loads(self.PILOT.read_text(encoding="utf-8"))
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
        self.assertEqual(
            microtopic["compact_anchor"]["result"],
            "F_avg,on_ejecta = R Delta p_item = 5(+2) = +10 N. The launcher receives the interaction-partner recoil force -10 N, so a fixed launcher requires a +10 N external holding force to balance that recoil.",
        )
        self.assertNotIn("representation_ref", microtopic["compact_anchor"])

    def test_renderer_emits_zero_gap_declared_first_stage_pages(self):
        pages, gaps, _digest = render_core.build(self.PILOT, mode="PAGES")
        self.assertEqual(set(pages), {"core1.html", "index.html"})
        self.assertEqual(gaps, [])
        self.assertIn("MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE", pages["core1.html"])
        self.assertIn('data-g9-meta-value="HARD"', pages["core1.html"])
        self.assertIn("5(+2) = +10 N", pages["core1.html"])
        learner_surface = pages["core1.html"] + pages["index.html"]
        self.assertNotIn("LP-H1", learner_surface)
        self.assertNotIn("interaction value", learner_surface.lower())
        self.assertNotIn("Q-PHY-NLM-MTR-2A-", learner_surface)
        self.assertNotIn("Q-PHY-NLM-MTR-2B-", learner_surface)
        for role in product_manifest.OUTPUT_ROLES[1:]:
            filename = render_core.ROLE_FILE[role]
            self.assertNotIn(filename, pages)
            self.assertNotIn(f'href="{filename}"', pages["core1.html"])
            self.assertNotIn(f'href="{filename}"', pages["index.html"])

    def test_single_file_contains_only_zero_gap_declared_first_stage_role(self):
        pages, gaps, _digest = render_core.build(self.PILOT, mode="SINGLE_FILE")
        self.assertEqual(set(pages), {"product.html"})
        self.assertEqual(gaps, [])
        html = pages["product.html"]
        self.assertIn('id="g9-role-CORE1"', html)
        self.assertIn('href="#g9-role-CORE1"', html)
        self.assertIn("5(+2) = +10 N", html)
        self.assertNotIn("LP-H1", html)
        self.assertNotIn("Q-PHY-NLM-MTR-2A-", html)
        self.assertNotIn("Q-PHY-NLM-MTR-2B-", html)
        for role in product_manifest.OUTPUT_ROLES[1:]:
            self.assertNotIn(f'id="g9-role-{role}"', html)
            self.assertNotIn(f'href="#g9-role-{role}"', html)

    def test_bank_first_route_can_emit_core2_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._scoped_manifest(self.BANK_FIRST, ["CORE2"], tmp)
            pages, gaps, _digest = render_core.build(path, mode="PAGES")
        self.assertEqual(set(pages), {"core2.html", "index.html"})
        self.assertIn("PYQ-PHY-IITJEE-2007-P1-Q03", pages["core2.html"])
        self.assertIn('href="core2.html"', pages["index.html"])
        for role in product_manifest.OUTPUT_ROLES:
            if role == "CORE2":
                continue
            filename = render_core.ROLE_FILE[role]
            self.assertNotIn(filename, pages)
            self.assertNotIn(f'href="{filename}"', pages["core2.html"])
            self.assertNotIn(f'href="{filename}"', pages["index.html"])
        self.assertTrue(all(gap["core"] in {"CORE2", "INDEX"} for gap in gaps), gaps)

    def test_bank_first_single_file_contains_only_core2(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._scoped_manifest(self.BANK_FIRST, ["CORE2"], tmp)
            pages, gaps, _digest = render_core.build(path, mode="SINGLE_FILE")
        self.assertEqual(set(pages), {"product.html"})
        html = pages["product.html"]
        self.assertIn('id="g9-role-CORE2"', html)
        self.assertIn('href="#g9-role-CORE2"', html)
        for role in product_manifest.OUTPUT_ROLES:
            if role == "CORE2":
                continue
            self.assertNotIn(f'id="g9-role-{role}"', html)
            self.assertNotIn(f'href="#g9-role-{role}"', html)
        self.assertTrue(all(gap["core"] == "CORE2" for gap in gaps), gaps)

    def test_build_pipeline_exercises_zero_gap_scoped_browser_and_pdf_path_without_turning_quality_into_a_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = ("WORK", "PUBLIC", "STANDALONE_WORK", "STANDALONE", "REVIEWS", "ACCEPTANCE")
            original = {name: getattr(build_products, name) for name in names}
            try:
                build_products.WORK = root / "publication/products"
                build_products.PUBLIC = root / "public/products"
                build_products.STANDALONE_WORK = root / "publication/standalone/products"
                build_products.STANDALONE = root / "standalone/products"
                build_products.REVIEWS = root / "products/verification"
                build_products.ACCEPTANCE = root / "products/acceptance"
                row = build_products.build_one(self.PILOT, static=False)
                out = build_products.WORK / "physics/phy-nlm-momentum-transfer"
                receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
                print_receipt = json.loads((out / "print-receipt.json").read_text(encoding="utf-8"))
                report = json.loads((out / "gate-report.json").read_text(encoding="utf-8"))
                standalone = build_products.STANDALONE_WORK / "physics/phy-nlm-momentum-transfer.html"
                standalone_text = standalone.read_text(encoding="utf-8")
                pdf_present = (out / "core1.pdf").is_file()
                from pypdf import PdfReader
                pdf_text = [page.extract_text() for page in PdfReader(out / "core1.pdf").pages]
            finally:
                for name, value in original.items():
                    setattr(build_products, name, value)
        self.assertEqual(receipt["pages"], ["core1.html", "index.html"])
        self.assertEqual(receipt["output_roles"], ["CORE1"])
        self.assertEqual(receipt["gaps"], [])
        self.assertEqual(row["gaps"], 0)
        self.assertEqual(print_receipt["mode"], "LEARNER_PDF")
        self.assertEqual([page["page"] for page in print_receipt["pages"]], ["core1.html"])
        self.assertTrue(pdf_present)
        self.assertIn("Governing relation", pdf_text[0], "the title must not consume an otherwise empty page")
        anchor_page = next(text for text in pdf_text if "Compact anchor" in text)
        self.assertIn("5", anchor_page.split("Compact anchor", 1)[1], "keep the anchor heading with its example")
        self.assertTrue(report["rendered_measured"])
        self.assertEqual(report["not_measured"], [])
        self.assertIn('id="g9-role-CORE1"', standalone_text)
        self.assertNotIn('id="g9-role-CORE1A"', standalone_text)
        self.assertIn("5(+2) = +10 N", standalone_text)
        self.assertNotIn("LP-H1", standalone_text)
        self.assertNotIn("Q-PHY-NLM-MTR-2A-", standalone_text)
        self.assertNotIn("Q-PHY-NLM-MTR-2B-", standalone_text)
        self.assertEqual(row["product"], "phy-nlm-momentum-transfer")
        self.assertEqual(report["verdict"], "FAIL")
        finding_rules = {finding["rule"] for finding in report["findings"]}
        self.assertIn("C1-REPRESENTATION", finding_rules)
        self.assertNotIn("PRODUCT-ALL-ROLES", finding_rules)

    def test_legacy_renderer_still_emits_all_six_roles_when_scope_is_absent(self):
        manifest = json.loads(self.PILOT.read_text(encoding="utf-8"))
        manifest.pop("output_roles")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy-manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            pages, _gaps, _digest = render_core.build(path, mode="PAGES")
        expected = {render_core.ROLE_FILE[role] for role in render_core.ROLES} | {"index.html"}
        self.assertEqual(set(pages), expected)


if __name__ == "__main__":
    unittest.main()
