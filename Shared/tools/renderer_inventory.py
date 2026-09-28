#!/usr/bin/env python3
"""Phase-0 freeze: every code path that renders learner content must be in the inventory.

Scans the repository for code that emits HTML documents or PDFs (Python) or renders
learner content in the browser (JavaScript), and compares the result with the committed,
classified inventory (docs/plans/phase0/renderer-inventory.v1.json). A new renderer that
is not in the inventory fails the check. That is the freeze: no new learner-product
generator may appear until the single blueprint renderer of Phase 3 exists.

Usage:
    renderer_inventory.py            # report candidates and classification
    renderer_inventory.py --check    # exit 1 on unclassified or vanished entries
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INVENTORY = REPO / "docs/plans/phase0/renderer-inventory.v1.json"
PY_HTML = re.compile(r"<!doctype html|<html[\s>]", re.IGNORECASE)
PY_PDF = re.compile(r"\b(reportlab|fpdf|weasyprint|pdfkit|xhtml2pdf)\b|\.pdf\(")
JS_RENDER = re.compile(r"\binnerHTML\b|\binsertAdjacentHTML\b|document\.createElement\(")
SKIP_PARTS = {"node_modules", "__pycache__", ".git", "tests", "docs", ".source-cache", "publication"}
CLASSES = {"RENDERER", "ENGINE_KEEP", "MIGRATE", "RETIRE", "OUT_OF_SCOPE", "FROZEN_SNAPSHOT"}
THE_RENDERER = "Shared/tools/render_core.py"


def candidates(repo: Path = REPO) -> dict[str, str]:
    found: dict[str, str] = {}
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or SKIP_PARTS & set(path.relative_to(repo).parts):
            continue
        rel = path.relative_to(repo).as_posix()
        if rel == "Shared/tools/renderer_inventory.py":
            continue
        if path.suffix == ".py":
            text = path.read_text(encoding="utf-8", errors="replace")
            if PY_PDF.search(text):
                found[rel] = "PYTHON_PDF"
            elif PY_HTML.search(text):
                found[rel] = "PYTHON_HTML"
        elif path.suffix in {".js", ".mjs"} and rel.startswith(("public/", "tools/", "Shared/")):
            if "/data/" in rel or rel.endswith(("data.js", "catalog.js")):
                continue
            if "/explorers/" in rel:
                continue  # hand-authored explorer runtimes are inventoried as a group
            text = path.read_text(encoding="utf-8", errors="replace")
            if JS_RENDER.search(text):
                found[rel] = "JS_RENDER"
    return found


def check(repo: Path = REPO) -> dict:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    listed = {row["path"]: row for row in inventory["renderers"] if row.get("location", "main") == "main"}
    found = candidates(repo)
    findings = []
    for path, kind in sorted(found.items()):
        if path not in listed:
            findings.append({"code": "UNCLASSIFIED_RENDERER", "path": path, "detail": kind})
        elif listed[path]["classification"] not in CLASSES:
            findings.append({"code": "BAD_CLASSIFICATION", "path": path, "detail": listed[path]["classification"]})
    for path, row in sorted(listed.items()):
        if row["classification"] == "RENDERER" and path != THE_RENDERER:
            findings.append({"code": "SECOND_RENDERER", "path": path,
                             "detail": f"only {THE_RENDERER} renders learner pages; extend it instead"})
    for path in sorted(set(listed) - set(found)):
        if "*" in path or " " in path:
            continue  # grouped entries (explorers, snapshots) are described, not file paths
        if not (repo / path).exists():
            findings.append({"code": "INVENTORY_ENTRY_VANISHED", "path": path,
                             "detail": "file removed; update the inventory (a RETIRE entry may be deleted)"})
    return {"candidates": found, "findings": findings, "passed": not findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report = check()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    by_path = {r["path"]: r for r in inventory["renderers"]}
    for path, kind in report["candidates"].items():
        row = by_path.get(path, {})
        print(f"{row.get('classification', 'UNCLASSIFIED'):16s} {kind:12s} {path}")
    for f in report["findings"]:
        print(f"{f['code']}: {f['path']} ({f['detail']})", file=sys.stderr)
    print(f"renderer inventory: {len(report['candidates'])} renderers in main, {len(report['findings'])} findings")
    return 1 if args.check and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
