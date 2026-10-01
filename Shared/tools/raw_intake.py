#!/usr/bin/env python3
"""Research-first intake: start a learner-product job from raw owner input.

The owner supplies questions, prompts and syllabus text as they have them. Nothing here
requires a canonical repository identifier, a matrix/rung, or a learner profile. The
intake normalises the input, gives every item a content-derived id, proposes a
reconciliation between questions and syllabus subtopics, and emits the research and
authoring tasks the job must complete. It never returns a hold: gaps are work.

The browser entry (public/js/raw-intake.js) implements the same normalisation; the two
must agree on ids and on intake_digest (tests/raw_intake.test.mjs).

Usage:
    python3 Shared/tools/raw_intake.py --input request.json [--out intake.json]
    python3 Shared/tools/raw_intake.py --write-browser-data | --check-browser-data
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO / "Shared/workflows/research-first.v1.json"
SCHEMA = "research-first-intake/v1"
STATUS = "RESEARCH_AND_AUTHOR"
BROWSER_DATA = REPO / "public/data/research-first-workflow.js"

TOKEN = re.compile(r"[a-z0-9]+")
NUMBER = re.compile(r"[0-9]+(?:\.[0-9]+)?")
LABEL_PREFIX = re.compile(r"^\s*([Qq]?[0-9]+[a-z]?)\s*[:.)]\s+(.+)$", re.S)
LABEL_ONLY = re.compile(r"^[A-Za-z]{0,3}\s*[0-9]+[a-z]?$")
STOPWORDS = frozenset(
    "the and for with from that this into its are was were has have had how what when "
    "which who why find show state give take using use its their them then than per "
    "each after before between about over under two one also can will not all any".split()
)


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def digest(value: object) -> str:
    return "sha256:" + sha(value if isinstance(value, str) else canonical_json(value))


def load_workflow(path: Path = WORKFLOW_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def clean(text: object) -> str:
    return " ".join(str(text or "").split())


def clean_block(text: object) -> str:
    """A question as the Owner laid it out: spacing inside a line is tidied, the line breaks are kept.

    Parts (a), (b), (c) on their own lines stay on their own lines; the page shows them that way. Identity
    (`item_id`) is taken from the whitespace-collapsed text, so it does not depend on the layout."""
    return "\n".join(line for line in (clean(row) for row in str(text or "").splitlines()) if line)


def tokens(text: str) -> list[str]:
    return [t for t in TOKEN.findall(text.lower()) if len(t) >= 3 and t not in STOPWORDS]


def conditions(text: str) -> list[str]:
    """Stated numeric conditions, in order of first appearance, without duplicates."""
    seen: list[str] = []
    for value in NUMBER.findall(text):
        if value not in seen:
            seen.append(value)
    return seen


def item_id(prefix: str, text: str) -> str:
    return prefix + sha(clean(text).lower())[:10]


def _lines(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, str):
        return [part for part in (clean(line) for line in value.splitlines()) if part]
    return list(value)


def _question(raw: object) -> dict:
    if isinstance(raw, str):
        raw = {"text": raw}
    text = clean_block(raw.get("text"))
    label = clean(raw.get("label")) or None
    match = LABEL_PREFIX.match(text)
    if match and not label:
        label, text = match.group(1), clean_block(match.group(2))
    source_hint = clean(raw.get("source_hint")) or None
    if not text or LABEL_ONLY.match(text):
        label = label or text or None
        return {
            "id": item_id("q", "label:" + (label or "")),
            "text": "",
            "label": label,
            "source_hint": source_hint,
            "conditions": [],
            "text_status": "LABEL_ONLY",
            "identity_claim_requested": True,
        }
    return {
        "id": item_id("q", text),
        "text": text,
        "label": label,
        "source_hint": source_hint,
        "conditions": conditions(text),
        "text_status": "SUPPLIED",
        "identity_claim_requested": bool(label or source_hint),
    }


def _dedupe(rows: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for row in rows:
        if row["id"] in seen:
            seen[row["id"]]["supplied_count"] += 1
        else:
            seen[row["id"]] = {**row, "supplied_count": 1}
    return list(seen.values())


def reconcile(questions: list[dict], syllabus: list[dict]) -> dict:
    """Lexical proposal only; research confirms or replaces it in the coverage ledger."""
    subtopic_tokens = {row["id"]: set(tokens(row["text"])) for row in syllabus}
    links, outside = [], []
    used: set[str] = set()
    for question in questions:
        words = set(tokens(question["text"]))
        best, best_score = [], 0
        for row in syllabus:
            score = len(words & subtopic_tokens[row["id"]])
            if score > best_score:
                best, best_score = [row["id"]], score
            elif score == best_score and score > 0:
                best.append(row["id"])
        if best_score == 0:
            outside.append(question["id"])
        used.update(best)
        links.append({"question_id": question["id"], "subtopic_ids": best, "basis": "LEXICAL_PROPOSAL"})
    return {
        "question_to_subtopic": links,
        "questions_outside_syllabus": outside,
        "subtopics_without_questions": [row["id"] for row in syllabus if row["id"] not in used],
    }


def _core_names(value: object) -> list[str]:
    parts = re.split(r"[\s,;]+", value) if isinstance(value, str) else list(value or [])
    return [clean(part).upper() for part in parts if clean(part)]


def first_stage(request: dict, questions: list[dict], workflow: dict) -> tuple[dict, list[str], list[str]]:
    """Which Cores to show first, and what that packet contains.

    A Core the owner requests wins. Otherwise usable supplied question text selects Core2 and
    its absence selects source-grounded Core1 (docs/method/FIRST-STAGE-REVIEW.md). Later Cores
    are planned, not generated, until the first-stage packet has been shown.
    """
    config = workflow["first_stage"]
    order = config["core_order"]
    asked = _core_names(request.get("requested_cores"))
    unknown = sorted({name for name in asked if name not in order})
    wanted = [name for name in order if name in set(asked)]
    usable = any(row["text_status"] == "SUPPLIED" for row in questions)
    if wanted:
        cores, basis = wanted, "REQUESTED_CORES"
    elif usable:
        cores, basis = list(config["with_questions"]), "SUPPLIED_QUESTIONS"
    else:
        cores, basis = list(config["without_questions"]), "NO_QUESTION_BANK"
    notes = []
    if "CORE2" in cores and not usable:
        notes.append("CORE2_REQUESTED_WITHOUT_QUESTION_TEXT: acquire the source questions; do not invent a bank")
    deliverables: list[str] = []
    for name in cores:
        deliverables += [f"{name.lower()}_{item}" for item in config["per_core"]]
        deliverables += [f"{name.lower()}_{item}" for item in config.get("extra_by_core", {}).get(name, [])]
    deliverables += list(config["always"])
    stage = {"basis": basis, "cores": cores, "later_cores": [n for n in order if n not in cores],
             "notes": notes}
    return stage, deliverables, unknown


def research_tasks(prompts: list[dict], questions: list[dict], syllabus: list[dict], rec: dict) -> list[dict]:
    tasks: list[dict] = []

    def add(kind: str, input_id: str, needs: list[str]) -> None:
        tasks.append({"id": f"{kind}:{input_id}", "kind": kind, "input_id": input_id, "needs": needs})

    for row in prompts:
        add("interpret_prompt", row["id"], ["scope", "learner_goal"])
    for row in questions:
        if row["text_status"] == "LABEL_ONLY":
            add("recover_question_text", row["id"], ["original_text", "source_locator"])
        if row["identity_claim_requested"]:
            add("resolve_source_identity", row["id"], ["source_text", "matching_conditions", "discriminator"])
        add("solve_and_explain", row["id"], ["worked_answer", "hint", "visual"])
    outside = set(rec["questions_outside_syllabus"])
    for row in questions:
        if row["id"] in outside:
            add("place_unmatched_question", row["id"], ["owning_subtopic", "teaching"])
    for row in syllabus:
        add("teach_subtopic", row["id"], ["explanation", "worked_example", "visual", "misconception", "reconstruction"])
    for sid in rec["subtopics_without_questions"]:
        add("author_practice", sid, ["practice_question", "worked_answer"])
    return tasks


def intake(request: dict, workflow: dict | None = None) -> dict:
    workflow = workflow or load_workflow()
    subject = clean(request.get("subject"))
    prompts = _dedupe([{"id": item_id("p", t), "text": t}
                       for t in (clean(x) for x in _lines(request.get("prompts"))) if t])
    questions = _dedupe([_question(x) for x in _lines(request.get("questions"))])
    syllabus = _dedupe([{"id": item_id("s", t), "text": t}
                        for t in (clean(x) for x in _lines(request.get("syllabus"))) if t])
    errors = []
    if not subject:
        errors.append("subject is required (free text; no canonical id needed)")
    if not (prompts or questions or syllabus):
        errors.append("supply at least one prompt, question or syllabus subtopic")
    stage, deliverables, unknown_cores = first_stage(request, questions, workflow)
    if unknown_cores:
        errors.append("unknown Core in requested_cores: " + ", ".join(unknown_cores)
                      + " (use " + ", ".join(workflow["first_stage"]["core_order"]) + ")")

    learner = dict(workflow["default_learner_start"])
    owner = (request.get("learner") or {}).get("knowledge_percentage")
    owner_given = isinstance(owner, (int, float)) and not isinstance(owner, bool)
    learner.update({
        "source": "OWNER_ESTIMATE_AS_START_ONLY" if owner_given else "DEFAULT_MEDIAN",
        "knowledge_percentage": owner if owner_given else learner["knowledge_percentage"],
        "blocking": False,
    })
    rec = reconcile(questions, syllabus)
    inputs = {"prompts": prompts, "questions": questions, "syllabus": syllabus}
    ledger = [{"input_id": row["id"], "kind": kind, "teaching": None, "practice": None, "learner_location": None}
              for kind, rows in (("question", questions), ("syllabus", syllabus)) for row in rows]
    body = {
        "schema": SCHEMA,
        "workflow_digest": digest(workflow),
        "subject": subject,
        "grade": clean(request.get("grade")) or None,
        "learner_start": learner,
        "inputs": inputs,
        "reconciliation": rec,
        "research_tasks": research_tasks(prompts, questions, syllabus, rec),
        "coverage_ledger_template": ledger,
        "requested_cores": [name for name in workflow["first_stage"]["core_order"]
                            if name in set(_core_names(request.get("requested_cores")))],
        "first_stage": stage,
        "deliverables": deliverables,
        "invariants": [row["id"] for row in workflow["invariants"]],
        "status": STATUS if not errors else "INVALID_REQUEST",
        "errors": errors,
    }
    body["intake_digest"] = digest({"subject": subject, "grade": body["grade"], "inputs": inputs})
    return body


def browser_data(workflow: dict | None = None) -> str:
    body = json.dumps(workflow or load_workflow(), indent=1, ensure_ascii=False)
    return ("/* Generated by Shared/tools/raw_intake.py --write-browser-data from "
            "Shared/workflows/research-first.v1.json. Do not edit. */\n"
            f"window.GRADE9V3_RESEARCH_FIRST_WORKFLOW = {body};\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input")
    parser.add_argument("--out")
    parser.add_argument("--write-browser-data", action="store_true")
    parser.add_argument("--check-browser-data", action="store_true")
    args = parser.parse_args(argv)
    if args.write_browser_data:
        BROWSER_DATA.write_text(browser_data(), encoding="utf-8")
        return 0
    if args.check_browser_data:
        current = BROWSER_DATA.read_text(encoding="utf-8") if BROWSER_DATA.is_file() else ""
        if current != browser_data():
            print(f"{BROWSER_DATA.relative_to(REPO)} is stale; run --write-browser-data")
            return 1
        return 0
    if not args.input:
        parser.error("--input is required")
    result = intake(json.loads(Path(args.input).read_text(encoding="utf-8")))
    if result["errors"]:
        # With --out the JSON goes to a file, so the reason for a non-zero exit must not live only there.
        print(f"{result['status']}: " + "; ".join(result["errors"]), file=sys.stderr)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
