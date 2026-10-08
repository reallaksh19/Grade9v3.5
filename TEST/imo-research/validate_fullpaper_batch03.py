#!/usr/bin/env python3
"""Fail closed on B03's 16 scanned-paper AI-worked answers; no academic promotion."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction as F
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

HERE = Path(__file__).resolve().parent
SEED = HERE / "seed"
PILOT = HERE / "verification"
B03 = PILOT / "fullpaper-audit-b03.v1.json"
SOURCE_2023 = "SOF-IMO-G09-L1-2023-24-A"
SOURCE_2024 = "SOF-IMO-G09-L1-2024-25-B"
YEAR_COUNTS = {SOURCE_2023: 15, SOURCE_2024: 1}
LOCATORS = {
    (SOURCE_2023,6):(1,"D","beautiful"),
    (SOURCE_2023,19):(3,"C","Rectangle"),
    (SOURCE_2023,33):(5,"B","Exactly one parallel line"),
    (SOURCE_2023,34):(5,"D","1:4"),
    (SOURCE_2023,35):(5,"A","INR 15300"),
    (SOURCE_2023,36):(5,"A","36/7 days"),
    (SOURCE_2023,37):(5,"D","3/4 of women"),
    (SOURCE_2023,38):(5,"A","-25x+y=700"),
    (SOURCE_2023,39):(5,"B","13 seconds"),
    (SOURCE_2023,40):(5,"C","5/12"),
    (SOURCE_2023,42):(6,"B","INR 10000"),
    (SOURCE_2023,43):(6,"D","36 years"),
    (SOURCE_2023,47):(6,"C","Statement I true; Statement II true"),
    (SOURCE_2023,49):(7,"D","F,F"),
    (SOURCE_2023,50):(7,"C","(-7,5); 5 units; (-6,-3)"),
    (SOURCE_2024,43):(6,"A","4 days"),
}


def ensure(ok: bool, why: str) -> None:
    if not ok:
        raise SeedError(why)


def arithmetic_oracles() -> dict[tuple[str,int],str]:
    # Deliberately recompute outcomes independently of strings in the audit records.
    one_quarter_women = F(45-40*F(75,100), 60)
    lower_earning_women = 1-one_quarter_women
    combined_time = 1 / (F(1,9)+F(1,12))
    men, boys = F(1,100),F(1,200)
    ensure(6*men+8*boys==F(1,10) and 26*men+48*boys==F(1,2),
           "two original worker productivity equations not satisfied")
    p0 = F(20825) / ((1+F(1,6))**2)
    p1 = F(12000) / (1+F(16,100)*F(5,4))
    k = 5
    sachin = 7*k+1
    ensure(F(6*k,7*k)==F(6,7) and F(6*k+5,7*k+5)==F(7,8),
           "age ratio equations fail")
    areas = [4 * r*r for r in (7,14)] # omit shared pi
    black = F(5,3+5+4)
    speed = F(54+36,1)*F(5,18)
    digit_view = {
        "2023-24-A": "2023-24-A",
    }
    ensure(areas[0]*4==areas[1] and speed==25 and p0==15300 and p1==10000,
           "original paper arithmetic constraints inconsistent")
    positive_2023 = {
        6: "beautiful", 19: "Rectangle", 33: "Exactly one parallel line",
        34:f"{areas[0]//areas[0]}:{areas[1]//areas[0]}",
        35:f"INR {int(p0)}", 36:f"{combined_time} days",
        37:f"{lower_earning_women} of women",
        38:"-25x+y=700" if 700+25*2==750 else "INCORRECT",
        39:f"{int(F(150+175)/speed)} seconds",40:str(black),
        42:f"INR {int(p1)}",43:f"{sachin} years",
        47:"Statement I true; Statement II true" if 180-140+90+50==180 else "INCORRECT",
        49:"F,F" if 100*(4-1)==300 and F(2*30,13)!=60 else "INCORRECT",
        50:"(-7,5); 5 units; (-6,-3)" if math.isqrt(3**2+4**2)==5 else "INCORRECT",
    }
    producer = {
        (SOURCE_2023,n):result for n,result in positive_2023.items()
    }
    producer[SOURCE_2024,43]=f"{int(1/(15*men+20*boys))} days"
    return producer


def full_section(q: int) -> str:
    return ("LOGICAL_REASONING" if q<=15 else "MATHEMATICAL_REASONING" if q<=35
            else "EVERYDAY_MATHEMATICS" if q<=45 else "ACHIEVERS_SECTION")


def validate_batch03(seed_root: Path = SEED, verification_root: Path = PILOT) -> dict:
    validate_seed(seed_root)
    questions, _, _ = load_seed(seed_root)
    byid={q["id"]:q for q in questions}
    try:
        first=json.loads((seed_root/"math_audit_batch01.json").read_text(encoding="utf-8"))
        second=json.loads((verification_root/"fullpaper-source-math-batch02.v1.json").read_text(encoding="utf-8"))
        b03=json.loads((verification_root/B03.name).read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SeedError(f"paper audit unreadable: {exc}") from exc
    ensure(isinstance(b03,dict) and b03.get("schema")=="sof-imo-g09-fullpaper-audit-b03-v1" and
           b03.get("source_boundary")=="SOF_GRADE9_LEVEL1_SCHOOL_MIRROR_PRINTED_PAPERS",
           "B03 scope and authority changed")
    ensure(b03.get("original_seed_positions")==66 and b03.get("fullpaper_seed_positions")==58 and
           b03.get("b01_checked")==16 and b03.get("b02_checked")==15 and
           b03.get("b03_checked")==16 and b03.get("cumulative_agent_checked")==47 and
           b03.get("remaining_fullpaper_seed_positions")==11 and
           b03.get("b03_year_source_split")==YEAR_COUNTS and
           all(b03.get(k)==0 for k in ("b03_choice_disagreements","source_academically_accepted",
                "official_answer_key_verified","rights_clearance_accepted","qrt_cells_accepted","core_ready")),
           "B03 census, year split or academic acceptance unsupported")
    pastids={r["question_id"] for r in first["questions"]}|{r["question_id"] for r in second["observations"]}
    ensure(len(pastids)==31, "previous audit positions overlap or disappear")
    all_full={q["id"] for q in questions if "-L1-" in q["source_id_claim"]}
    ensure(len(all_full)==58, "sample and full Level1 candidates conflated")
    expected=arithmetic_oracles()
    ensure(set(expected)==set(LOCATORS), "calculation source census differs from expected positions")
    rows=b03.get("records")
    ensure(isinstance(rows,list) and len(rows)==16 and all(isinstance(r,dict) for r in rows),
           "B03 must preserve exactly 16 scanned-source reviews")
    actual,counts=set(),{sid:0 for sid in YEAR_COUNTS}
    for row in rows:
        qid=row.get("question_id")
        ensure(qid in byid and qid not in pastids and qid not in actual,
               f"not a new unique fullpaper question: {qid}")
        original=byid[qid]
        sid=original["source_id_claim"]
        n=int(original["original_question_number_claim"])
        key=(sid,n)
        ensure(key in LOCATORS, f"unexpected source position {qid}")
        physical_page,letter,outcome=LOCATORS[key]
        ensure(row.get("source_id")==sid and row.get("source_url")==original["source_url_claim"] and
               row.get("owner_compilation_entry")==original["seed_entry"] and
               row.get("printed_question_number")==str(n) and
               row.get("source_pdf_page_index")==physical_page and
               row.get("original_printed_page")==physical_page+1 and
               row.get("printed_level1_section")==full_section(n),
               f"{qid}: incorrect printed page/source/section locator")
        ensure(row.get("computed_result")==outcome==expected[key] and
               row.get("mathematically_selected_printed_option")==letter and
               row.get("attachment_claimed_option")==letter and
               isinstance(row.get("agent_mathematical_derivation"),str) and
               len(row["agent_mathematical_derivation"])>=120 and
               isinstance(row.get("alternate_verification"),str) and
               len(row["alternate_verification"])>=95 and
               isinstance(row.get("primary_microconcept_hint"),str),
               f"{qid}: derivation or answer not supported")
        ensure(row.get("source_host_status")=="SCHOOL_MIRROR_SOF_BRANDED_SCAN" and
               row.get("academic_status")=="AGENT_COMPUTED_NOT_PEER_ACCEPTED" and
               row.get("transcription_status")=="SOURCE_POSITION_VISUALLY_CHECKED_OPTIONS_NOT_RELICENSED" and
               row.get("organizer_official_key_receipt") is None and
               row.get("original_figure_rights")=="NOT_REVIEWED" and
               row.get("accepted_qrt_cell") is None and row.get("core_eligible") is False,
               f"{qid}: false academic/source/rights/QRT/Core approval")
        ensure(not (set(row)&{"stem","options","figure","source_pdf_bytes"}),
               f"{qid}: copying source text/figures without rights")
        counts[sid]+=1
        actual.add(qid)
    ensure(counts==YEAR_COUNTS and actual == {
        f"{sid}-Q{n:03d}" for sid,n in LOCATORS
    }, "B03 question inventory no longer matches paper locators")
    ensure(actual.isdisjoint(pastids), "B01/B02/B03 overlap")
    ensure(len(all_full-(pastids|actual))==11 and
           all(qid.startswith("SOF-IMO-G09-L1-2025-26-A-") for qid in all_full-(pastids|actual)),
           "remaining 11 should all be unreviewed 2025–26 Set A source positions")
    return {"result":"B03_MATH_RESEARCH_VALID_NO_ACCEPTANCE","new_agent_checked":len(actual),
            "cumulative_fullpaper_agent_checked":len(pastids|actual),"remaining_2025_set_a":11,
            "new_source_option_conflicts":0,"official_keys_accepted":0,"qrt_cells_accepted":0,
            "core_ready":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--verification",type=Path,default=PILOT)
    args=p.parse_args()
    try:
        print(json.dumps(validate_batch03(args.seed,args.verification),sort_keys=True))
    except SeedError as error:
        p.exit(1,f"IMO_FULLPAPER_B03_INVALID: {error}\n")


if __name__=="__main__":
    main()
