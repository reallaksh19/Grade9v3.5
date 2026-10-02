#!/usr/bin/env python3
"""Release eligibility verifier."""

import sys
import json
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", type=str, required=True)
    parser.add_argument("--bundle", type=str, required=True)
    parser.add_argument("--canonical-digest", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    with Path(args.bundle).open("r", encoding="utf-8") as f:
        bundle = json.load(f)

    if bundle.get("subject", {}).get("id") != args.product_id:
        print("Bundle subject ID does not match product ID")
        sys.exit(1)
        
    missing_types = bundle.get("missing_types", [])
    
    hard_integrity = "PASS"
    reviewable_findings = []
    
    evidence_dir = REPO / "Shared" / "assurance" / "evidence"
    for e_id in bundle.get("evidence_ids", []):
        ev_file = evidence_dir / f"{e_id}.json"
        if ev_file.exists():
            with ev_file.open("r", encoding="utf-8") as f:
                ev = json.load(f)
                for finding in ev.get("findings", []):
                    sev = finding.get("severity", "")
                    if sev in ("S0", "S1"):
                        hard_integrity = "FAIL"
                    elif sev in ("S2", "S3"):
                        reviewable_findings.append(finding)
    
    if hard_integrity == "FAIL":
        status = "INELIGIBLE"
    elif missing_types:
        status = "INCOMPLETE"
    else:
        status = "ELIGIBLE"
        
    record = {
        "schema_version": "release-eligibility/v1",
        "product_id": args.product_id,
        "status": status,
        "hard_integrity": hard_integrity,
        "missing_types": missing_types,
        "reviewable_findings": reviewable_findings
    }
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, sort_keys=True)
            
    print(f"Eligibility Decision: {status}")
    if args.enforce and status != "ELIGIBLE":
        sys.exit(1)

if __name__ == "__main__":
    main()
