#!/usr/bin/env python3
"""Every depth gap in every library package becomes a named duty.

The learner quality contract (Shared/quality/learner-quality.v1.json) says what a learner must
see. This tool checks whether the library records can supply it, across all subjects. Each
missing field becomes a duty that names:
- the role that must fix it (RESEARCHER, AUTHOR or RENDERER);
- the record;
- the contract rules the gap would fail.

Nothing is defaulted: a gap stays a duty until a record supplies the field.

Usage:
    package_depth.py [--subject Physics] [--json out.json] [--summary]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools.package_migrate import package_paths, max_decisions  # noqa: E402

# duty kind -> (role that fixes it, contract rules the gap fails)
DUTIES = {
    "AUTHOR_TYPED_MATH": ("AUTHOR", []),
    "AUTHOR_CONSTRUCTION_UNITS": ("AUTHOR", ["C1A-ANCHOR-PER-DECISION"]),
    "AUTHOR_WORKED_ANCHOR": ("AUTHOR", ["C1A-BLOCKS", "C1A-ANCHOR-PER-DECISION"]),
    "AUTHOR_INDEPENDENT_CHECK": ("AUTHOR", ["C1A-BLOCKS", "C2A-BLOCKS"]),
    "MOUNT_REPRESENTATION": ("AUTHOR", ["C1A-REPRESENTATION-BRIDGE", "C1B-REPRESENTATION"]),
    "STAGE_REPRESENTATION": ("AUTHOR", ["C1A-STAGED-REPRESENTATION"]),
    "BUILD_SCENE": ("RENDERER", ["C1A-REPRESENTATION-BRIDGE", "C2A-REPRESENTATION", "C2B-SAFE-REPRESENTATION"]),
    "TEACH_PREREQUISITE_BRIDGE": ("RESEARCHER", ["C1A-PREREQUISITES-BRIDGED"]),
    "AUTHOR_HINT_LADDER": ("AUTHOR", ["C2A-LADDER"]),
    "AUTHOR_QUESTION_REPRESENTATION": ("AUTHOR", ["C2A-REPRESENTATION"]),
    "AUTHOR_SAFE_REPRESENTATION": ("AUTHOR", ["C2B-SAFE-REPRESENTATION"]),
    "AUTHOR_FAILURE_SIGNAL": ("AUTHOR", ["C2A-TRAP", "C2A-SPECIFIC-SUPPORT"]),
    "AUTHOR_FAMILY_EXPOSURE": ("AUTHOR", ["C2A-FAMILY-CLOSURE"]),
    "AUTHOR_LINEAGE_CHECK": ("AUTHOR", ["C2B-LINEAGE"]),
    "REVIEW_MIGRATED_UNIT": ("AUTHOR", ["C1A-ANCHOR-PER-DECISION"]),
    "AUTHOR_COMPACT_ANCHOR": ("AUTHOR", ["C1-RELATION"]),
    "AUTHOR_GOVERNING_RELATION": ("AUTHOR", ["C1-RELATION"]),
    "AUTHOR_ELICITATION": ("AUTHOR", ["C1B-BLOCKS"]),
    "ACQUIRE_SOURCE": ("RESEARCHER", ["C2-BLOCKS"]),
    "AUTHOR_DIAGNOSTIC": ("AUTHOR", []),
    "AUTHOR_RECONSTRUCTION_TASK": ("AUTHOR", ["C1B-BLOCKS"]),
    "AUTHOR_TRANSFER_NOVELTY": ("AUTHOR", ["C2B-LINEAGE"]),
    "AUTHOR_COMPONENT": ("AUTHOR", ["BP-COMPONENTS-REQUIRED"]),
    "AUTHOR_LEARNER_METADATA": ("AUTHOR", ["C1-FAMILY-METADATA", "C2-METADATA", "C2A-METADATA", "C2B-METADATA"]),
}


def _cores(q: dict) -> set[str]:
    return {e["core"] for e in q.get("exposure", [])}


def taught_capabilities(repo: Path = REPO) -> set[str]:
    """Capability ids any library teaches, bare and as '<Subject>:<id>'."""
    out = set()
    for path in package_paths(repo):
        pkg = json.loads(path.read_text(encoding="utf-8"))
        for c in pkg.get("capabilities", []):
            out |= {c["id"], f"{pkg['subject']}:{c['id']}"}
    return out


def package_duties(pkg: dict, rel: str, taught: set[str], limit: int) -> list[dict]:
    duties: list[dict] = []

    def add(kind, record, detail):
        role, rules = DUTIES[kind]
        duties.append({"duty": kind, "role": role, "subject": pkg["subject"], "package": rel,
                       "record": record, "contract_rules": rules, "detail": detail})

    # A prerequisite taught by another microtopic of this same package is bridged inside the product.
    taught = taught | {c["id"] for c in pkg.get("capabilities", [])} | {
        f"{pkg.get('subject')}:{c['id']}" for c in pkg.get("capabilities", [])}
    reps = {r["id"]: r for r in pkg.get("representations", [])}
    for r in reps.values():
        if not (r.get("scene_instances") or r.get("rendered_asset_refs")):
            add("BUILD_SCENE", r["id"], "representation has no scene instance or rendered asset to mount")
        if len(r.get("reveal_stages") or []) < 2:
            add("STAGE_REPRESENTATION", r["id"], f"{len(r.get('reveal_stages') or [])} reveal stage(s); need 2")

    for m in pkg.get("microtopics", []):
        units = m.get("construction_units") or []
        steps = len(m.get("teaching_path") or [])
        if not units:
            add("AUTHOR_CONSTRUCTION_UNITS", m["id"],
                f"teaching_path has {steps} decisions (> {limit}); split into units, each with its own anchor")
        for u in units:
            if u.get("migrated_from"):
                add("REVIEW_MIGRATED_UNIT", u["id"], f"derived from {u['migrated_from']}; an author confirms the decision text and unit boundary")
            if not u.get("worked_anchor_ref"):
                add("AUTHOR_WORKED_ANCHOR", u["id"], "no CORE1A question exercises this unit's move")
            if not u.get("independent_checks"):
                add("AUTHOR_INDEPENDENT_CHECK", u["id"], "no independent check for this unit")
            if not u.get("representation_ref"):
                add("MOUNT_REPRESENTATION", u["id"], "unit names no representation")
            elif u["representation_ref"] not in reps:
                add("MOUNT_REPRESENTATION", u["id"], f"{u['representation_ref']} is not a representation of this package")
        if not m.get("compact_anchor"):
            add("AUTHOR_COMPACT_ANCHOR", m["id"], "no compact anchor for the Core1 map")
        if not m.get("relation_refs"):
            add("AUTHOR_GOVERNING_RELATION", m["id"], "no governing relation")
        if not m.get("elicitation"):
            add("AUTHOR_ELICITATION", m["id"], "no predict/attempt/reconstruct/boundary cycle for Core1B")
        elif not ((m["elicitation"].get("attempt") or {}).get("task")):
            add("AUTHOR_RECONSTRUCTION_TASK", m["id"], "no concrete Core1B task (elicitation.attempt.task); `produces` only describes the answer")
        for ref in m.get("prerequisite_refs", []):
            if ref not in taught:
                add("TEACH_PREREQUISITE_BRIDGE", m["id"], f"prerequisite {ref} is taught by no library")

    for q in pkg.get("questions", []):
        cores = _cores(q)
        roles = q.get("representation_roles") or {}
        if "CORE2A" in cores:
            if len(q.get("hint_ladder") or []) < 3:
                add("AUTHOR_HINT_LADDER", q["id"], f"{len(q.get('hint_ladder') or [])} rung(s); need 3")
            if not (roles.get("initial_ref") or q.get("figure_refs")):
                add("AUTHOR_QUESTION_REPRESENTATION", q["id"], "no representation shown with the stem")
            if not q.get("failure_signal"):
                add("AUTHOR_FAILURE_SIGNAL", q["id"], "no item-specific failure signal")
            if not (q.get("family_exposure") or {}).get("closure"):
                add("AUTHOR_FAMILY_EXPOSURE", q["id"], "no family/exposure closure")
        if "CORE2B" in cores:
            if not roles.get("safe_ref"):
                add("AUTHOR_SAFE_REPRESENTATION", q["id"], "no safe pre-commitment representation")
            nov = (q.get("transfer") or {}).get("novelty") or {}
            if not (nov.get("checked_against") and nov.get("why_new")):
                add("AUTHOR_TRANSFER_NOVELTY", q["id"], "no record of the earlier items this transfer was checked against, and why its decision is new")
            if not (q.get("transfer") or {}).get("invariant"):
                add("AUTHOR_LINEAGE_CHECK", q["id"], "no invariant-versus-changed lineage check")
        if cores & {"CORE2A", "CORE2B"} and not (q.get("independent_check") or (q.get("answer") or {}).get("check")):
            add("AUTHOR_INDEPENDENT_CHECK", q["id"], "no independent check")
    return duties


def all_duties(subject: str | None = None, repo: Path = REPO) -> list[dict]:
    taught, limit, out = taught_capabilities(repo), max_decisions(repo), []
    for path in package_paths(repo):
        pkg = json.loads(path.read_text(encoding="utf-8"))
        if subject and pkg["subject"] != subject:
            continue
        out += package_duties(pkg, str(path.relative_to(repo)), taught, limit)
    return out


def summary(duties: list[dict]) -> str:
    by = collections.Counter((d["subject"], d["duty"], d["role"]) for d in duties)
    rows = ["| Subject | Duty | Role | Count |", "|---|---|---|---|"]
    rows += [f"| {s} | {k} | {r} | {n} |" for (s, k, r), n in sorted(by.items())]
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject")
    parser.add_argument("--json")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    duties = all_duties(args.subject)
    if args.json:
        Path(args.json).write_text(json.dumps(duties, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.summary:
        print(summary(duties))
    else:
        for d in duties:
            print(f"{d['role']:10s} {d['duty']:32s} {d['record']:40s} {d['detail']}")
    print(f"{len(duties)} depth duties across {len({d['package'] for d in duties})} packages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
