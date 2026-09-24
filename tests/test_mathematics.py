"""The second subject: an incompatible result shape carried through the same engine.

Physics answers are measurements compared within a tolerance. Mathematics answers are
exact, and a tolerance applied to one would accept a wrong answer -- 2.333333333333 is
within 1e-9 of 7/3 and is not a solution of 3x + 2 = 9. These tests exist to hold that
distinction in place: if the exact path ever silently degrades to the tolerance path,
the suite must fail rather than publish a plausible falsehood.
"""
import copy
import json
import re
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Mathematics.adapter import load as load_mathematics  # noqa: E402
from Mathematics.adapter.validator import recompute  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402
from Shared.library.compile_inputs import compile_bucket, write  # noqa: E402
from Shared.library.resolve import build_index  # noqa: E402
from Shared.publication_host.host import publish  # noqa: E402
from Shared.publication_host.science import numeric_atom  # noqa: E402

BUCKET = "BUCKET-LINEAR-EQUATION"
PACKAGES = sorted((REPO / "Mathematics/library").glob("*.json"))
TRUNCATION = "2.333333333333"


def records():
    return build_index([json.loads(p.read_text(encoding="utf-8")) for p in PACKAGES])


def compile_inputs(into: Path, mutate=None):
    compiled = compile_bucket(records(), BUCKET, topic_id="MATH-LINEQ-G9",
                              title="Linear equations in one unknown", subject="Mathematics",
                              practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"})
    if mutate is not None:
        mutate(compiled)
    into.mkdir(parents=True, exist_ok=True)
    write(compiled, into)
    return compiled


class ExactArithmetic(unittest.TestCase):
    """The validator computes exactly, and refuses what it cannot decide."""

    def test_a_non_terminating_solution_comes_back_as_a_ratio_not_a_decimal(self):
        result = recompute({"validator_id": "LINEAR_EQUATION", "domain": "RATIONAL",
                            "a": 3, "b": 2, "c": 9})
        self.assertEqual(result, "7/3")
        self.assertNotIsInstance(result, float)

    def test_a_terminating_solution_comes_back_as_an_integer(self):
        self.assertEqual(recompute({"validator_id": "LINEAR_EQUATION", "domain": "RATIONAL",
                                    "a": 5, "b": -4, "c": 11}), 3)

    def test_a_zero_coefficient_is_refused_rather_than_divided_by(self):
        with self.assertRaises(ValueError) as caught:
            recompute({"validator_id": "LINEAR_EQUATION", "domain": "RATIONAL",
                       "a": 0, "b": 2, "c": 9})
        self.assertIn("LINEAR_SOLUTION_NOT_UNIQUE", str(caught.exception))

    def test_an_undeclared_domain_is_refused_rather_than_assumed(self):
        # Over the integers 3x + 2 = 9 has no solution. The validator will not guess
        # which number system the question meant.
        with self.assertRaises(ValueError) as caught:
            recompute({"validator_id": "LINEAR_EQUATION", "a": 3, "b": 2, "c": 9})
        self.assertIn("MATHEMATICAL_DOMAIN_UNSUPPORTED", str(caught.exception))

    def test_a_float_input_is_refused_because_it_is_already_inexact(self):
        with self.assertRaises(ValueError) as caught:
            recompute({"validator_id": "LINEAR_EQUATION", "domain": "RATIONAL",
                       "a": 3.0, "b": 2, "c": 9})
        self.assertIn("EXACT_RATIONAL_REQUIRED", str(caught.exception))


class ExactSourceAtoms(unittest.TestCase):
    """A source atom may be exact; reading it must not round it."""

    def _atoms(self, value):
        return {"atoms": {"a": {"value": value, "unit": "dimensionless"}}}

    def test_an_exact_rational_atom_is_read_as_a_fraction(self):
        self.assertEqual(numeric_atom(self._atoms("7/3"), "a"), Fraction(7, 3))

    def test_a_decimal_written_as_a_string_is_refused(self):
        # "2.333" as an atom is a rounded value claiming to be recorded exactly.
        # A genuinely approximate quantity is stored as a float and says so.
        with self.assertRaises(ContractError) as caught:
            numeric_atom(self._atoms("2.333"), "a")
        self.assertEqual(caught.exception.code, "NUMERIC_ATOM_INVALID")

    def test_a_float_atom_still_reads_as_a_float(self):
        self.assertEqual(numeric_atom(self._atoms(2.333333333333), "a"), 2.333333333333)


class NumberLineScene(unittest.TestCase):
    """The representation this subject leans on, drawn from library-held instances."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def _svg(self, out):
        figures = sorted((out / "figures").glob("*.svg"))
        self.assertEqual(len(figures), 1, "the two products share one content-addressed figure")
        return figures[0].read_text(encoding="utf-8")

    def test_the_axis_brackets_the_marks_with_integer_ticks(self):
        # A value drawn at the end of the line reads as the end of the number system.
        # 7/3 must sit between a 2 and a 3 that are both drawn.
        inputs, out = self.root / "inputs", self.root / "publication"
        compile_inputs(inputs)
        publish(inputs / "plan.json", inputs / "baseline.json", inputs, out, load_mathematics())
        ticks = re.findall(r'<text[^>]*y="117\.000"[^>]*>(-?\d+)</text>', self._svg(out))
        self.assertEqual(ticks, ["0", "1", "2", "3"])

    def test_two_marks_on_the_same_pixel_stay_separately_visible(self):
        # 7/3 and its truncation are 5e-11 pixels apart. Drawn both on the axis, one
        # would paint over the other and hide whether that endpoint is included.
        inputs, out = self.root / "inputs", self.root / "publication"
        compile_inputs(inputs)
        publish(inputs / "plan.json", inputs / "baseline.json", inputs, out, load_mathematics())
        svg = self._svg(out)
        circles = re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)"[^>]*fill="([^"]+)"', svg)
        self.assertEqual(len(circles), 2)
        self.assertEqual({c[0] for c in circles}, {circles[0][0]}, "neither mark moved sideways")
        self.assertNotEqual(circles[0][1], circles[1][1], "one mark was lifted clear")
        self.assertEqual({c[2] for c in circles}, {"white", "#135b89"},
                         "the excluded point stays open and the solution stays closed")

    def test_the_digest_distinguishes_marks_a_tolerance_would_not(self):
        inputs, out = self.root / "inputs", self.root / "publication"
        compile_inputs(inputs)
        publish(inputs / "plan.json", inputs / "baseline.json", inputs, out, load_mathematics())
        evidence = json.loads((out / "evidence.json").read_text(encoding="utf-8"))
        marks = evidence["figures"]["CORE1A-FIG-MATH-EXACT-VS-TRUNCATED"]["marks"]
        self.assertEqual(marks, ["7/3", TRUNCATION], "each mark is recorded as the library recorded it")

    def test_a_mark_that_does_not_declare_inclusion_is_refused(self):
        def drop_closed(compiled):
            for product in compiled["plan"]["products"]:
                for unit in product["units"]:
                    for block in unit["blocks"]:
                        if block["kind"] == "FIGURE":
                            block["scene"]["marks"][0].pop("closed")
        inputs, out = self.root / "inputs", self.root / "publication"
        compile_inputs(inputs, drop_closed)
        with self.assertRaises(ContractError) as caught:
            publish(inputs / "plan.json", inputs / "baseline.json", inputs, out, load_mathematics())
        self.assertEqual(caught.exception.code, "NUMBER_LINE_ENDPOINT_UNDECLARED")

    def test_a_figure_may_not_draw_a_value_it_did_not_declare(self):
        def steal_atom(compiled):
            for product in compiled["plan"]["products"]:
                for unit in product["units"]:
                    for block in unit["blocks"]:
                        if block["kind"] == "FIGURE":
                            block["scene"]["marks"][0]["atom"] = "DAT-MATH-A"
                            block["source_atom_ids"] = [a for a in block["source_atom_ids"]
                                                        if a != "DAT-MATH-A"]
        inputs, out = self.root / "inputs", self.root / "publication"
        compile_inputs(inputs, steal_atom)
        with self.assertRaises(ContractError) as caught:
            publish(inputs / "plan.json", inputs / "baseline.json", inputs, out, load_mathematics())
        self.assertEqual(caught.exception.code, "FIGURE_SOURCE_BINDING_MISSING")


class LibraryHeldFigures(unittest.TestCase):
    """A representation states a requirement; a scene instance on it states a figure."""

    def test_instances_compile_into_figure_blocks_bound_to_their_microtopic(self):
        compiled = compile_bucket(records(), BUCKET, topic_id="T", title="T", subject="Mathematics",
                                  practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"})
        blocks = [b for p in compiled["plan"]["products"] for u in p["units"]
                  for b in u["blocks"] if b["kind"] == "FIGURE"]
        self.assertEqual({b["id"] for b in blocks},
                         {"CORE1-FIG-MATH-EXACT-VS-TRUNCATED",
                          "CORE1A-FIG-MATH-EXACT-VS-TRUNCATED",
                          "CORE1B-FIG-MATH-EXACT-VS-TRUNCATED"})
        # The teaching products bind it to the microtopic it explains. Core1 binds the
        # same instance to the bucket's orientation instead: there it is the map of the
        # bucket rather than the illustration of one transition in it.
        for block in blocks:
            with self.subTest(block=block["id"]):
                self.assertEqual(block["obligation_ids"],
                                 ["OB-BUCKET-LINEAR-EQUATION-ORIENTATION"]
                                 if block["id"].startswith("CORE1-")
                                 else ["OB-MIC-MATH-EXACT-SOLUTION"])

    def test_a_representation_with_no_instance_reports_authoring_still_outstanding(self):
        data = records()
        data["REP-MATH-NUMBER-LINE"] = {**data["REP-MATH-NUMBER-LINE"], "scene_instances": []}
        compiled = compile_bucket(data, BUCKET, topic_id="T", title="T", subject="Mathematics",
                                  practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"})
        outstanding = [r for r in compiled["authoring_requirements"] if r["kind"] == "FIGURE_AUTHORING"]
        self.assertEqual([r["representation"] for r in outstanding], ["REP-MATH-NUMBER-LINE"])
        self.assertFalse([b for p in compiled["plan"]["products"] for u in p["units"]
                          for b in u["blocks"] if b["kind"] == "FIGURE"])

    def test_an_instance_binding_a_datum_this_bucket_does_not_carry_fails_closed(self):
        data = records()
        instance = copy.deepcopy(data["REP-MATH-NUMBER-LINE"]["scene_instances"][0])
        instance["datum_refs"] = instance["datum_refs"] + ["DAT-MATH-NOT-HERE"]
        data["REP-MATH-NUMBER-LINE"] = {**data["REP-MATH-NUMBER-LINE"], "scene_instances": [instance]}
        with self.assertRaises(ContractError) as caught:
            compile_bucket(data, BUCKET, topic_id="T", title="T", subject="Mathematics",
                           practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"})
        self.assertEqual(caught.exception.code, "FIGURE_BINDS_UNKNOWN_DATUM")


class EndToEnd(unittest.TestCase):
    """The whole path: library records in, verified publication out."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def _publish(self, mutate=None, name="publication"):
        inputs, out = self.root / name / "inputs", self.root / name / "publication"
        compile_inputs(inputs, mutate)
        return publish(inputs / "plan.json", inputs / "baseline.json", inputs, out,
                       load_mathematics()), out

    def test_the_bucket_publishes_and_its_exact_answer_is_verified(self):
        result, out = self._publish()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["products"], ["CORE1", "CORE1A", "CORE1B", "CORE2A"])
        # The authored Mathematics practice question remains available to the teaching
        # products but no longer masquerades as Core2 source custody. Its exact answer is
        # therefore checked only in the products that legitimately state it.
        self.assertEqual(result["numeric_answers_compared"], 2)
        self.assertEqual(result["scientific_reviews_pending"], 0)
        self.assertFalse(result["release_authorized"], "machine checks never authorise release")
        evidence = json.loads((out / "evidence.json").read_text(encoding="utf-8"))
        answer = evidence["numeric_answers"]["CORE2A-Q-MATH-LINEAR-01"]
        self.assertEqual(answer["value"], "7/3")
        self.assertEqual(answer["comparison"], "EXACT_RATIONAL_EQUALITY")
        self.assertEqual(answer["status"], "VERIFIED_BY_SUPPORTED_EVALUATOR")

    def test_the_decimal_a_tolerance_would_accept_is_rejected(self):
        # This is the whole reason the comparison is declared per validator rather
        # than assumed: substituting this value gives 8.999999999999, not 9.
        def truncate(compiled):
            for product in compiled["plan"]["products"]:
                for unit in product["units"]:
                    for block in unit["blocks"]:
                        if block["kind"] == "QUESTION":
                            block["answer"]["numeric"]["value"] = TRUNCATION
        with self.assertRaises(ContractError) as caught:
            self._publish(truncate)
        self.assertEqual(caught.exception.code, "PUBLISHED_ANSWER_MISMATCH")

    def test_the_basis_digest_covers_the_inputs_and_not_the_renderer(self):
        # Two runs of the same compiled inputs agree, so a digest mismatch reports a
        # changed plan or baseline rather than an unrelated code edit.
        first, _ = self._publish(name="run-a")
        second, _ = self._publish(name="run-b")
        self.assertEqual(first["basis_digest"], second["basis_digest"])

    def test_the_engine_refuses_this_subject_kit_on_another_subjects_plan(self):
        physics = REPO / "Physics/content/relative-motion-g9/inputs"
        with self.assertRaises(ContractError) as caught:
            publish(physics / "plan.json", physics / "baseline.json", physics,
                    self.root / "wrong", load_mathematics())
        self.assertEqual(caught.exception.code, "WRONG_SUBJECT_KIT")


if __name__ == "__main__":
    unittest.main()
