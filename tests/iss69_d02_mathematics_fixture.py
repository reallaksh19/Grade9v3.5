from __future__ import annotations

import copy
import json
from pathlib import Path

from Shared.tools import render_core

REPO = Path(__file__).resolve().parents[1]
PACKAGE_PATH = REPO / "Mathematics/library/linear-equations.v1.json"
BLUEPRINTS_PATH = REPO / "Shared/web/interactive-page-blueprints.v1.json"
WITNESS = "Q-MAT-LEQ-04-EXEMPLAR9-4-3-Q7"
MICROTOPIC = "MIC-MAT-LEQ-04-TWO-VARIABLES-LINE-OF-SOLUTIONS"
TARGET_UNIT = "CU-MAT-LEQ-04-2"
REPRESENTATION = "REP-MAT-LEQ-04-SOLUTION-LINE"
QUALIFICATION_ASSET = "evidence/architectural-recovery/ISS69/d02/REP-MAT-LEQ-04-SOLUTION-LINE.qualification.svg"


def qualification_question(package: dict) -> dict:
    source = next(q for q in package["questions"] if q["id"] == WITNESS)
    q = copy.deepcopy(source)
    q["status"] = "CANDIDATE"

    extensions = q.setdefault("extensions", {})
    analysis = extensions.setdefault("grade9v3:analysis", {})
    analysis.update({
        "stable_crux_move": "Choose what counts as a solution in each setting: one coordinate on the number line, but an ordered pair on the Cartesian plane.",
        "common_wrong_route": "Solve for x = -4 and then assume the Cartesian-plane answer is also one solution.",
        "difficulty": {
            "band": "D2",
            "score": 5,
            "requested_band": "D2",
            "components": {
                "concept_model_selection": 2,
                "representation_translation": 1,
                "reasoning_chain_length": 1,
                "algebra_computational_load": 0,
                "trap_exception_sensitivity": 1
            },
            "basis": "The algebra is short; the decisive burden is changing the solution object from one coordinate to an ordered pair and noticing the unconstrained y-coordinate."
        }
    })
    extensions["grade9v3:cognitive_demand"] = {
        "primary": "MODEL",
        "secondary": ["REPRESENT"],
        "basis": "The decisive move is selecting the solution model appropriate to the setting, not executing the one-variable algebra."
    }

    # The source item has no source-given figure. The qualification intentionally
    # does not turn the Core1A teaching figure into a pre-attempt Core2 clue.
    q.pop("representation_roles", None)

    extensions["grade9v3:learning_repair"] = {
        "status": "GENERIC_REPAIR_CANDIDATE",
        "question_ref": WITNESS,
        "construction_ref": TARGET_UNIT,
        "crux_move_ref": "Q37-DEC",
        "clarify": "Keep the algebraic result x = -4 separate from the object called a solution in each setting.",
        "connect": "A point on a number line has one coordinate; a point on the Cartesian plane is an ordered pair.",
        "way": "First solve for x, then ask what coordinates remain free in the setting.",
        "rule": "A solution contains every coordinate needed by the setting, and any coordinate absent from the equation remains free.",
        "check": "Substitute two different pairs (-4, 0) and (-4, 5); both make the equation true.",
        "probe": "If x = 2 is the only restriction on a Cartesian plane, how many points satisfy it?",
        "pattern": "All points (2, y) satisfy the restriction, so the solution set is a vertical line.",
        "transfer": "For y = 3 on the Cartesian plane, describe the full solution set.",
        "wrong_idea": "One solved x-value means there is only one Cartesian-plane solution."
    }
    return q


def qualification_package() -> tuple[dict, dict, dict]:
    package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
    q = qualification_question(package)
    pkg = copy.deepcopy(package)

    # Replace only the qualification copy of the unmaterialised canonical visual.
    rep = next(r for r in pkg["representations"] if r["id"] == REPRESENTATION)
    rep["rendered_asset_refs"] = [QUALIFICATION_ASSET]
    rep.setdefault("extensions", {})["grade9v3:stage_mode"] = "REPLACE"

    microtopic = next(m for m in pkg["microtopics"] if m["id"] == MICROTOPIC)\n    target_unit = next(u for u in microtopic["construction_units"] if u["id"] == TARGET_UNIT)\n    target_unit["crux_question_refs"] = [WITNESS]\n    target_unit["crux_step_ref"] = "LEQ4-3"\n    manifest = {
        "schema": "product-manifest/v1",
        "product_id": "ISS69-D02-MATHEMATICS-QUALIFICATION",
        "title": "Mathematics qualification · linear-equation solution spaces",
        "subject": "Mathematics",
        "home_href": "index.html",
        "question_bank_href": "index.html",
        "package_refs": ["Mathematics/library/linear-equations.v1.json"],
        "bank_refs": [],
        "output_roles": ["CORE1A", "CORE2"],
        "selection": {
            "microtopics": [MICROTOPIC],
            "core2": [WITNESS],
            "core2a": [],
            "core2b": []
        }
    }
    return pkg, q, microtopic


def context() -> render_core.Ctx:
    package, q, microtopic = qualification_package()
    return render_core.Ctx(
        manifest={
            "schema": "product-manifest/v1",
            "product_id": "ISS69-D02-MATHEMATICS-QUALIFICATION",
            "title": "Mathematics qualification · linear-equation solution spaces",
            "subject": "Mathematics",
            "home_href": "index.html",
            "question_bank_href": "index.html",
            "output_roles": ["CORE1A", "CORE2"],
            "selection": {
                "microtopics": [MICROTOPIC],
                "core2": [WITNESS],
                "core2a": [],
                "core2b": []
            }
        },
        packages=[package],
        bank=[q],
        blueprints=json.loads(BLUEPRINTS_PATH.read_text(encoding="utf-8")),
        selection_rows={
            "microtopics": [microtopic],
            "core2": [q],
            "core2a": [],
            "core2b": []
        },
        authority_hashes=[
            ("qualification-package-source", render_core._file_sha256(PACKAGE_PATH)),
            ("qualification-visual", render_core._file_sha256(REPO / QUALIFICATION_ASSET)),
            ("blueprints", render_core._file_sha256(BLUEPRINTS_PATH))
        ]
    )


def render(out: Path) -> dict[str, str]:
    ctx = context()
    digest = render_core.render_digest(ctx)
    out.mkdir(parents=True, exist_ok=True)
    pages = {
        "core1a.html": render_core.page(ctx, "CORE1A", "SINGLE_FILE", digest),
        "core2.html": render_core.page(ctx, "CORE2", "SINGLE_FILE", digest)
    }
    for name, html in pages.items():
        (out / name).write_text(html, encoding="utf-8")
    return {"digest": digest, "gaps": ctx.gaps, "pages": list(pages)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.out), indent=2))
