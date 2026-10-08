#!/usr/bin/env python3
"""Validate a new agent-only SOF Class 9 sample Q5 geometry proof without peer approval."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

ROOT=Path(__file__).resolve().parent
SEED=ROOT/"seed"
PROOF=ROOT/"verification"/"official-sample-q5-agent-geometry-proof.v1.json"
PILOT=ROOT/"verification"/"official-sample-2026-27-math-qrt-pilot.v1.json"
REGISTER=ROOT/"adjudication"/"source-discrepancy-register.v1.json"
QUEUE=ROOT/"review-gates"/"independent-review-queue.v1.json"
SAMPLE=ROOT/"taxonomy"/"official-sample-2026-27-observations.v1.json"
QID="SOF-IMO-G09-SAMPLE-2026-27-Q005"
URL="https://sofworld.org/download/file/fid/73719"
LANDING="https://sofworld.org/imo/class-9/sample-model-test-papers/imo-sample-papers-class-9"
FACTS=[
    "Printed labels identify l1 parallel to l2 and l3 parallel to l4.",
    "At l1/l3 a marked acute sector x lies between a downward ray of l1 and a down-left ray of l3.",
    "At l2/l4 the down-left ray of l4 and downward ray of l2 enclose a corresponding angle x.",
    "The upward-right l4 ray is opposite its downward-left ray, forming the adjacent supplementary angle to x.",
    "A third drawn oblique down-right ray partitions that supplementary angle into two adjacent sectors explicitly labelled y and y.",
]
STEPS=["parallel_transfer","supplementary_angle","two_equal_y_sectors","symbolic_solution"]
REVIEW_REQUIREMENTS=["source diagram","parallel","two y","independently","distribute"]


def ensure(ok: bool,why: str) -> None:
    if not ok: raise SeedError(why)


def independent_ray_angle_check(values: tuple[int,...]=(30,60,80)) -> list[int]:
    """Independent vector model: angle between a ray and the antipode of a ray x away."""
    out=[]
    for x in values:
        ensure(type(x) is int and 0 < x < 90,"source x sector must remain acute")
        theta=math.radians(x)
        down=(0.0,-1.0)
        up_right=(math.sin(theta),math.cos(theta))
        down_left=(-up_right[0],-up_right[1])
        bisector=(up_right[0]+down[0],up_right[1]+down[1])
        norm=math.hypot(*bisector)
        ensure(norm>0,"degenerate supplementary sector")
        bisector=(bisector[0]/norm,bisector[1]/norm)
        angle=lambda a,b:math.degrees(math.acos(max(-1.0,min(1.0,a[0]*b[0]+a[1]*b[1]))))
        transferred=angle(down,down_left)
        supplemental=angle(down,up_right)
        left_y=angle(up_right,bisector)
        right_y=angle(down,bisector)
        expected=(180-x)/2
        ensure(all(math.isclose(value,target,abs_tol=1e-8) for value,target in (
            (transferred,x),(supplemental,180-x),
            (left_y,expected),(right_y,expected),(left_y+right_y,supplemental))),
            "Q5 vector and angle-bisector geometry contradiction")
        out.append(round(expected))
    return out


def validate_proof(seed: Path=SEED, pilot: Path=PILOT,
                   register: Path=REGISTER, queue: Path=QUEUE,
                   official_sample: Path=SAMPLE, proof: Path=PROOF) -> dict:
    validate_seed(seed)
    original,_,_=load_seed(seed)
    baseline={r["id"]:r for r in original}
    try:
        p=json.loads(proof.read_text(encoding="utf-8"))
        sample=json.loads(official_sample.read_text(encoding="utf-8"))
        old=json.loads(pilot.read_text(encoding="utf-8"))
        issues=json.loads(register.read_text(encoding="utf-8"))
        tasks=json.loads(queue.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SeedError(f"source figure proof unreadable: {exc}") from exc
    ensure(isinstance(p,dict) and p.get("schema")=="sof-imo-g09-sample-q5-agent-figure-proof-v1" and
           p.get("source_role")=="ORGANIZER_HOSTED_SAMPLE_NOT_LICENSED_FOR_REPRODUCTION" and
           p.get("original_source_document_id")=="SOF-IMO-G09-SAMPLE-2026-27" and
           p.get("original_question_id")==QID and
           p.get("official_sample_pdf_url")==URL and
           p.get("owner_seed_sample_landing_url")==LANDING and
           p.get("source_pdf_zero_index_page")==1 and
           p.get("original_seed_owner_compilation_entry")==23 and
           p.get("printed_section")=="MATHEMATICAL_REASONING",
           "wrong original SOF sample source, question locator or publishing authority")
    source=baseline.get(QID)
    ensure(source is not None and source["seed_entry"]==23 and
           source["source_url_claim"]==LANDING and
           source["original_question_number_claim"]=="5" and
           source["core_eligible"] is False,
           "original owner Q5 seed changed or falsely accepted")
    sight=next((r for r in sample["records"] if r.get("question_id")==QID),None)
    prior=next((r for r in old["records"] if r.get("question_id")==QID),None)
    case=next((r for r in issues["cases"] if r.get("case_id")=="IMO-SOURCE-CONFLICT-009"),None)
    task=next((r for r in tasks["records"] if r.get("case_id")=="IMO-SOURCE-CONFLICT-009"),None)
    ensure(sight is not None and sight["printed_answer_key_option"]=="C" and
           sight["pdf_page_index"]==1 and sight["academic_answer_status"]=="NOT_INDEPENDENTLY_VERIFIED" and
           sight["core_eligible"] is False,
           "organizer sample printed source key/academic hold changed")
    ensure(prior is not None and prior["agent_derived_option"] is None and
           prior["qrt_proposal"] is None and prior["agent_answer_status"]=="FIGURE_GEOMETRY_PENDING" and
           prior["accepted_qrt_cell"] is None and prior["core_eligible"] is False,
           "historical pilot Q5 research hold must remain unchanged")
    ensure(case is not None and case["question_ids"]==[QID] and
           case["source_finding_status"]=="DIAGRAM_MATH_PENDING" and
           case["figure_required"] is True and case["core_eligible"] is False,
           "upstream Q5 source custody hold overwritten")
    ensure(task is not None and task["priority"]=="P0" and
           task["assigned_reviewer_role_required"]=="INDEPENDENT_GEOMETRY_REVIEWER" and
           task["minimum_receipt_type"]=="SIGNED_ORIGINAL_SAMPLE_Q5_ANGLE_PROOF" and
           task["signed_mathematical_receipt"] is None and
           task["peer_approval_decision"] is None and
           task["learner_content_eligible"] is False,
           "external Q5 human reviewer decision falsely supplied")
    ensure(p.get("printed_sof_answer_key_option")=="C" and
           p.get("owner_compilation_claimed_option")=="C" and
           p.get("independent_agent_computed_choice")=="C" and
           p.get("independent_agent_mathematical_result")=="y=90°−x/2" and
           p.get("result_kind")=="ADDITIONAL_AGENT_DIAGRAM_PROOF_CANDIDATE_NOT_PEER_ACCEPTED",
           "agent proof or letter did not match printed sample")
    ensure(p.get("source_diagram_facts_requiring_external_confirmation")==FACTS,
           "source line/ray labels or the two equal y sectors lost")
    steps=p.get("agent_proof_steps")
    ensure(isinstance(steps,list) and len(steps)==4 and
           [s.get("claim") for s in steps]==STEPS and
           all(isinstance(s.get("reason"),str) and len(s["reason"])>=100 for s in steps),
           "corresponding/supplementary/bisected angle proof incomplete")
    explanation=" ".join(s["reason"] for s in steps).lower()
    ensure(all(part in explanation for part in ("l1∥l2","l3∥l4","opposite","180°","2y","90°")),
           "critical parallel, opposite-ray and equal-sector warrants not explained")
    analytic=p.get("independent_analytic_check")
    ensure(isinstance(analytic,dict) and
           analytic.get("probe_x_degrees")==[30,60,80] and
           analytic.get("expected_each_y_degrees")==[75,60,50] and
           independent_ray_angle_check()==[75,60,50],
           "separate vector model or probe angles disagree")
    reviewer=p.get("external_independent_geometry_reviewer_checklist")
    ensure(isinstance(reviewer,list) and len(reviewer)==5 and
           all(isinstance(r,str) and len(r)>65 for r in reviewer),
           "missing independent source-figure reviewer acceptance tasks")
    holds={
        "previous_pilot_snapshot_status":"FIGURE_GEOMETRY_PENDING",
        "previous_dispute_case_id":"IMO-SOURCE-CONFLICT-009",
        "previous_case_status":"DIAGRAM_MATH_PENDING",
        "previous_queue_priority":"P0",
        "source_original_figure_copied":False,
        "source_original_text_or_options_copied":False,
        "original_figure_reproduction_rights":"NOT_REVIEWED",
        "independent_human_source_fidelity_signoff":None,
        "independent_human_mathematical_signoff":None,
        "academic_answer_accepted":False,
        "qrt_candidate_proposed":False,
        "qrt_acceptance":None,
        "core_eligible":False,
        "existing_pilot_and_review_queue_holds_preserved":True,
    }
    ensure(all(p.get(k)==v for k,v in holds.items()),
           "figure copied, fake external review/rights granted or premature QRT/Core admission")
    ensure(not(set(p)&{"stem","options","original_figure_image","pdf_bytes","source_diagram_svg"}),
           "original SOF published material is not cleared for reproduction")
    return {"result":"Q5_AGENT_GEOMETRY_PROOF_CANDIDATE_NOT_ACADEMICALLY_ACCEPTED",
            "original_source_question":QID,"agent_printed_option_match":"C",
            "symbolic_relation":"x + 2y = 180°",
            "independent_vector_probes":3,
            "independent_human_signoffs":0,"accepted_qrt_cells":0,"core_eligible":0}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--proof",type=Path,default=PROOF)
    a=ap.parse_args()
    try: print(json.dumps(validate_proof(proof=a.proof),sort_keys=True))
    except SeedError as exc: ap.exit(1,f"IMO_Q5_SOURCE_GEOMETRY_INVALID: {exc}\n")


if __name__=="__main__":
    main()
