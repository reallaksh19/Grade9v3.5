#!/usr/bin/env python3
"""Fail-closed research guard for source/math/QRT sample evidence; no Core admission."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_seed import SeedError
from validate_taxonomy import validate_taxonomy, load_taxonomy

BASE = Path(__file__).resolve().parent
PILOT = BASE / "verification" / "official-sample-2026-27-math-qrt-pilot.v1.json"
SAMPLE = BASE / "taxonomy" / "official-sample-2026-27-observations.v1.json"
SAMPLE_ID = "SOF-IMO-G09-SAMPLE-2026-27"
SOURCE_URL = "https://sofworld.org/download/file/fid/73719"
DEMANDS = {"RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"}
COMPONENTS = {"concept_model_selection", "representation_translation",
              "reasoning_chain_length", "algebra_computational_load", "trap_exception_sensitivity"}
PRINTED_KEYS = {2:"B",4:"B",5:"C",6:"C",7:"D",8:"D",9:"D",10:"A"}
EXPECTED_RESULTS = {
    2:("B", "wealth maps to liv"), 4:("B", "y = 2x - 1"),
    6:("C", "equals added to equals remain equal"), 7:("D", "Rs 60"),
    8:("D", "15 metres"), 9:("D", "Statement I false; Statement II true (3/80)"),
    10:("A", "Option A is the incorrect claim"),
}
HISTORICAL_QRT = ("reallaksh19/Grade9v3.5@8678645ef2fd5e63401ef5af3621b94e925732a8:"
                  "Shared/quality/question-demand-matrix.v1.json")


def ensure(condition: bool, why: str) -> None:
    if not condition:
        raise SeedError(why)


def score_band(score: int) -> str:
    return "D1" if score <= 2 else "D2" if score <= 5 else "D3" if score <= 7 else "D4"


def check_pilot(seed: Path = BASE / "seed",
                taxonomy: Path = BASE / "taxonomy",
                pilot: Path = PILOT) -> dict:
    validate_taxonomy(seed, taxonomy)
    try:
        data = json.loads(pilot.read_text(encoding="utf-8"))
        orig = json.loads((taxonomy / SAMPLE.name).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"pilot source unreadable: {exc}") from exc
    ensure(isinstance(data, dict) and data.get("schema") == "sof-imo-g09-sample-math-qrt-pilot-v1",
           "unsupported pilot schema")
    ensure(data.get("source_url") == SOURCE_URL and data.get("source_page_count") == 2 and
           data.get("cognitive_authority") == HISTORICAL_QRT and
           data.get("source_rights_status") == "NOT_REVIEWED" and
           data.get("record_type") == "RESEARCH_OVERLAY_NO_QUESTION_TEXT_OR_FIGURES",
           "false source/cognitive/rights authority")
    ensure(data.get("qrt_accepted_count") == 0 and
           data.get("independent_peer_accepted_count") == 0 and
           data.get("core_ready_count") == 0,
           "nonzero acceptance claim not supported")
    issue_text = " ".join(data.get("source_issues") or [])
    ensure("Q9" in issue_text and "radical" in issue_text and "Q5" in issue_text,
           "source mismatch and diagram hold not visible")

    _, mapped, _ = load_taxonomy(taxonomy)
    mapped_ids = {m["question_id"] for m in mapped if m["source_id"] == SAMPLE_ID}
    originals = {r["question_id"]:r for r in orig["records"]}
    rows = data.get("records")
    ensure(isinstance(rows, list) and len(rows) == 8 and
           all(isinstance(r, dict) for r in rows), "pilot must cover exactly 8 seeded sample instances")
    seen, proposed, computed, cells = set(), 0, 0, set()
    for row in rows:
        qid = row.get("question_id")
        ensure(qid in originals and qid in mapped_ids and qid not in seen,
               f"pilot has unknown/duplicate question: {qid}")
        seen.add(qid)
        q = originals[qid]
        n = q["sample_question_number"]
        ensure(row.get("sample_question_number") == n and row.get("source_id") == SAMPLE_ID and
               row.get("source_url") == SOURCE_URL and
               row.get("source_pdf_page_index") == q["pdf_page_index"] and
               row.get("source_section") == q["section_observed"] and
               row.get("figure_dependency") == q["source_asset_dependency"] and
               row.get("organizer_printed_key") == PRINTED_KEYS[n] == q["printed_answer_key_option"],
               f"{qid}: provenance or organizer-key mismatch")
        ensure(row.get("official_key_sighted") is True and
               row.get("external_independent_academic_review") == "PENDING" and
               row.get("official_source_reproduction_rights") == "NOT_REVIEWED" and
               row.get("core_eligible") is False and
               row.get("accepted_qrt_cell") is None,
               f"{qid}: attempted official/academic/rights/Core promotion")
        ensure(not (set(row) & {"stem", "options", "figure_image", "pdf_bytes"}),
               f"{qid}: original source text/figure not licensed for reproduction")
        proposal = row.get("qrt_proposal")
        if n == 5:
            ensure(row.get("agent_derived_option") is None and
                   row.get("answer_meaning") is None and
                   row.get("agent_answer_status") == "FIGURE_GEOMETRY_PENDING" and
                   row.get("source_vs_owner_transcription_status") == "SOURCE_FIGURE_INTERPRETATION_HOLD" and
                   proposal is None,
                   "Q5 diagram-dependent maths must stay on hold without an invented QRT cell")
            continue
        want_choice, want_result = EXPECTED_RESULTS[n]
        ensure(row.get("agent_derived_option") == want_choice and
               row.get("answer_meaning") == want_result and
               len(row.get("source_mathematical_derivation") or "") >= 85 and
               len(row.get("independent_check") or "") >= 45,
               f"{qid}: insufficient agent-derived mathematics")
        ensure(row["agent_derived_option"] == row["organizer_printed_key"],
               f"{qid}: mathematical work vs organizer key mismatch")
        ensure(row.get("agent_answer_status") in {
            "AGENT_MATH_CHECKED_ORIGINAL_PDF", "AGENT_MATH_CHECKED_SOURCE_BUT_OWNER_STEM_DISPUTED"},
            f"{qid}: incorrect maths source status")
        if n == 9:
            ensure(row.get("source_vs_owner_transcription_status") == "MATERIAL_TRANSCRIPTION_CONFLICT" and
                   "3/80" in row["source_mathematical_derivation"] and
                   "389/90" in row["source_mathematical_derivation"],
                   "Q9 source transcription/answer conflict silently erased")
        ensure(isinstance(proposal, dict) and proposal.get("primary_demand") in DEMANDS and
               proposal.get("classification_status") == "PROPOSED_AI_NOT_ACADEMICALLY_ACCEPTED" and
               proposal.get("accepted") is False and
               len(proposal.get("protected_decision") or "") >= 40 and
               len(proposal.get("justification") or "") >= 40,
               f"{qid}: missing substantive QRT proposal")
        components = proposal.get("score_components")
        ensure(isinstance(components, dict) and set(components) == COMPONENTS and
               all(type(v) is int and 0 <= v <= 2 for v in components.values()),
               f"{qid}: invalid difficulty component evidence")
        score = sum(components.values())
        band = score_band(score)
        ensure(proposal.get("score") == score and proposal.get("band") == band and
               proposal.get("cell") == f"QRT-{proposal['primary_demand']}-{band}" and
               isinstance(proposal.get("secondary_demands"), list) and
               all(d in DEMANDS and d != proposal["primary_demand"] for d in proposal["secondary_demands"]),
               f"{qid}: illegal difficulty/cell derivation")
        proposed += 1; computed += 1; cells.add(proposal["cell"])
    ensure(seen == mapped_ids and set(PRINTED_KEYS) == {originals[q]["sample_question_number"] for q in seen},
           "source question inventory drift")
    ensure(proposed == 7 and computed == 7 and len(cells) == 6,
           "pilot provisional QRT coverage drift")
    return {"result":"SAMPLE_MATH_AND_QRT_PROPOSALS_ONLY", "sample_seed_questions":len(seen),
            "agent_calculated":computed, "printed_key_agreements":computed,
            "on_figure_hold":1, "proposed_primary_qrt_assignments":proposed,
            "distinct_proposed_qrt_cells":len(cells), "accepted_qrt_cells":0,
            "independent_peer_accepted":0, "core_ready":0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, default=BASE / "seed")
    parser.add_argument("--taxonomy", type=Path, default=BASE / "taxonomy")
    parser.add_argument("--pilot", type=Path, default=PILOT)
    args = parser.parse_args()
    try:
        print(json.dumps(check_pilot(args.seed,args.taxonomy,args.pilot), sort_keys=True))
    except SeedError as exc:
        parser.exit(1, f"IMO_SAMPLE_PILOT_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
