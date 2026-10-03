#!/usr/bin/env python3
"""Deterministic self-audit for hints, solution routes, and arithmetic evidence.

This is local evidence only. PASS is not QRT semantic acceptance, Chromium evidence,
or release approval.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
from typing import Any

class AuditError(ValueError):
    pass

BIN = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
}
UNARY = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}
STAGE = {"REPRESENTATION": 0, "KEY_CONCEPT": 1, "CRUX": 2, "FORMAL_MODEL": 3, "CHECKPOINT": 4}

def safe_number(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in BIN:
            return BIN[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
            return UNARY[type(node.op)](visit(node.operand))
        raise AuditError(f"CALC_EXPRESSION_UNSAFE:{expr}")
    value = visit(tree)
    if not math.isfinite(value):
        raise AuditError(f"CALC_NONFINITE:{expr}")
    return value

def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def protected_literals(question: dict[str, Any]) -> list[str]:
    rows = ((question.get("extensions") or {}).get("grade9v3:calculation_audit") or [])
    values = []
    for row in rows:
        if not row.get("protected_result"):
            continue
        value = row.get("expected")
        if isinstance(value, (int, float)):
            values.append(str(int(value)) if float(value).is_integer() else str(value))
    return sorted(set(values), key=lambda s: (len(s), s), reverse=True)

def audit_question(question: dict[str, Any]) -> dict[str, Any]:
    answer = question.get("answer") or {}
    route = answer.get("reasoning_route") or []
    move_ids = [row.get("id") for row in route if isinstance(row, dict)]
    move_set = {row for row in move_ids if isinstance(row, str)}
    protected = protected_literals(question)

    hint_items = []
    stage_values = []
    for index, hint in enumerate(question.get("scaffolds") or []):
        body = " ".join(str(hint.get(key) or "") for key in ("prompt", "text"))
        stage = hint.get("learner_stage")
        stage_values.append(STAGE.get(stage, 99))
        checks = {
            "text_present": bool(str(hint.get("prompt") or "").strip() and str(hint.get("text") or "").strip()),
            "stage_known": stage in STAGE,
            "target_move_exists": hint.get("supports_move_ref") in move_set,
            "protected_result_absent": all(value not in body for value in protected),
            "answer_summary_absent": (
                str(answer.get("summary") or "").strip() not in body
                if str(answer.get("summary") or "").strip()
                else True
            ),
        }
        hint_items.append({
            "hint_ref": f"{question['id']}.scaffolds[{index}]",
            "learner_stage": stage,
            "verdict": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
            "evidence": [
                f"question:{question['id']}",
                f"supports_move_ref:{hint.get('supports_move_ref')}",
            ],
        })
    stage_order_valid = all(left <= right for left, right in zip(stage_values, stage_values[1:]))

    calculation_items = []
    for row in ((question.get("extensions") or {}).get("grade9v3:calculation_audit") or []):
        observed = safe_number(str(row.get("expression") or ""))
        expected = float(row["expected"])
        ok = (
            math.isclose(observed, expected, rel_tol=1e-9, abs_tol=1e-9)
            and row.get("move_ref") in move_set
        )
        calculation_items.append({
            "calculation_ref": row["id"],
            "move_ref": row["move_ref"],
            "expression": row["expression"],
            "expected": row["expected"],
            "observed": observed,
            "unit": row["unit"],
            "protected_result": bool(row.get("protected_result")),
            "verdict": "PASS" if ok else "FAIL",
            "evidence": [
                f"extensions.grade9v3:calculation_audit:{row['id']}",
                f"answer.reasoning_route:{row['move_ref']}",
            ],
        })

    calc_by_move: dict[str, list[str]] = {}
    for row in calculation_items:
        calc_by_move.setdefault(row["move_ref"], []).append(row["calculation_ref"])

    solution_moves = []
    for move in route:
        complete = all(str(move.get(key) or "").strip() for key in ("id", "kind", "action", "why_valid", "output"))
        solution_moves.append({
            "move_ref": move.get("id"),
            "kind": move.get("kind"),
            "verdict": "PASS" if complete else "FAIL",
            "checks": {"structured_explanation_complete": complete},
            "calculation_evidence": calc_by_move.get(move.get("id"), []),
            "evidence": [f"answer.reasoning_route:{move.get('id')}"],
        })

    solution_checks = {
        "reasoning_route_present": bool(route),
        "move_ids_unique": len(move_ids) == len(set(move_ids)),
        "crux_ref_resolves": answer.get("crux_move_ref") in move_set,
        "answer_summary_present": bool(str(answer.get("summary") or "").strip()),
        "independent_check_present": bool(str(answer.get("check") or "").strip()),
        "verification_status_present": bool(str(answer.get("verification_status") or "").strip()),
    }

    failures = (
        sum(row["verdict"] == "FAIL" for row in hint_items + calculation_items + solution_moves)
        + (0 if stage_order_valid else 1)
        + sum(not value for value in solution_checks.values())
    )
    return {
        "question_ref": question["id"],
        "question_digest": digest(question),
        "hint_audit": {
            "verdict": "PASS" if all(row["verdict"] == "PASS" for row in hint_items) and stage_order_valid else "FAIL",
            "stage_order_valid": stage_order_valid,
            "items": hint_items,
        },
        "solution_audit": {
            "verdict": "PASS" if all(solution_checks.values()) and all(row["verdict"] == "PASS" for row in solution_moves) else "FAIL",
            "checks": solution_checks,
            "moves": solution_moves,
        },
        "calculation_audit": {
            "verdict": "PASS" if calculation_items and all(row["verdict"] == "PASS" for row in calculation_items) else "FAIL",
            "items": calculation_items,
        },
        "failure_count": failures,
    }

def audit_bank(bank: dict[str, Any]) -> dict[str, Any]:
    items = [audit_question(question) for question in (bank.get("questions") or [])]
    return {
        "schema": "question-content-audit/v1",
        "bank_ref": bank.get("bank_id"),
        "bank_digest": digest(bank),
        "scope": ["HINT_SAFETY", "SOLUTION_STRUCTURE", "INDEPENDENT_CALCULATION"],
        "items": items,
        "status": "PASS" if items and all(item["failure_count"] == 0 for item in items) else "FAIL",
        "note": "PASS means only these deterministic self-checks passed; it is not QRT semantic review, Chromium evidence, or release approval.",
    }

def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    report = audit_bank(json.loads(args.bank.read_text(encoding="utf-8")))
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
