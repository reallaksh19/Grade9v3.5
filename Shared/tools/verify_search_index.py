#!/usr/bin/env python3
"""Verifies the committed search index is consistent with the current canonical state."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.assurance_record import make_evidence, write_evidence


def compute_sha256_of_files(files: list[Path]) -> str:
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: str(x)):
        if f.is_file():
            h.update(f.read_bytes())
    return "sha256:" + h.hexdigest()

def compute_sha256_of_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--library-dirs", nargs="+", required=True)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    index_path = Path(args.index)
    manifest_path = Path(args.manifest)

    if not index_path.exists() or not manifest_path.exists():
        print("Missing index or manifest files.")
        if args.enforce:
            sys.exit(1)
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    indexed_ids = set(manifest.get("canonical_ids", []))
    manifest_index_digest = manifest.get("index_digest", "")
    manifest_canonical_digest = manifest.get("canonical_snapshot_digest", "")

    # 1. Load all canonical question IDs
    canonical_ids = set()
    canonical_files = []
    
    for d in args.library_dirs:
        dir_path = Path(d)
        if not dir_path.exists():
            continue
        for root, _, files in os.walk(dir_path):
            for file_name in files:
                if file_name.endswith(".json"):
                    filepath = Path(root) / file_name
                    canonical_files.append(filepath)
                    try:
                        with open(filepath, "r", encoding="utf-8") as file_obj:
                            data = json.load(file_obj)
                    except Exception:
                        continue
                    
                    if not isinstance(data, dict) or "questions" not in data:
                        continue
                    
                    for q in data["questions"]:
                        if q.get("extensions", {}).get("search_visibility") == "EXCLUDED":
                            continue
                        canonical_ids.add(q["id"])

    # 2. Check canonical staleness
    recomputed_canonical_digest = compute_sha256_of_files(canonical_files)
    is_stale = (recomputed_canonical_digest != manifest_canonical_digest)

    # 3. Check membership
    missing_from_index = canonical_ids - indexed_ids
    phantom_in_index = indexed_ids - canonical_ids

    membership_fail = bool(missing_from_index or phantom_in_index)
    
    membership_outcome = "PASS"
    if is_stale:
        membership_outcome = "INCONCLUSIVE"
    elif membership_fail:
        membership_outcome = "FAIL"

    membership_findings = []
    if missing_from_index:
        membership_findings.append({"missing": list(missing_from_index)})
    if phantom_in_index:
        membership_findings.append({"phantom": list(phantom_in_index)})

    membership_evidence = make_evidence(
        assurance_type="SEARCH_MEMBERSHIP",
        subject_kind="SEARCH_INDEX",
        subject_id=str(index_path.name),
        outcome=membership_outcome,
        producer_name="verify_search_index",
        producer_version="1.0.0",
        findings=membership_findings if membership_findings else None
    )

    # 4. Check retrievability
    with open(index_path, "rb") as f:
        index_bytes = f.read()
    
    recomputed_index_digest = compute_sha256_of_bytes(index_bytes)
    retrievability_outcome = "PASS" if recomputed_index_digest == manifest_index_digest else "FAIL"

    retrievability_evidence = make_evidence(
        assurance_type="SEARCH_RETRIEVABILITY",
        subject_kind="SEARCH_INDEX",
        subject_id=str(index_path.name),
        outcome=retrievability_outcome,
        producer_name="verify_search_index",
        producer_version="1.0.0"
    )

    # Output results
    print("=== Search Index Verification ===")
    print(f"Canonical staleness: {'STALE' if is_stale else 'CURRENT'}")
    print(f"Membership: {membership_outcome}")
    if membership_findings:
        print(f"  Missing: {len(missing_from_index)}")
        print(f"  Phantom: {len(phantom_in_index)}")
    print(f"Retrievability: {retrievability_outcome}")
    
    # Save evidence
    evidence_dir = Path("standalone")
    write_evidence(membership_evidence, evidence_dir / "SEARCH_MEMBERSHIP_evidence.json")
    write_evidence(retrievability_evidence, evidence_dir / "SEARCH_RETRIEVABILITY_evidence.json")

    if args.enforce and (membership_outcome == "FAIL" or retrievability_outcome == "FAIL"):
        sys.exit(1)

if __name__ == "__main__":
    main()
