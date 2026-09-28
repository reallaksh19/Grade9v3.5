"""Structural and render-basis regressions exposed by the Polynomials draft."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import accept_product, render_core


REPO = Path(__file__).resolve().parents[1]
NLM = REPO / "products/physics/phy-nlm-first-law.manifest.json"


class ProductBlueprintSafety(unittest.TestCase):
    def test_malformed_representation_refuses_draft_render(self):
        manifest = json.loads(NLM.read_text(encoding="utf-8"))
        package = json.loads((REPO / manifest["package_refs"][0]).read_text(encoding="utf-8"))
        package["representations"][0]["title"] = "field outside the package schema"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package_path = root / "package.json"
            package_path.write_text(json.dumps(package), encoding="utf-8")
            manifest["package_refs"] = [str(package_path)]
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PRODUCT_STRUCTURE_INVALID.*representations"):
                render_core.context(manifest_path)

    def test_unknown_custody_is_not_labelled_official(self):
        self.assertEqual(render_core._custody({"extensions": {}}), "Source unverified")
        self.assertEqual(render_core._custody({"extensions": {"grade9v3:source_custody": {
            "authority_class": "OFFICIAL_EXAM_ORGANIZER_ARCHIVE",
            "source_status": "PYQ_VERIFIED_PARENT",
            "paper_url": "https://example.org/paper.pdf",
        }}}), "Official past paper")

    def test_renderer_cannot_write_directly_to_public(self):
        target = REPO / "public" / "blueprint-safety-probe"
        self.assertFalse(target.exists())
        with self.assertRaisesRegex(ValueError, "cannot write to public"):
            render_core.main(["build", "--manifest", str(NLM), "--out", str(target), "--draft"])
        self.assertFalse(target.exists())

    def test_acceptance_rechecks_current_render_basis(self):
        pages, gaps, digest = render_core.build(NLM, mode="PAGES")
        self.assertFalse(gaps)
        receipt = {"renderer": render_core.RENDERER_VERSION, "digest": digest,
                   "gaps": gaps, "pages": sorted(pages),
                   "semantic_digest": render_core.semantic_metadata_digest(pages, "PAGES")}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for name, page in pages.items():
                (folder / name).write_bytes(page.encode("utf-8"))
            accept_product.verify_current_basis(folder, NLM, receipt)
            changed = dict(pages)
            changed["core1.html"] += "changed source"
            with mock.patch.object(render_core, "build", return_value=(changed, gaps, digest)):
                with self.assertRaisesRegex(ValueError, "differs from the current renderer"):
                    accept_product.verify_current_basis(folder, NLM, receipt)


if __name__ == "__main__":
    unittest.main()
