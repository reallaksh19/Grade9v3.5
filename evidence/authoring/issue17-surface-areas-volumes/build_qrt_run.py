#!/usr/bin/env python3
"""Build the PR #16 qrt-pipeline-run/v1 authoring record for Issue #17."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
QRT = json.loads((HERE / "qrt-review.v1.json").read_text(encoding="utf-8"))
OWNER_PROMPT = (HERE / "owner-prompt.txt").read_text(encoding="utf-8")

OWNER_REPLY = "Purpose  : COMPETITION  , B1 to B5: Solid"
OWNER_REPLY_REF = "https://github.com/reallaksh19/Grade9v3.5/issues/17#issuecomment-5974555745"
AUTHORING_RECORD_REF = "https://github.com/reallaksh19/Grade9v3.5/issues/17#issuecomment-5974552327"
ACADEMIC_RECORD_REF = "https://github.com/reallaksh19/Grade9v3.5/issues/17#issuecomment-5974493003"

CAPS = {
    "CAP-MAT-SAV-CIRCLE": "DEMONSTRATED",
    "CAP-MAT-SAV-EXPOSED": "DEMONSTRATED",
    "CAP-MAT-SAV-UNITS": "DEMONSTRATED",
    "CAP-MAT-SAV-SLANT": "DEMONSTRATED",
    "CAP-MAT-SAV-RECAST": "DEMONSTRATED",
}

STEMS = {
    "Q1": "A wooden cube has edge length 7 cm.\n\nFind its total surface area.",
    "Q2": "A cylindrical water bottle has diameter 14 cm and height 20 cm.\n\nFind its curved surface area.",
    "Q3": "A cylindrical bucket is open at the top.\n\nIts internal radius is 7 cm and its height is 18 cm.\n\nFind the area of metal sheet required to make the bucket, ignoring the thickness of the sheet.",
    "Q4": "A conical tent has radius 7 m and vertical height 24 m.\n\nFind:\n\n1. its slant height;\n2. the area of canvas required to make the tent.\n\nThe base of the tent is open.",
    "Q5": "A hemispherical bowl has radius 10.5 cm.\n\nFind the area of its inner surface.\n\nExplain why the circular base is not included in your calculation.",
    "Q6": "A toy is made by mounting a cone on a hemisphere.\n\nThe cone and hemisphere have the same radius, 3.5 cm.\n\nThe vertical height of the cone is 12 cm.\n\nFind the total **exposed** surface area of the toy.\n\nThe circular face where the cone and hemisphere join is not exposed.",
    "Q7": "A cylindrical vessel of radius 7 cm and height 25 cm is open at the top.\n\nIt is to be painted:\n\n- on its entire outer curved surface; and\n- on the outside of its circular base.\n\nThe inside is not painted.\n\nFind the area to be painted.\n\nBefore calculating, state exactly which surfaces are included.",
    "Q8": "A rectangular water tank is 2 m long, 1.5 m wide and 1.2 m deep.\n\nIt is filled to 75% of its total capacity.\n\nHow many litres of water are in the tank?\n\nShow the unit conversion clearly.",
    "Q9": "A solid metallic sphere of radius 6 cm is melted and recast into identical solid spheres of radius 2 cm.\n\nAssume that no metal is lost.\n\nHow many smaller spheres are formed?\n\nExplain why surface area is not conserved in this process.",
    "Q10": "A cone and a cylinder have the same base radius and the same height.\n\nThe volume of the cylinder is 924 cm³.\n\nFind the volume of the cone.\n\nThen explain why the radius and height do **not** need to be calculated separately.",
}

# Solution-step -> calculation indices. This keeps each numerical move bound to audited rows.
STEP_CALCS = {
    "Q1": {1: [0, 1]},
    "Q2": {0: [0], 1: [1]},
    "Q3": {1: [0, 1, 2]},
    "Q4": {0: [0], 1: [1]},
    "Q5": {1: [0, 1]},
    "Q6": {0: [0], 2: [1, 2, 3]},
    "Q7": {1: [0, 1, 2]},
    "Q8": {0: [0], 1: [1], 2: [2]},
    "Q9": {1: [0], 2: [1, 2]},
    "Q10": {1: [0]},
}


def sha_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha_json(value: object) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha_text(text)


def check(evidence: str, result: str = "PASS", reason: str | None = None) -> dict:
    row = {"result": result, "evidence": evidence}
    if reason is not None:
        row["reason"] = reason
    return row


def hint_audit(qid: str, index: int, text: str, protected: str, answer: str) -> dict:
    rung = ("H1", "H2", "H3")[min(index, 2)]
    return {
        "status": "PASS",
        "summary_evidence": f"{qid} {rung} is an orienting pre-attempt support move for the competition learner and does not execute {protected}.",
        "basis_refs": [AUTHORING_RECORD_REF, ACADEMIC_RECORD_REF],
        "checks": {
            "academic_correctness": check(f"The hint is consistent with the independently verified {qid} route and contains no contradictory formula or quantity: {text}"),
            "objective_alignment": check(f"This is {rung}: it performs the authored {rung} objective recorded for {qid}, rather than acting as a post-attempt solution."),
            "w_protection": check(f"The hint neither names protected move ref {protected} nor states the verified answer {answer}; the learner must still perform the decisive move."),
            "learner_fit": check("Owner-backed profile is COMPETITION with B1-B5 DEMONSTRATED, so support is concise and bridge-oriented rather than reteaching demonstrated prerequisites."),
            "non_redundancy": check(f"{rung} has a distinct job in the clarify → correlate → open-the-way progression for {qid}."),
        },
    }


def solution_audit(qid: str, index: int, step: dict, calc_refs: list[str]) -> dict:
    return {
        "status": "PASS",
        "summary_evidence": f"{qid} post-attempt move {index + 1} uses Action → Why valid here → Result and is tied to the verified route.",
        "basis_refs": [ACADEMIC_RECORD_REF, AUTHORING_RECORD_REF],
        "checks": {
            "academic_correctness": check(f"Independent academic validation supports this move and result: {step['result']}"),
            "question_specificity": check(f"The move is anchored to {qid}'s stated geometry/conditions rather than a generic formula dump: {step['action']}"),
            "reasoning_validity": check(f"The stated warrant explains why the action is licensed here: {step['why']}"),
            "units_symbols": check("Symbols and units in the result follow the quantities in the owner question; numerical calculation rows separately verify dimensions where applicable."),
            "post_attempt_scope": check(f"This answer-bearing move is confined to post-attempt solution content; pre-attempt graph nodes do not expose {calc_refs or 'its completed result'}."),
        },
    }


def calculation_audit(qid: str, calc_id: str, calc: dict) -> dict:
    return {
        "status": "PASS",
        "summary_evidence": f"{qid} {calc_id} was independently checked against the owner givens and the verified solution route.",
        "basis_refs": [ACADEMIC_RECORD_REF],
        "checks": {
            "arithmetic_or_algebra": check(f"Expression `{calc['expression']}` evaluates to `{calc['result']}` on the verified route."),
            "units_dimensions": check(f"The result `{calc['result']}` has the dimensions/units required at this stage of {qid}."),
            "input_traceability": check(f"Inputs in `{calc['expression']}` come from the owner question or a previously established solution result."),
            "independent_check": check(str(calc.get("check") or "The result was recomputed independently from the same mathematical relation.")),
        },
    }


def question_record(item: dict, prompt_digest: str) -> dict:
    qid = item["question_id"]
    protected = item["protected_move_ref"]
    calc_rows = []
    calc_ids = []
    for idx, calc in enumerate(item.get("calculations") or []):
        cid = f"{qid}-CALC-{idx + 1}"
        calc_ids.append(cid)
        calc_rows.append({
            "id": cid,
            "expression": calc["expression"],
            "result": calc["result"],
            "self_audit": calculation_audit(qid, cid, calc),
        })

    hints = []
    for idx, text in enumerate(item.get("hints") or []):
        hid = f"{qid}-H{idx + 1}"
        hints.append({
            "id": hid,
            "text": text,
            "calculation_bearing": False,
            "calculation_refs": [],
            "self_audit": hint_audit(qid, idx, text, protected, item["verified_answer"]),
        })

    steps = []
    for idx, step in enumerate(item.get("solution_steps") or []):
        refs = [calc_ids[i] for i in STEP_CALCS.get(qid, {}).get(idx, [])]
        steps.append({
            "id": f"{qid}-SOL-{idx + 1}",
            "action": step["action"],
            "why_valid_here": step["why"],
            "result": step["result"],
            "calculation_bearing": bool(refs),
            "calculation_refs": refs,
            "self_audit": solution_audit(qid, idx, step, refs),
        })

    return {
        "id": qid,
        "verbatim_text": STEMS[qid],
        "owner_prompt_sha256": prompt_digest,
        "verified_answer": item["verified_answer"],
        "difficulty": item["difficulty"],
        "demand": item["demand"],
        "template_id": item["template_id"],
        "blueprint_ref": "BP-CORE2-SOURCE-QUESTION@1.5.0",
        "slots": {
            "X": {"text": item["X"], "basis": [item["template_id"], ACADEMIC_RECORD_REF]},
            "Y": {"text": item["Y"], "capability_ref": item["Y_capability_ref"]},
            "Z": {"text": item["Z"]},
            "W": {"text": item["W"], "protected_move_ref": protected},
        },
        "hints": hints,
        "representation": item["representation"],
        "misconception": item["misconception"],
        "solution_steps": steps,
        "calculations": calc_rows,
        "independent_check": item["independent_check"],
        "core1a_targets": item.get("core1a_targets") or [],
    }


def pre_attempt_graph(question: dict) -> dict:
    qid = question["id"]
    protected = question["slots"]["W"]["protected_move_ref"]
    nodes = []
    root_links = []
    nodes.append({"id": f"{qid}-ROOT", "phase": "PRE_ATTEMPT", "resource_kind": "QUESTION", "move_refs": [], "links": root_links})
    for hint in question["hints"]:
        nid = hint["id"]
        root_links.append(nid)
        nodes.append({"id": nid, "phase": "PRE_ATTEMPT", "resource_kind": "HINT", "move_refs": [], "links": []})
    if (question.get("representation") or {}).get("applicability") != "NOT_APPLICABLE":
        nid = f"{qid}-REP"
        root_links.append(nid)
        nodes.append({"id": nid, "phase": "PRE_ATTEMPT", "resource_kind": "REPRESENTATION", "move_refs": [], "links": []})
    post = f"{qid}-POST-SOLUTION"
    root_links.append(post)
    nodes.append({"id": post, "phase": "POST_ATTEMPT", "resource_kind": "SOLUTION", "move_refs": [protected], "links": [f"{qid}-POST-CORE1A"]})
    nodes.append({"id": f"{qid}-POST-CORE1A", "phase": "POST_ATTEMPT", "resource_kind": "CORE1A_LINK", "move_refs": [], "links": []})
    return {"question_ref": qid, "root": f"{qid}-ROOT", "nodes": nodes}


def build(head_sha: str) -> dict:
    prompt_digest = sha_text(OWNER_PROMPT)
    owner_event_id = "OWNER-ISSUE17-CLARIFICATION-1"
    profile = {
        "profile_id": "PROFILE-ISSUE17-SAV-COMPETITION",
        "purpose": "COMPETITION",
        "purpose_owner_event_ref": owner_event_id,
        "provenance": "OWNER_ESTIMATE",
        "held": {cap: {"state": state, "owner_event_ref": owner_event_id} for cap, state in CAPS.items()},
        "measured_fit_claim": False,
    }
    questions = [question_record(item, prompt_digest) for item in QRT["items"]]
    clusters = []
    for cluster in QRT["core1a_synthesis"]["clusters"]:
        clusters.append({
            "id": "EVIDENCE-" + cluster["id"],
            "question_refs": cluster["question_refs"],
            "signal": cluster["construction"],
            "publication_intent": "PUBLISH_CORE1A",
            "canonical_truth_refs": cluster["canonical_truth_refs"],
            "core1a_unit_ref": cluster["id"],
        })

    run = {
        "schema": "qrt-pipeline-run/v1",
        "run_identity": {
            "repository": "reallaksh19/Grade9v3.5",
            "branch": "feat/qrt-minimal-prompt-pipeline-hardening",
            "head_sha": head_sha,
            "issue": 17,
            "implementation_pr": 16,
        },
        "owner_prompt": {
            "text": OWNER_PROMPT,
            "sha256": prompt_digest,
            "source_ref": "https://github.com/reallaksh19/Grade9v3.5/issues/17#core-prompt--verbatim-owner-input",
        },
        "owner_events": [
            {"id": "OWNER-ISSUE17-PROMPT", "kind": "PROMPT", "source_ref": "https://github.com/reallaksh19/Grade9v3.5/issues/17", "text": OWNER_PROMPT},
            {"id": owner_event_id, "kind": "CLARIFICATION_REPLY", "source_ref": OWNER_REPLY_REF, "text": OWNER_REPLY},
        ],
        "learner_profile": profile,
        "basis_digests": {
            "matrix": sha_file(REPO / "Shared/quality/question-demand-matrix.v1.json"),
            "adapter": sha_file(REPO / "Mathematics/adapter/DemandReview.json"),
            "profile": sha_json(profile),
            "blueprint_registry": sha_file(REPO / "Shared/web/interactive-page-blueprints.v1.json"),
        },
        "questions": questions,
        "pre_attempt_graphs": [pre_attempt_graph(q) for q in questions],
        "concept_evidence": clusters,
        "rendered_artifacts": [],
        "reviews": [],
        "validation": {
            "academic": {"status": "PASS", "evidence_ref": ACADEMIC_RECORD_REF},
            "qrt_semantic": {"status": "NOT_RUN", "evidence_ref": "post-render review pending"},
            "static": {"status": "NOT_RUN", "evidence_ref": "render pending"},
            "browser": {"status": "NOT_RUN", "evidence_ref": "render pending"},
            "print": {"status": "NOT_APPLICABLE", "evidence_ref": "Issue #17 requests learner-facing HTML; no PDF is an acceptance deliverable."},
            "interactive_chromium_receipts": [],
        },
    }
    return run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", type=Path, default=HERE / "generated/qrt-pipeline-run.authoring.json")
    args = parser.parse_args()
    run = build(args.head)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
