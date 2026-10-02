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


def _shell_lines(shell: dict) -> list[str]:
    """The header every rendered page carries, and the one control an author or a run must know about: the PDF icon."""
    pp = shell.get("print_policy")
    lines = ["## The shell (every page)", "",
             f"`{shell['id']}` {shell.get('version', '')}: a fixed header with " + ", ".join(f"`{c}`" for c in shell["controls"]) + ".", ""]
    if pp:
        lines += [f"**{pp['control']}** · the PDF icon in the header. {pp['purpose']}", "",
                  f"- Pages: {', '.join(pp['applies_to_roles'])}, in PAGES mode; a single-file page has {pp['single_file_mode'].replace('_', ' ').lower()} (no file beside it).",
                  f"- It opens (in a {pp['opens'].replace('_', ' ').lower()}): the PDF printed from this very page, `{pp['target_pattern']}`; its accessible name is \"{pp['accessible_name']}\".",
                  f"- It is a touch target of at least {pp['target_css_px_min']} px and is {pp['in_print'].lower()} when the page is printed.",
                  f"- It never links: {', '.join(pp['never_linked'])} (a key PDF holds the answers).",
                  f"- {pp['link_must_resolve']}",
                  "- A Core2 question whose source is a verified official past paper also links the paper itself as a PDF: see the `SOURCE_PDF` component.", ""]
    return lines


def _product_rules(policy: dict) -> list[str]:
    """The rules about a whole product, not a page: what it covers, what it may select, how its equations are shown."""
    cov, pro, typ = policy["coverage"], policy["promotion"], policy["typeset"]
    word = {"ADVISORY": "an advisory", "GAP": "a gap"}
    return [
        "## Rules about a whole product", "",
        f"**Coverage** (component `{cov['component']}`, duty `{cov['duty']}`). {cov['purpose']}", "",
        f"- The denominator: {cov['denominator']}",
        f"- The rule: {cov['rule']}",
        f"- A shortfall is {word[cov['held_to']['FLOOR']]} for an official product (held to the floor) and {word[cov['held_to']['REFERENCE']]} for new authoring (held to the reference).",
        f"- {cov['sources']}", "",
        f"**Promotion.** {pro['purpose']}", "",
        f"- Selectable statuses: {', '.join(pro['selectable_statuses'])}. Refused: {', '.join(pro['refused_statuses'])}, with `{pro['refusal']}`; it applies to {', '.join(pro['applies_to'])}.",
        f"- {pro['note']}", "",
        f"**Typeset** (component `{typ['component']}`, duty `{typ['duty']}`). {typ['purpose']}", "",
        f"- {typ['rule']}",
        f"- It is {word[typ['held_to']['FLOOR']]} for an official product and {word[typ['held_to']['REFERENCE']]} for new authoring.", "",
    ]


def _standalone_lines(shell: dict) -> list[str]:
    """What a page that did not come through the renderer is held to: the shell's own policies, read from its bytes."""
    sp = shell.get("standalone_policy")
    if not sp:
        return []
    audit = sp["browser_audit"]
    lines = ["## Pages that do not come through the renderer", "",
             sp["purpose"], "",
             f"Governed roots: {', '.join(f'`{r}/`' for r in sp['governed_roots'])}. A page there that is not listed in the ledger has no findings; an unknown page fails closed. "
             f"Checker: `{sp['checker']}`; zoom is never limited below {sp['zoom_max_scale_min']}x.", "",
             "| Rule | Held | Assurance type | Executes | What it asks |", "|---|---|---|---|---|"]
    lines += [f"| `{r['id']}` | {'blocks' if r['severity'] == 'BLOCK' else 'said'} | `{r['assurance_type']}` | `{r['executes']}` | {r['statement']} |" for r in sp["rules"]]
    lines += ["", f"Ledger (`{sp['ledger']}`): {sp['ledger_rule']}", "",
              f"Browser audit (`{audit['tool']} --profile {audit['profile']}`): measures {', '.join(audit['measures'])}. {audit['note']}", ""]
    return lines


def _admission_lines(policy: dict) -> list[str]:
    """How a question record gets into a library, and how a digest is kept the same on every machine."""
    adm, ev = policy["admission"], policy["evidence"]
    return ["## Rules about a record and its evidence", "",
            f"**Admission.** {adm['purpose']} Authority: {', '.join(f'`{a}`' for a in adm['authority'])}.", "",
            *[f"- `{pt['id']}` ({'blocks' if pt['severity'] == 'BLOCK' else 'said'}; evidence of type `{pt['assurance_type']}`): {pt['statement']}" for pt in adm["points"]],
            f"- {adm['note']}", "",
            f"**Evidence.** {ev['purpose']} Line endings: {ev['line_endings']} (`{ev['attributes_file']}`). {ev['note']}", ""]


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
        *_shell_lines(registry["shell"]),
        *_standalone_lines(registry["shell"]),
        *_product_rules(policy),
        *_admission_lines(policy),
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
            *([f"Route: the learner meets the steps in this order, each after the one before is done: " + " → ".join(blueprint["route"]) + ".", ""]
              if blueprint.get("route") else []),
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
