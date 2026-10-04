#!/usr/bin/env python3
"""Make and check an owner-supplied question bank: questions the Owner wrote, kept verbatim with no exam identity.

CORE2.md says a question the owner supplied is custody in its own right (class OWNER_SUPPLIED) and appears
verbatim, with an exam identity only where research has matched the original. The official exam-bank schema
cannot hold that (it requires an exam, year, paper and archive URLs), so an owner bank is a separate file kind.
It may live in TEST/question-bank/*.json for sandbox work or <Subject>/library/owner-bank/*.json for a canonical
subject. It never lives under exam-bank/ and never acquires an official-exam identity from this file kind.

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
    python3 Shared/tools/owner_bank.py new --intake workspace/intake.json --bank-id SLUG --out Chemistry/library/owner-bank/SLUG.json
    python3 Shared/tools/owner_bank.py check Chemistry/library/owner-bank/SLUG.json --intake workspace/intake.json

`new` leaves the answer, the capability and family refs, the question type and the difficulty estimate empty for the
author to fill; `check` names each one, with the same messages the renderer would give.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import core2_v2, learner_metadata  # noqa: E402
from Shared.tools import web_blueprint_contract as blueprints  # noqa: E402

TEST_BANK_DIR = ("TEST", "question-bank")
SUBJECT_BANK_DIR = ("library", "owner-bank")
ANALYSIS_KEY = "grade9v3:analysis"

SCHEMA_VERSION = "grade9v3-owner-supplied-bank-v1"
CUSTODY_CLASS = "OWNER_SUPPLIED_RAW_INPUT"
CUSTODY_KEY = "grade9v3:source_custody"
OFFICIAL_ONLY = ("exam", "year", "paper", "section", "question_number", "paper_url", "archive_url",
                 "answer_key_url", "answer_authority", "source_status", "parent_ref")
REQUIRED = ("id", "original_identifier", "stem", "answer", "primary_capability_ref", "extensions")
BANK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
HINTS = {"primary_capability_ref": " (the id of a capability in the package this bank is used with)",
         "answer": " (an object: summary, a typed reasoning_route, crux_move_ref)"}

# What a Core2 page needs to be more than a stem and a text box is the Core2 blueprint's to say
# (Shared/web/interactive-page-blueprints.v1.json): its REQUIRED components, how deep each is, and how to author it.
# This file asks for what the blueprint asks, at the depth of the reference page, and scaffolds what it lists.
SUPPORT_KINDS = ("REPRESENT", "CONNECT", "EXECUTE")
SUPPORT_REVEALS = ("CONCEPT", "METHOD", "ANSWER")
MOVE_KINDS = tuple(core2_v2.SOLUTION_STAGE_BY_KIND)


def core2_blueprint() -> dict:
    return blueprints.blueprint_for_role(blueprints.load_registry(), "CORE2") or {}


def text_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def is_owner_bank(document: object) -> bool:
    return isinstance(document, dict) and document.get("schema_version") == SCHEMA_VERSION


def intake_questions(intake: dict) -> list[dict]:
    return list((intake.get("inputs") or {}).get("questions") or [])


def _page_problems(question: dict, label: str, complete: bool = True, seen: set | None = None) -> list[str]:
    """What the learner would not see: the blueprint's required components, then the typing the renderer relies on."""
    problems: list[str] = []
    if question.get("hints"):
        problems.append(f"{label}: hints are a source's own words; an owner question has no source. "
                        "Put guided support in scaffolds")
    if complete:
        problems += blueprints.record_problems(core2_blueprint(), question, label, seen)
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    route = answer.get("reasoning_route")
    moves = [m for m in route if isinstance(m, dict)] if isinstance(route, list) else []
    ids = [m.get("id") for m in moves]
    if moves:
        try:
            core2_v2.project_solution(answer)
        except core2_v2.Core2SolutionProjectionError as caught:
            problems.append(f"{label}: answer.reasoning_route: {caught}")
        if answer.get("crux_move_ref") not in ids:
            problems.append(f"{label}: answer.crux_move_ref must be the id of the move a learner is most likely to miss "
                            f"(one of {ids})")
    scaffolds = question.get("scaffolds") if isinstance(question.get("scaffolds"), list) else []
    typed = True
    for number, rung in enumerate(scaffolds):
        where = f"{label}: scaffolds[{number}]"
        if not isinstance(rung, dict) or not str(rung.get("text") or "").strip():
            problems.append(f"{where}.text is empty: write the hint the learner sees")
            typed = False
            continue
        if rung.get("support_kind") not in SUPPORT_KINDS:
            problems.append(f"{where}.support_kind must be one of {', '.join(SUPPORT_KINDS)}")
            typed = False
        if rung.get("reveals") not in SUPPORT_REVEALS:
            problems.append(f"{where}.reveals must be one of {', '.join(SUPPORT_REVEALS)}")
            typed = False
        if rung.get("supports_move_ref") not in ids:
            problems.append(f"{where}.supports_move_ref must be the id of a reasoning_route move (one of {ids})")
            typed = False
    if typed and scaffolds:
        try:
            rungs = core2_v2.pre_solution_support(question)
        except core2_v2.Core2SupportProjectionError as caught:
            problems.append(f"{label}: scaffolds: {caught}")
        else:
            if len(rungs) < len(scaffolds):
                problems.append(f"{label}: only {len(rungs)} of {len(scaffolds)} scaffold(s) can be shown before the answer "
                                "(reveals ANSWER is held back until the solution)")
    return problems


def check(document: dict, where: str = "bank", intake: dict | None = None, complete: bool = True) -> list[str]:
    """Problems with an owner bank, one line each. Empty means it can be used.

    With the intake it was made from, each stem is also compared with the intake's text and every intake
    question must be in the bank. With `complete`, the bank is also held to the page blueprint at the reference depth:
    each REQUIRED component as deep as the question's band asks, each EXPECTED one supplied or waived with a reason.
    The renderer asks with complete=False: it builds the draft and reports each of those as a gap, all of them, in the receipt."""
    problems: list[str] = []
    if not is_owner_bank(document):
        return [f"{where}: schema_version must be {SCHEMA_VERSION}"]
    if not str(document.get("bank_id") or "").strip():
        problems.append(f"{where}: bank_id is required")
    questions = document.get("questions")
    if not isinstance(questions, list) or not questions:
        return problems + [f"{where}: questions must be a non-empty list"]
    seen: set[str] = set()
    explained: set[str] = set()          # a component's authoring instruction is given once, at its first shortfall
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
        problems += _page_problems(question, label, complete, explained)
        # The same projection the renderer makes: provenance, difficulty and question type. Say it here, not as a gap later.
        problems += [f"{label}: {problem}" for problem in learner_metadata.bank_question_problems(question)]
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
        question_id = f"OWN-{bank_id.upper()}-{number:02d}"
        questions.append({
            "id": question_id,
            "original_identifier": f"Q{item.get('label') or number}",
            "stem": text,
            "answer": {"kind": "EXACT", "summary": "", "verification_status": "NOT_RUN"},
            "primary_capability_ref": "",
            "family_ref": "",
            "extensions": {
                CUSTODY_KEY: {
                    "authority_class": CUSTODY_CLASS,
                    "intake_ref": item["id"],
                    "wording_custody": "VERBATIM",
                    "text_sha256": text_digest(text),
                },
                # The difficulty is the author's estimate: five components, each 0 to 2, their sum as the score, and the
                # band that sum falls in (see Shared/vocabularies/learner-question-metadata.v1.json). Fill every empty value.
                # To typeset maths, add {"target": "answer_reasoning:1", "literal": "sqrt(3^2 + 4^2)", "tex": "\\sqrt{3^{2}+4^{2}}",
                # "display": false} here; the literal must occur in the target text (stem, answer_summary, answer_reasoning:N).
                "grade9v3:math_spans": [],
                ANALYSIS_KEY: {
                    "learner_question_type": "",
                    "difficulty": {"band": "", "score": 0, "basis": "",
                                   "components": {name: 0 for name in sorted(learner_metadata.DIFFICULTY_COMPONENTS)}},
                },
            },
        })
    wanted = blueprints.skeleton(core2_blueprint())
    for question in questions:
        _merge(question, json.loads(json.dumps(wanted).replace("{qid}", question["id"])))
    return {"schema_version": SCHEMA_VERSION, "bank_id": bank_id, "intake_digest": intake.get("intake_digest"),
            "questions": questions}


def _merge(into: dict, add: dict) -> None:
    """Add the blueprint's empty fields to a new question without replacing anything already set."""
    for key, value in add.items():
        if isinstance(value, dict) and isinstance(into.get(key), dict):
            _merge(into[key], value)
        else:
            into.setdefault(key, value)


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def owner_bank_destination(path: str | Path) -> str | None:
    """Return the repository-relative path when `path` is an allowed owner-bank destination.

    TEST keeps its historical TEST/question-bank/<slug>.json location. Canonical subjects use the separate
    <Subject>/library/owner-bank/<slug>.json lane. Resolution happens before classification so path traversal
    and symlink escapes cannot smuggle a write outside the repository. A canonical subject is one that already
    declares adapter/CoreContracts.json; arbitrary top-level directories do not become source authorities.
    """
    resolved = Path(path).resolve()
    try:
        relative = resolved.relative_to(REPO)
    except ValueError:
        return None
    if resolved.suffix != ".json":
        return None
    parts = relative.parts
    if len(parts) == 3 and parts[:2] == TEST_BANK_DIR:
        return relative.as_posix()
    if len(parts) == 4 and parts[1:3] == SUBJECT_BANK_DIR:
        subject = parts[0]
        if subject == "TEST":
            return None
        if not (REPO / subject / "adapter" / "CoreContracts.json").is_file():
            return None
        return relative.as_posix()
    return None


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
        relative = owner_bank_destination(out)
        if relative is None:
            print("an owner bank is written to TEST/question-bank/SLUG.json or "
                  "<Subject>/library/owner-bank/SLUG.json for a canonical subject; "
                  "never to exam-bank/ or outside the repository", file=sys.stderr)
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
              "For each: fill every empty field it lists, and primary_capability_ref, family_ref, answer.summary and the "
              "question type and difficulty in extensions[\"grade9v3:analysis\"]. The fields are the ones the Core2 page "
              "blueprint asks for (what each is for: docs/specs/PAGE-BLUEPRINT-COMPONENTS.md). "
              "Do not edit a stem: its digest is checked.")
        return 0

    intake = _load(parsed.intake) if parsed.intake else None
    failed = False
    for path in parsed.banks:
        document = _load(path)
        problems = check(document, path, intake)
        print("\n".join(problems) if problems else f"{path}: OK")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

