#!/usr/bin/env python3
"""Deploy stress-run output to the TEST area of the site, as labelled drafts.

TEST is a sandbox subject (see TEST/README.md). Nothing deployed here is reviewed, accepted or curriculum, so
this is deliberately not `accept_product.py`: it renders a TEST manifest as a draft, stamps every page with a
TEST banner, and writes a receipt that says `accepted: false`. It refuses anything that is not TEST.

    python3 Shared/tools/deploy_test.py product TEST/products/SLUG.manifest.json
    python3 Shared/tools/deploy_test.py interactive TEST/interactive/SLUG
    python3 Shared/tools/deploy_test.py pages            # rebuild the TEST hub, rungs and deployments pages
    python3 Shared/tools/deploy_test.py pages --check    # verify them without writing

`product` and `interactive` rebuild the TEST pages and then the GitHub Pages mirror (docs/) unless `--no-mirror`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import build_pages_site, build_test_site, product_manifest, render_core, site_nav_audit  # noqa: E402

TEST_ROOT = REPO / "TEST"
PUBLIC_TEST = REPO / "public" / "test"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
PRODUCT_SCHEMA = "grade9v3-test-deploy-receipt-v1"
INTERACTIVE_SCHEMA = "grade9v3-test-interactive-v1"
INTERACTIVE_RECEIPT_SCHEMA = "grade9v3-test-interactive-receipt-v1"
NOTICE = "TEST sandbox draft: not reviewed, not accepted, not curriculum. accept_product.py refuses TEST."
BANNER_TEXT = "TEST sandbox draft · not reviewed, not accepted, not curriculum"
ALLOWED_SUFFIXES = {".html", ".css", ".js", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".txt"}
MAX_FILES, MAX_BYTES = 30, 2_000_000
EXTERNAL = re.compile(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.IGNORECASE)
EXTERNAL_CSS = re.compile(r"""@import\s+(?:url\()?\s*["']?\s*(?:https?:)?//""", re.IGNORECASE)


class DeployError(ValueError):
    """An input problem, reported as one line and exit status 1."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def banner(home: str) -> str:
    return (f'<div data-g9-test-banner role="note" style="background:#7c2d12;color:#fff;padding:8px 14px;'
            f'font:600 14px/1.4 system-ui,sans-serif">{BANNER_TEXT} · <a href="{home}" style="color:#fde68a">TEST home</a></div>')


def _stamp(page: str, top: str) -> str:
    """Mark the page as TEST in the markup itself: `top` right after the body tag and an attribute on the html element."""
    if page.count("<body") != 1 or page.count("<html") != 1:
        raise DeployError("a page must have exactly one html element and one body element to be stamped as TEST")
    page = re.sub(r"(<html\b)", r'\1 data-g9-test="sandbox-draft"', page, count=1)
    return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + top, page, count=1)


def stamp(page: str, home: str) -> str:
    """A rendered product page: it has the shared shell header already, so it gets the draft banner only."""
    return _stamp(page, banner(home))


def _slug(value: str, what: str) -> str:
    if not SLUG.fullmatch(value or ""):
        raise DeployError(f"{what} {value!r} must match {SLUG.pattern}")
    return value


# ------------------------------------------------------------------ products

def deploy_product(manifest_path: Path) -> dict:
    manifest_path = manifest_path.resolve()
    if not manifest_path.is_file():
        raise DeployError(f"no such manifest: {manifest_path}")
    if not manifest_path.is_relative_to(TEST_ROOT.resolve()):
        raise DeployError("a TEST product manifest must live under TEST/ (for example TEST/products/SLUG.manifest.json)")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("subject") != "TEST":
        raise DeployError(f"manifest subject is {manifest.get('subject')!r}; only TEST products can be deployed here")
    slug = _slug(str(manifest.get("product_id", "")), "product_id")
    refs = list(manifest.get("package_refs") or []) + list(manifest.get("bank_refs") or [])
    outside = [ref for ref in refs if not str(ref).startswith("TEST/")]
    if outside:
        raise DeployError(f"a TEST product may only use TEST records; outside TEST/: {outside}")

    # The pages live three levels below the site root. Set the links here so a wrong --home is not the thing
    # that stops a run.
    deployed = dict(manifest, home_href="../../../index.html", question_bank_href="../../../question-bank/index.html")
    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / manifest_path.name
        staged.write_text(json.dumps(deployed, indent=2), encoding="utf-8")
        try:
            pages, gaps, digest = render_core.build(staged, "PAGES")
        except product_manifest.ProductSelectionError as caught:
            raise DeployError(f"selection rejected: {caught}") from caught
    out = PUBLIC_TEST / "products" / slug
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    written = {}
    for name, text in sorted(pages.items()):
        data = stamp(text, "../../index.html").encode("utf-8")
        (out / name).write_bytes(data)
        written[name] = _sha(data)
    selection = manifest.get("selection") or {}
    by_core: dict[str, int] = {}
    for gap in gaps:
        by_core[gap["core"]] = by_core.get(gap["core"], 0) + 1
    receipt = {
        "schema": PRODUCT_SCHEMA,
        "slug": slug,
        "title": next((p for p in [manifest.get("title")] if p), slug),
        "subject": "TEST",
        "manifest": _rel(manifest_path),
        "manifest_sha256": _sha(manifest_path.read_bytes()),
        "inputs_sha256": {ref: _sha((REPO / ref).read_bytes()) for ref in sorted(refs) if (REPO / ref).is_file()},
        "links_overridden_for_location": True,
        "renderer": render_core.RENDERER_VERSION,
        "render_digest": digest,
        "draft": bool(gaps),
        "gap_count": len(gaps),
        "gaps_by_core": dict(sorted(by_core.items())),
        "roles": product_manifest.selected_output_roles(manifest),
        "selection_counts": {key: len(selection.get(key) or []) for key in product_manifest.SELECTION_KEYS},
        "empty_roles": render_core.empty_roles(manifest),
        "pages": written,
        "accepted": False,
        "notice": NOTICE,
    }
    (out / "deploy-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


# ------------------------------------------------------------------ interactive pages

def _validate_interactive(source: Path) -> tuple[dict, list[Path]]:
    if not source.is_dir() or not source.resolve().is_relative_to((TEST_ROOT / "interactive").resolve()):
        raise DeployError("an interactive page source must be a directory under TEST/interactive/")
    meta_path = source / "interactive.json"
    if not (source / "index.html").is_file() or not meta_path.is_file():
        raise DeployError("an interactive page needs index.html and interactive.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    missing = [key for key in ("schema", "slug", "title", "purpose", "records", "blueprint_ref", "status")
               if not meta.get(key)]
    if missing:
        raise DeployError(f"interactive.json is missing {missing}")
    if meta["schema"] != INTERACTIVE_SCHEMA:
        raise DeployError(f"interactive.json schema must be {INTERACTIVE_SCHEMA}")
    if meta["status"] != "DRAFT":
        raise DeployError("interactive.json status must be DRAFT")
    if not isinstance(meta["records"], list) or not all(isinstance(r, str) and r for r in meta["records"]):
        raise DeployError("interactive.json records must list the canonical record ids the page is built from")
    if _slug(str(meta["slug"]), "slug") != source.name:
        raise DeployError(f"slug {meta['slug']!r} must equal the directory name {source.name!r}")
    files = sorted(p for p in source.rglob("*") if p.is_file())
    if len(files) > MAX_FILES:
        raise DeployError(f"at most {MAX_FILES} files per interactive page")
    for path in files:
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise DeployError(f"{path.relative_to(source)}: file type {path.suffix!r} is not allowed")
        if path.stat().st_size > MAX_BYTES:
            raise DeployError(f"{path.relative_to(source)}: larger than {MAX_BYTES} bytes")
        if path.suffix.lower() in {".html", ".css", ".js"}:
            text = path.read_text(encoding="utf-8")
            if EXTERNAL.search(text) or EXTERNAL_CSS.search(text):
                raise DeployError(f"{path.relative_to(source)}: loads something from another host; the site must work offline")
    html = (source / "index.html").read_text(encoding="utf-8")
    if not re.search(r"""<meta[^>]+name\s*=\s*["']viewport["']""", html, re.IGNORECASE):
        raise DeployError("index.html needs a viewport meta tag")
    return meta, files


def deploy_interactive(source: Path) -> dict:
    source = source.resolve()
    meta, files = _validate_interactive(source)
    out = PUBLIC_TEST / "interactive" / meta["slug"]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    written = {}
    for path in files:
        rel = path.relative_to(source)
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        if rel.as_posix() == "index.html":
            # The page brings no shell header of its own, so it gets the sandbox header: draft label, portal, TEST pages.
            data = _stamp(data.decode("utf-8"), build_test_site.sandbox_bar("../../../")).encode("utf-8")
        target.write_bytes(data)
        written[rel.as_posix()] = _sha(data)
    missing = {name: site_nav_audit.missing_targets(REPO / "public", out / name)
               for name in written if name.endswith(".html")}
    missing = {name: refs for name, refs in missing.items() if refs}
    if missing:
        shutil.rmtree(out)
        detail = "; ".join(f"{name} links to {', '.join(refs)}" for name, refs in sorted(missing.items()))
        raise DeployError(f"{detail} (no such file at the deployed location public/test/interactive/{meta['slug']}/; "
                          "put it in the page's folder and link it relative to index.html)")
    receipt = {
        "schema": INTERACTIVE_RECEIPT_SCHEMA,
        "slug": meta["slug"],
        "title": meta["title"],
        "purpose": meta["purpose"],
        "records": meta["records"],
        "blueprint_ref": meta["blueprint_ref"],
        "source": _rel(source),
        "source_sha256": {p.relative_to(source).as_posix(): _sha(p.read_bytes()) for p in files},
        "files": written,
        "status": "DRAFT",
        "accepted": False,
        "notice": NOTICE,
    }
    (out / "interactive-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


# ------------------------------------------------------------------ command line

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("product")
    p.add_argument("manifest")
    p.add_argument("--no-mirror", action="store_true")
    p = sub.add_parser("interactive")
    p.add_argument("source")
    p.add_argument("--no-mirror", action="store_true")
    p = sub.add_parser("pages")
    p.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "pages":
            if args.check:
                findings = build_test_site.check()
                print("\n".join(findings) if findings else "TEST pages are current")
                return 1 if findings else 0
            build_test_site.write()
            return 0
        if args.cmd == "product":
            receipt = deploy_product(Path(args.manifest))
            print(f"deployed {receipt['slug']}: {len(receipt['pages'])} page(s), "
                  f"{'DRAFT with ' + str(receipt['gap_count']) + ' gap(s)' if receipt['draft'] else 'no gaps'}, accepted=false")
            print("selected records: " + " ".join(f"{k}={v}" for k, v in receipt["selection_counts"].items()))
            for role in receipt["empty_roles"]:
                print(f"WARNING: {role} is part of this product but selects no records, so its page has no items.", file=sys.stderr)
        else:
            receipt = deploy_interactive(Path(args.source))
            print(f"deployed interactive {receipt['slug']}: {len(receipt['files'])} file(s), DRAFT, accepted=false")
        build_test_site.write()
        if not args.no_mirror:
            build_pages_site.write(REPO)
    except (DeployError, ValueError, json.JSONDecodeError) as caught:
        print(f"deploy_test: {caught}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
