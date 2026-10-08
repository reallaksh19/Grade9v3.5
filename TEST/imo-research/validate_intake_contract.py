#!/usr/bin/env python3
"""Fail-closed admission contract for planned original (not SOF-source) G9 practice."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

HERE=Path(__file__).resolve().parent
DATA=HERE/"intake"/"original-practice-intake-contract.v1.json"
SEED=HERE/"seed"
CELLS=(
 "QRT-JUSTIFY-D3","QRT-REPRESENT-D1","QRT-JUSTIFY-D1",
 "QRT-MODEL-D2","QRT-REPRESENT-D2","QRT-MODEL-D3","QRT-REPRESENT-D3",
)
TOPICS=(
 "universal divisibility reasoning","signed Cartesian coordinate translation",
 "equal base/altitude triangle area","curved cylinder surface model",
 "linear table relation and inversion","two-variable invoice modelling",
 "ordered coordinate transformation and invariant",
)
GATES=("UPSTREAM_RESEARCH_QUALIFIED","MATHEMATICAL_CORRECTNESS",
       "SOURCE_INDEPENDENCE","QRT_PRODUCT_DECISION",
       "LEARNER_QUALITY","PRODUCT_OWNER_AUTHORIZATION")
EVIDENCE=[
 "EXACT_CANDIDATE_HEAD_CI_SUCCESS","SOURCE_INDEPENDENCE_CONTENT_CHECK",
 "MATH_ORACLE_RESULT","QRT_CELL_PRODUCT_DECISION",
 "LANGUAGE_AND_FEEDBACK_QA","OWNER_CONTENT_ADMISSION_DECISION",
]


def ensure(ok: bool, reason: str) -> None:
    if not ok: raise SeedError(reason)


def validate_contract(seed: Path=SEED, contract: Path=DATA) -> dict:
    validate_seed(seed)
    originals,_,_=load_seed(seed)
    original_ids={q["id"] for q in originals}
    try:
        d=json.loads(contract.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise SeedError(f"original-practice intake unreadable: {e}") from e
    ensure(isinstance(d,dict) and
           d.get("schema")=="sof-imo-g9-original-practice-intake-contract-v1" and
           d.get("issue")==271 and
           d.get("governing_scope")=="RESEARCH_METADATA_ONLY_NOT_LIVE_CONTENT" and
           d.get("policy_reference")=="OWNER_2026_10_08_HUMAN_ACADEMIC_SIGNOFF_NOT_APPLICABLE" and
           d.get("upstream_draft_pr")==270 and
           d.get("upstream_merge_head_sha") is None and
           d.get("upstream_pr_merge_qualification")=="NOT_YET_VERIFIED" and
           d.get("source_paper_question_reproduction_rights")==
               "DO_NOT_REPRODUCE_ORIGINAL_SOF_SOURCE_CONTENT" and
           d.get("practice_authorship_boundary")==
               "ORIGINAL_AI_AUTHORED_QUESTION_REQUIRES_FINAL_SOURCE_INDEPENDENCE_QA",
           "source authority, admission scope, or upstream merge status overclaimed")
    numeric={
      "source_seed_original_question_count":66,
      "planned_candidate_count":7,
      "planned_distinct_proposed_qrt_cells_count":7,
      "canonical_qrt_accepted_cells":0,
      "product_approved_candidate_count":0,
      "core_2_admitted_count":0,
      "core_1a_admitted_count":0,
      "learner_published_count":0,
    }
    ensure(all(type(d.get(k)) is int and d[k]==v for k,v in numeric.items()),
           "false question census/QRT/Core/learner acceptance")
    ensure(d.get("human_academic_peer_signature_requirement")==
               "NOT_APPLICABLE_OWNER_DIRECTED" and
           d.get("separate_software_qa_required") is True and
           d.get("original_sof_copyright_reuse_not_authorized") is True and
           d.get("automated_ci_is_not_product_owner") is True,
           "owner waiver cannot erase QA, licensing or owner product decision")
    ids=[f"IMO-G9-ORIGINAL-PRACTICE-{i:03d}" for i in range(1,8)]
    ensure(d.get("planned_candidate_ids")==ids and
           not (set(ids)&original_ids), "candidate ID mismatch or source collision")
    guards=d.get("required_gates")
    ensure(isinstance(guards,list) and len(guards)==6 and
           [g.get("gate") for g in guards]==list(GATES) and
           all(g.get("must_not_autofill_from_ci") is True and
               isinstance(g.get("condition"),str) and len(g["condition"])>=70
               for g in guards), "product owner, source or QRT gate silently removed")
    rows=d.get("records")
    ensure(isinstance(rows,list) and len(rows)==7 and all(isinstance(x,dict) for x in rows),
           "one planned intake packet per seven original practice items required")
    observed=set()
    for i,r in enumerate(rows):
        id=ids[i]
        ensure(r.get("candidate_id")==id and id not in observed and
               r.get("expected_proposal_cell")==CELLS[i] and
               r.get("candidate_topic")==TOPICS[i] and
               r.get("upstream_candidate_repository_pr")==270 and
               r.get("record_source_kind")=="FUTURE_LINKED_NEW_AI_AUTHORED_PRACTICE_NOT_SOF_PAPER",
               f"{id}: incorrect source question or provisional matrix cell")
        ensure(r.get("upstream_source_pr_merge_verified") is False and
               r.get("mathematical_oracle_ci_receipt") is None and
               r.get("mathematical_correctness_stage")=="NOT_YET_ADMITTED" and
               all(r.get(field)=="PENDING" for field in
                   ("accessibility_and_wording_review","learner_feedback_and_misconception_review",
                    "grade_9_curriculum_fit_review")),
               f"{id}: unsupported readiness or math/test receipt")
        ensure(r.get("source_originality_boundary")==
                   "NO_SOF_STEM_OPTION_OR_DIAGRAM_COPYING_CLAIMED" and
               r.get("independent_human_academic_signoff_required") is False and
               r.get("qrt_product_admission_decision")=="NOT_REQUESTED" and
               r.get("qrt_acceptance_receipt") is None and
               r.get("qrt_accepted_cell") is None and
               r.get("product_owner_admission_decision")=="NOT_REQUESTED" and
               r.get("product_owner_identity") is None and
               r.get("product_owner_decision_date") is None and
               r.get("core_2_approved") is False and
               r.get("core_1a_approved") is False and
               r.get("learner_published") is False and
               r.get("blocked_next_action")==
                   "NO_LEARNER_PUBLICATION_UNTIL_SEPARATE_QUALIFIED_ADMISSION_PR",
               f"{id}: fabricated owner approval, QRT cell, Core or publication")
        ensure(r.get("requires_future_evidence")==EVIDENCE,
               f"{id}: one required evidence receipt removed")
        ensure(not (set(r)&{"original_sof_stem","sof_option_set","sof_figure",
                             "fake_owner_signature","source_pdf_bytes"}),
               f"{id}: unlicensed source material/fake product authorization")
        observed.add(id)
    ensure(len(observed)==7 and len(set(CELLS))==7,
           "planned seven proposed cells missing/overlapping")
    return {"result":"SEVEN_INTAKE_PACKETS_PREPARED_NO_CONTENT_ADMISSION",
            "source_independent_candidate_slots":7,"separate_required_gates":len(GATES),
            "human_academic_signoff_required":False,"qrt_accepted_cells":0,
            "core_ready":0,"learner_published":0}


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed",type=Path,default=SEED)
    ap.add_argument("--intake",type=Path,default=DATA)
    args=ap.parse_args()
    try:
        print(json.dumps(validate_contract(args.seed,args.intake),sort_keys=True))
    except SeedError as exc:
        ap.exit(1,f"IMO_ORIGINAL_INTAKE_INVALID: {exc}\n")


if __name__=="__main__":
    main()
