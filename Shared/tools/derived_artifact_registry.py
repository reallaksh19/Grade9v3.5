#!/usr/bin/env python3
"""Persist and search content-addressed derived Core artifacts without promoting them to academic authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "publication" / "derived-artifacts"
CORE_DIR = ROOT / "core-projections"
INDEX = ROOT / "derived-artifact-index.v1.json"
CONTRACT_VERSION = "1.0.0"
WEB_GENERATOR_INPUTS = (
    "Shared/tools/web_resolver.py",
    "Shared/tools/build_explore_page.py",
    "Shared/tools/build_interactive_page.py",
    "Shared/tools/web_run_bundle.py",
    "Shared/tools/web_validator.py",
    "Shared/library/web-resolution-plan.schema.json",
    "Shared/web/interactive-page-blueprints.v1.json",
    "Shared/web/explorer-profiles.v1.json",
    "Shared/workbench/core-learning-page.mjs",
)

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.library.resolve import build_index, load_packages
from Shared.tools import build_core_learning_data


def digest(value: Any) -> str:
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _repository_basis(repo: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _web_generator_digest(repo: Path) -> str:
    return digest({
        relative: bytes_digest(path.read_bytes()) if path.is_file() else None
        for relative in WEB_GENERATOR_INPUTS
        for path in [repo / relative]
    })


def _canonical_input_digest(row: dict, refs: dict[str, list[str]], records: dict[str, dict]) -> str:
    selected = {row.get("source_ref")}
    for key, values in refs.items():
        if key.endswith("_refs"):
            selected.update(values)
    selected.discard(None)
    return digest({
        ref: records.get(ref)
        for ref in sorted(selected)
    })


def _subject_records(subject: str, repo: Path) -> dict[str, dict]:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths)) if paths else {}


def _refs(row: dict, records: dict[str, dict]) -> dict[str, list[str]]:
    projection = row.get("projection") or {}
    orientation = projection.get("orientation") or {}
    concept = projection.get("concept") or {}
    application = projection.get("application") or {}
    microtopics = [concept.get("microtopic_ref")] if concept.get("microtopic_ref") else []
    questions = [application.get("question_ref")] if application.get("question_ref") else []
    families = [application.get("family_ref")] if application.get("family_ref") else []
    buckets = [orientation.get("bucket_ref")] if orientation.get("bucket_ref") else []
    capabilities: list[str] = []
    representations: list[str] = list(concept.get("representation_refs") or [])

    for microtopic_ref in microtopics:
        record = records.get(microtopic_ref) or {}
        value = record.get("primary_capability_ref")
        if isinstance(value, str) and value not in capabilities:
            capabilities.append(value)
        for ref in record.get("representation_refs") or []:
            if isinstance(ref, str) and ref not in representations:
                representations.append(ref)

    for question_ref in questions:
        record = records.get(question_ref) or {}
        for value in [record.get("primary_capability_ref"), *(record.get("secondary_capability_refs") or [])]:
            if isinstance(value, str) and value not in capabilities:
                capabilities.append(value)
        value = record.get("family_ref")
        if isinstance(value, str) and value not in families:
            families.append(value)
        for move in (record.get("answer") or {}).get("reasoning_route", []):
            ref = move.get("representation_ref") if isinstance(move, dict) else None
            if isinstance(ref, str) and ref not in representations:
                representations.append(ref)
        for scaffold in record.get("scaffolds") or []:
            ref = scaffold.get("visual_ref") if isinstance(scaffold, dict) else None
            if isinstance(ref, str) and ref not in representations:
                representations.append(ref)

    initial = (projection.get("presentation") or {}).get("initial_visual_ref")
    if isinstance(initial, str) and initial not in representations:
        representations.append(initial)

    return {
        "bucket_refs": sorted(set(buckets)),
        "microtopic_refs": sorted(set(microtopics)),
        "capability_refs": sorted(set(capabilities)),
        "question_refs": sorted(set(questions)),
        "family_refs": sorted(set(families)),
        "representation_refs": sorted(set(representations)),
    }


def _search_text(row: dict, records: dict[str, dict]) -> str:
    projection = row.get("projection") or {}
    concept = projection.get("concept") or {}
    application = projection.get("application") or {}
    pieces = [
        row.get("source_ref"),
        projection.get("core"),
        concept.get("title"),
        concept.get("inferential_jump"),
        application.get("stem"),
        application.get("family_ref"),
        application.get("crux_move_ref"),
    ]
    for item in concept.get("misconceptions") or []:
        if isinstance(item, dict):
            pieces.extend([item.get("wrong_idea"), item.get("repair")])
    move_map = {
        move.get("id"): move
        for move in application.get("reasoning_route") or []
        if isinstance(move, dict)
    }
    crux = move_map.get(application.get("crux_move_ref")) or {}
    pieces.extend([crux.get("kind"), crux.get("action"), crux.get("why_valid")])
    return " ".join(str(piece) for piece in pieces if piece).lower()


def current_entries(repo: Path = REPO) -> tuple[list[dict], dict]:
    payload = build_core_learning_data.build()
    records_by_subject: dict[str, dict] = {}
    entries = []
    repository_basis = _repository_basis(repo)
    for row in payload.get("core_projections", []):
        subject = row.get("subject")
        if subject not in records_by_subject:
            records_by_subject[subject] = _subject_records(subject, repo)
        refs = _refs(row, records_by_subject[subject])
        projection_digest = digest(row)
        canonical_digest = _canonical_input_digest(row, refs, records_by_subject[subject])
        contract_version = (payload.get("provider") or {}).get("contract_version")
        version_digest = digest([row.get("id"), canonical_digest, contract_version, projection_digest])
        short = version_digest.split(":", 1)[1][:20]
        artifact_id = f"derived-core-projection-{short}"
        entries.append({
            "artifact_id": artifact_id,
            "artifact_type": "CORE_PROJECTION",
            "semantic_id": row.get("id"),
            "subject": subject,
            "core": (row.get("projection") or {}).get("core"),
            "source_ref": row.get("source_ref"),
            **refs,
            "provider_contract_version": contract_version,
            "repository_basis": repository_basis,
            "canonical_input_digest": canonical_digest,
            "artifact_digest": projection_digest,
            "payload_path": f"core-projections/{artifact_id}.json",
            "status": "CURRENT",
            "search_text": _search_text(row, records_by_subject[subject]),
            "_payload": row,
        })
    entries.sort(key=lambda item: (item["subject"] or "", item["core"] or "", item["semantic_id"] or ""))
    return entries, payload


def build_index_payload(repo: Path = REPO, previous: dict | None = None) -> dict:
    current, provider = current_entries(repo)
    current_ids = {row["artifact_id"] for row in current}
    old = [
        dict(row)
        for row in (previous or {}).get("artifacts", [])
        if row.get("artifact_id") not in current_ids
    ]
    current_semantic = {
        (row.get("subject"), row.get("core"), row.get("semantic_id")): row["artifact_id"]
        for row in current
    }
    for row in old:
        if row.get("artifact_type") == "CORE_PROJECTION":
            key = (row.get("subject"), row.get("core"), row.get("semantic_id"))
            row["status"] = "STALE" if key in current_semantic else "REFERENCE_ONLY"
        row.pop("_payload", None)
    clean_current = []
    for row in current:
        copy = dict(row)
        copy.pop("_payload", None)
        clean_current.append(copy)
    artifacts = sorted(
        [*old, *clean_current],
        key=lambda item: (
            item.get("subject") or "",
            item.get("core") or "",
            item.get("semantic_id") or "",
            item.get("artifact_id") or "",
        ),
    )
    return {
        "contract_version": CONTRACT_VERSION,
        "authority": "DERIVED_PRODUCTION_MEMORY_ONLY",
        "provider": provider.get("provider"),
        "artifact_count": len(artifacts),
        "current_count": sum(row.get("status") == "CURRENT" for row in artifacts),
        "artifacts": artifacts,
    }


def write(repo: Path = REPO) -> dict:
    previous = None
    index_path = repo / INDEX.relative_to(REPO)
    if index_path.is_file():
        previous = json.loads(index_path.read_text(encoding="utf-8"))
    current, _ = current_entries(repo)
    core_dir = repo / CORE_DIR.relative_to(REPO)
    core_dir.mkdir(parents=True, exist_ok=True)
    for row in current:
        path = core_dir / f'{row["artifact_id"]}.json'
        if path.exists():
            if digest(json.loads(path.read_text(encoding="utf-8"))) != row["artifact_digest"]:
                raise ValueError(f"ARTIFACT_DIGEST_MISMATCH:{path}")
        else:
            path.write_text(
                json.dumps(row["_payload"], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    payload = build_index_payload(repo, previous)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return payload


def load_index(repo: Path = REPO) -> dict:
    path = repo / INDEX.relative_to(REPO)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"contract_version": CONTRACT_VERSION, "artifacts": []}


def register_run_bundle(
    *,
    files: dict[str, bytes],
    plan: dict,
    release_ready: bool = False,
    repo: Path = REPO,
) -> list[str]:
    """Archive and index the exact outputs of a completed web run."""
    root = repo / ROOT.relative_to(REPO)
    index = load_index(repo)
    if index.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("ARTIFACT_INDEX_CONTRACT_INCOMPATIBLE")
    basis = bytes_digest(files["canonical/canonical-slice.json"])
    bundle_id = digest({path: bytes_digest(value) for path, value in sorted(files.items())}).split(":")[1][:20]
    refs = (plan.get("target") or {}).get("resolved_refs") or {}
    canonical_records = json.loads(files["canonical/canonical-slice.json"])["records"]
    canonical_input_digest = digest({
        "subject": plan["subject"],
        "authority": "CANONICAL_SLICE_FOR_REPRODUCTION_ONLY",
        "records": canonical_records,
    })
    kind_by_path = {
        "request/web-request.json": "WEB_REQUEST",
        "resolution/web-resolution-plan.json": "WEB_RESOLUTION_PLAN",
        "resolution/target-demand-route.json": "TARGET_DEMAND_ROUTE",
        "validation/web-validation.json": "VALIDATION_REPORT",
        "manifest.json": "RUN_MANIFEST",
        "outputs/index.html": "WEBPAGE",
    }
    existing = {row["artifact_id"]: row for row in index["artifacts"]}
    registered = []
    generator_digest = _web_generator_digest(repo)
    for relative, content in sorted(files.items()):
        artifact_type = kind_by_path.get(relative, "RUN_ARTIFACT")
        semantic_id = f'{plan["request_id"]}:{relative}'
        artifact_id = "derived-web-" + digest([
            semantic_id, basis, plan.get("pins"), bytes_digest(content),
        ]).split(":")[1][:20]
        payload_path = f"run-bundles/{bundle_id}/{relative}"
        path = root / payload_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"ARTIFACT_DIGEST_MISMATCH:{path}")
        if not path.exists():
            path.write_bytes(content)
        for old in index["artifacts"]:
            if old.get("semantic_id") == semantic_id and old.get("artifact_id") != artifact_id:
                old["status"] = "STALE"
        existing[artifact_id] = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "semantic_id": semantic_id,
            "subject": plan["subject"],
            "core": next(
                (row.get("core") for row in plan.get("experience_segments") or [] if row.get("core")), None
            ),
            "source_ref": (plan.get("target") or {}).get("exact_ref"),
            "matrix_ref": (plan.get("target") or {}).get("matrix_ref"),
            "rung": (plan.get("target") or {}).get("rung"),
            "canonical_record_refs": sorted(canonical_records),
            **{key: refs.get(key) or [] for key in (
                "bucket_refs", "microtopic_refs", "capability_refs", "question_refs",
                "family_refs", "representation_refs", "activity_refs",
            )},
            "repository_basis": _repository_basis(repo),
            "canonical_input_digest": canonical_input_digest,
            "artifact_digest": bytes_digest(content),
            "contract_versions": plan.get("pins"),
            "generator_digest": generator_digest,
            "payload_path": payload_path,
            "status": (
                "CURRENT" if release_ready and plan.get("request_satisfaction") in {"FULL", "DEGRADED_ACCEPTABLE"}
                else "HELD"
            ),
            "search_text": "",
        }
        registered.append(artifact_id)
    index["artifacts"] = sorted(
        existing.values(),
        key=lambda row: (row.get("subject") or "", row.get("semantic_id") or "", row["artifact_id"]),
    )
    index["artifact_count"] = len(index["artifacts"])
    index["current_count"] = sum(row.get("status") == "CURRENT" for row in index["artifacts"])
    (root / INDEX.name).write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return registered


def search(
    *,
    subject: str | None = None,
    core: str | None = None,
    artifact_type: str | None = None,
    exact_ref: str | None = None,
    text: str | None = None,
    repo: Path = REPO,
) -> list[dict]:
    index = load_index(repo)
    if not index.get("artifacts"):
        return []
    if index.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("ARTIFACT_INDEX_CONTRACT_INCOMPATIBLE")
    current_rows, _ = current_entries(repo)
    generator_digest = _web_generator_digest(repo)
    current_by_semantic = {
        (row.get("subject"), row.get("core"), row.get("semantic_id")): row
        for row in current_rows
    }
    results = []
    for row in index.get("artifacts", []):
        if subject and row.get("subject") != subject:
            continue
        if core and row.get("core") != core:
            continue
        if artifact_type and row.get("artifact_type") != artifact_type:
            continue
        exact_fields = [
            row.get("semantic_id"), row.get("source_ref"),
            *(row.get("bucket_refs") or []),
            *(row.get("microtopic_refs") or []),
            *(row.get("capability_refs") or []),
            *(row.get("question_refs") or []),
            *(row.get("family_refs") or []),
            *(row.get("representation_refs") or []),
            *(row.get("activity_refs") or []),
            *(row.get("canonical_record_refs") or []),
        ]
        if exact_ref and exact_ref not in exact_fields:
            continue
        if text and text.lower() not in (row.get("search_text") or ""):
            continue
        key = (row.get("subject"), row.get("core"), row.get("semantic_id"))
        current = current_by_semantic.get(key)
        payload_path = row.get("payload_path")
        stored = repo / ROOT.relative_to(REPO) / payload_path if isinstance(payload_path, str) else None
        valid_path = stored is not None and stored.resolve().is_relative_to((repo / ROOT.relative_to(REPO)).resolve())
        try:
            payload_valid = bool(
                valid_path and stored.is_file()
                and (
                    digest(json.loads(stored.read_text(encoding="utf-8")))
                    if row.get("artifact_type") == "CORE_PROJECTION"
                    else bytes_digest(stored.read_bytes())
                ) == row.get("artifact_digest")
            )
        except (OSError, ValueError, json.JSONDecodeError):
            payload_valid = False
        if not payload_valid:
            freshness, reuse = "INCOMPATIBLE", "FORBIDDEN"
        elif (
            current
            and current["artifact_digest"] == row.get("artifact_digest")
            and current["canonical_input_digest"] == row.get("canonical_input_digest")
            and current["provider_contract_version"] == row.get("provider_contract_version")
        ):
            freshness, reuse = "CURRENT", "DIRECT"
        elif current:
            freshness, reuse = "STALE", "REGENERATE"
        elif row.get("artifact_type") != "CORE_PROJECTION":
            records = _subject_records(row["subject"], repo)
            canonical_slice = {
                "subject": row["subject"],
                "authority": "CANONICAL_SLICE_FOR_REPRODUCTION_ONLY",
                "records": {
                    ref: records[ref]
                    for ref in row.get("canonical_record_refs") or []
                    if ref in records
                },
            }
            if row.get("status") == "HELD":
                freshness, reuse = "INCOMPATIBLE", "FORBIDDEN"
            elif (
                row.get("status") == "CURRENT"
                and digest(canonical_slice) == row.get("canonical_input_digest")
                and row.get("generator_digest") == generator_digest
            ):
                freshness, reuse = "CURRENT", "DIRECT"
            else:
                freshness, reuse = "STALE", "REGENERATE"
        else:
            freshness, reuse = "REFERENCE_ONLY", "REFERENCE_ONLY"
        match_kind = "EXACT_REF" if exact_ref else ("TEXT" if text else "FILTER")
        results.append({
            "artifact_ref": row.get("artifact_id"),
            "artifact_type": row.get("artifact_type"),
            "semantic_id": row.get("semantic_id"),
            "subject": row.get("subject"),
            "core": row.get("core"),
            "payload_path": row.get("payload_path"),
            "match": {"kind": match_kind, "matched_refs": [exact_ref] if exact_ref else []},
            "freshness": freshness,
            "reuse": reuse,
            "canonical_basis": row.get("canonical_input_digest"),
            "artifact_digest": row.get("artifact_digest"),
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--subject")
    parser.add_argument("--core")
    parser.add_argument("--exact-ref")
    parser.add_argument("--text")
    args = parser.parse_args()
    if args.write:
        result = write()
    else:
        result = {
            "results": search(
                subject=args.subject,
                core=args.core,
                exact_ref=args.exact_ref,
                text=args.text,
            )
        }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
