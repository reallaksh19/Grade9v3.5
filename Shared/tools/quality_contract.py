#!/usr/bin/env python3
"""Judge what a learner product shows against the learner quality contract.

The contract (Shared/quality/learner-quality.v1.json) is a list of subject-neutral rules over
a learner observation (Shared/quality/learner-observation.schema.json). An observation is
produced from delivered files by Shared/tools/quality_observe.py, or written by hand for a
sample unit. The subject adapter (<Subject>/adapter/QualityVocabulary.json) supplies the
subject's figure kinds and check types.

Usage:
    quality_contract.py --check                      # the contract itself is well formed
    quality_contract.py evaluate OBSERVATION.json    # findings for one observation
    quality_contract.py calibrate                    # corpus: negatives fail, references pass
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

CONTRACT = REPO / "Shared/quality/learner-quality.v1.json"
OBS_SCHEMA = REPO / "Shared/quality/learner-observation.schema.json"
ROLES = ["CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B"]
OPS: dict = {}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def contract() -> dict:
    return load_json(CONTRACT)


def vocabulary(subject: str, repo: Path = REPO) -> dict:
    path = repo / subject / "adapter" / "QualityVocabulary.json"
    return load_json(path) if path.is_file() else {}


def op(name):
    def register(fn):
        OPS[name] = fn
        return fn
    return register


def _threshold(check: dict, key: str, c: dict):
    return c["thresholds"][check[key + "_from"]] if key + "_from" in check else check.get(key)


# ------------------------------------------------------------------ unit ops
# Each unit op returns a list of problem strings for one unit (empty = pass).

@op("blocks_present")
def _blocks_present(unit, check, ctx):
    missing = [b for b in check["blocks"] if not unit["blocks"].get(b, "").strip()]
    out = [f"missing block(s): {', '.join(missing)}"] if missing else []
    need = check.get("min_lineage_refs")
    if need and len(unit.get("lineage_refs", [])) < need:
        out.append(f"{len(unit.get('lineage_refs', []))} lineage reference(s); need {need}")
    return out


@op("figures_min")
def _figures_min(unit, check, ctx):
    figs = [f for f in unit["figures"] if f["stage"] in check["stages"]]
    out = []
    if len(figs) < check["min"]:
        out.append(f"{len(figs)} figure(s) at stage {'/'.join(check['stages'])}; need {check['min']}")
    if check.get("no_unmounted_refs") and unit.get("representation_refs_unmounted"):
        out.append("representation named but not shown: " + ", ".join(unit["representation_refs_unmounted"][:3]))
    return out


@op("figure_reveal_stages_min")
def _reveal_stages(unit, check, ctx):
    need = _threshold(check, "min", ctx["contract"])
    flat = [f for f in unit["figures"] if f.get("reveal_stages", 1) < need]
    return [f"{len(flat)} figure(s) with fewer than {need} reveal stages"] if flat else []


@op("decisions_per_anchor_max")
def _decisions(unit, check, ctx):
    limit = _threshold(check, "max", ctx["contract"])
    decisions, anchors = unit.get("decisions", 0), max(unit.get("worked_anchors", 0), 0)
    if decisions and (anchors == 0 or decisions / anchors > limit):
        return [f"{decisions} decisions carried by {anchors} worked anchor(s); at most {limit} per anchor"]
    return []


@op("prerequisites_bridged")
def _prereqs(unit, check, ctx):
    open_ = [p for p in unit.get("prerequisites_assumed", []) if p not in unit.get("prerequisites_bridged", [])]
    return [f"{len(open_)} assumed prerequisite(s) not linked to a teaching unit: " + "; ".join(p[:60] for p in open_[:3])] if open_ else []


@op("attempt_present")
def _attempt(unit, check, ctx):
    return [] if unit["attempt"] else ["no attempt control"]


@op("reveals_gated")
def _reveals_gated(unit, check, ctx):
    out = []
    for block in check["blocks"]:
        if block not in unit["blocks"]:
            continue
        holders = [r for r in unit["reveals"] if block in r["blocks"]]
        if not holders:
            out.append(f"{block} is visible without any reveal")
        elif not all(r["gated"] for r in holders) or not unit["attempt"]:
            out.append(f"{block} can be revealed before an attempt")
    return out


@op("blocks_only_in_reveal")
def _only_in_reveal(unit, check, ctx):
    out = []
    for block in check["blocks"]:
        if block not in unit["blocks"]:
            continue
        holders = [r for r in unit["reveals"] if block in r["blocks"]]
        if not holders:
            out.append(f"{block} is shown immediately")
        elif check.get("gated") and not all(r["gated"] for r in holders):
            out.append(f"{block} reveal is not gated on an attempt")
    return out


@op("block_order")
def _order(unit, check, ctx):
    order = unit["block_order"]
    if check["first"] not in order:
        return [f"{check['first']} absent"]
    i = order.index(check["first"])
    early = [b for b in check["before"] if b in order and order.index(b) < i]
    return [f"{', '.join(early)} before {check['first']}"] if early else []


@op("support_levels_min")
def _support(unit, check, ctx):
    need = _threshold(check, "min", ctx["contract"])
    n = len([s for s in unit["support_levels"] if s.strip()])
    return [f"{n} support level(s); need {need}"] if n < need else []


@op("no_placeholders")
def _no_placeholders(unit, check, ctx):
    return [f"placeholder shown: {p[:70]}" for p in unit["placeholders"]]


@op("metadata_exact")
def _metadata_exact(unit, check, ctx):
    # Legacy calibration/reference observations predate learner metadata. render_core observations
    # always carry this key (including an empty list), so production absence still fails closed.
    if "metadata" not in unit:
        return []
    rows = unit["metadata"]
    expected = set(check["kinds"])
    present = [row.get("kind") for row in rows]
    problems = []
    missing = sorted(expected - set(present))
    extra = sorted(set(present) - expected)
    duplicates = sorted(kind for kind in set(present) if present.count(kind) != 1)
    if missing:
        problems.append("missing metadata kind(s): " + ", ".join(missing))
    if extra:
        problems.append("unexpected metadata kind(s): " + ", ".join(extra))
    if duplicates:
        problems.append("metadata kind must occur exactly once: " + ", ".join(duplicates))
    for row in rows:
        if not all(isinstance(row.get(field), str) and row[field].strip()
                   for field in ("kind", "ref", "value", "display_name", "label")):
            problems.append(f"incomplete metadata item: {row.get('kind')}")
    return problems


@op("pre_attempt_figures_partial")
def _pre_attempt_partial(unit, check, ctx):
    full = [f for f in unit["figures"] if f["stage"] == "PRE_ATTEMPT" and f.get("stages_total", 1) > 1
            and f.get("reveal_stages", 1) >= f["stages_total"]]
    return [f"{len(full)} pre-attempt figure(s) show every stage, including the result"] if full else []


@op("pre_attempt_markup_withheld")
def _pre_attempt_withheld(unit, check, ctx):
    out = []
    for f in unit["figures"]:
        if f["stage"] != "PRE_ATTEMPT":
            continue
        if f.get("stages_in_dom", 0) > f.get("reveal_stages", 1):
            out.append(f"a pre-attempt figure carries {f['stages_in_dom']} stage groups in its markup but shows "
                       f"{f.get('reveal_stages', 1)}; hidden stages still reach the DOM, tooltips and screen readers")
        if f.get("asset_text") and f.get("stages_total", 1) > f.get("reveal_stages", 1):
            out.append("a pre-attempt figure keeps its asset's <title>/<desc>, which describe the whole figure")
        if f.get("caption_source") == "purpose":
            out.append("a pre-attempt figure is captioned with its representation's design purpose, which may name the "
                       "result; caption it with the shown stages only")
    return out


@op("figures_titled")
def _titled(unit, check, ctx):
    n = sum(1 for f in unit["figures"] if not f["titled"])
    return [f"{n} figure(s) without a title"] if n else []


@op("figure_kinds_in_vocabulary")
def _kinds(unit, check, ctx):
    known = set(ctx["vocabulary"].get("representation_kinds", []))
    bad = sorted({f["kind"] for f in unit["figures"] if f.get("kind") and f["kind"] not in known})
    return [f"figure kind not in {ctx['subject']} vocabulary: {', '.join(bad)}"] if bad else []


@op("check_types_in_vocabulary")
def _check_types(unit, check, ctx):
    known = set(ctx["vocabulary"].get("check_types", []))
    bad = sorted({t for t in unit.get("check_types", []) if t not in known})
    return [f"check type not in {ctx['subject']} vocabulary: {', '.join(bad)}"] if bad else []


UNIT_OPS = set(OPS)


# ------------------------------------------------------------------ page and product ops

@op("distinct_across_page")
def _distinct(page, check, ctx):
    out = []
    for field in check["fields"]:
        seen: dict[str, list[str]] = {}
        for unit in page["units"]:
            values = unit["support_levels"] if field == "support_levels" else [unit["blocks"].get(field, "")]
            for v in values:
                key = re.sub(r"\s+", " ", v.strip().lower())
                if key:
                    seen.setdefault(key, []).append(unit["id"])
        repeated = {k: v for k, v in seen.items() if len(set(v)) > 1}
        if repeated:
            text, units = next(iter(repeated.items()))
            out.append(f"{field} repeats across {len(set(units))} items: \"{text[:60]}\"")
    return out


@op("figures_specific_across_page")
def _figures_specific(page, check, ctx):
    """A teaching or pre-attempt figure is staged for one unit or question, not reused for others."""
    mounts: dict[str, set] = {}
    for unit in page["units"]:
        for f in unit["figures"]:
            if f["stage"] in check["stages"] and f.get("representation_ref"):
                mounts.setdefault(f["representation_ref"], set()).add(f.get("mount") or unit["id"])
    shared = {rep: sorted(ms) for rep, ms in mounts.items() if len(ms) > 1}
    return [f"{rep} is the {'/'.join(check['stages']).lower()} figure for {len(ms)} different units or questions "
            f"({', '.join(ms[:3])}{'…' if len(ms) > 3 else ''}); each needs a figure that depicts its own situation"
            for rep, ms in shared.items()]


@op("page_figures_min")
def _page_figures(page, check, ctx):
    n = len(page.get("figures", [])) + sum(len(u["figures"]) for u in page["units"])
    return [f"{n} figure(s) on the page; need {check['min']}"] if n < check["min"] else []


@op("page_flag")
def _page_flag(page, check, ctx):
    shell = page.get("shell")
    if shell is None:
        return None  # not a web page
    return [] if shell.get(check["field"]) else [f"page {check['field']} absent"]


@op("rendered_zero")
def _rendered_zero(page, check, ctx):
    r = page.get("rendered")
    if r is None or check["field"] not in r:
        return None
    return [] if r[check["field"]] == 0 else [f"{r[check['field']]} {check['field'].replace('_', ' ')}"]


@op("rendered_flag")
def _rendered_flag(page, check, ctx):
    r = page.get("rendered")
    if r is None or check["field"] not in r:
        return None
    return [] if r[check["field"]] else [f"{check['field'].replace('_', ' ')} absent"]


PAGE_OPS = set(OPS) - UNIT_OPS


@op("product_no_escape_states")
def _escape(obs, check, ctx):
    return [f"escape state shown to the learner: {', '.join(obs['escape_states'][:5])}"] if obs["escape_states"] else []


@op("product_render_stamp")
def _stamp(obs, check, ctx):
    p = obs["provenance"]
    return [] if p["render_stamp"] and not p["hand_authored"] else ["no governed-renderer stamp" + (" (hand-authored)" if p["hand_authored"] else "")]


@op("product_roles")
def _roles(obs, check, ctx):
    if "roles_rendered" not in obs:
        return None
    missing = [r for r in check["roles"] if r not in obs["roles_rendered"]]
    return [f"roles not rendered: {', '.join(missing)}"] if missing else []


@op("product_shared_atlas")
def _atlas(obs, check, ctx):
    a = obs.get("atlas")
    if not a or not a["present"]:
        return None
    return [] if a["shared_runtime"] else ["Atlas is a per-job page, not the shared Atlas"]


@op("product_print_from_page")
def _print(obs, check, ctx):
    p = obs.get("print")
    if not p or not p["present"]:
        return None
    out = []
    if not p["from_page"]:
        out.append("print product made by a separate generator, not printed from the page")
    if p["figures"] < p["web_figures"]:
        out.append(f"print has {p['figures']} figure(s); the web page has {p['web_figures']}")
    return out


PRODUCT_OPS = set(OPS) - UNIT_OPS - PAGE_OPS


# ------------------------------------------------------------------ evaluation

def _applies(rule: dict, role: str) -> bool:
    return "*" in rule["roles"] or role in rule["roles"]


def evaluate(obs: dict, c: dict | None = None, repo: Path = REPO) -> dict:
    """Findings (one per rule x location) and the rules that were not measured."""
    c = c or contract()
    ctx = {"contract": c, "vocabulary": vocabulary(obs["subject"], repo), "subject": obs["subject"]}
    findings: list[dict] = []
    not_measured: set[str] = set()

    def add(rule, where, problems):
        for p in problems:
            findings.append({"rule": rule["id"], "severity": rule["severity"], "family": rule["family"],
                             "audit_refs": rule["audit_refs"], "where": where, "detail": p})

    for rule in c["rules"]:
        name = rule["check"]["op"]
        fn = OPS[name]
        if name in PRODUCT_OPS:
            res = fn(obs, rule["check"], ctx)
            if res is None:
                continue
            add(rule, obs["product_id"], res)
            continue
        for page in obs["pages"]:
            if not _applies(rule, page["role"]):
                continue
            if name in PAGE_OPS:
                res = fn(page, rule["check"], ctx)
                if res is None:
                    if rule["measure"] == "RENDERED":
                        not_measured.add(rule["id"])
                    continue
                add(rule, page["path"], res)
                continue
            for unit in page["units"]:
                if rule.get("unit_kind") and unit["kind"] != rule["unit_kind"]:
                    continue
                add(rule, f"{page['path']}#{unit['id']}", fn(unit, rule["check"], ctx))
    rules_failed = sorted({f["rule"] for f in findings})
    return {"product_id": obs["product_id"], "findings": findings, "rules_failed": rules_failed,
            "audit_refs_caught": sorted({a for f in findings for a in f["audit_refs"]}),
            "not_measured": sorted(not_measured), "passed": not findings}


def validate_observation(obs: dict) -> list[str]:
    try:
        import jsonschema  # noqa: PLC0415
    except ModuleNotFoundError:
        return []
    v = jsonschema.Draft202012Validator(load_json(OBS_SCHEMA))
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(obs)]


# ------------------------------------------------------------------ contract self-check

def check_contract(c: dict | None = None) -> list[str]:
    c = c or contract()
    problems = []
    ids = [r["id"] for r in c["rules"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate rule ids")
    grammar_steps = {f"{ref}:{step}" for ref, row in c["references"].items() for step in row["grammar"]}
    for r in c["rules"]:
        if r["check"]["op"] not in OPS:
            problems.append(f"{r['id']}: unknown op {r['check']['op']}")
        if r["family"] not in c["families"] or r["measure"] not in c["measures"]:
            problems.append(f"{r['id']}: unknown family or measure")
        for role in r["roles"]:
            if role != "*" and role not in ROLES:
                problems.append(f"{r['id']}: unknown role {role}")
        for block in r["check"].get("blocks", []):
            roles = ROLES if "*" in r["roles"] else r["roles"]
            if not any(block in c["blocks"][role] for role in roles):
                problems.append(f"{r['id']}: block {block} is not a contract block of {roles}")
        for key in ("min_from", "max_from"):
            if key in r["check"] and r["check"][key] not in c["thresholds"]:
                problems.append(f"{r['id']}: unknown threshold {r['check'][key]}")
        if r.get("grammar") and r["grammar"] not in grammar_steps:
            problems.append(f"{r['id']}: grammar step {r['grammar']} is not a reference grammar step")
    covered = {r["grammar"] for r in c["rules"] if r.get("grammar")} | set(c.get("grammar_step_notes", {}))
    for step in sorted(grammar_steps - covered):
        problems.append(f"reference grammar step not encoded by any rule: {step}")
    return problems


# ------------------------------------------------------------------ calibration

def calibrate(repo: Path = REPO) -> dict:
    """Negative specimens must fail for every expected finding; R2 must pass its grammar rules."""
    from Shared.tools import quality_observe  # noqa: PLC0415
    c = contract()
    manifest = load_json(repo / "benchmarks/quality-calibration/manifest.v1.json")
    rows = []
    for spec in manifest["specimens"]:
        obs = quality_observe.observe_specimen(spec, repo)
        res = evaluate(obs, c, repo)
        expected = {f["id"] for f in spec["expected_findings"]}
        missed = sorted(expected - set(res["audit_refs_caught"]))
        extra = sorted(r for r in res["rules_failed"]
                       if not set(next(x for x in c["rules"] if x["id"] == r)["audit_refs"]) & expected)
        unreviewed = sorted(set(extra) - set(spec.get("acknowledged_extra_rules", {})))
        rows.append({"id": spec["id"], "kind": "NEGATIVE", "ok": not missed and not unreviewed and not res["passed"],
                     "unreviewed_extra_rules": unreviewed,
                     "expected": sorted(expected), "missed": missed, "rules_failed": res["rules_failed"],
                     "extra_rules_failed": extra, "not_measured": res["not_measured"]})
    for ref in manifest["references"]:
        ref_role = c["references"].get(ref["id"], {}).get("role")
        rule_ids = [r["id"] for r in c["rules"] if (r.get("grammar") or "").startswith(ref["id"] + ":")
                    and (ref_role is None or _applies(r, ref_role))]
        if ref.get("custody") != "REPOSITORY":
            rows.append({"id": ref["id"], "kind": "POSITIVE", "ok": True, "status": "NOT_LOCATED",
                         "grammar_rules": rule_ids})
            continue
        observations = quality_observe.observe_reference(ref, repo)
        results = [evaluate(obs, c, repo) for obs in observations]
        findings = [f for res in results for f in res["findings"]]
        failing = sorted({f["rule"] for f in findings if f["rule"] in rule_ids})
        rows.append({"id": ref["id"], "kind": "POSITIVE", "ok": not failing, "status": "CALIBRATED",
                     "units": sum(len(p["units"]) for obs in observations for p in obs["pages"]),
                     "grammar_rules": rule_ids, "failing_grammar_rules": failing,
                     "other_rules_failed": sorted({f["rule"] for f in findings} - set(rule_ids)),
                     "sample": [f for f in findings if f["rule"] in failing][:5]})
    return {"rows": rows, "passed": all(r["ok"] for r in rows)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="check the contract is well formed")
    sub = parser.add_subparsers(dest="cmd")
    e = sub.add_parser("evaluate")
    e.add_argument("observation")
    sub.add_parser("calibrate")
    args = parser.parse_args(argv)
    if args.check or not args.cmd:
        problems = check_contract()
        for p in problems:
            print(p, file=sys.stderr)
        c = contract()
        print(f"learner quality contract {c['version']}: {len(c['rules'])} rules, {len(problems)} problems")
        if problems:
            return 1
    if args.cmd == "evaluate":
        obs = load_json(Path(args.observation))
        errors = validate_observation(obs)
        for err in errors:
            print("OBSERVATION_INVALID:", err, file=sys.stderr)
        res = evaluate(obs)
        for f in res["findings"]:
            print(f"{f['severity']} {f['rule']:28s} {f['where']}: {f['detail']}")
        print(f"{res['product_id']}: {len(res['findings'])} finding(s), {len(res['rules_failed'])} rule(s) failed"
              + (f"; not measured: {', '.join(res['not_measured'])}" if res["not_measured"] else ""))
        return 1 if errors or res["findings"] else 0
    if args.cmd == "calibrate":
        report = calibrate()
        for r in report["rows"]:
            mark = "ok " if r["ok"] else "BAD"
            if r["kind"] == "NEGATIVE":
                print(f"{mark} {r['id']:3s} negative: caught {len(r['expected']) - len(r['missed'])}/{len(r['expected'])} expected"
                      + (f"; MISSED {', '.join(r['missed'])}" if r["missed"] else "")
                      + (f"; also fails (reviewed) {', '.join(sorted(set(r['extra_rules_failed']) - set(r['unreviewed_extra_rules'])))}"
                         if set(r["extra_rules_failed"]) - set(r["unreviewed_extra_rules"]) else "")
                      + (f"; UNREVIEWED extra failures {', '.join(r['unreviewed_extra_rules'])}" if r["unreviewed_extra_rules"] else ""))
            else:
                print(f"{mark} {r['id']:3s} positive: {r['status']}"
                      + (f", {r['units']} units, grammar rules {len(r['grammar_rules'])}" if r["status"] == "CALIBRATED" else "")
                      + (f"; FAILS {', '.join(r['failing_grammar_rules'])}" if r.get("failing_grammar_rules") else "")
                      + (f"; outside its grammar also fails {', '.join(r['other_rules_failed'])}" if r.get("other_rules_failed") else ""))
                for f in r.get("sample", []):
                    print(f"      {f['rule']} {f['where']}: {f['detail']}")
        print("calibration " + ("passed" if report["passed"] else "FAILED"))
        return 0 if report["passed"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
