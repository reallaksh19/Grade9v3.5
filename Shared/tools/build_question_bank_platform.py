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
        load_subtopic_titles,
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
        load_subtopic_titles,
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
    "questions": Path("public/data/question-bank-questions.js"),
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
    return build_from_projection(browser, resources, resource_basis, load_subtopic_titles(repo, browser.get("questions", [])))


def build_from_projection(browser: dict, resources: list[dict] = (), resource_basis: list[dict] = (),
                          subtopic_titles: dict | None = None) -> dict:
    """The whole platform, detail shards and receipt included, from one canonical browser projection."""
    platform = assemble_platform(browser, resources, resource_basis, subtopic_titles=subtopic_titles)
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


TRACE_LINKS = (
    "canonical_record", "taxonomy_membership", "source_provenance", "normalizing_worker",
    "generated_artifacts", "search_document", "browser_id", "build",
)


def trace(platform: dict, record_id: str, repo: Path | None = None) -> dict | None:
    """Answer, for one visible question, the eight lineage questions of #359 STEP-QB-10.

    Every link is read from the build itself (lineage rows, search documents, detail shards,
    worker receipts), never restated. With ``repo`` the deployment link also compares the committed
    ``public/`` and ``docs/`` copies of each artifact with the bytes this build would generate.
    Explanation only: nothing here owns academic truth.
    """
    explained = explain(platform, record_id)
    if explained is None:
        return None
    lineage, document = explained["lineage"], explained["search_document"]
    shard = next((row for row in platform.get("detail_shards", [])
                  if any(q.get("id") == record_id for q in row["payload"]["questions"])), None)
    detail = next((q for q in shard["payload"]["questions"] if q.get("id") == record_id), None) if shard else None
    receipts = {row["worker_id"]: row for row in platform["receipt"]["workers"]}

    chain = {
        "canonical_record": {
            "source_path": lineage.get("source_path"),
            "adapter": lineage.get("adapter"),
            "package_id": ((detail or {}).get("lineage") or {}).get("package_id"),
        },
        "taxonomy_membership": {
            "subject_ref": lineage["subject_ref"],
            "topic_ref": lineage["topic_ref"],
            "subtopic_refs": lineage.get("subtopic_refs", []),
        },
        "source_provenance": {
            key: (detail or {}).get(key)
            for key in ("exam", "year", "paper", "question_number", "source_status", "authority_class")
        },
        "normalizing_worker": {
            "adapter": lineage.get("adapter"),
            "reads_it": sorted(w for w in ("catalog", "search", "dedup", "details") if w in receipts),
            "receipts": {w: receipts[w] for w in ("catalog", "search", "dedup", "details") if w in receipts},
        },
        "generated_artifacts": {
            "search_index": OUTPUTS["search"].as_posix(),
            "detail_shard": {"id": shard["id"], "path": shard["path"], "digest": shard["digest"]} if shard else None,
        },
        "search_document": {"indexed": bool(lineage.get("search_indexed") and document), "label": (document or {}).get("label")},
        "browser_id": {
            "id": record_id,
            "same_in_search_and_detail": bool(document and detail and document["id"] == detail["id"] == record_id),
        },
        "build": {"build_id": platform["build_id"], "receipt_digest": digest(platform["receipt"])},
    }
    result = {
        "id": record_id,
        "found": True,
        "chain": chain,
        "broken_links": [name for name, ok in _link_status(chain).items() if not ok],
    }
    if repo is not None:
        result["deployment"] = _deployment(platform, repo, chain)
    return result


def _link_status(chain: dict) -> dict[str, bool]:
    return {
        "canonical_record": bool(chain["canonical_record"]["source_path"] or chain["canonical_record"]["package_id"])
        and bool(chain["canonical_record"]["adapter"]),
        "taxonomy_membership": bool(chain["taxonomy_membership"]["subject_ref"] and chain["taxonomy_membership"]["topic_ref"]),
        "source_provenance": any(v not in (None, "") for v in chain["source_provenance"].values()),
        "normalizing_worker": bool(chain["normalizing_worker"]["adapter"] and chain["normalizing_worker"]["reads_it"]),
        "generated_artifacts": chain["generated_artifacts"]["detail_shard"] is not None,
        "search_document": chain["search_document"]["indexed"],
        "browser_id": chain["browser_id"]["same_in_search_and_detail"],
        "build": bool(chain["build"]["build_id"]),
    }


def _deployment(platform: dict, repo: Path, chain: dict) -> dict:
    """Is the committed public/ copy, and its docs/ mirror, exactly what this build generates?"""
    expected = artifact_payloads(platform)
    wanted = [OUTPUTS["search"], OUTPUTS["questions"], OUTPUTS["catalog"], OUTPUTS["manifest"]]
    shard = chain["generated_artifacts"]["detail_shard"]
    if shard:
        wanted.append(Path("public") / shard["path"])
    rows = []
    for path in wanted:
        want = expected.get(path)
        public = repo / path
        mirror = repo / "docs" / path.relative_to("public")
        rows.append({
            "artifact": path.as_posix(),
            "public_matches_build": bool(want is not None and public.is_file() and public.read_bytes() == want),
            "docs_matches_build": bool(want is not None and mirror.is_file() and mirror.read_bytes() == want),
        })
    return {"checked_against": repo.name, "artifacts": rows,
            "deployed": all(r["public_matches_build"] and r["docs_matches_build"] for r in rows)}


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
    summaries = {**platform["summaries"], "build_id": build_id}
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
        "questions": {"path": OUTPUTS["questions"].as_posix().removeprefix("public/"), "digest": digest(summaries)},
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
        "readiness": ["APP_SHELL_READY", "CATALOG_READY", "LIST_READY", "SEARCH_READY", "STUDY_DETAIL_READY_ON_DEMAND"],
        "bootstrap": {
            "catalog": {**logical["catalog"], "required": True},
            "questions": {**logical["questions"], "required": True},
            "search": {**logical["search"], "required": True},
            "resources": {**logical["resources"], "required": False},
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
        OUTPUTS["questions"]: render_js("GRADE9_QUESTION_BANK_QUESTIONS", summaries).encode("utf-8"),
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
        p = repo / relative
        if p.is_file():
            p.unlink()
            print(f"removed {relative.as_posix()}")
        if relative.parts[0] == "public":
            docs_stale = repo / "docs" / relative.relative_to("public")
            if docs_stale.is_file():
                docs_stale.unlink()
                print(f"removed mirror {docs_stale.relative_to(repo).as_posix()}")
    for relative, content in intended.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"wrote {relative.as_posix()}")
        if relative.parts[0] == "public":
            mirror = repo / "docs" / relative.relative_to("public")
            mirror.parent.mkdir(parents=True, exist_ok=True)
            mirror.write_bytes(content)
            print(f"mirrored {mirror.relative_to(repo).as_posix()}")


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
        traced = trace(platform, args.explain, REPO)
        print(json.dumps({"id": args.explain, "found": True, **result, "trace": traced}, indent=2, ensure_ascii=False))
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
