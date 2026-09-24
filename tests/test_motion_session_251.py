import os
import shutil
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class MotionSession251BrowserRuntimeTest(unittest.TestCase):
    def test_motion_session_browser_and_trace_contract(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required for the Issue #251 Motion session proof")

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
                self.fail("GitHub Actions Issue #251 Motion session proof requires ChromeDriver")
            self.skipTest("ChromeDriver is not available")

        result = subprocess.run(
            [node, "--test", str(REPO / "tests/motion_session_251.test.mjs")],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
