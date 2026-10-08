from __future__ import annotations

import unittest
from pathlib import Path

from Shared.tools import build_pages_site


REPO = Path(__file__).resolve().parents[1]


class PagesSiteTest(unittest.TestCase):
    def test_committed_pages_mirror_is_current(self):
        self.assertEqual(build_pages_site.check(REPO), [])

    def test_pages_root_contains_prompt_composer_and_run_builder(self):
        desired = build_pages_site.desired_files(REPO)
        for target in (
            "index.html",
            "core-prompt-composer/index.html",
            "tools/index.html",
            "tools/app.css",
            "tools/library/index.html",
            "tools/run-builder/index.html",
            "tools/data.js",
            ".nojekyll",
            ".pages-manifest.json",
        ):
            self.assertIn(target, desired)

    def test_pages_rewrites_keep_run_builder_inside_project_site(self):
        desired = build_pages_site.desired_files(REPO)
        composer = desired["core-prompt-composer/index.html"][1].decode("utf-8")
        atlas = desired["js/topic-atlas.js"][1].decode("utf-8")
        self.assertIn('href="../tools/run-builder/index.html"', composer)
        self.assertNotIn('href="../../tools/run-builder/index.html"', composer)
        self.assertIn('href="../../tools/run-builder/index.html"', atlas)
        self.assertNotIn('href="../../../tools/run-builder/index.html"', atlas)

    def test_html_entities_are_decoded_for_official_links_and_traversal(self):
        official = {"test/index.html": ("public/test/index.html",
                    b'<a href="https&#58;//ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf">NCERT</a>')}
        self.assertEqual(build_pages_site.link_findings(official), [])
        escape = {"test/index.html": ("public/test/index.html",
                  b'<a href="&#46;&#46;/&#46;&#46;/&#46;&#46;/outside.html">escape</a>')}
        self.assertTrue(any("link escapes docs/ Pages root" in reason
                            for reason in build_pages_site.link_findings(escape)))
        with self.assertRaisesRegex(ValueError, "unapproved external runtime dependency"):
            build_pages_site._public_payload(
                "test/index.html",
                b'<script src="https&#58;//cdn.example.invalid/payload.js"></script>',
            )

    def test_generated_html_links_do_not_escape_docs_root(self):
        desired = build_pages_site.desired_files(REPO)
        self.assertEqual(build_pages_site.link_findings(desired), [])

    def test_publication_rewrites_tailwind_and_katex_to_local_runtime(self):
        relative = "physics/deep/explorer/index.html"
        source = b"""<!doctype html><html><head>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
</head><body></body></html>"""
        out = build_pages_site._public_payload(relative, source).decode("utf-8")
        self.assertIn('../../../vendor/tailwind/3.4.17/tailwind-play.js', out)
        self.assertIn('../../../vendor/katex/0.16.8/katex.min.css', out)
        self.assertIn('../../../vendor/katex/0.16.8/katex.min.js', out)
        self.assertNotIn("https://cdn.tailwindcss.com", out)
        self.assertNotIn("https://cdn.jsdelivr.net", out)

    def test_publication_rewrites_legacy_gstatic_tailwind_runtime(self):
        out = build_pages_site._public_payload(
            "physics/motion-in-2d/explorers/x/index.html",
            b'<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>',
        ).decode("utf-8")
        self.assertIn('../../../../vendor/tailwind/3.4.17/tailwind-play.js', out)
        self.assertNotIn("gstatic.com", out)

    def test_publication_fails_closed_on_unknown_external_runtime(self):
        with self.assertRaisesRegex(ValueError, "unapproved external runtime dependency"):
            build_pages_site._public_payload(
                "physics/x/index.html",
                b'<script src="https://cdn.example.invalid/new-runtime.js"></script>',
            )
        with self.assertRaisesRegex(ValueError, "unapproved external runtime dependency"):
            build_pages_site._public_payload(
                "physics/x/index.html",
                b'<link rel="stylesheet" href="https://cdn.example.invalid/new.css">',
            )

    def test_tailwind_vendor_snapshot_is_versioned_and_declared(self):
        runtime = REPO / "public" / "vendor" / "tailwind" / "3.4.17" / "tailwind-play.js"
        readme = (REPO / "public" / "vendor" / "README.md").read_text(encoding="utf-8")
        self.assertTrue(runtime.is_file())
        self.assertIn("3.4.17", runtime.read_text(encoding="utf-8"))
        self.assertIn("20fda8a2158e83d6f78aa7e614ec1f7183ac10423cf956ded061cbe664c87bef", readme)
        self.assertTrue((runtime.parent / "LICENSE").is_file())


if __name__ == "__main__":
    unittest.main()