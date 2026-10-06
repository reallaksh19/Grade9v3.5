#!/usr/bin/env python3
"""Compile and verify the 7-demand x 4-band Question Review Template matrix."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from Shared.tools import question_difficulty
except ModuleNotFoundError:  # Script entry point: python Shared/tools/<tool>.py
    import question_difficulty  # type: ignore

REPO = Path(__file__).resolve().parents[2]
VOCAB_PATH = REPO / "Shared" / "vocabularies" / "cognitive-demand.v1.json"
MATRIX_PATH = REPO / "Shared" / "quality" / "question-demand-matrix.v1.json"
GENERATED_PATH = REPO / "Shared" / "quality" / "question-demand-templates.v1.json"
ADAPTER_SCHEMA_PATH = REPO / "Shared" / "quality" / "demand-review-adapter.schema.json"

DEMANDS = ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
BANDS = ("D1", "D2", "D3", "D4")
ASKS = ("H1", "H2", "H3", "S1", "S2", "S3", "P1", "P2", "P3", "M1", "M2", "M3")
TARGETS = ("X", "Y", "Z", "W", "wrong_idea", "replacement_rule", "visual_job", "check_job")
FORBIDDEN_SCORE_KEYS = {"score", "scores", "points", "weight", "weights", "threshold", "thresholds"}
VERDICTS = ("YES", "PARTLY", "NO")
SEVERITIES = ("S0", "S1", "S2", "S3")


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



def canonical_digest(value: Any) -> str:
    material = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(material).hexdigest()


def _question_difficulty(question: dict[str, Any]) -> dict[str, Any]:
    direct = question.get("difficulty")
    analysis = ((question.get("extensions") or {}).get("grade9v3:analysis") or {})
    difficulty = direct if isinstance(direct, dict) else analysis.get("difficulty")
    qid = str(question.get("id") or "<unknown>")
    try:
        return question_difficulty.derive(difficulty, question_ref=qid)
    except question_difficulty.DifficultyContractError as exc:
        raise QRTContractError(str(exc)) from exc


def _question_band(question: dict[str, Any]) -> str:
    return str(_question_difficulty(question)["band"])


def _question_demand(question: dict[str, Any]) -> dict[str, Any]:
    extension = ((question.get("extensions") or {}).get("grade9v3:cognitive_demand"))
    if not isinstance(extension, dict):
        raise QRTContractError(f"COGNITIVE_DEMAND_MISSING: {question.get('id', '<unknown>')}")
    primary = extension.get("primary")
    if primary not in DEMANDS:
        raise QRTContractError(f"COGNITIVE_DEMAND_INVALID: {primary!r}")
    secondary = extension.get("secondary") or []
    if not isinstance(secondary, list) or any(item not in DEMANDS or item == primary for item in secondary):
        raise QRTContractError("COGNITIVE_DEMAND_SECONDARY_INVALID")
    basis = extension.get("basis")
    if not isinstance(basis, str) or not basis.strip():
        raise QRTContractError("COGNITIVE_DEMAND_BASIS_MISSING")
    return {"primary": primary, "secondary": secondary, "basis": basis}


def _analysis(question: dict[str, Any]) -> dict[str, Any]:
    value = ((question.get("extensions") or {}).get("grade9v3:analysis") or {})
    return value if isinstance(value, dict) else {}


def _reasoning_move(question: dict[str, Any], ref: str | None) -> dict[str, Any] | None:
    if not ref:
        return None
    route = ((question.get("answer") or {}).get("reasoning_route") or [])
    for move in route:
        if isinstance(move, dict) and move.get("id") == ref:
            return move
    return None


def _candidate(text: str, *basis: str) -> dict[str, Any]:
    return {"text": text, "basis": [item for item in basis if item]}


def resolve_slots(question: dict[str, Any], profile: dict[str, Any], template: dict[str, Any]) -> dict[str, dict[str, Any]]:
    held = profile.get("held") or {}
    if not isinstance(held, dict):
        raise QRTContractError("PROFILE_HELD_INVALID")
    capabilities = [
        ref for ref in [question.get("primary_capability_ref"), *(question.get("secondary_capability_refs") or [])]
        if isinstance(ref, str) and ref
    ]
    uncertain = next((ref for ref in capabilities if held.get(ref) in ("UNCERTAIN", "MISSING")), None)
    demonstrated = next((ref for ref in capabilities if held.get(ref) == "DEMONSTRATED"), None)
    if demonstrated is None:
        demonstrated = next((ref for ref, state in held.items() if state == "DEMONSTRATED"), None)

    analysis = _analysis(question)
    stable_crux = analysis.get("stable_crux_move")
    wrong_route = analysis.get("common_wrong_route")
    answer = question.get("answer") or {}
    crux_ref = answer.get("crux_move_ref")
    crux_move = _reasoning_move(question, crux_ref)
    protected_ref = ((question.get("transfer") or {}).get("protected_move_ref"))
    protected_move = _reasoning_move(question, protected_ref)

    x_text = stable_crux if isinstance(stable_crux, str) and stable_crux.strip() else template["slots"]["X"]
    x_basis = ["extensions.grade9v3:analysis.stable_crux_move"] if x_text == stable_crux else ["template.slots.X"]
    if uncertain:
        x_text = f"{x_text} Learner uncertainty: {uncertain} is {held[uncertain]}."
        x_basis.append(f"profile.held.{uncertain}")

    if demonstrated:
        y_text = demonstrated
        y_basis = [f"profile.held.{demonstrated}"]
    else:
        y_text = "UNRESOLVED: no DEMONSTRATED bridge is available in the supplied profile"
        y_basis = ["profile.held"]

    if crux_move and isinstance(crux_move.get("action"), str):
        z_text = crux_move["action"]
        z_basis = [f"answer.reasoning_route[{crux_ref}].action", "answer.crux_move_ref"]
    elif isinstance(stable_crux, str) and stable_crux.strip():
        z_text = stable_crux
        z_basis = ["extensions.grade9v3:analysis.stable_crux_move"]
    else:
        z_text = template["slots"]["Z"]
        z_basis = ["template.slots.Z"]

    if protected_move and isinstance(protected_move.get("action"), str):
        w_text = protected_move["action"]
        w_basis = [f"answer.reasoning_route[{protected_ref}].action", "transfer.protected_move_ref"]
    elif crux_move and isinstance(crux_move.get("action"), str):
        w_text = crux_move["action"]
        w_basis = [f"answer.reasoning_route[{crux_ref}].action", "answer.crux_move_ref"]
    elif isinstance(stable_crux, str) and stable_crux.strip():
        w_text = stable_crux
        w_basis = ["extensions.grade9v3:analysis.stable_crux_move"]
    else:
        w_text = template["slots"]["W"].split(". Band protection:", 1)[0]
        w_basis = ["template.slots.W"]

    wrong_text = wrong_route if isinstance(wrong_route, str) and wrong_route.strip() else template["slots"]["wrong_idea"]
    wrong_basis = ["extensions.grade9v3:analysis.common_wrong_route"] if wrong_text == wrong_route else ["template.slots.wrong_idea"]

    return {
        "X": _candidate(x_text, *x_basis),
        "Y": _candidate(y_text, *y_basis),
        "Z": _candidate(z_text, *z_basis),
        "W": _candidate(w_text, *w_basis),
        "wrong_idea": _candidate(wrong_text, *wrong_basis),
        "replacement_rule": _candidate(template["slots"]["replacement_rule"], "template.slots.replacement_rule"),
        "visual_job": _candidate(template["slots"]["visual_job"], "template.slots.visual_job"),
        "check_job": _candidate(template["slots"]["check_job"], "template.slots.check_job"),
    }


def resolve_review(question: dict[str, Any], profile: dict[str, Any], matrix: dict[str, Any], vocab: dict[str, Any]) -> dict[str, Any]:
    demand = _question_demand(question)
    difficulty = _question_difficulty(question)
    band = str(difficulty["band"])
    template = next(row for row in compile_templates(matrix, vocab)
                    if row["demand"] == demand["primary"] and row["band"] == band)
    slots = resolve_slots(question, profile, template)
    values = {key: row["text"] for key, row in slots.items()}
    values["band_protected_work"] = template["band_policy"]["protected_work"]
    review = {
        ask: {
            "verb": row["verb"],
            "objective": _fill(row["objective"], values),
            "question": _fill(row["question"], values),
        }
        for ask, row in matrix["review_asks"].items()
    }
    return {
        "schema": "question-review-resolution/v1",
        "template_id": template["template_id"],
        "question_ref": question.get("id"),
        "profile_ref": profile.get("profile_id"),
        "classification": {
            "demand": demand,
            "band": band,
            "requested_band": difficulty.get("requested_band"),
            "difficulty_score": difficulty["score"],
        },
        "basis_digests": {
            "question": canonical_digest(question),
            "profile": canonical_digest(profile),
            "matrix": canonical_digest(matrix),
            "vocabulary": canonical_digest(vocab),
            "difficulty_metadata": canonical_digest(question_difficulty.metadata()),
        },
        "slots": slots,
        "review": review,
    }




def validate_subject_adapter(adapter: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if adapter.get("schema") != "demand-review-adapter/v1":
        problems.append("adapter schema must be demand-review-adapter/v1")
    subject = adapter.get("subject")
    if subject not in ("Physics", "Chemistry", "Mathematics"):
        problems.append(f"adapter subject invalid: {subject!r}")
    demands = adapter.get("demands") or {}
    if tuple(demands) != DEMANDS:
        problems.append(f"adapter demands must be exactly {list(DEMANDS)} in order")
    vocab_ref = adapter.get("vocabulary_ref")
    vocab_path = REPO / str(vocab_ref or "")
    try:
        subject_vocab = load(vocab_path)
    except (OSError, json.JSONDecodeError, QRTContractError) as exc:
        problems.append(f"adapter vocabulary_ref cannot be loaded: {exc}")
        return problems
    if subject_vocab.get("subject") != subject:
        problems.append("adapter subject does not match its QualityVocabulary subject")
    known_reps = set(subject_vocab.get("representation_kinds") or [])
    known_checks = set(subject_vocab.get("check_types") or [])
    for demand in DEMANDS:
        row = demands.get(demand)
        if not isinstance(row, dict):
            continue
        if not isinstance(row.get("review_focus"), str) or not row["review_focus"].strip():
            problems.append(f"{demand}.review_focus: non-empty text required")
        reps = row.get("representation_kinds")
        checks = row.get("check_types")
        if not isinstance(reps, list) or any(item not in known_reps for item in reps):
            problems.append(f"{demand}.representation_kinds contains values outside {vocab_ref}")
        if not isinstance(checks, list) or any(item not in known_checks for item in checks):
            problems.append(f"{demand}.check_types contains values outside {vocab_ref}")
        misconceptions = row.get("misconception_patterns")
        if not isinstance(misconceptions, list) or not misconceptions:
            problems.append(f"{demand}.misconception_patterns: at least one pattern required")
        else:
            for index, item in enumerate(misconceptions):
                if not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip()
                                                     for k in ("wrong_idea", "diagnostic_prompt", "repair")):
                    problems.append(f"{demand}.misconception_patterns[{index}]: wrong_idea/diagnostic_prompt/repair required")
    return problems


def specialize_resolution(resolution: dict[str, Any], adapter: dict[str, Any]) -> dict[str, Any]:
    problems = validate_subject_adapter(adapter)
    if problems:
        raise QRTContractError("; ".join(problems))
    demand = ((resolution.get("classification") or {}).get("demand") or {}).get("primary")
    if demand not in DEMANDS:
        raise QRTContractError("RESOLUTION_DEMAND_INVALID")
    out = copy.deepcopy(resolution)
    out["subject"] = adapter["subject"]
    out["subject_adapter"] = {
        "schema": adapter["schema"],
        "version": adapter["version"],
        "subject": adapter["subject"],
        "demand": demand,
        "guidance": copy.deepcopy(adapter["demands"][demand]),
        "basis_refs": copy.deepcopy(adapter.get("basis_refs") or []),
        "adapter_digest": canonical_digest(adapter),
    }
    return out

def project_product_review_findings(
    resolution: dict[str, Any],
    judgements: dict[str, Any],
) -> dict[str, Any]:
    """Project actionable QRT judgements into product-review/v2 finding-shaped rows.

    YES judgements are not defects and therefore emit no finding. NO defaults to S2 and PARTLY to S3,
    matching the quality-by-objective proposal; callers may explicitly change severity when the
    actual learner impact warrants it (for example a spoiler may be S1).
    """
    review = resolution.get("review") or {}
    findings: list[dict[str, Any]] = []
    for ask in ASKS:
        judgement = judgements.get(ask)
        if judgement is None:
            continue
        if not isinstance(judgement, dict):
            raise QRTContractError(f"JUDGEMENT_INVALID: {ask}")
        verdict = judgement.get("verdict")
        if verdict not in VERDICTS:
            raise QRTContractError(f"VERDICT_INVALID: {ask}={verdict!r}")
        if verdict == "YES":
            continue
        row = review.get(ask)
        if not isinstance(row, dict):
            raise QRTContractError(f"RESOLUTION_REVIEW_MISSING: {ask}")
        severity = judgement.get("severity") or ("S2" if verdict == "NO" else "S3")
        if severity not in SEVERITIES:
            raise QRTContractError(f"SEVERITY_INVALID: {ask}={severity!r}")
        evidence = judgement.get("evidence")
        if isinstance(evidence, list):
            evidence_text = "; ".join(str(item) for item in evidence if str(item).strip())
        else:
            evidence_text = str(evidence or "").strip()
        fix = str(judgement.get("fix") or "").strip()
        page = str(judgement.get("page") or "").strip()
        findings.append({
            "id": f"QRT-{resolution.get('question_ref')}-{ask}",
            "severity": severity,
            "kind": "figure" if ask.startswith("S") else "content",
            "record": str(resolution.get("question_ref") or ""),
            "page": page,
            "learner_impact": f"{ask} {verdict}: {row['objective']}",
            "detail": f"{row['question']}" + (f" Evidence: {evidence_text}" if evidence_text else ""),
            "suggested_fix": fix,
            "asks": ask,
        })
    return {
        "profile_ref": resolution.get("profile_ref"),
        "question_ref": resolution.get("question_ref"),
        "template_id": resolution.get("template_id"),
        "basis_digests": copy.deepcopy(resolution.get("basis_digests") or {}),
        "findings": findings,
    }


def _require_quality_gate_report(report: dict[str, Any], label: str) -> None:
    if report.get("schema") != "gate-report/v1" or report.get("tool") != "quality_gate/1":
        raise QRTContractError(f"{label}: expected tool-written gate-report/v1 from quality_gate/1")
    if not isinstance(report.get("findings"), list) or not isinstance(report.get("continuity"), list):
        raise QRTContractError(f"{label}: malformed gate report")


def _finding_identity(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("rule") or ""),
        str(row.get("where") or ""),
        str(row.get("detail") or ""),
    )


def _continuity_identity(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("code") or ""), str(row.get("detail") or ""))


def compare_quality_gate_reports(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Compare two real quality_gate/1 reports without re-evaluating any gate rule."""
    _require_quality_gate_report(before, "before")
    _require_quality_gate_report(after, "after")
    if before.get("product_id") != after.get("product_id"):
        raise QRTContractError("GATE_DELTA_PRODUCT_MISMATCH")
    if before.get("subject") != after.get("subject"):
        raise QRTContractError("GATE_DELTA_SUBJECT_MISMATCH")

    before_findings = {_finding_identity(row): row for row in before["findings"] if isinstance(row, dict)}
    after_findings = {_finding_identity(row): row for row in after["findings"] if isinstance(row, dict)}
    before_cont = {_continuity_identity(row): row for row in before["continuity"] if isinstance(row, dict)}
    after_cont = {_continuity_identity(row): row for row in after["continuity"] if isinstance(row, dict)}

    before_pages = {
        str(row.get("page")): str(row.get("sha256"))
        for row in before.get("pages") or []
        if isinstance(row, dict) and row.get("page") and row.get("sha256")
    }
    after_pages = {
        str(row.get("page")): str(row.get("sha256"))
        for row in after.get("pages") or []
        if isinstance(row, dict) and row.get("page") and row.get("sha256")
    }
    changed_pages = [
        {
            "page": page,
            "before_sha256": before_pages.get(page),
            "after_sha256": after_pages.get(page),
            "status": (
                "ADDED" if page not in before_pages
                else "REMOVED" if page not in after_pages
                else "CHANGED"
            ),
        }
        for page in sorted(set(before_pages) | set(after_pages))
        if before_pages.get(page) != after_pages.get(page)
    ]

    return {
        "schema": "qrt-gate-delta/v1",
        "product_id": after.get("product_id"),
        "subject": after.get("subject"),
        "basis_digests": {
            "before_report": canonical_digest(before),
            "after_report": canonical_digest(after),
        },
        "before": {
            "verdict": before.get("verdict"),
            "render_stamp": before.get("render_stamp"),
            "rendered_measured": before.get("rendered_measured"),
        },
        "after": {
            "verdict": after.get("verdict"),
            "render_stamp": after.get("render_stamp"),
            "rendered_measured": after.get("rendered_measured"),
        },
        "new_findings": [after_findings[key] for key in sorted(after_findings.keys() - before_findings.keys())],
        "closed_findings": [before_findings[key] for key in sorted(before_findings.keys() - after_findings.keys())],
        "persisting_findings": [after_findings[key] for key in sorted(after_findings.keys() & before_findings.keys())],
        "new_continuity": [after_cont[key] for key in sorted(after_cont.keys() - before_cont.keys())],
        "closed_continuity": [before_cont[key] for key in sorted(before_cont.keys() - after_cont.keys())],
        "persisting_continuity": [after_cont[key] for key in sorted(after_cont.keys() & before_cont.keys())],
        "changed_pages": changed_pages,
    }

def _select_question(source: dict[str, Any], question_id: str | None) -> dict[str, Any]:
    if isinstance(source.get("stem"), str) and source.get("id"):
        if question_id and source.get("id") != question_id:
            raise QRTContractError(f"QUESTION_NOT_FOUND: {question_id}")
        return source
    questions = source.get("questions")
    if not isinstance(questions, list):
        raise QRTContractError("SOURCE_HAS_NO_QUESTIONS")
    if not question_id:
        raise QRTContractError("QUESTION_ID_REQUIRED_FOR_COLLECTION")
    matches = [row for row in questions if isinstance(row, dict) and row.get("id") == question_id]
    if len(matches) != 1:
        raise QRTContractError(f"QUESTION_NOT_FOUND_OR_DUPLICATE: {question_id}")
    return matches[0]

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("compile", help="print the compiled 28-cell projection")
    write_p = sub.add_parser("write", help="regenerate the committed 28-cell projection")
    write_p.add_argument("--check", action="store_true", help="write nothing; fail when the projection is stale")
    sub.add_parser("check", help="validate the source contract and committed projection")
    resolve_p = sub.add_parser("resolve", help="resolve one question + learner profile to a concrete QRT worksheet")
    resolve_p.add_argument("--source", type=Path, required=True, help="JSON question or package/bank containing questions[]")
    resolve_p.add_argument("--question", help="question id when --source contains questions[]")
    resolve_p.add_argument("--profile", type=Path, required=True, help="learner-profile JSON")
    delta_p = sub.add_parser("gate-delta", help="compare before/after tool-written quality_gate/1 reports")
    delta_p.add_argument("--before", type=Path, required=True)
    delta_p.add_argument("--after", type=Path, required=True)
    resolve_p.add_argument("--adapter", type=Path, help="optional subject DemandReview.json specialization")
    args = parser.parse_args(argv)

    matrix, vocab = load(MATRIX_PATH), load(VOCAB_PATH)
    payload = generated_payload(matrix, vocab)

    if args.cmd == "gate-delta":
        before = load(args.before)
        after = load(args.after)
        print(dumps(compare_quality_gate_reports(before, after)), end="")
        return 0
    if args.cmd == "resolve":
        source = load(args.source)
        profile = load(args.profile)
        question = _select_question(source, args.question)
        resolution = resolve_review(question, profile, matrix, vocab)
        if args.adapter:
            resolution = specialize_resolution(resolution, load(args.adapter))
        print(dumps(resolution), end="")
        return 0
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
