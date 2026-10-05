"""Replay four frozen Set B failures through optional support structures.

This constructs partial question contexts, not accepted candidate packages.
Use: python tools/staged_set_b_replay.py --out <evidence-folder>
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from Shared.tools import core2_v2, render_core  # noqa: E402

FIXTURE = REPO / "tests/fixtures/staged_set_b/cases.json"
ASSETS = "tests/fixtures/staged_set_b"


def cases():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]


def adopt(case):
    """Add links without changing the frozen stem, answer or support wording."""
    q, rep = copy.deepcopy(case["question"]), copy.deepcopy(case["representation"])
    issue = case["issue"]
    moves = [move["id"] for move in q["answer"]["reasoning_route"]]
    completions = {53: {}, 54: {1: [moves[0]]},
                   55: {1: moves[:2], 2: moves[:2], 3: moves[:2], 4: [moves[2]]},
                   56: {2: [moves[1]]}}[issue]
    protected = moves[:3] if issue != 56 else moves[:2]
    rep["scene_instances"] = [{
        "id": f"ISS{issue}-CASE", "cores": ["CORE2"], "question_ref": q["id"],
        "datum_refs": [f"ISS{issue}-GIVENS"], "asset_ref": f"{ASSETS}/ISS{issue}-case.svg",
        "scene": {"kind": "QUESTION_CASE", "frame": "900x360", "caption": f"Question {case['question_number']}: stated givens and worked result"}}]
    rep["reveal_stages"] = [
        {"id": "GIVENS", "label": "Stated givens", "purpose": "Read the supplied information", "visible_elements": ["givens"]},
        {"id": "WORKED", "label": "Worked result", "purpose": "Check the result after your attempt", "visible_elements": ["worked"]}]
    q.setdefault("extensions", {})[core2_v2.SUPPORT_PLAN_KEY] = {
        "protected_move_refs": protected,
        "support_completions": [{"support_ref": f"scaffolds[{i}]", "completed_move_refs": completions.get(i, [])}
                                for i in range(len(q.get("scaffolds", [])))],
        "visuals": [{"representation_ref": rep["id"], "instance_ref": f"ISS{issue}-CASE", "stages": [
            {"stage_ref": "GIVENS", "completed_move_refs": []},
            {"stage_ref": "WORKED", "completed_move_refs": protected}]}]}
    datum = {"id": f"ISS{issue}-GIVENS", "version": "1.0.0", "status": "CANDIDATE", "source_refs": [],
             "evidence_refs": [f"https://github.com/reallaksh19/Grade9v3.5/issues/{issue}"], "extensions": {},
             "kind": "EQUATION", "locator": f"Owner-authored issue #{issue} Q{case['question_number']}; frozen head {case['head_sha']}",
             "meaning": "Exact question givens; no source publication is claimed.",
             "value": '<math xmlns="http://www.w3.org/1998/Math/MathML"><mtext>' + html.escape(q["stem"]) + '</mtext></math>'}
    return q, rep, datum


def context(adopted=True):
    questions, representations, data = [], [], []
    for case in cases():
        if adopted:
            q, rep, datum = adopt(case)
            data.append(datum)
        else:
            q, rep = copy.deepcopy(case["question"]), copy.deepcopy(case["representation"])
        questions.append(q)
        representations.append(rep)
    authority_paths = [FIXTURE, Path(__file__), render_core.PACKAGE_SCHEMA, render_core.BANK_SCHEMA,
                       Path(render_core.__file__), Path(core2_v2.__file__), render_core.BLUEPRINTS,
                       render_core.TABLET_CSS, REPO / "public/css/modern-learner.css",
                       REPO / "public/js/display-controls.js", REPO / "public/js/site-header.js"]
    authority_paths.extend(REPO / ref for rep in representations for ref in rep["rendered_asset_refs"])
    authority_paths.extend(REPO / scene["asset_ref"] for rep in representations for scene in rep.get("scene_instances", []))
    return render_core.Ctx(
        manifest={"product_id": "ISS29-STAGED-SET-B-REPLAY", "subject": "Mathematics",
                  "title": "Polynomial questions · staged repair replay", "home_href": "../../../../public/index.html",
                  "question_bank_href": "../../../../public/Mathematics/question-bank/index.html", "output_roles": ["CORE2"]},
        packages=[{"representations": representations, "data": data}], bank=questions,
        selection_rows={"core2": questions, "microtopics": [], "core2a": [], "core2b": []},
        blueprints=render_core.load_json(render_core.BLUEPRINTS),
        authority_hashes=[(path.relative_to(REPO).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
                          for path in authority_paths])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    report = {"schema": "staged-support-replay/v1", "scope": "Four partial question contexts; no candidate acceptance or publication.",
              "fixture_sha256": "sha256:" + hashlib.sha256(FIXTURE.read_bytes()).hexdigest(), "pages": [], "cases": []}
    for adopted, name in [(False, "before.html"), (True, "core2.html")]:
        ctx = context(adopted)
        output = render_core.page(ctx, "CORE2", "SINGLE_FILE", render_core.render_digest(ctx))
        path = args.out / name
        path.write_text(output, encoding="utf-8")
        report["pages"].append({"path": name, "sha256": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
                                "authority_hashes": ctx.authority_hashes, "render_gaps": ctx.gaps, "advisories": ctx.advisories})
    for case in cases():
        q, rep, datum = adopt(case)
        report["cases"].append({"issue": case["issue"], "head_sha": case["head_sha"], "question_ref": q["id"],
                                "stem_preserved": q["stem"] == case["question"]["stem"],
                                "answer_preserved": q["answer"] == case["question"]["answer"],
                                "support_text_preserved": q["scaffolds"] == case["question"]["scaffolds"],
                                "deferred_support": [r["source"] for r in core2_v2.project_support(q) if not r["eligible_pre_solution"]],
                                "selected_asset": rep["scene_instances"][0]["asset_ref"]})
    (args.out / "replay-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": [p["path"] for p in report["pages"]], "scope": report["scope"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
