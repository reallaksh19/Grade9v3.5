#!/usr/bin/env python3
"""Build and analyse compositional interaction-reuse lineage evidence.

This is derived production memory only. It helps later agents discover what was actually
consumed, composed, extended or created. It never grants permission to research/build and it
does not turn superficial similarity into reuse maturity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "Shared/library/interaction-reuse-evidence.schema.json"
AUTHORITY = "DERIVED_INTERACTION_REUSE_EVIDENCE_ONLY"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import canonical, load


class InteractionReuseError(ValueError):
    pass


MODE_RELATIONS = {
    "R1": {"CONSUMES", "EXAMPLE_OF"},
    "R2": {"COMPOSES", "CONSUMES"},
    "R3": {"EXTENDS", "DERIVED_FROM"},
    "R4": {"CREATES"},
}
CONSUMER_RELATIONS = {"CONSUMES", "COMPOSES", "EXTENDS", "DERIVED_FROM"}


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractionReuseError(f"{code}: {detail}" if detail else code)


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


def validate(record: dict, *, repo: Path = REPO) -> None:
    errors = _schema_errors(record, repo)
    _require(not errors, "INTERACTION_REUSE_SCHEMA_INVALID", "; ".join(errors[:8]))
    _require(
        record.get("authority") == AUTHORITY,
        "INTERACTION_REUSE_AUTHORITY_INVALID",
    )
    for decision in record.get("decisions") or []:
        mode = decision.get("mode")
        relation = decision.get("relation")
        _require(
            relation in MODE_RELATIONS.get(mode, set()),
            "INTERACTION_REUSE_MODE_RELATION_INVALID",
            f"{mode}:{relation}",
        )
    shared = record.get("shared_binding")
    if isinstance(shared, dict):
        implementation_ref = shared.get("implementation_ref")
        _require(
            any(
                decision.get("implementation_ref") == implementation_ref
                for decision in record.get("decisions") or []
            ),
            "INTERACTION_REUSE_SHARED_BINDING_UNREFERENCED",
            str(implementation_ref or ""),
        )


def _evidence_id(payload: dict) -> str:
    token = hashlib.sha256(canonical(payload)).hexdigest()[:20].upper()
    return f"IRE-{token}"


def build_evidence(
    *,
    interaction_ref: str,
    subject_ref: str,
    runtime_binding_ref: str,
    mechanic_refs: list[str],
    decisions: list[dict],
    shared_binding: dict | None = None,
    repo: Path = REPO,
) -> dict[str, Any]:
    """Create one deterministic evidence record for a concrete interaction implementation."""
    body = {
        "schema_version": "1.0.0",
        "authority": AUTHORITY,
        "interaction_ref": interaction_ref,
        "subject_ref": subject_ref,
        "runtime_binding_ref": runtime_binding_ref,
        "mechanic_refs": sorted(set(mechanic_refs)),
        "decisions": decisions,
        "shared_binding": shared_binding,
    }
    record = {"evidence_id": _evidence_id(body), **body}
    validate(record, repo=repo)
    return record


def interaction_summary(record: dict, *, repo: Path = REPO) -> dict[str, Any]:
    """Expose all R1-R4 modes present; never flatten a mixed interaction to one required label."""
    validate(record, repo=repo)
    modes = sorted({row["mode"] for row in record["decisions"]})
    return {
        "interaction_ref": record["interaction_ref"],
        "runtime_binding_ref": record["runtime_binding_ref"],
        "modes_present": modes,
        "mixed_path": len(modes) > 1,
        "decisions": list(record["decisions"]),
    }


def analyse_implementation(
    records: list[dict],
    implementation_ref: str,
    *,
    repo: Path = REPO,
) -> dict[str, Any]:
    """Derive maturity from concrete lineage, never from similarity or absent evidence."""
    for record in records:
        validate(record, repo=repo)

    creators: set[str] = set()
    consumers: dict[str, dict[str, Any]] = {}
    shared_owner_refs: set[str] = set()
    mechanic_refs: set[str] = set()
    matching_edges: list[dict[str, Any]] = []

    for record in records:
        decisions = [
            row for row in record["decisions"]
            if row.get("implementation_ref") == implementation_ref
        ]
        if not decisions:
            continue
        mechanic_refs.update(record.get("mechanic_refs") or [])
        for decision in decisions:
            edge = {
                "interaction_ref": record["interaction_ref"],
                "subject_ref": record["subject_ref"],
                "runtime_binding_ref": record["runtime_binding_ref"],
                **decision,
            }
            matching_edges.append(edge)
            if decision["relation"] == "CREATES":
                creators.add(record["interaction_ref"])
            elif decision["relation"] in CONSUMER_RELATIONS:
                consumers[record["interaction_ref"]] = edge
        shared = record.get("shared_binding")
        if isinstance(shared, dict) and shared.get("implementation_ref") == implementation_ref:
            shared_owner_refs.add(shared["owner_ref"])

    consumer_subjects = {row["subject_ref"] for row in consumers.values()}
    if shared_owner_refs and len(consumers) >= 2 and len(consumer_subjects) >= 2:
        maturity: str | None = "SHARED"
    elif consumers:
        maturity = "REUSED"
    elif creators:
        maturity = "LOCAL"
    else:
        maturity = None

    return {
        "implementation_ref": implementation_ref,
        "maturity": maturity,
        "maturity_status": "OBSERVED" if maturity is not None else "UNOBSERVED",
        "creator_interaction_refs": sorted(creators),
        "consumer_interaction_refs": sorted(consumers),
        "consumer_subject_refs": sorted(consumer_subjects),
        "shared_owner_refs": sorted(shared_owner_refs),
        "subject_neutral_shared_claim_proven": maturity == "SHARED",
        "lineage_edges": matching_edges,
        "mechanic_refs": sorted(mechanic_refs),
        "reconstruction_debt": (
            [] if matching_edges else ["NO_IMPLEMENTATION_LINEAGE_EVIDENCE"]
        ),
        "claim_note": (
            "LOCAL itself requires evidence that one concrete implementation exists. "
            "REUSED is derived from concrete consume/compose/extend/derive lineage. "
            "A shared owner plus at least two concrete consumers across at least two subject refs "
            "is required for a subject-neutral SHARED claim."
        ),
    }


def duplication_opportunities(
    records: list[dict],
    *,
    repo: Path = REPO,
) -> list[dict[str, Any]]:
    """Find independently created lookalikes without mislabelling them as REUSED."""
    for record in records:
        validate(record, repo=repo)
    by_mechanic: dict[str, list[dict]] = {}
    for record in records:
        created = any(row.get("relation") == "CREATES" for row in record["decisions"])
        if not created:
            continue
        for mechanic_ref in record.get("mechanic_refs") or []:
            by_mechanic.setdefault(mechanic_ref, []).append(record)

    opportunities = []
    for mechanic_ref, rows in sorted(by_mechanic.items()):
        implementation_refs = {
            decision["implementation_ref"]
            for record in rows
            for decision in record["decisions"]
            if decision.get("relation") == "CREATES"
        }
        if len(implementation_refs) < 2:
            continue
        opportunities.append({
            "mechanic_ref": mechanic_ref,
            "interaction_refs": sorted({row["interaction_ref"] for row in rows}),
            "implementation_refs": sorted(implementation_refs),
            "disposition": "DUPLICATION_OPPORTUNITY_ONLY",
            "maturity_effect": "NONE_WITHOUT_LINEAGE",
        })
    return opportunities


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument("--implementation-ref")
    parser.add_argument("--duplication-opportunities", action="store_true")
    args = parser.parse_args()
    records = [load(path) for path in args.evidence]
    if args.duplication_opportunities:
        result: Any = duplication_opportunities(records)
    else:
        _require(bool(args.implementation_ref), "INTERACTION_REUSE_IMPLEMENTATION_REF_REQUIRED")
        result = analyse_implementation(records, args.implementation_ref)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
