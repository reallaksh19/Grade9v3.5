#!/usr/bin/env python3
"""Build and revalidate bounded Interaction Briefs from canonical academic records.

Interaction Briefs are derived engineering handoffs. They preserve exact canonical refs and a
content digest so a later agent can detect academic drift. They never become curriculum truth,
learner evidence, a difficulty/priority authority, or permission to research/build.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "Shared/library/interaction-brief.schema.json"
IDEA_KEY = "grade9v3:interactive_idea"
AUTHORITY = "DERIVED_INTERACTION_HANDOFF_ONLY"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import canonical, load
from Shared.library.resolve import build_index, load_packages


class InteractionBriefError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractionBriefError(f"{code}: {detail}" if detail else code)


def _repository_basis(repo: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo,
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _subject_records(subject: str, repo: Path = REPO) -> dict[str, dict]:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths)) if paths else {}


def _canonical_slice(records: dict[str, dict], refs: list[str]) -> dict[str, dict]:
    return {ref: records[ref] for ref in sorted(set(refs)) if ref in records}


def _canonical_input_digest(records: dict[str, dict], refs: list[str]) -> str:
    body = canonical(_canonical_slice(records, refs))
    return "sha256:" + hashlib.sha256(body).hexdigest()


def _brief_id(subject: str, target_ref: str, canonical_input_digest: str) -> str:
    token = hashlib.sha256(
        canonical([subject, target_ref, canonical_input_digest])
    ).hexdigest()[:20].upper()
    return f"IBR-{token}"


def _intent_decision(microtopic: dict, capability: dict) -> str:
    predict = ((microtopic.get("elicitation") or {}).get("predict") or {}).get("prompt")
    if isinstance(predict, str) and predict.strip():
        return predict.strip()
    exit_prompt = (microtopic.get("exit_task") or {}).get("prompt")
    if isinstance(exit_prompt, str) and exit_prompt.strip():
        return exit_prompt.strip()
    success = capability.get("success_criterion")
    if isinstance(success, str) and success.strip():
        return success.strip()
    raise InteractionBriefError("INTERACTION_BRIEF_EXPECTED_DECISION_UNRESOLVED")


def _schema_errors(brief: dict, repo: Path = REPO) -> list[str]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / SCHEMA.relative_to(REPO))
    return [
        f"{'/'.join(str(part) for part in error.path)}: {error.message}"
        for error in jsonschema.Draft202012Validator(schema).iter_errors(brief)
    ]


def build_from_microtopic(
    subject: str,
    microtopic_ref: str,
    *,
    required_core: str | None = None,
    pre_attempt_protected_refs: list[str] | None = None,
    repo: Path = REPO,
) -> dict[str, Any]:
    """Derive one brief from an existing canonical microtopic interactive idea."""
    records = _subject_records(subject, repo)
    microtopic = records.get(microtopic_ref)
    _require(
        isinstance(microtopic, dict) and microtopic.get("_collection") == "microtopics",
        "INTERACTION_BRIEF_MICROTOPIC_UNRESOLVED",
        microtopic_ref,
    )
    idea = (microtopic.get("extensions") or {}).get(IDEA_KEY)
    _require(isinstance(idea, dict), "INTERACTION_BRIEF_INTENT_MISSING", microtopic_ref)

    capability_ref = microtopic.get("primary_capability_ref")
    capability = records.get(capability_ref) if isinstance(capability_ref, str) else None
    _require(
        isinstance(capability, dict) and capability.get("_collection") == "capabilities",
        "INTERACTION_BRIEF_CAPABILITY_UNRESOLVED",
        str(capability_ref or ""),
    )
    representation_ref = idea.get("representation_ref")
    representation = records.get(representation_ref) if isinstance(representation_ref, str) else None
    _require(
        isinstance(representation, dict) and representation.get("_collection") == "representations",
        "INTERACTION_BRIEF_REPRESENTATION_UNRESOLVED",
        str(representation_ref or ""),
    )

    for field in ("learner_manipulates", "becomes_visible", "misconception_targeted"):
        _require(
            isinstance(idea.get(field), str) and bool(idea[field].strip()),
            "INTERACTION_BRIEF_INTENT_FIELD_MISSING",
            field,
        )

    refs = [microtopic_ref, capability_ref, representation_ref]
    canonical_input_digest = _canonical_input_digest(records, refs)
    goal = microtopic.get("inferential_jump") or capability.get("success_criterion")
    _require(isinstance(goal, str) and bool(goal.strip()), "INTERACTION_BRIEF_LEARNER_GOAL_UNRESOLVED")

    brief = {
        "schema_version": "1.0.0",
        "brief_id": _brief_id(subject, microtopic_ref, canonical_input_digest),
        "subject": subject,
        "academic_target": {
            "target_ref": microtopic_ref,
            "microtopic_refs": [microtopic_ref],
            "capability_refs": [capability_ref],
            "question_refs": [],
            "representation_refs": [representation_ref],
        },
        "learner_goal": goal.strip(),
        "interaction_intent": {
            "learner_manipulates": idea["learner_manipulates"].strip(),
            "becomes_visible": idea["becomes_visible"].strip(),
            "misconception_targeted": idea["misconception_targeted"].strip(),
            "expected_decision_or_observation": _intent_decision(microtopic, capability),
        },
        "constraints": {
            "required_core": required_core,
            "pre_attempt_protected_refs": sorted(set(pre_attempt_protected_refs or [])),
        },
        "provenance": {
            "authority": AUTHORITY,
            "source_kind": "GRADE9V3_INTERACTIVE_IDEA",
            "canonical_record_refs": sorted(refs),
            "canonical_input_digest": canonical_input_digest,
            "repository_basis": _repository_basis(repo),
        },
    }
    errors = _schema_errors(brief, repo)
    _require(not errors, "INTERACTION_BRIEF_SCHEMA_INVALID", "; ".join(errors[:8]))
    return brief


def freshness(brief: dict, *, repo: Path = REPO) -> dict[str, Any]:
    """Re-read canonical records and report whether the brief's academic basis still matches."""
    errors = _schema_errors(brief, repo)
    if errors:
        return {
            "status": "INVALID",
            "brief_id": brief.get("brief_id"),
            "detail": "; ".join(errors[:8]),
        }
    provenance = brief.get("provenance") or {}
    if provenance.get("authority") != AUTHORITY:
        return {
            "status": "INVALID",
            "brief_id": brief.get("brief_id"),
            "detail": "Interaction Brief authority is not derived handoff authority.",
        }
    subject = brief.get("subject")
    records = _subject_records(subject, repo) if isinstance(subject, str) else {}
    refs = list(provenance.get("canonical_record_refs") or [])
    missing = [ref for ref in refs if ref not in records]
    if missing:
        return {
            "status": "UNRESOLVED",
            "brief_id": brief.get("brief_id"),
            "missing_refs": missing,
            "expected_digest": provenance.get("canonical_input_digest"),
            "current_digest": None,
        }
    current_digest = _canonical_input_digest(records, refs)
    expected = provenance.get("canonical_input_digest")
    return {
        "status": "CURRENT" if current_digest == expected else "STALE",
        "brief_id": brief.get("brief_id"),
        "missing_refs": [],
        "expected_digest": expected,
        "current_digest": current_digest,
        "repository_basis": _repository_basis(repo),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject")
    parser.add_argument("--microtopic-ref")
    parser.add_argument("--required-core")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        result = freshness(load(args.check))
    else:
        _require(bool(args.subject and args.microtopic_ref), "INTERACTION_BRIEF_TARGET_REQUIRED")
        result = build_from_microtopic(
            args.subject, args.microtopic_ref, required_core=args.required_core,
        )
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
