#!/usr/bin/env python3
"""Static navigation audit of the deployed site (docs/): every page reachable, never a dead end.

Findings (code, page):
  BROKEN_LINK            a static href/src that resolves to no file
  ORPHAN                 no other page links to it (portal index.html and 404.html excepted)
  NO_WAY_HOME            no link to the portal and no shared shell header (which provides one)
  NO_SHELL               the page does not load the shared tablet shell (data-g9-shell)
  EXTERNAL_RUNTIME_DEP   a script or stylesheet loaded from another host (fails offline on a tablet)
  NO_VIEWPORT            no <meta name="viewport">
  SITE_MAP_MISSING       data/site-map.js (window.G9_SITE_MAP) does not exist yet
  NOT_IN_SITE_MAP        a page that the site map does not list (breadcrumbs/search cannot find it)
  SITE_MAP_DEAD_ENTRY    a site-map entry whose file does not exist

The committed baseline (tests/fixtures/site-audit/baseline.json) lists today's findings. The
test fails on any finding not in the baseline, so work can only remove problems. After fixing,
run with --write-baseline to shrink it.

Usage:
    site_nav_audit.py [--root docs] [--json] [--write-baseline]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[2]
BASELINE = REPO / "tests/fixtures/site-audit/baseline.json"
REF = re.compile(r"""\b(href|src)\s*=\s*["']([^"'<>]+)["']""", re.IGNORECASE)
EXTERNAL_ASSET = re.compile(r"""<(?:script|link)\b[^>]*\b(?:src|href)\s*=\s*["'](https?:)?//([^/"']+)""", re.IGNORECASE)
SHELL_MARK = "data-g9-shell"
ENTRY_PAGES = {"index.html", "404.html"}


def _skip(url: str) -> bool:
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return True
    if "${" in url or "{{" in url or "'+" in url or '"+' in url:
        return True
    return bool(urlsplit(url).scheme) or url.startswith("//")


def _resolve(root: Path, page: Path, url: str) -> Path | None:
    path = unquote(urlsplit(url).path)
    if not path:
        return page
    target = (root / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
    target = target.resolve()
    if target.is_dir() or path.endswith("/"):
        target = target / "index.html"
    return target


def audit(root: Path = REPO / "docs") -> dict:
    root = root.resolve()
    pages = sorted(p for p in root.rglob("*.html") if ".source-cache" not in p.parts)
    rel = {p: str(p.relative_to(root)) for p in pages}
    inbound: dict[str, set[str]] = {r: set() for r in rel.values()}
    findings: list[dict] = []
    portal = (root / "index.html").resolve()

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        name = rel[page]
        links_home = False
        for attr, raw in REF.findall(text):
            url = html.unescape(raw).strip()
            if _skip(url):
                continue
            target = _resolve(root, page, url)
            if target is None:
                continue
            if not target.exists():
                findings.append({"code": "BROKEN_LINK", "page": name, "detail": url})
                continue
            if target == portal:
                links_home = True
            if attr.lower() == "href" and target.suffix == ".html" and target != page.resolve():
                try:
                    inbound[str(target.relative_to(root))].add(name)
                except (KeyError, ValueError):
                    pass
        has_shell = SHELL_MARK in text
        if not has_shell:
            findings.append({"code": "NO_SHELL", "page": name, "detail": "shared tablet shell not loaded"})
        if not links_home and not has_shell and name != "index.html":
            findings.append({"code": "NO_WAY_HOME", "page": name, "detail": "no link to the portal"})
        for _scheme, host in EXTERNAL_ASSET.findall(text):
            findings.append({"code": "EXTERNAL_RUNTIME_DEP", "page": name, "detail": host})
        if not re.search(r"""<meta[^>]+name\s*=\s*["']viewport["']""", text, re.IGNORECASE):
            findings.append({"code": "NO_VIEWPORT", "page": name, "detail": ""})

    site_map = root / "data" / "site-map.js"
    if not site_map.is_file():
        findings.append({"code": "SITE_MAP_MISSING", "page": "data/site-map.js", "detail": ""})
    else:
        body = site_map.read_text(encoding="utf-8")
        start = body.find("{")
        try:
            entries = json.loads(body[start:body.rstrip().rstrip(";").rfind("}") + 1]).get("pages", [])
        except (ValueError, AttributeError):
            entries = []
            findings.append({"code": "SITE_MAP_MISSING", "page": "data/site-map.js", "detail": "not valid JSON after 'window.G9_SITE_MAP ='"})
        listed = {e.get("path") for e in entries}
        for name in rel.values():
            if name not in listed and name != "404.html":
                findings.append({"code": "NOT_IN_SITE_MAP", "page": name, "detail": ""})
        for path in sorted(p for p in listed if p):
            if not (root / path).is_file():
                findings.append({"code": "SITE_MAP_DEAD_ENTRY", "page": path, "detail": ""})

    for name, sources in inbound.items():
        if name not in ENTRY_PAGES and not sources:
            findings.append({"code": "ORPHAN", "page": name, "detail": "no page links here"})

    unique = {(f["code"], f["page"], f["detail"]): f for f in findings}
    findings = [unique[k] for k in sorted(unique)]
    return {"root": str(root.relative_to(REPO)) if root.is_relative_to(REPO) else str(root),
            "pages": len(pages), "findings": findings,
            "counts": {code: sum(1 for f in findings if f["code"] == code) for code in sorted({f["code"] for f in findings})}}


def keys(findings: list[dict]) -> set[tuple[str, str, str]]:
    return {(f["code"], f["page"], f["detail"]) for f in findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO / "docs")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)
    report = audit(args.root)
    if args.write_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps({"findings": report["findings"]}, indent=1) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for f in report["findings"]:
            print(f"{f['code']:22s} {f['page']}  {f['detail']}")
        print(f"site nav audit: {report['pages']} pages, " +
              ", ".join(f"{k} {v}" for k, v in report["counts"].items()) if report["counts"] else
              f"site nav audit: {report['pages']} pages, no findings")
    new = keys(report["findings"]) - keys(json.loads(BASELINE.read_text())["findings"]) if BASELINE.is_file() else set()
    for code, page, detail in sorted(new):
        print(f"NEW (not in baseline): {code} {page} {detail}", file=sys.stderr)
    return 1 if new else 0


if __name__ == "__main__":
    raise SystemExit(main())
