#!/usr/bin/env python3
"""What a product covers of what the library holds: the denominator the blueprint judges a product against.

A manifest lists the questions a product shows. That list is a choice, and a choice that leaves no record turns into a ceiling:
the product shows what was listed, nobody can say what was left out, and the hard question that was never listed is never missed.
The blueprint's coverage rule (Shared/web/interactive-page-blueprints.v1.json, component_policy.coverage) asks three things of every
product:

1. every record the library holds for the product's package (what `product_manifest.derive` would select) is selected, or omitted
   by the manifest with a reason (`coverage.omitted`: {record id: why});
2. the hardest of those records, by the toughest-concept rule, is selected;
3. the source documents whose questions the library does not hold as records yet are declared (`coverage.sources`), so that the
   product can say "selected 15 of 15 in the library; 59 + 48 + 70 + 19 more in sources not yet ingested" and not only "15".

The figures of `coverage.sources` are the author's claim, counted and said, never rendered. Held to the floor (official products) a
shortfall is an advisory; held to the reference (new authoring) it is a gap, `AUTHOR_COVERAGE`.

    python3 Shared/tools/product_coverage.py products/physics/SLUG.manifest.json [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import product_manifest, toughest_concept  # noqa: E402

CORES = ("core2", "core2a", "core2b")
ROLE_OF = {"core2": "CORE2", "core2a": "CORE2A", "core2b": "CORE2B"}
SOURCE_STATUS = ("NOT_INGESTED", "PARTLY_INGESTED", "INGESTED", "EXCLUDED")
MIN_REASON = 10      # a reason is a sentence, not a word


def policy() -> dict:
    from Shared.tools import web_blueprint_contract  # noqa: PLC0415  (the registry owns the rule)
    return web_blueprint_contract.load_registry()["component_policy"]["coverage"]


def _invalid(detail: str) -> product_manifest.ProductSelectionError:
    return product_manifest.ProductSelectionError(f"PRODUCT_COVERAGE_INVALID: {detail}")


def validate(manifest: dict, held: dict[str, list[str]]) -> None:
    """A malformed coverage block is an integrity error, like a malformed selection: it would say something untrue about the product.

    `held` is what the library holds, by Core (product_manifest.derivable)."""
    block = manifest.get("coverage")
    if block is None:
        return
    if not isinstance(block, dict) or set(block) - {"omitted", "sources"}:
        raise _invalid("coverage may hold only 'omitted' and 'sources'")
    selection = manifest.get("selection") or {}
    omitted = block.get("omitted", {})
    if not isinstance(omitted, dict):
        raise _invalid("coverage.omitted must map a record id to the reason it is left out")
    for record_id, reason in omitted.items():
        if not isinstance(reason, str) or len(reason.strip()) < MIN_REASON:
            raise _invalid(f"coverage.omitted.{record_id}: the reason is a sentence of at least {MIN_REASON} characters, not {reason!r}")
        cores = [key for key in CORES if record_id in selection.get(key, [])]
        if cores:
            raise _invalid(f"coverage.omitted.{record_id} is also selected in {cores[0]}: a record is selected or omitted, not both")
        if not any(record_id in held[key] for key in CORES):
            raise _invalid(f"coverage.omitted.{record_id} names no record the library holds for this package (a reason attached to nothing hides intent)")
    sources = block.get("sources", [])
    if not isinstance(sources, list):
        raise _invalid("coverage.sources must be a list")
    for i, row in enumerate(sources):
        where = f"coverage.sources[{i}]"
        if not isinstance(row, dict) or set(row) - {"source", "kind", "questions", "ingested", "status", "reason"}:
            raise _invalid(f"{where} holds source, kind, questions, ingested, status and an optional reason")
        for key in ("source", "kind"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise _invalid(f"{where}.{key} is missing")
        for key in ("questions", "ingested"):
            if not isinstance(row.get(key), int) or isinstance(row.get(key), bool) or row[key] < 0:
                raise _invalid(f"{where}.{key} is a count, not {row.get(key)!r}")
        if row["ingested"] > row["questions"]:
            raise _invalid(f"{where}: {row['ingested']} ingested of {row['questions']} questions")
        if row.get("status") not in SOURCE_STATUS:
            raise _invalid(f"{where}.status is one of {', '.join(SOURCE_STATUS)}")
        if row["status"] == "EXCLUDED" and not (isinstance(row.get("reason"), str) and len(row["reason"].strip()) >= MIN_REASON):
            raise _invalid(f"{where}: a source left out says why (reason)")


def report(manifest: dict, packages: list[dict], bank_questions: list[dict]) -> dict[str, Any]:
    """What the product covers: per Core, what is selected, what the library holds, what is omitted with a reason and what is neither."""
    held = product_manifest.derivable(packages, bank_questions)
    block = manifest.get("coverage") or {}
    omitted = dict(block.get("omitted") or {})
    selection = manifest.get("selection") or {}
    cores: dict[str, dict] = {}
    for key in CORES:
        selected = list(selection.get(key) or [])
        available = held[key]
        chosen = set(selected)
        unselected = [i for i in available if i not in chosen]
        cores[key] = {"selected": len(selected), "available": len(available), "unselected": unselected,
                      "omitted": {i: omitted[i] for i in unselected if i in omitted},
                      "unexplained": [i for i in unselected if i not in omitted],
                      "selected_beyond_library": [i for i in selected if i not in set(available)]}
    sources = [dict(row) for row in block.get("sources") or []]
    total, ingested = sum(r["questions"] for r in sources), sum(r["ingested"] for r in sources)
    return {"product": manifest.get("product_id"), "cores": cores, "toughest": _toughest(manifest, packages, bank_questions, held),
            "sources": {"declared": len(sources), "questions": total, "ingested": ingested, "not_yet_records": total - ingested, "rows": sources}}


def _toughest(manifest: dict, packages: list[dict], bank_questions: list[dict], held: dict[str, list[str]]) -> dict[str, Any]:
    """The hardest Core2 question the library holds, and whether the product selects it (the rule of toughest_concept.py)."""
    by_id = {q["id"]: q for q in bank_questions}
    microtopics = [m for pkg in packages for m in pkg.get("microtopics", [])]
    chosen = set((manifest.get("selection") or {}).get("core2") or [])
    brief = toughest_concept.derive([by_id[i] for i in held["core2"] if i in by_id], microtopics)
    if not brief:
        return {"available": None, "selected": None, "selects_it": None}
    return {"available": brief["question_ref"], "label": brief.get("label"), "selected": brief["question_ref"] in chosen,
            "selects_it": brief["question_ref"] in chosen}


def findings(rep: dict, roles: list[str]) -> list[dict]:
    """The shortfalls of a report as {record, detail, core}, one per Core that has some and one for the hardest question.

    Only the Cores the product delivers are judged. The caller decides what a finding is: an advisory at the floor, a gap at the reference."""
    out: list[dict] = []
    product = rep["product"]
    for key in CORES:
        row = rep["cores"][key]
        if ROLE_OF[key] not in roles or not row["unexplained"]:
            continue
        shown = ", ".join(row["unexplained"][:6]) + (f" and {len(row['unexplained']) - 6} more" if len(row["unexplained"]) > 6 else "")
        out.append({"record": f"{product}:{key}", "core": ROLE_OF[key],
                    "detail": f"{key}: the library holds {row['available']} question(s) for this package and the product selects {row['selected']}; "
                              f"{len(row['unexplained'])} are neither selected nor omitted with a reason ({shown}): select them, or say why "
                              f"not in the manifest's coverage.omitted"})
    top = rep["toughest"]
    if "CORE2" in roles and top["available"] and top["selects_it"] is False:
        out.append({"record": f"{product}:toughest", "core": "CORE2",
                    "detail": f"the hardest question the library holds for this package, {top['label'] or top['available']}, is not selected: "
                              f"a product that leaves it out cannot teach the move the hardest question turns on"})
    return out


def summary_lines(rep: dict) -> list[str]:
    lines = [f"coverage of {rep['product']}:"]
    for key in CORES:
        row = rep["cores"][key]
        if not row["available"] and not row["selected"]:
            continue
        lines.append(f"  {key}: selected {row['selected']} of {row['available']} in the library; omitted with a reason {len(row['omitted'])}; "
                     f"neither {len(row['unexplained'])}" + (f"; {len(row['selected_beyond_library'])} selected that the derivation would not" if row["selected_beyond_library"] else ""))
    top = rep["toughest"]
    if top["available"]:
        lines.append(f"  hardest question the library holds: {top['label'] or top['available']} ({'selected' if top['selects_it'] else 'NOT selected'})")
    src = rep["sources"]
    if src["declared"]:
        lines.append(f"  sources declared: {src['declared']}; {src['questions']} question(s), {src['ingested']} ingested, {src['not_yet_records']} not yet records (the author's figures)")
    else:
        lines.append("  sources declared: none")
    return lines


def for_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packages = [json.loads((REPO / ref).read_text(encoding="utf-8")) for ref in manifest["package_refs"]]
    bank = [q for ref in manifest.get("bank_refs", []) for q in json.loads((REPO / ref).read_text(encoding="utf-8")).get("questions", [])]
    return report(manifest, packages, bank)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    rep = for_manifest(Path(args.manifest))
    print(json.dumps(rep, indent=2, ensure_ascii=False) if args.json else "\n".join(summary_lines(rep)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
