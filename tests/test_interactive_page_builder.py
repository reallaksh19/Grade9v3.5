from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import build_interactive_page

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests/fixtures/workbench/core-learning-projections.json"


class InteractivePageBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(FIXTURE.read_text(encoding="utf-8"))["projections"]

    def row(self, core):
        projection = copy.deepcopy(next(row for row in self.rows if row["core"] == core))
        return {
            "id": f"fixture:{core.lower()}",
            "subject": "Fixture Subject",
            "source_ref": f"SOURCE-{core}",
            "projection": projection,
            "scene_ref": None,
            "adapter_ref": None,
            "injection_refs": [],
            "explorer_locator": None,
        }

    def test_package_uses_projection_blueprint_without_subject_switch(self):
        for core in ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"):
            package = build_interactive_page.compile_page_package(self.row(core))
            self.assertEqual(package["core"], core)
            self.assertEqual(
                package["blueprint"]["ref"],
                self.row(core)["projection"]["delivery"]["web"]["blueprint_ref"],
            )
            self.assertEqual(package["blueprint"]["touch_policy"]["minimum_target_css_px"], 48)

    def test_mismatched_blueprint_fails_closed(self):
        row = self.row("CORE2B")
        row["projection"]["delivery"]["web"]["blueprint_ref"] = "BP-WRONG@1.0.0"
        with self.assertRaisesRegex(
            build_interactive_page.InteractivePageBuildError,
            "WEB_BLUEPRINT_CORE_INCOMPATIBLE",
        ):
            build_interactive_page.compile_page_package(row)

    def test_existing_explorer_locator_is_explicit_legacy_migration_mode(self):
        row = self.row("CORE2A")
        row["explorer_locator"] = "public/example/explorer/index.html"
        package = build_interactive_page.compile_page_package(row)
        self.assertEqual(package["representation"]["mount_mode"], "LEGACY_IFRAME")
        self.assertEqual(
            package["blueprint"]["representation_policy"]["legacy_iframe"],
            "MIGRATION_ONLY",
        )

    def test_offline_directory_has_only_local_runtime_dependencies(self):
        package = build_interactive_page.compile_page_package(self.row("CORE1B"))
        rendered = build_interactive_page.render_offline_directory(package)
        self.assertEqual(
            set(rendered),
            {
                "index.html", "data.js", "runtime.mjs", "semantic-workbench.mjs",
                "core-learning-page.mjs", "core-learning-host.mjs",
                "interactive-page-package.json",
            },
        )
        html = rendered["index.html"].decode("utf-8")
        self.assertNotIn("https://", html)
        self.assertIn('src="./data.js"', html)
        self.assertIn('import "./core-learning-page.mjs"', html)

    def test_single_file_contains_no_network_or_external_script_dependency(self):
        package = build_interactive_page.compile_page_package(self.row("CORE2A"))
        html = build_interactive_page.render_single_file(package).decode("utf-8")
        self.assertIn('content="SINGLE_FILE"', html)
        self.assertNotIn("https://", html)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("fetch(", html)
        self.assertIn(package["blueprint"]["ref"], html)
        self.assertIn("URL.createObjectURL", html)
        self.assertIn("window.__interactivePageReady=true", html)

    def test_offline_shell_instantiates_declared_tablet_controls(self):
        package = build_interactive_page.compile_page_package(self.row("CORE2A"))
        html = build_interactive_page.render_offline_directory(package)["index.html"].decode("utf-8")
        self.assertIn('data-shell-ref="G9-TABLET-SHELL-V1"', html)
        for control in ("back", "home", "subject-context", "question-bank", "site-search", "refresh", "display-down", "display-up"):
            self.assertIn(f'id="{control}"', html)

    def test_public_pages_and_embed_modes_write_real_html_not_contract_only(self):
        package = build_interactive_page.compile_page_package(self.row("CORE2A"))
        for mode in ("PUBLIC", "PAGES", "EMBED"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / mode.lower()
                build_interactive_page.write_mode(package, mode, target)
                self.assertTrue((target / "index.html").is_file())
                html = (target / "index.html").read_text(encoding="utf-8")
                self.assertIn(f'content="{mode}"', html)
                self.assertTrue((target / "interactive-page-package.json").is_file())
                self.assertTrue((target / "agent-contract.json").is_file())

    def test_cli_writes_true_single_file(self):
        package = build_interactive_page.compile_page_package(self.row("CORE1A"))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "page.html"
            build_interactive_page.write_mode(package, "SINGLE_FILE", target)
            self.assertTrue(target.is_file())
            self.assertEqual(len(list(Path(tmp).iterdir())), 1)


if __name__ == "__main__":
    unittest.main()
