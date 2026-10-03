#!/usr/bin/env python3
"""Validate item-level author self-audits and exact-byte Chromium receipts.

This layer is deliberately separate from independent post-render QRT review:
- author self-audit: every hint, solution move and calculation carries evidence;
- independent review: H1-H3/S1-S3/P1-P3/M1-M3 judges the rendered learner artifact.

Every named author check carries its own result and evidence. A single generic
"checked" sentence cannot satisfy several different quality claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

SELF_AUDIT_STATUSES = {"PASS", "FAIL"}
CHECK_RESULTS = {"PASS", "FAIL", "NOT_APPLICABLE"}
INTERACTIVE_KINDS = {"INTERACTIVE_HTML", "INTERACTIVE_PAGE", "EXPLORER"}
INTERACTIVE_NODE_KINDS = {"INTERACTIVE", "INTERACTIVE_HTML", "INTERACTIVE_PAGE", "EXPLORER"}
EXPLORER_BLUEPRINT_PREFIX = "BP-EXPLORER-GCDR@"
CHROMIUM_TOOL = "tools/site-audit/interactive-page-audit.mjs"
CHROMIUM_ENGINE = "playwright.chromium"

HINT_CHECKS = (
    "academic_correctness",
    "objective_alignment",
    "w_protection",
    "learner_fit",
    "non_redundancy",
)
SOLUTION_CHECKS = (
    "academic_correctness",
    "question_specificity",
    "reasoning_validity",
    "units_symbols",
    "post_attempt_scope",
)
CALCULATION_CHECKS = (
    "arithmetic_or_algebra",
    "units_dimensions",
    "input_traceability",
    "independent_check",
)


class SelfAuditError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SelfAuditError(f"{path}: expected object")
    return value


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _evidence_present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(str(item).strip() for item in value)
    return False


def _validate_audit(qid: str, kind: str, item_id: str, audit: Any, required_checks: tuple[str, ...]) -> list[str]:
    prefix = f"{qid}:{kind}:{item_id}"
    if not isinstance(audit, dict):
        return [f"SELF_AUDIT_MISSING: {prefix}"]

    problems: list[str] = []
    status = audit.get("status")
    if status not in SELF_AUDIT_STATUSES:
        problems.append(f"SELF_AUDIT_STATUS_INVALID: {prefix}:{status}")
    if not _evidence_present(audit.get("summary_evidence")):
        problems.append(f"SELF_AUDIT_SUMMARY_EVIDENCE_MISSING: {prefix}")
    if not _evidence_present(audit.get("basis_refs")):
        problems.append(f"SELF_AUDIT_BASIS_REFS_MISSING: {prefix}")

    checks = audit.get("checks")
    if not isinstance(checks, dict):
        problems.append(f"SELF_AUDIT_CHECKS_INVALID: {prefix}")
        return problems

    for check in required_checks:
        row = checks.get(check)
        if not isinstance(row, dict):
            problems.append(f"SELF_AUDIT_CHECK_MISSING_OR_INVALID: {prefix}:{check}")
            continue
        result = row.get("result")
        if result not in CHECK_RESULTS:
            problems.append(f"SELF_AUDIT_CHECK_RESULT_INVALID: {prefix}:{check}:{result}")
            continue
        if not _evidence_present(row.get("evidence")):
            problems.append(f"SELF_AUDIT_CHECK_EVIDENCE_MISSING: {prefix}:{check}")
        if result == "NOT_APPLICABLE" and not str(row.get("reason") or "").strip():
            problems.append(f"SELF_AUDIT_CHECK_NA_REASON_MISSING: {prefix}:{check}")
        if result == "FAIL":
            problems.append(f"SELF_AUDIT_CHECK_FAILED: {prefix}:{check}")

    if status == "FAIL":
        problems.append(f"SELF_AUDIT_FAILED: {prefix}")
    return problems


def validate_content_self_audits(run: dict[str, Any]) -> list[str]:
    """Require a self-audit for every authored hint, solution move and calculation."""
    problems: list[str] = []

    for question in run.get("questions") or []:
        if not isinstance(question, dict):
            continue
        qid = str(question.get("id") or "<unknown>")

        hints = question.get("hints")
        if not isinstance(hints, list):
            problems.append(f"HINTS_LIST_MISSING: {qid}")
            hints = []
        for index, hint in enumerate(hints):
            if not isinstance(hint, dict):
                problems.append(f"HINT_INVALID: {qid}:{index}")
                continue
            hid = str(hint.get("id") or f"index-{index}")
            if not str(hint.get("text") or "").strip():
                problems.append(f"HINT_TEXT_MISSING: {qid}:{hid}")
            calc_bearing = hint.get("calculation_bearing")
            if calc_bearing not in {True, False}:
                problems.append(f"HINT_CALCULATION_DECLARATION_MISSING: {qid}:{hid}")
            refs = hint.get("calculation_refs") or []
            if calc_bearing is True and not refs:
                problems.append(f"HINT_CALCULATION_REFS_MISSING: {qid}:{hid}")
            if calc_bearing is False and refs:
                problems.append(f"HINT_CALCULATION_REFS_UNEXPECTED: {qid}:{hid}")
            problems.extend(_validate_audit(qid, "HINT", hid, hint.get("self_audit"), HINT_CHECKS))

        steps = question.get("solution_steps")
        if not isinstance(steps, list) or not steps:
            problems.append(f"SOLUTION_STEPS_MISSING: {qid}")
            steps = []
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                problems.append(f"SOLUTION_STEP_INVALID: {qid}:{index}")
                continue
            sid = str(step.get("id") or f"index-{index}")
            for field in ("action", "why_valid_here", "result"):
                if not str(step.get(field) or "").strip():
                    problems.append(f"SOLUTION_STEP_FIELD_MISSING: {qid}:{sid}:{field}")
            calc_bearing = step.get("calculation_bearing")
            if calc_bearing not in {True, False}:
                problems.append(f"SOLUTION_CALCULATION_DECLARATION_MISSING: {qid}:{sid}")
            refs = step.get("calculation_refs") or []
            if calc_bearing is True and not refs:
                problems.append(f"SOLUTION_CALCULATION_REFS_MISSING: {qid}:{sid}")
            if calc_bearing is False and refs:
                problems.append(f"SOLUTION_CALCULATION_REFS_UNEXPECTED: {qid}:{sid}")
            problems.extend(_validate_audit(qid, "SOLUTION", sid, step.get("self_audit"), SOLUTION_CHECKS))

        calculations = question.get("calculations")
        if not isinstance(calculations, list):
            problems.append(f"CALCULATIONS_LIST_MISSING: {qid}")
            calculations = []
        calc_ids: set[str] = set()
        for index, calc in enumerate(calculations):
            if not isinstance(calc, dict):
                problems.append(f"CALCULATION_INVALID: {qid}:{index}")
                continue
            cid = str(calc.get("id") or f"index-{index}")
            if cid in calc_ids:
                problems.append(f"CALCULATION_ID_DUPLICATE: {qid}:{cid}")
            calc_ids.add(cid)
            for field in ("expression", "result"):
                if not str(calc.get(field) or "").strip():
                    problems.append(f"CALCULATION_FIELD_MISSING: {qid}:{cid}:{field}")
            problems.extend(_validate_audit(qid, "CALCULATION", cid, calc.get("self_audit"), CALCULATION_CHECKS))

        for item_kind, rows in (("HINT", hints), ("SOLUTION", steps)):
            for index, row in enumerate(rows):
                if not isinstance(row, dict):
                    continue
                item_id = str(row.get("id") or f"index-{index}")
                for ref in row.get("calculation_refs") or []:
                    if str(ref) not in calc_ids:
                        problems.append(f"CALCULATION_REF_UNKNOWN: {qid}:{item_kind}:{item_id}:{ref}")

    return problems


def _load_receipt_report(report_path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    return (value if isinstance(value, dict) else None), (None if isinstance(value, dict) else "report is not an object")


def _is_interactive_artifact(artifact: dict[str, Any]) -> bool:
    kind = str(artifact.get("kind") or "")
    blueprint = str(artifact.get("blueprint_ref") or "")
    return kind in INTERACTIVE_KINDS or blueprint.startswith(EXPLORER_BLUEPRINT_PREFIX)


def _validate_interactive_graph_registration(run: dict[str, Any], artifacts: dict[str, dict[str, Any]]) -> list[str]:
    """An interactive resource linked from a question graph must be a registered artifact.

    This prevents a linked explorer from evading Chromium simply by being omitted from
    rendered_artifacts. Both pre- and post-attempt interactive nodes are inventory-checked.
    """
    problems: list[str] = []
    for graph in run.get("pre_attempt_graphs") or []:
        if not isinstance(graph, dict):
            continue
        qid = str(graph.get("question_ref") or "<unknown>")
        for node in graph.get("nodes") or []:
            if not isinstance(node, dict):
                continue
            kind = str(node.get("resource_kind") or "")
            blueprint = str(node.get("blueprint_ref") or "")
            if kind not in INTERACTIVE_NODE_KINDS and not blueprint.startswith(EXPLORER_BLUEPRINT_PREFIX):
                continue
            nid = str(node.get("id") or "<unknown>")
            artifact_ref = str(node.get("artifact_ref") or "")
            if not artifact_ref:
                problems.append(f"INTERACTIVE_GRAPH_ARTIFACT_REF_MISSING: {qid}:{nid}")
            elif artifact_ref not in artifacts:
                problems.append(f"INTERACTIVE_GRAPH_ARTIFACT_UNKNOWN: {qid}:{nid}:{artifact_ref}")
    return problems


def validate_interactive_chromium(run: dict[str, Any]) -> list[str]:
    """Require an exact-byte Chromium receipt for every governed interactive artifact."""
    problems: list[str] = []
    head = str((run.get("run_identity") or {}).get("head_sha") or "")
    artifacts = {
        str(row.get("id")): row
        for row in run.get("rendered_artifacts") or []
        if isinstance(row, dict) and row.get("id")
    }
    problems.extend(_validate_interactive_graph_registration(run, artifacts))

    receipts = {
        str(row.get("artifact_ref")): row
        for row in ((run.get("validation") or {}).get("interactive_chromium_receipts") or [])
        if isinstance(row, dict) and row.get("artifact_ref")
    }

    for aid, artifact in artifacts.items():
        if not _is_interactive_artifact(artifact):
            continue
        receipt = receipts.get(aid)
        if not receipt:
            problems.append(f"INTERACTIVE_CHROMIUM_RECEIPT_MISSING: {aid}")
            continue

        artifact_digest = str(artifact.get("sha256") or "")
        if receipt.get("artifact_sha256") != artifact_digest:
            problems.append(f"INTERACTIVE_CHROMIUM_ARTIFACT_DIGEST_MISMATCH: {aid}")
        if receipt.get("head_sha") != head:
            problems.append(f"INTERACTIVE_CHROMIUM_HEAD_MISMATCH: {aid}")
        if receipt.get("tool") != CHROMIUM_TOOL:
            problems.append(f"INTERACTIVE_CHROMIUM_TOOL_INVALID: {aid}:{receipt.get('tool')}")
        if receipt.get("engine") != CHROMIUM_ENGINE:
            problems.append(f"INTERACTIVE_CHROMIUM_ENGINE_INVALID: {aid}:{receipt.get('engine')}")
        if receipt.get("status") != "PASS":
            problems.append(f"INTERACTIVE_CHROMIUM_NOT_PASS: {aid}:{receipt.get('status')}")
        if receipt.get("profile") != "tablet-12.7":
            problems.append(f"INTERACTIVE_CHROMIUM_PROFILE_INVALID: {aid}:{receipt.get('profile')}")

        report_text = str(receipt.get("report_path") or "")
        if not report_text:
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_PATH_MISSING: {aid}")
            continue
        report_path = REPO / report_text
        if not report_path.exists() or not report_path.is_file():
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_MISSING: {aid}:{report_text}")
            continue
        actual_report_digest = sha256_file(report_path)
        if receipt.get("report_sha256") != actual_report_digest:
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_DIGEST_MISMATCH: {aid}")

        report, error = _load_receipt_report(report_path)
        if report is None:
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_INVALID: {aid}:{error}")
            continue
        if report.get("schema") != "interactive-page-audit/v1":
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_SCHEMA_INVALID: {aid}")
        if report.get("engine") != CHROMIUM_ENGINE:
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_ENGINE_INVALID: {aid}")
        if report.get("artifact_sha256") != artifact_digest:
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_ARTIFACT_MISMATCH: {aid}")
        if report.get("status") != "PASS":
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_NOT_PASS: {aid}:{report.get('status')}")
        if report.get("head_sha") not in {None, "", head}:
            problems.append(f"INTERACTIVE_CHROMIUM_REPORT_HEAD_MISMATCH: {aid}")

    return problems


def check(run: dict[str, Any], *, final: bool = True) -> list[str]:
    problems = validate_content_self_audits(run)
    if final:
        problems.extend(validate_interactive_chromium(run))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--phase", choices=("authoring", "final"), default="final")
    args = parser.parse_args(argv)
    try:
        run = load(args.run)
        problems = check(run, final=args.phase == "final")
    except (OSError, json.JSONDecodeError, SelfAuditError) as exc:
        print(f"load failed: {exc}")
        return 1
    if problems:
        print("\n".join(problems))
        return 1
    print("ok: qrt content self-audit" if args.phase == "authoring" else "ok: qrt content self-audit + interactive Chromium")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
