#!/usr/bin/env python3
"""Compile a resolved authoring request into a stale-detectable third-agent work packet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, file_digest, load  # noqa: E402
from Shared.tools import author_brief, plan_request, source_receipts  # noqa: E402
from Shared.tools.spec_conformance import requirements  # noqa: E402

SCHEMA = REPO / "Shared/library/execution-packet.schema.json"
AUTHOR_FIXTURE_GLOB = "*.author-request.json"
SOURCE_CORES = {"CORE2", "CORE2A", "CORE2B"}
LEARNER_CORES = {"CORE1A", "CORE1B", "CORE2A", "CORE2B"}

COMMON_PROHIBITIONS = [
    "Do not change canonical rung order, prerequisite refs, inferential jumps, misconceptions, exits, or vocabulary ceilings to make the requested product easier to build.",
    "Do not treat an owner estimate or percentage as evidence that any capability is demonstrated.",
    "Do not promote a CANDIDATE record to REVIEWED or imply human academic approval.",
    "Do not present an authored or reconstructed question as source custody or as a supplied original.",
    "Do not invent source identity, exam identity, question number, or provenance from memory.",
    "Do not introduce untaught conceptual content under a Core2B transfer label.",
]

ACTION_SCOPE = {
    "INSPECT_AND_INGEST_SOURCE_BASIS": SOURCE_CORES,
    "RESEARCH_SOURCE_BASIS": SOURCE_CORES,
    "RESOLVE_SOURCE_BASIS_DRIFT": SOURCE_CORES,
    "AUTHOR_SUPPLEMENTAL_PRACTICE": {"CORE2A", "CORE2B"},
    "SCHEDULE_PREREQUISITE_BRIDGES": LEARNER_CORES,
}
# Every work order is executable. Duties name what the agent researches or authors first.
RUNNABLE_ACTIONS = {
    "BUILD_FROM_CANONICAL", "RESEARCH_SOURCE", "AUTHOR_CANDIDATE_QUESTION",
    "AUTHOR_CANONICAL_CANDIDATE", "AUTHOR_BRIDGE_THEN_BUILD", "REPAIR_CANONICAL_TOPOLOGY",
    "FIX_FINDINGS_THEN_BUILD",
}


def _subject_library(subject: str, repo: Path) -> tuple[list[str], str]:
    rows = []
    files = []
    for path in sorted((repo / subject / "library").glob("*.json")):
        files.append(str(path.relative_to(repo)))
        rows.append({"path": str(path.relative_to(repo)), "value": load(path)})
    return files, digest(rows)


def _matrix_snapshot(plan: dict, repo: Path) -> dict:
    path = repo / plan["matrix"]
    value = load(path)
    return {"path": plan["matrix"], "digest": digest(value)}


def _role_snapshot(core: str, repo: Path) -> dict:
    path = repo / "Shared" / "roles" / f"{core}.md"
    reqs = requirements(path)
    return {
        "path": str(path.relative_to(repo)),
        "sha256": file_digest(path),
        "required_fields": reqs or [],
    }


def _segment(plan: dict) -> list[dict]:
    route = plan.get("learner_route", {})
    entry = route.get("entry")
    rows = sorted(plan.get("canonical_rungs", []), key=lambda row: row["position"])
    if not entry:
        return []

    requested = route.get("requested_entry") or entry
    requested_row = next((row for row in rows if row["rung"] == requested), None)
    explicit_nondefault = (
        route.get("selected_by") == "OWNER_NAMED"
        and requested_row is not None
        and requested_row.get("default_entry_eligible", True) is False
    )
    segment_rows = rows if explicit_nondefault else [
        row for row in rows if row.get("default_entry_eligible", True)
    ]
    positions = {row["rung"]: row["position"] for row in segment_rows}
    if entry not in positions:
        return []
    return [row for row in segment_rows if row["position"] >= positions[entry]]


def _duties(plan: dict, core: str) -> list[str]:
    duties = [f["point"] for f in plan.get("findings", [])]
    for row in plan.get("agent_actions", []):
        if core in ACTION_SCOPE.get(row["id"], set()):
            duties.append(row["id"])
    return sorted(set(duties))


def _action(request: dict, product: dict, duties: list[str]) -> tuple[str, str]:
    core, state = product["core"], product["state"]
    duty = (product.get("duty") or {}).get("duty")
    source_only = request.get("supplemental_question_policy") == "SOURCE_ONLY"
    if state == "OWNER_EXCLUDED":
        return "OWNER_EXCLUDED", "The owner's declared purpose excludes this product."
    if duty == "REPAIR_LADDER_TOPOLOGY":
        return "REPAIR_CANONICAL_TOPOLOGY", "Correct the ladder/prerequisite contradiction in the canonical records, then build."
    if duty == "ACQUIRE_SOURCE" or (core == "CORE2" and duty) or any(
            d in {"INSPECT_AND_INGEST_SOURCE_BASIS", "RESEARCH_SOURCE_BASIS", "RESOLVE_SOURCE_BASIS_DRIFT"}
            for d in duties):
        return "RESEARCH_SOURCE", (
            "Research and inspect the original source, write the source receipt and custody records "
            "(stem, conditions, options, figures, answer), then build. Owner-supplied question text is "
            "custody of class OWNER_SUPPLIED."
        )
    if duty == "AUTHOR_PRACTICE" or "AUTHOR_SUPPLEMENTAL_PRACTICE" in duties:
        if source_only:
            return "RESEARCH_SOURCE", "SOURCE_ONLY: research further authorised sources to cover the practice."
        return "AUTHOR_CANDIDATE_QUESTION", (
            "Author truthful candidate practice inside the taught capability, labelled AUTHORED_PRACTICE."
        )
    if duty == "AUTHOR_ASSET":
        if core in {"CORE2A", "CORE2B"} and not source_only:
            return "AUTHOR_CANDIDATE_QUESTION", (
                "Author truthful candidate practice inside the taught capability, labelled AUTHORED_PRACTICE."
            )
        return "AUTHOR_CANONICAL_CANDIDATE", (
            "Research and author the missing canonical asset as a CANDIDATE library record, then build."
        )
    if "SCHEDULE_PREREQUISITE_BRIDGES" in duties:
        return "AUTHOR_BRIDGE_THEN_BUILD", "Author the prerequisite bridge teaching first, then build."
    if duties:
        return "FIX_FINDINGS_THEN_BUILD", "Fix the listed findings in the canonical records, then build."
    return "BUILD_FROM_CANONICAL", "All currently required inputs/assets for this Core are present."


def _write_scope(action: str, core: str) -> dict:
    if action == "AUTHOR_CANDIDATE_QUESTION":
        return {
            "mode": "CANDIDATE_RECORDS_ONLY",
            "collections": ["questions"],
            "status": "CANDIDATE",
            "origin": "AUTHORED",
            "note": "Write into the subject library only through its package/schema contract.",
        }
    if action == "RESEARCH_SOURCE":
        return {
            "mode": "CANDIDATE_RECORDS_ONLY",
            "collections": ["questions", "resources"],
            "status": "CANDIDATE",
            "origin": "ORIGINAL",
            "origins": {"questions": ["ORIGINAL", "ADAPTED"], "resources": ["LOCAL", "WEB"]},
            "note": "Record researched source custody and receipts; never present authored text as source.",
        }
    if action in {"AUTHOR_CANONICAL_CANDIDATE", "AUTHOR_BRIDGE_THEN_BUILD",
                  "REPAIR_CANONICAL_TOPOLOGY", "FIX_FINDINGS_THEN_BUILD"}:
        return {
            "mode": "CANDIDATE_RECORDS_ONLY",
            "collections": ["capabilities", "microtopics", "relations", "representations",
                            "teaching_routes"],
            "status": "CANDIDATE",
            "origin": "AUTHORED",
            "note": "Add or correct CANDIDATE canonical records through the package/schema contract, then build.",
        }
    if action == "BUILD_FROM_CANONICAL":
        return {
            "mode": "PRODUCT_OUTPUT_ONLY",
            "collections": [],
            "note": "Compose the requested product from canonical records; do not rewrite curriculum truth.",
        }
    return {"mode": "NO_WRITE", "collections": [], "note": "The owner excluded this product."}


def compile_packet(request: dict, repo: Path = REPO, diagnostic: dict | None = None) -> dict:
    plan = plan_request.plan(request, repo, diagnostic)
    subject = plan.get("subject") or request.get("subject")
    library_files, library_digest = _subject_library(subject, repo)
    packet = {
        "schema_version": "1.0.0",
        "packet_id": f'PACKET-{request.get("request_id", "UNNAMED")}',
        "request_id": request.get("request_id"),
        "request_digest": digest(request),
        "mode": "AUTHORING_EXECUTION_PACKET",
        "subject": subject,
        "bucket": plan.get("bucket"),
        "lifecycle": plan.get("lifecycle"),
        "pins": {
            "matrix": _matrix_snapshot(plan, repo) if plan.get("matrix") else None,
            "library": {"files": library_files, "digest": library_digest},
            "source_receipt": (
                {
                    "receipt_id": plan.get("source", {}).get("receipt_ref"),
                    "digest": plan.get("source", {}).get("receipt_digest"),
                }
                if plan.get("source", {}).get("receipt_ref") else None
            ),
            "diagnostic": (
                {"digest": digest(diagnostic)}
                if diagnostic is not None else None
            ),
        },
        "canonical": {
            "rungs": plan.get("canonical_rungs", []),
            "selected_segment": _segment(plan),
            "learner_route": plan.get("learner_route"),
            "practice_inventory": plan.get("practice_inventory"),
            "diagnostic_focus": plan.get("diagnostic_focus"),
            "source": plan.get("source"),
        },
        "owner_decisions": {
            "learner": request.get("learner"),
            "practice": request.get("practice", {}),
            "supplemental_question_policy": request.get("supplemental_question_policy"),
        },
        "global_prohibitions": COMMON_PROHIBITIONS,
        "acceptance_commands": author_brief.gates(),
        "work_orders": [],
        "findings": list(plan.get("findings", [])),
    }

    for product in plan.get("products", []):
        core = product["core"]
        duties = _duties(plan, core)
        action, reason = _action(request, product, duties)
        role = _role_snapshot(core, repo)
        target = {
            "bucket": plan.get("bucket"),
            "segment": (
                [row["rung"] for row in packet["canonical"]["selected_segment"]]
                if core in {"CORE1A", "CORE1B"} else []
            ),
            "owned_questions": (
                plan.get("practice_inventory", {}).get("questions", [])
                if core == "CORE2" else
                plan.get("practice_inventory", {}).get(core, [])
                if core in {"CORE2A", "CORE2B"} else []
            ),
            "diagnostic_focus": (plan.get("core_focus") or {}).get(core),
            "focus_inventory": (plan.get("focus_inventory") or {}).get(core),
        }
        packet["work_orders"].append({
            "core": core,
            "product_state": product["state"],
            "authoring_action": action,
            "reason": reason,
            "duties": duties,
            "role": role,
            "target": target,
            "write_scope": _write_scope(action, core),
            "authority": {
                "semantic_authority": role["path"],
                "canonical_truth": "subject library + matrix references; record-owned truths are read-only here",
                "source_custody": (
                    "must remain source-derived" if core == "CORE2"
                    else "authored candidates must retain AUTHORED provenance"
                    if core in {"CORE2A", "CORE2B"} else "not applicable"
                ),
            },
        })

    runnable = [row for row in packet["work_orders"] if row["authoring_action"] in RUNNABLE_ACTIONS]
    direct = [row for row in runnable if row["authoring_action"] == "BUILD_FROM_CANONICAL"]
    packet["packet_state"] = "READY" if len(direct) == len(runnable) else "RESEARCH_AND_AUTHOR"
    packet["summary"] = {
        "runnable_cores": [row["core"] for row in runnable],
        "research_and_author_cores": [row["core"] for row in runnable
                                      if row["authoring_action"] != "BUILD_FROM_CANONICAL"],
        "owner_excluded_cores": [row["core"] for row in packet["work_orders"]
                                 if row["authoring_action"] == "OWNER_EXCLUDED"],
    }
    return packet


def _schema_findings(packet: dict, repo: Path = REPO) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / "Shared/library/execution-packet.schema.json")
    return [
        {
            "point": "EXECUTION_PACKET_STRUCTURE",
            "where": "/".join(str(part) for part in error.path),
            "detail": error.message,
        }
        for error in jsonschema.Draft202012Validator(schema).iter_errors(packet)
    ]


def verify(packet: dict, request: dict, repo: Path = REPO, diagnostic: dict | None = None) -> dict:
    found = list(_schema_findings(packet, repo))
    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    if packet.get("request_digest") != digest(request):
        fail("EXECUTION_PACKET_REQUEST_STALE", request.get("request_id", ""),
             "request changed after this packet was compiled")

    subject = packet.get("subject") or request.get("subject")
    _, current_library = _subject_library(subject, repo)
    pinned_library = (packet.get("pins", {}).get("library") or {}).get("digest")
    if pinned_library != current_library:
        fail("EXECUTION_PACKET_LIBRARY_STALE", subject,
             "subject library changed after this packet was compiled")

    matrix = packet.get("pins", {}).get("matrix")
    if matrix:
        path = repo / matrix["path"]
        current = digest(load(path)) if path.exists() else None
        if current != matrix.get("digest"):
            fail("EXECUTION_PACKET_MATRIX_STALE", matrix["path"],
                 "matrix changed after this packet was compiled")

    receipt_pin = packet.get("pins", {}).get("source_receipt")
    if receipt_pin:
        current_receipt = source_receipts.resolve(
            receipt_pin.get("receipt_id"), request=request,
            expected_bucket=(packet.get("bucket") or None), repo=repo,
        )
        if not current_receipt.get("verified"):
            fail("EXECUTION_PACKET_SOURCE_RECEIPT_INVALID",
                 receipt_pin.get("receipt_id", ""),
                 "pinned source receipt no longer verifies")
        elif current_receipt.get("digest") != receipt_pin.get("digest"):
            fail("EXECUTION_PACKET_SOURCE_RECEIPT_STALE",
                 receipt_pin.get("receipt_id", ""),
                 "source receipt changed after this packet was compiled")

    diagnostic_pin = packet.get("pins", {}).get("diagnostic")
    if diagnostic_pin:
        if diagnostic is None:
            fail("EXECUTION_PACKET_DIAGNOSTIC_MISSING", packet.get("request_id", ""),
                 "packet was compiled with a diagnostic envelope but none was supplied for verification")
        elif diagnostic_pin.get("digest") != digest(diagnostic):
            fail("EXECUTION_PACKET_DIAGNOSTIC_STALE", packet.get("request_id", ""),
                 "diagnostic envelope changed after this packet was compiled")
    elif diagnostic is not None:
        fail("EXECUTION_PACKET_DIAGNOSTIC_STALE", packet.get("request_id", ""),
             "verification supplied a diagnostic envelope to a packet compiled without one")

    for order in packet.get("work_orders", []):
        role = order.get("role", {})
        path = repo / role.get("path", "")
        current = file_digest(path) if path.is_file() else None
        if current != role.get("sha256"):
            fail("EXECUTION_PACKET_ROLE_STALE", order.get("core", ""),
                 f'{role.get("path")} changed after this packet was compiled')

    fresh = compile_packet(request, repo, diagnostic)
    current_orders = {
        row["core"]: (row["product_state"], row["authoring_action"], row["duties"])
        for row in fresh.get("work_orders", [])
    }
    pinned_orders = {
        row["core"]: (row["product_state"], row["authoring_action"], row["duties"])
        for row in packet.get("work_orders", [])
    }
    if current_orders != pinned_orders:
        fail("EXECUTION_PACKET_PLAN_STALE", request.get("request_id", ""),
             "planner output changed after this packet was compiled")

    return {"passed": not found, "findings": found,
            "packet_id": packet.get("packet_id"), "request_id": request.get("request_id")}


def audit(repo: Path = REPO) -> dict:
    rows = []
    for path in sorted((repo / "Requests").glob(AUTHOR_FIXTURE_GLOB)):
        request = load(path)
        packet = compile_packet(request, repo)
        checked = verify(packet, request, repo)
        rows.append({
            "request": str(path.relative_to(repo)),
            "packet_state": packet["packet_state"],
            "summary": packet["summary"],
            "findings": checked["findings"],
            "passed": checked["passed"],
        })
    return {"requests": len(rows), "packets": rows,
            "findings": sum(len(row["findings"]) for row in rows),
            "passed": all(row["passed"] for row in rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--diagnostic", type=Path,
                        help="optional external diagnostic envelope pinned into the packet")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    diagnostic = load(args.diagnostic) if args.diagnostic else None

    if args.verify:
        if not args.request:
            parser.error("--verify requires --request")
        report = verify(load(args.verify), load(args.request), diagnostic=diagnostic)
    elif args.request:
        report = compile_packet(load(args.request), diagnostic=diagnostic)
    else:
        report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report.get("passed", True) else 0


if __name__ == "__main__":
    raise SystemExit(main())
