"""Phase-2 Core1A conceptual-construction inventory and forward gate.

The canonical crux is microtopic.inferential_jump. This audit checks structural
evidence for a completed conceptual construction without pretending that field
presence proves pedagogical quality. The final judgment that the route genuinely
constructs the inference remains a reviewer obligation.
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


def _index(packages: list[dict], key: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for package in packages:
        for row in package.get(key, []) or []:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                out[row["id"]] = row
    return out


def _question_family_ref(question: dict) -> str | None:
    value = question.get("family_ref") or question.get("family")
    return value if isinstance(value, str) and value else None


def _is_core1a_worked_anchor(question: dict) -> bool:
    exposures = question.get("exposure") or []
    exposed = any(
        isinstance(row, dict) and row.get("core") == "CORE1A"
        for row in exposures
    )
    reasoning = (question.get("answer") or {}).get("reasoning") or []
    return exposed and isinstance(reasoning, list) and bool(reasoning)


def _bound_representations(
    microtopic: dict,
    representations: dict[str, dict],
) -> tuple[list[str], list[str], int]:
    microtopic_ref = microtopic.get("id")
    explicit = [
        ref
        for ref in (microtopic.get("representation_refs") or [])
        if isinstance(ref, str) and ref
    ]
    bound = set(explicit)
    scene_bound = set()
    bridge_count = 0

    for rep_ref, rep in representations.items():
        scenes = rep.get("scene_instances") or []
        if any(
            isinstance(scene, dict)
            and scene.get("microtopic_ref") == microtopic_ref
            and "CORE1A" in (scene.get("cores") or [])
            for scene in scenes
        ):
            bound.add(rep_ref)
            scene_bound.add(rep_ref)

    for rep_ref in bound:
        rep = representations.get(rep_ref)
        if not isinstance(rep, dict):
            continue
        for row in rep.get("correspondence") or []:
            if not isinstance(row, dict):
                continue
            if all(
                isinstance(row.get(key), str) and row[key].strip()
                for key in ("symbol", "element", "in_words")
            ):
                bridge_count += 1

    return sorted(bound), sorted(scene_bound), bridge_count


def audit_microtopic(
    subject: str,
    package_path: str,
    microtopic: dict,
    *,
    representations: dict[str, dict],
    relations: dict[str, dict],
    questions: list[dict],
) -> dict:
    findings: list[dict] = []
    ref = microtopic.get("id")
    assumptions = microtopic.get("entry_assumptions") or []
    jump = microtopic.get("inferential_jump")
    path = microtopic.get("teaching_path") or []
    misconceptions = microtopic.get("misconceptions") or []
    exit_task = microtopic.get("exit_task") or {}
    answer = exit_task.get("answer") or {}

    if not assumptions:
        findings.append(_finding(
            "ENTRY_ASSUMPTIONS_MISSING",
            "Core1A does not state the learner capability assumed at entry.",
            ref,
        ))
    if not isinstance(jump, str) or not jump.strip():
        findings.append(_finding(
            "INFERENTIAL_JUMP_MISSING",
            "The conceptual crux is not authored.",
            ref,
        ))
    if not path:
        findings.append(_finding(
            "TEACHING_PATH_MISSING",
            "The inferential jump has no completed construction route.",
            ref,
        ))
    for step in path:
        sid = step.get("id") if isinstance(step, dict) else None
        if (
            not isinstance(step, dict)
            or not isinstance(step.get("action"), str)
            or not step["action"].strip()
        ):
            findings.append(_finding(
                "TEACHING_STEP_ACTION_MISSING",
                "A teaching step has no action.",
                sid or ref,
            ))
        if (
            not isinstance(step, dict)
            or not isinstance(step.get("why_valid"), str)
            or not step["why_valid"].strip()
        ):
            findings.append(_finding(
                "TEACHING_STEP_WHY_VALID_MISSING",
                "A teaching step does not justify why the move is valid.",
                sid or ref,
            ))

    explicit_rep_refs = [
        item
        for item in (microtopic.get("representation_refs") or [])
        if isinstance(item, str) and item
    ]
    for rep_ref in explicit_rep_refs:
        if rep_ref not in representations:
            findings.append(_finding(
                "REPRESENTATION_REF_UNRESOLVED",
                "A Core1A representation reference does not resolve subject-wide.",
                rep_ref,
            ))

    bound_rep_refs, scene_bound_refs, bridge_count = _bound_representations(
        microtopic,
        representations,
    )
    if not bound_rep_refs:
        findings.append(_finding(
            "REPRESENTATION_BRIDGE_MISSING",
            "No canonical representation is bound to this Core1A concept.",
            ref,
        ))
    elif not scene_bound_refs:
        findings.append(_finding(
            "REPRESENTATION_SCENE_BINDING_MISSING",
            "No canonical representation has a CORE1A scene bound to this microtopic.",
            ref,
        ))
    if bound_rep_refs and bridge_count == 0:
        findings.append(_finding(
            "REPRESENTATION_CORRESPONDENCE_MISSING",
            "The bound representation has no explicit picture/word/symbol correspondence.",
            ref,
        ))

    if not misconceptions:
        findings.append(_finding(
            "MISCONCEPTION_REPAIR_MISSING",
            "No plausible wrong path with diagnostic and repair is authored.",
            ref,
        ))
    for row in misconceptions:
        if (
            not isinstance(row, dict)
            or not all(
                isinstance(row.get(key), str) and row[key].strip()
                for key in ("wrong_idea", "diagnostic_prompt", "repair")
            )
        ):
            findings.append(_finding(
                "MISCONCEPTION_REPAIR_INCOMPLETE",
                "A misconception row lacks wrong idea, diagnostic prompt, or repair.",
                ref,
            ))

    if not isinstance(exit_task.get("prompt"), str) or not exit_task["prompt"].strip():
        findings.append(_finding(
            "EXIT_PROMPT_MISSING",
            "Core1A has no observable exit prompt.",
            ref,
        ))
    if not isinstance(answer.get("summary"), str) or not answer["summary"].strip():
        findings.append(_finding(
            "EXIT_CLOSURE_MISSING",
            "The exit task has no model answer summary.",
            ref,
        ))
    if not isinstance(answer.get("check"), str) or not answer["check"].strip():
        findings.append(_finding(
            "INDEPENDENT_CHECK_MISSING",
            "The learner has no explicit independent check on the exit result.",
            ref,
        ))

    relation_refs = [
        item
        for item in (microtopic.get("relation_refs") or [])
        if isinstance(item, str) and item
    ]
    relation_check_refs = [
        relation_ref
        for relation_ref in relation_refs
        if isinstance(relations.get(relation_ref), dict)
        and (relations[relation_ref].get("checks") or [])
    ]
    if relation_refs and not relation_check_refs:
        findings.append(_finding(
            "RELATION_CHECK_MISSING",
            "The microtopic uses governing relations but none provides an independent learner check.",
            ref,
        ))

    family_refs = {
        item
        for item in (microtopic.get("question_family_refs") or [])
        if isinstance(item, str) and item
    }
    worked_anchor_refs = sorted(
        question["id"]
        for question in questions
        if isinstance(question, dict)
        and _question_family_ref(question) in family_refs
        and _is_core1a_worked_anchor(question)
        and isinstance(question.get("id"), str)
    )
    if not worked_anchor_refs:
        findings.append(_finding(
            "WORKED_CONCEPTUAL_ANCHOR_MISSING",
            "No mapped question is exposed to CORE1A with a completed answer.reasoning[] route.",
            ref,
        ))

    badge = microtopic.get("intrinsic_badge")
    research = microtopic.get("research_contribution")
    if badge in {"MEDIUM", "HARD"} and (
        not isinstance(research, str) or not research.strip()
    ):
        findings.append(_finding(
            "RESEARCH_CONTRIBUTION_MISSING",
            "MEDIUM/HARD Core1A content has no declared research-informed contribution.",
            ref,
        ))

    return {
        "subject": subject,
        "package_path": package_path,
        "microtopic_ref": ref,
        "bucket_ref": microtopic.get("bucket_id"),
        "intrinsic_badge": badge,
        "representation_refs": bound_rep_refs,
        "core1a_scene_representation_refs": scene_bound_refs,
        "representation_bridge_count": bridge_count,
        "worked_anchor_refs": worked_anchor_refs,
        "relation_check_refs": sorted(relation_check_refs),
        "finding_codes": sorted({row["code"] for row in findings}),
        "findings": findings,
        "manual_review_obligations": [
            "TEACHING_PATH_ACTUALLY_CONSTRUCTS_INFERENTIAL_JUMP",
            "WORKED_ANCHOR_ILLUMINATES_CONCEPT_NOT_APPLICATION_DRILL",
            "REPRESENTATION_BRIDGE_IS_SEMANTICALLY_BIDIRECTIONAL",
        ],
    }


def audit(repo: Path) -> dict:
    packages_by_subject: dict[str, list[tuple[Path, dict]]] = {}
    for subject, path, package in core1_orientation.subject_packages(repo):
        packages_by_subject.setdefault(subject, []).append((path, package))

    rows = []
    for subject, packages in sorted(packages_by_subject.items()):
        package_docs = [package for _, package in packages]
        representations = _index(package_docs, "representations")
        relations = _index(package_docs, "relations")
        questions = [
            question
            for package in package_docs
            for question in (package.get("questions") or [])
            if isinstance(question, dict)
        ]
        for path, package in packages:
            relative = str(path.relative_to(repo))
            for microtopic in package.get("microtopics", []) or []:
                if isinstance(microtopic, dict):
                    rows.append(audit_microtopic(
                        subject,
                        relative,
                        microtopic,
                        representations=representations,
                        relations=relations,
                        questions=questions,
                    ))

    rows.sort(key=lambda row: (row["subject"], row["microtopic_ref"] or ""))
    counts: dict[str, int] = {}
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
            "worked_anchor_mechanism": "question exposure CORE1A + answer.reasoning[]",
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
