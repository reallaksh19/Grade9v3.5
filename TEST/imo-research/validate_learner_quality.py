#!/usr/bin/env python3
"""Fail-closed research-only learner-quality proposal checks for seven SOF-style originals."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_seed import SeedError
from validate_qualification_evidence import validate_qualification, git_blob_sha

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "original-practice" / "learner-quality-proposals.v1.json"
LEDGER = ROOT / "intake" / "original-practice-qualification-evidence.v1.json"
PRACTICE = ROOT / "original-practice" / "seven-cell-original-problems.v1.json"
DIAGNOSTICS = ROOT / "original-practice" / "diagnostics" / "structured-checker-cases.v1.json"
SYLLABUS = ROOT / "taxonomy" / "sof-class9-topic-registry.v1.json"
SOURCE_PATHS = (
    ("qualification_overlay",
     "TEST/imo-research/intake/original-practice-qualification-evidence.v1.json",
     "6197814723cc7082e332dcd3c68e0d56b8fad98b"),
    ("authored_practice",
     "TEST/imo-research/original-practice/seven-cell-original-problems.v1.json",
     "8ee7cc78f34cc1fa640e4abac84620f43d5538c1"),
    ("structured_diagnostics",
     "TEST/imo-research/original-practice/diagnostics/structured-checker-cases.v1.json",
     "bf2136743e96e97c323c7fcd6826ef0720a3b3e7"),
    ("syllabus_registry",
     "TEST/imo-research/taxonomy/sof-class9-topic-registry.v1.json",
     "718b227c475e5d593b6b3254146a0432a64ea90c"),
)
TOPICS = ("NS", "COORD", "TRIANGLE_AREAS", "MENSURATION",
          "LIN_EQ", "LIN_EQ", "COORD")
HOLDS = (
    "PROOF_CERTIFICATE_NOT_PROSE_PROOF", "DIRECTION_AND_UNITS_ACCESSIBILITY",
    "ALTITUDE_WORDING_CLARITY", "CYLINDER_SCOPE_CLARITY",
    "LINEAR_INVERSE_INPUT_FEEDBACK", "INVOICE_VARIABLE_SEMANTICS",
    "TRANSFORM_ORDER_AND_SIGNED_AREA",
)
CODES = ("EXAMPLE_ONLY", "AXES_SWAPPED", "SLANTED_HEIGHT", "END_CAPS_INCLUDED",
         "DELTA_X_IGNORED", "UNIT_PRICES_SWAPPED",
         "REFLECTION_TRANSLATION_MISORDER")
# Deliberately include the actual diagnostic category, not an inferred error.
TOP_LEVEL = {
    "schema", "issue", "owner_instruction", "base_main_sha", "provenance",
    "evidence_limits", "third_party_sof_exam_stems_options_figures_copied",
    "official_sof_syllabus_topic_crosswalk_is_only_provisional",
    "source_owner_seed_positions_unchanged",
    "agent_audited_attachment_fullpaper_positions_unchanged",
    "organizer_sample_source_positions_unchanged", "historical_qrt_accepted_cells",
    "product_approved", "core_2_ready", "core_1a_ready", "learner_published",
    "records",
}
ROW_FIELDS = {
    "candidate_id", "inherited_hold_code", "proposed_syllabus_topic_id",
    "topic_alignment", "scope_review_note", "wording_risk",
    "learner_support_prompt_draft", "spoken_math_text_draft",
    "accessible_response_capture_spec", "targeted_misconception_code",
    "non_answer_leading_feedback_draft", "scope", "actual_screen_reader_audit",
    "learner_comprehension_test", "independent_curriculum_review",
    "authoring_change_to_source_question", "source_independence_review",
    "academic_human_signoff_requirement", "proposed_qrt_only",
    "accepted_qrt_cell", "core_2_ready", "core_1a_ready",
    "learner_published", "owner_product_approval", "next_action",
}
COUNTS = {
    "source_owner_seed_positions_unchanged": 66,
    "agent_audited_attachment_fullpaper_positions_unchanged": 58,
    "organizer_sample_source_positions_unchanged": 10,
    "historical_qrt_accepted_cells": 0, "product_approved": 0,
    "core_2_ready": 0, "core_1a_ready": 0, "learner_published": 0,
}


def ensure(predicate: bool, error: str) -> None:
    if not predicate:
        raise SeedError(error)


def read(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"learner-quality evidence unreadable: {path}: {exc}") from exc
    ensure(isinstance(data, dict), f"{path}: JSON object expected")
    return data


def validate_quality(
    file: Path = DATA, ledger: Path = LEDGER, practice: Path = PRACTICE,
    diagnostics: Path = DIAGNOSTICS, syllabus: Path = SYLLABUS,
) -> dict:
    # The upstream validator also executes source, math, intake and diagnostic checks.
    validate_qualification()
    d, prior, problems, probes, registry = tuple(
        read(p) for p in (file, ledger, practice, diagnostics, syllabus)
    )
    ensure(set(d) == TOP_LEVEL
           and d["schema"] == "sof-imo-g09-original-practice-learner-quality-proposals-v1"
           and type(d["issue"]) is int and d["issue"] == 292
           and d["owner_instruction"] == "PROCEED_2026_10_08"
           and d["base_main_sha"] == "5ce1737573715e7b52dc93fa7993cbb8e3d7b7f8",
           "wrong learner-quality version/issue/base or unreviewed top-level material")
    ensure(d["evidence_limits"] ==
           "Text-only analyst-drafted accessibility, readability, response collection and feedback proposals. No browser, assistive technology, learner, expert or owner testing occurred."
           and d["third_party_sof_exam_stems_options_figures_copied"] is False
           and d["official_sof_syllabus_topic_crosswalk_is_only_provisional"] is True,
           "research proposals misreported as accessibility, curricular or reuse approval")
    ensure(all(type(d.get(k)) is int and d[k] == value
               for k, value in COUNTS.items()),
           "historical source/QRT/Core/learner status inflated")
    paths = (ledger, practice, diagnostics, syllabus)
    ensure(isinstance(d["provenance"], list) and len(d["provenance"]) == 4,
           "four source Git blob references required")
    for ref, path, (role, source, sha) in zip(d["provenance"], paths, SOURCE_PATHS):
        ensure(isinstance(ref, dict) and ref == {
            "role": role, "path": source, "git_blob_sha": sha
        } and git_blob_sha(path) == sha, f"{role}: stale or false provenance")
    ensure(registry.get("authority_claim") == "SOF_ORGANIZER_HOSTED_SYLLABUS_PAGE"
           and registry.get("grade") == 9
           and registry.get("disposition") ==
           "RESEARCH_TAXONOMY_NOT_ACADEMICALLY_ACCEPTED",
           "syllabus authority or academic status unsupported")
    allowed = {
        entry["topic_id"] for entry in registry["official_topics"]
        if entry.get("official_syllabus") is True
    }
    ensure(len(allowed) == 17, "official topic census changed")
    rows = d.get("records")
    ensure(isinstance(rows, list) and len(rows) == 7,
           "seven learner-quality packets required")
    for index, (row, historical, question, diagnostic) in enumerate(
        zip(rows, prior["records"], problems["records"], probes["records"])
    ):
        name = f"IMO-G9-ORIGINAL-PRACTICE-{index+1:03d}"
        ensure(isinstance(row, dict) and set(row) == ROW_FIELDS
               and row["candidate_id"] == name ==
               historical["candidate_id"] == question["id"] ==
               diagnostic["candidate_id"],
               f"{name}: missing, duplicated or extra fields or source identity mismatch")
        ensure(row["inherited_hold_code"] == HOLDS[index] ==
               historical["quality_hold_code"],
               f"{name}: historical hold incorrectly closed or swapped")
        ensure(row["proposed_syllabus_topic_id"] == TOPICS[index]
               and row["proposed_syllabus_topic_id"] in allowed,
               f"{name}: inferred or nonofficial syllabus topic")
        expected_scope = ("POTENTIAL_ABOVE_GRADE9_EXTENSION" if index in (5, 6)
                          else "TOPIC_MATCH_NOT_GRADE_ATTAINMENT")
        ensure(row["topic_alignment"] == expected_scope
               and isinstance(row["scope_review_note"], str)
               and len(row["scope_review_note"]) >= 70,
               f"{name}: provisional grade-scope caveat missing")
        if index == 5:
            ensure("simultaneous-equation" in row["scope_review_note"],
                   f"{name}: simultaneous-equation scope unresolved")
        if index == 6:
            ensure("determinant" in row["scope_review_note"],
                   f"{name}: extended determinant scope unresolved")
        ensure(row["targeted_misconception_code"] == CODES[index] and
               row["targeted_misconception_code"] in {
                   m["code"] for m in diagnostic["misconception_probes"]
               }, f"{name}: feedback no longer tied to diagnosed error")
        for field, minimum in (
            ("wording_risk", 65),
            ("learner_support_prompt_draft", 80),
            ("spoken_math_text_draft", 90),
            ("accessible_response_capture_spec", 110),
            ("non_answer_leading_feedback_draft", 95),
        ):
            value = row.get(field)
            ensure(isinstance(value, str) and len(value) >= minimum
                   and "APPROVED" not in value.upper()
                   and "CERTIFIED" not in value.upper(),
                   f"{name}: empty/overclaiming proposed {field}")
        matched_hint = next(
            m["actionable_hint"] for m in diagnostic["misconception_probes"]
            if m["code"] == row["targeted_misconception_code"]
        )
        ensure(row["non_answer_leading_feedback_draft"] != matched_hint,
               f"{name}: proposed feedback must be separately authored")
        ensure(row["scope"] == "STATIC_ANALYST_DESIGN_PROPOSAL"
               and row["actual_screen_reader_audit"] == "NOT_PERFORMED"
               and row["learner_comprehension_test"] == "NOT_PERFORMED"
               and row["independent_curriculum_review"] == "NOT_PERFORMED"
               and row["source_independence_review"] == "PENDING"
               and row["authoring_change_to_source_question"] is False
               and row["academic_human_signoff_requirement"] ==
               "NOT_APPLICABLE_OWNER_2026_10_08"
               and row["proposed_qrt_only"] is True
               and row["accepted_qrt_cell"] is None
               and row["owner_product_approval"] is None
               and row["core_2_ready"] is False and
               row["core_1a_ready"] is False and
               row["learner_published"] is False and row["next_action"] ==
               "VALIDATE_DESIGN_WITH_LEARNER_SURFACE_AND_OWNER_CURRICULUM_REVIEW",
               f"{name}: invented learner validation, academic review or publication")
    return {
        "result": "SEVEN_LEARNER_QUALITY_DESIGN_PROPOSALS_ONLY",
        "candidate_packets": 7, "draft_feedback_revisions": 7,
        "provisional_official_topic_matches": 7,
        "possible_grade9_extension_holds": 2,
        "screen_reader_tests_performed": 0,
        "learner_tests_performed": 0,
        "qrt_accepted": 0, "core_ready": 0, "learner_published": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", type=Path, default=DATA)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_quality(file=args.file), sort_keys=True))
    except SeedError as exc:
        parser.exit(1, f"IMO_LEARNER_QUALITY_INVALID: {exc}\\n")


if __name__ == "__main__":
    main()
