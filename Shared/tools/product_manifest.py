#!/usr/bin/env python3
"""Derive a product manifest: which units, questions and Core roles a product shows.

A manifest holds selection only, never content. render_core.py reads the content from the
library records the manifest names. The derivation is mechanical:
- Core1, Core1A and Core1B: every microtopic of the package, in package order.
- Core2A and Core2B: the package questions exposed to that Core.
- Core2: exam-bank items whose capability or concept bucket belongs to the package.
- output_roles: optional learner-product role scope; absent preserves legacy all-six-role output.

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

SELECTION_KEYS = ("microtopics", "core2", "core2a", "core2b")
OUTPUT_ROLES = ("CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B")


class ProductSelectionError(ValueError):
    """The product manifest cannot be resolved to one unambiguous record authority."""


def selected_output_roles(manifest: dict) -> list[str]:
    """Resolve learner-product role scope without changing legacy manifests.

    Existing manifests predate first-stage scoped delivery and therefore imply all six roles.
    New manifests may opt into a strict non-empty subset. This field controls projection/output
    only; it never changes record authority, Core semantics or academic truth.
    """
    if "output_roles" not in manifest:
        return list(OUTPUT_ROLES)
    value = manifest["output_roles"]
    if not isinstance(value, list) or not value:
        raise ProductSelectionError("PRODUCT_OUTPUT_ROLES_INVALID: output_roles must be a non-empty list")
    if any(not isinstance(role, str) or role not in OUTPUT_ROLES for role in value):
        raise ProductSelectionError(
            "PRODUCT_OUTPUT_ROLES_INVALID: allowed=" + ",".join(OUTPUT_ROLES)
        )
    if len(value) != len(set(value)):
        raise ProductSelectionError("PRODUCT_OUTPUT_ROLES_DUPLICATE")
    return list(value)


def _unique_index(records: list[dict], authority: str, collection: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in records:
        record_id = row.get("id")
        if not isinstance(record_id, str) or not record_id:
            continue
        if record_id in out:
            raise ProductSelectionError(
                f"PRODUCT_SELECTION_AUTHORITY_DUPLICATE_ID: {authority}:{collection}:{record_id}"
            )
        out[record_id] = row
    return out


def validate_selection(manifest: dict, packages: list[dict], bank_questions: list[dict]) -> dict[str, list[dict]]:
    """Resolve every selected id exactly once in the authority owned by its Core role.

    This is deliberately stricter than renderer list filtering. A malformed selection is an
    integrity error, not an authoring-depth gap: strict and draft renders must both refuse a
    manifest that silently drops, duplicates, or crosses the package/source-bank boundary.
    """
    selected_output_roles(manifest)
    selection = manifest.get("selection")
    if not isinstance(selection, dict):
        raise ProductSelectionError("PRODUCT_SELECTION_INVALID: selection must be an object")

    missing_keys = [key for key in SELECTION_KEYS if key not in selection]
    if missing_keys:
        raise ProductSelectionError(
            "PRODUCT_SELECTION_KEYS_MISSING: " + ",".join(missing_keys)
        )

    package_microtopics = _unique_index(
        [row for package in packages for row in package.get("microtopics", [])],
        "PACKAGE",
        "microtopics",
    )
    package_questions = _unique_index(
        [row for package in packages for row in package.get("questions", [])],
        "PACKAGE",
        "questions",
    )
    bank_index = _unique_index(bank_questions, "BANK", "questions")

    resolved: dict[str, list[dict]] = {}
    for key in SELECTION_KEYS:
        selected = selection.get(key)
        if not isinstance(selected, list) or any(
            not isinstance(record_id, str) or not record_id for record_id in selected
        ):
            raise ProductSelectionError(
                f"PRODUCT_SELECTION_IDS_INVALID: {key} must contain non-empty string ids"
            )

        seen: set[str] = set()
        for record_id in selected:
            if record_id in seen:
                raise ProductSelectionError(
                    f"PRODUCT_SELECTION_DUPLICATE_ID: {key}:{record_id}"
                )
            seen.add(record_id)

        if key == "microtopics":
            expected = package_microtopics
            foreign: dict[str, dict] = {}
            expected_authority = "PACKAGE"
        elif key == "core2":
            expected = bank_index
            foreign = package_questions
            expected_authority = "BANK"
        else:
            expected = package_questions
            foreign = bank_index
            expected_authority = "PACKAGE"

        rows: list[dict] = []
        for record_id in selected:
            if record_id in foreign:
                raise ProductSelectionError(
                    f"PRODUCT_SELECTION_WRONG_AUTHORITY: {key}:{record_id}:expected={expected_authority}"
                )
            row = expected.get(record_id)
            if row is None:
                raise ProductSelectionError(
                    f"PRODUCT_SELECTION_UNRESOLVED: {key}:{record_id}:expected={expected_authority}"
                )
            rows.append(row)
        resolved[key] = rows

    return resolved


def derive(package_ref: str, bank_refs: list[str], product_id: str, home: str,
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
    d.add_argument("--home", required=True)
    d.add_argument("--question-bank")
    d.add_argument("--out", required=True)
    d.add_argument("--intake", help="raw_intake output (research-first-intake/v1): adds the owner's ledger and diagnostic")
    a = p.parse_args(argv)
    m = derive(a.package, a.bank, a.product_id, a.home, a.question_bank)
    if a.intake:
        m = with_intake(m, json.loads(Path(a.intake).read_text(encoding="utf-8")))
    Path(a.out).write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = m["selection"]
    print(f"{a.out}: {len(s['microtopics'])} microtopics, Core2 {len(s['core2'])}, Core2A {len(s['core2a'])}, Core2B {len(s['core2b'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
