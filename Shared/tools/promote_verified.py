#!/usr/bin/env python3
"""Historical record merge helper for the M3 Mathematics staging migration.

This module has no publication or authoring gate. New records belong in the unit's
canonical library package; verification and completeness are advisory observations.
"""
from __future__ import annotations

import copy
import json

COLLECTIONS = ("capabilities", "microtopics", "relations", "representations", "question_families", "questions")


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
    for key in ("resources", "buckets", "known_issues", "application_contexts"):
        known = {r["id"] for r in out.get(key, [])}
        out[key] = out.get(key, []) + [r for r in staging_header.get(key, []) if r["id"] not in known]
    known_mappings = {json.dumps(r, sort_keys=True, ensure_ascii=False) for r in out.get("curriculum_mappings", [])}
    out["curriculum_mappings"] = out.get("curriculum_mappings", []) + [
        r for r in staging_header.get("curriculum_mappings", [])
        if json.dumps(r, sort_keys=True, ensure_ascii=False) not in known_mappings
    ]
    return out
