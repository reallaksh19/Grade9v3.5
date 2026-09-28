#!/usr/bin/env python3
"""Project canonical learner-facing metadata without creating a second academic authority.

This module only resolves and validates values that already live in canonical package or exam-bank
records. It emits a learner-safe semantic projection consumed by delivery surfaces; it never infers
academic metadata from Core role, raw ids, stem wording, option shape, HTML or CSS.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
VOCABULARY = REPO / "Shared/vocabularies/learner-question-metadata.v1.json"
CONCEPT_ROLES = {"CORE1", "CORE1A", "CORE1B"}
ASSESSMENT_ROLES = {"CORE2", "CORE2A", "CORE2B"}
DIFFICULTY_COMPONENTS = {
    "concept_model_selection",
    "representation_translation",
    "reasoning_chain_length",
    "algebra_computational_load",
    "trap_exception_sensitivity",
}


class LearnerMetadataError(ValueError):
    """Canonical metadata cannot be projected without guessing or contradicting authority."""


def load_vocabulary(path: Path = VOCABULARY) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _one(rows: list[dict], missing: str, ambiguous: str) -> dict:
    if not rows:
        raise LearnerMetadataError(missing)
    if len(rows) != 1:
        raise LearnerMetadataError(ambiguous)
    return rows[0]


def _package_subject(packages: list[dict]) -> str:
    subjects = {p.get("subject") for p in packages if p.get("subject")}
    if len(subjects) != 1:
        raise LearnerMetadataError("METADATA_SUBJECT_AMBIGUOUS")
    return next(iter(subjects))


def resolve_concept(packages: list[dict], capability_ref: str, vocabulary: dict[str, Any] | None = None) -> dict:
    vocabulary = vocabulary or load_vocabulary()
    owners = [
        m
        for package in packages
        for m in package.get("microtopics", [])
        if m.get("primary_capability_ref") == capability_ref
    ]
    microtopic = _one(
        owners,
        f"METADATA_CONCEPT_OWNER_MISSING: {capability_ref}",
        f"METADATA_CONCEPT_OWNER_AMBIGUOUS: {capability_ref}",
    )
    title = microtopic.get("title")
    if not isinstance(title, str) or not title.strip():
        raise LearnerMetadataError(f"METADATA_CONCEPT_TITLE_MISSING: {microtopic.get('id')}")

    badge = microtopic.get("intrinsic_badge")
    labels = vocabulary["concept_difficulty"]
    if badge not in labels:
        raise LearnerMetadataError(f"METADATA_CONCEPT_DIFFICULTY_INVALID: {microtopic['id']}:{badge}")
    reason = microtopic.get("badge_reason")
    if not isinstance(reason, str) or not reason.strip():
        raise LearnerMetadataError(f"METADATA_CONCEPT_DIFFICULTY_REASON_MISSING: {microtopic['id']}")

    bucket_ref = microtopic.get("bucket_id")
    buckets = [
        b
        for package in packages
        for b in package.get("buckets", [])
        if b.get("id") == bucket_ref
    ]
    bucket = _one(
        buckets,
        f"METADATA_TOPIC_MISSING: {bucket_ref}",
        f"METADATA_TOPIC_AMBIGUOUS: {bucket_ref}",
    )
    topic = bucket.get("topic") or bucket.get("title")
    if not isinstance(topic, str) or not topic.strip():
        raise LearnerMetadataError(f"METADATA_TOPIC_LABEL_MISSING: {bucket_ref}")

    return {
        "subject": _package_subject(packages),
        "topic_ref": bucket_ref,
        "topic": topic,
        "concept_ref": microtopic["id"],
        "concept": title,
        "concept_difficulty": badge,
        "concept_difficulty_label": labels[badge],
        "concept_difficulty_reason": reason,
    }


def resolve_family(packages: list[dict], family_ref: str) -> dict:
    rows = [
        family
        for package in packages
        for family in package.get("question_families", [])
        if family.get("id") == family_ref
    ]
    family = _one(
        rows,
        f"METADATA_FAMILY_MISSING: {family_ref}",
        f"METADATA_FAMILY_AMBIGUOUS: {family_ref}",
    )
    title = family.get("title")
    if not isinstance(title, str) or not title.strip():
        raise LearnerMetadataError(f"METADATA_FAMILY_TITLE_MISSING: {family_ref}")
    return {"family_ref": family_ref, "family": title}


def _difficulty(value: Any, record_id: str, vocabulary: dict[str, Any]) -> dict:
    if not isinstance(value, dict):
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_MISSING: {record_id}")
    band = value.get("band")
    if band not in vocabulary["question_difficulty"]:
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_INVALID: {record_id}:{band}")
    ranges = vocabulary.get("question_difficulty_score_ranges") or {}
    score_range = ranges.get(band)
    if not isinstance(score_range, dict):
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_RANGE_MISSING: {record_id}:{band}")
    components = value.get("components")
    if not isinstance(components, dict) or set(components) != DIFFICULTY_COMPONENTS:
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_COMPONENTS_INVALID: {record_id}")
    if any(not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 2 for v in components.values()):
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_COMPONENTS_INVALID: {record_id}")
    score = value.get("score")
    if not isinstance(score, int) or isinstance(score, bool) or score != sum(components.values()):
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_SCORE_INVALID: {record_id}")
    if not score_range["min"] <= score <= score_range["max"]:
        raise LearnerMetadataError(
            f"METADATA_QUESTION_DIFFICULTY_BAND_SCORE_MISMATCH: {record_id}:{band}:{score}"
        )
    basis = value.get("basis")
    if not isinstance(basis, str) or not basis.strip():
        raise LearnerMetadataError(f"METADATA_QUESTION_DIFFICULTY_BASIS_MISSING: {record_id}")
    return {
        "question_difficulty": band,
        "question_difficulty_label": vocabulary["question_difficulty"][band],
        "question_difficulty_score": score,
    }


def _question_type(value: Any, record_id: str, vocabulary: dict[str, Any]) -> dict:
    if value not in vocabulary["question_types"]:
        code = "MISSING" if value in (None, "") else "INVALID"
        raise LearnerMetadataError(f"METADATA_QUESTION_TYPE_{code}: {record_id}:{value}")
    return {
        "question_type": value,
        "question_type_label": vocabulary["question_types"][value],
    }


def _bank_question_metadata(question: dict, vocabulary: dict[str, Any]) -> dict:
    extensions = question.get("extensions") or {}
    analysis = extensions.get("grade9v3:analysis") or {}
    custody = extensions.get("grade9v3:source_custody") or {}
    provenance = extensions.get("grade9v3:provenance_class")
    if provenance not in vocabulary["provenance"]:
        raise LearnerMetadataError(f"METADATA_PROVENANCE_INVALID: {question['id']}:{provenance}")
    source_status = custody.get("source_status")
    if provenance in {"PYQ_VERIFIED", "PYQ_ADAPTED"} and not (
        isinstance(source_status, str) and source_status.startswith("PYQ_VERIFIED")
    ):
        raise LearnerMetadataError(
            f"METADATA_PROVENANCE_SOURCE_CONTRADICTION: {question['id']}:{provenance}:{source_status}"
        )
    source = analysis.get("exam_source_badge")
    if not isinstance(source, str) or not source.strip():
        raise LearnerMetadataError(f"METADATA_SOURCE_LABEL_MISSING: {question['id']}")
    return {
        **_difficulty(analysis.get("difficulty"), question["id"], vocabulary),
        **_question_type(analysis.get("learner_question_type"), question["id"], vocabulary),
        "source": source,
        "provenance": provenance,
        "provenance_label": vocabulary["provenance"][provenance],
    }


def _authored_question_metadata(question: dict, vocabulary: dict[str, Any]) -> dict:
    extensions = question.get("extensions") or {}
    external_claim = extensions.get("grade9v3:provenance_class")
    if external_claim in {"PYQ_VERIFIED", "PYQ_ADAPTED"}:
        raise LearnerMetadataError(
            f"METADATA_AUTHORED_EXTERNAL_PROVENANCE: {question['id']}:{external_claim}"
        )
    provenance = question.get("origin")
    if provenance not in {"AUTHORED", "ADAPTED", "ORIGINAL"}:
        raise LearnerMetadataError(f"METADATA_PROVENANCE_INVALID: {question['id']}:{provenance}")
    return {
        **_difficulty(question.get("difficulty"), question["id"], vocabulary),
        **_question_type(question.get("learner_question_type"), question["id"], vocabulary),
        "provenance": provenance,
        "provenance_label": vocabulary["provenance"][provenance],
    }


def project(role: str, record: dict, packages: list[dict], vocabulary: dict[str, Any] | None = None) -> dict:
    """Return the safe semantic metadata projection for one rendered Core unit."""
    if role not in CONCEPT_ROLES | ASSESSMENT_ROLES:
        raise LearnerMetadataError(f"METADATA_ROLE_INVALID: {role}")
    vocabulary = vocabulary or load_vocabulary()
    concept = resolve_concept(packages, record.get("primary_capability_ref"), vocabulary)
    items = [
        {"kind": "subject", "ref": concept["subject"], "value": concept["subject"], "label": concept["subject"]},
        {"kind": "topic", "ref": concept["topic_ref"], "value": concept["topic"], "label": concept["topic"]},
        {"kind": "concept", "ref": concept["concept_ref"], "value": concept["concept"], "label": concept["concept"]},
        {
            "kind": "concept-difficulty",
            "ref": concept["concept_ref"],
            "value": concept["concept_difficulty"],
            "label": concept["concept_difficulty_label"],
        },
    ]

    out = {
        "role": role,
        "record_ref": record["id"],
        "subject": concept["subject"],
        "topic_ref": concept["topic_ref"],
        "topic": concept["topic"],
        "concept": concept,
        "field_labels": vocabulary["field_labels"],
        "items": items,
    }
    if role in CONCEPT_ROLES:
        return out

    family = resolve_family(packages, record.get("family_ref"))
    metadata = (
        _bank_question_metadata(record, vocabulary)
        if role == "CORE2"
        else _authored_question_metadata(record, vocabulary)
    )
    items.extend([
        {
            "kind": "question-difficulty",
            "ref": record["id"],
            "value": metadata["question_difficulty"],
            "label": metadata["question_difficulty_label"],
        },
        {
            "kind": "family",
            "ref": family["family_ref"],
            "value": family["family"],
            "label": family["family"],
        },
        {
            "kind": "question-type",
            "ref": record["id"],
            "value": metadata["question_type"],
            "label": metadata["question_type_label"],
        },
    ])
    if role == "CORE2":
        items.extend([
            {
                "kind": "source",
                "ref": record["id"],
                "value": metadata["source"],
                "label": metadata["source"],
            },
            {
                "kind": "provenance",
                "ref": record["id"],
                "value": metadata["provenance"],
                "label": metadata["provenance_label"],
            },
        ])
    else:
        items.append({
            "kind": "provenance",
            "ref": record["id"],
            "value": metadata["provenance"],
            "label": metadata["provenance_label"],
        })

    if role == "CORE2B":
        transfer = record.get("transfer") or {}
        dimension = transfer.get("dimension")
        if dimension not in vocabulary["transfer_dimension"]:
            raise LearnerMetadataError(
                f"METADATA_TRANSFER_DIMENSION_INVALID: {record['id']}:{dimension}"
            )
        items.append({
            "kind": "transfer-dimension",
            "ref": record["id"],
            "value": dimension,
            "label": vocabulary["transfer_dimension"][dimension],
        })

    out.update({"family": family, **metadata})
    return out


def safe_search_text(projection: dict, record: dict, role: str) -> str:
    """Return only metadata and question text that are safe before commitment.

    Protected answer summaries, reasoning routes, hints, failure signals, repair payloads and
    transfer changed-demand statements are never part of this corpus.
    """
    parts = [item.get("label", "") for item in projection.get("items", [])]
    if role in ASSESSMENT_ROLES:
        parts.append(record.get("stem", ""))
        parts.extend(record.get("conditions") or [])
        parts.extend(record.get("options") or [])
    else:
        parts.append((projection.get("concept") or {}).get("concept", ""))
    return " ".join(str(value).strip() for value in parts if str(value).strip())


def audit_manifest(manifest_path: Path) -> dict:
    """Report metadata coverage for one product without changing product acceptance state."""
    from Shared.tools import product_manifest  # local import avoids a projection/selection cycle

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packages = [json.loads((REPO / ref).read_text(encoding="utf-8")) for ref in manifest["package_refs"]]
    bank_questions = [
        question
        for ref in manifest.get("bank_refs", [])
        for question in json.loads((REPO / ref).read_text(encoding="utf-8")).get("questions", [])
    ]
    selection = manifest.get("selection") or {}
    selected_counts = {
        "microtopics": len(selection.get("microtopics") or []),
        "core2": len(selection.get("core2") or []),
        "core2a": len(selection.get("core2a") or []),
        "core2b": len(selection.get("core2b") or []),
    }
    assessment_total = selected_counts["core2"] + selected_counts["core2a"] + selected_counts["core2b"]
    unit_total = selected_counts["microtopics"] + assessment_total
    denominators = {
        "concept": unit_total,
        "concept-difficulty": unit_total,
        "question-difficulty": assessment_total,
        "family": assessment_total,
        "question-type": assessment_total,
        "source": selected_counts["core2"],
        "provenance": assessment_total,
        "transfer-dimension": selected_counts["core2b"],
    }
    resolved_counts = {kind: 0 for kind in denominators}
    findings: list[dict] = []
    try:
        resolved = product_manifest.validate_selection(manifest, packages, bank_questions)
    except product_manifest.ProductSelectionError as exc:
        findings.append({"code": "METADATA_SELECTION_INVALID", "detail": str(exc)})
        return {
            "schema": "learner-metadata-audit/v1",
            "product_id": manifest.get("product_id"),
            "selection": selected_counts,
            "coverage": {
                kind: {"resolved": 0, "selected": selected}
                for kind, selected in denominators.items()
            },
            "findings": findings,
        }

    tasks = [
        *[("CORE1", row) for row in resolved["microtopics"]],
        *[("CORE2", row) for row in resolved["core2"]],
        *[("CORE2A", row) for row in resolved["core2a"]],
        *[("CORE2B", row) for row in resolved["core2b"]],
    ]
    for role, record in tasks:
        try:
            projected = project(role, record, packages)
        except LearnerMetadataError as exc:
            findings.append({
                "code": str(exc).split(":", 1)[0],
                "role": role,
                "record": record.get("id"),
                "detail": str(exc),
            })
            continue
        kinds = {item["kind"] for item in projected["items"]}
        for kind in resolved_counts:
            if kind in kinds:
                resolved_counts[kind] += 1

    return {
        "schema": "learner-metadata-audit/v1",
        "product_id": manifest.get("product_id"),
        "selection": selected_counts,
        "coverage": {
            kind: {"resolved": resolved_counts[kind], "selected": selected}
            for kind, selected in denominators.items()
        },
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Read-only learner metadata coverage audit.")
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    print(json.dumps(audit_manifest(args.manifest), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
