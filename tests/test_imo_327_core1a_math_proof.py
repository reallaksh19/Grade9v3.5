"""IMO #327 Core1A semantic proof: true maths, three wrong-route repairs and held source.

This follows draft #312, does not assert independent human academic acceptance and
does not certify authentic SOF Core2 or public learner admission.
"""
from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json"
MANIFEST = ROOT / "TEST/imo-research/candidates/imo-g9-r1-qrt-core2a-core1a.test.manifest.json"
MIC = "MIC-TEST-IMO-G9-COMMON-BASE-RELATION"
CAP = "CAP-TEST-IMO-G9-COMMON-EXPONENTIAL-QUANTITY"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def unique_real_solution(base: int, offset: int) -> float | None:
    """Independent oracle for a^(2x+1)=(a^2)^x+k, a>1, x real.

    Let t=a^(2x)>0. Then a*t=t+k. For a>1, it has a real
    solution if and only if k>0, where x=log_a(k/(a-1))/2.
    """
    if not isinstance(base, int) or base <= 1:
        raise ValueError("Oracle applies to integer bases greater than one")
    if not isinstance(offset, int):
        raise ValueError("Use an exact integer additive offset")
    t = offset / (base - 1)
    if t <= 0:
        return None
    return math.log(t, base) / 2


def evaluate_original(base: int, offset: int, x: float) -> tuple[float, float]:
    return (base ** (2*x + 1), (base*base)**x + offset)


def verify_structure(pkg: dict, manifest: dict) -> None:
    if pkg.get("status") != "CANDIDATE" or pkg.get("subject") != "TEST":
        raise ValueError("Core1A cannot be represented as canonical or academically admitted")
    if pkg["capabilities"][0]["acceptance_status"] != "CANDIDATE":
        raise ValueError("Premature capability admission")
    if pkg.get("curriculum_mappings") != []:
        raise ValueError("A provisional source family is not an accepted curriculum mapping")
    for key in ("grade9v3:qrt_admitted", "grade9v3:core2_source_custody_granted",
                "grade9v3:learner_published"):
        if pkg["extensions"].get(key) is not False:
            raise ValueError("Authority has not granted QRT, custody or learner publication")
    if pkg["resources"][0]["origin"] != "AUTHORED" or pkg["resources"][0]["source_refs"]:
        raise ValueError("Source provenance is misrepresented")
    micro = next(m for m in pkg["microtopics"] if m["id"] == MIC)
    if micro["primary_capability_ref"] != CAP:
        raise ValueError("Wrong teaching capability")
    steps = micro["teaching_path"]
    if [s["id"] for s in steps] != ["TC-01", "TC-02", "TC-03", "TC-04", "TC-05"]:
        raise ValueError("Lost or reordered core inferential steps")
    if not all(s["why_valid"] and s["action"] and s["output"] for s in steps):
        raise ValueError("A mathematical construction must explain why each step is valid")
    problems = micro["misconceptions"]
    if len(problems) != 3 or not all(
        isinstance(m.get(k), str) and m[k] for m in problems
        for k in ("wrong_idea", "diagnostic_prompt", "repair")
    ):
        raise ValueError("Exactly three distinct wrong routes need diagnostic and repair")
    combined = " ".join([problems[2][k] for k in
                         ("wrong_idea", "diagnostic_prompt", "repair")])
    for token in ("2x=4", "x=4", "x=2", "19683", "6723"):
        if token not in combined:
            raise ValueError("Exponent inversion repair must discriminate x=4 and x=2")
    construction = micro["construction_units"][0]
    if construction["misconception_indexes"] != [0, 1, 2]:
        raise ValueError("Third diagnostic disconnected from teaching construction")
    if construction["step_refs"] != [s["id"] for s in steps]:
        raise ValueError("Construction references fail to cover the lesson")
    if construction.get("worked_anchor_ref") != "Q-TEST-IMO-G9-Q26-CORE1A-WORKED-ANCHOR":
        raise ValueError("Lesson lost its authored worked anchor")
    questions = pkg["questions"]
    if {q["id"] for q in questions} != {
            "Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01",
            "Q-TEST-IMO-G9-Q26-CORE1A-WORKED-ANCHOR"}:
        raise ValueError("Question identity changed unexpectedly")
    if any(q["origin"] != "AUTHORED" for q in questions):
        raise ValueError("SOF source question copied into an authored lesson")
    authored = next(q for q in questions if q["id"].endswith("SUPPORTED-01"))
    if authored["repair_ref"] != "TC-02" or authored["primary_capability_ref"] != CAP:
        raise ValueError("Authored challenge must target the factor-law teaching repair")
    if manifest["selection"]["core2"] or manifest["selection"]["core2b"] or manifest["bank_refs"]:
        raise ValueError("Genuine source Core2 or bank is not authorized")
    if (manifest["output_roles"] != ["CORE1A", "CORE2A"] or
            manifest["selection"]["core2a"] != [authored["id"]]):
        raise ValueError("Incorrect source-versus-authored role mapping")


class IndexLawsCore1AMath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pkg = load(PACKAGE)
        cls.manifest = load(MANIFEST)

    def test_three_independent_exact_authored_models(self):
        # Anchor a=3, k=162; fresh Core1A exit a=2, k=64;
        # wholly authored Core2A attempt a=4, k=192.
        for a, k, expected, exact_left in (
            (3, 162, 2, 243),
            (2, 64, 3, 128),
            (4, 192, 1.5, 256),
        ):
            with self.subTest(a=a, k=k):
                x = unique_real_solution(a, k)
                self.assertIsNotNone(x)
                self.assertTrue(math.isclose(x, expected, abs_tol=1e-12))
                lhs, rhs = evaluate_original(a, k, expected)
                self.assertTrue(math.isclose(lhs, rhs, rel_tol=1e-12))
                self.assertEqual(lhs, exact_left)
                self.assertEqual(rhs, exact_left)

    def test_exponent_offset_is_multiplication_for_fresh_real_values(self):
        for a in (2, 3, 4, 7):
            for x in (-2.25, -0.5, 0, 0.75, 2):
                with self.subTest(a=a, x=x):
                    t = a ** (2*x)
                    self.assertGreater(t, 0)
                    self.assertTrue(math.isclose((a*a)**x, t, rel_tol=1e-12))
                    self.assertTrue(math.isclose(a**(2*x+1), a*t, rel_tol=1e-12))

    def test_nonpositive_substitution_has_no_real_solution(self):
        for a in (2, 3, 4):
            for k in (-5, 0, -100):
                self.assertIsNone(unique_real_solution(a, k))
        for base in (1, 0, -3):
            with self.assertRaises(ValueError):
                unique_real_solution(base, 12)

    def test_inversion_error_fails_original_equation(self):
        # If 3^(2x)=81=3^4, then 2x=4, NOT x=4.
        self.assertEqual(3**(2*2), 81)
        self.assertEqual(evaluate_original(3, 162, 2), (243, 243))
        self.assertEqual(evaluate_original(3, 162, 4), (19683, 6723))
        self.assertNotEqual(*evaluate_original(3, 162, 4))

    def test_complete_construction_and_candidate_authority(self):
        verify_structure(self.pkg, self.manifest)

    def test_third_repair_cannot_be_unindexed(self):
        d = copy.deepcopy(self.pkg)
        d["microtopics"][0]["construction_units"][0]["misconception_indexes"] = [0, 1]
        with self.assertRaises(ValueError):
            verify_structure(d, self.manifest)

    def test_source_core2_cannot_be_silently_promoted(self):
        m = copy.deepcopy(self.manifest)
        m["selection"]["core2"] = [m["selection"]["core2a"][0]]
        with self.assertRaises(ValueError):
            verify_structure(self.pkg, m)

    def test_repair_math_must_remain_specific(self):
        d = copy.deepcopy(self.pkg)
        d["microtopics"][0]["misconceptions"][2]["repair"] = "Simply set x=4."
        with self.assertRaises(ValueError):
            verify_structure(d, self.manifest)


if __name__ == "__main__":
    unittest.main()
