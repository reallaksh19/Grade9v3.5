#!/usr/bin/env python3
"""Derive a product manifest: which units and questions a Core product shows, in which order.

A manifest holds selection only, never content. render_core.py reads the content from the
library records the manifest names. The derivation is mechanical:
- Core1, Core1A and Core1B: every microtopic of the package, in package order.
- Core2A and Core2B: the package questions exposed to that Core.
- Core2: exam-bank items whose capability or concept bucket belongs to the package.

Usage:
    product_manifest.py derive --package Physics/library/phy-kin-2d-motion.v1.json \
        --bank Physics/library/exam-bank/competitive-exam-question-bank.v2.json \
        --product-id PRODUCT-PHY-KIN-2D --title "Motion in a Plane" --home ../../index.html --out M.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def derive(package_ref: str, bank_refs: list[str], product_id: str, title: str, home: str,
           question_bank_href: str | None = None) -> dict:
    pkg = json.loads((REPO / package_ref).read_text(encoding="utf-8"))
    caps = {c["id"] for c in pkg.get("capabilities", [])}
    buckets = {b["id"] for b in pkg.get("buckets", [])}

    def exposed(core):
        return [q["id"] for q in pkg.get("questions", []) if any(e["core"] == core for e in q.get("exposure", []))]

    core2 = []
    for ref in bank_refs:
        for q in json.loads((REPO / ref).read_text(encoding="utf-8")).get("questions", []):
            bucket = ((q.get("extensions") or {}).get("grade9v3:analysis") or {}).get("concept_bucket")
            if q.get("primary_capability_ref") in caps or bucket in buckets:
                core2.append(q["id"])
    return {
        "schema": "product-manifest/v1",
        "product_id": product_id,
        "title": title,
        "subject": pkg["subject"],
        "home_href": home,
        "question_bank_href": question_bank_href or home,
        "package_refs": [package_ref],
        "bank_refs": bank_refs,
        "selection": {
            "microtopics": [m["id"] for m in pkg.get("microtopics", [])],
            "core2": core2,
            "core2a": exposed("CORE2A"),
            "core2b": exposed("CORE2B"),
        },
    }


def with_intake(manifest: dict, intake: dict) -> dict:
    """Attach the owner's inputs (raw_intake coverage ledger) and the diagnostic minimum.

    Each ledger row starts unresolved. A researcher or author resolves it to the record that
    teaches the input (`teaching`, a microtopic id) or practises it (`practice`, a question id).
    The gate fails every row that is unresolved or not rendered.
    """
    m = dict(manifest)
    m["intake_digest"] = intake["intake_digest"]
    m["ledger"] = [{"input_id": r["input_id"], "kind": r["kind"], "teaching": r.get("teaching"), "practice": r.get("practice")}
                   for r in intake["coverage_ledger_template"]]
    m["diagnostic_min"] = intake["learner_start"]["diagnostic"]["min_items"]
    m.setdefault("diagnostic", [])
    return m


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("derive")
    d.add_argument("--package", required=True)
    d.add_argument("--bank", action="append", default=[])
    d.add_argument("--product-id", required=True)
    d.add_argument("--title", required=True)
    d.add_argument("--home", required=True)
    d.add_argument("--question-bank")
    d.add_argument("--out", required=True)
    d.add_argument("--intake", help="raw_intake output (research-first-intake/v1): adds the owner's ledger and diagnostic")
    a = p.parse_args(argv)
    m = derive(a.package, a.bank, a.product_id, a.title, a.home, a.question_bank)
    if a.intake:
        m = with_intake(m, json.loads(Path(a.intake).read_text(encoding="utf-8")))
    Path(a.out).write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = m["selection"]
    print(f"{a.out}: {len(s['microtopics'])} microtopics, Core2 {len(s['core2'])}, Core2A {len(s['core2a'])}, Core2B {len(s['core2b'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
