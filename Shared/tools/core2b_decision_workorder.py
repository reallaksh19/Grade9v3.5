#!/usr/bin/env python3
"""Read-only, exact-source I5 academic decision work order for one authored Physics pair.

This is a review packet generator, NOT a transfer verdict, signed academic review,
ordinary-Core2 source-custody grant, or learner-facing artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))
from Shared.tools import core2b_inventory

SOURCE = "Physics/library/phy-kin-2d-motion.v1.json"
PARENT = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"
CHILD = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"


def _hash(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _stable_hash(value: Any) -> str:
    return _hash(json.dumps(value, sort_keys=True, ensure_ascii=False,
                            separators=(",", ":")).encode("utf-8"))


def _is_exposed(row: dict, core: str) -> bool:
    return any(isinstance(x, dict) and x.get("core") == core
               for x in row.get("exposure", []))


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def build_packet(source_bytes: bytes, *, source_path: str = SOURCE) -> dict:
    """Audit explicit source pair and emit questions for a different human reviewer.

    All authored claims are displayed for scrutiny, never marked independent truth.
    No reviewer identity, timestamp, acceptance or signoff is fabricated.
    """
    source = json.loads(source_bytes)
    if not isinstance(source, dict) or not isinstance(source.get("questions"), list):
        raise ValueError("REVIEW_SOURCE_NOT_CANONICAL_QUESTION_PACKAGE")
    questions = source["questions"]
    if any(not isinstance(q, dict) or not _text(q.get("id")) for q in questions):
        raise ValueError("REVIEW_SOURCE_QUESTION_ID_INVALID")
    ids = [q["id"] for q in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("REVIEW_SOURCE_DUPLICATE_QUESTION_ID")
    matches_a = [q for q in questions if q["id"] == PARENT]
    matches_b = [q for q in questions if q["id"] == CHILD]
    if len(matches_a) != 1 or len(matches_b) != 1:
        raise ValueError("REVIEW_PAIR_SOURCE_QUESTION_MISSING")
    a, b = matches_a[0], matches_b[0]
    transfer = b.get("transfer") or {}
    b_answer = b.get("answer") or {}
    a_answer = a.get("answer") or {}
    route_a = a_answer.get("reasoning_route") or []
    route_b = b_answer.get("reasoning_route") or []
    parent_crux = [m for m in route_a if isinstance(m, dict)
                   and m.get("id") == a_answer.get("crux_move_ref")]
    protected = [m for m in route_b if isinstance(m, dict)
                 and m.get("id") == transfer.get("protected_move_ref")]
    source_steps = {
        step.get("id"): {"microtopic_ref": micro.get("id"), **step}
        for micro in source.get("microtopics", [])
        if isinstance(micro, dict)
        for step in micro.get("teaching_path", [])
        if isinstance(step, dict) and _text(step.get("id"))
    }
    repair = source_steps.get(b.get("repair_ref"))
    reviewer_holds: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            reviewer_holds.append(code)

    require(_is_exposed(a, "CORE2A") and _is_exposed(b, "CORE2B"),
            "PAIR_ROLE_EXPOSURE_INVALID")
    require(a.get("origin") == "AUTHORED" and b.get("origin") == "AUTHORED",
            "QUESTION_ORIGIN_NOT_BOTH_AUTHORED")
    require(_text(a.get("family_ref"))
            and a.get("family_ref") == b.get("family_ref"),
            "PAIR_FAMILY_MISMATCH")
    require((b.get("adaptation") or {}).get("parent_ref") == PARENT
            and PARENT in (transfer.get("builds_on") or []),
            "TRANSFER_CONCRETE_PARENT_LINEAGE_MISMATCH")
    require(len(parent_crux) == 1 and _text(parent_crux[0].get("action"))
            if parent_crux else False, "FAMILIAR_CRUX_NOT_RESOLVED")
    require(len(protected) == 1 and protected[0].get("kind") == "DECIDE"
            and b_answer.get("crux_move_ref") == transfer.get("protected_move_ref")
            if protected else False, "TRANSFER_PROTECTED_DECIDE_INVALID")
    require(transfer.get("dimension") == "model_choice"
            and _text(transfer.get("statement"))
            and _text(transfer.get("invariant"))
            and _text((transfer.get("novelty") or {}).get("why_new")),
            "TRANSFER_CHANGED_DEMAND_UNSUPPORTED")
    require(a.get("stem") != b.get("stem") and _text(a.get("stem"))
            and _text(b.get("stem")), "PARENT_CHILD_STEMS_UNCHANGED")
    require(bool(repair) and _text(repair.get("action")),
            "TRANSFER_REPAIR_NOT_SPECIFIC_TEACHING_STEP")
    rubric = b_answer.get("rubric") or []
    require(bool(rubric) and all(
        isinstance(x, dict) and _text(x.get("criterion"))
        and _text(x.get("evidence_of")) for x in rubric),
        "TRANSFER_RUBRIC_MISSING")
    require(bool(route_a) and _text(a_answer.get("check")),
            "FAMILIAR_WORKED_RECONSTRUCTION_MISSING")

    # Existing Core2B authority owns semantic structural debt, including capability
    # closure across all Physics ordinary packages. The reviewer still adjudicates
    # whether the transfer is genuinely unfamiliar and within taught scope.
    source_root = REPO / "Physics"
    records = core2b_inventory._subject_records(source_root) if source_root.is_dir() else {}
    if records and PARENT in records and CHILD in records:
        mature = core2b_inventory.classify(
            records[CHILD], records, core2b_inventory._step_ids(records)
        )
        structural_debt = mature["debt_reasons"]
    else:
        # An isolated test fixture is not evidence that capabilities are established.
        structural_debt = ["CAPABILITY_CLOSURE_NOT_EVALUATED_IN_ISOLATED_CONTEXT"]
    review_asks = [
        {
            "code": "A_PARENT_CRUX",
            "prompt": "What action was already demonstrated by the familiar question, and what was supplied to the learner rather than chosen?",
            "check": "Distinguish given horizontal launch speed from identifying the common ground-contact event.",
            "evidence_paths": ["parent.stem", "parent.reasoning_crux", "parent.answer_check"],
        },
        {
            "code": "B_REAL_NEW_DECIDE",
            "prompt": "Ignoring wording changes and new numerical values, is the protected release-state DECIDE genuinely absent from earlier Core1A/B and Core2A exposure? Dispute the authored novelty comparison if not.",
            "check": "Check the actual prior materials; a novelty.why_new assertion is not independent confirmation.",
            "evidence_paths": ["child.stem", "child.protected_decide", "child.novelty_author_claim", "child.novelty_checked_against"],
        },
        {
            "code": "C_CAPABILITY_CLOSURE",
            "prompt": "Does choosing initial package velocity at carrier release require an untaught concept rather than transfer of established component-motion truth?",
            "check": "Compare the actual taught Core1A/Core1B capability and the declared lineage, not inferred mastery.",
            "evidence_paths": ["child.transfer_lineage", "capability_debt_from_existing_inventory"],
        },
        {
            "code": "D_PHYSICS_AND_COUNTERMODEL",
            "prompt": "Check physical assumptions, ground/plane frame consistency, release velocity, gravity-only force, common time and reject the zero-velocity/continued-thrust distractors.",
            "check": "Independently calculate t=4 s and horizontal travel 200 m; distinguish assertion from actual proof.",
            "evidence_paths": ["child.conditions", "child.protected_decide", "child.solution", "child.answer_check"],
        },
        {
            "code": "E_PREATTEMPT_W",
            "prompt": "Could any preview, figure stage, navigation text, hint or scaffold disclose the release-state model decision before learner commitment?",
            "check": "Compare each rendered channel to the protected action; assess the actual browser and PDF separately.",
            "evidence_paths": ["child.protected_decide", "child.hints", "child.scaffolds", "child.transfer_statement", "child.invariant"],
        },
        {
            "code": "F_REPAIR_RUBRIC",
            "prompt": "Does the exact canonical repair step teach the missed initial-state decision, and does the rubric distinguish model-choice failure from later arithmetic?",
            "check": "If K2D3-1 only states the standard projectile model, request a more specific repair instead of accepting by matching an ID.",
            "evidence_paths": ["child.repair_step", "child.rubric", "child.protected_decide"],
        },
        {
            "code": "G_INDEPENDENT_DISPOSITION",
            "prompt": "Independently decide ACCEPT_TRANSFER, REWORK_TO_CORE2A, or TEACH_PREREQUISITE_FIRST and cite source/learner evidence for the decision.",
            "check": "Only a separately identified qualified reviewer can conclude. No reviewer receipt exists in this generated work order.",
            "evidence_paths": ["parent", "child", "source_sha256"],
        },
    ]
    return {
        "schema": "core2b-independent-decision-workorder/v1",
        "audience": "INTERNAL_REVIEW_ONLY_CONTAINS_PROTECTED_ANSWER",
        "source_path": source_path,
        "source_sha256": _hash(source_bytes),
        "source_package_id": source.get("package_id"),
        "source_package_status": source.get("status"),
        "parent": {
            "id": PARENT, "question_sha256": _stable_hash(a),
            "stem": a["stem"], "conditions": a.get("conditions") or [],
            "role": "CORE2A", "origin": a.get("origin"),
            "family_ref": a.get("family_ref"),
            "reasoning_crux": parent_crux[0] if len(parent_crux) == 1 else None,
            "reasoning_route": route_a, "answer_check": a_answer.get("check"),
        },
        "child": {
            "id": CHILD, "question_sha256": _stable_hash(b),
            "stem": b["stem"], "conditions": b.get("conditions") or [],
            "role": "CORE2B", "origin": b.get("origin"),
            "family_ref": b.get("family_ref"),
            "transfer_dimension": transfer.get("dimension"),
            "transfer_lineage": transfer.get("builds_on") or [],
            "transfer_statement": transfer.get("statement"),
            "invariant": transfer.get("invariant"),
            "novelty_author_claim": (transfer.get("novelty") or {}).get("why_new"),
            "novelty_checked_against": (transfer.get("novelty") or {}).get("checked_against") or [],
            "protected_decide": protected[0] if len(protected) == 1 else None,
            "reasoning_route": route_b,
            "solution": b_answer.get("summary"),
            "answer_check": b_answer.get("check"),
            "hints": b.get("hints") or [],
            "scaffolds": b.get("scaffolds") or [],
            "repair_ref": b.get("repair_ref"),
            "repair_step": repair,
            "rubric": rubric,
        },
        "capability_debt_from_existing_inventory": structural_debt,
        "structural_holds": reviewer_holds,
        "packet_status": ("PREPARED_WITH_STRUCTURAL_HOLDS" if reviewer_holds
                          else "PREPARED_UNASSIGNED"),
        "review_questions": review_asks,
        "independent_reviewer": None,
        "independent_reviewed_at": None,
        "independent_academic_decision": "PENDING_INDEPENDENT_ADJUDICATION",
        "signed_evidence_ref": None,
        "learner_observation": "NOT_RUN",
        "question_qrt_review": "NOT_EVALUATED",
        "ordinary_core2_source_custody": "NOT_EVALUATED",
        "rights_to_reuse_external_source": "NOT_GRANTED_OR_EVIDENCED",
        "release_eligible": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, default=REPO / SOURCE)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--enforce-structure", action="store_true",
                        help="Only fail structural contradiction, NOT lack of academic decision")
    args = parser.parse_args(argv)
    try:
        # Only the one bounded canonical source is authorized as this packet's input.
        if args.source.resolve() != (REPO / SOURCE).resolve():
            raise ValueError("TRANSFER_PACKET_UNEXPECTED_SOURCE_PATH")
        result = build_packet(args.source.read_bytes())
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"TRANSFER_REVIEW_WORKORDER_INVALID: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(json.dumps({
        "packet_status": result["packet_status"],
        "source_sha256": result["source_sha256"],
        "parent": result["parent"]["id"],
        "child": result["child"]["id"],
        "structural_holds": result["structural_holds"],
        "academic_decision": result["independent_academic_decision"],
        "release_eligible": result["release_eligible"],
        "out": str(args.out) if args.out else None,
    }, indent=2))
    return 1 if args.enforce_structure and result["structural_holds"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
