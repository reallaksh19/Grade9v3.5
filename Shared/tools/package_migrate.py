#!/usr/bin/env python3
"""Migrate library packages from schema 0.1.0 to 0.2.0 (the depth fields).

The migration is mechanical and lossless: it only restructures what a record already says.
It never invents content. Anything it cannot derive is left absent, and
Shared/tools/package_depth.py reports it as a named duty.

What it derives:
- microtopic.construction_units: one unit covering the whole teaching_path, only when the path
  has no more decisions than the contract allows per worked anchor
  (thresholds.max_decisions_per_anchor). The decision points to the microtopic's
  inferential_jump (decision_from), not a copy of it. The representation and stages are the microtopic's first representation.
  The worked anchor is the question exposed to CORE1A for the same capability. Longer paths
  get no unit: splitting them needs an author.
- question.hint_ladder: hints then scaffolds, ordered by how far each reveals
  (CONCEPT < METHOD < ANSWER), with provenance kept. Each rung points to its hint or
  scaffold (`from`) instead of copying the text, so there is one source of truth.
- question.representation_roles.bound_ref: the representation the reasoning route binds.
- question.family_exposure.family_ref: question.family_ref (closure left unset).

Usage:
    package_migrate.py --check      # exit 1 if any package is not at 0.2.0 or would change
    package_migrate.py --write      # migrate every <Subject>/library/*.v1.json in place
"""
from __future__ import annotations

import argparse
import copy
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET = "0.2.0"
REVEAL_ORDER = {"CONCEPT": 0, "METHOD": 1, "ANSWER": 2}
SUPPORT_PURPOSE = {"REPRESENT": "REPRESENT", "CONNECT": "CONNECT", "DECIDE": "FIRST_RELATION",
                   "TRANSFORM": "FIRST_RELATION", "VERIFY": "CHECK", "ORIENT": "ORIENT"}
HINT_PURPOSE = {"CONCEPT": "ORIENT", "METHOD": "FIRST_RELATION", "ANSWER": "ANSWER"}


def package_paths(repo: Path = REPO) -> list[Path]:
    return sorted(Path(p) for p in glob.glob(str(repo / "*" / "library" / "*.v1.json")))


def max_decisions(repo: Path = REPO) -> int:
    contract = json.loads((repo / "Shared/quality/learner-quality.v1.json").read_text(encoding="utf-8"))
    return contract["thresholds"]["max_decisions_per_anchor"]


def _slug(record_id: str) -> str:
    return record_id.split("-", 1)[1] if "-" in record_id else record_id


def migrate_package(pkg: dict, limit: int) -> dict:
    out = copy.deepcopy(pkg)
    out["schema_version"] = TARGET
    reps = {r["id"]: r for r in out.get("representations", [])}
    anchors: dict[str, list[str]] = {}
    for q in out.get("questions", []):
        if any(e["core"] == "CORE1A" for e in q.get("exposure", [])):
            anchors.setdefault(q["primary_capability_ref"], []).append(q["id"])

    for m in out.get("microtopics", []):
        if "construction_units" in m:
            continue
        path = m.get("teaching_path") or []
        if not path or len(path) > limit:
            continue  # nothing to cover, or a split an author must decide
        rep_ref = (m.get("representation_refs") or [None])[0]
        rep = reps.get(rep_ref) if rep_ref else None
        anchor = (anchors.get(m["primary_capability_ref"]) or [None])[0]
        m["construction_units"] = [{
            "id": f"CU-{_slug(m['id'])}-1",
            "decision_from": "inferential_jump",
            "step_refs": [s["id"] for s in path],
            "representation_ref": rep_ref,
            "reveal_stage_refs": [s["id"] for s in (rep or {}).get("reveal_stages", [])],
            "worked_anchor_ref": anchor,
            "misconception_indexes": list(range(len(m.get("misconceptions", [])))),
            "independent_checks": [],
            "migrated_from": "teaching_path",
        }]

    for q in out.get("questions", []):
        if "hint_ladder" not in q:
            rungs = [(REVEAL_ORDER.get(h.get("reveals"), 1), 0, i, {
                "purpose": HINT_PURPOSE.get(h.get("reveals"), "ORIENT"), "from": f"hints[{i}]",
                "provenance": "SOURCE_HINT" if q.get("origin") == "SOURCE" else "AUTHORED_HINT"})
                for i, h in enumerate(q.get("hints", []))]
            rungs += [(REVEAL_ORDER.get(s.get("reveals"), 1), 1, i, {
                "purpose": SUPPORT_PURPOSE.get(s.get("support_kind"), "CONNECT"), "from": f"scaffolds[{i}]",
                "provenance": "AUTHORED_SCAFFOLD"}) for i, s in enumerate(q.get("scaffolds", []))]
            q["hint_ladder"] = [dict(order=n + 1, **r[3]) for n, r in enumerate(sorted(rungs, key=lambda r: r[:3]))]
        if "representation_roles" not in q:
            bound = next((s.get("representation_ref") for s in (q.get("answer") or {}).get("reasoning_route") or []
                          if s.get("representation_ref")), None)
            stages = [s["visual_stage_ref"] for s in (q.get("answer") or {}).get("reasoning_route") or []
                      if s.get("visual_stage_ref")]
            q["representation_roles"] = {"initial_ref": None, "safe_ref": None, "bound_ref": bound, "stage_refs": stages}
        if "failure_signal" not in q:
            q["failure_signal"] = None
        if "family_exposure" not in q and q.get("family_ref"):
            q["family_exposure"] = {"family_ref": q["family_ref"], "closure": None}
    return out


def dump_like(original: str, before: dict, after: dict) -> str:
    """Serialize `after` in the formatting the file already uses, so a migration diff shows content only."""
    for ascii_ in (False, True):
        text = json.dumps(before, indent=2, ensure_ascii=ascii_)
        if original.rstrip("\n") == text:
            return json.dumps(after, indent=2, ensure_ascii=ascii_) + ("\n" if original.endswith("\n") else "")
    return json.dumps(after, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    limit = max_decisions()
    stale = []
    for path in package_paths():
        pkg = json.loads(path.read_text(encoding="utf-8"))
        new = migrate_package(pkg, limit)
        if new != pkg:
            stale.append(path)
            if args.write:
                path.write_text(dump_like(path.read_text(encoding="utf-8"), pkg, new), encoding="utf-8")
    rel = [str(p.relative_to(REPO)) for p in stale]
    if args.check and rel:
        print("packages not migrated to 0.2.0:\n  " + "\n  ".join(rel), file=sys.stderr)
        return 1
    print(f"{len(package_paths())} packages; {'migrated' if args.write else 'current'}: "
          f"{len(rel) if args.write else len(package_paths()) - len(rel)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
