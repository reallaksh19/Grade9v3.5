import os
import shutil
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class ReadinessJoin215BrowserRuntimeTest(unittest.TestCase):
    def test_joined_atlas_core_portable_browser_contract(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required for the Issue #215 joined browser proof")

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
                self.fail("GitHub Actions Issue #215 joined browser proof requires ChromeDriver")
            self.skipTest("ChromeDriver is not available")

        result = subprocess.run(
            [node, "--test", str(REPO / "tests/readiness_join_215.test.mjs")],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
