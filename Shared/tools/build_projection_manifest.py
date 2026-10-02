#!/usr/bin/env python3
"""Builds a projection manifest from a render receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Add Shared/tools to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from assurance_record import make_evidence, write_evidence
except ImportError:
    pass  # We'll fail later if it's really missing, but this makes it robust

def compute_sha256(files: list[Path]) -> str:
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: str(x)):
        if f.is_file():
            h.update(f.read_bytes())
    return "sha256:" + h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--projection-type", choices=["WEB", "STANDALONE", "PDF", "SEARCH"], required=True)
    parser.add_argument("--canonical-dir", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    render_dir = Path(args.render_dir)
    canonical_dir = Path(args.canonical_dir)
    
    receipt_file = render_dir / "render-receipt.json"
    if not receipt_file.exists():
        print(f"Error: {receipt_file} not found")
        sys.exit(1)
        
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    
    canonical_files = list(canonical_dir.rglob("*.json"))
    canonical_digest = compute_sha256(canonical_files)
    
    html_files = list(render_dir.rglob("*.html"))
    artifact_digest = compute_sha256(html_files)
    
    record_ids = [str(Path(p).with_suffix("")) for p in receipt.get("pages", [])]
    
    manifest = {
        "schema": "projection-manifest/v1",
        "projection_type": args.projection_type,
        "canonical_snapshot_digest": canonical_digest,
        "generator": {"name": "render_core", "version": "render_core/2"},
        "generator_input_digest": canonical_digest,
        "record_ids": record_ids,
        "artifact_digest": artifact_digest,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    if args.output:
        Path(args.output).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    else:
        print(json.dumps(manifest, indent=2))
        
    is_pass = (artifact_digest == receipt.get("digest"))
    evidence = make_evidence(
        assurance_type="PROJECTION_INTEGRITY",
        subject_kind="PROJECTION",
        subject_id=str(render_dir),
        outcome="PASS" if is_pass else "FAIL",
        producer_name="build_projection_manifest",
        producer_version="1.0"
    )
    write_evidence(evidence, render_dir / "build_manifest_evidence.json")

if __name__ == "__main__":
    main()
