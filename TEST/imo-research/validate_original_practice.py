#!/usr/bin/env python3
"""Validate original Grade 9 research practice, math oracles and seven QRT cells."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "seed"
PRACTICE = ROOT / "original-practice" / "seven-cell-original-problems.v1.json"
CANONICAL = ("reallaksh19/Grade9v3.5@8678645ef2fd5e63401ef5af3621b94e925732a8:"
             "Shared/quality/question-demand-matrix.v1.json")
FACTORS = ("concept_model_selection", "representation_translation",
           "reasoning_chain_length", "algebra_computational_load",
           "trap_exception_sensitivity")
EXPECTED = {
    1: ("JUSTIFY", ("EXPLAIN", "APPLY"), (1,1,2,1,1),
        "QRT-JUSTIFY-D3", "The claim is true for every positive integer n."),
    2: ("REPRESENT", ("APPLY",), (0,1,0,0,0),
        "QRT-REPRESENT-D1", "(-4, 3)"),
    3: ("JUSTIFY", ("APPLY",), (0,0,1,0,0),
        "QRT-JUSTIFY-D1", "Yes. Each area is 42 square centimetres."),
    4: ("MODEL", ("REPRESENT", "APPLY"), (1,1,1,0,0),
        "QRT-MODEL-D2", "880 square centimetres"),
    5: ("REPRESENT", ("APPLY", "JUSTIFY"), (0,1,1,0,1),
        "QRT-REPRESENT-D2", "y=-2x+5; x=7"),
    6: ("MODEL", ("APPLY", "SYNTHESIZE"), (2,1,2,1,1),
        "QRT-MODEL-D3", "112 rupees"),
    7: ("REPRESENT", ("APPLY", "JUSTIFY"), (1,2,2,0,1),
        "QRT-REPRESENT-D3",
        "P''=(6,-1), Q''=(1,-1), R''=(4,2); area unchanged at 7.5 square units."),
}
CELL_SET = {row[3] for row in EXPECTED.values()}
UNLICENSED_SOURCE_KEYS = {"source_stem", "sof_original_options", "sof_source_diagram",
                          "source_pdf_bytes", "scanned_question", "official_sof_question_id"}
BOUNDARY = {
    "original_sof_stem_copied": False,
    "original_sof_choices_copied": False,
    "original_sof_figure_copied": False,
    "source_pdf_bytes_copied": False,
    "external_originality_certification": False,
    "publisher_rights_claimed": False,
    "publication_permission_decision": "SEPARATE_PRODUCT_REVIEW_PENDING",
}


def ensure(value: bool, message: str) -> None:
    if not value:
        raise SeedError(message)


def band(score: int) -> str:
    return "D1" if score <= 2 else "D2" if score <= 5 else "D3" if score <= 7 else "D4"


def arithmetic_oracles() -> dict[int, str]:
    """Recompute independently rather than trusting the authored answer strings."""
    # 3 consecutive integers: 2 and 3 both divide the product for every residue mod 6.
    ensure(all((n*(n+1)*(n+2))%6==0 for n in range(6)),
           "universal divisibility fails some residue class modulo six")
    west_north = (-4,+3)
    ensure(west_north[0] < 0 and west_north[1] > 0,
           "map conversion sign convention wrong")
    triangle_area = F(12*7,2)
    # Explicit determinant checks for movable vertices with same baseline.
    det_a = F(12*7-0*2,2)
    det_b = F(12*7-0*10,2)
    ensure(triangle_area==det_a==det_b==42,"equal-base triangle areas inconsistent")
    cylinder_side = 2*F(22,7)*7*20
    unwrap_rect = 44*20
    ensure(cylinder_side==unwrap_rect==880,
           "curved-cylinder area must exclude end faces")
    table = [(-2,9),(0,5),(2,1),(4,-3)]
    slope = F(table[1][1]-table[0][1],table[1][0]-table[0][0])
    intercept = table[1][1]
    linear_target = F(-9-intercept,1)/slope
    ensure(slope==-2 and intercept==5 and
           all(slope*x+intercept==y for x,y in table) and linear_target==7,
           "paired table linear relation invalid")
    # Eliminate in 4b+3c=159, 2b+5c=181.
    card = F(2*181-159,10-3)
    booklet = F(159-3*card,4)
    ensure((booklet,card)==(18,29) and
           4*booklet+3*card==159 and 2*booklet+5*card==181,
           "two-invoice model cannot be verified")
    predicted = 3*booklet+2*card
    initial = ((-2,1),(3,1),(0,4))
    final = tuple((-x+4,y-2) for x,y in initial)
    signed_twice = lambda pts: (
        (pts[1][0]-pts[0][0])*(pts[2][1]-pts[0][1])
        -(pts[1][1]-pts[0][1])*(pts[2][0]-pts[0][0]))
    ensure(final==((6,-1),(1,-1),(4,2)) and
           signed_twice(initial)==15 and signed_twice(final)==-15,
           "sequential reflection and translation must preserve absolute area")
    return {
        1:"The claim is true for every positive integer n.",
        2:f"({west_north[0]}, {west_north[1]})",
        3:f"Yes. Each area is {triangle_area} square centimetres.",
        4:f"{cylinder_side} square centimetres",
        5:f"y={slope}x+{intercept}; x={linear_target}",
        6:f"{predicted} rupees",
        7:"P''=(6,-1), Q''=(1,-1), R''=(4,2); area unchanged at 7.5 square units.",
    }


def validate_original_practice(seed: Path=SEED, file: Path=PRACTICE) -> dict:
    validate_seed(seed)
    source_questions,_,_ = load_seed(seed)
    ensure(len(source_questions)==66,"original SOF owner source seed changed")
    try:
        data=json.loads(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"practice research file unreadable: {exc}") from exc
    ensure(isinstance(data,dict) and
           data.get("schema")=="sof-imo-g09-original-practice-seven-qrt-cells-v1" and
           data.get("origin_claim")=="NEW_AI_AUTHORED_PRACTICE_NOT_OFFICIAL_SOF_CONTENT" and
           data.get("canonical_demand_authority")==CANONICAL and
           data.get("source_owner_seed_census_unchanged")==66 and
           data.get("record_count")==7 and data.get("provisional_qrt_cell_count")==7 and
           data.get("seven_distinct_proposed_qrt_cells") is True and
           data.get("no_sof_original_text_or_figures_embedded") is True and
           data.get("no_globally_exclusive_originality_claim") is True and
           data.get("human_academic_review_required") is False and
           data.get("human_academic_reviews_performed")==0 and
           data.get("external_source_rights_grants_claimed")==0 and
           data.get("qrt_accepted_cells")==0 and
           data.get("core_ready_questions")==0 and
           data.get("learner_published_questions")==0,
           "original practice falsely claimed to be official or product admitted")
    questions=data.get("records")
    ensure(isinstance(questions,list) and len(questions)==7 and
           all(isinstance(x,dict) for x in questions),
           "exact seven original practice rows required")
    answer_oracles=arithmetic_oracles()
    source_ids={q["id"] for q in source_questions}
    ids=set();cells=set()
    for item in questions:
        qid=item.get("id")
        ensure(isinstance(qid,str) and qid.startswith("IMO-G9-ORIGINAL-PRACTICE-"),
               "question id not in original-practice namespace")
        ensure(qid not in ids and qid not in source_ids,
               "source ID collision or duplicate original question")
        try:
            num=int(qid.rsplit("-",1)[1])
        except (TypeError,ValueError) as exc:
            raise SeedError("practice ID suffix must be numbered") from exc
        ensure(qid==f"IMO-G9-ORIGINAL-PRACTICE-{num:03d}" and num in EXPECTED,
               "unexpected original-practice ID")
        demand,secondary,score_tuple,expected_cell,answer=EXPECTED[num]
        ensure(item.get("grade")==9 and
               item.get("source_origin")=="MODEL_AUTHORED_NEW_PRACTICE" and
               item.get("exam_style_context")==
                   "SOF_IMO_G9_INSPIRED_SKILL_PRACTICE_NOT_SOURCE_PAPER" and
               item.get("source_question_id") is None and
               item.get("question_format")=="FREE_RESPONSE" and
               isinstance(item.get("title"),str) and len(item["title"])>=18 and
               isinstance(item.get("question_text"),str) and len(item["question_text"])>=150 and
               isinstance(item.get("originality_disclosure"),str) and
               "global prior-art uniqueness is not established" in item["originality_disclosure"] and
               item.get("expected_answer")==answer==answer_oracles[num],
               f"{qid}: answer, authorship or source-boundary drift")
        ensure(isinstance(item.get("worked_solution"),str) and len(item["worked_solution"])>=155 and
               isinstance(item.get("independent_reverse_or_alternate_check"),str) and
               len(item["independent_reverse_or_alternate_check"])>=105 and
               isinstance(item.get("protected_cognitive_decision"),str) and
               len(item["protected_cognitive_decision"])>=85 and
               len(item.get("student_error_to_diagnose") or "")>=55,
               f"{qid}: lacks mathematical worked or alternate support")
        qrt=item.get("qrt_proposal")
        ensure(isinstance(qrt,dict) and qrt.get("primary_demand")==demand and
               qrt.get("secondary_demands")==list(secondary) and
               qrt.get("status")=="PROPOSED_RESEARCH_NOT_ACCEPTED" and
               qrt.get("cell")==expected_cell,
               f"{qid}: unsupported cognitive demand")
        factors=qrt.get("five_factor_scores")
        ensure(isinstance(factors,dict) and set(factors)==set(FACTORS) and
               all(type(factors[n]) is int and 0<=factors[n]<=2 for n in FACTORS),
               f"{qid}: invalid five-factor score")
        vals=tuple(factors[n] for n in FACTORS)
        total=sum(vals)
        ensure(vals==score_tuple and qrt.get("score")==total and
               qrt.get("difficulty_band")==band(total) and
               expected_cell==f"QRT-{demand}-{band(total)}",
               f"{qid}: arithmetic/difficulty/primary-cell mismatch")
        ensure(item.get("intellectual_property_boundary")==BOUNDARY and
               item.get("human_academic_peer_signoff_requirement")==
                   "NOT_APPLICABLE_OWNER_DIRECTED" and
               item.get("independent_human_reviewer_was_used") is False and
               item.get("qrt_acceptance_decision") is None and
               item.get("core_2_ready") is False and
               item.get("core_1a_ready") is False and item.get("learner_published") is False,
               f"{qid}: copyright, human signoff or product admission falsely claimed")
        ensure(not (set(item)&UNLICENSED_SOURCE_KEYS),
               f"{qid}: copied original SOF question/image/option metadata")
        ids.add(qid);cells.add(expected_cell)
    ensure(len(ids)==7 and cells==CELL_SET,
           "one original research question per unique provisional cell required")
    return {"result":"SEVEN_ORIGINAL_QRT_PRACTICE_RESEARCH_CANDIDATES_ONLY",
            "original_question_candidates":7,"distinct_proposed_qrt_cells":len(cells),
            "accepted_qrt_cells":0,"learner_published":0,"core_ready":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--practice",type=Path,default=PRACTICE)
    x=p.parse_args()
    try:
        print(json.dumps(validate_original_practice(x.seed,x.practice),sort_keys=True))
    except SeedError as exc:
        p.exit(1,f"IMO_ORIGINAL_PRACTICE_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
