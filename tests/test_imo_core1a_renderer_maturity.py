"""Canonical Core1A renderer pilot: deterministic TEST-only outputs, no source admission.

This test deliberately uses the real manifest and sole shared renderer, not the
manual public/test/imo-grade9/core1a.html preview. It is reusable as a pattern
for future subject-neutral Core authors, never a new acceptance gate.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import product_coverage, product_manifest, render_core

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "TEST/products/core1a-divisibility-render-maturity.manifest.json"
PACKAGE = ROOT / "TEST/library/imo-g9-divisibility-core1a.v1.json"
MICRO = "MIC-TEST-IMO-G9-CONSECUTIVE-FACTOR-INVARIANTS"


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class Core1ARendererMaturityTests(unittest.TestCase):
    def test_manifest_is_a_test_only_canonical_selection(self):
        m = json.loads(MANIFEST.read_text(encoding="utf-8"))
        pkg = json.loads(PACKAGE.read_text(encoding="utf-8"))
        self.assertEqual(m["schema"], "product-manifest/v1")
        self.assertEqual(m["subject"], "TEST")
        self.assertEqual(m["output_roles"], ["CORE1A"])
        self.assertEqual(m["package_refs"], ["TEST/library/imo-g9-divisibility-core1a.v1.json"])
        self.assertEqual(m["bank_refs"], [])
        self.assertEqual(m["selection"], {
            "microtopics": [MICRO], "core2": [], "core2a": [], "core2b": [],
        })
        self.assertEqual(pkg["subject"], "TEST")
        self.assertEqual(pkg["status"], "CANDIDATE")
        self.assertEqual(pkg["questions"], [])
        self.assertEqual(pkg["extensions"]["grade9v3:core2_source_custody_granted"], False)
        self.assertEqual(pkg["extensions"]["grade9v3:learner_published"], False)
        self.assertEqual(pkg["extensions"]["grade9v3:qrt_admitted"], False)
        self.assertEqual(product_manifest.selected_output_roles(m), ["CORE1A"])
        product_coverage.validate(m, product_manifest.derivable([pkg], []))

    def test_real_renderer_pages_are_deterministic_and_role_scoped(self):
        one, gaps, render_digest, advice, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        two, gaps2, digest2, advice2, waivers2 = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE")
        self.assertEqual(one, two)
        self.assertEqual(gaps, gaps2)
        self.assertEqual(advice, advice2)
        self.assertEqual(waivers, waivers2)
        self.assertEqual(render_digest, digest2)
        self.assertEqual(set(one), {"index.html", "core1a.html"})
        html = one["core1a.html"]
        self.assertIn(MICRO, html)
        self.assertIn("CORE1A", html)
        self.assertIn("divisible by 6", html.lower())
        self.assertNotIn("data-g9-role=\"CORE2\"", html)
        self.assertNotIn("SOF-IMO-G09-L1", html)
        self.assertEqual(len(render_digest), 16)
        self.assertTrue(all({"core", "record", "duty", "detail"} <= set(g) for g in gaps))

    def test_actual_cli_stages_hashed_pages_with_honest_receipt(self):
        with tempfile.TemporaryDirectory() as staging:
            out = Path(staging)
            result = render_core.main([
                "build", "--manifest", str(MANIFEST), "--out", str(out),
                "--draft", "--reference",
            ])
            self.assertEqual(result, 0)
            self.assertEqual({p.name for p in out.glob("*.html")}, {"core1a.html", "index.html"})
            receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["output_roles"], ["CORE1A"])
            self.assertEqual(receipt["mode"], "PAGES")
            self.assertEqual(receipt["held_to"], "REFERENCE")
            self.assertEqual(receipt["renderer"], render_core.RENDERER_VERSION)
            self.assertEqual(set(receipt["pages"]), {"index.html", "core1a.html"})
            self.assertNotIn("accepted", receipt)  # renderer receipt is not owner acceptance
            self.assertEqual(receipt["draft"], bool(receipt["gaps"]))
            for name in receipt["pages"]:
                self.assertGreater(len((out / name).read_bytes()), 0)
            html_digest_before = {p.name: digest(p.read_bytes()) for p in out.glob("*.html")}
            result2 = render_core.main([
                "build", "--manifest", str(MANIFEST), "--out", str(out),
                "--draft", "--reference",
            ])
            self.assertEqual(result2, 0)
            self.assertEqual(
                html_digest_before,
                {p.name: digest(p.read_bytes()) for p in out.glob("*.html")},
            )

    def test_malformed_selection_refused_in_strict_and_draft_contexts(self):
        base = json.loads(MANIFEST.read_text(encoding="utf-8"))
        base["selection"]["microtopics"] = ["NONEXISTENT-CORE-MICROTOPIC"]
        with tempfile.TemporaryDirectory() as staging:
            bad = Path(staging) / "invalid.manifest.json"
            bad.write_text(json.dumps(base), encoding="utf-8")
            with self.assertRaisesRegex(
                product_manifest.ProductSelectionError, "PRODUCT_SELECTION_UNRESOLVED"
            ):
                render_core.build_report(bad, "PAGES", held_to="REFERENCE")


if __name__ == "__main__":
    unittest.main()
