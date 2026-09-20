#!/usr/bin/env python3
"""Validate GCDR v1.3 master-suite, diagnostic-item, helper and delivery contracts.

The guard deliberately keeps explorer governance separate from suite/item governance.
It validates the existing flat JEE question registries through a normalized diagnostic
contract, so runtime pages do not need to duplicate governance objects in browser data.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import jsonschema

REPO = Path(__file__).resolve().parents[2]
SUITES = REPO / "docs" / "gcdr-suites"
SUITE_SCHEMA = REPO / "Shared" / "library" / "gcdr_suite_contract.schema.json"
ITEM_SCHEMA = REPO / "Shared" / "library" / "gcdr_diagnostic_item.schema.json"
HELPER_SCHEMA = REPO / "Shared" / "library" / "gcdr_helper_contract.schema.json"

GENERIC_FINAL_ANSWER = re.compile(
    r"^\s*(?:"
    r"(?:apply|use|evaluate|solve|calculate|compute|derive|verify)"
    r"(?:\s+(?:the|a|given|standard))?(?:\s+(?:formula|equation|expression|relation|result))?"
    r"|(?:symmetry|identity|relation|equation|result)\s+(?:verified|holds|satisfied)"
    r"|(?:as\s+required|as\s+shown)"
    r")[\s.:;!-]*$",
    re.I,
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_bank(path: Path, fmt: str) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if fmt == "JSON":
        data = json.loads(text)
    elif fmt == "WINDOW_JEE_QUESTIONS_DATA_JS":
        match = re.search(r"window\.JEE_QUESTIONS_DATA\s*=\s*", text)
        if not match:
            raise ValueError("cannot locate window.JEE_QUESTIONS_DATA assignment")
        payload = text[match.end():].lstrip()
        try:
            data, _ = json.JSONDecoder().raw_decode(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(f"cannot parse window.JEE_QUESTIONS_DATA: {exc}") from exc
    else:
        raise ValueError(f"unsupported diagnostic source format {fmt!r}")
    if not isinstance(data, list):
        raise ValueError("diagnostic source is not a list")
    return data


def normalize_item(q: dict, suite: dict) -> dict:
    fidelity = q.get("simFidelity", "UNAVAILABLE")
    sim_params = q.get("simParams") or {}
    binding_refs = q.get("simBindingRefs") or []
    return {
        "schema_version": "1.0.0",
        "item_id": q.get("id"),
        "source_provenance": {
            "provider": suite["external_corpus"]["provider"],
            "source_label": q.get("source", ""),
            "verification_status": q.get("sourceAudit", "SOURCE_UNVERIFIED"),
            "source_snapshot_date": suite["external_corpus"]["snapshot_date"],
        },
        "answer_contract": {
            "status": q.get("answerAudit", "PENDING"),
            "final_answer": q.get("ans", ""),
            "derivation_specific": bool(q.get("steps")),
            "derivation_steps": q.get("steps") or [],
            "independent_check": q.get("teacherCheck", ""),
            "audit_evidence_ref": suite["audit_evidence_ref"],
        },
        "teaching_contract": {
            "trap_alert": q.get("trap", ""),
            "transfer_takeaway": q.get("takeaway", ""),
            "chalkboard_check": q.get("teacherCheck", ""),
            "helpers": q.get("helperTags") or [],
        },
        "simulation_contract": {
            "fidelity": fidelity,
            "target_activity": q.get("targetTab", ""),
            "binding_refs": binding_refs,
            "fidelity_note": q.get("simFidelityNote", ""),
        },
    }


def _schema_errors(instance: Any, schema: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    return [
        f"{'.'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}"
        for error in validator.iter_errors(instance)
    ]


def _evidence_ref_exists(repo: Path, ref: str | None) -> bool:
    if not ref:
        return False
    path_text = ref.split("#", 1)[0]
    return bool(path_text) and (repo / path_text).is_file()


def _external_dependencies(text: str) -> set[str]:
    """Return remote runtime dependencies, not ordinary navigation/source links."""
    out: set[str] = set()
    pattern = re.compile(
        r'<script\b[^>]*\bsrc="(https?://[^"]+)"[^>]*>'
        r'|<link\b[^>]*\bhref="(https?://[^"]+)"[^>]*>',
        re.I,
    )
    for match in pattern.finditer(text):
        out.add(match.group(1) or match.group(2))
    return out


def _local_resource_dependencies(text: str) -> list[str]:
    out = []
    for match in re.finditer(r'<script\b[^>]*\bsrc="([^"]+)"[^>]*>|<link\b[^>]*\bhref="([^"]+)"[^>]*>', text, re.I):
        value = match.group(1) or match.group(2)
        if value.startswith(("http://", "https://", "data:", "#")):
            continue
        out.append(value)
    return out


def is_generic_final_answer(value: str) -> bool:
    return bool(GENERIC_FINAL_ANSWER.fullmatch(value or ""))


def findings(repo: Path = REPO) -> list[dict]:
    suite_schema = load(repo / "Shared/library/gcdr_suite_contract.schema.json")
    item_schema = load(repo / "Shared/library/gcdr_diagnostic_item.schema.json")
    helper_schema = load(repo / "Shared/library/gcdr_helper_contract.schema.json")
    suite_dir = repo / "docs/gcdr-suites"
    result: list[dict] = []

    def add(suite_id: str, point: str, detail: str, item_id: str | None = None):
        row = {"suite": suite_id, "point": point, "detail": detail}
        if item_id:
            row["item"] = item_id
        result.append(row)

    for suite_path in sorted(suite_dir.glob("*.json")):
        try:
            suite = load(suite_path)
        except (OSError, json.JSONDecodeError) as exc:
            add(suite_path.name, "SUITE_PARSE", str(exc))
            continue

        suite_id = suite.get("suite_id", suite_path.stem)
        for err in _schema_errors(suite, suite_schema):
            add(suite_id, "SUITE_SCHEMA_INVALID", err)
        if any(row["suite"] == suite_id and row["point"] == "SUITE_SCHEMA_INVALID" for row in result):
            continue

        if not _evidence_ref_exists(repo, suite["audit_evidence_ref"]):
            add(suite_id, "MISSING_SUITE_AUDIT_EVIDENCE", suite["audit_evidence_ref"])

        for invariant in suite["representation_invariants"]:
            if not _evidence_ref_exists(repo, invariant["evidence_ref"]):
                add(
                    suite_id,
                    "MISSING_REPRESENTATION_EVIDENCE",
                    f"{invariant['id']}: {invariant['evidence_ref']}",
                )

        geometry = suite["geometry_truth_contract"]
        if not _evidence_ref_exists(repo, geometry["evidence_ref"]):
            add(
                suite_id,
                "MISSING_GEOMETRY_EVIDENCE",
                geometry["evidence_ref"],
            )

        helper_ids: set[str] = set()
        for helper in suite["helper_contracts"]:
            helper_id = helper.get("helper_id", "<missing>")
            for err in _schema_errors(helper, helper_schema):
                add(suite_id, "HELPER_SCHEMA_INVALID", f"{helper_id}: {err}")
            if helper_id in helper_ids:
                add(suite_id, "DUPLICATE_HELPER_CONTRACT", helper_id)
            helper_ids.add(helper_id)
            if helper.get("activation_status") == "AUDITED" and not _evidence_ref_exists(
                repo, helper.get("evidence_ref")
            ):
                add(
                    suite_id,
                    "MISSING_HELPER_AUDIT_EVIDENCE",
                    f"{helper_id}: {helper.get('evidence_ref')}",
                )

        source = suite["diagnostic_source"]
        bank_path = repo / source["locator"]
        if not bank_path.is_file():
            add(suite_id, "MISSING_DIAGNOSTIC_SOURCE", source["locator"])
            continue
        try:
            bank = load_bank(bank_path, source["format"])
        except Exception as exc:
            add(suite_id, "DIAGNOSTIC_SOURCE_PARSE", str(exc))
            continue

        if len(bank) != suite["external_corpus"]["embedded_item_count"]:
            add(
                suite_id,
                "EMBEDDED_ITEM_COUNT_DRIFT",
                f"manifest={suite['external_corpus']['embedded_item_count']} actual={len(bank)}",
            )

        repo_bundle = next(
            (row for row in suite["delivery_artifacts"] if row["profile"] == "REPO_BUNDLE"),
            None,
        )
        repo_bundle_text = ""
        if repo_bundle:
            repo_bundle_path = repo / repo_bundle["locator"]
            if repo_bundle_path.is_file():
                repo_bundle_text = repo_bundle_path.read_text(encoding="utf-8")

        seen_items: set[str] = set()
        for q in bank:
            item = normalize_item(q, suite)
            item_id = str(item.get("item_id") or "<missing>")
            if item_id in seen_items:
                add(suite_id, "DUPLICATE_DIAGNOSTIC_ITEM", item_id, item_id)
            seen_items.add(item_id)

            for err in _schema_errors(item, item_schema):
                add(suite_id, "DIAGNOSTIC_SCHEMA_INVALID", err, item_id)

            if not isinstance(q.get("simBindingRefs"), list):
                add(suite_id, "MISSING_SIM_BINDING_REFS", "simBindingRefs must be an array", item_id)

            fidelity = item["simulation_contract"]["fidelity"]
            if fidelity in {"EXACT", "CONSTRAINT_FAITHFUL"}:
                sim_params = q.get("simParams") or {}
                expected_refs = {f"simParams.{key}" for key in sim_params}
                actual_refs = set(item["simulation_contract"]["binding_refs"])
                if actual_refs != expected_refs:
                    add(
                        suite_id,
                        "ACTIVE_SIM_BINDING_DRIFT",
                        f"simParams={sorted(expected_refs)} binding_refs={sorted(actual_refs)}",
                        item_id,
                    )
                for ref in sorted(actual_refs):
                    key = ref.removeprefix("simParams.")
                    if not ref.startswith("simParams.") or f"p.{key}" not in repo_bundle_text:
                        add(
                            suite_id,
                            "SIM_BINDING_NOT_CONSUMED",
                            f"{ref} is not visibly consumed by the REPO_BUNDLE loader",
                            item_id,
                        )

            if is_generic_final_answer(item["answer_contract"]["final_answer"]):
                add(
                    suite_id,
                    "GENERIC_FINAL_ANSWER",
                    item["answer_contract"]["final_answer"],
                    item_id,
                )

            missing_helpers = sorted(set(item["teaching_contract"]["helpers"]) - helper_ids)
            if missing_helpers:
                add(
                    suite_id,
                    "UNCONTRACTED_HELPER",
                    ", ".join(missing_helpers),
                    item_id,
                )
            if suite["external_corpus"]["coverage_claim"] != "DEMAND_RECONNAISSANCE_ONLY":
                helper_by_id = {row["helper_id"]: row for row in suite["helper_contracts"]}
                unaudited = sorted(
                    helper_id
                    for helper_id in item["teaching_contract"]["helpers"]
                    if helper_id in helper_by_id
                    and helper_by_id[helper_id]["activation_status"] != "AUDITED"
                )
                if unaudited:
                    add(
                        suite_id,
                        "UNAUDITED_HELPER_ACTIVATION",
                        ", ".join(unaudited),
                        item_id,
                    )

        for artifact in suite["delivery_artifacts"]:
            locator = artifact["locator"]
            artifact_path = repo / locator
            if not artifact_path.is_file():
                add(suite_id, "MISSING_DELIVERY_ARTIFACT", locator)
                continue
            text = artifact_path.read_text(encoding="utf-8")
            actual_remote = _external_dependencies(text)
            declared_remote = set(artifact["remote_dependencies_declared"])
            if actual_remote != declared_remote:
                add(
                    suite_id,
                    "REMOTE_DEPENDENCY_DRIFT",
                    f"{locator}: declared={sorted(declared_remote)} actual={sorted(actual_remote)}",
                )

            if artifact["profile"] in {"SINGLE_FILE_ONLINE", "SINGLE_FILE_OFFLINE"}:
                local_dependencies = _local_resource_dependencies(text)
                if local_dependencies:
                    add(
                        suite_id,
                        "SINGLE_FILE_LOCAL_DEPENDENCY",
                        f"{locator}: {local_dependencies}",
                    )
                try:
                    embedded = load_bank(artifact_path, "WINDOW_JEE_QUESTIONS_DATA_JS")
                except Exception as exc:
                    add(suite_id, "SINGLE_FILE_BANK_MISSING", f"{locator}: {exc}")
                else:
                    if embedded != bank:
                        add(suite_id, "SINGLE_FILE_BANK_DRIFT", locator)

            if artifact["profile"] == "SINGLE_FILE_OFFLINE" and actual_remote:
                add(
                    suite_id,
                    "OFFLINE_PROFILE_HAS_REMOTE_DEPENDENCIES",
                    f"{locator}: {sorted(actual_remote)}",
                )

    return result


def audit(repo: Path = REPO) -> dict:
    rows = findings(repo)
    return {
        "schemas": [
            str(SUITE_SCHEMA.relative_to(REPO)),
            str(ITEM_SCHEMA.relative_to(REPO)),
            str(HELPER_SCHEMA.relative_to(REPO)),
        ],
        "suite_directory": str(SUITES.relative_to(REPO)),
        "findings": rows,
        "passed": not rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
