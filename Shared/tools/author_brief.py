#!/usr/bin/env python3
"""Compile the binding brief an authoring agent works from. Never write one by hand.

Every other claim in this repository must be derived from a record rather than
remembered. The authoring prompt was the exception -- produced from whoever happened to
recall the invariants that day -- which is the same defect class as the five the gates
already catch, sitting at the point that decides what gets authored at all.

A hand-written brief also goes stale silently. The moment a rung is authored, a line
saying it does not exist becomes false and the brief starts misleading. A compiled one
is regenerated, and its digest moves when the library moves.

Six inputs. Five already exist machine-readable; the matrix supplies the sixth.

  the rung, and whether it exists   the capability prerequisite chain
  what the product must contain     the role spec's `requires` block
  authority to bind                 gate_relation_ref, expression, conditions
  gates to pass                     the CI workflow
  what may not be consulted         the role invariants
  the vocabulary ceiling            the matrix  <- no schema home yet

Fails closed. No rung record means the brief emitted is the *rung-authoring* contract,
not the product one, because authoring a product against an absent rung is how an
existing rung gets diluted to serve a lower ladder position.
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

from Shared.contracts import digest, load  # noqa: E402
from Shared.tools.spec_conformance import requirements  # noqa: E402

WORKFLOW = REPO / ".github/workflows/guardrails.yml"


def matrix(subject: str, bucket_id: str) -> dict:
    for path in sorted((REPO / subject / "matrices").glob("*.rungs.json")):
        found = load(path)
        if found.get("bucket_id") == bucket_id:
            return {**found, "_path": str(path.relative_to(REPO)),
                    "_digest": digest(found)[:16]}
    raise SystemExit(f"no matrix for {bucket_id}")


def capability_chain(subject: str) -> tuple[dict, dict]:
    """Every capability and every microtopic's claim on one, across the subject."""
    caps, mics = {}, {}
    for path in sorted((REPO / subject / "library").glob("*.json")):
        package = load(path)
        for cap in package.get("capabilities", []):
            caps[cap["id"]] = cap
        for mic in package.get("microtopics", []):
            mics[mic["id"]] = mic
    return caps, mics


def rung_state(row: dict, caps: dict, mics: dict) -> dict:
    """Whether this rung has a record -- read from the library, never from the matrix.

    A matrix may claim SOURCE for a rung nobody authored. The library decides.
    """
    ref = row.get("microtopic_ref")
    if ref and ref in mics:
        mic = mics[ref]
        return {"state": "PRESENT", "microtopic": ref,
                "capability": mic.get("primary_capability_ref"),
                "entry": mic.get("entry_assumptions", []),
                "jump": mic.get("inferential_jump", "")}
    roots = sorted(c for c, v in caps.items() if not v.get("prerequisite_refs"))
    riders = [(c, caps[c].get("success_criterion", "")) for c in roots
              if re.search(r"\band\b", caps[c].get("success_criterion", ""))]
    return {"state": "ABSENT", "microtopic": ref,
            "root_capabilities": roots,
            "conjunctive_roots": riders}


def gates() -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.exists() else ""
    return sorted(set(re.findall(r"run: (python3 Shared/[^\n]+)", text)))


# The two layers read a percentage differently, and this is where that becomes
# executable rather than documented. On the teaching side a number can only be a
# curriculum coordinate, because Core1A/Core1B depth is intrinsic; on the practice side
# it is a routing input, which is the one place a learner estimate is admissible.
TEACHING = ("CORE1", "CORE1A", "CORE1B")
PRACTICE = ("CORE2A", "CORE2B")
# Thresholds only. What a level hands over is a property of the subtopic, not of the
# engine -- "observer named, axes declared" is true of relative motion and meaningless for
# thermodynamics -- so it is read from the matrix's family.support_ladder. The level names
# are the purpose vocabulary's, so the repository keeps one spelling of four things.
SUPPORT = [(0, "high"), (40, "medium"), (70, "low")]


def resolve(board: dict, knowledge: int, core: str) -> tuple[str | None, list[str]]:
    """Turn a requested percentage into something the named product may legally consume.

    Returns the rung to author and the lines explaining the translation. A percentage is
    never passed through untranslated: handing one to Core1A is how an existing rung gets
    taught more gently instead of the missing rung being written.
    """
    rungs = sorted(board["rungs"], key=lambda r: r.get("ladder_position", 0))
    positions = ", ".join(f'{r["rung"]}={r.get("ladder_position")}' for r in rungs)

    if core in PRACTICE:
        level = next(lvl for floor, lvl in reversed(SUPPORT) if knowledge >= floor)
        ladder = {row["level"]: row["handed_over"]
                  for row in (board.get("family") or {}).get("support_ladder", [])}
        lines = [
            f"## {knowledge}% read as a routing input", "",
            f"{core} is one of the two products permitted to consult capability evidence",
            "or an owner waiver, so this number is legal here -- for routing and support",
            "only. It may not be used to infer that a prerequisite is mastered.", "",
            f"  support level : {level}"]
        if level in ladder:
            lines += [f"  handed over   : {ladder[level]}"]
        else:
            # Fails closed rather than describing some other subtopic's support.
            lines += [f"  handed over   : AUTHOR_REQUIRED -- this family declares no",
                      f"                  support_ladder row for {level}, and what support",
                      f"                  hands over cannot be guessed from the engine."]
        return None, lines + [
            "", "All support levels are the same product. Removing help does not create",
            "transfer: the decision structure is unchanged. Changing it is Core2B.", ""]

    exact = [r for r in rungs if r.get("ladder_position") == knowledge]
    header = [f"## {knowledge}% read as a ladder position, not a learner estimate", "",
              f"{core} depth is intrinsic and may not shrink because a learner is",
              "estimated to know more, so the number cannot be consumed as given. It is",
              "resolved against this subtopic's ladder instead.", "",
              f"  ladder : {positions}", ""]
    if exact:
        return exact[0]["rung"], header + [f'  resolved : {knowledge}% -> {exact[0]["rung"]}', ""]
    below = [r for r in rungs if r.get("ladder_position", 0) < knowledge]
    above = [r for r in rungs if r.get("ladder_position", 0) > knowledge]
    return None, header + [
        "## STOP -- no rung sits at this position", "",
        f'  nearest below : {below[-1]["rung"] if below else "none"}',
        f'  nearest above : {above[0]["rung"] if above else "none"}', "",
        "This is a hole in the ladder, not a depth to interpolate. Teaching the rung",
        "above more gently is the forbidden move; the rung at this position has to be",
        "written. Add it to the matrix first, with its own aha, ceiling and closure.", "",
        "And never move an existing rung to this position to make this command resolve.",
        "ladder_position is a curriculum coordinate. Three matrices were edited that way",
        "before anyone noticed, which is why this paragraph exists: the probe is wrong,",
        "not the ladder. Probe at a position the ladder actually has.", ""]


def practice(board: dict, core: str) -> list[str]:
    """The family, and for the transfer product the rows that change its demand.

    Core2A and Core2B are two questions asked of one family: A selects or authors a
    familiar instance while preserving the family demand and decision structure; B varies
    the decision structure while preserving mathematics already taught. Both read the
    family; only B reads transfer, and a Core2B brief with no transfer row says so rather
    than offering the family twice.
    """
    family = board.get("family") or {}
    if not family:
        return ["## STOP -- this subtopic declares no question family", "",
                "A practice product with no invariant demand has nothing to vary and no",
                "check to hold an answer to. Write family{invariant_demand,",
                "difficult_move, independent_check} into the matrix first.", ""]
    out = ["## The family -- what every instance demands", "",
           f'  invariant demand  : {family["invariant_demand"]}',
           f'  difficult move    : {family["difficult_move"]}',
           f'  independent check : {family["independent_check"]}', ""]
    if core == "CORE2A":
        return out + [
            "Select or author a familiar same-family application whose invariant demand",
            "and decision structure stay unchanged. Surface details may vary, but synthetic",
            "number/object/cover-story variation is not required and is never the purpose",
            "of Core2A. Changing the demand is the other product.", ""]

    rows = board.get("transfer") or []
    if not rows:
        return out + [
            "## STOP -- this subtopic declares no transfer row", "",
            "Core2B cannot be built from the family alone: same-family practice with less",
            "help is Core2A with a label. Write transfer rows into the matrix first, each",
            "naming a changed demand and what is not handed over.", ""]
    out += [f"## Transfer -- {len(rows)} changed demands, one product each", ""]
    for row in rows:
        out += [f'  dimension  {row["dimension"]}',
                f'  demand     {row["changed_demand"]}',
                f'  NOT given  {row["information_not_handed_over"]}',
                f'  repairs to {row["repair_to"]}', ""]
    return out + [
        "A hint disclosing a row's NOT-given line turns that task back into Core2A.",
        "That is the one mechanical test of a transfer claim.", ""]


def required_content(core: str) -> list[str]:
    spec = REPO / f"Shared/roles/{core}.md"
    paths = [r for r in (requirements(spec) or []) if not r.get("author_only")]
    return ([f"## {core} required content -- {len(paths)} binding paths", ""]
            + [f'  {r["path"]:52} {r["phrase"]}' for r in paths] + [""])


def brief(subject: str, bucket_id: str, rung: str, core: str) -> str:
    board = matrix(subject, bucket_id)
    row = next((r for r in board["rungs"] if r["rung"] == rung), None)
    if row is None:
        raise SystemExit(f'{rung} is not a rung of {bucket_id} in {board["_path"]}')
    caps, mics = capability_chain(subject)
    state = rung_state(row, caps, mics)
    out = [f'# Authoring brief -- {core}, {board["subtopic"]}, rung {rung}',
           "",
           f'Compiled from {board["_path"]} ({board["_digest"]}) and the library. Do not',
           "hand-edit: regenerate. A brief that disagrees with the library is stale by",
           "construction.", ""]

    out += [f'## Rung {rung}: {row.get("aha") or state.get("jump", "(from the record)")}', ""]
    if row.get("learner_owns") or state.get("entry"):
        out += ["The learner arrives able to:"]
        out += [f'  - {x}' for x in (row.get("learner_owns") or state.get("entry"))] + [""]

    if state["state"] == "ABSENT":
        out += ["## STOP -- this rung has no record. The task is rung authoring.", "",
                "Authoring a product against an absent rung is how an existing rung gets",
                "diluted to serve a lower ladder position. Produce, in order:", "",
                "  1. a capability with ONE non-conjunctive success_criterion, below:",
                f'     {", ".join(state["root_capabilities"])}',
                "  2. the microtopic: entry_assumptions, inferential_jump, teaching_path with",
                "     why_valid per step, the misconception below, exit_task with an oracle",
                f'  3. only then the {core} projection', ""]
        for cap, criterion in state["conjunctive_roots"]:
            out += [f'Check first: {cap}.success_criterion is a conjunction --',
                    f'  "{criterion}"',
                    "A conceptual clause riding inside a procedural prerequisite is a rung",
                    "hiding in a delegation. Confirm whether it is this one.", ""]
    else:
        out += [f'## Bind to {state["microtopic"]} (capability {state["capability"]})', "",
                "Copy `expression` exactly from the gate relation. `conditions` may narrow,",
                "never widen or reword.", ""]

    if row.get("ceiling"):
        out += ["## Vocabulary ceiling -- enforced, not stylistic", "",
                "The explanation may NOT use:", "",
                f'  {" · ".join(row["ceiling"])}', "",
                "Each presupposes what this rung teaches. A fluent explanation that uses",
                "them is the failure this ceiling exists to prevent.", ""]
    if row.get("must_contain"):
        out += ["## Must contain", ""] + [f'  - {x}' for x in row["must_contain"]] + [""]
    if row.get("misconception"):
        m = row["misconception"]
        out += ["## The wrong path, its diagnostic and its repair", "",
                f'  wrong idea : {m["wrong_idea"]}',
                f'  diagnostic : {m["diagnostic_prompt"]}',
                f'  repair     : {m["repair"]}', ""]
    for phase in row.get("controlled_variation", []):
        out += [f'## Controlled experience, phase {phase["phase"]}', "",
                f'  vary   {phase["vary"]}',
                f'  hold   {phase["hold"]}',
                f'  notice {phase["notice"]}', ""]
    if row.get("closure"):
        out += ["## Closure", "", f'  {row["closure"]}', ""]

    out += required_content(core)
    out += ["## Prohibited", "",
            "  - diluting an existing rung to serve a lower ladder position",
            "  - using a term the ceiling forbids",
            "  - filling an absent field instead of naming it AUTHOR_REQUIRED",
            f'  - consulting a knowledge estimate: {core} depth is intrinsic', ""]
    out += ["## Green before done", ""] + [f'  {g}' for g in gates()] + [""]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--rung", help="the rung to author, when it is already known")
    parser.add_argument("--knowledge", type=int,
                        help="a requested percentage; translated per layer, never passed "
                             "through as given")
    parser.add_argument("--core", default="CORE1A")
    args = parser.parse_args()
    if (args.rung is None) == (args.knowledge is None):
        raise SystemExit("give exactly one of --rung or --knowledge")

    rung, preface = args.rung, []
    if args.knowledge is not None:
        board = matrix(args.subject, args.bucket)
        rung, preface = resolve(board, args.knowledge, args.core)
        if rung is None:
            out = [f'# Authoring brief -- {args.core}, {board["subtopic"]}', ""] + preface
            if args.core in PRACTICE:
                out += practice(board, args.core) + required_content(args.core)
                out += ["## Prohibited", "",
                        "  - disclosing a transfer row's NOT-given line in any hint",
                        "  - presenting a low-support instance of the family as transfer",
                        "  - reading the percentage as evidence that a prerequisite is held",
                        ""]
                out += ["## Green before done", ""] + [f'  {g}' for g in gates()] + [""]
            print("\n".join(out))
            return 0
    print("\n".join(preface + [brief(args.subject, args.bucket, rung, args.core)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
