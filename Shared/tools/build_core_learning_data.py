#!/usr/bin/env python3
"""Generate learner CoreProjection rows from canonical compiler output."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.contracts import ContractError
from Shared.library.compile_inputs import compile_bucket
from Shared.library.resolve import build_index, load_packages
from Shared.tools.core_learning_projection_adapter import adapt_compiled_bucket_with_status

OUT = REPO / "public" / "core-learning" / "data.js"


def subjects() -> list[str]:
    return sorted(p.parent.parent.name for p in REPO.glob("*/adapter/CoreContracts.json"))


def _subject_rows(subject: str) -> tuple[list[dict], list[dict]]:
    paths = sorted((REPO / subject / "library").glob("*.json"))
    if not paths:
        return [], []
    records = build_index(load_packages(paths))
    bucket_ids = sorted(
        row["id"]
        for row in records.values()
        if isinstance(row, dict) and row.get("_collection") == "buckets"
    )
    rows = []
    availability = []
    for bucket_id in bucket_ids:
        try:
            compiled = compile_bucket(
                records,
                bucket_id,
                topic_id=bucket_id,
                title=records[bucket_id]["title"],
                subject=subject,
                practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
            )
        except ContractError as exc:
            availability.append({
                "subject": subject,
                "bucket_ref": bucket_id,
                "status": "UNSUPPORTED",
                "code": exc.code,
                "detail": exc.detail,
                "projection_refs": [],
            })
            continue
        bucket_rows, findings = adapt_compiled_bucket_with_status(compiled, records, subject=subject)
        rows.extend(bucket_rows)
        first = findings[0] if findings else None
        availability.append({
            "subject": subject,
            "bucket_ref": bucket_id,
            "status": "AVAILABLE" if bucket_rows else "UNSUPPORTED",
            "code": first["code"] if first else None,
            "detail": first["detail"] if first else None,
            "findings": findings,
            "projection_refs": [row["id"] for row in bucket_rows],
        })
    return rows, availability


def build() -> dict:
    rows = []
    availability = []
    for subject in subjects():
        subject_rows, subject_availability = _subject_rows(subject)
        rows.extend(subject_rows)
        availability.extend(subject_availability)
    rows.sort(key=lambda row: row["id"])
    availability.sort(key=lambda row: (row["subject"], row["bucket_ref"]))
    return {
        "generated_by": "Shared/tools/build_core_learning_data.py",
        "provider_status": "PRODUCTION_COMPILED_CANONICAL",
        "provider": {
            "mode": "CANONICAL_LIBRARY_TO_COMPILE_BUCKET_TO_CORE_PROJECTION",
            "contract_version": "1.1",
        },
        "core_projections": rows,
        "bucket_availability": availability,
        "findings": [
            {
                "subject": row["subject"],
                "bucket_ref": row["bucket_ref"],
                **finding,
            }
            for row in availability
            for finding in row.get("findings", [])
        ],
    }



def build_public() -> dict:
    """Fail closed for distributable Core data absent academic release receipts.

    build() remains the complete canonical compiler preview for internal
    integration and derived production memory. Nothing currently supplies an
    independently verified Core public-release grant. No preview identities,
    findings or applications may be serialized into public/data.js.
    Changing this gate requires an independently reviewed, source-bound grant
    protocol, not a status string or an old orientation inventory.
    """
    return {
        "generated_by": "Shared/tools/build_core_learning_data.py",
        "provider_status": "PUBLICATION_HELD",
        "provider": {
            "mode": "PUBLIC_RELEASE_GATE_NO_GRANTS",
            "contract_version": "1.1",
        },
        "publication_gate": {
            "status": "HOLD",
            "code": "NO_INDEPENDENT_CORE_PUBLICATION_GRANT",
            "authority": "NOT_GRANTED_BY_ANY_MACHINE_CHECK",
        },
        "core_projections": [],
        "bucket_availability": [],
        "findings": [],
    }


def preflight_projection(
    *,
    subject: str,
    core: str,
    target_refs: list[str],
    payload: dict | None = None,
) -> dict:
    """Let the canonical Core provider decide whether an exact projection already exists.

    The web resolver must not infer Core sufficiency from individual academic fields.
    This provider eagerly compiles every currently buildable projection, so absence here
    is reported as a named provider hold rather than guessed DERIVABLE by a consumer.
    """
    payload = payload or build()
    refs = {ref for ref in target_refs if isinstance(ref, str) and ref}
    rows = [
        row for row in payload.get("core_projections", [])
        if row.get("subject") == subject
        and (row.get("projection") or {}).get("core") == core
    ]

    def semantic_refs(row: dict) -> set[str]:
        projection = row.get("projection") or {}
        orientation = projection.get("orientation") or {}
        concept = projection.get("concept") or {}
        application = projection.get("application") or {}
        return {
            value for value in (
                row.get("id"),
                row.get("source_ref"),
                orientation.get("bucket_ref"),
                concept.get("microtopic_ref"),
                application.get("question_ref"),
            )
            if isinstance(value, str) and value
        }

    matches = [
        row for row in rows
        if refs.intersection(semantic_refs(row))
    ]
    if len(matches) == 1:
        return {
            "status": "READY_EXISTING",
            "projection_ref": matches[0]["id"],
            "projection": matches[0],
            "code": None,
            "detail": "Exact canonical provider projection is available.",
        }
    if len(matches) > 1:
        return {
            "status": "UNSUPPORTED",
            "projection_ref": None,
            "projection": None,
            "code": "CORE_PROVIDER_TARGET_AMBIGUOUS",
            "detail": "More than one projection matches the supplied semantic target refs.",
        }

    if core == "CORE2":
        code = "SOURCE_CUSTODY_HOLD"
        detail = "No compiler-emitted source-custody projection matches this target."
    else:
        code = "ACADEMIC_INPUT_MISSING"
        detail = "The canonical Core provider cannot currently compile this requested Core/target pair."
    return {
        "status": code,
        "projection_ref": None,
        "projection": None,
        "code": code,
        "detail": detail,
    }

def render(payload: dict) -> str:
    # This is the distributable JavaScript serializer, not an internal
    # preview serializer. No publication grant exists yet: reject any
    # payload beyond the exact fail-closed public envelope.
    if payload != build_public():
        raise ValueError("CORE_PUBLICATION_HOLD: independently verified release grant required")
    return (
        "// Generated by Shared/tools/build_core_learning_data.py -- do not edit by hand.\n"
        "window.GRADE9V3_CORE = "
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + ";\n"
    )


def rendered_file() -> dict[str, bytes]:
    return {OUT.relative_to(REPO).as_posix(): render(build_public()).encode("utf-8")}


def write() -> dict:
    # Fail closed *before* attempting potentially failing internal compilation.
    # Otherwise a compiler error can leave a previous, preview-bearing public
    # data.js in place. Pages mirroring separately rejects stale public bytes.
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(build_public()), encoding="utf-8", newline="\n")
    payload = build()
    # Persist current Core projections as derived production memory. The import is
    # local to avoid a module cycle: the registry reads build(), never write().
    from Shared.tools import derived_artifact_registry
    derived_artifact_registry.write()
    return payload


def main() -> int:
    payload = write()
    print(
        f"wrote {OUT.relative_to(REPO)}: "
        f"{len(payload['core_projections'])} internal preview projection(s); "
        "public release gate: HOLD (0 public projections)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
