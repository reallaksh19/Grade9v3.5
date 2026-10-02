"""The assurance chain holds its own contracts: evidence, bundle and eligibility are schema-valid, and aggregation fails closed.

Every case here is one that the first version of the chain got wrong (pull request 395, head d39f0ca6): records that did not satisfy their schemas,
a later PASS hiding an earlier FAIL (or the reverse, by file order), a cited evidence file that was not there, evidence edited after the bundle, the
admission policy applied to the wrong subject, a policy that nothing satisfied reading as satisfied.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from Shared.assurance import aggregate, contract
from Shared.assurance.evidence import evidence_id, finding, load_evidence, make_evidence, write_evidence
from Shared.contracts import ContractError
from Shared.tools import assurance_product, release_eligibility

REPO = Path(__file__).resolve().parents[1]
ZERO = "sha256:" + "0" * 64
POLICY = {"schema": "canonical-admission-policy/v1", "policy_id": "test-admission", "version": "1", "subject_kind": "CANONICAL_RECORD",
          "required_pass": ["STRUCTURAL_VALIDITY", "SELF_CONTAINMENT"], "required_pass_or_na": ["ANSWER_CORRECTNESS"],
          "required_pass_or_reviewed": ["REASONING_VALIDITY"]}
TYPES = ["STRUCTURAL_VALIDITY", "SELF_CONTAINMENT", "ANSWER_CORRECTNESS", "REASONING_VALIDITY"]


class World(unittest.TestCase):
    """A repository of two package files, an evidence directory outside it, and helpers to put evidence about them."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        (self.repo / "lib").mkdir(parents=True)
        for name in ("one", "two"):
            (self.repo / "lib" / f"{name}.json").write_text(json.dumps({"package_id": name, "questions": []}), encoding="utf-8")
        self.evidence = self.tmp / "evidence"
        self.evidence.mkdir()
        self.subjects = aggregate.package_subjects(["lib"], self.repo)
        self.policies = [POLICY]

    def put(self, assurance_type, outcome, subject=None, *, findings=None, name=None, digest=None):
        subject = subject or self.subjects[0]
        record = make_evidence(assurance_type, "CANONICAL_RECORD", subject.id, outcome, "test", "1", findings=findings, subject_digest=digest or subject.digest)
        write_evidence(record, self.evidence / f"{name or record['evidence_id']}.json")
        return record

    def everything_passes(self):
        for subject in self.subjects:
            for t in TYPES[:2]:
                self.put(t, "PASS", subject)
            self.put("ANSWER_CORRECTNESS", "NOT_APPLICABLE", subject)
            self.put("REASONING_VALIDITY", "PASS", subject)

    def bundle(self, waivers=None):
        records, problems = aggregate.collect(self.evidence)
        ev = aggregate.evaluate(self.subjects, self.policies, records, waivers)
        ev.problems = problems + ev.problems
        return aggregate.build_bundle("P", self.subjects, self.policies, ev), ev

    def decide(self, bundle, waivers=None):
        return aggregate.evaluate_release(bundle, self.evidence, self.policies, waivers, repo=self.repo)


class Evidence(unittest.TestCase):
    def make(self, **kw):
        base = dict(assurance_type="LINK_INTEGRITY", subject_kind_="PROJECTION", subject_id="standalone", outcome="PASS", producer_name="t", producer_version="1",
                    subject_digest=ZERO)
        base.update(kw)
        return make_evidence(**base)

    def test_a_record_satisfies_its_schema_and_has_the_same_id_for_the_same_judgment(self):
        a = self.make()
        self.assertEqual(contract.schema_problems("evidence", a), [])
        time.sleep(1.1)
        self.assertEqual(a["evidence_id"], self.make()["evidence_id"], "the id is not over the timestamp")
        self.assertNotEqual(a["evidence_id"], self.make(outcome="FAIL")["evidence_id"])

    def test_a_subject_kind_that_is_not_in_the_schema_is_refused_not_passed_through(self):
        with self.assertRaises(ValueError):
            self.make(subject_kind_="PROJECTION_MANIFEST")
        self.assertEqual(self.make(subject_kind_="library", assurance_type="STRUCTURAL_VALIDITY")["subject"]["kind"], "CANONICAL_RECORD")

    def test_evidence_that_is_not_bound_to_content_is_refused(self):
        with self.assertRaises(ValueError):
            self.make(subject_digest=None)

    def test_a_pass_cannot_carry_a_severe_finding_and_a_fail_has_a_severity(self):
        severe = finding("X", "S1", "q", "m")
        with self.assertRaises(ValueError):
            self.make(findings=[severe])
        failed = self.make(outcome="FAIL", findings=[finding("X", "S2", "q", "m")])
        self.assertEqual(failed["severity"], "S2")
        self.assertEqual(self.make(outcome="FAIL")["severity"], "S1")

    def test_a_finding_in_the_wrong_shape_is_refused(self):
        with self.assertRaises(contract.ContractViolation):
            self.make(outcome="FAIL", findings=[{"file": "a.html"}])

    def test_an_evidence_file_edited_after_it_was_written_is_not_read(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        path = tmp / "e.json"
        record = self.make()
        write_evidence(record, path)
        self.assertEqual(load_evidence(path)["evidence_id"], record["evidence_id"])
        edited = json.loads(path.read_text())
        edited["outcome"] = "FAIL"
        path.write_text(json.dumps(edited))
        with self.assertRaises(contract.ContractViolation):
            load_evidence(path)
        path.write_text("{ not json")
        with self.assertRaises(contract.ContractViolation):
            load_evidence(path)

    def test_evidence_is_not_written_into_the_tree_it_judges(self):
        with self.assertRaises(ValueError):
            write_evidence(self.make(), REPO / "standalone" / "LINK_INTEGRITY.json")
        self.assertFalse((REPO / "standalone" / "LINK_INTEGRITY.json").exists())


class Needs(World):
    def test_all_needs_met_is_eligible(self):
        self.everything_passes()
        bundle, ev = self.bundle()
        self.assertEqual((ev.missing, ev.problems), ([], []))
        self.assertEqual(self.decide(bundle)["status"], "ELIGIBLE")

    def test_no_evidence_leaves_every_need_open_and_is_incomplete(self):
        bundle, ev = self.bundle()
        self.assertEqual(len(ev.missing), 8)               # four types x two packages
        self.assertEqual(self.decide(bundle)["status"], "INCOMPLETE")

    def test_the_outcome_is_the_worst_of_the_evidence_and_does_not_depend_on_file_order(self):
        for name in ("000-fail", "zzz-fail"):
            self.setUp()
            self.everything_passes()
            self.put("SELF_CONTAINMENT", "FAIL", findings=[finding("HIDDEN_GIVEN", "S2", "Q-1", "u is not in the stem")], name=name)
            bundle, ev = self.bundle()
            self.assertEqual(ev.outcomes["SELF_CONTAINMENT@CANONICAL_RECORD:one"], "FAIL", name)
            self.assertEqual(self.decide(bundle)["status"], "INELIGIBLE", name)

    def test_a_not_run_or_inconclusive_record_does_not_satisfy_a_need(self):
        for outcome in ("NOT_RUN", "INCONCLUSIVE"):
            self.setUp()
            self.everything_passes()
            self.put("STRUCTURAL_VALIDITY", outcome)
            bundle, ev = self.bundle()
            self.assertIn("STRUCTURAL_VALIDITY", ev.missing_types, outcome)
            self.assertEqual(self.decide(bundle)["status"], "INCOMPLETE", outcome)

    def test_not_applicable_satisfies_only_the_buckets_that_say_so(self):
        self.everything_passes()
        self.put("STRUCTURAL_VALIDITY", "NOT_APPLICABLE")       # required_pass: the worst of PASS and NOT_APPLICABLE is PASS, so this still holds
        self.assertNotIn("STRUCTURAL_VALIDITY", self.bundle()[1].missing_types)
        self.setUp()
        self.everything_passes()
        for r in list(self.evidence.glob("*.json")):
            if json.loads(r.read_text())["assurance_type"] == "STRUCTURAL_VALIDITY":
                r.unlink()
        for subject in self.subjects:
            self.put("STRUCTURAL_VALIDITY", "NOT_APPLICABLE", subject)
        self.assertIn("STRUCTURAL_VALIDITY", self.bundle()[1].missing_types, "NOT_APPLICABLE alone does not satisfy required_pass")
        self.assertNotIn("ANSWER_CORRECTNESS", self.bundle()[1].missing_types)

    def test_evidence_about_another_subject_satisfies_nothing(self):
        for subject in self.subjects:
            for t in TYPES:
                record = make_evidence(t, "CANONICAL_RECORD", "Q-PHY-X-1", "PASS", "t", "1", subject_digest=subject.digest)   # about a question, not a package
                write_evidence(record, self.evidence / f"{record['evidence_id']}.json")
        bundle, ev = self.bundle()
        self.assertEqual(len(ev.missing), 8)
        self.assertEqual(self.decide(bundle)["status"], "INCOMPLETE")

    def test_evidence_of_older_content_is_stale_and_the_need_stays_open(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        (self.repo / "lib" / "one.json").write_text(json.dumps({"package_id": "one", "questions": [{"id": "new"}]}), encoding="utf-8")
        decision = self.decide(bundle)
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertIn("STALE_SNAPSHOT", {m["reason"] for m in decision["missing"]})
        self.assertIn("STALE", {m["reason"] for m in decision["missing"]})

    def test_a_policy_with_no_subject_of_its_kind_is_not_satisfied(self):
        self.policies = [{**POLICY, "subject_kind": "PROJECTION", "policy_id": "test-release"}]
        self.everything_passes()
        bundle, ev = self.bundle()
        self.assertEqual({m["reason"] for m in ev.missing}, {"NO_SUBJECTS"})
        self.assertEqual(self.decide(bundle)["status"], "INCOMPLETE")

    def test_a_reviewed_type_is_satisfied_by_a_reasoned_waiver_and_only_by_that(self):
        self.everything_passes()
        for r in list(self.evidence.glob("*.json")):
            if json.loads(r.read_text())["assurance_type"] == "REASONING_VALIDITY":
                r.unlink()
        for subject in self.subjects:
            self.put("REASONING_VALIDITY", "INCONCLUSIVE", subject)
        bundle, _ = self.bundle()
        self.assertEqual(self.decide(bundle)["status"], "INCOMPLETE")
        waivers = {f"REASONING_VALIDITY@{s.key}": {"type": "REASONING_VALIDITY", "subject": s.key, "reason": "checked by the Owner on the page", "approval_ref": "comment 1"}
                   for s in self.subjects}
        self.assertEqual(self.decide(bundle, waivers)["status"], "ELIGIBLE")
        no_ref = {k: {**v, "approval_ref": ""} for k, v in waivers.items()}
        decision = self.decide(bundle, no_ref)
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertIn("WAIVER_INVALID", {p["code"] for p in decision["problems"]})

    def test_a_waiver_cannot_satisfy_a_type_that_is_not_reviewable(self):
        self.everything_passes()
        for r in list(self.evidence.glob("*.json")):
            if json.loads(r.read_text())["assurance_type"] == "STRUCTURAL_VALIDITY":
                r.unlink()
        for subject in self.subjects:
            self.put("STRUCTURAL_VALIDITY", "INCONCLUSIVE", subject)
        bundle, _ = self.bundle()
        waivers = {f"STRUCTURAL_VALIDITY@{s.key}": {"type": "STRUCTURAL_VALIDITY", "subject": s.key, "reason": "a reason that is long enough", "approval_ref": "comment 2"}
                   for s in self.subjects}
        self.assertEqual(self.decide(bundle, waivers)["status"], "INCOMPLETE", "a waiver rescues only a required_pass_or_reviewed type")


class OwnerWaivers(World):
    """A waiver the Owner grants for every subject of a type that has no working checker yet. It covers what is open and never what failed."""

    def waiver(self, assurance_type, **changes):
        row = {"type": assurance_type, "subject": "*", "reason": "no working checker exists for this type yet", "approval_ref": "the Owner's reply, quoted"}
        row.update(changes)
        return {f"{assurance_type}@*": row}

    def open_need(self, assurance_type, outcome=None):
        """Every package passes everything, except that `assurance_type` has no evidence or has `outcome`."""
        self.everything_passes()
        for r in list(self.evidence.glob("*.json")):
            if json.loads(r.read_text())["assurance_type"] == assurance_type:
                r.unlink()
        if outcome:
            for subject in self.subjects:
                self.put(assurance_type, outcome, subject)

    def test_it_covers_a_need_that_is_missing_inconclusive_or_not_run_in_any_bucket(self):
        for t in ("SELF_CONTAINMENT", "REASONING_VALIDITY", "STRUCTURAL_VALIDITY"):          # required_pass, reviewed, required_pass
            for outcome in (None, "INCONCLUSIVE", "NOT_RUN"):
                self.setUp()
                self.open_need(t, outcome)
                bundle, _ = self.bundle()
                self.assertEqual(self.decide(bundle)["status"], "INCOMPLETE", (t, outcome))
                decision = self.decide(bundle, self.waiver(t))
                self.assertEqual(decision["status"], "ELIGIBLE", (t, outcome))
                self.assertEqual({(w["type"], w["subject"]) for w in decision["waived"]}, {(t, s.key) for s in self.subjects}, "the decision says what it waived")

    def test_it_never_covers_a_failure(self):
        self.open_need("SELF_CONTAINMENT", "FAIL")
        bundle, _ = self.bundle()
        decision = self.decide(bundle, self.waiver("SELF_CONTAINMENT"))
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertNotIn("waived", decision)

    def test_it_does_not_cover_evidence_that_has_gone_stale(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        (self.repo / "lib" / "one.json").write_text(json.dumps({"package_id": "one", "questions": [{"id": "new"}]}), encoding="utf-8")
        decision = self.decide(bundle, self.waiver("SELF_CONTAINMENT"))
        self.assertEqual(decision["status"], "INCOMPLETE")
        self.assertIn(("SELF_CONTAINMENT", "STALE"), {(m["type"], m["reason"]) for m in decision["missing"]}, "the changed package is stale, not waived")

    def test_old_evidence_lying_in_the_directory_does_not_make_a_correct_bundle_look_broken(self):
        self.everything_passes()
        for subject in self.subjects:
            self.put("SELF_CONTAINMENT", "PASS", subject, digest="sha256:" + "1" * 64)      # about an earlier content of the package
        bundle, _ = self.bundle()
        self.assertEqual(self.decide(bundle)["status"], "ELIGIBLE", "the current evidence is there and counts; the old is not cited")
        self.setUp()
        self.open_need("SELF_CONTAINMENT")
        for subject in self.subjects:
            self.put("SELF_CONTAINMENT", "PASS", subject, digest="sha256:" + "1" * 64)
        bundle, _ = self.bundle()
        decision = self.decide(bundle)
        self.assertEqual((decision["status"], decision["problems"]), ("INCOMPLETE", []))

    def test_a_real_verdict_is_what_counts_once_a_checker_exists(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        decision = self.decide(bundle, self.waiver("SELF_CONTAINMENT"))
        self.assertEqual((decision["status"], decision.get("waived")), ("ELIGIBLE", None), "a PASS needs no waiver and none is reported")

    def test_a_waiver_without_a_reason_or_an_approval_is_not_applied(self):
        self.open_need("SELF_CONTAINMENT")
        bundle, _ = self.bundle()
        for changes in ({"reason": "no"}, {"approval_ref": ""}):
            decision = self.decide(bundle, self.waiver("SELF_CONTAINMENT", **changes))
            self.assertEqual(decision["status"], "INCOMPLETE", changes)
            self.assertIn("WAIVER_INVALID", {p["code"] for p in decision["problems"]}, changes)

    def test_the_bundle_is_facts_and_a_waiver_is_only_a_decision(self):
        self.open_need("SELF_CONTAINMENT")
        bundle, _ = self.bundle()
        self.assertIn("SELF_CONTAINMENT", bundle["missing_types"], "the bundle says the need is open")
        baked, _ = self.bundle(self.waiver("SELF_CONTAINMENT"))
        self.assertNotIn("SELF_CONTAINMENT", baked["missing_types"])
        self.assertIn("BUNDLE_MISMATCH", {p["code"] for p in self.decide(baked)["problems"]}, "a bundle with the waiver written into it is not what its evidence gives")

    def test_the_committed_waivers_are_the_owners_and_every_one_names_a_type_a_policy_requires(self):
        waivers = aggregate.default_waivers()
        required = set(aggregate.required_types(aggregate.load_policies()))
        self.assertTrue(waivers)
        for key, row in waivers.items():
            self.assertEqual((row["subject"], row["approved_by"]), ("*", "owner"), key)
            self.assertIn(row["type"], required, f"{key} waives a type no policy requires")
            self.assertIn("future_scope", row, key)

    def test_a_waiver_file_that_does_not_satisfy_the_schema_is_not_read(self):
        path = self.tmp / "w.json"
        for change in ({"approved_by": "agent"}, {"reason": "short"}, {"approval_ref": "ok"}, {"approved_at": "yesterday"}):
            row = {**self.waiver("SELF_CONTAINMENT")["SELF_CONTAINMENT@*"], "reason": "no working checker exists for this type yet", "approved_by": "owner",
                   "approval_ref": "the Owner's reply, quoted in full here", "approved_at": "2026-10-02T04:45:02Z", **change}
            path.write_text(json.dumps([row]), encoding="utf-8")
            with self.assertRaises(contract.ContractViolation, msg=change):
                aggregate.load_waivers(path)


class Integrity(World):
    def test_the_bundle_and_the_decision_satisfy_their_schemas(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        self.assertEqual(contract.schema_problems("bundle", bundle), [])
        self.assertEqual(contract.schema_problems("eligibility", self.decide(bundle)), [])

    def test_the_bundle_id_and_digest_are_the_same_for_the_same_content(self):
        self.everything_passes()
        a, _ = self.bundle()
        time.sleep(1.1)
        b, _ = self.bundle()
        self.assertEqual((a["bundle_id"], a["bundle_digest"]), (b["bundle_id"], b["bundle_digest"]))

    def test_a_cited_evidence_file_that_is_not_there_makes_the_product_ineligible(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        next(self.evidence.glob("*.json")).unlink()
        decision = self.decide(bundle)
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertIn("EVIDENCE_MISSING", {p["code"] for p in decision["problems"]})

    def test_evidence_edited_after_the_bundle_was_made_makes_the_product_ineligible(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        path = next(p for p in self.evidence.glob("*.json") if json.loads(p.read_text())["assurance_type"] == "SELF_CONTAINMENT")
        edited = json.loads(path.read_text())
        edited["outcome"] = "FAIL"
        path.write_text(json.dumps(edited))
        decision = self.decide(bundle)
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertIn("EVIDENCE_INVALID", {p["code"] for p in decision["problems"]})

    def test_a_new_failing_record_after_the_bundle_is_not_hidden_by_the_bundle(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        record = self.put("SELF_CONTAINMENT", "FAIL", findings=[finding("HIDDEN_GIVEN", "S2", "Q-1", "m")])
        bundle["evidence_refs"] = sorted(bundle["evidence_refs"] + [record["evidence_id"]])    # cite it, without recomputing the rest
        decision = self.decide(bundle)
        self.assertEqual(decision["status"], "INELIGIBLE")

    def test_an_edited_bundle_is_not_trusted(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        bundle["missing_types"] = []
        bundle["outcomes"] = {k: "PASS" for k in bundle["outcomes"]}
        self.assertIn("BUNDLE_ID_MISMATCH", {p["code"] for p in aggregate.verify_bundle(bundle)})
        self.assertEqual(self.decide(bundle)["status"], "INELIGIBLE")

    def test_a_bundle_edited_in_a_field_nothing_recomputes_is_caught_by_its_digest(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        edited = {**bundle, "problems": [{"code": "NOTE", "message": "a field that nothing recomputes"}]}
        self.assertEqual({p["code"] for p in aggregate.verify_bundle(edited)}, {"BUNDLE_ID_MISMATCH", "BUNDLE_DIGEST_MISMATCH"})
        self.assertEqual(self.decide(edited)["status"], "INELIGIBLE")

    def test_a_pass_that_carries_a_severe_finding_is_a_problem_even_if_it_was_not_made_by_make_evidence(self):
        record = make_evidence("SELF_CONTAINMENT", "CANONICAL_RECORD", self.subjects[0].id, "PASS", "t", "1", subject_digest=self.subjects[0].digest)
        record["findings"] = [finding("HIDDEN_GIVEN", "S1", "Q-1", "u is not in the stem")]
        record["evidence_id"] = evidence_id(record)
        contract.write_json(self.evidence / f"{record['evidence_id']}.json", record)
        _, ev = self.bundle()
        self.assertIn("PASS_WITH_SEVERE_FINDING", {p["code"] for p in ev.problems})

    def test_a_bundle_that_claims_less_is_open_than_its_evidence_gives_is_not_trusted(self):
        bundle, _ = self.bundle()                                        # nothing has run: everything is open
        forged = {**bundle, "missing_types": [], "missing": [], "outcomes": {k: "PASS" for k in bundle["outcomes"]}}
        body = {k: v for k, v in forged.items() if k not in ("bundle_id", "bundle_digest", "bundled_at")}
        import hashlib
        from Shared.contracts import canonical
        forged["bundle_id"] = "AB-" + hashlib.sha256(canonical(body)).hexdigest()[:16]
        forged["bundle_digest"] = contract.digest({**body, "bundle_id": forged["bundle_id"]})
        self.assertEqual(aggregate.verify_bundle(forged), [], "a self-consistent forgery")
        decision = self.decide(forged)
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertIn("BUNDLE_MISMATCH", {p["code"] for p in decision["problems"]})

    def test_a_bundle_for_other_policies_is_not_trusted(self):
        self.everything_passes()
        bundle, _ = self.bundle()
        decision = aggregate.evaluate_release(bundle, self.evidence, [{**POLICY, "policy_id": "another"}], None, repo=self.repo)
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertIn("POLICY_MISMATCH", {p["code"] for p in decision["problems"]})

    def test_junk_in_the_evidence_directory_is_a_problem_not_something_to_skip(self):
        self.everything_passes()
        (self.evidence / "junk.json").write_text("{}")
        bundle, ev = self.bundle()
        self.assertIn("EVIDENCE_INVALID", {p["code"] for p in ev.problems})
        self.assertTrue(bundle["problems"])


class Commands(unittest.TestCase):
    """The same chain through the command line, with files under the repository's untracked build/ directory."""

    def setUp(self):
        base = REPO / "build" / "test-assurance"
        base.mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(dir=base))
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / "lib").mkdir()
        (self.root / "lib" / "one.json").write_text(json.dumps({"package_id": "one", "questions": []}), encoding="utf-8")
        self.rel = self.root.relative_to(REPO).as_posix()
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()

    def bundle_args(self, *extra):
        return ["--product-id", "P", "--packages", f"{self.rel}/lib", "--policy", "canonical-admission-default", "--evidence-dir", f"{self.rel}/evidence",
                "--output", f"{self.rel}/P.bundle.json", *extra]

    def test_enforce_exits_nonzero_while_anything_is_open_and_zero_when_nothing_is(self):
        self.assertEqual(assurance_product.main(self.bundle_args("--enforce")), 1)
        subject = aggregate.package_subjects([f"{self.rel}/lib"])[0]
        policy = aggregate.load_policies(["canonical-admission-default"])[0]
        for t in aggregate.required_types([policy]):
            record = make_evidence(t, "CANONICAL_RECORD", "one", "PASS", "t", "1", subject_digest=subject.digest)
            write_evidence(record, self.evidence / f"{record['evidence_id']}.json")
        self.assertEqual(assurance_product.main(self.bundle_args("--enforce")), 0)
        argv = ["--product-id", "P", "--bundle", f"{self.rel}/P.bundle.json", "--evidence-dir", f"{self.rel}/evidence", "--output", f"{self.rel}/E.json", "--enforce"]
        self.assertEqual(release_eligibility.main(argv), 0)
        self.assertEqual(contract.schema_problems("eligibility", json.loads((self.root / "E.json").read_text())), [])

    def test_a_bundle_for_another_product_is_refused(self):
        assurance_product.main(self.bundle_args())
        argv = ["--product-id", "OTHER", "--bundle", f"{self.rel}/P.bundle.json", "--evidence-dir", f"{self.rel}/evidence", "--enforce"]
        self.assertEqual(release_eligibility.main(argv), 1)

    def test_an_unreadable_or_invalid_bundle_is_refused(self):
        (self.root / "bad.json").write_text("{ nope")
        with self.assertRaises(ContractError):
            release_eligibility.load_and_check(f"{self.rel}/bad.json", "P", f"{self.rel}/evidence")
        (self.root / "bad.json").write_text("{}")
        with self.assertRaises(ContractError):
            release_eligibility.load_and_check(f"{self.rel}/bad.json", "P", f"{self.rel}/evidence")


if __name__ == "__main__":
    unittest.main()
