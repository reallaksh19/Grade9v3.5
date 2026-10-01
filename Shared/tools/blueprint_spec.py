#!/usr/bin/env python3
"""Write the readable page specification of the blueprints that declare components.

The blueprint registry (Shared/web/interactive-page-blueprints.v1.json) is the one source of what a Core page
shows, in what layout, how much of it matters and how an author supplies it. The renderer builds pages from it,
the quality gate judges pages against it and the owner-bank scaffold is cut from it. This document is a view of
the same data for a person or an agent about to author a page; it is generated and never edited.

    python3 Shared/tools/blueprint_spec.py --write
    python3 Shared/tools/blueprint_spec.py --check
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import web_blueprint_contract as blueprints  # noqa: E402

OUT = REPO / "docs/specs/PAGE-BLUEPRINT-COMPONENTS.md"
LEVEL_WORDS = {
    "REQUIRED": "Required: a page without it is a gap, and the quality gate fails it.",
    "EXPECTED": "Expected: an official page missing it carries an advisory naming the field to author; new authoring "
                "must supply it or waive it with a written reason, else it is a gap.",
    "OPTIONAL": "Optional: shown when the record has it.",
}


def _depth(component: dict) -> str:
    floor, target = component.get("min_items"), component.get("target_items")
    by_band = component.get("target_items_by_band")
    if not floor:
        return ""
    if by_band:
        shown = ", ".join(f"{band} {count}" for band, count in sorted(by_band.items()))
        return f" · at least {floor} item(s); the reference has {shown} by difficulty band"
    return f" · at least {floor} item(s)" + (f" (the reference has {target})" if target and target != floor else "")


def render(registry: dict | None = None) -> str:
    registry = registry or blueprints.load_registry()
    policy = registry["component_policy"]
    lines = [
        "# Page blueprint components",
        "",
        "Generated from `Shared/web/interactive-page-blueprints.v1.json` by `Shared/tools/blueprint_spec.py`. Do not edit.",
        "To change what a page shows, change the blueprint; the renderer, the quality gate and the owner-bank scaffold follow.",
        "",
        f"Registry {registry['registry_version']}. Levels: " + " ".join(f"**{k}**: {v}" for k, v in policy["levels"].items()),
        "",
        f"Depth: {policy['depth']}",
        "",
        f"Waivers: {policy['waivers']}",
        "",
        f"Held to: {policy['held_to']}",
        "",
    ]
    for blueprint in registry["blueprints"]:
        if not blueprints.components(blueprint):
            continue
        policy_row = blueprint["responsive_policy"]
        lines += [
            f"## {blueprint['id']}@{blueprint['version']} ({', '.join(blueprint['core_roles'])})",
            "",
            f"Learner job: {blueprint['learner_job']}",
            "",
            f"Theme: opens {blueprint.get('presentation_policy', {}).get('default_theme', 'light')}, and the learner can switch.",
            "",
            f"Layout: from {policy_row.get('expanded_min_px', 1100)} px wide, the primary column is "
            f"{policy_row['primary_fraction'] * 100:g}% and the support column {policy_row['support_fraction'] * 100:g}%"
            + ("; the support column stays in view while the primary column scrolls" if policy_row.get("support_sticky") else "")
            + ". Narrower, everything is one column, primary first.",
            "",
            "| Slot | Column | Kept |",
            "|---|---|---|",
        ]
        for slot in blueprint["slots"]:
            lines.append(f"| `{slot['id']}` | {slot['column']} | {'always' if slot['required'] else 'when it has content'} |")
        lines.append("")
        for level in blueprints.LEVELS:
            rows = [c for c in blueprints.components(blueprint) if c["level"] == level]
            if not rows:
                continue
            lines += [f"### {level.title()} components", "", LEVEL_WORDS[level], ""]
            for c in rows:
                where = f"slot `{c['slot']}`" + (f", inside {c['parent']}" if c.get("parent") else "") \
                    + (", once per construction unit" if c.get("repeat") else "")
                lines += [f"**{c['id']}** · {where} · {c['presentation']}{_depth(c)}", "",
                          f"- The learner gets: {c['purpose']}",
                          f"- The reference page: {c['benchmark']}"]
                if c.get("source"):
                    lines.append("- Record fields: " + ", ".join(f"`{s}`" for s in c["source"]))
                hint = (c.get("authoring") or {}).get("hint")
                if hint:
                    lines.append(f"- To author it: {hint}")
                lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = render()
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if current != text:
            print(f"{OUT.relative_to(REPO)} is stale; run Shared/tools/blueprint_spec.py --write")
            return 1
        print(f"{OUT.relative_to(REPO)} is current")
        return 0
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUT.relative_to(REPO)}")
        return 0
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
