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
from Shared.tools import (academic_readiness, atlas_need, capability_graph, core_focus,
                          focus_inventory, learner_evidence, research_first_policy, resolve_request,
                          source_receipts)

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

    Nothing here is a stop. Findings and product duties are work the agent carries out in
    the same job; the build is ready once no duty remains. Human academic review is the
    owner's release decision: the product is still delivered, labelled with the reviews
    that have not happened.
    """
    structural = [f["point"] for f in report.get("findings", [])]
    actions = [row["id"] for row in report.get("agent_actions", [])]
    product_duties = [
        f'{row["core"]}:{row["duty"]["duty"]}' for row in report.get("products", [])
        if row.get("duty")
    ]

    authoring_duties = sorted(set(structural + actions))
    build_duties = sorted(set(authoring_duties + product_duties))
    review_labels = []
    academic = report.get("academic_readiness") or {}
    if academic.get("mechanical_findings"):
        review_labels.append("ACADEMIC_READINESS")
    if report.get("readiness", {}).get("ACADEMIC_REVIEW") != "REVIEWED":
        review_labels.append("ACADEMIC_REVIEW")

    return {
        "AUTHORING": {"state": "READY_FOR_AUTHORING", "duties": authoring_duties},
        "BUILD": {
            "state": "READY_FOR_BUILD" if not build_duties else research_first_policy.RESEARCH_AND_AUTHOR,
            "duties": build_duties,
        },
        "RELEASE": {
            "state": "READY_FOR_RELEASE" if not build_duties and not review_labels else "OWNER_REVIEW",
            "duties": build_duties,
            "review_labels": sorted(review_labels),
        },
        "rule": "Author and build every product in the job; release is the owner's decision on a delivered, truthfully labelled product.",
    }


def plan(request: dict, repo: Path = REPO, diagnostic: dict | None = None) -> dict:
    workflow = research_first_policy.load_workflow()
    request, defaults_applied = research_first_policy.apply_request_defaults(request, workflow)
    board, findings = resolve_board(request, repo)
    requested = list(request.get("requested_cores", []))
    if board is None:
        return {"mode": "PLAN_ONLY", "findings": findings, "passed": False,
                "defaults_applied": defaults_applied, "required_owner_inputs": [],
                "agent_actions": [], "products": []}

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
    if learner_route["state"] == "BLOCKED" and not learner_route.get("unresolved"):
        # A dangling profile or an unplaceable entry falls back to the default learner.
        fallback = {**request, "learner": {"owner_estimate": dict(
            workflow["default_request_values"]["learner"]["owner_estimate"])}}
        defaults_applied.append({"field": "learner", "value": fallback["learner"],
                                 "basis": "DEFAULT_MEDIAN", "replaced": learner_route.get("reason")})
        learner_route = _learner_route(fallback, board, caps, mics, repo)
    if learner_route["state"] == "BLOCKED":
        # Unresolved prerequisites are taught as bridges inside the product, never a stop.
        learner_route = {**learner_route, "state": "READY_WITH_BRIDGES",
                         "bridges": sorted(set(learner_route.get("bridges", []))
                                           | set(learner_route.get("unresolved", [])))}
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

    intent = request.get("practice", {})
    actions = []

    source_basis = request.get("source_basis", [])
    receipt = source_receipts.resolve(
        request.get("source_receipt_ref"), request=request,
        expected_bucket=board["bucket_id"], repo=repo,
    )
    if receipt["state"] in {"INVALID", "DANGLING"}:
        findings.extend(receipt.get("findings", []))

    if any(c in SOURCE_PRODUCTS for c in requested) and not source_basis:
        actions.append({"id": "RESEARCH_SOURCE_BASIS", "owner": "AGENT",
                        "detail": "Research the original sources for the requested questions and record them as the source basis; owner-supplied question text is custody of class OWNER_SUPPLIED."})

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
        actions.append({
            "id": "RESOLVE_SOURCE_BASIS_DRIFT", "owner": "AGENT",
            "candidates": candidates,
            "detail": "Research which source basis matches the requested topic scope, record it, and inspect it.",
        })

    insufficient_practice = any(
        core in requested and (coverage.get(core) or {}).get("status") != "SUFFICIENT"
        for core in PRACTICE
    )
    if (receipt.get("verified") and not unresolved_basis_drift and insufficient_practice
            and request.get("supplemental_question_policy") != "SOURCE_ONLY"):
        actions.append({"id": "AUTHOR_SUPPLEMENTAL_PRACTICE", "owner": "AGENT",
                        "detail": "Author practice inside the taught capability, labelled AUTHORED_PRACTICE, to cover what the source does not."})

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
            state, reason = "INVALID_REQUEST", "UNKNOWN_CORE"
        elif topology_blocked and core in PERSONALISED_TEACHING:
            state, reason = "BLOCKED_TOPOLOGY", "ladder contradicts prerequisite topology"
        elif core in SOURCE_PRODUCTS and source_basis and receipt["state"] == "MISSING":
            state, reason = "WAITING_FOR_SOURCE_RECEIPT", "supplied source has no verified inspection receipt"
        elif core in SOURCE_PRODUCTS and receipt["state"] in {"INVALID", "DANGLING"}:
            state, reason = "BLOCKED_SOURCE_RECEIPT", "source inspection receipt is invalid or unresolved"
        elif core in SOURCE_PRODUCTS and unresolved_basis_drift:
            state, reason = "WAITING_FOR_SOURCE_BASIS_DECISION", "verified inspection found that the supplied source basis has drifted from the requested topic scope"
        elif core == "CORE2" and source_basis and (coverage.get(core) or {}).get("status") != "SUFFICIENT":
            state, reason = "BLOCKED_SOURCE_CUSTODY", "verified source receipt does not establish sufficient Core2 custody"
        elif core in PRACTICE and source_basis and (coverage.get(core) or {}).get("status") != "SUFFICIENT":
            state, reason = "BLOCKED_SOURCE_COVERAGE", "source does not cover this practice; author labelled practice for the rest"
        elif core not in supported:
            state, reason = "BLOCKED_ASSET", "compiler/library does not support this product yet"
        elif core == "CORE2B":
            purpose = intent[core]["purpose"]
            if purpose == "NONE" or (purpose in purposes and not purposes[purpose]["routes_transfer"]):
                state, reason = "OWNER_EXCLUDED", "owner's declared purpose excludes transfer"
        row = {"core": core, "state": state, **({"reason": reason} if reason else {})}
        if state not in {"READY", "INVALID_REQUEST", "OWNER_EXCLUDED"}:
            row = {"core": core, "state": research_first_policy.RESEARCH_AND_AUTHOR,
                   "reason": reason, "duty": research_first_policy.duty_for(state, workflow)}
        if state == "INVALID_REQUEST":
            findings.append({"point": "UNKNOWN_CORE", "where": core, "detail": "not one of the six Core roles"})
        products.append(row)

    academic = academic_readiness.board_report(board, subject, repo)
    review = academic["human_review"]
    expansion = ("READY" if not findings and academic["learner_release_ready"]
                 else research_first_policy.RESEARCH_AND_AUTHOR)
    report = {
        "mode": "PLAN_ONLY",
        "request_id": request.get("request_id"),
        "subject": subject,
        "subtopic": board.get("subtopic"),
        "bucket": board["bucket_id"],
        "matrix": board["_path"],
        "canonical_rungs": _rung_inventory(board, mics),
        "readiness": {
            "STRUCTURE": "READY" if not findings else research_first_policy.RESEARCH_AND_AUTHOR,
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
        "defaults_applied": defaults_applied,
        # Kept for callers: the planner never waits on the owner; defaults fill every input.
        "required_owner_inputs": [],
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
