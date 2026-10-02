#!/usr/bin/env python3
"""Run every verifier over the packages and projections and write the evidence: one record per (assurance type, subject), bound to what it judged.

    python3 Shared/tools/assurance_run.py --packages Physics/library Mathematics/library --projection standalone=standalone \\
        [--evidence-dir build/assurance/evidence] [--enforce]

CI mode (--enforce) fails the run on what must not get worse: a canonical finding that is not in the baseline of what was already there
(Shared/assurance/baseline.v1.json), and a projection page worse than its ledger (Shared/web/standalone-ledger.v1.json). Both are written by the tools, never by
hand (--write-baseline; standalone_conformance.py --write-ledger). The evidence is not softened by either: a known FAIL is still a FAIL, and a product with one is not
eligible. INCONCLUSIVE and NOT_RUN never fail a run; they keep a product from being released (release_eligibility.py).
Evidence is written outside the trees it judges, and the directory is emptied first so that it holds exactly this run.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import baseline, verifiers  # noqa: E402

DEFAULT_PACKAGES = ["Physics/library", "Mathematics/library", "Chemistry/library"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packages", nargs="+", default=None, help="package files or directories, relative to the repository (default: the subject libraries that hold packages)")
    parser.add_argument("--projection", action="append", default=[], metavar="ID=PATH")
    parser.add_argument("--evidence-dir", default="build/assurance/evidence")
    parser.add_argument("--keep", action="store_true", help="do not empty the evidence directory first")
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--baseline", default=str(baseline.BASELINE.relative_to(REPO)))
    parser.add_argument("--write-baseline", action="store_true", help="record the canonical findings of this run as the baseline")
    args = parser.parse_args(argv)

    packages = args.packages or [p for p in DEFAULT_PACKAGES if any((REPO / p).glob("*.json"))]
    result = verifiers.run(REPO, packages, args.projection, REPO / args.evidence_dir, clean=not args.keep)

    table: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for (t, outcome), n in result.by_outcome().items():
        table[t][outcome] = n
    print(f"{len(result.evidence)} evidence record(s) in {args.evidence_dir}")
    for t in sorted(table):
        print(f"  {t:<30} " + "  ".join(f"{o} {n}" for o, n in sorted(table[t].items())))
    path = REPO / args.baseline
    if args.write_baseline:
        baseline.write(baseline.keys(result.evidence), path)
        print(f"baseline written: {len(baseline.keys(result.evidence))} known canonical finding(s) in {args.baseline}")
        return 0
    known = baseline.load(path)
    new = baseline.new_findings(result.evidence, known)
    for k in new[:20]:
        print("NEW FINDING:", k)
    for k in baseline.fixed(result.evidence, known)[:10]:
        print("FIXED (tighten the baseline):", k)
    for line in result.ratchet_problems[:20]:
        print("WORSE THAN THE LEDGER:", line)
    print(f"known canonical findings: {len(baseline.keys(result.evidence)) - len(new)}; new: {len(new)}; pages worse than the ledger: {len(result.ratchet_problems)}")
    return 1 if (args.enforce and (new or result.ratchet_problems)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
