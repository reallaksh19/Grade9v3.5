#!/usr/bin/env python3
"""Deploy stress-run output to the TEST area of the site, as labelled drafts.

TEST is a sandbox subject (see TEST/README.md). Nothing deployed here is reviewed, accepted or curriculum, so
this is deliberately not `accept_product.py`: it renders a TEST manifest as a draft, stamps every page with a
TEST banner, and writes a receipt that says `accepted: false`. It refuses anything that is not TEST.

    python3 Shared/tools/deploy_test.py product TEST/products/SLUG.manifest.json
    python3 Shared/tools/deploy_test.py interactive TEST/interactive/SLUG   # explorer.json: built and checked; or index.html + interactive.json: hand-written
    python3 Shared/tools/deploy_test.py pages            # rebuild the TEST pages, then the Pages mirror (docs/)
    python3 Shared/tools/deploy_test.py pages --check    # verify both without writing

`product` and `interactive` rebuild the TEST pages and then the GitHub Pages mirror (docs/) unless `--no-mirror`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import (build_pages_site, build_test_site, explorer_build, product_manifest, quality_gate, render_core,  # noqa: E402
                          site_nav_audit, toughest_concept)
from Shared.tools import web_blueprint_contract as blueprints  # noqa: E402

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
GAPS_SHOWN = 60          # a ten-question bank held to the benchmark can have dozens; the receipt keeps all
QUALITY_SHOWN = 12
# Rules about roles a manifest did not ask for follow from the Owner's scope, not from the pages: a Core2-and-Core1A job is
# not "missing" Core1B. They are left out of the findings and named in the receipt.
ROLE_SCOPED_RULES = {"PRODUCT-ALL-ROLES"}
# These three rules read the blueprint's component list off the pages; the gaps and advisories already say the same thing, with
# the record to author. They stay in the receipt and are left out of the console summary.
RESTATED_RULES = {"BP-COMPONENTS-REQUIRED", "BP-COMPONENTS-EXPECTED", "BP-COMPONENTS-DEPTH"}


def blueprint_refs(roles: list[str]) -> dict[str, str]:
    """The blueprint each role's page was built from (id@version)."""
    registry = blueprints.load_registry()
    return {role: blueprints.blueprint_ref(bp) for role in roles
            if (bp := blueprints.blueprint_for_role(registry, role)) is not None}


def authoring_hints(roles: list[str]) -> dict[str, dict]:
    """What the blueprint tells an author to write for each component: {component: {level, hint}}."""
    registry = blueprints.load_registry()
    out: dict[str, dict] = {}
    for role in roles:
        bp = blueprints.blueprint_for_role(registry, role)
        for cid, level, hint in (blueprints.authoring_hints(bp) if bp else []):
            out.setdefault(cid, {"level": level, "hint": hint})
    return out


def quality_report(folder: Path, slug: str, roles: list[str]) -> dict:
    """The learner-quality contract read off the deployed pages (static: no browser), as a receipt block.

    The depth gaps say what a record lacks; this says what the learner would actually see: a figure shared by seventeen
    units, a figure with no stages, a role with no page. It never says the content is good."""
    scoped = set(roles) != set(product_manifest.OUTPUT_ROLES)
    try:
        report = quality_gate.gate(folder, "TEST", slug, static=True)
    except Exception as caught:   # the report is advice; a failure to make it must be said, not hidden
        return {"checked": "not run", "error": f"{type(caught).__name__}: {caught}", "findings": [], "continuity": []}
    left_out = sorted({f["rule"] for f in report["findings"] if scoped and f["rule"] in ROLE_SCOPED_RULES})
    findings = [{key: f[key] for key in ("severity", "rule", "where", "detail")} for f in report["findings"]
                if not (scoped and f["rule"] in ROLE_SCOPED_RULES)]
    continuity = [c for c in report["continuity"] if not (scoped and "CORE1B" not in roles and c["code"] == "CONT_1A_1B_PARITY")]
    return {
        "checked": "static: the pages' own markers against Shared/quality/learner-quality.v1.json; no browser measurement",
        "findings": findings,
        "continuity": continuity,
        "left_out": left_out + (["CONT_1A_1B_PARITY"] if len(continuity) != len(report["continuity"]) else []),
    }
EXTERNAL = re.compile(r"""(?:src|href)\s*=\s*["']\s*(?:https?:)?//""", re.IGNORECASE)
EXTERNAL_CSS = re.compile(r"""@import\s+(?:url\()?\s*["']?\s*(?:https?:)?//""", re.IGNORECASE)


class DeployError(ValueError):
    """An input problem, reported as one line and exit status 1."""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def banner(home: str) -> str:
    return (f'<div data-g9-test-banner role="note" style="background:#7c2d12;color:#fff;padding:0 14px;'
            f'font:600 14px/1.4 system-ui,sans-serif">{BANNER_TEXT} · <a href="{home}" style="color:#fde68a;display:inline-block;'
            f'min-height:48px;line-height:48px;padding:0 8px">TEST home</a></div>')


def _stamp(page: str, top: str) -> str:
    """Mark the page as TEST in the markup itself: `top` right after the body tag and an attribute on the html element."""
    if page.count("<body") != 1 or page.count("<html") != 1:
        raise DeployError("a page must have exactly one html element and one body element to be stamped as TEST")
    page = re.sub(r"(<html\b)", r'\1 data-g9-test="sandbox-draft"', page, count=1)
    page = re.sub(r"(<title[^>]*>)", r"\1TEST draft · ", page, count=1)   # the browser tab and history say it too
    return re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + top, page, count=1)


def stamp(page: str, home: str) -> str:
    """A rendered product page: it has the shared shell header already, so it gets the draft banner only."""
    return _stamp(page, banner(home))


def _slug(value: str, what: str) -> str:
    if not SLUG.fullmatch(value or ""):
        raise DeployError(f"{what} {value!r} must match {SLUG.pattern}")
    return value


# ------------------------------------------------------------------ products

PRINT_TOOL = REPO / "tools" / "print" / "print-product.mjs"


def print_pdfs(out: Path) -> dict:
    """Print the learner PDF of each deployed page, as the browser prints it (the draft's TEST banner included).

    Every role page links the PDF printed from it (the shell's PRINT_PDF control), so a deploy that cannot print leaves links that go
    nowhere: it says so, in the receipt and on the page of Deployments, and does not pretend. Only the learner copy is printed here; a key
    PDF holds the answers and a TEST sandbox does not make one."""
    node = shutil.which("node")
    if not node:
        return {"status": "NOT_PRINTED", "reason": "node is not installed, so the PDF links of these pages go nowhere", "files": {}}
    try:
        run = subprocess.run([node, str(PRINT_TOOL), str(out)], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as caught:
        return {"status": "NOT_PRINTED", "reason": f"printing failed: {caught}", "files": {}}
    if run.returncode:
        reason = (run.stderr or run.stdout).strip().splitlines()[-1:] or ["no message"]
        return {"status": "NOT_PRINTED", "reason": f"print-product.mjs exited {run.returncode}: {reason[0][:200]}", "files": {}}
    problems = render_core.pdf_publication_problems(out)
    files = {pdf.name: _sha(pdf.read_bytes()) for pdf in sorted(out.glob("*.pdf"))}
    return {"status": "PRINTED" if not problems else "MISMATCH", "reason": "; ".join(problems), "files": files}


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
            # New authoring is held to the benchmark: the reference depth, and every expected component present or waived.
            pages, gaps, digest, advisories, waived = render_core.build_report(staged, "PAGES", held_to="REFERENCE")
            toughest = toughest_concept.for_manifest(staged)
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
    printed = print_pdfs(out)
    if printed["status"] != "PRINTED":
        print(f"deploy_test: the PDF links of {slug} do not work: {printed['reason']}", file=sys.stderr)
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
        "draft": True,                      # everything deployed here is a sandbox draft, whatever the gap count
        "gap_count": len(gaps),
        "gaps_by_core": dict(sorted(by_core.items())),
        "gaps": [{key: gap.get(key) for key in ("core", "duty", "record", "detail", "component") if gap.get(key)} for gap in gaps],
        "advisories": [{key: row.get(key) for key in ("core", "component", "record", "detail")} for row in advisories],
        "waived": [{key: row.get(key) for key in ("core", "component", "record", "reason")} for row in waived],
        "held_to": "REFERENCE",
        "toughest": toughest,               # the concept the concept book and the interactive page are built for
        "blueprints": blueprint_refs(product_manifest.selected_output_roles(manifest)),
        "authoring": authoring_hints(product_manifest.selected_output_roles(manifest)),
        "quality": quality_report(out, slug, product_manifest.selected_output_roles(manifest)),
        "roles": product_manifest.selected_output_roles(manifest),
        "selection_counts": {key: len(selection.get(key) or []) for key in product_manifest.SELECTION_KEYS},
        "empty_roles": render_core.empty_roles(manifest),
        "pages": written,
        "pdf": printed,                     # the learner PDF printed from each role page, which the page links (never a key PDF)
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
    """An explorer spec (explorer.json) is built into a page whose numbers are checked; a hand-written page is accepted as a draft and said to be unchecked."""
    source = source.resolve()
    if (source / explorer_build.SPEC_FILE).is_file():
        return deploy_explorer(source)
    return deploy_hand_written(source)


def _write_interactive(out: Path, files: dict[str, bytes]) -> dict[str, str]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    written = {}
    for name, data in sorted(files.items()):
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        written[name] = _sha(data)
    return written


def _links_resolve(out: Path, slug: str, written: dict[str, str]) -> None:
    missing = {name: site_nav_audit.missing_targets(REPO / "public", out / name) for name in written if name.endswith(".html")}
    missing = {name: refs for name, refs in missing.items() if refs}
    if missing:
        shutil.rmtree(out)
        detail = "; ".join(f"{name} links to {', '.join(refs)}" for name, refs in sorted(missing.items()))
        raise DeployError(f"{detail} (no such file at the deployed location public/test/interactive/{slug}/; "
                          "put it in the page's folder and link it relative to index.html)")


def deploy_explorer(source: Path) -> dict:
    """Build the explorer from its spec, refuse it if a number in it is wrong, and deploy it as a draft with its contract and its evidence."""
    if not source.is_dir() or not source.resolve().is_relative_to((TEST_ROOT / "interactive").resolve()):
        raise DeployError("an interactive page source must be a directory under TEST/interactive/")
    try:
        document, compiled, spec, report, brief = explorer_build.build(source)
    except (ValueError, json.JSONDecodeError) as caught:
        raise DeployError(str(caught)) from caught
    rel = source.relative_to(REPO).as_posix()
    if report.errors:
        shown = "\n".join(f"  {f.line()}" for f in report.errors[:12])
        more = f"\n  ... {len(report.errors) - 12} more" if len(report.errors) > 12 else ""
        raise DeployError(f"{len(report.errors)} error(s) in {explorer_build.SPEC_FILE}; no page was written (a page that would show a number nobody checked, "
                          f"or break, is not deployed):\n{shown}{more}\nrun python3 Shared/tools/explorer_build.py check {rel} for the rest and how to author each")
    slug = _slug(str(spec["slug"]), "slug")
    out = PUBLIC_TEST / "interactive" / slug
    page = _stamp(document, build_test_site.sandbox_bar("../../../")).encode("utf-8")
    locator = f"public/test/interactive/{slug}/index.html"
    design = explorer_build.contract(spec, brief, locator)
    problems = explorer_build.contract_findings(design)
    if problems:
        raise DeployError("the design contract written for this page does not match Shared/library/explorer_design_contract.schema.json "
                          "(a fault in the builder, not in the spec): " + "; ".join(problems[:4]))
    evidence = explorer_build.evidence_record(spec, report, _sha(page))
    written = _write_interactive(out, {"index.html": page,
                                       "explorer-contract.json": (json.dumps(design, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
                                       "explorer-evidence.json": (json.dumps(evidence, indent=2, ensure_ascii=False) + "\n").encode("utf-8")})
    _links_resolve(out, slug, written)
    toughest = brief.brief
    spec_path = source / explorer_build.SPEC_FILE
    receipt = {
        "schema": INTERACTIVE_RECEIPT_SCHEMA,
        "slug": slug,
        "title": spec["title"],
        "purpose": f"A guided explorer of the toughest concept of the set ({toughest['label']}): {spec['target']['operation']}",
        "records": [r for r in [toughest["question_ref"], toughest.get("microtopic_ref"), *(toughest.get("relation_refs") or [])] if r],
        "blueprint_ref": spec["blueprint_ref"],
        "built_by": "EXPLORER_BUILDER",
        "builder": explorer_build.BUILDER,
        "machine_checked": True,
        "toughest": toughest,
        "product": spec["product"],
        "links": brief.links(),
        "gap_count": len(report.gaps),
        "gaps": [{"component": f.component, "where": f.where, "detail": f.detail} for f in report.gaps],
        "checks": report.evidence,
        "design_contract": {"file": "explorer-contract.json", "conformance_status": design["conformance_status"], "audit_status": design["quality_audit"]["audit_status"]},
        "source": rel,
        "source_sha256": {explorer_build.SPEC_FILE: _sha(spec_path.read_bytes())},
        "files": written,
        "status": "DRAFT",
        "accepted": False,
        "notice": NOTICE,
    }
    (out / "interactive-receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


def deploy_hand_written(source: Path) -> dict:
    meta, files = _validate_interactive(source)
    out = PUBLIC_TEST / "interactive" / meta["slug"]
    contents = {}
    for path in files:
        rel = path.relative_to(source).as_posix()
        data = path.read_bytes()
        if rel == "index.html":
            # The page brings no shell header of its own, so it gets the sandbox header: draft label, portal, TEST pages.
            data = _stamp(data.decode("utf-8"), build_test_site.sandbox_bar("../../../")).encode("utf-8")
        contents[rel] = data
    written = _write_interactive(out, contents)
    _links_resolve(out, meta["slug"], written)
    receipt = {
        "schema": INTERACTIVE_RECEIPT_SCHEMA,
        "slug": meta["slug"],
        "title": meta["title"],
        "purpose": meta["purpose"],
        "records": meta["records"],
        "blueprint_ref": meta["blueprint_ref"],
        "built_by": "HAND_WRITTEN",
        "machine_checked": False,
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

def _print_blueprint_notes(receipt: dict) -> None:
    """Say what the blueprint asks for, once per component, beside the gaps and advisories that name the records."""
    hints = receipt.get("authoring") or {}
    refs = ", ".join(receipt.get("blueprints", {}).values())
    gap_components = sorted({g["component"] for g in receipt["gaps"] if g.get("component")})
    if gap_components:
        print(f"required by the blueprint ({refs}); how to author each:")
        for cid in gap_components:
            print(f"  {cid}: {(hints.get(cid) or {}).get('hint', 'see the blueprint component')}")
    waived = receipt.get("waived") or []
    if waived:
        print(f"waived by the records, each with a written reason ({len(waived)}):")
        for row in waived:
            print(f"  {row['component']} · {row['record']}: {row['reason']}")
    advised: dict[str, list[str]] = {}
    for row in receipt.get("advisories", []):
        advised.setdefault(row["component"], []).append(row["record"])
    if advised:
        print("expected by the blueprint and absent (advisory, not a gap; the reference page has each):")
        for cid, records in sorted(advised.items()):
            hint = (hints.get(cid) or {}).get("hint")
            print(f"  {cid}: {len(records)} record(s), e.g. {records[0]}" + (f". {hint}" if hint else ""))


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
    p.add_argument("--no-mirror", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "pages":
            if args.check:
                # The Atlas reads public/data/data.js and the site is served from docs/, so a stale copy there counts.
                findings = build_test_site.check() + ([] if args.no_mirror else build_pages_site.check(REPO))
                print("\n".join(findings) if findings else "TEST pages and the Pages mirror are current")
                return 1 if findings else 0
            build_test_site.write()
            if not args.no_mirror:
                build_pages_site.write(REPO)
            return 0
        if args.cmd == "product":
            receipt = deploy_product(Path(args.manifest))
            print(f"deployed {receipt['slug']}: {len(receipt['pages'])} page(s), "
                  f"DRAFT, {str(receipt['gap_count']) + ' gap(s)' if receipt['gap_count'] else 'no gaps reported (that is not a review)'}, accepted=false")
            print("selected records: " + " ".join(f"{k}={v}" for k, v in receipt["selection_counts"].items()))
            shown = receipt["gaps"][:GAPS_SHOWN]
            for gap in shown:
                print(f"  gap {gap['core']:6s} {gap['record']}: {gap['detail']}")
            if len(receipt["gaps"]) > len(shown):
                print(f"  ... {len(receipt['gaps']) - len(shown)} more in public/test/products/{receipt['slug']}/deploy-receipt.json")
            _print_blueprint_notes(receipt)
            print("\n".join(toughest_concept.describe(receipt.get("toughest"))))
            quality = receipt["quality"]
            if quality.get("error"):
                print(f"  quality check could not run: {quality['error']}", file=sys.stderr)
            else:
                findings = [f for f in quality["findings"] if f["rule"] not in RESTATED_RULES] + [{"severity": "CONT", "rule": c["code"], "where": "", "detail": c["detail"]}
                                                  for c in quality["continuity"]]
                counts = {}
                for finding in findings:
                    counts[finding["severity"]] = counts.get(finding["severity"], 0) + 1
                print("quality (static): " + (", ".join(f"{n} {sev}" for sev, n in sorted(counts.items())) if findings
                                              else "no finding") + "; it checks what the learner sees, not that it is right")
                for finding in findings[:QUALITY_SHOWN]:
                    print(f"  {finding['severity']:4s} {finding['rule']} {finding['where']}: {finding['detail']}")
                if len(findings) > QUALITY_SHOWN:
                    print(f"  ... {len(findings) - QUALITY_SHOWN} more in public/test/products/{receipt['slug']}/deploy-receipt.json")
            for role in receipt["empty_roles"]:
                print(f"WARNING: {role} is part of this product but selects no records, so its page has no items.", file=sys.stderr)
        else:
            receipt = deploy_interactive(Path(args.source))
            print(f"deployed interactive {receipt['slug']}: {len(receipt['files'])} file(s), DRAFT, accepted=false")
            if receipt["built_by"] == "EXPLORER_BUILDER":
                brief = receipt["toughest"]
                print(f"built by the explorer builder for the toughest concept of the set, {brief['label']} ({brief['question_ref']}); "
                      f"{receipt['checks'].get('states_checked', 0)} positions of the sliders checked; {receipt['gap_count']} gap(s)")
                for gap in receipt["gaps"][:GAPS_SHOWN]:
                    print(f"  gap {gap['component']:12s} {gap['where']}: {gap['detail']}")
                if receipt["gaps"]:
                    print("how to author what is flagged: python3 Shared/tools/explorer_build.py check " + receipt["source"])
                links = receipt["links"]
                if not (links.get("question") or links.get("concept")):
                    print("note: the product pages for this question are not deployed, so the end of the route has nothing to link back to. "
                          "Deploy the product first, then this page again.")
            else:
                print("note: this page was written by hand, so nothing in it is machine-checked and it is not built from the explorer blueprint. "
                      "Write TEST/interactive/SLUG/explorer.json instead (python3 Shared/tools/explorer_build.py new TEST/products/SLUG.manifest.json).",
                      file=sys.stderr)
        build_test_site.write()
        if not args.no_mirror:
            build_pages_site.write(REPO)
    except (DeployError, ValueError, json.JSONDecodeError) as caught:
        print(f"deploy_test: {caught}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
