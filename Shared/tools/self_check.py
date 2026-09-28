#!/usr/bin/env python3
"""Write an advisory map of a unit's current render, sources and device observations."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import evidence_check, package_depth, quality_gate, render_core, unit_status  # noqa: E402


def _lines(rows: list[str], empty: str) -> str:
    return "\n".join(f"- {row}" for row in rows) if rows else f"- {empty}"


def _device(out: Path) -> tuple[str, list[str]]:
    if not shutil.which("node"):
        return "NOT_RUN", ["Chromium audit runtime (Node.js) unavailable."]
    audit = out / "tablet-audit.json"
    try:
        result = subprocess.run(
            ["node", str(REPO / "tools/site-audit/core-page-audit.mjs"), str(out),
             "--profile", "tablet-12.7", "--json", str(audit)],
            capture_output=True, text=True, timeout=300, check=False,
        )
        if result.returncode or not audit.is_file():
            return "NOT_RUN", [f"Audit unavailable: {(result.stderr or result.stdout).strip()[:300]}"]
        report = json.loads(audit.read_text(encoding="utf-8"))
        views = [view for page in report.values() for view in page["viewports"].values()]
        return "OBSERVED", [
            f"{len(report)} Core pages × {len(views) // max(len(report), 1)} tablet profiles.",
            f"{sum(v['smallTargets'] for v in views)} controls below 48 px across all measurements.",
            f"Maximum horizontal overflow: {max((v['horizontalOverflowPx'] for v in views), default=0)} px.",
            f"Hover-only handlers: {sum(v.get('hoverOnlyHandlers', 0) for v in views)}; "
            f"external requests: {sum(len(v.get('externalRequests', [])) for v in views)}; "
            f"page errors: {sum(len(p.get('errors', [])) for p in report.values())}.",
            f"Measured JSON: {audit.relative_to(REPO).as_posix()}.",
        ]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return "NOT_RUN", [f"Audit unavailable: {type(exc).__name__}: {exc}"]


def report(subject: str, slug: str, device: bool = True) -> tuple[Path, str]:
    out = REPO / "publication" / "products" / subject.lower() / slug
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = REPO / "products" / subject.lower() / f"{slug}.manifest.json"
    if not manifest_path.is_file():
        text = f"# Self-check: {subject}/{slug}\n\nManifest missing: {manifest_path.relative_to(REPO)}.\n"
        path = out / "SELF-CHECK.md"
        path.write_text(text, encoding="utf-8")
        return path, text

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    render_core.main(["build", "--manifest", str(manifest_path), "--out", str(out), "--draft"])
    receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
    digest = receipt["digest"]
    gaps = receipt["gaps"]
    lint = quality_gate.gate(out, subject, manifest["product_id"], static=True)
    status = unit_status.status(subject, slug, render=(gaps, digest))
    package_ref = status["package"]
    duties = [d for d in package_depth.all_duties(subject)
              if d["package"].replace("\\", "/") == package_ref.replace("\\", "/")]
    package_path = REPO / package_ref
    package = json.loads(package_path.read_text(encoding="utf-8")) if package_path.is_file() else {}
    inventory = evidence_check.inventory_index(subject)
    linked = sorted({ref for q in package.get("questions", [])
                     if (ref := (q.get("extensions") or {}).get("grade9v3:inventory_item"))})
    missing_refs = [ref for ref in linked if ref not in inventory]
    device_state, device_notes = _device(out) if device else ("NOT_RUN", ["Device measurement omitted by --no-device."])
    review = status.get("earlier_review_digest")
    acceptance = status.get("earlier_acceptance_digest")

    text = f"""# Self-check: {subject}/{slug}

Advisory observations for render `{digest}`. This report does not approve content or publication; the author and independent reviewer should inspect the actual pages.

## Linter notes

{_lines([f"{f['severity']} {f['rule']} — {f['where']}: {f['detail']}" for f in lint['findings']], 'No static linter finding. Browser-only rules remain unmeasured here.')}

Renderer gaps: {len(gaps)}. Static linter verdict: {lint['verdict']} (advisory).

## Fields not supplied

{_lines([f"{d['duty']} — {d['record']}: {d['detail']}" for d in duties], 'No package-depth field observation for this package.')}

## Sources

Cited records with current independent verification: {len(status['facts']['verified'])}/{status['facts']['cited']}.
Unverified cited records: {', '.join(status['facts']['unverified']) or 'none'}.
Linked inventory items: {len(linked)}; unresolved refs: {', '.join(missing_refs) or 'none'}.
Inventory formats: {status['inventory_formats']}; selected question formats: {status['selected_formats']}.
Source readback and digest changes are observed through the existing `inputs_digest`; this report creates no second ledger.

## Device

Status: **{device_state}**.
{_lines(device_notes, 'No device observation.')}

## Staleness

Current render digest: `{digest}`.
Earlier review digest: `{review or 'none'}`.
Earlier Owner acceptance digest: `{acceptance or 'none'}`.
Current lifecycle observation: {status['current_state']}.

Next judgement belongs to the author, independent reviewer and Owner, in that order.
"""
    path = out / "SELF-CHECK.md"
    path.write_text(text, encoding="utf-8")
    return path, text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--unit", required=True, help="Subject/slug")
    parser.add_argument("--no-device", action="store_true", help="record device as NOT_RUN")
    args = parser.parse_args(argv)
    try:
        subject, slug = args.unit.split("/", 1)
        path, _ = report(subject, slug, device=not args.no_device)
        print(path)
    except Exception as exc:  # a self-check reports its own failure; it never refuses authoring
        message = f"self-check observation unavailable: {type(exc).__name__}: {exc}"
        print(message, file=sys.stderr)
        if "/" in args.unit:
            subject, slug = args.unit.split("/", 1)
            out = REPO / "publication" / "products" / subject.lower() / slug
            out.mkdir(parents=True, exist_ok=True)
            (out / "SELF-CHECK.md").write_text(f"# Self-check: {args.unit}\n\nNOT_RUN: {message}\n",
                                               encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
