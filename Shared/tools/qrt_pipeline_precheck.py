#!/usr/bin/env python3
"""Fail early on custody/QRT/Blueprint/Core1A, purpose and item-self-audit defects before HTML rendering."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Shared.tools import qrt_content_self_audit as content_audit
from Shared.tools import qrt_pipeline_guard as guard
from Shared.tools import qrt_purpose_overlay as purpose_overlay


def precheck(run: dict) -> list[str]:
    if run.get("schema") != "qrt-pipeline-run/v1":
        return ["schema must be qrt-pipeline-run/v1"]
    try:
        registry = guard.load(guard.BLUEPRINTS)
    except Exception as exc:
        return [f"BLUEPRINT_REGISTRY_LOAD_FAILED: {exc}"]
    problems: list[str] = []
    problems.extend(guard.validate_owner_truth(run))
    problems.extend(guard.validate_basis_digests(run))
    problems.extend(guard.validate_slots(run))
    problems.extend(content_audit.validate_content_self_audits(run))
    problems.extend(purpose_overlay.check_run(run, final=False))
    problems.extend(guard.validate_pre_attempt_graphs(run))
    problems.extend(guard.validate_blueprints(run, registry))
    problems.extend(guard.validate_core1a_boundary(run))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    try:
        value = json.loads(args.run.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"load failed: {exc}")
        return 1
    if not isinstance(value, dict):
        print("run must be a JSON object")
        return 1
    problems = precheck(value)
    if problems:
        print("\n".join(problems))
        return 1
    print("ok: qrt minimal-prompt pre-render check with purpose and item self-audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
