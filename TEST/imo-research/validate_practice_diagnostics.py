#!/usr/bin/env python3
"""Research-only structured diagnostic certificates for seven original Grade 9 tasks."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from validate_seed import SeedError
from validate_original_practice import validate_original_practice

ROOT=Path(__file__).resolve().parent
DATA=ROOT/"original-practice"/"diagnostics"/"structured-checker-cases.v1.json"
PRACTICE=ROOT/"original-practice"/"seven-cell-original-problems.v1.json"
HEAD="1caa71fc3deda2fbff70bed40f0a092a13457bff"
CODES={
    1:("EXAMPLE_ONLY","MISSING_THREE_FACTOR"),
    2:("AXES_SWAPPED","WEST_SIGN","NORTH_SIGN"),
    3:("TRIANGLE_HALF_FACTOR","EQUAL_HEIGHT_NOT_RECOGNIZED","SLANTED_HEIGHT"),
    4:("END_CAPS_INCLUDED","MISSING_CIRCUMFERENCE_FACTOR"),
    5:("DELTA_X_IGNORED","TARGET_SIGN","INTERCEPT_MISREAD"),
    6:("UNIT_PRICES_SWAPPED","TARGET_TOTAL_MISCOMPUTED"),
    7:("REFLECTION_TRANSLATION_MISORDER","AREA_NOT_PRESERVED",
       "DETERMINANT_HALF_FACTOR"),
}
FIELDS={
    1:{"claim_true","even_factor","factor_three","proof_basis"},
    2:{"x","y"},
    3:{"equal_area","area_cm2","used_perpendicular_height"},
    4:{"surface_scope","area_cm2"},
    5:{"slope","intercept","target_x"},
    6:{"booklet_rupees","card_rupees","target_total_rupees"},
    7:{"vertices","twice_area","area_preserved"},
}
CONTRACT_FIELDS={"product_owner_decision":None,"qrt_acceptance":None,
                 "core_ready":False,"learner_published":False,
                 "grading_admission":"RESEARCH_ONLY_NOT_LIVE",
                 "accessibility_readability_signoff":"NOT_COMPLETED"}


def ensure(ok: bool,why: str) -> None:
    if not ok:raise SeedError(why)


def number(v: object) -> bool:
    return type(v) in (int,float) and math.isfinite(v)


def coords_ok(v: object) -> bool:
    return (isinstance(v,dict) and set(v)=={"P","Q","R"} and
            all(isinstance(v[k],list) and len(v[k])==2 and
                all(number(z) for z in v[k]) for k in ("P","Q","R")))


def diagnose(n: int,response: object) -> str:
    """Evaluate structured sample certificates; never parse free-form reasoning."""
    if n not in FIELDS or not isinstance(response,dict) or set(response)!=FIELDS[n]:
        return "INVALID_STRUCTURE"
    if n==1:
        if (any(type(response[k]) is not bool for k in
                ("claim_true","even_factor","factor_three")) or
            not isinstance(response["proof_basis"],str)):
            return "INVALID_STRUCTURE"
        if response["proof_basis"]=="example_only":
            return "EXAMPLE_ONLY"
        if not response["factor_three"]:
            return "MISSING_THREE_FACTOR"
        return ("PASS" if response["claim_true"] and response["even_factor"] and
                response["factor_three"] and
                response["proof_basis"] in ("parity_and_mod3","residue_mod6")
                else "PROOF_CERT_MISSING")
    if n==2:
        if not all(number(response[k]) for k in ("x","y")):
            return "INVALID_STRUCTURE"
        x,y=response["x"],response["y"]
        if (x,y)==(-4,3): return "PASS"
        if (x,y)==(3,-4): return "AXES_SWAPPED"
        if (x,y)==(4,3): return "WEST_SIGN"
        if (x,y)==(-4,-3): return "NORTH_SIGN"
        return "COORDINATE_MISMATCH"
    if n==3:
        if (type(response["equal_area"]) is not bool or
            type(response["used_perpendicular_height"]) is not bool or
            not number(response["area_cm2"])):
            return "INVALID_STRUCTURE"
        if response["area_cm2"]==84:return "TRIANGLE_HALF_FACTOR"
        if not response["equal_area"]:return "EQUAL_HEIGHT_NOT_RECOGNIZED"
        if not response["used_perpendicular_height"]:return "SLANTED_HEIGHT"
        return "PASS" if response["area_cm2"]==42 else "TRIANGLE_AREA_MISMATCH"
    if n==4:
        if not isinstance(response["surface_scope"],str) or not number(response["area_cm2"]):
            return "INVALID_STRUCTURE"
        if response["surface_scope"]!="curved_only":return "END_CAPS_INCLUDED"
        if response["area_cm2"]==440:return "MISSING_CIRCUMFERENCE_FACTOR"
        return "PASS" if response["area_cm2"]==880 else "CURVED_AREA_MISMATCH"
    if n==5:
        if not all(number(response[k]) for k in ("slope","intercept","target_x")):
            return "INVALID_STRUCTURE"
        m,b,x=(response[k] for k in ("slope","intercept","target_x"))
        if m==-4:return "DELTA_X_IGNORED"
        if b!=5:return "INTERCEPT_MISREAD"
        if x==-7:return "TARGET_SIGN"
        return "PASS" if (m,b,x)==(-2,5,7) else "AFFINE_RELATION_MISMATCH"
    if n==6:
        if not all(number(response[k]) for k in
                   ("booklet_rupees","card_rupees","target_total_rupees")):
            return "INVALID_STRUCTURE"
        b,c,cost=(response[k] for k in
                  ("booklet_rupees","card_rupees","target_total_rupees"))
        if (b,c)==(29,18):return "UNIT_PRICES_SWAPPED"
        if (b,c)==(18,29) and cost!=112:return "TARGET_TOTAL_MISCOMPUTED"
        return "PASS" if (b,c,cost)==(18,29,112) else "INVOICE_MODEL_MISMATCH"
    if (not coords_ok(response["vertices"]) or
        not number(response["twice_area"]) or
        type(response["area_preserved"]) is not bool):
        return "INVALID_STRUCTURE"
    vertices=response["vertices"]
    if vertices!={"P":[6,-1],"Q":[1,-1],"R":[4,2]}:
        return "REFLECTION_TRANSLATION_MISORDER"
    if not response["area_preserved"]:return "AREA_NOT_PRESERVED"
    if response["twice_area"]==30:return "DETERMINANT_HALF_FACTOR"
    return "PASS" if response["twice_area"]==15 else "TWICE_AREA_MISMATCH"


def validate_diagnostics(data_path: Path=DATA,
                         practice_path: Path=PRACTICE) -> dict:
    validate_original_practice(file=practice_path)
    try:
        d=json.loads(data_path.read_text(encoding="utf-8"))
        practice=json.loads(practice_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise SeedError(f"practice diagnostic data unreadable: {e}") from e
    ensure(isinstance(d,dict) and
           d.get("schema")=="sof-imo-g09-original-practice-structured-diagnostics-v1" and
           d.get("issue")==277 and d.get("source_pr_merged")==270 and
           d.get("source_original_content_head")==HEAD and
           d.get("source_path")==
               "TEST/imo-research/original-practice/seven-cell-original-problems.v1.json" and
           d.get("scope")=="STRUCTURED_RESEARCH_CHECKER_NOT_PUBLIC_FREE_TEXT_GRADER" and
           d.get("human_independent_academic_review_required") is False and
           d.get("original_sof_stems_options_figures_included") is False and
           d.get("grading_coverage")=="POSITIVE_AND_INTENDED_MISCONCEPTION_TEST_CASES_ONLY" and
           isinstance(d.get("explicit_limit"),str) and
           "cannot reliably automatically score arbitrary proof prose" in d["explicit_limit"],
           "source attribution, owner waiver or diagnostic limitations fabricated")
    counts={"provisional_qrt_cells":7,"accepted_qrt_cells":0,
            "core_2_ready":0,"core_1a_ready":0,"learner_published":0}
    ensure(all(type(d.get(k)) is int and d[k]==v for k,v in counts.items()),
           "research-only provisional/canonical source status inflated")
    practice_by_id={r["id"]:r for r in practice["records"]}
    rows=d.get("records")
    ensure(isinstance(rows,list) and len(rows)==7 and
           all(isinstance(x,dict) for x in rows),
           "seven structured research diagnostic packets mandatory")
    seen=set();mistake_count=0
    for i,row in enumerate(rows,start=1):
        qid=f"IMO-G9-ORIGINAL-PRACTICE-{i:03d}"
        source=practice_by_id.get(qid)
        ensure(source is not None and row.get("candidate_id")==qid and qid not in seen and
               row.get("proposed_qrt_cell")==source["qrt_proposal"]["cell"],
               f"{qid}: source-original question/qrt identity mismatch")
        ensure(set(row.get("response_fields",[]))==FIELDS[i] and
               len(row.get("response_fields",[]))==len(FIELDS[i]),
               f"{qid}: duplicate, missing or unsupported structured answer fields")
        for field,value in CONTRACT_FIELDS.items():
            ensure(row.get(field)==value,
                   f"{qid}: unearned product/Core/QRT/accessibility acceptance: {field}")
        ensure(isinstance(row.get("grader_limit"),str) and
               len(row["grader_limit"])>=72 and
               diagnose(i,row.get("accepted_illustrative_response"))=="PASS" and
               diagnose(i,row.get("equivalent_illustrative_response"))=="PASS",
               f"{qid}: correct/equivalent answer or grader limitation mismatch")
        wrong=row.get("misconception_probes")
        ensure(isinstance(wrong,list) and
               len(wrong)==len(CODES[i]) and
               [m.get("code") for m in wrong]==list(CODES[i]),
               f"{qid}: required misconception classes lost or duplicated")
        for m in wrong:
            ensure(isinstance(m.get("actionable_hint"),str) and
                   len(m["actionable_hint"])>=65 and
                   diagnose(i,m.get("response"))==m["code"],
                   f"{qid}: misconception no longer deterministically diagnosed")
            mistake_count+=1
        ensure(not(set(row)&{"sof_stem","sof_options","sof_diagram",
                             "published_question","auto_accepted_qrt"}),
               f"{qid}: original SOF content or automatic product acceptance injected")
        seen.add(qid)
    ensure(len(seen)==7 and mistake_count==18,
           "item and diagnostic coverage census must be exact")
    return {"result":"SEVEN_STRUCTURED_RESEARCH_DIAGNOSTIC_PACKETS_NOT_LIVE",
            "question_count":7,"distinct_provisional_qrt_cells":7,
            "targeted_misconception_probes":mistake_count,
            "human_academic_signoff_required":False,
            "accepted_qrt_cells":0,"core_ready":0,"learner_published":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--diagnostics",type=Path,default=DATA)
    p.add_argument("--practice",type=Path,default=PRACTICE)
    a=p.parse_args()
    try:print(json.dumps(validate_diagnostics(a.diagnostics,a.practice),sort_keys=True))
    except SeedError as e:p.exit(1,f"IMO_DIAGNOSTICS_INVALID: {e}\n")


if __name__=="__main__":
    main()
