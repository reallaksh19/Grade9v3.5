#!/usr/bin/env python3
"""Build converged learner discovery search index for Grade9V3.5.

Combines:
1. Publishable Resource Registry (LEARNER audience only)
2. Concept Bundles
3. Canonical Question Bank questions

Generates:
- public/data/learner-search-index.v1.json
- public/data/learner-search-index-manifest.v1.json
- public/data/site-search-resources.js (compatibility projection)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def build_search_documents(repo_root: Path) -> tuple[list[dict], dict]:
    registry_file = repo_root / "public" / "data" / "resource-registry.v1.json"
    bundles_file = repo_root / "public" / "data" / "concept-bundles.v1.json"
    qb_search_file = repo_root / "public" / "data" / "search-index.v1.json"

    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)

    bundles = []
    if bundles_file.exists():
        with open(bundles_file, "r", encoding="utf-8") as f:
            bundles = json.load(f)

    qb_questions = []
    if qb_search_file.exists():
        with open(qb_search_file, "r", encoding="utf-8") as f:
            qb_questions = json.load(f)

    docs = []
    seen_ids = set()

    # 1. Registered Learner Resources (Exclude OWNER / LAB / INTERNAL)
    for rec in registry:
        if rec.get("audience") != "LEARNER" or rec.get("search", {}).get("visibility") == "EXCLUDED":
            continue

        rid = rec["id"]
        if rid in seen_ids:
            continue
        seen_ids.add(rid)

        search_meta = rec.get("search", {})
        classification = rec.get("classification", {})
        title = search_meta.get("title", rid)
        aliases = search_meta.get("aliases", [])
        role = rec.get("learner_role", "RESOURCE")
        subj = classification.get("subject_ref", "Common")
        caps = classification.get("capability_refs", [])
        ep = rec.get("artifact", {}).get("entrypoint", "")

        docs.append({
            "id": f"RES-{rid}",
            "type": f"{role}_RESOURCE",
            "subject": subj,
            "title": title,
            "search_text": f"{title} {' '.join(aliases)} {' '.join(caps)} {subj}".lower(),
            "url": ep,
            "target": "_blank" if role == "EXPLORE" else "_self",
            "concept_refs": caps
        })

    # 2. Concept Bundles
    for b in bundles:
        cref = b["concept_ref"]
        title = b.get("title", cref)
        subj = b.get("subject_ref", "Physics")
        docs.append({
            "id": f"CON-{cref}",
            "type": "CONCEPT",
            "subject": subj,
            "title": title,
            "search_text": f"{title} {cref} {subj}".lower(),
            "url": f"topics/nlm/index.html#{cref}" if "nlm" in b.get("topic_ref", "") else f"topics/{b.get('topic_ref')}/index.html",
            "target": "_self",
            "concept_refs": [cref]
        })

    # 3. Canonical Questions (from existing search index)
    for q in qb_questions:
        qid = q.get("canonical_id") or q.get("id")
        if not qid:
            continue
        title = q.get("title") or f"Question {qid}"
        stext = q.get("search_text", "")
        subj = q.get("subject", "Physics")
        docs.append({
            "id": f"Q-{qid}",
            "type": "QUESTION",
            "subject": subj,
            "title": title,
            "search_text": f"{title} {stext} {subj}".lower(),
            "url": f"question-bank/index.html?search={qid}",
            "target": "_self",
            "concept_refs": q.get("concept_refs", [])
        })

    # Build stats
    stats = {
        "total_documents": len(docs),
        "by_type": {}
    }
    for d in docs:
        t = d["type"]
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    return docs, stats


def generate_compatibility_site_search_js(docs: list[dict]) -> str:
    """Generate the legacy window.GRADE9_SITE_SEARCH_RESOURCES compatibility projection."""
    compat_list = []
    for d in docs:
        if d["type"] in ("LEARN_RESOURCE", "PRACTICE_RESOURCE", "EXPLORE_RESOURCE"):
            compat_list.append({
                "title": d["title"],
                "path": d["url"],
                "kind": d["type"].lower().replace("_resource", ""),
                "keywords": d["search_text"].split()
            })

    js_code = f"window.GRADE9_SITE_SEARCH_RESOURCES = {json.dumps(compat_list, indent=2)};\n"
    return js_code


def main():
    parser = argparse.ArgumentParser(description="Build converged learner discovery search index")
    parser.add_argument("--repo-root", type=Path, default=REPO)
    parser.add_argument("--output-index", type=Path, default=REPO / "public" / "data" / "learner-search-index.v1.json")
    parser.add_argument("--output-manifest", type=Path, default=REPO / "public" / "data" / "learner-search-index-manifest.v1.json")
    parser.add_argument("--output-compat", type=Path, default=REPO / "public" / "data" / "site-search-resources.js")
    args = parser.parse_args()

    docs, stats = build_search_documents(args.repo_root)

    # Sort deterministically
    docs.sort(key=lambda d: d["id"])

    # Write search index JSON
    index_bytes = json.dumps(docs, indent=2, sort_keys=True).encode("utf-8")
    args.output_index.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_index, "wb") as f:
        f.write(index_bytes)

    index_digest = f"sha256:{hashlib.sha256(index_bytes).hexdigest()}"

    # Write manifest JSON
    manifest = {
        "schema": "learner-search-manifest/v1",
        "generator": {
            "name": "build_learner_search_index",
            "version": "1.0.0"
        },
        "index_digest": index_digest,
        "record_count": len(docs),
        "type_counts": stats["by_type"],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    with open(args.output_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    # Write compatibility JS
    compat_js = generate_compatibility_site_search_js(docs)
    with open(args.output_compat, "w", encoding="utf-8") as f:
        f.write(compat_js)

    # Copy to docs/
    for p in [args.output_index, args.output_manifest, args.output_compat]:
        rel = p.relative_to(args.repo_root / "public")
        dst = args.repo_root / "docs" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(p.read_bytes())

    print(f"Successfully generated Converged Learner Discovery Index:")
    print(f"  Total records: {len(docs)}")
    print(f"  Type breakdown: {stats['by_type']}")
    print(f"  Index digest: {index_digest}")
    print(f"  Compatibility JS generated at {args.output_compat}")


if __name__ == "__main__":
    main()
