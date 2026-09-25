#!/usr/bin/env python3
"""Compose a traceable Core-agent prompt bundle from owner-supplied question rows.

This is a planning layer only. Canonical curriculum/question records remain authoritative,
learner percentages remain routing coordinates only, and plan_request.py remains the
authoritative planner for readiness, prerequisites, source receipts and product holds.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import load  # noqa: E402
from Shared.tools import core_authority_contract, study_map  # noqa: E402

BRIEF_SCHEMA = REPO / "Shared/library/prompt-brief.schema.json"
AUTHORING_SCHEMA = "Shared/library/authoring-request.schema.json"
TEMPLATE_PATH = REPO / "template/core-prompt-composer/core-agent-prompt.v1.json"
ALL_CORES = ("CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
DEFAULT_EXECUTION_ORDER = ("CORE2", "CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
HOLD_STATUSES = {"AGENT_PROPOSAL_PENDING_REVIEW", "IDENTITY_HOLD", "MIXED_SUBTOPIC_HOLD", "UNMAPPED_HOLD"}
LEARNER_ELIGIBILITY = {"ELIGIBLE", "EXCLUDED", "HOLD", "NOT_ESTABLISHED"}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: object) -> str:
    body = value if isinstance(value, str) else canonical_json(value)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


def git_basis(repo: Path = REPO) -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        ).stdout.strip()
        if sha:
            return f"HEAD@{sha}"
    except (OSError, subprocess.CalledProcessError):
        pass
    return "UNRESOLVED_REPOSITORY_BASIS"


def _boards(subject: str, repo: Path = REPO) -> list[dict]:
    rows = []
    for path in sorted((repo / subject / "matrices").glob("*.rungs.json")):
        board = load(path)
        rows.append({**board, "_path": str(path.relative_to(repo))})
    return rows


def _board_by_id(subject: str, repo: Path = REPO) -> dict[str, dict]:
    return {row["matrix_id"]: row for row in _boards(subject, repo)}


def _find_rung(board: dict, rung: str) -> dict | None:
    return next((row for row in board.get("rungs", []) if row.get("rung") == rung), None)


def _location_for_primary(capability_ref: str | None, index: dict) -> tuple[dict | None, str | None]:
    if not capability_ref:
        return None, "primary capability is not supplied"
    locations = list(index.get("locations", {}).get(capability_ref, []))
    if len(locations) == 1:
        return locations[0], None
    if not locations:
        return None, f"{capability_ref} has no canonical teaching location"
    return None, f"{capability_ref} has {len(locations)} canonical teaching locations; scope is ambiguous"


def _source_custody(question: dict) -> dict | None:
    value = (question.get("extensions") or {}).get("grade9v3:source_custody")
    return value if isinstance(value, dict) else None


def _analysis(question: dict) -> dict | None:
    value = (question.get("extensions") or {}).get("grade9v3:analysis")
    return value if isinstance(value, dict) else None


def _resolve_question_row(raw: dict, index: dict, owner_scope: dict | None) -> tuple[dict, list[dict]]:
    owner_id = str(raw.get("question_id") or "").strip()
    summary = str(raw.get("summary") or "").strip()
    canonical_ref = raw.get("canonical_question_ref")
    candidates = list(dict.fromkeys(raw.get("candidate_question_refs") or []))
    canonical = index["canonical_questions"].get(canonical_ref or "") if canonical_ref else None
    holds: list[dict] = []

    eligibility = str(raw.get("learner_eligibility") or "NOT_ESTABLISHED").strip().upper()
    if eligibility not in LEARNER_ELIGIBILITY:
        holds.append({
            "status": "UNMAPPED_HOLD",
            "point": "LEARNER_ELIGIBILITY_INVALID",
            "detail": f"{owner_id}: learner_eligibility {eligibility!r} is not recognized",
        })
        eligibility = "NOT_ESTABLISHED"
    eligibility_basis = raw.get("learner_eligibility_basis")

    if not canonical_ref and candidates:
        valid_candidates = [ref for ref in candidates if ref in index["canonical_questions"]]
        unknown_candidates = [ref for ref in candidates if ref not in index["canonical_questions"]]
        detail = (
            f"{owner_id}: multiple candidate question identities require explicit exact-ref confirmation: "
            + ", ".join(valid_candidates or candidates)
        )
        if unknown_candidates:
            detail += "; unknown candidate refs: " + ", ".join(unknown_candidates)
        holds.append({
            "status": "IDENTITY_HOLD",
            "point": "QUESTION_IDENTITY_AMBIGUOUS",
            "detail": detail,
        })
        return ({
            "owner_question_id": owner_id,
            "summary": summary,
            "canonical_question_ref": None,
            "candidate_question_refs": candidates,
            "identity_status": "IDENTITY_HOLD",
            "demand_evidence_refs": valid_candidates,
            "learner_eligibility": eligibility,
            "learner_eligibility_basis": eligibility_basis,
            "mapping_basis": "UNMAPPED",
            "mapping_status": "IDENTITY_HOLD",
            "primary_capability_ref": None,
            "secondary_capability_refs": [],
            "primary_location": None,
            "record_status": None,
            "source_custody": None,
            "analysis": None,
            "finding": detail,
        }, holds)

    if canonical_ref and canonical is not None:
        primary = canonical.get("primary_capability_ref")
        secondary = list(canonical.get("secondary_capability_refs") or [])
        location, location_finding = _location_for_primary(primary, index)
        finding = location_finding
        status = "CANONICAL_MATCH" if location else "UNMAPPED_HOLD"
        if location_finding:
            holds.append({
                "status": "UNMAPPED_HOLD",
                "point": "PRIMARY_LOCATION_UNRESOLVED",
                "detail": f"{owner_id}: {location_finding}",
            })
        return ({
            "owner_question_id": owner_id,
            "summary": summary,
            "canonical_question_ref": canonical_ref,
            "candidate_question_refs": candidates,
            "identity_status": "EXACT_CONFIRMED",
            "demand_evidence_refs": [canonical_ref],
            "learner_eligibility": eligibility,
            "learner_eligibility_basis": eligibility_basis,
            "mapping_basis": "CANONICAL_QUESTION",
            "mapping_status": status,
            "primary_capability_ref": primary,
            "secondary_capability_refs": secondary,
            "primary_location": location,
            "record_status": canonical.get("status"),
            "source_custody": _source_custody(canonical),
            "analysis": _analysis(canonical),
            "finding": finding,
        }, holds)

    if canonical_ref and canonical is None:
        detail = f"{owner_id}: exact canonical_question_ref {canonical_ref} is not present; short labels or summaries are not source identity"
        return ({
            "owner_question_id": owner_id,
            "summary": summary,
            "canonical_question_ref": canonical_ref,
            "candidate_question_refs": candidates,
            "identity_status": "UNMAPPED",
            "demand_evidence_refs": [],
            "learner_eligibility": eligibility,
            "learner_eligibility_basis": eligibility_basis,
            "mapping_basis": "UNMAPPED",
            "mapping_status": "UNMAPPED_HOLD",
            "primary_capability_ref": None,
            "secondary_capability_refs": [],
            "primary_location": None,
            "record_status": None,
            "source_custody": None,
            "analysis": None,
            "finding": detail,
        }, [{"status": "UNMAPPED_HOLD", "point": "CANONICAL_QUESTION_UNKNOWN", "detail": detail}])

    basis = raw.get("mapping_basis")
    primary = raw.get("primary_capability_ref")
    secondary = list(raw.get("secondary_capability_refs") or [])
    location, location_finding = _location_for_primary(primary, index)
    shared = {
        "owner_question_id": owner_id,
        "summary": summary,
        "canonical_question_ref": None,
        "candidate_question_refs": candidates,
        "identity_status": "UNMAPPED",
        "demand_evidence_refs": [],
        "learner_eligibility": eligibility,
        "learner_eligibility_basis": eligibility_basis,
        "primary_capability_ref": primary,
        "secondary_capability_refs": secondary,
        "primary_location": location,
        "record_status": None,
        "source_custody": None,
        "analysis": None,
    }
    if basis == "AGENT_PROPOSAL":
        detail = f"{owner_id}: proposed mapping requires owner review before it can constrain a Core prompt"
        return ({
            **shared,
            "mapping_basis": "AGENT_PROPOSAL",
            "mapping_status": "AGENT_PROPOSAL_PENDING_REVIEW",
            "finding": detail,
        }, [{"status": "AGENT_PROPOSAL_PENDING_REVIEW", "point": "AGENT_MAPPING_REVIEW_REQUIRED", "detail": detail}])

    if basis == "MANUAL" and primary and location and owner_scope:
        return ({
            **shared,
            "mapping_basis": "MANUAL",
            "mapping_status": "OWNER_CONFIRMED_CANONICAL_RUNG",
            "finding": None,
        }, [])

    detail = f"{owner_id}: no exact canonical question mapping or owner-confirmed manual canonical mapping is available"
    if location_finding:
        detail += f" ({location_finding})"
    return ({
        **shared,
        "mapping_basis": "UNMAPPED",
        "mapping_status": "UNMAPPED_HOLD",
        "finding": detail,
    }, [{"status": "UNMAPPED_HOLD", "point": "QUESTION_MAPPING_UNRESOLVED", "detail": detail}])


def _resolve_scope(subject: str, rows: list[dict], owner_scope: dict | None, repo: Path) -> tuple[dict, list[dict]]:
    holds: list[dict] = []
    locations = [row["primary_location"] for row in rows if row.get("primary_location")]
    matrix_ids = sorted({row["matrix_id"] for row in locations})
    boards = _board_by_id(subject, repo)

    if not matrix_ids:
        return ({
            "status": "UNMAPPED_HOLD", "matrix_ref": None, "bucket_ref": None,
            "topic": None, "subtopic": None, "canonical_primary_rungs": [],
            "owner_confirmed_rung": owner_scope,
        }, [{"status": "UNMAPPED_HOLD", "point": "COMPOSITION_SCOPE_UNMAPPED",
             "detail": "No unique canonical primary teaching matrix can be established from the question rows."}])

    if len(matrix_ids) > 1:
        detail = "Primary question mappings span multiple matrices: " + ", ".join(matrix_ids)
        return ({
            "status": "MIXED_SUBTOPIC_HOLD", "matrix_ref": None, "bucket_ref": None,
            "topic": None, "subtopic": None,
            "canonical_primary_rungs": sorted({row.get("rung") for row in locations if row.get("rung")}),
            "owner_confirmed_rung": owner_scope,
        }, [{"status": "MIXED_SUBTOPIC_HOLD", "point": "MIXED_PRIMARY_MATRICES", "detail": detail}])

    matrix_id = matrix_ids[0]
    board = boards.get(matrix_id)
    if board is None:
        return ({
            "status": "UNMAPPED_HOLD", "matrix_ref": matrix_id, "bucket_ref": None,
            "topic": None, "subtopic": None, "canonical_primary_rungs": [],
            "owner_confirmed_rung": owner_scope,
        }, [{"status": "UNMAPPED_HOLD", "point": "MATRIX_RECORD_MISSING",
             "detail": f"{matrix_id} is referenced by capability locations but its matrix record is unavailable."}])

    primary_rungs = sorted({row.get("rung") for row in locations if row.get("rung")})
    status = "CANONICAL_MATCH"
    if len(primary_rungs) > 1:
        if not owner_scope:
            holds.append({
                "status": "UNMAPPED_HOLD",
                "point": "OWNER_RUNG_CONFIRMATION_REQUIRED",
                "detail": "Question primaries span canonical rungs " + ", ".join(primary_rungs) + "; confirm one composition rung without rewriting per-question mappings.",
            })
            status = "UNMAPPED_HOLD"
        elif owner_scope.get("matrix_id") != matrix_id or _find_rung(board, owner_scope.get("rung", "")) is None:
            holds.append({
                "status": "UNMAPPED_HOLD",
                "point": "OWNER_RUNG_CONFIRMATION_INVALID",
                "detail": "The owner-confirmed composition rung does not resolve inside the question set's canonical matrix.",
            })
            status = "UNMAPPED_HOLD"
        else:
            status = "OWNER_CONFIRMED_CANONICAL_RUNG"
    elif owner_scope:
        if owner_scope.get("matrix_id") != matrix_id or _find_rung(board, owner_scope.get("rung", "")) is None:
            holds.append({
                "status": "UNMAPPED_HOLD",
                "point": "OWNER_RUNG_CONFIRMATION_INVALID",
                "detail": "The owner-confirmed composition rung does not resolve inside the canonical matrix.",
            })
            status = "UNMAPPED_HOLD"
        else:
            status = "OWNER_CONFIRMED_CANONICAL_RUNG"

    return ({
        "status": status,
        "matrix_ref": matrix_id,
        "bucket_ref": board.get("bucket_id"),
        "topic": board.get("topic"),
        "subtopic": board.get("subtopic"),
        "canonical_primary_rungs": primary_rungs,
        "owner_confirmed_rung": owner_scope,
    }, holds)


def _fingerprint(rows: list[dict], scope: dict, subject: str, repo: Path, index: dict) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    def add(phrase: str | None, kind: str, evidence: list[str]) -> None:
        text = " ".join(str(phrase or "").split())
        key = text.casefold()
        if not text or key in seen:
            return
        seen.add(key)
        items.append({
            "keyword_id": f"KW-{len(items)+1:02d}",
            "phrase": text,
            "kind": kind,
            "evidence_refs": sorted(set(evidence)),
        })

    for row in rows:
        analysis = row.get("analysis") or {}
        canonical_ref = row.get("canonical_question_ref")
        add(analysis.get("stable_crux_move"), "QUESTION_CRUX",
            [canonical_ref] if canonical_ref else [row["owner_question_id"]])
        if not analysis.get("stable_crux_move"):
            cap = index.get("capabilities", {}).get(row.get("primary_capability_ref") or "", {})
            add(cap.get("action"), "CAPABILITY_ACTION", [row.get("primary_capability_ref") or row["owner_question_id"]])

    matrix_id = scope.get("matrix_ref")
    if matrix_id:
        board = _board_by_id(subject, repo).get(matrix_id) or {}
        family = board.get("family") or {}
        add(family.get("invariant_demand"), "MATRIX_INVARIANT", [matrix_id])
        add(family.get("difficult_move"), "MATRIX_DIFFICULT_MOVE", [matrix_id])
    if not items:
        add("No trustworthy concept fingerprint can be emitted until the question mapping is resolved.",
            "CAPABILITY_ACTION", ["COMPOSER_HOLD"])
    return items


def _validate_core_order(requested: list[str], order: list[str]) -> list[dict]:
    holds = []
    unknown = sorted({core for core in requested + order if core not in ALL_CORES})
    if unknown:
        holds.append({"status": "UNMAPPED_HOLD", "point": "UNKNOWN_CORE",
                      "detail": "Unknown Core role(s): " + ", ".join(unknown)})
    if len(requested) != len(set(requested)):
        holds.append({"status": "UNMAPPED_HOLD", "point": "DUPLICATE_REQUESTED_CORE",
                      "detail": "requested_cores must not contain duplicates."})
    if len(order) != len(set(order)) or set(order) != set(requested):
        holds.append({"status": "UNMAPPED_HOLD", "point": "CORE_ORDER_INVALID",
                      "detail": "execution_order must contain every requested Core exactly once and no others."})
    return holds


def _source_basis_hold(source_basis: list[str], rows: list[dict]) -> list[dict]:
    canonical_refs = {row["canonical_question_ref"] for row in rows if row.get("canonical_question_ref")}
    invalid = [item for item in source_basis if item in canonical_refs]
    if not invalid:
        return []
    return [{"status": "UNMAPPED_HOLD", "point": "SOURCE_BASIS_QUESTION_ID_INVALID",
             "detail": "authoring-request source_basis is a source locator/receipt basis, not canonical question IDs: " + ", ".join(invalid)}]


def _worksheet_map(doc: dict, rows: list[dict]) -> dict:
    questions = []
    for row in rows:
        if not row.get("primary_capability_ref"):
            continue
        basis = row["mapping_basis"]
        if basis == "UNMAPPED":
            continue
        q = {
            "question_id": row["owner_question_id"],
            "primary_capability_ref": row["primary_capability_ref"],
            "secondary_capability_refs": row["secondary_capability_refs"],
            "mapping_basis": basis,
        }
        if basis == "CANONICAL_QUESTION" and row.get("canonical_question_ref"):
            q["canonical_question_ref"] = row["canonical_question_ref"]
        if row.get("summary"):
            q["note"] = row["summary"]
        questions.append(q)
    return {
        "worksheet_id": doc.get("worksheet_id") or f"WS-{digest(doc)[7:19].upper()}",
        "subject": doc["subject"],
        "source_note": "Owner-supplied question set mapped by Core Prompt Composer; mapping is planning demand, not curriculum or source authority.",
        "questions": questions,
    }


def _authoring_request(doc: dict, scope: dict, brief_id: str, holds: list[dict]) -> dict:
    request = {
        "request_id": doc.get("request_id") or f"REQ-{brief_id[3:]}",
        "subject": doc["subject"],
        "requested_cores": list(doc["requested_cores"]),
    }
    if scope.get("bucket_ref"):
        request["bucket_id"] = scope["bucket_ref"]
    elif scope.get("subtopic"):
        request["subtopic"] = scope["subtopic"]

    learner = doc.get("learner")
    if learner:
        request["learner"] = learner
    if doc.get("practice"):
        request["practice"] = doc["practice"]
    if doc.get("supplemental_question_policy"):
        request["supplemental_question_policy"] = doc["supplemental_question_policy"]

    source_basis = list(doc.get("source_basis") or [])
    if source_basis and not _source_basis_hold(source_basis, []):
        request["source_basis"] = source_basis
    if doc.get("source_receipt_ref") and request.get("source_basis"):
        request["source_receipt_ref"] = doc["source_receipt_ref"]
    if doc.get("source_basis_drift_acknowledgement") and request.get("source_basis"):
        request["source_basis_drift_acknowledgement"] = doc["source_basis_drift_acknowledgement"]
    return request


def _trace(rows: list[dict], fingerprint: list[dict]) -> list[dict]:
    by_ref: dict[str, str] = {}
    for item in fingerprint:
        for ref in item["evidence_refs"]:
            by_ref.setdefault(ref, item["phrase"])
    trace = []
    for idx, row in enumerate(rows, start=1):
        loc = row.get("primary_location") or {}
        key = row.get("canonical_question_ref") or row["owner_question_id"]
        trace.append({
            "trace_id": f"trace-q-{idx:02d}",
            "question_ids": [row["owner_question_id"]],
            "input_or_owner_decision": row.get("summary") or row["owner_question_id"],
            "canonical_ref": row.get("canonical_question_ref"),
            "candidate_question_refs": row.get("candidate_question_refs") or [],
            "demand_evidence_refs": row.get("demand_evidence_refs") or [],
            "learner_eligibility": row.get("learner_eligibility"),
            "primary_capability_ref": row.get("primary_capability_ref"),
            "secondary_capability_refs": row.get("secondary_capability_refs") or [],
            "matrix_ref": loc.get("matrix_id"),
            "rung": loc.get("rung"),
            "keyword": by_ref.get(key),
            "prompt_clause": "FIXED_SOURCE_QUESTIONS;KEYWORD_FINGERPRINT",
            "mapping_basis": row.get("mapping_basis"),
            "provenance": [ref for ref in [
                row.get("canonical_question_ref"),
                loc.get("matrix_path"),
                row.get("primary_capability_ref"),
            ] if ref],
            "status": row.get("mapping_status"),
            "finding": row.get("finding"),
        })
    return trace


def _difficulty(rows: list[dict]) -> list[str]:
    bands = []
    for row in rows:
        band = (((row.get("analysis") or {}).get("difficulty") or {}).get("band"))
        if band and band not in bands:
            bands.append(band)
    return sorted(bands, key=lambda value: (int(value[1:]) if value.startswith("D") and value[1:].isdigit() else 999, value))


def render_prompt(brief: dict, template: dict, authority_contract: dict | None = None) -> str:
    role_refs = template["role_contract_refs"]
    role_guardrails = template["role_guardrails"]
    rows = brief["question_rows"]
    fingerprint = brief["keyword_fingerprint"]
    scope = brief["scope"]
    holds = brief["holds"]
    sections = []

    fixed = "\n".join(
        f"- {row['owner_question_id']}: {row['summary'] or '(no summary supplied)'}"
        + (f" [canonical: {row['canonical_question_ref']}]" if row.get("canonical_question_ref") else "")
        + (f" [candidates: {', '.join(row.get('candidate_question_refs') or [])}]" if row.get("candidate_question_refs") else "")
        + f" [mapping: {row['mapping_status']}]"
        + f" [learner eligibility: {row.get('learner_eligibility') or 'NOT_ESTABLISHED'}]"
        for row in rows
    )
    learner = brief.get("learner_entry")
    learner_text = canonical_json(learner) if learner else "No learner input supplied."
    order = " → ".join(brief["execution_order"])
    boundary = (
        f"Subject: {brief['subject']}. Matrix: {scope.get('matrix_ref') or 'UNRESOLVED'}. "
        f"Bucket: {scope.get('bucket_ref') or 'UNRESOLVED'}. "
        f"Canonical primary rungs represented: {', '.join(scope.get('canonical_primary_rungs') or []) or 'none'}. "
        f"Composition scope status: {scope['status']}."
    )
    core_lines = "\n".join(
        f"- {core}: {role_guardrails[core]} Contract: {role_refs[core]}"
        for core in brief["requested_cores"]
    )
    authority_contract = authority_contract or core_authority_contract.load_contract()
    authority_lines = []
    for core in brief["requested_cores"]:
        rule = authority_contract["roles"][core]
        required = ", ".join(rule.get("required_authority") or []) or "none"
        one_of = ", ".join(rule.get("one_of_authority") or [])
        optional = ", ".join(rule.get("optional_authority") or [])
        line = f"- {core}: required authority = {required}"
        if one_of:
            line += f"; one of = {one_of}"
        if optional:
            line += f"; optional support = {optional}"
        authority_lines.append(line)
    authority_text = "\n".join(authority_lines) + (
        "\nExecution order is production control only; it is not derivation or authority order."
        "\nA Core2 HOLD does not become academic authority and does not automatically block valid Core1-family study products."
        "\nPreserve question.primary_capability_ref; set-level topic/rung scope is composition context only."
        "\nDemand evidence and learner eligibility are independent states."
        "\nSource question.hints[] and authored question.scaffolds[] remain separate custody classes."
        "\nExtension demands do not become Core1/Core1A/Core1B microtopics unless canonical academic authority admits them."
    )
    diff = " → ".join(brief["validation"].get("difficulty_bands") or []) or "Use the canonical/intrinsic difficulty information available in the referenced records; do not infer it from learner percentage."
    kws = "\n".join(f"- {item['phrase']} ({item['kind']}; evidence: {', '.join(item['evidence_refs'])})" for item in fingerprint)
    trace = "\n".join(
        f"- {row['trace_id']}: {', '.join(row['question_ids'])} → {row['primary_capability_ref'] or 'UNMAPPED'}"
        f" → {row['matrix_ref'] or 'UNMAPPED'}/{row['rung'] or 'UNMAPPED'}; status={row['status']}"
        for row in brief["trace_rows"]
    )
    hold_text = "\n".join(f"- {h['status']} / {h['point']}: {h['detail']}" for h in holds) or "- No composer-level HOLD. Downstream planner holds still apply."
    downstream = (
        "The intended downstream publication is one role-specific PDF for each valid/publishable requested Core. "
        "Do not render PDFs here; #273 owns PDF publication after validated learner products exist."
    )

    content = {
        "GOAL_OUTCOME": "Produce the requested six-Core authoring outputs from this fixed planning bundle without changing canonical curriculum, question identity, role semantics, or planner authority.",
        "FIXED_SOURCE_QUESTIONS": fixed,
        "LEARNER_PROFILE": learner_text + "\nA percentage is a starting coordinate only; it is not evidence of prerequisite mastery.",
        "EXECUTION_ORDER": order + "\nTreat this as production control only. It does not override readiness, HOLD decisions, or the authority graph.",
        "AUTHORITY_GRAPH": authority_text,
        "TOPIC_BOUNDARY": boundary,
        "CORE_OBLIGATIONS": core_lines,
        "DIFFICULTY_PROGRESSION": diff + "\nPreserve intrinsic Core1A/Core1B depth regardless of the learner estimate.",
        "KEYWORD_FINGERPRINT": kws,
        "PROVENANCE_TRACE": trace + "\nUse only the cited repository/owner inputs. Do not expose or invent private reasoning traces.",
        "ACCEPTANCE": "Keep every fixed question traceable to its mapping finding; preserve per-question primary_capability_ref independently from set-level scope; keep demand evidence separate from learner eligibility; preserve the requested Core set/order without treating order as authority; distinguish source hints from authored scaffolds and source/adapted/authored material; do not promote extension demand into Core1-family teaching without canonical admission; and hand the unchanged authoring request to the existing planner.",
        "NON_GOALS": "Do not select a new canonical question set, create a seventh Core, infer mastery, fabricate source receipts, duplicate plan_request.py, or author/publish PDFs in this task.",
        "HOLD_FAIL": hold_text + "\nIf a composer HOLD is present, do not silently resolve it. If the planner requests source basis, prerequisites or owner input, preserve that HOLD.",
        "DOWNSTREAM_DELIVERABLE": downstream,
    }

    sections.append(f"# Core-agent authoring prompt\n\nPrompt brief: {brief['prompt_brief_id']}\nRepository basis: {brief['repository_basis']}")
    for spec in template["sections"]:
        sections.append(f"## [{spec['id']}] {spec['title']}\n\n{content[spec['id']]}")
    return "\n\n".join(sections).strip() + "\n"


def _validate_brief(brief: dict, repo: Path) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / "Shared/library/prompt-brief.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    return [{
        "point": "PROMPT_BRIEF_STRUCTURE",
        "where": "/".join(str(x) for x in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(brief)]


def compose(doc: dict, repo: Path = REPO, repository_basis: str | None = None) -> dict:
    subject = str(doc.get("subject") or "").strip()
    requested = list(doc.get("requested_cores") or [])
    order = list(doc.get("execution_order") or requested or DEFAULT_EXECUTION_ORDER)
    questions = list(doc.get("questions") or [])
    owner_scope = doc.get("owner_confirmed_rung")
    template = load(repo / "template/core-prompt-composer/core-agent-prompt.v1.json")
    authority_path = core_authority_contract.discover_contract(repo / "Shared" / "roles")
    authority = core_authority_contract.load_contract(authority_path)
    normalized = json.loads(canonical_json(doc))
    input_digest = digest(normalized)
    brief_id = "PB-" + input_digest.split(":", 1)[1][:16].upper()

    holds: list[dict] = []
    if not subject:
        holds.append({"status": "UNMAPPED_HOLD", "point": "SUBJECT_REQUIRED", "detail": "subject is required"})
    if not questions:
        holds.append({"status": "UNMAPPED_HOLD", "point": "QUESTION_SET_REQUIRED", "detail": "at least one question row is required"})

    if subject and (repo / subject / "library").is_dir():
        index = study_map.subject_index(subject, repo)
    else:
        index = {"canonical_questions": {}, "capabilities": {}, "locations": {}}
        if subject:
            holds.append({"status": "UNMAPPED_HOLD", "point": "SUBJECT_UNKNOWN",
                          "detail": f"{subject} has no canonical subject library"})

    rows = []
    for raw in questions:
        row, row_holds = _resolve_question_row(raw, index, owner_scope)
        rows.append(row)
        holds.extend(row_holds)

    scope, scope_holds = _resolve_scope(subject, rows, owner_scope, repo) if subject else ({
        "status": "UNMAPPED_HOLD", "matrix_ref": None, "bucket_ref": None, "topic": None,
        "subtopic": None, "canonical_primary_rungs": [], "owner_confirmed_rung": owner_scope,
    }, [])
    holds.extend(scope_holds)
    holds.extend(_validate_core_order(requested, order))
    source_basis = list(doc.get("source_basis") or [])
    holds.extend(_source_basis_hold(source_basis, rows))

    fingerprint = _fingerprint(rows, scope, subject, repo, index)
    trace_rows = _trace(rows, fingerprint)
    worksheet = _worksheet_map(doc, rows)

    unique_holds = []
    seen_holds = set()
    for hold in holds:
        key = (hold["status"], hold["point"], hold["detail"])
        if key not in seen_holds:
            seen_holds.add(key)
            unique_holds.append(hold)
    holds = unique_holds

    brief = {
        "prompt_brief_id": brief_id,
        "template": {
            "id": template["template_id"],
            "version": template["version"],
            "path": str(TEMPLATE_PATH.relative_to(REPO)),
        },
        "repository_basis": repository_basis or doc.get("repository_basis") or git_basis(repo),
        "authority_contract": {
            "version": authority["version"],
            "path": str(authority_path.relative_to(repo)),
            "digest": digest(authority),
        },
        "input_digest": input_digest,
        "prompt_digest": "sha256:" + ("0" * 64),
        "subject": subject,
        "scope": scope,
        "question_rows": rows,
        "keyword_fingerprint": fingerprint,
        "learner_entry": doc.get("learner"),
        "requested_cores": requested,
        "execution_order": order,
        "source_authoring_policy": {
            "question_identity_rule": "Exact canonical_question_ref may adopt stored mapping metadata without promoting record lifecycle status.",
            "source_basis_rule": "authoring-request source_basis accepts source locator/receipt basis only; canonical question IDs remain in this brief/worksheet map.",
            "source_receipt_rule": "The composer never creates or upgrades source receipts and never claims source-product readiness.",
            "supplemental_question_policy": doc.get("supplemental_question_policy"),
        },
        "scope_boundaries": [
            "Canonical subject/question records remain authority.",
            "Existing six Core role contracts remain authority; no seventh Core is created.",
            "Learner percentage is a routing coordinate only and cannot shrink CORE1A/CORE1B intrinsic depth.",
            "plan_request.py remains authoritative for readiness, prerequisite bridges, source receipts and product holds.",
            "Reusable question-set selection and strict exam mode remain outside this composer.",
            "PDF publication remains downstream under issue #273.",
        ],
        "validation": {
            "composer_state": "HOLD" if holds else "PASS",
            "difficulty_bands": _difficulty(rows),
            "question_count": len(rows),
            "mapped_question_count": sum(1 for row in rows if row.get("primary_capability_ref")),
            "core_order_exact": not any(h["point"] == "CORE_ORDER_INVALID" for h in holds),
            "source_basis_contains_question_ids": any(h["point"] == "SOURCE_BASIS_QUESTION_ID_INVALID" for h in holds),
        },
        "trace_rows": trace_rows,
        "holds": holds,
        "planner_handoff": {
            "state": "COMPOSER_HOLD" if holds else "READY_FOR_PLANNER",
            "authoring_request_schema": AUTHORING_SCHEMA,
            "planner_command": "python3 Shared/tools/plan_request.py --plan <authoring-request.json>",
            "run_builder": "tools/run-builder/index.html",
            "note": "Composer PASS means only that the prompt bundle is structurally/mapping-ready for the existing planner; it does not mean any Core product is ready.",
        },
    }
    prompt = render_prompt(brief, template, authority)
    brief["prompt_digest"] = digest(prompt)
    structure_findings = _validate_brief(brief, repo)
    if structure_findings:
        raise ValueError("prompt brief failed schema validation: " + "; ".join(f["detail"] for f in structure_findings))

    authoring_request = _authoring_request(doc, scope, brief_id, holds)
    # Invalid question IDs are never copied into source_basis.
    if _source_basis_hold(source_basis, rows):
        authoring_request.pop("source_basis", None)
        authoring_request.pop("source_receipt_ref", None)
        authoring_request.pop("source_basis_drift_acknowledgement", None)

    study_report = study_map.resolve(worksheet, repo) if worksheet["questions"] else {
        "worksheet_id": worksheet["worksheet_id"], "subject": subject, "questions": [],
        "findings": [{"point": "WORKSHEET_MAP_EMPTY_AFTER_HOLDS", "detail": "No mapped question can be exported."}],
        "passed": False,
    }
    return {
        "prompt_brief": brief,
        "agent_prompt": prompt,
        "worksheet_map": worksheet,
        "worksheet_resolution": study_report,
        "authoring_request": authoring_request,
        "passed": not holds and study_report.get("passed", False),
    }


def write_bundle(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "prompt-brief.json": result["prompt_brief"],
        "worksheet-map.json": result["worksheet_map"],
        "authoring-request.json": result["authoring_request"],
        "trace.json": result["prompt_brief"]["trace_rows"],
    }
    for name, value in artifacts.items():
        (out_dir / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "agent-prompt.md").write_text(result["agent_prompt"], encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, required=True, help="owner question-set input JSON")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--repo-basis")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    result = compose(load(args.input), repository_basis=args.repo_basis)
    if args.out_dir:
        write_bundle(result, args.out_dir)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not result["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
