#!/usr/bin/env python3
"""Completion gate for a governed minimal-prompt QRT run.

This is the command a run uses for completion evidence. It combines:
- the shared custody/QRT/exact-render guard;
- item-level author self-audits plus mandatory Chromium receipts for interactive HTML;
- learner-purpose transfer requirements;
- learner-facing presentation-value checks; and
- exact-byte Chromium evidence for staged instructional SVGs.

None of these layers replaces independent academic judgement or the H/S/P/M review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Shared.tools import qrt_content_self_audit as content_audit
from Shared.tools import qrt_learner_value_guard as learner_value
from Shared.tools import qrt_pipeline_guard as pipeline_guard
from Shared.tools import qrt_purpose_overlay as purpose_overlay
from Shared.tools import qrt_staged_svg_guard as staged_svg


def check(run: dict) -> list[str]:
    problems = pipeline_guard.check(run)
    problems.extend(content_audit.check(run, final=True))
    problems.extend(purpose_overlay.check_run(run, final=True))
    problems.extend(learner_value.check(run))
    problems.extend(staged_svg.check(run))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args(argv)
    try:
        run = json.loads(args.run.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"load failed: {exc}")
        return 1
    if not isinstance(run, dict):
        print("run must be a JSON object")
        return 1

    problems = check(run)
    if problems:
        print("\n".join(problems))
        return 1
    print("ok: qrt governed completion gate with purpose and staged-SVG audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
