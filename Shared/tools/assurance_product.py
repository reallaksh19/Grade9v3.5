#!/usr/bin/env python3
"""Product-level assurance aggregator."""

import sys
import json
import hashlib
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.assurance_record import make_evidence, write_evidence, load_policy, check_missing

def hash_dir(directory: Path) -> str:
    hashes = []
    if directory.exists():
        for p in sorted(directory.rglob("*")):
            if p.is_file():
                with p.open("rb") as f:
                    hashes.append(hashlib.sha256(f.read()).hexdigest())
    content = "".join(hashes).encode("utf-8")
    return hashlib.sha256(content).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", type=str, required=True)
    parser.add_argument("--canonical-dir", type=str, required=True)
    parser.add_argument("--output", type=str)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    canonical_dir = Path(args.canonical_dir)
    canonical_digest = hash_dir(canonical_dir)

    evidence_dir = REPO / "Shared" / "assurance" / "evidence"
    evidence_list = []
    if evidence_dir.exists():
        for p in evidence_dir.rglob("*.json"):
            try:
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("subject", {}).get("id") == args.product_id:
                        evidence_list.append(data)
            except Exception:
                pass

    policy_path = REPO / "Shared" / "assurance" / "policies" / "canonical-admission.v1.json"
    required_types = []
    if policy_path.exists():
        policy = load_policy(policy_path)
        required_types = policy.get("required_types", [])
        
    missing = check_missing(evidence_list, required_types)
    
    bundle = {
        "schema_version": "assurance-bundle/v1",
        "subject": {
            "kind": "product",
            "id": args.product_id,
            "digest": canonical_digest
        },
        "missing_types": missing,
        "evidence_ids": [ev.get("evidence_id") for ev in evidence_list if "evidence_id" in ev]
    }
    
    bundle_str = json.dumps(bundle, sort_keys=True).encode("utf-8")
    bundle["bundle_digest"] = hashlib.sha256(bundle_str).hexdigest()
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, sort_keys=True)
            
    print(f"Product ID: {args.product_id}")
    print(f"Canonical Digest: {canonical_digest}")
    print(f"Missing Types: {missing}")
    
    if args.enforce and missing:
        sys.exit(1)

if __name__ == "__main__":
    main()
