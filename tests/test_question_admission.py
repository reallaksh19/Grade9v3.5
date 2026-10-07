"""A question record asks a question, says something about it, and can be started before the first hint (component_policy.admission)."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from Shared.library import intake, question_admission as qa
from Shared.library.question_admission import findings
from Shared.tools import web_blueprint_contract as contract

REPO = Path(__file__).resolve().parents[1]

GOOD = {"id": "Q-1", "stem": "A block of mass 2 kg is pulled across a rough table by a 12 N force. Find its acceleration.",
        "options": [], "conditions": ["g = 10 m/s^2"],
        "answer": {"kind": "MODEL_RESPONSE", "verification_status": "CHECKED_BY_AUTHOR",
                   "summary": "a = 6 m/s^2 for the 2 kg block pulled by the 12 N force.",
                   "reasoning": ["The block is the system and the 12 N force is the only horizontal force on it (the table is smooth for this part).",
                                 "F = m a gives a = 12 N / 2 kg = 6 m/s^2."]},
        "hints": [{"text": "Which forces act along the table?", "reveals": "CONCEPT"}]}


def package(package_id: str = "phy-test", **question) -> dict:
    row = json.loads(json.dumps(GOOD))
    for key, value in question.items():
        if isinstance(value, dict) and isinstance(row.get(key), dict):
            row[key].update(value)
        else:
            row[key] = value
    return {"package_id": package_id, "questions": [row]}


class Points(unittest.TestCase):
    def points(self, **question):
        return {(f["point"], f["severity"]) for f in findings(package(**question))}

    def test_a_good_record_has_no_finding(self):
        self.assertEqual(self.points(), set())

    def test_a_stem_that_asks_nothing_is_refused(self):
        self.assertIn(("QUESTION_STEM", "BLOCK"), self.points(stem="Compare squared speeds"))

    def test_a_short_mcq_source_lead_in_may_be_completed_by_its_options(self):
        points = self.points(
            stem="Every rational number is",
            options=[
                "(A) a natural number",
                "(B) a whole number",
                "(C) a real number",
                "(D) an integer",
            ],
        )
        self.assertNotIn(("QUESTION_STEM", "BLOCK"), points)
        self.assertNotIn(("QUESTION_STEM_COMPLETE", "ADVISE"), points)

    def test_a_short_stem_without_visible_completion_is_still_refused(self):
        self.assertIn(("QUESTION_STEM", "BLOCK"), self.points(stem="Every rational number is", options=[]))

    def test_conditions_do_not_pad_a_short_non_question_past_the_stem_floor(self):
        self.assertIn(
            ("QUESTION_STEM", "BLOCK"),
            self.points(stem="Compare squared speeds", options=[], conditions=["Take g = 10 m/s^2."]),
        )

    def test_a_stem_made_of_the_records_own_hints_is_refused(self):
        """Q-PHY-KIN-2D-SRC-40 of pull request 375: the stem is the sentences of the solution."""
        hint = "Velocity direction comes from the ratio of the components. Minimum projectile speed occurs at the apex."
        stem = hint + " Compare squared speeds at apex and at half maximum height."
        self.assertIn(("QUESTION_STEM", "BLOCK"), self.points(stem=stem, hints=[{"text": hint, "reveals": "METHOD"}]))
        self.assertIn(("QUESTION_STEM", "BLOCK"), self.points(stem=stem, answer={"reasoning": [hint, "Then compare."]}))

    def test_a_stem_cut_off_mid_sentence_is_said(self):
        cut = self.points(stem="A block of mass 2 kg is pulled across a rough table by a 12 N force. Find its")
        self.assertEqual(cut & {("QUESTION_STEM_COMPLETE", "ADVISE")}, {("QUESTION_STEM_COMPLETE", "ADVISE")})
        for ends in ("Find its acceleration.", "Is the block in equilibrium?", "Solve and check your result: 3x = 2x + 18", "Find the value of x for which 3x - 4 and 2x + 1 become equal is",
                     "Find the current in the 4 ohm resistor (use V = I R)"):
            stem = f"A block of mass 2 kg is pulled across a rough table by a 12 N force. {ends}"
            self.assertNotIn(("QUESTION_STEM_COMPLETE", "ADVISE"), self.points(stem=stem), ends)

    def test_options_that_are_their_letters_are_refused(self):
        self.assertIn(("QUESTION_OPTIONS", "BLOCK"), self.points(options=["(A) A", "(B) B", "(C) C", "(D) D"]))
        self.assertNotIn(("QUESTION_OPTIONS", "BLOCK"), self.points(options=["(A) 6 m/s^2", "(B) 4 m/s^2"]))
        self.assertIn(("QUESTION_OPTIONS", "BLOCK"), self.points(options=["A. 4", "B. 6", "C", "D. 8"]))

    def test_a_number_a_hint_relies_on_that_the_stem_does_not_give_is_said_not_held(self):
        hints = [{"text": "Use u = 24.5 m/s and 30 degrees.", "reveals": "METHOD"}]
        self.assertIn(("QUESTION_GIVENS", "ADVISE"), self.points(hints=hints))
        self.assertNotIn(("QUESTION_GIVENS", "ADVISE"), self.points(hints=[{"text": "The answer is 24.5.", "reveals": "ANSWER"}]))
        self.assertNotIn(("QUESTION_GIVENS", "ADVISE"), self.points(stem="A ball leaves at 24.5 m/s and 30 degrees; find its range. Take g = 9.8.", hints=hints))

    def test_an_answer_that_could_stand_under_any_question_is_refused(self):
        """The 244 records of pull request 375 said 'Apply 2D projectile kinematic decomposition.' under every question."""
        generic = {"summary": "Apply 2D projectile kinematic decomposition.", "reasoning": ["Follow step-by-step kinematics setup and verify dimensional units.", "Check the result."]}
        self.assertIn(("ANSWER_ANCHORED", "BLOCK"), self.points(answer=generic))
        self.assertNotIn(("ANSWER_ANCHORED", "BLOCK"), self.points())
        phrase_changed = {"summary": "Resolve the motion into components and be systematic about it.", "reasoning": ["Set up the axes first.", "Then solve each axis separately and recombine."]}
        self.assertIn(("ANSWER_ANCHORED", "BLOCK"), self.points(answer=phrase_changed), "a new phrase is still no answer: no phrase list is needed")

    def test_an_answer_is_worked(self):
        one_line = {"summary": "a = 6 m/s^2 for the 2 kg block.", "reasoning": ["F = m a gives a = 6 m/s^2 for the 2 kg block pulled by the 12 N force on it."]}
        self.assertIn(("ANSWER_WORKED", "BLOCK"), self.points(answer=one_line))
        self.assertIn(("ANSWER_WORKED", "BLOCK"), self.points(answer={"summary": "x" * 501}), "a page pasted in as the summary")
        self.assertNotIn(("ANSWER_WORKED", "BLOCK"), self.points())

    def test_a_key_nobody_ran_does_not_enter_a_library(self):
        for status in ("NOT_RUN", "DISPUTED"):
            self.assertIn(("ANSWER_VERIFIED", "BLOCK"), self.points(answer={"verification_status": status}))
        for status in ("CHECKED_BY_AUTHOR", "INDEPENDENTLY_CHECKED", None):
            answer = {"verification_status": status} if status else {}
            self.assertNotIn(("ANSWER_VERIFIED", "BLOCK"), self.points(answer=answer))

    def test_a_deferred_concept_is_refused_unless_the_record_is_routed_as_an_extension(self):
        """Q-PHY-KIN-2D-SRC-45 of pull request 375: angular momentum under a projectile capability. The capability tag was in scope; the question was not."""
        question = {"stem": "A projectile of mass 2 kg is launched at 20 m/s. Find its angular momentum about the launch point at the apex.",
                    "answer": {"summary": "L = 2 kg x 20 m/s x height about the launch point at the apex of the projectile.",
                               "reasoning": ["Use L = r x p about the launch point for the 2 kg projectile.", "At the apex the 20 m/s horizontal momentum acts at the height h."]}}
        self.assertIn(("QUESTION_SCOPE", "BLOCK"), self.points(**question))
        self.assertNotIn(("QUESTION_SCOPE", "BLOCK"), self.points(extensions={"grade9v3:scope_route": "DECLARED_EXTENSION"}, **question))
        self.assertEqual({f["point"] for f in findings(package("phy-rot-rigid-body", **question))} & {"QUESTION_SCOPE"}, set(), "the package that owns the concept may teach it")

    def test_a_concept_the_question_declares_in_its_specification_is_held_to_the_policy(self):
        """The typed way: problem_specification.concept_refs names the concepts. Every DEFER concept, by its own id, however the id is spelled."""
        for entry in qa.scope()["deferred"]:
            for spelling in (entry["concept"], "CONCEPT-" + entry["concept"].replace("_", "-"), entry["concept"].lower().replace("_", "-")):
                spec = {"problem_specification": {"concept_refs": [spelling]}}
                held = "BLOCK" if entry["document_row"] else "ADVISE"
                self.assertIn(("QUESTION_SCOPE", held), self.points(extensions=spec), f"{entry['concept']} as {spelling}")

    def test_a_question_that_excludes_a_deferred_concept_is_not_refused(self):
        """A Grade-9 question on a pulley says 'Do not invent a torque equation': it excludes the concept."""
        self.assertNotIn(("QUESTION_SCOPE", "BLOCK"), self.points(conditions=["Do not invent a torque or rotational-inertia equation."]))
        self.assertNotIn(("QUESTION_SCOPE", "BLOCK"), self.points(conditions=["Ignore torque; the pulley is ideal."]))
        self.assertIn(("QUESTION_SCOPE", "BLOCK"), self.points(conditions=["The pulley is not ideal. Include the torque on it."]))

    def test_intake_blocks_on_the_blocking_points_and_only_reports_the_others(self):
        report = intake.check(package(hints=[{"text": "Use 24.5 m/s.", "reveals": "METHOD"}]))
        self.assertEqual([a["point"] for a in report["advisories"]], ["QUESTION_GIVENS"])
        self.assertNotIn("QUESTION_GIVENS", {f["point"] for f in report["findings"]})
        blocked = intake.check(package(options=["(A) A", "(B) B"]))
        self.assertIn("QUESTION_OPTIONS", {f["point"] for f in blocked["findings"]})
        self.assertFalse(blocked["admitted"])


class Library(unittest.TestCase):
    PACKAGES = sorted((REPO / "Physics/library").glob("*.v1.json")) + sorted((REPO / "Mathematics/library").glob("*.v1.json"))

    def test_no_record_the_library_holds_is_refused_by_a_blocking_point(self):
        """The points were measured against pull request 375 and must not refuse what was authored before it."""
        refused = []
        for path in self.PACKAGES:
            for f in findings(json.loads(path.read_text(encoding="utf-8"))):
                if f["severity"] == "BLOCK":
                    refused.append(f"{path.name}: {f['detail']}")
        self.assertEqual(refused, [])

    def test_every_committed_library_is_admitted_by_intake(self):
        """The gate of record: the one that runs in CI over every committed library, not one a registration brings with it."""
        for path in self.PACKAGES:
            with self.subTest(package=path.name):
                report = intake.check(json.loads(path.read_text(encoding="utf-8")))
                self.assertEqual([f"{f['point']}: {f['detail']}" for f in report["findings"]][:3], [])


class Scope(unittest.TestCase):
    def test_a_deferred_entry_that_names_a_document_row_is_held_to_that_row(self):
        document = (REPO / qa.scope()["source"]).read_text(encoding="utf-8")
        named = [e for e in qa.scope()["deferred"] if e["document_row"]]
        self.assertTrue(named, "the scope policy names no document row: nothing holds it to the document")
        for entry in named:
            rows = [line for line in document.splitlines() if line.lstrip().startswith("|") and entry["document_row"] in line and "`DEFER`" in line]
            self.assertTrue(rows, f"{entry['document_row']!r} is not a DEFER row of {qa.scope()['source']}")

    def test_every_owner_is_a_package_that_exists(self):
        for entry in qa.scope()["deferred"]:
            for owner in entry["owners"]:
                self.assertTrue((REPO / "Physics/library" / f"{owner}.v1.json").exists(), owner)

    def test_every_waiver_route_is_one_the_document_names(self):
        document = (REPO / qa.scope()["source"]).read_text(encoding="utf-8")
        for route in qa.scope()["waiver_routes"]:
            self.assertIn(route, document)

    def test_the_policy_satisfies_its_schema(self):
        import jsonschema
        schema = json.loads((REPO / "Shared/policy/concept-policy.schema.json").read_text(encoding="utf-8"))
        policy = json.loads(qa.SCOPE_POLICY.read_text(encoding="utf-8"))
        self.assertEqual([e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(policy)], [])

    def test_every_deferred_concept_in_the_policy_is_refused_unless_routed(self):
        """Generated from the policy file, not from a list of its own: each DEFER or PROHIBITED concept, by each of its terms; blocking for a document row, said otherwise."""
        for entry in qa.scope()["deferred"]:
            for term in entry["terms"]:
                question = {"id": "Q-1", "stem": f"A block of mass 2 kg slides down a smooth ramp; find the {term} of the block about the foot of the ramp.",
                            "answer": {"summary": f"The {term} of the 2 kg block about the foot of the ramp is found from its speed and position.",
                                       "reasoning": [f"Define the {term} of the block about the foot of the ramp.", "Substitute the 2 kg mass and the speed from the ramp."]}}
                found = list(findings({"package_id": "phy-kin-2d-motion", "questions": [question]}))
                held = "BLOCK" if entry["document_row"] else "ADVISE"
                self.assertIn(("QUESTION_SCOPE", held), {(f["point"], f["severity"]) for f in found}, f"{entry['concept']}: {term}")
                routed = dict(question, extensions={"grade9v3:scope_route": entry and qa.scope()["waiver_routes"][0]})
                self.assertNotIn("QUESTION_SCOPE", {f["point"] for f in findings({"package_id": "phy-kin-2d-motion", "questions": [routed]})})
                for owner in entry["owners"]:
                    self.assertNotIn("QUESTION_SCOPE", {f["point"] for f in findings({"package_id": owner, "questions": [question]})})


class Registry(unittest.TestCase):
    def test_the_registry_and_the_module_name_the_same_points_with_the_same_severity(self):
        points = contract.load_registry()["component_policy"]["admission"]["points"]
        self.assertEqual({p["id"]: p["severity"] for p in points}, qa.BLOCKING)
        for authority in contract.load_registry()["component_policy"]["admission"]["authority"]:
            self.assertTrue((REPO / authority).exists(), authority)

    def test_the_thresholds_are_the_ones_the_registry_states(self):
        statements = " ".join(p["statement"] for p in contract.load_registry()["component_policy"]["admission"]["points"])
        for number in (qa.STEM_MIN_WORDS, qa.ANCHORS_MIN, qa.WORKED_MIN_STEPS, qa.WORKED_MIN_CHARS, qa.SUMMARY_MAX_CHARS):
            self.assertRegex(statements, rf"\b{number}\b", f"the threshold {number} is in the code and not in the statement of the rule")


if __name__ == "__main__":
    unittest.main()
