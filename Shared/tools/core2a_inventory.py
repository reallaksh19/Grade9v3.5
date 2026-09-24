#!/usr/bin/env python3
"""Inventory Core2A reasoning maturity and prevent new legacy debt.

The repository deliberately keeps answer.reasoning[] and difficult_move as migration
fallbacks. That compatibility must not become permission to create more fallback-only
Core2A content. This tool therefore has two jobs:

1. report every Core2A-exposed question's structured reasoning state; and
2. compare current legacy items with a deterministic baseline so a new or materially
   revised Core2A item cannot remain on the legacy representation.

The baseline is debt, not acceptance. An unchanged legacy item may remain while a topic
is migrated deliberately; once it is structured it disappears from the debt set.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402

DEFAULT_BASELINE = REPO / "docs/core2a-legacy-reasoning-baseline.json"
APPLICATION_CRUX_KINDS = {"REPRESENT", "DECIDE", "CONNECT", "TRANSFORM"}

GENERIC_CHECKS = {
    "check", "check answer", "check the answer", "check your answer",
    "check your work", "recheck", "recheck your work", "verify",
    "verify answer", "verify your answer", "redo calculation",
    "redo the calculation", "recalculate", "make sure it is correct",
    "make sure your answer is correct",
}
GENERIC_JUSTIFICATIONS = {
    "because it is valid", "because this is valid", "because it works",
    "the formula applies", "use the formula", "this is the formula",
}
CHECK_CLASSES = (
    ("SUBSTITUTE_ORIGINAL_CONDITION", re.compile(
        r"\b(substitut|plug|insert|put)\w*\b.*\b(original|condition|equation|relation)\b"
        r"|\b(back[- ]?substitut)\w*\b"
    )),
    ("REVERSE_OR_INVERSE", re.compile(
        r"\b(reverse|inverse|work backward|work backwards|undo)\b"
    )),
    ("INDEPENDENT_RECOMPUTATION", re.compile(
        r"\b(independent|another method|second method|recompute|recalculate)\b"
    )),
    ("LIMITING_OR_SPECIAL_CASE", re.compile(
        r"\b(limit|limiting|special case|extreme case|tends? to)\b"
    )),
    ("DIMENSION_OR_UNIT", re.compile(r"\b(dimension|dimensional|unit|units)\b")),
    ("SIGN_DIRECTION_BOUND", re.compile(
        r"\b(sign|direction|positive|negative|bound|bounds|range|magnitude)\b"
    )),
    ("REPRESENTATION_CROSSCHECK", re.compile(
        r"\b(graph|diagram|vector|plot|figure|representation|component)\b"
    )),
)

SEMANTIC_FIELDS = (
    "stem",
    "subparts",
    "options",
    "conditions",
    "figure_refs",
    "primary_capability_ref",
    "secondary_capability_refs",
    "family_ref",
    "hints",
    "scaffolds",
    "exposure",
)


def subjects(repo: Path = REPO) -> list[Path]:
    """Discover subject roots from their declared adapter contracts."""
    return sorted(path.parent.parent for path in repo.glob("*/adapter/CoreContracts.json"))


def package_paths(subject: Path) -> list[Path]:
    return sorted(path for path in (subject / "library").rglob("*.json")
                  if path.name != "package.schema.json")


def _core2a_roles(question: dict) -> list[str]:
    return sorted({
        str(row.get("role"))
        for row in question.get("exposure", [])
        if isinstance(row, dict) and row.get("core") == "CORE2A" and row.get("role")
    })


def _semantic_digest(question: dict) -> str:
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    payload = {field: question.get(field) for field in SEMANTIC_FIELDS}
    payload["answer"] = {
        field: answer.get(field)
        for field in (
            "kind", "summary", "reasoning", "reasoning_route", "crux_move_ref",
            "difficult_move", "check", "subpart_answers", "rubric",
        )
    }
    return digest(payload)


def _normalise_text(value: object) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").lower()))


def check_quality(answer: dict) -> dict:
    """Classify learner checks conservatively; only generic checks are machine-blocking."""
    raw = str(answer.get("check") or "").strip()
    norm = _normalise_text(raw)
    if not norm:
        return {"state": "MISSING", "class": None}
    if norm in GENERIC_CHECKS:
        return {"state": "GENERIC_NON_EXECUTABLE", "class": None}
    lowered = raw.lower()
    for name, pattern in CHECK_CLASSES:
        if pattern.search(lowered):
            return {"state": "EXECUTABLE", "class": name}
    return {"state": "EXECUTABLE_UNCLASSIFIED", "class": None}


def obvious_reasoning_findings(question: dict) -> list[dict]:
    """Catch only falsifiable route fraud; nuanced pedagogy remains human review."""
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    route = answer.get("reasoning_route")
    route = route if isinstance(route, list) else []
    qid = str(question.get("id") or "")
    found: list[dict] = []

    def fail(point: str, detail: str) -> None:
        found.append({"point": point, "where": qid, "detail": detail})

    seen_payloads: dict[tuple[str, str, str], str] = {}
    for position, move in enumerate(route):
        if not isinstance(move, dict):
            continue
        move_id = str(move.get("id") or position)
        action = _normalise_text(move.get("action"))
        why = _normalise_text(move.get("why_valid"))
        output = _normalise_text(move.get("output"))
        if action and action == why:
            fail(
                "CORE2A_REASONING_JUSTIFICATION_REPEATS_ACTION",
                f"{move_id}: why_valid merely repeats the action",
            )
        if why and why == output:
            fail(
                "CORE2A_REASONING_JUSTIFICATION_REPEATS_OUTPUT",
                f"{move_id}: why_valid merely repeats the output",
            )
        if why in GENERIC_JUSTIFICATIONS:
            fail(
                "CORE2A_REASONING_JUSTIFICATION_GENERIC",
                f"{move_id}: why_valid is generic rather than a condition/principle",
            )
        payload = (action, why, output)
        if all(payload):
            if payload in seen_payloads:
                fail(
                    "CORE2A_REASONING_MOVE_DUPLICATE",
                    f"{move_id}: duplicates reasoning move {seen_payloads[payload]}",
                )
            else:
                seen_payloads[payload] = move_id
    return found


def quality_findings(question: dict) -> list[dict]:
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    found = obvious_reasoning_findings(question)
    check = check_quality(answer)
    if check["state"] == "MISSING":
        found.append({
            "point": "CORE2A_LEARNER_CHECK_MISSING",
            "where": str(question.get("id") or ""),
            "detail": "Core2A answer has no learner-runnable check",
        })
    elif check["state"] == "GENERIC_NON_EXECUTABLE":
        found.append({
            "point": "CORE2A_LEARNER_CHECK_GENERIC",
            "where": str(question.get("id") or ""),
            "detail": (
                "learner check only tells the learner to check/recalculate; "
                "it supplies no independent action"
            ),
        })
    return found


def classify(question: dict) -> dict:
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    route = answer.get("reasoning_route")
    crux = answer.get("crux_move_ref")
    route = route if isinstance(route, list) else []
    moves = {
        move.get("id"): move
        for move in route
        if isinstance(move, dict) and isinstance(move.get("id"), str) and move.get("id")
    }
    crux_move = moves.get(crux)
    scaffolds = question.get("scaffolds")
    scaffolds = scaffolds if isinstance(scaffolds, list) else []

    if route and crux:
        if crux_move is None:
            state = "INVALID_DANGLING_CRUX"
        elif crux_move.get("kind") not in APPLICATION_CRUX_KINDS:
            state = "INVALID_CRUX_KIND"
        else:
            state = "STRUCTURED"
    elif route or crux or scaffolds:
        state = "INVALID_PARTIAL_STRUCTURED_APPLICATION"
    elif answer.get("reasoning"):
        state = "LEGACY_REASONING_MIGRATION_REQUIRED"
    else:
        state = "MISSING_APPLICATION_REASONING"

    scaffold_targets = [
        row.get("supports_move_ref")
        for row in scaffolds
        if isinstance(row, dict)
    ]
    learner_check = check_quality(answer)
    obvious = quality_findings(question)
    return {
        "state": state,
        "reasoning_moves": len(route),
        "crux_move_ref": crux,
        "crux_kind": crux_move.get("kind") if crux_move else None,
        "crux_resolves": bool(crux and crux_move),
        "difficult_move_present": answer.get("difficult_move") is not None,
        "scaffold_count": len(scaffolds),
        "scaffold_targets_resolve": all(ref in moves for ref in scaffold_targets),
        "check_present": bool(str(answer.get("check") or "").strip()),
        "check_quality_state": learner_check["state"],
        "check_class": learner_check["class"],
        "obvious_quality_findings": obvious,
        "obvious_quality_finding_count": len(obvious),
        "representation_bound_moves": sum(
            1 for move in route
            if isinstance(move, dict)
            and move.get("representation_ref")
            and move.get("visual_stage_ref")
        ),
        "figure_refs_count": len(question.get("figure_refs") or []),
        "migration_required": state != "STRUCTURED",
    }


def inventory(repo: Path = REPO) -> dict:
    rows: list[dict] = []
    parse_findings: list[dict] = []

    for subject in subjects(repo):
        for path in package_paths(subject):
            try:
                package = load(path)
            except Exception as exc:
                parse_findings.append({
                    "point": "CORE2A_INVENTORY_PACKAGE_UNREADABLE",
                    "where": str(path.relative_to(repo)),
                    "detail": str(exc),
                })
                continue
            if not isinstance(package, dict):
                continue
            questions = package.get("questions")
            if not isinstance(questions, list):
                continue
            package_id = (
                package.get("package_id")
                or package.get("manifest_id")
                or str(path.relative_to(repo))
            )
            for question in questions:
                if not isinstance(question, dict):
                    continue
                roles = _core2a_roles(question)
                if not roles:
                    continue
                maturity = classify(question)
                rows.append({
                    "subject": subject.name,
                    "package_path": str(path.relative_to(repo)),
                    "package_id": package_id,
                    "question_id": question.get("id"),
                    "question_status": question.get("status"),
                    "core2a_roles": roles,
                    "family_ref": question.get("family_ref"),
                    "semantic_digest": _semantic_digest(question),
                    **maturity,
                })

    rows.sort(key=lambda row: (
        row["subject"], row["package_path"], str(row["question_id"])
    ))
    states = Counter(row["state"] for row in rows)
    quality_count = sum(row["obvious_quality_finding_count"] for row in rows)
    check_states = Counter(row["check_quality_state"] for row in rows)
    subjects_summary = {}
    for subject in sorted({row["subject"] for row in rows}):
        subset = [row for row in rows if row["subject"] == subject]
        subjects_summary[subject] = {
            "core2a_questions": len(subset),
            "structured": sum(row["state"] == "STRUCTURED" for row in subset),
            "migration_required": sum(row["migration_required"] for row in subset),
            "obvious_quality_findings": sum(
                row["obvious_quality_finding_count"] for row in subset
            ),
        }

    return {
        "schema_version": "1.0.0",
        "summary": {
            "core2a_questions": len(rows),
            "structured": states.get("STRUCTURED", 0),
            "migration_required": sum(row["migration_required"] for row in rows),
            "states": dict(sorted(states.items())),
            "obvious_quality_findings": quality_count,
            "check_quality_states": dict(sorted(check_states.items())),
            "subjects": subjects_summary,
        },
        "rows": rows,
        "findings": parse_findings,
    }


def baseline_document(report: dict) -> dict:
    debt = [{
        "subject": row["subject"],
        "package_path": row["package_path"],
        "question_id": row["question_id"],
        "state": row["state"],
        "semantic_digest": row["semantic_digest"],
    } for row in report["rows"] if row["migration_required"]]
    return {
        "schema_version": "1.0.0",
        "policy": (
            "Existing fallback-only Core2A items may remain unchanged while they migrate; "
            "new or materially revised Core2A items must use reasoning_route + crux_move_ref."
        ),
        "generated_by": "Shared/tools/core2a_inventory.py --write-baseline",
        "items": debt,
    }


def _key(row: dict) -> tuple[str, str, str]:
    return (
        str(row.get("subject") or ""),
        str(row.get("package_path") or ""),
        str(row.get("question_id") or ""),
    )


def forward_findings(report: dict, baseline: dict) -> list[dict]:
    """Find new legacy debt plus mechanically falsifiable Core2A quality defects."""
    prior = {_key(row): row for row in baseline.get("items", []) if isinstance(row, dict)}
    found = list(report.get("findings", []))

    for row in report.get("rows", []):
        found.extend(row.get("obvious_quality_findings") or [])
        if not row.get("migration_required"):
            continue
        key = _key(row)
        before = prior.get(key)
        where = ":".join(key)
        if before is None:
            found.append({
                "point": "CORE2A_NEW_LEGACY_REASONING",
                "where": where,
                "detail": (
                    "new Core2A-exposed question is not structurally migrated; author "
                    "reasoning_route[] and crux_move_ref before adding it"
                ),
            })
        elif before.get("semantic_digest") != row.get("semantic_digest"):
            found.append({
                "point": "CORE2A_LEGACY_MATERIAL_EDIT_WITHOUT_STRUCTURED_ROUTE",
                "where": where,
                "detail": (
                    "legacy Core2A teaching semantics changed while the question still "
                    "lacks a complete structured reasoning route/crux"
                ),
            })
    return found


def audit(repo: Path = REPO, baseline_path: Path | None = None) -> dict:
    report = inventory(repo)
    baseline_path = baseline_path or (repo / DEFAULT_BASELINE.relative_to(REPO))
    if not baseline_path.is_file():
        return {
            **report,
            "forward_findings": [{
                "point": "CORE2A_LEGACY_BASELINE_MISSING",
                "where": str(baseline_path),
                "detail": "generate the deterministic legacy baseline before enforcing forward migration",
            }],
            "passed_forward": False,
        }
    baseline = load(baseline_path)
    found = forward_findings(report, baseline)
    return {**report, "forward_findings": found, "passed_forward": not found}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--enforce-forward", action="store_true")
    args = parser.parse_args()

    report = inventory(REPO)
    if args.write_baseline:
        target = args.baseline
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(baseline_document(report), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.enforce_forward:
        audited = audit(REPO, args.baseline)
        print(json.dumps(audited, indent=2, ensure_ascii=False))
        return 1 if not audited["passed_forward"] else 0

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
