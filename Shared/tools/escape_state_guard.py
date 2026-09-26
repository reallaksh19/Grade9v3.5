#!/usr/bin/env python3
"""Fail when an agent-facing surface offers an escape state (HOLD, BLOCKED, WAITING, ...).

Agents read the role contracts and prompt templates, and receive composer prompts, planner
reports and execution packets. None of them may present a hold, block, wait or failure as an
outcome; each gap must arrive as a research or authoring duty
(Shared/workflows/research-first.v1.json). A line that names the forbidden states in order to
forbid them ("... are never an outcome") is allowed.

Usage:
    python3 Shared/tools/escape_state_guard.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import (compile_execution_packet, plan_request, prompt_composer,  # noqa: E402
                          research_first_policy)

TEXT_SURFACES = ("Shared/roles/*.md", "template/core-prompt-composer/*.json")
# Schema -> the outcome properties an agent acts on (None = every enum in the schema).
# Availability dimensions (READY/UNAVAILABLE per resource) describe inputs, not outcomes.
SCHEMA_SURFACES = {
    "Shared/library/prompt-brief.schema.json": None,
    "Shared/library/execution-packet.schema.json": None,
    "Shared/library/web-resolution-plan.schema.json": ("request_satisfaction", "build_action"),
}
COMPOSER_FIXTURES = "tests/fixtures/prompt-composer/*.json"
REQUEST_FIXTURES = ("Requests/*.plan-request.json", "Requests/*.author-request.json")
DEFINITION_LINE = re.compile(r"never an outcome|no hold, fail or incomplete outcome", re.IGNORECASE)


def _text_findings(rel: str, text: str, workflow: dict) -> list[dict]:
    rows = []
    for number, line in enumerate(text.splitlines(), start=1):
        if DEFINITION_LINE.search(line):
            continue
        for state in research_first_policy.escape_states(line, workflow):
            rows.append({"surface": f"{rel}:{number}", "state": state})
    return rows


def _enums(value: object) -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        out += [v for v in value.get("enum", []) if isinstance(v, str)]
        for child in value.values():
            out += _enums(child)
    elif isinstance(value, list):
        for child in value:
            out += _enums(child)
    return out


def _states(rel: str, values: list[str], workflow: dict) -> list[dict]:
    return [{"surface": rel, "state": state}
            for state in research_first_policy.escape_states(values, workflow)]


def audit(repo: Path = REPO) -> dict:
    workflow = research_first_policy.load_workflow()
    findings: list[dict] = []
    checked = 0
    for pattern in TEXT_SURFACES:
        for path in sorted(repo.glob(pattern)):
            checked += 1
            findings += _text_findings(str(path.relative_to(repo)), path.read_text(encoding="utf-8"), workflow)
    for rel, fields in SCHEMA_SURFACES.items():
        checked += 1
        schema = json.loads((repo / rel).read_text(encoding="utf-8"))
        scope = schema if fields is None else [schema["properties"][field] for field in fields]
        findings += _states(rel, _enums(scope), workflow)
    for path in sorted(repo.glob(COMPOSER_FIXTURES)):
        checked += 1
        rel = str(path.relative_to(repo))
        result = prompt_composer.compose(json.loads(path.read_text(encoding="utf-8")), repo)
        brief = result["prompt_brief"]
        findings += _text_findings(f"{rel} (agent prompt)", result["agent_prompt"], workflow)
        findings += _states(f"{rel} (brief states)", [
            brief["scope"]["status"], brief["planner_handoff"]["state"],
            brief["validation"]["composer_state"],
            *[row["mapping_status"] for row in brief["question_rows"]],
            *[row["identity_status"] for row in brief["question_rows"]],
            *[row["learner_eligibility"] for row in brief["question_rows"]],
            *[row["status"] for row in brief["duties"]],
        ], workflow)
    for pattern in REQUEST_FIXTURES:
        for path in sorted(repo.glob(pattern)):
            checked += 1
            rel = str(path.relative_to(repo))
            request = json.loads(path.read_text(encoding="utf-8"))
            report = plan_request.plan(request, repo)
            if "lifecycle" not in report:
                continue
            findings += _states(f"{rel} (plan states)", [
                *[row["state"] for row in report["products"]],
                *[report["lifecycle"][k]["state"] for k in ("AUTHORING", "BUILD", "RELEASE")],
                *report["readiness"].values(), report["learner_route"]["state"],
            ], workflow)
            if report["required_owner_inputs"]:
                findings.append({"surface": f"{rel} (plan)", "state": "OWNER_WAIT"})
            packet = compile_execution_packet.compile_packet(request, repo)
            findings += _states(f"{rel} (work orders)", [
                packet["packet_state"], *[row["authoring_action"] for row in packet["work_orders"]],
            ], workflow)
    return {"surfaces_checked": checked, "findings": findings, "passed": not findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.parse_args(argv)
    report = audit()
    for row in report["findings"]:
        print(f"{row['surface']}: {row['state']}")
    print(f"escape-state guard: {report['surfaces_checked']} surfaces, "
          f"{len(report['findings'])} findings")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
