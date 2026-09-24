"""Phase-2 Core1A conceptual-construction inventory and forward gate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Shared.library import core1_orientation


def _finding(code: str, detail: str, ref: str | None = None) -> dict:
    row = {"code": code, "detail": detail}
    if ref:
        row["ref"] = ref
    return row


def _index(packages: list[dict], key: str) -> dict[str, dict]:
    out = {}
    for package in packages:
        for row in package.get(key, []) or []:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                out[row["id"]] = row
    return out


def audit_microtopic(subject: str, package_path: str, microtopic: dict, *, representations: dict[str, dict]) -> dict:
    findings = []
    ref = microtopic.get("id")
    assumptions = microtopic.get("entry_assumptions") or []
    jump = microtopic.get("inferential_jump")
    path = microtopic.get("teaching_path") or []
    misconceptions = microtopic.get("misconceptions") or []
    exit_task = microtopic.get("exit_task") or {}
    answer = exit_task.get("answer") or {}

    if not assumptions:
        findings.append(_finding("ENTRY_ASSUMPTIONS_MISSING", "Core1A does not state the learner capability assumed at entry.", ref))
    if not isinstance(jump, str) or not jump.strip():
        findings.append(_finding("INFERENTIAL_JUMP_MISSING", "The conceptual crux is not authored.", ref))
    if not path:
        findings.append(_finding("TEACHING_PATH_MISSING", "The inferential jump has no completed construction route.", ref))
    for step in path:
        sid = step.get("id") if isinstance(step, dict) else None
        if not isinstance(step, dict) or not isinstance(step.get("action"), str) or not step["action"].strip():
            findings.append(_finding("TEACHING_STEP_ACTION_MISSING", "A teaching step has no action.", sid or ref))
        if not isinstance(step, dict) or not isinstance(step.get("why_valid"), str) or not step["why_valid"].strip():
            findings.append(_finding("TEACHING_STEP_WHY_VALID_MISSING", "A teaching step does not justify why the move is valid.", sid or ref))

    rep_refs = [x for x in (microtopic.get("representation_refs") or []) if isinstance(x, str)]
    bridge_count = 0
    for rep_ref in rep_refs:
        rep = representations.get(rep_ref)
        if rep is None:
            findings.append(_finding("REPRESENTATION_REF_UNRESOLVED", "A Core1A representation reference does not resolve subject-wide.", rep_ref))
            continue
        for row in rep.get("correspondence") or []:
            if not isinstance(row, dict):
                continue
            if all(isinstance(row.get(k), str) and row[k].strip() for k in ("symbol", "element", "in_words")):
                bridge_count += 1
    if rep_refs and bridge_count == 0:
        findings.append(_finding("REPRESENTATION_BRIDGE_MISSING", "Referenced representations do not carry a complete picture/word/symbol correspondence.", ref))

    if not misconceptions:
        findings.append(_finding("MISCONCEPTION_REPAIR_MISSING", "No plausible wrong path with diagnostic and repair is authored.", ref))
    for row in misconceptions:
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str) and row[k].strip() for k in ("wrong_idea", "diagnostic_prompt", "repair")):
            findings.append(_finding("MISCONCEPTION_REPAIR_INCOMPLETE", "A misconception row lacks wrong idea, diagnostic prompt, or repair.", ref))

    if not isinstance(exit_task.get("prompt"), str) or not exit_task["prompt"].strip():
        findings.append(_finding("EXIT_PROMPT_MISSING", "Core1A has no observable exit prompt.", ref))
    if not isinstance(answer.get("summary"), str) or not answer["summary"].strip():
        findings.append(_finding("EXIT_CLOSURE_MISSING", "The exit task has no model answer summary.", ref))
    if not isinstance(answer.get("check"), str) or not answer["check"].strip():
        findings.append(_finding("INDEPENDENT_CHECK_MISSING", "The learner has no explicit independent check on the exit result.", ref))

    badge = microtopic.get("intrinsic_badge")
    research = microtopic.get("research_contribution")
    if badge in {"MEDIUM", "HARD"} and (not isinstance(research, str) or not research.strip()):
        findings.append(_finding("RESEARCH_CONTRIBUTION_MISSING", "MEDIUM/HARD Core1A content has no declared research-informed contribution.", ref))

    return {
        "subject": subject,
        "package_path": package_path,
        "microtopic_ref": ref,
        "bucket_ref": microtopic.get("bucket_id"),
        "intrinsic_badge": badge,
        "representation_refs": rep_refs,
        "representation_bridge_count": bridge_count,
        "finding_codes": sorted({row["code"] for row in findings}),
        "findings": findings,
        "manual_review_obligations": [
            "TEACHING_PATH_ACTUALLY_CONSTRUCTS_INFERENTIAL_JUMP",
            "WORKED_ANCHOR_ILLUMINATES_CONCEPT_NOT_APPLICATION_DRILL",
        ],
    }


def audit(repo: Path) -> dict:
    packages_by_subject: dict[str, list[tuple[Path, dict]]] = {}
    for subject, path, package in core1_orientation.subject_packages(repo):
        packages_by_subject.setdefault(subject, []).append((path, package))

    rows = []
    for subject, packages in sorted(packages_by_subject.items()):
        representations = _index([p for _, p in packages], "representations")
        for path, package in packages:
            rel = str(path.relative_to(repo))
            for microtopic in package.get("microtopics", []) or []:
                if isinstance(microtopic, dict):
                    rows.append(audit_microtopic(subject, rel, microtopic, representations=representations))
    rows.sort(key=lambda row: (row["subject"], row["microtopic_ref"] or ""))
    counts = {}
    for row in rows:
        for code in row["finding_codes"]:
            counts[code] = counts.get(code, 0) + 1
    return {
        "schema_version": "1.0.0",
        "audit": "CORE1A_CONCEPTUAL_CONSTRUCTION",
        "semantics": {
            "crux": "microtopic.inferential_jump",
            "structural_gate_only": True,
            "manual_review_required": True,
        },
        "summary": {
            "microtopic_count": len(rows),
            "structured_microtopics": sum(1 for row in rows if not row["findings"]),
            "microtopics_with_debt": sum(1 for row in rows if row["findings"]),
            "finding_counts": dict(sorted(counts.items())),
        },
        "microtopics": rows,
    }


def baseline(report: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "audit": report["audit"],
        "basis": "legacy Core1A construction debt; forward-only migration baseline",
        "microtopics": {row["microtopic_ref"]: row["finding_codes"] for row in report["microtopics"]},
    }


def forward_findings(report: dict, baseline_doc: dict) -> list[dict]:
    previous = baseline_doc.get("microtopics") or {}
    out = []
    for row in report["microtopics"]:
        current = set(row["finding_codes"])
        allowed = set(previous.get(row["microtopic_ref"], []))
        for code in sorted(current - allowed):
            out.append({
                "microtopic_ref": row["microtopic_ref"],
                "subject": row["subject"],
                "code": code,
                "detail": "new structural Core1A construction debt relative to committed baseline",
            })
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--write-report")
    parser.add_argument("--write-baseline")
    parser.add_argument("--check-baseline")
    args = parser.parse_args()
    report = audit(Path(args.repo).resolve())
    if args.write_report:
        Path(args.write_report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.write_baseline:
        Path(args.write_baseline).write_text(json.dumps(baseline(report), indent=2) + "\n", encoding="utf-8")
    if args.check_baseline:
        base = json.loads(Path(args.check_baseline).read_text(encoding="utf-8"))
        findings = forward_findings(report, base)
        print(json.dumps({"passed": not findings, "findings": findings}, indent=2))
        return 1 if findings else 0
    if not (args.write_report or args.write_baseline):
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
