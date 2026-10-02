#!/usr/bin/env python3
"""Verifies a projection manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Add Shared/tools to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from assurance_record import make_evidence, write_evidence
except ImportError:
    pass

def compute_sha256(files: list[Path]) -> str:
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: str(x)):
        if f.is_file():
            h.update(f.read_bytes())
    return "sha256:" + h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    manifest_file = Path(args.manifest)
    render_dir = Path(args.render_dir)
    
    if not manifest_file.exists():
        print(f"Error: {manifest_file} not found")
        sys.exit(1)
        
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    
    html_files = list(render_dir.rglob("*.html"))
    recomputed_digest = compute_sha256(html_files)
    
    committed_digest = manifest.get("artifact_digest")
    
    is_pass = (committed_digest == recomputed_digest)
    outcome = "PASS" if is_pass else "FAIL"
    
    print(f"Committed digest:  {committed_digest}")
    print(f"Recomputed digest: {recomputed_digest}")
    print(f"Outcome: {outcome}")
    
    evidence = make_evidence(
        assurance_type="PROJECTION_INTEGRITY",
        subject_kind="PROJECTION_MANIFEST",
        subject_id=str(manifest_file),
        outcome=outcome,
        producer_name="verify_projection_manifest",
        producer_version="1.0"
    )
    write_evidence(evidence, render_dir / "verify_projection_evidence.json")
    
    if not is_pass and args.enforce:
        sys.exit(1)

if __name__ == "__main__":
    main()
