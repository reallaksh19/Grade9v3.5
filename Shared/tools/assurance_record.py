#!/usr/bin/env python3
"""Utility for writing assurance-evidence/v1 records."""

import sys
import json
import hashlib
from datetime import datetime
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
) -> dict:
    """Build a validated assurance-evidence/v1 record."""
    evidence = {
        "schema_version": "assurance-evidence/v1",
        "assurance_type": assurance_type,
        "subject": {
            "kind": subject_kind,
            "id": subject_id,
        },
        "outcome": outcome,
        "producer": {
            "name": producer_name,
            "version": producer_version,
        },
        "produced_at": datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat() + 'Z'
    }
    if findings is not None:
        evidence["findings"] = findings
    if confidence is not None:
        evidence["confidence"] = confidence
    if dependencies is not None:
        evidence["dependencies"] = dependencies
    if subject_digest is not None:
        evidence["subject"]["digest"] = subject_digest
    if producer_config_digest is not None:
        evidence["producer"]["config_digest"] = producer_config_digest
    
    content_str = json.dumps(evidence, sort_keys=True).encode('utf-8')
    digest = hashlib.sha256(content_str).hexdigest()[:16]
    evidence["evidence_id"] = f"AE-{digest}"
    return evidence

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
