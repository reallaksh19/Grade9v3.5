#!/usr/bin/env python3
"""M2: give each inherited package an honest unit home without inventing design work."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import package_migrate  # noqa: E402


def unit_path(package_path: Path) -> Path:
    slug = package_path.name.removesuffix(".v1.json")
    return REPO / package_path.parent.parent.name / "units" / slug / "UNIT.md"


def scaffold(package_path: Path) -> str:
    package = json.loads(package_path.read_text(encoding="utf-8"))
    slug = package_path.name.removesuffix(".v1.json")
    nodes = sorted({ext["grade9v3:research_node"]
                    for kind in ("microtopics", "questions") for row in package.get(kind, [])
                    if (ext := row.get("extensions") or {}).get("grade9v3:research_node")})
    grades = sorted({m["grade"] for m in package.get("curriculum_mappings", []) if isinstance(m.get("grade"), int)})
    grade = grades[0] if len(grades) == 1 else None
    prerequisites = sorted({ref for m in package.get("microtopics", []) for ref in m.get("prerequisite_refs", [])})
    microtopics = [m["id"] for m in package.get("microtopics", [])]
    sources = [r["id"] for r in package.get("resources", [])]
    y = lambda value: json.dumps(value, ensure_ascii=False)
    rel = package_path.relative_to(REPO).as_posix()
    return (f"---\nunit: {slug}\npackage: {rel}\nowner_agent: UNASSIGNED\n"
            f"spine_nodes: {y(nodes)}\nmicrotopics: {y(microtopics)}\nsources: {y(sources)}\ninventories: []\n"
            f"grade_profile:\n  base_grade: {y(grade)}\n  assumed_prerequisites: {y(prerequisites)}\n"
            f"  enrichment: []\ncoverage:\n  mode: CURATED_SELECTION\n  inventory: null\n"
            f"budget_usd: null\n---\n\n# {package['title']}\n\n"
            f"Existing package scope (carried forward): {package.get('scope_summary', '').strip()}\n\n"
            "## Status notes\n\n"
            "- This is an inherited package. Unit ownership, source readback and budget are not assigned by this migration.\n"
            "- `spine_nodes`, sources, grade and prerequisites above are copied from explicit package data; empty or null means unrecorded.\n"
            "- No design note, self-critique, prototype review or Owner calibration is claimed here.\n"
            "- The selected product remains governed by its existing manifest; an inventory denominator is not yet declared.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    paths = package_migrate.package_paths()
    missing = []
    for package_path in paths:
        target = unit_path(package_path)
        if not target.is_file():
            missing.append(target)
            if args.write:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(scaffold(package_path), encoding="utf-8", newline="\n")
    if missing and not args.write:
        print("\n".join(str(p.relative_to(REPO)) for p in missing))
        return 1
    print(f"M2: {len(paths)} packages, {len(missing)} scaffold(s) written" if args.write
          else f"M2: all {len(paths)} unit homes present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
