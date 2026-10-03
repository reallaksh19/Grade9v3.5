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
    synonyms_file = repo_root / "public" / "data" / "keyword-synonyms.v1.json"
    synonyms = []
    if synonyms_file.exists():
        try:
            with open(synonyms_file, "r", encoding="utf-8") as f:
                syn_data = json.load(f)
                synonyms = syn_data.get("synonyms", [])
        except Exception as e:
            print("Failed loading keyword-synonyms.v1.json:", e)

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
        topic_refs = classification.get("topic_refs", [])
        ep = rec.get("artifact", {}).get("entrypoint", "")

        is_core1a = "core1a" in rid.lower() or "core1a" in ep.lower() or "core 1a" in title.lower()
        is_core2 = "core2" in rid.lower() or "core2" in ep.lower() or "core 2" in title.lower()
        is_suite = "master-suite" in ep.lower() or "master suite" in title.lower()
        is_explorer = role == "EXPLORE" or "explorer" in ep.lower()

        if is_core1a:
            badge = "CORE 1A FOUNDATION"
            sub_type = "CORE_1A"
        elif is_core2:
            badge = "CORE 2 CHALLENGE"
            sub_type = "CORE_2"
        elif is_suite:
            badge = "MASTER SUITE"
            sub_type = "SUITE"
        elif is_explorer:
            badge = "EXPLORER"
            sub_type = "EXPLORER"
        else:
            badge = "PRACTICE" if role == "PRACTICE" else ("CORE STUDY" if role == "LEARN" else role)
            sub_type = role

        topic_clean = topic_refs[0].split(".")[-1].replace("-", " ").title() if topic_refs else ""
        breadcrumb = f"{subj} · {topic_clean} · {badge}".replace(" ·  ·", " ·").strip(" ·")

        # Inject thesaurus synonyms matching resource
        res_syns = []
        for syn in synonyms:
            slug = syn.get("slug", "")
            if slug and any(slug in tr.lower() for tr in topic_refs):
                res_syns.extend(syn.get("aliases", []))
            elif syn.get("entity_refs", {}).get("concept_ref") in caps:
                res_syns.extend(syn.get("aliases", []))

        docs.append({
            "id": f"RES-{rid}",
            "type": f"{role}_RESOURCE",
            "category": "tablet" if sub_type in ("CORE_1A", "CORE_2", "SUITE", "EXPLORER", "LEARN", "PRACTICE") or "12-7-tablet" in ep else "page",
            "sub_type": sub_type,
            "badge": badge,
            "breadcrumb": breadcrumb,
            "subject": subj,
            "title": title,
            "search_text": f"{title} {' '.join(aliases)} {' '.join(res_syns)} {' '.join(topic_refs)} {' '.join(caps)} {subj} {badge} {sub_type}".lower(),
            "url": ep,
            "target": "_blank" if role == "EXPLORE" else "_self",
            "concept_refs": caps
        })

    # 2. Concept Bundles
    for b in bundles:
        cref = b["concept_ref"]
        title = b.get("title", cref)
        subj = b.get("subject_ref", "Physics")
        tref = b.get("topic_ref", "")
        slug = tref.split(".")[-1]
        subj_slug = subj.lower()
        if tref == "chem.mole":
            target_url = f"{subj_slug}/some-basic-concepts/index.html#{cref}"
        elif len(b.get("learn", [])) == 0 and len(b.get("interactive", [])) > 0:
            target_url = b["interactive"][0]["entrypoint"]
        else:
            target_url = f"{subj_slug}/{slug}/index.html#{cref}"

        con_syns = []
        for syn in synonyms:
            s_slug = syn.get("slug", "")
            if s_slug and s_slug in tref.lower():
                con_syns.extend(syn.get("aliases", []))
            elif syn.get("entity_refs", {}).get("concept_ref") == cref:
                con_syns.extend(syn.get("aliases", []))

        docs.append({
            "id": f"CON-{cref}",
            "type": "CONCEPT",
            "category": "curriculum",
            "badge": "CONCEPT",
            "breadcrumb": f"{subj} · {slug.replace('-', ' ').title()} · Concept",
            "subject": subj,
            "title": title,
            "search_text": f"{title} {' '.join(con_syns)} {cref} {tref} {subj} concept".lower(),
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
        title = stem[:90] or f"Question {qid}"
        ans = q.get("answer", {})
        ans_summary = ans.get("summary", "") if isinstance(ans, dict) else str(ans)
        ans_reasoning = " ".join(ans.get("reasoning", [])) if isinstance(ans, dict) else ""
        scaffolds = " ".join(s.get("text", "") for s in q.get("scaffolds", []) if isinstance(s, dict))
        hints = " ".join(str(h) for h in q.get("source_hints", []))
        options_text = " ".join(opt.get("text", "") for opt in q.get("options", []) if isinstance(opt, dict))
        topic = q.get("topic", "")
        subj = q.get("subject", "Physics")
        cap = q.get("primary_capability_ref", "")

        exam = q.get("exam", "")
        year = str(q.get("year") or "")
        paper = q.get("paper", "")
        qnum = str(q.get("question_number") or qid)
        diff_info = q.get("difficulty") or {}
        diff_band = diff_info.get("band", "") if isinstance(diff_info, dict) else str(diff_info)
        tags = [str(t).lower() for t in q.get("tags") or []]

        aliases = []
        exam_l = exam.lower()
        qid_l = qid.lower()
        if "ncert" in exam_l or "ncert" in qid_l or any("ncert" in t for t in tags):
            aliases.extend(["ncert", "cbse", "textbook", "exemplar"])
        if "jee" in exam_l or "iit" in exam_l or "jee" in qid_l or any("jee" in t for t in tags):
            aliases.extend(["jee", "iit", "iit-jee", "pyq", "competitive"])
        if qid_l.startswith("1d-q") or "core" in qid_l or "core2" in qid_l or any("core2" in t for t in tags):
            aliases.extend(["core2", "core 2", "challenge"])

        # Inject thesaurus synonyms matching question topic, exam, or capability
        for syn in synonyms:
            erefs = syn.get("entity_refs", {})
            slug_spaced = syn.get("slug", "").replace("-", " ")
            canon = syn.get("canonical_term", "").lower()
            topic_l = topic.lower()
            if (slug_spaced and slug_spaced in topic_l) or (canon and (canon in topic_l or topic_l in canon)):
                aliases.extend(syn.get("aliases", []))
            elif erefs.get("exam_family") and erefs.get("exam_family").lower() in exam_l:
                aliases.extend(syn.get("aliases", []))
            elif erefs.get("concept_ref") and erefs.get("concept_ref") == cap:
                aliases.extend(syn.get("aliases", []))

        diff_words = {"d1": "d1 easy foundation", "d2": "d2 medium standard", "d3": "d3 hard advanced", "d4": "d4 olympiad"}.get(diff_band.lower(), diff_band)
        search_vector = f"{qid} {title} {stem} {options_text} {topic} {cap} {subj} {exam} {year} {paper} Q{qnum} {diff_words} {' '.join(aliases)}".lower()

        exam_tag = f"NCERT · {diff_band}".strip(" ·") if "ncert" in aliases else (f"JEE · {diff_band}".strip(" ·") if "jee" in aliases else (f"{exam} · {diff_band}".strip(" ·") or "QUESTION"))
        breadcrumb = f"{subj} · {topic} · {exam} {year} · Q{qnum}".replace("  ", " ").strip(" ·")

        docs.append({
            "id": f"Q-{qid}",
            "type": "QUESTION",
            "category": "question",
            "badge": exam_tag,
            "breadcrumb": breadcrumb,
            "subject": subj,
            "title": title,
            "search_text": search_vector,
            "url": f"question-bank/index.html?q={qid}#{qid}",
            "target": "_self",
            "concept_refs": [cap] if cap else []
        })

    # 4. Curriculum Nodes (Topics and Subtopics from catalog)
    cat_file = repo_root / "public" / "data" / "question-bank-catalog.js"
    if cat_file.exists():
        try:
            raw_cat = cat_file.read_text(encoding="utf-8")
            prefix_cat = "window.GRADE9_QUESTION_BANK_CATALOG="
            if raw_cat.startswith(prefix_cat):
                cat_obj = json.loads(raw_cat[len(prefix_cat):].rstrip(";\n "))
                for top in cat_obj.get("topics", []):
                    tid = top.get("id")
                    if not tid or top.get("question_count", 0) == 0:
                        continue
                    t_label = top.get("label", tid)
                    t_subj = top.get("subject_ref", "").replace("SUBJECT-", "").title()
                    top_syns = []
                    for syn in synonyms:
                        if syn.get("entity_refs", {}).get("topic_ref") == tid or syn.get("slug", "") in t_label.lower():
                            top_syns.extend(syn.get("aliases", []))
                    docs.append({
                        "id": f"TOPIC-{tid}",
                        "type": "TOPIC",
                        "category": "curriculum",
                        "subject": t_subj,
                        "title": t_label,
                        "search_text": f"topic {t_label} {' '.join(top_syns)} {t_subj} {tid}".lower(),
                        "url": f"question-bank/index.html?topic={tid}",
                        "target": "_self",
                        "badge": "TOPIC",
                        "breadcrumb": f"{t_subj} · Curriculum Topic · {top.get('question_count', 0)} Questions",
                        "concept_refs": []
                    })
                for sub in cat_obj.get("subtopics", []):
                    sid = sub.get("id")
                    if not sid or sub.get("question_count", 0) == 0:
                        continue
                    if sub.get("label_source") != "CANONICAL_TITLE":
                        continue
                    s_label = sub.get("label", sid)
                    s_subj = sub.get("subject_ref", "").replace("SUBJECT-", "").title()
                    docs.append({
                        "id": f"SUBTOPIC-{sid}",
                        "type": "SUBTOPIC",
                        "category": "curriculum",
                        "subject": s_subj,
                        "title": s_label,
                        "search_text": f"subtopic capability {s_label} {s_subj} {sid}".lower(),
                        "url": f"question-bank/index.html?subtopic={sid}",
                        "target": "_self",
                        "badge": "SUBTOPIC",
                        "breadcrumb": f"{s_subj} · Subtopic Capability · {sub.get('question_count', 0)} Questions",
                        "concept_refs": [sid]
                    })
        except Exception as e:
            print("Failed indexing curriculum catalog nodes:", e)

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
