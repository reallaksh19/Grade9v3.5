#!/usr/bin/env python3
"""Describe existing independent readback against current source inputs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import evidence_check, library_board, package_migrate  # noqa: E402


def report(subject: str, node: str, repo: Path = REPO) -> dict:
    path = library_board.verification_path(subject, node, repo)
    verification = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    records = []
    for package_path in package_migrate.package_paths(repo):
        package = json.loads(package_path.read_text(encoding="utf-8"))
        if package.get("subject") == subject:
            records.extend(row for _, row in library_board._node_records(package, node))
    current = library_board.inputs_digest(subject, node, records, repo)
    items = evidence_check.inventory_index(subject, repo)
    cards = {card["card_id"] for file in evidence_check.evidence_files(subject, repo=repo)
             for card in json.loads(file.read_text(encoding="utf-8")).get("cards", [])}
    rows = []
    for entry in verification.get("readback", []):
        ref = entry["ref"]
        kind = "inventory item" if "#" in ref else "evidence card"
        present = ref in (items if kind == "inventory item" else cards)
        rows.append({"ref": ref, "reader": entry["reader"], "state": entry["state"],
                     "correction": entry.get("correction"), "note": entry.get("note", ""),
                     "kind": kind, "source_present": present})
    return {"subject": subject, "node": node, "verification": str(path.relative_to(repo)),
            "verification_exists": path.is_file(),
            "record_count": len(records), "stored_digest": verification.get("inputs_digest"),
            "current_digest": current,
            "stale": bool(verification) and verification.get("inputs_digest") != current,
            "readback": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", required=True)
    parser.add_argument("--node", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = report(args.subject, args.node)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"{args.subject}/{args.node}: "
                  f"{'RECORDED' if result['verification_exists'] else 'NOT_RECORDED'}; "
                  f"{len(result['readback'])} readback ref(s); "
                  f"stored {result['stored_digest'] or 'NONE'}; current {result['current_digest']}; "
                  f"stale {result['stale']}")
            for row in result["readback"]:
                print(f"  {row['ref']}: {row['state']} by {row['reader']} "
                      f"({row['kind']}, source {'present' if row['source_present'] else 'missing'})")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"readback observation unavailable: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0  # advisory; the report is not permission to continue


if __name__ == "__main__":
    raise SystemExit(main())
