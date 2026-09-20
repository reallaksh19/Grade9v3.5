#!/usr/bin/env python3
"""Keep learner claims grounded in observations, while allowing practical owner routing.

Profiles remain capability-keyed and outside subjects. A profile knowledge_percentage is
still a summary and is never treated as evidence that a prerequisite is held. Separately,
an explicit owner_estimate inside a build request may choose a conservative starting
coordinate; resolve_request owns that decision.

For routing from a profile, evidence precedence is deliberately small and inspectable:

  DIRECT_ATTEMPT > PRIOR_DIAGNOSTIC > PRIOR_STUDY_MAP > profile held state > unobserved

Within one evidence kind, the newest ISO date/timestamp wins. This is not a Bayesian
mastery model. It is simply a deterministic rule for preferring current task evidence over
older imported evidence.

A DEMONSTRATED result obtained with a hint, worked example or solution is treated as
UNCERTAIN for effective routing. It may still be retained as an honest observation of what
happened; it just does not prove independent mastery.
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

PROFILES = "Learners/profiles"
OBSERVATIONS = "Learners/observations"
OBSERVATION_SCHEMA = "Shared/library/observation.schema.json"
NEEDS_WAIVER = {"OWNER_ESTIMATE", "UNKNOWN"}

EVIDENCE_PRIORITY = {
    "DIRECT_ATTEMPT": 30,
    "PRIOR_DIAGNOSTIC": 20,
    "PRIOR_STUDY_MAP": 10,
    None: 20,  # backwards-compatible diagnostic observations with no structured kind
}
NONINDEPENDENT_HELP = {"HINT", "WORKED_EXAMPLE", "SOLUTION"}


def capabilities(repo: Path = REPO) -> set[str]:
    return {cap["id"] for path in sorted(repo.glob("*/library/*.json"))
            if path.name != "package.schema.json"
            for cap in load(path).get("capabilities", [])}


def load_observations(repo: Path = REPO) -> dict[str, dict]:
    root = repo / OBSERVATIONS
    return ({load(path)["observation_id"]: load(path)
             for path in sorted(root.glob("*.json"))}
            if root.exists() else {})


def load_profiles(repo: Path = REPO) -> dict[str, dict]:
    root = repo / PROFILES
    return ({load(path)["profile_id"]: load(path)
             for path in sorted(root.glob("*.json"))}
            if root.exists() else {})


def _effective_observation_result(observation: dict) -> str:
    result = observation.get("result", "UNCERTAIN")
    if result == "DEMONSTRATED" and observation.get("help") in NONINDEPENDENT_HELP:
        return "UNCERTAIN"
    return result


def evidence_for_capability(profile: dict, capability_ref: str,
                            repo: Path = REPO) -> list[dict]:
    """Referenced observations for one capability, strongest/current first."""
    observations = load_observations(repo)
    rows = [
        observations[ref]
        for ref in profile.get("observation_refs", [])
        if ref in observations and observations[ref].get("capability_ref") == capability_ref
    ]
    return sorted(
        rows,
        key=lambda row: (
            EVIDENCE_PRIORITY.get(row.get("evidence_kind"), 0),
            str(row.get("when") or ""),
            str(row.get("observation_id") or ""),
        ),
        reverse=True,
    )


def effective_state(profile: dict, capability_ref: str, repo: Path = REPO) -> dict:
    """Current routing state for one capability, with its evidence source."""
    evidence = evidence_for_capability(profile, capability_ref, repo)
    if evidence:
        chosen = evidence[0]
        return {
            "state": _effective_observation_result(chosen),
            "source": chosen.get("evidence_kind") or "OBSERVATION",
            "observation_ref": chosen["observation_id"],
            "when": chosen.get("when"),
            "help": chosen.get("help"),
            "error_stage": chosen.get("error_stage"),
        }

    if capability_ref in profile.get("held", {}):
        return {
            "state": profile["held"][capability_ref],
            "source": f'PROFILE_{profile.get("provenance", "UNKNOWN")}',
            "observation_ref": None,
            "when": None,
            "help": None,
            "error_stage": None,
        }

    return {
        "state": "UNOBSERVED",
        "source": "UNOBSERVED",
        "observation_ref": None,
        "when": None,
        "help": None,
        "error_stage": None,
    }


def effective_held(profile: dict, repo: Path = REPO) -> dict[str, str]:
    """Capability -> current state for routing, observations overriding profile snapshot."""
    keys = set(profile.get("held", {}))
    observations = load_observations(repo)
    keys.update(
        observations[ref]["capability_ref"]
        for ref in profile.get("observation_refs", [])
        if ref in observations
    )
    resolved = {}
    for capability in sorted(keys):
        state = effective_state(profile, capability, repo)["state"]
        if state != "UNOBSERVED":
            resolved[capability] = state
    return resolved


def referenced_profiles(repo: Path = REPO) -> dict[str, list[str]]:
    """Every practice_profile_ref in the libraries, and who made it."""
    found: dict[str, list[str]] = {}
    for path in sorted(repo.glob("*/library/*.json")):
        if path.name == "package.schema.json":
            continue
        for route in load(path).get("teaching_routes", []):
            ref = route.get("practice_profile_ref")
            if ref:
                found.setdefault(ref, []).append(f'{path.name}:{route["id"]}')
    return found


def audit(repo: Path = REPO) -> dict:
    declared = capabilities(repo)
    observations = load_observations(repo)
    profiles = load_profiles(repo)
    findings: list[dict] = []

    def fail(point: str, who: str, detail: str):
        findings.append({"point": point, "profile": who, "detail": detail})

    try:
        import jsonschema
    except ModuleNotFoundError:
        jsonschema = None
    observation_validator = (
        jsonschema.Draft202012Validator(load(repo / OBSERVATION_SCHEMA))
        if jsonschema is not None else None
    )

    for oid, observation in sorted(observations.items()):
        if observation_validator is not None:
            for error in observation_validator.iter_errors(observation):
                findings.append({
                    "point": "OBSERVATION_STRUCTURE",
                    "profile": oid,
                    "detail": error.message,
                })
        capability = observation.get("capability_ref")
        if capability and capability not in declared:
            findings.append({
                "point": "OBSERVATION_CAPABILITY_UNKNOWN",
                "profile": oid,
                "detail": f"observes {capability}, which no subject declares",
            })

    for pid, profile in sorted(profiles.items()):
        provenance = profile["provenance"]
        for cap in profile.get("held", {}):
            if cap not in declared:
                fail("HELD_CAPABILITY_UNKNOWN", pid,
                     f"claims a state for {cap}, which no subject declares")
        if provenance in NEEDS_WAIVER and not profile.get("owner_waiver"):
            fail("CLAIM_WITHOUT_EVIDENCE_OR_WAIVER", pid,
                 f"{provenance} is not a measurement, so it needs the owner instruction it "
                 "is following instead")
        if provenance == "DIAGNOSTIC":
            demonstrated = {
                observations[ref]["capability_ref"]
                for ref in profile.get("observation_refs", [])
                if ref in observations
                and _effective_observation_result(observations[ref]) == "DEMONSTRATED"
            }
            for cap, state in profile.get("held", {}).items():
                if state == "DEMONSTRATED" and cap not in demonstrated:
                    fail("DEMONSTRATED_WITHOUT_AN_OBSERVATION", pid,
                         f"says {cap} is demonstrated and no independent observation records it")
        for ref in profile.get("observation_refs", []):
            if ref not in observations:
                fail("OBSERVATION_REF_DANGLING", pid, f"names {ref}, which does not exist")
        if profile.get("measured_fit_claim") and provenance != "DIAGNOSTIC":
            fail("FIT_CLAIMED_WITHOUT_DIAGNOSIS", pid,
                 f"claims measured fit on {provenance} evidence")

    for ref, users in sorted(referenced_profiles(repo).items()):
        if ref not in profiles:
            fail("PROFILE_REF_DANGLING", ref,
                 f'referenced by {", ".join(users)} and no profile holds that id')
        elif profiles[ref]["provenance"] == "SYNTHETIC_TEST":
            fail("SYNTHETIC_PROFILE_ROUTED", ref,
                 f'referenced by {", ".join(users)}; a synthetic profile is never routed')

    return {"profiles": len(profiles), "observations": len(observations),
            "findings": findings, "passed": not findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
