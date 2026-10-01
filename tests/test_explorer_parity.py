"""The page computes what the build checked: Python and JavaScript evaluate one language and one model, on the same states."""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import unittest
from pathlib import Path

from Shared.tools import explorer_expr as expr
from Shared.tools import explorer_model as em

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests/fixtures/explorer/projectile-range.explorer.json"

CORPUS = [
    # arithmetic, precedence, associativity
    "1+2*3", "(1+2)*3", "10-4-3", "8/4/2", "-2^2", "(-2)^2", "2^3^2", "2*-3", "+5", "1e3+2.5e-1", "theta/7*7 - theta",
    # functions
    "sqrt(theta)", "abs(theta-45)", "exp(theta/50)", "ln(theta)", "log10(theta)", "sin(theta)", "cos(theta)", "tan(theta)",
    "asin(theta/100)", "acos(theta/100)", "atan(theta)", "atan2(theta, 3)", "sind(theta)", "cosd(theta)", "tand(theta)",
    "asind(theta/100)", "acosd(theta/100)", "atand(theta)", "atan2d(theta, 3)", "floor(theta/7)", "ceil(theta/7)", "round(theta/7)",
    "round(theta/7, 2)", "round(2.5)", "round(-2.5)", "round(2.675, 2)", "hypot(theta, 3)", "pow(theta, 0.5)", "sign(theta-30)",
    "clamp(theta, 10, 50)", "min(theta, 40, 50)", "max(theta, 40, 50)", "deg(theta/10)", "rad(theta)", "pi*theta", "e^1",
    # not a number
    "1/0", "sqrt(0-theta)", "ln(0)", "0^(0-1)", "10^1000", "acos(2)", "1/(theta-30)", "if(theta > 40, 1/(theta-50), 7)",
    "if(1/0, 1, 2)", "max(1, 1/0)", "sqrt(1/0) + 1",
    # comparisons and logic
    "theta < 40", "theta <= 30", "theta >= 30", "theta == 30", "theta != 30", "not theta > 20", "theta > 10 and theta < 50",
    "theta < 10 or theta > 20", "R == vx*T", "0.1 + 0.2 == 0.3", "0 and 1/0", "1 or 1/0", "2 and 3",
    # the model, as the page's claims read it
    "at(R, theta, 45)", "maxover(R, theta)", "minover(R, theta)", "argmax(R, theta)", "argmin(R, theta)", "at(H, theta, theta + 1)",
    "if(theta + 1 <= 85, at(R, theta, theta + 1) > R, 1)", "at(R, theta, 90 - theta) == R", "argmax(Rtempt, theta)",
    "maxover(R, theta) - minover(R, theta)", "at(R, v, 30, theta, 45)", "at(R, theta, 7)", "argmax(R, v)",
    # the scene's own numbers
    "landing_x", "hypot(vxArrow_x2 - vxArrow_x1, vyArrow_y2 - vyArrow_y1)", "peak_y - H",
]
TEMPLATES = [
    ("{R:1} m", {"R": 34.641016}, {"R": 2}, False), ("{R} m", {"R": 34.641016}, {"R": 2}, False), ("{x:0}", {"x": -0.4}, {}, False),
    ("{x:1}", {"x": -0.04}, {}, False), ("{R:1}", {"R": None}, {}, False), ("{R:1}", {"R": 1.0}, {}, True), ("{nope:1}", {}, {}, False),
]


def _states(model: em.Model) -> list[dict]:
    states = list(model.states())
    thin = [states[i] for i in range(0, len(states), 9)]
    return states[:1] + thin + [model.with_set({"v": 15, "g": 9.8}, s) for s in thin[:3]] + [model.with_set({"theta": 30.5})]


def _close(a, b) -> bool:
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    if math.isnan(a) or math.isnan(b):
        return math.isnan(a) and math.isnan(b)
    return abs(a - b) <= 1e-11 * max(1.0, abs(a), abs(b))


def _plain(value: float):
    return "NaN" if math.isnan(value) else "Inf" if value == math.inf else "-Inf" if value == -math.inf else value


def _two_slider_spec() -> dict:
    return {"parameters": [{"id": "a", "label": "a", "value": 3, "min": 0, "max": 10, "step": 1},
                           {"id": "b", "label": "b", "value": 2, "min": 0, "max": 4, "step": 0.5},
                           {"id": "c", "label": "c", "value": 7, "fixed": True}],
            "quantities": [{"id": "s", "label": "s", "expr": "a + b"}], "scene": {"elements": [], "world": {"x": [0, 1], "y": [0, 1]}}}


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class Parity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.model = em.Model(cls.spec)
        cls.compiled = em.compile_page_model(cls.spec)
        cls.states = _states(cls.model)
        cls.cases = [{"text": text, "state": state} for text in CORPUS for state in cls.states[:: max(1, len(cls.states) // 4)]]
        two = _two_slider_spec()
        wide = {**two, "parameters": [{"id": "a", "label": "a", "value": 500, "min": 0, "max": 1000, "step": 1}, two["parameters"][1], two["parameters"][2]]}
        cls.grids = [{"compiled": {"parameters": [dict(p, fixed=bool(p.get("fixed"))) for p in s["parameters"]], "steps": []}, "cap": cap}
                     for s in (two, wide) for cap in (3000, 100, 20)]
        cls.lattices = [{"id": "theta", "cap": cap} for cap in (361, 40, 7, 5)]
        payload = {"compiled": cls.compiled, "states": cls.states, "cases": cls.cases, "lattices": cls.lattices, "grids": cls.grids,
                   "formats": [list(t) for t in TEMPLATES]}
        run = subprocess.run(["node", str(REPO / "tests/explorer_parity.cjs")], input=json.dumps(payload), capture_output=True, text=True,
                             cwd=REPO, timeout=120)
        if run.returncode:
            raise AssertionError(run.stderr[-2000:])
        cls.js = json.loads(run.stdout)

    def test_every_number_of_the_model_is_the_same_in_both(self):
        for state, theirs in zip(self.states, self.js["values"]):
            mine = self.model.values(state)
            self.assertEqual(set(mine), set(theirs))
            for name, value in mine.items():
                self.assertTrue(_close(_plain(value), theirs[name]), (name, state, value, theirs[name]))

    def test_every_expression_of_the_corpus_is_the_same_in_both(self):
        for case, theirs in zip(self.cases, self.js["cases"]):
            try:
                mine = _plain(self.model.evaluate(case["text"], case["state"]))
            except expr.ExprError as caught:
                self.assertIsInstance(theirs, dict, (case, theirs))
                self.assertIn("error", theirs)
                continue
            self.assertFalse(isinstance(theirs, dict) and "error" in theirs, (case, theirs))
            self.assertTrue(_close(mine, theirs), (case["text"], case["state"], mine, theirs))

    def test_the_corpus_reaches_every_function_and_form_of_the_language(self):
        used = set()
        for text in CORPUS:
            used |= expr.names(expr.parse(text))[1]
        self.assertEqual((set(expr.FUNCTIONS) | expr.AGGREGATES) - used, set())

    def test_the_sliders_lattice_and_the_states_swept_are_the_same_in_both(self):
        for row, theirs in zip(self.lattices, self.js["lattices"]):
            self.assertEqual(self.model.lattice(row["id"], row["cap"]), theirs, row)
        for row, theirs in zip(self.grids, self.js["grids"]):
            params = row["compiled"]["parameters"]
            mine = list(em.Model({"parameters": params, "quantities": [{"id": "s", "label": "s", "expr": "1"}],
                                  "scene": {"elements": []}}).states(row["cap"]))
            self.assertEqual(mine, theirs, row["cap"])

    def test_numbers_are_written_the_same_in_both(self):
        for (template, env, decimals, hidden), theirs in zip(TEMPLATES, self.js["formats"]):
            self.assertIsInstance(theirs, str)
        self.assertEqual(self.js["formats"][0], "34.6 m")
        self.assertEqual(self.js["formats"][1], "34.64 m")
        self.assertEqual(self.js["formats"][2], "0", "a small negative number is not written as minus zero")
        self.assertEqual(self.js["formats"][4], "—")
        self.assertEqual(self.js["formats"][5], "?")


if __name__ == "__main__":
    unittest.main()
