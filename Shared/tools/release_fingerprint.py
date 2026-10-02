#!/usr/bin/env python3
"""Build the immutable release fingerprint per spec 32."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _hash_files(directory: Path, pattern: str = "*", file_list: list[Path] | None = None) -> str:
    """Hash files using filename_bytes + \\0 + file_bytes."""
    if not directory.exists():
        return None
        
    if file_list is None:
        files = list(directory.rglob(pattern))
    else:
        files = file_list
        
    valid_files = [f for f in files if f.is_file()]
    if not valid_files:
        return None
        
    # Sort files by their relative path as a string (using posix forward slashes)
    valid_files.sort(key=lambda f: f.relative_to(directory).as_posix())
    
    h = hashlib.sha256()
    for f in valid_files:
        rel_path = f.relative_to(directory).as_posix().encode("utf-8")
        content = f.read_bytes()
        h.update(rel_path + b"\0" + content)
    return "sha256:" + h.hexdigest()


def find_source_refs(obj, refs=None):
    if refs is None:
        refs = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source_refs" and isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        refs.add(item)
            else:
                find_source_refs(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            find_source_refs(item, refs)
    return refs


def build_fingerprint(args) -> dict:
    canonical_dir = Path(args.canonical_dir)
    web_dir = Path(args.web_dir)
    
    # 1. canonical_snapshot_digest
    canonical_digest = _hash_files(canonical_dir, "*.json")
    
    # 2. source_set_digest
    refs = set()
    if canonical_dir.exists():
        for f in canonical_dir.rglob("*.json"):
            if f.is_file():
                try:
                    data = json.loads(f.read_text("utf-8"))
                    find_source_refs(data, refs)
                except Exception:
                    pass
    h_src = hashlib.sha256()
    for ref in sorted(refs):
        h_src.update(ref.encode("utf-8") + b"\0")
    source_set_digest = "sha256:" + h_src.hexdigest() if refs else None

    # 3. policy_digest
    policy_dir = REPO / "Shared" / "policy"
    policy_digest = _hash_files(policy_dir)

    # 4. assurance_bundle_digest
    bundle_digest = None
    if args.assurance_bundle:
        bp = Path(args.assurance_bundle)
        if bp.exists():
            h_b = hashlib.sha256()
            h_b.update(bp.name.encode("utf-8") + b"\0" + bp.read_bytes())
            bundle_digest = "sha256:" + h_b.hexdigest()

    # 5. web_projection_digest
    web_digest = _hash_files(web_dir, "*.html")

    # 6. standalone_projection_digest
    standalone_digest = None
    if args.standalone_dir:
        sd = Path(args.standalone_dir)
        standalone_digest = _hash_files(sd, "*.html")

    # 7. search_projection_digest
    search_digest = None
    if args.search_index:
        sp = Path(args.search_index)
        if sp.exists():
            h_s = hashlib.sha256()
            h_s.update(sp.name.encode("utf-8") + b"\0" + sp.read_bytes())
            search_digest = "sha256:" + h_s.hexdigest()

    record = {
        "schema": "release-fingerprint/v1",
        "product": args.product_id,
        "source_set_digest": source_set_digest,
        "canonical_snapshot_digest": canonical_digest,
        "policy_digest": policy_digest,
        "assurance_bundle_digest": bundle_digest,
        "renderer_version": "render_core/2",
        "web_projection_digest": web_digest,
        "standalone_projection_digest": standalone_digest,
        "pdf_projection_digest": None,
        "search_projection_digest": search_digest,
        "fingerprinted_at": dt.datetime.now(dt.timezone.utc).isoformat()
    }
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--canonical-dir", required=True)
    parser.add_argument("--web-dir", required=True)
    parser.add_argument("--standalone-dir")
    parser.add_argument("--search-index")
    parser.add_argument("--search-manifest")
    parser.add_argument("--assurance-bundle")
    parser.add_argument("--output")
    args = parser.parse_args()

    record = build_fingerprint(args)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
    else:
        print(json.dumps(record, indent=2))

if __name__ == "__main__":
    main()
