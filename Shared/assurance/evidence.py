"""Evidence records (assurance-evidence/v1): build, write, load and verify.

The schema in Shared/assurance/assurance-evidence.schema.json is the only definition of the shape; this module builds records that satisfy it and
refuses to write or read one that does not. A record is bound to the content it judges by the subject digest, and its id is the digest of the
record without its timestamp and id, so the same judgment of the same content always has the same id and a changed judgment cannot keep an old one.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from Shared.assurance import contract
from Shared.contracts import canonical

SUBJECT_KINDS = ("CANONICAL_RECORD", "PRODUCT", "PROJECTION", "SOURCE")
ALIASES = {"library": "CANONICAL_RECORD", "package": "CANONICAL_RECORD", "question": "CANONICAL_RECORD", "record": "CANONICAL_RECORD",
           "product": "PRODUCT", "projection": "PROJECTION", "source": "SOURCE"}
OUTCOMES = ("PASS", "FAIL", "INCONCLUSIVE", "NOT_APPLICABLE", "NOT_RUN")
SEVERITIES = ("S0", "S1", "S2", "S3")          # worst first


def subject_kind(value: str) -> str:
    """The schema's subject kind for `value`. A kind that is not one of them, or a known alias, is an error: it is not passed through."""
    if value in SUBJECT_KINDS:
        return value
    if value.lower() in ALIASES:
        return ALIASES[value.lower()]
    raise ValueError(f"unknown subject kind {value!r}; it is one of {', '.join(SUBJECT_KINDS)}")


def finding(code: str, severity: str, subject: str, message: str, *, location: str | None = None, evidence: dict | None = None) -> dict:
    row = {"code": code, "severity": severity, "subject": subject, "message": message}
    if location:
        row["location"] = location
    if evidence:
        row["evidence"] = evidence
    return row


def worst(severities) -> str | None:
    found = [s for s in severities if s in SEVERITIES]
    return min(found, key=SEVERITIES.index) if found else None


def evidence_id(record: dict) -> str:
    body = {k: v for k, v in record.items() if k not in ("evidence_id", "produced_at")}
    return "AE-" + hashlib.sha256(canonical(body)).hexdigest()[:16]


def make_evidence(assurance_type: str, subject_kind_: str, subject_id: str, outcome: str, producer_name: str, producer_version: str,
                  findings: list[dict] | None = None, confidence: float | None = None, dependencies: list[str] | None = None,
                  subject_digest: str | None = None, producer_config_digest: str | None = None, severity: str | None = None,
                  configuration: dict | None = None) -> dict:
    """Build a record that satisfies assurance-evidence/v1, or raise.

    `subject_digest` is required: evidence that is not bound to the content it judged cannot be told stale. `configuration` is what the verifier
    was configured with (thresholds, policy digests); its digest is the producer's configuration digest.
    """
    if outcome not in OUTCOMES:
        raise ValueError(f"unknown outcome {outcome!r}; it is one of {', '.join(OUTCOMES)}")
    if subject_digest is None:
        raise ValueError("evidence must carry the digest of the subject it judged (subject_digest)")
    findings = list(findings or [])
    if outcome == "PASS" and any(f.get("severity") in ("S0", "S1") for f in findings):
        raise ValueError("a PASS cannot carry an S0 or S1 finding")
    record = {
        "schema": "assurance-evidence/v1",
        "assurance_type": assurance_type,
        "subject": {"kind": subject_kind(subject_kind_), "id": subject_id, "digest": subject_digest},
        "producer": {"name": producer_name, "version": producer_version,
                     "configuration_digest": producer_config_digest or contract.digest(configuration or {})},
        "outcome": outcome,
        "findings": findings,
        "dependencies": sorted(dependencies or []),
        "produced_at": contract.now(),
    }
    if outcome == "FAIL":
        record["severity"] = worst([severity, *[f.get("severity") for f in findings]]) or "S1"
    if confidence is not None:
        record["confidence"] = confidence
    record["evidence_id"] = evidence_id(record)
    return contract.require_valid("evidence", record)


def validate_evidence(record: dict) -> bool:
    """True when `record` satisfies the schema and its id is the digest of its content; the problems go to stderr."""
    problems = contract.schema_problems("evidence", record)
    if not problems and record.get("evidence_id") != evidence_id(record):
        problems = ["evidence_id is not the digest of the record's content"]
    for line in problems:
        print(line, file=sys.stderr)
    return not problems


def write_evidence(record: dict, output_path: Path) -> None:
    """Write one evidence record. Refused if the record is invalid, or if the path is inside a subject tree (standalone/, docs/, public/)."""
    contract.require_valid("evidence", record)
    if record["evidence_id"] != evidence_id(record):
        raise contract.ContractViolation("evidence", ["evidence_id is not the digest of the record's content"])
    if not contract.outside_subject_trees(Path(output_path)):
        raise ValueError(f"{output_path} is inside a subject tree; evidence about a projection is not written into it")
    contract.write_json(Path(output_path), record)


def load_evidence(path: Path) -> dict:
    """Read one evidence record, or raise: unparseable, schema-invalid, or an id that is not the digest of its content."""
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise contract.ContractViolation("evidence", [f"{path}: {exc}"]) from exc
    contract.require_valid("evidence", record)
    if record["evidence_id"] != evidence_id(record):
        raise contract.ContractViolation("evidence", [f"{path}: evidence_id is not the digest of the record's content (edited after it was written)"])
    return record


def load_policy(policy_path: Path) -> dict:
    """Read an assurance policy and check it against the policy schema."""
    policy = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    return contract.require_valid("policy", policy)
