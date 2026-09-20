#!/usr/bin/env python3
"""What a person asks for, turned into a build plan -- or into a named refusal.

The production input this repository never had. Every gate below it could refuse bad
content; nothing could answer *"create Core1A, 1B, 2A and 2B for relative motion"*,
because three inputs had no home:

  which rung to start at    the learner's per-capability state, or an owner's decision
  what 2A is for            a purpose, which carries its own support level
  what 2B is for            a purpose, which decides whether transfer is routed at all

Two rules come from layers already built here, and both survive into this one.

  selection, not dilution   a knowledge input selects the ENTRY rung. It never changes
                            what a rung teaches. Core1A depth is intrinsic, so a learner
                            thought to know more starts higher and is taught no less.
  a number is a decision    `knowledge_percentage` is stored and never computed from. So
                            a request cannot carry a bare percentage: it carries a profile,
                            an owner's named entry rung, or an owner estimate that says on
                            its face that it is one. The schema makes this unavoidable.

The practice side needs no percentage at all. A purpose already declares its support
level, and support and placement were previously the same number doing two jobs.

Fails closed everywhere it cannot answer. The most useful refusal is
ENTRY_UNDECIDABLE_FROM_THE_PROFILE: a ladder whose lower rungs have no records has no
capabilities to observe, so nobody can be placed on it -- which is a fact about the
library, reported here rather than papered over with a default.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import load  # noqa: E402
from Shared.library.practice_inventory import questions_for_core  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402
from Shared.tools import (atlas_need, capability_graph, core_focus, focus_inventory,\n                          learner_evidence)  # noqa: E402
from Shared.tools.author_brief import capability_chain, rung_state  # noqa: E402

SCHEMA = REPO / "Shared/library/request.schema.json"
VOCABULARY = REPO / "Shared/vocabularies/purpose.json"
REQUESTS = "Requests"
PROFILES = "Learners/profiles"
TEACHING = ("CORE1", "CORE1A", "CORE1B")
PRACTICE = ("CORE2A", "CORE2B")
TRANSFER = "CORE2B"


def purposes() -> dict:
    return {p["id"]: p for p in load(VOCABULARY)["purposes"]}


def profiles(repo: Path = REPO) -> dict:
    return {p["profile_id"]: p for path in sorted((repo / PROFILES).glob("*.json"))
            for p in [load(path)]}


def ladder(subject: str, bucket_id: str, repo: Path = REPO) -> dict | None:
    for path in sorted((repo / subject / "matrices").glob("*.rungs.json")):
        board = load(path)
        if board.get("bucket_id") == bucket_id:
            return {**board, "_path": str(path.relative_to(repo))}
    return None


def library_records(subject: str, repo: Path = REPO) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))



def automatic_entry_rows(rows: list[dict]) -> list[dict]:
    """Rows eligible for generic profile/estimate placement and the default route.

    A false flag keeps a canonical rung available for explicit extension/question demand
    while preventing missing evidence or a rough percentage from turning that extension
    into an ordinary learner requirement. Absence means eligible for backward compatibility.
    """
    return [row for row in rows if row.get("default_entry_eligible", True)]


def entry_from_profile(rows: list, profile: dict, caps: dict, mics: dict) -> dict:
    """The lowest default-route rung this learner cannot yet do.

    Never from `knowledge_percentage`: reading placement off an aggregate is the inference
    the role specs forbid, and the field exists to be stored rather than consulted.
    Non-default extension rungs remain canonical but do not gate ordinary progression.
    """
    rows = automatic_entry_rows(rows)
    held = profile.get("held", {})
    for row in rows:
        state = rung_state(row, caps, mics)
        capability = state.get("capability")
        if state["state"] == "ABSENT" or not capability:
            return {"rung": None, "why": "UNDECIDABLE", "at": row["rung"],
                    "detail": f'{row["rung"]} has no record, so it declares no capability '
                              f"to observe; nobody can be placed against it"}
        if held.get(capability) != "DEMONSTRATED":
            return {"rung": row["rung"], "why": "FIRST_NOT_DEMONSTRATED",
                    "capability": capability,
                    "detail": f'{capability} is {held.get(capability) or "unrecorded"}'}
    return {"rung": None, "why": "ABOVE_THE_LADDER",
            "detail": "every rung's capability is demonstrated; this ladder has nothing "
                      "left to teach this learner"}


def entry_from_position(rows: list, position: int) -> dict:
    """Use an owner estimate as a conservative default-route coordinate, never as mastery.

    A parent's "about 60%" is useful even when the ladder happens to use 20/55/70/85.
    Select the greatest default-entry position not above the estimate; below the first rung,
    start at the first rung. Extension-only coordinates do not become ordinary targets merely
    because a percentage crosses them. Earlier capabilities are never marked demonstrated.
    """
    rows = automatic_entry_rows(rows)
    if not rows:
        return {"rung": None, "why": "EMPTY_LADDER",
                "detail": "the ladder has no positions to route against"}
    ordered = sorted(rows, key=lambda r: r.get("ladder_position", 0))
    eligible = [row for row in ordered if row.get("ladder_position", 0) <= position]
    selected = eligible[-1] if eligible else ordered[0]
    return {
        "rung": selected["rung"],
        "why": "OWNER_ESTIMATE_CONSERVATIVE_FLOOR",
        "requested_position": position,
        "selected_position": selected.get("ladder_position"),
        "detail": (
            f'owner estimate {position} routed conservatively to '
            f'{selected["rung"]} at {selected.get("ladder_position")}; '
            "this is a starting coordinate, not evidence of prerequisite mastery"
        ),
    }


def resolve_owner_estimate(rows: list, position: int, caps: dict, mics: dict) -> dict:
    """Respect a rough owner estimate while naming what still has not been evidenced.

    The estimate is allowed to choose a starting rung because that is the practical value
    of asking for it. Its prerequisite closure is returned as quick-check candidates,
    not converted into DEMONSTRATED states and not used to force the learner back to the
    bottom before she has attempted anything.
    """
    entry = entry_from_position(rows, position)
    if not entry.get("rung"):
        return {**entry, "prerequisite_checks": [], "bridges": [],
                "unresolved_prerequisites": []}

    board = {"rungs": rows}
    by_rung, _ = capability_graph.ladder_capabilities(board, mics)
    target = by_rung.get(entry["rung"])
    if target is None:
        return {
            **entry,
            "capability": None,
            "prerequisite_checks": [],
            "bridges": [],
            "unresolved_prerequisites": [],
        }

    capability = target["capability"]
    checks = capability_graph.prerequisite_closure(capability, caps)
    unresolved = capability_graph.unknown_prerequisites([capability], caps)
    return {
        **entry,
        "capability": capability,
        "prerequisite_checks": checks,
        "bridges": [],
        "unresolved_prerequisites": unresolved,
        "prerequisite_policy": "CHECK_IF_NEEDED_DO_NOT_ASSUME_MASTERED",
    }


def plan(request: dict, repo: Path = REPO, diagnostic: dict | None = None) -> dict:
    """The build plan and every finding against it. Never raises on content."""
    found: list[dict] = []

    def fail(point: str, where: str, detail: str):
        found.append({"point": point, "where": where, "detail": detail})

    subject, bucket_id = request.get("subject", ""), request.get("bucket_id", "")
    cores = list(request.get("cores", []))
    vocabulary, store = purposes(), profiles(repo)
    board = ladder(subject, bucket_id, repo)
    if board is None:
        fail("REQUEST_BUCKET_HAS_NO_MATRIX", bucket_id,
             f"no {subject}/matrices/*.rungs.json declares this bucket, so there is no "
             f"ladder to place anyone on")
        return {"request": request.get("request_id"), "findings": found, "cores": [],
                "passed": False}

    rows = sorted(board.get("rungs", []), key=lambda r: r.get("ladder_position", 0))
    caps, mics = capability_chain(subject)
    records = library_records(subject, repo)
    for finding in capability_graph.topology_findings(board, caps, mics):
        found.append(finding)

    # --- entry rung -------------------------------------------------------------
    learner = request.get("learner", {})
    entry, provenance = {"rung": None, "why": "NO_LEARNER_BLOCK"}, "NONE"
    explicit_nondefault = False
    if "profile_ref" in learner:
        profile = store.get(learner["profile_ref"])
        if profile is None:
            fail("PROFILE_REF_DANGLING", learner["profile_ref"],
                 f"no profile in {PROFILES} carries this id")
        elif profile.get("provenance") == "SYNTHETIC_TEST":
            fail("SYNTHETIC_PROFILE_ROUTED", learner["profile_ref"],
                 "a synthetic profile is a fixture; routing one produces a real product "
                 "for a learner who does not exist")
        else:
            provenance = profile.get("provenance", "UNKNOWN")
            effective = {**profile, "held": learner_evidence.effective_held(profile, repo)}
            entry = entry_from_profile(rows, effective, caps, mics)
            if entry["why"] == "UNDECIDABLE":
                fail("ENTRY_UNDECIDABLE_FROM_THE_PROFILE", entry["at"], entry["detail"])
    elif "owner_entry" in learner:
        provenance, named = "OWNER_DECISION", learner["owner_entry"]["rung"]
        entry = {"rung": named, "why": "OWNER_NAMED"}
        named_row = next((row for row in rows if row["rung"] == named), None)
        if named_row is None:
            fail("ENTRY_RUNG_NOT_ON_THE_LADDER", named,
                 f'this ladder runs {", ".join(r["rung"] for r in rows) or "empty"}')
            entry = {"rung": None, "why": "OWNER_NAMED_AN_ABSENT_RUNG"}
        else:
            explicit_nondefault = not named_row.get("default_entry_eligible", True)
    elif "owner_estimate" in learner:
        provenance = "OWNER_ESTIMATE"
        entry = resolve_owner_estimate(
            rows,
            learner["owner_estimate"]["knowledge_percentage"],
            caps,
            mics,
        )
        if entry.get("unresolved_prerequisites"):
            fail(
                "ENTRY_PREREQUISITE_UNRESOLVED",
                entry.get("rung") or "OWNER_ESTIMATE",
                "prerequisites are unknown: "
                + ", ".join(entry["unresolved_prerequisites"]),
            )

    # A profile or explicitly named rung still uses strict prerequisite safety. A rough
    # owner estimate is different: it is useful only if it can choose where to try first.
    # Its prerequisites remain explicitly unverified and can be checked/diagnosed during
    # use; they are never silently marked as held.
    held = {}
    if "profile_ref" in learner and learner["profile_ref"] in store:
        held = learner_evidence.effective_held(store[learner["profile_ref"]], repo)
    if (
        provenance != "OWNER_ESTIMATE"
        and entry.get("rung") in {r["rung"] for r in rows}
    ):
        safe = capability_graph.resolve_entry(rows, entry["rung"], held, caps, mics)
        requested_rung = entry["rung"]
        entry["rung"] = safe["rung"]
        entry["bridges"] = safe["bridges"]
        entry["unresolved_prerequisites"] = safe["unresolved"]
        entry.setdefault("prerequisite_checks", [])
        if safe["reason"] == "PREREQUISITE_BACKTRACK":
            entry["requested_rung"] = requested_rung
            entry["why"] = "PREREQUISITE_BACKTRACK"
            entry["detail"] = (
                f'{requested_rung} was requested, but {safe["rung"]} is the earliest '
                "same-ladder prerequisite not demonstrated"
            )
        if safe["unresolved"]:
            fail("ENTRY_PREREQUISITE_UNRESOLVED", entry["rung"],
                 "prerequisites have no recorded bridge: " + ", ".join(safe["unresolved"]))

    segment_rows = rows if explicit_nondefault else automatic_entry_rows(rows)
    positions = {r["rung"]: r.get("ladder_position", 0) for r in segment_rows}
    segment = ([r["rung"] for r in segment_rows
                if positions[r["rung"]] >= positions[entry["rung"]]]
               if entry.get("rung") in positions else [])
    # Practice varies instances of what teaching established, and transfer changes the
    # demand while holding truth already taught. Both presuppose a taught rung, so a
    # ladder with no records supports neither -- found by planning every bucket in a
    # subject instead of the one with a library behind it.
    taught = sum(1 for row in rows if rung_state(row, caps, mics)["state"] == "PRESENT")

    # --- purposes ---------------------------------------------------------------
    practice = request.get("practice", {})
    for core in practice:
        if core not in cores:
            fail("PURPOSE_FOR_A_CORE_NOT_REQUESTED", core,
                 "a purpose was declared for a product this request does not ask for")
    for core in [c for c in cores if c in PRACTICE]:
        if core not in practice:
            fail("PRACTICE_CORE_WITHOUT_A_PURPOSE", core,
                 "what the run is for decides its support and whether transfer is routed; "
                 "there is no default that would not be a guess")
        elif practice[core]["purpose"] not in vocabulary:
            fail("PURPOSE_UNKNOWN", practice[core]["purpose"],
                 f'not declared in the vocabulary, which declares '
                 f'{", ".join(sorted(vocabulary))}')
        elif core == TRANSFER and not vocabulary[practice[core]["purpose"]]["routes_transfer"]:
            fail("TRANSFER_REQUESTED_UNDER_A_PURPOSE_THAT_WITHHOLDS_IT",
                 practice[core]["purpose"],
                 vocabulary[practice[core]["purpose"]].get("reason_when_withheld", ""))

    # --- per core ---------------------------------------------------------------
    built = []
    for core in cores:
        if core in PRACTICE:
            intent = practice.get(core, {})
            purpose = vocabulary.get(intent.get("purpose"))
            handed = {row["level"]: row["handed_over"] for row
                      in (board.get("family") or {}).get("support_ladder", [])}
            if purpose is None:
                built.append({"core": core, "state": "BLOCKED",
                              "reason": "no purpose, so no support level and no routing"})
                continue
            if not taught:
                built.append({"core": core, "state": "BLOCKED",
                              "purpose": purpose["id"],
                              "reason": "no rung of this ladder has a record, so there is "
                                        "no established decision structure to vary and "
                                        "nothing already taught to hold"})
                continue
            if core == TRANSFER and not purpose["routes_transfer"]:
                built.append({"core": core, "state": "WITHHELD",
                              "purpose": purpose["id"],
                              "reason": purpose.get("reason_when_withheld", "")})
                continue
            exposed = questions_for_core(records, bucket_id, core)
            if not exposed:
                built.append({"core": core, "state": "BLOCKED",
                              "purpose": purpose["id"],
                              "support": purpose["support"],
                              "handed_over": handed.get(purpose["support"]),
                              "reason": "the library holds no bucket-owned question "
                                        "exposed to this product"})
                continue
            built.append({"core": core, "state": "READY", "purpose": purpose["id"],
                          "support": purpose["support"],
                          "handed_over": handed.get(purpose["support"]),
                          "questions": [q["id"] for q in exposed],
                          "rows": len(board.get("transfer") or []) if core == TRANSFER
                          else None})
            continue
        if core not in TEACHING:
            built.append({"core": core, "state": "NOT_PLANNED_HERE",
                          "reason": "source custody, not compiled from a ladder"})
            continue
        if not segment:
            built.append({"core": core, "state": "BLOCKED",
                          "reason": f'no entry rung: {entry.get("why")}'})
            continue
        steps = []
        for name in segment:
            row = next(r for r in rows if r["rung"] == name)
            state = rung_state(row, caps, mics)
            steps.append({"rung": name, "state": state["state"],
                          "microtopic": state.get("microtopic"),
                          "task": "AUTHOR_THE_RUNG" if state["state"] == "ABSENT"
                          else "AUTHOR_THE_PRODUCT"})
        built.append({"core": core, "state": "READY", "segment": steps})

    diagnostic_focus = (
        atlas_need.resolve(
            diagnostic,
            repo,
            expected_subject=subject,
            expected_matrix_id=board["matrix_id"],
        )
        if diagnostic is not None
        else {
            "state": "NOT_SUPPLIED",
            "passed": True,
            "matrix_id": board["matrix_id"],
            "subject": subject,
            "targets": [],
            "rejected": [],
            "warnings": [],
            "errors": [],
            "rule": "no external diagnostic supplied; strict request semantics are unchanged",
        }
    )
    focus_targets = list(diagnostic_focus.get("targets") or [])
    core_emphasis = core_focus.for_cores(cores, focus_targets)
    focused_inventory = focus_inventory.for_cores(
        subject, bucket_id, cores, focus_targets, repo
    )

    return {"request": request.get("request_id"), "subject": subject,
            "bucket": bucket_id, "matrix": board["_path"],
            "entry": {**entry, "provenance": provenance}, "segment": segment,
            "cores": built, "diagnostic_focus": diagnostic_focus,
            "core_focus": core_emphasis, "focus_inventory": focused_inventory,
            "findings": found, "passed": not found}


def audit(repo: Path = REPO) -> dict:
    try:
        import jsonschema
    except ModuleNotFoundError:
        jsonschema = None
    validator = (jsonschema.Draft202012Validator(load(SCHEMA))
                 if jsonschema is not None else None)
    rows = []
    for path in sorted((repo / REQUESTS).glob("*.request.json")):
        request = load(path)
        structural = ([{"point": "REQUEST_STRUCTURE",
                        "where": "/".join(str(p) for p in e.path), "detail": e.message}
                       for e in validator.iter_errors(request)] if validator else [])
        report = ({"request": request.get("request_id"), "findings": [], "cores": []}
                  if structural else plan(request, repo))
        report["findings"] = structural + report["findings"]
        report["passed"] = not report["findings"]
        rows.append({**report, "path": str(path.relative_to(repo))})
    return {"requests": len(rows), "plans": rows,
            "findings": sum(len(r["findings"]) for r in rows),
            "passed": all(r["passed"] for r in rows)}


def readable(report: dict) -> str:
    out = [f'# Build plan -- {report["request"]}', "",
           f'  subject  {report.get("subject")}',
           f'  bucket   {report.get("bucket")}',
           f'  matrix   {report.get("matrix")}', ""]
    entry = report.get("entry") or {}
    out += ["## Entry rung", "",
            f'  rung        {entry.get("rung") or "NONE"}',
            f'  selected by {entry.get("why")}',
            f'  provenance  {entry.get("provenance")}']
    if entry.get("detail"):
        out += [f'  detail      {entry["detail"]}']
    if entry.get("prerequisite_checks"):
        out += [
            "  quick checks  " + ", ".join(entry["prerequisite_checks"]),
            "  note         these are unverified prerequisites, not assumed mastery",
        ]
    out += ["",
            "Selection, never dilution: this chooses where teaching starts and changes",
            "nothing about what any rung teaches.", ""]
    for core in report.get("cores", []):
        out += [f'## {core["core"]} -- {core["state"]}', ""]
        if core.get("reason"):
            out += [f'  {core["reason"]}', ""]
        for step in core.get("segment", []):
            out += [f'  {step["rung"]:4} {step["state"]:8} {step["task"]:18} '
                    f'{step.get("microtopic") or ""}']
        if core.get("segment"):
            out += [""]
        if core.get("purpose"):
            out += [f'  purpose      {core["purpose"]}',
                    f'  support      {core.get("support") or "NOT_RESOLVED"}',
                    f'  handed over  {core.get("handed_over") or "AUTHOR_REQUIRED"}']
            if core.get("rows") is not None:
                out += [f'  transfer     {core["rows"]} rows available']
            out += [""]
    if report.get("findings"):
        out += ["## Refused", ""]
        out += [f'  {f["point"]:46} {f["where"]}' for f in report["findings"]] + [""]
    return "\n".join(out)


def briefs(request: dict, repo: Path = REPO, diagnostic: dict | None = None) -> str:
    """Every brief the plan calls for, in build order. One command, one request.

    The teaching cores get one brief per rung of the segment -- a ladder segment, not a
    single rung, because "teach this subtopic from here" means here and everything above
    it. The practice cores get the family and, for the transfer product, the rows that
    change its demand; their support level comes from the purpose rather than from a
    percentage, so nothing here consults a knowledge input at all.
    """
    from Shared.tools import author_brief

    report = plan(request, repo)
    if report["findings"]:
        return readable(report)
    board = ladder(report["subject"], report["bucket"], repo)
    out = [readable(report), "=" * 78, ""]
    for core in report["cores"]:
        if core["state"] != "READY":
            continue
        for step in core.get("segment", []):
            out += [author_brief.brief(report["subject"], report["bucket"],
                                       step["rung"], core["core"]), "-" * 78, ""]
        if core["core"] in PRACTICE:
            out += [f'# Authoring brief -- {core["core"]}, {board["subtopic"]}', "",
                    f'## Purpose {core["purpose"]} -- support {core["support"]}', "",
                    f'  handed over : {core.get("handed_over") or "AUTHOR_REQUIRED"}', "",
                    "The purpose carries the support level. No knowledge input is read",
                    "here: support and placement are different questions and were",
                    "previously the same number.", ""]
            out += author_brief.practice(board, core["core"])
            out += author_brief.required_content(core["core"])
            out += ["## Green before done", ""]
            out += [f'  {g}' for g in author_brief.gates()] + ["", "-" * 78, ""]
    return "\n".join(x if isinstance(x, str) else str(x) for x in out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--enforce", action="store_true",
                        help="exit nonzero when any request has a finding")
    parser.add_argument("--plan", help="print one request's plan as text")
    parser.add_argument("--briefs",
                        help="print every authoring brief the plan calls for")
    parser.add_argument("--diagnostic",
                        help="optional external diagnostic gap envelope; never replaces learner placement")
    args = parser.parse_args()
    diagnostic = load(Path(args.diagnostic)) if args.diagnostic else None
    if args.plan:
        print(readable(plan(load(Path(args.plan)), diagnostic=diagnostic)))
        return 0
    if args.briefs:
        print(briefs(load(Path(args.briefs)), diagnostic=diagnostic))
        return 0
    report = audit()
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] or not args.enforce else 1


if __name__ == "__main__":
    raise SystemExit(main())
