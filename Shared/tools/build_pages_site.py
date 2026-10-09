#!/usr/bin/env python3
"""Build or verify the GitHub Pages site served from the repository docs/ folder.

Source authority remains public/ plus the existing Run Builder assets under tools/.
The docs/ web tree is generated deployment output. Existing non-site documentation
under docs/ is preserved and never deleted by this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[2]
PUBLIC = REPO / "public"
DOCS = REPO / "docs"
PAGES_MANIFEST = DOCS / ".pages-manifest.json"
GENERATOR_VERSION = "1.2.0"

EXTRA_SOURCES = {
    "tools/app.css": "tools/app.css",
    "tools/data.js": "tools/data.js",
    "tools/index.html": "tools/index.html",
    "tools/library/index.html": "tools/library/index.html",
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

# External runtime URLs are permitted in source only when publication can deterministically
# rewrite them to a checked-in compatible runtime. The deployed docs/ tree is local-only.
VENDOR_REWRITES = {
    "https://cdn.tailwindcss.com/3.4.17": "vendor/tailwind/3.4.17/tailwind-play.js",
    "https://cdn.tailwindcss.com": "vendor/tailwind/3.4.17/tailwind-play.js",
    "https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js": "vendor/tailwind/3.4.17/tailwind-play.js",
    "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css": "vendor/katex/0.16.8/katex.min.css",
    "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js": "vendor/katex/0.16.8/katex.min.js",
    "https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js": "vendor/katex/0.16.8/contrib/auto-render.min.js",
}

RUNTIME_TAG = re.compile(r"<(?:script|link)\b[^>]*>", re.IGNORECASE)

HTML_LINK = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"'<>]+)["']""", re.IGNORECASE)
ROOT_PROJECT_LINK = re.compile(
    r"""(\b(?:href|src)\s*=\s*["'])/([^/"'][^"']*)(["'])""",
    re.IGNORECASE,
)
REPO_DOC_LINK = re.compile(
    r"""(\b(?:href|src)\s*=\s*["'])\.\./docs/([^"']+)(["'])""",
    re.IGNORECASE,
)
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _relative_from(relative: str, target: str) -> str:
    start = posixpath.dirname(relative) or "."
    return posixpath.relpath(target, start)


def _public_payload(relative: str, content: bytes) -> bytes:
    rewrites = TEXT_REWRITES.get(relative, ())
    needs_html_transform = relative.endswith(".html")
    if not rewrites and not needs_html_transform:
        return content

    text = content.decode("utf-8")
    for before, after in rewrites:
        if before not in text:
            raise ValueError(f"expected Pages rewrite token missing for {relative}: {before}")
        text = text.replace(before, after)

    if needs_html_transform:
        # Runtime dependencies are publication authority, not page-local policy. Keep legacy
        # source compatible while making the generated Pages bytes deterministic and offline.
        for external, local_target in VENDOR_REWRITES.items():
            if external in text:
                text = text.replace(external, _relative_from(relative, local_target))

        # Fail closed on any remaining remote script or stylesheet. Ordinary external learner
        # links (for example official source papers) are navigation, not runtime dependencies.
        for tag in RUNTIME_TAG.findall(text):
            lower = tag.lower()
            is_runtime = lower.startswith("<script") or (
                lower.startswith("<link") and "stylesheet" in lower
            )
            if not is_runtime:
                continue
            for raw in HTML_LINK.findall(tag):
                split = urlsplit(html.unescape(raw.strip()))
                if split.scheme.lower() in {"http", "https"} or split.netloc:
                    raise ValueError(
                        f"unapproved external runtime dependency in {relative}: {raw}"
                    )

        # GitHub project Pages is served below /<repo>/, so domain-root links from
        # static source pages must become paths relative to the mirrored document.
        def root_repl(match: re.Match[str]) -> str:
            raw = match.group(2)
            split = urlsplit(raw)
            target = split.path
            rewritten = _relative_from(relative, target)
            suffix = ""
            if split.query:
                suffix += "?" + split.query
            if split.fragment:
                suffix += "#" + split.fragment
            return match.group(1) + rewritten + suffix + match.group(3)

        text = ROOT_PROJECT_LINK.sub(root_repl, text)

        # Static repository tools may link back into repo/docs. Once tools are
        # mirrored under docs/tools, the docs directory is already the site root.
        if relative.startswith("tools/"):
            text = REPO_DOC_LINK.sub(
                lambda match: match.group(1) + "../" + match.group(2) + match.group(3),
                text,
            )

    return text.encode("utf-8")


def _render_manifest(files: dict[str, tuple[str, bytes]]) -> bytes:
    # Keep the deployment manifest structural. Freshness is verified byte-for-byte
    # by --check, so duplicating content digests here only makes remote generation
    # needlessly expensive without adding authority.
    rows = []
    for target in sorted(files):
        source, _content = files[target]
        rows.append({
            "source": source,
            "target": target,
        })
    payload = {
        "schema_version": "grade9v3-pages-mirror-v1",
        "generator": "Shared/tools/build_pages_site.py",
        "generator_version": GENERATOR_VERSION,
        "site_root": "docs",
        "source_roots": ["public", "tools"],
        "files": rows,
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _assert_core_public_data_safe(repo: Path) -> None:
    """Never mirror raw internal Core previews through the Pages deployment path.

    The source public/ asset is the only Core data Pages may copy. Validate it
    against the authoritative generator's *public* (not preview) output before
    reading the rest of the site. A partial temporary site without a Core host
    is permitted for unrelated site-building tests.
    """
    public = repo / "public"
    data = public / "core-learning" / "data.js"
    host = public / "core-learning" / "index.html"
    if not host.is_file() and not data.is_file():
        return
    if not host.is_file() or not data.is_file():
        raise ValueError("CORE_PUBLICATION_HOLD_SOURCE_MISSING")

    # build_pages_site.py is also callable as a directly executed script.
    # Ensure the common repository modules resolve in that mode.
    import sys
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from Shared.tools import build_core_learning_data

    expected = build_core_learning_data.rendered_file()["public/core-learning/data.js"]
    if data.read_bytes() != expected:
        raise ValueError("CORE_PUBLICATION_HOLD_PUBLIC_SOURCE_MISMATCH")


def desired_files(repo: Path = REPO) -> dict[str, tuple[str, bytes]]:
    _assert_core_public_data_safe(repo)
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
        files[target_rel] = (source_rel, _public_payload(target_rel, source.read_bytes()))

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


def link_findings(
    files: dict[str, tuple[str, bytes]],
    repo: Path = REPO,
) -> list[str]:
    """Return broken/escaping links in generated HTML using the intended Pages tree."""
    docs = repo / "docs"
    existing_docs = {
        path.relative_to(docs).as_posix()
        for path in docs.rglob("*")
        if path.is_file()
    }
    available = set(files) | existing_docs
    findings: list[str] = []
    for target, (_source, content) in sorted(files.items()):
        if not target.endswith(".html"):
            continue
        text = content.decode("utf-8")
        for raw in HTML_LINK.findall(text):
            raw = html.unescape(raw.strip())
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
    findings = link_findings(files, repo)
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
