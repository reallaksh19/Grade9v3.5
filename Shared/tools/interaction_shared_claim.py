#!/usr/bin/env python3
"""Assess whether observed interaction lineage proves a subject-neutral SHARED claim.

This module validates the strength of a maturity claim only. A false or unproven SHARED claim
never blocks research, a governed LOCAL build, or REUSED learner delivery. Promotion remains
optional and evidence-driven.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "Shared/library/interaction-shared-claim.schema.json"
AUTHORITY = "DERIVED_INTERACTION_SHARED_CLAIM_ONLY"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import load
from Shared.tools import interaction_discovery, interaction_reuse


class InteractionSharedClaimError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractionSharedClaimError(f"{code}: {detail}" if detail else code)


def _schema_errors(record: dict, repo: Path = REPO) -> list[str]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / SCHEMA.relative_to(REPO))
    return [
        f"{'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in jsonschema.Draft202012Validator(schema).iter_errors(record)
    ]


def assess_analysis(analysis: dict, *, repo: Path = REPO) -> dict[str, Any]:
    """Turn lineage analysis into a falsifiable SHARED-claim assessment."""
    implementation_ref = analysis.get("implementation_ref")
    _require(bool(implementation_ref), "INTERACTION_SHARED_CLAIM_IMPLEMENTATION_REF_REQUIRED")

    creators = sorted(set(analysis.get("creator_interaction_refs") or []))
    consumers = sorted(set(analysis.get("consumer_interaction_refs") or []))
    consumer_subjects = sorted(set(analysis.get("consumer_subject_refs") or []))
    owners = sorted(set(analysis.get("shared_owner_refs") or []))
    observed = analysis.get("maturity")

    missing: list[str] = []
    if not creators:
        missing.append("CONCRETE_CREATOR_EVIDENCE")
    if len(consumers) < 2:
        missing.append("MULTIPLE_REAL_CONSUMER_EVIDENCE")
    if len(consumer_subjects) < 2:
        missing.append("CROSS_SUBJECT_CONSUMER_EVIDENCE")
    if not owners:
        missing.append("JUSTIFIED_SHARED_OWNER")
    elif len(owners) != 1:
        missing.append("UNAMBIGUOUS_SHARED_OWNER")

    shared_claim_proven = (
        observed == "SHARED"
        and not missing
        and bool(analysis.get("subject_neutral_shared_claim_proven"))
    )

    if shared_claim_proven:
        decision = "SHARED_CLAIM_PROVEN"
    elif observed == "REUSED":
        decision = "KEEP_REUSED"
    elif observed == "LOCAL":
        decision = "KEEP_LOCAL"
    elif observed == "SHARED":
        decision = "SHARED_CLAIM_UNPROVEN"
    else:
        decision = "UNOBSERVED"

    result = {
        "schema_version": "1.0.0",
        "authority": AUTHORITY,
        "implementation_ref": implementation_ref,
        "observed_maturity": observed,
        "decision": decision,
        "shared_claim_proven": shared_claim_proven,
        "evidence_summary": {
            "creator_interaction_refs": creators,
            "consumer_interaction_refs": consumers,
            "consumer_subject_refs": consumer_subjects,
            "shared_owner_refs": owners,
        },
        "missing_claim_evidence": sorted(set(missing)),
        "execution_policy": {
            "advisory_only": True,
            "research_may_continue": True,
            "local_or_reused_delivery_not_blocked": True,
            "promotion_required": False,
        },
        "claim_note": (
            "SHARED is a claim about observed subject-neutral reuse, not a promotion target. "
            "It requires concrete creator lineage, multiple real consumers across multiple "
            "subjects, and one unambiguous shared owner. Missing evidence falsifies only the "
            "SHARED claim; it does not block research, governed LOCAL builds, or REUSED delivery."
        ),
    }
    errors = _schema_errors(result, repo)
    _require(not errors, "INTERACTION_SHARED_CLAIM_SCHEMA_INVALID", "; ".join(errors[:8]))
    return result


def assess_records(
    records: list[dict],
    implementation_ref: str,
    *,
    repo: Path = REPO,
) -> dict[str, Any]:
    analysis = interaction_reuse.analyse_implementation(
        records, implementation_ref, repo=repo,
    )
    return assess_analysis(analysis, repo=repo)


def assess_repository(
    implementation_ref: str,
    *,
    repo: Path = REPO,
) -> dict[str, Any]:
    """Assess one implementation from the reconstructable repository discovery projection."""
    index = interaction_discovery.build(repo=repo)
    rows = interaction_discovery.search(
        index, implementation_ref=implementation_ref,
    )
    _require(
        len(rows) == 1,
        "INTERACTION_SHARED_CLAIM_IMPLEMENTATION_UNRESOLVED",
        implementation_ref,
    )
    row = rows[0]
    analysis = {
        "implementation_ref": implementation_ref,
        "maturity": row.get("maturity"),
        "creator_interaction_refs": row.get("creator_interaction_refs") or [],
        "consumer_interaction_refs": row.get("consumer_interaction_refs") or [],
        "consumer_subject_refs": row.get("consumer_subject_refs") or [],
        "shared_owner_refs": row.get("shared_owner_refs") or [],
        "subject_neutral_shared_claim_proven": row.get(
            "subject_neutral_shared_claim_proven", False
        ),
    }
    return assess_analysis(analysis, repo=repo)


def assert_shared(assessment: dict) -> None:
    """Fail only an explicit SHARED assertion when the evidence does not prove that claim."""
    _require(
        assessment.get("shared_claim_proven") is True,
        "INTERACTION_SHARED_CLAIM_UNPROVEN",
        ",".join(assessment.get("missing_claim_evidence") or []) or str(
            assessment.get("decision") or ""
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--implementation-ref", required=True)
    parser.add_argument("--assert-shared", action="store_true")
    args = parser.parse_args()
    result = assess_repository(args.implementation_ref)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.assert_shared:
        assert_shared(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
