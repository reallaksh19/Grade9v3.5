#!/usr/bin/env python3
"""Fail closed on human-review and rights handoff for SOF IMO source disputes."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from validate_seed import SeedError
from validate_discrepancy_register import validate_register

ROOT = Path(__file__).resolve().parent
QUEUE = ROOT / "review-gates" / "independent-review-queue.v1.json"
SOURCE_REGISTER = ROOT / "adjudication" / "source-discrepancy-register.v1.json"
PROPOSALS = {
    "001":("P1","MATHEMATICS_REVIEWER","SIGNED_DIGIT_COMPUTATION_AND_PRINTED_OPTION_CHECK"),
    "002":("P1","SOURCE_TRANSCRIPTION_REVIEWER","SIGNED_SOURCE_DISTRACTOR_RECONCILIATION"),
    "003":("P1","SOURCE_AND_MATH_REVIEWER","SIGNED_OPTION_REORDER_AND_ADD_INVERSE_CHECK"),
    "004":("P1","FIGURE_AND_SOURCE_REVIEWER","SIGNED_CHART_LABEL_AND_COUNT_CHECK"),
    "005":("P2","SOURCE_SECTION_REVIEWER","SIGNED_PRINTED_SECTION_LOCATOR"),
    "006":("P0","SOURCE_EDITORIAL_AND_MATH_REVIEWER","ORGANIZER_EDITORIAL_RESOLUTION_AND_SIGNED_MATH"),
    "007":("P0","INDEPENDENT_GEOMETRY_REVIEWER","SIGNED_SOURCE_RAY_GEOMETRY_PROOF"),
    "008":("P2","SOURCE_AND_FIGURE_REVIEWER","SIGNED_TWO_ITEM_SINGLE_CHART_CROSSWALK"),
    "009":("P0","INDEPENDENT_GEOMETRY_REVIEWER","SIGNED_ORIGINAL_SAMPLE_Q5_ANGLE_PROOF"),
    "010":("P0","MATHEMATICAL_NOTATION_REVIEWER","SIGNED_NOTATION_TRANSCRIPTION_AND_ROOT_PROOF"),
}
PRIORITIES = {"P0":4,"P1":4,"P2":2}
SOURCE_HOLD_FIELDS = {
    "publisher_rights_holder_identity":"NOT_ESTABLISHED",
    "official_organizer_key_url":None,
    "permission_request_status":"NOT_SENT",
    "permission_request_recipient":None,
    "permission_request_sent_at":None,
    "license_text_evidence_url":None,
    "license_document_sha256":None,
    "rights_review_decision":"NOT_GRANTED_OR_EVIDENCED",
    "figure_and_text_reuse_authorized":False,
    "usage_contexts_authorized":[],
}
ROW_HOLD_FIELDS = {
    "assigned_reviewer_identity":None,
    "source_fidelity_review_status":"AWAITING_INDEPENDENT_SIGNOFF",
    "mathematical_review_status":"AWAITING_INDEPENDENT_SIGNOFF",
    "official_answer_key_or_erratum_status":"NO_NEW_KEY_OR_ERRATUM",
    "licensing_review_status":"UNAUTHORIZED_FOR_REPUBLICATION",
    "signed_source_receipt":None,
    "signed_mathematical_receipt":None,
    "official_key_or_erratum_url":None,
    "source_figure_permission_receipt":None,
    "peer_approval_decision":None,
    "peer_approval_actor":None,
    "peer_approval_timestamp":None,
    "qrt_acceptance_decision":None,
    "accepted_qrt_cell":None,
    "learner_content_eligible":False,
    "review_packet_status":"PREPARED_UNASSIGNED",
    "calculation_provenance":"EXISTING_AGENT_WORK_NOT_PEER_REVIEW",
}


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SeedError(message)


def validate_queue(seed: Path = ROOT / "seed",
                   verify: Path = ROOT / "verification",
                   register: Path = SOURCE_REGISTER,
                   queue: Path = QUEUE) -> dict:
    # The upstream source/option/semantic case register itself must be valid.
    result = validate_register(seed, verify, register)
    ensure(result["cases"]==10 and result["distinct_source_positions_in_cases"]==11,
           "upstream discrepancy register failed expected case census")
    try:
        source=json.loads(register.read_text(encoding="utf-8"))
        data=json.loads(queue.read_text(encoding="utf-8"))
    except (OSError,UnicodeError,json.JSONDecodeError) as exc:
        raise SeedError(f"review gate data unreadable: {exc}") from exc
    ensure(isinstance(data,dict) and data.get("schema")=="sof-imo-g09-independent-review-queue-v1" and
           data.get("source_register_path")==
               "TEST/imo-research/adjudication/source-discrepancy-register.v1.json" and
           data.get("case_count")==10 and data.get("source_position_count")==11 and
           data.get("source_document_count")==4 and data.get("priority_counts")==PRIORITIES and
           all(data.get(k)==0 for k in ("signed_academic_reviews",
               "publisher_license_grants_evidenced","accepted_qrt_cells","core_eligible")),
           "review counts or source authority inflated")
    sources={
        c["original_source_id"]:(c["original_source_url"],c["source_host_class"])
        for c in source["cases"]
    }
    ensure(len(sources)==4,"four distinct source documents expected")
    doc_rows=data.get("source_documents")
    ensure(isinstance(doc_rows,list) and len(doc_rows)==4 and all(isinstance(d,dict) for d in doc_rows),
           "one rights record required for each source document")
    seen_docs=set()
    for doc in doc_rows:
        sid=doc.get("source_id")
        ensure(sid in sources and sid not in seen_docs and
               (doc.get("source_url"),doc.get("source_host_class"))==sources[sid],
               f"{sid}: false or repeated source rights identity")
        for field,expected in SOURCE_HOLD_FIELDS.items():
            ensure(doc.get(field)==expected,
                   f"{sid}: source license, rights, or official-key approval unsupported: {field}")
        ensure(not(set(doc)&{"source_pdf_bytes","original_figure_bytes","license_granted"}),
               f"{sid}: original source rights material not authorized")
        seen_docs.add(sid)
    ensure(seen_docs==set(sources),"source documents omitted from rights queue")
    cases={c["case_id"]:c for c in source["cases"]}
    queue_rows=data.get("records")
    ensure(isinstance(queue_rows,list) and len(queue_rows)==10 and
           all(isinstance(r,dict) for r in queue_rows),"ten case packets required")
    ids=set()
    for row in queue_rows:
        case=row.get("case_id")
        ensure(case in cases and case not in ids,f"unknown/repeated reviewer case {case}")
        sourcecase=cases[case]
        suffix=case[-3:]
        prio,role,receipt=PROPOSALS[suffix]
        ensure(row.get("source_question_ids")==sourcecase["question_ids"] and
               row.get("source_document_id")==sourcecase["original_source_id"] and
               row.get("original_source_url")==sourcecase["original_source_url"] and
               row.get("source_page_index")==sourcecase["source_pdf_page_index"] and
               row.get("original_conflict_type")==sourcecase["conflict_type"] and
               row.get("prior_source_observation_status")==sourcecase["source_finding_status"],
               f"{case}: reviewer queue diverges from source/owner evidence")
        ensure(row.get("priority")==prio and
               row.get("assigned_reviewer_role_required")==role and
               row.get("minimum_receipt_type")==receipt and
               isinstance(row.get("reason_for_priority"),str) and
               len(row["reason_for_priority"])>=65 and
               isinstance(row.get("review_question"),str) and
               len(row["review_question"])>=45 and
               isinstance(row.get("reviewer_requested_action"),str) and
               len(row["reviewer_requested_action"])>=85,
               f"{case}: wrong review priority, reviewer evidence, or vague human task")
        for field,expected in ROW_HOLD_FIELDS.items():
            ensure(row.get(field)==expected,
                   f"{case}: forged human academic, notation, source, QRT or Core approval: {field}")
        ensure(not(set(row)&{"stem","options","source_figure","full_pdf","signed_by_ai"}),
               f"{case}: verbatim question/figure or improper academic identity")
        ids.add(case)
    ensure(ids==set(cases),"one or more source cases lack reviewer packets")
    actual=dict(Counter(r["priority"] for r in queue_rows))
    ensure(actual==PRIORITIES,"priority count drift")
    return {"result":"TEN_REVIEW_PACKETS_PREPARED_NONE_ACCEPTED",
            "review_packets":len(ids),"source_positions":result["distinct_source_positions_in_cases"],
            "distinct_source_rights_holds":len(seen_docs),"urgent_p0":actual["P0"],
            "reviewer_signoffs":0,"source_reuse_grants":0,"accepted_qrt_cells":0,
            "core_eligible":0}


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed",type=Path,default=ROOT/"seed")
    p.add_argument("--verification",type=Path,default=ROOT/"verification")
    p.add_argument("--register",type=Path,default=SOURCE_REGISTER)
    p.add_argument("--queue",type=Path,default=QUEUE)
    args=p.parse_args()
    try:
        print(json.dumps(validate_queue(args.seed,args.verification,args.register,args.queue),
                         sort_keys=True))
    except SeedError as exc:
        p.exit(1,f"IMO_REVIEW_GATES_INVALID: {exc}\n")


if __name__=="__main__":
    main()
