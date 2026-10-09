#!/usr/bin/env python3
"""Read-only, opt-in per-question QRT coverage and dependency freshness (#313 I1b).

This composes the existing full QRT completion gate and never authors review
judgements, promotes a reviewer, accepts a QRT cell, or modifies learner files.
Only explicitly inventoried changed candidates are reported; an empty index
cannot establish repository-wide coverage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import qrt_pipeline_gate, question_review_matrix as qrt

REQUIRED_INPUTS = {
    "Shared/quality/question-demand-matrix.v1.json",
    "Shared/vocabularies/cognitive-demand.v1.json",
    "Shared/web/interactive-page-blueprints.v1.json",
    "Shared/quality/question-demand-templates.v1.json",
    "Shared/vocabularies/learner-question-metadata.v1.json",
}
DIGEST = re.compile(r"sha256:[a-f0-9]{64}\Z")
SHA = re.compile(r"[a-f0-9]{40}\Z")


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _path(repo: Path, raw: Any) -> tuple[Path | None, str | None]:
    if not isinstance(raw, str) or not raw:
        return None, "PATH_MISSING"
    given = Path(raw)
    resolved = (repo / given).resolve()
    if given.is_absolute() or not resolved.is_relative_to(repo.resolve()):
        return None, "PATH_OUTSIDE_REPOSITORY"
    return resolved, None


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("expected JSON object")
    return value


def _finding(code: str, where: str, detail: str = "") -> dict[str, str]:
    return {"code": code, "where": where, "detail": detail}


def _tracked_file(
    repo: Path, row: Any, *, category: str,
) -> tuple[Path | None, list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    if not isinstance(row, dict):
        return None, [_finding(f"{category}_RECORD_INVALID", "")]
    raw = row.get("path")
    path, issue = _path(repo, raw)
    if issue:
        return None, [_finding(f"{category}_{issue}", str(raw))]
    assert path is not None
    label = str(raw)
    claimed = row.get("sha256")
    if not isinstance(claimed, str) or not DIGEST.fullmatch(claimed):
        findings.append(_finding(f"{category}_DIGEST_INVALID", label))
    if not path.is_file():
        findings.append(_finding(f"{category}_MISSING", label))
    elif isinstance(claimed, str) and claimed != sha256(path):
        findings.append(_finding(f"{category}_DIGEST_STALE", label))
    return path, findings


def _status(findings: list[dict], reviews: list[dict]) -> str:
    if findings:
        return "REVIEW_REQUIRED_OR_STALE"
    if any(any(verdict in {"PARTLY", "NO"} for verdict in [
        item.get("verdict") for item in (review.get("judgements") or {}).values()
        if isinstance(item, dict)
    ]) for review in reviews if isinstance(review.get("judgements"), dict)):
        return "SEMANTIC_REWORK_REQUIRED"
    return "REVIEW_EVIDENCE_COMPLETE_NOT_ACCEPTANCE"


def candidate(repo: Path, row: Any, *, head: str) -> dict:
    """One explicit scope row: no discovery by guessed paths or QRT acceptance."""
    if not isinstance(row, dict):
        return {"question_ref": None, "status": "REVIEW_REQUIRED_OR_STALE",
                "findings": [_finding("CANDIDATE_INVALID", "")]}
    qid = str(row.get("question_ref") or "")
    findings: list[dict[str, str]] = []
    if not qid:
        findings.append(_finding("QUESTION_REF_MISSING", ""))
    run_path, run_findings = _tracked_file(
        repo, row.get("run"), category="RUN",
    )
    findings.extend(run_findings)

    inputs = row.get("tracked_inputs")
    if not isinstance(inputs, list) or not inputs:
        findings.append(_finding("TRACKED_INPUTS_MISSING", qid))
        inputs = []
    seen: set[str] = set()
    for item in inputs:
        raw = item.get("path") if isinstance(item, dict) else None
        if isinstance(raw, str):
            if raw in seen:
                findings.append(_finding("TRACKED_INPUT_DUPLICATE", raw))
            seen.add(raw)
        _, errors = _tracked_file(repo, item, category="INPUT")
        findings.extend(errors)
    for required in sorted(REQUIRED_INPUTS - seen):
        findings.append(_finding("CANONICAL_AUTHORITY_INPUT_UNTRACKED", required))
    source_name = row.get("question_source_path")
    profile_name = row.get("learner_profile_path")
    for label, raw in (("QUESTION_SOURCE", source_name), ("LEARNER_PROFILE", profile_name)):
        if not isinstance(raw, str) or not raw:
            findings.append(_finding(f"{label}_REF_MISSING", qid))
        elif raw not in seen:
            findings.append(_finding(f"{label}_NOT_TRACKED", str(raw)))
    selected_cell = None
    demand = None
    band = None
    if (isinstance(source_name, str) and source_name in seen
            and isinstance(profile_name, str) and profile_name in seen):
        source_path, source_err = _path(repo, source_name)
        profile_path, profile_err = _path(repo, profile_name)
        if source_err or profile_err:
            findings.append(_finding("QRT_RESOLUTION_SOURCE_PATH_INVALID", qid))
        elif source_path is not None and profile_path is not None and source_path.is_file() and profile_path.is_file():
            try:
                source_doc, profile = _load_json(source_path), _load_json(profile_path)
                source_question = qrt._select_question(source_doc, qid)
                resolution = qrt.resolve_review(
                    source_question, profile,
                    qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH),
                )
                selected_cell = resolution["template_id"]
                demand = resolution["classification"]["demand"]["primary"]
                band = resolution["classification"]["band"]
            except (OSError, ValueError, KeyError, StopIteration, TypeError) as exc:
                findings.append(_finding("CANONICAL_QRT_RESOLUTION_FAILED", qid, str(exc)))
    reviewed_asks: dict[str, str] = {}
    review_basis = "NOT_RECORDED"
    bound_artifact = None
    head_from_run = None
    if run_path is not None and run_path.is_file():
        try:
            run = _load_json(run_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            findings.append(_finding("RUN_INVALID", str(run_path.relative_to(repo)), str(exc)))
        else:
            head_from_run = (run.get("run_identity") or {}).get("head_sha")
            if head_from_run != head:
                findings.append(_finding("RUN_HEAD_STALE", qid, str(head_from_run)))
            requirements = run.get("review_requirements") or {}
            if not requirements.get("independent_rendered_review_required"):
                findings.append(_finding("INDEPENDENT_REVIEW_NOT_REQUIRED_BY_RUN", qid))
            if not requirements.get("question_anchor_binding_required"):
                findings.append(_finding("QUESTION_ARTICLE_BINDING_NOT_REQUIRED_BY_RUN", qid))
            ids = [x.get("id") for x in run.get("questions") or [] if isinstance(x, dict)]
            if ids.count(qid) != 1:
                findings.append(_finding("CANDIDATE_QUESTION_NOT_UNIQUE_IN_RUN", qid))
            # The entire governed gate includes author self-audit, artifact/hash,
            # 12-ask reviews, preattempt W and interactive Chromium receipts.
            try:
                gate_problems = qrt_pipeline_gate.check(run)
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
                findings.append(_finding("GOVERNED_QRT_GATE_EXCEPTION", qid, str(exc)))
                gate_problems = []
            for problem in gate_problems:
                findings.append(_finding("GOVERNED_QRT_GATE_FAILURE", qid, problem))
            matches = [x for x in run.get("reviews") or []
                       if isinstance(x, dict) and x.get("question_ref") == qid
                       and x.get("basis") != "AUTHOR_ONLY"]
            if len(matches) != 1:
                findings.append(_finding("QUESTION_RENDERED_REVIEW_COUNT_INVALID", qid, str(len(matches))))
            elif matches:
                review = matches[0]
                review_basis = str(review.get("basis") or "RENDERED")
                bound_artifact = review.get("artifact_ref")
                judgements = review.get("judgements") or {}
                for ask in qrt_pipeline_gate.pipeline_guard.ASKS:
                    answer = judgements.get(ask) if isinstance(judgements, dict) else None
                    answer = answer if isinstance(answer, dict) else {}
                    reviewed_asks[ask] = str(
                        answer.get("verdict") or
                        ("NOT_APPLICABLE" if answer.get("applicability") == "NOT_APPLICABLE" else "MISSING")
                    )
            reviews = matches
    else:
        reviews = []

    return {
        "question_ref": qid or None,
        "run_path": row.get("run", {}).get("path") if isinstance(row.get("run"), dict) else None,
        "run_head_sha": head_from_run,
        "review_basis": review_basis,
        "resolved_qrt_cell": selected_cell,
        "resolved_primary_demand": demand,
        "derived_difficulty_band": band,
        "artifact_ref": bound_artifact,
        "ask_verdicts": reviewed_asks,
        "tracked_input_count": len(inputs),
        "status": _status(findings, reviews),
        "findings": findings,
        "academic_acceptance": "NOT_EVALUATED",
        "source_rights": "NOT_EVALUATED",
        "learner_trial": "NOT_EVALUATED",
    }


def report(index: dict, *, repo: Path, head: str) -> dict:
    items = index.get("items")
    if index.get("schema") != "qrt-coverage-index/v1" or not isinstance(items, list):
        return {"schema": "qrt-coverage-report/v1", "head_sha": head,
                "passed_scoped_evidence": False, "empty_scope": True, "rows": [],
                "findings": [_finding("COVERAGE_INDEX_INVALID", "index")]}
    rows = [candidate(repo, item, head=head) for item in items]
    names = [row["question_ref"] for row in rows]
    findings = [_finding("CANDIDATE_DUPLICATE", str(name))
                for name in sorted(set(names), key=str) if names.count(name) > 1]
    return {
        "schema": "qrt-coverage-report/v1",
        "head_sha": head,
        "scope": "EXPLICIT_NEW_OR_CHANGED_QUESTION_CANDIDATES_ONLY",
        "candidate_count": len(rows),
        "empty_scope": not rows,
        "passed_scoped_evidence": bool(rows) and not findings and all(
            x["status"] == "REVIEW_EVIDENCE_COMPLETE_NOT_ACCEPTANCE" for x in rows
        ),
        "rows": rows,
        "findings": findings,
        "academic_acceptance": "NOT_EVALUATED",
        "repository_wide_qrt_acceptance": "NOT_EVALUATED",
        "source_rights": "NOT_EVALUATED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--index", type=Path, default=REPO / "docs/qrt-coverage-index.v1.json")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--enforce-scoped", action="store_true",
                        help="Fail for empty scope, missing, stale or rework-required candidate")
    args = parser.parse_args(argv)
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True,
                         text=True, check=False)
    if rev.returncode or not SHA.fullmatch(rev.stdout.strip()):
        print("Cannot identify exact checkout HEAD", file=sys.stderr)
        return 2
    try:
        index = _load_json(args.index)
        result = report(index, repo=REPO, head=rev.stdout.strip())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"COVERAGE_INDEX_UNREADABLE: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(text, end="")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    return 1 if args.enforce_scoped and not result["passed_scoped_evidence"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
