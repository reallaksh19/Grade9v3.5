#!/usr/bin/env python3
"""Build/check deterministic Question Bank growth artifacts from canonical projection data."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Shared.tools import build_question_bank_web
from Shared.tools.question_bank_platform import (
    assemble_platform,
    digest,
    explain,
    load_resources,
    render_js,
)

REPO = Path(__file__).resolve().parents[2]
GENERATOR_VERSION = "1.0.0"

OUTPUTS = {
    "catalog": Path("public/data/question-bank-catalog.js"),
    "search": Path("public/data/question-bank-search.js"),
    "resources": Path("public/data/question-bank-resources.js"),
    "manifest": Path("public/data/question-bank-manifest.js"),
    "dedup": Path("artifacts/question-bank/dedup-report.json"),
    "lineage": Path("artifacts/question-bank/lineage.json"),
    "receipt": Path("artifacts/question-bank/build-receipt.json"),
}


def build(repo: Path = REPO) -> dict:
    browser = build_question_bank_web.build(repo)
    resources, resource_basis = load_resources(repo)
    return assemble_platform(browser, resources, resource_basis)


def artifact_payloads(platform: dict) -> dict[Path, bytes]:
    build_id = platform["build_id"]
    catalog = {**platform["catalog"], "build_id": build_id}
    search = {**platform["search"], "build_id": build_id}
    resources = dict(platform["resources"])

    logical = {
        "catalog": {"path": OUTPUTS["catalog"].as_posix(), "digest": digest(catalog)},
        "search": {"path": OUTPUTS["search"].as_posix(), "digest": digest(search)},
        "resources": {"path": OUTPUTS["resources"].as_posix(), "digest": digest(resources)},
        "dedup": {"path": OUTPUTS["dedup"].as_posix(), "digest": digest(platform["dedup"])},
        "lineage": {"path": OUTPUTS["lineage"].as_posix(), "digest": digest(platform["lineage"])},
        "receipt": {"path": OUTPUTS["receipt"].as_posix(), "digest": digest(platform["receipt"])},
    }
    manifest = {
        "schema_version": "grade9v3-question-bank-manifest-v1",
        "generator": "Shared/tools/build_question_bank_platform.py",
        "generator_version": GENERATOR_VERSION,
        "build_id": build_id,
        "artifacts": logical,
    }

    def json_bytes(value: object) -> bytes:
        return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")

    return {
        OUTPUTS["catalog"]: render_js("GRADE9_QUESTION_BANK_CATALOG", catalog).encode("utf-8"),
        OUTPUTS["search"]: render_js("GRADE9_QUESTION_BANK_SEARCH", search).encode("utf-8"),
        OUTPUTS["resources"]: render_js("GRADE9_QUESTION_BANK_RESOURCES", resources).encode("utf-8"),
        OUTPUTS["manifest"]: render_js("GRADE9_QUESTION_BANK_MANIFEST", manifest).encode("utf-8"),
        OUTPUTS["dedup"]: json_bytes(platform["dedup"]),
        OUTPUTS["lineage"]: json_bytes(platform["lineage"]),
        OUTPUTS["receipt"]: json_bytes(platform["receipt"]),
    }


def findings(repo: Path = REPO) -> list[str]:
    intended = artifact_payloads(build(repo))
    out: list[str] = []
    for relative, content in intended.items():
        path = repo / relative
        if not path.is_file():
            out.append(f"missing generated Question Bank artifact: {relative.as_posix()}")
        elif path.read_bytes() != content:
            out.append(f"stale generated Question Bank artifact: {relative.as_posix()}")
    return out


def write(repo: Path = REPO) -> None:
    for relative, content in artifact_payloads(build(repo)).items():
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
