#!/usr/bin/env python3
"""Fail-closed crosswalk of seven SOF-style original-practice research candidates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from validate_seed import SeedError
from validate_intake_contract import validate_contract
from validate_original_practice import validate_original_practice
from validate_practice_diagnostics import validate_diagnostics

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "intake" / "original-practice-qualification-evidence.v1.json"
PRACTICE = ROOT / "original-practice" / "seven-cell-original-problems.v1.json"
DIAGNOSTICS = ROOT / "original-practice" / "diagnostics" / "structured-checker-cases.v1.json"
INTAKE = ROOT / "intake" / "original-practice-intake-contract.v1.json"
POLICY = ROOT / "governance" / "owner-independent-academic-review-waiver.v1.json"
SEED = ROOT / "seed"
BASE_MAIN = "81295f602fb25c8662e56d9aeb29dcd805f45b1c"

# Historic, immutable PR evidence: SUCCESS is asserted only at these PR heads.
RECEIPTS = (
    (270, "bbdbee6c9b056f9843f877a22386468be3d96e5d",
     "1caa71fc3deda2fbff70bed40f0a092a13457bff", 37773725447,
     "SEVEN_ORIGINAL_PRACTICE"),
    (274, "43fff921627df50f80516d00be253289975b7a47",
     "041817515a5b6c7b0fd3bf54ccd12ef203977c60", 37776239987,
     "UNADMITTED_SIX_GATE_INTAKE"),
    (279, "0899532e330a6e3732d9b2ed07283ff234918185",
     "c98122f2c676675590593b926e7e5b18f42a86e8", 37777242871,
     "STRUCTURED_DIAGNOSTIC_RESEARCH"),
)
BLOBS = (
    ("practice", "TEST/imo-research/original-practice/seven-cell-original-problems.v1.json",
     "8ee7cc78f34cc1fa640e4abac84620f43d5538c1"),
    ("diagnostics", "TEST/imo-research/original-practice/diagnostics/structured-checker-cases.v1.json",
     "bf2136743e96e97c323c7fcd6826ef0720a3b3e7"),
    ("intake_snapshot", "TEST/imo-research/intake/original-practice-intake-contract.v1.json",
     "7c243f2ef39190ddb815e67961c2185823e39fe6"),
    ("owner_waiver", "TEST/imo-research/governance/owner-independent-academic-review-waiver.v1.json",
     "b647f1f3998a3d88fa91d99e193aaaf372279a93"),
)
RISKS = (
    ("PROOF_CERTIFICATE_NOT_PROSE_PROOF",
     "Require a learner-facing proof rubric that checks reasoning, not only the true/factor flags in the structured certificate."),
    ("DIRECTION_AND_UNITS_ACCESSIBILITY",
     "Verify screen-reader reading order for signed coordinate pairs, map directions and kilometre units with an actual learner interface."),
    ("ALTITUDE_WORDING_CLARITY",
     "Review whether the phrase perpendicular distance to line AB is clear without a diagram, and test equal-area justification feedback."),
    ("CYLINDER_SCOPE_CLARITY",
     "Check that learners understand only lateral material is used, and that curved-surface versus end-cap feedback is accessible."),
    ("LINEAR_INVERSE_INPUT_FEEDBACK",
     "Test how learners express the line equation and solve the inverse target; structured fields do not assess written working."),
    ("INVOICE_VARIABLE_SEMANTICS",
     "Review booklet and card naming, price units, and explanatory feedback for swapping two simultaneous-equation variables."),
    ("TRANSFORM_ORDER_AND_SIGNED_AREA",
     "Test explanation of reflection-before-translation, vertex labelling and determinant sign versus absolute area in accessible display."),
)
PROBE_COUNTS = (2, 3, 3, 2, 3, 2, 3)
COUNT_FIELDS = dict(
    sample_original_source_positions_unchanged=10,
    owner_seed_positions_unchanged=66,
    fullpaper_attachment_selected_agent_audit_unchanged=58,
    qrt_accepted_cells=0, core_2_admitted=0, core_1a_admitted=0,
    learner_published=0, product_approved=0,
)
TOP_LEVEL_FIELDS = {
    "schema",
    "responsibility",
    "scope",
    "base_main_sha",
    "historical_intake_is_immutable_snapshot",
    "ci_provenance_notice",
    "upstream_receipts",
    "input_git_blobs",
    "academic_peer_review",
    "policy_interpretation",
    "original_sof_text_options_diagrams_reproduced",
    "independently_licensed_source_material",
    "sample_original_source_positions_unchanged",
    "owner_seed_positions_unchanged",
    "fullpaper_attachment_selected_agent_audit_unchanged",
    "qrt_accepted_cells",
    "core_2_admitted",
    "core_1a_admitted",
    "learner_published",
    "product_approved",
    "reviewed_for_accessibility_with_learners",
    "evidence_class",
    "records",
}

ROW_FIELDS = {
    "candidate_id", "source_pr", "intake_pr", "diagnostics_pr",
    "original_practice_row", "structured_diagnostic_row", "provisional_qrt_cell",
    "mathematics_evidence", "mathematical_answer",
    "checked_positive_structured_examples", "checked_misconception_probes",
    "diagnostic_scope", "originality_evidence", "learner_quality_gate",
    "grade9_fit_gate", "quality_hold_code", "quality_hold_action",
    "academic_peer_signature_requirement", "qrt_acceptance",
    "product_owner_decision", "product_owner_identity", "core_2_ready",
    "core_1a_ready", "learner_published", "disposition",
}


def ensure(ok: bool, message: str) -> None:
    if not ok:
        raise SeedError(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SeedError(f"qualification file unreadable: {path}: {exc}") from exc
    ensure(isinstance(value, dict), f"qualification JSON object required: {path}")
    return value


def git_blob_sha(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise SeedError(f"missing pinned research input: {path}: {exc}") from exc
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def validate_qualification(
    ledger: Path = LEDGER, practice: Path = PRACTICE,
    diagnostics: Path = DIAGNOSTICS, intake: Path = INTAKE,
    policy: Path = POLICY, seed: Path = SEED,
) -> dict:
    # These are existing validators; success is research integrity, not external acceptance.
    validate_contract(seed, intake)
    validate_original_practice(seed, practice)
    validate_diagnostics(diagnostics, practice)
    d = read_json(ledger)
    ensure(set(d) == TOP_LEVEL_FIELDS, "unexpected qualification fields or source material")
    p = read_json(practice)
    g = read_json(diagnostics)
    old = read_json(intake)
    waiver = read_json(policy)
    ensure(d.get("schema") == "sof-imo-g09-original-practice-qualification-evidence-v1"
           and d.get("responsibility") ==
           "OWNER_DIRECTED_SEVEN_CANDIDATE_EVIDENCE_RECONCILIATION_2026_10_08"
           and d.get("scope") == "RESEARCH_ONLY_NON_ADMITTING_OVERLAY"
           and d.get("base_main_sha") == BASE_MAIN
           and d.get("historical_intake_is_immutable_snapshot") is True,
           "historical lineage or non-admission intent changed")
    ensure(d.get("ci_provenance_notice") ==
           "Prior focused SUCCESS receipts are GitHub run evidence at their named historical PR heads, not current-head certification or learner approval.",
           "historical CI confused with new PR exact-head result")
    receipts = d.get("upstream_receipts")
    ensure(isinstance(receipts, list) and len(receipts) == 3,
           "three exact upstream PR receipts required")
    for row, (pr, head, merged, run_id, scope) in zip(receipts, RECEIPTS):
        ensure(isinstance(row, dict) and row == dict(
            pr=pr, head_sha=head, merge_commit=merged,
            focused_workflow="SOF IMO research seed integrity",
            run_id=run_id, result="SUCCESS", scope=scope),
            f"PR#{pr} head/merge/run receipt mutated or unproven")
    source_paths = (practice, diagnostics, intake, policy)
    pins = d.get("input_git_blobs")
    ensure(isinstance(pins, list) and len(pins) == 4,
           "four immutable crosswalk input file pins required")
    for pin, (role, path, sha), local_file in zip(pins, BLOBS, source_paths):
        ensure(isinstance(pin, dict) and pin == dict(
            role=role, path=path, blob_sha=sha) and git_blob_sha(local_file) == sha,
            f"{role}: historical source content changed or pin misattributed")
    ensure(old.get("upstream_pr_merge_qualification") == "NOT_YET_VERIFIED"
           and old.get("upstream_merge_head_sha") is None,
           "historical intake snapshot must not be rewritten as a current receipt")
    ensure(waiver.get("effective_policy") ==
           "INDEPENDENT_HUMAN_ACADEMIC_SIGNOFF_NOT_REQUIRED_BY_OWNER"
           and waiver.get("original_human_signoffs_obtained") == 0
           and waiver.get("publisher_redistribution_or_figure_rights_not_waived") is True,
           "human-review waiver is not permission to copy or an expert receipt")
    ensure(d.get("academic_peer_review") ==
           "NOT_APPLICABLE_BY_OWNER_2026_10_08"
           and d.get("policy_interpretation") ==
           "No human academic reviewer required; this does not provide external reviewer signoff, source reuse rights, or product admission."
           and d.get("original_sof_text_options_diagrams_reproduced") is False
           and d.get("independently_licensed_source_material") is False
           and d.get("reviewed_for_accessibility_with_learners") is False
           and d.get("evidence_class") ==
           "MACHINE_CHECKED_RESEARCH_PLUS_PROPOSED_HUMAN_PRODUCT_QA",
           "false source rights, learner usability or human academic signoff")
    ensure(all(type(d.get(k)) is int and d[k] == expected
               for k, expected in COUNT_FIELDS.items()),
           "historical census, QRT/Core, publication or product acceptance inflated")
    rows = d.get("records")
    ensure(isinstance(rows, list) and len(rows) == 7,
           "one qualification packet required per distinct original practice question")
    for index, (row, question, diagnosed, intake_row) in enumerate(
        zip(rows, p["records"], g["records"], old["records"]), start=1
    ):
        qid = f"IMO-G9-ORIGINAL-PRACTICE-{index:03d}"
        ensure(isinstance(row, dict) and set(row) == ROW_FIELDS and
               row.get("candidate_id") == qid == question["id"] ==
               diagnosed["candidate_id"] == intake_row["candidate_id"],
               f"{qid}: duplicated, missing or source-colliding candidate")
        ensure(row.get("source_pr") == 270 and row.get("intake_pr") == 274
               and row.get("diagnostics_pr") == 279
               and type(row.get("original_practice_row")) is int
               and row["original_practice_row"] == index
               and type(row.get("structured_diagnostic_row")) is int
               and row["structured_diagnostic_row"] == index
               and row.get("provisional_qrt_cell") ==
               question["qrt_proposal"]["cell"] ==
               diagnosed["proposed_qrt_cell"] ==
               intake_row["expected_proposal_cell"],
               f"{qid}: proposed QRT or lineage crosswalk mismatch")
        ensure(row.get("mathematics_evidence") ==
               "EXISTING_DETERMINISTIC_ORACLE_PASS_NOT_INDEPENDENT_ACADEMIC_CERTIFICATION"
               and row.get("mathematical_answer") == question["expected_answer"]
               and type(row.get("checked_positive_structured_examples")) is int
               and row["checked_positive_structured_examples"] == 2
               and type(row.get("checked_misconception_probes")) is int
               and row["checked_misconception_probes"] ==
               len(diagnosed["misconception_probes"]) == PROBE_COUNTS[index-1]
               and row.get("diagnostic_scope") ==
               "STRUCTURED_EXAMPLES_NOT_ARBITRARY_FREE_RESPONSE",
               f"{qid}: mathematical or diagnostic evidence overclaimed")
        ensure(row.get("originality_evidence") ==
               "AI_AUTHORED_SOURCE_INDEPENDENCE_CLAIM_REQUIRES_FINAL_CONTENT_CHECK"
               and row.get("learner_quality_gate") ==
               "PENDING_ACCESSIBILITY_WORDING_AND_FEEDBACK_REVIEW"
               and row.get("grade9_fit_gate") == "PENDING_PRODUCT_CURRICULUM_REVIEW"
               and (row.get("quality_hold_code"), row.get("quality_hold_action")) ==
               RISKS[index-1],
               f"{qid}: removed or altered evidence-backed learner-quality hold")
        ensure(row.get("academic_peer_signature_requirement") ==
               "NOT_APPLICABLE_OWNER_POLICY"
               and row.get("qrt_acceptance") is None
               and row.get("product_owner_decision") is None
               and row.get("product_owner_identity") is None
               and row.get("core_2_ready") is False
               and row.get("core_1a_ready") is False
               and row.get("learner_published") is False
               and row.get("disposition") ==
               "HOLD_FOR_SEPARATE_PRODUCT_QRT_AND_LEARNER_QUALITY_DECISION",
               f"{qid}: fabricated QRT, Core, owner or learner publication")
    ensure(sum(r["checked_misconception_probes"] for r in rows) == 18,
           "18 targeted misconception checks missing")
    return dict(result="SEVEN_CANDIDATES_EVIDENCE_RECONCILED_RESEARCH_ONLY",
                upstream_focused_head_receipts=3,
                original_candidates=7, structured_positive_examples=14,
                misconception_probes=18, accepted_qrt_cells=0,
                product_approved=0, core_ready=0, learner_published=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--qualification", type=Path, default=LEDGER)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_qualification(ledger=args.qualification), sort_keys=True))
    except SeedError as exc:
        parser.exit(1, f"IMO_QUALIFICATION_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
