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

    def test_generated_html_links_do_not_escape_docs_root(self):
        desired = build_pages_site.desired_files(REPO)
        self.assertEqual(build_pages_site.link_findings(desired), [])


if __name__ == "__main__":
    unittest.main()
