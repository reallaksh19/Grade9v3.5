#!/usr/bin/env python3
"""Authorize CANDIDATE -> REVIEWED -> CURATED using digest-bound external receipts."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402
from Shared.library import intake, promote, source_custody  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402

REQUEST_SCHEMA = REPO / "Shared/library/review-promotion-request.schema.json"
RECEIPT_SCHEMA = REPO / "Shared/library/review-promotion-receipt.schema.json"
AUTHORING_RECEIPT_SCHEMA = REPO / "Shared/library/authoring-run-receipt.schema.json"

STAGE_NEXT = {"CANDIDATE": "REVIEWED", "REVIEWED": "CURATED"}


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


def _safe_path(path_text: str, root: Path, repo: Path = REPO) -> Path | None:
    candidate = (repo / path_text).resolve()
    try:
        candidate.relative_to((repo / root).resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() else None


def _target_path(path_text: str, subject: str, repo: Path = REPO) -> Path | None:
    candidate = (repo / path_text).resolve()
    try:
        candidate.relative_to((repo / subject / "library").resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() and candidate.suffix == ".json" else None


def _record_location(package: dict, record_id: str) -> tuple[str, int, dict] | None:
    for collection, rows in package.items():
        if not isinstance(rows, list):
            continue
        for index, row in enumerate(rows):
            if isinstance(row, dict) and row.get("id") == record_id:
                return collection, index, row
    return None


def _load_pinned(ref: dict | None, root: Path, schema: Path,
                 missing_point: str, stale_point: str,
                 repo: Path = REPO) -> tuple[dict | None, list[dict]]:
    found = []
    if not ref:
        return None, [{"point": missing_point, "where": "", "detail": "required receipt reference is missing"}]
    path = _safe_path(ref.get("path", ""), root, repo)
    if path is None:
        return None, [{"point": missing_point, "where": ref.get("path", ""),
                       "detail": "receipt path does not resolve inside the required repository root"}]
    value = load(path)
    found.extend(_schema_findings(value, schema, missing_point + "_STRUCTURE"))
    if digest(value) != ref.get("digest"):
        found.append({"point": stale_point, "where": ref.get("path", ""),
                      "detail": "receipt digest differs from the pinned digest"})
    return value, found


def _authoring_receipt(ref: dict | None, repo: Path = REPO) -> tuple[dict | None, list[dict]]:
    return _load_pinned(
        ref, Path("publication/authoring-runs"), AUTHORING_RECEIPT_SCHEMA,
        "REVIEW_AUTHORING_RECEIPT_INVALID", "REVIEW_AUTHORING_RECEIPT_STALE", repo)


def _promotion_receipt(ref: dict | None, repo: Path = REPO) -> tuple[dict | None, list[dict]]:
    return _load_pinned(
        ref, Path("Reviews/receipts"), RECEIPT_SCHEMA,
        "PRIOR_PROMOTION_RECEIPT_INVALID", "PRIOR_PROMOTION_RECEIPT_STALE", repo)


def _author_changed_record(receipt: dict, record_id: str) -> dict | None:
    return next((row for row in receipt.get("changed_records", [])
                 if row.get("id") == record_id), None)


def _subject_records(subject: str, replacement_path: Path | None = None,
                     replacement_package: dict | None = None,
                     repo: Path = REPO) -> dict:
    packages = []
    for path in sorted((repo / subject / "library").glob("*.json")):
        if replacement_path is not None and path.resolve() == replacement_path.resolve():
            packages.append(replacement_package)
        else:
            packages.append(load(path))
    return build_index(packages)


def verify_receipt(receipt: dict, record: dict, repo: Path = REPO) -> dict:
    """Verify a stored promotion receipt against the exact current/reconstructed record."""
    found = _schema_findings(
        receipt, repo / "Shared/library/review-promotion-receipt.schema.json",
        "REVIEW_PROMOTION_RECEIPT_STRUCTURE",
    )

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    if receipt.get("record_id") != record.get("id"):
        fail("REVIEW_RECEIPT_RECORD_MISMATCH", receipt.get("record_id", ""),
             "receipt names a different record")
    if receipt.get("record_digest_after") != digest(record):
        fail("REVIEW_RECEIPT_RECORD_STALE", record.get("id", ""),
             "current record digest differs from the reviewed/curated digest")

    to_stage = receipt.get("to_stage")
    from_stage = receipt.get("from_stage")
    if STAGE_NEXT.get(from_stage) != to_stage:
        fail("REVIEW_RECEIPT_STAGE_SKIP", receipt.get("promotion_id", ""),
             f"illegal promotion chain {from_stage} -> {to_stage}")
    if record.get("status") != to_stage:
        fail("REVIEW_RECEIPT_STATUS_MISMATCH", record.get("id", ""),
             f"record status is {record.get('status')} but receipt grants {to_stage}")

    before = copy.deepcopy(record)
    before["status"] = from_stage
    if digest(before) != receipt.get("record_digest_before"):
        fail("REVIEW_RECEIPT_HIDDEN_EDIT", record.get("id", ""),
             "promotion receipt cannot be explained by a status-only transition")

    evidence = receipt.get("evidence") or {}
    authoring_actor = receipt.get("authoring_actor_id")

    if to_stage == "REVIEWED":
        if evidence.get("kind") != "INDEPENDENT_REVIEW":
            fail("REVIEW_EVIDENCE_KIND_MISMATCH", record.get("id", ""),
                 "REVIEWED requires independent-review evidence")
        if evidence.get("reviewer_id") == authoring_actor:
            fail("SELF_REVIEW_NOT_INDEPENDENT", record.get("id", ""),
                 "author cannot review their own record")
        if evidence.get("originals_inspected") is not True:
            fail("REVIEW_DID_NOT_INSPECT_ORIGINALS", record.get("id", ""),
                 "independent review did not inspect the original material")
        authoring, issues = _authoring_receipt(receipt.get("authoring_run_receipt"), repo)
        found.extend(issues)
        if authoring:
            changed = _author_changed_record(authoring, record.get("id", ""))
            if not changed:
                fail("REVIEW_RECORD_NOT_IN_AUTHORING_RECEIPT", record.get("id", ""),
                     "authoring receipt does not claim creation of this record")
            elif changed.get("sha256") != receipt.get("record_digest_before"):
                fail("REVIEW_AUTHORING_DIGEST_MISMATCH", record.get("id", ""),
                     "reviewed candidate digest differs from the authoring receipt")
            if authoring.get("actor_id") != authoring_actor:
                fail("REVIEW_AUTHOR_ID_MISMATCH", record.get("id", ""),
                     "promotion receipt authoring actor differs from the authoring receipt")
        if receipt.get("prior_promotion_receipt") is not None:
            fail("REVIEW_UNEXPECTED_PRIOR_PROMOTION", record.get("id", ""),
                 "first review must chain from authoring, not another promotion")

    elif to_stage == "CURATED":
        if evidence.get("kind") != "CURATION_ACCEPTANCE":
            fail("CURATION_EVIDENCE_KIND_MISMATCH", record.get("id", ""),
                 "CURATED requires curation-acceptance evidence")
        if evidence.get("accepted_by") == authoring_actor:
            fail("SELF_CURATE_NOT_INDEPENDENT", record.get("id", ""),
                 "original author cannot curate their own record")
        prior, issues = _promotion_receipt(receipt.get("prior_promotion_receipt"), repo)
        found.extend(issues)
        if prior:
            if prior.get("record_id") != record.get("id") or prior.get("to_stage") != "REVIEWED":
                fail("CURATION_PRIOR_REVIEW_MISMATCH", record.get("id", ""),
                     "curation must chain from a REVIEWED receipt for the same record")
            if prior.get("record_digest_after") != receipt.get("record_digest_before"):
                fail("CURATION_PRIOR_DIGEST_MISMATCH", record.get("id", ""),
                     "curation input digest differs from the prior reviewed digest")
            reviewed = copy.deepcopy(record)
            reviewed["status"] = "REVIEWED"
            prior_report = verify_receipt(prior, reviewed, repo)
            found.extend(prior_report["findings"])
            if prior.get("authoring_actor_id") != authoring_actor:
                fail("CURATION_AUTHOR_CHAIN_MISMATCH", record.get("id", ""),
                     "curation receipt changes the original author identity")
        if receipt.get("authoring_run_receipt") is not None:
            fail("CURATION_UNEXPECTED_AUTHORING_RECEIPT", record.get("id", ""),
                 "curation must chain through the prior REVIEWED receipt")
    else:
        fail("REVIEW_RECEIPT_UNKNOWN_STAGE", str(to_stage or ""),
             "promotion receipt grants an unsupported stage")

    return {"verified": not found, "findings": found, "stage": to_stage,
            "record_id": receipt.get("record_id"), "promotion_id": receipt.get("promotion_id")}


def receipt_store(repo: Path = REPO) -> list[tuple[str, dict]]:
    root = repo / "Reviews/receipts"
    if not root.is_dir():
        return []
    return [(str(path.relative_to(repo)), load(path)) for path in sorted(root.glob("*.json"))]


def authority_for_record(subject: str, target_package: str, record: dict,
                         repo: Path = REPO) -> dict:
    """Return receipt-backed effective review stage for one current canonical record."""
    status = record.get("status", "CANDIDATE")
    if status == "CANDIDATE":
        return {"state": "CANDIDATE", "record_status": status, "receipt": None,
                "findings": [], "verified": True}
    if status not in {"REVIEWED", "CURATED"}:
        return {"state": "NOT_REVIEWED", "record_status": status, "receipt": None,
                "findings": [{"point": "REVIEW_STATUS_NOT_RELEASE_STAGE",
                              "where": record.get("id", ""),
                              "detail": f"status {status} is not a release review stage"}],
                "verified": False}

    candidates = [
        (path, receipt) for path, receipt in receipt_store(repo)
        if receipt.get("subject") == subject
        and receipt.get("target_package") == target_package
        and receipt.get("record_id") == record.get("id")
        and receipt.get("to_stage") == status
    ]
    reports = []
    for path, receipt in candidates:
        report = verify_receipt(receipt, record, repo)
        reports.append({"path": path, "receipt": receipt, "report": report})
        if report["verified"]:
            return {"state": status, "record_status": status, "receipt": path,
                    "promotion_id": receipt.get("promotion_id"),
                    "findings": [], "verified": True}
    findings = [item for row in reports for item in row["report"]["findings"]]
    if not candidates:
        findings.append({
            "point": "REVIEW_STATUS_UNBACKED",
            "where": record.get("id", ""),
            "detail": f"record claims {status} but no matching promotion receipt exists",
        })
    return {"state": "UNBACKED_" + status, "record_status": status, "receipt": None,
            "findings": findings, "verified": False}


def validate_promotion(request: dict, repo: Path = REPO) -> dict:
    found = _schema_findings(
        request, repo / "Shared/library/review-promotion-request.schema.json",
        "REVIEW_PROMOTION_REQUEST_STRUCTURE",
    )

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    subject = request.get("subject", "")
    target = _target_path(request.get("target_package", ""), subject, repo)
    if target is None:
        fail("REVIEW_TARGET_PACKAGE_INVALID", request.get("target_package", ""),
             "target package must be an existing JSON package inside subject/library")
        return {"passed": False, "findings": found, "receipt": None, "merged_package": None}

    package = load(target)
    located = _record_location(package, request.get("record_id", ""))
    if located is None:
        fail("REVIEW_TARGET_RECORD_MISSING", request.get("record_id", ""),
             "target package does not contain this record")
        return {"passed": False, "findings": found, "receipt": None, "merged_package": None}
    collection, index, record = located

    if digest(record) != request.get("record_digest"):
        fail("REVIEW_TARGET_RECORD_STALE", record.get("id", ""),
             "record changed after the review request was prepared")

    current = record.get("status", "CANDIDATE")
    target_stage = request.get("target_stage")
    if STAGE_NEXT.get(current) != target_stage:
        fail("REVIEW_PROMOTION_STAGE_INVALID", record.get("id", ""),
             f"only {current} -> {STAGE_NEXT.get(current)} is legal, not {target_stage}")

    if (target_stage == "REVIEWED" and collection == "questions"
            and record.get("origin") in {"ORIGINAL", "ADAPTED"}):
        try:
            custody_records = _subject_records(subject, target, package, repo)
        except Exception as exc:
            fail("REVIEW_SOURCE_CUSTODY_LIBRARY_UNREADABLE", record.get("id", ""), str(exc))
        else:
            found.extend(source_custody.validate_question(
                record, records=custody_records, require_resolved=True, repo=repo))

    evidence = request.get("evidence") or {}
    authoring_actor = None
    if target_stage == "REVIEWED":
        if evidence.get("kind") != "INDEPENDENT_REVIEW":
            fail("REVIEW_EVIDENCE_KIND_MISMATCH", record.get("id", ""),
                 "CANDIDATE -> REVIEWED requires independent-review evidence")
        authoring, issues = _authoring_receipt(request.get("authoring_run_receipt"), repo)
        found.extend(issues)
        if request.get("prior_promotion_receipt") is not None:
            fail("REVIEW_UNEXPECTED_PRIOR_PROMOTION", record.get("id", ""),
                 "first review cannot provide a prior promotion receipt")
        if authoring:
            changed = _author_changed_record(authoring, record.get("id", ""))
            if not changed or changed.get("sha256") != digest(record):
                fail("REVIEW_AUTHORING_DIGEST_MISMATCH", record.get("id", ""),
                     "current candidate is not the exact record created by the authoring receipt")
            authoring_actor = authoring.get("actor_id")
            if evidence.get("reviewer_id") == authoring_actor:
                fail("SELF_REVIEW_NOT_INDEPENDENT", record.get("id", ""),
                     "author cannot review their own record")
    elif target_stage == "CURATED":
        if evidence.get("kind") != "CURATION_ACCEPTANCE":
            fail("CURATION_EVIDENCE_KIND_MISMATCH", record.get("id", ""),
                 "REVIEWED -> CURATED requires curation acceptance")
        prior, issues = _promotion_receipt(request.get("prior_promotion_receipt"), repo)
        found.extend(issues)
        if request.get("authoring_run_receipt") is not None:
            fail("CURATION_UNEXPECTED_AUTHORING_RECEIPT", record.get("id", ""),
                 "curation must chain through the prior review receipt")
        if prior:
            if prior.get("record_id") != record.get("id") or prior.get("to_stage") != "REVIEWED":
                fail("CURATION_PRIOR_REVIEW_MISMATCH", record.get("id", ""),
                     "prior receipt must grant REVIEWED to this record")
            if prior.get("record_digest_after") != digest(record):
                fail("CURATION_PRIOR_DIGEST_MISMATCH", record.get("id", ""),
                     "current reviewed record changed after its prior review")
            prior_report = verify_receipt(prior, record, repo)
            found.extend(prior_report["findings"])
            authoring_actor = prior.get("authoring_actor_id")
            if evidence.get("accepted_by") == authoring_actor:
                fail("SELF_CURATE_NOT_INDEPENDENT", record.get("id", ""),
                     "original author cannot curate their own record")

    if found:
        return {"passed": False, "findings": found, "receipt": None, "merged_package": None}

    merged = copy.deepcopy(package)
    merged[collection][index]["status"] = target_stage

    intake_report = intake.check(merged)
    if not intake_report["admitted"]:
        for item in intake_report["findings"]:
            fail("REVIEW_PROMOTED_PACKAGE_REJECTED", request.get("target_package", ""),
                 f"{item['point']}: {item['detail']}")

    records = _subject_records(subject, target, merged, repo)
    maturity = promote.maturity_violations(records)
    for row in maturity:
        if row.get("record") == record.get("id"):
            fail("REVIEW_PROMOTION_DEPENDENCY_IMMATURITY", record.get("id", ""),
                 f"promoted record would outrank dependency {row['depends_on']} ({row['dependency_status']})")

    if found:
        return {"passed": False, "findings": found, "receipt": None, "merged_package": None}

    promoted = merged[collection][index]
    receipt = {
        "promotion_id": request["promotion_id"],
        "version": "1.0.0",
        "subject": subject,
        "target_package": request["target_package"],
        "record_id": record["id"],
        "from_stage": current,
        "to_stage": target_stage,
        "record_digest_before": digest(record),
        "record_digest_after": digest(promoted),
        "package_digest_before": digest(package),
        "package_digest_after": digest(merged),
        "authoring_actor_id": authoring_actor,
        "evidence": evidence,
        "authoring_run_receipt": request.get("authoring_run_receipt"),
        "prior_promotion_receipt": request.get("prior_promotion_receipt"),
        "validation": {
            "state": "VALIDATED",
            "findings": [],
            "note": "Promotion receipt proves evidence/stage/digest authority only; it does not prove learner outcomes.",
        },
    }
    receipt_findings = _schema_findings(
        receipt, repo / "Shared/library/review-promotion-receipt.schema.json",
        "REVIEW_PROMOTION_RECEIPT_STRUCTURE",
    )
    if receipt_findings:
        found.extend(receipt_findings)
        receipt = None

    return {
        "passed": not found,
        "findings": found,
        "receipt": receipt,
        "merged_package": merged if not found else None,
    }


def write_promotion(report: dict, repo: Path = REPO) -> dict:
    if not report.get("passed") or report.get("receipt") is None:
        raise ValueError("cannot write a rejected promotion")
    receipt = report["receipt"]
    target = repo / receipt["target_package"]
    target.write_text(json.dumps(report["merged_package"], indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    out = repo / "Reviews/receipts" / f'{receipt["promotion_id"]}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"receipt_path": str(out.relative_to(repo)), "receipt": receipt}


def audit(repo: Path = REPO) -> dict:
    rows, findings = [], []
    for path, receipt in receipt_store(repo):
        target = _target_path(receipt.get("target_package", ""), receipt.get("subject", ""), repo)
        if target is None:
            report = {"verified": False, "findings": [{
                "point": "REVIEW_RECEIPT_TARGET_MISSING", "where": path,
                "detail": "receipt target package no longer resolves"}]}
        else:
            package = load(target)
            located = _record_location(package, receipt.get("record_id", ""))
            if located is None:
                report = {"verified": False, "findings": [{
                    "point": "REVIEW_RECEIPT_RECORD_MISSING", "where": path,
                    "detail": "receipt target record no longer exists"}]}
            else:
                record = located[2]
                # A historical REVIEWED receipt under a currently CURATED record is
                # verified as part of the CURATED chain; audit only the current-stage receipt.
                if record.get("status") != receipt.get("to_stage"):
                    continue
                report = verify_receipt(receipt, record, repo)
        rows.append({"path": path, **report})
        findings.extend(report.get("findings", []))
    return {"receipts": rows, "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    if args.audit:
        report = audit()
    elif args.request:
        report = validate_promotion(load(args.request))
        if args.write and report["passed"]:
            report["written"] = write_promotion(report)
    else:
        parser.error("provide --request or --audit")

    printable = {k: v for k, v in report.items() if k != "merged_package"}
    print(json.dumps(printable, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report.get("passed", True) else 0


if __name__ == "__main__":
    raise SystemExit(main())
