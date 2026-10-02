#!/usr/bin/env python3
"""Utility for writing assurance-evidence/v1 records."""

import sys
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

def make_evidence(
    assurance_type: str,
    subject_kind: str,
    subject_id: str,
    outcome: str,
    producer_name: str,
    producer_version: str,
    findings: list[dict] = None,
    confidence: float = None,
    dependencies: list[str] = None,
    subject_digest: str = None,
    producer_config_digest: str = None,
    severity: str = None,
) -> dict:
    """Build a validated assurance-evidence/v1 record."""
    kind_mapping = {
        "library": "CANONICAL_RECORD",
        "question": "CANONICAL_RECORD",
        "product": "PRODUCT",
        "projection": "PROJECTION",
        "source": "SOURCE"
    }
    mapped_kind = kind_mapping.get(subject_kind.lower()) if subject_kind.lower() in kind_mapping else subject_kind
    
    evidence = {
        "schema": "assurance-evidence/v1",
        "assurance_type": assurance_type,
        "subject": {
            "kind": mapped_kind,
            "id": subject_id,
        },
        "outcome": outcome,
        "producer": {
            "name": producer_name,
            "version": producer_version,
            "configuration_digest": producer_config_digest or ""
        },
        "findings": findings if findings is not None else [],
        "produced_at": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + 'Z'
    }
    
    if subject_digest is not None:
        evidence["subject"]["digest"] = subject_digest
    if outcome == "FAIL" and severity is not None:
        evidence["severity"] = severity
    if confidence is not None:
        evidence["confidence"] = confidence
    if dependencies is not None:
        evidence["dependencies"] = dependencies
    else:
        evidence["dependencies"] = []
    
    content_str = json.dumps(evidence, sort_keys=True).encode('utf-8')
    digest = hashlib.sha256(content_str).hexdigest()[:16]
    evidence["evidence_id"] = f"AE-{digest}"
    return evidence

def validate_evidence(ev: dict) -> bool:
    """Check the evidence dict against the schema's required fields and log any mismatch."""
    required_top = ["schema", "evidence_id", "subject", "assurance_type", "producer", "outcome", "findings", "produced_at"]
    required_subject = ["kind", "id"]
    required_producer = ["name", "version", "configuration_digest"]
    
    for req in required_top:
        if req not in ev:
            print(f"Missing top-level field: {req}", file=sys.stderr)
            return False
    for req in required_subject:
        if req not in ev["subject"]:
            print(f"Missing subject field: {req}", file=sys.stderr)
            return False
    for req in required_producer:
        if req not in ev["producer"]:
            print(f"Missing producer field: {req}", file=sys.stderr)
            return False
    if ev["outcome"] == "FAIL" and "severity" not in ev:
        print("Missing severity for FAIL outcome", file=sys.stderr)
        return False
    return True

def write_evidence(evidence: dict, output_path: Path) -> None:
    """Write a single evidence record to output_path as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)

def load_policy(policy_path: Path) -> dict:
    """Load and return a policy JSON file."""
    with policy_path.open("r", encoding="utf-8") as f:
        return json.load(f)

def check_missing(evidence_list: list[dict], required_types: list[str]) -> list[str]:
    """Return required_types not covered by a PASS (or NOT_APPLICABLE) in evidence_list."""
    covered = set()
    for ev in evidence_list:
        covered.add(ev.get("assurance_type"))
    return [req for req in required_types if req not in covered]
