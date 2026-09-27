#!/usr/bin/env python3
"""Build every product through the one pipeline; publish only what passes the gate.

For every product manifest in products/<subject>/*.manifest.json:
1. render with render_core (a draft when gaps remain);
2. print the PDFs from the pages;
3. run the rendered quality gate.

A product is copied to public/products/<subject>/<name>/ only when its gate verdict is PASS AND an
independent product review of this exact render (products/verification/<name>.review.json, with
`render_digest` equal to the render receipt's digest) records no open S0 or S1 finding. A product
that is not cleared has any earlier public copy removed.
The status report (products/STATUS.md and products/status.v1.json) lists every product with
its verdict, its gap count and its duties, so the board and the owner see why a product is
not live.

Usage:
    build_products.py derive      # (re)derive a manifest for every library package
    build_products.py build [--static] [--only NAME]
"""
from __future__ import annotations

import argparse
import collections
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
PUBLIC = REPO / "public" / "products"
REVIEWS = PRODUCTS / "verification"
REVIEW_BLOCKING = {"S0", "S1"}


def review_clearance(name: str, digest: str, reviews: Path = REVIEWS) -> str | None:
    """None when an independent review of this render leaves nothing blocking; else why not."""
    path = reviews / f"{name}.review.json"
    if not path.is_file():
        return "NO_REVIEW"
    review = json.loads(path.read_text(encoding="utf-8"))
    if review.get("render_digest") != digest:
        return "REVIEW_STALE"                          # the review saw a different render
    if any(f.get("severity") in REVIEW_BLOCKING and not f.get("resolved") for f in review.get("findings", [])):
        return "REVIEW_BLOCKING"
    return None


def manifests() -> list[Path]:
    return sorted(PRODUCTS.glob("*/*.manifest.json"))


def learner_title(pkg: dict, name: str) -> str:
    """The learner-facing name: the package's first bucket title (scope_summary is internal prose)."""
    return next((b["title"] for b in pkg.get("buckets", []) if b.get("title")), name.replace("-", " ").capitalize())


def _old_default_title(pkg: dict, name: str) -> str:
    """What earlier versions derived: scope_summary cut at 80 characters. Such a title is replaced."""
    return pkg.get("scope_summary", name).split(".")[0][:80]


def derive_all() -> list[Path]:
    out = []
    for path in package_migrate.package_paths():
        pkg = json.loads(path.read_text(encoding="utf-8"))
        subject = pkg["subject"]
        bank = REPO / subject / "library" / "exam-bank" / "competitive-exam-question-bank.v2.json"
        name = path.name.replace(".v1.json", "")
        target = PRODUCTS / subject.lower() / f"{name}.manifest.json"
        m = product_manifest.derive(str(path.relative_to(REPO)), [str(bank.relative_to(REPO))] if bank.is_file() else [],
                                    f"PRODUCT-{name.upper()}", learner_title(pkg, name),
                                    "../../../index.html", "../../../question-bank/index.html")
        if target.is_file():                           # keep owner/agent edits: ledger, diagnostic, title
            old = json.loads(target.read_text(encoding="utf-8"))
            for key in ("title", "ledger", "diagnostic", "diagnostic_min", "intake_digest", "prerequisite_links"):
                if key in old and not (key == "title" and old[key] == _old_default_title(pkg, name)):
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
    published = None
    review = review_clearance(name, receipt["digest"]) if report["verdict"] == "PASS" else None
    dest = PUBLIC / manifest.parent.name / name
    if dest.exists():
        shutil.rmtree(dest)                            # nothing stays live that is not cleared now
    if report["verdict"] == "PASS" and review is None:
        shutil.copytree(out, dest, ignore=shutil.ignore_patterns("*.pdf"))   # PDF = print of the page, on demand
        published = str(dest.relative_to(REPO))
    return {"product": name, "subject": m["subject"], "product_id": m["product_id"], "verdict": report["verdict"],
            "fail_reasons": report["fail_reasons"], "gaps": len(receipt["gaps"]),
            "gap_kinds": dict(collections.Counter(g["duty"] for g in receipt["gaps"])),
            "blocking_findings": sum(1 for f in report["findings"] if f["severity"] in quality_gate.BLOCKING),
            "render_digest": receipt["digest"], "review": review, "published": published}


def status_markdown(rows: list[dict]) -> str:
    live = sum(1 for r in rows if r["published"])
    lines = ["# Product status", "",
             "Generated by `python3 Shared/tools/build_products.py build`. A product goes live only when the",
             "rendered quality gate passes; until then its gaps are duties on the board",
             "(`library_board.py --subject <S> --depth`).", "",
             f"{live} of {len(rows)} products live.", "",
             "A product that passes the gate still waits for an independent product review of its exact render",
             "(`products/verification/<name>.review.json` with `render_digest`) with no open S0/S1 finding.", "",
             "| Product | Subject | Verdict | Review | Gaps | Blocking findings | Largest gap kinds |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        top = ", ".join(f"{k} {v}" for k, v in sorted(r["gap_kinds"].items(), key=lambda kv: -kv[1])[:3])
        review = "live" if r["published"] else (r.get("review") or "—")
        lines.append(f"| {r['product']} | {r['subject']} | {r['verdict']} | {review} | {r['gaps']} | {r['blocking_findings']} | {top} |")
    return "\n".join(lines) + "\n"


RATCHET = PRODUCTS / "ratchet.v1.json"


def current_gaps() -> dict[str, int]:
    """Render every product in memory and count its gaps (no browser, no files)."""
    out = {}
    for m in manifests():
        _, gaps, _ = render_core.build(m)
        out[m.name.replace(".manifest.json", "")] = len(gaps)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("derive")
    b = sub.add_parser("build")
    b.add_argument("--static", action="store_true")
    b.add_argument("--only")
    r = sub.add_parser("ratchet", help="gap counts may only go down; --write lowers the baseline")
    r.add_argument("--write", action="store_true")
    r.add_argument("--raise-bar", metavar="REASON",
                   help="the contract or duties got stricter: rebaseline to today's counts and record why")
    a = p.parse_args(argv)
    if a.cmd == "ratchet":
        now = current_gaps()
        base = json.loads(RATCHET.read_text(encoding="utf-8"))["gaps"] if RATCHET.is_file() else {}
        worse = {k: (base[k], v) for k, v in now.items() if k in base and v > base[k]}
        for k, (was, is_) in worse.items():
            print(f"RATCHET: {k} gaps rose from {was} to {is_}", file=sys.stderr)
        if a.raise_bar:
            doc = json.loads(RATCHET.read_text(encoding="utf-8")) if RATCHET.is_file() else {"schema": "product-ratchet/v1"}
            history = doc.get("bar_raises", [])
            history.append({"reason": a.raise_bar, "from_total": sum(base.values()), "to_total": sum(now.values())})
            RATCHET.write_text(json.dumps({"schema": "product-ratchet/v1", "gaps": now, "bar_raises": history},
                                          indent=2) + "\n", encoding="utf-8")
            print(f"bar raised: baseline {sum(base.values())} -> {sum(now.values())} ({a.raise_bar})")
            return 0
        if a.write and not worse:
            RATCHET.write_text(json.dumps({"schema": "product-ratchet/v1", "gaps": {k: min(v, base.get(k, v)) for k, v in now.items()},
                                           "bar_raises": json.loads(RATCHET.read_text(encoding="utf-8")).get("bar_raises", []) if RATCHET.is_file() else []},
                                          indent=2) + "\n", encoding="utf-8")
        print(f"{sum(now.values())} gaps across {len(now)} products (baseline {sum(base.values()) if base else 'none'})")
        return 1 if worse else 0
    if a.cmd == "derive":
        print(f"{len(derive_all())} product manifests")
        return 0
    rows = [build_one(m, a.static) for m in manifests() if not a.only or a.only in m.name]
    if not a.only:
        (PRODUCTS / "status.v1.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        (PRODUCTS / "STATUS.md").write_text(status_markdown(rows), encoding="utf-8")
    waiting = [f"{r['product']} ({r['review']})" for r in rows if r["verdict"] == "PASS" and not r["published"]]
    if waiting:
        print("gate PASS, waiting for product review: " + ", ".join(waiting) + f"; the review must carry render_digest")
    print(f"{sum(1 for r in rows if r['published'])} of {len(rows)} products passed the gate and review and are live")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
