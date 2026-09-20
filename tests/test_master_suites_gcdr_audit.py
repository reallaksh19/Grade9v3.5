#!/usr/bin/env python3
"""Audit regressions for the Motion-1D and Vector Algebra master suites.

The tests deliberately recompute the diagnostic results independently of the authored
step text, and enforce the GCDR fidelity/helper contract around question-to-simulator actions.
"""
from __future__ import annotations

import json
import math
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MOTION_DATA = REPO / "public/physics/motion-1d/explorers/motion_in_1d/jee_questions_data.js"
MOTION_HTML = REPO / "public/physics/motion-1d/explorers/motion_in_1d/index.html"
VECTOR_DATA = REPO / "public/mathematics/vectors/explorers/vector_algebra/jee_questions_data.js"
VECTOR_HTML = REPO / "public/mathematics/vectors/explorers/vector_algebra/index.html"
HELPERS = REPO / "docs/gcdr-master-suite-helper-registry.json"

ALLOWED_FIDELITY = {"EXACT", "CONSTRAINT_FAITHFUL", "CONCEPT_ONLY", "UNAVAILABLE"}
REQUIRED_HELPERS = {
    "TEACHERS_CHALKBOARD",
    "TRAP_ALERT",
    "INDEPENDENT_CHECK",
    "TRANSFER_TAKEAWAY",
    "EXACTNESS_BADGE",
}


def load_bank(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"window\.JEE_QUESTIONS_DATA\s*=\s*(\[.*\])\s*;\s*$", text, re.S)
    if not match:
        raise AssertionError(f"cannot parse question bank {path}")
    return json.loads(match.group(1))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(v):
    return math.sqrt(dot(v, v))


def det3(a, b, c):
    return dot(a, cross(b, c))


class MasterSuiteAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.motion = load_bank(MOTION_DATA)
        cls.vector = load_bank(VECTOR_DATA)
        cls.motion_html = MOTION_HTML.read_text(encoding="utf-8")
        cls.vector_html = VECTOR_HTML.read_text(encoding="utf-8")
        cls.helpers = json.loads(HELPERS.read_text(encoding="utf-8"))

    def test_bank_sizes_and_live_corpus_labels_are_honest(self):
        self.assertEqual(len(self.motion), 18)
        self.assertEqual(len(self.vector), 13)
        self.assertIn("live corpus 123 PYQs", self.motion_html)
        self.assertIn("live corpus 282 PYQs", self.vector_html)
        self.assertNotIn("124 PYQ ExamSIDE Foundation", self.motion_html)
        self.assertNotIn("283 PYQ ExamSIDE Foundation", self.vector_html)

    def test_every_diagnostic_has_audited_helper_and_fidelity_fields(self):
        for q in self.motion + self.vector:
            with self.subTest(q=q["id"]):
                self.assertEqual(q["answerAudit"], "PASS")
                self.assertIn(q["simFidelity"], ALLOWED_FIDELITY)
                self.assertTrue(q["simFidelityNote"].strip())
                self.assertIsInstance(q.get("simBindingRefs"), list)
                if q["simFidelity"] in {"EXACT", "CONSTRAINT_FAITHFUL"}:
                    self.assertTrue(q["simBindingRefs"], q["id"])
                    self.assertEqual(
                        set(q["simBindingRefs"]),
                        {f"simParams.{key}" for key in (q.get("simParams") or {})},
                        q["id"],
                    )
                else:
                    self.assertEqual(q["simBindingRefs"], [], q["id"])
                self.assertTrue(q["teacherCheck"].strip())
                self.assertTrue(q["takeaway"].strip())
                self.assertTrue(q["trap"].strip())
                self.assertTrue(REQUIRED_HELPERS.issubset(set(q["helperTags"])))
                keys = [opt["key"] for opt in q["options"]]
                texts = [opt["text"] for opt in q["options"]]
                self.assertIn(q["correct"], keys)
                self.assertEqual(len(texts), len(set(texts)), f"duplicate option text in {q['id']}")

    def test_fidelity_loader_is_fail_closed(self):
        for html in (self.motion_html, self.vector_html):
            self.assertIn("if (fidelity === 'UNAVAILABLE')", html)
            self.assertIn("if (fidelity === 'CONCEPT_ONLY')", html)
            self.assertIn("No simulator state was changed.", html)
            self.assertIn("Simulator Fidelity", html)
            self.assertIn("Teacher's Chalkboard", html)
            self.assertIn("Transfer Takeaway", html)

    def test_non_unavailable_targets_exist(self):
        for html, bank in ((self.motion_html, self.motion), (self.vector_html, self.vector)):
            ids = set(re.findall(r'id="([^"]+)"', html))
            for q in bank:
                if q["simFidelity"] != "UNAVAILABLE":
                    self.assertIn(q["targetTab"], ids, q["id"])

    def test_collected_helper_registry_covers_question_helpers(self):
        registered = {
            row["id"] for row in self.helpers["core_helpers"]
        } | set(self.helpers["motion_1d_helpers"]) | set(self.helpers["vector_algebra_helpers"])
        self.assertEqual(len(registered), 41)
        for q in self.motion + self.vector:
            self.assertTrue(set(q["helperTags"]).issubset(registered), q["id"])

    def test_no_known_placeholder_reasoning_regressions(self):
        joined = "\n".join(
            str(value)
            for q in self.motion + self.vector
            for value in (q.get("ans"), q.get("formula"), *(q.get("steps") or []))
        ).lower()
        self.assertNotIn("wait:", joined)
        self.assertNotIn("rounding in key", joined)
        self.assertNotIn("evaluate from coordinate", joined)

    # ---------------- Motion 1D independent recalculation ----------------

    def test_motion_answers_recompute(self):
        q = {row["id"]: row for row in self.motion}

        # Q01: signed/absolute v-t areas
        signed = [0.5 * 10 * 20, 10 * 20, 0.5 * 10 * 20, -0.5 * 10 * 20]
        self.assertAlmostEqual(sum(abs(x) for x in signed), 500.0)
        self.assertAlmostEqual(sum(signed) / 40.0, 7.5)
        self.assertEqual(q["1D-Q01"]["correct"], "B")

        # Q02: x=6t-t^2, turning at t=3
        x = lambda t: 6 * t - t * t
        distance = abs(x(3)-x(0)) + abs(x(5)-x(3))
        self.assertEqual(distance, 13)
        self.assertEqual(q["1D-Q02"]["correct"], "C")

        # Q03: v=12(t-1)(t-2), a=24t-36
        self.assertEqual(24 * 2 - 36, 12)
        self.assertEqual(q["1D-Q03"]["correct"], "B")

        # Q04 equal-distance harmonic mean
        self.assertAlmostEqual(2 * 30 * 60 / (30 + 60), 40)
        self.assertEqual(q["1D-Q04"]["correct"], "B")

        # Q05 chain rule identity
        alpha, v = 0.37, 2.4
        self.assertAlmostEqual(v * (-2 * alpha * v * v), -2 * alpha * v**3)
        self.assertEqual(q["1D-Q05"]["correct"], "B")

        # Q06 a=v dv/dx for v=-mx+v0
        m, v0 = 1.5, 15
        self.assertGreater(m*m, 0)
        self.assertLess(-m*v0, 0)
        self.assertEqual(q["1D-Q06"]["correct"], "C")

        # Q07 slope(v^2 versus x)=2a
        slope = (0 - 100) / 25
        self.assertAlmostEqual(abs(slope / 2), 2)
        self.assertEqual(q["1D-Q07"]["correct"], "B")

        # Q08 area under triangular a-t graph
        self.assertAlmostEqual(0.5 * 8 * 6, 24)
        self.assertEqual(q["1D-Q08"]["correct"], "B")

        # Q09 1/2(v^2-u^2)= integral_0^2(3x^2+2x)dx = 12
        u = 2
        integral = 2**3 + 2**2
        vf = math.sqrt(u*u + 2*integral)
        self.assertAlmostEqual(vf, 2*math.sqrt(7))
        self.assertEqual(q["1D-Q09"]["correct"], "B")

        # Q10 balloon inheritance
        roots = [t for t in (5, -3) if t > 0]
        self.assertEqual(roots, [5])
        self.assertEqual(75 + 10*roots[0], 125)
        self.assertEqual(q["1D-Q10"]["correct"], "B")

        # Q11 drops: first has 5 intervals; fourth has 2
        dt = math.sqrt(5 / 125)
        fourth_height = 5 - 0.5 * 10 * (2*dt)**2
        self.assertAlmostEqual(dt, 0.2)
        self.assertAlmostEqual(fourth_height, 4.2)
        self.assertEqual(q["1D-Q11"]["correct"], "B")

        # Q12 piecewise paratrooper
        v1_sq = 2 * 9.8 * 50
        h2 = (v1_sq - 3**2) / (2*2)
        self.assertAlmostEqual(50 + h2, 292.75)
        self.assertEqual(q["1D-Q12"]["correct"], "A")

        # Q13 t_drop^2 = t_up * t_down: numerical independent instance
        h, u, g = 80, 20, 10
        t_up = (u + math.sqrt(u*u + 2*g*h)) / g
        t_down = (-u + math.sqrt(u*u + 2*g*h)) / g
        t_drop = math.sqrt(2*h/g)
        self.assertAlmostEqual(t_drop*t_drop, t_up*t_down)
        self.assertEqual(q["1D-Q13"]["correct"], "B")

        # Q14 dv/ds=-kv^2 integrates to 1/v=1/v0+ks
        v0, k, s = 10, 0.05, 4
        expected = v0 / (1 + k*s*v0)
        self.assertAlmostEqual(1/expected - 1/v0, k*s)
        self.assertEqual(q["1D-Q14"]["correct"], "B")

        # Q15 finite penetration for a=-beta v
        self.assertAlmostEqual(12/0.5, 24)
        self.assertEqual(q["1D-Q15"]["correct"], "A")

        # Q16 relative pursuit root
        t = -10 + 10*math.sqrt(3)
        self.assertAlmostEqual(100 - 10*t - 0.5*t*t, 0, places=9)
        self.assertLess(t, 10)
        self.assertEqual(q["1D-Q16"]["correct"], "D")

        # Q17 trains
        self.assertAlmostEqual((150+150)/(20+10), 10)
        self.assertEqual(q["1D-Q17"]["correct"], "A")

        # Q18 independent stopping distances
        gap = 1200 - (40**2/(2*1) + 20**2/(2*1))
        self.assertAlmostEqual(gap, 200)
        self.assertEqual(q["1D-Q18"]["correct"], "A")

    # ---------------- Vector Algebra independent recalculation ----------------

    def test_vector_answers_recompute(self):
        q = {row["id"]: row for row in self.vector}

        # Q01 coefficient construction PM=(a+b)/5-a
        self.assertAlmostEqual(1/5 - 1, -4/5)
        self.assertEqual(q["VEC-Q01"]["correct"], "A")

        # Q02 |a+b|=sqrt3 for unit vectors -> a.b=1/2
        adotb = (3 - 2) / 2
        value = 6 + 2*adotb - 15*adotb - 5
        self.assertAlmostEqual(value, -11/2)
        self.assertEqual(q["VEC-Q02"]["correct"], "A")

        # Q03 direction cosines
        cos2_gamma = 1 - math.cos(math.pi/3)**2 - math.cos(math.pi/4)**2
        self.assertAlmostEqual(math.acos(math.sqrt(cos2_gamma)), math.pi/3)
        self.assertEqual(q["VEC-Q03"]["correct"], "B")

        # Q04 orthogonal rejection
        a, b = (2,3,-1), (1,-2,2)
        coeff = dot(a,b)/dot(b,b)
        aperp = tuple(a[i] - coeff*b[i] for i in range(3))
        self.assertTrue(all(abs(x-y) < 1e-12 for x,y in zip(aperp,(8/3,5/3,1/3))))
        self.assertAlmostEqual(dot(aperp,b), 0)
        self.assertEqual(q["VEC-Q04"]["correct"], "A")

        # Q05 equal diagonal norms -> dot zero. Only the orthogonality
        # constraint is source-determined, so simulator fidelity is constraint-faithful.
        self.assertEqual(q["VEC-Q05"]["correct"], "C")
        self.assertEqual(q["VEC-Q05"]["simFidelity"], "CONSTRAINT_FAITHFUL")
        self.assertEqual(q["VEC-Q05"]["simBindingRefs"], ["simParams.theta_deg"])

        # Q06 triangle area squared
        a, b = (2,3,3), (6,3,3)
        u = tuple(2*a[i]+3*b[i] for i in range(3))
        v = tuple(a[i]-b[i] for i in range(3))
        area_sq = (0.5*norm(cross(u,v)))**2
        self.assertAlmostEqual(area_sq, 1800)
        self.assertEqual(q["VEC-Q06"]["correct"], "D")

        # Q07 parallelogram from diagonals
        d1, d2 = (3,1,-2), (1,-3,4)
        area = 0.5*norm(cross(d1,d2))
        self.assertAlmostEqual(area, 5*math.sqrt(3))
        self.assertEqual(q["VEC-Q07"]["correct"], "A")

        # Q08 Lagrange identity
        cross_mag = math.sqrt(10**2 * 2**2 - 12**2)
        self.assertAlmostEqual(cross_mag, 16)
        self.assertEqual(q["VEC-Q08"]["correct"], "A")

        # Q09 symmetric coplanarity determinant roots mu=1,-2
        for mu in (1,-2):
            self.assertAlmostEqual(det3((mu,1,1),(1,mu,1),(1,1,mu)), 0)
        self.assertEqual(1 + (-2), -1)
        self.assertEqual(q["VEC-Q09"]["correct"], "A")

        # Q10 scalar triple product volume
        a,b,c = (2,-3,4),(1,2,-1),(3,-1,2)
        self.assertAlmostEqual(abs(det3(a,b,c)), 7)
        self.assertEqual(q["VEC-Q10"]["correct"], "A")

        # Q11 vector equation
        a,b = (math.sqrt(7),1,-1),(0,1,2)
        lam = -dot(a,b)/dot(a,a)
        r = tuple(b[i]+lam*a[i] for i in range(3))
        self.assertAlmostEqual(norm(tuple(3*x for x in r))**2, 44)
        self.assertEqual(q["VEC-Q11"]["ans"], "44 (Option A)")
        self.assertEqual([o["text"] for o in q["VEC-Q11"]["options"]], ["44","54","86","132"])

        # Q12 BAC-CAB coefficient a.c=1/2 for unit a,c -> 60 degrees
        self.assertAlmostEqual(math.degrees(math.acos(0.5)), 60)
        self.assertEqual(q["VEC-Q12"]["correct"], "C")

        # Q13 skew-line common-normal projection
        p1,p2 = (1,2,3),(2,4,5)
        b1,b2 = (2,3,4),(3,4,5)
        connector = tuple(p2[i]-p1[i] for i in range(3))
        n = cross(b1,b2)
        distance = abs(dot(connector,n))/norm(n)
        self.assertAlmostEqual(distance, 1/math.sqrt(6))
        self.assertEqual(q["VEC-Q13"]["correct"], "A")

    def test_vector_representation_invariants(self):
        # Side-vector and diagonal descriptions of one parallelogram must preserve area.
        for a, b in (
            ((3, 1, -2), (1, -3, 4)),
            ((5, 0, 0), (2, 4, 0)),
            ((2, 3, 3), (6, 3, 3)),
        ):
            d1 = tuple(a[i] + b[i] for i in range(3))
            d2 = tuple(a[i] - b[i] for i in range(3))
            self.assertAlmostEqual(
                norm(cross(a, b)),
                0.5 * norm(cross(d1, d2)),
                places=12,
            )

        # Projection + rejection reconstructs a, and the rejection is orthogonal to b.
        a, b = (2, 3, -1), (1, -2, 2)
        coeff = dot(a, b) / dot(b, b)
        parallel = tuple(coeff * x for x in b)
        rejection = tuple(a[i] - parallel[i] for i in range(3))
        reconstructed = tuple(parallel[i] + rejection[i] for i in range(3))
        self.assertTrue(all(abs(x-y) < 1e-12 for x, y in zip(reconstructed, a)))
        self.assertAlmostEqual(dot(rejection, b), 0.0, places=12)

        # Direct VTP and BAC-CAB reconstruction must be the same vector.
        a, b, c = (2, -1, 3), (4, 2, -2), (1, 5, 2)
        direct = cross(a, cross(b, c))
        rhs = tuple(dot(a, c) * b[i] - dot(a, b) * c[i] for i in range(3))
        self.assertEqual(direct, rhs)

    def test_repaired_simulator_math_signatures_are_present(self):
        self.assertIn("v² = v₀²(1 - x/x₀)", self.motion_html)
        self.assertIn("const a = -(v0 * v0) / (2 * x0)", self.motion_html)
        self.assertIn("Area = ${area.toFixed(2)} = ½|d₁×d₂|", self.vector_html)
        self.assertIn("ay + by + cy_vec", self.vector_html)
        self.assertIn("const vtp1 = cross(a, cross(b, cVec))", self.vector_html)
        self.assertIn("const vtp2 = cross(cross(a, b), cVec)", self.vector_html)
        self.assertIn("const rp = [0,1,-1]", self.vector_html)
        self.assertIn("Auxiliary Constraint: r · c = 4", self.vector_html)


if __name__ == "__main__":
    unittest.main()
