#!/usr/bin/env python3
"""Record an Owner decision on an exact rendered build, then publish its pages.

This is the only publication entry point. Gate verdicts, review findings and
source status are information for the Owner, never prerequisites.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import build_pages_site, render_core  # noqa: E402


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_render(folder: Path) -> dict:
    """Check that the receipt still identifies precisely these rendered pages."""
    receipt = _json(folder / "render-receipt.json")
    digest = receipt["digest"]
    if receipt.get("mode") != "PAGES" or not re.fullmatch(r"[0-9a-f]{16}", digest):
        raise ValueError("acceptance requires a PAGES render with a valid digest")
    pages = receipt.get("pages")
    if not isinstance(pages, list) or not pages or len(set(pages)) != len(pages):
        raise ValueError("receipt has no unique page list")
    if set(pages) != {p.name for p in folder.glob("*.html")}:
        raise ValueError("rendered page set differs from the receipt")
    h = hashlib.sha256()
    for name in sorted(pages):
        if Path(name).name != name:
            raise ValueError("unsafe page name")
        page = (folder / name).read_bytes().decode("utf-8")
        stamp = f'<meta name="g9-render" content="{receipt["renderer"]} {digest}">'
        if page.count(stamp) != 1:
            raise ValueError(f"{name}: missing or repeated digest stamp")
        neutral = page.replace(stamp, stamp.replace(digest, "g9-digest-pending"))
        if receipt.get("draft"):
            neutral = re.sub(r'<html data-g9-draft="[0-9]+" ', "<html ", neutral, count=1)
        h.update(name.encode() + b"\0" + neutral.encode())
    if h.hexdigest()[:16] != digest:
        raise ValueError("rendered page bytes no longer match the receipt digest")
    return receipt


def open_findings(review: dict) -> list[dict]:
    return [f for f in review.get("findings", [])
            if f.get("severity") in {"S0", "S1"} and not f.get("resolved")
            and f.get("status") != "FIXED"]


def source_status(manifest: dict, repo: Path) -> tuple[list[str], list[str]]:
    """Conservative until WP4 derives independent verification from citations."""
    authors: set[str] = set()
    unknown: set[str] = set()
    for ref in manifest.get("package_refs", []):
        package = _json(repo / ref)
        for rows in package.values():
            if not isinstance(rows, list):
                continue
            for record in rows:
                if not isinstance(record, dict) or "id" not in record:
                    continue
                ext = record.get("extensions") or {}
                if ext.get("grade9v3:authored_by"):
                    authors.add(ext["grade9v3:authored_by"])
                if ext.get("grade9v3:citations"):
                    unknown.add(record["id"])
    return sorted(authors), sorted(unknown)


def mirror_pages(repo: Path) -> None:
    build_pages_site.write(repo)
    findings = build_pages_site.check(repo)
    if findings:
        raise RuntimeError("Pages mirror findings: " + "; ".join(findings))


def accept(slug: str, note: str = "", accept_open: str = "", repo: Path = REPO,
           confirm=input) -> dict:
    manifests = list((repo / "products").glob(f"*/{slug}.manifest.json"))
    if len(manifests) != 1:
        raise ValueError(f"expected exactly one manifest for {slug}, got {len(manifests)}")
    manifest = _json(manifests[0])
    subject = manifest["subject"].lower()
    folder = repo / "publication" / "products" / subject / slug
    receipt = verify_render(folder)
    standalone_stage = repo / "publication" / "standalone" / "products" / subject / f"{slug}.html"
    standalone_dest = repo / "standalone" / "products" / subject / f"{slug}.html"
    if not standalone_stage.is_file() and standalone_dest.exists():
        raise ValueError("a published standalone page exists; rebuild both modes before Owner acceptance")
    standalone_bytes = None
    standalone_render_digest = None
    if standalone_stage.is_file():
        standalone_receipt = _json(standalone_stage.with_suffix(".receipt.json"))
        single_pages, _single_gaps, single_digest = render_core.build(manifests[0], mode="SINGLE_FILE")
        standalone_bytes = standalone_stage.read_bytes()
        standalone_render_digest = single_digest
        if (standalone_receipt.get("pages_digest") != receipt["digest"]
                or standalone_receipt.get("render_digest") != single_digest
                or standalone_receipt.get("sha256") != _sha(standalone_bytes)
                or standalone_bytes != single_pages["product.html"].encode("utf-8")):
            raise ValueError("staged standalone page no longer matches this exact render")
    review_path = repo / "products" / "verification" / f"{slug}.review.json"
    review = _json(review_path) if review_path.is_file() else {}
    findings = open_findings(review)
    authors, unknown = source_status(manifest, repo)
    print(f"Build: {slug} @ {receipt['digest']}; review: {review.get('render_digest', 'NONE')}")
    print(f"Recommendation: {review.get('overall', {}).get('recommendation', 'UNRECORDED')}")
    print(f"Open S0/S1: {[f.get('id', f.get('record', '?')) for f in findings]}")
    print(f"Reviewer: {review.get('reviewer', review.get('verifier', 'UNRECORDED'))}; authors: {authors}")
    print(f"Fact status: {len(unknown)} cited records not yet classified by WP4 (shown conservatively as unverified)")
    print(f"Standalone: {'STAGED_FOR_THIS_RENDER' if standalone_bytes is not None else 'NOT_STAGED'}")
    if findings or unknown:
        if confirm("Owner acceptance with open/unknown findings? [y/N] ").strip().lower() != "y":
            raise ValueError("Owner did not accept this exact render")
    accepted = {
        "schema": "product-acceptance/v1", "product": slug,
        "render_digest": receipt["digest"], "accepted_by": "owner",
        "accepted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "review_ref": str(review_path.relative_to(repo)) if review else None,
        "review_digest": _sha(review_path.read_bytes()) if review else None,
        "accepted_open_findings": sorted((set(accept_open.split(",")) - {""}) |
                                         {f.get("id", f.get("record", "?")) for f in findings}),
        "unverified_fact_records": unknown, "note": note,
        "standalone_sha256": _sha(standalone_bytes) if standalone_bytes is not None else None,
        "standalone_render_digest": standalone_render_digest,
    }
    # Stage first, then replace the public directory. Check its bytes again before
    # recording publication; PDFs are print artifacts, not public learner pages.
    dest = repo / "public" / "products" / subject / slug
    dest.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{slug}-", dir=dest.parent))
    try:
        shutil.rmtree(staged)
        shutil.copytree(folder, staged, ignore=shutil.ignore_patterns("*.pdf"))
        verify_render(staged)
        previous = dest.with_name(f".{slug}-previous")
        if previous.exists():
            shutil.rmtree(previous)
        if dest.exists():
            dest.rename(previous)
        try:
            staged.rename(dest)
        except Exception:
            if previous.exists():
                previous.rename(dest)
            raise
        if previous.exists():
            shutil.rmtree(previous)
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    if standalone_bytes is not None:
        standalone_dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix=f".{slug}-", suffix=".html", dir=standalone_dest.parent,
                                         delete=False) as staged_file:
            staged_file.write(standalone_bytes)
            staged_path = Path(staged_file.name)
        try:
            staged_path.replace(standalone_dest)
        finally:
            staged_path.unlink(missing_ok=True)
        if _sha(standalone_dest.read_bytes()) != accepted["standalone_sha256"]:
            raise RuntimeError("standalone copy differs from the accepted render")
    acceptance = repo / "products" / "acceptance" / f"{slug}.json"
    acceptance.parent.mkdir(parents=True, exist_ok=True)
    acceptance.write_text(json.dumps(accepted, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mirror_pages(repo)
    return accepted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug")
    parser.add_argument("--note", default="")
    parser.add_argument("--accept-open", default="")
    args = parser.parse_args(argv)
    try:
        decision = accept(args.slug, args.note, args.accept_open)
    except (ValueError, OSError, RuntimeError, EOFError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Owner accepted {args.slug} @ {decision['render_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
