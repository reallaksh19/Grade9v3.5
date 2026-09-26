#!/usr/bin/env python3
"""Agent spend per unit, against the owner's cost ceiling (rebuild plan, Phase 5).

The ceiling is a review signal, never a stop. At 100% of a unit's ceiling the board shows
REVIEW, and at 200% ESCALATE (the owner looks). Work continues either way; there is no hold state.

Ledger: <Subject>/research/cost-ledger.json, one row per agent session or run:
    {"date", "session", "role", "scope": "<node or chapter id>", "usd", "note"}
A chapter-level row is spread evenly over the chapter's MICROTOPIC nodes.
Ceiling: work-rules.json `cost_ceiling`, i.e. {"per_unit_usd": 15, "by_role_usd": {...}}.

Usage:
    cost_ledger.py add --subject Physics --session S --role AUTHOR --scope NODE --usd 3.2 [--note ...]
    cost_ledger.py summary --subject Physics
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def ledger_path(subject: str, repo: Path = REPO) -> Path:
    return repo / subject / "research" / "cost-ledger.json"


def load(subject: str, repo: Path = REPO) -> dict:
    path = ledger_path(subject, repo)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"schema": "cost-ledger/v1", "rows": []}


def summary(subject: str, spine_nodes: list[dict], ceiling: dict, ledger: dict) -> list[dict]:
    micro = [n for n in spine_nodes if n["level"] == "MICROTOPIC"]
    by_chapter: dict[str, list[str]] = {}
    for n in micro:
        by_chapter.setdefault(n["parent"], []).append(n["id"])
    spend = {n["id"]: 0.0 for n in micro}
    for row in ledger["rows"]:
        if row["scope"] in spend:
            spend[row["scope"]] += row["usd"]
        elif row["scope"] in by_chapter:
            share = row["usd"] / len(by_chapter[row["scope"]])
            for nid in by_chapter[row["scope"]]:
                spend[nid] += share
    limit = ceiling["per_unit_usd"]
    out = []
    for nid, usd in spend.items():
        if usd <= 0:
            continue
        ratio = usd / limit
        out.append({"node": nid, "usd": round(usd, 2), "ceiling_usd": limit, "ratio": round(ratio, 2),
                    "signal": "ESCALATE" if ratio >= 2 else "REVIEW" if ratio >= 1 else "OK"})
    return sorted(out, key=lambda r: -r["usd"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    for f in ("--subject", "--session", "--role", "--scope"):
        a.add_argument(f, required=True)
    a.add_argument("--usd", type=float, required=True)
    a.add_argument("--note", default="")
    s = sub.add_parser("summary")
    s.add_argument("--subject", required=True)
    args = p.parse_args(argv)
    if args.cmd == "add":
        ledger = load(args.subject)
        ledger["rows"].append({"date": datetime.date.today().isoformat(), "session": args.session, "role": args.role,
                               "scope": args.scope, "usd": args.usd, "note": args.note})
        ledger_path(args.subject).write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
        print(f"recorded ${args.usd:.2f} for {args.scope}")
        return 0
    from Shared.tools import evidence_check  # noqa: PLC0415
    rules = json.loads((REPO / args.subject / "research" / "work-rules.json").read_text(encoding="utf-8"))
    rows = summary(args.subject, evidence_check.spine(args.subject)["nodes"], rules["cost_ceiling"], load(args.subject))
    total = sum(r["usd"] for r in rows)
    for r in rows:
        print(f"{r['signal']:8s} {r['node']:36s} ${r['usd']:.2f} of ${r['ceiling_usd']:.2f}")
    print(f"total ${total:.2f} across {len(rows)} unit(s); ceiling ${rules['cost_ceiling']['per_unit_usd']:.2f} per unit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
