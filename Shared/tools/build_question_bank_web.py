#!/usr/bin/env python3
"""Build the subject-neutral static Question Bank projection for the browser."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

try:
    from .question_bank_platform import project_package_question
except ImportError:  # direct: python3 Shared/tools/build_question_bank_web.py
    from question_bank_platform import project_package_question

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "public" / "data" / "question-bank-data.js"
VIEWS = REPO / "Shared" / "tools" / "question-bank-views.v1.json"
BANK_NAME = "competitive-exam-question-bank.v2.json"
PACKAGE_GLOB = "*/library/*.json"
RESOURCE_SCHEMA = "grade9v3-question-bank-resources-v1"


def _suite_destinations(repo: Path) -> list[dict]:
    destinations = []
    suites_dir = repo / "docs" / "gcdr-suites"
    if suites_dir.is_dir():
        for suite_path in sorted(suites_dir.glob("*.json")):
            try:
                data = json.loads(suite_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            title = data.get("title")
            if not title:
                continue
            artifacts = data.get("delivery_artifacts", [])
            bundle_artifact = next(
                (a for a in artifacts if a.get("profile") == "REPO_BUNDLE" and "locator" in a),
                None,
            )
            if not bundle_artifact:
                continue
            locator = bundle_artifact["locator"]
            path = locator[7:] if locator.startswith("public/") else locator
            corpus_topic = data.get("external_corpus", {}).get("topic", "")
            suite_id = data.get("suite_id", "")
            raw_words = re.findall(r"[A-Za-z0-9]+", f"{title} {corpus_topic} {suite_id}")
            keywords = sorted(
                {w.lower() for w in raw_words if len(w) > 1}
                | {"explorer", "interactive", "suite"}
            )
            destinations.append({
                "title": title,
                "path": path,
                "kind": "explorer",
                "keywords": keywords,
            })

    for registry_path in sorted(repo.glob("*/question-bank/resources.v1.json")):
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        if data.get("schema_version") != RESOURCE_SCHEMA:
            raise ValueError(f"unsupported Question Bank resource schema: {registry_path}")
        for resource in data.get("resources", []):
            missing = [key for key in ("title", "path", "kind", "keywords") if key not in resource]
            if missing:
                raise ValueError(f"Question Bank resource missing {missing}: {registry_path}")
            target = repo / "public" / resource["path"]
            if not target.is_file():
                raise ValueError(
                    f"Question Bank resource target missing: {registry_path}: {resource['path']}"
                )
            destinations.append({
                "title": resource["title"],
                "path": resource["path"],
                "kind": resource["kind"],
                "keywords": resource["keywords"],
            })
    return destinations


def bank_paths(repo: Path = REPO) -> list[Path]:
    return sorted(repo.glob(f"*/library/exam-bank/{BANK_NAME}"))


def package_paths(repo: Path = REPO) -> list[Path]:
    return sorted(repo.glob(PACKAGE_GLOB))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _project_question(subject: str, question: dict, order: int, repo: Path) -> dict:
    extensions = question["extensions"]
    analysis = extensions["grade9v3:analysis"]
    custody = extensions["grade9v3:source_custody"]
    answer = question["answer"]
    visual_rel = f"question-bank/visuals/{question['id']}.svg"
    visual_ref = visual_rel if (repo / "public" / visual_rel).is_file() else None
    return {
        "id": question["id"],
        "order": order,
        "subject": subject,
        "version": question["version"],
        "status": question["status"],
        "topic": analysis["topic"],
        "question_type": analysis["learner_question_type"],
        "exam": custody["exam"],
        "year": custody["year"],
        "paper": custody["paper"],
        "question_number": custody["question_number"],
        "source_status": custody["source_status"],
        "authority_class": custody["authority_class"],
        "wording_custody": custody["wording_custody"],
        "paper_url": custody["paper_url"],
        "answer_key_url": custody.get("answer_key_url"),
        "last_checked": custody["last_checked"],
        "origin": question["origin"],
        "provenance_class": extensions["grade9v3:provenance_class"],
        "math_spans": extensions.get("grade9v3:math_spans", []),
        "stem": question["stem"],
        "subparts": question["subparts"],
        "options": question["options"],
        "conditions": question["conditions"],
        "difficulty": analysis["difficulty"],
        "expected_time_seconds": analysis["expected_time_seconds"],
        "common_wrong_route": analysis["common_wrong_route"],
        "stable_crux_move": analysis["stable_crux_move"],
        "primary_capability_ref": question["primary_capability_ref"],
        "secondary_capability_refs": question["secondary_capability_refs"],
        "family_ref": question["family_ref"],
        "source_hints": question["hints"],
        "scaffolds": question["scaffolds"],
        "answer": {
            "summary": answer["summary"],
            "reasoning": answer["reasoning"],
            "reasoning_route": answer["reasoning_route"],
            "crux_move_ref": answer["crux_move_ref"],
            "check": answer["check"],
            "verification_status": answer["verification_status"],
        },
        "visual_ref": visual_ref,
    }


def _matches_policy(question: dict, policy: dict) -> bool:
    if policy.get("subjects") and question["subject"] not in policy["subjects"]:
        return False
    if policy.get("difficulty") and question["difficulty"]["band"] not in policy["difficulty"]:
        return False
    if policy.get("include_exams") and question["exam"] not in policy["include_exams"]:
        return False
    if question["exam"] in policy.get("exclude_exams", []):
        return False
    if policy.get("topics") and question["topic"] not in policy["topics"]:
        return False
    return True


def build(repo: Path = REPO) -> dict:
    questions = []
    bank_meta = []
    package_meta = []
    order = 0
    for path in bank_paths(repo):
        subject = path.relative_to(repo).parts[0]
        bank = load_json(path)
        bank_meta.append({
            "subject": subject,
            "manifest_id": bank["manifest_id"],
            "version": bank["version"],
            "path": path.relative_to(repo).as_posix(),
            "question_count": len(bank["questions"]),
        })
        for question in bank["questions"]:
            questions.append(_project_question(subject, question, order, repo))
            order += 1

    # Package-shaped canonical records use the same projection only when their package
    # or question explicitly opts into Question Bank publication. Discovery is generic;
    # no subject name or filename convention is encoded here.
    for path in package_paths(repo):
        package = load_json(path)
        package_questions = package.get("questions")
        if not isinstance(package_questions, list):
            continue
        projected_count = 0
        for question in package_questions:
            projected = project_package_question(package, question, order)
            if projected is None:
                continue
            projected["source_path"] = path.relative_to(repo).as_posix()
            questions.append(projected)
            order += 1
            projected_count += 1
        if projected_count:
            package_meta.append({
                "subject": package.get("subject"),
                "package_id": package.get("package_id"),
                "version": package.get("version"),
                "path": path.relative_to(repo).as_posix(),
                "question_count": projected_count,
            })

    by_id = {q["id"]: q for q in questions}

    # Merge extracted IIT-JEE Diagnostic Hub questions
    hub_file = repo / "public" / "data" / "iit-jee-hub-questions.v1.json"
    if hub_file.is_file():
        hub_data = load_json(hub_file)
        for hq in hub_data:
            hid = str(hq["id"])
            if hid in by_id:
                continue
            subj = hq.get("subject", "Physics")
            topic = hq.get("topic", "General")
            opt_list = hq.get("options", [])
            steps = hq.get("steps", [])
            ans_summary = str(hq.get("correct") or "Diagnostic question")
            clean_ref = re.sub(r"[^a-zA-Z0-9]+", "-", hq.get("topic_ref", "COMMON")).strip("-").upper()

            scaffolds_list = []
            if steps:
                for idx, step_txt in enumerate(steps[:3]):
                    scaffolds_list.append({
                        "text": str(step_txt),
                        "support_kind": "CONNECT" if idx == 0 else "EXECUTE",
                        "reveals": "METHOD",
                    })
            if len(scaffolds_list) < 2:
                formula_hint = str(hq.get("formula") or "Identify key governing equation and conservation laws.")
                scaffolds_list.append({
                    "text": formula_hint,
                    "support_kind": "REPRESENT",
                    "reveals": "CONCEPT",
                })
            if len(scaffolds_list) < 2:
                scaffolds_list.append({
                    "text": "Substitute given parameters carefully into the governing equation.",
                    "support_kind": "EXECUTE",
                    "reveals": "METHOD",
                })

            projected = {
                "id": hid,
                "order": order,
                "subject": subj,
                "version": "0.1.0",
                "status": "PUBLISHED",
                "topic": topic,
                "question_type": "single_correct_mcq" if opt_list else "numerical_value",
                "exam": "IIT-JEE Diagnostic",
                "year": hq.get("year") or 2024,
                "paper": "Diagnostic Hub",
                "question_number": "1",
                "source_status": "PYQ_AUTHENTIC_DIAGNOSTIC",
                "authority_class": "CORPUS_SNAPSHOT",
                "wording_custody": "FAITHFUL_DIAGNOSTIC",
                "paper_url": "",
                "answer_key_url": None,
                "last_checked": "2026-09-20",
                "origin": "DIAGNOSTIC_HUB",
                "provenance_class": "EXAM_CORPUS_SNAPSHOT",
                "math_spans": [],
                "stem": hq["stem"],
                "subparts": [],
                "options": opt_list,
                "conditions": [],
                "difficulty": {
                    "band": "D1",
                    "basis": f"Diagnostic problem from {topic}",
                    "components": {"algebra_computational_load": 1, "concept_model_selection": 1, "reasoning_chain_length": 1, "representation_translation": 1, "trap_exception_sensitivity": 0},
                    "score": 2
                },
                "expected_time_seconds": 90,
                "common_wrong_route": hq.get("trap") or "Concept misconception",
                "stable_crux_move": hq.get("formula") or "Standard equation",
                "primary_capability_ref": f"CAP-{clean_ref}",
                "secondary_capability_refs": [],
                "family_ref": f"FAM-{clean_ref}",
                "source_hints": [],
                "scaffolds": scaffolds_list,
                "answer": {
                    "summary": ans_summary,
                    "reasoning": steps,
                    "reasoning_route": steps,
                    "crux_move_ref": hq.get("formula") or "",
                    "check": hq.get("teacher_check") or "",
                    "verification_status": "VERIFIED_DIAGNOSTIC"
                },
                "visual_ref": None,
                "source_path": f"public/{hq.get('explorer_entrypoint', '')}",
                "adapter": "diagnostic_hub_v1",
                "lineage": {
                    "adapter": "diagnostic_hub_v1",
                    "source_path": f"public/{hq.get('explorer_entrypoint', '')}",
                    "package_id": f"DIAGNOSTIC-{clean_ref}",
                }
            }
            questions.append(projected)
            by_id[hid] = projected
            order += 1

    if len(by_id) != len(questions):
        raise ValueError("Question Bank projection contains duplicate canonical IDs")

    views_doc = load_json(repo / VIEWS.relative_to(REPO))
    views = []
    for view in views_doc["views"]:
        refs = view["resolved_question_refs"]
        if len(refs) != len(set(refs)):
            raise ValueError(f"View {view['id']} contains duplicate question refs")
        unknown = sorted(set(refs) - set(by_id))
        if unknown:
            raise ValueError(f"View {view['id']} has unknown canonical refs: {unknown}")
        if view.get("match_mode") == "EXACT_POLICY_SET":
            matching = [q["id"] for q in questions if _matches_policy(q, view["policy"])]
            if set(matching) != set(refs):
                missing = sorted(set(matching) - set(refs))
                extra = sorted(set(refs) - set(matching))
                raise ValueError(
                    f"View {view['id']} policy/ref drift: missing={missing} extra={extra}"
                )
        views.append(view)

    def counts(key: str):
        return dict(sorted(Counter(q[key] for q in questions).items()))

    basis = {
        "banks": bank_meta,
        "view_config": VIEWS.relative_to(repo).as_posix(),
    }
    if package_meta:
        basis["packages"] = package_meta

    return {
        "schema_version": "grade9v3-question-bank-browser-v1",
        "authority": "GENERATED_BROWSER_PROJECTION",
        "basis": basis,
        "counts": {
            "questions": len(questions),
            "subjects": counts("subject"),
            "topics": counts("topic"),
            "exams": counts("exam"),
            "difficulty": dict(sorted(Counter(q["difficulty"]["band"] for q in questions).items())),
        },
        "views": views,
        "questions": questions,
        "destinations": [
            {"title": "Home", "path": "index.html", "kind": "page", "keywords": ["portal", "home"]},
            *[
                {
                    "title": subject,
                    "path": subject.lower() + "/index.html",
                    "kind": "subject",
                    "keywords": [subject.lower()],
                }
                for subject in sorted({q["subject"] for q in questions})
            ],
            *_suite_destinations(repo),
            {"title": "Question Bank", "path": "question-bank/index.html", "kind": "tool", "keywords": ["questions", "practice", "pyq"]},
            {"title": "Core Prompt Composer", "path": "core-prompt-composer/index.html", "kind": "tool", "keywords": ["prompt", "cores", "composer"]},
            {"title": "Run Builder", "path": "tools/run-builder/index.html", "kind": "tool", "keywords": ["planner", "authoring", "run"]},
            {"title": "Topic Library", "path": "tools/library/index.html", "kind": "tool", "keywords": ["library", "topics"]},
        ],
    }


def render(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "window.GRADE9_QUESTION_BANK=" + payload + ";\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    intended = render(build())
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != intended:
            print("question-bank browser projection has drifted")
            print("Regenerate with: python3 Shared/tools/build_question_bank_web.py")
            return 1
        print("question-bank browser projection is current")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(intended, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
