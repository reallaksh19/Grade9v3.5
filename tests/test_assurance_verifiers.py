"""The verifiers run the checks of the blueprint and of the library in the vocabulary of the assurance chain, and a defect of each kind fails the type it belongs to.

The last class is the architecture's acceptance test: for each defect class that the validation of pull request 375 found, a package or a page with that one defect goes
verifiers -> evidence -> bundle -> eligibility, and the product is not eligible; the same package without it is.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Shared.assurance import aggregate, baseline, contract, typed, verifiers
from Shared.assurance.evidence import load_evidence
from Shared.tools import assurance_run

REPO = Path(__file__).resolve().parents[1]
LIB = "Physics/library"
TARGET = "phy-nlm-first-law.v1.json"
GENERIC = {"kind": "MODEL_RESPONSE", "summary": "Apply 2D projectile kinematic decomposition.", "verification_status": "CHECKED_BY_AUTHOR",
           "reasoning": ["Follow step-by-step kinematics setup and verify dimensional units.", "Check the result."], "check": "Check dimensions and physical boundary conditions.",
           "acceptable_alternatives": [], "subpart_answers": []}

_BASE: Path | None = None


def setUpModule():
    global _BASE
    _BASE = Path(tempfile.mkdtemp())
    shutil.copytree(REPO / LIB, _BASE / LIB, ignore=shutil.ignore_patterns("exam-bank"))


def tearDownModule():
    shutil.rmtree(_BASE, ignore_errors=True)


class Repo(unittest.TestCase):
    """A copy of the Physics library in a temporary repository, a package of which a test may spoil."""

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.repo, True)
        shutil.copytree(_BASE / LIB, self.repo / LIB)
        (self.repo / "standalone").mkdir()

    def edit(self, fn, name=TARGET):
        path = self.repo / LIB / name
        package = json.loads(path.read_text(encoding="utf-8"))
        fn(package)
        path.write_text(json.dumps(package), encoding="utf-8")

    def subjects(self):
        return aggregate.package_subjects([LIB], self.repo)

    def verdicts(self):
        """Every package's verdicts by assurance type, as {type: {package id: outcome}}, with the references checked across the whole library."""
        subjects = self.subjects()
        references = verifiers.verify_references(subjects, self.repo)
        out: dict[str, dict[str, str]] = {}
        findings: dict[tuple[str, str], list[str]] = {}
        for s in subjects:
            per_type = verifiers.verify_package(s, self.repo)
            per_type["REFERENCE_INTEGRITY"] = references[s.key]
            for t, v in per_type.items():
                out.setdefault(t, {})[s.id] = v.outcome
                findings[(t, s.id)] = [f["code"] for f in v.findings]
        self.found = findings
        return out

    def target_id(self):
        return json.loads((self.repo / LIB / TARGET).read_text(encoding="utf-8"))["package_id"]


def first_question(package):
    return package["questions"][0]


class Defects(Repo):
    def assert_fails(self, assurance_type, code=None):
        out = self.verdicts()
        target = self.target_id()
        self.assertEqual(out[assurance_type][target], "FAIL", f"{assurance_type}: {out[assurance_type][target]}")
        if code:
            self.assertIn(code, self.found[(assurance_type, target)])

    def test_the_library_as_committed_has_no_failing_evidence_in_physics(self):
        out = self.verdicts()
        self.assertEqual({t: [p for p, o in per.items() if o == "FAIL"] for t, per in out.items()}, {t: [] for t in out})

    def test_a_boilerplate_answer_fails_corpus_specificity(self):
        """The 244 records of pull request 375: the same answer under every question."""
        self.edit(lambda p: first_question(p).update(answer=dict(GENERIC)))
        self.assert_fails("CORPUS_SPECIFICITY", "ANSWER_ANCHORED")

    def test_the_same_answer_text_on_many_records_fails_corpus_specificity(self):
        def spoil(p):
            for q in p["questions"][:4]:
                q["answer"]["check"] = "Check dimensions and physical boundary conditions."
        self.edit(spoil)
        self.assert_fails("CORPUS_SPECIFICITY", "DUPLICATED")

    def test_options_that_are_their_letters_fail_structural_validity(self):
        self.edit(lambda p: first_question(p).update(options=["(A) A", "(B) B", "(C) C", "(D) D"]))
        self.assert_fails("STRUCTURAL_VALIDITY", "QUESTION_OPTIONS")

    def test_a_stem_that_asks_nothing_fails_structural_validity(self):
        self.edit(lambda p: first_question(p).update(stem="Compare squared speeds"))
        self.assert_fails("STRUCTURAL_VALIDITY", "QUESTION_STEM")

    def test_a_deferred_concept_fails_scope_conformance(self):
        def spoil(p):
            q = first_question(p)
            q["stem"] = "A puck of mass 0.2 kg slides at 4 m/s on smooth ice. Find its angular momentum about the stick."
            q["answer"]["summary"] = "The angular momentum of the 0.2 kg puck at 4 m/s about the stick is its mass times speed times distance."
            q["answer"]["reasoning"] = ["Use the angular momentum of the 0.2 kg puck about the stick.", "Multiply the 0.2 kg mass, the 4 m/s speed and the distance."]
        self.edit(spoil)
        self.assert_fails("SCOPE_CONFORMANCE", "QUESTION_SCOPE")

    def test_a_key_nobody_ran_fails_reasoning_validity(self):
        self.edit(lambda p: first_question(p)["answer"].update(verification_status="NOT_RUN"))
        self.assert_fails("REASONING_VALIDITY", "ANSWER_VERIFIED")

    def test_an_unresolved_reference_fails_reference_integrity(self):
        self.edit(lambda p: p["capabilities"][0].update(prerequisite_refs=["CAP-DOES-NOT-EXIST"]))
        self.assert_fails("REFERENCE_INTEGRITY", "LIBRARY_UNRESOLVED_REFERENCE")

    def test_a_package_that_does_not_parse_fails_structural_validity_and_runs_nothing_else(self):
        (self.repo / LIB / TARGET).write_text("{ not json", encoding="utf-8")
        out = verifiers.verify_package(next(s for s in self.subjects() if s.path.endswith(TARGET)), self.repo)
        self.assertEqual(out["STRUCTURAL_VALIDITY"].outcome, "FAIL")
        self.assertEqual({o.outcome for t, o in out.items() if t != "STRUCTURAL_VALIDITY"}, {"NOT_RUN"}, "a check that could not run has not passed")

    def test_a_package_that_breaks_its_schema_fails_structural_validity(self):
        self.edit(lambda p: p.pop("scope_summary", None) or p.update(status="DRAFT-ISH"))
        self.assert_fails("STRUCTURAL_VALIDITY")

    def test_a_package_that_declares_no_specification_is_inconclusive_for_self_containment_not_a_pass(self):
        out = self.verdicts()
        self.assertEqual(out["SELF_CONTAINMENT"][self.target_id()], "INCONCLUSIVE")
        self.assertEqual(out["REASONING_VALIDITY"][self.target_id()], "INCONCLUSIVE", "keys checked by their author only")


SPEC = {"problem_specification": {"requested_outputs": [{"id": "R", "quantity_kind": "LENGTH"}], "visible_facts": [{"symbol": "u", "value": 20, "unit": "m/s"}, {"symbol": "theta", "value": 30, "unit": "deg"}],
                                  "declared_assumptions": [], "permitted_constants": [{"symbol": "g", "value": 10, "unit": "m/s^2"}]},
        "answer_contract": {"answer_type": "NUMERIC", "requested_outputs": ["R"], "equivalence_policy": "NUMERIC_UNIT_EQUIVALENCE", "expected_dimension": "LENGTH", "tolerance": {"relative": 0.01}},
        "computation_model": {"model_type": "PROJECTILE_NO_DRAG", "variables": {"u": {"value": 20}, "theta": {"value": 30}, "g": {"value": 10}}, "requested_outputs": ["R"]}}


def typed_question(stem="A ball is launched at 20 m/s at 30 degrees. Find its range. Take g = 10 m/s^2.", value=34.641, unit="m", **spec_changes):
    ext = json.loads(json.dumps(SPEC))
    for k, v in spec_changes.items():
        ext[k] = v
    return {"id": "Q-T-1", "stem": stem, "answer": {"numeric": {"value": value, "unit": unit}}, "extensions": ext}


class TypedChecks(unittest.TestCase):
    def test_a_question_that_declares_nothing_is_inconclusive_never_a_pass(self):
        self.assertEqual(typed.self_containment({"id": "q", "stem": "x"})[0], "INCONCLUSIVE")
        self.assertEqual(typed.answer_correctness({"id": "q"})[0], "NOT_APPLICABLE")

    def test_a_complete_specification_passes(self):
        q = typed_question()
        self.assertEqual((typed.self_containment(q)[0], typed.answer_correctness(q)[0], typed.dimensional_correctness(q)[0]), ("PASS", "PASS", "PASS"))

    def test_a_given_that_the_computation_needs_and_the_specification_does_not_declare_is_hidden(self):
        ext = json.loads(json.dumps(SPEC["problem_specification"]))
        ext["permitted_constants"] = []
        outcome, problems = typed.self_containment(typed_question(problem_specification=ext))
        self.assertEqual((outcome, [p["code"] for p in problems]), ("FAIL", ["HIDDEN_GIVEN"]))

    def test_a_visible_fact_that_is_not_in_the_text_is_not_visible(self):
        outcome, problems = typed.self_containment(typed_question(stem="A ball is launched at 30 degrees. Find its range. Take g = 10 m/s^2."))
        self.assertEqual((outcome, [p["code"] for p in problems]), ("FAIL", ["GIVEN_NOT_VISIBLE"]))

    def test_a_specification_that_contradicts_the_computation_fails(self):
        model = json.loads(json.dumps(SPEC["computation_model"]))
        model["variables"]["u"]["value"] = 25
        self.assertEqual(typed.self_containment(typed_question(computation_model=model))[1][0]["code"], "GIVEN_MISMATCH")

    def test_a_wrong_key_and_a_wrong_unit_fail(self):
        self.assertEqual(typed.answer_correctness(typed_question(value=40.0))[1][0]["code"], "WRONG_ANSWER")
        self.assertEqual(typed.dimensional_correctness(typed_question(unit="s"))[1][0]["code"], "WRONG_UNIT")

    def test_the_symbols_are_the_computations_not_the_small_words_of_the_answer(self):
        q = typed_question()
        q["answer"]["summary"] = "So it is 34.6 m, in kg and cm, as we do."
        self.assertEqual(typed.self_containment(q)[0], "PASS")


class TypedPackages(Repo):
    def declare(self, **changes):
        def spoil(package):
            question = first_question(package)
            question["stem"] = typed_question()["stem"]
            question["extensions"] = typed_question(**changes)["extensions"]
            question["answer"]["numeric"] = {"value": changes.get("value", 34.641), "unit": changes.get("unit", "m")}
        self.edit(spoil)
        return self.verdicts()

    def test_a_declared_wrong_key_fails_answer_correctness(self):
        self.assertEqual(self.declare(value=40.0)["ANSWER_CORRECTNESS"][self.target_id()], "FAIL")

    def test_a_declared_wrong_unit_fails_dimensional_correctness(self):
        self.assertEqual(self.declare(unit="s")["DIMENSIONAL_CORRECTNESS"][self.target_id()], "FAIL")

    def test_a_declared_hidden_given_fails_self_containment(self):
        spec = json.loads(json.dumps(SPEC["problem_specification"]))
        spec["permitted_constants"] = []
        self.assertEqual(self.declare(problem_specification=spec)["SELF_CONTAINMENT"][self.target_id()], "FAIL")
        self.assertIn("HIDDEN_GIVEN", self.found[("SELF_CONTAINMENT", self.target_id())])

    def test_one_declared_question_among_undeclared_ones_is_not_enough_to_pass(self):
        self.assertEqual(self.declare()["SELF_CONTAINMENT"][self.target_id()], "INCONCLUSIVE")


class Projections(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.repo, True)
        (self.repo / "standalone").mkdir()

    def page(self, name, body="", head=""):
        (self.repo / "standalone" / name).write_text(
            f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>t</title>{head}</head><body>{body}</body></html>',
            encoding="utf-8")

    def verdicts(self):
        subject = aggregate.projection_subjects(["standalone=standalone"], self.repo)[0]
        return subject, verifiers.verify_projection(subject, self.repo)

    def test_a_clean_page_passes_the_three_types(self):
        self.page("a.html", "<h1 id='x'>t</h1><a href='#x'>x</a>")
        _, out = self.verdicts()
        self.assertEqual({t: v.outcome for t, v in out.items()}, {"NETWORK_POLICY": "PASS", "LINK_INTEGRITY": "PASS", "PROJECTION_STATIC_CONFORMANCE": "PASS"})

    def test_each_page_defect_fails_the_type_the_registry_assigns_it(self):
        self.page("a.html", "<a href='gone.html'>x</a><p>$\x0bec{F}$</p>", '<script src="https://www.gstatic.com/x.js"></script><style>p{font-size:11px}</style>')
        _, out = self.verdicts()
        self.assertEqual({t: v.outcome for t, v in out.items()}, {"NETWORK_POLICY": "FAIL", "LINK_INTEGRITY": "FAIL", "PROJECTION_STATIC_CONFORMANCE": "FAIL"})
        self.assertEqual({f["code"] for f in out["PROJECTION_STATIC_CONFORMANCE"].findings}, {"FONT_FLOOR", "MATH_CONTROL_CHARS"})
        self.assertEqual({f["code"] for f in out["NETWORK_POLICY"].findings}, {"REMOTE_RUNTIME"})

    def test_the_rule_to_type_assignment_is_the_registrys_and_every_type_is_one_the_evidence_schema_knows(self):
        known = set(json.loads((REPO / "Shared/assurance/assurance-evidence.schema.json").read_text())["properties"]["assurance_type"]["enum"])
        assigned = set(verifiers.rule_types().values()) | set(verifiers.point_types().values())
        self.assertEqual(assigned - known, set())
        self.assertEqual(set(verifiers.rule_types().values()), set(verifiers.PAGE_TYPES))

    def test_a_static_check_does_not_claim_a_layout_it_cannot_see(self):
        self.page("a.html", "<h1>t</h1>")
        _, out = self.verdicts()
        self.assertNotIn("RESPONSIVE_LAYOUT", out)
        self.assertNotIn("ACCESSIBILITY", out)

    def test_a_new_page_with_a_finding_is_worse_than_the_ledger(self):
        self.page("brand-new.html", "<a href='gone.html'>x</a>")
        subject, _ = self.verdicts()
        problems = verifiers.projection_ratchet(subject, self.repo)
        self.assertTrue(any("LINKS_RESOLVE" in p for p in problems), problems)


class Ratchet(unittest.TestCase):
    def test_a_finding_in_the_baseline_is_known_and_a_new_one_is_not(self):
        subject = aggregate.Subject("CANONICAL_RECORD", "pkg", "sha256:" + "1" * 64, "x.json")
        record = {"assurance_type": "REFERENCE_INTEGRITY", "outcome": "FAIL", "subject": {"kind": "CANONICAL_RECORD", "id": subject.id},
                  "findings": [{"code": "LIBRARY_NESTED_ID_COLLISION", "severity": "S1", "subject": "Q1-CHK", "message": "m"}]}
        known = set(baseline.keys([record]))
        self.assertEqual(baseline.new_findings([record], known), [])
        record["findings"].append({"code": "LIBRARY_NESTED_ID_COLLISION", "severity": "S1", "subject": "Q9-CHK", "message": "a second collision in the same package"})
        self.assertEqual(len(baseline.new_findings([record], known)), 1, "a second collision in a package that has one is a new finding")
        record["findings"] = []
        self.assertEqual(len(baseline.fixed([record], known)), 1)

    def test_the_committed_baseline_is_current_and_holds_only_what_main_has(self):
        out = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out, True)
        run = verifiers.run(REPO, ["Physics/library", "Mathematics/library"], [], out)
        found = set(baseline.keys(run.evidence))
        known = baseline.load()
        self.assertEqual(sorted(found - known), [], "a new canonical finding: fix it, or (if it is old debt) rewrite the baseline with assurance_run.py --write-baseline")
        self.assertEqual(sorted(known - found), [], "the baseline lists a finding that is gone: tighten it with assurance_run.py --write-baseline")

    def test_enforce_passes_at_the_baseline_and_fails_on_a_new_finding(self):
        empty = REPO / "build" / "test-assurance" / "empty-baseline.json"
        baseline.write([], empty)
        self.addCleanup(lambda: empty.unlink(missing_ok=True))
        out = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, out, True)
        argv = ["--packages", "Physics/library", "Mathematics/library", "--evidence-dir", f"build/test-assurance/{Path(out).name}"]
        self.assertEqual(assurance_run.main(argv + ["--enforce"]), 0, "main at its committed baseline")
        self.assertEqual(assurance_run.main(argv + ["--enforce", "--baseline", empty.relative_to(REPO).as_posix()]), 1, "the Mathematics collisions are new against an empty baseline")


# -- the acceptance test -------------------------------------------------------------------------------------------------------------------------

TEST_POLICY = {"schema": "canonical-admission-policy/v1", "policy_id": "test-admission", "version": "1", "subject_kind": "CANONICAL_RECORD",
               "required_pass": ["STRUCTURAL_VALIDITY", "REFERENCE_INTEGRITY", "CORPUS_SPECIFICITY", "SCOPE_CONFORMANCE"],
               "required_pass_or_na": ["ANSWER_CORRECTNESS", "DIMENSIONAL_CORRECTNESS", "DISCLOSURE_CONFORMANCE"], "required_pass_or_reviewed": ["REASONING_VALIDITY"]}


class Acceptance(Repo):
    """Product = the Physics library; the policy asks for the types the verifiers can establish today."""

    def release(self, waive_author_only=True):
        evidence_dir = self.repo / "evidence"
        verifiers.run(self.repo, [LIB], [], evidence_dir)
        subjects = self.subjects()
        records, problems = aggregate.collect(evidence_dir)
        ev = aggregate.evaluate(subjects, [TEST_POLICY], records)
        ev.problems = problems + ev.problems
        bundle = aggregate.build_bundle("physics", subjects, [TEST_POLICY], ev)
        waivers = {}
        if waive_author_only:
            waivers = {f"REASONING_VALIDITY@{s.key}": {"type": "REASONING_VALIDITY", "subject": s.key, "reason": "keys checked by their author; the Owner accepts that for now",
                                                       "approval_ref": "test"} for s in subjects}
        return aggregate.evaluate_release(bundle, evidence_dir, [TEST_POLICY], waivers, repo=self.repo)

    def test_the_library_as_it_is_in_physics_is_eligible_under_a_policy_of_what_is_verified_with_the_owners_waiver_for_author_only_keys(self):
        decision = self.release()
        self.assertEqual((decision["status"], decision["problems"], decision["missing"]), ("ELIGIBLE", [], []))
        self.assertEqual(contract.schema_problems("eligibility", decision), [])

    def test_without_the_waiver_author_only_keys_leave_it_incomplete(self):
        decision = self.release(waive_author_only=False)
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertEqual({m["type"] for m in decision["missing"]}, {"REASONING_VALIDITY"})

    DEFECTS = {
        "a boilerplate answer": lambda p: first_question(p).update(answer=dict(GENERIC)),
        "options that are their letters": lambda p: first_question(p).update(options=["(A) A", "(B) B"]),
        "a stem that asks nothing": lambda p: first_question(p).update(stem="Compare squared speeds"),
        "a key nobody ran": lambda p: first_question(p)["answer"].update(verification_status="NOT_RUN"),
        "an unresolved reference": lambda p: p["capabilities"][0].update(prerequisite_refs=["CAP-DOES-NOT-EXIST"]),
    }

    def test_each_defect_class_of_the_validation_makes_the_product_ineligible(self):
        for name, spoil in self.DEFECTS.items():
            with self.subTest(defect=name):
                self.setUp()
                self.edit(spoil)
                decision = self.release()
                self.assertEqual(decision["status"], "INELIGIBLE", name)
                self.assertTrue(any(f["severity"] in ("S0", "S1") for f in decision["reviewable_findings"]), name)

    def test_a_package_that_does_not_parse_makes_the_product_ineligible_not_silently_smaller(self):
        (self.repo / LIB / TARGET).write_text("{ not json", encoding="utf-8")
        self.assertEqual(self.release()["status"], "INELIGIBLE")

    def test_the_evidence_directory_holds_exactly_the_last_run(self):
        evidence_dir = self.repo / "evidence"
        verifiers.run(self.repo, [LIB], [], evidence_dir)
        stale = evidence_dir / "AE-0000000000000000.json"
        stale.write_text("{}", encoding="utf-8")
        verifiers.run(self.repo, [LIB], [], evidence_dir)
        self.assertFalse(stale.exists())
        self.assertEqual(aggregate.collect(evidence_dir)[1], [], "every file in the directory is evidence of this run")

    def test_evidence_the_run_wrote_is_valid_and_deterministic(self):
        evidence_dir = self.repo / "evidence"
        first = verifiers.run(self.repo, [LIB], [], evidence_dir)
        ids = sorted(e["evidence_id"] for e in first.evidence)
        for path in evidence_dir.glob("*.json"):
            self.assertEqual(load_evidence(path)["evidence_id"], path.stem)
        second = verifiers.run(self.repo, [LIB], [], evidence_dir)
        self.assertEqual(sorted(e["evidence_id"] for e in second.evidence), ids, "the same judgment of the same content has the same id")


if __name__ == "__main__":
    unittest.main()
