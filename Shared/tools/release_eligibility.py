#!/usr/bin/env python3
"""Release eligibility verifier."""

import sys
import json
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

def load_and_check(bundle_path: str, product_id: str) -> dict:
    with Path(bundle_path).open("r", encoding="utf-8") as f:
        bundle = json.load(f)

    if bundle.get("subject", {}).get("id") != product_id:
        print("Bundle subject ID does not match product ID")
        sys.exit(1)

    policy_path = REPO / "Shared" / "assurance" / "policies" / "canonical-admission.v1.json"
    policy = {}
    if policy_path.exists():
        with policy_path.open("r", encoding="utf-8") as f:
            policy = json.load(f)
    req_pass = policy.get("required_pass", [])

    missing_types = bundle.get("missing_types", [])
    hard_integrity = "PASS"
    reviewable_findings = []

    evidence_dir = REPO / "Shared" / "assurance" / "evidence"
    for e_id in bundle.get("evidence_ids", []):
        ev_file = evidence_dir / f"{e_id}.json"
        if ev_file.exists():
            with ev_file.open("r", encoding="utf-8") as f:
                ev = json.load(f)
                
                # Check outcome and severity on evidence level
                outcome = ev.get("outcome", "")
                sev = ev.get("severity", "")
                assurance_type = ev.get("assurance_type", "")

                if outcome == "FAIL" and sev in ("S0", "S1"):
                    hard_integrity = "FAIL"
                
                if assurance_type in req_pass and outcome in ("NOT_RUN", "INCONCLUSIVE"):
                    hard_integrity = "FAIL"

                for finding in ev.get("findings", []):
                    # For backwards compat or findings that still have severity
                    f_sev = finding.get("severity", "")
                    if f_sev in ("S0", "S1"):
                        hard_integrity = "FAIL"
                    elif f_sev in ("S2", "S3"):
                        reviewable_findings.append(finding)

    if hard_integrity == "FAIL":
        status = "INELIGIBLE"
    elif missing_types:
        status = "INCOMPLETE"
    else:
        status = "ELIGIBLE"

    return {
        "schema_version": "release-eligibility/v1",
        "product_id": product_id,
        "status": status,
        "hard_integrity": hard_integrity,
        "missing_types": missing_types,
        "reviewable_findings": reviewable_findings
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", type=str, required=True)
    parser.add_argument("--bundle", type=str, required=True)
    parser.add_argument("--canonical-digest", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    record = load_and_check(args.bundle, args.product_id)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, sort_keys=True)

    status = record["status"]
    print(f"Eligibility Decision: {status}")
    if args.enforce and status != "ELIGIBLE":
        sys.exit(1)

if __name__ == "__main__":
    main()
