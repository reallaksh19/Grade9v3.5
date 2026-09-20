#!/usr/bin/env python3
"""Resolve a short human authoring request before any learner-facing content is authored."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import ContractError, load
from Shared.library.compile_inputs import compile_bucket
from Shared.library.practice_inventory import coverage as practice_coverage
from Shared.library.resolve import build_index, load_packages
from Shared.tools import (academic_readiness, atlas_need, capability_graph, core_focus,\n                          focus_inventory, learner_evidence, resolve_request, source_receipts)

ALL_CORES = ("CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
PERSONALISED_TEACHING = ("CORE1A", "CORE1B")
PRACTICE = ("CORE2A", "CORE2B")
LEARNER_ROUTED = PERSONALISED_TEACHING + PRACTICE
SOURCE_PRODUCTS = ("CORE2", "CORE2A", "CORE2B")
SCHEMA = REPO / "Shared/library/authoring-request.schema.json"
FIXTURE_GLOB = "*.plan-request.json"


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _boards(subject: str, repo: Path) -> list[dict]:
    rows = []
    for path in sorted((repo / subject / "matrices").glob("*.rungs.json")):
        board = load(path)
        rows.append({**board, "_path": str(path.relative_to(repo))})
    return rows


def resolve_board(request: dict, repo: Path = REPO) -> tuple[dict | None, list[dict]]:
    boards = _boards(request.get("subject", ""), repo)
    bucket = request.get("bucket_id")
    if bucket:
        matches = [b for b in boards if b.get("bucket_id") == bucket]
    else:
        needle = _norm(request.get("subtopic", ""))
        matches = [b for b in boards if needle and needle in {
            _norm(b.get("subtopic", "")), _norm(b.get("bucket_id", "")),
        }]
    if len(matches) == 1:
        return matches[0], []
    if not matches:
        return None, [{"point": "AUTHORING_REQUEST_SUBTOPIC_UNRESOLVED",
                       "where": request.get("subtopic") or bucket or "",
                       "detail": "no matrix resolves this subject/subtopic request"}]
    return None, [{"point": "AUTHORING_REQUEST_SUBTOPIC_AMBIGUOUS",
                   "where": request.get("subtopic") or bucket or "",
                   "detail": f"matches {', '.join(b['bucket_id'] for b in matches)}"}]


def _records(subject: str, repo: Path) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def _compiler_support(records: dict, board: dict, subject: str) -> tuple[set[str], str | None]:
    try:
        compiled = compile_bucket(
            records, board["bucket_id"], topic_id=f'PLAN-{board["bucket_id"]}',
            title=board.get("subtopic") or board["bucket_id"], subject=subject,
            practice_control={"mode": "PLAN_ONLY", "purpose": "PRACTICE"},
        )
    except ContractError as exc:
        return set(), f"{exc.code}: {exc.detail}"
    return set(compiled["baseline"]["selected_cores"]), None


def _learner_route(request: dict, board: dict, caps: dict, mics: dict,
                   repo: Path) -> dict:
    learner = request.get("learner")
    if not learner:
        return {"state": "WAITING_FOR_OWNER_INPUT", "entry": None,
                "bridges": [], "unresolved": []}
    rows = sorted(board.get("rungs", []), key=lambda r: r.get("ladder_position", 0))
    held = {}
    if "profile_ref" in learner:
        profile = resolve_request.profiles(repo).get(learner["profile_ref"])
        if profile is None:
            return {"state": "BLOCKED", "entry": None, "bridges": [],
                    "unresolved": [learner["profile_ref"]], "reason": "PROFILE_REF_DANGLING"}
        held = learner_evidence.effective_held(profile, repo)
        candidate = resolve_request.entry_from_profile(
            rows, {**profile, "held": held}, caps, mics)
    elif "owner_entry" in learner:
        candidate = {"rung": learner["owner_entry"].get("rung"), "why": "OWNER_NAMED"}
    elif "owner_estimate" in learner:
        estimate = resolve_request.resolve_owner_estimate(
            rows,
            learner["owner_estimate"].get("knowledge_percentage"),
            caps,
            mics,
        )
        if not estimate.get("rung"):
            return {
                "state": "BLOCKED",
                "entry": None,
                "bridges": [],
                "prerequisite_checks": [],
                "unresolved": estimate.get("unresolved_prerequisites", []),
                "reason": estimate.get("why"),
                "detail": estimate.get("detail"),
            }
        state = (
            "BLOCKED"
            if estimate.get("unresolved_prerequisites")
            else ("READY_WITH_CHECKS" if estimate.get("prerequisite_checks") else "READY")
        )
        return {
            "state": state,
            "entry": estimate["rung"],
            "requested_entry": estimate["rung"],
            "selected_by": estimate.get("why"),
            "bridges": [],
            "prerequisite_checks": estimate.get("prerequisite_checks", []),
            "unresolved": estimate.get("unresolved_prerequisites", []),
            "route_reason": "OWNER_ESTIMATE_START_HERE_CHECK_PREREQUISITES_IF_NEEDED",
        }
    elif "unknown" in learner:
        return {"state": "BLOCKED", "entry": None, "bridges": [], "unresolved": [],
                "reason": "LEARNER_ENTRY_EXPLICITLY_UNKNOWN",
                "detail": "owner explicitly supplied no learner-entry evidence"}
    else:
        return {"state": "BLOCKED", "entry": None, "bridges": [], "unresolved": [],
                "reason": "LEARNER_ENTRY_UNRECOGNISED"}
    if not candidate.get("rung"):
        return {"state": "BLOCKED", "entry": None, "bridges": [], "unresolved": [],
                "reason": candidate.get("why"), "detail": candidate.get("detail")}
    resolved = capability_graph.resolve_entry(rows, candidate["rung"], held, caps, mics)
    if resolved["unresolved"]:
        state = "BLOCKED"
    elif resolved["bridges"]:
        state = "READY_WITH_BRIDGES"
    else:
        state = "READY"
    return {"state": state, "entry": resolved["rung"],
            "requested_entry": candidate["rung"], "selected_by": candidate.get("why"),
            "bridges": resolved["bridges"], "prerequisite_checks": [],
            "unresolved": resolved["unresolved"],
            "route_reason": resolved["reason"]}


def _rung_inventory(board: dict, mics: dict) -> list[dict]:
    """Keep existence, matrix provenance, library status and source refs on separate axes."""
    rows = []
    for row in board.get("rungs", []):
        record = mics.get(row.get("microtopic_ref"))
        rows.append({
            "rung": row["rung"],
            "position": row["ladder_position"],
            "default_entry_eligible": row.get("default_entry_eligible", True),
            "microtopic": row.get("microtopic_ref"),
            "existence": "PRESENT" if record else "ABSENT",
            "matrix_provenance": row.get("provenance"),
            "library_record_status": record.get("status") if record else None,
            "source_refs": list(record.get("source_refs") or []) if record else [],
        })
    return rows


def lifecycle_handoff(report: dict) -> dict:
    """Keep authoring, product build and learner release as distinct transitions.

    Human academic review gates RELEASE, not AUTHORING. Otherwise a candidate could never
    be written before it was reviewed. Build readiness remains stricter than authoring:
    missing assets may be legitimate authoring work but they are not buildable products.
    """
    structural = [f["point"] for f in report.get("findings", [])]
    owner = [row["id"] for row in report.get("required_owner_inputs", [])]
    actions = [row["id"] for row in report.get("agent_actions", [])]
    product_holds = [
        f'{row["core"]}:{row["state"]}' for row in report.get("products", [])
        if row["state"] not in {"READY", "WITHHELD"}
    ]

    authoring_blockers = sorted(set(structural + owner + actions))
    build_blockers = sorted(set(authoring_blockers + product_holds))
    release_blockers = list(build_blockers)
    academic = report.get("academic_readiness") or {}
    if academic.get("mechanical_findings"):
        release_blockers.append("ACADEMIC_READINESS")
    if report.get("readiness", {}).get("ACADEMIC_REVIEW") != "REVIEWED":
        release_blockers.append("ACADEMIC_REVIEW")
    release_blockers = sorted(set(release_blockers))

    return {
        "AUTHORING": {
            "state": "READY_FOR_AUTHORING" if not authoring_blockers else "BLOCKED",
            "blockers": authoring_blockers,
        },
        "BUILD": {
            "state": "READY_FOR_BUILD" if not build_blockers else "BLOCKED",
            "blockers": build_blockers,
        },
        "RELEASE": {
            "state": "READY_FOR_RELEASE" if not release_blockers else "BLOCKED",
            "blockers": release_blockers,
        },
        "rule": "Author candidates before review; build only supported products; release only reviewed ones.",
    }


def plan(request: dict, repo: Path = REPO, diagnostic: dict | None = None) -> dict:
    board, findings = resolve_board(request, repo)
    requested = list(request.get("requested_cores", []))
    if board is None:
        return {"mode": "PLAN_ONLY", "findings": findings, "passed": False,
                "required_owner_inputs": [], "agent_actions": [], "products": []}

    subject = request["subject"]
    caps, mics = capability_graph.subject_graph(subject, repo)
    topology = capability_graph.topology_findings(board, caps, mics)
    findings += topology
    records = _records(subject, repo)
    supported, compiler_error = _compiler_support(records, board, subject)
    if compiler_error:
        findings.append({"point": "COMPILER_PREVIEW_FAILED", "where": board["bucket_id"],
                         "detail": compiler_error})
    practice = practice_coverage(records, board["bucket_id"])
    learner_route = _learner_route(request, board, caps, mics, repo)
    purposes = resolve_request.purposes()

    diagnostic_focus = (
        atlas_need.resolve(
            diagnostic,
            repo,
            expected_subject=subject,
            expected_matrix_id=board["matrix_id"],
        )
        if diagnostic is not None
        else {
            "state": "NOT_SUPPLIED",
            "passed": True,
            "matrix_id": board["matrix_id"],
            "subject": subject,
            "targets": [],
            "rejected": [],
            "warnings": [],
            "errors": [],
            "rule": "no external diagnostic supplied; planner readiness remains canonical",
        }
    )
    focus_targets = list(diagnostic_focus.get("targets") or [])
    core_emphasis = core_focus.for_cores(requested, focus_targets)
    focused_inventory = focus_inventory.for_cores(
        subject, board["bucket_id"], requested, focus_targets, repo
    )

    owner_inputs = []
    if any(c in LEARNER_ROUTED for c in requested) and not request.get("learner"):
        owner_inputs.append({"id": "LEARNER_ENTRY", "choices": [
            "profile/diagnostic", "owner_entry", "owner_estimate", "unknown"]})
    intent = request.get("practice", {})
    if "CORE2A" in requested and not intent.get("CORE2A", {}).get("purpose"):
        owner_inputs.append({"id": "CORE2A_PURPOSE",
                             "choices": ["STARTER", "PRACTICE", "REVISION", "COMPETITION"]})
    if "CORE2B" in requested and not intent.get("CORE2B", {}).get("purpose"):
        owner_inputs.append({"id": "CORE2B_PURPOSE",
                             "choices": ["PRACTICE", "REVISION", "COMPETITION", "NONE"]})

    source_basis = request.get("source_basis", [])
    receipt = source_receipts.resolve(
        request.get("source_receipt_ref"), request=request,
        expected_bucket=board["bucket_id"], repo=repo,
    )
    if receipt["state"] in {"INVALID", "DANGLING"}:
        findings.extend(receipt.get("findings", []))

    if any(c in SOURCE_PRODUCTS for c in requested) and not source_basis:
        owner_inputs.append({"id": "SOURCE_BASIS", "choices": ["supply source reference"]})

    coverage = receipt.get("coverage", {}) if receipt.get("verified") else {}
    basis_assessment = receipt.get("basis_assessment") or {}
    unresolved_basis_drift = (
        receipt.get("verified")
        and basis_assessment.get("status") == "DRIFT"
        and request.get("source_basis_drift_acknowledgement")
            != "KEEP_SUPPLIED_DESPITE_DRIFT"
    )
    if unresolved_basis_drift:
        candidates = list(basis_assessment.get("replacement_candidates") or [])
        owner_inputs.append({
            "id": "SOURCE_BASIS_DRIFT_DECISION",
            "choices": (
                ["KEEP_SUPPLIED_DESPITE_DRIFT"]
                + [f"CHANGE_SOURCE_BASIS:{candidate}" for candidate in candidates]
            ),
        })

    insufficient_practice = any(
        core in requested and (coverage.get(core) or {}).get("status") != "SUFFICIENT"
        for core in PRACTICE
    )
    if (receipt.get("verified") and not unresolved_basis_drift
            and insufficient_practice
            and not request.get("supplemental_question_policy")):
        owner_inputs.append({"id": "SUPPLEMENTAL_QUESTION_POLICY",
                             "choices": ["SOURCE_ONLY", "ALLOW_AUTHORED_CANDIDATES"]})

    actions = []
    if source_basis and receipt["state"] == "MISSING":
        actions.append({"id": "INSPECT_AND_INGEST_SOURCE_BASIS", "owner": "AGENT",
                        "detail": "Inspect the supplied source and write a verified source receipt before asking whether supplemental questions are allowed."})
    if learner_route.get("bridges"):
        actions.append({"id": "SCHEDULE_PREREQUISITE_BRIDGES", "owner": "AGENT",
                        "capabilities": learner_route["bridges"]})

    products = []
    topology_blocked = bool(topology)
    for core in requested:
        state, reason = "READY", None
        if core not in ALL_CORES:
            state, reason = "BLOCKED", "UNKNOWN_CORE"
        elif topology_blocked and core in PERSONALISED_TEACHING:
            state, reason = "BLOCKED_TOPOLOGY", "ladder contradicts prerequisite topology"
        elif core in PERSONALISED_TEACHING and learner_route["state"] == "WAITING_FOR_OWNER_INPUT":
            state, reason = "WAITING_FOR_LEARNER_ENTRY", "learner entry has not been supplied"
        elif core in PERSONALISED_TEACHING and learner_route["state"] == "BLOCKED":
            state, reason = "BLOCKED_PREREQUISITE", "learner entry is not prerequisite-reachable"
        elif core in SOURCE_PRODUCTS and source_basis and receipt["state"] == "MISSING":
            state, reason = "WAITING_FOR_SOURCE_RECEIPT", "supplied source has no verified inspection receipt"
        elif core in SOURCE_PRODUCTS and receipt["state"] in {"INVALID", "DANGLING"}:
            state, reason = "BLOCKED_SOURCE_RECEIPT", "source inspection receipt is invalid or unresolved"
        elif core in SOURCE_PRODUCTS and unresolved_basis_drift:
            state, reason = "WAITING_FOR_SOURCE_BASIS_DECISION", "verified inspection found that the supplied source basis has drifted from the requested topic scope"
        elif core == "CORE2" and source_basis and (coverage.get(core) or {}).get("status") != "SUFFICIENT":
            state, reason = "BLOCKED_SOURCE_CUSTODY", "verified source receipt does not establish sufficient Core2 custody"
        elif core in PRACTICE and source_basis and (coverage.get(core) or {}).get("status") != "SUFFICIENT" and not request.get("supplemental_question_policy"):
            state, reason = "WAITING_FOR_SUPPLEMENT_POLICY", "verified source receipt does not establish source-derived coverage"
        elif core in PRACTICE and source_basis and (coverage.get(core) or {}).get("status") != "SUFFICIENT" and request.get("supplemental_question_policy") == "SOURCE_ONLY":
            state, reason = "BLOCKED_SOURCE_COVERAGE", "source-only policy forbids filling uncovered practice with authored candidates"
        elif core in PRACTICE and learner_route["state"] == "WAITING_FOR_OWNER_INPUT":
            state, reason = "WAITING_FOR_LEARNER_ENTRY", "practice routing requires learner evidence or an explicit owner decision"
        elif core in PRACTICE and learner_route["state"] == "BLOCKED":
            state, reason = "BLOCKED_PREREQUISITE", "learner practice route is not prerequisite-reachable"
        elif core not in supported:
            state, reason = "BLOCKED_ASSET", "compiler/library does not support this product"
        elif core == "CORE2A" and not intent.get(core, {}).get("purpose"):
            state, reason = "WAITING_FOR_PURPOSE", "support level is selected by purpose"
        elif core == "CORE2B" and not intent.get(core, {}).get("purpose"):
            state, reason = "WAITING_FOR_PURPOSE", "transfer routing is selected by purpose"
        elif core == "CORE2B":
            purpose = intent[core]["purpose"]
            if purpose == "NONE" or (purpose in purposes and not purposes[purpose]["routes_transfer"]):
                state, reason = "WITHHELD", "declared purpose does not route transfer"
        products.append({"core": core, "state": state, **({"reason": reason} if reason else {})})

    academic = academic_readiness.board_report(board, subject, repo)
    review = academic["human_review"]
    expansion = ("READY" if not findings and academic["learner_release_ready"]
                 else "BLOCKED")
    report = {
        "mode": "PLAN_ONLY",
        "request_id": request.get("request_id"),
        "subject": subject,
        "subtopic": board.get("subtopic"),
        "bucket": board["bucket_id"],
        "matrix": board["_path"],
        "canonical_rungs": _rung_inventory(board, mics),
        "readiness": {
            "STRUCTURE": "READY" if not findings else "BLOCKED",
            "REACHABLE_TO_LEARN": learner_route["state"],
            "ACADEMIC_REVIEW": review["state"],
            "CONTENT_EXPANSION": expansion,
        },
        "invariant": "READY_TO_BUILD != REACHABLE_TO_LEARN",
        "learner_route": learner_route,
        "source": {
            "basis": source_basis,
            "receipt_ref": request.get("source_receipt_ref"),
            "receipt_state": receipt.get("state"),
            "receipt_digest": receipt.get("digest"),
            "inspection": receipt.get("inspection"),
            "basis_assessment": basis_assessment or None,
            "coverage": coverage,
            "resource_refs": receipt.get("resource_refs", []),
        },
        "practice_inventory": practice,
        "diagnostic_focus": diagnostic_focus,
        "core_focus": core_emphasis,
        "focus_inventory": focused_inventory,
        "compiler_supported": sorted(supported),
        "products": products,
        "required_owner_inputs": owner_inputs,
        "agent_actions": actions,
        "academic_readiness": academic,
        "review": review,
        "core_relationships": {
            "CORE1A_CORE1B": "same canonical rung segment; agency changes, target does not",
            "CORE2A": "practice inside the taught capability family; support may vary",
            "CORE2B": "transfer changes decision structure while preserving taught truth",
        },
        "findings": findings,
        "passed": not findings,
        "no_content_authored": True,
    }
    report["lifecycle"] = lifecycle_handoff(report)
    # Compatibility surface for callers written against PR #10. It now means build,
    # not authoring or learner release.
    report["execution"] = report["lifecycle"]["BUILD"]
    return report


def audit(repo: Path = REPO) -> dict:
    try:
        import jsonschema
    except ModuleNotFoundError:
        jsonschema = None
    validator = jsonschema.Draft202012Validator(load(SCHEMA)) if jsonschema else None
    rows = []
    for path in sorted((repo / "Requests").glob(FIXTURE_GLOB)):
        request = load(path)
        structural = ([{"point": "AUTHORING_REQUEST_STRUCTURE",
                        "where": "/".join(str(x) for x in err.path), "detail": err.message}
                       for err in validator.iter_errors(request)] if validator else [])
        report = plan(request, repo) if not structural else {
            "findings": structural, "passed": False, "required_owner_inputs": [],
            "agent_actions": [], "products": []}
        rows.append({"path": str(path.relative_to(repo)), **report})
    return {"requests": len(rows), "plans": rows,
            "findings": sum(len(r.get("findings", [])) for r in rows),
            "passed": all(not r.get("findings") for r in rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--diagnostic", type=Path,
                        help="optional external diagnostic gap envelope kept separate from learner placement")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    diagnostic = load(args.diagnostic) if args.diagnostic else None
    report = plan(load(args.plan), diagnostic=diagnostic) if args.plan else audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report.get("passed", False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
