#!/usr/bin/env python3
"""Validate canonical visual-support ownership without making renderers academic authority."""
from __future__ import annotations


def findings(records: dict[str, dict]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []

    def fail(code: str, record: str, detail: str) -> None:
        out.append({"code": code, "record": record, "detail": detail})

    representations = {
        rid: row for rid, row in records.items()
        if row.get("_collection") == "representations"
    }
    resources = {
        rid: row for rid, row in records.items()
        if row.get("_collection") == "resources"
    }

    for rid, rep in representations.items():
        required = set(rep.get("required_elements", []))
        stages = rep.get("reveal_stages", []) or []
        stage_ids = [row.get("id") for row in stages]
        if len(stage_ids) != len(set(stage_ids)):
            fail("VISUAL_STAGE_DUPLICATE", rid, "reveal stage ids must be unique within one representation")
        stage_set = set(stage_ids)

        for stage in stages:
            unknown = sorted(set(stage.get("visible_elements", [])) - required)
            if unknown:
                fail("VISUAL_STAGE_UNKNOWN_ELEMENT", rid,
                     f"{stage.get('id')} exposes undeclared elements: {', '.join(unknown)}")

        seen_support = set()
        for binding in rep.get("support_stage_map", []) or []:
            level = binding.get("support_level")
            target = binding.get("visual_stage_ref")
            if level in seen_support:
                fail("VISUAL_SUPPORT_LEVEL_DUPLICATE", rid, f"support level {level} is mapped more than once")
            seen_support.add(level)
            if target not in stage_set:
                fail("VISUAL_SUPPORT_STAGE_FOREIGN", rid,
                     f"support level {level} points to {target}, not a stage of this representation")

        for resource_ref in rep.get("interactive_resource_refs", []) or []:
            resource = resources.get(resource_ref)
            if not resource:
                fail("VISUAL_EXPLORER_UNKNOWN", rid, f"interactive resource {resource_ref} does not resolve")
            elif "ACTIVITY" not in (resource.get("role") or []):
                fail("VISUAL_EXPLORER_NOT_ACTIVITY", rid,
                     f"interactive resource {resource_ref} does not carry ACTIVITY role")

    for rid, row in records.items():
        if row.get("_collection") == "microtopics":
            for rep_ref in row.get("representation_refs", []) or []:
                if rep_ref not in representations:
                    fail("MICROTOPIC_VISUAL_WRONG_TYPE", rid,
                         f"representation_refs contains {rep_ref}, which is not a representation")

        if row.get("_collection") != "questions":
            continue
        previous: dict[str, int] = {}
        for position, hint in enumerate(row.get("hints", []) or []):
            visual_ref = hint.get("visual_ref")
            stage_ref = hint.get("visual_stage_ref")
            if visual_ref is None and stage_ref is None:
                continue
            if not visual_ref or not stage_ref:
                fail("HINT_VISUAL_PAIR_INCOMPLETE", rid,
                     f"hint {position + 1} must provide visual_ref and visual_stage_ref together")
                continue
            rep = representations.get(visual_ref)
            if rep is None:
                fail("HINT_VISUAL_WRONG_TYPE", rid,
                     f"hint {position + 1} visual_ref {visual_ref} is not a representation")
                continue
            ids = [stage.get("id") for stage in rep.get("reveal_stages", []) or []]
            if stage_ref not in ids:
                fail("HINT_VISUAL_STAGE_FOREIGN", rid,
                     f"hint {position + 1} stage {stage_ref} does not belong to {visual_ref}")
                continue
            index = ids.index(stage_ref)
            if visual_ref in previous and index < previous[visual_ref]:
                fail("HINT_VISUAL_STAGE_REGRESSION", rid,
                     f"hint {position + 1} moves {visual_ref} backward from stage {previous[visual_ref]} to {index}")
            previous[visual_ref] = index
    return out
