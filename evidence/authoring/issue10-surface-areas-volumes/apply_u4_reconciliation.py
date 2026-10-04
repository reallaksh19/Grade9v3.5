#!/usr/bin/env python3
"""Apply PR #8 U4: representation/hint depth must follow semantic applicability.

This script is an idempotent branch-maintenance helper for the Issue #10 cold-run.
It edits the authoritative Blueprint/QC files, then regenerates the derived blueprint spec.
It exists so the cold-run can make the discovered policy conflict durable rather than
working around it with decorative figures.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
BLUEPRINT = REPO / "Shared/web/interactive-page-blueprints.v1.json"
QUALITY = REPO / "Shared/quality/learner-quality.v1.json"
QUALITY_TOOL = REPO / "Shared/tools/quality_contract.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_blueprint() -> None:
    data = load(BLUEPRINT)
    for bp in data["blueprints"]:
        if bp["id"] == "BP-CORE1A-CONSTRUCTION":
            visual = next(c for c in bp["components"] if c["id"] == "STAGED_VISUAL")
            visual["level"] = "EXPECTED"
            visual["purpose"] = (
                "When a spatial or mechanism representation materially helps the construction, show it as a "
                "picture that builds stage by stage. A construction with no useful visual is explicitly waived "
                "by the authored record; no decorative figure is invented."
            )
            visual["authoring"]["hint"] = (
                "First decide whether a staged visual has a real semantic job for this construction. When it does, "
                "representation_ref names a package representation with an authored accessible SVG and at least 2 "
                "data-g9-stage-id groups; reveal_stages names the useful build-up. The reference depth is 3 stages "
                "(4 for a D3/D4 crux), not a semantic pass count. When a visual is genuinely not applicable, waive "
                "STAGED_VISUAL with a written reason instead of drawing decoration."
            )
        if bp["id"] == "BP-CORE2-SOURCE-QUESTION":
            rep = next(c for c in bp["components"] if "figure_refs" in (c.get("source") or []))
            rep["purpose"] = (
                "Show a question-aligned representation only when it materially helps the learner interpret, "
                "translate or reason about the question; otherwise preserve the explicit applicability waiver."
            )
            rep["authoring"]["hint"] = (
                "Decide representation applicability from the question's semantic review. If useful, add an "
                "accessible authored SVG drawn only from the question data and name it in figure_refs. If a figure "
                "would be decorative or would leak protected work, waive REPRESENTATION with a written reason."
            )
            ladder = next(c for c in bp["components"] if "scaffolds" in (c.get("source") or []))
            ladder["authoring"]["hint"] = (
                "Author question-specific scaffolds for the semantic jobs the resolved QRT requires: clarify the "
                "learner-relative obstacle, connect to demonstrated knowledge, and open the route toward the crux "
                "while preserving the learner-owned move. Add further rungs only when they do useful work. The "
                "3-rung D1/D2 and 5-rung D3/D4 values are reference depth, not semantic pass counts; never create "
                "filler merely to reach a number. Each rung keeps typed support_kind/reveals/learner_stage and a "
                "supports_move_ref, and pre-solution support must not reveal the answer."
            )
    write(BLUEPRINT, data)


def patch_quality_contract() -> None:
    data = load(QUALITY)
    data["version"] = "1.8.1"
    for rule in data["rules"]:
        if rule["id"] == "C1A-REPRESENTATION-BRIDGE":
            rule["check"]["waiver_component"] = "STAGED_VISUAL"
            rule["text"] = (
                "A Core1A construction mounts a useful representation when applicable; an explicit authored "
                "STAGED_VISUAL waiver records a genuine not-applicable case instead of forcing decoration."
            )
        elif rule["id"] == "C1A-STAGED-REPRESENTATION":
            rule["text"] = (
                "When a Core1A representation is present, it builds in at least two stages that follow the construction."
            )
    write(QUALITY, data)

    text = QUALITY_TOOL.read_text(encoding="utf-8")
    old = '''@op("figures_min")\ndef _figures_min(unit, check, ctx):\n    figs = [f for f in unit["figures"] if f["stage"] in check["stages"]]\n    out = []\n    if len(figs) < check["min"]:\n        out.append(f"{len(figs)} figure(s) at stage {'/'.join(check['stages'])}; need {check['min']}")\n    if check.get("no_unmounted_refs") and unit.get("representation_refs_unmounted"):\n        out.append("representation named but not shown: " + ", ".join(unit["representation_refs_unmounted"][:3]))\n    return out\n'''
    new = '''@op("figures_min")\ndef _figures_min(unit, check, ctx):\n    waiver_component = check.get("waiver_component")\n    if waiver_component:\n        waived = unit.get("waived") or {}\n        construction_units = unit.get("construction_units") or []\n        fully_waived = (\n            waiver_component in waived\n            or (construction_units and all(\n                f"{waiver_component}@{cu}" in waived for cu in construction_units\n            ))\n        )\n        if fully_waived:\n            return []\n    figs = [f for f in unit["figures"] if f["stage"] in check["stages"]]\n    out = []\n    if len(figs) < check["min"]:\n        out.append(f"{len(figs)} figure(s) at stage {'/'.join(check['stages'])}; need {check['min']}")\n    if check.get("no_unmounted_refs") and unit.get("representation_refs_unmounted"):\n        out.append("representation named but not shown: " + ", ".join(unit["representation_refs_unmounted"][:3]))\n    return out\n'''
    if old in text:
        text = text.replace(old, new)
    elif new not in text:
        raise SystemExit("quality_contract figures_min body no longer matches expected authority")
    QUALITY_TOOL.write_text(text, encoding="utf-8")


def main() -> None:
    patch_blueprint()
    patch_quality_contract()
    subprocess.run(["python3", "Shared/tools/blueprint_spec.py", "--write"], cwd=REPO, check=True)
    print("U4 applicability reconciliation applied")


if __name__ == "__main__":
    main()
