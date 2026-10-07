#!/usr/bin/env python3
"""Validate TEST Stage-1 official-source intake and emit deterministic blueprint handoffs."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "grade9v3-test-source-question-intake-v1"
SCHEMA = REPO / "TEST" / "contracts" / "source-question-intake.schema.json"
OFFICIAL_HOSTS = {
    "NCERT_OFFICIAL": {"ncert.nic.in", "www.ncert.nic.in"},
    "CBSE_OFFICIAL": {"cbse.gov.in", "www.cbse.gov.in", "cbseacademic.nic.in", "www.cbseacademic.nic.in"},
}
READY = "READY_FOR_BLUEPRINT"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def text_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _schema_findings(bank: dict) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["jsonschema is required to validate the TEST intake contract"]
    schema = load(SCHEMA)
    return [
        "schema " + "/".join(str(x) for x in error.absolute_path) + ": " + error.message
        for error in sorted(Draft202012Validator(schema).iter_errors(bank), key=lambda e: tuple(str(x) for x in e.absolute_path))
    ]


def _official(authority: str, url: str) -> bool:
    host = (urlsplit(url).hostname or "").lower()
    return host in OFFICIAL_HOSTS.get(authority, set())


def findings(bank: dict) -> list[str]:
    found = _schema_findings(bank)
    if bank.get("schema_version") != SCHEMA_VERSION:
        return found

    scope = set(bank.get("source_scope") or [])
    documents = {}
    for row in bank.get("documents") or []:
        ident = row.get("id")
        if ident in documents:
            found.append(f"document {ident}: duplicate id")
            continue
        documents[ident] = row
        authority = row.get("authority")
        if authority not in scope:
            found.append(f"document {ident}: authority {authority!r} is outside source_scope")
        if not _official(str(authority), str(row.get("url") or "")):
            found.append(f"document {ident}: URL is not on an allowed official {authority} host")

    seen_ids: set[str] = set()
    seen_instances: dict[tuple, str] = {}
    for q in bank.get("questions") or []:
        qid = str(q.get("id") or "<missing-id>")
        if qid in seen_ids:
            found.append(f"{qid}: duplicate question id")
        seen_ids.add(qid)

        stem = q.get("stem")
        if isinstance(stem, str) and q.get("stem_sha256") != text_digest(stem):
            found.append(f"{qid}: stem_sha256 does not match exact stem bytes")

        doc = documents.get(q.get("source_document_ref"))
        if not doc:
            found.append(f"{qid}: source_document_ref names no declared document")
            continue
        if doc.get("role") != "QUESTION_SOURCE":
            found.append(f"{qid}: source document is not QUESTION_SOURCE")

        loc = q.get("source_locator") or {}
        instance = (
            q.get("source_document_ref"),
            loc.get("chapter_or_unit"),
            loc.get("exercise_or_section"),
            str(loc.get("question_number")),
            loc.get("printed_page"),
        )
        if instance in seen_instances:
            found.append(f"{qid}: duplicate source instance also used by {seen_instances[instance]}")
        else:
            seen_instances[instance] = qid

        if q.get("subject") != bank.get("subject") or q.get("grade") != bank.get("grade"):
            found.append(f"{qid}: subject/grade differs from its bank")

        if q.get("official_answer_available"):
            ans = q.get("official_answer") or {}
            answer_doc = documents.get(ans.get("document_ref"))
            if not answer_doc or answer_doc.get("role") != "ANSWER_KEY":
                found.append(f"{qid}: official answer must reference a declared ANSWER_KEY document")
            elif answer_doc.get("authority") != doc.get("authority"):
                found.append(f"{qid}: answer authority differs from question source authority")

        if q.get("workflow_status") == READY:
            if q.get("source_verification_status") != "SOURCE_VERIFIED_OFFICIAL":
                found.append(f"{qid}: READY_FOR_BLUEPRINT requires SOURCE_VERIFIED_OFFICIAL")
            if q.get("text_verification_status") != "TEXT_VERIFIED_AGAINST_OFFICIAL":
                found.append(f"{qid}: READY_FOR_BLUEPRINT requires TEXT_VERIFIED_AGAINST_OFFICIAL")
            if not q.get("verification_evidence_ref"):
                found.append(f"{qid}: READY_FOR_BLUEPRINT requires verification evidence")

    return sorted(set(found))


def handoff(bank: dict) -> list[dict]:
    docs = {row["id"]: row for row in bank.get("documents", [])}
    rows = []
    for q in sorted(bank.get("questions", []), key=lambda row: row["id"]):
        if q.get("workflow_status") != READY:
            continue
        doc = docs[q["source_document_ref"]]
        row = {
            "intake_question_ref": q["id"],
            "source_identity": {
                "authority": doc["authority"],
                "kind": doc["kind"],
                "document_title": doc["title"],
                "document_url": doc["url"],
            },
            "source_locator": q["source_locator"],
            "stem": q["stem"],
            "stem_sha256": q["stem_sha256"],
            "options": q.get("options", []),
            "subparts": q.get("subparts", []),
            "subject": q["subject"],
            "grade": q["grade"],
            "topic_label": q["topic_label"],
            "subtopic_label": q.get("subtopic_label"),
            "question_type": q["question_type"],
            "verification_evidence_ref": q["verification_evidence_ref"],
            "official_answer": q.get("official_answer") if q.get("official_answer_available") else None,
            "intake_status": READY,
        }
        rows.append(row)
    return rows


def report(bank: dict) -> dict:
    rows = bank.get("questions", [])
    by_status: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    for q in rows:
        by_status[q.get("workflow_status", "UNKNOWN")] = by_status.get(q.get("workflow_status", "UNKNOWN"), 0) + 1
        by_topic[q.get("topic_label", "UNKNOWN")] = by_topic.get(q.get("topic_label", "UNKNOWN"), 0) + 1
    return {
        "bank_id": bank.get("bank_id"),
        "total_questions": len(rows),
        "ready_for_blueprint": sum(1 for q in rows if q.get("workflow_status") == READY),
        "by_status": dict(sorted(by_status.items())),
        "by_topic": dict(sorted(by_topic.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "report"):
        p = sub.add_parser(name)
        p.add_argument("bank", type=Path)
    p = sub.add_parser("handoff")
    p.add_argument("bank", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    bank = load(args.bank)
    problems = findings(bank)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    if args.command == "check":
        print(f"OK: {len(bank.get('questions', []))} Stage-1 question(s)")
    elif args.command == "report":
        print(json.dumps(report(bank), indent=2, sort_keys=True))
    else:
        payload = handoff(bank)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {len(payload)} READY_FOR_BLUEPRINT record(s) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
