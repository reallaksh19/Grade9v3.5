#!/usr/bin/env python3
"""Build/check deterministic Question Bank growth artifacts from canonical projection data."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

try:
    from . import build_question_bank_web
    from .question_bank_platform import (
        WORKER_CONTRACT_VERSION,
        assemble_platform,
        digest,
        enrich_question_refs,
        explain,
        load_resources,
        render_js,
        subject_ref,
    )
except ImportError:  # direct: python3 Shared/tools/build_question_bank_platform.py
    import build_question_bank_web
    from question_bank_platform import (
        WORKER_CONTRACT_VERSION,
        assemble_platform,
        digest,
        enrich_question_refs,
        explain,
        load_resources,
        render_js,
        subject_ref,
    )

REPO = Path(__file__).resolve().parents[2]
GENERATOR_VERSION = "1.1.0"
DETAIL_SCHEMA = "grade9v3-question-bank-detail-shard-v1"
DETAIL_DIR = Path("public/data/question-bank-details")

OUTPUTS = {
    "catalog": Path("public/data/question-bank-catalog.js"),
    "search": Path("public/data/question-bank-search.js"),
    "resources": Path("public/data/question-bank-resources.js"),
    "manifest": Path("public/data/question-bank-manifest.js"),
    "dedup": Path("artifacts/question-bank/dedup-report.json"),
    "lineage": Path("artifacts/question-bank/lineage.json"),
    "receipt": Path("artifacts/question-bank/build-receipt.json"),
}


def _detail_file(subject_identity: str) -> Path:
    safe = re.sub(r"[^a-z0-9]+", "-", subject_identity.casefold()).strip("-") or "subject"
    suffix = digest(subject_identity).split(":", 1)[1][:10]
    return DETAIL_DIR / f"{safe[:80]}-{suffix}.js"


def _detail_shards(questions: list[dict], build_id: str) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for raw in questions:
        question = enrich_question_refs(raw)
        grouped[question["subject_ref"]].append(question)

    shards: list[dict] = []
    for subject_identity in sorted(grouped):
        rows = sorted(grouped[subject_identity], key=lambda row: (row.get("order", 0), str(row["id"])))
        shard_id = f"details:{subject_identity}"
        payload = {
            "schema_version": DETAIL_SCHEMA,
            "build_id": build_id,
            "shard_id": shard_id,
            "subject_ref": subject_identity,
            "question_count": len(rows),
            "questions": rows,
        }
        path = _detail_file(subject_identity)
        shards.append({
            "id": shard_id,
            "subject_ref": subject_identity,
            "path": path.as_posix().removeprefix("public/"),
            "output_path": path,
            "question_count": len(rows),
            "digest": digest(payload),
            "payload": payload,
        })
    return shards


def _trace_canonical_sources(platform: dict, browser: dict) -> None:
    """Fill audit lineage from browser basis without changing the legacy learner payload."""
    bank_sources = {
        subject_ref(str(row["subject"])): row["path"]
        for row in browser.get("basis", {}).get("banks", [])
        if row.get("subject") and row.get("path")
    }
    for row in platform["lineage"]["questions"]:
        if row.get("source_path"):
            continue
        source_path = bank_sources.get(row.get("subject_ref"))
        if source_path:
            row["source_path"] = source_path
            row["adapter"] = "competitive_exam_bank_v2"
    platform["receipt"]["outputs"]["lineage"] = digest(platform["lineage"])


def build(repo: Path = REPO) -> dict:
    browser = build_question_bank_web.build(repo)
    resources, resource_basis = load_resources(repo)
    platform = assemble_platform(browser, resources, resource_basis)
    _trace_canonical_sources(platform, browser)

    shards = _detail_shards(browser.get("questions", []), platform["build_id"])
    shard_identity = [
        {
            "id": row["id"],
            "subject_ref": row["subject_ref"],
            "question_count": row["question_count"],
            "digest": row["digest"],
        }
        for row in shards
    ]
    platform["detail_shards"] = shards
    platform["receipt"]["counts"]["detail_shards"] = len(shards)
    platform["receipt"]["workers"].append({
        "worker_id": "details",
        "contract_version": WORKER_CONTRACT_VERSION,
        "input_digest": digest(browser.get("questions", [])),
        "output_digest": digest(shard_identity),
    })
    platform["receipt"]["workers"].sort(key=lambda row: row["worker_id"])
    platform["receipt"]["outputs"]["detail_shards"] = digest(shard_identity)
    return platform


def _detail_script(shard: dict) -> bytes:
    payload = json.dumps(shard["payload"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    shard_id = json.dumps(shard["id"], ensure_ascii=False)
    return (
        "window.GRADE9_QUESTION_BANK_DETAIL_SHARDS=window.GRADE9_QUESTION_BANK_DETAIL_SHARDS||{};\n"
        f"window.GRADE9_QUESTION_BANK_DETAIL_SHARDS[{shard_id}]={payload};\n"
    ).encode("utf-8")


def artifact_payloads(platform: dict) -> dict[Path, bytes]:
    build_id = platform["build_id"]
    catalog = {**platform["catalog"], "build_id": build_id}
    search = {**platform["search"], "build_id": build_id}
    resources = dict(platform["resources"])

    detail_manifest = [
        {
            "id": row["id"],
            "subject_ref": row["subject_ref"],
            "path": row["path"],
            "digest": row["digest"],
            "question_count": row["question_count"],
        }
        for row in platform.get("detail_shards", [])
    ]
    logical = {
        "catalog": {"path": OUTPUTS["catalog"].as_posix().removeprefix("public/"), "digest": digest(catalog)},
        "search": {"path": OUTPUTS["search"].as_posix().removeprefix("public/"), "digest": digest(search)},
        "resources": {"path": OUTPUTS["resources"].as_posix().removeprefix("public/"), "digest": digest(resources)},
        "dedup": {"path": OUTPUTS["dedup"].as_posix(), "digest": digest(platform["dedup"])},
        "lineage": {"path": OUTPUTS["lineage"].as_posix(), "digest": digest(platform["lineage"])},
        "receipt": {"path": OUTPUTS["receipt"].as_posix(), "digest": digest(platform["receipt"])},
    }
    manifest = {
        "schema_version": "grade9v3-question-bank-manifest-v1",
        "generator": "Shared/tools/build_question_bank_platform.py",
        "generator_version": GENERATOR_VERSION,
        "build_id": build_id,
        "readiness": ["APP_SHELL_READY", "CATALOG_READY", "SEARCH_READY", "STUDY_DETAIL_READY_ON_DEMAND"],
        "bootstrap": {
            "catalog": logical["catalog"],
            "search": logical["search"],
            "resources": logical["resources"],
        },
        "detail_shards": detail_manifest,
        "audit_artifacts": {
            "dedup": logical["dedup"],
            "lineage": logical["lineage"],
            "receipt": logical["receipt"],
        },
    }

    def json_bytes(value: object) -> bytes:
        return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

    payloads: dict[Path, bytes] = {
        OUTPUTS["catalog"]: render_js("GRADE9_QUESTION_BANK_CATALOG", catalog).encode("utf-8"),
        OUTPUTS["search"]: render_js("GRADE9_QUESTION_BANK_SEARCH", search).encode("utf-8"),
        OUTPUTS["resources"]: render_js("GRADE9_QUESTION_BANK_RESOURCES", resources).encode("utf-8"),
        OUTPUTS["manifest"]: render_js("GRADE9_QUESTION_BANK_MANIFEST", manifest).encode("utf-8"),
        OUTPUTS["dedup"]: json_bytes(platform["dedup"]),
        OUTPUTS["lineage"]: json_bytes(platform["lineage"]),
        OUTPUTS["receipt"]: json_bytes(platform["receipt"]),
    }
    for shard in platform.get("detail_shards", []):
        payloads[shard["output_path"]] = _detail_script(shard)
    return payloads


def _stale_detail_files(repo: Path, intended: set[Path]) -> list[Path]:
    root = repo / DETAIL_DIR
    if not root.is_dir():
        return []
    return sorted(
        path.relative_to(repo)
        for path in root.glob("*.js")
        if path.relative_to(repo) not in intended
    )


def findings(repo: Path = REPO) -> list[str]:
    intended = artifact_payloads(build(repo))
    output: list[str] = []
    for relative, content in intended.items():
        path = repo / relative
        if not path.is_file():
            output.append(f"missing generated Question Bank artifact: {relative.as_posix()}")
        elif path.read_bytes() != content:
            output.append(f"stale generated Question Bank artifact: {relative.as_posix()}")
    for relative in _stale_detail_files(repo, set(intended)):
        output.append(f"stale generated Question Bank detail shard: {relative.as_posix()}")
    return output


def write(repo: Path = REPO) -> None:
    intended = artifact_payloads(build(repo))
    for relative in _stale_detail_files(repo, set(intended)):
        (repo / relative).unlink()
        print(f"removed {relative.as_posix()}")
    for relative, content in intended.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"wrote {relative.as_posix()}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--explain", metavar="RECORD_ID")
    args = parser.parse_args(argv)

    if args.explain:
        platform = build(REPO)
        result = explain(platform, args.explain)
        if result is None:
            print(json.dumps({"id": args.explain, "found": False}, indent=2))
            return 1
        print(json.dumps({"id": args.explain, "found": True, **result}, indent=2, ensure_ascii=False))
        return 0
    if args.write or not args.check:
        write(REPO)
        return 0
    errors = findings(REPO)
    if errors:
        print("\n".join(errors))
        print("Regenerate with: python3 Shared/tools/build_question_bank_platform.py --write")
        return 1
    print("Question Bank platform artifacts are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
