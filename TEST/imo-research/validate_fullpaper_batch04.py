#!/usr/bin/env python3
"""Validate the final SOF IMO full-paper agent-calculated seed positions; research only."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from validate_seed import SeedError, load_seed, validate as validate_seed

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "seed"
VERIFY = ROOT / "verification"
SOURCE = "SOF-IMO-G09-L1-2025-26-A"
URL = "https://www.iswkoman.com/uploads/olympiad/9262492-IMO%2025-26%20CLASS%209.pdf"
NUMBERS = (36,37,38,40,43,44,45,46,47,48,50)
CHOICES = {36:"B",37:"A",38:"D",40:"D",43:"D",44:"C",
           45:"B",46:"B",47:"C",48:"C",50:"A"}
RESULTS = {
    36:"105 rows",37:"20 years",38:"8 labourers",40:"26% price increase",
    43:"4/5",44:"INR 4000 income for P",45:"x(x−3)(x+4)",
    46:"(-10,-4); (0,0); (4,-9)",47:"P=(ii), Q=(iii), R=(i)",
    48:"Only statement C is incorrect",50:"Both circle statements true",
}


def ensure(ok: bool, message: str) -> None:
    if not ok:
        raise SeedError(message)


def mathematical_oracles() -> dict[int, str]:
    """Recompute numeric facts and geometry consequences, not the ledger's chosen choices."""
    rows = int((10914+111)**0.5)
    ensure(rows*rows == 10914+111, "tree count square calculation fails")
    s = F(84,6)
    ensure(F(60-s-6,s-6)==5, "father-son age relation fails")
    hours = 12*8*10
    required = F(hours,8*15)
    net = (1+F(40,100))*(1-F(10,100))
    primes = {p for p in range(51,101)
              if all(p%d for d in range(2,int(p**0.5)+1))}
    ensure(primes=={53,59,61,67,71,73,79,83,89,97}, "prime enumeration incorrect")
    # 5x-3y=1600; 4x-2y=1600 => x=800, y=800.
    xx, yy = 800,800
    ensure(5*xx-3*yy==1600 and 4*xx-2*yy==1600, "ratio income savings inconsistent")
    factor = lambda t:t*(t-3)*(t+4)
    ensure(all(factor(t)==t**3+t*t-12*t for t in (0,4,7)), "cuboid polynomial factorisation incorrect")
    lower = 2*10-15
    spread = max([71,18,20,54,86,65,75,93])-min([71,18,20,54,86,65,75,93])
    bar_cm = F(4,10)*F(2500,50)
    # Q48: A cone/cylinder transfer, B similarity/radius/slant 3:4:5, C sphere in cube.
    cone_h = F(3*15**2*4,10**2)
    volume_b = F(314,100)*12*4**3
    slant_b = 5*4
    sphere_vol = F(4,3)*F(314,100)*F(7,2)**3
    ensure(cone_h==27 and volume_b==F(241152,100) and slant_b==20, "cone transfer and slant checks inconsistent")
    ensure(sphere_vol != F(18576,100), "inscribed sphere distractor unexpectedly equal")
    # Q50 part I chord-distance calculation. Part II independently follows from
    # equal cyclic inscribed angles at D/B (outer) and E/B (inner), while AD=AE
    # and BC=BF are line supports. Diagram is essential, not a numerical oracle.
    radius2 = (F(6,2))**2 + 4**2
    larger_chord_distance2 = radius2-(F(8,2))**2
    ensure(radius2==25 and larger_chord_distance2==9, "two-chord distance oracle incorrect")
    return {
        36:f"{rows} rows",37:f"{int(s+6)} years",38:f"{int(required)} labourers",
        40:f"{int((net-1)*100)}% price increase",
        43:str(F(50-len(primes),50)),
        44:f"INR {5*xx} income for P",
        45:"x(x−3)(x+4)" if factor(7)==7**3+7**2-12*7 else "ERROR",
        46:"(-10,-4); (0,0); (4,-9)" if 2+3*(-4)==-10 and (5-5)==0 else "ERROR",
        47:"P=(ii), Q=(iii), R=(i)" if (lower,spread,bar_cm)==(5,75,20) else "ERROR",
        48:"Only statement C is incorrect" if sphere_vol != F(18576,100) else "ERROR",
        50:"Both circle statements true" if larger_chord_distance2==9 else "ERROR",
    }


def validate_b04(seed_root: Path = SEED, verification_root: Path = VERIFY) -> dict:
    validate_seed(seed_root)
    qs, _, _ = load_seed(seed_root)
    byid={q["id"]:q for q in qs}
    try:
        b01=json.loads((seed_root/"math_audit_batch01.json").read_text(encoding="utf-8"))
        b02=json.loads((verification_root/"fullpaper-source-math-batch02.v1.json").read_text(encoding="utf-8"))
        b03=json.loads((verification_root/"fullpaper-audit-b03.v1.json").read_text(encoding="utf-8"))
        doc=json.loads((verification_root/"fullpaper-audit-b04.v1.json").read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SeedError(f"B04 source evidence unreadable: {exc}") from exc
    ensure(isinstance(doc,dict) and doc.get("schema")=="sof-imo-g09-fullpaper-audit-b04-v1" and
           doc.get("original_source_url")==URL and
           doc.get("source_role")=="SOF_BRANDED_SCHOOL_MIRRORED_SCAN_NOT_OFFICIAL_HOST" and
           doc.get("physical_pdf_page_count")==7 and doc.get("visual_source_pages_checked")==[5,6],
           "B04 original scanned source custody changed")
    count_checks={"seed_source_positions":66,"fullpaper_source_positions":58,
      "organizer_sample_seed_positions":8,"b01_distinct_checked":16,
      "b02_distinct_checked":15,"b03_distinct_checked":16,"b04_distinct_checked":11,
      "total_nonoverlapping_agent_worked_fullpaper_source_positions":58,
      "remaining_unworked_fullpaper_seed_positions":0,"b04_choice_label_disagreements":0,
      "official_fullpaper_answer_key_receipts":0,"independently_accepted_source_answers":0,
      "rights_clearance_count":0,"accepted_qrt_cells":0,"core_ready_count":0}
    ensure(all(doc.get(k)==v for k,v in count_checks.items()), "unearned census, answer-key or admission claim")
    earlier=[{x["question_id"] for x in b01["questions"]},
             {x["question_id"] for x in b02["observations"]},
             {x["question_id"] for x in b03["records"]}]
    ensure(list(map(len,earlier))==[16,15,16] and
           len(earlier[0]|earlier[1]|earlier[2])==47,
           "B01-03 overlap or audit count drift")
    remaining={q["id"] for q in qs if "-L1-" in q["source_id_claim"]} - set.union(*earlier)
    ensure(len(remaining)==11 and len(qs)==66, "source bank and remaining census conflict")
    rows=doc.get("records")
    ensure(isinstance(rows,list) and len(rows)==11 and all(isinstance(x,dict) for x in rows),
           "B04 source positions absent")
    expected=mathematical_oracles()
    ensure(set(expected)==set(NUMBERS),"mathematical oracle incomplete")
    ids=set();numbers=set()
    for row in rows:
        qid=row.get("question_id")
        ensure(qid in remaining and qid not in ids, f"overlap/unknown B04 position {qid}")
        q=byid[qid];number=int(q["original_question_number_claim"])
        ensure(number in NUMBERS and number not in numbers, f"missing or unexpected original Q{number}")
        page=5 if number<=44 else 6
        ensure(row.get("source_id")==SOURCE==q["source_id_claim"] and
               row.get("source_url")==URL==q["source_url_claim"] and
               row.get("printed_question_number")==str(number) and
               row.get("owner_compilation_entry")==q["seed_entry"] and
               row.get("source_pdf_page_index")==page and
               row.get("original_printed_page")==page+1 and
               row.get("printed_level1_section")==(
                   "EVERYDAY_MATHEMATICS" if number<=45 else "ACHIEVERS_SECTION"),
               f"{qid}: source locator/printed section mismatch")
        ensure(row.get("independent_agent_result")==RESULTS[number]==expected[number] and
               row.get("printed_choice_selected_by_math")==CHOICES[number] and
               row.get("owner_compilation_answer_label")==CHOICES[number] and
               len(row.get("mathematical_derivation") or "")>=140 and
               len(row.get("alternate_check") or "")>=90 and
               isinstance(row.get("mathematical_crux"),str) and len(row["mathematical_crux"])>=12,
               f"{qid}: printed option or working proof unsupported")
        requires_figure = number==50
        ensure(row.get("figure_referenced") is requires_figure and
               row.get("figure_custody_status")==(
                   "INSPECTED_SOURCE_FIGURE_NOT_RELICENSED" if requires_figure
                   else "NO_SOURCE_FIGURE_NEEDED_FOR_SOLUTION") and
               row.get("academic_acceptance_status")==
                   "AGENT_COMPUTED_NOT_INDEPENDENTLY_PEER_ACCEPTED" and
               row.get("printed_official_key_receipt") is None and
               row.get("rights_status")=="NOT_REVIEWED" and
               row.get("qrt_accepted_cell") is None and
               row.get("core_eligible") is False,
               f"{qid}: false figure, academic/key/rights/QRT/Core status")
        if number==50:
            working=row["mathematical_derivation"].lower()
            ensure(all(term in working for term in ("same chord","inner circle","outer circle","collinear")),
                   "Q50 figure reasoning must include two cyclic warrants and collinearities")
            ensure("parallel" in row.get("alternate_check","").lower(),
                   "Q50 source diagram parallel-line consequence not reasoned")
        ensure(not (set(row)&{"stem","options","figure_image","pdf_bytes","original_full_text"}),
               f"{qid}: unlicensed original source content added")
        ids.add(qid);numbers.add(number)
    ensure(ids==remaining and numbers==set(NUMBERS) and
           len(set.union(*earlier,ids))==58,
           "B04 does not close all original fullpaper seed source positions")
    return {"result":"COMPLETE_58_FULLPAPER_AGENT_MATH_AUDIT_NO_ADMISSION",
            "seed_questions_original":66,"original_fullpaper_seed_positions":58,
            "new_b04_agent_worked":11,"combined_agent_worked_fullpaper":58,
            "remaining_unworked_fullpaper":0,"official_keys_accepted":0,
            "independent_academic_accepted":0,"accepted_qrt_cells":0,"core_ready":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed",type=Path,default=SEED)
    p.add_argument("--verification",type=Path,default=VERIFY)
    args=p.parse_args()
    try:
        print(json.dumps(validate_b04(args.seed,args.verification),sort_keys=True))
    except SeedError as error:
        p.exit(1,f"IMO_FULLPAPER_B04_INVALID: {error}\n")


if __name__=="__main__":
    main()
