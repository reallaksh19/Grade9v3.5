#!/usr/bin/env python3
"""Validate source-vs-attachment differences without treating an audit as academic acceptance."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "seed"
ADJUDICATION = ROOT / "adjudication" / "source-discrepancy-register.v1.json"
B01 = "math_audit_batch01.json"
B02 = "fullpaper-source-math-batch02.v1.json"
SAMPLE = "official-sample-2026-27-math-qrt-pilot.v1.json"
DOCS = {
 "23":("SOF-IMO-G09-L1-2023-24-A","https://iswkoman.com/uploads/olympiad/8919398-CL%20IX%20IMO%202023-24%20(1).pdf","SCHOOL_MIRROR"),
 "24":("SOF-IMO-G09-L1-2024-25-B","https://www.iswkoman.com/uploads/olympiad/2107431-CLASS%209-IMO24.pdf","SCHOOL_MIRROR"),
 "25":("SOF-IMO-G09-L1-2025-26-A","https://www.iswkoman.com/uploads/olympiad/9262492-IMO%2025-26%20CLASS%209.pdf","SCHOOL_MIRROR"),
 "S":("SOF-IMO-G09-SAMPLE-2026-27","https://sofworld.org/download/file/fid/73719","SOF_ORGANIZER_HOSTED_SAMPLE"),
}
# case_id => source doc, source numbers, owner entry, PDF page, source choice, owner choice,
# required discrepancy class, source-observation state.
EXPECTED = {
 "IMO-SOURCE-CONFLICT-001":("23",(13,),(46,),2,"B","C","ANSWER_CALCULATION_DISAGREEMENT","SOURCE_OBSERVED_MATH_AGENT_RECHECKED",False),
 "IMO-SOURCE-CONFLICT-002":("23",(17,),(31,),3,"C","C","DISTRACTOR_OPTION_REPLACEMENT","SOURCE_OPTION_DIFFERENCE_DOCUMENTED",False),
 "IMO-SOURCE-CONFLICT-003":("23",(18,),(1,),3,"C","A","CORRECT_OPTION_REORDERED","SOURCE_OPTION_DIFFERENCE_DOCUMENTED",False),
 "IMO-SOURCE-CONFLICT-004":("24",(16,),(37,),3,"A","A","SOURCE_CHART_DEPENDENCY","SOURCE_FIGURE_CUSTODY_PENDING",True),
 "IMO-SOURCE-CONFLICT-005":("24",(44,),(9,),6,"B","B","EXAM_SECTION_MISLABEL","SOURCE_SECTION_MAPPING_RESOLVED",False),
 "IMO-SOURCE-CONFLICT-006":("25",(28,),(2,),4,"B","C","STEM_SEMANTIC_CHANGE","SOURCE_STEM_DISPUTED_DO_NOT_NORMALIZE",False),
 "IMO-SOURCE-CONFLICT-007":("25",(31,),(22,),4,"C","D","FIGURE_DEPENDENT_ANSWER_DISAGREEMENT","SOURCE_DIAGRAM_MATH_AGENT_RECHECKED",True),
 "IMO-SOURCE-CONFLICT-008":("25",(32,33),(38,),4,"B/B","B/B","MULTIPLE_ORIGINAL_SOURCE_ITEMS_COMBINED","SOURCE_SPLIT_MAPPING_RESOLVED",True),
 "IMO-SOURCE-CONFLICT-009":("S",(5,),(23,),1,"C","C","UNSOLVED_FIGURE_GEOMETRY","DIAGRAM_MATH_PENDING",True),
 "IMO-SOURCE-CONFLICT-010":("S",(9,),(6,),1,"D","D","RADICAL_INDEX_STATEMENT_REWRITTEN","SOURCE_NOTATION_DISPUTED_DO_NOT_NORMALIZE",False),
}

def ensure(ok: bool, reason: str) -> None:
    if not ok:
        raise SeedError(reason)


def mathematical_checks() -> dict[str,str]:
    transformed=sorted(int(x)-1 for x in "5736928")
    ensure(transformed==[1,2,4,5,6,7,8],"digit substitution or sorting incorrect")
    b_plus_c=F(-2,3)+F(1,2)
    inverse=-(F(1,4)-b_plus_c)
    other=F(-16,35)/F(-15,14)
    angle_b=F(180-75,5)
    angle_a=4*angle_b
    angle_c=(75+angle_b)/2
    sample_ratio=(F(1,2)*25)/(F(1000,27)*9)
    ensure((inverse,other,angle_a,angle_b,angle_c,sample_ratio)==
           (F(-5,12),F(32,75),84,21,48,F(3,80)),
           "source-backed math recalc contradiction")
    return {
      "IMO-SOURCE-CONFLICT-001":"5",
      "IMO-SOURCE-CONFLICT-002":"4:9",
      "IMO-SOURCE-CONFLICT-003":"-5/12",
      "IMO-SOURCE-CONFLICT-004":"60",
      "IMO-SOURCE-CONFLICT-005":"4x^4−2x^3+27x^2+4x+11",
      "IMO-SOURCE-CONFLICT-006":"0 if literal identity; −32/75 for changed inverse problem",
      "IMO-SOURCE-CONFLICT-007":"a=84°, b=21°, c=48°",
      "IMO-SOURCE-CONFLICT-008":"Hindi+Social Science 250 marks; Maths 22 2/9%",
      "IMO-SOURCE-CONFLICT-009":None,
      "IMO-SOURCE-CONFLICT-010":"Statement II = 3/80; statement I false; printed choice D",
    }


def validate_register(seed: Path = SOURCE,
                      verify: Path = ROOT / "verification",
                      register: Path = ADJUDICATION) -> dict:
    validate_seed(seed)
    questions, _, _ = load_seed(seed)
    seeds={q["id"]:q for q in questions}
    try:
        ledger=json.loads(register.read_text(encoding="utf-8"))
        b01=json.loads((seed/B01).read_text(encoding="utf-8"))
        b02=json.loads((verify/B02).read_text(encoding="utf-8"))
        sample=json.loads((verify/SAMPLE).read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SeedError(f"adjudication source unreadable: {exc}") from exc
    ensure(isinstance(ledger,dict) and ledger.get("schema")=="sof-imo-g09-source-discrepancy-register-v1",
           "discrepancy register schema missing")
    counts={"original_seed_question_count":66,"original_fullpaper_source_positions_agent_worked":58,
            "separate_organizer_sample_seed_positions":8,"additional_discovered_sample_source_positions":2,
            "case_count":10,"cases_involving_multiple_source_positions":1,
            "printed_fullpaper_official_key_receipts_accepted":0,
            "independent_academic_answers_accepted":0,"rights_approvals":0,
            "qrt_cells_accepted":0,"core_ready":0}
    ensure(all(ledger.get(k)==v for k,v in counts.items()),"source census or acceptance inflated")
    prior={r["question_id"]:r for r in b01["questions"]}
    previous_b02={r["question_id"]:r for r in b02["observations"]}
    sample_records={r["sample_question_number"]:r for r in sample["records"]}
    ensure(len(prior)==16 and len(previous_b02)==15 and len(sample_records)==8,
           "original math/source evidence missing or duplicated")
    cases=ledger.get("cases")
    ensure(isinstance(cases,list) and len(cases)==10 and all(isinstance(x,dict) for x in cases),
           "must cover 10 explicit dispute categories")
    seen,all_qids,had_multi=set(),set(),0
    computed=mathematical_checks()
    for c in cases:
        cid=c.get("case_id")
        ensure(cid in EXPECTED and cid not in seen,f"unknown or repeated case {cid}")
        year,numbers,owners,page,choice,owner_choice,kind,status,figure=EXPECTED[cid]
        source_id,url,host=DOCS[year]
        qids=[f"{source_id}-Q{n:03d}" for n in numbers]
        ensure(c.get("question_ids")==qids and
               c.get("original_source_id")==source_id and
               c.get("original_source_url")==url and
               c.get("source_host_class")==host and
               c.get("source_pdf_page_index")==page and
               c.get("source_numbers")==list(numbers) and
               c.get("owner_compilation_entries")==list(owners),
               f"{cid}: original source locator/owner reference drift")
        for qid in qids:
            ensure(qid in seeds and seeds[qid]["source_id_claim"]==source_id and
                   seeds[qid]["source_url_claim"]==url and
                   seeds[qid]["seed_entry"] in owners,
                   f"{cid}: cannot crosswalk source question {qid}")
            all_qids.add(qid)
        ensure(c.get("conflict_type")==kind and c.get("source_finding_status")==status and
               c.get("printed_option_selection_by_math_or_key")==choice and
               c.get("owner_compilation_option_claim")==owner_choice and
               c.get("agent_mathematical_result")==computed[cid],
               f"{cid}: source/attachment dispute outcome mutated")
        if cid=="IMO-SOURCE-CONFLICT-009":
            ensure(c.get("agent_calculation_recheck") is None,
                   "sample diagram Q5 cannot acquire unsupported worked solution")
        else:
            ensure(isinstance(c.get("agent_calculation_recheck"),str) and
                   len(c["agent_calculation_recheck"])>=60,
                   f"{cid}: missing source-worked independent mathematics")
        ensure(c.get("figure_required") is figure and
               c.get("organizer_sample_key_sighted") is (year=="S") and
               c.get("original_fullpaper_official_key_receipt") is None and
               c.get("independent_academic_acceptance") is False and
               c.get("figure_reuse_rights_status")=="NOT_REVIEWED" and
               c.get("verbatim_source_publication_rights_status")=="NOT_REVIEWED" and
               c.get("source_wording_reconciled_for_learner") is False and
               c.get("accepted_qrt_cell") is None and c.get("core_eligible") is False,
               f"{cid}: source observation promoted without approval")
        ensure(isinstance(c.get("previous_research_evidence_refs"),list) and
               len(c["previous_research_evidence_refs"])>0 and
               all(isinstance(p,str) and p.startswith("TEST/imo-research/") for p in
                   c["previous_research_evidence_refs"]) and
               len(c.get("printed_source_evidence_summary") or "")>=75 and
               len(c.get("owner_compilation_claim_summary") or "")>=50 and
               len(c.get("manual_reviewer_next_step") or "")>=55,
               f"{cid}: incomplete source/owner/reviewer decision packet")
        ensure(not(set(c)&{"stem","options","source_figure_bytes","original_pdf_bytes"}),
               f"{cid}: unlicensed original question text/image stored")
        if len(qids)>1:had_multi+=1
        if cid in {"IMO-SOURCE-CONFLICT-002","IMO-SOURCE-CONFLICT-003",
                   "IMO-SOURCE-CONFLICT-004","IMO-SOURCE-CONFLICT-005",
                   "IMO-SOURCE-CONFLICT-006","IMO-SOURCE-CONFLICT-007",
                   "IMO-SOURCE-CONFLICT-008"}:
            for qid in qids:
                row=prior.get(qid)
                ensure(row is not None and row["math_derived_printed_choice"]==choice.split("/")[qids.index(qid)]
                       and row["compilation_claimed_choice"]==owner_choice.split("/")[qids.index(qid)],
                       f"{cid}: conflicts with source-grounded B01 answer overlay")
        if cid=="IMO-SOURCE-CONFLICT-001":
            r=previous_b02[qids[0]]
            ensure(r["printed_correct_choice_by_agent"]=="B" and
                   r["owner_compilation_claimed_choice"]=="C","B02 Q13 digit correction missing")
        if year=="S":
            s=sample_records[numbers[0]]
            ensure(s["organizer_printed_key"]==choice and s["core_eligible"] is False and
                   s["accepted_qrt_cell"] is None, f"{cid}: sample organizer key or hold changed")
            if numbers[0]==5:
                ensure(s["agent_derived_option"] is None and s["qrt_proposal"] is None,
                       "sample Q5 still an unresolved geometry problem")
            if numbers[0]==9:
                ensure(s["agent_derived_option"]=="D" and
                       s["source_vs_owner_transcription_status"]=="MATERIAL_TRANSCRIPTION_CONFLICT",
                       "source sample radical/index discrepancy erased")
        seen.add(cid)
    ensure(seen==set(EXPECTED) and had_multi==1 and len(all_qids)==11,
           "discrepancy source ledger census not exact")
    return {"result":"SOURCE_DISCREPANCIES_DOCUMENTED_NO_LEARNER_ADMISSION",
            "cases":len(seen),"distinct_source_positions_in_cases":len(all_qids),
            "one_multi_source_case":had_multi,
            "figure_dependent_cases":sum(x["figure_required"] for x in cases),
            "academically_accepted":0,"accepted_qrt_cells":0,"core_ready":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed",type=Path,default=SOURCE)
    p.add_argument("--verification",type=Path,default=ROOT/"verification")
    p.add_argument("--register",type=Path,default=ADJUDICATION)
    x=p.parse_args()
    try:
        print(json.dumps(validate_register(x.seed,x.verification,x.register),sort_keys=True))
    except SeedError as exc:
        p.exit(1,f"IMO_DISCREPANCY_REGISTER_INVALID: {exc}\n")


if __name__=="__main__":
    main()
