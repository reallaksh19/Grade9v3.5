#!/usr/bin/env python3
"""Advisory rendered quality report: what does the built product appear to contain?

Runs on a render_core product directory:
1. Reads the pages (data-g9-* markers) into a learner observation and judges it against the
   learner quality contract (Shared/quality/learner-quality.v1.json).
2. Measures the rendered pages in Chromium (tools/site-audit/core-page-audit.mjs) for the
   RENDERED rules (touch targets, stage-support layout), unless --static.
3. Checks continuity across the Cores:
   - Core1A and Core1B cover the same units;
   - every Core2B lineage link and every repair link resolves to a rendered unit.
4. Writes a tool-written report (Shared/quality/gate-report.schema.json) of checks, digests and
   findings. The verdict is computed; no field accepts a free-text claim.

PASS needs all of:
- no S0, S1 or S2 finding;
- no continuity finding;
- not a draft;
- every RENDERED rule measured.

Usage:
    quality_gate.py DIR --subject Physics --product-id P [--static] [--report out.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import quality_contract, quality_observe  # noqa: E402

REPORT_SCHEMA = REPO / "Shared/quality/gate-report.schema.json"
BLOCKING = {"S0", "S1", "S2"}


def measure(folder: Path) -> dict | None:
    out = Path(tempfile.mkdtemp()) / "rendered.json"
    try:
        subprocess.run(["node", str(REPO / "tools/site-audit/core-page-audit.mjs"), str(folder), "--json", str(out)],
                       check=True, capture_output=True, timeout=300)
        return json.loads(out.read_text(encoding="utf-8"))
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


def continuity(folder: Path) -> list[dict]:
    pages = {p.name: p.read_text(encoding="utf-8") for p in folder.glob("core*.html")}
    units = {name: set(re.findall(r'data-g9-unit="([^"]+)"', text)) for name, text in pages.items()}
    found = []
    a, b = units.get("core1a.html", set()), units.get("core1b.html", set())
    receipt = folder / "render-receipt.json"
    rec = json.loads(receipt.read_text(encoding="utf-8")) if receipt.is_file() else {}
    expected_roles = set(rec.get("output_roles") or ("CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B"))
    if {"CORE1A", "CORE1B"} <= expected_roles and a != b:
        found.append({"code": "CONT_1A_1B_PARITY", "detail": f"only in Core1A: {sorted(a - b)[:3]}; only in Core1B: {sorted(b - a)[:3]}"})
    for name, text in pages.items():
        for href in re.findall(r'href="(core\w+\.html)#([^"]+)"', text):
            target, anchor = href
            if anchor not in units.get(target, set()):
                found.append({"code": "CONT_LINK_UNRESOLVED", "detail": f"{name} links to {target}#{anchor}, which is not a rendered unit"})
    rendered_ids = set().union(*units.values()) if units else set()
    for row in rec.get("ledger", []):
        targets = [t for t in (row.get("teaching"), row.get("practice")) if t]
        if not targets:
            found.append({"code": "CONT_INPUT_UNRESOLVED", "detail": f"owner {row['kind']} {row['input_id']} is mapped to no record"})
        elif not any(t in rendered_ids for t in targets):
            found.append({"code": "CONT_INPUT_NOT_RENDERED", "detail": f"owner {row['kind']} {row['input_id']} maps to {targets}, none rendered"})
    index = folder / "index.html"
    if rec.get("diagnostic_min") and index.is_file():
        n = len(re.findall(r"data-g9-diagnostic=", index.read_text(encoding="utf-8")))
        if n < rec["diagnostic_min"]:
            found.append({"code": "CONT_DIAGNOSTIC_MISSING", "detail": f"{n} diagnostic item(s) on the start page; need {rec['diagnostic_min']}"})
    return found


def gate(folder: Path, subject: str, product_id: str, static: bool = False) -> dict:
    rendered = None if static else measure(folder)
    obs = quality_observe.observe_render_core(folder, product_id, subject, rendered)
    res = quality_contract.evaluate(obs)
    cont = continuity(folder)
    draft = any("data-g9-draft" in p.read_text(encoding="utf-8")[:400] for p in folder.glob("core*.html"))
    blocking = [f for f in res["findings"] if f["severity"] in BLOCKING]
    reasons = []
    if blocking:
        reasons.append("BLOCKING_FINDINGS")
    if cont:
        reasons.append("CONTINUITY")
    if draft:
        reasons.append("DRAFT")
    if res["not_measured"]:
        reasons.append("RENDERED_RULES_NOT_MEASURED")
    c = quality_contract.contract()
    return {
        "schema": "gate-report/v1",
        "tool": "quality_gate/1",
        "contract_version": c["version"],
        "product_id": product_id,
        "subject": subject,
        "render_stamp": obs["provenance"]["render_stamp"],
        "pages": [{"page": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(folder.glob("core*.html"))],
        "rules_evaluated": [r["id"] for r in c["rules"]],
        "rendered_measured": rendered is not None,
        "not_measured": res["not_measured"],
        "findings": [{k: f[k] for k in ("rule", "severity", "where", "detail")} for f in res["findings"]],
        "continuity": cont,
        "verdict": "FAIL" if reasons else "PASS",
        "fail_reasons": reasons,
    }


def validate(report: dict) -> list[str]:
    try:
        import jsonschema  # noqa: PLC0415
    except ModuleNotFoundError:
        return []
    v = jsonschema.Draft202012Validator(json.loads(REPORT_SCHEMA.read_text(encoding="utf-8")))
    return [e.message for e in v.iter_errors(report)]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dir")
    p.add_argument("--subject", required=True)
    p.add_argument("--product-id", required=True)
    p.add_argument("--static", action="store_true", help="skip the browser measurement (verdict cannot be PASS)")
    p.add_argument("--report")
    p.add_argument("--strict", action="store_true", help="nonzero for reported content findings in tool self-tests")
    a = p.parse_args(argv)
    report = gate(Path(a.dir), a.subject, a.product_id, a.static)
    errors = validate(report)
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for f in report["findings"]:
        print(f"{f['severity']} {f['rule']:28s} {f['where']}: {f['detail']}")
    for f in report["continuity"]:
        print(f"CONT {f['code']}: {f['detail']}")
    print(f"{report['product_id']}: {report['verdict']}" + (f" ({', '.join(report['fail_reasons'])})" if report["fail_reasons"] else "")
          + f"; {len(report['findings'])} finding(s)")
    if errors:
        print("REPORT_INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1
    return 1 if a.strict and report["verdict"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
