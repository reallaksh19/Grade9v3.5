#!/usr/bin/env python3
"""Build or verify the GitHub Pages site served from the repository docs/ folder.

Source authority remains public/ plus the existing Run Builder assets under tools/.
The docs/ web tree is generated deployment output. Existing non-site documentation
under docs/ is preserved and never deleted by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[2]
PUBLIC = REPO / "public"
DOCS = REPO / "docs"
PAGES_MANIFEST = DOCS / ".pages-manifest.json"
GENERATOR_VERSION = "1.0.0"

EXTRA_SOURCES = {
    "tools/data.js": "tools/data.js",
    "tools/run-builder/index.html": "tools/run-builder/index.html",
}

TEXT_REWRITES = {
    "core-prompt-composer/index.html": (
        ("../../tools/run-builder/index.html", "../tools/run-builder/index.html"),
    ),
    "js/topic-atlas.js": (
        ("../../../tools/run-builder/index.html", "../../tools/run-builder/index.html"),
    ),
}

HTML_LINK = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"'<>]+)["']""", re.IGNORECASE)
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _public_payload(relative: str, content: bytes) -> bytes:
    rewrites = TEXT_REWRITES.get(relative)
    if not rewrites:
        return content
    text = content.decode("utf-8")
    for before, after in rewrites:
        if before not in text:
            raise ValueError(f"expected Pages rewrite token missing in public/{relative}: {before}")
        text = text.replace(before, after)
    return text.encode("utf-8")


def _render_manifest(files: dict[str, tuple[str, bytes]]) -> bytes:
    rows = []
    for target in sorted(files):
        source, content = files[target]
        rows.append({
            "target": target,
            "source": source,
            "bytes": len(content),
            "sha256": _sha256(content),
        })
    payload = {
        "schema_version": "grade9v3-pages-mirror-v1",
        "generator": "Shared/tools/build_pages_site.py",
        "generator_version": GENERATOR_VERSION,
        "site_root": "docs",
        "source_roots": ["public", "tools/run-builder", "tools/data.js"],
        "files": rows,
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def desired_files(repo: Path = REPO) -> dict[str, tuple[str, bytes]]:
    public = repo / "public"
    files: dict[str, tuple[str, bytes]] = {}
    for source in sorted(public.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(public).as_posix()
        files[relative] = (
            f"public/{relative}",
            _public_payload(relative, source.read_bytes()),
        )

    for source_rel, target_rel in EXTRA_SOURCES.items():
        source = repo / source_rel
        if not source.is_file():
            raise FileNotFoundError(f"Pages source missing: {source_rel}")
        files[target_rel] = (source_rel, source.read_bytes())

    files[".nojekyll"] = ("GENERATED", b"")
    manifest_bytes = _render_manifest(files)
    files[".pages-manifest.json"] = ("GENERATED", manifest_bytes)
    return files


def _previous_generated_targets(repo: Path = REPO) -> set[str]:
    path = repo / "docs" / ".pages-manifest.json"
    if not path.is_file():
        return set()
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {
        row["target"]
        for row in doc.get("files", [])
        if isinstance(row, dict) and isinstance(row.get("target"), str)
    } | {".pages-manifest.json", ".nojekyll"}


def _candidate_targets(path: str) -> tuple[str, ...]:
    if path.endswith("/"):
        return (path + "index.html",)
    suffix = posixpath.splitext(path)[1]
    if suffix:
        return (path,)
    return (path, path + "/index.html")


def link_findings(files: dict[str, tuple[str, bytes]]) -> list[str]:
    """Return broken/escaping links in generated HTML using the intended Pages tree."""
    available = set(files)
    findings: list[str] = []
    for target, (_source, content) in sorted(files.items()):
        if not target.endswith(".html"):
            continue
        text = content.decode("utf-8")
        for raw in HTML_LINK.findall(text):
            raw = raw.strip()
            if not raw or raw.startswith("#") or raw.startswith("//"):
                continue
            split = urlsplit(raw)
            if split.scheme.lower() in SKIP_SCHEMES or split.netloc:
                continue
            path = unquote(split.path)
            if not path:
                continue
            if path.startswith("/"):
                findings.append(f"{target}: root-absolute project link escapes Pages base: {raw}")
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(target), path))
            if resolved == ".." or resolved.startswith("../"):
                findings.append(f"{target}: link escapes docs/ Pages root: {raw}")
                continue
            if not any(candidate in available for candidate in _candidate_targets(resolved)):
                findings.append(f"{target}: generated target missing for {raw} -> {resolved}")
    return findings


def check(repo: Path = REPO) -> list[str]:
    files = desired_files(repo)
    findings = link_findings(files)
    docs = repo / "docs"

    for relative, (_source, intended) in sorted(files.items()):
        target = docs / relative
        if not target.is_file():
            findings.append(f"missing generated Pages file: docs/{relative}")
            continue
        actual = target.read_bytes()
        if actual != intended:
            findings.append(
                f"stale generated Pages file: docs/{relative} "
                f"(expected sha256:{_sha256(intended)}, got sha256:{_sha256(actual)})"
            )

    desired_targets = set(files)
    stale = sorted(_previous_generated_targets(repo) - desired_targets)
    for relative in stale:
        if (docs / relative).exists():
            findings.append(f"stale generated Pages target remains: docs/{relative}")
    return findings


def write(repo: Path = REPO) -> None:
    files = desired_files(repo)
    docs = repo / "docs"
    old_targets = _previous_generated_targets(repo)
    desired_targets = set(files)

    for relative in sorted(old_targets - desired_targets):
        target = docs / relative
        if target.is_file():
            target.unlink()

    # Manifest last so an interrupted build never claims a complete mirror.
    ordered = [name for name in sorted(files) if name != ".pages-manifest.json"]
    ordered.append(".pages-manifest.json")
    for relative in ordered:
        _source, content = files[relative]
        target = docs / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if docs/ Pages output is stale")
    args = parser.parse_args()
    if args.check:
        findings = check()
        if findings:
            print("GitHub Pages mirror is stale or invalid:")
            for finding in findings:
                print(f"  - {finding}")
            print("\nRegenerate with: python3 Shared/tools/build_pages_site.py")
            return 1
        print("GitHub Pages mirror is current and internally linked.")
        return 0

    write()
    findings = check()
    if findings:
        print("Pages build wrote files but validation still failed:")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("GitHub Pages mirror written to docs/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
