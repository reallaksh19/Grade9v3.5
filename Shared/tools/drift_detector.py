#!/usr/bin/env python3
"""Drift classification per spec 33-34."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.release_fingerprint import build_fingerprint
from Shared.tools.assurance_record import make_evidence


class DummyArgs:
    def __init__(self, product_id, canonical_dir, web_dir, standalone_dir, search_index, search_manifest, assurance_bundle):
        self.product_id = product_id
        self.canonical_dir = canonical_dir
        self.web_dir = web_dir
        self.standalone_dir = standalone_dir
        self.search_index = search_index
        self.search_manifest = search_manifest
        self.assurance_bundle = assurance_bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-fingerprint", required=True)
    parser.add_argument("--canonical-dir", required=True)
    parser.add_argument("--web-dir", default="")
    parser.add_argument("--standalone-dir", default="")
    parser.add_argument("--search-index", default="")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    with Path(args.accepted_fingerprint).open("r", encoding="utf-8") as f:
        accepted = json.load(f)

    # Re-calculate current fingerprint
    dummy = DummyArgs(
        product_id=accepted.get("product", "unknown"),
        canonical_dir=args.canonical_dir,
        web_dir=args.web_dir,
        standalone_dir=args.standalone_dir,
        search_index=args.search_index,
        search_manifest=None,
        assurance_bundle=None
    )
    current = build_fingerprint(dummy)

    drifts = {}
    
    # Check canonical
    if current.get("canonical_snapshot_digest") != accepted.get("canonical_snapshot_digest"):
        drifts["canonical_snapshot"] = "REQUIRES_REBUILD"
    else:
        drifts["canonical_snapshot"] = "CURRENT"

    # Check policy
    if current.get("policy_digest") != accepted.get("policy_digest"):
        drifts["policy"] = "REQUIRES_REASSURANCE"
    else:
        drifts["policy"] = "CURRENT"

    # Check projections
    for proj in ["web_projection", "standalone_projection", "search_projection"]:
        accepted_dig = accepted.get(f"{proj}_digest")
        if not accepted_dig:
            drifts[proj] = "CURRENT"
            continue
            
        current_dig = current.get(f"{proj}_digest")
        if current_dig != accepted_dig:
            drifts[proj] = "REQUIRES_REBUILD"
        else:
            drifts[proj] = "CURRENT"

    # UNAUTHORIZED override: projection changed but canonical didn't
    canonical_current = drifts["canonical_snapshot"] == "CURRENT"
    has_unauthorized = False
    
    for proj in ["web_projection", "standalone_projection", "search_projection"]:
        if drifts[proj] == "REQUIRES_REBUILD" and canonical_current:
            drifts[proj] = "UNAUTHORIZED"
            has_unauthorized = True

    print(f"{'canonical_snapshot':<20} {drifts['canonical_snapshot']}")
    for proj in ["web_projection", "standalone_projection", "search_projection"]:
        name = proj.replace("_projection", "")
        print(f"{name:<20} {drifts[proj]}")

    outcome = "PASS"
    if has_unauthorized:
        outcome = "FAIL"
    elif any(d == "REQUIRES_REBUILD" for d in drifts.values()):
        outcome = "INCONCLUSIVE"
    elif any(d == "REQUIRES_REASSURANCE" for d in drifts.values()):
        outcome = "INCONCLUSIVE"

    evidence = make_evidence(
        assurance_type="DEPLOYMENT_INTEGRITY",
        subject_kind="RELEASE_FINGERPRINT",
        subject_id=accepted.get("product", "unknown"),
        outcome=outcome,
        producer_name="drift_detector",
        producer_version="1.0"
    )
    
    # Just printing the evidence for debug could be helpful but not strictly required unless instructed.
    if args.enforce and outcome == "FAIL":
        sys.exit(1)

if __name__ == "__main__":
    main()
