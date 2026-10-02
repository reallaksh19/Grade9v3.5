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
        # The renderer also writes the digest into `data-g9-render-digest`, which scopes a
        # learner's saved state to this exact render. It is one of the two stamped fields.
        neutral = neutral.replace(f'data-g9-render-digest="{digest}"', 'data-g9-render-digest="g9-digest-pending"')
        if digest in neutral:
            raise ValueError(f"{name}: the digest appears outside its stamped fields")
        if receipt.get("draft"):
            neutral = re.sub(r'<html data-g9-draft="[0-9]+" ', "<html ", neutral, count=1)
        h.update(name.encode() + b"\0" + neutral.encode())
    if h.hexdigest()[:16] != digest:
        raise ValueError("rendered page bytes no longer match the receipt digest")
    return receipt


def verify_current_basis(folder: Path, manifest_path: Path, receipt: dict) -> None:
    """Require staged bytes to come from the current sole renderer and sources."""
    if receipt.get("renderer") != render_core.RENDERER_VERSION:
        raise ValueError("staged render uses a different renderer version")
    pages, gaps, digest = render_core.build(manifest_path, mode="PAGES")
    if (receipt.get("digest") != digest or receipt.get("gaps") != gaps
            or receipt.get("semantic_digest") != render_core.semantic_metadata_digest(pages, "PAGES")
            or set(receipt.get("pages", [])) != set(pages)):
        raise ValueError("staged render differs from the current renderer or source records")
    for name, page in pages.items():
        if gaps:
            page = page.replace("<html ", f'<html data-g9-draft="{len(gaps)}" ', 1)
        if (folder / name).read_bytes() != page.encode("utf-8"):
            raise ValueError(f"{name}: staged page differs from the current renderer")


def open_findings(review: dict) -> list[dict]:
    return [f for f in review.get("findings", [])
            if f.get("severity") in {"S0", "S1"} and not f.get("resolved")
            and f.get("status") != "FIXED"]


def source_status(manifest: dict, repo: Path) -> tuple[list[str], list[str]]:
    """Show independently current cited facts; unresolved records remain visible to the Owner."""
    from Shared.tools.unit_status import fact_status  # noqa: PLC0415
    authors: set[str] = set()
    unknown: set[str] = set()
    for ref in manifest.get("package_refs", []):
        package = _json(repo / ref)
        unknown.update(fact_status(package, manifest["subject"], repo)["unverified"])
        for rows in package.values():
            if not isinstance(rows, list):
                continue
            for record in rows:
                if not isinstance(record, dict) or "id" not in record:
                    continue
                ext = record.get("extensions") or {}
                if ext.get("grade9v3:authored_by"):
                    authors.add(ext["grade9v3:authored_by"])
    return sorted(authors), sorted(unknown)


def mirror_pages(repo: Path) -> None:
    build_pages_site.write(repo)
    findings = build_pages_site.check(repo)
    if findings:
        raise RuntimeError("Pages mirror findings: " + "; ".join(findings))


def accept(slug: str, note: str = "", accept_open: str = "", repo: Path = REPO,
           confirm=input, approval_ref: str = "") -> dict:
    manifests = list((repo / "products").glob(f"*/{slug}.manifest.json"))
    if len(manifests) != 1:
        raise ValueError(f"expected exactly one manifest for {slug}, got {len(manifests)}")
    manifest = _json(manifests[0])
    if manifest["subject"] == "TEST":
        raise ValueError("TEST is a sandbox subject: its products are labelled drafts and are never accepted or published as learner products")
    subject = manifest["subject"].lower()
    folder = repo / "publication" / "products" / subject / slug
    receipt = verify_render(folder)
    verify_current_basis(folder, manifests[0], receipt)
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
    authority_findings = render_core.subject_authority_findings(manifests[0], repo)
    print(f"Build: {slug} @ {receipt['digest']}; review: {review.get('render_digest', 'NONE')}")
    print(f"Recommendation: {review.get('overall', {}).get('recommendation', 'UNRECORDED')}")
    print(f"Open S0/S1: {[f.get('id', f.get('record', '?')) for f in findings]}")
    print(f"Reviewer: {review.get('reviewer', review.get('verifier', 'UNRECORDED'))}; authors: {authors}")
    print(f"Fact status: {len(unknown)} cited records without current independent verification")
    print(f"Subject authority: {len(authority_findings)} finding(s): "
          f"{[(f['point'], f['record']) for f in authority_findings]}")
    print(f"Standalone: {'STAGED_FOR_THIS_RENDER' if standalone_bytes is not None else 'NOT_STAGED'}")
    approval_ref = " ".join(str(approval_ref or "").split())[:500]
    print(f"Approval reference: {approval_ref or 'NOT_RECORDED'}")
    if findings or unknown or authority_findings:
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
        # Where the Owner's approval was given (a message or comment link, or a quotation).
        # Recorded so an acceptance can be traced to the Owner's words; never verified and
        # never required.
        "approval_ref": approval_ref or None,
        "subject_authority_findings": authority_findings,
        "standalone_sha256": _sha(standalone_bytes) if standalone_bytes is not None else None,
        "standalone_render_digest": standalone_render_digest,
    }
    # Stage first, then replace the public directory. Check its bytes again before
    # recording publication. The learner PDFs go with the pages they were printed from, because the pages link them
    # (the shell's PRINT_PDF control); a key PDF holds the answers and is never copied.
    dest = repo / "public" / "products" / subject / slug
    dest.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{slug}-", dir=dest.parent))
    try:
        shutil.rmtree(staged)
        shutil.copytree(folder, staged, ignore=shutil.ignore_patterns("*.key.pdf", "print-key-receipt.json"))
        verify_render(staged)
        pdf_problems = render_core.pdf_publication_problems(staged)
        if pdf_problems:
            raise ValueError("the PDFs do not match the pages they are linked from: " + "; ".join(pdf_problems))
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


def _release_eligible(slug: str, bundle: str | None) -> bool:
    """The assurance gate. With a bundle, its evidence is recomputed and the product must be ELIGIBLE. Without one, the release policy decides: acceptance_gate
    REQUIRED refuses, ADVISORY (the policy as shipped, until every verifier the release policy asks for exists) says so and goes on."""
    from Shared.assurance import aggregate
    from Shared.contracts import ContractError
    if bundle is None:
        gate = next((p.get("acceptance_gate", "ADVISORY") for p in aggregate.load_policies(["learner-release-default"])), "ADVISORY")
        if gate == "REQUIRED":
            print("No assurance bundle was supplied (--eligibility) and the release policy requires one.", file=sys.stderr)
            return False
        print("Note: no assurance bundle was supplied (--eligibility); the release policy treats it as advisory for now.")
        return True
    from Shared.tools.release_eligibility import load_and_check
    try:
        decision = load_and_check(bundle, slug)
    except ContractError as exc:
        print(f"Release ineligible: {exc}", file=sys.stderr)
        return False
    print(f"Release eligibility: {decision['status']}")
    if decision["status"] != "ELIGIBLE":
        for row in decision["missing"][:12]:
            print(f"  open     {row['type']} {row['subject']} {row['reason']}", file=sys.stderr)
        for row in decision["problems"]:
            print(f"  problem  {row['code']}: {row['message']}", file=sys.stderr)
        for row in decision["reviewable_findings"][:8]:
            print(f"  [{row['severity']}] {row['code']} {row['subject']}: {row['message'][:100]}", file=sys.stderr)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("slug")
    parser.add_argument("--note", default="")
    parser.add_argument("--accept-open", default="")
    parser.add_argument("--approval-ref", default="",
                        help="where the Owner's approval was given (message or comment link, or a quotation)")
    parser.add_argument("--eligibility", default=None, metavar="BUNDLE",
                        help="the assurance bundle (assurance_product.py) whose evidence the release decision is recomputed from")
    args = parser.parse_args(argv)

    if not _release_eligible(args.slug, args.eligibility):
        return 1

    try:
        decision = accept(args.slug, args.note, args.accept_open, approval_ref=args.approval_ref)
    except (ValueError, OSError, RuntimeError, EOFError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Owner accepted {args.slug} @ {decision['render_digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
