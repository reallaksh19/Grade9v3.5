#!/usr/bin/env python3
"""Derive an advisory interaction discovery index from real implementation/reuse evidence.

The index is a reconstructable projection for cold-agent discovery. It never grants permission,
never blocks research/building when no row exists, and never turns similarity into reuse evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "Shared/library/interaction-discovery-index.schema.json"
AUTHORITY = "DERIVED_INTERACTION_DISCOVERY_ONLY"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import canonical, load
from Shared.tools import (
    interaction_local_runtime,
    interaction_reuse,
    interaction_reuse_binding,
)


class InteractionDiscoveryError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractionDiscoveryError(f"{code}: {detail}" if detail else code)


def _subject_roots(repo: Path) -> list[Path]:
    return sorted(path.parent.parent for path in repo.glob("*/adapter/CoreContracts.json"))


def _relative(path: Path, repo: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path)


def _local_source_paths(repo: Path) -> list[Path]:
    return [
        path
        for root in _subject_roots(repo)
        for path in sorted((root / "interactions").glob("*.local.json"))
    ]


def _explicit_evidence_paths(repo: Path) -> list[Path]:
    return [
        path
        for root in _subject_roots(repo)
        for path in sorted((root / "interactions").glob("*.reuse.json"))
    ]


def _reuse_consumer_source_paths(repo: Path) -> list[Path]:
    return [
        path
        for root in _subject_roots(repo)
        for path in sorted((root / "interactions").glob("*.reuse-consumer.json"))
    ]


def _schema_errors(index: dict, repo: Path = REPO) -> list[str]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / SCHEMA.relative_to(REPO))
    return [
        f"{'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in jsonschema.Draft202012Validator(schema).iter_errors(index)
    ]


def _dedupe_evidence(records: list[dict], *, repo: Path) -> list[dict]:
    by_id: dict[str, dict] = {}
    for record in records:
        interaction_reuse.validate(record, repo=repo)
        evidence_id = record["evidence_id"]
        previous = by_id.get(evidence_id)
        if previous is not None:
            _require(
                canonical(previous) == canonical(record),
                "INTERACTION_DISCOVERY_EVIDENCE_ID_CONFLICT",
                evidence_id,
            )
        by_id[evidence_id] = record
    return [by_id[key] for key in sorted(by_id)]


def _implementation_refs(evidence_records: list[dict]) -> list[str]:
    return sorted({
        decision["implementation_ref"]
        for record in evidence_records
        for decision in record.get("decisions") or []
    })


def build_from_records(
    local_runtime_records: list[dict],
    evidence_records: list[dict],
    *,
    local_source_paths: list[str] | None = None,
    explicit_evidence_paths: list[str] | None = None,
    reuse_consumer_source_paths: list[str] | None = None,
    repo: Path = REPO,
) -> dict[str, Any]:
    """Build the projection from supplied concrete runtime/evidence records."""
    local_by_impl = {
        row["runtime"]["activity_ref"]: row
        for row in local_runtime_records
    }
    combined = list(evidence_records)
    combined.extend(
        row["reuse_evidence"] for row in local_runtime_records
        if isinstance(row.get("reuse_evidence"), dict)
    )
    evidence = _dedupe_evidence(combined, repo=repo)

    implementations = []
    for implementation_ref in _implementation_refs(evidence):
        matching = [
            record for record in evidence
            if any(
                decision.get("implementation_ref") == implementation_ref
                for decision in record.get("decisions") or []
            )
        ]
        analysis = interaction_reuse.analyse_implementation(
            evidence, implementation_ref, repo=repo,
        )
        local = local_by_impl.get(implementation_ref)
        implementations.append({
            "implementation_ref": implementation_ref,
            "maturity": analysis["maturity"],
            "maturity_status": analysis["maturity_status"],
            "subject_refs": sorted({row["subject_ref"] for row in matching}),
            "interaction_refs": sorted({row["interaction_ref"] for row in matching}),
            "mechanic_refs": sorted(set(analysis["mechanic_refs"])),
            "runtime_binding_refs": sorted({row["runtime_binding_ref"] for row in matching}),
            "package_refs": (
                [local["runtime"]["package_ref"]] if local else []
            ),
            "example_artifact_refs": sorted({
                decision["evidence_ref"]
                for row in matching
                for decision in row.get("decisions") or []
                if isinstance(decision.get("evidence_ref"), str) and decision["evidence_ref"]
            }),
            "source_paths": [local["source_path"]] if local else [],
            "creator_interaction_refs": list(analysis["creator_interaction_refs"]),
            "consumer_interaction_refs": list(analysis["consumer_interaction_refs"]),
            "consumer_subject_refs": list(analysis["consumer_subject_refs"]),
            "shared_owner_refs": list(analysis["shared_owner_refs"]),
            "subject_neutral_shared_claim_proven": analysis["subject_neutral_shared_claim_proven"],
            "reconstruction_debt": list(analysis["reconstruction_debt"]),
            "lineage_edges": list(analysis["lineage_edges"]),
        })

    body = {
        "schema_version": "1.0.0",
        "authority": AUTHORITY,
        "execution_policy": {
            "advisory_only": True,
            "research_may_continue": True,
            "unindexed_build_allowed": True,
            "promotion_not_required": True,
            "similarity_is_not_reuse_evidence": True,
        },
        "implementations": implementations,
        "duplication_opportunities": interaction_reuse.duplication_opportunities(
            evidence, repo=repo,
        ),
        "source_inventory": {
            "local_source_paths": sorted(set(local_source_paths or [])),
            "explicit_reuse_evidence_paths": sorted(set(explicit_evidence_paths or [])),
            "reuse_consumer_source_paths": sorted(set(reuse_consumer_source_paths or [])),
        },
    }
    index = {
        **body,
        "index_digest": "sha256:" + hashlib.sha256(canonical(body)).hexdigest(),
    }
    errors = _schema_errors(index, repo)
    _require(not errors, "INTERACTION_DISCOVERY_SCHEMA_INVALID", "; ".join(errors[:8]))
    return index


def build(*, repo: Path = REPO) -> dict[str, Any]:
    """Scan production memory under each subject and derive the current index."""
    local_paths = _local_source_paths(repo)
    explicit_paths = _explicit_evidence_paths(repo)
    consumer_paths = _reuse_consumer_source_paths(repo)
    local_records = [
        interaction_local_runtime.compile_source(path, repo=repo)
        for path in local_paths
    ]
    explicit_records = [load(path) for path in explicit_paths]
    consumer_records = [
        interaction_reuse_binding.compile_source(path, repo=repo)
        for path in consumer_paths
    ]
    evidence_records = list(explicit_records)
    evidence_records.extend(row["reuse_evidence"] for row in consumer_records)
    return build_from_records(
        local_records,
        evidence_records,
        local_source_paths=[_relative(path, repo) for path in local_paths],
        explicit_evidence_paths=[_relative(path, repo) for path in explicit_paths],
        reuse_consumer_source_paths=[_relative(path, repo) for path in consumer_paths],
        repo=repo,
    )


def search(
    index: dict,
    *,
    mechanic_refs: list[str] | None = None,
    subject_ref: str | None = None,
    maturity: str | None = None,
    implementation_ref: str | None = None,
) -> list[dict]:
    """Exact advisory discovery; absence is never an execution refusal."""
    wanted_mechanics = set(mechanic_refs or [])
    rows = []
    for row in index.get("implementations") or []:
        if implementation_ref and row.get("implementation_ref") != implementation_ref:
            continue
        if subject_ref and subject_ref not in (row.get("subject_refs") or []):
            continue
        if maturity and row.get("maturity") != maturity:
            continue
        if wanted_mechanics and not wanted_mechanics.issubset(set(row.get("mechanic_refs") or [])):
            continue
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mechanic-ref", action="append")
    parser.add_argument("--subject-ref")
    parser.add_argument("--maturity", choices=["LOCAL", "REUSED", "SHARED"])
    parser.add_argument("--implementation-ref")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    index = build()
    filters_used = any([
        args.mechanic_ref, args.subject_ref, args.maturity, args.implementation_ref,
    ])
    result: Any = search(
        index,
        mechanic_refs=args.mechanic_ref,
        subject_ref=args.subject_ref,
        maturity=args.maturity,
        implementation_ref=args.implementation_ref,
    ) if filters_used else index
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
