#!/usr/bin/env python3
"""Compile and verify the 7-demand x 4-band Question Review Template matrix."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
VOCAB_PATH = REPO / "Shared" / "vocabularies" / "cognitive-demand.v1.json"
MATRIX_PATH = REPO / "Shared" / "quality" / "question-demand-matrix.v1.json"
GENERATED_PATH = REPO / "Shared" / "quality" / "question-demand-templates.v1.json"

DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")
ASKS = ("H1", "H2", "H3", "S1", "S2", "S3", "P1", "P2", "P3", "M1", "M2", "M3")
TARGETS = ("X", "Y", "Z", "W", "wrong_idea", "replacement_rule", "visual_job", "check_job")
FORBIDDEN_SCORE_KEYS = {"score", "scores", "points", "weight", "weights", "threshold", "thresholds"}


class QRTContractError(ValueError):
    """Raised when the source matrix cannot resolve safely."""


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise QRTContractError(f"{path}: expected an object")
    return data


def forbidden_score_keys(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{path}.{key}" if path else key
            if key.lower() in FORBIDDEN_SCORE_KEYS:
                found.append(here)
            found.extend(forbidden_score_keys(child, here))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_score_keys(child, f"{path}[{index}]"))
    return found


def validate_contract(matrix: dict[str, Any], vocab: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if matrix.get("schema") != "question-demand-matrix/v1":
        problems.append("matrix schema must be question-demand-matrix/v1")
    if vocab.get("schema") != "grade9v3-cognitive-demand/v1":
        problems.append("vocabulary schema must be grade9v3-cognitive-demand/v1")

    vocab_demands = tuple((vocab.get("demands") or {}).keys())
    matrix_demands = tuple((matrix.get("demands") or {}).keys())
    if tuple(vocab_demands) != DEMANDS:
        problems.append(f"vocabulary demands must be exactly {list(DEMANDS)} in order")
    if tuple(matrix_demands) != DEMANDS:
        problems.append(f"matrix demands must be exactly {list(DEMANDS)} in order")
    if matrix_demands != vocab_demands:
        problems.append("matrix and vocabulary demand ids differ")

    asks = matrix.get("review_asks") or {}
    if tuple(asks) != ASKS:
        problems.append(f"review asks must be exactly {list(ASKS)} in order")
    for ask in ASKS:
        row = asks.get(ask)
        if not isinstance(row, dict):
            problems.append(f"{ask}: missing review ask")
            continue
        for field in ("verb", "objective", "question"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                problems.append(f"{ask}.{field}: non-empty text required")

    for demand in DEMANDS:
        row = (matrix.get("demands") or {}).get(demand)
        if not isinstance(row, dict):
            continue
        targets = row.get("targets") or {}
        if tuple(targets) != TARGETS:
            problems.append(f"{demand}.targets must be exactly {list(TARGETS)} in order")
        for target in TARGETS:
            if not isinstance(targets.get(target), str) or not targets[target].strip():
                problems.append(f"{demand}.targets.{target}: non-empty text required")

    band_policies = matrix.get("band_policies") or {}
    if tuple(band_policies) != BANDS:
        problems.append(f"band policies must be exactly {list(BANDS)} in order")
    for band in BANDS:
        row = band_policies.get(band)
        if not isinstance(row, dict):
            continue
        for field in ("label", "protected_work", "support_posture"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                problems.append(f"{band}.{field}: non-empty text required")

    forbidden = forbidden_score_keys(matrix)
    if forbidden:
        problems.append("numeric-quality scoring fields are forbidden: " + ", ".join(forbidden))
    return problems


def _fill(text: str, values: dict[str, str]) -> str:
    try:
        return text.format_map(values)
    except KeyError as exc:
        raise QRTContractError(f"unknown review placeholder {exc.args[0]!r} in {text!r}") from exc


def compile_templates(matrix: dict[str, Any], vocab: dict[str, Any]) -> list[dict[str, Any]]:
    problems = validate_contract(matrix, vocab)
    if problems:
        raise QRTContractError("; ".join(problems))
    compiled: list[dict[str, Any]] = []
    for demand in DEMANDS:
        demand_row = matrix["demands"][demand]
        for band in BANDS:
            band_row = matrix["band_policies"][band]
            values = {**demand_row["targets"], "band_protected_work": band_row["protected_work"]}
            review = {
                ask: {
                    "verb": row["verb"],
                    "objective": _fill(row["objective"], values),
                    "question": _fill(row["question"], values),
                }
                for ask, row in matrix["review_asks"].items()
            }
            slots = copy.deepcopy(demand_row["targets"])
            slots["W"] = f"{slots['W']}. Band protection: {band_row['protected_work']}"
            compiled.append({
                "template_id": f"QRT-{demand}-{band}",
                "demand": demand,
                "demand_label": demand_row["label"],
                "band": band,
                "band_label": band_row["label"],
                "decisive_act": demand_row["decisive_act"],
                "slots": slots,
                "band_policy": {
                    "protected_work": band_row["protected_work"],
                    "support_posture": band_row["support_posture"],
                },
                "review": review,
            })
    return compiled


def generated_payload(matrix: dict[str, Any], vocab: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "question-demand-templates/v1",
        "version": matrix["version"],
        "source_matrix_ref": MATRIX_PATH.relative_to(REPO).as_posix(),
        "vocabulary_ref": VOCAB_PATH.relative_to(REPO).as_posix(),
        "templates": compile_templates(matrix, vocab),
    }


def dumps(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def normalized_signature(template: dict[str, Any]) -> str:
    material = {
        "slots": template["slots"],
        "band_policy": template["band_policy"],
        "review": template["review"],
    }
    return json.dumps(material, sort_keys=True, ensure_ascii=False)


def check_paths() -> list[str]:
    try:
        matrix, vocab = load(MATRIX_PATH), load(VOCAB_PATH)
    except (OSError, json.JSONDecodeError, QRTContractError) as exc:
        return [f"load failed: {exc}"]
    problems = validate_contract(matrix, vocab)
    if problems:
        return problems
    try:
        payload = generated_payload(matrix, vocab)
    except QRTContractError as exc:
        return [str(exc)]
    templates = payload["templates"]
    if len(templates) != 28:
        problems.append(f"compile must yield 28 templates, found {len(templates)}")
    ids = [row["template_id"] for row in templates]
    if len(ids) != len(set(ids)):
        problems.append("compiled template ids are not unique")
    signatures = [normalized_signature(row) for row in templates]
    if len(signatures) != len(set(signatures)):
        problems.append("compiled semantic signatures are not unique")
    for row in templates:
        if tuple(row["review"]) != ASKS:
            problems.append(f"{row['template_id']}: missing or reordered review asks")
        forbidden = forbidden_score_keys(row)
        if forbidden:
            problems.append(f"{row['template_id']}: numeric-quality scoring fields are forbidden: {', '.join(forbidden)}")
    expected = dumps(payload)
    try:
        actual = GENERATED_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        problems.append(f"generated projection missing: {exc}")
    else:
        if actual != expected:
            problems.append(f"{GENERATED_PATH.relative_to(REPO)} is stale; run question_review_matrix.py write")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("compile", help="print the compiled 28-cell projection")
    write_p = sub.add_parser("write", help="regenerate the committed 28-cell projection")
    write_p.add_argument("--check", action="store_true", help="write nothing; fail when the projection is stale")
    sub.add_parser("check", help="validate the source contract and committed projection")
    args = parser.parse_args(argv)

    matrix, vocab = load(MATRIX_PATH), load(VOCAB_PATH)
    payload = generated_payload(matrix, vocab)

    if args.cmd == "compile":
        print(dumps(payload), end="")
        return 0
    if args.cmd == "write":
        expected = dumps(payload)
        current = GENERATED_PATH.read_text(encoding="utf-8") if GENERATED_PATH.exists() else None
        if args.check:
            if current != expected:
                print(f"STALE: {GENERATED_PATH.relative_to(REPO)}")
                return 1
            print("ok")
            return 0
        GENERATED_PATH.write_text(expected, encoding="utf-8")
        print(f"wrote {GENERATED_PATH.relative_to(REPO)}")
        return 0

    problems = check_paths()
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("ok: 7 demands x 4 bands = 28 unique QRT cells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
