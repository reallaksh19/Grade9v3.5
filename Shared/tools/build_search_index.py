#!/usr/bin/env python3
"""Build the search index: one document per canonical question, and the manifest that says which canonical state it was built from.

The index is a projection. Its manifest names the canonical inputs it read by digest (every JSON file under the library directories, LF-normalised), the ids it
holds and the ids it left out, and the digest of the index itself, so that verify_search_index.py can say whether it is current, complete and unaltered.
A library file that does not parse stops the build: an index built over what could be read would be missing questions and say nothing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import contract  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402


def build_search_document(q: dict, subject: str) -> dict | None:
    if q.get("extensions", {}).get("search_visibility") == "EXCLUDED":
        return None
    concept_refs = []
    if "extensions" in q and "problem_specification" in q["extensions"]:
        concept_refs = q["extensions"]["problem_specification"].get("concept_refs", [])
    stem = q.get("stem", "")
    answer = q.get("answer", {})
    parts = [stem] + ([answer["summary"]] if isinstance(answer, dict) and "summary" in answer else []) + list(q.get("conditions", []))
    source_refs = q.get("source_refs", [])
    return {
        "schema": "search-document/v1",
        "canonical_id": q["id"],
        "canonical_digest": contract.digest(q),
        "type": "QUESTION",
        "subject": subject,
        "concept_refs": concept_refs,
        "title": stem[:80],
        "search_text": " ".join(part for part in parts if part),
        "aliases": [q["id"]],
        "canonical_url": f"/products/{subject.lower()}/{q.get('primary_capability_ref', '')}/",
        "source_refs": [source_refs[0]] if source_refs else [],
    }


def read_questions(roots: list[Path]) -> list[tuple[str, dict]]:
    """(subject, question) for every question under the library directories, in a fixed order; a file that cannot be read is an error."""
    found = []
    for root in roots:
        for path in sorted(root.rglob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise ContractError("SEARCH_INDEX_UNREADABLE_LIBRARY", f"{path}: {exc}") from exc
            if isinstance(data, dict) and isinstance(data.get("questions"), list):
                found += [(data.get("subject", "Unknown"), q) for q in data["questions"]]
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--library-dirs", nargs="+", required=True)
    parser.add_argument("--output-index", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--canonical-snapshot-digest", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    roots = [Path(d) for d in args.library_dirs if Path(d).exists()]
    documents, excluded = [], []
    for subject, q in read_questions(roots):
        doc = build_search_document(q, subject)
        (documents if doc else excluded).append(doc or q["id"])
    documents.sort(key=lambda d: d["canonical_id"])
    index_text = json.dumps(documents, indent=2, sort_keys=True)
    manifest = {
        "schema": "search-index-manifest/v1",
        "index_version": "1",
        "canonical_snapshot_digest": args.canonical_snapshot_digest or contract.digest_roots(roots),
        "generator": {"name": "build_search_index", "version": "1.1.0"},
        "record_count": len(documents),
        "canonical_ids": [d["canonical_id"] for d in documents],
        "excluded_ids": sorted(excluded),
        "index_digest": "sha256:" + hashlib.sha256(contract.normalise_text(index_text.encode("utf-8"))).hexdigest(),
        "generated_at": datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0).isoformat() + "Z",
    }
    if args.dry_run:
        print(f"Would write {len(documents)} documents to {args.output_index} and a manifest with {len(excluded)} excluded to {args.output_manifest}")
        return 0
    for path, text in ((Path(args.output_index), index_text), (Path(args.output_manifest), json.dumps(manifest, indent=2, sort_keys=True))):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Indexed {len(documents)} documents; excluded {len(excluded)}. Wrote {args.output_index} and {args.output_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
