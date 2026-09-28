#!/usr/bin/env python3
"""Build every product through the one pipeline and report observations.

For every product manifest in products/<subject>/*.manifest.json:
1. render with render_core (a draft when gaps remain);
2. print the PDFs from the pages;
3. run the rendered quality gate.

This command stages PAGES and SINGLE_FILE renders in publication/. It never writes
to or deletes from public/products or standalone/products. The Owner accepts an
exact render through accept_product.py; gate and review findings are advisory.

Usage:
    build_products.py derive      # (re)derive a manifest for every library package
    build_products.py build [--static] [--only NAME]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import package_migrate, product_manifest, quality_gate, render_core  # noqa: E402

PRODUCTS = REPO / "products"
WORK = REPO / "publication" / "products"          # git-ignored build area
PUBLIC = REPO / "public" / "products"  # read-only here
STANDALONE_WORK = REPO / "publication" / "standalone" / "products"
STANDALONE = REPO / "standalone" / "products"  # read-only here
REVIEWS = PRODUCTS / "verification"
ACCEPTANCE = PRODUCTS / "acceptance"


def decision_state(name: str, subject: str, digest: str) -> tuple[str, str | None]:
    """Describe the review and accepted render; never authorize publication."""
    path = REVIEWS / f"{name}.review.json"
    review = "NO_REVIEW"
    if path.is_file():
        observed = json.loads(path.read_text(encoding="utf-8"))
        review = "CURRENT" if observed.get("render_digest") == digest else "REVIEW_STALE"
    accepted = ACCEPTANCE / f"{name}.json"
    if not accepted.is_file():
        return review, None
    record = json.loads(accepted.read_text(encoding="utf-8"))
    if record.get("render_digest") != digest:
        return review, "ACCEPTED_EARLIER_RENDER"
    dest = PUBLIC / subject.lower() / name
    receipt = dest / "render-receipt.json"
    if not receipt.is_file():
        return review, "ACCEPTED_NOT_MIRRORED"
    from Shared.tools.accept_product import verify_render  # noqa: PLC0415
    try:
        public_digest = verify_render(dest)["digest"]
    except (ValueError, OSError, KeyError, json.JSONDecodeError):
        return review, "PUBLIC_RENDER_INVALID"
    return review, str(dest.relative_to(REPO)) if public_digest == digest else "PUBLIC_DIGEST_MISMATCH"


def accepted_standalone(name: str, subject: str, digest: str) -> str | None:
    """Report a standalone page only when it matches this Owner decision."""
    accepted = ACCEPTANCE / f"{name}.json"
    dest = STANDALONE / subject.lower() / f"{name}.html"
    if not accepted.is_file() or not dest.is_file():
        return None
    record = json.loads(accepted.read_text(encoding="utf-8"))
    if record.get("render_digest") != digest or not record.get("standalone_sha256"):
        return None
    if hashlib.sha256(dest.read_bytes()).hexdigest() != record["standalone_sha256"]:
        return None
    return str(dest.relative_to(REPO))


def manifests() -> list[Path]:
    return sorted(PRODUCTS.glob("*/*.manifest.json"))


def derive_all() -> list[Path]:
    out = []
    for path in package_migrate.package_paths():
        pkg = json.loads(path.read_text(encoding="utf-8"))
        subject = pkg["subject"]
        bank = REPO / subject / "library" / "exam-bank" / "competitive-exam-question-bank.v2.json"
        name = path.name.replace(".v1.json", "")
        target = PRODUCTS / subject.lower() / f"{name}.manifest.json"
        m = product_manifest.derive(str(path.relative_to(REPO)), [str(bank.relative_to(REPO))] if bank.is_file() else [],
                                    f"PRODUCT-{name.upper()}",
                                    "../../../index.html", "../../../question-bank/index.html")
        if target.is_file():                           # keep owner/agent selection edits
            old = json.loads(target.read_text(encoding="utf-8"))
            for key in ("ledger", "diagnostic", "diagnostic_min", "intake_digest", "prerequisite_links"):
                if key in old:
                    m[key] = old[key]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        out.append(target)
    return out


def build_one(manifest: Path, static: bool) -> dict:
    m = json.loads(manifest.read_text(encoding="utf-8"))
    name = manifest.name.replace(".manifest.json", "")
    out = WORK / manifest.parent.name / name
    if out.exists():
        shutil.rmtree(out)
    render_core.main(["build", "--manifest", str(manifest), "--out", str(out), "--draft"])
    receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
    if not receipt["gaps"] and shutil.which("node"):
        subprocess.run(["node", str(REPO / "tools/print/print-product.mjs"), str(out)], capture_output=True)
    report = quality_gate.gate(out, m["subject"], m["product_id"], static=static)
    (out / "gate-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    single_pages, single_gaps, single_digest = render_core.build(manifest, mode="SINGLE_FILE")
    semantic_digest = receipt.get("semantic_digest")
    single_semantic_digest = render_core.semantic_metadata_digest(single_pages, "SINGLE_FILE")
    if semantic_digest is not None and semantic_digest != single_semantic_digest:
        raise RuntimeError(f"{name}: SINGLE_FILE semantic metadata/search differs from PAGES")
    staged_standalone = STANDALONE_WORK / manifest.parent.name / f"{name}.html"
    staged_standalone.parent.mkdir(parents=True, exist_ok=True)
    standalone_bytes = single_pages["product.html"].encode("utf-8")
    staged_standalone.write_bytes(standalone_bytes)
    staged_standalone.with_suffix(".receipt.json").write_text(json.dumps({
        "pages_digest": receipt["digest"], "render_digest": single_digest,
        "sha256": hashlib.sha256(standalone_bytes).hexdigest(), "mode": "SINGLE_FILE",
        "semantic_digest": single_semantic_digest,
    }, indent=2) + "\n", encoding="utf-8")
    review, published = decision_state(name, m["subject"], receipt["digest"])
    return {"product": name, "subject": m["subject"], "product_id": m["product_id"], "verdict": report["verdict"],
            "fail_reasons": report["fail_reasons"], "gaps": len(receipt["gaps"]),
            "gap_kinds": dict(collections.Counter(g["duty"] for g in receipt["gaps"])),
            "blocking_findings": sum(1 for f in report["findings"] if f["severity"] in quality_gate.BLOCKING),
            "render_digest": receipt["digest"], "semantic_digest": semantic_digest,
             "review": review, "published": published,
            "standalone": accepted_standalone(name, m["subject"], receipt["digest"]),
            "staged_standalone": f"publication/standalone/products/{manifest.parent.name}/{name}.html",
            "standalone_render_digest": single_digest,
            "standalone_gaps": len(single_gaps)}


def status_markdown(rows: list[dict]) -> str:
    live = sum(1 for r in rows if r["published"] and str(r["published"]).startswith("public/"))
    lines = ["# Product status", "",
             "Generated by `python3 Shared/tools/build_products.py build`. The gate verdict",
             "and gaps are advisory observations. Only Owner acceptance of an exact digest",
             "through `accept_product.py` publishes a product.", "",
             f"{live} of {len(rows)} products have a matching accepted public receipt.", "",
             "| Product | Subject | Verdict | Review | Acceptance/publication | Standalone | Gaps | S0–S2 observations | Largest gap kinds |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        top = ", ".join(f"{k} {v}" for k, v in sorted(r["gap_kinds"].items(), key=lambda kv: -kv[1])[:3])
        review = r.get("review") or "—"
        lines.append(f"| {r['product']} | {r['subject']} | {r['verdict']} | {review} | {r['published'] or 'NOT_ACCEPTED'} | {r.get('standalone') or 'NOT_ACCEPTED'} | {r['gaps']} | {r['blocking_findings']} | {top} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("derive")
    b = sub.add_parser("build")
    b.add_argument("--static", action="store_true")
    b.add_argument("--only")
    a = p.parse_args(argv)
    if a.cmd == "derive":
        print(f"{len(derive_all())} product manifests")
        return 0
    rows = [build_one(m, a.static) for m in manifests() if not a.only or a.only in m.name]
    if not a.only:
        (PRODUCTS / "status.v1.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        (PRODUCTS / "STATUS.md").write_text(status_markdown(rows), encoding="utf-8")
    print(f"built {len(rows)} product(s); publication is an Owner acceptance decision")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
