#!/usr/bin/env python3
"""Research library board: each spine node's stage, derived from files, and the next work order.

Stages run RESEARCHER -> AUTHOR -> VERIFIER -> VERIFIED. A node's stage is computed from what is
actually on disk and passing — evidence cards re-found in their sources, staging records whose
required fields cite passing cards, and an independent, current verification record — never from
an agent's own report. Verifier findings send the node back to the named role as duties.

Usage:
    library_board.py --subject S                      # board (markdown)
    library_board.py --subject S --json
    library_board.py --subject S --next ROLE [--lane 1/2] [--fetch]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import operator
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.library import intake  # noqa: E402
from Shared.tools import evidence_check  # noqa: E402

ROLES = ("RESEARCHER", "AUTHOR", "VERIFIER")
CITATIONS = "grade9v3:citations"
NODE_KEY = "grade9v3:research_node"
AUTHOR_KEY = "grade9v3:authored_by"
IDEA_KEY = "grade9v3:interactive_idea"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def rules(subject: str, repo: Path = REPO) -> dict:
    return _load(evidence_check.research_dir(subject, repo) / "work-rules.json")


def staging_path(subject: str, chapter: str, repo: Path = REPO) -> Path:
    return evidence_check.research_dir(subject, repo) / "packages" / f"{chapter}.package.json"


def verification_path(subject: str, node: str, repo: Path = REPO) -> Path:
    return evidence_check.research_dir(subject, repo) / "verification" / f"{node}.verification.json"


def chapter_of(node: dict) -> str:
    return node["id"] if node["level"] == "CHAPTER" else node["parent"]


# ------------------------------------------------------------------ numeric checks

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
_NAMES = {name: getattr(math, name) for name in ("sqrt", "sin", "cos", "tan", "asin", "acos", "atan",
                                                  "atan2", "radians", "degrees", "log", "exp", "pi", "e")}


def safe_eval(expr: str) -> float:
    """Evaluate arithmetic with math functions only; anything else raises."""
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        if isinstance(node, ast.Name) and node.id in _NAMES:
            return _NAMES[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _NAMES:
            return _NAMES[node.func.id](*[ev(a) for a in node.args])
        raise ValueError(f"unsupported expression: {ast.dump(node)[:60]}")
    return float(ev(ast.parse(expr, mode="eval")))


def first_number(text: str) -> float | None:
    match = re.search(r"-?\d+(?:\.\d+)?(?:[eE]-?\d+)?", text.replace(",", ""))
    return float(match.group(0)) if match else None


# ------------------------------------------------------------------ board

def inputs_digest(subject: str, node_id: str, records: list[dict], repo: Path = REPO,
                  readback_refs: list[str] | None = None) -> str:
    cards = evidence_check.research_dir(subject, repo) / "evidence" / f"{node_id}.cards.json"
    inputs = {"cards": _load(cards) if cards.is_file() else None,
              "records": sorted(records, key=lambda r: r.get("id", ""))}
    refs = {(r.get("extensions") or {}).get("grade9v3:inventory_item") for r in records}
    verification = verification_path(subject, node_id, repo)
    if readback_refs is None:
        readback_refs = ([row.get("ref", "") for row in _load(verification).get("readback", [])]
                         if verification.is_file() else [])
    refs.update(ref for ref in readback_refs if "#" in ref)
    refs.discard(None)
    if refs:
        index = evidence_check.inventory_index(subject, repo)
        inputs["inventory_items"] = {}
        for ref in sorted(refs):
            pair = index.get(ref)
            if pair:
                inventory, item = pair
                acq_ref = item.get("locator", {}).get("acquisition_ref")
                member = next((m for m in inventory.get("members", []) if m.get("acquisition_ref") == acq_ref), None)
                inputs["inventory_items"][ref] = {"item": item, "member": member}
            else:
                inputs["inventory_items"][ref] = None
    card_refs = sorted(set(ref for ref in readback_refs if ref and "#" not in ref))
    if card_refs:
        card_index = {card["card_id"]: card
                      for path in evidence_check.evidence_files(subject, repo=repo)
                      for card in _load(path).get("cards", [])}
        inputs["readback_cards"] = {ref: card_index.get(ref) for ref in card_refs}
    body = json.dumps(inputs, sort_keys=True, ensure_ascii=False)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def _node_records(package: dict | None, node_id: str) -> list[tuple[str, dict]]:
    if not package:
        return []
    rows = []
    for collection in ("microtopics", "capabilities", "relations", "representations", "question_families", "questions"):
        for row in package.get(collection, []):
            if (row.get("extensions") or {}).get(NODE_KEY) == node_id:
                rows.append((collection, row))
    return rows


def build(subject: str, fetch: bool = False, repo: Path = REPO) -> dict:
    spine = evidence_check.spine(subject, repo)
    work = rules(subject, repo)
    evidence = evidence_check.check(subject, fetch=fetch, repo=repo)
    card_ok = evidence["card_ok"]
    cards_by_node: dict[str, list[dict]] = {}
    for path in evidence_check.evidence_files(subject, repo=repo):
        doc = _load(path)
        cards_by_node.setdefault(doc.get("node_ref"), []).extend(doc.get("cards", []))
    all_cards = {c["card_id"]: c for rows in cards_by_node.values() for c in rows}
    children: dict[str, list[str]] = {}
    for node in spine["nodes"]:
        if node["parent"]:
            children.setdefault(node["parent"], []).append(node["id"])
    packages: dict[str, dict | None] = {}
    rows = []

    for node in spine["nodes"]:
        nid, level = node["id"], node["level"]
        duties: list[dict] = []
        passing = [c for c in cards_by_node.get(nid, []) if card_ok.get(c["card_id"])]
        failing = [c["card_id"] for c in cards_by_node.get(nid, []) if not card_ok.get(c["card_id"])]
        counts: dict[str, int] = {}
        for card in passing:
            counts[card["kind"]] = counts.get(card["kind"], 0) + 1
        if work.get("syllabus_scope_may_come_from_parent") and node["parent"]:
            parent_scope = sum(1 for c in cards_by_node.get(node["parent"], [])
                               if c["kind"] == "SYLLABUS_SCOPE" and card_ok.get(c["card_id"]))
            counts["SYLLABUS_SCOPE"] = counts.get("SYLLABUS_SCOPE", 0) + parent_scope
        for kinds, need in work["harvest_minimum"][level].items():
            have = sum(counts.get(k, 0) for k in kinds.split("|"))
            if have < need:
                duties.append({"role": "RESEARCHER", "duty": f"collect {need - have} more passing {kinds} card(s)"})
        if failing:
            duties.append({"role": "RESEARCHER", "duty": "fix failing cards: " + ", ".join(failing)})
        if level == "CHAPTER" and not children.get(nid):
            duties.append({"role": "RESEARCHER", "duty": "expand this chapter into MICROTOPIC spine nodes from the textbook's section headings"})

        records: list[tuple[str, dict]] = []
        if level == "MICROTOPIC" and not duties:
            chapter = chapter_of(node)
            if chapter not in packages:
                path = staging_path(subject, chapter, repo)
                packages[chapter] = _load(path) if path.is_file() else None
            package = packages[chapter]
            records = _node_records(package, nid)
            if package is not None:
                admitted = intake.check(package)
                for f in admitted["findings"]:
                    if nid in json.dumps(f) or not records:
                        duties.append({"role": "AUTHOR", "duty": f"intake: {f['point']}: {f['detail']}"})
            duties += author_duties(records, cards_by_node.get(nid, []), all_cards, card_ok, work)

        verification = None
        if level == "MICROTOPIC" and not duties:
            duties += verifier_duties(subject, node, records, cards_by_node.get(nid, []), work, repo)
            verification = verification_path(subject, nid, repo)

        stage = duties[0]["role"] if duties else "VERIFIED"
        rows.append({"node": nid, "chapter": chapter_of(node), "level": level, "title": node["title"],
                     "track": node["track"],
                     "stage": stage, "cards_passing": len(passing), "cards_failing": len(failing),
                     "records": len(records), "duties": duties,
                     "verification": str(verification.relative_to(repo)) if verification and verification.is_file() else None,
                     "owner_frozen": node["owner_frozen"]})

    summary = {role: sum(1 for r in rows if r["stage"] == role) for role in (*ROLES, "VERIFIED")}
    return {"subject": subject, "nodes": rows, "summary": summary,
            "priority_chapters": work.get("priority_chapters", []),
            "evidence": {k: evidence[k] for k in ("cards", "cards_passing", "files")}}


def author_duties(records: list[tuple[str, dict]], node_cards: list[dict], cards: dict, card_ok: dict,
                  work: dict) -> list[dict]:
    duties = []
    marker = work["authored_marker"]
    if not any(c == "microtopics" for c, _ in records):
        return [{"role": "AUTHOR", "duty": "write the microtopic record (and its capability/relations/questions) in the staging package, tagged extensions['grade9v3:research_node']"}]
    for collection, row in records:
        cites = (row.get("extensions") or {}).get(CITATIONS) or {}
        if not (row.get("extensions") or {}).get(AUTHOR_KEY):
            duties.append({"role": "AUTHOR", "duty": f"{row['id']}: set extensions['{AUTHOR_KEY}'] to your agent id"})
        for field in work["cited_fields"].get(collection, []):
            if field not in row:
                continue
            refs = cites.get(field)
            if not refs:
                duties.append({"role": "AUTHOR", "duty": f"{row['id']}.{field}: cite evidence cards or mark {marker}"})
                continue
            factual = field in work.get("must_cite_cards", {}).get(collection, []) and not (
                collection == "questions" and row.get("origin") == "AUTHORED")
            for ref in ([refs] if isinstance(refs, str) else refs):
                if ref == marker:
                    if factual:
                        duties.append({"role": "AUTHOR", "duty": f"{row['id']}.{field}: carries facts and must cite evidence cards, not {marker}"})
                    continue
                if ref not in cards:
                    duties.append({"role": "AUTHOR", "duty": f"{row['id']}.{field}: cited card {ref} does not exist"})
                elif not card_ok.get(ref):
                    duties.append({"role": "AUTHOR", "duty": f"{row['id']}.{field}: cited card {ref} is not verified in its source"})
        if collection == "questions" and row.get("origin") != "AUTHORED":
            kinds = {cards[r]["kind"] for f in cites.values() for r in ([f] if isinstance(f, str) else f) if r in cards}
            for need in work["question_record_must_cite"]:
                if need not in kinds:
                    duties.append({"role": "AUTHOR", "duty": f"{row['id']}: a source question must cite a {need} card"})
        if collection == "microtopics" and row.get("intrinsic_badge") in work["interactive_idea"]["required_when_badge"]:
            idea = (row.get("extensions") or {}).get(IDEA_KEY) or {}
            missing = [f for f in work["interactive_idea"]["fields"] if not idea.get(f)]
            if missing:
                duties.append({"role": "AUTHOR", "duty": f"{row['id']}: HARD microtopic needs an interactive idea with {', '.join(missing)}"})
    covered = {r for _, row in records for f in ((row.get("extensions") or {}).get(CITATIONS) or {}).values()
               for r in ([f] if isinstance(f, str) else f)}
    for cid in [c["card_id"] for c in node_cards if c["kind"] == "QUESTION"]:
        if cid not in covered:
            duties.append({"role": "AUTHOR", "duty": f"question card {cid} has no question record citing it"})
    return duties


def verifier_duties(subject: str, node: dict, records: list[tuple[str, dict]], node_cards: list[dict],
                    work: dict, repo: Path) -> list[dict]:
    path = verification_path(subject, node["id"], repo)
    if not path.is_file():
        return [{"role": "VERIFIER", "duty": "independently verify this node and write its verification record"}]
    doc = _load(path)
    duties = []
    harvesters = {c.get("harvested_by") for c in node_cards}
    authors = {(row.get("extensions") or {}).get(AUTHOR_KEY) for _, row in records}
    if doc.get("verified_by") in harvesters | authors:
        duties.append({"role": "VERIFIER", "duty": "verification must be done by an agent that neither harvested nor authored this node"})
    if doc.get("inputs_digest") != inputs_digest(subject, node["id"], [row for _, row in records], repo):
        duties.append({"role": "VERIFIER", "duty": "cards or records changed since verification; verify again"})
    for q in doc.get("questions", []):
        if not q.get("agrees"):
            duties.append({"role": "AUTHOR", "duty": f"{q['card_ref']}: independent answer disagrees with the official key; re-check the record, the card or the key"})
        expr = q.get("numeric_check")
        if expr:
            try:
                value = safe_eval(expr)
            except Exception as exc:  # noqa: BLE001
                duties.append({"role": "VERIFIER", "duty": f"{q['card_ref']}: numeric_check does not evaluate ({exc})"})
                continue
            official = first_number(q.get("official_answer", ""))
            if official is not None and not math.isclose(value, official, rel_tol=work["numeric_check_relative_tolerance"]):
                duties.append({"role": "AUTHOR", "duty": f"{q['card_ref']}: numeric check gives {value:g}, official answer {official:g}"})
    question_cards = {c["card_id"] for c in node_cards if c["kind"] == "QUESTION"}
    solved = {q["card_ref"] for q in doc.get("questions", [])}
    for cid in sorted(question_cards - solved):
        duties.append({"role": "VERIFIER", "duty": f"{cid}: solve independently and compare with the official key"})
    checked = {r["record_ref"] for r in doc.get("records", [])}
    for _, row in records:
        if row["id"] not in checked:
            duties.append({"role": "VERIFIER", "duty": f"{row['id']}: check its cited fields"})
    for r in doc.get("records", []):
        if not r.get("agrees"):
            duties.append({"role": "AUTHOR", "duty": f"{r['record_ref']}: verifier disagrees; see findings"})
    for f in doc.get("findings", []):
        duties.append({"role": f["duty_for"], "duty": f"{f['target']}: {f['detail']}"})
    return duties


# ------------------------------------------------------------------ output

def markdown(board: dict) -> str:
    s = board["summary"]
    out = [f"# {board['subject']} research library board", "",
           f"Researcher: {s['RESEARCHER']} · Author: {s['AUTHOR']} · Verifier: {s['VERIFIER']} · Verified: {s['VERIFIED']}  ",
           f"Evidence cards verified in source: {board['evidence']['cards_passing']}/{board['evidence']['cards']}", "",
           "| Node | Level | Track | Stage | Cards ok/bad | Records | Next duty |", "|---|---|---|---|---|---|---|"]
    for r in board["nodes"]:
        duty = r["duties"][0]["duty"] if r["duties"] else "—"
        out.append(f"| `{r['node']}` {r['title']} | {r['level']} | {r['track']} | {r['stage']} | "
                   f"{r['cards_passing']}/{r['cards_failing']} | {r['records']} | {duty} |")
    return "\n".join(out) + "\n"


def next_order(board: dict, role: str, lane: str | None, subject: str) -> str | None:
    priority = board.get("priority_chapters", [])

    def rank(row: dict) -> int:
        chapter = row["chapter"]
        return priority.index(chapter) if chapter in priority else len(priority)

    rows = sorted((r for r in board["nodes"] if r["stage"] == role), key=rank)
    if lane:
        k, n = (int(x) for x in lane.split("/"))
        rows = [r for i, r in enumerate(rows) if i % n == k - 1]
    if not rows:
        return None
    r = rows[0]
    duties = "\n".join(f"- {d['duty']}" for d in r["duties"] if d["role"] == role)
    guide = ("docs/method/roles/SOURCE-READER.md" if role in {"RESEARCHER", "VERIFIER", "SCANNER"}
             else "docs/method/roles/UNIT-AUTHOR.md")
    return (f"SOURCE/UNIT OBSERVATION — {role} — {r['node']} ({r['title']})\n"
            f"Read {guide} and docs/method/PROTOCOL.md. This is an advisory view of existing records.\n\n"
            f"Earlier board duties (not delivery prerequisites):\n{duties}\n\n"
            f"For an updated observation run evidence_check.py and library_board.py for {subject}; "
            "decide what to research or revise from the source and learner task.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", required=True)
    parser.add_argument("--next", choices=ROLES)
    parser.add_argument("--lane", help="k/n: take every n-th node starting at k (parallel agents of one role)")
    parser.add_argument("--fetch", action="store_true", help="download missing source snapshots")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--digest", metavar="NODE", help="print the inputs_digest a verification record must carry")
    parser.add_argument("--readback-ref", action="append", default=[],
                        help="item or card ref included in a new readback (repeat with --digest)")
    parser.add_argument("--products", action="store_true",
                        help="product stage: gate verdict and gaps per product (products/status.v1.json)")
    parser.add_argument("--budget", action="store_true", help="agent spend per unit against the cost ceiling")
    parser.add_argument("--depth", action="store_true",
                        help="depth duties: every gap between the subject's library packages and the learner quality contract")
    args = parser.parse_args(argv)
    if args.products:
        status = REPO / "products" / "status.v1.json"
        rows = [r for r in (json.loads(status.read_text(encoding="utf-8")) if status.is_file() else [])
                if r["subject"] == args.subject]
        print("| Product | Verdict | Gaps | Blocking findings | Live |\n|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['product']} | {r['verdict']} | {r['gaps']} | {r['blocking_findings']} | {r['published'] or '-'} |")
        print(f"{sum(1 for r in rows if r['published'])} of {len(rows)} {args.subject} products live "
              "(rebuild: python3 Shared/tools/build_products.py build)")
        return 0
    if args.budget:
        from Shared.tools import cost_ledger  # noqa: PLC0415
        rows = cost_ledger.summary(args.subject, evidence_check.spine(args.subject)["nodes"],
                                   rules(args.subject)["cost_ceiling"], cost_ledger.load(args.subject))
        for r in rows:
            print(f"{r['signal']:8s} {r['node']:36s} ${r['usd']:.2f} of ${r['ceiling_usd']:.2f}")
        print(f"${sum(r['usd'] for r in rows):.2f} recorded across {len(rows)} unit(s)")
        return 0
    if args.depth:
        from Shared.tools import package_depth  # noqa: PLC0415
        duties = package_depth.all_duties(args.subject)
        if args.json:
            print(json.dumps(duties, indent=2, ensure_ascii=False))
        else:
            print(package_depth.summary(duties))
            if args.next:
                mine = [d for d in duties if d["role"] == args.next]
                for d in mine[:20]:
                    print(f"- {d['duty']} {d['record']} ({d['package']}): {d['detail']}; contract {', '.join(d['contract_rules'])}")
                if len(mine) > 20:
                    print(f"… {len(mine) - 20} more for {args.next}")
            print(f"{len(duties)} depth duties for {args.subject}")
        return 0
    if args.digest:
        spine_nodes = {n["id"]: n for n in evidence_check.spine(args.subject)["nodes"]}
        node = spine_nodes[args.digest]
        records = {}
        for path in sorted((REPO / args.subject / "library").glob("*.v1.json")):
            for _, row in _node_records(_load(path), args.digest):
                records[row["id"]] = row
        if not records:
            path = staging_path(args.subject, chapter_of(node))
            for _, row in _node_records(_load(path) if path.is_file() else None, args.digest):
                records[row["id"]] = row
        refs = args.readback_ref or None
        print(inputs_digest(args.subject, args.digest, list(records.values()), readback_refs=refs))
        return 0
    board = build(args.subject, fetch=args.fetch)
    if args.next:
        order = next_order(board, args.next, args.lane, args.subject)
        print(order or f"No node is at the {args.next} stage right now.")
        return 0
    print(json.dumps(board, indent=2) if args.json else markdown(board))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
