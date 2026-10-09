#!/usr/bin/env python3
"""Validate one minimal-prompt QRT authoring run end to end.

This is an orchestration/evidence guard, not a second academic or render gate.
It verifies that a run preserves owner truth, keeps QRT slot semantics honest,
binds semantic review to exact rendered bytes, protects W across pre-attempt
reachable resources, uses real Blueprint refs, and does not promote question
clusters into Core1A authority without canonical truth refs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Any

REPO = Path(__file__).resolve().parents[2]
BLUEPRINTS = REPO / "Shared/web/interactive-page-blueprints.v1.json"
ASKS = ("H1", "H2", "H3", "S1", "S2", "S3", "P1", "P2", "P3", "M1", "M2", "M3")
VERDICTS = {"YES", "PARTLY", "NO"}
LAYER_STATUSES = {"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"}


class GuardError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GuardError(f"{path}: expected object")
    return value


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def blueprint_pairs(registry: dict[str, Any]) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for row in registry.get("blueprints") or []:
        if isinstance(row, dict) and row.get("id") and row.get("version"):
            out.add((str(row["id"]), str(row["version"])))
    return out


def split_blueprint_ref(ref: str) -> tuple[str, str] | None:
    if "@" not in ref:
        return None
    left, right = ref.rsplit("@", 1)
    return (left, right) if left and right else None


def validate_owner_truth(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    prompt = run.get("owner_prompt") or {}
    text = str(prompt.get("text") or "")
    digest = str(prompt.get("sha256") or "")
    actual = sha256_text(text)
    if digest != actual:
        problems.append(f"OWNER_PROMPT_DIGEST_MISMATCH: declared {digest}, actual {actual}")

    events = {str(row.get("id")): row for row in run.get("owner_events") or [] if isinstance(row, dict) and row.get("id")}
    profile = run.get("learner_profile") or {}
    purpose_ref = str(profile.get("purpose_owner_event_ref") or "")
    if purpose_ref not in events:
        problems.append("LEARNER_PURPOSE_HAS_NO_OWNER_EVENT")
    for capability, row in (profile.get("held") or {}).items():
        if not isinstance(row, dict):
            problems.append(f"LEARNER_STATE_INVALID: {capability}")
            continue
        ref = str(row.get("owner_event_ref") or "")
        if ref not in events:
            problems.append(f"LEARNER_STATE_HAS_NO_OWNER_EVENT: {capability}")

    for event_id, row in events.items():
        if not str(row.get("source_ref") or "").strip():
            problems.append(f"OWNER_EVENT_SOURCE_REF_MISSING: {event_id}")
        if not str(row.get("text") or "").strip():
            problems.append(f"OWNER_EVENT_TEXT_MISSING: {event_id}")

    for question in run.get("questions") or []:
        if not isinstance(question, dict):
            continue
        qid = str(question.get("id") or "<unknown>")
        if question.get("owner_prompt_sha256") != digest:
            problems.append(f"QUESTION_PROMPT_DIGEST_MISMATCH: {qid}")
        verbatim = str(question.get("verbatim_text") or "")
        if not verbatim or verbatim not in text:
            problems.append(f"QUESTION_NOT_VERBATIM_FROM_OWNER_PROMPT: {qid}")
    return problems


def validate_slots(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    held = (run.get("learner_profile") or {}).get("held") or {}
    for question in run.get("questions") or []:
        if not isinstance(question, dict):
            continue
        qid = str(question.get("id") or "<unknown>")
        slots = question.get("slots") or {}
        try:
            x = str(slots["X"]["text"])
            y = str(slots["Y"]["text"])
            y_cap = str(slots["Y"]["capability_ref"])
            z = str(slots["Z"]["text"])
            w = str(slots["W"]["text"])
            protected = str(slots["W"]["protected_move_ref"])
        except Exception:
            problems.append(f"QRT_SLOTS_INCOMPLETE: {qid}")
            continue

        answer = norm(question.get("verified_answer"))
        if answer and len(answer) >= 3 and answer in norm(x):
            problems.append(f"X_CONTAINS_VERIFIED_ANSWER: {qid}")
        if norm(x) in {norm(z), norm(w)}:
            problems.append(f"X_COLLAPSES_INTO_CRUX_OR_PROTECTED_WORK: {qid}")
        if not y.strip():
            problems.append(f"Y_EMPTY: {qid}")
        state = held.get(y_cap)
        if not isinstance(state, dict) or state.get("state") != "DEMONSTRATED":
            problems.append(f"Y_NOT_BACKED_BY_DEMONSTRATED_CAPABILITY: {qid}:{y_cap}")
        if norm(z) == norm(w):
            if question.get("z_w_overlap_policy") != "NO_PREATTEMPT_SCAFFOLD":
                problems.append(f"Z_W_COLLAPSE_WITH_SCAFFOLDING: {qid}")
        if not protected.strip():
            problems.append(f"W_PROTECTED_MOVE_REF_MISSING: {qid}")
    return problems


def validate_pre_attempt_graphs(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    questions = {str(q.get("id")): q for q in run.get("questions") or [] if isinstance(q, dict) and q.get("id")}
    graphs = {str(g.get("question_ref")): g for g in run.get("pre_attempt_graphs") or [] if isinstance(g, dict) and g.get("question_ref")}
    for qid, question in questions.items():
        graph = graphs.get(qid)
        if not graph:
            problems.append(f"PRE_ATTEMPT_GRAPH_MISSING: {qid}")
            continue
        nodes = {str(n.get("id")): n for n in graph.get("nodes") or [] if isinstance(n, dict) and n.get("id")}
        root = str(graph.get("root") or "")
        if root not in nodes:
            problems.append(f"PRE_ATTEMPT_ROOT_INVALID: {qid}")
            continue
        protected = str((((question.get("slots") or {}).get("W") or {}).get("protected_move_ref")) or "")
        seen: set[str] = set()
        queue = [root]
        while queue:
            node_id = queue.pop(0)
            if node_id in seen:
                continue
            seen.add(node_id)
            node = nodes[node_id]
            phase = str(node.get("phase") or "PRE_ATTEMPT")
            if phase == "POST_ATTEMPT":
                continue
            move_refs = {str(v) for v in node.get("move_refs") or []}
            if protected and protected in move_refs:
                problems.append(f"W_LEAK_PRE_ATTEMPT_REACHABLE: {qid}:{node_id}:{protected}")
            for target in node.get("links") or []:
                target = str(target)
                if target not in nodes:
                    problems.append(f"PRE_ATTEMPT_LINK_TARGET_MISSING: {qid}:{node_id}->{target}")
                elif target not in seen:
                    queue.append(target)
    return problems


def validate_blueprints(run: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    valid = blueprint_pairs(registry)
    for question in run.get("questions") or []:
        if not isinstance(question, dict):
            continue
        qid = str(question.get("id") or "<unknown>")
        ref = str(question.get("blueprint_ref") or "")
        pair = split_blueprint_ref(ref)
        if pair not in valid:
            problems.append(f"BLUEPRINT_REF_NOT_IN_ACTIVE_REGISTRY: {qid}:{ref}")
    for artifact in run.get("rendered_artifacts") or []:
        if not isinstance(artifact, dict):
            continue
        ref = artifact.get("blueprint_ref")
        if ref:
            pair = split_blueprint_ref(str(ref))
            if pair not in valid:
                problems.append(f"ARTIFACT_BLUEPRINT_REF_NOT_IN_ACTIVE_REGISTRY: {artifact.get('id')}:{ref}")
    return problems


class _QuestionArticleParser(HTMLParser):
    """Observe real rendered question units, never plain text or quoted JS strings."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.question_refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "article":
            ref = dict(attrs).get("data-g9-unit")
            if ref:
                self.question_refs.add(ref)


def validate_artifacts_and_reviews(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    head = str((run.get("run_identity") or {}).get("head_sha") or "")
    strict_binding = bool(
        (run.get("review_requirements") or {}).get("question_anchor_binding_required")
    )
    question_ids = {
        str(q.get("id")) for q in run.get("questions") or []
        if isinstance(q, dict) and q.get("id")
    }
    artifacts: dict[str, dict[str, Any]] = {}
    observed_units: dict[str, set[str]] = {}
    for artifact in run.get("rendered_artifacts") or []:
        if not isinstance(artifact, dict):
            continue
        aid = str(artifact.get("id") or "")
        path_text = str(artifact.get("path") or "")
        if not aid or not path_text:
            problems.append("RENDERED_ARTIFACT_ID_OR_PATH_MISSING")
            continue
        if aid in artifacts:
            problems.append(f"RENDERED_ARTIFACT_ID_DUPLICATE: {aid}")
            continue
        artifacts[aid] = artifact
        # Run evidence may cite only repository-relative files. Absolute or
        # escaping paths can otherwise bind QRT reviews to unrelated local bytes.
        path = (REPO / path_text).resolve()
        if Path(path_text).is_absolute() or not path.is_relative_to(REPO.resolve()):
            problems.append(f"RENDERED_ARTIFACT_PATH_OUTSIDE_REPO: {aid}:{path_text}")
            continue
        if not path.exists() or not path.is_file():
            problems.append(f"RENDERED_ARTIFACT_MISSING: {aid}:{path_text}")
            continue
        if path.stat().st_size == 0:
            problems.append(f"RENDERED_ARTIFACT_EMPTY: {aid}:{path_text}")
            continue
        actual = sha256_file(path)
        if artifact.get("sha256") != actual:
            problems.append(f"RENDERED_ARTIFACT_DIGEST_MISMATCH: {aid}")
        if artifact.get("head_sha") != head:
            problems.append(f"RENDERED_ARTIFACT_HEAD_MISMATCH: {aid}")
        if strict_binding:
            if path.suffix.lower() != ".html":
                problems.append(f"QRT_QUESTION_ARTIFACT_NOT_HTML: {aid}")
                continue
            try:
                parser = _QuestionArticleParser()
                parser.feed(path.read_text(encoding="utf-8"))
                observed_units[aid] = parser.question_refs
            except (UnicodeError, OSError) as exc:
                problems.append(f"QRT_QUESTION_ARTIFACT_UNREADABLE: {aid}:{type(exc).__name__}")

    review_by_question: dict[str, dict[str, Any]] = {}
    independent_reviewed_questions: set[str] = set()
    for review in run.get("reviews") or []:
        if not isinstance(review, dict):
            continue
        basis = review.get("basis", "RENDERED")
        if basis == "AUTHOR_ONLY":
            continue  # Retain author assessments without promoting them to post-render evidence.
        if basis not in {"RENDERED", "INDEPENDENT_RENDERED"}:
            problems.append(f"REVIEW_BASIS_INVALID: {review.get('question_ref')}")
            continue
        qid = str(review.get("question_ref") or "")
        if strict_binding and qid not in question_ids:
            problems.append(f"QRT_REVIEW_QUESTION_UNKNOWN: {qid}")
        if qid:
            if strict_binding and qid in review_by_question:
                problems.append(f"QRT_REVIEW_QUESTION_DUPLICATE: {qid}")
            review_by_question[qid] = review
        if basis == "INDEPENDENT_RENDERED":
            reviewer_ref = str(review.get("reviewer_ref") or "").strip()
            if not reviewer_ref:
                problems.append(f"INDEPENDENT_REVIEWER_REF_MISSING: {qid}")
            elif qid:
                independent_reviewed_questions.add(qid)
        aid = str(review.get("artifact_ref") or "")
        artifact = artifacts.get(aid)
        if not artifact:
            problems.append(f"REVIEW_ARTIFACT_UNKNOWN: {qid}:{aid}")
            continue
        if review.get("artifact_sha256") != artifact.get("sha256"):
            problems.append(f"REVIEW_NOT_BOUND_TO_RENDERED_BYTES: {qid}:{aid}")
        if strict_binding:
            declared = artifact.get("question_refs") or []
            if qid not in declared:
                problems.append(f"QRT_REVIEW_QUESTION_NOT_DECLARED_IN_ARTIFACT: {qid}:{aid}")
            if qid not in observed_units.get(aid, set()):
                problems.append(f"QRT_REVIEW_QUESTION_NOT_RENDERED_IN_ARTIFACT: {qid}:{aid}")
        judgements = review.get("judgements") or {}
        for ask in ASKS:
            row = judgements.get(ask)
            if not isinstance(row, dict):
                problems.append(f"QRT_JUDGEMENT_MISSING: {qid}:{ask}")
                continue
            if row.get("applicability") == "NOT_APPLICABLE":
                if not str(row.get("reason") or "").strip():
                    problems.append(f"QRT_NA_REASON_MISSING: {qid}:{ask}")
                continue
            verdict = row.get("verdict")
            if verdict not in VERDICTS:
                problems.append(f"QRT_VERDICT_INVALID: {qid}:{ask}:{verdict}")
                continue
            if not str(row.get("evidence") or "").strip():
                problems.append(f"QRT_EVIDENCE_MISSING: {qid}:{ask}")
            if verdict in {"PARTLY", "NO"} and not str(row.get("fix") or "").strip():
                problems.append(f"QRT_FIX_MISSING: {qid}:{ask}")

    require_independent = bool(
        (run.get("review_requirements") or {}).get("independent_rendered_review_required")
    )
    for question in run.get("questions") or []:
        if not isinstance(question, dict):
            continue
        qid = str(question.get("id") or "")
        if qid not in review_by_question:
            problems.append(f"POST_RENDER_QRT_REVIEW_MISSING: {question.get('id')}")
        if require_independent and qid not in independent_reviewed_questions:
            problems.append(f"INDEPENDENT_RENDERED_QRT_REVIEW_MISSING: {question.get('id')}")
    return problems


def validate_core1a_boundary(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    questions = {str(q.get("id")): q for q in run.get("questions") or [] if isinstance(q, dict) and q.get("id")}
    for row in run.get("concept_evidence") or []:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("id") or "<unknown>")
        qrefs = [str(v) for v in row.get("question_refs") or []]
        for qref in qrefs:
            if qref not in questions:
                problems.append(f"CONCEPT_EVIDENCE_QUESTION_UNKNOWN: {cid}:{qref}")
        intent = row.get("publication_intent")
        truth = [str(v) for v in row.get("canonical_truth_refs") or [] if str(v).strip()]
        unit_ref = str(row.get("core1a_unit_ref") or "")
        if intent == "PUBLISH_CORE1A":
            if not truth:
                problems.append(f"CORE1A_CANONICAL_TRUTH_MISSING: {cid}")
            if not unit_ref:
                problems.append(f"CORE1A_UNIT_REF_MISSING: {cid}")
            for qref in qrefs:
                targets = [str(v) for v in (questions[qref].get("core1a_targets") or [])]
                if unit_ref and unit_ref not in targets:
                    problems.append(f"CORE2_TO_CORE1A_LINEAGE_MISSING: {qref}->{unit_ref}")
    return problems


def validate_purpose_delivery(run: dict[str, Any], *, rendered: bool = False) -> list[str]:
    """Validate an opt-in purpose projection without retroactively invalidating older accepted runs."""
    delivery = run.get("purpose_delivery")
    if delivery is None:
        return []
    if not isinstance(delivery, dict):
        return ["PURPOSE_DELIVERY_INVALID"]
    problems: list[str] = []
    purpose = str((run.get("learner_profile") or {}).get("purpose") or "")
    declared = str(delivery.get("purpose") or "")
    if declared != purpose:
        problems.append(f"PURPOSE_DELIVERY_MISMATCH: profile={purpose}:delivery={declared}")

    expected_support = {"REVISION": "REDUCED_SUPPORT", "COMPETITION": "NO_MID_TASK_BRIDGING"}.get(purpose)
    expected_section = {"REVISION": "NEXT_LEVEL", "COMPETITION": "CHALLENGE_SET"}.get(purpose)
    if expected_support and delivery.get("support_policy") != expected_support:
        problems.append(
            f"PURPOSE_SUPPORT_POLICY_INVALID: {purpose}:{delivery.get('support_policy')} expected {expected_support}"
        )

    item_rows = [row for row in delivery.get("items") or [] if isinstance(row, dict)]
    by_id = {str(row.get("id") or ""): row for row in item_rows if str(row.get("id") or "")}
    projection = delivery.get("projection") or {}
    for role in ("CORE1A", "CORE2"):
        row = projection.get(role)
        if not isinstance(row, dict):
            problems.append(f"PURPOSE_PROJECTION_MISSING: {purpose}:{role}")
            continue
        if expected_section and row.get("section_kind") != expected_section:
            problems.append(
                f"PURPOSE_SECTION_KIND_INVALID: {purpose}:{role}:{row.get('section_kind')} expected {expected_section}"
            )
        refs = [str(value) for value in row.get("item_refs") or [] if str(value)]
        if not refs:
            problems.append(f"PURPOSE_PROJECTION_EMPTY: {purpose}:{role}")
        for ref in refs:
            item = by_id.get(ref)
            if item is None:
                problems.append(f"PURPOSE_ITEM_UNKNOWN: {purpose}:{role}:{ref}")
                continue
            if role not in (item.get("roles") or []):
                problems.append(f"PURPOSE_ITEM_ROLE_MISMATCH: {purpose}:{role}:{ref}")

    for item_id, item in by_id.items():
        source_kind = str(item.get("source_kind") or "")
        source_ref = str(item.get("source_ref") or "").strip()
        source_label = str(item.get("source_label") or "").strip()
        if source_kind == "VERIFIED_COMPETITIVE_SOURCE":
            if not source_ref.startswith("https://") or not source_label:
                problems.append(f"PURPOSE_VERIFIED_SOURCE_INCOMPLETE: {item_id}")
        elif source_kind == "AUTHOR_CREATED_COMPETITION_STYLE":
            if purpose != "COMPETITION":
                problems.append(f"PURPOSE_SOURCE_KIND_WRONG_FOR_MODE: {purpose}:{item_id}:{source_kind}")
            if not source_label:
                problems.append(f"PURPOSE_ORIGINAL_SOURCE_LABEL_MISSING: {item_id}")
        elif source_kind == "AUTHOR_CREATED_REVISION_TRANSFER":
            if purpose != "REVISION":
                problems.append(f"PURPOSE_SOURCE_KIND_WRONG_FOR_MODE: {purpose}:{item_id}:{source_kind}")
        else:
            problems.append(f"PURPOSE_SOURCE_KIND_INVALID: {item_id}:{source_kind}")

    if rendered and not problems:
        artifacts = {
            str(row.get("id") or ""): row
            for row in run.get("rendered_artifacts") or []
            if isinstance(row, dict)
        }
        for role in ("CORE1A", "CORE2"):
            artifact = artifacts.get(role)
            if not artifact:
                problems.append(f"PURPOSE_RENDERED_ARTIFACT_MISSING: {role}")
                continue
            path_text = str(artifact.get("path") or "")
            path = REPO / path_text
            if not path.is_file():
                continue  # validate_artifacts_and_reviews owns the missing-file error.
            html = path.read_text(encoding="utf-8")
            if f'data-g9-purpose-delivery="{purpose}"' not in html:
                problems.append(f"PURPOSE_RENDER_MARKER_MISSING: {role}:{purpose}")
            refs = [str(value) for value in ((projection.get(role) or {}).get("item_refs") or [])]
            for ref in refs:
                if f'data-g9-purpose-item="{ref}"' not in html:
                    problems.append(f"PURPOSE_RENDER_ITEM_MISSING: {role}:{ref}")
    return problems


def validate_validation_layers(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    validation = run.get("validation") or {}
    if "overall" in validation or "overall_status" in validation:
        problems.append("AGGREGATE_SELF_CERTIFICATION_FORBIDDEN")
    for layer in ("academic", "qrt_semantic", "static", "browser", "print"):
        row = validation.get(layer)
        if not isinstance(row, dict):
            problems.append(f"VALIDATION_LAYER_MISSING: {layer}")
            continue
        status = row.get("status")
        if status not in LAYER_STATUSES:
            problems.append(f"VALIDATION_STATUS_INVALID: {layer}:{status}")
        if status == "PASS" and not str(row.get("evidence_ref") or "").strip():
            problems.append(f"VALIDATION_PASS_WITHOUT_EVIDENCE: {layer}")
    return problems


def validate_basis_digests(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    basis = run.get("basis_digests") or {}
    for key in ("matrix", "adapter", "profile", "blueprint_registry"):
        value = str(basis.get(key) or "")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", value):
            problems.append(f"BASIS_DIGEST_MISSING_OR_INVALID: {key}")
    return problems


def check(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if run.get("schema") != "qrt-pipeline-run/v1":
        return ["schema must be qrt-pipeline-run/v1"]
    try:
        registry = load(BLUEPRINTS)
    except Exception as exc:
        return [f"BLUEPRINT_REGISTRY_LOAD_FAILED: {exc}"]
    problems.extend(validate_owner_truth(run))
    problems.extend(validate_basis_digests(run))
    problems.extend(validate_slots(run))
    problems.extend(validate_pre_attempt_graphs(run))
    problems.extend(validate_blueprints(run, registry))
    problems.extend(validate_artifacts_and_reviews(run))
    problems.extend(validate_core1a_boundary(run))
    problems.extend(validate_purpose_delivery(run, rendered=True))
    problems.extend(validate_validation_layers(run))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, help="qrt-pipeline-run/v1 JSON")
    args = parser.parse_args(argv)
    try:
        run = load(args.run)
        problems = check(run)
    except (OSError, json.JSONDecodeError, GuardError) as exc:
        print(f"load failed: {exc}")
        return 1
    if problems:
        for problem in problems:
            print(problem)
        return 1
    print("ok: qrt minimal-prompt pipeline run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
