from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import build_products, render_core


REPO = Path(__file__).resolve().parents[1]


class ProductStandaloneContractTest(unittest.TestCase):
    def test_single_file_mode_is_self_contained_for_nlm_pilot(self):
        manifest = REPO / "products" / "physics" / "phy-nlm-first-law.manifest.json"
        ctx = render_core.context(manifest)
        labels = {label for label, _digest in ctx.authority_hashes}
        self.assertIn("learner-metadata-source", labels)
        self.assertIn("learner-metadata-vocabulary", labels)
        pages, gaps, digest = render_core.build(manifest, mode="SINGLE_FILE")
        self.assertEqual(gaps, [])
        self.assertEqual(set(pages), {"product.html"})
        html = pages["product.html"]
        self.assertIn(f"render_core/2 {digest}", html)
        self.assertIn('data-g9-mode="SINGLE_FILE"', html)
        self.assertIn('data-g9-tablet-shell', html)
        self.assertNotRegex(html, r'<script\b[^>]*\bsrc="https?://')
        self.assertNotRegex(html, r'<link\b[^>]*\bhref="https?://')
        self.assertNotIn('href="core1.html"', html)
        self.assertNotIn('href="core2a.html"', html)
        self.assertIn('href="../../../public/index.html"', html)
        self.assertIn('href="../../../public/question-bank/index.html"', html)
        for role in render_core.ROLES:
            self.assertIn(f'id="g9-role-{role}"', html)
            self.assertIn(f'href="#g9-role-{role}"', html)

    def test_pages_and_single_file_have_distinct_exact_identity_but_equal_metadata_semantics(self):
        manifest = REPO / "products" / "physics" / "phy-nlm-first-law.manifest.json"
        pages, page_gaps, page_digest = render_core.build(manifest, mode="PAGES")
        single, single_gaps, single_digest = render_core.build(manifest, mode="SINGLE_FILE")
        self.assertEqual(page_gaps, [])
        self.assertEqual(single_gaps, [])
        self.assertNotEqual(page_digest, single_digest)

        page_snapshot = render_core.semantic_metadata_snapshot(pages, "PAGES")
        single_snapshot = render_core.semantic_metadata_snapshot(single, "SINGLE_FILE")
        self.assertEqual(len(page_snapshot), 84)
        self.assertEqual(page_snapshot, single_snapshot)
        self.assertEqual(
            render_core.semantic_metadata_digest(pages, "PAGES"),
            render_core.semantic_metadata_digest(single, "SINGLE_FILE"),
        )
        self.assertIn(f"render_core/2 {page_digest}", pages["core1.html"])
        self.assertIn(f"render_core/2 {single_digest}", single["product.html"])

    def test_pass_status_rows_may_bind_one_generated_standalone_artifact(self):
        rows = json.loads((REPO / "products" / "status.v1.json").read_text(encoding="utf-8"))
        for row in rows:
            if row["verdict"] == "PASS":
                expected = f"standalone/products/{row['subject'].lower()}/{row['product']}.html"
                # Current committed status may predate this generator revision; the next full
                # build must fill the binding rather than allowing an arbitrary path.
                if row.get("standalone") is not None:
                    self.assertEqual(row["standalone"], expected)


if __name__ == "__main__":
    unittest.main()