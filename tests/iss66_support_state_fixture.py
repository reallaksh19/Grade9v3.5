from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import core2_v2, render_core
from tools import staged_set_b_replay as replay


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    ctx = replay.context()
    q = ctx.bank[2]  # frozen #55 Q1 pilot from the PR #65 staged replay
    plan = q["extensions"][core2_v2.SUPPORT_PLAN_KEY]
    protected = set(plan["protected_move_refs"])
    completion = next(
        item for item in plan["support_completions"]
        if protected.intersection(item["completed_move_refs"])
    )
    completion["availability"] = core2_v2.AFTER_ATTEMPT

    # Keep the WORKED visual at the legacy solution-only boundary so the browser
    # can distinguish after-attempt support from the full solution disclosure.
    for visual in plan.get("visuals", []):
        for stage in visual.get("stages", []):
            if protected.intersection(stage["completed_move_refs"]):
                stage["availability"] = core2_v2.POST_SOLUTION

    html = render_core.page(ctx, "CORE2", "SINGLE_FILE", render_core.render_digest(ctx))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html, encoding="utf-8", newline="\n")
    print(q["id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
