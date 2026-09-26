#!/usr/bin/env python3
"""Validate and optionally apply one execution-packet work order."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402
from Shared.library import intake, practice_inventory  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402
from Shared.tools import compile_execution_packet  # noqa: E402

PROPOSAL_SCHEMA = REPO / "Shared/library/authoring-proposal.schema.json"
RECEIPT_SCHEMA = REPO / "Shared/library/authoring-run-receipt.schema.json"


def _schema_findings(value: dict, schema_path: Path, point: str) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    validator = jsonschema.Draft202012Validator(load(schema_path))
    return [{
        "point": point,
        "where": "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(value)]


def _subject_records(subject: str, repo: Path) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def _safe_target(path_text: str | None, subject: str, repo: Path) -> Path | None:
    if path_text is None:
        return None
    path = repo / path_text
    try:
        resolved = path.resolve()
        root = (repo / subject / "library").resolve()
        resolved.relative_to(root)
    except Exception:
        return None
    return resolved if resolved.suffix == ".json" else None


def _artifact_path(run_id: str, core: str, relative: str, repo: Path) -> Path | None:
    root = (repo / "publication" / "drafts" / run_id / core).resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _find_order(packet: dict, core: str) -> dict | None:
    return next((row for row in packet.get("work_orders", []) if row.get("core") == core), None)


def _record_map(package: dict) -> dict[str, tuple[str, dict]]:
    found = {}
    for collection, rows in package.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                found[row["id"]] = (collection, row)
    return found


def _validate_transfer(record: dict, records: dict, bucket_id: str, core: str) -> list[dict]:
    found = []
    if core != "CORE2B":
        return found

    adaptation = record.get("adaptation")
    transfer = record.get("transfer")
    if not isinstance(adaptation, dict):
        found.append({
            "point": "AUTHORING_CORE2B_ADAPTATION_REQUIRED",
            "where": record.get("id", ""),
            "detail": "Core2B candidate must name a real parent and the fields changed from it",
        })
        return found
    parent_ref = adaptation.get("parent_ref")
    parent = records.get(parent_ref)
    if not parent or parent.get("_collection") != "questions":
        found.append({
            "point": "AUTHORING_CORE2B_PARENT_DANGLING",
            "where": str(parent_ref or ""),
            "detail": "Core2B adaptation parent must be an existing canonical question",
        })
        return found
    if parent.get("family_ref") != record.get("family_ref"):
        found.append({
            "point": "AUTHORING_CORE2B_FAMILY_CHANGED",
            "where": record.get("id", ""),
            "detail": "transfer must preserve the base question family",
        })

    changed = adaptation.get("changed_fields") or []
    meaningful = {"stem", "subparts", "options", "conditions", "figure_refs", "answer"}
    actual = []
    for field in changed:
        if field in record and record.get(field) != parent.get(field):
            actual.append(field)
    if not actual:
        found.append({
            "point": "AUTHORING_CORE2B_ADAPTATION_NOT_REAL",
            "where": record.get("id", ""),
            "detail": "adaptation.changed_fields names no field whose value actually differs from the parent",
        })
    if not (set(actual) & meaningful):
        found.append({
            "point": "AUTHORING_CORE2B_DEMAND_UNCHANGED",
            "where": record.get("id", ""),
            "detail": "Core2B must change a task-demand field, not only metadata",
        })

    if not isinstance(transfer, dict):
        found.append({
            "point": "AUTHORING_CORE2B_TRANSFER_REQUIRED",
            "where": record.get("id", ""),
            "detail": "Core2B candidate must state the changed demand dimension and exposure lineage",
        })
    else:
        builds_on = set(transfer.get("builds_on") or [])
        if parent_ref not in builds_on:
            found.append({
                "point": "AUTHORING_CORE2B_LINEAGE_MISSING_PARENT",
                "where": record.get("id", ""),
                "detail": "transfer.builds_on must include the adaptation parent question",
            })
        missing = sorted(ref for ref in builds_on if ref not in records)
        if missing:
            found.append({
                "point": "AUTHORING_CORE2B_LINEAGE_DANGLING",
                "where": record.get("id", ""),
                "detail": "transfer lineage names unknown records: " + ", ".join(missing),
            })
    return found


def _validate_candidate_records(proposal: dict, packet: dict, order: dict,
                                repo: Path) -> tuple[list[dict], dict | None, dict | None]:
    found = []
    subject = packet["subject"]
    bucket_id = packet.get("bucket")
    target = _safe_target(proposal.get("target_package"), subject, repo)
    if target is None or not target.is_file():
        found.append({
            "point": "AUTHORING_TARGET_PACKAGE_INVALID",
            "where": str(proposal.get("target_package") or ""),
            "detail": "candidate record writes must target an existing JSON package inside subject/library",
        })
        return found, None, None

    before = load(target)
    merged = copy.deepcopy(before)
    current_records = _subject_records(subject, repo)
    owned = practice_inventory.bucket_capabilities(current_records, bucket_id)

    entries = proposal.get("proposed_records", [])
    if not entries:
        found.append({
            "point": "AUTHORING_CANDIDATE_RECORDS_REQUIRED",
            "where": order["core"],
            "detail": "CANDIDATE_RECORDS_ONLY work order requires at least one proposed record",
        })
        return found, before, None

    allowed = set(order.get("write_scope", {}).get("collections") or [])
    seen = set()
    for entry in entries:
        collection = entry.get("collection")
        record = entry.get("record") or {}
        rid = record.get("id", "")
        if collection not in allowed:
            found.append({
                "point": "AUTHORING_COLLECTION_OUT_OF_SCOPE",
                "where": str(collection),
                "detail": f"work order allows only {sorted(allowed)}",
            })
            continue
        if rid in seen:
            found.append({
                "point": "AUTHORING_DUPLICATE_PROPOSED_ID",
                "where": rid,
                "detail": "proposal repeats the same record id",
            })
            continue
        seen.add(rid)
        if rid in current_records:
            found.append({
                "point": "AUTHORING_EXISTING_RECORD_MUTATION_FORBIDDEN",
                "where": rid,
                "detail": "candidate authoring may add records but may not mutate existing canonical records",
            })
            continue
        if record.get("status") != order["write_scope"].get("status"):
            found.append({
                "point": "AUTHORING_STATUS_OUT_OF_SCOPE",
                "where": rid,
                "detail": "candidate record must retain the work-order status",
            })
        scope = order["write_scope"]
        origins = (scope.get("origins") or {}).get(collection) or [scope.get("origin")]
        if record.get("origin") not in origins:
            found.append({
                "point": "AUTHORING_ORIGIN_OUT_OF_SCOPE",
                "where": rid,
                "detail": f"candidate record must carry the work order's provenance ({', '.join(map(str, origins))})",
            })
        if collection == "questions":
            if record.get("primary_capability_ref") not in owned:
                found.append({
                    "point": "AUTHORING_QUESTION_OUTSIDE_BUCKET",
                    "where": rid,
                    "detail": "question primary capability is not taught by this bucket",
                })
            if not any(row.get("core") == order["core"] for row in record.get("exposure", [])):
                found.append({
                    "point": "AUTHORING_CORE_EXPOSURE_MISSING",
                    "where": rid,
                    "detail": f"candidate question is not exposed to {order['core']}",
                })
            origin_ref = record.get("origin_ref")
            origin = current_records.get(origin_ref)
            if not origin or origin.get("_collection") != "resources" or origin.get("origin") != "AUTHORED":
                found.append({
                    "point": "AUTHORING_AUTHORED_ORIGIN_REF_INVALID",
                    "where": rid,
                    "detail": "AUTHORED candidate must point at a canonical AUTHORED resource",
                })
            elif origin_ref not in record.get("source_refs", []):
                found.append({
                    "point": "AUTHORING_AUTHORED_SOURCE_REF_MISSING",
                    "where": rid,
                    "detail": "origin_ref must also appear in source_refs",
                })
            found.extend(_validate_transfer(record, current_records, bucket_id, order["core"]))

        merged.setdefault(collection, []).append(record)

    if found:
        return found, before, None

    report = intake.check(merged)
    if not report["admitted"]:
        for item in report["findings"]:
            found.append({
                "point": "AUTHORING_MERGED_PACKAGE_REJECTED",
                "where": proposal.get("target_package", ""),
                "detail": f"{item['point']}: {item['detail']}",
            })
        return found, before, None
    return found, before, merged


def _validate_artifacts(proposal: dict, order: dict, repo: Path) -> tuple[list[dict], list[dict]]:
    found, rows = [], []
    artifacts = proposal.get("artifacts", [])
    if not artifacts:
        found.append({
            "point": "AUTHORING_PRODUCT_ARTIFACT_REQUIRED",
            "where": order["core"],
            "detail": "PRODUCT_OUTPUT_ONLY work order requires at least one product artifact",
        })
        return found, rows
    seen = set()
    for artifact in artifacts:
        rel = artifact.get("relative_path", "")
        if rel in seen:
            found.append({
                "point": "AUTHORING_DUPLICATE_ARTIFACT_PATH",
                "where": rel,
                "detail": "proposal repeats an artifact path",
            })
            continue
        seen.add(rel)
        path = _artifact_path(proposal["run_id"], order["core"], rel, repo)
        if path is None:
            found.append({
                "point": "AUTHORING_ARTIFACT_PATH_OUT_OF_SCOPE",
                "where": rel,
                "detail": "product outputs must stay inside publication/drafts/<run>/<core>",
            })
            continue
        rows.append({
            "relative_path": rel,
            "media_type": artifact["media_type"],
            "sha256": _hash_text(artifact["content"]),
            "bytes": len(artifact["content"].encode("utf-8")),
        })
    return found, rows


def validate_run(request: dict, packet: dict, proposal: dict, repo: Path = REPO) -> dict:
    found = _schema_findings(
        proposal, repo / "Shared/library/authoring-proposal.schema.json",
        "AUTHORING_PROPOSAL_STRUCTURE",
    )

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    packet_check = compile_execution_packet.verify(packet, request, repo)
    found.extend(packet_check["findings"])

    if proposal.get("packet_digest") != digest(packet):
        fail("AUTHORING_PACKET_STALE", proposal.get("run_id", ""),
             "proposal was prepared against a different execution packet")
    if proposal.get("request_digest") != digest(request):
        fail("AUTHORING_REQUEST_STALE", proposal.get("run_id", ""),
             "proposal was prepared against a different request")

    order = _find_order(packet, proposal.get("core"))
    if order is None:
        fail("AUTHORING_WORK_ORDER_MISSING", proposal.get("core", ""),
             "execution packet does not contain this Core")
        return {"passed": False, "findings": found, "receipt": None,
                "merged_package": None, "artifact_writes": []}
    # Duties on a work order are the research/authoring this run performs, never a block.
    action = order.get("authoring_action")
    if action not in compile_execution_packet.RUNNABLE_ACTIONS:
        fail("AUTHORING_ACTION_NOT_RUNNABLE", order["core"],
             f"work order action {action} does not permit authoring")

    before = after = None
    artifact_rows = []
    mode = order.get("write_scope", {}).get("mode")
    if not found and mode == "CANDIDATE_RECORDS_ONLY":
        if proposal.get("artifacts"):
            fail("AUTHORING_PRODUCT_OUTPUT_OUT_OF_SCOPE", order["core"],
                 "candidate-record work order may not write product artifacts")
        candidate_findings, before, after = _validate_candidate_records(
            proposal, packet, order, repo)
        found.extend(candidate_findings)
    elif not found and mode == "PRODUCT_OUTPUT_ONLY":
        if proposal.get("proposed_records"):
            fail("AUTHORING_LIBRARY_WRITE_OUT_OF_SCOPE", order["core"],
                 "product-output work order may not write canonical records")
        if proposal.get("target_package") is not None:
            fail("AUTHORING_TARGET_PACKAGE_OUT_OF_SCOPE", order["core"],
                 "product-output work order must not name a library package")
        artifact_findings, artifact_rows = _validate_artifacts(proposal, order, repo)
        found.extend(artifact_findings)
    elif not found:
        fail("AUTHORING_WRITE_SCOPE_NOT_RUNNABLE", order["core"],
             f"write scope {mode} is not executable")

    changed = []
    library_before = library_after = None
    if before is not None and after is not None and not found:
        path = proposal["target_package"]
        library_before = {"path": path, "digest": digest(before)}
        library_after = {"path": path, "digest": digest(after)}
        before_map = _record_map(before)
        after_map = _record_map(after)
        for rid in sorted(set(after_map) - set(before_map)):
            collection, record = after_map[rid]
            changed.append({
                "id": rid,
                "collection": collection,
                "status": record.get("status"),
                "origin": record.get("origin"),
                "sha256": digest(record),
            })

    receipt = None
    if not found:
        receipt = {
            "run_id": proposal["run_id"],
            "version": "1.0.0",
            "actor_id": proposal["actor_id"],
            "run_date": proposal["run_date"],
            "packet_id": packet["packet_id"],
            "packet_digest": digest(packet),
            "request_id": request.get("request_id"),
            "request_digest": digest(request),
            "core": order["core"],
            "authoring_action": action,
            "work_order_digest": digest(order),
            "write_scope": order["write_scope"],
            "library_before": library_before,
            "library_after": library_after,
            "changed_records": changed,
            "artifacts": artifact_rows,
            "validation": {
                "state": "VALIDATED",
                "findings": [],
                "note": "Receipt proves scope/schema enforcement only; it does not grant academic review or learner release.",
            },
            "acceptance_commands": packet.get("acceptance_commands", []),
        }
        receipt_findings = _schema_findings(
            receipt, repo / "Shared/library/authoring-run-receipt.schema.json",
            "AUTHORING_RUN_RECEIPT_STRUCTURE",
        )
        found.extend(receipt_findings)
        if receipt_findings:
            receipt = None

    return {
        "passed": not found,
        "findings": found,
        "receipt": receipt,
        "merged_package": after if not found else None,
        "artifact_writes": proposal.get("artifacts", []) if not found and mode == "PRODUCT_OUTPUT_ONLY" else [],
    }


def write_run(report: dict, proposal: dict, repo: Path = REPO,
              receipt_output: Path | None = None) -> dict:
    if not report.get("passed"):
        raise ValueError("cannot write a rejected authoring run")
    receipt = report["receipt"]
    if report.get("merged_package") is not None:
        target = repo / receipt["library_after"]["path"]
        target.write_text(json.dumps(report["merged_package"], indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    for artifact in report.get("artifact_writes", []):
        path = _artifact_path(proposal["run_id"], proposal["core"],
                              artifact["relative_path"], repo)
        if path is None:
            raise ValueError("artifact path escaped after validation")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(artifact["content"], encoding="utf-8")
    out = receipt_output or (
        repo / "publication" / "authoring-runs" / f'{proposal["run_id"]}.receipt.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"receipt_path": str(out), "receipt": receipt}


def audit(repo: Path = REPO) -> dict:
    supported = {("BUILD_FROM_CANONICAL", "PRODUCT_OUTPUT_ONLY")} | {
        (action, "CANDIDATE_RECORDS_ONLY")
        for action in compile_execution_packet.RUNNABLE_ACTIONS - {"BUILD_FROM_CANONICAL"}
    }
    rows, findings = [], []
    for path in sorted((repo / "Requests").glob("*.author-request.json")):
        request = load(path)
        packet = compile_execution_packet.compile_packet(request, repo)
        unsupported = []
        for order in packet.get("work_orders", []):
            action = order.get("authoring_action")
            mode = (order.get("write_scope") or {}).get("mode")
            if action in compile_execution_packet.RUNNABLE_ACTIONS and (action, mode) not in supported:
                unsupported.append({"core": order.get("core"), "action": action, "mode": mode})
        row_findings = [{
            "point": "AUTHORING_EXECUTOR_SCOPE_UNSUPPORTED",
            "where": item["core"] or "",
            "detail": f'executor does not support {item["action"]} with write scope {item["mode"]}',
        } for item in unsupported]
        rows.append({
            "request": str(path.relative_to(repo)),
            "packet_state": packet.get("packet_state"),
            "runnable": packet.get("summary", {}).get("runnable_cores", []),
            "findings": row_findings,
        })
        findings.extend(row_findings)
    return {"requests": len(rows), "rows": rows, "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--proposal", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--receipt-output", type=Path)
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    if args.audit:
        report = audit()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if args.enforce and not report["passed"] else 0

    if not args.request or not args.packet or not args.proposal:
        parser.error("execution requires --request, --packet and --proposal")

    request = load(args.request)
    packet = load(args.packet)
    proposal = load(args.proposal)
    report = validate_run(request, packet, proposal)
    if args.write and report["passed"]:
        written = write_run(report, proposal, receipt_output=args.receipt_output)
        report["written"] = {"receipt_path": written["receipt_path"]}
    printable = {k: v for k, v in report.items()
                 if k not in {"merged_package", "artifact_writes"}}
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
