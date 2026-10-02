#!/usr/bin/env python3
"""The tests that fail at HEAD and did not fail at the merge base, by id.

    python3 Shared/tools/diff_test_failures.py --base base.json --head head.json [--enforce]

Both files are written by run_test_ids.py. A count does not decide: one test fixed and another broken is the same count and a regression. Nor does an
absence: a head that ran no tests, or whose modules did not load, has not passed, so those fail the comparison instead of reading as "no new failures".
A test that failed at the base and fails at HEAD is not new; it is listed so that it is not forgotten.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(path: str) -> dict:
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
        return {"ran": int(record["ran"]), "failed": set(record["failed"]), "load_errors": set(record["load_errors"])}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(f"{path}: not a run_test_ids.py record ({type(exc).__name__}: {exc})")


def compare(base: dict, head: dict) -> dict:
    infrastructure = []
    if head["ran"] == 0:
        infrastructure.append("HEAD ran no tests")
    infrastructure += [f"does not load at HEAD: {t}" for t in sorted(head["load_errors"] - base["load_errors"])]
    return {"new": sorted(head["failed"] - base["failed"]), "fixed": sorted(base["failed"] - head["failed"]),
            "still_failing": sorted(head["failed"] & base["failed"]), "infrastructure": infrastructure}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)
    result = compare(load(args.base), load(args.head))
    for label in ("infrastructure", "new", "fixed"):
        for item in result[label]:
            print(f"{label.upper()}: {item}")
    print(f"new {len(result['new'])}; fixed {len(result['fixed'])}; still failing (not new) {len(result['still_failing'])}")
    return 1 if args.enforce and (result["new"] or result["infrastructure"]) else 0


if __name__ == "__main__":
    sys.exit(main())
