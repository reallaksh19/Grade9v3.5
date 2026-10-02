#!/usr/bin/env python3
"""The release decision for a product, recomputed from its bundle's evidence and from the subjects as they are now.

ELIGIBLE: nothing is open and no required check failed. INELIGIBLE: a required check failed, an S0 or S1 finding stands, or a record is broken
(evidence edited, missing or invalid; a bundle that is not what its evidence gives). INCOMPLETE: everything else: missing, stale, inconclusive,
not run. A waiver (--waivers) can satisfy only a required_pass_or_reviewed type, and says why and where it was approved.

    python3 Shared/tools/release_eligibility.py --product-id P --bundle build/assurance/P.bundle.json [--waivers W.json] [--output E.json] [--enforce]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import aggregate, contract  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402

DEFAULT_EVIDENCE = "build/assurance/evidence"


def load_and_check(bundle_path: str, product_id: str, evidence_dir: str = DEFAULT_EVIDENCE, waivers_path: str | None = None) -> dict:
    """The eligibility record for the bundle at `bundle_path`, or a ContractError: a bundle that is unreadable, invalid, or about another product."""
    try:
        bundle = json.loads(Path(bundle_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError("ASSURANCE_BUNDLE_UNREADABLE", f"{bundle_path}: {exc}") from exc
    contract.require_valid("bundle", bundle)
    if bundle["subject"]["id"] != product_id:
        raise ContractError("ASSURANCE_BUNDLE_OTHER_PRODUCT", f"the bundle is for {bundle['subject']['id']!r}, not {product_id!r}")
    policies = aggregate.load_policies(bundle["policies"])
    waivers = {**aggregate.default_waivers(), **aggregate.load_waivers(Path(waivers_path) if waivers_path else None)}
    return aggregate.evaluate_release(bundle, REPO / evidence_dir, policies, waivers)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--evidence-dir", default=DEFAULT_EVIDENCE)
    parser.add_argument("--waivers")
    parser.add_argument("--output")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)
    try:
        record = load_and_check(args.bundle, args.product_id, args.evidence_dir, args.waivers)
    except ContractError as exc:
        print(f"Eligibility Decision: INELIGIBLE ({exc})")
        return 1
    if args.output:
        contract.write_json(REPO / args.output, record)
    print(f"Eligibility Decision: {record['status']}")
    for m in record["missing"][:12]:
        print(f"  open     {m['type']:<26} {m['subject']:<40} {m['reason']}")
    for p in record["problems"]:
        print(f"  problem  {p['code']}: {p['message']}")
    waived: dict[str, int] = {}
    for w in record.get("waived", []):
        waived[w["type"]] = waived.get(w["type"], 0) + 1
    for t, n in sorted(waived.items()):
        print(f"  waived   {t:<26} {n} need(s), by the Owner's waiver")
    for f in record["reviewable_findings"][:8]:
        print(f"  finding  {f['severity']} {f['code']} {f['subject']}: {f['message'][:100]}")
    return 1 if (args.enforce and record["status"] != "ELIGIBLE") else 0


if __name__ == "__main__":
    raise SystemExit(main())
