"""The regression delta compares tests by id, and a suite that did not run is not a suite that passed."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import diff_test_failures  # noqa: E402

RUN = REPO / "Shared" / "tools" / "run_test_ids.py"


def record(failed=(), ran=10, load_errors=()):
    return {"ran": ran, "failed": set(failed), "load_errors": set(load_errors)}


class CompareTests(unittest.TestCase):
    def test_a_swap_is_a_regression_although_the_count_is_unchanged(self):
        result = diff_test_failures.compare(record(["a"]), record(["b"]))
        self.assertEqual((result["new"], result["fixed"]), (["b"], ["a"]))

    def test_a_failure_that_was_already_there_is_not_new(self):
        result = diff_test_failures.compare(record(["a"]), record(["a"]))
        self.assertEqual((result["new"], result["still_failing"]), ([], ["a"]))

    def test_a_head_that_ran_nothing_is_infrastructure_not_a_pass(self):
        self.assertTrue(diff_test_failures.compare(record(["a"]), record(ran=0))["infrastructure"])

    def test_a_module_that_stopped_loading_is_infrastructure(self):
        result = diff_test_failures.compare(record(), record(load_errors=["unittest.loader._FailedTest.test_x"]))
        self.assertEqual(len(result["infrastructure"]), 1)

    def test_a_module_that_never_loaded_is_not_blamed_on_this_change(self):
        self.assertEqual(diff_test_failures.compare(record(load_errors=["x"]), record(load_errors=["x"]))["infrastructure"], [])


class EndToEndTests(unittest.TestCase):
    """The two tools together, on a small tree with a failing test, a passing test and a module that does not import."""

    def run_tool(self, tree: Path, name: str) -> Path:
        out = tree / name
        subprocess.run([sys.executable, str(RUN), "--output", str(out)], cwd=tree, check=True, capture_output=True)
        return out

    def test_ids_are_recorded_and_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            (tree / "tests").mkdir()
            (tree / "tests" / "test_ok.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_a(self): pass\n")
            base = self.run_tool(tree, "base.json")
            (tree / "tests" / "test_bad.py").write_text("import unittest\nclass T(unittest.TestCase):\n    def test_b(self): self.fail('x')\n")
            (tree / "tests" / "test_broken.py").write_text("import not_a_module_anywhere\n")
            head = self.run_tool(tree, "head.json")
            recorded = json.loads(head.read_text())
            self.assertIn("test_bad.T.test_b", recorded["failed"])
            self.assertEqual(len(recorded["load_errors"]), 1)
            done = subprocess.run([sys.executable, str(REPO / "Shared/tools/diff_test_failures.py"), "--base", str(base), "--head", str(head), "--enforce"],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 1)
            self.assertIn("NEW: test_bad.T.test_b", done.stdout)
            self.assertIn("INFRASTRUCTURE", done.stdout)
            same = subprocess.run([sys.executable, str(REPO / "Shared/tools/diff_test_failures.py"), "--base", str(head), "--head", str(head), "--enforce"],
                                  capture_output=True, text=True)
            self.assertEqual(same.returncode, 0, same.stdout)


if __name__ == "__main__":
    unittest.main()
