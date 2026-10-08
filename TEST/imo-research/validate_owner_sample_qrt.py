#!/usr/bin/env python3
"""Owner-authorized no-human-signoff math QA and complete source-sample QRT proposals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_seed import SeedError
from validate_sample_pilot import check_pilot, score_band
from validate_sample_extension import validate_extension, check_geometric_math
from validate_sample_q5_geometry import validate_proof, independent_ray_angle_check

ROOT=Path(__file__).resolve().parent
POLICY=ROOT/"governance"/"owner-independent-academic-review-waiver.v1.json"
OVERLAY=ROOT/"verification"/"official-sample-2026-27-new-qrt-proposals.v1.json"
SOURCE_URL="https://sofworld.org/download/file/fid/73719"
SAMPLE_ID="SOF-IMO-G09-SAMPLE-2026-27"
DEMANDS={"RETRIEVE","EXPLAIN","APPLY","MODEL","REPRESENT","SYNTHESIZE","JUSTIFY"}
SCORES=("concept_model_selection","representation_translation","reasoning_chain_length",
        "algebra_computational_load","trap_exception_sensitivity")
EXPECTED={
  1:("REPRESENT",("MODEL","JUSTIFY"),(1,2,2,0,1),"D3","QRT-REPRESENT-D3","B"),
  3:("MODEL",("REPRESENT","APPLY"),(1,1,2,1,0),"D2","QRT-MODEL-D2","B"),
  5:("JUSTIFY",("REPRESENT","APPLY"),(1,2,2,0,1),"D3","QRT-JUSTIFY-D3","C"),
}
OLD_CELLS={
  "QRT-JUSTIFY-D3","QRT-REPRESENT-D1","QRT-JUSTIFY-D1",
  "QRT-MODEL-D2","QRT-REPRESENT-D2","QRT-MODEL-D3"
}


def ensure(condition: bool,why: str) -> None:
    if not condition:raise SeedError(why)


def validate_owner_sample_qrt(
    policy_path: Path=POLICY, overlay_path: Path=OVERLAY
) -> dict:
    # All three existing validators remain in force: old source/pilot holds, new
    # Q1/Q3 source mathematics, and the separate Q5 figure proof.
    existing=check_pilot()
    extended=validate_extension()
    figure=validate_proof()
    ensure(check_geometric_math()==(4,49) and independent_ray_angle_check()==[75,60,50],
           "source Q1/Q3/Q5 mathematical rechecks conflict")
    try:
        policy=json.loads(policy_path.read_text(encoding="utf-8"))
        d=json.loads(overlay_path.read_text(encoding="utf-8"))
        pilot=json.loads((ROOT/"verification"/"official-sample-2026-27-math-qrt-pilot.v1.json")
                         .read_text(encoding="utf-8"))
        newer=json.loads((ROOT/"verification"/"official-sample-2026-27-new-positions.v1.json")
                         .read_text(encoding="utf-8"))
        q5=json.loads((ROOT/"verification"/"official-sample-q5-agent-geometry-proof.v1.json")
                      .read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SeedError(f"sample QRT/owner policy source unreadable: {exc}") from exc
    ensure(isinstance(policy,dict) and
           policy.get("schema")=="sof-imo-g09-owner-academic-review-policy-v1" and
           policy.get("owner_instruction_quoted")==
               "Independent human academic approval — Not applicable, you may proceed with the next" and
           policy.get("owner_instruction_date_utc")=="2026-10-08" and
           policy.get("effective_policy")==
               "INDEPENDENT_HUMAN_ACADEMIC_SIGNOFF_NOT_REQUIRED_BY_OWNER" and
           policy.get("approval_claim_boundary")=="POLICY_WAIVER_NOT_EVIDENCE_OF_PEER_APPROVAL" and
           policy.get("original_human_signoffs_obtained")==0 and
           policy.get("computational_mathematical_evidence_still_required") is True and
           policy.get("historic_research_records_mutated") is False and
           policy.get("historic_human_review_queue_status")==
               "HISTORICAL_UNASSIGNED_NOT_REQUIRED_UNDER_CURRENT_OWNER_POLICY" and
           policy.get("source_semantic_disputes_still_flagged") is True and
           policy.get("publisher_redistribution_or_figure_rights_not_waived") is True and
           policy.get("independent_rights_grants_evidenced")==0 and
           policy.get("official_fullpaper_keys_not_invented") is True and
           policy.get("accepted_qrt_cells")==0 and
           policy.get("core_ready_questions")==0,
           "owner-waiver policy altered, rights promoted or fake human approval")
    needed={"source_question_identity","original_printed_option_or_key_sighting",
            "agent_derivation","alternate_mathematical_check",
            "source_diagram_dependency_when_applicable"}
    ensure(set(policy.get("mathematical_provenance_required",[]))==needed and
           set(policy.get("residual_not_automatic",[]))==
               {"SOURCE_FIDELITY","SOURCE_DIAGRAM_OR_NOTATION_EVIDENCE",
                "COPYRIGHT_AND_FIGURE_REUSE_RIGHTS",
                "QRT_FIVE_FACTOR_CLASSIFICATION_AND_EXPLICIT_ACCEPTANCE",
                "CORE_2_OR_CORE_1A_PRODUCT_PUBLICATION"},
           "waiver illegally removed source, mathematics or publication requirements")
    ensure(isinstance(d,dict) and
           d.get("schema")=="sof-imo-g09-official-sample-provisional-qrt-completion-v1" and
           d.get("source_document_id")==SAMPLE_ID and d.get("source_pdf_url")==SOURCE_URL,
           "new source QRT data changed organizer source identity")
    count_checks={
      "source_sample_original_positions":10,
      "original_owner_sample_seed_positions":8,
      "additional_source_position_count":2,
      "older_provisional_sample_qrt_proposals":7,
      "new_provisional_sample_qrt_proposals":3,
      "total_source_positions_with_proposed_qrt":10,
      "unique_proposed_qrt_cells_count":7,
      "accepted_primary_qrt_cells":0,
      "core_ready_count":0,
    }
    ensure(all(d.get(k)==v for k,v in count_checks.items()) and
           d.get("ten_source_question_numbers")==list(range(1,11)) and
           d.get("new_proposed_qrt_cells")==
               ["QRT-REPRESENT-D3","QRT-MODEL-D2","QRT-JUSTIFY-D3"] and
           d.get("human_independent_signoff_gate")=="NOT_APPLICABLE_OWNER_DIRECTED" and
           d.get("historic_pilot_qrt_fields_mutated") is False and
           d.get("sample_q9_source_radical_transcription_dispute_remains") is True and
           d.get("sample_q5_prior_p0_review_hold_historical_not_required_by_current_owner_policy") is True and
           d.get("original_paper_stems_figures_options_republished") is False and
           d.get("source_reproduction_license_evidenced") is False,
           "10-sample QRT census, disputes or reuse status changed")
    old_proposed=[r for r in pilot["records"] if r.get("qrt_proposal") is not None]
    ensure(len(old_proposed)==7 and set(r["qrt_proposal"]["cell"] for r in old_proposed)==OLD_CELLS,
           "historical seven proposals and cell coverage drift")
    ensure(all(r["qrt_proposal"]["accepted"] is False and r["core_eligible"] is False
               for r in old_proposed),"historical sample prematurely admitted")
    previous={r["sample_question_number"]:r for r in newer["entries"]}
    ensure(set(previous)=={1,3} and
           all(previous[q]["agent_derived_option"]==previous[q]["printed_key_option"]=="B"
               for q in (1,3)) and
           q5["independent_agent_computed_choice"]==q5["printed_sof_answer_key_option"]=="C" and
           q5["academic_answer_accepted"] is False and
           q5["core_eligible"] is False,
           "original visual sample maths evidence changed")
    records=d.get("records")
    ensure(isinstance(records,list) and len(records)==3 and
           all(isinstance(r,dict) for r in records),"three new scored sample QRT items required")
    seen=set();candidate_cells=set(OLD_CELLS)
    for r in records:
        number=r.get("sample_original_question_number")
        ensure(type(number) is int and number in EXPECTED and number not in seen,
               "duplicate/unexpected sample QRT position")
        demand,secondary,factors,band,cell,option=EXPECTED[number]
        proof=("TEST/imo-research/verification/official-sample-q5-agent-geometry-proof.v1.json"
               if number==5 else
               "TEST/imo-research/verification/official-sample-2026-27-new-positions.v1.json")
        ensure(r.get("question_id")==f"{SAMPLE_ID}-Q{number:03d}" and
               r.get("source_document_id")==SAMPLE_ID and
               r.get("organizer_printed_key_option")==option and
               r.get("agent_derived_source_option")==option and
               r.get("primary_demand")==demand and
               r.get("secondary_demands")==list(secondary) and
               r.get("primary_demand") in DEMANDS and
               all(x in DEMANDS for x in r.get("secondary_demands",[])) and
               r.get("mathematical_evidence_reference")==proof,
               f"source Q{number}: identity/key/demand/provenance mismatch")
        components=r.get("five_factor_scores")
        ensure(isinstance(components,dict) and
               set(components)==set(SCORES) and
               all(type(components[k]) is int and 0<=components[k]<=2 for k in SCORES),
               f"source Q{number}: five-factor scoring not well-formed")
        values=tuple(components[k] for k in SCORES)
        total=sum(values)
        ensure(values==factors and r.get("difficulty_score")==total and
               score_band(total)==band==r.get("difficulty_band") and
               r.get("proposed_qrt_cell")==f"QRT-{demand}-{band}"==cell,
               f"source Q{number}: wrong demand band or QRT cell")
        ensure(len(r.get("protected_decision") or "")>=95 and
               len(r.get("agent_justification") or "")>=95 and
               len(r.get("brief_agent_check") or "")>=105 and
               r.get("figure_custody_hold")==
                 {1:"SOURCE_DICE_FIGURES_RIGHTS_NOT_REVIEWED",
                  3:"SOURCE_RADIAL_NUMBER_DIAGRAM_RIGHTS_NOT_REVIEWED",
                  5:"SOURCE_PARALLEL_LINE_FIGURE_RIGHTS_NOT_REVIEWED"}[number] and
               r.get("prior_record_status")==(
                   "OLD_PILOT_FIGURE_GEOMETRY_PENDING_NEW_AGENT_PROOF_AVAILABLE"
                   if number==5 else
                   "NEW_SAMPLE_DISCOVERED_OUTSIDE_ORIGINAL_66_SEED") and
               r.get("independent_human_academic_review_requirement")==
                   "NOT_APPLICABLE_PER_OWNER_DIRECTIVE" and
               r.get("question_qrt_acceptance_status")=="PROPOSED_NOT_ACCEPTED" and
               r.get("source_reproduction_rights_status")=="NOT_REVIEWED" and
               r.get("accepted_qrt_cell") is None and
               r.get("core_eligible") is False,
               f"source Q{number}: incomplete math case or approval without evidence")
        ensure(not(set(r)&{"stem","options","source_diagram_image","original_pdf_bytes"}),
               f"source Q{number}: original copyrighted source content copied")
        seen.add(number);candidate_cells.add(cell)
    ensure(seen==set(EXPECTED) and len(candidate_cells)==7 and
           set(r["sample_question_number"] for r in old_proposed)|seen==set(range(1,11)),
           "ten-source QRT proposal coverage or cell census incorrect")
    return {"result":"TEN_SAMPLE_QRT_PROPOSALS_OWNER_NO_HUMAN_REVIEW",
            "source_sample_positions_with_proposals":10,"unique_provisional_qrt_cells":7,
            "new_provisional_proposals":3,"independent_human_review_required":False,
            "rights_granted":False,"qrt_accepted_cells":0,"core_ready":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--policy",type=Path,default=POLICY)
    p.add_argument("--overlay",type=Path,default=OVERLAY)
    a=p.parse_args()
    try:
        print(json.dumps(validate_owner_sample_qrt(a.policy,a.overlay),sort_keys=True))
    except SeedError as exc:
        p.exit(1,f"IMO_OWNER_QRT_INVALID: {exc}\n")


if __name__=="__main__":
    main()
