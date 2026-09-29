#!/usr/bin/env python3
"""Compile one governed LOCAL interaction source onto the existing portable workbench runtime.

The compiler binds lesson-local engineering data to a CURRENT Interaction Brief, derives stable
activity identity plus content-addressed scene/adapter/package/binding identities, validates the
existing data-only portable package contract, and emits R4 production-memory evidence. LOCAL is
a delivery/maturity fact, not permission to research or a claim of shared architecture.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SOURCE_SCHEMA = REPO / "Shared/library/interaction-local-runtime-source.schema.json"
AUTHORITY = "DERIVED_LOCAL_INTERACTION_RUNTIME_ONLY"
SOURCE_AUTHORITY = "LOCAL_INTERACTION_IMPLEMENTATION_SOURCE"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import canonical, load
from Shared.portable.package import COMPONENT_API_VERSION, build_package, validate_package
from Shared.tools import interaction_brief, interaction_reuse


class InteractionLocalRuntimeError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractionLocalRuntimeError(f"{code}: {detail}" if detail else code)


def _digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def _token(value: object, length: int = 16) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()[:length]


def _source_schema_errors(source: dict, repo: Path = REPO) -> list[str]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / SOURCE_SCHEMA.relative_to(REPO))
    return [
        f"{'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in jsonschema.Draft202012Validator(schema).iter_errors(source)
    ]


def _resolve_source_path(source_path: Path, repo: Path) -> Path:
    return source_path if source_path.is_absolute() else repo / source_path


def _display_path(path: Path, repo: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path)


def compile_source(source_path: Path, *, repo: Path = REPO) -> dict[str, Any]:
    """Compile a lesson-local source into one deterministic governed runtime binding."""
    path = _resolve_source_path(source_path, repo)
    source = load(path)
    errors = _source_schema_errors(source, repo)
    _require(not errors, "LOCAL_RUNTIME_SOURCE_SCHEMA_INVALID", "; ".join(errors[:8]))
    _require(source.get("authority") == SOURCE_AUTHORITY, "LOCAL_RUNTIME_SOURCE_AUTHORITY_INVALID")
    scene_source = source.get("scene") or {}
    _require("id" not in scene_source, "LOCAL_RUNTIME_SCENE_ID_OVERRIDE_FORBIDDEN")
    _require("apiVersion" not in scene_source, "LOCAL_RUNTIME_SCENE_API_OVERRIDE_FORBIDDEN")

    brief = interaction_brief.build_from_microtopic(
        source["subject"], source["microtopic_ref"], repo=repo,
    )
    brief_freshness = interaction_brief.freshness(brief, repo=repo)
    _require(
        brief_freshness.get("status") == "CURRENT",
        "LOCAL_RUNTIME_INTERACTION_BRIEF_NOT_CURRENT",
        str(brief_freshness.get("status")),
    )

    source_digest = _digest(source)
    brief_digest = brief["provenance"]["canonical_input_digest"]
    stable_token = _token([brief["brief_id"], source["implementation_key"]])
    revision_token = _token([brief_digest, source_digest])

    activity_ref = f"local-activity-{stable_token}"
    scene_ref = f"local-scene-{stable_token}-{revision_token}"
    adapter_ref = f"local-adapter-{stable_token}-{revision_token}"
    package_ref = f"local-package-{stable_token}-{revision_token}"
    binding_ref = f"local-binding-{stable_token}-{revision_token}"

    scene = copy.deepcopy(scene_source)
    scene["apiVersion"] = COMPONENT_API_VERSION
    scene["id"] = scene_ref

    package = build_package({
        "id": package_ref,
        "title": source["title"],
        "sourceKind": "LOCAL_INTERACTION_IMPLEMENTATION",
        "sourceRefs": list(brief["provenance"]["canonical_record_refs"]),
        "representationRefs": list(brief["academic_target"]["representation_refs"]),
        "assetRefs": [],
        "accessibilityRefs": list(source["accessibility_refs"]),
        "questionBindings": [],
        "injections": [],
        "adapterRules": copy.deepcopy(source["adapter_rules"]),
    }, scene)

    reuse_evidence = interaction_reuse.build_evidence(
        interaction_ref=brief["brief_id"],
        subject_ref=source["subject"],
        runtime_binding_ref=binding_ref,
        mechanic_refs=list(source["mechanic_refs"]),
        decisions=[{
            "slice_ref": "whole-interaction",
            "mode": "R4",
            "relation": "CREATES",
            "implementation_ref": activity_ref,
            "evidence_ref": package_ref,
        }],
        repo=repo,
    )
    reuse_analysis = interaction_reuse.analyse_implementation(
        [reuse_evidence], activity_ref, repo=repo,
    )
    _require(
        reuse_analysis.get("maturity") == "LOCAL",
        "LOCAL_RUNTIME_MATURITY_NOT_LOCAL",
        str(reuse_analysis.get("maturity")),
    )

    runtime_binding = {
        "binding_ref": binding_ref,
        "activity_ref": activity_ref,
        "scene_ref": scene_ref,
        "adapter_ref": adapter_ref,
        "adapter_implementation_ref": package["adapter"]["id"],
        "package_ref": package_ref,
        "maturity": reuse_analysis["maturity"],
    }
    package["runtimeBinding"] = copy.deepcopy(runtime_binding)
    package["provenance"]["localInteraction"] = {
        "authority": AUTHORITY,
        "briefRef": brief["brief_id"],
        "canonicalInputDigest": brief_digest,
        "sourceDigest": source_digest,
    }
    package = validate_package(package)

    identity_body = {
        "brief_ref": brief["brief_id"],
        "canonical_input_digest": brief_digest,
        "source_digest": source_digest,
        "runtime": runtime_binding,
        "package": package,
        "reuse_evidence": reuse_evidence,
    }
    binding_digest = _digest(identity_body)
    return {
        "schema_version": "1.0.0",
        "authority": AUTHORITY,
        "status": "CURRENT",
        "subject": source["subject"],
        "source_path": _display_path(path, repo),
        "source_digest": source_digest,
        "interaction_brief": {
            "brief_ref": brief["brief_id"],
            "target_ref": brief["academic_target"]["target_ref"],
            "canonical_record_refs": list(brief["provenance"]["canonical_record_refs"]),
            "canonical_input_digest": brief_digest,
            "freshness": brief_freshness["status"],
        },
        "runtime": runtime_binding,
        "package": package,
        "reuse_evidence": reuse_evidence,
        "reuse_analysis": reuse_analysis,
        "binding_digest": binding_digest,
        "claim_note": (
            "This is a governed LOCAL implementation bound to a current academic handoff. "
            "The portable package remains non-canonical academic data; LOCAL maturity comes "
            "from concrete R4 creation evidence and does not imply REUSED or SHARED status."
        ),
    }


def freshness(record: dict, source_path: Path, *, repo: Path = REPO) -> dict[str, Any]:
    """Recompile from canonical + local source and detect academic or engineering drift."""
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
        "brief_freshness": current["interaction_brief"]["freshness"],
        "runtime": current["runtime"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--package-out", type=Path)
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
    if args.package_out and not args.check:
        args.package_out.parent.mkdir(parents=True, exist_ok=True)
        args.package_out.write_text(
            json.dumps(result["package"], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return 1 if args.enforce and result.get("status") != "CURRENT" else 0


if __name__ == "__main__":
    raise SystemExit(main())
