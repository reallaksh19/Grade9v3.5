"""Fail-closed #327 teaching-vs-hint mode checks for the single candidate in #312.

Authoring/content gate ONLY. Renderer does not enforce concept-check completion,
track hint usage as assisted evidence, or require a fresh unaided retry.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"

def assert_distinct_modes(pkg: dict, manifest: dict) -> None:
    if pkg.get("subject") != "TEST" or pkg.get("status") != "CANDIDATE":
        raise ValueError("Only unadmitted TEST authoring is in scope")
    if pkg.get("curriculum_mappings") or pkg.get("extensions", {}).get("grade9v3:learner_published") is not False:
        raise ValueError("Unreviewed teaching cannot be published or mapped")
    micro = next(x for x in pkg["microtopics"] if x["id"] == "MIC-TEST-IMO-G9-COMMON-BASE-RELATION")
    q = next(x for x in pkg["questions"] if x["id"] == "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01")
    steps = micro["teaching_path"]
    if [s["id"] for s in steps] != ["TC-01", "TC-02", "TC-03", "TC-04", "TC-05"]:
        raise ValueError("All five reasoning steps must survive")
    lead = steps[0]["action"]
    if (not lead.startswith("CONCEPT BEFORE AID:")
            or "2^4" not in lead or "2P" not in lead or "P+2" not in lead
            or "5^(n+1)" not in lead or "why?" not in lead
            or "3^(2x+1)" not in lead or lead.index("2^4") > lead.index("3^(2x+1)")
            or "x=2" in lead or "t=81" in lead):
        raise ValueError("Core1A must teach and probe a neutral exponent-offset concept before worked aid")
    if (not micro["inferential_jump"].startswith("CONCEPT FIRST:")
            or "2^4=2*2^3" not in micro["inferential_jump"]
            or "5^(n+1)" not in micro["compact_anchor"]["prompt"]
            or "3^(2x+1)" in micro["compact_anchor"]["prompt"]):
        raise ValueError("Core1A concept first is not independent of the worked equation")
    checks = micro["construction_units"][0].get("independent_checks") or []
    if (not checks or checks[0].get("role") != "CHECK"
            or "5^(n+1)" not in checks[0]["statement"]
            or "x=2" not in checks[0]["statement"]):
        raise ValueError("Concept-check authorship/role not explicit")
    if (not steps[1]["output"].startswith("3^(2x+1)=3t")
            or "3t=t+162" not in steps[2]["output"]
            or "x=2" not in steps[3]["output"]):
        raise ValueError("Worked application no longer explains the factor, solve and inversion")

    support = q.get("scaffolds") or []
    ladder = q.get("hint_ladder") or []
    if len(support) != 3 or len(ladder) != 3 or q.get("hints") != []:
        raise ValueError("Exactly three authored question hints; no authentic source hints")
    if ([h["order"] for h in ladder] != [1,2,3] or
            [h["from"] for h in ladder] != ["scaffolds[0]", "scaffolds[1]", "scaffolds[2]"] or
            [h["purpose"] for h in ladder] != ["ORIENT", "CONNECT", "CONNECT"]):
        raise ValueError("Question hint ordering/source changed")
    for index, item in enumerate(support):
        text = item["text"]
        banned = ("u=3/2", "u = 3/2", "t=64", "t = 64", "3t=192",
                  "4t=t+192", "256", "4^(2u)=64", "64=4^3")
        if any(token in text for token in banned):
            raise ValueError(f"Hint {index+1} disclosed the answer or solved the protected step")
    if (not support[0]["text"].startswith("Look at 16 and 4:")
            or "Do not introduce a numerical answer." not in support[0]["text"]
            or "a^(n+1)=a*a^n" not in support[1]["text"]
            or "Where" not in support[1]["text"]
            or not support[2]["text"].startswith("Choose a strictly positive common power")):
        raise ValueError("Hints must orient then remind then invite the learner's own application")
    if q.get("repair_ref") != "TC-02":
        raise ValueError("Exact factor-law concept repair lost")
    if (manifest.get("output_roles") != ["CORE1A", "CORE2A"]
            or manifest.get("selection", {}).get("core2") != []
            or manifest.get("selection", {}).get("core2a") != [q["id"]]):
        raise ValueError("No authentic source Core2 is authorized")
    routes = pkg.get("teaching_routes") or []
    if len(routes) != 1 or "TEST-only browser formative choice+rationale gate is implemented" not in " ".join(routes[0]["help_plan"]):
        raise ValueError("Concept check must describe the format gate, not independent comprehension")
    if "renderer/QRT work not delivered" not in " ".join(routes[0]["help_plan"]):
        raise ValueError("Assisted-vs-independent evidence/return-to-fresh-attempt debt must remain explicit")


class HelpModeSeparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = json.loads(CANDIDATE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_real_authored_modes_are_distinct_and_held(self):
        assert_distinct_modes(self.pkg, self.manifest)

    def test_hint_cannot_reveal_substitution_solution(self):
        d = copy.deepcopy(self.pkg)
        d["questions"][0]["scaffolds"][1]["text"] = "Now write 4t=t+192, so t=64."
        with self.assertRaises(ValueError):
            assert_distinct_modes(d, self.manifest)

    def test_concept_law_cannot_be_replaced_with_answer(self):
        d = copy.deepcopy(self.pkg)
        d["microtopics"][0]["teaching_path"][0]["action"] = "CONCEPT BEFORE AID: x=2."
        with self.assertRaises(ValueError):
            assert_distinct_modes(d, self.manifest)

    def test_concept_check_cannot_be_dropped(self):
        d = copy.deepcopy(self.pkg)
        d["microtopics"][0]["construction_units"][0]["independent_checks"].pop(0)
        with self.assertRaises(ValueError):
            assert_distinct_modes(d, self.manifest)

    def test_wrong_question_hint_sequence_rejected(self):
        d = copy.deepcopy(self.pkg)
        d["questions"][0]["hint_ladder"][0]["from"] = "scaffolds[2]"
        with self.assertRaises(ValueError):
            assert_distinct_modes(d, self.manifest)

    def test_forged_authentic_core2_rejected(self):
        m = copy.deepcopy(self.manifest)
        m["output_roles"].append("CORE2")
        m["selection"]["core2"] = [self.pkg["questions"][0]["id"]]
        with self.assertRaises(ValueError):
            assert_distinct_modes(self.pkg, m)

    def test_forged_runtime_concept_check_claim_rejected(self):
        d = copy.deepcopy(self.pkg)
        d["teaching_routes"][0]["help_plan"][1] = "The learner understands the concept and earns independent mastery."
        with self.assertRaises(ValueError):
            assert_distinct_modes(d, self.manifest)


if __name__ == "__main__":
    unittest.main()
