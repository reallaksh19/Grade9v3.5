#!/usr/bin/env python3
"""A matrix may reference the library. It may not restate it, and it may not outrank it.

The matrix is the human-authored half of the pipeline -- the ladder, each rung's
vocabulary ceiling and controlled experience, the family, the transfer rows. It feeds the
authoring brief and never the product compiler, so a claim in it reaches no learner until
a record carries it.

Two rules make that safe, and they are the A4 discipline applied to a new layer.

  the library decides   a row may claim SOURCE for a rung nobody authored. Existence is
                        read from the records, and a disagreement is the matrix's fault.
  reference, never copy where a microtopic exists it owns its jump, its misconceptions
                        and its exit task. A matrix restating them is a second authority
                        for one claim, and the two will drift.

Everything else checked here is internal consistency the schema cannot express: the
ladder is ordered and its positions unique, a rung nothing teaches still says what it is,
a phase's hold is stated, a transfer row names a rung that exists, and a dimension is one
the subject already declares rather than a fifth spelling of four things.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import load, normalise  # noqa: E402
from Shared.tools import capability_graph  # noqa: E402

SCHEMA = REPO / "Shared/library/matrix.schema.json"
# Where a record exists, these belong to it. A matrix carrying them is the second copy.
RECORD_OWNED = ("aha", "learner_owns", "misconception", "closure")


def library(subject: str) -> tuple[dict, set[str]]:
    """Microtopics by id, and every demand dimension this subject declares."""
    mics, dimensions = {}, set()
    for path in sorted((REPO / subject / "library").glob("*.json")):
        package = load(path)
        for mic in package.get("microtopics", []):
            mics[mic["id"]] = mic
        for family in package.get("question_families", []):
            dimensions |= set(family.get("demand_dimensions", {}))
    return mics, dimensions


def findings(board: dict, mics: dict, dimensions: set[str]) -> list[dict]:
    found: list[dict] = []

    def fail(point: str, where: str, detail: str):
        found.append({"point": point, "where": where, "detail": detail})

    seen_positions, seen_rungs = {}, set()
    previous = None
    for row in board.get("rungs", []):
        rung, position = row["rung"], row["ladder_position"]
        if rung in seen_rungs:
            fail("RUNG_LABEL_REUSED", rung, "two rows share a label")
        seen_rungs.add(rung)
        if position in seen_positions:
            fail("LADDER_POSITION_REUSED", rung,
                 f"position {position} is also {seen_positions[position]}; a ladder is ordered")
        seen_positions[position] = rung
        if previous is not None and position <= previous:
            fail("LADDER_OUT_OF_ORDER", rung,
                 f"position {position} follows {previous}; rows must ascend")
        previous = position

        ref = row.get("microtopic_ref")
        if row["provenance"] in ("SOURCE", "AUTHORED"):
            if not ref:
                fail("PROVENANCE_CLAIMS_A_RECORD_WITH_NO_REF", rung,
                     f'claims {row["provenance"]} and names no microtopic')
            elif ref not in mics:
                # The library decides. A matrix asserting a record exists does not make
                # one, and this is the direction the disagreement must be resolved in.
                fail("PROVENANCE_DISAGREES_WITH_LIBRARY", rung,
                     f"claims {row['provenance']} for {ref}, which the library does not hold")
        if ref and ref in mics:
            for field in RECORD_OWNED:
                if field in row:
                    fail("MATRIX_RESTATES_THE_RECORD", f"{rung}.{field}",
                         f"{ref} owns this; a second copy is a second authority and they drift")
        if row["provenance"] == "ABSENT" and ref and ref in mics:
            fail("PROVENANCE_DISAGREES_WITH_LIBRARY", rung,
                 f"claims ABSENT while the library holds {ref}")

        # The complement of MATRIX_RESTATES_THE_RECORD, and the hole it left. Where a
        # record exists it owns these four; where none does, the matrix is the only place
        # they can be. A row carrying a position and nothing else passed every check above
        # and compiled a brief reading "Rung R1: (from the record)" -- pointing at a record
        # the same row says is absent.
        if ref not in mics and row["provenance"] in ("SYNTHESIS", "ABSENT"):
            if not str(row.get("aha", "")).strip():
                fail("RUNG_NAMES_NO_JUMP", rung,
                     "nothing teaches this rung and the row does not say what it is; a "
                     "hole in the ladder must be visible, and a bare position is not")
            if row["provenance"] == "SYNTHESIS":
                # ABSENT may stop at naming the hole -- saying more would be invention.
                # SYNTHESIS claims the row was constructed, so it is the only copy there
                # is and an authoring brief has nowhere else to read these from.
                missing = [field for field in RECORD_OWNED[1:] if not row.get(field)]
                if missing:
                    fail("SYNTHESIS_INCOMPLETE", rung,
                         f'claims construction but carries no {", ".join(missing)}; mark '
                         f"it ABSENT rather than inventing the rest")

        for phase in row.get("controlled_variation", []):
            if not str(phase.get("hold", "")).strip():
                fail("PHASE_HOLDS_NOTHING", f'{rung}.phase{phase.get("phase")}',
                     "an experience with no invariant cannot show one")

    # The matrix coordinate is presentation order; capability prerequisites are the
    # reachability authority. A mechanically valid row order may still be impossible to
    # learn if a dependant appears before one of its prerequisites.
    if board.get("subject"):
        caps, graph_mics = capability_graph.subject_graph(board["subject"])
        found.extend(capability_graph.topology_findings(board, caps, graph_mics))

    for row in board.get("transfer", []):
        if dimensions and row["dimension"] not in dimensions:
            fail("TRANSFER_DIMENSION_UNDECLARED", row["dimension"],
                 f'not a demand dimension this subject declares; it declares '
                 f'{", ".join(sorted(dimensions)) or "none"}')
        if row["repair_to"] not in seen_rungs:
            fail("TRANSFER_REPAIRS_TO_NO_RUNG", row["dimension"],
                 f'repairs to {row["repair_to"]}, which is not a rung of this ladder')
        if normalise(row["information_not_handed_over"]) == normalise(row["changed_demand"]):
            fail("WITHHELD_RESTATES_THE_DEMAND", row["dimension"],
                 "what is withheld must be narrower than the demand, or the row says "
                 "nothing a hint could violate")

    family = board.get("family") or {}
    demand = normalise(family.get("invariant_demand", ""))
    levels = set()
    for row in family.get("support_ladder", []):
        level = row["level"]
        if level in levels:
            fail("SUPPORT_LEVEL_REUSED", level, "two rows describe the same level")
        levels.add(level)
        if demand and normalise(row["handed_over"]) == demand:
            # Support removes work. Handing over the invariant demand removes the
            # decision, and what is left is transcription wearing a practice label.
            fail("SUPPORT_HANDS_OVER_THE_DEMAND", level,
                 "the invariant demand handed over as support is the Core2A/Core2B "
                 "collapse, from the support side")
    return found


def board_findings(board: dict, validator=None) -> list[dict]:
    """One board's findings: its structure first, then its meaning.

    The semantic checks read a rung as a mapping with a label and a position; running them on a board that is not yet
    that shape turned a malformed file into a traceback, and a traceback names no rule. Found by feeding the gate the
    shapes thirteen parallel authors could produce, rather than the one committed board that is already well formed."""
    if validator is None:
        try:
            import jsonschema
        except ModuleNotFoundError:
            jsonschema = None
        validator = jsonschema.Draft202012Validator(load(SCHEMA)) if jsonschema is not None else None
    structural = ([{"point": "MATRIX_STRUCTURE", "where": "/".join(str(p) for p in e.path), "detail": e.message}
                   for e in validator.iter_errors(board)] if validator else [])
    return structural or findings(board, *library(board.get("subject", "")))


def audit(repo: Path = REPO) -> dict:
    try:
        import jsonschema
    except ModuleNotFoundError:
        jsonschema = None
    validator = (jsonschema.Draft202012Validator(load(SCHEMA))
                 if jsonschema is not None else None)
    rows = []
    for path in sorted(repo.glob("*/matrices/*.rungs.json")):
        board = load(path)
        found = board_findings(board, validator)
        rows.append({"matrix": str(path.relative_to(repo)),
                     "bucket": board.get("bucket_id"),
                     "rungs": len(board.get("rungs") or []), "findings": found,
                     "passed": not found})
    return {"matrices": len(rows), "boards": rows,
            "findings": sum(len(r["findings"]) for r in rows),
            "passed": all(r["passed"] for r in rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
