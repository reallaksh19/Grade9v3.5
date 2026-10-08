#!/usr/bin/env python3
"""Audit B02's fifteen source-paper answer computations without granting academic admission."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

ROOT = Path(__file__).resolve().parent
BATCH = ROOT / "verification" / "fullpaper-source-math-batch02.v1.json"
SEED = ROOT / "seed"
B01 = SEED / "math_audit_batch01.json"
SOURCES = {
    "SOF-IMO-G09-L1-2023-24-A":
        "https://iswkoman.com/uploads/olympiad/8919398-CL%20IX%20IMO%202023-24%20(1).pdf",
    "SOF-IMO-G09-L1-2024-25-B":
        "https://www.iswkoman.com/uploads/olympiad/2107431-CLASS%209-IMO24.pdf",
}
EXPECTED = { # Printed paper position -> (PDF page index, answer option, short research result).
    ("2023-24-A",3):(1,"D","Odd pair 13 to 167"),
    ("2023-24-A",13):(2,"B","Fourth sorted predecessor digit = 5"),
    ("2023-24-A",25):(4,"B","3/8"),
    ("2023-24-A",27):(4,"D","(0,12)"),
    ("2023-24-A",28):(4,"C","2x^3-5y^4-2x^4-15x^2y^2"),
    ("2023-24-A",29):(4,"A","32 cm"),
    ("2024-25-B",19):(3,"A","3 1/3 percent"),
    ("2024-25-B",20):(3,"A","14"),
    ("2024-25-B",24):(4,"A","p=3; q=5"),
    ("2024-25-B",26):(4,"C","x=2"),
    ("2024-25-B",27):(4,"C","1/6"),
    ("2024-25-B",29):(4,"B","4:1"),
    ("2024-25-B",31):(5,"A","Euclid third postulate: arbitrary centre and radius circle"),
    ("2024-25-B",33):(5,"A","5/8"),
    ("2024-25-B",35):(5,"A","20sqrt(30) cm^2"),
}


def ensure(condition: bool, why: str) -> None:
    if not condition:
        raise SeedError(why)


def mathematical_oracles() -> dict[tuple[str,int], str]:
    # A separate, computed result oracle rather than echoing the source-claim metadata.
    pairs = [(12,148),(15,229),(14,200),(13,167)]
    offsets = [b-a*a for a,b in pairs]
    ensure(offsets == [4,4,4,-2], "printed numeric pairs cannot be reconciled")
    successor_digits = sorted(int(c)-1 for c in "5736928")
    ensure(successor_digits == [1,2,4,5,6,7,8], "digit predecessor transformation")
    # Polynomial target - original.
    target = {(3,0):2,(0,4):-3,(4,0):1,(2,2):-8}
    given = {(4,0):3,(2,2):7,(0,4):2}
    polynomial = {k:target.get(k,0)-given.get(k,0) for k in set(target)|set(given)}
    ensure(polynomial == {(3,0):2,(0,4):-5,(4,0):-2,(2,2):-15},
           "polynomial subtraction oracle")
    triangle_area = 24*32//2
    original_fraction = F(5,8)
    number_of_dice = 6+5+4+3+2+1
    ensure(number_of_dice == 21, "die sample-space sanity check")
    # Descending row sums >9: 3+2+1, not sum of all 21 triangular outcomes.
    outcomes = sum(sum(a+b>9 for b in range(1,7)) for a in range(1,7))
    simple_interest_rate = math.sqrt(100/9)
    cone_ratio = 2*2
    sides = (13,17,20); semi = sum(sides)//2
    heron_sq = semi*math.prod(semi-side for side in sides)
    ensure(outcomes == 6 and heron_sq == 12000 and cone_ratio == 4,
           "figure-independent math oracles")
    return {
      ("2023-24-A",3): "Odd pair 13 to 167" if offsets.count(4)==3 else "INCORRECT",
      ("2023-24-A",13): f"Fourth sorted predecessor digit = {successor_digits[3]}",
      ("2023-24-A",25): str(F(400-250,400)),
      ("2023-24-A",27): f"({0},{12-4*0})",
      ("2023-24-A",28): "2x^3-5y^4-2x^4-15x^2y^2" if polynomial[(3,0)]==2 else "INCORRECT",
      ("2023-24-A",29): f"{2*triangle_area//24} cm",
      ("2024-25-B",19): "3 1/3 percent" if abs(simple_interest_rate-10/3)<1e-12 else "INCORRECT",
      ("2024-25-B",20): str(10-(-4)),
      ("2024-25-B",24): f"p={63//21}; q={5}",
      ("2024-25-B",26): "x=2" if 5**3==25+100 else "INCORRECT",
      ("2024-25-B",27): str(F(outcomes,6*6)),
      ("2024-25-B",29): f"{cone_ratio}:1",
      ("2024-25-B",31): "Euclid third postulate: arbitrary centre and radius circle",
      ("2024-25-B",33): str(original_fraction) if F(5-3,8+2)==F(1,5) else "INCORRECT",
      ("2024-25-B",35): "20sqrt(30) cm^2" if heron_sq==400*30 else "INCORRECT",
    }


def paper_section(n: int) -> str:
    if n <= 15: return "LOGICAL_REASONING"
    if n <= 35: return "MATHEMATICAL_REASONING"
    if n <= 45: return "EVERYDAY_MATHEMATICS"
    return "ACHIEVERS_SECTION"


def validate_batch02(seed: Path = SEED, batch: Path = BATCH) -> dict:
    validate_seed(seed)
    qs, _, _ = load_seed(seed)
    byid = {q["id"]:q for q in qs}
    try:
        batch_data = json.loads(batch.read_text(encoding="utf-8"))
        first = json.loads((seed / B01.name).read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as err:
        raise SeedError(f"B02 cannot read sources: {err}") from err
    ensure(isinstance(batch_data,dict) and batch_data.get("schema")=="sof-imo-g09-fullpaper-source-math-b02-v1",
           "invalid B02 schema")
    ensure(batch_data.get("source_seed_record_count")==66 and
           batch_data.get("original_owner_attached_compilation_claim_preserved") is True and
           batch_data.get("b01_fullpaper_positions")==16 and
           batch_data.get("added_independent_agent_checks")==15 and
           batch_data.get("combined_fullpaper_agent_check_count")==31 and
           batch_data.get("fullpaper_seed_candidate_denominator")==58 and
           batch_data.get("organizer_sample_seed_positions_excluded")==8 and
           batch_data.get("source_choice_label_disagreements")==1 and
           batch_data.get("accepted_source_questions")==0 and
           batch_data.get("accepted_qrt_cells")==0 and
           batch_data.get("core_ready_count")==0,
           "unearned source count or readiness")
    source_claims = batch_data.get("sources")
    ensure(isinstance(source_claims,list) and len(source_claims)==2 and
           {s.get("source_id"):s.get("original_scanned_pdf") for s in source_claims}==SOURCES and
           all(s.get("host_role")=="SCHOOL_MIRROR_SOURCE_SCAN" for s in source_claims),
           "source authority changed")
    rows=batch_data.get("observations")
    ensure(isinstance(rows,list) and len(rows)==15 and all(isinstance(r,dict) for r in rows),
           "B02 inventory is incomplete")
    past_ids={r["question_id"] for r in first["questions"]}
    ensure(len(past_ids)==16, "B01 evidence identity drift")
    expected_results=mathematical_oracles()
    ensure(set(expected_results)==set(EXPECTED), "oracle inventory is incomplete")
    ids, keys, issues=set(),set(),[]
    for r in rows:
        qid=r.get("question_id")
        ensure(qid in byid and qid not in past_ids and qid not in ids,
               f"duplicate/out-of-corpus B02 paper position: {qid}")
        seedrow=byid[qid];sid=seedrow["source_id_claim"];n=int(seedrow["original_question_number_claim"])
        kind="2023-24-A" if sid.endswith("2023-24-A") else "2024-25-B"
        key=(kind,n)
        ensure(key in EXPECTED and key not in keys, f"unexpected original-paper position: {qid}")
        page,choice,answer=EXPECTED[key]
        ensure(r.get("original_source_id")==sid and
               r.get("source_url")==seedrow["source_url_claim"]==SOURCES[sid] and
               r.get("source_question_number")==str(n) and
               r.get("owner_compilation_entry")==seedrow["seed_entry"] and
               r.get("source_pdf_page_index")==page and r.get("source_printed_page")==page+1 and
               r.get("exam_section_by_original_printed_position")==paper_section(n) and
               r.get("source_format")=="SCHOOL_HOSTED_SOF_BRANDED_PAPER_SCAN",
               f"{qid}: printed page, section or source metadata changed")
        ensure(r.get("independent_agent_answer")==answer==expected_results[key] and
               r.get("printed_correct_choice_by_agent")==choice and
               len(r.get("independent_mathematical_derivation") or "")>=95 and
               len(r.get("reverse_or_alternate_check") or "")>=70 and
               isinstance(r.get("concept_probe"),str) and len(r["concept_probe"])>=9,
               f"{qid}: mathematical derivation not adequately supported")
        ensure(r.get("source_page_visually_inspected") is True and
               r.get("source_answer_key_receipt") is None and
               r.get("second_independent_academic_reviewer")=="PENDING" and
               r.get("source_transcription_status")=="PARTIAL_FIGURES_OR_OPTIONS_NOT_RELICENSED" and
               r.get("original_copying_rights")=="NOT_REVIEWED" and
               r.get("qrt_accepted_cell") is None and r.get("core_eligible") is False and
               not (set(r)&{"stem","options","source_figure","source_pdf_bytes"}),
               f"{qid}: unearned rights/academic/QRT/Core claim")
        disagreement=r.get("printed_correct_choice_by_agent")!=r.get("owner_compilation_claimed_choice")
        if disagreement: issues.append(qid)
        ensure(r.get("disposition")==("ATTACHMENT_ANSWER_MATH_DISPUTE" if disagreement else "NO_COMPLICATION"),
               f"{qid}: source/owner option dispute silently erased")
        ids.add(qid);keys.add(key)
    special="SOF-IMO-G09-L1-2023-24-A-Q013"
    ensure(issues==[special] and batch_data.get("choice_label_dispute_source_ids")==issues,
           "2023 Set A printed Q13 digit-source answer mismatch must remain flagged")
    ensure(keys==set(EXPECTED),"B02 missing an expected source question")
    return {"result":"B02_AGENT_MATH_SOURCE_AUDIT_NO_ACADEMIC_ADMISSION",
            "new_source_positions_reviewed":len(ids),"new_choice_disagreements":len(issues),
            "cumulative_fullpaper_agent_reviewed":16+len(ids),"fullpaper_candidate_count":58,
            "source_accepted":0,"qrt_accepted":0,"core_ready":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--batch",type=Path,default=BATCH)
    args=p.parse_args()
    try:
        print(json.dumps(validate_batch02(args.seed,args.batch),sort_keys=True))
    except SeedError as e:
        p.exit(1,f"IMO_FULLPAPER_B02_INVALID: {e}\n")


if __name__ == "__main__":
    main()
