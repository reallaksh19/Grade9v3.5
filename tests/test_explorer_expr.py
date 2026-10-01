"""The expression language an explorer's numbers are written in: one grammar, checked, evaluated and shown."""
from __future__ import annotations

import math
import unittest
import xml.etree.ElementTree as ET

from Shared.tools import explorer_expr as expr

MATHML_TAGS = {"math", "mrow", "mi", "mn", "mo", "msub", "msup", "mfrac", "mtext", "msqrt"}


class Evaluate(unittest.TestCase):
    def test_arithmetic_follows_the_usual_precedence_and_a_unary_minus_binds_looser_than_a_power(self):
        for text, want in [("1+2*3", 7), ("(1+2)*3", 9), ("10-4-3", 3), ("8/4/2", 1), ("-2^2", -4), ("(-2)^2", 4),
                           ("2^3^2", 512), ("2*-3", -6), ("+5", 5), ("1e3+2.5e-1", 1000.25)]:
            self.assertAlmostEqual(expr.evaluate(text), want, msg=text)

    def test_names_and_constants(self):
        self.assertAlmostEqual(expr.evaluate("2*pi*r", {"r": 1}), 2 * math.pi)
        self.assertAlmostEqual(expr.evaluate("e^1"), math.e)
        self.assertEqual(expr.evaluate("sqrt(a^2+b^2)", {"a": 5, "b": 12}), 13)

    def test_a_name_without_a_value_is_an_error_and_never_zero(self):
        with self.assertRaisesRegex(expr.ExprError, "'x' has no value"):
            expr.evaluate("x+1", {})

    def test_degree_functions_and_the_half_up_rounding_the_page_uses(self):
        self.assertAlmostEqual(expr.evaluate("cosd(60)"), 0.5)
        self.assertAlmostEqual(expr.evaluate("atan2d(6,8)"), 36.8698976, places=6)
        self.assertAlmostEqual(expr.evaluate("asind(0.5)"), 30)
        self.assertEqual(expr.evaluate("round(2.5)"), 3)
        self.assertEqual(expr.evaluate("round(-2.5)"), -2)
        self.assertEqual(expr.evaluate("round(2.675, 2)"), 2.68)   # half up on the scaled value, as the page does
        self.assertEqual(expr.evaluate("clamp(9, 0, 3)"), 3)
        self.assertEqual(expr.evaluate("min(4, 2, 9)"), 2)
        self.assertEqual(expr.evaluate("hypot(5, 12)"), 13)

    def test_a_result_that_is_not_a_finite_number_is_nan_and_stays_nan(self):
        for text in ("1/0", "sqrt(0-1)", "ln(0)", "acos(2)", "0^(-1)", "10^1000", "sqrt(1/0)+1", "max(1, 1/0)"):
            self.assertTrue(math.isnan(expr.evaluate(text)), text)
        self.assertFalse(expr.holds("1/0 > 1", {}))
        self.assertFalse(expr.holds("not (1/0)", {}), "NaN is neither true nor false, so a check on it fails")

    def test_if_evaluates_only_the_branch_it_takes(self):
        self.assertEqual(expr.evaluate("if(a == 0, 0, 1/a)", {"a": 0}), 0)
        self.assertEqual(expr.evaluate("if(a == 0, 0, 1/a)", {"a": 4}), 0.25)
        self.assertTrue(math.isnan(expr.evaluate("if(1/0, 1, 2)")))

    def test_comparisons_are_one_or_zero_and_equality_allows_a_relative_tolerance(self):
        self.assertEqual(expr.evaluate("3 < 4"), 1)
        self.assertEqual(expr.evaluate("4 <= 4"), 1)
        self.assertEqual(expr.evaluate("5 != 5"), 0)
        self.assertEqual(expr.evaluate("a == b", {"a": 0.1 + 0.2, "b": 0.3}), 1)
        self.assertEqual(expr.evaluate("a == b", {"a": 1e12, "b": 1e12 * (1 + 1e-12)}), 1)
        self.assertEqual(expr.evaluate("a == b", {"a": 1.0, "b": 1.0001}), 0)
        self.assertEqual(expr.evaluate("a >= b", {"a": 0.1 + 0.2, "b": 0.3}), 1, "a bound that is met up to rounding is met")

    def test_logic_reads_any_non_zero_number_as_true_and_short_circuits(self):
        self.assertEqual(expr.evaluate("2 and 3"), 1)
        self.assertEqual(expr.evaluate("0 or 0"), 0)
        self.assertEqual(expr.evaluate("not 0"), 1)
        self.assertEqual(expr.evaluate("0 and 1/0"), 0)
        self.assertEqual(expr.evaluate("1 or 1/0"), 1)
        self.assertEqual(expr.evaluate("a < b and b < c", {"a": 1, "b": 2, "c": 3}), 1)
        self.assertEqual(expr.evaluate("not a < b or a == b", {"a": 2, "b": 2}), 1)


class Check(unittest.TestCase):
    def test_what_is_wrong_is_said_in_the_authors_terms(self):
        self.assertEqual(expr.check("sqrt(a^2 + b^2)", {"a", "b"}), [])
        self.assertIn("is not a parameter or an earlier quantity", expr.check("a + c", {"a"})[0])
        self.assertIn("foo() is not a function", expr.check("foo(1)")[0])
        self.assertIn("sqrt() takes 1 argument(s), got 2", expr.check("sqrt(1, 2)")[0])
        self.assertIn("atan2() takes 2 argument(s), got 1", expr.check("atan2(1)")[0])
        self.assertIn("at least one", expr.check("max()")[0])
        self.assertEqual(expr.check("round(2.5, 1)"), [])
        self.assertIn("1 or 2", expr.check("round(1, 2, 3)")[0])

    def test_there_is_no_implicit_multiplication_and_the_error_says_what_to_write(self):
        for text in ("2a", "2(3)", "a b", "3 4"):
            self.assertIn("no implicit multiplication", expr.check(text, {"a", "b"})[0], text)

    def test_syntax_errors_name_the_position_or_the_missing_piece(self):
        self.assertEqual(expr.check(""), ["the expression is empty"])
        self.assertEqual(expr.check("a +", {"a"}), ["the expression ends where more is expected"])
        self.assertIn("expected ')'", expr.check("(1+2")[0])
        self.assertIn("unexpected character '$' at position 3", expr.check("x $ y", {"x", "y"})[0])
        self.assertIn("keyword", expr.check("and + 1")[0])
        self.assertEqual(expr.check(7), ["an expression is a string"])

    def test_a_character_the_language_does_not_have_comes_with_what_to_write_instead(self):
        for text, advice in [("a ** 2", "write powers with ^"), ("a = b", "write =="), ("5 × 3", "write multiplication as *"), ("√x", "write sqrt(x)"),
                             ("θ + 1", "theta"), ("x²", "x^2"), ("30°", "sind, cosd"), ("a & b", "write and"), ("a | b", "write or"), ("50%", "/100"),
                             ("\\frac{1}{2}", "not LaTeX"), ("[a]", "use ( )")]:
            self.assertIn(advice, expr.check(text, {"a", "b", "x", "theta"})[0], text)

    def test_each_problem_is_listed_once(self):
        problems = expr.check("foo(a) + bar(a) + zed", {"a"})
        self.assertEqual(len(problems), 3, problems)

    def test_names_reports_variables_and_functions_without_constants(self):
        tree = expr.parse("sqrt(a^2 + 2*pi*b) / hypot(c, d)")
        self.assertEqual(expr.names(tree), ({"a", "b", "c", "d"}, {"sqrt", "hypot"}))


class FakeModel:
    """R is 17 at 0 degrees, 13 at 90 and 7 at 180: the resolver answers what the explorer's model would."""
    points = [(0.0, 17.0), (45.0, 15.0), (90.0, 13.0), (135.0, 10.0), (180.0, 7.0)]

    def at(self, name: str, overrides: dict) -> float:
        if name == "R":
            return dict(self.points).get(overrides.get("theta"), float("nan"))
        raise KeyError(name)

    def sweep(self, name: str, parameter: str) -> list:
        return list(self.points)


class ModelForms(unittest.TestCase):
    def test_at_reads_the_model_with_a_parameter_set_and_the_rest_as_they_are(self):
        self.assertEqual(expr.evaluate("at(R, theta, 90)", {}, FakeModel()), 13)
        self.assertEqual(expr.evaluate("at(R, theta, 90) == 13", {}, FakeModel()), 1)
        self.assertEqual(expr.evaluate("at(R, theta, 2*45)", {}, FakeModel()), 13, "the value is an expression")

    def test_maxover_minover_argmax_argmin_sweep_the_parameter(self):
        model = FakeModel()
        self.assertEqual(expr.evaluate("maxover(R, theta)", {}, model), 17)
        self.assertEqual(expr.evaluate("minover(R, theta)", {}, model), 7)
        self.assertEqual(expr.evaluate("argmax(R, theta)", {}, model), 0)
        self.assertEqual(expr.evaluate("argmin(R, theta)", {}, model), 180)
        self.assertEqual(expr.evaluate("maxover(R, theta) - minover(R, theta)", {}, model), 10)

    def test_a_tie_goes_to_the_first_value(self):
        model = FakeModel()
        model.points = [(10.0, 5.0), (20.0, 5.0), (30.0, 5.0 + 1e-12)]
        self.assertEqual(expr.evaluate("argmax(R, theta)", {}, model), 10)

    def test_a_model_form_without_a_model_is_an_error_and_a_gap_in_the_model_is_nan(self):
        with self.assertRaisesRegex(expr.ExprError, "no model here"):
            expr.evaluate("maxover(R, theta)", {})
        self.assertTrue(math.isnan(expr.evaluate("at(R, theta, 7)", {}, FakeModel())))
        model = FakeModel()
        model.points = [(0.0, 1.0), (1.0, float("nan"))]
        self.assertTrue(math.isnan(expr.evaluate("maxover(R, theta)", {}, model)))

    def test_what_is_wrong_with_a_model_form_is_said_in_the_authors_terms(self):
        known = {"R", "theta", "a"}
        self.assertEqual(expr.check("maxover(R, theta) == a + 5", known, parameters={"theta", "a"}), [])
        self.assertIn("takes a quantity and a parameter", expr.check("maxover(R)", known)[0])
        self.assertIn("then pairs of a parameter and a value", expr.check("at(R, theta)", known)[0])
        self.assertIn("must be a name", expr.check("at(R, 3, 90)", known)[0])
        self.assertIn("'R' is not a parameter, so at() cannot set or sweep it", expr.check("at(a, R, 1)", known, parameters={"theta", "a"})[0])
        self.assertIn("not in a quantity or in the geometry of a scene", expr.check("maxover(R, theta)", known, model_forms=False)[0])

    def test_the_forms_read_as_maths(self):
        self.assertIn("<mi>max</mi>", expr.to_mathml("maxover(R, theta)"))
        markup = expr.to_mathml("at(R, theta, 90 - theta) == R")
        self.assertIn("<msub>", markup)
        self.assertNotIn("<mi>at</mi>", markup)


class Display(unittest.TestCase):
    def tags(self, markup: str) -> set[str]:
        return {node.tag.split("}", 1)[-1] for node in ET.fromstring(markup).iter()}

    def test_the_markup_is_well_formed_and_inside_the_restricted_presentation_subset(self):
        for text in ("sqrt(a^2 + b^2 + 2*a*b*cosd(theta))", "(a - b)/(c + d)", "-x^2", "a <= b", "a == b and c != d",
                     "abs(x_1 - x_2)", "atan2d(y, x)", "round(a, 2)", "a < 2 or not b", "2^(n+1)"):
            markup = expr.to_mathml(text)
            self.assertLessEqual(self.tags(markup), MATHML_TAGS, text)

    def test_the_markup_is_built_from_the_tree_so_the_text_cannot_inject_anything(self):
        with self.assertRaises(expr.ExprError):
            expr.to_mathml("a + <script>alert(1)</script>")
        self.assertNotIn("<script", expr.to_mathml("a<b"))
        self.assertIn("&lt;", expr.to_mathml("a<b"))

    def test_structure_reads_as_the_maths_it_is(self):
        self.assertIn("<msqrt>", expr.to_mathml("sqrt(x)"))
        self.assertIn("<mfrac>", expr.to_mathml("a/b"))
        self.assertIn("<msup><mi>a</mi><mn>2</mn></msup>", expr.to_mathml("a^2"))
        self.assertIn("<msub><mi>v</mi><mi>1</mi></msub>", expr.to_mathml("v_1"))
        self.assertIn("<mi>θ</mi>", expr.to_mathml("theta"))
        self.assertIn("<mi>cos</mi>", expr.to_mathml("cosd(theta)"), "the degree functions read as the ordinary ones")
        self.assertIn("≤", expr.to_mathml("a <= b"))

    def test_brackets_appear_where_the_precedence_needs_them_and_only_there(self):
        self.assertIn("<mo>(</mo>", expr.to_mathml("(a + b)*c"))
        self.assertNotIn("<mo>(</mo>", expr.to_mathml("a*b + c"))
        self.assertIn("<mo>(</mo>", expr.to_mathml("a - (b - c)"))
        self.assertIn("<mo>(</mo>", expr.to_mathml("(a + b)^2"))
        self.assertNotIn("<mo>(</mo>", expr.to_mathml("a^2"))


if __name__ == "__main__":
    unittest.main()
