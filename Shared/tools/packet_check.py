#!/usr/bin/env python3
"""Local first-stage review checks. Never builds, publishes, or constrains research.

Compare an explicit uploaded source inventory with canonical selection and delivered HTML.
Write the review outside the learner packet; a machine PASS is not pedagogical approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from Shared.tools import product_manifest, quality_observe, render_core


def question_digest(question: dict) -> str:
    """Bind reviewed visual exceptions to academic bytes, excluding the review itself."""
    value = json.loads(json.dumps(question))
    value.get("extensions", {}).pop("grade9v3:visual_review", None)
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                                 ensure_ascii=False).encode()).hexdigest()


def inspect(ctx, pages: dict[str, str], inventory: dict | None = None) -> dict:
    checks = []

    def add(name, passed, detail, record=None):
        checks.append(dict(check=name, status="NOT_RUN" if passed is None else "PASS" if passed else "FAIL",
                           record=record, detail=detail))

    roles = product_manifest.selected_output_roles(ctx.manifest)
    expected = {}; delivered = {}; nodes = {}
    for role in roles:
        selected = render_core.units_for(ctx, role)
        expected[role] = [q["id"] for q in selected]
        name = render_core.ROLE_FILE[role]
        # SINGLE_FILE sections carry roles; never infer a role from an arbitrary article.
        doc = quality_observe.parse(pages.get(name, pages.get("product.html", "")))
        if name not in pages:
            sections = [n for n in doc.find_all(attr="data-g9-role-section")
                        if n.attrs["data-g9-role-section"] == role]
            doc = sections[0] if len(sections) == 1 else quality_observe.parse("")
        articles = list(doc.find_all(tag="article", attr="data-g9-unit"))
        delivered[role] = [a.attrs["data-g9-unit"] for a in articles]
        nodes[role] = {a.attrs["data-g9-unit"]: a for a in articles}
        add("HTML_ID_TALLY", Counter(expected[role]) == Counter(delivered[role]),
            {"role": role, "selected": len(expected[role]), "rendered": len(delivered[role]),
             "missing": sorted((Counter(expected[role]) - Counter(delivered[role])).elements()),
             "extra": sorted((Counter(delivered[role]) - Counter(expected[role])).elements())})
        add("HTML_UNIQUE_IDS", len(delivered[role]) == len(set(delivered[role])), role)

    if "CORE2" in roles:
        if inventory is None:
            add("UPLOAD_TALLY", None, "No uploaded source inventory supplied; bank size is not the upload denominator.")
        else:
            from jsonschema import Draft202012Validator
            errors = [e.message for e in Draft202012Validator(render_core.load_json(
                REPO / "Shared/library/source-inventory.schema.json")).iter_errors(inventory)]
            add("INVENTORY_STRUCTURE", not errors, errors)
            items = inventory.get("items", [])
            ids = [i.get("item_id") for i in items]
            selected = ctx.selection_rows["core2"]
            # Inventory question_card is an exact canonical ref. Explicit inventory_item
            # links support sources whose evidence card and canonical ID differ.
            mapped = []
            for item in items:
                matches = [q["id"] for q in selected if q["id"] == item.get("question_card") or
                           (q.get("extensions") or {}).get("grade9v3:inventory_item") == item.get("item_id")]
                mapped.append({"item": item.get("item_id"), "questions": matches})
            mapped_ids = [q for m in mapped for q in m["questions"]]
            count_ok = inventory.get("counts", {}).get("items") == len(items)
            for state in ("PRESENT", "ABSENT", "AMBIGUOUS"):
                add("INVENTORY_KEY_" + state,
                    inventory.get("counts", {}).get("key_" + state.lower()) ==
                    sum(i.get("key", {}).get("state") == state for i in items), state)
            add("UPLOAD_TALLY", count_ok and len(ids) == len(set(ids)) and
                all(len(m["questions"]) == 1 for m in mapped) and
                Counter(mapped_ids) == Counter(delivered["CORE2"]),
                {"scope": inventory.get("declared_scope"), "uploaded": len(items),
                 "selected": len(selected), "rendered": len(delivered["CORE2"]), "mapping": mapped})

        for q in ctx.selection_rows["core2"]:
            qid = q["id"]; ext = q.get("extensions") or {}
            band = (q.get("difficulty") or (ext.get("grade9v3:analysis") or {}).get("difficulty") or {}).get("band")
            add("QUESTION_DIFFICULTY", band in {"D1", "D2", "D3", "D4"}, band, qid)
            node = nodes["CORE2"].get(qid, quality_observe.parse(""))
            add("OPTIONS_TALLY", len(list(node.find_all(cls="g9-answer-option"))) ==
                (len(q.get("options") or []) or (2 if render_core.response_for(q)["type"] == "true_false" else 0)),
                {"expected": len(q.get("options") or []), "rendered": len(list(node.find_all(cls="g9-answer-option")))}, qid)
            add("SOURCE_FIGURE_TALLY", len(q.get("figure_refs") or []) ==
                sum(n.attrs.get("data-g9-stage") == "PRE_ATTEMPT" for n in node.find_all(attr="data-g9-figure")),
                {"source_references": q.get("figure_refs") or []}, qid)
            add("LEARNER_METADATA", bool(node.first(attr="data-g9-meta-strip")) and
                not node.first(attr="data-g9-meta-incomplete"), "Concept/topic, question difficulty and source labels", qid)
            blocks = [n for n in node.find_all(attr="data-g9-block")
                      if n.attrs["data-g9-block"] == "authored_hints"]
            rungs = [n.content() for b in blocks for n in b.find_all(attr="data-g9-rung")]
            moves = list(node.find_all(attr="data-g9-reasoning-move"))
            if band in {"D2", "D3", "D4"}:
                add("AUTHORED_HINT_LADDER", len(rungs) >= 3 and all(rungs) and
                    len(set(rungs)) == len(rungs), {"rungs": len(rungs), "minimum": 3}, qid)
                route = (q.get("answer") or {}).get("reasoning_route") or []
                fields = ("id", "kind", "action", "why_valid", "inputs", "output")
                valid = bool(route) and all(all(m.get(f) for f in fields) for m in route)
                add("REASONING_ROUTE", valid and Counter(m.get("id") for m in route) ==
                    Counter(n.attrs["data-g9-reasoning-move"] for n in moves) and
                    len({m.get("id") for m in route}) == len(route), {"moves": len(moves)}, qid)
            if band in {"D3", "D4"}:
                svgs = list(node.find_all(tag="svg"))
                review = ext.get("grade9v3:visual_review") or {}
                exception = (review.get("applicable") is False and bool(str(review.get("reason", "")).strip())
                             and bool(str(review.get("reviewer", "")).strip()) and
                             review.get("question_digest") == question_digest(q))
                accessible = [s for s in svgs if (s.attrs.get("aria-label") or s.attrs.get("aria-labelledby"))
                              and s.first(tag="title") and s.first(tag="desc")]
                add("HARD_VISUAL", bool(accessible) or exception,
                    {"accessible_svg_count": len(accessible), "reviewed_exception": exception,
                     "reason": review.get("reason") if exception else None}, qid)
            add("PEDAGOGICAL_REVIEW", None, "Human review: useful hints, valid reasoning, figure purpose and disclosure.", qid)
    for name in ("TABLET_LANDSCAPE", "TABLET_PORTRAIT", "TOUCH_TARGETS", "OFFLINE_MATH",
                 "COMMITMENT_AND_SEARCH", "LEARNER_PDF", "KEY_PDF"):
        add(name, None, "Requires actual browser/PDF evidence at this artifact hash; structural inspection cannot establish it.")
    return {"schema": "packet-check/v1", "product": ctx.manifest["product_id"],
            "artifact_sha256": {n: hashlib.sha256(v.encode()).hexdigest() for n, v in sorted(pages.items())},
            "inventory_sha256": hashlib.sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest() if inventory else None,
            "status": "FAIL" if any(c["status"] == "FAIL" for c in checks) else "NOT_RUN" if
                      any(c["status"] == "NOT_RUN" for c in checks) else "PASS", "checks": checks}


def report_html(report: dict) -> str:
    escape = html.escape
    rows = "".join("<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in
        (c["check"], c["record"] or "Packet", c["status"], json.dumps(c["detail"], ensure_ascii=False))) + "</tr>"
        for c in report["checks"])
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Packet review</title><style>body{font:17px system-ui;max-width:1200px;margin:auto;padding:24px}'
            'td,th{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #ccc;overflow-wrap:anywhere}'
            'table{width:100%;table-layout:fixed}</style><h1>Packet review: ' + escape(report["product"]) +
            '</h1><p>Overall: ' + report["status"] + '. Local review evidence; not publication acceptance.</p>'
            '<table><thead><tr><th>Check</th><th>Record</th><th>Status</th><th>Evidence / gap</th></tr></thead><tbody>' +
            rows + '</tbody></table></html>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--rendered", required=True, type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Review directory outside the learner packet")
    args = parser.parse_args(argv)
    if args.out.resolve() == args.rendered.resolve() or args.out.resolve().is_relative_to((REPO / "public").resolve()):
        parser.error("review output must be separate from learner HTML and public")
    receipt = render_core.load_json(args.rendered / "render-receipt.json")
    pages = {}
    for name in receipt["pages"]:
        if name not in set(render_core.ROLE_FILE.values()) | {"index.html", "product.html"}:
            parser.error("unexpected receipt page name")
        path = args.rendered / name
        if path.is_file():
            pages[name] = path.read_text(encoding="utf-8")
    report = inspect(render_core.context(args.manifest), pages,
                     render_core.load_json(args.inventory) if args.inventory else None)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "packet-check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.out / "index.html").write_text(report_html(report), encoding="utf-8")
    print(report["status"])
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
