#!/usr/bin/env python3
"""Validate source-inspection receipts against the canonical subject library."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402
from Shared.library.practice_inventory import bucket_capabilities  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402
from Shared.library import source_custody  # noqa: E402
from Shared.tools import review_authority  # noqa: E402

SCHEMA = REPO / "Shared/library/source-inspection-receipt.schema.json"
RECEIPTS = REPO / "Sources/receipts"
CORES = ("CORE2", "CORE2A", "CORE2B")


def store(repo: Path = REPO) -> dict[str, dict]:
    found = {}
    root = repo / "Sources/receipts"
    if not root.is_dir():
        return found
    for path in sorted(root.glob("*.json")):
        receipt = load(path)
        rid = receipt.get("receipt_id")
        if rid:
            found[rid] = {**receipt, "_path": str(path.relative_to(repo))}
    return found


def _records(subject: str, repo: Path) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def _schema_findings(receipt: dict, repo: Path) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    validator = jsonschema.Draft202012Validator(load(repo / "Shared/library/source-inspection-receipt.schema.json"))
    public = {key: value for key, value in receipt.items() if not key.startswith("_")}
    return [{
        "point": "SOURCE_RECEIPT_STRUCTURE",
        "where": "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(public)]


def _package_paths(subject: str, repo: Path) -> dict[str, str]:
    found = {}
    for path in sorted((repo / subject / "library").glob("*.json")):
        package = load(path)
        pid = package.get("package_id")
        if pid:
            found[pid] = str(path.relative_to(repo))
    return found


def _public(record: dict) -> dict:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def derive_coverage(records: dict, bucket_id: str, resource_refs: list[str],
                    subject: str | None = None, repo: Path = REPO) -> dict:
    """Derive structural source coverage from reviewed canonical questions.

    SUFFICIENT is intentionally strict: every capability taught by the bucket must be
    represented by at least one REVIEWED/CURATED source-bound question eligible for that
    Core. Candidate transcription is evidence-in-progress, not custody authority.
    """
    owned = bucket_capabilities(records, bucket_id)
    resources = set(resource_refs)
    package_paths = _package_paths(subject, repo) if subject else {}
    eligible = []
    for row in records.values():
        if row.get("_collection") != "questions":
            continue
        if row.get("status") not in {"REVIEWED", "CURATED"}:
            continue
        if row.get("primary_capability_ref") not in owned:
            continue
        if not (set(row.get("source_refs", [])) & resources):
            continue
        if subject:
            target = package_paths.get(row.get("_package"))
            authority = (
                review_authority.authority_for_record(subject, target, _public(row), repo)
                if target else {"verified": False}
            )
            if not authority.get("verified") or authority.get("state") not in {"REVIEWED", "CURATED"}:
                continue
        eligible.append(row)

    result = {}
    for core in CORES:
        if core == "CORE2":
            questions = [
                q for q in eligible
                if source_custody.valid_for_core2(q, records, repo)
            ]
        else:
            questions = [
                q for q in eligible
                if any(exposure.get("core") == core for exposure in q.get("exposure", []))
            ]
        represented = {q.get("primary_capability_ref") for q in questions}
        missing = sorted(owned - represented)
        status = "SUFFICIENT" if owned and not missing else "INSUFFICIENT"
        result[core] = {
            "status": status,
            "question_refs": sorted(q["id"] for q in questions),
            "basis": (
                "Every bucket-owned capability has reviewed/curated source-bound question evidence for this Core."
                if status == "SUFFICIENT"
                else "Missing reviewed/curated source-bound coverage for: "
                + (", ".join(missing) if missing else "all bucket capabilities")
            ),
        }
    return result


def verify(receipt: dict, *, request: dict | None = None,
           expected_bucket: str | None = None, records_override: dict | None = None,
           repo: Path = REPO) -> dict:
    found = list(_schema_findings(receipt, repo))

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    subject = receipt.get("subject", "")
    try:
        records = records_override if records_override is not None else (_records(subject, repo) if subject else {})
    except Exception as exc:
        records = {}
        fail("SOURCE_RECEIPT_LIBRARY_UNREADABLE", subject, str(exc))

    if expected_bucket and receipt.get("bucket_id") != expected_bucket:
        fail("SOURCE_RECEIPT_BUCKET_MISMATCH", receipt.get("bucket_id", ""),
             f"receipt is for {receipt.get('bucket_id')} but request resolves to {expected_bucket}")

    if request is not None:
        expected_sources = sorted(request.get("source_basis", []))
        if sorted(receipt.get("source_basis", [])) != expected_sources:
            fail("SOURCE_RECEIPT_BASIS_MISMATCH", receipt.get("receipt_id", ""),
                 "receipt source_basis does not exactly match the request source_basis")
        if receipt.get("subject") != request.get("subject"):
            fail("SOURCE_RECEIPT_SUBJECT_MISMATCH", receipt.get("subject", ""),
                 f"receipt subject differs from request subject {request.get('subject')}")

    resources = []
    for ref in receipt.get("resource_refs", []):
        record = records.get(ref)
        if not record or record.get("_collection") != "resources":
            fail("SOURCE_RECEIPT_RESOURCE_DANGLING", ref,
                 "receipt names a resource not held in the canonical subject library")
            continue
        resources.append(record)

    locators = {row.get("locator") for row in resources}
    for basis in receipt.get("source_basis", []):
        if basis not in locators:
            fail("SOURCE_RECEIPT_BASIS_NOT_LIBRARY_RESOURCE", basis,
                 "requested source basis is not the locator of a receipt-bound resource")

    inspection = receipt.get("inspection") or {}
    if inspection.get("inspector_kind") == "LEGACY_METADATA_MIGRATION":
        for core in CORES:
            if (receipt.get("coverage", {}).get(core) or {}).get("status") == "SUFFICIENT":
                fail("LEGACY_RECEIPT_CANNOT_ASSERT_SUFFICIENCY", core,
                     "migrated metadata may preserve an inspection fact but cannot prove product coverage")

    owned = bucket_capabilities(records, receipt.get("bucket_id", ""))
    resource_ids = set(receipt.get("resource_refs", []))
    any_sufficient = any(
        ((receipt.get("coverage") or {}).get(core) or {}).get("status") == "SUFFICIENT"
        for core in CORES
    )
    if any_sufficient and not inspection.get("content_sha256"):
        fail("SOURCE_RECEIPT_SUFFICIENT_WITHOUT_CONTENT_DIGEST",
             receipt.get("receipt_id", ""),
             "SUFFICIENT coverage requires a digest of the inspected source content")

    for core in CORES:
        claim = (receipt.get("coverage") or {}).get(core) or {}
        status = claim.get("status")
        refs = claim.get("question_refs", [])
        if status == "SUFFICIENT" and not refs:
            fail("SOURCE_RECEIPT_SUFFICIENT_WITHOUT_QUESTIONS", core,
                 "sufficiency requires at least one evidenced canonical question")
        represented = set()
        for qref in refs:
            question = records.get(qref)
            if not question or question.get("_collection") != "questions":
                fail("SOURCE_RECEIPT_QUESTION_DANGLING", qref,
                     f"{core} coverage names a question not held in the canonical library")
                continue
            capability_in_scope = question.get("primary_capability_ref") in owned
            if not capability_in_scope:
                fail("SOURCE_RECEIPT_QUESTION_OUTSIDE_BUCKET", qref,
                     "question primary capability is not taught by this bucket")
            if not (set(question.get("source_refs", [])) & resource_ids):
                fail("SOURCE_RECEIPT_QUESTION_SOURCE_MISMATCH", qref,
                     "question is not bound to any resource evidenced by this receipt")
            if status == "SUFFICIENT":
                if question.get("status") not in {"REVIEWED", "CURATED"}:
                    fail("SOURCE_RECEIPT_UNREVIEWED_QUESTION_CLAIMS_SUFFICIENCY", qref,
                         "SUFFICIENT coverage may cite only REVIEWED or CURATED questions")
                else:
                    target = _package_paths(subject, repo).get(question.get("_package"))
                    authority = (
                        review_authority.authority_for_record(subject, target, _public(question), repo)
                        if target else {"verified": False, "state": "NOT_REVIEWED"}
                    )
                    if not authority.get("verified") or authority.get("state") not in {"REVIEWED", "CURATED"}:
                        fail("SOURCE_RECEIPT_UNBACKED_REVIEW_CLAIMS_SUFFICIENCY", qref,
                             "question status is not backed by a valid digest-bound promotion receipt")
            if core == "CORE2":
                if question.get("origin") not in {"ORIGINAL", "ADAPTED"}:
                    fail("SOURCE_RECEIPT_CORE2_AUTHORED_QUESTION", qref,
                         "Core2 custody cannot be established by an AUTHORED question")
                    custody_ok = False
                else:
                    custody_findings = source_custody.validate_question(
                        question, records=records, require_resolved=True, repo=repo)
                    found.extend(custody_findings)
                    custody_ok = not custody_findings
                if capability_in_scope and custody_ok:
                    represented.add(question.get("primary_capability_ref"))
            else:
                if not any(row.get("core") == core for row in question.get("exposure", [])):
                    fail("SOURCE_RECEIPT_QUESTION_NOT_EXPOSED", qref,
                         f"question is not exposed to {core}")
                elif capability_in_scope:
                    represented.add(question.get("primary_capability_ref"))
        if status == "SUFFICIENT":
            missing = sorted(owned - represented)
            if missing:
                fail("SOURCE_RECEIPT_CAPABILITY_COVERAGE_INCOMPLETE", core,
                     "SUFFICIENT coverage misses bucket capabilities: " + ", ".join(missing))

    verified = not found
    return {
        "receipt_id": receipt.get("receipt_id"),
        "path": receipt.get("_path"),
        "digest": digest({k: v for k, v in receipt.items() if not k.startswith("_")}),
        "verified": verified,
        "coverage": receipt.get("coverage", {}),
        "inspection": receipt.get("inspection"),
        "basis_assessment": receipt.get("basis_assessment"),
        "resource_refs": receipt.get("resource_refs", []),
        "findings": found,
    }


def resolve(receipt_ref: str | None, *, request: dict | None = None,
            expected_bucket: str | None = None, repo: Path = REPO) -> dict:
    if not receipt_ref:
        return {
            "receipt_id": None, "verified": False, "state": "MISSING",
            "coverage": {}, "findings": [],
        }
    receipt = store(repo).get(receipt_ref)
    if receipt is None:
        return {
            "receipt_id": receipt_ref, "verified": False, "state": "DANGLING",
            "coverage": {},
            "findings": [{
                "point": "SOURCE_RECEIPT_REF_DANGLING",
                "where": receipt_ref,
                "detail": "no source inspection receipt carries this id",
            }],
        }
    report = verify(receipt, request=request, expected_bucket=expected_bucket, repo=repo)
    return {**report, "state": "VERIFIED" if report["verified"] else "INVALID"}


def audit(repo: Path = REPO) -> dict:
    rows = []
    findings = []
    for rid, receipt in store(repo).items():
        report = verify(receipt, repo=repo)
        rows.append(report)
        findings.extend(report["findings"])
    return {"receipts": rows, "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--receipt")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = resolve(args.receipt) if args.receipt else audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report.get("passed", report.get("verified", False)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
