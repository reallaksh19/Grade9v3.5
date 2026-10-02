#!/usr/bin/env python3
"""Bundle the evidence for a product: which assurance types hold for which subjects, and what is left open.

The bundle is facts, recomputed by anyone who reads it (Shared/assurance/aggregate.py). It names the subjects as they are now, the evidence about them
that is current, and every need the evidence leaves unsatisfied. With --enforce the exit status is 1 unless nothing is left open and no record is broken.

    python3 Shared/tools/assurance_product.py --product-id P --packages Physics/library --projection standalone=standalone \\
        --evidence-dir build/assurance/evidence --output build/assurance/P.bundle.json [--enforce]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import aggregate, contract  # noqa: E402

DEFAULT_EVIDENCE = "build/assurance/evidence"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--packages", nargs="+", required=True, help="package files, or directories of them, relative to the repository")
    parser.add_argument("--projection", action="append", default=[], metavar="ID=PATH", help="a projection (a directory of pages, or a file); repeatable")
    parser.add_argument("--evidence-dir", default=DEFAULT_EVIDENCE)
    parser.add_argument("--policy", action="append", default=None, metavar="ID", help="policy ids (default: canonical-admission-default, and learner-release-default when a projection is given)")
    parser.add_argument("--output")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)

    subjects = aggregate.package_subjects(args.packages) + aggregate.projection_subjects(args.projection)
    policy_ids = args.policy or ["canonical-admission-default"] + (["learner-release-default"] if args.projection else [])
    policies = aggregate.load_policies(policy_ids)
    records, problems = aggregate.collect(REPO / args.evidence_dir)
    ev = aggregate.evaluate(subjects, policies, records)
    ev.problems = problems + ev.problems
    bundle = aggregate.build_bundle(args.product_id, subjects, policies, ev)
    if args.output:
        contract.write_json(REPO / args.output, bundle)

    print(f"product {args.product_id}: {len(subjects)} subject(s), {len(bundle['evidence_refs'])} current evidence record(s)")
    print(f"snapshot {bundle['canonical_snapshot_digest']}")
    print(f"open needs: {len(bundle['missing'])}" + (f" ({', '.join(bundle['missing_types'])})" if bundle["missing_types"] else ""))
    for m in bundle["missing"][:12]:
        print(f"  {m['type']:<26} {m['subject']:<40} {m['reason']}")
    for p in bundle["problems"]:
        print(f"PROBLEM {p['code']}: {p['message']}")
    return 1 if (args.enforce and (bundle["missing"] or bundle["problems"] or ev.failing or ev.severe)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
