"""An explorer spec is held to its own numbers: every claim it makes is computed at every position the learner's sliders can reach."""
from __future__ import annotations

import copy
import json
import math
import unittest
from pathlib import Path

from Shared.tools import explorer_model as em

FIXTURE = Path(__file__).resolve().parent / "fixtures/explorer/projectile-range.explorer.json"
BRIEF = {"question_ref": "Q-PROJ-8", "label": "Q8", "rule": "the most conceptual question first"}
BASE = json.loads(FIXTURE.read_text(encoding="utf-8"))


def run(change=None, brief=BRIEF) -> em.Report:
    spec = copy.deepcopy(BASE)
    if change:
        change(spec)
    return em.check(spec, brief)


def lines(report: em.Report, kind: str | None = None) -> list[str]:
    return [f.line() for f in report.findings if kind in (None, f.kind)]


class Reference(unittest.TestCase):
    def test_the_reference_spec_has_no_finding_and_its_evidence_is_computed_not_declared(self):
        report = run()
        self.assertEqual(lines(report), [])
        e = report.evidence
        self.assertEqual(e["states_checked"], 81)
        self.assertEqual(e["prediction"], {"options": 3, "true": [1]})
        self.assertEqual(e["observations"], ["sometimes", "always", "always", "never"])
        self.assertEqual((e["invariants_held"], e["oracles_held"]), (2, 3))
        self.assertEqual(e["boundary"], ["holds", "fails", "fails"])
        self.assertLess(e["equation"]["largest_relative_difference"], 1e-12)
        self.assertEqual(e["contradiction"]["states_that_agree"], 1, "the tempting model is right at 60 degrees and nowhere else")

    def test_the_blueprint_names_the_route_and_every_step_of_it_is_a_component(self):
        bp = em.blueprint()
        ids = {c["id"] for c in bp["components"]}
        self.assertEqual(em.stages(bp), ["CONTEXT", "PREDICT", "MANIPULATE", "OBSERVE", "CONTRADICT", "DECONSTRUCT", "RECONSTRUCT", "INVARIANT",
                                         "BOUNDARY", "FADE", "TRANSFER"])
        self.assertTrue(set(em.stages(bp)) <= ids)
        self.assertTrue(all(c["level"] == "REQUIRED" for c in bp["components"]), "an explorer is the route or it is not an explorer")


class Structure(unittest.TestCase):
    def test_a_key_that_is_not_in_the_spec_a_missing_key_and_an_empty_sentence_are_each_named_where_they_are(self):
        def change(spec):
            spec["predict"]["extra"] = 1
            del spec["boundary"]["assumption"]
            spec["context"]["situation"] = ""
        found = lines(run(change), "error")
        self.assertIn("PREDICT predict: unknown key 'extra'", found)
        self.assertIn("BOUNDARY boundary: the key 'assumption' is missing", found)
        self.assertIn("CONTEXT context.situation: is empty; write it", found)

    def test_nothing_else_is_judged_while_the_structure_is_wrong(self):
        report = run(lambda spec: spec.pop("transfer"))
        self.assertEqual([f.component for f in report.errors], ["TRANSFER"])

    def test_the_blueprint_the_spec_names_must_be_the_active_one(self):
        found = lines(run(lambda spec: spec.update(blueprint_ref="BP-EXPLORER-GCDR@0.9.0")), "error")
        self.assertTrue(any("not the active explorer blueprint BP-EXPLORER-GCDR@1.0.0" in line for line in found), found)


class NeverCrashes(unittest.TestCase):
    """Whatever an author puts in a field, the check answers with findings; it never stops with a traceback."""

    JUNK_TEXT = ["", "1/0", "at(R)", "maxover(R, theta", "nonexistent", "R == ", "at(R, 5, 6)", "θ"]
    JUNK_NUMBER = [-1, 0, 1e9]

    def leaves(self, node, path=()):
        if isinstance(node, dict):
            for key, value in node.items():
                yield from self.leaves(value, path + (key,))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                yield from self.leaves(value, path + (index,))
        elif isinstance(node, (str, int, float)) and not isinstance(node, bool):
            yield path, node

    def put(self, spec, path, value):
        node = spec
        for part in path[:-1]:
            node = node[part]
        node[path[-1]] = value

    def test_a_junk_value_in_any_field_gives_findings_and_never_a_traceback(self):
        leaves = list(self.leaves(BASE))
        ran = 0
        for number, (path, original) in enumerate(leaves):
            if number % 9:
                continue
            for junk in (self.JUNK_TEXT if isinstance(original, str) else self.JUNK_NUMBER):
                spec = copy.deepcopy(BASE)
                self.put(spec, path, junk)
                try:
                    report = em.check(spec, BRIEF)
                except Exception as caught:      # noqa: BLE001
                    self.fail(f"{'.'.join(map(str, path))} = {junk!r} stopped the check: {type(caught).__name__}: {caught}")
                self.assertIsInstance(report.findings, list)
                ran += 1
        self.assertGreater(ran, 150)

    def test_a_field_of_the_wrong_kind_gives_a_structure_finding(self):
        for change in (lambda s: s.update(scene=[]), lambda s: s.update(parameters={}), lambda s: s["scene"]["elements"].append("point"),
                       lambda s: s["predict"].update(options="three"), lambda s: s.update(transfer=None)):
            spec = copy.deepcopy(BASE)
            change(spec)
            report = em.check(spec, BRIEF)
            self.assertTrue(report.errors)


class Numbers(unittest.TestCase):
    def test_a_number_where_an_expression_goes_is_the_expression_that_number(self):
        def change(spec):
            elements = {e["id"]: e for e in spec["scene"]["elements"]}
            elements["ground"].update({"from": [-2, 0], "to": [44, 0]})
            elements["angleArc"].update({"r": 6, "from_deg": 0})
            elements["launch"].update({"at": [0, 0.0]})
            elements["path"].update({"t_min": 0})
        report = run(change)
        self.assertEqual(lines(report), [])
        normalized = em.normalize(json.loads(json.dumps(BASE | {"scene": {**BASE["scene"], "elements": [
            {"id": "a", "kind": "polygon", "points": [[0, 0], [1.5, 2], [3, 0]]}, {"id": "b", "kind": "arc", "center": [1, 1], "r": 2.5, "from_deg": 0, "to_deg": 90}]}})))
        self.assertEqual(normalized["scene"]["elements"][0]["points"], [["0", "0"], ["1.5", "2"], ["3", "0"]])
        self.assertEqual(normalized["scene"]["elements"][1]["r"], "2.5")

    def test_normalising_never_touches_what_is_not_a_spec(self):
        self.assertEqual(em.normalize("not a spec"), "not a spec")
        self.assertEqual(em.normalize({"scene": 3}), {"scene": 3})


class Target(unittest.TestCase):
    def test_an_explorer_for_another_question_than_the_toughest_is_refused_and_the_toughest_is_named(self):
        found = lines(run(lambda spec: spec["target"].update(question_ref="Q-OTHER")), "error")
        self.assertEqual(len(found), 1)
        for phrase in ("Q-OTHER", "Q8 (Q-PROJ-8)", "the most conceptual question first", "built for it"):
            self.assertIn(phrase, found[0])

    def test_with_no_toughest_concept_chosen_there_is_nothing_to_build_for(self):
        found = lines(run(brief=None), "error")
        self.assertTrue(any("not chosen" in line for line in found), found)

    def test_the_quantity_the_page_is_about_must_exist(self):
        found = lines(run(lambda spec: spec["target"].update(quantity="Rr")), "error")
        self.assertIn("TARGET target.quantity: 'Rr' is not one of the quantities", found)


class State(unittest.TestCase):
    def test_a_name_of_the_expression_language_and_a_name_used_twice_are_refused(self):
        def change(spec):
            spec["parameters"][0]["id"] = "min"
            spec["quantities"][1]["id"] = "vx"
        found = lines(run(change), "error")
        self.assertTrue(any("'min' is a word of the expression language" in line for line in found), found)
        self.assertTrue(any("'vx' is used twice" in line for line in found), found)

    def test_a_slider_has_a_whole_number_of_steps_and_a_value_on_it(self):
        def change(spec):
            spec["parameters"][2].update(max=85.5, value=30.5)
        found = lines(run(change), "error")
        self.assertTrue(any("not a whole number of steps" in line for line in found), found)
        self.assertTrue(any("must be a position of the slider" in line for line in found), found)

    def test_a_number_that_is_not_one_at_a_position_the_learner_can_reach_is_an_error_naming_the_position(self):
        found = lines(run(lambda spec: spec["quantities"].append({"id": "bad", "label": "bad", "expr": "1/(theta-30)"})), "error")
        self.assertEqual(len(found), 1)
        self.assertIn("QUANTITIES bad: is not a number when theta = 30", found[0])
        self.assertIn("guard it with if()", found[0])

    def test_there_is_no_implicit_multiplication_and_the_message_says_what_to_write(self):
        found = lines(run(lambda spec: spec["quantities"][0].update(expr="v cosd(theta)")), "error")
        self.assertTrue(any("write 2*a*b" in line for line in found), found)

    def test_a_quantity_cannot_read_the_whole_model(self):
        found = lines(run(lambda spec: spec["quantities"][0].update(expr="maxover(R, theta)")), "error")
        self.assertTrue(any("not in a quantity or in the geometry of a scene" in line for line in found), found)

    def test_a_quantity_reads_only_what_comes_before_it(self):
        found = lines(run(lambda spec: spec["quantities"][0].update(expr="vy*2")), "error")
        self.assertTrue(any("'vy' is not a parameter or an earlier quantity" in line for line in found), found)

    def test_the_depth_asked_for_is_the_blueprints_not_the_checks(self):
        bp = copy.deepcopy(em.blueprint())
        quantities = next(c for c in bp["components"] if c["id"] == "QUANTITIES")
        quantities.update(min_items=8, target_items=9)
        report = em.check(copy.deepcopy(BASE), BRIEF, bp)
        self.assertEqual(lines(report, "gap"), ["QUANTITIES quantities: 7 quantities; the blueprint's reference page has 9 (and 8 is the fewest that counts)"])


class Scene(unittest.TestCase):
    def test_an_element_that_leaves_the_picture_is_an_error_naming_the_element_the_position_and_the_side(self):
        found = lines(run(lambda spec: spec["scene"].update(world={"x": [-2, 30], "y": [-1.5, 21.5]})), "error")
        self.assertTrue(any(line.startswith("SCENE element landing: reaches (") and "right of the picture" in line and "when theta = " in line for line in found), found)
        self.assertTrue(any("widen scene.world" in line for line in found))

    def test_a_picture_that_is_too_tall_or_too_flat_is_an_error(self):
        found = lines(run(lambda spec: spec["scene"].update(world={"x": [-2, 44], "y": [-1.5, 80]})), "error")
        self.assertTrue(any("keep the ratio between" in line for line in found), found)

    def test_ids_are_unique_and_each_kind_has_its_own_fields(self):
        def change(spec):
            spec["scene"]["elements"].append({"id": "ground", "kind": "segment", "from": ["0", "0"]})
            spec["scene"]["elements"].append({"id": "word", "kind": "text", "at": ["1", "1"], "text": "x", "label": "y"})
        found = lines(run(change), "error")
        self.assertTrue(any("the id 'ground' is used twice" in line for line in found), found)
        self.assertTrue(any("a segment needs 'to'" in line for line in found), found)
        self.assertTrue(any("a text element is its own label" in line for line in found), found)

    def test_a_curve_cannot_use_the_name_of_a_parameter_for_its_own(self):
        def change(spec):
            next(e for e in spec["scene"]["elements"] if e["id"] == "path").update(param="theta")
        found = lines(run(change), "error")
        self.assertTrue(any("already a parameter or a quantity" in line for line in found), found)

    def test_a_label_may_only_show_a_number_the_model_has(self):
        def change(spec):
            next(e for e in spec["scene"]["elements"] if e["id"] == "landing").update(label="lands {Rr:1} m")
        found = lines(run(change), "error")
        self.assertTrue(any("{Rr} in 'lands {Rr:1} m' is not a parameter or a quantity" in line for line in found), found)

    def test_a_scene_with_nothing_on_show_at_the_start_is_an_error(self):
        def change(spec):
            for element in spec["scene"]["elements"]:
                element["reveal"] = "deconstruct" if element["id"] in {"velocity", "vxArrow", "vyArrow", "peak"} else "manipulate"
        found = lines(run(change), "error")
        self.assertTrue(any("nothing is on show at the start" in line for line in found), found)

    def test_the_oracles_tie_the_picture_to_the_numbers_and_a_broken_picture_is_found(self):
        def change(spec):
            next(e for e in spec["scene"]["elements"] if e["id"] == "landing").update(at=["R*1.1", "0"])
        found = lines(run(change), "error")
        self.assertTrue(any("the picture disagrees with the quantities" in line and "landing_x" in line for line in found), found)

    def test_an_oracle_that_does_not_read_the_picture_is_a_gap(self):
        def change(spec):
            spec["oracles"].append({"text": "R is R", "left": "vx*T", "right": "R"})
        found = lines(run(change), "gap")
        self.assertTrue(any("does not read any element of the scene" in line for line in found), found)


class SecondView(unittest.TestCase):
    def test_the_graph_runs_along_a_slider_and_shows_quantities_that_exist(self):
        def change(spec):
            spec["second_view"]["x"] = "v"
            spec["second_view"]["series"][0]["quantity"] = "Rr"
        found = lines(run(change), "error")
        self.assertTrue(any("must be a parameter the learner can move" in line for line in found), found)
        self.assertTrue(any("'Rr' is not one of the quantities" in line for line in found), found)

    def test_a_graph_that_leaves_out_the_quantity_the_page_is_about_is_a_gap(self):
        def change(spec):
            spec["second_view"]["series"][0]["quantity"] = "H"
        self.assertTrue(any("does not show the quantity the page is about" in line for line in lines(run(change), "gap")))

    def test_the_tempting_model_is_drawn_on_the_graph(self):
        def change(spec):
            del spec["second_view"]["ghost"]
        found = lines(run(change), "gap")
        self.assertTrue(any("does not draw the tempting model 'Rtempt'" in line for line in found), found)

    def test_the_range_of_the_graph_is_the_whole_range_of_what_it_can_show(self):
        compiled = em.compile_page_model(copy.deepcopy(BASE))
        low, high = compiled["y_range"]
        self.assertEqual(low, 0.0)
        self.assertGreater(high, 40.0, "the most any angle can give is 40 m, and the range is drawn above it")
        self.assertLess(high, 50.0)


class Predict(unittest.TestCase):
    def test_the_right_option_is_the_one_the_tests_show_and_a_wrong_index_is_an_error(self):
        found = lines(run(lambda spec: spec["predict"].update(correct=0)), "error")
        self.assertIn("PREDICT predict.correct: says option 0 is right, but the tests show it is option 1", found)

    def test_two_true_options_and_none_are_both_errors(self):
        def two(spec):
            spec["predict"]["options"][0]["tests"][0]["holds"] = "1"
        def none(spec):
            spec["predict"]["options"][1]["tests"][0]["holds"] = "0"
        self.assertTrue(any("exactly one option should be true" in line and "2 are" in line for line in lines(run(two), "error")))
        self.assertTrue(any("exactly one option should be true" in line and "0 are" in line for line in lines(run(none), "error")))

    def test_a_test_may_only_set_parameters_inside_their_range(self):
        def change(spec):
            spec["predict"]["options"][0]["tests"][0]["set"] = {"theta": 120, "R": 1}
        found = lines(run(change), "error")
        self.assertTrue(any("theta = 120 is outside the slider's range 5 to 85" in line for line in found), found)
        self.assertTrue(any("'R' is not a parameter" in line for line in found), found)

    def test_what_a_failing_test_says_may_only_show_numbers_the_model_has(self):
        def change(spec):
            spec["predict"]["options"][0]["tests"][0]["says"] = "it lands {Q:1} m away"
        found = lines(run(change), "error")
        self.assertTrue(any("{Q} in" in line for line in found), found)

    def test_fewer_options_than_the_reference_is_a_gap(self):
        def change(spec):
            del spec["predict"]["options"][2]
        found = lines(run(change), "gap")
        self.assertTrue(any(line.startswith("PREDICT predict.options: 2 options; the blueprint's reference page has 3") for line in found), found)


class Goals(unittest.TestCase):
    def test_a_goal_nobody_can_reach_is_an_error(self):
        found = lines(run(lambda spec: spec["manipulate"]["goals"][0].update(goal="R > 50")), "error")
        self.assertTrue(any("not true at any state the sliders can reach" in line for line in found), found)

    def test_a_goal_already_met_at_the_start_is_an_error(self):
        found = lines(run(lambda spec: spec["manipulate"]["goals"][0].update(goal="R > 10")), "error")
        self.assertTrue(any("already true at the starting state" in line for line in found), found)

    def test_a_goal_that_asks_for_a_slider_position_the_steps_skip_is_unreachable(self):
        found = lines(run(lambda spec: spec["manipulate"]["goals"][0].update(goal="theta == 45.5")), "error")
        self.assertTrue(any("not true at any state the sliders can reach" in line for line in found), found)


class Observe(unittest.TestCase):
    def test_the_declared_truth_is_checked_against_every_state_and_a_counterexample_is_named(self):
        found = lines(run(lambda spec: spec["observe"]["statements"][1].update(claim="argmax(R, theta) == 44", truth="always")), "error")
        self.assertTrue(any("is 'never' over the states the sliders can reach" in line for line in found), found)
        found = lines(run(lambda spec: spec["observe"]["statements"][0].update(truth="always")), "error")
        self.assertTrue(any("is 'sometimes'" in line and "it fails when theta = " in line for line in found), found)

    def test_a_statement_that_is_not_a_number_somewhere_is_an_error(self):
        found = lines(run(lambda spec: spec["observe"]["statements"][0].update(claim="1/(theta-30)")), "error")
        self.assertTrue(any("not a number when theta = 30" in line for line in found), found)

    def test_all_true_and_none_true_are_gaps(self):
        def all_true(spec):
            spec["observe"]["statements"][0].update(claim="1", truth="always")
            spec["observe"]["statements"][3].update(claim="1", truth="always")
        def none_true(spec):
            spec["observe"]["statements"][1].update(claim="0", truth="never")
            spec["observe"]["statements"][2].update(claim="0", truth="never")
        self.assertTrue(any("every statement is true" in line for line in lines(run(all_true), "gap")))
        self.assertTrue(any("no statement is a general truth" in line for line in lines(run(none_true), "gap")))


class Contradict(unittest.TestCase):
    def test_a_tempting_model_that_agrees_with_the_truth_everywhere_is_not_wrong(self):
        def change(spec):
            spec["quantities"][5]["expr"] = "v^2*sind(2*theta)/g"
            spec["contradict"]["goal"]["goal"] = "theta > 40 and theta < 50"
        found = lines(run(change), "error")
        self.assertTrue(any("agrees with 'R' at every state, so it is not wrong" in line for line in found), found)

    def test_the_tempting_model_must_not_be_the_truth_itself(self):
        found = lines(run(lambda spec: spec["contradict"]["wrong_model"].update(quantity="R")), "error")
        self.assertIn("CONTRADICT contradict.wrong_model.quantity: the tempting model is the true quantity itself", found)

    def test_nothing_that_shows_the_tempting_model_is_a_gap(self):
        def change(spec):
            del spec["second_view"]["ghost"]
            spec["scene"]["elements"] = [e for e in spec["scene"]["elements"] if e["id"] != "tempt"]
        found = lines(run(change), "gap")
        self.assertTrue(any("no contradiction to see" in line for line in found), found)


class Deconstruct(unittest.TestCase):
    def test_each_hidden_element_is_revealed_by_exactly_one_step(self):
        def change(spec):
            spec["deconstruct"]["steps"][1]["reveals"] = ["vxArrow", "ground", "velocity", "nothing"]
        found = lines(run(change), "error")
        self.assertTrue(any("'ground' does not have reveal: 'deconstruct'" in line for line in found), found)
        self.assertTrue(any("'velocity' is revealed twice" in line for line in found), found)
        self.assertTrue(any("'nothing' is not an element of the scene" in line for line in found), found)

    def test_an_element_no_step_reveals_would_never_be_seen(self):
        def change(spec):
            spec["deconstruct"]["steps"][2]["reveals"] = ["vyArrow"]
        found = lines(run(change), "error")
        self.assertTrue(any("'peak' has reveal: 'deconstruct' but no step reveals it" in line for line in found), found)

    def test_a_question_asks_about_an_option_that_exists(self):
        def change(spec):
            spec["deconstruct"]["steps"][2]["ask"]["correct"] = 3
        self.assertTrue(any("there is no option 3" in line for line in lines(run(change), "error")))


class Reconstruct(unittest.TestCase):
    def test_an_equation_that_is_not_the_quantity_is_an_error_with_the_state_where_they_differ(self):
        found = lines(run(lambda spec: spec["reconstruct"]["equation"].update(expr="v^2*sind(theta)/g")), "error")
        self.assertEqual(len(found), 1)
        self.assertIn("is not equal to 'R'", found[0])
        self.assertIn("when theta = ", found[0])

    def test_the_equation_is_written_with_the_parameters_only_so_it_is_the_closed_form_of_the_steps(self):
        found = lines(run(lambda spec: spec["reconstruct"]["equation"].update(expr="vx*T")), "error")
        self.assertEqual(len(found), 1)
        self.assertIn("uses T, vx, which are steps of the working", found[0])
        self.assertIn("with the parameters only (v, g, theta)", found[0])

    def test_a_target_quantity_that_is_already_the_closed_form_leaves_nothing_to_compress(self):
        def change(spec):
            spec["quantities"][3]["expr"] = "v^2*sind(2*theta)/g"
        found = lines(run(change), "error")
        self.assertTrue(any("is the same expression as the quantity 'R', so nothing was compressed" in line for line in found), found)

    def test_a_step_names_a_quantity_the_mechanism_shows(self):
        found = lines(run(lambda spec: spec["reconstruct"]["steps"][0].update(quantity="vz")), "error")
        self.assertTrue(any("'vz' is not one of the quantities" in line for line in found), found)


class Invariants(unittest.TestCase):
    def test_an_invariant_that_breaks_somewhere_is_an_error_naming_where(self):
        found = lines(run(lambda spec: spec["invariants"][0].update(rhs="at(R, theta, 80 - theta)")), "error")
        self.assertTrue(any("is not an invariant" in line and "when theta = " in line for line in found), found)

    def test_an_inequality_that_is_met_up_to_rounding_holds_and_one_that_is_not_does_not(self):
        self.assertEqual(lines(run(lambda spec: spec["invariants"][1].update(rhs="Rmax")), "error"), [])
        found = lines(run(lambda spec: spec["invariants"][1].update(rhs="Rmax*0.9")), "error")
        self.assertTrue(any("is not an invariant" in line for line in found), found)

    def test_both_sides_the_same_says_nothing(self):
        found = lines(run(lambda spec: spec["invariants"][0].update(rhs="R")), "error")
        self.assertTrue(any("both sides are the same expression" in line for line in found), found)


class Boundary(unittest.TestCase):
    def test_what_the_case_expects_is_checked_against_the_model(self):
        found = lines(run(lambda spec: spec["boundary"]["cases"][1].update(expect="holds")), "error")
        self.assertTrue(any("says the shortcut holds" in line and "so it fails" in line for line in found), found)

    def test_a_boundary_with_only_one_outcome_is_a_gap(self):
        def change(spec):
            spec["boundary"]["cases"] = spec["boundary"]["cases"][1:]
        found = lines(run(change), "gap")
        self.assertTrue(any("no case where the shortcut holds" in line for line in found), found)

    def test_a_case_sets_parameters_inside_their_range(self):
        found = lines(run(lambda spec: spec["boundary"]["cases"][0].update(set={"theta": 200})), "error")
        self.assertTrue(any("outside the slider's range" in line for line in found), found)


class Tasks(unittest.TestCase):
    def test_a_transfer_task_with_the_starting_numbers_is_not_fresh(self):
        found = lines(run(lambda spec: spec["transfer"][0].update(set={"theta": 30})), "error")
        self.assertTrue(any("not a fresh task" in line for line in found), found)

    def test_a_transfer_task_may_use_numbers_outside_the_sliders_but_a_fade_task_may_not(self):
        self.assertEqual(lines(run(lambda spec: spec["transfer"][0].update(set={"theta": 120})), "error"), [])
        found = lines(run(lambda spec: spec["fade"][0].update(set={"theta": 120})), "error")
        self.assertTrue(any("outside the slider's range" in line for line in found), found)

    def test_an_answer_must_be_a_number_at_its_state(self):
        found = lines(run(lambda spec: spec["transfer"][0].update(answer="1/(theta-20)")), "error")
        self.assertTrue(any("is not a number when theta = 20" in line for line in found), found)

    def test_the_text_of_a_task_may_show_the_answer_and_the_model_numbers_and_nothing_else(self):
        self.assertEqual(lines(run(lambda spec: spec["fade"][1].update(why="It is {answer:0} degrees.")), "error"), [])
        found = lines(run(lambda spec: spec["fade"][1].update(why="It is {nope:0} degrees.")), "error")
        self.assertTrue(any("{nope}" in line for line in found), found)

    def test_fewer_than_three_levels_or_one_set_of_numbers_throughout_are_gaps(self):
        found = lines(run(lambda spec: spec["fade"].pop()), "gap")
        self.assertTrue(any("2 level(s); the ladder has three" in line for line in found), found)
        def same(spec):
            for task in spec["transfer"]:
                task["set"] = {"v": 15, "theta": 20}
        self.assertTrue(any("every task uses the same numbers" in line for line in lines(run(same), "gap")))


class Prose(unittest.TestCase):
    def test_a_sentence_too_short_to_teach_is_a_gap(self):
        found = lines(run(lambda spec: spec["context"].update(situation="A ball.")), "gap")
        self.assertTrue(any("too short to teach anything" in line for line in found), found)

    def test_a_decimal_typed_into_a_sentence_is_a_number_nothing_checks(self):
        found = lines(run(lambda spec: spec["contradict"].update(why_wrong="At 30 degrees the true range is 34.6 m, which the tempting model misses.")), "gap")
        self.assertTrue(any("types the number 34.6 itself" in line and "{quantity:decimals}" in line for line in found), found)

    def test_a_decimal_that_is_a_given_of_the_question_is_fine_and_so_is_one_the_page_computes(self):
        def change(spec):
            spec["transfer"][0]["set"] = {"v": 15, "theta": 20, "g": 9.8}
            spec["transfer"][0]["prompt"] = "A ball is launched at 15 m/s, 20° above level ground (g = 9.8 m/s²). How far does it land?"
            spec["contradict"]["why_wrong"] = "It forgets the horizontal speed, which is {vx:2} m/s at this angle, so it ignores most of the distance."
        self.assertEqual(lines(run(change)), [])


class Lattice(unittest.TestCase):
    def setUp(self):
        self.model = em.Model(copy.deepcopy(BASE))

    def test_the_sliders_positions_are_min_plus_whole_steps_and_a_fixed_parameter_has_one(self):
        self.assertEqual(self.model.lattice("theta")[:3], [5.0, 6.0, 7.0])
        self.assertEqual(self.model.lattice("theta")[-1], 85.0)
        self.assertEqual(self.model.lattice("v"), [20.0])

    def test_a_thinned_lattice_keeps_both_ends_and_the_starting_value(self):
        thin = self.model.lattice("theta", 7)
        self.assertEqual((thin[0], thin[-1]), (5.0, 85.0))
        self.assertIn(30.0, thin)
        self.assertLessEqual(len(thin), 8)
        self.assertEqual(thin, sorted(thin))

    def test_the_states_begin_with_the_starting_state_and_never_exceed_the_cap(self):
        states = list(self.model.states(20))
        self.assertEqual(states[0], self.model.initial())
        self.assertLessEqual(len(states), 21)
        self.assertEqual(len({tuple(sorted(s.items())) for s in states}), len(states), "no state is visited twice")

    def test_with_two_sliders_each_is_thinned_so_the_product_stays_inside_the_cap(self):
        spec = copy.deepcopy(BASE)
        spec["parameters"][0] = {"id": "v", "label": "launch speed", "unit": "m/s", "min": 5, "max": 45, "step": 0.5, "value": 20}
        model = em.Model(spec)
        states = list(model.states(3000))
        self.assertLessEqual(len(states), 3001)
        self.assertGreater(len(states), 1000)
        self.assertEqual(states[0], model.initial())
        self.assertTrue(any(s["v"] == 45 for s in states) and any(s["theta"] == 85 for s in states))


class ModelForms(unittest.TestCase):
    def setUp(self):
        self.model = em.Model(copy.deepcopy(BASE))
        self.state = self.model.initial()

    def test_at_reads_the_model_with_a_slider_set(self):
        self.assertAlmostEqual(self.model.evaluate("at(R, theta, 45)", self.state), 40.0)
        self.assertAlmostEqual(self.model.evaluate("at(R, theta, 30) - R", self.state), 0.0)

    def test_the_sweep_forms_find_the_peak_of_the_range(self):
        self.assertEqual(self.model.evaluate("argmax(R, theta)", self.state), 45)
        self.assertAlmostEqual(self.model.evaluate("maxover(R, theta)", self.state), 40.0)
        self.assertAlmostEqual(self.model.evaluate("minover(R, theta)", self.state), 40 * math.sin(math.radians(10)), places=6)

    def test_the_whole_env_has_the_scenes_numbers(self):
        env = self.model.values(self.state)
        self.assertAlmostEqual(env["landing_x"], env["R"])
        self.assertAlmostEqual(env["peak_y"], env["H"])
        self.assertAlmostEqual(env["velocity_x2"], env["vx"] / 2)


class Compiled(unittest.TestCase):
    def test_the_page_is_given_the_sliders_the_steps_in_order_and_the_scene_by_name(self):
        compiled = em.compile_page_model(copy.deepcopy(BASE))
        self.assertEqual([p["id"] for p in compiled["parameters"]], ["v", "g", "theta"])
        self.assertEqual(compiled["parameters"][2]["decimals"], 0)
        names = [name for name, _ in compiled["steps"]]
        self.assertLess(names.index("vx"), names.index("T"))
        self.assertLess(names.index("R"), names.index("landing_x"))
        self.assertEqual(compiled["view_box"], [440, 220])
        landing = next(e for e in compiled["elements"] if e["id"] == "landing")
        self.assertEqual((landing["kind"], landing["reveal"], landing["vars"]), ("point", "manipulate", ["landing_x", "landing_y"]))
        curve = next(e for e in compiled["elements"] if e["id"] == "path")
        self.assertEqual(curve["curve"]["param"], "t")
        self.assertEqual(curve["curve"]["steps"], 60)


if __name__ == "__main__":
    unittest.main()
