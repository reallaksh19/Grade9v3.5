#!/usr/bin/env python3
"""Validate SOF Grade 9 syllabus mapping; never accept QRT or learner products."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = ROOT / "seed"
TAX = ROOT / "taxonomy"

from validate_seed import SeedError, validate as validate_seed, load_seed  # noqa: E402

OFFICIAL_TOPIC_IDS = (
    "NS", "POLY", "ALG_ID", "COORD", "LIN_EQ", "EUCLID", "ANGLES",
    "SEQUENCES", "TRIANGLES", "QUADS", "TRIANGLE_AREAS", "CIRCLES",
    "AREA_PERIM", "CONSTRUCTIONS", "MENSURATION", "STATISTICS", "PROBABILITY",
)
ADJUNCT_TOPIC_IDS = ("LOGIC", "QUANT")
SECTIONS = ("LOGICAL_REASONING", "MATHEMATICAL_REASONING", "EVERYDAY_MATHEMATICS", "ACHIEVERS_SECTION")
SYLLABUS = "https://sofworld.org/imo/class-9/imo-syllabus/imo-syllabus-class-9"
SAMPLE_PDF = "https://sofworld.org/download/file/fid/73719"
SAMPLE_KEY = {2:"B",4:"B",5:"C",6:"C",7:"D",8:"D",9:"D",10:"A"}


def ensure(ok: bool, detail: str) -> None:
    if not ok:
        raise SeedError(detail)


def load_taxonomy(root: Path = TAX) -> tuple[dict, list[dict], dict]:
    try:
        register = json.loads((root / "sof-class9-topic-registry.v1.json").read_text(encoding="utf-8"))
        subtopics = json.loads((root / "sof-class9-subtopics.v1.json").read_text(encoding="utf-8"))
        lines = (root / "seed-question-topic-map.v1.jsonl").read_text(encoding="utf-8").splitlines()
        ensure(bool(lines) and all(line.strip() for line in lines), "taxonomy blank/absent rows")
        rows = [json.loads(line) for line in lines]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"taxonomy unreadable: {exc}") from exc
    ensure(isinstance(register, dict) and isinstance(subtopics, dict) and
           all(isinstance(x, dict) for x in rows),
           "taxonomy records must be objects")
    return register, rows, subtopics


def full_paper_section(number: int) -> str:
    if not 1 <= number <= 50:
        raise SeedError(f"invalid Level 1 printed paper position {number}")
    return SECTIONS[0 if number <= 15 else 1 if number <= 35 else 2 if number <= 45 else 3]


def validate_taxonomy(seed: Path = SEED, root: Path = TAX) -> dict:
    validate_seed(seed)
    qs, _, _ = load_seed(seed)
    q_by_id = {q["id"]: q for q in qs}
    registry, rows, subtopic_data = load_taxonomy(root)
    try:
        sample = json.loads((root / "official-sample-2026-27-observations.v1.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"sample evidence unreadable: {exc}") from exc
    ensure(isinstance(sample, dict) and
           sample.get("schema") == "sof-imo-g09-official-sample-observations-v1" and
           sample.get("organizer_url") == SAMPLE_PDF and
           sample.get("host_class") == "SOF_ORGANIZER_HOSTED" and
           sample.get("source_id") == "SOF-IMO-G09-SAMPLE-2026-27" and
           sample.get("page_count") == 2 and
           sample.get("full_sample_question_count") == 10 and
           sample.get("captured_seed_question_count") == 8 and
           sample.get("missing_from_seed") == [1, 3] and
           sample.get("document_sha256") is None and
           sample.get("source_rights_status") == "NOT_REVIEWED" and
           sample.get("academic_review_status") == "NOT_REVIEWED",
           "unverified organizer sample custody/key claim")
    sample_rows = sample.get("records")
    ensure(isinstance(sample_rows, list) and len(sample_rows) == 8 and
           all(isinstance(x, dict) for x in sample_rows), "sample observation census changed")
    sample_by_qid = {x.get("question_id"):x for x in sample_rows}
    ensure(len(sample_by_qid) == 8, "duplicate organizer sample observation question")
    ensure(subtopic_data.get("schema") == "sof-imo-g09-subtopics-v1" and
           subtopic_data.get("authority") == "ANALYST_PROVISIONAL_NOT_OFFICIAL_SOFSUBTOPICS",
           "subtopic authority is not independently accepted")
    subtopics = subtopic_data.get("subtopics")
    ensure(isinstance(subtopics, list) and all(isinstance(x, dict) for x in subtopics),
           "subtopic catalogue malformed")
    sub_by_id = {x.get("id"):x for x in subtopics}
    ensure(len(sub_by_id) == len(subtopics) and all(isinstance(k, str) for k in sub_by_id),
           "subtopic catalogue duplicates/invalid IDs")
    ensure(registry.get("schema") == "sof-imo-g09-taxonomy-v1" and
           registry.get("source_url") == SYLLABUS and registry.get("grade") == 9 and
           registry.get("exam_level") == "LEVEL_1", "syllabus identity not grounded")
    ensure(registry.get("authority_claim") == "SOF_ORGANIZER_HOSTED_SYLLABUS_PAGE" and
           registry.get("disposition") == "RESEARCH_TAXONOMY_NOT_ACADEMICALLY_ACCEPTED",
           "unearned taxonomy authority")
    official, adjunct = registry.get("official_topics"), registry.get("adjunct_topics")
    ensure(isinstance(official, list) and isinstance(adjunct, list),
           "missing official/adjunct topic taxonomies")
    ensure(tuple(x.get("topic_id") for x in official) == OFFICIAL_TOPIC_IDS and
           all(x.get("official_syllabus") is True and x.get("section") == "SECTION_2"
               and x.get("ordinal") == i for i, x in enumerate(official, 1)),
           "official SOF Section 2 taxonomy/order drift")
    ensure(tuple(x.get("topic_id") for x in adjunct) == ADJUNCT_TOPIC_IDS and
           all(x.get("official_syllabus") is False for x in adjunct) and
           tuple(x.get("section") for x in adjunct) == ("SECTION_1", "SECTION_3"),
           "adjunct incorrectly claimed as official Section 2 topic")
    section_map = registry.get("exam_sections")
    ensure(isinstance(section_map, list) and
           tuple(x.get("id") for x in section_map) == SECTIONS and
           [x.get("count") for x in section_map] == [15, 20, 10, 5] and
           [x.get("marks_per_question") for x in section_map] == [1, 1, 1, 3],
           "SOF Level 1 exam section pattern changed")
    ensure(len(rows) == len(qs) == 66, "incomplete source-question taxonomy mapping")
    count, seen, section_counts, used_subtopics, sample_counts = Counter(), set(), Counter(), set(), Counter()
    for row in rows:
        qid = row.get("question_id")
        ensure(isinstance(qid, str) and qid in q_by_id and qid not in seen,
               f"duplicate/unavailable taxonomy question: {qid}")
        q = q_by_id[qid]
        ensure(row.get("source_id") == q["source_id_claim"] and
               row.get("original_q") == q["original_question_number_claim"] and
               row.get("attachment_entry") == q["seed_entry"] and
               row.get("attachment_subentry") == q["seed_subentry"],
               f"{qid}: wrong original source/compilation locator")
        topic = row.get("primary_topic_id")
        ensure(topic in OFFICIAL_TOPIC_IDS + ADJUNCT_TOPIC_IDS, f"{qid}: undeclared topic")
        sub = row.get("subtopic_id")
        ensure(isinstance(sub, str) and sub.startswith(topic + "-") and len(sub) > len(topic) + 2,
               f"{qid}: missing/invalid topic-specific subtopic")
        candidate = sub_by_id.get(sub)
        ensure(candidate is not None and candidate.get("topic_id") == topic and
               candidate.get("academic_status") == "PROVISIONAL_FROM_ATTACHMENT" and
               isinstance(candidate.get("title"), str) and candidate["title"] and
               candidate.get("microconcept_ref") == "MIC-" + sub and
               row.get("microconcept_ref") == candidate["microconcept_ref"],
               f"{qid}: missing/ungrounded subtopic and microconcept registry reference")
        used_subtopics.add(sub)
        ensure(isinstance(row.get("learning_demand_summary"), str) and
               len(row["learning_demand_summary"]) >= 15,
               f"{qid}: no specific inferred micro-concept")
        ensure(row.get("source_custody_status") == q["source_custody_status"] and
               row.get("academic_taxonomy_status") == "PROVISIONAL_FROM_ATTACHMENT" and
               row.get("qrt_status") == "NOT_CLASSIFIED" and
               row.get("accepted_primary_qrt_cell") is None and
               row.get("core_eligible") is False,
               f"{qid}: unearned custody/academic/QRT/Core acceptance")
        is_sample = "SAMPLE-" in q["source_id_claim"]
        observed_section = row.get("full_paper_exam_section")
        expected = None if is_sample else full_paper_section(int(q["original_question_number_claim"]))
        ensure(observed_section == expected and
               row.get("section_basis") == (
                   "SAMPLE_SECTION_UNRESOLVED" if is_sample
                   else "SOF_LEVEL1_POSITION_RULE_WITH_PAPER_SOURCE_CLAIM"),
               f"{qid}: source question number misused as Level 1 section")
        if is_sample:
            ev = sample_by_qid.get(qid)
            ensure(ev is not None and
                   ev.get("source_document_ref") == q["source_id_claim"] and
                   ev.get("seed_entry") == q["seed_entry"] and
                   ev.get("sample_question_number") == int(q["original_question_number_claim"]) and
                   ev.get("printed_answer_key_option") == SAMPLE_KEY.get(int(q["original_question_number_claim"])) and
                   ev.get("section_observed") in SECTIONS and
                   row.get("sample_section_observed") == ev["section_observed"] and
                   row.get("sample_section_basis") == "SOF_ORGANIZER_PDF_VISUAL_SECTION_HEADER" and
                   ev.get("academic_answer_status") == "NOT_INDEPENDENTLY_VERIFIED" and
                   ev.get("source_comparison_status") == "SECTION_AND_KEY_PANEL_SIGHTED_ONLY" and
                   ev.get("rights_status") == "NOT_REVIEWED" and
                   ev.get("core_eligible") is False,
                   f"{qid}: organizer sample section/key evidence invalid or overclaimed")
            sample_counts[ev["section_observed"]] += 1
        else:
            ensure(row.get("sample_section_observed") is None and
                   row.get("sample_section_basis") == "NOT_APPLICABLE_FULL_LEVEL1",
                   f"{qid}: unexpected sample metadata on full Level1 paper")
        if observed_section:
            section_counts[observed_section] += 1
        count[topic] += 1
        seen.add(qid)
    ensure(seen == set(q_by_id), "taxonomy coverage is not source-complete")
    ensure(set(sample_by_qid) == {r["question_id"] for r in rows if r["source_id"] == "SOF-IMO-G09-SAMPLE-2026-27"},
           "sample evidence does not cover all sample source positions")
    ensure(used_subtopics == set(sub_by_id), "unused/omitted subtopic catalogue entry")
    by_seed = {q["seed_entry"]: q for q in qs if q["seed_entry"] != 38}
    by_id = {row["question_id"]: row for row in rows}
    ensure(by_id[by_seed[9]["id"]]["full_paper_exam_section"] == "EVERYDAY_MATHEMATICS" and
           by_id[by_seed[65]["id"]]["full_paper_exam_section"] == "ACHIEVERS_SECTION" and
           by_id[by_seed[65]["id"]]["primary_topic_id"] == "NS", "original section/topic independent")
    ensure({by_id[q["id"]]["subtopic_id"] for q in qs if q["seed_entry"] == 38} ==
           {"STATISTICS-PIE-CHARTS"}, "two printed chart questions require separate records")
    missing = [topic for topic in OFFICIAL_TOPIC_IDS if count[topic] == 0]
    return {"result":"PROVISIONAL_TOPIC_COVERAGE_NO_ADMISSION", "mapped_questions":len(seen),
            "official_topics":len(OFFICIAL_TOPIC_IDS), "adjunct_topics":len(ADJUNCT_TOPIC_IDS),
            "provisional_subtopics":len(sub_by_id),
            "by_topic":{t:count[t] for t in OFFICIAL_TOPIC_IDS + ADJUNCT_TOPIC_IDS},
            "uncovered_official_topics":missing, "by_source_section":dict(section_counts),
            "full_paper_section_unknown":len(rows)-sum(section_counts.values()),
            "by_sample_section":dict(sample_counts),
            "organizer_sample_key_sightings":len(sample_by_qid),
            "independently_reviewed_sample_keys":0,
            "accepted_qrt_cells":0, "core_eligible":0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=Path, default=SEED)
    parser.add_argument("--taxonomy", type=Path, default=TAX)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_taxonomy(args.seed, args.taxonomy), sort_keys=True))
    except SeedError as exc:
        parser.exit(1, f"IMO_TAXONOMY_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
