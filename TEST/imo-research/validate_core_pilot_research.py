#!/usr/bin/env python3
"""Validate source-custody census + first mathematical Core1A construction research."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_seed import SeedError, validate as validate_seed
from validate_qualification_evidence import git_blob_sha
from validate_learner_quality import validate_quality

ROOT = Path(__file__).resolve().parent
CENSUS = ROOT / "intake" / "core2-source-custody-eligibility.v1.json"
CONCEPT = ROOT / "intake" / "core1a-number-systems-construction-proposal.v1.json"
SEED = ROOT / "seed" / "questions.jsonl"
SOURCES = ROOT / "seed" / "sources.json"
DISPUTES = ROOT / "adjudication" / "source-discrepancy-register.v1.json"
SAMPLE = ROOT / "verification" / "official-sample-2026-27-new-positions.v1.json"
TOPICS = ROOT / "taxonomy" / "seed-question-topic-map.v1.jsonl"
WAIVER = ROOT / "governance" / "owner-independent-academic-review-waiver.v1.json"
PINS = (
    ("owner_seed","TEST/imo-research/seed/questions.jsonl",
     "6d0e9a1d74403a221362c0121322d885025b11fb"),
    ("source_ledger","TEST/imo-research/seed/sources.json",
     "4057e7642402915e9dacdb4b54fc7fbe9b42867f"),
    ("source_discrepancies",
     "TEST/imo-research/adjudication/source-discrepancy-register.v1.json",
     "4761aecd4e54c0c694026ab10c4aa7cbfa539e56"),
    ("sample_extension",
     "TEST/imo-research/verification/official-sample-2026-27-new-positions.v1.json",
     "95cdfc8dd277b1b9fcd78c05828b501361f1e763"),
    ("topic_mapping","TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl",
     "80816f9bb5a579f4c822a477ce53e8b98be1381b"),
    ("owner_waiver",
     "TEST/imo-research/governance/owner-independent-academic-review-waiver.v1.json",
     "b647f1f3998a3d88fa91d99e193aaaf372279a93"),
)
COMPONENTS = (
    "original_identity", "original_stem", "subparts_conditions",
    "complete_option_order", "source_figures_and_captions",
    "source_hints", "source_answer_rubric"
)
CENSUS_KEYS = {
    "schema","responsibility_issue","governing_scope","research_basis_main_sha",
    "inputs","source_census","canonical_source_custody_required",
    "current_source_eligibility_policy","original_owner_source_seed_not_modified",
    "compiled_owner_answer_and_printed_organizer_key_are_separate_authorities",
    "prior_agent_math_checks_do_not_grant_core2",
    "human_independent_academic_signoff","source_redistribution_license_claimed",
    "accepted_qrt_cells","core2_admitted_positions","core1a_admitted_units",
    "learner_published","records",
}
ROW_KEYS = {
    "question_id","identity_class","origin_scope","source_id",
    "source_host_kind","original_printed_position_claim",
    "original_printed_position_observed","source_document_url",
    "source_locator_pdf_page_index","source_locator_basis",
    "document_retained_sha256","source_text_fidelity_status",
    "source_seed_custody_status","official_printed_key_receipt",
    "agent_mathematical_evidence","provisional_topic_id",
    "source_discrepancy_case_id","material_source_discrepancy_hold",
    "original_sof_media_copied_into_overlay","component_verification",
    "publisher_publication_rights","external_reference_custody_authorized",
    "core2_eligible","core2_admitted","learner_published","disposition",
    "next_source_action"
}
CONCEPT_KEYS = {
    "schema", "responsibility_issue", "base_main_sha", "status",
    "canonical_academic_package_ref", "project_source",
    "syllabus_topic_reference", "official_syllabus_granularity_limit",
    "dedicated_core2_source_question_ref", "author_created_example_ref",
    "authored_example_source_status", "source_question_identity_granted",
    "qrt_cell_accepted", "core1a_admitted", "core2_admitted",
    "learner_published", "research_human_academic_signature_required",
    "product_owner_curriculum_acceptance", "concept_slice", "topic_rollout",
    "next_release_requirement"
}
SOURCE_NAMES = {p[0] for p in PINS}


def ensure(ok: bool,why: str) -> None:
    if not ok:
        raise SeedError(why)


def read(path: Path) -> dict:
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"IMO Core pilot unreadable: {path}: {exc}") from exc
    ensure(isinstance(d,dict), f"{path}: JSON object required")
    return d


def read_lines(path: Path) -> list[dict]:
    try:
        return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()
                if x.strip()]
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"IMO Core research lines unreadable: {path}: {exc}") from exc


def validate_census(
    census: Path = CENSUS, seed: Path = SEED, sources: Path = SOURCES,
    disputes: Path = DISPUTES, sample: Path = SAMPLE, topics: Path = TOPICS,
    waiver: Path = WAIVER,
) -> dict:
    validate_seed(seed.parent)
    d, ledger, differences, addon, policy = tuple(
        read(x) for x in (census,sources,disputes,sample,waiver))
    questions,topic_rows = read_lines(seed),read_lines(topics)
    ensure(set(d) == CENSUS_KEYS and
           d["schema"] == "sof-imo-g09-core2-source-custody-eligibility-census-v1"
           and type(d["responsibility_issue"]) is int
           and d["responsibility_issue"] == 294
           and d["governing_scope"] ==
           "RESEARCH_INVENTORY_NOT_CORE2_CUSTODY_OR_LEARNER_PUBLICATION"
           and d["research_basis_main_sha"] ==
           "9a51fb9ae65a4b81f2dc6b791cbbc4eeba3c4260",
           "invented scope, source authority or extra original content")
    ensure(d["canonical_source_custody_required"] ==
           "SOURCE_DIGEST_PLUS_PRECISE_ITEM_LOCATOR_PLUS_SEVEN_COMPONENT_STATUS_PLUS_RIGHTS_DISPOSITION_PLUS_INDEPENDENT_ACCEPTANCE"
           and d["current_source_eligibility_policy"] ==
           "FAIL_CLOSED_NO_RETAINED_PDF_DIGEST_NO_FULL_SOURCE_CUSTODY_OR_REUSE_RIGHTS",
           "Core2 source custody weakened")
    ensure(d["original_owner_source_seed_not_modified"] is True and
           d["compiled_owner_answer_and_printed_organizer_key_are_separate_authorities"] is True
           and d["prior_agent_math_checks_do_not_grant_core2"] is True and
           d["human_independent_academic_signoff"] ==
           "NOT_APPLICABLE_OWNER_RESEARCH_POLICY"
           and d["source_redistribution_license_claimed"] is False,
           "historic owner waiver or source/rights authority overclaimed")
    ensure(all(type(d.get(k)) is int and d[k] == 0 for k in
               ("accepted_qrt_cells","core2_admitted_positions",
                "core1a_admitted_units","learner_published")),
           "unauthorized QRT, Core or publication")
    expected_files = (seed,sources,disputes,sample,topics,waiver)
    refs = d.get("inputs")
    ensure(isinstance(refs,list) and len(refs) == len(PINS),
           "six exact source input provenance pins mandatory")
    for ref, (role,path,sha),file in zip(refs,PINS,expected_files):
        ensure(isinstance(ref,dict) and ref == dict(
            role=role,path=path,git_blob_sha=sha) and git_blob_sha(file) == sha,
            f"{role}: evidence input drift or ungrounded Git blob")
    ensure({q["id"] for q in questions} == {t["question_id"] for t in topic_rows}
           and len(questions) == len(topic_rows) == 66,
           "topic/seed mapping identity or 66-source census changed")
    ensure(len({q["seed_entry"] for q in questions}) == 65,
           "original source entries/split question changed")
    orig_sample = [q for q in questions if "SAMPLE" in q["source_id_claim"]]
    full = [q for q in questions if "SAMPLE" not in q["source_id_claim"]]
    extra = addon.get("entries",[])
    cases = differences.get("cases",[])
    claims = d.get("source_census")
    ensure(claims == dict(
        owner_compilation_entries_excluding_aliases=65,
        source_seed_positions=66,source_seed_fullpaper_positions=58,
        source_seed_sample_positions=8,additional_organizer_sample_positions=2,
        total_distinct_source_positions=68,source_discrepancy_cases=10,
        source_discrepancy_printed_positions=11)
        and len(full) == 58 and len(orig_sample) == 8 and len(extra) == 2
        and len(cases) == 10 and sum(len(c["question_ids"]) for c in cases) == 11,
        "source overlap/extra two sample positions or dispute cases mishandled")
    ensure(policy.get("effective_policy") ==
           "INDEPENDENT_HUMAN_ACADEMIC_SIGNOFF_NOT_REQUIRED_BY_OWNER"
           and policy.get("publisher_redistribution_or_figure_rights_not_waived") is True,
           "research peer-review waiver cannot grant SOF rights")
    source_by_id = {s["source_id"]:s for s in ledger["sources"]}
    ensure(len(source_by_id) == 4 and
           all(s["document_sha256"] is None and s["rights_status"] == "NOT_REVIEWED"
               for s in source_by_id.values()),
           "this pinned corpus lacks source bytes/rights; refresh overlay if changed")
    case_by_id = {}
    for case in cases:
        for id in case["question_ids"]:
            ensure(id not in case_by_id,"multiple dispute cases for one printed position")
            case_by_id[id] = case
    topic_by_id = {t["question_id"]: t for t in topic_rows}
    expected_seed = {q["id"]:q for q in questions}
    expected_extra = {q["question_id"]:q for q in extra}
    ensure(not (set(expected_seed)&set(expected_extra)) and
           len(expected_seed) == 66 and len(expected_extra) == 2,
           "sample extension must add two *new* original source positions")
    rows = d.get("records")
    ensure(isinstance(rows,list) and len(rows) == 68 and
           all(isinstance(row,dict) and set(row) == ROW_KEYS for row in rows),
           "68 full per-position, field-closed custody rows required")
    ids = [r["question_id"] for r in rows]
    ensure(len(set(ids)) == len(ids) and set(ids) ==
           set(expected_seed)|set(expected_extra),
           "missing/duplicate/novel source question IDs")
    ensure(ids == sorted(ids,key=lambda i:(
        ("FULLPAPER_OWNER_SEED_POSITION" if i in expected_seed and
         "SAMPLE" not in expected_seed[i]["source_id_claim"] else
         "ORGANIZER_SAMPLE_SEED_POSITION" if i in expected_seed else
         "ORGANIZER_SAMPLE_ADDITIONAL_POSITION"),i)),
           "source row sort changed unexpectedly")
    for row in rows:
        id = row["question_id"]
        seeded = expected_seed.get(id)
        if seeded:
            source_id = seeded["source_id_claim"]
            source = source_by_id[source_id]
            case = case_by_id.get(id)
            sample_row = "SAMPLE" in source_id
            expected = {
              "identity_class":"OWNER_COMPILATION_SEED_CLAIM_NOT_VERIFIED_SOURCE",
              "origin_scope":"ORGANIZER_SAMPLE_SEED_POSITION" if sample_row else
                             "FULLPAPER_OWNER_SEED_POSITION",
              "source_id":source_id,"source_host_kind":source["host_type"],
              "original_printed_position_claim":seeded["original_question_number_claim"],
              "original_printed_position_observed":(
                  str(seeded["original_question_number_claim"])
                  if case and int(seeded["original_question_number_claim"]) in case["source_numbers"]
                  else None),
              "source_document_url":addon["official_source_url"] if sample_row
                                    else source["url"],
              "source_locator_pdf_page_index":(
                  case["source_pdf_page_index"] if case else None),
              "source_locator_basis":(
                  "DISCREPANCY_REGISTER_SCAN_OBSERVATION" if case
                  else "INSUFFICIENT_ITEM_LOCATOR"),
              "document_retained_sha256":source["document_sha256"],
              "source_text_fidelity_status":seeded["transcription_status"],
              "source_seed_custody_status":seeded["source_custody_status"],
              "official_printed_key_receipt":"NOT_ESTABLISHED_FOR_CORE2",
              "agent_mathematical_evidence":
                  "SEPARATE_RESEARCH_AGENT_WORK_NOT_ACADEMIC_APPROVAL",
              "provisional_topic_id":topic_by_id[id]["primary_topic_id"],
              "source_discrepancy_case_id":case["case_id"] if case else None,
              "material_source_discrepancy_hold":bool(case),
              "next_source_action":(
                  "Resolve specific printed-versus-owner discrepancy with retained source bytes, complete item-component checks, and rights disposition."
                  if case else
                  "Acquire/retain original PDF digest, establish exact printed item locator, check every source component, and record reproduction/external-reference rights.")
            }
        else:
            question = expected_extra[id]
            expected = {
              "identity_class":"SOF_ORGANIZER_SAMPLE_NEW_POSITION_AGENT_OBSERVED",
              "origin_scope":"ORGANIZER_SAMPLE_ADDITIONAL_POSITION",
              "source_id":question["source_id"],
              "source_host_kind":"SOF_ORGANIZER_HOSTED_PDF",
              "original_printed_position_claim":str(question["sample_question_number"]),
              "original_printed_position_observed":str(question["sample_question_number"]),
              "source_document_url":addon["official_source_url"],
              "source_locator_pdf_page_index":question["original_page_index"],
              "source_locator_basis":
                  "ORGANIZER_SAMPLE_AGENT_SCAN_OBSERVATION_NOT_COMPLETE_CUSTODY",
              "document_retained_sha256":None,
              "source_text_fidelity_status":"DIAGRAM_REQUIRES_COMPONENT_VERIFICATION",
              "source_seed_custody_status":"NOT_IN_66_OWNER_SEED",
              "official_printed_key_receipt":
                  "SAMPLE_SOURCE_KEY_OBSERVED_NOT_CORE2_VERIFIED",
              "agent_mathematical_evidence":
                  "SEPARATE_RESEARCH_AGENT_WORK_NOT_ACADEMIC_APPROVAL",
              "provisional_topic_id":question["primary_topic_proposal"],
              "source_discrepancy_case_id":None,
              "material_source_discrepancy_hold":False,
              "next_source_action":
                  "Retain and digest organizer PDF, verify full figure and item components including exact page locator and source key, then determine rights/externally referenced custody."
            }
        for name,value in expected.items():
            ensure(row.get(name) == value,
                   f"{id}: unsupported source locator/topic, separate key, discrepancy or next step: {name}")
        ensure(row["original_sof_media_copied_into_overlay"] is False
               and row["component_verification"] ==
                   {name:"NOT_FULLY_COMPONENT_VERIFIED" for name in COMPONENTS}
               and row["publisher_publication_rights"] == "NOT_REVIEWED"
               and row["external_reference_custody_authorized"] is False
               and row["core2_eligible"] is False
               and row["core2_admitted"] is False
               and row["learner_published"] is False
               and row["disposition"] ==
                    "HOLD_SOURCE_BYTE_DIGEST_COMPONENT_CUSTODY_AND_RIGHTS",
               f"{id}: full source-custody/rights or eligibility fabricated")
    return dict(
        result="SIXTY_EIGHT_SOURCE_POSITIONS_CUSTODY_HELD",
        owner_seed_positions=66,additional_sample_positions=2,
        source_positions=68,source_conflict_cases=10,affected_positions=11,
        retained_source_pdf_digests=0,core2_eligible=0,core2_admitted=0,
        accepted_qrt_cells=0,learner_published=0)


def validate_concept(
    concept: Path = CONCEPT, census: Path = CENSUS,
) -> dict:
    validate_census(census)
    d = read(concept)
    ensure(set(d) == CONCEPT_KEYS and
           d["schema"] ==
             "sof-imo-g09-core1a-canonical-teaching-construction-proposal-v1"
           and d["responsibility_issue"] == 294
           and d["base_main_sha"] ==
             "9a51fb9ae65a4b81f2dc6b791cbbc4eeba3c4260"
           and d["status"] == "PRE_CANONICAL_TEST_DESIGN_NOT_CORE1A_LEARNER_PRODUCT"
           and d["canonical_academic_package_ref"] is None
           and d["project_source"] ==
             "MATHEMATICS_DOMAIN_REASONING_INDEPENDENT_OF_SOF_SOURCE_ANSWER_KEYS"
           and d["syllabus_topic_reference"] ==
             "TEST/imo-research/taxonomy/sof-class9-topic-registry.v1.json#NS"
           and d["official_syllabus_granularity_limit"] ==
             "NUMBER_SYSTEMS_TOPIC_OBSERVED_NO_OFFICIAL_DIVISIBILITY_SUBTOPIC_CERTIFICATION",
           "candidate construction must not pretend canonical/syllabus acceptance")
    ensure(d["dedicated_core2_source_question_ref"] is None
           and d["author_created_example_ref"] == "IMO-G9-ORIGINAL-PRACTICE-001"
           and d["authored_example_source_status"] ==
               "MODEL_AUTHORED_NOT_SOF_SOURCE_NOT_CORE2"
           and d["source_question_identity_granted"] is False
           and d["qrt_cell_accepted"] is False
           and d["core1a_admitted"] is False and d["core2_admitted"] is False
           and d["learner_published"] is False
           and d["research_human_academic_signature_required"] is False
           and d["product_owner_curriculum_acceptance"] is None
           and d["next_release_requirement"] ==
            "FORMAL_CANONICAL_PACKAGE_ACCEPTANCE_PLUS_REAL_SOURCE_CUSTODY_FOR_CORE2_PLUS_RIGHTS_REVIEW_PLUS_EXACT_RENDER_QA_PLUS_DATED_OWNER_DECISION",
           "authored practice relabelled as source or Core1A accepted")
    s = d.get("concept_slice")
    keys = {"proposal_id","bucket_ref_candidate","capability_ref_candidate",
            "microtopic_ref_candidate","intrinsic_badge_proposal",
            "intrinsic_badge_reason","entry_assumptions","initial_conventions",
            "inferential_jump","representation_bridges",
            "completed_teaching_path","misconception_repair",
            "independent_reverse_checks","worked_concept_anchor",
            "exit_task","safety_limits"}
    ensure(isinstance(s,dict) and set(s) == keys and
           s["proposal_id"] == "IMO-G9-CORE1A-NS-CONSECUTIVE-DIVISIBILITY-001"
           and all(str(s[field]).endswith("CANDIDATE") for field in
                   ("bucket_ref_candidate","capability_ref_candidate",
                    "microtopic_ref_candidate"))
           and s["intrinsic_badge_proposal"] == "HARD",
           "canonical inference reference or intrinsic depth was fabricated")
    for key,count in (("entry_assumptions",4),("initial_conventions",3),
                      ("representation_bridges",3),("completed_teaching_path",4),
                      ("independent_reverse_checks",2),("safety_limits",3)):
        ensure(isinstance(s.get(key),list) and len(s[key]) == count,
               f"missing essential mathematical teaching operator {key}")
    ensure(len(s["inferential_jump"]) >= 135 and
           "coprime" in s["inferential_jump"],
           "Core1A decisive universal reasoning cannot disappear")
    for index,bridge in enumerate(s["representation_bridges"],start=1):
        ensure(isinstance(bridge,dict) and set(bridge) ==
               {"kind","verbal","symbolic","visual_spec"} and
               all(isinstance(bridge[k],str) and len(bridge[k]) >= 10
                   for k in ("verbal","symbolic","visual_spec")),
               f"representation {index}: no two-way words/symbols/visual plan")
    ensure([step.get("step_ref") for step in s["completed_teaching_path"]] ==
           [f"STEP-{i:02d}" for i in range(1,5)],
           "Core1A four-step inferential route lost")
    for step in s["completed_teaching_path"]:
        ensure(set(step) == {"step_ref","action","why_valid"}
               and len(step["action"]) >= 70
               and len(step["why_valid"]) >= 80,
               "conclusion asserted without inferential justification")
    repair = s.get("misconception_repair",{})
    ensure(set(repair) == {"code","wrong_idea","diagnostic_prompt","repair"}
           and repair["code"] == "EXAMPLE_ONLY" and
           all(len(repair[k]) >= 55 for k in
               ("wrong_idea","diagnostic_prompt","repair")),
           "must diagnose example-only false universal proof")
    anchor = s.get("worked_concept_anchor",{})
    ensure(set(anchor) == {"status","prompt","model_answer",
                           "source_identity_claim"}
           and anchor["status"] == "NEWLY_AUTHORED_TEACHING_ANCHOR_NOT_SOF_SOURCE"
           and anchor["source_identity_claim"] is False
           and len(anchor["model_answer"]) >= 140,
           "original authored worked concept anchor not SOF source")
    exit_task = s.get("exit_task",{})
    ensure(set(exit_task) == {"prompt","answer","check"}
           and "divisible by 24" in exit_task["prompt"]
           and "divisible by 4" in exit_task["answer"]
           and "divisible by 8" in exit_task["answer"]
           and "gcd(8,3)=1" in exit_task["answer"]
           and len(exit_task["check"]) >= 95,
           "four-successive-integers exit proof or independent check missing")
    # For polynomial products, a complete residue set modulo the divisor
    # establishes the modular identity for every integer, not just sampled n.
    ensure(all(n*(n+1)*(n+2)%6 == 0 for n in range(6))
           and all(n*(n+1)*(n+2)*(n+3)%24 == 0 for n in range(24)),
           "modular proof or exit invariant contradicted")
    rollout = d.get("topic_rollout")
    expected = (
       ("NS",("001",),"INITIAL_HARD_CONCEPT_SLICE","PROPOSED_NOT_CANONICAL"),
       ("COORD",("002","007"),"NEXT_CONCEPT_CLUSTER_WITH_EXTENSION_HOLD_007",
        "NOT_AUTHORED"),
       ("TRIANGLE_AREAS",("003",),"NEXT_CONCEPT_CLUSTER","NOT_AUTHORED"),
       ("MENSURATION",("004",),"NEXT_CONCEPT_CLUSTER","NOT_AUTHORED"),
       ("LIN_EQ",("005","006"),"NEXT_CONCEPT_CLUSTER_WITH_EXTENSION_HOLD_006",
        "NOT_AUTHORED")
    )
    ensure(isinstance(rollout,list) and len(rollout) == 5,
           "five topic-cluster rollout inventory mandatory")
    for row,(topic,ids,role,stage) in zip(rollout,expected):
        ensure(isinstance(row,dict) and row == dict(
            topic_id=topic,
            original_practice_ids=[
                "IMO-G9-ORIGINAL-PRACTICE-"+suff for suff in ids],
            role=role,core1a_design=stage,core2_source_ready=False),
            "invented Core2 custody, Core1A completion, or missing extension hold")
    return dict(result="CORE1A_NUMBER_SYSTEMS_CONSTRUCTION_PROPOSED_NOT_ADMITTED",
                complete_teaching_steps=4,
                topic_clusters=5,source_backed_core2_anchors=0,
                canonical_microtopics_admitted=0,
                qrt_accepted=0,learner_published=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--census",type=Path,default=CENSUS)
    parser.add_argument("--concept",type=Path,default=CONCEPT)
    args = parser.parse_args()
    try:
        validate_quality()
        print(json.dumps({"census":validate_census(args.census),
                          "core1a":validate_concept(args.concept,args.census)},
                         sort_keys=True))
    except SeedError as exc:
        parser.exit(1, f"IMO_CORE_PILOT_RESEARCH_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
