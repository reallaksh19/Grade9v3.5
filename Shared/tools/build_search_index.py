#!/usr/bin/env python3
"""Builds a search index from canonical library files."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def compute_sha256_of_files(files: list[Path]) -> str:
    h = hashlib.sha256()
    for f in sorted(files, key=lambda x: str(x)):
        if f.is_file():
            h.update(f.read_bytes())
    return "sha256:" + h.hexdigest()

def compute_digest(data: dict | list | str | bytes) -> str:
    if isinstance(data, (dict, list)):
        content_str = json.dumps(data, sort_keys=True).encode("utf-8")
    elif isinstance(data, str):
        content_str = data.encode("utf-8")
    else:
        content_str = data
    return "sha256:" + hashlib.sha256(content_str).hexdigest()


def build_search_document(q: dict, subject: str) -> dict | None:
    # Check exclusion
    if q.get("extensions", {}).get("search_visibility") == "EXCLUDED":
        return None

    canonical_id = q["id"]
    canonical_digest = compute_digest(q)

    concept_refs = []
    if "extensions" in q and "problem_specification" in q["extensions"]:
        concept_refs = q["extensions"]["problem_specification"].get("concept_refs", [])

    stem = q.get("stem", "")
    title = stem[:80]

    search_parts = [stem]
    answer = q.get("answer", {})
    if isinstance(answer, dict) and "summary" in answer:
        search_parts.append(answer["summary"])
    
    conditions = q.get("conditions", [])
    if conditions:
        search_parts.extend(conditions)
    
    search_text = " ".join(part for part in search_parts if part)

    primary_cap = q.get("primary_capability_ref", "")
    subject_lower = subject.lower()
    canonical_url = f"/products/{subject_lower}/{primary_cap}/"

    source_refs = q.get("source_refs", [])
    doc_source_refs = [source_refs[0]] if source_refs else []

    return {
        "schema": "search-document/v1",
        "canonical_id": canonical_id,
        "canonical_digest": canonical_digest,
        "type": "QUESTION",
        "subject": subject,
        "concept_refs": concept_refs,
        "title": title,
        "search_text": search_text,
        "aliases": [canonical_id],
        "canonical_url": canonical_url,
        "source_refs": doc_source_refs
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-dirs", nargs="+", required=True)
    parser.add_argument("--output-index", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--canonical-snapshot-digest", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    documents = []
    excluded_ids = []
    canonical_ids = []
    canonical_files = []

    for d in args.library_dirs:
        dir_path = Path(d)
        if not dir_path.exists():
            continue
        for root, _, files in os.walk(dir_path):
            for f in files:
                if f.endswith(".json"):
                    filepath = Path(root) / f
                    canonical_files.append(filepath)
                    try:
                        with open(filepath, "r", encoding="utf-8") as file_obj:
                            data = json.load(file_obj)
                    except Exception:
                        continue
                    
                    if not isinstance(data, dict) or "questions" not in data:
                        continue
                    
                    subject = data.get("subject", "Unknown")
                    
                    for q in data["questions"]:
                        doc = build_search_document(q, subject)
                        if doc:
                            documents.append(doc)
                            canonical_ids.append(doc["canonical_id"])
                        else:
                            excluded_ids.append(q["id"])

    # Output index
    output_index_json = json.dumps(documents, indent=2, sort_keys=True)
    index_digest = compute_digest(output_index_json)

    # Output manifest
    manifest = {
        "schema": "search-index-manifest/v1",
        "index_version": "1",
        "canonical_snapshot_digest": args.canonical_snapshot_digest or compute_sha256_of_files(canonical_files),
        "generator": {"name": "build_search_index", "version": "1.0.0"},
        "record_count": len(documents),
        "canonical_ids": canonical_ids,
        "excluded_ids": excluded_ids,
        "index_digest": index_digest,
        "generated_at": datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat() + "Z"
    }
    output_manifest_json = json.dumps(manifest, indent=2, sort_keys=True)

    if args.dry_run:
        print(f"Would write index to {args.output_index}:")
        print(f"  {len(documents)} documents")
        print(f"Would write manifest to {args.output_manifest}:")
        print(f"  {len(excluded_ids)} excluded")
        return

    out_idx = Path(args.output_index)
    out_idx.parent.mkdir(parents=True, exist_ok=True)
    with open(out_idx, "w", encoding="utf-8", newline="\n") as f:
        f.write(output_index_json)

    out_mnf = Path(args.output_manifest)
    out_mnf.parent.mkdir(parents=True, exist_ok=True)
    with open(out_mnf, "w", encoding="utf-8", newline="\n") as f:
        f.write(output_manifest_json)

    print(f"Indexed {len(documents)} documents.")
    print(f"Excluded {len(excluded_ids)} documents.")
    print(f"Wrote index to {args.output_index}")
    print(f"Wrote manifest to {args.output_manifest}")

if __name__ == "__main__":
    main()
