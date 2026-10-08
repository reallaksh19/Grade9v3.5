#!/usr/bin/env python3
"""Validate the quarantined SOF IMO source/answer audit; never admit learner records."""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

ROOT = Path(__file__).resolve().parent / "seed"
EXPECTED_COMPARISONS = {
    "SOF-IMO-G09-L1-2023-24-A-Q017": "STEM_MATCH_OPTIONS_DIFFER",
    "SOF-IMO-G09-L1-2023-24-A-Q018": "OPTION_SET_REORDERED",
    "SOF-IMO-G09-L1-2025-26-A-Q028": "STEM_SEMANTIC_DISPUTE",
    "SOF-IMO-G09-L1-2025-26-A-Q031": "DIAGRAM_AND_ANSWER_DISPUTE",
}
EXPECTED_DIVERGENCES = {
    "SOF-IMO-G09-L1-2023-24-A-Q018": ("C", "A"),
    "SOF-IMO-G09-L1-2025-26-A-Q028": ("B", "C"),
    "SOF-IMO-G09-L1-2025-26-A-Q031": ("C", "D"),
}


def ensure(ok: bool, message: str) -> None:
    if not ok:
        raise SeedError(message)


def expected_mathematics() -> dict[str, str]:
    """Recalculate source-prompt results, not the compilation's asserted answer labels."""
    f = Fraction
    # 2023 Q17, Q18, Q45
    cone = "4:9"
    inverse = str(-(f(1, 4) - (f(-2, 3) + f(1, 2))))
    pi = f(22, 7)
    radius = f(88, 5) / (2 * pi)
    dome_cost = (2 * pi * radius**2) * 10000 * f(8, 100)
    # 2024 Q16, Q44
    pie_english = 140 * 15 // 35
    # (2x^2 + 4)^2 - (2x^3 - 11x^2 - 4x + 5)
    difference = {4: 4, 3: -2, 2: 16 + 11, 1: 4, 0: 16 - 5}
    ensure(difference == {4: 4, 3: -2, 2: 27, 1: 4, 0: 11}, "polynomial oracle")
    # 2025 Q28–Q35, Q39, Q42, Q49
    p = f(16, 8)
    q = (15 + (1 - 2 * p) * 6) / 3
    interest = 15000 * (f(11, 10)**3 - 1)
    b = (180 - 75) // 5
    a, c = 4 * b, (75 + b) // 2
    maths_angle = 360 - (80 + 75 + 55 + 70)
    exponent_numerator = 125 - 4 - 64
    exponent_denominator = f(5, 3) + 1 + f(1, 2)
    b_capital = 12000 * 3 + 17000 * 9
    c_capital = 21000 * 6
    a_capital = 16000 * 3 + 11000 * 9
    capital_delta = f(b_capital - c_capital, a_capital + b_capital + c_capital) * 17600
    # Q49: x=2+sqrt(3) -> x^2=7+4sqrt(3), x^3=26+15sqrt(3), expression=3.
    achieves = ((26 - 14 - 14 + 5) != 5, math.isclose(math.sqrt(4), 2),
                not math.isclose(math.sqrt(22), math.sqrt(23)))
    ensure(achieves == (True, True, True), "achievers oracle")
    return {
        "SOF-IMO-G09-L1-2023-24-A-Q017": cone,
        "SOF-IMO-G09-L1-2023-24-A-Q018": inverse,
        "SOF-IMO-G09-L1-2023-24-A-Q045": f"INR {int(dome_cost)}",
        "SOF-IMO-G09-L1-2024-25-B-Q016": str(pie_english),
        "SOF-IMO-G09-L1-2024-25-B-Q044": "4x^4-2x^3+27x^2+4x+11",
        "SOF-IMO-G09-L1-2025-26-A-Q028": "0 (literal printed wording)",
        "SOF-IMO-G09-L1-2025-26-A-Q029": f"q={int(q)}",
        "SOF-IMO-G09-L1-2025-26-A-Q030": f"INR {int(interest)}",
        "SOF-IMO-G09-L1-2025-26-A-Q031": f"a={a}deg,b={b}deg,c={c}deg",
        "SOF-IMO-G09-L1-2025-26-A-Q032": "Hindi and Social Science" if (70 + 55) * 720 // 360 == 250 else "WRONG",
        "SOF-IMO-G09-L1-2025-26-A-Q033": f"{int(maths_angle * f(100, 360))} 2/9 percent",
        "SOF-IMO-G09-L1-2025-26-A-Q034": f"{5**2}:1",
        "SOF-IMO-G09-L1-2025-26-A-Q035": str(int(exponent_numerator / exponent_denominator)),
        "SOF-IMO-G09-L1-2025-26-A-Q039": f"INR {int(capital_delta)}",
        "SOF-IMO-G09-L1-2025-26-A-Q042": "28x-4y=75" if f(560, 100) * 5 == 28 else "WRONG",
        "SOF-IMO-G09-L1-2025-26-A-Q049": "F,F,F" if all(achieves) else "WRONG",
    }


def validate_audit(root: Path = ROOT) -> dict:
    validate_seed(root)
    questions, sources, _ = load_seed(root)
    source_map = {s["source_id"]: s for s in sources["sources"]}
    by_id = {q["id"]: q for q in questions}
    try:
        audit = json.loads((root / "math_audit_batch01.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"audit unreadable: {exc}") from exc
    ensure(isinstance(audit, dict) and audit.get("schema") == "sof-imo-grade9-source-math-audit-v1",
           "audit schema mismatch")
    rows = audit.get("questions")
    ensure(isinstance(rows, list) and len(rows) == 16, "bounded 16-question audit census changed")
    ensure(audit.get("core_ready_count") == 0 and audit.get("accepted_qrt_cells") == 0,
           "audit claims unearned acceptance")
    ensure(isinstance(audit.get("cross_document_candidates"), list), "cross-paper link missing")
    actual, expected = set(), expected_mathematics()
    for row in rows:
        ensure(isinstance(row, dict), "audit row not object")
        qid = row.get("question_id")
        ensure(qid in by_id and qid not in actual, f"audit unknown/duplicate question: {qid}")
        original = by_id[qid]
        sid = original["source_id_claim"]
        ensure(row.get("source_id") == sid and row.get("source_url") == source_map[sid]["url"],
               f"{qid}: source evidence mismatch")
        ensure(row.get("original_printed_question") == original["original_question_number_claim"] and
               row.get("compilation_entry") == original["seed_entry"] and
               row.get("compilation_subentry") == original["seed_subentry"], f"{qid}: source-position drift")
        page = row.get("source_pdf_page_index")
        ensure(type(page) is int and 0 <= page < 8 and row.get("source_printed_page") == page + 1,
               f"{qid}: missing/invalid printed page")
        number = int(original["original_question_number_claim"])
        section = ("LOGICAL_REASONING" if number <= 15 else "MATHEMATICAL_REASONING" if number <= 35
                   else "EVERYDAY_MATHEMATICS" if number <= 45 else "ACHIEVERS_SECTION")
        ensure(row.get("exam_section_observed") == section, f"{qid}: section differs from printed SOF sections")
        ensure(row.get("computed_answer") == expected.get(qid), f"{qid}: calculation result unsupported")
        ensure(row.get("math_derived_printed_choice") in "ABCD" and
               row.get("compilation_claimed_choice") in "ABCD" and
               isinstance(row.get("independent_computation"), str) and len(row["independent_computation"]) >= 35,
               f"{qid}: insufficient answer reasoning")
        ensure(row.get("source_comparison") in {
            "MATCH_PARTIAL", "MATH_NOTATION_VISUALLY_CHECKED", "FIGURE_DEPENDENT",
            "STEM_MATCH_OPTIONS_DIFFER", "OPTION_SET_REORDERED", "MATCH_REQUIRES_ARITHMETIC_REVIEW",
            "SECTION_CORRECTED", "STEM_SEMANTIC_DISPUTE", "DIAGRAM_AND_ANSWER_DISPUTE"},
            f"{qid}: unknown source comparison")
        ensure(row.get("academic_review_status") == "AGENT_SOLVED_NOT_INDEPENDENTLY_REVIEWED" and
               row.get("source_integrity_status") == "SCANNED_PAGE_COMPARISON_PARTIAL" and
               row.get("official_key_receipt") is None and row.get("rights_status") == "NOT_REVIEWED" and
               row.get("qrt_status") == "NOT_CLASSIFIED" and row.get("core_eligible") is False,
               f"{qid}: unsupported source/answer/rights/QRT/Core promotion")
        actual.add(qid)
    ensure(actual == set(expected), "audit question inventory mismatch")
    for qid, category in EXPECTED_COMPARISONS.items():
        row = next(r for r in rows if r["question_id"] == qid)
        ensure(row["source_comparison"] == category, f"{qid}: dispute silently discarded")
    observed_differences = {r["question_id"]:(r["math_derived_printed_choice"],r["compilation_claimed_choice"])
                            for r in rows if r["math_derived_printed_choice"] != r["compilation_claimed_choice"]}
    ensure(observed_differences == EXPECTED_DIVERGENCES, "three researched answer discrepancies lost")
    link = audit["cross_document_candidates"]
    ensure(len(link) == 1 and link[0].get("source_b_seed_record") is False and
           link[0].get("printed_question_a") == "45" and link[0].get("printed_question_b") == "42",
           "cross-year duplicate remains distinct and outside seed")
    return {"result":"RESEARCH_AUDIT_VALID_NO_ADMISSION", "worked_source_questions":len(actual),
            "choice_discrepancies":len(observed_differences), "core_eligible":0, "official_answer_keys_verified":0,
            "independently_peer_reviewed":0, "qrt_accepted":0}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed", type=Path, default=ROOT)
    args = p.parse_args()
    try:
        print(json.dumps(validate_audit(args.seed), sort_keys=True))
    except SeedError as exc:
        p.exit(1, f"IMO_AUDIT_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
