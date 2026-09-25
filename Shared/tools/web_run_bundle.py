#!/usr/bin/env python3
"""Write a reproducible web-generation run bundle from a WebResolutionPlan."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import load
from Shared.library.resolve import build_index, load_packages
from Shared.tools import (
    build_core_learning_data, build_explore_page, build_interactive_page,
    derived_artifact_registry, web_validator,
)


def _bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _records(subject: str, repo: Path) -> dict[str, dict]:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths)) if paths else {}


def canonical_slice(plan: dict, repo: Path = REPO) -> dict:
    records = _records(plan["subject"], repo)
    refs = set()
    for values in (plan.get("target", {}).get("resolved_refs") or {}).values():
        if isinstance(values, list):
            refs.update(value for value in values if isinstance(value, str))
    rows = {
        ref: records[ref]
        for ref in sorted(refs)
        if ref in records
    }
    return {
        "subject": plan["subject"],
        "authority": "CANONICAL_SLICE_FOR_REPRODUCTION_ONLY",
        "records": rows,
    }


def projection_slice(plan: dict) -> dict:
    payload = build_core_learning_data.build()
    wanted = {
        row.get("projection_ref")
        for row in plan.get("experience_segments", [])
        if row.get("projection_ref")
    }
    return {
        "provider": payload.get("provider"),
        "core_projections": [
            row for row in payload.get("core_projections", [])
            if row.get("id") in wanted
        ],
    }


def write_bundle(
    request: dict,
    plan: dict,
    out_dir: Path,
    *,
    route_artifact: dict | None = None,
    repo: Path = REPO,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    files: dict[str, bytes] = {
        "request/web-request.json": _bytes(request),
        "resolution/web-resolution-plan.json": _bytes(plan),
        "canonical/canonical-slice.json": _bytes(canonical_slice(plan, repo)),
        "projection/core-projections.json": _bytes(projection_slice(plan)),
    }
    if route_artifact is not None:
        files["resolution/target-demand-route.json"] = _bytes(route_artifact)

    validation = web_validator.validate(request, plan, route_artifact=route_artifact, repo=repo)
    files["validation/web-validation.json"] = _bytes(validation)
    if validation["release_ready"]:
        if plan["build_action"] == "CORE_PAGE_ADAPTER":
            projection_ref = plan["experience_segments"][0]["projection_ref"]
            row = next(
                row for row in build_core_learning_data.build()["core_projections"]
                if row["id"] == projection_ref
            )
            package = build_interactive_page.compile_page_package(row)
            if request["packaging_mode"] == "SINGLE_FILE":
                outputs = {"index.html": build_interactive_page.render_single_file(package)}
            else:
                outputs = build_interactive_page.render_offline_directory(
                    package, request["packaging_mode"],
                )
        elif plan["build_action"] == "EXPLORE_PAGE_ADAPTER":
            package = build_explore_page.compile_page_package(plan, repo)
            if request["packaging_mode"] == "SINGLE_FILE":
                outputs = {"index.html": build_explore_page.render_single_file(package)}
            else:
                outputs = build_explore_page.render_directory(package, request["packaging_mode"])
        else:
            raise ValueError(f"WEB_BUILD_ACTION_UNSUPPORTED:{plan['build_action']}")
        files.update({f"outputs/{name}": content for name, content in outputs.items()})

    remembered = []
    for segment in plan.get("experience_segments", []):
        ref = segment.get("remembered_artifact_ref")
        if ref:
            remembered.append({
                "core": segment.get("core"),
                "artifact_ref": ref,
                "reuse": segment.get("remembered_reuse"),
            })
    files["resolution/remembered-artifacts.json"] = _bytes({"artifacts": remembered})

    manifest_files = []
    for relative, content in sorted(files.items()):
        path = out_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        manifest_files.append({
            "path": relative,
            "bytes": len(content),
            "sha256": _digest(content),
        })

    # Register the provider projections that this run actually used.
    registry = derived_artifact_registry.write(repo)
    manifest = {
        "schema_version": "1.0.0",
        "request_id": request.get("request_id"),
        "subject": plan.get("subject"),
        "request_satisfaction": plan.get("request_satisfaction"),
        "build_action": plan.get("build_action"),
        "pins": plan.get("pins"),
        "files": manifest_files,
        "fixture_promotion": "EXPLICIT_REVIEW_REQUIRED",
        "registered_core_artifacts": [
            row["artifact_id"]
            for row in registry["artifacts"]
            if row.get("artifact_type") == "CORE_PROJECTION"
            and row.get("status") == "CURRENT"
            and row.get("semantic_id") in {
                item.get("projection_ref") for item in plan.get("experience_segments", [])
            }
        ],
    }
    manifest_content = _bytes(manifest)
    (out_dir / "manifest.json").write_bytes(manifest_content)
    derived_artifact_registry.register_run_bundle(
        files={**files, "manifest.json": manifest_content}, plan=plan, repo=repo,
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--route-artifact", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = write_bundle(
        load(args.request),
        load(args.plan),
        args.out_dir,
        route_artifact=load(args.route_artifact) if args.route_artifact else None,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
