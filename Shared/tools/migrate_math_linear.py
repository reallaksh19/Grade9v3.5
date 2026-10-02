#!/usr/bin/env python3
"""One-time M3 fold of the verified Mathematics staging records into the unit package.

`--write` reads the old staging file, merges through promote_verified.merge, writes a
compact ID/reference ledger, and checks every row before removing the staging copy.
The default read-only check works after the staging copy has been retired.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import library_board, promote_verified  # noqa: E402
SOURCE = REPO / "Mathematics/research/packages/MAT-09-LINEAR-EQUATIONS.package.json"
TARGET = REPO / "Mathematics/library/linear-equations.v1.json"
LEDGER = REPO / "Mathematics/units/linear-equations/M3-MIGRATION.json"
COLLECTIONS = ("resources", "buckets", "capabilities", "microtopics", "relations", "representations",
               "question_families", "questions", "known_issues", "application_contexts")
NODES = tuple(f"MAT-09-LINEAR-EQUATIONS-0{i}" for i in range(1, 5))


def canonical(row: dict) -> dict:
    row = copy.deepcopy(row)
    (row.get("extensions") or {}).pop("grade9v3:promotion", None)
    return row


def digest(row: dict) -> str:
    data = json.dumps(canonical(row), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def references(value, key: str = "") -> list[str]:
    """Preserve every explicitly named reference value, including nested role refs."""
    refs = []
    if isinstance(value, dict):
        for name, child in value.items():
            refs += references(child, name)
    elif isinstance(value, list):
        for child in value:
            refs += references(child, key)
    elif isinstance(value, str) and (key.endswith("_ref") or key.endswith("_refs")):
        refs.append(value)
    return sorted(refs)


def rows(package: dict) -> dict[str, dict[str, dict]]:
    return {collection: {row["id"]: row for row in package.get(collection, [])}
            for collection in COLLECTIONS}


def make_ledger(source: dict, before: dict, after: dict, source_bytes: bytes) -> dict:
    existing = rows(before)
    staged = rows(source)
    overlap = {collection: sorted(set(staged[collection]) & set(existing[collection]))
               for collection in COLLECTIONS}
    if any(overlap.values()):
        raise ValueError(f"staged IDs overlap existing IDs: {overlap}")
    return {
        "schema": "math-linear-m3-migration/v1",
        "source_path": SOURCE.relative_to(REPO).as_posix(),
        "source_sha256": "sha256:" + hashlib.sha256(source_bytes).hexdigest(),
        "target_path": TARGET.relative_to(REPO).as_posix(),
        "existing_counts": {k: len(v) for k, v in existing.items()},
        "staged_counts": {k: len(v) for k, v in staged.items()},
        "merged_counts": {k: len(rows(after)[k]) for k in COLLECTIONS},
        "records": {k: {record_id: {"digest": digest(row), "references": references(row)}
                         for record_id, row in staged[k].items()}
                    for k in COLLECTIONS},
    }


def verify_ledger(package: dict, ledger: dict) -> list[str]:
    issues = []
    current = rows(package)
    for collection, records in ledger["records"].items():
        for record_id, expected in records.items():
            row = current.get(collection, {}).get(record_id)
            if row is None:
                issues.append(f"{collection}:{record_id} missing")
            elif digest(row) != expected["digest"] or references(row) != expected["references"]:
                issues.append(f"{collection}:{record_id} changed fields or references")
    for collection, count in ledger["merged_counts"].items():
        if len(package.get(collection, [])) != count:
            issues.append(f"{collection}: expected {count}, found {len(package.get(collection, []))}")
    families = current["question_families"]
    capabilities = current["capabilities"]
    representations = current["representations"]
    for record_id in ledger["records"]["questions"]:
        question = current["questions"][record_id]
        if question.get("family_ref") not in families:
            issues.append(f"{record_id}: family_ref unresolved")
        if question.get("primary_capability_ref") not in capabilities:
            issues.append(f"{record_id}: primary_capability_ref unresolved")
        for ref in (question.get("representation_roles") or {}).values():
            if isinstance(ref, str) and ref not in representations:
                issues.append(f"{record_id}: representation role {ref} unresolved")
    return issues


def migrate() -> dict:
    if not SOURCE.is_file():
        raise FileNotFoundError("staging source already retired; use the default ledger check")
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    before = json.loads(TARGET.read_text(encoding="utf-8"))
    items = []
    for node in NODES:
        selected = library_board._node_records(source, node)
        items.append({"node": node,
                      "verification": f"Mathematics/research/verification/{node}.verification.json",
                      "package": {k: [row for collection, row in selected if collection == k]
                                  for k in promote_verified.COLLECTIONS}})
    after = promote_verified.merge(before, source, "Mathematics", "MAT-09-LINEAR-EQUATIONS", items,
                                    "2026-09-28")
    for collection in promote_verified.COLLECTIONS:
        for row in after.get(collection, []):
            (row.get("extensions") or {}).pop("grade9v3:promotion", None)
    ledger = make_ledger(source, before, after, source_bytes)
    issues = verify_ledger(after, ledger)
    if issues:
        raise ValueError("M3 would lose data: " + "; ".join(issues))
    TARGET.write_text(json.dumps(after, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    SOURCE.unlink()
    return ledger


def amend(record_ids: list[str], reason: str) -> list[str]:
    """Move the ledger to a deliberate change made to records of the fold after it: the row's digest and references are taken from the package as it is now, and the
    digest the row had is kept in `amendments` with the reason. The ledger of the fold itself cannot be written again (the staging file is retired), so this is the
    one way it changes. Returns the records whose row changed."""
    if len(reason.strip()) < 20:
        raise ValueError("an amendment gives its reason (at least 20 characters)")
    current = rows(json.loads(TARGET.read_text(encoding="utf-8")))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    changed = []
    for record_id in record_ids:
        collection = next((c for c, records in ledger["records"].items() if record_id in records), None)
        if collection is None:
            raise ValueError(f"{record_id} is not a record of this migration")
        row = current[collection].get(record_id)
        if row is None:
            raise ValueError(f"{collection}:{record_id} is not in the package")
        now = {"digest": digest(row), "references": references(row)}
        was = ledger["records"][collection][record_id]
        if now != was:
            ledger.setdefault("amendments", []).append({"collection": collection, "record": record_id, "was_digest": was["digest"], "reason": reason.strip()})
            ledger["records"][collection][record_id] = now
            changed.append(record_id)
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--amend", nargs="+", metavar="RECORD", help="move the ledger to a deliberate change made to these records since the fold (needs --reason)")
    parser.add_argument("--reason", default="")
    args = parser.parse_args(argv)
    if args.amend:
        try:
            changed = amend(args.amend, args.reason)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 1
        print("amended: " + (", ".join(changed) or "nothing changed"))
    ledger = migrate() if args.write else json.loads(LEDGER.read_text(encoding="utf-8"))
    issues = verify_ledger(json.loads(TARGET.read_text(encoding="utf-8")), ledger)
    if issues:
        print("\n".join(issues))
        return 1
    print("M3 preserved " + ", ".join(f"{k}={v}" for k, v in ledger["staged_counts"].items() if v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
