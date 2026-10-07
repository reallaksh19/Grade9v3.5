from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[2]
SCHEMA = "grade9v3-test-derived-question-bank-v1"
SCHEMA_PATH = REPO / "TEST" / "contracts" / "derived-question-bank.schema.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_claimed(bank: dict) -> bool:
    return bank.get("schema") == SCHEMA or bank.get("authority_model") == "SOURCE_LINKED_DERIVATIVE"


def findings(bank: dict) -> list[str]:
    problems: list[str] = []
    schema = load(SCHEMA_PATH)
    for error in sorted(Draft202012Validator(schema).iter_errors(bank), key=lambda e: tuple(str(x) for x in e.absolute_path)):
        where = "/".join(str(x) for x in error.absolute_path) or "<root>"
        problems.append(f"{where}: {error.message}")
    if problems:
        return problems

    intake_path = REPO / bank["source_intake_ref"]
    if not intake_path.is_file():
        return [f"source_intake_ref missing: {bank['source_intake_ref']}"]
    intake = load(intake_path)
    source_questions = {row["id"]: row for row in intake.get("questions") or []}
    documents = {row["id"]: row for row in intake.get("documents") or []}

    for question in bank["questions"]:
        source = source_questions.get(question["origin_ref"])
        if not source:
            problems.append(f"{question['id']}: origin_ref does not resolve in source intake")
            continue
        for field in ("original_identifier", "stem", "stem_sha256", "options"):
            if question.get(field) != source.get(field):
                problems.append(f"{question['id']}: source-owned {field} drifted from intake")
        digest = "sha256:" + hashlib.sha256(question["stem"].encode("utf-8")).hexdigest()
        if question["stem_sha256"] != digest:
            problems.append(f"{question['id']}: stem_sha256 does not match stem bytes")

        ext = question["extensions"]
        custody = ext["grade9v3:source_custody"]
        if ext["grade9v3:provenance_class"] != "CURRICULAR_VERIFIED":
            problems.append(f"{question['id']}: learner provenance must be CURRICULAR_VERIFIED")
        if (custody.get("authority_class"), custody.get("source_status"), custody.get("wording_custody")) != (
            "CURRICULAR_STANDARD", "NCERT_AUTHENTIC", "VERBATIM"
        ):
            problems.append(f"{question['id']}: curricular custody triple is not verified/verbatim")

        source_doc = documents.get(source["source_document_ref"])
        if not source_doc:
            problems.append(f"{question['id']}: source document does not resolve")
        else:
            expected = {
                "source_document_ref": source_doc["id"],
                "source_document_title": source_doc["title"],
                "source_url": source_doc["url"],
                "source_locator": source["source_locator"],
                "text_verification_status": source["text_verification_status"],
                "verification_evidence_ref": source["verification_evidence_ref"],
            }
            for field, value in expected.items():
                if custody.get(field) != value:
                    problems.append(f"{question['id']}: custody {field} drifted from intake")

        official = source.get("official_answer") or {}
        answer_doc = documents.get(official.get("document_ref"))
        source_key = (question.get("answer") or {}).get("source_key") or {}
        if not source.get("official_answer_available"):
            problems.append(f"{question['id']}: derivative requires an independently verified official key")
        elif not answer_doc:
            problems.append(f"{question['id']}: official answer document does not resolve")
        else:
            expected_key = {
                "answer_key_document_ref": answer_doc["id"],
                "answer_key_url": answer_doc["url"],
                "answer_key_evidence_ref": official["verification_evidence_ref"],
            }
            for field, value in expected_key.items():
                if custody.get(field) != value:
                    problems.append(f"{question['id']}: custody {field} drifted from intake")
            if source_key.get("state") != "PRESENT" or source_key.get("value") != official.get("answer_key"):
                problems.append(f"{question['id']}: source_key does not match official answer key")
            if source_key.get("document_ref") != answer_doc["id"] or source_key.get("verification_evidence_ref") != official.get("verification_evidence_ref"):
                problems.append(f"{question['id']}: source_key custody does not match answer evidence")

        overlay = ext["grade9v3:authored_overlay"]
        if overlay.get("authority") != "AGENT_AUTHORED_SANDBOX":
            problems.append(f"{question['id']}: authored overlay is not sandbox-labelled")
        if question.get("hints"):
            problems.append(f"{question['id']}: source hints are not authorised by the Stage-1 record")
    return problems


def check_path(path: Path) -> list[str]:
    return findings(load(path))
