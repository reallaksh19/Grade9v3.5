#!/usr/bin/env python3
"""The only way content enters the canonical library: promote verified research nodes.

A MICROTOPIC node's staging records (<Subject>/research/packages/<CHAPTER>.package.json) are
promoted into the canonical library only when:
1. the research board shows the node VERIFIED against its current inputs (no stale
   verification), and
2. the records carry no depth duty (Shared/tools/package_depth.py): the records can supply
   what the learner quality contract requires.

Anything else is refused with the duties that block it. Promoted records land in
<Subject>/library/research-<chapter>.v1.json (schema 0.2.0). Each record carries
extensions["grade9v3:promotion"]: the verification file, its inputs digest and the date.

Usage:
    promote_verified.py --subject Physics [--chapter PHY-11-MOTION-IN-A-PLANE] [--write]
"""
from __future__ import annotations

import argparse
import copy
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import library_board, package_depth, package_migrate  # noqa: E402

COLLECTIONS = ("capabilities", "microtopics", "relations", "representations", "question_families", "questions")


def canonical_path(subject: str, chapter: str, repo: Path = REPO) -> Path:
    return repo / subject / "library" / f"research-{chapter.lower()}.v1.json"


def plan(board: dict, staging: dict[str, dict], taught: set[str], limit: int) -> dict:
    """Which nodes' records may be promoted, and why the others may not. Pure: no files.

    A prerequisite taught by a sibling node counts only when that sibling is promoted in the same
    batch, so the plan is repeated until the set of promotable nodes stops growing."""
    batch: set[str] = set()
    while True:
        result = _plan_once(board, staging, taught | batch, limit)
        grown = {f"{board['subject']}:{c['id']}" for item in result["promotable"]
                 for c in item["package"].get("capabilities", [])}
        grown |= {c.split(":", 1)[1] for c in grown}
        if grown <= batch:
            return result
        batch |= grown


def _plan_once(board: dict, staging: dict[str, dict], taught: set[str], limit: int) -> dict:
    promotable, refused = [], []
    for row in board["nodes"]:
        if row["level"] != "MICROTOPIC":
            continue
        chapter = row["chapter"]
        package = staging.get(chapter)
        records = library_board._node_records(package, row["node"]) if package else []
        if row["stage"] != "VERIFIED":
            refused.append({"node": row["node"], "reason": f"stage {row['stage']}", "duties": row["duties"][:3]})
            continue
        if not records:
            refused.append({"node": row["node"], "reason": "no staging records", "duties": []})
            continue
        mini = package_migrate.migrate_package(
            {"schema_version": package.get("schema_version", "0.1.0"), "subject": board["subject"],
             **{c: [r for coll, r in records if coll == c] for c in COLLECTIONS}}, limit)
        duties = package_depth.package_duties(mini, f"staging:{chapter}", taught, limit)
        if duties:
            refused.append({"node": row["node"], "reason": "depth duties", "duties": duties})
            continue
        promotable.append({"node": row["node"], "chapter": chapter, "verification": row["verification"],
                           "package": mini})
    return {"promotable": promotable, "refused": refused}


def merge(canonical: dict | None, staging_header: dict, subject: str, chapter: str, items: list[dict], today: str) -> dict:
    out = copy.deepcopy(canonical) if canonical else {
        "schema_version": "0.2.0", "package_id": f"LIB-{subject[:3].upper()}-RESEARCH-{chapter}",
        "version": "0.1.0", "status": "CANDIDATE", "subject": subject,
        "scope_summary": staging_header.get("scope_summary") or f"Verified research records for {chapter}.",
        **{k: [] for k in ("curriculum_mappings", "resources", "buckets", *COLLECTIONS, "teaching_routes",
                           "practice_profiles", "evidence", "known_issues", "data", "application_contexts")},
        "extensions": {}}
    for item in items:
        stamp = {"verification": item["verification"], "promoted_at": today, "research_node": item["node"]}
        for coll in COLLECTIONS:
            for rec in item["package"].get(coll, []):
                rec = copy.deepcopy(rec)
                rec.setdefault("extensions", {})["grade9v3:promotion"] = stamp
                rows = [r for r in out.setdefault(coll, []) if r["id"] != rec["id"]]
                out[coll] = rows + [rec]
    for key in ("resources", "buckets"):
        known = {r["id"] for r in out.get(key, [])}
        out[key] = out.get(key, []) + [r for r in staging_header.get(key, []) if r["id"] not in known]
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--subject", required=True)
    p.add_argument("--chapter")
    p.add_argument("--write", action="store_true")
    a = p.parse_args(argv)
    board = library_board.build(a.subject)
    chapters = {r["chapter"] for r in board["nodes"] if not a.chapter or r["chapter"] == a.chapter}
    staging = {c: library_board._load(library_board.staging_path(a.subject, c))
               for c in chapters if library_board.staging_path(a.subject, c).is_file()}
    board["nodes"] = [r for r in board["nodes"] if r["chapter"] in chapters]
    result = plan(board, staging, package_depth.taught_capabilities(), package_migrate.max_decisions())
    for r in result["refused"]:
        print(f"refused {r['node']}: {r['reason']}" + (f" ({len(r['duties'])} duties, e.g. {r['duties'][0].get('duty')})" if r["duties"] else ""))
    for item in result["promotable"]:
        print(f"promotable {item['node']}")
    if a.write and result["promotable"]:
        today = datetime.date.today().isoformat()
        by_chapter: dict[str, list[dict]] = {}
        for item in result["promotable"]:
            by_chapter.setdefault(item["chapter"], []).append(item)
        for chapter, items in by_chapter.items():
            path = canonical_path(a.subject, chapter)
            current = library_board._load(path) if path.is_file() else None
            path.write_text(json.dumps(merge(current, staging[chapter], a.subject, chapter, items, today),
                                       indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    print(f"{len(result['promotable'])} promotable, {len(result['refused'])} refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
