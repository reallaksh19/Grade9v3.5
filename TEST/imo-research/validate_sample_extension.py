#!/usr/bin/env python3
"""Quarantined source-completeness and mathematical checks for SOF sample Q1/Q3."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed, load_seed

HERE = Path(__file__).resolve().parent
FILENAME = "official-sample-2026-27-new-positions.v1.json"
SOURCE_URL = "https://sofworld.org/download/file/fid/73719"
SAMPLE_SOURCE = "SOF-IMO-G09-SAMPLE-2026-27"
NEW_NUMBERS = {1, 3}


def ensure(ok: bool, reason: str) -> None:
    if not ok:
        raise SeedError(reason)


def cross(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def check_geometric_math() -> tuple[int, int]:
    """Orient an integer-labelled cube; compute radial quadrant missing square."""
    directions = {
        2:(0,0,1), 6:(0,0,-1),
        4:(0,1,0), 1:(0,-1,0),
        5:(1,0,0), 3:(-1,0,0),
    }
    # Source first die: top=2, front=4, right=5; third: top=5, front=6, right=1.
    for top, front, right in ((2,4,5),(5,6,1)):
        ensure(cross(directions[front], directions[top]) == directions[right],
               "printed die orientations conflict with proposed cube assignment")
    # Second printed die: top=6, right=3; front inferred using top x right.
    desired_front = cross(directions[6], directions[3])
    faces = [name for name,vector in directions.items() if vector == desired_front]
    ensure(faces == [4], "source dice face calculation is not uniquely 4")
    # For each quadrant: square of average of two neighbouring outer numbers.
    quadrant_squares = [((a+b)//2)**2 for a,b in ((14,8),(6,12),(3,13),(5,9))]
    ensure(quadrant_squares == [121,81,64,49], "printed radial figure rule inconsistent")
    return faces[0], quadrant_squares[-1]


def validate_extension(seed_root: Path = HERE / "seed",
                       taxonomy_root: Path = HERE / "taxonomy",
                       extension_root: Path = HERE / "verification") -> dict:
    validate_seed(seed_root)
    questions, _, _ = load_seed(seed_root)
    source_ids = {q["id"] for q in questions}
    try:
        sample = json.loads((taxonomy_root / "official-sample-2026-27-observations.v1.json")
                            .read_text(encoding="utf-8"))
        data = json.loads((extension_root / FILENAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SeedError(f"sample extension unreadable: {error}") from error
    ensure(isinstance(data, dict) and data.get("schema") == "sof-imo-g09-sample-extension-census-v1" and
           data.get("official_source_url") == sample.get("organizer_url") == SOURCE_URL and
           data.get("source_kind") == "SOF_ORGANIZER_HOSTED_SAMPLE" and
           data.get("source_document_page_count") == sample.get("page_count") == 2 and
           data.get("owner_attached_seed_census_unmodified") == len(questions) == 66 and
           data.get("original_sample_question_count") == 10 and
           data.get("owner_seed_sample_question_count") == 8 and
           data.get("additional_discovered_count") == 2 and
           data.get("total_source_positions_with_locator") == 10 and
           data.get("question_numbers_missing_owner_seed") == [1,3] and
           data.get("independent_academic_accepted_count") == 0 and
           data.get("accepted_qrt_cell_count") == 0 and
           data.get("core_ready_count") == 0,
           "source census or research-only authority drift")
    seed_sample_numbers = {int(q["original_question_number_claim"]) for q in questions
                           if q["source_id_claim"] == SAMPLE_SOURCE}
    ensure(seed_sample_numbers == set(range(1,11)) - NEW_NUMBERS and
           {x["sample_question_number"] for x in sample["records"]} == seed_sample_numbers,
           "eight previous sample positions must remain source-bound")
    records = data.get("entries")
    ensure(isinstance(records, list) and len(records) == 2 and
           all(isinstance(r,dict) for r in records), "exactly two source discoveries required")
    expected_results = check_geometric_math()
    found = set()
    for record in records:
        n = record.get("sample_question_number")
        ensure(type(n) is int and n in NEW_NUMBERS and n not in found,
               f"duplicate/unknown new sample position: {n}")
        found.add(n)
        qid = f"{SAMPLE_SOURCE}-Q{n:03d}"
        ensure(record.get("question_id") == qid and qid not in source_ids and
               record.get("source_id") == SAMPLE_SOURCE and
               record.get("source_url") == SOURCE_URL and
               record.get("original_page_index") == 0 and
               record.get("organizer_key_panel_page_index") == 1 and
               record.get("section_observed") == "LOGICAL_REASONING" and
               record.get("source_figure_required") is True and
               record.get("figure_kind") == ("SPATIAL_DICE_ORIENTATIONS" if n == 1 else "RADIAL_NUMBER_PATTERN") and
               record.get("printed_key_option") == record.get("agent_derived_option") == "B",
               f"{qid}: original source, diagram or answer-key mismatch")
        ensure(record.get("original_owner_seed_membership") is False and
               record.get("agent_work_status") == "AGENT_SOURCE_FIGURE_SOLVED_NOT_PEER_REVIEWED" and
               record.get("publication_rights_status") == "NOT_REVIEWED" and
               record.get("independent_academic_acceptance") is False and
               record.get("accepted_primary_qrt_cell") is None and
               record.get("core_eligible") is False and
               record.get("primary_topic_proposal") == "LOGIC" and
               record.get("microconcept_proposal") == "MIC-" + record.get("subtopic_proposal","") and
               len(record.get("independent_mathematical_check") or "") >= 130 and
               len(record.get("crosscheck") or "") >= 120,
               f"{qid}: unsupported mathematics/custody/readiness assertion")
        ensure(not (set(record) & {"stem","options","original_figure","image_data","pdf_bytes"}),
               f"{qid}: copyrighted original question content not cleared for reproduction")
        ensure(("4" if n == 1 else "49") in record["independent_mathematical_check"] and
               expected_results[n == 3] == (4 if n == 1 else 49),
               f"{qid}: mathematical answer claim not grounded")
    ensure(found == NEW_NUMBERS, "missing newly discovered sample question")
    return {"result":"SOURCE_COMPLETE_SAMPLE_RESEARCH_ONLY",
            "owner_seed_sample_questions":len(seed_sample_numbers),
            "new_sample_source_positions":len(found),
            "total_sample_source_positions":len(found)+len(seed_sample_numbers),
            "attachment_seed_questions_unchanged":len(source_ids),
            "agent_computed_new_key_matches":2,
            "independent_peer_accepted":0, "accepted_qrt_cells":0, "core_ready":0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed",type=Path,default=HERE/"seed")
    parser.add_argument("--taxonomy",type=Path,default=HERE/"taxonomy")
    parser.add_argument("--extension",type=Path,default=HERE/"verification")
    args = parser.parse_args()
    try:
        print(json.dumps(validate_extension(args.seed,args.taxonomy,args.extension),sort_keys=True))
    except SeedError as exc:
        parser.exit(1,f"IMO_SAMPLE_EXTENSION_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
