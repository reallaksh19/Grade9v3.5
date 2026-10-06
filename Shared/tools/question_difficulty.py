"""Canonical question-difficulty derivation shared by authoring and QRT resolution.

The five component scores are authored academic evidence. The total score and D-band are
mechanical projections of those components using Shared/vocabularies/learner-question-metadata.v1.json.
A requested/target band is planning metadata only and never changes the derived classification.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
METADATA_PATH = REPO / "Shared" / "vocabularies" / "learner-question-metadata.v1.json"
COMPONENT_KEYS = (
    "concept_model_selection",
    "representation_translation",
    "reasoning_chain_length",
    "algebra_computational_load",
    "trap_exception_sensitivity",
)
BANDS = ("D1", "D2", "D3", "D4")


class DifficultyContractError(ValueError):
    """Raised when authored difficulty evidence and its derived projection disagree."""


def _metadata() -> dict[str, Any]:
    value = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if value.get("schema") != "grade9v3-learner-question-metadata/v1":
        raise DifficultyContractError("QUESTION_DIFFICULTY_METADATA_SCHEMA_INVALID")
    return value


def score_ranges() -> dict[str, dict[str, int]]:
    ranges = (_metadata().get("question_difficulty_score_ranges") or {})
    if tuple(ranges) != BANDS:
        raise DifficultyContractError("QUESTION_DIFFICULTY_SCORE_RANGES_INVALID")
    expected_next = 0
    out: dict[str, dict[str, int]] = {}
    for band in BANDS:
        row = ranges.get(band)
        if not isinstance(row, dict):
            raise DifficultyContractError(f"QUESTION_DIFFICULTY_SCORE_RANGE_INVALID: {band}")
        low, high = row.get("min"), row.get("max")
        if not isinstance(low, int) or not isinstance(high, int) or low != expected_next or high < low:
            raise DifficultyContractError(f"QUESTION_DIFFICULTY_SCORE_RANGE_INVALID: {band}")
        out[band] = {"min": low, "max": high}
        expected_next = high + 1
    if expected_next != 11:
        raise DifficultyContractError("QUESTION_DIFFICULTY_SCORE_RANGES_MUST_COVER_0_TO_10")
    return out


def band_for_score(score: int) -> str:
    if not isinstance(score, int) or isinstance(score, bool):
        raise DifficultyContractError("QUESTION_DIFFICULTY_SCORE_INVALID")
    for band, row in score_ranges().items():
        if row["min"] <= score <= row["max"]:
            return band
    raise DifficultyContractError(f"QUESTION_DIFFICULTY_SCORE_OUT_OF_RANGE: {score}")


def score_band_map() -> dict[int, str]:
    return {
        score: band
        for band, row in score_ranges().items()
        for score in range(row["min"], row["max"] + 1)
    }


def derive(difficulty: dict[str, Any], *, question_ref: str = "<unknown>") -> dict[str, Any]:
    if not isinstance(difficulty, dict):
        raise DifficultyContractError(f"QUESTION_DIFFICULTY_MISSING_OR_INVALID: {question_ref}")
    components = difficulty.get("components")
    if not isinstance(components, dict) or set(components) != set(COMPONENT_KEYS):
        raise DifficultyContractError(f"QUESTION_DIFFICULTY_COMPONENTS_INVALID: {question_ref}")
    for key in COMPONENT_KEYS:
        value = components.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 2:
            raise DifficultyContractError(f"QUESTION_DIFFICULTY_COMPONENT_INVALID: {question_ref}:{key}")
    score = sum(components[key] for key in COMPONENT_KEYS)
    if difficulty.get("score") != score:
        raise DifficultyContractError(
            f"QUESTION_DIFFICULTY_SCORE_MISMATCH: {question_ref}:stored={difficulty.get('score')}:derived={score}"
        )
    band = band_for_score(score)
    if difficulty.get("band") != band:
        raise DifficultyContractError(
            f"QUESTION_DIFFICULTY_BAND_MISMATCH: {question_ref}:stored={difficulty.get('band')}:derived={band}"
        )
    requested = difficulty.get("requested_band")
    if requested is not None and requested not in BANDS:
        raise DifficultyContractError(f"QUESTION_DIFFICULTY_REQUESTED_BAND_INVALID: {question_ref}:{requested}")
    return {
        "score": score,
        "band": band,
        "requested_band": requested,
        "components": {key: components[key] for key in COMPONENT_KEYS},
    }
