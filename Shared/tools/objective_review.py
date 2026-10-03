#!/usr/bin/env python3
"""Resolve and validate the 4×7 Difficulty × Demand objective-review policy.

Blueprint 1.9 remains the page/component authority. This module supplies the
semantic job of those components and never auto-decides YES/PARTLY/NO.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "Shared/quality/objective-review"
BANDS_FILE = ROOT / "bands.v1.json"
MATRIX_FILE = ROOT / "question-demand-matrix.v1.json"
STRATEGIES_FILE = ROOT / "validation-strategies.v1.json"
DEMAND_DIR = ROOT / "demands"
OVERLAYS = {
    "Physics": REPO / "Physics/adapter/QuestionDemandOverlay.json",
    "Chemistry": REPO / "Chemistry/adapter/QuestionDemandOverlay.json",
    "Mathematics": REPO / "Mathematics/adapter/QuestionDemandOverlay.json",
}
BANDS = ("D1", "D2", "D3", "D4")
DEMANDS = ("RCL", "CON", "REP", "PRC", "MOD", "PRF", "EVD")
STAGES = ("REPRESENTATION", "KEY_CONCEPT", "CRUX", "FORMAL_MODEL", "CHECKPOINT")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def demand_policy(demand: str) -> dict:
    if demand not in DEMANDS:
        raise ValueError(f"unknown demand {demand!r}")
    return load(DEMAND_DIR / f"{demand}.v1.json")


def template_id(band: str, demand: str) -> str:
    if band not in BANDS:
        raise ValueError(f"unknown band {band!r}")
    if demand not in DEMANDS:
        raise ValueError(f"unknown demand {demand!r}")
    return f"QRT-{band}-{demand}"


def resolve(band: str, demand: str) -> dict:
    band_policy = load(BANDS_FILE)["bands"][band]
    dp = demand_policy(demand)
    tid = template_id(band, demand)
    return {
        "template_id": tid,
        "difficulty_band": band,
        "demand_family": demand,
        "name": f"{band_policy['label']} × {dp['name']}",
        "objective": dp["objective"],
        "choose_when": dp["choose_when"],
        "do_not_choose_when": dp["do_not_choose_when"],
        "difficulty_character": band_policy["difficulty_character"],
        "adjacent_cells": [template_id(band, item) for item in dp["adjacent_demands"]],
        "slots": {**dp["slots"], "W": dp["slots"]["W"] + "; at this band: " + band_policy["W_band_semantics"]},
        "attempt_first": {
            "protected_slot": "W",
            "rule": "Hints, safe figures and pre-attempt panels may orient or bridge but must not directly state or execute W.",
            "band_posture": band_policy["support_posture"],
        },
        "hint_objectives": {
            "REPRESENTATION": {"review_id": "H1", "objective": dp["hint_objectives"]["REPRESENTATION"], "applicability": "APPLICABLE"},
            "KEY_CONCEPT": {"review_id": "H2", "objective": dp["hint_objectives"]["KEY_CONCEPT"], "applicability": "APPLICABLE"},
            "CRUX": {"review_id": "H3", "objective": dp["hint_objectives"]["CRUX"], "applicability": "APPLICABLE"},
            "FORMAL_MODEL": {"review_id": None, "objective": "Supply or focus a formal relation only when it unlocks continuation and still leaves W unresolved.", "applicability": band_policy["FORMAL_MODEL"]},
            "CHECKPOINT": {"review_id": None, "objective": "Offer an intermediate state only when it helps continuation without revealing W or the final answer.", "applicability": band_policy["CHECKPOINT"]},
        },
        "figure_policy": {
            **dp["figure_policy"],
            "stage_objectives": {
                "S1": "Clarify X in the question's own situation without embedding the answer or W.",
                "S2": "Show Y or its correspondence on the same complete representation using the question's own data or symbols.",
                "S3": "Show the construction or evidential route toward Z while leaving W and the result unresolved.",
            },
            "complete_stage_rule": "Every displayed stage is independently intelligible as a complete representation.",
        },
        "helper_policy": {
            "P1": "Pre-attempt conditions, trap and difficulty panels leave W to the learner and do not state the right route as a warning.",
            "P2": "Concept navigation lands on the canonical unit that teaches or repairs X, not merely the same broad topic.",
            "P3": "Post-attempt working says why each step is valid here, identifies the true crux and checks by an independent route.",
        },
        "misconception_policy": {
            "M1": "Name the plausible wrong idea or wrong route most likely to interfere with X for this demand.",
            "M2": "Use a diagnostic prompt whose reasoning distinguishes holding the wrong idea from an execution slip.",
            "M3": "Repair by showing why the wrong idea fails here and state the replacement rule or condition.",
            "families": dp["misconception_families"],
        },
        "solution_architecture": dp["solution_architecture"],
        "validation_strategy_refs": dp["validation_strategy_refs"],
        "core1a_extraction": {
            "required_signals": dp["core1a_extraction_signals"],
            "authority_rule": "Core2 demand evidence guides emphasis and traceability only; Core1A academic truth remains canonical or researched.",
            "lineage": ["canonical_refs", "evidence_question_ids"],
        },
    }


def strategy_ids() -> set[str]:
    return {row["id"] for row in load(STRATEGIES_FILE)["strategies"]}


def problems() -> list[str]:
    out: list[str] = []
    matrix = load(MATRIX_FILE)
    cells = matrix.get("cells") or []
    expected = {(band, demand) for band in BANDS for demand in DEMANDS}
    actual: list[tuple[str, str]] = []
    if len(cells) != 28:
        out.append(f"matrix has {len(cells)} cells; expected 28")
    for index, row in enumerate(cells):
        band, demand = row.get("difficulty_band"), row.get("demand_family")
        actual.append((band, demand))
        try:
            wanted = template_id(band, demand)
        except ValueError as exc:
            out.append(f"cells[{index}]: {exc}")
            continue
        if row.get("template_id") != wanted:
            out.append(f"cells[{index}]: expected {wanted}")
        policy = resolve(band, demand)
        for key in ("X", "Y", "Z", "W"):
            if not policy["slots"].get(key):
                out.append(f"{wanted}: missing {key}")
    for band, demand in sorted(expected - set(actual)):
        out.append(f"missing {band}×{demand}")
    for pair in sorted({item for item in actual if actual.count(item) > 1}):
        out.append(f"duplicate {pair[0]}×{pair[1]}")
    known = strategy_ids()
    for band, demand in expected:
        for ref in resolve(band, demand)["validation_strategy_refs"]:
            if ref not in known:
                out.append(f"{template_id(band, demand)}: unknown strategy {ref}")
    for subject, path in OVERLAYS.items():
        if not path.is_file():
            out.append(f"{subject}: missing QuestionDemandOverlay.json")
            continue
        overlay = load(path)
        rows = overlay.get("demand_overlays") or {}
        for demand in set(DEMANDS) - set(rows):
            out.append(f"{subject}: overlay missing {demand}")
        for demand, row in rows.items():
            if demand not in DEMANDS:
                out.append(f"{subject}: unknown overlay demand {demand}")
            for ref in row.get("preferred_strategies") or []:
                if ref not in known:
                    out.append(f"{subject}/{demand}: unknown strategy {ref}")
    return out


def packet(band: str, demand: str, subject: str | None = None) -> dict:
    result = {
        "schema_version": "1.0.0",
        "matrix_ref": load(MATRIX_FILE)["matrix_id"],
        "matrix_digest": digest(MATRIX_FILE),
        "template_ref": template_id(band, demand),
        "template": resolve(band, demand),
    }
    if subject:
        if subject not in OVERLAYS:
            raise ValueError(f"unknown subject {subject!r}")
        overlay = load(OVERLAYS[subject])
        result.update(
            subject=subject,
            subject_overlay_ref=str(OVERLAYS[subject].relative_to(REPO)),
            subject_overlay=overlay["demand_overlays"][demand],
        )
    return result


def question_pedagogy_problems(record: dict) -> list[str]:
    """Check explicit matrix bindings and addressable W leakage.

    This cannot infer semantic leakage from prose or SVG pixels. The qualitative
    H/S/P/M review remains a reviewer judgement.
    """
    out: list[str] = []
    band = record.get("difficulty_band")
    demand = record.get("primary_demand")
    try:
        wanted = template_id(band, demand)
    except ValueError as exc:
        return [str(exc)]
    if record.get("matrix_template_ref") != wanted:
        out.append(f"matrix_template_ref must be {wanted}")
    secondary = record.get("secondary_demands") or []
    if demand in secondary:
        out.append("secondary_demands repeats primary_demand")
    for index, binding in enumerate(record.get("hint_bindings") or []):
        stage = binding.get("stage")
        if stage not in STAGES:
            out.append(f"hint_bindings[{index}]: unknown stage {stage!r}")
            continue
        objective_ref = f"{wanted}#{stage}"
        if binding.get("objective_ref") != objective_ref:
            out.append(f"hint_bindings[{index}]: objective_ref must be {objective_ref}")
    protected = (((record.get("slots") or {}).get("W") or {}).get("protected_move_ref"))
    if protected:
        for index, binding in enumerate(record.get("hint_bindings") or []):
            if binding.get("supports_move_ref") == protected:
                out.append(f"W_LEAK hint_bindings[{index}] supports protected move {protected}")
        if protected in ((record.get("figure") or {}).get("reveals_move_refs") or []):
            out.append(f"W_LEAK figure reveals protected move {protected}")
        if protected in ((record.get("pre_attempt") or {}).get("move_refs_revealed") or []):
            out.append(f"W_LEAK pre_attempt material reveals protected move {protected}")
    known = strategy_ids()
    for ref in record.get("validation_strategy_refs") or []:
        if ref not in known:
            out.append(f"unknown validation strategy {ref}")
    evidence = ((record.get("core1a_extraction") or {}).get("evidence_question_ids") or [])
    if record.get("question_id") and record["question_id"] not in evidence:
        out.append("core1a_extraction.evidence_question_ids must include this question_id")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    make = commands.add_parser("packet")
    make.add_argument("--band", choices=BANDS, required=True)
    make.add_argument("--demand", choices=DEMANDS, required=True)
    make.add_argument("--subject", choices=tuple(OVERLAYS))
    check_question = commands.add_parser("check-question")
    check_question.add_argument("file", type=Path)
    args = parser.parse_args(argv)
    if args.command == "check":
        errors = problems()
        if errors:
            print("\n".join(errors))
            return 1
        print("ok: 28 Difficulty × Demand cells, strategies and subject overlays")
        return 0
    if args.command == "packet":
        print(json.dumps(packet(args.band, args.demand, args.subject), indent=2, ensure_ascii=False))
        return 0
    errors = question_pedagogy_problems(load(args.file))
    if errors:
        print("\n".join(errors))
        return 1
    print("ok: question pedagogy bindings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
