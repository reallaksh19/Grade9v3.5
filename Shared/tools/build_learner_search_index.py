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

    qb_data_file = repo_root / "public" / "data" / "question-bank-data.js"
    loaded_questions = []
    if qb_data_file.exists():
        try:
            raw = qb_data_file.read_text(encoding="utf-8")
            prefix = "window.GRADE9_QUESTION_BANK="
            if raw.startswith(prefix):
                raw_json = raw[len(prefix):].rstrip(";\n ")
                qb_obj = json.loads(raw_json)
                loaded_questions = qb_obj.get("questions", [])
        except Exception as e:
            print("Failed loading question-bank-data.js:", e)

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
        slug = b.get("topic_ref", "").split(".")[-1]
        subj_slug = subj.lower()
        if b.get("topic_ref") == "chem.mole":
            target_url = f"{subj_slug}/some-basic-concepts/index.html#{cref}"
        elif len(b.get("learn", [])) == 0 and len(b.get("interactive", [])) > 0:
            target_url = b["interactive"][0]["entrypoint"]
        else:
            target_url = f"{subj_slug}/{slug}/index.html#{cref}"
        docs.append({
            "id": f"CON-{cref}",
            "type": "CONCEPT",
            "subject": subj,
            "title": title,
            "search_text": f"{title} {cref} {subj}".lower(),
            "url": target_url,
            "target": "_self",
            "concept_refs": [cref]
        })

    # 3. Canonical Questions (with Stems, Options, Worked Reasoning, Scaffolds, and Hints)
    for q in loaded_questions:
        qid = q.get("id")
        if not qid:
            continue
        stem = q.get("stem", "")
        title = stem[:80] or f"Question {qid}"
        ans = q.get("answer", {})
        ans_summary = ans.get("summary", "") if isinstance(ans, dict) else str(ans)
        ans_reasoning = " ".join(ans.get("reasoning", [])) if isinstance(ans, dict) else ""
        scaffolds = " ".join(s.get("text", "") for s in q.get("scaffolds", []) if isinstance(s, dict))
        hints = " ".join(str(h) for h in q.get("source_hints", []))
        options_text = " ".join(opt.get("text", "") for opt in q.get("options", []) if isinstance(opt, dict))
        topic = q.get("topic", "")
        subj = q.get("subject", "Physics")
        cap = q.get("primary_capability_ref", "")

        search_vector = f"{qid} {title} {stem} {options_text} {ans_summary} {ans_reasoning} {scaffolds} {hints} {topic} {cap} {subj}".lower()
        docs.append({
            "id": f"Q-{qid}",
            "type": "QUESTION",
            "subject": subj,
            "title": title,
            "search_text": search_vector,
            "url": f"question-bank/index.html?search={qid}",
            "target": "_self",
            "concept_refs": [cap] if cap else []
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
        compat_list.append({
            "title": d["title"],
            "path": d["url"],
            "kind": d["type"].lower().replace("_resource", ""),
            "keywords": d["search_text"].split()[:50]
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
