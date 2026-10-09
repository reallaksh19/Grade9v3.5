"""Local, stdlib-only fail-closed PRECHECK for #327's Common V3.2 candidate graph.

This precheck is deliberately NOT a replacement for the pinned Common
delp_projection_v32.py decompose-check. Parent/child release requires that tool.
"""
from __future__ import annotations
import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "TEST/imo-research/intake/imo-327-delp-proposal-v2.json"
ROOT_REF = "reallaksh19/Grade9v3.5#327"
CLAIMS = {"C1": 1500, "C2": 2500, "C3": 1500, "C4": 2000, "C5": 1500, "G1": 1000}
LEAVES = {"C1": "IMO-F01", "C2": "IMO-F02", "C3": "IMO-F03",
          "C4": "IMO-F04", "C5": "IMO-F05", "G1": "IMO-F06"}
MECHANISMS = {"workflow", "ci", "browser", "evidence", "handoff",
              "renderer", "migration", "test", "tests", "testing",
              "checkpoint", "schema", "script", "fixture", "fixtures"}


def overlaps(a: str, b: str) -> bool:
    return a == b or a.endswith("/") and b.startswith(a) or b.endswith("/") and a.startswith(b)


def check(graph: dict) -> None:
    if graph.get("schema") != "relay-v3.2-delp-execution-graph":
        raise ValueError("Wrong V3.2 graph schema")
    p = graph["programme"]
    if (p.get("root") != ROOT_REF or p.get("repository") != "reallaksh19/Grade9v3.5"
            or p.get("base_ref") != "main" or p.get("total_weight") != 10000):
        raise ValueError("Programme identity or denominator drift")
    policy = p.get("decomposition_policy", {})
    if (policy.get("mode") != "ENFORCED"
            or policy.get("claim_first", {}).get("mode") != "ENFORCED"):
        raise ValueError("Both decomposition gates must be ENFORCED")
    if graph.get("nodes") != [{"ref": ROOT_REF, "kind": "ROOT"}]:
        raise ValueError("No child provider bindings before official proposal release")
    claims = p["acceptance_claims"]
    if (len(claims) != 6 or {c["id"]: c["weight"] for c in claims} != CLAIMS
            or sum(c["weight"] for c in claims) != 10000):
        raise ValueError("Parent claim coverage and weight conservation failed")
    for c in claims:
        if c["kind"] != ("DELIVERY_GATE" if c["id"] == "G1" else "SEMANTIC"):
            raise ValueError("Wrong semantic/release-claim kind")
    proposed = p["decomposition_proposal"]
    if (proposed.get("version") != "V2" or proposed.get("bindings")
            or proposed.get("released_proposal_digest")):
        raise ValueError("Uncertified proposal cannot have provider bindings or a release digest")
    items = proposed["responsibilities"]
    if (len(items) != 6 or len({r["id"] for r in items}) != 6
            or {r["id"]: r["owns_claims"][0] for r in items} !=
            {leaf: claim for claim, leaf in LEAVES.items()}):
        raise ValueError("Unexpected responsibility claim topology")
    by_id = {r["id"]: r for r in items}
    for row in items:
        claim = row["owns_claims"][0]
        kind = "GATE" if claim == "G1" else "PRODUCT"
        if row["work_class"] != kind:
            raise ValueError("Product and release-gate work classes differ")
        if row["claim_allocations"] != [{"claim_id": claim, "weight": CLAIMS[claim]}]:
            raise ValueError("Claim allocations do not conserve parent weight")
        if not row.get("outcome") or not row.get("independence_basis"):
            raise ValueError("Responsibility needs actual semantic outcome and independent acceptance basis")
        if len(row.get("acceptance_methods", [])) < 2:
            raise ValueError("Acceptance methods not declared")
        size = row["size_budget"]
        if not (0 < size["target_loc"] <= 700 and size["target_loc"] <= size["hard_loc"] <= 1500
                and 0 < size["target_minutes"] <= 15
                and size["target_minutes"] <= size["hard_minutes"] <= 20):
            raise ValueError("Exceeded V3.2 target/hard review budget")
        units = row["semantic_units"]
        if len(units) != 4 or len({u["id"] for u in units}) != len(units):
            raise ValueError("Four reviewable semantic outcomes required per leaf")
        for u in units:
            if (u["weight"] != 25 or
                    u["kind"] != ("DELIVERY_GATE" if kind == "GATE" else "SEMANTIC") or
                    not u.get("outcome") or not u.get("verify")):
                raise ValueError("Progress cannot be earned from mechanisms or unverifiable work")
            text = row["outcome"] + " " + u["outcome"]
            if MECHANISMS.intersection(re.findall(r"[a-z0-9]+", text.lower())) and kind == "PRODUCT":
                raise ValueError("PRODUCT outcome falsely describes a mechanism as a semantic unit")
        if not row["write_surface"] or any("*" in x or "?" in x or ".." in x for x in row["write_surface"]):
            raise ValueError("Precise nonwildcard write surfaces required")
        for dep in row["depends_on"]:
            if dep not in by_id or dep == row["id"]:
                raise ValueError("Invalid dependency or cycle")
    def ancestors(rid: str, chain=frozenset()) -> set[str]:
        if rid in chain:
            raise ValueError("Cyclic dependency")
        result = set(by_id[rid]["depends_on"])
        for dep in by_id[rid]["depends_on"]:
            result |= ancestors(dep, chain | {rid})
        return result
    ancestor = {k: ancestors(k) for k in by_id}
    for i, left in enumerate(items):
        for right in items[i + 1:]:
            if (any(overlaps(x, y) for x in left["write_surface"] for y in right["write_surface"])
                    and left["id"] not in ancestor[right["id"]]
                    and right["id"] not in ancestor[left["id"]]):
                raise ValueError("Unfenced concurrent write collision")
    # C4 and G1 must permit independent Core1A-only release while source
    # rights are held; later Stage B/C roles each need their own review.
    if "IMO-F05" in ancestor["IMO-F04"] | ancestor["IMO-F06"]:
        raise ValueError("Genuine-source hold must not force unapproved substitute or block Core1A-only release")
    if "IMO-F02" not in ancestor["IMO-F04"] or "IMO-F04" not in ancestor["IMO-F06"]:
        raise ValueError("Academic lesson and homepage prerequisite lost")


class ClaimFirstProposalPrecheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(FILE.read_text(encoding="utf-8"))

    def invalid(self, fn):
        graph = copy.deepcopy(self.plan)
        fn(graph)
        with self.assertRaises(ValueError):
            check(graph)

    def test_first_pass_on_pinned_candidate(self):
        check(self.plan)

    def test_no_false_proposal_release_digest(self):
        self.invalid(lambda g: g["programme"]["decomposition_proposal"].update(
            released_proposal_digest="sha256:" + "0" * 64))

    def test_uncovered_parent_claim_fails(self):
        self.invalid(lambda g: g["programme"]["decomposition_proposal"]["responsibilities"].pop())

    def test_progress_unit_cannot_be_ci_mechanic(self):
        self.invalid(lambda g: g["programme"]["decomposition_proposal"]["responsibilities"][0]
                     ["semantic_units"][0].update(outcome="A CI workflow passes"))

    def test_custody_dependency_must_not_block_lesson_release(self):
        def mutate(g):
            r = g["programme"]["decomposition_proposal"]["responsibilities"]
            next(x for x in r if x["id"] == "IMO-F04")["depends_on"].append("IMO-F05")
        self.invalid(mutate)

    def test_concurrent_write_collision_is_rejected(self):
        def mutate(g):
            r = g["programme"]["decomposition_proposal"]["responsibilities"]
            next(x for x in r if x["id"] == "IMO-F05")["write_surface"] = \
                next(x for x in r if x["id"] == "IMO-F02")["write_surface"]
        self.invalid(mutate)

    def test_wrong_semantic_class_is_rejected(self):
        self.invalid(lambda g: g["programme"]["decomposition_proposal"]["responsibilities"][0]
                     ["semantic_units"][0].update(kind="MECHANICAL"))


if __name__ == "__main__":
    unittest.main()
