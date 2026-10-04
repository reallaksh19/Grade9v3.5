#!/usr/bin/env python3
"""Require Chromium evidence for every governed render that contains a staged SVG."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
TOOL = "tools/site-audit/staged-svg-audit.mjs"


def _sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _has_staged_svg(path: Path) -> bool:
    if path.suffix.lower() != ".html" or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "data-g9-figure" in text and ("data-g9-stages-total=\"2\"" in text or "data-g9-stages-total=\"3\"" in text or "data-g9-stages-total=\"4\"" in text or "data-g9-stage-sequence" in text)


def check(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    head = str((run.get("run_identity") or {}).get("head_sha") or "")
    artifacts = {str(a.get("id")): a for a in run.get("rendered_artifacts") or [] if isinstance(a, dict) and a.get("id")}
    staged: dict[str, dict[str, Any]] = {}
    for aid, artifact in artifacts.items():
        path = REPO / str(artifact.get("path") or "")
        if _has_staged_svg(path):
            staged[aid] = artifact
    receipts = {
        str(r.get("artifact_ref")): r
        for r in ((run.get("validation") or {}).get("staged_svg_chromium_receipts") or [])
        if isinstance(r, dict) and r.get("artifact_ref")
    }
    if not staged:
        return problems
    for aid, artifact in staged.items():
        receipt = receipts.get(aid)
        if not receipt:
            problems.append(f"STAGED_SVG_CHROMIUM_RECEIPT_MISSING:{aid}")
            continue
        if receipt.get("tool") != TOOL:
            problems.append(f"STAGED_SVG_CHROMIUM_TOOL_INVALID:{aid}:{receipt.get('tool')}")
        if receipt.get("engine") != "playwright.chromium":
            problems.append(f"STAGED_SVG_CHROMIUM_ENGINE_INVALID:{aid}:{receipt.get('engine')}")
        if receipt.get("profile") != "tablet-12.7":
            problems.append(f"STAGED_SVG_CHROMIUM_PROFILE_INVALID:{aid}:{receipt.get('profile')}")
        if receipt.get("status") != "PASS":
            problems.append(f"STAGED_SVG_CHROMIUM_NOT_PASS:{aid}:{receipt.get('status')}")
        if receipt.get("head_sha") != head:
            problems.append(f"STAGED_SVG_CHROMIUM_HEAD_MISMATCH:{aid}")
        if receipt.get("artifact_sha256") != artifact.get("sha256"):
            problems.append(f"STAGED_SVG_CHROMIUM_ARTIFACT_DIGEST_MISMATCH:{aid}")
        report_path = REPO / str(receipt.get("report_path") or "")
        if not report_path.is_file():
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_MISSING:{aid}")
            continue
        actual_report_sha = _sha256_file(report_path)
        if receipt.get("report_sha256") != actual_report_sha:
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_DIGEST_MISMATCH:{aid}")
            continue
        try:
            report = _load(report_path)
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_INVALID:{aid}:{exc}")
            continue
        if report.get("schema") != "staged-svg-chromium-audit/v1":
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_SCHEMA_INVALID:{aid}")
        if report.get("tool") != TOOL or report.get("engine") != "playwright.chromium":
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_AUTHORITY_INVALID:{aid}")
        if report.get("profile") != "tablet-12.7":
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_PROFILE_INVALID:{aid}")
        if report.get("status") != "PASS" or (report.get("findings") or []):
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_HAS_FINDINGS:{aid}")
        page_rows = [row for row in report.get("pages") or [] if isinstance(row, dict)]
        artifact_sha = artifact.get("sha256")
        if not any(row.get("sha256") == artifact_sha for row in page_rows):
            problems.append(f"STAGED_SVG_CHROMIUM_REPORT_NOT_BOUND_TO_ARTIFACT:{aid}")
        viewports = {
            str(v.get("name"))
            for row in page_rows
            for v in row.get("viewports") or []
            if isinstance(v, dict)
        }
        required = {"landscape-1366", "landscape-1440", "portrait-854", "portrait-900"}
        if not required.issubset(viewports):
            problems.append(f"STAGED_SVG_CHROMIUM_VIEWPORTS_INCOMPLETE:{aid}:{sorted(viewports)}")
    return problems
