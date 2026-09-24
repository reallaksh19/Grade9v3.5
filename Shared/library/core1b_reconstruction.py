"""Phase-3 Core1B genuine-reconstruction inventory and forward gate.

Core1B owns no second conceptual truth. It reuses microtopic.inferential_jump and
changes who performs the inference and when the completed construction is revealed.
This audit checks falsifiable structure and route coverage. Whether the learner route
is cognitively genuine rather than a paraphrase remains an explicit reviewer judgment.
"""
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


def _route_coverage(packages: list[dict], core: str) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = {}
    for package in packages:
        for route in package.get("teaching_routes", []) or []:
            if not isinstance(route, dict) or core not in (route.get("cores") or []):
                continue
            route_ref = route.get("id")
            for microtopic_ref in route.get("microtopic_refs") or []:
                if not isinstance(microtopic_ref, str):
                    continue
                coverage.setdefault(microtopic_ref, [])
                if isinstance(route_ref, str) and route_ref:
                    coverage[microtopic_ref].append(route_ref)
    return {
        key: sorted(set(values))
        for key, values in coverage.items()
    }


def _valid_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _closure_findings(attempt: dict, ref: str) -> list[dict]:
    findings: list[dict] = []
    closure = attempt.get("closure")
    if not _valid_text(attempt.get("produces")):
        findings.append(_finding(
            "ATTEMPT_PRODUCTION_MISSING",
            "Core1B does not state what the learner must produce.",
            ref,
        ))
    if closure not in {"MODEL_RESPONSE", "RUBRIC", "CRITERIA"}:
        findings.append(_finding(
            "ATTEMPT_CLOSURE_INVALID",
            "Attempt closure is missing or outside the governed closure modes.",
            ref,
        ))
        return findings

    if closure == "MODEL_RESPONSE":
        if not _valid_text(attempt.get("model_response")):
            findings.append(_finding(
                "ATTEMPT_MODEL_RESPONSE_MISSING",
                "MODEL_RESPONSE closure has no model response.",
                ref,
            ))
        return findings

    rubric = attempt.get("rubric") or []
    if not isinstance(rubric, list) or not rubric:
        findings.append(_finding(
            "ATTEMPT_RUBRIC_MISSING",
            f"{closure} closure has no rubric/criteria.",
            ref,
        ))
    else:
        for index, criterion in enumerate(rubric):
            if (
                not isinstance(criterion, dict)
                or not _valid_text(criterion.get("criterion"))
                or not _valid_text(criterion.get("evidence_of"))
            ):
                findings.append(_finding(
                    "ATTEMPT_RUBRIC_INCOMPLETE",
                    "A rubric criterion lacks criterion or evidence_of.",
                    f"{ref}:rubric:{index}",
                ))

    if closure == "RUBRIC":
        if not (isinstance(attempt.get("accepted"), list) and attempt["accepted"]):
            findings.append(_finding(
                "ATTEMPT_ACCEPTED_EXAMPLES_MISSING",
                "RUBRIC closure has no representative accepted response.",
                ref,
            ))
        if not (isinstance(attempt.get("rejected"), list) and attempt["rejected"]):
            findings.append(_finding(
                "ATTEMPT_REJECTED_EXAMPLES_MISSING",
                "RUBRIC closure has no representative rejected response.",
                ref,
            ))
    return findings


def audit_microtopic(
    subject: str,
    package_path: str,
    microtopic: dict,
    *,
    core1a_route_refs: list[str],
    core1b_route_refs: list[str],
) -> dict:
    findings: list[dict] = []
    ref = microtopic.get("id")

    in_a = bool(core1a_route_refs)
    in_b = bool(core1b_route_refs)
    if in_a and not in_b:
        findings.append(_finding(
            "CORE1B_COVERAGE_MISSING",
            "Core1A teaching routes include this microtopic but Core1B routes do not.",
            ref,
        ))
    if in_b and not in_a:
        findings.append(_finding(
            "CORE1B_ORPHAN_COVERAGE",
            "Core1B routes include a microtopic absent from Core1A route coverage.",
            ref,
        ))

    elicitation = microtopic.get("elicitation")
    if not isinstance(elicitation, dict):
        findings.append(_finding(
            "ELICITATION_MISSING",
            "The microtopic has no Core1B self-tutor cycle.",
            ref,
        ))
        return {
            "subject": subject,
            "package_path": package_path,
            "microtopic_ref": ref,
            "bucket_ref": microtopic.get("bucket_id"),
            "core1a_route_refs": sorted(core1a_route_refs),
            "core1b_route_refs": sorted(core1b_route_refs),
            "coverage_equal": in_a == in_b,
            "finding_codes": sorted({row["code"] for row in findings}),
            "findings": findings,
            "manual_review_obligations": [
                "RECONSTRUCTION_GENUINELY_DIFFERS_FROM_TEACHING_PATH",
                "BOUNDARY_TEST_CHECKS_UNDERSTANDING_NOT_RECALL",
            ],
        }

    predict = elicitation.get("predict") or {}
    if not _valid_text(predict.get("prompt")):
        findings.append(_finding(
            "PREDICT_PROMPT_MISSING",
            "The learner is not given a decision to commit to before reveal.",
            ref,
        ))
    if not _valid_text(predict.get("defensible_answer")):
        findings.append(_finding(
            "PREDICT_DEFENSIBLE_ANSWER_MISSING",
            "The prediction has no defensible answer for self-study closure.",
            ref,
        ))

    attempt = elicitation.get("attempt")
    if not isinstance(attempt, dict):
        findings.append(_finding(
            "ATTEMPT_MISSING",
            "The self-tutor cycle does not define a learner attempt.",
            ref,
        ))
    else:
        findings.extend(_closure_findings(attempt, str(ref)))

    teaching_steps = {
        row.get("id")
        for row in (microtopic.get("teaching_path") or [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    reconstruct = elicitation.get("reconstruct") or {}
    route = reconstruct.get("route") or []
    if not isinstance(route, list) or not route:
        findings.append(_finding(
            "RECONSTRUCT_ROUTE_MISSING",
            "Core1B has no learner-directed reconstruction route.",
            ref,
        ))
    else:
        for index, step in enumerate(route):
            step_ref = f"{ref}:reconstruct:{index}"
            if not isinstance(step, dict) or not _valid_text(step.get("ask")):
                findings.append(_finding(
                    "RECONSTRUCT_ASK_MISSING",
                    "A reconstruction move has no learner-facing ask.",
                    step_ref,
                ))
            if not isinstance(step, dict) or not _valid_text(step.get("why_this_ask")):
                findings.append(_finding(
                    "RECONSTRUCT_RATIONALE_MISSING",
                    "A reconstruction move does not explain why this ask belongs here.",
                    step_ref,
                ))
            if isinstance(step, dict) and step.get("from_step_ref") is not None:
                source = step.get("from_step_ref")
                if not _valid_text(source) or source not in teaching_steps:
                    findings.append(_finding(
                        "RECONSTRUCT_STEP_REF_UNKNOWN",
                        "A reconstruction move points to an unknown Core1A teaching step.",
                        str(source),
                    ))
    if not _valid_text(reconstruct.get("differs_from_teaching_path")):
        findings.append(_finding(
            "RECONSTRUCT_DIFFERENCE_CLAIM_MISSING",
            "The author has not stated how the learner route differs from the teaching path.",
            ref,
        ))

    misconceptions = microtopic.get("misconceptions") or []
    if not misconceptions:
        findings.append(_finding(
            "DIAGNOSE_REPAIR_MISSING",
            "Core1B has no shared misconception diagnosis/repair claim.",
            ref,
        ))
    for index, row in enumerate(misconceptions):
        if (
            not isinstance(row, dict)
            or not all(
                _valid_text(row.get(key))
                for key in ("wrong_idea", "diagnostic_prompt", "repair")
            )
        ):
            findings.append(_finding(
                "DIAGNOSE_REPAIR_INCOMPLETE",
                "A misconception lacks wrong idea, diagnostic prompt, or repair.",
                f"{ref}:misconception:{index}",
            ))

    boundary = elicitation.get("boundary_test") or {}
    for key, code in (
        ("prompt", "BOUNDARY_PROMPT_MISSING"),
        ("answer", "BOUNDARY_ANSWER_MISSING"),
        ("confirms", "BOUNDARY_CONFIRMATION_MISSING"),
    ):
        if not _valid_text(boundary.get(key)):
            findings.append(_finding(
                code,
                f"Boundary test {key} is missing.",
                ref,
            ))

    return {
        "subject": subject,
        "package_path": package_path,
        "microtopic_ref": ref,
        "bucket_ref": microtopic.get("bucket_id"),
        "core1a_route_refs": sorted(core1a_route_refs),
        "core1b_route_refs": sorted(core1b_route_refs),
        "coverage_equal": in_a == in_b,
        "reconstruct_step_count": len(route) if isinstance(route, list) else 0,
        "finding_codes": sorted({row["code"] for row in findings}),
        "findings": findings,
        "manual_review_obligations": [
            "RECONSTRUCTION_GENUINELY_DIFFERS_FROM_TEACHING_PATH",
            "BOUNDARY_TEST_CHECKS_UNDERSTANDING_NOT_RECALL",
            "PREDICTION_REQUIRES_A_REAL_CONCEPTUAL_DECISION",
        ],
    }


def audit(repo: Path) -> dict:
    packages_by_subject: dict[str, list[tuple[Path, dict]]] = {}
    for subject, path, package in core1_orientation.subject_packages(repo):
        packages_by_subject.setdefault(subject, []).append((path, package))

    rows = []
    for subject, packages in sorted(packages_by_subject.items()):
        docs = [package for _, package in packages]
        core1a = _route_coverage(docs, "CORE1A")
        core1b = _route_coverage(docs, "CORE1B")
        for path, package in packages:
            relative = str(path.relative_to(repo))
            for microtopic in package.get("microtopics", []) or []:
                if not isinstance(microtopic, dict):
                    continue
                ref = microtopic.get("id")
                rows.append(audit_microtopic(
                    subject,
                    relative,
                    microtopic,
                    core1a_route_refs=core1a.get(ref, []),
                    core1b_route_refs=core1b.get(ref, []),
                ))

    rows.sort(key=lambda row: (row["subject"], row["microtopic_ref"] or ""))
    counts: dict[str, int] = {}
    for row in rows:
        for code in row["finding_codes"]:
            counts[code] = counts.get(code, 0) + 1
    return {
        "schema_version": "1.0.0",
        "audit": "CORE1B_GENUINE_RECONSTRUCTION",
        "semantics": {
            "crux": "same microtopic.inferential_jump as Core1A",
            "agency_change": "learner reconstructs before reveal",
            "structural_gate_only": True,
            "manual_review_required": True,
        },
        "summary": {
            "microtopic_count": len(rows),
            "structured_microtopics": sum(1 for row in rows if not row["findings"]),
            "microtopics_with_debt": sum(1 for row in rows if row["findings"]),
            "coverage_mismatches": sum(1 for row in rows if not row["coverage_equal"]),
            "finding_counts": dict(sorted(counts.items())),
        },
        "microtopics": rows,
    }


def baseline(report: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "audit": report["audit"],
        "basis": "legacy Core1B reconstruction debt; forward-only migration baseline",
        "microtopics": {
            row["microtopic_ref"]: row["finding_codes"]
            for row in report["microtopics"]
        },
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
                "detail": "new structural Core1B reconstruction debt relative to committed baseline",
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
        Path(args.write_report).write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.write_baseline:
        Path(args.write_baseline).write_text(
            json.dumps(baseline(report), indent=2) + "\n",
            encoding="utf-8",
        )
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
