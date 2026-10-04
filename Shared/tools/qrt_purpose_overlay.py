#!/usr/bin/env python3
"""Validate the learner-purpose overlay for a governed QRT run.

Purpose is deliberately downstream of difficulty/demand selection. It may alter support posture
and require a fresh post-core transfer experience, but it must never relabel the source question's
D-band or base QRT cell.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO / "Shared/quality/qrt-purpose-overlay.v1.json"
TRANSFER_DIMS = ("model_choice", "novelty", "reasoning_steps", "representation_translation")


class PurposeOverlayError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PurposeOverlayError(f"{path}: expected object")
    return value


def validate_policy(policy: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if policy.get("schema") != "qrt-purpose-overlay/v1":
        problems.append("PURPOSE_POLICY_SCHEMA_INVALID")
    purposes = policy.get("purposes") or {}
    if tuple(purposes) != ("STARTER", "PRACTICE", "REVISION", "COMPETITION"):
        problems.append("PURPOSE_POLICY_IDS_INVALID")
    if tuple(policy.get("transfer_dimensions") or ()) != TRANSFER_DIMS:
        problems.append("PURPOSE_TRANSFER_DIMENSIONS_INVALID")
    for purpose in ("REVISION", "COMPETITION"):
        row = purposes.get(purpose) or {}
        if row.get("extension_requirement") != "REQUIRED":
            problems.append(f"PURPOSE_EXTENSION_NOT_REQUIRED:{purpose}")
        if not str(row.get("learner_title") or "").strip():
            problems.append(f"PURPOSE_LEARNER_TITLE_MISSING:{purpose}")
    return problems


def _extensions(run: dict[str, Any]) -> list[dict[str, Any]]:
    rows = run.get("purpose_extensions") or []
    return [row for row in rows if isinstance(row, dict)]


def _has_transfer_increase(delta: dict[str, Any]) -> bool:
    for key in TRANSFER_DIMS:
        value = delta.get(key, 0)
        if isinstance(value, (int, float)) and value > 0:
            return True
    return False


def _official_claim_problems(ext: dict[str, Any], competition_policy: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    claim = ext.get("source_claim")
    provenance = ext.get("provenance")
    if provenance == "AUTHORED_COMPETITION_STYLE":
        if isinstance(claim, dict) and claim.get("official_exam_claim"):
            problems.append(f"AUTHORED_COMPETITION_STYLE_CANNOT_CLAIM_OFFICIAL:{ext.get('id')}")
        return problems
    if provenance not in {"VERIFIED_COMPETITION_SOURCE", "ADAPTED_VERIFIED_COMPETITION_SOURCE"}:
        return problems
    if not isinstance(claim, dict):
        return [f"COMPETITION_SOURCE_CLAIM_MISSING:{ext.get('id')}"]
    policy = competition_policy.get("official_claim") or {}
    for field in policy.get("required_fields") or []:
        if not str(claim.get(field) or "").strip():
            problems.append(f"COMPETITION_SOURCE_FIELD_MISSING:{ext.get('id')}:{field}")
    if claim.get("verification_status") != policy.get("verification_status"):
        problems.append(f"COMPETITION_SOURCE_NOT_VERIFIED:{ext.get('id')}")
    if claim.get("exam_system") not in set(policy.get("allowed_exam_systems") or []):
        problems.append(f"COMPETITION_EXAM_SYSTEM_INVALID:{ext.get('id')}:{claim.get('exam_system')}")
    return problems


def check_run(run: dict[str, Any], *, final: bool = False) -> list[str]:
    policy = load(POLICY_PATH)
    problems = validate_policy(policy)
    profile = run.get("learner_profile") or {}
    purpose = profile.get("purpose")
    if purpose not in (policy.get("purposes") or {}):
        problems.append(f"PURPOSE_INVALID:{purpose}")
        return problems

    purpose_policy = policy["purposes"][purpose]
    rows = _extensions(run)
    matching = [row for row in rows if row.get("purpose") == purpose]
    required = purpose_policy.get("extension_requirement") == "REQUIRED"
    if required and not matching:
        problems.append(f"PURPOSE_EXTENSION_MISSING:{purpose}")
        return problems
    if not matching:
        return problems

    expected_kind = purpose_policy.get("extension_kind")
    allowed_provenance = set(purpose_policy.get("allowed_provenance") or [])
    owner_question_ids = {str(q.get("id")) for q in run.get("questions") or [] if isinstance(q, dict)}
    for ext in matching:
        eid = str(ext.get("id") or "<unknown>")
        if ext.get("kind") != expected_kind:
            problems.append(f"PURPOSE_EXTENSION_KIND_INVALID:{eid}:{ext.get('kind')}")
        if ext.get("provenance") not in allowed_provenance:
            problems.append(f"PURPOSE_EXTENSION_PROVENANCE_INVALID:{eid}:{ext.get('provenance')}")
        text = str(ext.get("question_text") or "").strip()
        if not text:
            problems.append(f"PURPOSE_EXTENSION_QUESTION_MISSING:{eid}")
        if ext.get("source_question_ref") in owner_question_ids and ext.get("fresh_question") is not True:
            problems.append(f"PURPOSE_EXTENSION_NOT_FRESH:{eid}")
        if not str(ext.get("canonical_concept_or_family_ref") or "").strip():
            problems.append(f"PURPOSE_EXTENSION_CONCEPT_LINEAGE_MISSING:{eid}")
        delta = ext.get("transfer_delta") or {}
        if not isinstance(delta, dict) or not _has_transfer_increase(delta):
            problems.append(f"PURPOSE_EXTENSION_TRANSFER_NOT_INCREASED:{eid}")
        if ext.get("attempt_gate") is not True:
            problems.append(f"PURPOSE_EXTENSION_NOT_ATTEMPT_GATED:{eid}")
        if not str(ext.get("protected_move_ref") or "").strip():
            problems.append(f"PURPOSE_EXTENSION_PROTECTED_MOVE_MISSING:{eid}")
        if purpose == "COMPETITION":
            problems.extend(_official_claim_problems(ext, purpose_policy))
            if ext.get("competitive_reasoning_basis") in (None, ""):
                problems.append(f"COMPETITIVE_REASONING_BASIS_MISSING:{eid}")
        if purpose == "REVISION" and ext.get("revision_progression_basis") in (None, ""):
            problems.append(f"REVISION_PROGRESSION_BASIS_MISSING:{eid}")

        if final:
            marker = str(ext.get("rendered_marker") or "")
            artifact_ref = str(ext.get("artifact_ref") or "")
            if not marker:
                problems.append(f"PURPOSE_EXTENSION_RENDER_MARKER_MISSING:{eid}")
            if not artifact_ref:
                problems.append(f"PURPOSE_EXTENSION_ARTIFACT_REF_MISSING:{eid}")
            artifact = next((a for a in run.get("rendered_artifacts") or []
                             if isinstance(a, dict) and str(a.get("id")) == artifact_ref), None)
            if artifact is None:
                problems.append(f"PURPOSE_EXTENSION_ARTIFACT_UNKNOWN:{eid}:{artifact_ref}")
            else:
                path = REPO / str(artifact.get("path") or "")
                if not path.is_file():
                    problems.append(f"PURPOSE_EXTENSION_ARTIFACT_MISSING:{eid}:{artifact_ref}")
                else:
                    html = path.read_text(encoding="utf-8", errors="replace")
                    if marker and marker not in html:
                        problems.append(f"PURPOSE_EXTENSION_NOT_RENDERED:{eid}:{marker}")
                    title = str(purpose_policy.get("learner_title") or "")
                    if title and title not in html:
                        problems.append(f"PURPOSE_EXTENSION_TITLE_NOT_RENDERED:{eid}:{title}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--check-policy", action="store_true")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args(argv)
    try:
        policy = load(POLICY_PATH)
        if args.check_policy:
            problems = validate_policy(policy)
        elif args.run:
            run = load(args.run)
            problems = check_run(run, final=args.final)
        else:
            parser.error("provide RUN or --check-policy")
    except (OSError, json.JSONDecodeError, PurposeOverlayError) as exc:
        print(f"load failed: {exc}")
        return 1
    if problems:
        print("\n".join(problems))
        return 1
    print("ok: qrt purpose overlay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
