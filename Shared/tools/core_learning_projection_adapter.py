"""Adapt compiler output plus canonical records to the learner CoreProjection envelope.

This module is a provider-side adapter. It does not own academic truth: concepts,
questions, representations, reveal stages and explorer locators are read from the
same canonical records the compiler consumed. Browser/runtime code receives only
the resulting explicit projection rows.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

CORE_ORDER = ("CORE1A", "CORE1B", "CORE2A", "CORE2B")


class CoreLearningProjectionAdapterError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise CoreLearningProjectionAdapterError(f"{code}: {detail}" if detail else code)


def _products(compiled: dict) -> dict[str, dict]:
    return {row["core"]: row for row in (compiled.get("plan") or {}).get("products", [])}


def _question_blocks(product: dict | None) -> list[dict]:
    if not product:
        return []
    return [
        block
        for unit in product.get("units", [])
        for block in unit.get("blocks", [])
        if block.get("kind") == "QUESTION"
    ]


def _initial_stage(records: dict, representation_ref: str | None) -> str | None:
    if not representation_ref:
        return None
    rep = records.get(representation_ref) or {}
    for row in rep.get("support_stage_map") or []:
        if row.get("support_level") == "low":
            return row.get("visual_stage_ref")
    stages = rep.get("reveal_stages") or []
    return stages[0].get("id") if stages else None


def _explorer_locator(records: dict, representation_ref: str | None) -> str | None:
    if not representation_ref:
        return None
    rep = records.get(representation_ref) or {}
    for ref in rep.get("interactive_resource_refs") or []:
        resource = records.get(ref) or {}
        locator = resource.get("locator")
        if isinstance(locator, str) and locator:
            return locator
    return None


def _concept(records: dict, microtopic_ref: str, *, eliciting: bool) -> dict:
    row = records[microtopic_ref]
    elicitation = row.get("elicitation") or {}
    predict = elicitation.get("predict") or {}
    return {
        "microtopic_ref": row["id"],
        "inferential_jump": row["inferential_jump"],
        "teaching_path": deepcopy(row.get("teaching_path") or []),
        "elicitation": (
            {"prompt": predict["prompt"]}
            if eliciting and isinstance(predict.get("prompt"), str) and predict["prompt"]
            else None
        ),
        "misconceptions": deepcopy(row.get("misconceptions") or []),
        "representation_refs": list(row.get("representation_refs") or []),
    }


def _first_route_representation(block: dict) -> str | None:
    for move in (block.get("answer") or {}).get("reasoning_route") or []:
        ref = move.get("representation_ref")
        if isinstance(ref, str) and ref:
            return ref
    return None


def _application(block: dict) -> dict:
    answer = block.get("answer") or {}
    return {
        "question_ref": block["source_question_id"],
        "family_ref": block["family"],
        "stem": block["stem"],
        "reasoning_route": deepcopy(answer.get("reasoning_route") or []),
        "crux_move_ref": answer.get("crux_move_ref"),
        "hints": deepcopy(block.get("hints") or []),
        "scaffolds": deepcopy(block.get("scaffolds") or []),
        "transfer": deepcopy(block.get("transfer")) if block.get("transfer") else None,
        "check": answer.get("check") or "",
    }


def _row_id(subject: str, source_ref: str, core: str) -> str:
    safe_subject = subject.lower().replace(" ", "-")
    return f"{safe_subject}:{source_ref.lower()}:{core.lower()}"


def _projection(
    *,
    core: str,
    concept: dict,
    application: dict | None,
    records: dict,
    initial_representation_ref: str | None,
) -> dict:
    transfer = (application or {}).get("transfer") or {}
    protected = transfer.get("protected_move_ref")
    return {
        "contract_version": "1.0",
        "core": core,
        "concept": deepcopy(concept),
        "application": deepcopy(application),
        "presentation": {
            "attempt_before_reveal": core in {"CORE1B", "CORE2B"},
            "show_full_construction": core == "CORE1A",
            "initial_visual_ref": initial_representation_ref,
            "initial_visual_stage_ref": _initial_stage(records, initial_representation_ref),
            "protected_move_refs": [protected] if protected else [],
        },
    }


def _candidate_pairs(compiled: dict) -> list[tuple[dict, dict]]:
    products = _products(compiled)
    familiar = [
        row for row in _question_blocks(products.get("CORE2A"))
        if (row.get("answer") or {}).get("reasoning_route")
        and (row.get("answer") or {}).get("crux_move_ref")
    ]
    transfers = [
        row for row in _question_blocks(products.get("CORE2B"))
        if (row.get("transfer") or {}).get("protected_move_ref")
        and (row.get("answer") or {}).get("reasoning_route")
    ]
    pairs = []
    for transfer in transfers:
        builds_on = set((transfer.get("transfer") or {}).get("builds_on") or [])
        for base in familiar:
            if (
                base.get("source_question_id") in builds_on
                and base.get("family") == transfer.get("family")
            ):
                pairs.append((base, transfer))
    return pairs


def _concept_for_pair(compiled: dict, records: dict, familiar: dict) -> str | None:
    rep_ref = _first_route_representation(familiar)
    candidates = []
    for ref in (compiled.get("derived_from") or {}).get("microtopics") or []:
        row = records.get(ref) or {}
        if (
            rep_ref in (row.get("representation_refs") or [])
            and row.get("elicitation")
            and _explorer_locator(records, rep_ref)
        ):
            candidates.append(ref)
    return candidates[0] if candidates else None


def adapt_compiled_bucket(compiled: dict, records: dict, *, subject: str) -> list[dict]:
    """Return production learner rows for compiler-backed parent/transfer pairs."""
    products = _products(compiled)
    if not all(core in products for core in CORE_ORDER):
        return []

    rows: list[dict[str, Any]] = []
    for familiar, transfer in _candidate_pairs(compiled):
        microtopic_ref = _concept_for_pair(compiled, records, familiar)
        if not microtopic_ref:
            continue
        concept_a = _concept(records, microtopic_ref, eliciting=False)
        concept_b = _concept(records, microtopic_ref, eliciting=True)
        concept_rep = (concept_a.get("representation_refs") or [None])[0]

        pair_rows = [
            ("CORE1A", microtopic_ref, concept_a, None, concept_rep),
            ("CORE1B", microtopic_ref, concept_b, None, concept_rep),
            (
                "CORE2A",
                familiar["source_question_id"],
                concept_a,
                _application(familiar),
                _first_route_representation(familiar) or concept_rep,
            ),
            (
                "CORE2B",
                transfer["source_question_id"],
                concept_a,
                _application(transfer),
                _first_route_representation(transfer) or concept_rep,
            ),
        ]
        for core, source_ref, concept, application, initial_rep in pair_rows:
            locator = _explorer_locator(records, initial_rep)
            projection = _projection(
                core=core,
                concept=concept,
                application=application,
                records=records,
                initial_representation_ref=initial_rep,
            )
            rows.append({
                "id": _row_id(subject, source_ref, core),
                "subject": subject,
                "source_ref": source_ref,
                "projection": projection,
                "scene_ref": None,
                "adapter_ref": None,
                "injection_refs": [],
                "explorer_locator": locator,
            })

    unique = {}
    for row in rows:
        unique[row["id"]] = row
    return sorted(
        unique.values(),
        key=lambda row: (
            row["subject"],
            row["source_ref"],
            CORE_ORDER.index(row["projection"]["core"]),
        ),
    )
