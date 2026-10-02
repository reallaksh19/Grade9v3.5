#!/usr/bin/env python3
"""Drift of the current state from an accepted release fingerprint.

For the canonical inputs and the policy: CURRENT, or REQUIRES_REBUILD / REQUIRES_REASSURANCE (they changed, which is allowed and means the release needs doing again).
For each projection: CURRENT, REQUIRES_REBUILD (it changed together with the canonical inputs), or UNAUTHORIZED (it changed and the canonical inputs did not: someone edited
a projection by hand, or built it from something other than the library). The evidence is DEPLOYMENT_INTEGRITY about the PRODUCT, bound to the digest of the current fingerprint:
FAIL for an unauthorized change, INCONCLUSIVE while a rebuild or a reassurance is owed, PASS when nothing drifted. With --enforce the exit status is 1 on FAIL only: a library
that changed is not a defect, a projection that changed without it is.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import contract  # noqa: E402
from Shared.assurance.evidence import finding, make_evidence, write_evidence  # noqa: E402
from Shared.tools.release_fingerprint import build_fingerprint  # noqa: E402

PROJECTIONS = ("web_projection", "standalone_projection", "search_projection")


def classify(accepted: dict, current: dict) -> dict[str, str]:
    drift = {"canonical_snapshot": "CURRENT" if current["canonical_snapshot_digest"] == accepted["canonical_snapshot_digest"] else "REQUIRES_REBUILD",
             "policy": "CURRENT" if current["policy_digest"] == accepted["policy_digest"] else "REQUIRES_REASSURANCE"}
    for name in PROJECTIONS:
        was, now = accepted.get(f"{name}_digest"), current.get(f"{name}_digest")
        drift[name] = "CURRENT" if (was is None or was == now) else "REQUIRES_REBUILD"
        if drift[name] == "REQUIRES_REBUILD" and drift["canonical_snapshot"] == "CURRENT":
            drift[name] = "UNAUTHORIZED"
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--accepted-fingerprint", required=True)
    parser.add_argument("--canonical-dir", required=True, nargs="+")
    parser.add_argument("--web-dir")
    parser.add_argument("--standalone-dir")
    parser.add_argument("--search-index")
    parser.add_argument("--evidence-dir", default="build/assurance/evidence")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)

    accepted = contract.require_valid("release-fingerprint", json.loads(Path(args.accepted_fingerprint).read_text(encoding="utf-8")))
    current = build_fingerprint(accepted["product"], [Path(d) for d in args.canonical_dir], Path(args.web_dir) if args.web_dir else None,
                                Path(args.standalone_dir) if args.standalone_dir else None, Path(args.search_index) if args.search_index else None)
    drift = classify(accepted, current)
    for name, state in drift.items():
        print(f"{name:<22} {state}")

    unauthorized = [n for n, s in drift.items() if s == "UNAUTHORIZED"]
    owed = [n for n, s in drift.items() if s.startswith("REQUIRES_")]
    outcome = "FAIL" if unauthorized else ("INCONCLUSIVE" if owed else "PASS")
    found = [finding("UNAUTHORIZED_CHANGE", "S1", n, f"{n} changed and the canonical inputs did not") for n in unauthorized]
    found += [finding("DRIFT_OWED", "S3", n, f"{n}: {drift[n]}") for n in owed]
    record = make_evidence("DEPLOYMENT_INTEGRITY", "PRODUCT", accepted["product"], outcome, "drift_detector", "1.1.0", findings=found,
                           subject_digest=contract.digest({k: v for k, v in current.items() if k != "fingerprinted_at"}), configuration={"accepted": contract.digest(accepted)})
    write_evidence(record, REPO / args.evidence_dir / f"{record['evidence_id']}.json")
    return 1 if (args.enforce and outcome == "FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main())
