#!/usr/bin/env python3
"""Acquire source bytes, ingest explicit custody records, and derive a verified receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import shutil
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402
from Shared.library.intake import schema_errors  # noqa: E402
from Shared.library.resolve import build_index  # noqa: E402
from Shared.library import source_custody  # noqa: E402
from Shared.tools import source_receipts  # noqa: E402

ACQUISITION_SCHEMA = REPO / "Shared/library/source-acquisition.schema.json"
CUSTODY_SCHEMA = REPO / "Shared/library/source-custody-manifest.schema.json"
PACKAGE_SCHEMA = REPO / "Shared/library/package.schema.json"


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


def _record_findings(record: dict, definition: str, repo: Path) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / "Shared/library/package.schema.json")
    local = {
        "$schema": schema.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$defs": schema["$defs"],
        "$ref": f"#/$defs/{definition}",
    }
    validator = jsonschema.Draft202012Validator(local)
    return [{
        "point": "SOURCE_INGEST_RECORD_STRUCTURE",
        "where": f"{definition}/" + "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(record)]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def acquire_file(*, path: Path, subject: str, bucket_id: str, resource_ref: str,
                 requested_locator: str, acquired_at: str,
                 snapshot_output: Path | None = None) -> dict:
    data = path.read_bytes()
    if not data:
        raise ValueError("source file is empty")
    if snapshot_output is not None:
        snapshot_output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, snapshot_output)
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return {
        "acquisition_id": f"ACQ-{_sha256(data)[:20].upper()}",
        "version": "1.0.0",
        "subject": subject,
        "bucket_id": bucket_id,
        "resource_ref": resource_ref,
        "source_kind": "FILE",
        "requested_locator": requested_locator,
        "resolved_locator": str(path),
        "acquired_at": acquired_at,
        "media_type": media_type,
        "byte_length": len(data),
        "sha256": _sha256(data),
        "snapshot_ref": str(snapshot_output) if snapshot_output is not None else str(path),
    }


def acquire_url(*, url: str, subject: str, bucket_id: str, resource_ref: str,
                acquired_at: str, snapshot_output: Path | None = None) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "Grade9V3-source-acquisition/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
        resolved = response.geturl()
        media_type = response.headers.get_content_type() or "application/octet-stream"
    if not data:
        raise ValueError("downloaded source is empty")
    if snapshot_output is not None:
        snapshot_output.parent.mkdir(parents=True, exist_ok=True)
        snapshot_output.write_bytes(data)
    return {
        "acquisition_id": f"ACQ-{_sha256(data)[:20].upper()}",
        "version": "1.0.0",
        "subject": subject,
        "bucket_id": bucket_id,
        "resource_ref": resource_ref,
        "source_kind": "URL",
        "requested_locator": url,
        "resolved_locator": resolved,
        "acquired_at": acquired_at,
        "media_type": media_type,
        "byte_length": len(data),
        "sha256": _sha256(data),
        "snapshot_ref": str(snapshot_output) if snapshot_output is not None else None,
    }


def verify_acquisition(acquisition: dict, repo: Path = REPO) -> dict:
    found = _schema_findings(
        acquisition, repo / "Shared/library/source-acquisition.schema.json",
        "SOURCE_ACQUISITION_STRUCTURE",
    )
    snapshot = acquisition.get("snapshot_ref")
    if snapshot:
        path = Path(snapshot)
        if not path.is_absolute():
            path = repo / path
        if not path.is_file():
            found.append({
                "point": "SOURCE_ACQUISITION_SNAPSHOT_MISSING",
                "where": str(snapshot),
                "detail": "snapshot_ref does not resolve to bytes",
            })
        else:
            data = path.read_bytes()
            if len(data) != acquisition.get("byte_length"):
                found.append({
                    "point": "SOURCE_ACQUISITION_LENGTH_MISMATCH",
                    "where": str(snapshot),
                    "detail": "snapshot byte length differs from acquisition metadata",
                })
            if _sha256(data) != acquisition.get("sha256"):
                found.append({
                    "point": "SOURCE_ACQUISITION_DIGEST_MISMATCH",
                    "where": str(snapshot),
                    "detail": "snapshot digest differs from acquisition metadata",
                })
    return {"passed": not found, "findings": found}


def _replace_or_append(rows: list[dict], record: dict, *, allow_resource_update: bool) -> tuple[list[dict], list[dict]]:
    found = []
    existing = next((row for row in rows if row.get("id") == record.get("id")), None)
    if existing is None:
        return rows + [record], found
    if existing == record:
        return rows, found
    if allow_resource_update and existing.get("locator") == record.get("locator"):
        return [record if row.get("id") == record.get("id") else row for row in rows], found
    found.append({
        "point": "SOURCE_INGEST_ID_COLLISION",
        "where": record.get("id", ""),
        "detail": "an unequal canonical record already owns this id",
    })
    return rows, found


def plan_ingestion(acquisition: dict, manifest: dict, package: dict,
                   repo: Path = REPO) -> dict:
    found = []
    found += _schema_findings(
        acquisition, repo / "Shared/library/source-acquisition.schema.json",
        "SOURCE_ACQUISITION_STRUCTURE",
    )
    found += _schema_findings(
        manifest, repo / "Shared/library/source-custody-manifest.schema.json",
        "SOURCE_CUSTODY_MANIFEST_STRUCTURE",
    )
    found += verify_acquisition(acquisition, repo)["findings"]

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    if manifest.get("acquisition_ref") != acquisition.get("acquisition_id"):
        fail("SOURCE_INGEST_ACQUISITION_MISMATCH", manifest.get("manifest_id", ""),
             "custody manifest does not name this acquisition")
    if package.get("subject") != acquisition.get("subject"):
        fail("SOURCE_INGEST_SUBJECT_MISMATCH", package.get("package_id", ""),
             "target package subject differs from acquisition subject")
    resource = manifest.get("resource") or {}
    if resource.get("id") != acquisition.get("resource_ref"):
        fail("SOURCE_INGEST_RESOURCE_MISMATCH", resource.get("id", ""),
             "resource id differs from acquisition.resource_ref")
    if resource.get("status") != "CANDIDATE":
        fail("SOURCE_INGEST_RESOURCE_NOT_CANDIDATE", resource.get("id", ""),
             "automated ingestion may create/update only CANDIDATE resources")
    if resource.get("origin") == "AUTHORED":
        fail("SOURCE_INGEST_AUTHORED_RESOURCE_AS_SOURCE", resource.get("id", ""),
             "source acquisition cannot turn an authored resource into external custody")
    if resource.get("locator") not in {
        acquisition.get("requested_locator"), acquisition.get("resolved_locator")
    }:
        fail("SOURCE_INGEST_RESOURCE_LOCATOR_MISMATCH", resource.get("id", ""),
             "resource locator does not match the acquired source")
    if resource.get("snapshot_digest") != acquisition.get("sha256"):
        fail("SOURCE_INGEST_RESOURCE_DIGEST_MISMATCH", resource.get("id", ""),
             "resource snapshot_digest must equal the acquired bytes")
    if resource.get("snapshot_ref") != acquisition.get("snapshot_ref"):
        fail("SOURCE_INGEST_RESOURCE_SNAPSHOT_MISMATCH", resource.get("id", ""),
             "resource snapshot_ref must equal the acquisition snapshot_ref")
    if resource.get("access_status") != manifest.get("access_status"):
        fail("SOURCE_INGEST_ACCESS_STATUS_MISMATCH", resource.get("id", ""),
             "resource access_status must equal the custody manifest inspection scope")
    found += _record_findings(resource, "resource", repo)

    questions = list(manifest.get("questions") or [])
    if questions and not acquisition.get("snapshot_ref"):
        fail("SOURCE_INGEST_SNAPSHOT_REQUIRED", acquisition.get("acquisition_id", ""),
             "exact question custody requires retained source bytes, not digest-only acquisition")
    for question in questions:
        qid = question.get("id", "")
        if question.get("status") != "CANDIDATE":
            fail("SOURCE_INGEST_QUESTION_NOT_CANDIDATE", qid,
                 "automated transcription may enter only as CANDIDATE")
        if question.get("origin") not in {"ORIGINAL", "ADAPTED"}:
            fail("SOURCE_INGEST_QUESTION_NOT_SOURCE_DERIVED", qid,
                 "custody ingestion accepts only ORIGINAL or ADAPTED source questions")
        if resource.get("id") not in question.get("source_refs", []):
            fail("SOURCE_INGEST_QUESTION_SOURCE_UNBOUND", qid,
                 "question must cite the acquired resource in source_refs")
        found += _record_findings(question, "question", repo)

    merged = json.loads(json.dumps(package))
    merged["resources"], collision = _replace_or_append(
        list(merged.get("resources", [])), resource, allow_resource_update=True)
    found += collision
    for question in questions:
        merged["questions"], collision = _replace_or_append(
            list(merged.get("questions", [])), question, allow_resource_update=False)
        found += collision

    try:
        records = build_index([merged])
    except Exception as exc:
        fail("SOURCE_INGEST_CUSTODY_INDEX_INVALID", manifest.get("manifest_id", ""), str(exc))
        records = None
    if records is not None:
        for question in questions:
            found += source_custody.validate_question(
                question,
                records=records,
                acquisition=acquisition,
                inspected_sections=manifest.get("inspection_sections") or [],
                access_status=manifest.get("access_status"),
                require_resolved=False,
                repo=repo,
            )

    for detail in schema_errors(merged):
        fail("SOURCE_INGEST_PACKAGE_STRUCTURE", manifest.get("target_package", ""), detail)

    receipt = None
    if not found:
        records = build_index([merged])
        coverage = source_receipts.derive_coverage(
            records, acquisition["bucket_id"], [resource["id"]],
            subject=acquisition["subject"], repo=repo)
        receipt = {
            "receipt_id": f'SRCREC-{manifest["manifest_id"]}',
            "version": "1.0.0",
            "subject": acquisition["subject"],
            "bucket_id": acquisition["bucket_id"],
            "source_basis": [acquisition["requested_locator"]],
            "resource_refs": [resource["id"]],
            "inspection": {
                "inspector_kind": "AGENT",
                "inspector_id": manifest["inspector_id"],
                "inspected_at": acquisition["acquired_at"],
                "access_status": manifest["access_status"],
                "sections": manifest["inspection_sections"],
                "content_sha256": acquisition["sha256"],
                "snapshot_ref": acquisition.get("snapshot_ref"),
            },
            "basis_assessment": {
                "status": "MATCH",
                "reason": "The custody manifest explicitly targets the acquired source and bucket.",
                "replacement_candidates": [],
            },
            "coverage": coverage,
            "notes": [
                "Generated by source_pipeline.py from a pinned acquisition, explicit custody manifest and question-level source-custody proof.",
                "Newly transcribed questions remain CANDIDATE and therefore cannot make coverage SUFFICIENT until separately reviewed/promoted.",
            ],
        }
        verification = source_receipts.verify(
            receipt, records_override=records, expected_bucket=acquisition["bucket_id"], repo=repo)
        if not verification["verified"]:
            found += verification["findings"]

    return {
        "passed": not found,
        "findings": found,
        "merged_package": merged if not found else None,
        "receipt": receipt if not found else None,
        "candidate_question_refs": [q.get("id") for q in questions],
        "package_digest_before": digest(package),
        "package_digest_after": digest(merged) if not found else None,
    }


def _load_acquisition(path: Path) -> dict:
    return load(path)


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def audit(repo: Path = REPO) -> dict:
    rows, findings = [], []
    for path in sorted((repo / "Sources/acquisitions").glob("*.json")) if (repo / "Sources/acquisitions").is_dir() else []:
        acquisition = load(path)
        report = verify_acquisition(acquisition, repo)
        rows.append({"path": str(path.relative_to(repo)), **report})
        findings += report["findings"]
    return {"acquisitions": rows, "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    acquire = sub.add_parser("acquire")
    source = acquire.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--file", type=Path)
    acquire.add_argument("--subject", required=True)
    acquire.add_argument("--bucket", required=True)
    acquire.add_argument("--resource-ref", required=True)
    acquire.add_argument("--locator", required=True)
    acquire.add_argument("--acquired-at", required=True)
    acquire.add_argument("--snapshot-output", type=Path)
    acquire.add_argument("--output", type=Path, required=True)

    ingest = sub.add_parser("ingest")
    ingest.add_argument("--acquisition", type=Path, required=True)
    ingest.add_argument("--manifest", type=Path, required=True)
    ingest.add_argument("--write", action="store_true")
    ingest.add_argument("--receipt-output", type=Path)

    check = sub.add_parser("audit")
    check.add_argument("--enforce", action="store_true")

    args = parser.parse_args()

    if args.command == "acquire":
        if args.url:
            result = acquire_url(
                url=args.url, subject=args.subject, bucket_id=args.bucket,
                resource_ref=args.resource_ref, acquired_at=args.acquired_at,
                snapshot_output=args.snapshot_output)
        else:
            result = acquire_file(
                path=args.file, subject=args.subject, bucket_id=args.bucket,
                resource_ref=args.resource_ref, requested_locator=args.locator,
                acquired_at=args.acquired_at, snapshot_output=args.snapshot_output)
        _write_json(args.output, result)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "ingest":
        acquisition = _load_acquisition(args.acquisition)
        manifest = load(args.manifest)
        target = REPO / manifest["target_package"]
        package = load(target)
        report = plan_ingestion(acquisition, manifest, package)
        if args.write and report["passed"]:
            _write_json(target, report["merged_package"])
            receipt_output = args.receipt_output or (
                REPO / "Sources/receipts" / (report["receipt"]["receipt_id"] + ".json"))
            _write_json(receipt_output, report["receipt"])
        printable = {k: v for k, v in report.items() if k != "merged_package"}
        print(json.dumps(printable, indent=2, ensure_ascii=False))
        return 0 if report["passed"] else 1

    report = audit()
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] or not args.enforce else 1


if __name__ == "__main__":
    raise SystemExit(main())
