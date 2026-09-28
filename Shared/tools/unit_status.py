#!/usr/bin/env python3
"""Describe a unit from its package, source, render, review and Owner decision artifacts.

Every state is an observation, never permission to author, build or publish.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import evidence_check, library_board, render_core  # noqa: E402

STATES = ("PLANNED", "SOURCED", "DESIGNED", "PROTOTYPED", "BUILT", "REVIEWED", "ACCEPTED", "PUBLISHED")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def front_matter(path: Path) -> dict:
    """Read the small JSON-compatible YAML subset used by UNIT.md, without a runtime YAML dependency."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    header = text.split("\n---\n", 1)[0].removeprefix("---\n")
    data, parent = {}, None
    for line in header.splitlines():
        if not line.strip() or ":" not in line:
            continue
        indent = len(line) - len(line.lstrip())
        name, raw = line.strip().split(":", 1)
        raw = raw.strip()
        if not indent and not raw:
            data[name] = {}
            parent = name
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        if indent and parent:
            data[parent][name] = value
        elif not indent:
            data[name] = value
            parent = None
    return data


def _cited_refs(record: dict) -> set[str]:
    cited = (record.get("extensions") or {}).get("grade9v3:citations") or {}
    refs = set()
    for value in cited.values():
        if isinstance(value, str):
            refs.add(value)
        elif isinstance(value, list):
            refs.update(ref for ref in value if isinstance(ref, str))
    return {ref for ref in refs if isinstance(ref, str)
            and ref not in {"AUTHOR_CREATED", "AUTHORED_PEDAGOGICAL"}}


def fact_status(package: dict, subject: str, repo: Path = REPO) -> dict:
    """Independent current card/record verification counts for Owner-facing display."""
    records = [row for collection in ("capabilities", "microtopics", "relations", "representations",
                                       "question_families", "questions") for row in package.get(collection, [])]
    cited_records = [row for row in records if _cited_refs(row)]
    cards = {card["card_id"]: card
             for path in evidence_check.evidence_files(subject, repo=repo)
             for card in _json(path).get("cards", [])}
    verifications = []
    folder = evidence_check.research_dir(subject, repo) / "verification"
    for path in sorted(folder.glob("*.verification.json")):
        doc = _json(path)
        node = doc.get("node_ref", "")
        node_records = [r for r in records if (r.get("extensions") or {}).get(library_board.NODE_KEY) == node]
        current = doc.get("inputs_digest") == library_board.inputs_digest(subject, node, node_records, repo)
        verifications.append((doc, current))
    verified, unverified = [], []
    for record in cited_records:
        refs = _cited_refs(record)
        author = (record.get("extensions") or {}).get("grade9v3:authored_by")
        cards_registered = all(ref in cards and evidence_check.acquisition_path(
            subject, cards[ref].get("acquisition_ref", ""), repo).is_file() for ref in refs)
        independently_read = False
        if author and cards_registered:
            for doc, current in verifications:
                if not current or doc.get("verified_by") == author:
                    continue
                checked = any(row.get("record_ref") == record["id"] and row.get("agrees")
                              for row in doc.get("records", []))
                readbacks = {row.get("ref") for row in doc.get("readback", [])
                             if row.get("state") in {"AGREED", "CORRECTED"} and row.get("reader") != author}
                if checked and (not doc.get("readback") or refs <= readbacks):
                    independently_read = True
                    break
        (verified if independently_read else unverified).append(record["id"])
    return {"cited": len(cited_records), "verified": sorted(verified), "unverified": sorted(unverified)}


def _designed(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    sections = re.findall(r"(?m)^##\s+([1-8])\b[^\n]*\n(.*?)(?=^##\s+|\Z)", text, flags=re.S | re.M)
    return {n for n, body in sections if body.strip() and not body.strip().startswith("<")} == set("12345678")


def status(subject: str, slug: str, repo: Path = REPO, render: tuple[list[dict], str] | None = None) -> dict:
    unit = repo / subject / "units" / slug
    unit_file = unit / "UNIT.md"
    front = front_matter(unit_file) if unit_file.is_file() else {}
    package_ref = front.get("package") or f"{subject}/library/{slug}.v1.json"
    package_path = repo / package_ref
    package = _json(package_path) if package_path.is_file() else None
    manifest_path = repo / "products" / subject.lower() / f"{slug}.manifest.json"
    manifest = _json(manifest_path) if manifest_path.is_file() else None
    gaps, digest = (None, None)
    if render is not None:
        gaps, digest = render
    elif manifest is not None and repo == REPO:
        _, gaps, digest = render_core.build(manifest_path)
    facts = fact_status(package, subject, repo) if package else {"cited": 0, "verified": [], "unverified": []}
    review_path = repo / "products" / "verification" / f"{slug}.review.json"
    acceptance_path = repo / "products" / "acceptance" / f"{slug}.json"
    review_digest = _json(review_path).get("render_digest") if review_path.is_file() else None
    acceptance = _json(acceptance_path) if acceptance_path.is_file() else {}
    accepted_digest = (acceptance.get("render_digest") if acceptance.get("schema") == "product-acceptance/v1"
                       and acceptance.get("accepted_by") == "owner" and acceptance.get("product") == slug else None)
    selected = set((manifest or {}).get("selection", {}).get("microtopics", []))
    listed = set(front.get("microtopics") or [])
    states = {
        "PLANNED": unit_file.is_file(),
        "SOURCED": facts["cited"] > 0 and not facts["unverified"],
        "DESIGNED": _designed(unit / "DESIGN-NOTE.md"),
        "PROTOTYPED": (unit / "SELF-CRITIQUE.md").is_file() and digest is not None,
        "BUILT": digest is not None and gaps is not None and not gaps and bool(listed) and listed <= selected,
        "REVIEWED": digest is not None and review_digest == digest,
        "ACCEPTED": digest is not None and accepted_digest == digest,
        "PUBLISHED": False,
    }
    public = repo / "public" / "products" / subject.lower() / slug
    if states["ACCEPTED"] and public.is_dir():
        try:
            from Shared.tools.accept_product import verify_render  # noqa: PLC0415
            states["PUBLISHED"] = verify_render(public)["digest"] == digest
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            pass
    formats = {}
    chosen = {}
    inventory_index = evidence_check.inventory_index(subject, repo)
    linked_refs = {(q.get("extensions") or {}).get("grade9v3:inventory_item")
                   for q in (package or {}).get("questions", [])}
    declared_inventories = set(front.get("inventories") or []) | {
        ref.split("#", 1)[0] for ref in linked_refs if isinstance(ref, str) and "#" in ref}
    for ref, (_inventory, item) in inventory_index.items():
        if ref.split("#", 1)[0] in declared_inventories:
            formats[item["format"]] = formats.get(item["format"], 0) + 1
    for question in (package or {}).get("questions", []):
        ref = (question.get("extensions") or {}).get("grade9v3:inventory_item")
        if ref in inventory_index:
            fmt = inventory_index[ref][1]["format"]
            chosen[fmt] = chosen.get(fmt, 0) + 1
    return {"unit": slug, "subject": subject, "package": package_ref, "render_digest": digest,
            "gaps": len(gaps) if gaps is not None else None, "facts": facts,
            "states": states, "current_state": next((state for state in reversed(STATES) if states[state]), "UNPLANNED"),
            "earlier_review_digest": review_digest if review_digest and review_digest != digest else None,
            "earlier_acceptance_digest": accepted_digest if accepted_digest and accepted_digest != digest else None,
            "spine_nodes": front.get("spine_nodes") or [],
            "inventory_formats": formats, "selected_formats": chosen}


def subject_status(subject: str, repo: Path = REPO) -> dict:
    units = [status(subject, path.parent.name, repo) for path in sorted((repo / subject / "units").glob("*/UNIT.md"))]
    spine_path = evidence_check.research_dir(subject, repo) / "syllabus-spine.json"
    spine = {row["id"] for row in _json(spine_path).get("nodes", [])} if spine_path.is_file() else set()
    declared = {node for unit in units for node in unit["spine_nodes"]}
    return {"subject": subject, "units": units, "spine_covered": sorted(spine & declared),
            "spine_uncovered": sorted(spine - declared), "spine_unknown": sorted(declared - spine)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", required=True)
    parser.add_argument("--unit")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = status(args.subject, args.unit) if args.unit else subject_status(args.subject)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.unit:
        print(f"{args.subject}/{args.unit}: {report['current_state']} @ {report['render_digest'] or 'NO_RENDER'}")
        print(" · ".join(f"{state}={'yes' if present else 'no'}" for state, present in report["states"].items()))
        print(f"facts verified {len(report['facts']['verified'])}/{report['facts']['cited']}; gaps {report['gaps']}")
        print(f"inventory formats {report['inventory_formats']}; selected {report['selected_formats']}")
    else:
        for unit in report["units"]:
            print(f"{unit['unit']}: {unit['current_state']} · facts {len(unit['facts']['verified'])}/{unit['facts']['cited']} · gaps {unit['gaps']}")
        print(f"spine coverage {len(report['spine_covered'])}/{len(report['spine_covered'])+len(report['spine_uncovered'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
