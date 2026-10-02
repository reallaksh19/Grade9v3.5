#!/usr/bin/env python3
"""Run the unittest suite and write what failed, by test id, for diff_test_failures.py.

    python3 Shared/tools/run_test_ids.py --output head.json [--start-dir tests] [--pattern 'test_*.py']

Run it from the root of the tree under test, so that one copy of this tool can measure the merge base as well as HEAD.

The record is {"ran": N, "failed": [ids], "load_errors": [ids]}. A module that does not import is a load error, not a quiet absence: a suite that
cannot be loaded has not passed, and the comparison treats it as the failure it is. The exit status is 0 whenever the run itself completed, so that the
comparison, and not this step, decides what a failure means.
"""
from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path


def flatten(suite: unittest.TestSuite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def run(start_dir: str, pattern: str) -> dict:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir, pattern=pattern)
    load_errors = sorted(t.id() for t in flatten(suite) if t.__class__.__name__ == "_FailedTest")
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=0, buffer=True).run(suite)
    failed = sorted({t.id() for t, _ in result.failures + result.errors})
    return {"ran": result.testsRun, "failed": failed, "load_errors": load_errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", required=True)
    parser.add_argument("--start-dir", default="tests")
    parser.add_argument("--pattern", default="test_*.py")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(Path.cwd()))
    record = run(args.start_dir, args.pattern)
    Path(args.output).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ran {record['ran']}; failed {len(record['failed'])}; load errors {len(record['load_errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
