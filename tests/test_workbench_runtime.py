import os
import shutil
import subprocess
import unittest
from pathlib import Path

from Shared.tools import build_manifest

REPO = Path(__file__).resolve().parents[1]


class WorkbenchRuntimeNodeTests(unittest.TestCase):
    def test_node_runtime_contract(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required by existing browser-runtime CI and the workbench contract tests")
        result = subprocess.run(
            [node, "--test", str(REPO / "tests/workbench_runtime.test.mjs")],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_real_browser_contract(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required by the workbench browser contract test")
        configured = os.environ.get("CHROMEWEBDRIVER")
        driver = None
        if configured:
            candidate = Path(configured)
            if candidate.is_file():
                driver = candidate
            elif (candidate / "chromedriver").is_file():
                driver = candidate / "chromedriver"
        if driver is None:
            executable = shutil.which("chromedriver")
            driver = Path(executable) if executable else None
        if driver is None:
            if os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("GitHub Actions browser proof requires the runner ChromeDriver")
            self.skipTest("ChromeDriver is not available in this local environment")

        result = subprocess.run(
            [node, "--test", str(REPO / "tests/workbench_browser.test.mjs")],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_manifest_classifies_workbench_es_modules(self):
        runtime = REPO / "Shared/workbench/runtime.mjs"
        role = build_manifest.classify(runtime)
        self.assertIsNotNone(role)
        self.assertEqual(role[0], "WEB_RUNTIME")
        self.assertIn("Shared/workbench/runtime.mjs", {row["path"] for row in build_manifest.collect()["components"]})


if __name__ == "__main__":
    unittest.main()
