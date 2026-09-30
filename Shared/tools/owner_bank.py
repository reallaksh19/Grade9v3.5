#!/usr/bin/env python3
"""Make and check an owner-supplied question bank: questions the Owner wrote, kept verbatim with no exam identity.

CORE2.md says a question the owner supplied is custody in its own right (class OWNER_SUPPLIED) and appears
verbatim, with an exam identity only where research has matched the original. The official exam-bank schema
cannot hold that (it requires an exam, year, paper and archive URLs), so an owner bank is a separate file kind,
for now used only by the TEST sandbox (TEST/question-bank/*.json; design question: issue #371).

An owner bank is a JSON file with `"schema_version": "grade9v3-owner-supplied-bank-v1"`, a `bank_id`, and
`questions[]` shaped like exam-bank questions except that `extensions["grade9v3:source_custody"]` is

    {"authority_class": "OWNER_SUPPLIED_RAW_INPUT", "intake_ref": "<the intake's id for the question>",
     "wording_custody": "VERBATIM", "text_sha256": "sha256:<digest of the stem as the Owner supplied it>"}

"Verbatim" is checked, not asserted: `new` copies each question's text from the intake and records its digest,
and `check` refuses a stem that no longer matches its digest, so tidying the Owner's words is caught. With
`--intake` it also checks each stem against the intake text itself and that no intake question is missing.
The check also refuses any official-exam field in the custody object: an owner question never gets an exam,
year, paper or URL from this file kind, so a guessed identity cannot hide under the owner class.

    python3 Shared/tools/owner_bank.py new --intake workspace/intake.json --bank-id SLUG --out TEST/question-bank/SLUG.json
    python3 Shared/tools/owner_bank.py check TEST/question-bank/SLUG.json --intake workspace/intake.json

`new` leaves `answer.summary` and `primary_capability_ref` empty for the author to fill; `check` names each one.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BANK_DIR = "TEST/question-bank"

SCHEMA_VERSION = "grade9v3-owner-supplied-bank-v1"
CUSTODY_CLASS = "OWNER_SUPPLIED_RAW_INPUT"
CUSTODY_KEY = "grade9v3:source_custody"
OFFICIAL_ONLY = ("exam", "year", "paper", "section", "question_number", "paper_url", "archive_url",
                 "answer_key_url", "answer_authority", "source_status", "parent_ref")
REQUIRED = ("id", "original_identifier", "stem", "answer", "primary_capability_ref", "extensions")
BANK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
HINTS = {"primary_capability_ref": " (the id of a capability in the package this bank is used with)",
         "answer": " (an object: summary, and reasoning as a list of steps)"}


def text_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_owner_bank(document: object) -> bool:
    return isinstance(document, dict) and document.get("schema_version") == SCHEMA_VERSION


def intake_questions(intake: dict) -> list[dict]:
    return list((intake.get("inputs") or {}).get("questions") or [])


def check(document: dict, where: str = "bank", intake: dict | None = None) -> list[str]:
    """Problems with an owner bank, one line each. Empty means it can be used.

    With the intake it was made from, each stem is also compared with the intake's text and every intake
    question must be in the bank."""
    problems: list[str] = []
    if not is_owner_bank(document):
        return [f"{where}: schema_version must be {SCHEMA_VERSION}"]
    if not str(document.get("bank_id") or "").strip():
        problems.append(f"{where}: bank_id is required")
    questions = document.get("questions")
    if not isinstance(questions, list) or not questions:
        return problems + [f"{where}: questions must be a non-empty list"]
    seen: set[str] = set()
    for index, question in enumerate(questions):
        label = f"{where}: questions[{index}]" + (f" {question.get('id')}" if isinstance(question, dict) else "")
        if not isinstance(question, dict):
            problems.append(f"{label}: must be an object")
            continue
        for key in REQUIRED:
            if not question.get(key):
                problems.append(f"{label}: {key} is required{HINTS.get(key, '')}")
        if question.get("id") in seen:
            problems.append(f"{label}: duplicate id")
        seen.add(question.get("id"))
        if isinstance(question.get("answer"), dict) and not str(question["answer"].get("summary") or "").strip():
            problems.append(f"{label}: answer.summary is required")
        custody = (question.get("extensions") or {}).get(CUSTODY_KEY) or {}
        if custody.get("authority_class") != CUSTODY_CLASS:
            problems.append(f"{label}: {CUSTODY_KEY}.authority_class must be {CUSTODY_CLASS}")
        if not str(custody.get("intake_ref") or "").strip():
            problems.append(f"{label}: {CUSTODY_KEY}.intake_ref is required (the intake digest or input id)")
        if custody.get("wording_custody") != "VERBATIM":
            problems.append(f"{label}: {CUSTODY_KEY}.wording_custody must be VERBATIM")
        stem = question.get("stem")
        if stem and not isinstance(stem, str):
            problems.append(f"{label}: stem must be the Owner's text, as one string")
        if not str(custody.get("text_sha256") or "").strip():
            problems.append(f"{label}: {CUSTODY_KEY}.text_sha256 is required; make the bank with "
                            "`owner_bank.py new` so the Owner's wording is recorded")
        elif isinstance(stem, str) and text_digest(stem) != custody["text_sha256"]:
            problems.append(f"{label}: the stem is not the text the Owner supplied (its digest differs from "
                            f"{CUSTODY_KEY}.text_sha256); owner questions are kept verbatim, so restore the stem")
        invented = [key for key in OFFICIAL_ONLY if key in custody]
        if invented:
            problems.append(f"{label}: {CUSTODY_KEY} must not carry official-exam fields {invented}; "
                            "an owner question has no exam identity unless research matched the original")
    if intake is not None:
        problems += _against_intake(document, questions, intake, where)
    return problems


def _against_intake(document: dict, questions: list, intake: dict, where: str) -> list[str]:
    supplied = {q.get("id"): q for q in intake_questions(intake)}
    if not supplied:
        return [f"{where}: the intake has no questions to compare with"]
    problems: list[str] = []
    if document.get("intake_digest") and document["intake_digest"] != intake.get("intake_digest"):
        problems.append(f"{where}: the bank was made from a different intake (intake_digest differs)")
    used: set[str] = set()
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            continue
        ref = ((question.get("extensions") or {}).get(CUSTODY_KEY) or {}).get("intake_ref")
        label = f"{where}: questions[{index}] {question.get('id')}"
        if ref not in supplied:
            problems.append(f"{label}: {CUSTODY_KEY}.intake_ref {ref!r} is not a question id in the intake")
            continue
        used.add(ref)
        if question.get("stem") != supplied[ref].get("text"):
            problems.append(f"{label}: the stem is not the intake's text for {ref}; the Owner's wording is kept exactly")
    for ref, question in supplied.items():
        if ref not in used:
            shown = str(question.get("text") or "")[:50]
            problems.append(f"{where}: intake question {ref} ({shown!r}) is not in the bank")
    return problems


def new(intake: dict, bank_id: str) -> dict:
    """An owner bank with one question per intake question: the text copied exactly, its digest recorded,
    and the answer and capability left empty for the author."""
    if not BANK_ID.fullmatch(bank_id or ""):
        raise ValueError(f"bank id {bank_id!r} must match {BANK_ID.pattern}")
    if intake.get("status") == "INVALID_REQUEST" or intake.get("errors"):
        raise ValueError(f"the intake has errors: {intake.get('errors')}")
    supplied = intake_questions(intake)
    if not supplied:
        raise ValueError("the intake has no questions")
    questions = []
    for number, item in enumerate(supplied, 1):
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"intake question {item.get('id')} has no text; there is nothing to keep verbatim")
        questions.append({
            "id": f"OWN-{bank_id.upper()}-{number:02d}",
            "original_identifier": f"Q{item.get('label') or number}",
            "stem": text,
            "answer": {"summary": ""},
            "primary_capability_ref": "",
            "extensions": {CUSTODY_KEY: {
                "authority_class": CUSTODY_CLASS,
                "intake_ref": item["id"],
                "wording_custody": "VERBATIM",
                "text_sha256": text_digest(text),
            }},
        })
    return {"schema_version": SCHEMA_VERSION, "bank_id": bank_id, "intake_digest": intake.get("intake_digest"),
            "questions": questions}


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print(__doc__.strip().splitlines()[0])
        return 2
    if args[0] not in {"new", "check"}:
        args = ["check"] + args            # a bare list of files means check
    parser = argparse.ArgumentParser(prog="owner_bank.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    make = sub.add_parser("new", help="an owner bank from an intake, verbatim")
    make.add_argument("--intake", required=True)
    make.add_argument("--bank-id", required=True)
    make.add_argument("--out", required=True)
    make.add_argument("--force", action="store_true", help="overwrite an existing bank (the answers in it are lost)")
    verify = sub.add_parser("check", help="problems with an owner bank")
    verify.add_argument("banks", nargs="+")
    verify.add_argument("--intake", help="also compare every stem with the intake it was made from")
    parsed = parser.parse_args(args)

    if parsed.cmd == "new":
        out = Path(parsed.out)
        resolved = out.resolve()
        try:
            relative = resolved.relative_to(REPO).as_posix()
        except ValueError:
            relative = ""
        if not relative.startswith(BANK_DIR + "/") or resolved.suffix != ".json":
            print(f"an owner bank is written to {BANK_DIR}/SLUG.json, never to an exam-bank directory", file=sys.stderr)
            return 1
        if resolved.exists() and not parsed.force:
            print(f"{parsed.out} exists; the answers in it would be lost. Edit it, or pass --force to start over", file=sys.stderr)
            return 1
        try:
            bank = new(_load(parsed.intake), parsed.bank_id)
        except ValueError as caught:
            print(f"owner_bank: {caught}", file=sys.stderr)
            return 1
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {parsed.out}: {len(bank['questions'])} question(s), each kept exactly as supplied.\n"
              "Fill answer.summary (and answer.reasoning, a list of steps) and primary_capability_ref for each; "
              "do not edit a stem, its digest is checked.")
        return 0

    intake = _load(parsed.intake) if parsed.intake else None
    failed = False
    for path in parsed.banks:
        problems = check(_load(path), path, intake)
        print("\n".join(problems) if problems else f"{path}: OK")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
