"""Adapt compiler output plus canonical records to the learner CoreProjection envelope.

This module is a provider-side adapter. It does not own academic truth: concepts,
questions, representations, reveal stages and explorer locators are read from the
same canonical records the compiler consumed. Browser/runtime code receives only
the resulting explicit projection rows.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

try:
    from Shared.tools import core_template_contract
except ModuleNotFoundError:  # direct script execution from Shared/tools
    import core_template_contract

CORE_ORDER = ("CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B")


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


def _worked_anchors(records: dict, microtopic: dict) -> list[dict]:
    families = {
        ref for ref in (microtopic.get("question_family_refs") or [])
        if isinstance(ref, str) and ref
    }
    rows = []
    for record in records.values():
        if not isinstance(record, dict):
            continue
        family = record.get("family_ref") or record.get("family")
        if family not in families:
            continue
        if not any(
            isinstance(exposure, dict) and exposure.get("core") == "CORE1A"
            for exposure in (record.get("exposure") or [])
        ):
            continue
        answer = record.get("answer") or {}
        reasoning = answer.get("reasoning") or []
        if not isinstance(reasoning, list) or not reasoning:
            continue
        rows.append({
            "question_ref": record.get("id"),
            "stem": record.get("stem"),
            "figure_refs": list(record.get("figure_refs") or []),
            "answer": {
                "summary": answer.get("summary") or "",
                "reasoning": deepcopy(reasoning),
                "check": answer.get("check") or "",
            },
        })
    return sorted(rows, key=lambda row: row.get("question_ref") or "")


def _concept_representations(records: dict, microtopic: dict, *, core: str) -> list[dict]:
    result = []
    for ref in microtopic.get("representation_refs") or []:
        if not isinstance(ref, str) or not ref:
            continue
        representation = records.get(ref)
        if not isinstance(representation, dict):
            continue
        scenes = [
            deepcopy(scene)
            for scene in (representation.get("scene_instances") or [])
            if isinstance(scene, dict)
            and scene.get("microtopic_ref") == microtopic.get("id")
            and core in (scene.get("cores") or [])
        ]
        result.append({
            "representation_ref": ref,
            "correspondence": deepcopy(representation.get("correspondence") or []),
            "scenes": scenes,
        })
    return result


def _concept(records: dict, microtopic_ref: str, *, core: str) -> dict:
    row = records[microtopic_ref]
    relation_checks = []
    for ref in row.get("relation_refs") or []:
        relation = records.get(ref) or {}
        for check in relation.get("checks") or []:
            if isinstance(check, str) and check not in relation_checks:
                relation_checks.append(check)
    return {
        "microtopic_ref": row["id"],
        "title": row.get("title"),
        "intrinsic_badge": row.get("intrinsic_badge"),
        "inferential_jump": row["inferential_jump"],
        "entry_assumptions": list(row.get("entry_assumptions") or []),
        "teaching_path": deepcopy(row.get("teaching_path") or []),
        "elicitation": deepcopy(row.get("elicitation")) if core == "CORE1B" else None,
        "misconceptions": deepcopy(row.get("misconceptions") or []),
        "representation_refs": list(row.get("representation_refs") or []),
        "representations": _concept_representations(records, row, core=core),
        "relation_checks": relation_checks,
        "exit_task": deepcopy(row.get("exit_task") or {}),
        "worked_anchors": _worked_anchors(records, row) if core == "CORE1A" else [],
    }


def _study_refs(compiled: dict, records: dict, core: str) -> list[str]:
    refs = []
    for obligation in (compiled.get("baseline") or {}).get("obligations") or []:
        if core not in (obligation.get("required_cores") or []):
            continue
        obligation_id = obligation.get("id")
        if not isinstance(obligation_id, str) or not obligation_id.startswith("OB-"):
            continue
        ref = obligation_id[3:]
        row = records.get(ref)
        if isinstance(row, dict) and row.get("_collection") == "microtopics":
            refs.append(ref)
    return sorted(set(refs))


def _orientation(product: dict, compiled: dict) -> dict:
    units = product.get("units") or []
    _require(bool(units), "CORE1_ORIENTATION_UNIT_MISSING")
    unit = units[0]
    blocks = []
    for block in unit.get("blocks") or []:
        kind = block.get("kind")
        if kind not in {"TEXT", "EQUATION", "FIGURE"}:
            continue
        payload = {
            "id": block.get("id"),
            "kind": kind,
        }
        for field in (
            "text",
            "mathml",
            "meaning",
            "symbols",
            "conditions",
            "correspondence",
            "scene",
        ):
            if field in block:
                payload[field] = deepcopy(block[field])
        blocks.append(payload)
    _require(bool(blocks), "CORE1_ORIENTATION_BLOCKS_MISSING")
    return {
        "bucket_ref": (compiled.get("derived_from") or {}).get("bucket"),
        "title": unit.get("title") or (compiled.get("plan") or {}).get("title"),
        "blocks": blocks,
    }


def _first_route_representation(block: dict) -> str | None:
    for move in (block.get("answer") or {}).get("reasoning_route") or []:
        ref = move.get("representation_ref")
        if isinstance(ref, str) and ref:
            return ref
    return None


def _figure_payload(records: dict | None, figure_refs: list[str]) -> list[dict]:
    if records is None:
        return []
    figures = []
    for ref in figure_refs:
        row = records.get(ref)
        _require(isinstance(row, dict), "QUESTION_FIGURE_REF_UNRESOLVED", ref)
        scenes = row.get("scene_instances") or []
        captions = [
            scene.get("scene", {}).get("caption")
            for scene in scenes
            if isinstance(scene, dict)
            and isinstance(scene.get("scene"), dict)
            and isinstance(scene["scene"].get("caption"), str)
            and scene["scene"]["caption"].strip()
        ]
        caption = row.get("caption") or (captions[0] if captions else None)
        purpose = row.get("purpose")
        read_order = list(row.get("read_order") or [])
        accessibility = list(row.get("accessibility") or [])
        _require(
            bool(caption or purpose or read_order or accessibility),
            "QUESTION_FIGURE_SEMANTIC_DESCRIPTION_MISSING",
            ref,
        )
        figures.append({
            "figure_ref": ref,
            "kind": row.get("kind"),
            "caption": caption,
            "purpose": purpose,
            "read_order": read_order,
            "accessibility": accessibility,
        })
    return figures


def _repair_payload(records: dict | None, repair_ref: str | None) -> dict | None:
    if not repair_ref:
        return None
    if records is None:
        return {"step_ref": repair_ref}
    for row in records.values():
        if not isinstance(row, dict) or row.get("_collection") != "microtopics":
            continue
        for step in row.get("teaching_path") or []:
            if isinstance(step, dict) and step.get("id") == repair_ref:
                return {
                    "step_ref": repair_ref,
                    "microtopic_ref": row.get("id"),
                    "action": step.get("action"),
                    "why_valid": step.get("why_valid"),
                    "output": step.get("output"),
                }
    raise CoreLearningProjectionAdapterError(
        f"REPAIR_ROUTE_UNRESOLVED: {repair_ref}"
    )


def _application(block: dict, records: dict | None = None) -> dict:
    answer = block.get("answer") or {}
    figure_refs = list(block.get("figure_refs") or [])
    return {
        "question_ref": block["source_question_id"],
        "family_ref": block["family"],
        "stem": block["stem"],
        "source_refs": list(block.get("source_refs") or []),
        "origin": block.get("origin"),
        "original_number": block.get("original_number"),
        "subparts": deepcopy(block.get("subparts") or []),
        "options": deepcopy(block.get("options") or []),
        "conditions": deepcopy(block.get("conditions") or []),
        "figure_refs": figure_refs,
        "figures": _figure_payload(records, figure_refs),
        "reasoning_route": deepcopy(answer.get("reasoning_route") or []),
        "crux_move_ref": answer.get("crux_move_ref"),
        "hints": deepcopy(block.get("hints") or []),
        "scaffolds": deepcopy(block.get("scaffolds") or []),
        "transfer": deepcopy(block.get("transfer")) if block.get("transfer") else None,
        "check": answer.get("check") or "",
        "solution": {
            "summary": answer.get("summary") or "",
            "steps": deepcopy(answer.get("steps") or []),
            "rubric": deepcopy(answer.get("rubric") or []),
        },
        "repair": _repair_payload(records, block.get("repair_ref")),
    }


def _row_id(subject: str, source_ref: str, core: str) -> str:
    safe_subject = subject.lower().replace(" ", "-")
    return f"{safe_subject}:{source_ref.lower()}:{core.lower()}"


def _move_map(application: dict | None) -> dict[str, dict]:
    return {
        row.get("id"): row
        for row in (application or {}).get("reasoning_route") or []
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _stage_index(records: dict, representation_ref: str, stage_ref: str) -> int | None:
    rep = records.get(representation_ref) or {}
    stages = [
        row.get("id")
        for row in rep.get("reveal_stages") or []
        if isinstance(row, dict) and row.get("id")
    ]
    try:
        return stages.index(stage_ref)
    except ValueError:
        return None


def _protected_move(application: dict | None) -> dict | None:
    transfer = (application or {}).get("transfer") or {}
    ref = transfer.get("protected_move_ref")
    return _move_map(application).get(ref) if ref else None


def _visual_is_pre_attempt_safe(
    records: dict,
    *,
    visual_ref: str | None,
    visual_stage_ref: str | None,
    protected_move: dict | None,
) -> bool:
    if not visual_ref and not visual_stage_ref:
        return True
    if not visual_ref or not visual_stage_ref:
        return False
    if not protected_move:
        return True
    protected_ref = protected_move.get("representation_ref")
    protected_stage = protected_move.get("visual_stage_ref")
    if not protected_ref or not protected_stage:
        return False
    if visual_ref != protected_ref:
        return False
    current = _stage_index(records, visual_ref, visual_stage_ref)
    protected = _stage_index(records, protected_ref, protected_stage)
    return current is not None and protected is not None and current < protected


def _safe_scaffold_prefix(application: dict | None, records: dict, *, core: str) -> int:
    scaffolds = list((application or {}).get("scaffolds") or [])
    if core != "CORE2B":
        return len(scaffolds)
    transfer = (application or {}).get("transfer") or {}
    protected_ref = transfer.get("protected_move_ref")
    protected = _protected_move(application)
    count = 0
    for scaffold in scaffolds:
        safe = (
            scaffold.get("reveals") == "CONCEPT"
            and scaffold.get("supports_move_ref") != protected_ref
            and _visual_is_pre_attempt_safe(
                records,
                visual_ref=scaffold.get("visual_ref"),
                visual_stage_ref=scaffold.get("visual_stage_ref"),
                protected_move=protected,
            )
        )
        if not safe:
            break
        count += 1
    return count


def _hint_prefix(hints: list[dict], allowed: set[str]) -> int:
    count = 0
    for hint in hints:
        if not isinstance(hint, dict) or hint.get("reveals") not in allowed:
            break
        count += 1
    return count


def _hint_limits(application: dict | None, *, core: str) -> tuple[int, int]:
    hints = list((application or {}).get("hints") or [])
    if core == "CORE2":
        return len(hints), len(hints)
    if core == "CORE2B":
        transfer = (application or {}).get("transfer") or {}
        pre = _hint_prefix(hints, {"CONCEPT"})
        post_allowed = {"CONCEPT"} if transfer.get("dimension") == "model_choice" else {"CONCEPT", "METHOD"}
        return pre, _hint_prefix(hints, post_allowed)
    return _hint_prefix(hints, {"CONCEPT", "METHOD"}), len(hints)


def _safe_initial_visual(
    records: dict,
    *,
    core: str,
    application: dict | None,
    initial_representation_ref: str | None,
) -> tuple[str | None, str | None]:
    stage = _initial_stage(records, initial_representation_ref)
    if core != "CORE2B":
        return initial_representation_ref, stage
    protected = _protected_move(application)
    if _visual_is_pre_attempt_safe(
        records,
        visual_ref=initial_representation_ref,
        visual_stage_ref=stage,
        protected_move=protected,
    ):
        return initial_representation_ref, stage
    return None, None


def _web_delivery(core: str) -> dict:
    blueprint = core_template_contract.resolve_web_blueprint_for_core(core)
    slots = blueprint.get("slots") or []
    return {
        "blueprint_ref": blueprint["ref"],
        "blueprint_id": blueprint["id"],
        "blueprint_version": blueprint["version"],
        "shell_ref": blueprint["shell_ref"],
        "layout_family": blueprint["layout_family"],
        "required_slots": [
            slot["id"] for slot in slots
            if isinstance(slot, dict) and slot.get("required") is True
        ],
        "slot_order": [
            slot["id"] for slot in slots
            if isinstance(slot, dict) and isinstance(slot.get("id"), str)
        ],
        "interaction_policy": deepcopy(blueprint["interaction_policy"]),
        "representation_policy": deepcopy(blueprint["representation_policy"]),
        "responsive_policy": deepcopy(blueprint["responsive_policy"]),
        "touch_policy": deepcopy(blueprint["touch_policy"]),
        "packaging_modes": list(blueprint["packaging_modes"]),
        "forbidden": list(blueprint["forbidden"]),
    }


def _projection(
    *,
    core: str,
    concept: dict | None,
    application: dict | None,
    records: dict,
    initial_representation_ref: str | None,
    orientation: dict | None = None,
) -> dict:
    transfer = (application or {}).get("transfer") or {}
    protected = transfer.get("protected_move_ref")
    initial_ref, initial_stage = _safe_initial_visual(
        records,
        core=core,
        application=application,
        initial_representation_ref=initial_representation_ref,
    )
    pre_hints, post_hints = _hint_limits(application, core=core)
    return {
        "contract_version": "1.1",
        "core": core,
        "orientation": deepcopy(orientation),
        "concept": deepcopy(concept),
        "application": deepcopy(application),
        "delivery": {
            "web": _web_delivery(core),
        },
        "presentation": {
            "attempt_before_reveal": core in {"CORE1B", "CORE2B"},
            "show_full_construction": core == "CORE1A",
            "show_solution_initially": core == "CORE2",
            "initial_visual_ref": initial_ref,
            "initial_visual_stage_ref": initial_stage,
            "protected_move_refs": [protected] if protected else [],
            "pre_attempt_scaffold_limit": _safe_scaffold_prefix(
                application, records, core=core
            ),
            "pre_attempt_hint_limit": pre_hints,
            "post_attempt_hint_limit": post_hints,
        },
    }


def _structured_familiar_blocks(products: dict[str, dict]) -> list[dict]:
    return [
        row for row in _question_blocks(products.get("CORE2A"))
        if (row.get("answer") or {}).get("reasoning_route")
        and (row.get("answer") or {}).get("crux_move_ref")
    ]


def _structured_transfer_blocks(products: dict[str, dict]) -> list[dict]:
    return [
        row for row in _question_blocks(products.get("CORE2B"))
        if (row.get("transfer") or {}).get("protected_move_ref")
        and (row.get("answer") or {}).get("reasoning_route")
    ]


def _concept_for_application(compiled: dict, records: dict, block: dict) -> str | None:
    rep_ref = _first_route_representation(block)
    if not rep_ref:
        return None
    candidates = []
    for ref in (compiled.get("derived_from") or {}).get("microtopics") or []:
        row = records.get(ref) or {}
        if (
            rep_ref in (row.get("representation_refs") or [])
            and row.get("elicitation")
        ):
            candidates.append(ref)
    return candidates[0] if candidates else None


def _finding(code: str, detail: str, source_ref: str | None = None) -> dict:
    row = {"code": code, "detail": detail}
    if source_ref:
        row["source_ref"] = source_ref
    return row


def adapt_compiled_bucket_with_status(
    compiled: dict, records: dict, *, subject: str
) -> tuple[list[dict], list[dict]]:
    """Return independent learner projections plus named provider findings.

    Core1-family delivery follows compiler ownership directly:
    - Core1 comes from the compiler's orientation product;
    - Core1A/Core1B concept coverage comes from compiled concept obligations;
    - Core2-family application projections remain question-driven.

    Optional explorers never gate static academic delivery.
    """
    products = _products(compiled)
    rows: list[dict[str, Any]] = []
    findings: list[dict] = []

    # Core1 is the compiler-owned semantic map. It is projected independently of
    # application-question maturity.
    core1_product = products.get("CORE1")
    if core1_product:
        try:
            orientation = _orientation(core1_product, compiled)
            bucket_ref = orientation["bucket_ref"]
            bucket = records.get(bucket_ref) or {}
            primary = bucket.get("primary_representation_ref")
            projection = _projection(
                core="CORE1",
                orientation=orientation,
                concept=None,
                application=None,
                records=records,
                initial_representation_ref=primary,
            )
            rows.append({
                "id": _row_id(subject, bucket_ref, "CORE1"),
                "subject": subject,
                "source_ref": bucket_ref,
                "projection": projection,
                "scene_ref": None,
                "adapter_ref": None,
                "injection_refs": [],
                "explorer_locator": _explorer_locator(records, primary),
            })
        except CoreLearningProjectionAdapterError as exc:
            findings.append(_finding("CORE1_PROJECTION_UNAVAILABLE", str(exc)))

    # Core2 is a source-custody product. Only compiler-emitted Core2 blocks can enter
    # this surface; authored A/B practice is never promoted here by the adapter.
    for block in _question_blocks(products.get("CORE2")):
        try:
            application = _application(block, records)
            initial_rep = (
                application["figure_refs"][0]
                if application["figure_refs"]
                else _first_route_representation(block)
            )
            projection = _projection(
                core="CORE2",
                concept=None,
                application=application,
                records=records,
                initial_representation_ref=initial_rep,
            )
            rows.append({
                "id": _row_id(subject, block["source_question_id"], "CORE2"),
                "subject": subject,
                "source_ref": block["source_question_id"],
                "projection": projection,
                "scene_ref": None,
                "adapter_ref": None,
                "injection_refs": [],
                "explorer_locator": _explorer_locator(records, initial_rep),
            })
        except CoreLearningProjectionAdapterError as exc:
            findings.append(_finding(
                "CORE2_PROJECTION_UNAVAILABLE", str(exc), block.get("source_question_id")
            ))

    # Study concepts are owned by compiler obligations, not discovered through practice
    # questions. This keeps concept acquisition independent of application maturity.
    for core in ("CORE1A", "CORE1B"):
        if core not in products:
            continue
        for concept_ref in _study_refs(compiled, records, core):
            try:
                concept = _concept(records, concept_ref, core=core)
                initial_rep = (
                    concept["representation_refs"][0]
                    if concept["representation_refs"]
                    else None
                )
                projection = _projection(
                    core=core,
                    concept=concept,
                    application=None,
                    records=records,
                    initial_representation_ref=initial_rep,
                )
                rows.append({
                    "id": _row_id(subject, concept_ref, core),
                    "subject": subject,
                    "source_ref": concept_ref,
                    "projection": projection,
                    "scene_ref": None,
                    "adapter_ref": None,
                    "injection_refs": [],
                    "explorer_locator": _explorer_locator(records, initial_rep),
                })
            except CoreLearningProjectionAdapterError as exc:
                findings.append(_finding(
                    f"{core}_PROJECTION_UNAVAILABLE", str(exc), concept_ref
                ))

    familiar = _structured_familiar_blocks(products)
    transfers = _structured_transfer_blocks(products)
    familiar_by_id = {row.get("source_question_id"): row for row in familiar}

    for block in familiar:
        qid = block["source_question_id"]
        try:
            application = _application(block, records)
            concept_ref = _concept_for_application(compiled, records, block)
            concept = _concept(records, concept_ref, core="CORE1A") if concept_ref else None
            initial_rep = _first_route_representation(block)
            projection = _projection(
                core="CORE2A",
                concept=concept,
                application=application,
                records=records,
                initial_representation_ref=initial_rep,
            )
            rows.append({
                "id": _row_id(subject, qid, "CORE2A"),
                "subject": subject,
                "source_ref": qid,
                "projection": projection,
                "scene_ref": None,
                "adapter_ref": None,
                "injection_refs": [],
                "explorer_locator": _explorer_locator(records, initial_rep),
            })
        except CoreLearningProjectionAdapterError as exc:
            findings.append(_finding("CORE2A_PROJECTION_UNAVAILABLE", str(exc), qid))

    for block in transfers:
        qid = block["source_question_id"]
        transfer = block.get("transfer") or {}
        lineage = list(transfer.get("builds_on") or [])
        parent = next((familiar_by_id[ref] for ref in lineage if ref in familiar_by_id), None)
        if parent is None:
            findings.append(_finding(
                "CORE2B_FAMILIAR_PARENT_UNAVAILABLE",
                "No structured familiar Core2A parent from transfer.builds_on[] was compiled.",
                qid,
            ))
            continue
        if parent.get("family") != block.get("family"):
            findings.append(_finding(
                "CORE2B_FAMILY_MISMATCH",
                f'{parent.get("family")} != {block.get("family")}',
                qid,
            ))
            continue
        try:
            application = _application(block, records)
            concept_ref = _concept_for_application(compiled, records, parent)
            concept = _concept(records, concept_ref, core="CORE1A") if concept_ref else None
            initial_rep = _first_route_representation(block) or _first_route_representation(parent)
            projection = _projection(
                core="CORE2B",
                concept=concept,
                application=application,
                records=records,
                initial_representation_ref=initial_rep,
            )
            rows.append({
                "id": _row_id(subject, qid, "CORE2B"),
                "subject": subject,
                "source_ref": qid,
                "projection": projection,
                "scene_ref": None,
                "adapter_ref": None,
                "injection_refs": [],
                "explorer_locator": _explorer_locator(
                    records, projection["presentation"]["initial_visual_ref"]
                ),
            })
        except CoreLearningProjectionAdapterError as exc:
            findings.append(_finding("CORE2B_PROJECTION_UNAVAILABLE", str(exc), qid))

    unique = {row["id"]: row for row in rows}
    result = sorted(
        unique.values(),
        key=lambda row: (
            row["subject"],
            row["source_ref"],
            CORE_ORDER.index(row["projection"]["core"]),
        ),
    )
    if not result and not findings:
        missing = [
            core for core in ("CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
            if core not in products
        ]
        if missing:
            findings.append(_finding("CORE_ROLES_MISSING", ", ".join(missing)))
        else:
            findings.append(_finding(
                "PROJECTION_UNAVAILABLE",
                "No mature learner projection was produced from the compiled bucket.",
            ))
    return result, findings

def adapt_compiled_bucket(compiled: dict, records: dict, *, subject: str) -> list[dict]:
    """Return production learner rows for compiler-backed canonical records."""
    rows, _ = adapt_compiled_bucket_with_status(compiled, records, subject=subject)
    return rows
