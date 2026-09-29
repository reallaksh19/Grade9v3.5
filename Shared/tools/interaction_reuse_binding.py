#!/usr/bin/env python3
"""Bind a real canonical consumer to an existing governed interaction implementation.

A consumer binding proves literal reuse by pointing a second canonical learner target at the
same runtime/package identity. It does not copy the scene, promote the implementation into
Shared architecture, or turn reuse metadata into execution permission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SOURCE_SCHEMA = REPO / "Shared/library/interaction-reuse-consumer-source.schema.json"
SOURCE_AUTHORITY = "INTERACTION_REUSE_CONSUMER_SOURCE"
AUTHORITY = "DERIVED_INTERACTION_REUSE_BINDING_ONLY"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import canonical, load
from Shared.library.resolve import build_index, load_packages
from Shared.tools import interaction_brief, interaction_local_runtime, interaction_reuse


class InteractionReuseBindingError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractionReuseBindingError(f"{code}: {detail}" if detail else code)


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def _resolve(path: Path, repo: Path) -> Path:
    return path if path.is_absolute() else repo / path


def _display(path: Path, repo: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path)


def _schema_errors(source: dict, repo: Path = REPO) -> list[str]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / SOURCE_SCHEMA.relative_to(REPO))
    return [
        f"{'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in jsonschema.Draft202012Validator(schema).iter_errors(source)
    ]


def _subject_records(subject: str, repo: Path) -> dict[str, dict]:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths)) if paths else {}


def compile_source(source_path: Path, *, repo: Path = REPO) -> dict[str, Any]:
    """Compile one real consumer into concrete reuse evidence."""
    path = _resolve(source_path, repo)
    source = load(path)
    errors = _schema_errors(source, repo)
    _require(not errors, "INTERACTION_REUSE_CONSUMER_SOURCE_SCHEMA_INVALID", "; ".join(errors[:8]))
    _require(source.get("authority") == SOURCE_AUTHORITY, "INTERACTION_REUSE_CONSUMER_SOURCE_AUTHORITY_INVALID")

    implementation_source_path = _resolve(Path(source["implementation_source_ref"]), repo)
    local = interaction_local_runtime.compile_source(implementation_source_path, repo=repo)
    _require(local.get("subject") == source["subject"], "INTERACTION_REUSE_CONSUMER_SUBJECT_MISMATCH")

    records = _subject_records(source["subject"], repo)
    consumer_ref = source["consumer_ref"]
    consumer = records.get(consumer_ref)
    _require(
        isinstance(consumer, dict) and consumer.get("_collection") == "questions",
        "INTERACTION_REUSE_CONSUMER_QUESTION_UNRESOLVED",
        consumer_ref,
    )

    target_ref = local["interaction_brief"]["target_ref"]
    brief = interaction_brief.build_from_microtopic(source["subject"], target_ref, repo=repo)
    capability_refs = set(brief["academic_target"]["capability_refs"])
    primary_capability_ref = consumer.get("primary_capability_ref")
    _require(
        primary_capability_ref in capability_refs,
        "INTERACTION_REUSE_CONSUMER_CAPABILITY_MISMATCH",
        str(primary_capability_ref or ""),
    )

    microtopic = records.get(target_ref)
    _require(
        isinstance(microtopic, dict) and microtopic.get("_collection") == "microtopics",
        "INTERACTION_REUSE_CONSUMER_MICROTOPIC_UNRESOLVED",
        target_ref,
    )
    family_refs = set(microtopic.get("question_family_refs") or [])
    consumer_family_ref = consumer.get("family_ref")
    if family_refs:
        _require(
            consumer_family_ref in family_refs,
            "INTERACTION_REUSE_CONSUMER_FAMILY_MISMATCH",
            str(consumer_family_ref or ""),
        )

    representation_refs = set(brief["academic_target"]["representation_refs"])
    representation_roles = consumer.get("representation_roles") or {}
    declared_representation_refs = {
        value for value in (
            representation_roles.get("initial_ref"),
            representation_roles.get("safe_ref"),
            representation_roles.get("bound_ref"),
        )
        if isinstance(value, str) and value
    }
    if declared_representation_refs:
        _require(
            bool(declared_representation_refs & representation_refs),
            "INTERACTION_REUSE_CONSUMER_REPRESENTATION_MISMATCH",
            ",".join(sorted(declared_representation_refs)),
        )

    evidence = interaction_reuse.build_evidence(
        interaction_ref=consumer_ref,
        subject_ref=source["subject"],
        runtime_binding_ref=local["runtime"]["binding_ref"],
        mechanic_refs=list(local["reuse_evidence"]["mechanic_refs"]),
        decisions=[{
            "slice_ref": source["slice_ref"],
            "mode": source["mode"],
            "relation": source["relation"],
            "implementation_ref": local["runtime"]["activity_ref"],
            "evidence_ref": local["runtime"]["package_ref"],
        }],
        repo=repo,
    )
    analysis = interaction_reuse.analyse_implementation(
        [local["reuse_evidence"], evidence],
        local["runtime"]["activity_ref"],
        repo=repo,
    )
    _require(
        analysis.get("maturity") == "REUSED",
        "INTERACTION_REUSE_CONSUMER_MATURITY_NOT_REUSED",
        str(analysis.get("maturity")),
    )
    _require(
        not analysis.get("subject_neutral_shared_claim_proven"),
        "INTERACTION_REUSE_CONSUMER_UNEXPECTED_SHARED_CLAIM",
    )

    consumer_digest = _digest({consumer_ref: consumer})
    body = {
        "source": source,
        "local_binding_digest": local["binding_digest"],
        "consumer_digest": consumer_digest,
        "reuse_evidence": evidence,
    }
    binding_digest = _digest(body)
    return {
        "schema_version": "1.0.0",
        "authority": AUTHORITY,
        "status": "CURRENT",
        "source_path": _display(path, repo),
        "subject": source["subject"],
        "implementation_source_ref": _display(implementation_source_path, repo),
        "consumer_ref": consumer_ref,
        "consumer_primary_capability_ref": primary_capability_ref,
        "consumer_family_ref": consumer_family_ref,
        "consumer_canonical_digest": consumer_digest,
        "runtime": local["runtime"],
        "reuse_evidence": evidence,
        "reuse_analysis": analysis,
        "binding_digest": binding_digest,
        "claim_note": (
            "The consumer points to the existing activity/package/binding unchanged. "
            "REUSED therefore comes from literal implementation lineage, not similarity. "
            "This remains same-subject reuse and does not prove a SHARED subject-neutral capability."
        ),
    }


def freshness(record: dict, source_path: Path, *, repo: Path = REPO) -> dict[str, Any]:
    try:
        current = compile_source(source_path, repo=repo)
    except Exception as exc:
        return {
            "status": "INVALID",
            "expected_binding_digest": record.get("binding_digest"),
            "current_binding_digest": None,
            "detail": str(exc),
        }
    expected = record.get("binding_digest")
    observed = current.get("binding_digest")
    return {
        "status": "CURRENT" if expected == observed else "STALE",
        "expected_binding_digest": expected,
        "current_binding_digest": observed,
        "consumer_ref": current["consumer_ref"],
        "runtime": current["runtime"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--evidence-out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    if args.check:
        result = freshness(load(args.check), args.source)
    else:
        result = compile_source(args.source)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.evidence_out and not args.check:
        args.evidence_out.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_out.write_text(
            json.dumps(result["reuse_evidence"], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 1 if args.enforce and result.get("status") != "CURRENT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
