"""Tooling: the manifest is deterministic and detects drift, the guard's exclusion
mechanism requires a reason, and generated web data tells the truth about compilation."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.library import compile_inputs  # noqa: E402
from Shared.tools import (  # noqa: E402
    author_brief, build_manifest, build_web_data, capability_audit, ceiling_audit,
    check_subjects, capability_collisions, learner_evidence, matrix_conformance,
    publication_provenance, resolve_request, spec_conformance, spec_delivery,
    topic_independence_guard,
)
from Shared.tools.topic_independence_guard import (  # noqa: E402
    excluded_globs, excluded_paths, is_excluded, scan_python, selftest,
)


class Manifest(unittest.TestCase):
    def test_is_deterministic(self):
        self.assertEqual(build_manifest.collect()["digest"], build_manifest.collect()["digest"])

    def test_committed_manifest_matches_the_tree(self):
        committed = json.loads((REPO / "docs/architecture-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(committed["digest"], build_manifest.collect()["digest"],
                         "regenerate with python3 Shared/tools/build_manifest.py")

    def test_collect_does_not_write_to_the_tree(self):
        # It used to regenerate tools/data.js as a side effect, so merely asking what
        # the manifest should be overwrote whatever was in the working copy.
        generated = REPO / "tools/data.js"
        before = generated.read_bytes()
        build_manifest.collect()
        self.assertEqual(generated.read_bytes(), before)

    def test_check_reports_a_stale_generated_file_without_repairing_it(self):
        generated = REPO / "tools/data.js"
        before = generated.read_bytes()
        generated.write_bytes(before + b"// tampered\n")
        try:
            result = subprocess.run([sys.executable, "Shared/tools/build_manifest.py", "--check"],
                                    cwd=REPO, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("tools/data.js", result.stdout)
            self.assertEqual(generated.read_bytes(), before + b"// tampered\n",
                             "a read-only check silently rewrote the file")
        finally:
            generated.write_bytes(before)

    def test_digest_changes_when_a_component_changes(self):
        before = build_manifest.collect()["digest"]
        scratch = REPO / "Shared" / "tools" / "_drift_probe.py"
        scratch.write_text("# temporary component used to prove drift is detected\n", encoding="utf-8")
        try:
            self.assertNotEqual(before, build_manifest.collect()["digest"])
        finally:
            scratch.unlink()
        self.assertEqual(before, build_manifest.collect()["digest"])

    def test_every_component_carries_a_role(self):
        for component in build_manifest.collect()["components"]:
            self.assertTrue(component["role"])
            self.assertTrue(component["role_description"])


class Guard(unittest.TestCase):
    def test_selftest_passes(self):
        self.assertEqual(selftest(), 0)

    def test_exclusions_are_declared_with_reasons(self):
        document = json.loads(
            (REPO / "Shared/tools/topic_independence_allowlist.json").read_text(encoding="utf-8"))
        self.assertTrue(document["exclude_paths"])
        for entry in document["exclude_paths"]:
            self.assertTrue(entry["reason"].strip())
        self.assertIn("tools/data.js", excluded_paths())

    def test_an_exclusion_without_a_reason_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            broken = Path(temp) / "allowlist.json"
            broken.write_text(json.dumps({"exclude_paths": [{"path": "x", "reason": " "}]}),
                              encoding="utf-8")
            import Shared.tools.topic_independence_guard as guard
            original = guard.ALLOWLIST
            guard.ALLOWLIST = broken
            try:
                with self.assertRaises(SystemExit):
                    guard.excluded_paths()
            finally:
                guard.ALLOWLIST = original

    def test_glob_exclusions_cover_hash_named_generated_files_but_not_their_generator(self):
        exact, globs = excluded_paths(), excluded_globs()
        for generated in (
            "public/data/question-bank-search.js",
            "docs/data/question-bank-catalog.js",
            "public/data/question-bank-details/subject-chemistry-97462a79cb.js",
            "docs/data/question-bank-details/subject-physics-fc07b0f63d.js",
        ):
            self.assertTrue(is_excluded(generated, exact, globs), generated)
        for scanned in (
            "Shared/tools/question_bank_platform.py",
            "Shared/tools/build_question_bank_platform.py",
            "public/js/question-bank.js",
            "public/js/question-bank-data-service.js",
            "public/data/question-bank/other.js",
        ):
            self.assertFalse(is_excluded(scanned, exact, globs), scanned)

    def test_method_document_names_are_not_identifiers_but_real_identifiers_still_are(self):
        from Shared.tools.topic_independence_guard import check_literal
        for document in ("DESIGN-NOTE.md", "SELF-CHECK.md", "docs/method/roles/SOURCE-READER.md"):
            self.assertIsNone(check_literal(document), document)
        for identifier in ("PHY-M2D", "BUCKET-RELATIVE-MOTION", "CAP-SIGNED-PAIR", "PHY-M2D.json"):
            self.assertEqual(check_literal(identifier), "governed identifier in engine code", identifier)

    def test_rule_id_allowlist_entries_still_name_rules_in_the_quality_contract(self):
        document = json.loads(
            (REPO / "Shared/tools/topic_independence_allowlist.json").read_text(encoding="utf-8"))
        contract = json.loads(
            (REPO / "Shared/quality/learner-quality.v1.json").read_text(encoding="utf-8"))
        rule_ids: set[str] = set()

        def walk(node):
            if isinstance(node, dict):
                if isinstance(node.get("id"), str):
                    rule_ids.add(node["id"])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)
        walk(contract)
        entries = [e for e in document["allow"] if e["path"] == "Shared/tools/package_depth.py"]
        self.assertTrue(entries)
        for entry in entries:
            self.assertIn(entry["literal"], rule_ids, entry["literal"])

    def test_every_glob_exclusion_has_a_reason_and_a_directory_anchor(self):
        document = json.loads(
            (REPO / "Shared/tools/topic_independence_allowlist.json").read_text(encoding="utf-8"))
        self.assertTrue(document["exclude_path_globs"])
        for entry in document["exclude_path_globs"]:
            self.assertTrue(entry["reason"].strip())
            self.assertIn("/", entry["glob"].split("*")[0])

    def test_a_glob_exclusion_that_is_unexplained_or_unanchored_is_refused(self):
        import Shared.tools.topic_independence_guard as guard
        original = guard.ALLOWLIST
        try:
            for entries in (
                [{"glob": "public/data/x-*.js", "reason": " "}],
                [{"glob": "*.js", "reason": "would exempt every script"}],
                [{"glob": "**/*.js", "reason": "would exempt every script"}],
            ):
                with tempfile.TemporaryDirectory() as temp:
                    broken = Path(temp) / "allowlist.json"
                    broken.write_text(json.dumps({"exclude_path_globs": entries}), encoding="utf-8")
                    guard.ALLOWLIST = broken
                    with self.assertRaises(SystemExit):
                        guard.excluded_globs()
        finally:
            guard.ALLOWLIST = original

    def test_a_planted_literal_is_still_caught(self):
        with tempfile.TemporaryDirectory() as temp:
            planted = Path(temp) / "p.py"
            planted.write_text('def f(x):\n    return x == "PHY-REL-VELOCITY"\n', encoding="utf-8")
            self.assertEqual(len(scan_python(planted, [])), 1)


class WebData(unittest.TestCase):
    def setUp(self):
        self.payload = build_web_data.build()

    def test_every_declared_subject_appears(self):
        contracts = {p.parent.parent.name for p in REPO.glob("*/adapter/CoreContracts.json")}
        self.assertEqual(set(self.payload["subjects"]), contracts)

    def test_every_bucket_carries_an_honest_compile_preview(self):
        for entry in self.payload["subjects"].values():
            for bucket in entry["buckets"]:
                preview = bucket["compile_preview"]
                self.assertIn("compilable", preview)
                if preview["compilable"]:
                    self.assertTrue(preview["supported_products"])
                else:
                    self.assertTrue(preview["code"], "an uncompilable bucket must say why")

    def test_a_subject_without_a_library_is_marked_rather_than_hidden(self):
        without = [name for name, entry in self.payload["subjects"].items()
                   if not entry["library_available"]]
        for name in without:
            self.assertEqual(self.payload["subjects"][name]["buckets"], [])
            self.assertTrue(self.payload["subjects"][name]["contract"]["validator_catalogue"],
                            f"{name} should still declare its contract")

    def test_unsupported_products_are_reported_not_omitted_silently(self):
        physics = self.payload["subjects"].get("Physics", {})
        target = next((b for b in physics.get("buckets", []) if b["compile_preview"]["compilable"]), None)
        self.assertIsNotNone(target)
        requirements = target["compile_preview"]["authoring_requirements"]
        self.assertTrue(any(r["kind"] == "PRODUCT_UNSUPPORTED" for r in requirements))

    def test_generated_file_on_disk_matches_a_fresh_build(self):
        text = (REPO / "tools/data.js").read_text(encoding="utf-8")
        on_disk = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))
        self.assertEqual(on_disk, json.loads(json.dumps(self.payload)),
                         "regenerate with python3 Shared/tools/build_web_data.py")


if __name__ == "__main__":
    unittest.main()


class SubjectCoverage(unittest.TestCase):
    """CI once checked one named subject. These hold the discovery honest."""

    def test_every_subject_directory_is_discovered(self):
        found = {p.name for p in check_subjects.subjects()}
        declared = {p.parent.parent.name for p in REPO.glob("*/adapter/CoreContracts.json")}
        self.assertEqual(found, declared)
        self.assertGreater(len(found), 1, "a single-subject sweep proves nothing about neutrality")

    def test_the_sweep_passes_on_the_committed_tree(self):
        report = check_subjects.run()
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["subjects_checked"], len(check_subjects.subjects()))

    def test_a_subject_declaring_a_contract_but_no_adapter_is_named_not_skipped(self):
        # A subject can be planned before it is built. That state is reported rather
        # than crashing the sweep or silently counting as checked.
        states = {r["subject"]: r["state"] for r in check_subjects.run()["subjects"]}
        self.assertIn("IMPLEMENTED", states.values())
        for subject in check_subjects.subjects():
            expected = "IMPLEMENTED" if (subject / "adapter/validator.py").is_file() else "CONTRACT_ONLY"
            self.assertEqual(states[subject.name], expected)

    def test_a_hollow_library_in_any_subject_is_caught(self):
        # The falsifier the old CI could not have run: break a subject that is not the
        # one a workflow file happened to name, and the sweep must still fail.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for subject in check_subjects.subjects():
                shutil.copytree(subject, root / subject.name)
            target = sorted(root.glob("*/library/*.json"))[-1]
            package = json.loads(target.read_text(encoding="utf-8"))
            package["microtopics"][0]["inferential_jump"] = ""
            target.write_text(json.dumps(package), encoding="utf-8")
            report = check_subjects.run(root)
            self.assertFalse(report["passed"])
            self.assertTrue(any("INFERENCE" in f for r in report["subjects"] for f in r["findings"]),
                            report)


class GuardRoots(unittest.TestCase):
    """The guard scans what must be neutral, without being told where to look."""

    def test_roots_are_derived_and_exclude_subjects_and_tests(self):
        names = {p.name for p in topic_independence_guard.default_roots()}
        subjects = {p.name for p in check_subjects.subjects()}
        self.assertFalse(names & subjects, "a subject directory is allowed to name its subject")
        self.assertNotIn("tests", names)
        self.assertIn("Shared", names)

    def test_a_new_neutral_directory_is_guarded_without_a_flag(self):
        scratch = REPO / "_guard_root_probe"
        scratch.mkdir()
        try:
            (scratch / "probe.py").write_text("# temporary\n", encoding="utf-8")
            self.assertIn("_guard_root_probe",
                          {p.name for p in topic_independence_guard.default_roots()})
        finally:
            shutil.rmtree(scratch)


class CapabilityClaims(unittest.TestCase):
    """A contract may not claim a capability the repository cannot perform.

    Built before anything was fixed, and it earned that order immediately: an ad-hoc
    survey had counted the unimplemented representation kinds as unbacked claims, when
    every one of them is correctly marked PROPOSED. The gate found three real false
    claims and six that have nowhere to be stated, not eleven of everything.
    """

    def _contract(self, subject="Physics"):
        return json.loads((REPO / subject / "adapter/CoreContracts.json")
                          .read_text(encoding="utf-8"))

    def test_a_status_that_says_proposed_is_not_a_false_claim(self):
        # The honest mechanism already exists for validators and representation kinds.
        report = capability_audit.audit()
        flagged = {f["capability"] for s in report["subjects"] for f in s["findings"]}
        for subject in ("Physics", "Mathematics", "Chemistry"):
            for kind in self._contract(subject)["representation_kinds"]:
                if kind["status"] != "IMPLEMENTED":
                    self.assertNotIn(kind["id"], flagged,
                                     "a capability declared as proposed is honest")

    def test_no_contract_in_the_tree_claims_what_nothing_backs(self):
        report = capability_audit.audit()
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["claims_unbacked"], 0)

    def test_a_product_not_compiled_here_is_honest_rather_than_a_finding(self):
        # Saying so is the point of the field. What must not pass is saying nothing.
        for subject in sorted(REPO.glob("*/adapter/CoreContracts.json")):
            contract = json.loads(subject.read_text(encoding="utf-8"))
            for product, declared in contract["learner_products"].items():
                compiled = declared["production"] == "COMPILED"
                self.assertEqual(compiled, product in compile_inputs.COMPOSABLE, product)
                if not compiled:
                    self.assertTrue(declared.get("reason", "").strip(), product)

    def test_claiming_a_product_is_compiled_when_nothing_builds_it_is_caught(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(REPO / "Mathematics", root / "Mathematics")
            target = root / "Mathematics/adapter/CoreContracts.json"
            contract = json.loads(target.read_text(encoding="utf-8"))
            contract["learner_products"]["CORE_NO_SUCH_PRODUCT"] = {
                "role": "INVENTED", "production": "COMPILED"}
            target.write_text(json.dumps(contract), encoding="utf-8")
            found = capability_audit.audit_subject(root / "Mathematics")["findings"]
            self.assertIn(("CLAIMED_WITHOUT_CODE", "CORE_NO_SUCH_PRODUCT"),
                          [(f["point"], f["capability"]) for f in found])

    def test_declining_to_say_why_a_product_is_not_compiled_is_caught(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(REPO / "Mathematics", root / "Mathematics")
            target = root / "Mathematics/adapter/CoreContracts.json"
            contract = json.loads(target.read_text(encoding="utf-8"))
            contract["learner_products"]["CORE_NO_SUCH_PRODUCT"] = {
                "role": "PLANNED", "production": "NOT_COMPILED", "reason": "   "}
            target.write_text(json.dumps(contract), encoding="utf-8")
            found = capability_audit.audit_subject(root / "Mathematics")["findings"]
            self.assertIn(("PRODUCT_NOT_COMPILED_WITHOUT_REASON", "CORE_NO_SUCH_PRODUCT"),
                          [(f["point"], f["capability"]) for f in found])

    def test_planting_a_false_claim_is_caught(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for subject in sorted(REPO.glob("*/adapter/CoreContracts.json")):
                shutil.copytree(subject.parent.parent, root / subject.parent.parent.name)
            target = root / "Mathematics/adapter/CoreContracts.json"
            contract = json.loads(target.read_text(encoding="utf-8"))
            contract["validator_catalogue"].append(
                {"id": "NO_SUCH_FAMILY", "status": "IMPLEMENTED", "inputs": [],
                 "input_units": {}, "requires": [], "proves": "x", "does_not_prove": "y",
                 "result": {"shape": "EXACT_RATIONAL", "unit": "dimensionless",
                            "comparison": "EXACT_RATIONAL_EQUALITY"}})
            target.write_text(json.dumps(contract), encoding="utf-8")
            found = capability_audit.audit_subject(root / "Mathematics")["findings"]
            self.assertIn(("CLAIMED_WITHOUT_CODE", "NO_SUCH_FAMILY"),
                          [(f["point"], f["capability"]) for f in found])

    def test_code_that_outruns_its_contract_is_reported_too(self):
        # The opposite drift: a renderer exists while the contract still calls it proposed.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(REPO / "Mathematics", root / "Mathematics")
            target = root / "Mathematics/adapter/CoreContracts.json"
            contract = json.loads(target.read_text(encoding="utf-8"))
            for kind in contract["representation_kinds"]:
                if kind["id"] == "NUMBER_LINE":
                    kind["status"] = "PROPOSED"
            target.write_text(json.dumps(contract), encoding="utf-8")
            found = capability_audit.audit_subject(root / "Mathematics")["findings"]
            self.assertIn(("BUILT_BUT_NOT_CLAIMED", "NUMBER_LINE"),
                          [(f["point"], f["capability"]) for f in found])


class SpecConformance(unittest.TestCase):
    """A role spec may not require content the schema has nowhere to keep.

    The checker's own falsifiers plant each finding rather than asserting against the
    real backlog, which shrinks as R1.3 closes it. What is asserted about the real
    tree is that all six specs carry a block and that every path is at least
    well-formed -- a typo must read as a typo, not as a missing field.
    """

    def setUp(self):
        self.schema = json.loads(
            (REPO / spec_conformance.SCHEMA).read_text(encoding="utf-8"))

    def resolve(self, path):
        return spec_conformance.resolve(path, self.schema)[0]

    def test_all_six_role_specs_are_found_from_the_index(self):
        found = [p.name for p in spec_conformance.role_specs()]
        self.assertEqual(len(found), 6, found)
        self.assertNotIn("README.md", found, "the invariants document is not a seventh role")

    def test_every_spec_carries_a_block(self):
        for role in spec_conformance.audit()["roles"]:
            with self.subTest(role=role["role"]):
                self.assertNotIn("SPEC_BLOCK_MISSING",
                                 [f["point"] for f in role["findings"]])
                self.assertGreater(role["required"], 0)

    def test_a_missing_block_is_a_finding_distinct_from_an_empty_one(self):
        with tempfile.TemporaryDirectory() as temp:
            spec = Path(temp) / "CORE1.md"
            spec.write_text("# no block here\n", encoding="utf-8")
            report = spec_conformance.audit_spec(spec, self.schema)
        self.assertEqual([f["point"] for f in report["findings"]], ["SPEC_BLOCK_MISSING"])
        self.assertEqual(report["required"], 0)

    def test_a_field_with_a_home_resolves(self):
        # Paths that must keep resolving whatever else changes: if these break, the
        # checker has stopped walking the schema rather than found a real defect.
        for path in ("microtopic.id", "relation.expression", "question.stem",
                     "microtopic.teaching_path[].why_valid",
                     "representation.scene_instances[].microtopic_ref"):
            with self.subTest(path=path):
                self.assertEqual(self.resolve(path), "", path)

    def test_a_planted_requirement_with_no_home_is_a_finding(self):
        self.assertEqual(self.resolve("microtopic.no_such_field"), "SPEC_FIELD_ABSENT")
        self.assertEqual(self.resolve("microtopic.teaching_path[].no_such_field"),
                         "SPEC_FIELD_ABSENT")

    def test_an_unknown_record_type_is_named_as_such(self):
        # Not SPEC_FIELD_ABSENT: a spec asking about a record that does not exist is a
        # different mistake from one asking for a field that does not exist.
        self.assertEqual(self.resolve("microtopics.id"), "SPEC_ROOT_UNKNOWN")
        self.assertEqual(self.resolve("answer.summary"), "SPEC_ROOT_UNKNOWN",
                         "a nested definition is not a root; a path says which record it starts from")

    def test_an_ordering_requirement_is_not_satisfied_by_a_scalar(self):
        # question.stem exists and is a string. Requiring it as an array must fail:
        # "in their original ordering" cannot be kept in something with no order.
        self.assertEqual(self.resolve("question.stem[]"), "SPEC_FIELD_NOT_ARRAY")

    def test_a_malformed_path_reads_as_malformed(self):
        for path in ("", "question..stem", "question.Stem", "question.stem[", "question[].stem"):
            with self.subTest(path=path):
                self.assertEqual(self.resolve(path), "SPEC_PATH_MALFORMED", path)

    def test_no_committed_path_is_malformed_or_names_an_unknown_record(self):
        # The backlog of absent fields is expected and shrinking. A typo is not.
        for role in spec_conformance.audit()["roles"]:
            for finding in role["findings"]:
                with self.subTest(role=role["role"], path=finding["path"]):
                    self.assertNotIn(finding["point"],
                                     ("SPEC_PATH_MALFORMED", "SPEC_ROOT_UNKNOWN"))

    def test_every_requirement_carries_the_phrase_it_came_from(self):
        # A path with no phrase cannot be checked against the prose by a reviewer,
        # which is the half of this that no gate can do.
        for spec in spec_conformance.role_specs():
            for row in spec_conformance.requirements(spec):
                with self.subTest(spec=spec.name, path=row["path"]):
                    self.assertTrue(row["phrase"], row["path"])

    def test_a_node_with_both_properties_and_a_combinator_keeps_its_properties(self):
        # Found by the gate reporting a field it had just been shown. scene_instance
        # names its fields and then uses anyOf to say that exactly one of two must be
        # present -- the ordinary way to write that -- and the first resolver dropped
        # the node's own properties in favour of the branches'.
        for path in ("representation.scene_instances[].microtopic_ref",
                     "representation.scene_instances[].question_ref",
                     "representation.scene_instances[].datum_refs[]"):
            with self.subTest(path=path):
                self.assertEqual(self.resolve(path), "", path)

    def test_the_whole_backlog_is_closed(self):
        # R1's exit condition. This is the assertion that makes --enforce meaningful:
        # once it holds, a spec requiring something with no home breaks the build.
        report = spec_conformance.audit()
        self.assertEqual(report["without_a_home"], 0,
                         [f for r in report["roles"] for f in r["findings"]])
        self.assertTrue(report["passed"])


class SweepRunsTheDifferentiationCheck(unittest.TestCase):
    """The A/B rule is enforced over every bucket, not only the one a test names.

    It is checked on the compiled plan rather than on the records, because the rule is
    about what a learner is asked to do and in what order, and only the plan says that.
    """

    def test_every_subject_passes_today(self):
        report = check_subjects.run()
        for row in report["subjects"]:
            with self.subTest(subject=row["subject"]):
                self.assertEqual([f for f in row["findings"] if "ELICITATION" in f
                                  or "OBLIGATION_WITHOUT" in f], [])

    def test_every_compilable_bucket_is_actually_checked(self):
        # The failure this prevents is a check that passes because it ran on nothing.
        # Both implemented subjects must contribute at least one bucket.
        for subject in check_subjects.subjects():
            packages = [json.loads(p.read_text(encoding="utf-8"))
                        for p in sorted((subject / "library").glob("*.json"))]
            if not packages:
                continue
            buckets = [b["id"] for package in packages for b in package.get("buckets", [])]
            with self.subTest(subject=subject.name):
                self.assertTrue(buckets)
                self.assertEqual(check_subjects._differentiation_findings(subject, packages), [])

    def test_removing_an_elicitation_makes_the_sweep_fail(self):
        # Planted against a copied tree, because the assertion is that the sweep reports
        # it -- not that some function does when called directly.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("Shared", "Physics", "Mathematics", "Chemistry"):
                shutil.copytree(REPO / name, root / name)
            target = next(root.glob("Mathematics/library/*.json"))
            package = json.loads(target.read_text(encoding="utf-8"))
            for row in package["microtopics"]:
                row.pop("elicitation", None)
            target.write_text(json.dumps(package, indent=2, ensure_ascii=False), encoding="utf-8")
            report = check_subjects.run(root)
        self.assertFalse(report["passed"])
        found = [f for row in report["subjects"] for f in row["findings"]
                 if "OBLIGATION_WITHOUT_ELICITATION" in f]
        self.assertEqual(len(found), 3, found)


class SpecDelivery(unittest.TestCase):
    """A requirement must reach the learner, not merely have somewhere to live.

    R1 proved every `requires` path has a schema home. This is the comparison neither
    R1 nor anything else made: does a compiled product carry it. Two products do not,
    and every gate was green over them.
    """

    def setUp(self):
        self.schema = json.loads(
            (REPO / spec_conformance.SCHEMA).read_text(encoding="utf-8"))
        self.roots = spec_conformance.record_types(self.schema)

    def segments(self, path):
        return [spec_conformance.SEGMENT.match(s) for s in path.split(".")]

    def test_a_path_walks_the_arrays_it_crosses(self):
        record = {"teaching_path": [{"why_valid": "first"}, {"why_valid": "second"}]}
        self.assertEqual(
            spec_delivery.values_at(record, self.segments("teaching_path[].why_valid")),
            ["first", "second"])

    def test_a_path_that_is_not_there_yields_nothing_rather_than_raising(self):
        self.assertEqual(spec_delivery.values_at({}, self.segments("a.b[].c")), [])

    def test_a_short_value_is_undecidable_rather_than_guessed(self):
        # A false DELIVERED is the one outcome this tool must never produce: an enum or
        # an id fragment can appear in compiled output by coincidence.
        rows = self.rows_for("Mathematics")
        undecidable = [r for r in rows if r.get("state") == "UNDECIDABLE"]
        self.assertTrue(undecidable)
        for row in undecidable:
            with self.subTest(path=row["path"]):
                held = spec_delivery.authored(self.records("Mathematics"), row["path"], self.roots)
                self.assertLess(max(len(v) for v in held), spec_delivery.DECIDABLE_LENGTH)

    def records(self, subject):
        from Shared.library.resolve import build_index  # noqa: PLC0415
        return build_index([json.loads(p.read_text(encoding="utf-8"))
                            for p in sorted((REPO / subject / "library").glob("*.json"))])

    def rows_for(self, subject):
        report = spec_delivery.audit_subject(REPO / subject, self.schema)
        return report["rows"]

    def test_something_is_delivered_so_the_check_is_not_vacuous(self):
        states = [r.get("state") for r in self.rows_for("Mathematics")]
        self.assertIn("DELIVERED", states)
        self.assertGreater(states.count("DELIVERED"), 10, states)

    def test_core1a_delivers_the_misconception_it_requires(self):
        """The sharpest finding R1.5 made, now closed.

        _teaching_text emitted misconceptions for CORE1B only -- and once Core1B
        compiled from elicitation instead, that branch survived solely as a fallback, so
        the wrong path reached neither product. Core1A's own spec says what that costs:
        "A misconception the learner never hears is a misconception they keep."

        Asserted for both subjects, because the defect was in shared code and fixing it
        for the subject a test happens to name would leave the other broken.
        """
        for subject in ("Mathematics", "Physics"):
            rows = {(r["role"], r["path"]): r["state"]
                    for r in self.rows_for(subject) if "path" in r}
            for field in ("wrong_idea", "diagnostic_prompt", "repair"):
                with self.subTest(subject=subject, field=field):
                    self.assertEqual(rows[("CORE1A", f"microtopic.misconceptions[].{field}")],
                                     "DELIVERED")

    def test_core1a_delivers_what_it_assumes_and_what_can_be_checked(self):
        # The other two Core1A gaps R1.5 found. entry_assumptions is named first in its
        # required content and reached nowhere: a learner who could not do it was on the
        # wrong page with no way to find out.
        for subject in ("Mathematics", "Physics"):
            rows = {(r["role"], r["path"]): r["state"]
                    for r in self.rows_for(subject) if "path" in r}
            for path in ("microtopic.entry_assumptions[]", "relation.checks[]"):
                with self.subTest(subject=subject, path=path):
                    self.assertEqual(rows[("CORE1A", path)], "DELIVERED")

    def test_the_two_products_frame_the_wrong_path_differently(self):
        # Both carry it; that is the coverage rule. They must not carry it identically,
        # which is the A/B rule -- Core1A reveals it inside a completed construction,
        # Core1B poses it as a prediction before anything is revealed.
        from Shared.library.compile_inputs import (  # noqa: PLC0415
            build_index, compile_bucket, load_packages)
        records = build_index(load_packages(sorted((REPO / "Physics/library").glob("*.json"))))
        compiled = compile_bucket(records, "BUCKET-RELATIVE-MOTION", topic_id="t", title="t",
                                  subject="Physics",
                                  practice_control={"mode": "DESIGN_PREVIEW",
                                                    "purpose": "PRACTICE"})
        texts = {p["core"]: "\n".join(b.get("text", "") for b in p["units"][0]["blocks"])
                 for p in compiled["plan"]["products"]}
        self.assertIn("Tell them apart:", texts["CORE1A"])
        self.assertNotIn("Predict first:", texts["CORE1A"])
        self.assertIn("A common wrong idea", texts["CORE1B"])

    def test_source_hints_do_not_manufacture_core2_from_authored_practice(self):
        # Core2 owns source-supplied hints, so an AUTHORED Mathematics practice question
        # must not make that role appear delivered. The projection-pipeline tests cover
        # preservation of question hints into legitimate practice blocks; this regression
        # check protects the ownership boundary and the compiler's non-dropping projection.
        subject_rows = self.rows_for("Mathematics")
        core2 = [r for r in subject_rows if r["role"] == "CORE2" and "path" not in r]
        self.assertEqual(core2, [{"role": "CORE2", "state": "NOT_COMPILED_HERE"}])
        source = (REPO / "Shared/library/compile_inputs.py").read_text(encoding="utf-8")
        self.assertNotIn('"hints": []', source)

    def test_the_compiler_drops_nothing_the_library_holds(self):
        # The enforcement line. A compiler that drops authored content is a defect; a
        # path nobody has written yet is a backlog, counted and named on every run.
        report = spec_delivery.audit()
        self.assertEqual(report["dropped_by_the_compiler"], 0,
                         [f for s in report["subjects"] for f in s["findings"]])
        self.assertTrue(report["passed"])

    def test_the_unwritten_backlog_is_named_rather_than_only_counted(self):
        report = spec_delivery.audit()
        self.assertGreater(report["not_yet_written"], 0, "nothing is owed, so this is vacuous")
        for subject in report["subjects"]:
            for row in subject.get("unwritten", ()):
                with self.subTest(row=row):
                    self.assertGreaterEqual(len(row.split(": ")), 3, row)

    def test_a_container_path_counts_what_is_inside_it(self):
        # The first measurement read a full container as UNAUTHORED, because the walker
        # stopped at it and returned nothing. Seven paths were counted as unwritten with
        # the content sitting inside them.
        record = {"hints": [{"text": "a hint long enough to be found", "reveals": "METHOD"}]}
        self.assertIn("a hint long enough to be found",
                      spec_delivery.values_at(record, self.segments("hints[]")))

    def test_a_role_that_compiles_nothing_here_is_said_once_not_per_requirement(self):
        # Core2 compiles no product for this Mathematics bucket (it has no source items yet;
        # Core2B gained transfer tasks in the Phase 6 pilot). Repeating that for each of its
        # requirements would bury the findings that are real.
        rows = self.rows_for("Mathematics")
        core2 = [r for r in rows if r["role"] == "CORE2"]
        self.assertEqual(core2, [{"role": "CORE2", "state": "NOT_COMPILED_HERE"}])


class CapabilityCollisions(unittest.TestCase):
    """One skill must have one id, and a prerequisite must not carry an untaught rung.

    Both findings land on the same two capabilities -- the ones delegated to another
    subject -- which is one root cause with two symptoms.
    """

    def test_the_committed_tree_reports_exactly_the_known_two(self):
        report = capability_collisions.audit()
        self.assertGreater(report["capabilities"], 0, "no capabilities, so this asserts nothing")
        forked = {f["capability"] for f in report["findings"]
                  if f["point"] == "CAPABILITY_NAMESPACE_FORKED"}
        untaught = {f["capability"] for f in report["findings"]
                    if f["point"] == "DISCRIMINATION_TAUGHT_BY_NOTHING"}
        self.assertEqual(forked, {"CAP-SIGNED-PAIR", "CAP-RIGHT-TRIANGLE"})
        self.assertEqual(untaught, forked, "the same two, which is the point")

    def test_a_fork_quotes_both_criteria_because_that_is_the_merge_evidence(self):
        # A merge proposal without both texts is not reviewable, and this gate must not
        # merge: collapsing two ids rewrites every prerequisite graph naming either.
        for finding in capability_collisions.audit()["findings"]:
            if finding["point"] != "CAPABILITY_NAMESPACE_FORKED":
                continue
            with self.subTest(stem=finding["capability"]):
                self.assertEqual(len(finding["success_criteria"]), 2)
                for text in finding["success_criteria"].values():
                    self.assertTrue(text.strip())
                self.assertIn("criteria_agree", finding)

    def test_it_reports_rather_than_resolves(self):
        source = (REPO / "Shared/tools/capability_collisions.py").read_text(encoding="utf-8")
        self.assertNotIn("def merge", source)
        self.assertIn("never resolves them", source)

    def test_the_same_id_in_two_packages_is_caught(self):
        declared = {"CAP-X": [{"id": "CAP-X", "_package": "A", "success_criterion": "Do a thing."},
                              {"id": "CAP-X", "_package": "B", "success_criterion": "Do a thing."}]}
        points = [f["point"] for f in capability_collisions.findings(declared, taught=set())]
        self.assertIn("CAPABILITY_DECLARED_TWICE", points)

    def test_a_discrimination_a_microtopic_teaches_is_not_a_finding(self):
        # The guard against the version of this gate I threw away. Matching on "and"
        # fired on 9 of 12 capabilities, 6 wrongly -- "reverse, translate, add
        # tail-to-head, and reconcile" is one composite procedure, not a rider.
        declared = {"CAP-Y": [{"id": "CAP-Y", "_package": "A",
                               "success_criterion": "State a magnitude as nonnegative and a "
                                                    "component as signed, without confusing them."}]}
        self.assertEqual(capability_collisions.findings(declared, taught={"CAP-Y"}), [])
        self.assertEqual([f["point"] for f in
                          capability_collisions.findings(declared, taught=set())],
                         ["DISCRIMINATION_TAUGHT_BY_NOTHING"])

    def test_a_composite_procedure_is_not_mistaken_for_a_rider(self):
        declared = {"CAP-Z": [{"id": "CAP-Z", "_package": "A",
                               "success_criterion": "Reverse the vector, translate it without "
                                                    "rotating, and add tail-to-head."}]}
        self.assertEqual(capability_collisions.findings(declared, taught=set()), [])


class MatrixConformance(unittest.TestCase):
    """A matrix may reference the library. It may not restate it, or outrank it.

    Two rules, both the A4 discipline on a new layer: the library decides whether a rung
    exists, and where a record exists it owns its jump, misconception and exit task.
    """

    def board(self):
        return json.loads((REPO / "Physics/matrices/relative-motion.rungs.json")
                          .read_text(encoding="utf-8"))

    def plant(self, mutate):
        board = self.board()
        mutate(board)
        mics, dimensions = matrix_conformance.library("Physics")
        return [f["point"] for f in matrix_conformance.findings(board, mics, dimensions)]

    def test_the_committed_matrix_passes(self):
        report = matrix_conformance.audit()
        self.assertGreater(report["matrices"], 0, "no matrix, so this asserts nothing")
        self.assertEqual(report["findings"], 0,
                         [f for b in report["boards"] for f in b["findings"]])

    def test_restating_a_record_is_refused(self):
        # The defect that matters most: a second copy of a jump or a misconception is a
        # second authority, and the two drift.
        self.assertEqual(self.plant(lambda b: b["rungs"][1].update(aha="Restated here.")),
                         ["MATRIX_RESTATES_THE_RECORD"])

    def test_the_library_decides_whether_a_rung_exists(self):
        self.assertEqual(
            self.plant(lambda b: b["rungs"][0].update(provenance="SOURCE",
                                                      microtopic_ref="MIC-NOT-REAL")),
            ["PROVENANCE_DISAGREES_WITH_LIBRARY"])

    def test_an_absent_claim_over_a_real_record_is_also_refused(self):
        # Both directions, because either disagreement means the matrix is stale.
        self.assertIn("PROVENANCE_DISAGREES_WITH_LIBRARY",
                      self.plant(lambda b: b["rungs"][1].update(provenance="ABSENT")))

    def test_the_ladder_must_ascend_and_not_repeat(self):
        self.assertEqual(self.plant(lambda b: b["rungs"][1].update(ladder_position=5)),
                         ["LADDER_OUT_OF_ORDER"])
        self.assertIn("LADDER_POSITION_REUSED",
                      self.plant(lambda b: b["rungs"][1].update(
                          ladder_position=b["rungs"][0]["ladder_position"])))

    def test_a_phase_with_no_invariant_is_refused(self):
        self.assertEqual(
            self.plant(lambda b: b["rungs"][3]["controlled_variation"][0].update(hold="  ")),
            ["PHASE_HOLDS_NOTHING"])

    def test_a_fifth_spelling_of_the_four_dimensions_is_refused(self):
        # question_family.demand_dimensions owns the vocabulary. CONTEXT is the prose
        # name for novelty, and accepting it would make a third spelling.
        self.assertEqual(self.plant(lambda b: b["transfer"][0].update(dimension="CONTEXT")),
                         ["TRANSFER_DIMENSION_UNDECLARED"])

    def test_a_repair_route_must_name_a_rung_of_this_ladder(self):
        self.assertEqual(self.plant(lambda b: b["transfer"][0].update(repair_to="R9")),
                         ["TRANSFER_REPAIRS_TO_NO_RUNG"])

    def test_withheld_information_must_be_narrower_than_the_demand(self):
        # If they are the same sentence the row says nothing a hint could violate, so
        # collapse becomes undetectable -- which is the whole purpose of the field.
        self.assertEqual(
            self.plant(lambda b: b["transfer"][0].update(
                information_not_handed_over=b["transfer"][0]["changed_demand"])),
            ["WITHHELD_RESTATES_THE_DEMAND"])

    # Every committed rung now references a record, so a record-less row is built here
    # rather than borrowed from a subtopic. The rule is subject-neutral; pinning it to
    # relative motion's R1 made it break the day that rung was authored.
    RECORDLESS = {"rung": "RX", "ladder_position": 15, "provenance": "SYNTHESIS",
                  "aha": "A thing measured one way is not the same as a thing measured another.",
                  "learner_owns": ["Can report a single reading."],
                  "misconception": {"wrong_idea": "One reading settles it.",
                                    "diagnostic_prompt": "Two readings agree. Same thing?",
                                    "repair": "Say what each was read against."},
                  "closure": "Decide whether two readings describe one thing."}

    def synthetic(self, mutate=None):
        row = json.loads(json.dumps(self.RECORDLESS))
        if mutate:
            mutate(row)
        mics, dimensions = matrix_conformance.library("Physics")
        return [f["point"] for f in
                matrix_conformance.findings({"rungs": [row]}, mics, dimensions)]

    def test_a_rung_nothing_teaches_must_still_say_what_it_is(self):
        # The hole the restatement rule left. A row with a position and nothing else
        # passed every other check and compiled a brief reading "(from the record)",
        # naming a record the same row says does not exist.
        self.assertEqual(self.synthetic(), [])
        self.assertEqual(self.synthetic(lambda r: r.pop("aha")), ["RUNG_NAMES_NO_JUMP"])

    def test_a_constructed_rung_carries_what_no_record_holds_for_it(self):
        self.assertEqual(self.synthetic(lambda r: r.pop("closure")),
                         ["SYNTHESIS_INCOMPLETE"])

    def test_absent_may_name_the_hole_and_stop(self):
        # ABSENT is the honest answer when the rung cannot be constructed. Demanding a
        # misconception and an exit task for it would be demanding invention, which is
        # the failure every gate here exists to prevent.
        def strip(row):
            row["provenance"] = "ABSENT"
            for field in ("learner_owns", "misconception", "closure"):
                row.pop(field)
        self.assertEqual(self.synthetic(strip), [])

    # Shapes a parallel author can produce. These promise findings, not tracebacks: a
    # stack trace names no rule, and the committed board is too well formed to reach them.
    MALFORMED = {
        "rungs is a string": {"subject": "Physics", "rungs": "nope"},
        "a rung is a string": {"subject": "Physics", "rungs": ["R1"]},
        "a rung is empty": {"subject": "Physics", "rungs": [{}]},
        "controlled_variation is null": {"subject": "Physics", "rungs": [
            {"rung": "R1", "ladder_position": 1, "provenance": "ABSENT",
             "controlled_variation": None}]},
        "a transfer row is empty": {"subject": "Physics", "rungs": [], "transfer": [{}]},
        "family is a list": {"subject": "Physics", "rungs": [], "family": []},
    }

    def test_structure_is_reported_before_meaning_is_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Physics/matrices").mkdir(parents=True)
            (root / "Physics/matrices/broken.rungs.json").write_text(
                json.dumps({"matrix_id": "X", "subject": "Physics", "bucket_id": "B",
                            "topic": "t", "subtopic": "s", "rungs": "nope"}),
                encoding="utf-8")
            report = matrix_conformance.audit(root)
        self.assertEqual([f["point"] for f in report["boards"][0]["findings"]],
                         ["MATRIX_STRUCTURE"])
        self.assertFalse(report["passed"])

    def test_the_ceiling_audit_never_raises_on_a_malformed_board(self):
        caps, mics = author_brief.capability_chain("Physics")
        for name, board in self.MALFORMED.items():
            with self.subTest(shape=name):
                self.assertEqual(ceiling_audit.findings(board, caps, mics), [])

    def test_support_may_not_hand_over_the_invariant_demand(self):
        # The collapse from the support side. Remove the decision and what is left is
        # transcription wearing a practice label.
        self.assertEqual(
            self.plant(lambda b: b["family"]["support_ladder"][0].update(
                handed_over=b["family"]["invariant_demand"])),
            ["SUPPORT_HANDS_OVER_THE_DEMAND"])

    def test_one_row_per_support_level(self):
        self.assertEqual(
            self.plant(lambda b: b["family"]["support_ladder"][1].update(level="high")),
            ["SUPPORT_LEVEL_REUSED"])

    def test_every_transfer_row_carries_all_four_parts(self):
        for row in self.board()["transfer"]:
            with self.subTest(dimension=row["dimension"]):
                for field in ("changed_demand", "information_not_handed_over", "repair_to"):
                    self.assertTrue(row[field].strip())


class LearnerEvidence(unittest.TestCase):
    """A claim about a learner must be backed by what was seen, or say it is a waiver.

    Profiles left the packages because a learner is not a property of a physics package:
    the two that lived inside one meant the same learner studying a second bucket needed
    a duplicate, and capabilities cross subjects so a package-scoped profile can never
    answer whether a prerequisite is held.
    """

    def test_no_package_holds_a_profile_any_more(self):
        for path in sorted(REPO.glob("*/library/*.v1.json")):
            with self.subTest(package=path.name):
                self.assertEqual(
                    json.loads(path.read_text(encoding="utf-8")).get("practice_profiles"), [])

    def test_the_committed_profiles_pass(self):
        report = learner_evidence.audit()
        self.assertEqual(report["profiles"], 2)
        self.assertEqual(report["findings"], [])

    def test_a_profile_reference_still_resolves_across_the_boundary(self):
        # practice_profile_ref now leaves the library, like gate_relation_ref. It must
        # still resolve -- just by its own gate rather than by the library resolver.
        from Shared.library.resolve import EXTERNAL_REF_KEYS  # noqa: PLC0415
        self.assertIn("practice_profile_ref", EXTERNAL_REF_KEYS)
        referenced = learner_evidence.referenced_profiles()
        self.assertTrue(referenced, "nothing references a profile, so this asserts nothing")
        self.assertNotIn("PROFILE_REF_DANGLING",
                         [f["point"] for f in learner_evidence.audit()["findings"]])

    def plant(self, profile):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("Physics", "Mathematics", "Chemistry", "Shared"):
                shutil.copytree(REPO / name, root / name)
            (root / "Learners/profiles").mkdir(parents=True)
            (root / "Learners/profiles/p.json").write_text(json.dumps(profile), encoding="utf-8")
            return [f["point"] for f in learner_evidence.audit(root)["findings"]]

    def test_an_estimate_without_a_waiver_is_refused(self):
        # An estimate is a decision, not a measurement, so it must carry the instruction
        # it is following instead.
        self.assertIn("CLAIM_WITHOUT_EVIDENCE_OR_WAIVER", self.plant({
            "profile_id": "P", "provenance": "OWNER_ESTIMATE", "held": {},
            "knowledge_percentage": 70, "measured_fit_claim": False}))

    def test_demonstrated_without_an_observation_is_refused(self):
        self.assertIn("DEMONSTRATED_WITHOUT_AN_OBSERVATION", self.plant({
            "profile_id": "P", "provenance": "DIAGNOSTIC",
            "held": {"CAP-SIGNED-PAIR": "DEMONSTRATED"},
            "observation_refs": [], "measured_fit_claim": False}))

    def test_fit_cannot_be_claimed_without_diagnosis(self):
        # A successfully generated book is not evidence of fit.
        self.assertIn("FIT_CLAIMED_WITHOUT_DIAGNOSIS", self.plant({
            "profile_id": "P", "provenance": "OWNER_ESTIMATE", "held": {},
            "owner_waiver": {"instruction_ref": "d.md", "instruction": "Proceed simply."},
            "measured_fit_claim": True}))

    def test_a_capability_no_subject_declares_is_refused(self):
        self.assertIn("HELD_CAPABILITY_UNKNOWN", self.plant({
            "profile_id": "P", "provenance": "UNKNOWN", "held": {"CAP-INVENTED": "MISSING"},
            "owner_waiver": {"instruction_ref": "d.md", "instruction": "No evidence."},
            "measured_fit_claim": False}))

    def test_the_percentage_is_stored_and_never_selected_from(self):
        # The rule the role specs state: mastery of a prerequisite may not be read off an
        # aggregate. Both committed profiles carry null, which is the honest value.
        source = (REPO / "Shared/library/learner-profile.schema.json").read_text(encoding="utf-8")
        self.assertIn("never computes from", source)
        for path in sorted((REPO / "Learners/profiles").glob("*.json")):
            with self.subTest(profile=path.name):
                self.assertIsNone(json.loads(path.read_text(encoding="utf-8"))
                                  ["knowledge_percentage"])


class AuthorBrief(unittest.TestCase):
    """The brief is compiled, never written. What it says is what the matrix and the
    library say, and where neither says anything it says AUTHOR_REQUIRED rather than
    describing some other subtopic.
    """

    BUCKET = "BUCKET-RELATIVE-MOTION"

    def board(self):
        return author_brief.matrix("Physics", self.BUCKET)

    def routing(self, knowledge, core):
        return "\n".join(author_brief.resolve(self.board(), knowledge, core)[1])

    def test_the_support_levels_are_the_purpose_vocabularys(self):
        # One spelling of four things. The thresholds are engine policy; the names are not
        # the engine's to coin.
        vocabulary = json.loads((REPO / "Shared/vocabularies/purpose.json")
                                .read_text(encoding="utf-8"))
        declared = {purpose["support"] for purpose in vocabulary["purposes"]}
        self.assertTrue({level for _, level in author_brief.SUPPORT} <= declared)

    def test_a_teaching_core_resolves_a_percentage_to_a_rung(self):
        rung, lines = author_brief.resolve(self.board(), 20, "CORE1A")
        self.assertEqual(rung, "R1")
        self.assertIn("ladder position, not a learner estimate", "\n".join(lines))

    def test_a_percentage_between_rungs_is_a_hole_rather_than_a_depth(self):
        rung, lines = author_brief.resolve(self.board(), 45, "CORE1A")
        self.assertIsNone(rung)
        self.assertIn("STOP -- no rung sits at this position", "\n".join(lines))

    def test_a_practice_core_reads_the_same_number_as_routing(self):
        text = self.routing(80, "CORE2B")
        self.assertIn("routing input", text)
        self.assertIn("support level : low", text)

    def test_what_a_support_level_hands_over_comes_from_the_matrix(self):
        # It used to be a constant in the engine reading "observer named, axes declared" --
        # true of relative motion and meaningless for thermodynamics.
        ladder = {row["level"]: row["handed_over"]
                  for row in self.board()["family"]["support_ladder"]}
        self.assertIn(ladder["low"], self.routing(80, "CORE2A"))

    def test_a_family_with_no_ladder_row_says_so_rather_than_guessing(self):
        board = self.board()
        board["family"]["support_ladder"] = []
        self.assertIn("AUTHOR_REQUIRED",
                      "\n".join(author_brief.resolve(board, 80, "CORE2A")[1]))

    def test_the_practice_brief_carries_the_family(self):
        text = "\n".join(author_brief.practice(self.board(), "CORE2A"))
        self.assertIn(self.board()["family"]["difficult_move"], text)

    def test_core2a_brief_defines_familiar_demand_not_surface_mutation(self):
        text = "\n".join(author_brief.practice(self.board(), "CORE2A"))
        self.assertIn("familiar same-family application", text)
        self.assertIn("synthetic", text)
        self.assertIn("not required", text)
        self.assertNotIn("Vary the numbers, the objects or the cover story", text)

    def test_only_the_transfer_product_reads_the_transfer_rows(self):
        board = self.board()
        dimension = board["transfer"][0]["dimension"]
        self.assertNotIn(dimension, "\n".join(author_brief.practice(board, "CORE2A")))
        self.assertIn(dimension, "\n".join(author_brief.practice(board, "CORE2B")))

    def test_every_transfer_row_reaches_the_brief_with_what_it_withholds(self):
        board = self.board()
        text = "\n".join(author_brief.practice(board, "CORE2B"))
        for row in board["transfer"]:
            with self.subTest(dimension=row["dimension"]):
                self.assertIn(row["information_not_handed_over"], text)
                self.assertIn(row["repair_to"], text)

    def test_core2b_without_a_transfer_row_refuses_rather_than_repeating_the_family(self):
        board = self.board()
        board["transfer"] = []
        text = "\n".join(author_brief.practice(board, "CORE2B"))
        self.assertIn("STOP -- this subtopic declares no transfer row", text)

    def test_an_absent_rung_gets_the_rung_authoring_contract_not_a_product_one(self):
        # Driven from the state rather than from a named rung: relative motion no longer
        # has a record-less one, and the contract is not that subtopic's property.
        caps, mics = author_brief.capability_chain("Physics")
        state = author_brief.rung_state({"rung": "RX", "microtopic_ref": "MIC-NOT-REAL"},
                                        caps, mics)
        self.assertEqual(state["state"], "ABSENT")
        self.assertTrue(state["root_capabilities"], "no roots, so the contract is empty")
        self.assertTrue(state["conjunctive_roots"],
                        "the two known conjunctive roots should still be named")

    def test_the_ceiling_reaches_the_brief_because_nothing_else_carries_it(self):
        text = author_brief.brief("Physics", self.BUCKET, "R1", "CORE1A")
        row = next(r for r in self.board()["rungs"] if r["rung"] == "R1")
        for word in row["ceiling"]:
            with self.subTest(word=word):
                self.assertIn(word, text)

    def test_a_rung_with_a_record_binds_to_it_rather_than_restating_it(self):
        text = author_brief.brief("Physics", self.BUCKET, "R3", "CORE1A")
        self.assertIn("Bind to MIC-SAME-TIME", text)


class ResolveRequest(unittest.TestCase):
    """A request is the production input every gate below it assumed and none provided.

    Two rules carry into this layer. A knowledge input selects the ENTRY rung and never
    changes what a rung teaches; and a percentage is a decision, so it cannot be typed
    into a request without saying so.
    """

    REQUEST = REPO / "Requests/relative-motion-g9.request.json"

    def request(self):
        return json.loads(self.REQUEST.read_text(encoding="utf-8"))

    def points(self, mutate=None):
        request = self.request()
        if mutate:
            mutate(request)
        return [f["point"] for f in resolve_request.plan(request)["findings"]]

    def rows(self):
        board = resolve_request.ladder("Physics", "BUCKET-RELATIVE-MOTION")
        return sorted(board["rungs"], key=lambda r: r.get("ladder_position", 0))

    def core(self, report, name):
        return next(c for c in report["cores"] if c["core"] == name)

    def test_the_committed_request_resolves(self):
        report = resolve_request.audit()
        self.assertGreater(report["requests"], 0, "no request, so this asserts nothing")
        self.assertEqual(report["findings"], 0,
                         [f for r in report["plans"] for f in r["findings"]])

    def test_a_bare_percentage_cannot_be_typed_into_a_request(self):
        # The A4 rule made structural. knowledge_percentage is stored and never computed
        # from, so the only way to supply one here is inside an owner_estimate that says
        # on its face that it is a decision.
        import jsonschema
        schema = json.loads((REPO / "Shared/library/request.schema.json")
                            .read_text(encoding="utf-8"))
        request = self.request()
        request["learner"] = {"knowledge_percentage": 20}
        self.assertTrue(list(jsonschema.Draft202012Validator(schema)
                             .iter_errors(request)))

    def test_two_sources_of_placement_at_once_are_refused(self):
        import jsonschema
        schema = json.loads((REPO / "Shared/library/request.schema.json")
                            .read_text(encoding="utf-8"))
        request = self.request()
        request["learner"]["owner_entry"] = {"rung": "R3", "by": "o", "instruction": "i"}
        self.assertTrue(list(jsonschema.Draft202012Validator(schema)
                             .iter_errors(request)))

    def test_a_practice_core_without_a_purpose_is_refused(self):
        # The question that was never asked. There is no default that would not be a guess.
        self.assertEqual(self.points(lambda r: r["practice"].pop("CORE2A")),
                         ["PRACTICE_CORE_WITHOUT_A_PURPOSE"])

    def test_transfer_requested_under_a_purpose_that_withholds_it(self):
        self.assertEqual(
            self.points(lambda r: r["practice"]["CORE2B"].update(purpose="STARTER")),
            ["TRANSFER_REQUESTED_UNDER_A_PURPOSE_THAT_WITHHOLDS_IT"])

    def test_a_purpose_the_vocabulary_does_not_declare(self):
        self.assertEqual(
            self.points(lambda r: r["practice"]["CORE2A"].update(purpose="REVISION_ISH")),
            ["PURPOSE_UNKNOWN"])

    def test_a_purpose_for_a_product_nobody_asked_for(self):
        self.assertEqual(self.points(lambda r: r["cores"].remove("CORE2B")),
                         ["PURPOSE_FOR_A_CORE_NOT_REQUESTED"])

    def test_an_owner_may_name_the_entry_rung_but_not_invent_one(self):
        def name(rung):
            return lambda r: r.__setitem__(
                "learner", {"owner_entry": {"rung": rung, "by": "owner",
                                            "instruction": "placement decision"}})
        self.assertEqual(self.points(name("R4")), [])
        self.assertEqual(self.points(name("R2")), ["ENTRY_RUNG_NOT_ON_THE_LADDER"])

    def test_an_owner_estimate_between_rungs_routes_conservatively(self):
        request = self.request()
        request["learner"]["owner_estimate"]["knowledge_percentage"] = 45
        report = resolve_request.plan(request)
        self.assertEqual(report["findings"], [])
        # 45 is a practical owner estimate, not a claim of mastery. It chooses the
        # greatest declared coordinate not above it and keeps earlier prerequisites as
        # unverified checks instead of silently marking them demonstrated.
        self.assertEqual(report["entry"]["requested_position"], 45)
        self.assertEqual(report["entry"]["selected_position"], 20)
        self.assertEqual(report["entry"]["why"], "OWNER_ESTIMATE_CONSERVATIVE_FLOOR")
        self.assertEqual(report["entry"]["rung"], "R1")
        self.assertEqual(report["entry"]["prerequisite_checks"], [])

    def test_a_dangling_profile_is_refused(self):
        self.assertEqual(
            self.points(lambda r: r.__setitem__("learner",
                                                {"profile_ref": "PROFILE-NOT-REAL"})),
            ["PROFILE_REF_DANGLING"])

    def test_a_synthetic_profile_is_never_routed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Learners/profiles").mkdir(parents=True)
            (root / "Physics/matrices").mkdir(parents=True)
            shutil.copy(REPO / "Physics/matrices/relative-motion.rungs.json",
                        root / "Physics/matrices/relative-motion.rungs.json")
            (root / "Learners/profiles/synthetic.json").write_text(json.dumps({
                "profile_id": "PROFILE-SYNTHETIC", "provenance": "SYNTHETIC_TEST",
                "held": {}, "measured_fit_claim": False}), encoding="utf-8")
            request = self.request()
            request["learner"] = {"profile_ref": "PROFILE-SYNTHETIC"}
            points = [f["point"] for f in
                      resolve_request.plan(request, root)["findings"]]
        self.assertEqual(points, ["SYNTHETIC_PROFILE_ROUTED"])

    def test_nobody_can_be_placed_on_a_ladder_whose_lower_rungs_have_no_records(self):
        # The refusal is a property of a ladder with a record-less rung below, not of any
        # subtopic: relative motion had one until R1 was authored, and the rule outlives
        # that. A rung with no record declares no capability, so no observation of this
        # learner can say whether they are past it.
        caps, mics = author_brief.capability_chain("Physics")
        rows = [{"rung": "R0", "ladder_position": 5, "provenance": "ABSENT"}] + self.rows()
        entry = resolve_request.entry_from_profile(
            rows, {"held": {"CAP-SAME-TIME": "DEMONSTRATED"}}, caps, mics)
        self.assertEqual(entry["why"], "UNDECIDABLE")
        self.assertEqual(entry["at"], "R0")

    def test_placement_reads_the_capability_map_and_never_an_aggregate(self):
        caps, mics = author_brief.capability_chain("Physics")
        rows = [r for r in self.rows() if r["rung"] != "R1"]
        held = {"CAP-SAME-TIME": "DEMONSTRATED", "CAP-RELATIVE-V": "UNCERTAIN"}
        entry = resolve_request.entry_from_profile(rows, {"held": held}, caps, mics)
        self.assertEqual(entry["rung"], "R4")
        self.assertEqual(entry["capability"], "CAP-RELATIVE-V")

    def test_a_learner_past_every_rung_is_said_so_rather_than_placed_at_the_top(self):
        caps, mics = author_brief.capability_chain("Physics")
        rows = [r for r in self.rows() if r["rung"] != "R1"]
        held = {row: "DEMONSTRATED" for row in
                ("CAP-SAME-TIME", "CAP-RELATIVE-V", "CAP-VECTOR-CHECK")}
        self.assertEqual(
            resolve_request.entry_from_profile(rows, {"held": held}, caps, mics)["why"],
            "ABOVE_THE_LADDER")

    def test_selection_not_dilution(self):
        # A rough owner estimate is useful only if a higher estimate can actually start
        # higher. It selects a suffix of the ladder; it never changes what a rung teaches
        # and it never turns earlier prerequisites into demonstrated mastery.
        def at(position):
            request = self.request()
            request["learner"]["owner_estimate"]["knowledge_percentage"] = position
            return resolve_request.plan(request)
        low, high = at(20), at(70)
        self.assertEqual(low["segment"], ["R1", "R3", "R4", "R5"])
        self.assertEqual(high["entry"]["rung"], "R4")
        self.assertEqual(high["entry"]["why"], "OWNER_ESTIMATE_CONSERVATIVE_FLOOR")
        self.assertEqual(high["segment"], ["R4", "R5"])
        self.assertEqual(high["segment"], low["segment"][-len(high["segment"]):])
        self.assertEqual(
            high["entry"]["prerequisite_checks"],
            ["CAP-SIGNED-PAIR", "CAP-SAME-TIME"],
        )
        self.assertNotIn("held", high["entry"])
        tasks = {s["rung"]: s["task"] for s in self.core(low, "CORE1A")["segment"]}
        for step in self.core(high, "CORE1A")["segment"]:
            with self.subTest(rung=step["rung"]):
                self.assertEqual(step["task"], tasks[step["rung"]])

    def test_purpose_decides_support_with_no_percentage_involved(self):
        # Support and placement were the same number doing two jobs. Changing only the
        # purpose changes the support and leaves the teaching segment untouched.
        def with_purpose(purpose):
            request = self.request()
            request["practice"]["CORE2A"]["purpose"] = purpose
            return resolve_request.plan(request)
        starter, revision = with_purpose("STARTER"), with_purpose("REVISION")
        self.assertEqual(self.core(starter, "CORE2A")["support"], "high")
        self.assertEqual(self.core(revision, "CORE2A")["support"], "low")
        self.assertEqual(starter["segment"], revision["segment"])

    def test_rung_work_is_planned_exactly_where_a_record_is_missing(self):
        # The rule: the task follows the state, never the position on the ladder.
        report = resolve_request.plan(self.request())
        steps = [s for c in report["cores"] for s in c.get("segment", [])]
        self.assertTrue(steps, "no segment, so this asserts nothing")
        for step in steps:
            with self.subTest(rung=step["rung"]):
                self.assertEqual(step["task"] == "AUTHOR_THE_RUNG",
                                 step["state"] == "ABSENT")

    def test_one_request_compiles_every_brief_the_plan_calls_for(self):
        text = resolve_request.briefs(self.request())
        report = resolve_request.plan(self.request())
        for core in report["cores"]:
            for step in core.get("segment", []):
                with self.subTest(core=core["core"], rung=step["rung"]):
                    self.assertIn(
                        f'# Authoring brief -- {core["core"]}, Relative motion, '
                        f'rung {step["rung"]}', text)
        self.assertIn("## Purpose PRACTICE -- support medium", text)
        # Matrix transfer rows are an authoring description, not a question asset.
        # With no bucket-owned CORE2B question the strict resolver blocks the product,
        # so no transfer brief may be emitted.
        self.assertNotIn("## Transfer -- 4 changed demands", text)
        transfer = self.core(report, "CORE2B")
        self.assertEqual(transfer["state"], "BLOCKED")
        self.assertIn("bucket-owned question", transfer["reason"])

    def test_a_refused_request_yields_the_refusal_rather_than_briefs(self):
        request = self.request()
        request["practice"].pop("CORE2A")
        text = resolve_request.briefs(request)
        self.assertIn("PRACTICE_CORE_WITHOUT_A_PURPOSE", text)
        self.assertNotIn("# Authoring brief", text)

    def test_practice_is_blocked_exactly_where_no_rung_has_a_record(self):
        # Found by planning every bucket in the subject rather than the one with a library
        # behind it: twelve reported CORE2A and CORE2B READY while teaching nothing.
        # Practice varies instances of what teaching established; transfer holds truth
        # already taught. Neither survives an empty ladder.
        #
        # Stated as the rule over every bucket, not against one named subtopic: that
        # bucket was BUCKET-PHY-NLM-FIRST-LAW, and it stopped being empty the day its
        # rungs were authored.
        import glob
        checked = 0
        for path in sorted(glob.glob(str(REPO / "Physics/matrices/*.rungs.json"))):
            board = json.loads(Path(path).read_text(encoding="utf-8"))
            request = self.request()
            request["bucket_id"] = board["bucket_id"]
            request["learner"]["owner_estimate"]["knowledge_percentage"] = min(
                r["ladder_position"] for r in board["rungs"])
            report = resolve_request.plan(request)
            caps, mics = author_brief.capability_chain("Physics")
            taught = any(
                author_brief.rung_state(row, caps, mics)["state"] == "PRESENT"
                for row in board["rungs"]
            )
            records = resolve_request.library_records("Physics")
            for name in ("CORE2A", "CORE2B"):
                with self.subTest(bucket=board["bucket_id"], core=name):
                    core = self.core(report, name)
                    exposed = resolve_request.questions_for_core(
                        records, board["bucket_id"], name)
                    purpose = request["practice"][name]["purpose"]
                    routes = resolve_request.purposes()[purpose]["routes_transfer"]
                    if not taught:
                        self.assertEqual(core["state"], "BLOCKED")
                        self.assertIn("no rung of this ladder has a record", core["reason"])
                    elif name == "CORE2B" and not routes:
                        self.assertEqual(core["state"], "WITHHELD")
                    elif exposed:
                        self.assertEqual(core["state"], "READY")
                    else:
                        self.assertEqual(core["state"], "BLOCKED")
                        self.assertIn("bucket-owned question", core["reason"])
            checked += 1
        self.assertGreater(checked, 0, "no matrices, so this asserts nothing")

    def test_practice_is_ready_where_the_ladder_is_taught(self):
        report = resolve_request.plan(self.request())
        self.assertEqual(self.core(report, "CORE2A")["state"], "READY")

    def test_a_withheld_transfer_product_says_why_rather_than_failing_quietly(self):
        request = self.request()
        request["practice"]["CORE2B"]["purpose"] = "STARTER"
        core = self.core(resolve_request.plan(request), "CORE2B")
        self.assertEqual(core["state"], "WITHHELD")
        self.assertIn("coverage gap wearing a transfer label", core["reason"])


class CeilingAudit(unittest.TestCase):
    """A ceiling excludes words from ABOVE a rung, never the rung's own output.

    A rung whose ceiling forbids what it teaches cannot be written: you cannot repair
    "distance is not displacement" without the word displacement. That is a contradiction
    in the file, so it is enforced. A rung whose text uses a word its ceiling correctly
    forbids is a content defect whose repair belongs to that rung's author, so it is
    reported and never fails the build.
    """

    def board(self):
        return json.loads((REPO / "Physics/matrices/vector-representation.rungs.json")
                          .read_text(encoding="utf-8"))

    def synthetic(self):
        """A stable falsifier independent of whichever Physics content happens to migrate."""
        board = {
            "rungs": [
                {
                    "rung": "R1",
                    "ladder_position": 10,
                    "provenance": "SOURCE",
                    "microtopic_ref": "MIC-CEIL-R1",
                    "ceiling": [],
                    "must_contain": [],
                    "controlled_variation": [],
                },
                {
                    "rung": "R2",
                    "ladder_position": 20,
                    "provenance": "SOURCE",
                    "microtopic_ref": "MIC-CEIL-R2",
                    "ceiling": [],
                    "must_contain": [],
                    "controlled_variation": [],
                },
                {
                    "rung": "R3",
                    "ladder_position": 30,
                    "provenance": "SOURCE",
                    "microtopic_ref": "MIC-CEIL-R3",
                    "ceiling": [],
                    "must_contain": [],
                    "controlled_variation": [],
                },
            ]
        }
        caps = {
            "CAP-CEIL-R1": {
                "id": "CAP-CEIL-R1",
                "action": "Distinguish a magnitude from a pair of signed components.",
                "success_criterion": "Name magnitude and components separately.",
                "prerequisite_refs": [],
            },
            "CAP-CEIL-R2": {
                "id": "CAP-CEIL-R2",
                "action": "Read a declared representation.",
                "success_criterion": "Read it.",
                "prerequisite_refs": [],
            },
            "CAP-CEIL-R3": {
                "id": "CAP-CEIL-R3",
                "action": "Construct tail-to-head addition.",
                "success_criterion": "Use the tail-to-head construction.",
                "prerequisite_refs": [],
            },
        }
        mics = {
            "MIC-CEIL-R1": {
                "id": "MIC-CEIL-R1",
                "primary_capability_ref": "CAP-CEIL-R1",
                "inferential_jump": "Separate magnitude from a pair of signed components.",
                "teaching_path": [{
                    "action": "Draw two perpendicular readings.",
                    "why_valid": "Axes declare what each reading means.",
                    "output": "A component pair.",
                }],
            },
            "MIC-CEIL-R2": {
                "id": "MIC-CEIL-R2",
                "primary_capability_ref": "CAP-CEIL-R2",
                "inferential_jump": "Read one declared representation.",
                "teaching_path": [],
            },
            "MIC-CEIL-R3": {
                "id": "MIC-CEIL-R3",
                "primary_capability_ref": "CAP-CEIL-R3",
                "inferential_jump": "Use a tail-to-head construction.",
                "teaching_path": [],
            },
        }
        return board, caps, mics

    def plant(self, mutate, index=0):
        """Return one planted finding from a synthetic rung, not mutable subject content."""
        board, caps, mics = self.synthetic()
        mutate(board)
        return [f["point"] for f in
                ceiling_audit.findings({"rungs": [board["rungs"][index]]}, caps, mics)]

    def test_no_committed_matrix_forbids_its_own_output(self):
        report = ceiling_audit.audit()
        self.assertGreater(report["ceiling_words"], 0, "no ceilings, so this asserts nothing")
        self.assertEqual(report["blocking"], 0,
                         [f for b in report["boards"] for f in b["findings"]
                          if f["point"] == ceiling_audit.BLOCKING])

    def test_forbidding_a_word_the_rung_teaches_is_refused(self):
        self.assertEqual(
            self.plant(lambda b: b["rungs"][0].update(ceiling=["magnitude"])),
            [ceiling_audit.BLOCKING])

    def test_a_source_rungs_own_output_is_read_from_the_record(self):
        # SOURCE rungs carry no `aha` -- the microtopic owns the learner-facing jump.
        board, _, _ = self.synthetic()
        self.assertIsNone(board["rungs"][0].get("aha"))
        self.assertEqual(
            self.plant(lambda b: b["rungs"][0].update(ceiling=["tail-to-head"])), [])
        self.assertEqual(
            self.plant(lambda b: b["rungs"][2].update(ceiling=["tail-to-head"]), index=2),
            [ceiling_audit.BLOCKING])

    def test_a_plural_in_the_jump_still_matches_the_ceiling_word(self):
        # The synthetic R1 says "a pair of signed components". This proves plural matching
        # without freezing the test to one subject package.
        self.assertEqual(
            self.plant(lambda b: b["rungs"][0].update(ceiling=["component"])),
            [ceiling_audit.BLOCKING])

    def test_a_ceiling_word_in_learner_text_is_reported_and_does_not_fail(self):
        def plant(board):
            board["rungs"][0]["ceiling"] = ["quadrant"]
            board["rungs"][0]["must_contain"] = ["Read the quadrant off the diagram."]
        self.assertEqual(self.plant(plant), [ceiling_audit.REPORTED])
        self.assertTrue(ceiling_audit.audit()["passed"])

    def test_author_facing_text_does_not_trip_the_reported_finding(self):
        # `wrong_idea` names the wrong path to the author. Binding the ceiling to it would
        # forbid an author from writing down the misconception the rung exists to kill.
        caps, mics = author_brief.capability_chain("Physics")
        row = {"rung": "R1", "ladder_position": 10, "provenance": "SYNTHESIS",
               "aha": "A thing is not another thing.", "ceiling": ["quadrant"],
               "misconception": {"wrong_idea": "Every reading names a quadrant.",
                                 "diagnostic_prompt": "Which one did you read?",
                                 "repair": "Say what you measured from."},
               "closure": "Say which of two readings is which."}
        self.assertEqual(ceiling_audit.findings({"rungs": [row]}, caps, mics), [])
        row["closure"] = "Name the quadrant."
        self.assertEqual([f["point"] for f in
                          ceiling_audit.findings({"rungs": [row]}, caps, mics)],
                         [ceiling_audit.REPORTED])

    def test_the_ceiling_is_compared_to_the_record_a_learner_actually_reads(self):
        # The matrix row is advice to an author; the record is the explanation. Nothing
        # compared the ceiling to it until relative motion's entry rung was authored.
        self.assertEqual(self.plant(lambda b: b["rungs"][0].update(ceiling=["perpendicular"])),
                         [ceiling_audit.AUTHORED])
        self.assertEqual(self.plant(lambda b: b["rungs"][0].update(ceiling=["determinant"])),
                         [], "a word the record does not use is not a finding")

    def test_a_ceiling_word_in_the_explanation_is_reported_and_does_not_fail(self):
        report = ceiling_audit.audit()
        self.assertGreater(report["in_the_explanation"], 0,
                           "nothing measured, so this asserts nothing")
        self.assertTrue(report["passed"])

    def test_vector_representation_benchmark_ceiling_failure_is_cleared(self):
        # The old Vector Representation R1 explanation crossed its own vocabulary ceiling.
        # After the content migration, the benchmark-named defect must stay cleared; the
        # generic ceiling falsifiers above remain synthetic so future migrations do not
        # require rewriting their expected findings.
        report = ceiling_audit.audit()
        found = {
            f["where"]
            for b in report["boards"]
            for f in b["findings"]
            if f["point"] == ceiling_audit.AUTHORED
            and "vector-representation" in b["matrix"]
        }
        self.assertEqual(
            {w for w in found if w.startswith("R1.")},
            set(),
        )

    def test_every_reported_finding_is_a_true_positive(self):
        # This asserted a list of four. It has been wrong twice since -- once when rungs
        # gained records and their text moved, once when eight subtopics were authored --
        # and each time the fix was to retype the list, which tests nothing. The rule is
        # that a reported word really is a ceiling word this rung's own text uses.
        report = ceiling_audit.audit()
        checked = 0
        for board in report["boards"]:
            rows = {r["rung"]: r for r in matrix_conformance.load(REPO / board["matrix"])["rungs"]}
            for finding in board["findings"]:
                if finding["point"] != ceiling_audit.REPORTED:
                    continue
                rung, word = finding["where"].split(".", 1)
                with self.subTest(matrix=board["matrix"], where=finding["where"]):
                    self.assertIn(word, rows[rung]["ceiling"])
                    self.assertTrue(ceiling_audit.says(
                        word, ceiling_audit.learner_text(rows[rung])))
                checked += 1
        # Non-vacuity is about the audit having done work, not about a defect existing:
        # the tracks cleared the last two reported findings and this guard then demanded
        # one be present. What must never be zero is the ceiling words examined.
        self.assertGreater(report["ceiling_words"], 0, "no ceilings, so this asserts nothing")
        self.assertEqual(report["blocking"], 0)


class RelativeMotionEntryRung(unittest.TestCase):
    """Regression case, not a rule. Authoring R1 is what the subject-neutral machinery was
    built for, so this pins what that one exercise established and nothing more.

    It is kept separate from the rules above on purpose: every failure in this class means
    the relative-motion records moved, and none of them means the blueprint is wrong.
    """

    MICROTOPIC = "MIC-MEASURED-FROM"
    CAPABILITY = "CAP-MEASURED-FROM"

    def package(self):
        return json.loads((REPO / "Physics/library/relative-motion.v1.json")
                          .read_text(encoding="utf-8"))

    def microtopic(self):
        return next(m for m in self.package()["microtopics"] if m["id"] == self.MICROTOPIC)

    def test_the_entry_rung_has_a_record_and_the_matrix_defers_to_it(self):
        board = json.loads((REPO / "Physics/matrices/relative-motion.rungs.json")
                           .read_text(encoding="utf-8"))
        row = next(r for r in board["rungs"] if r["rung"] == "R1")
        self.assertEqual((row["provenance"], row["microtopic_ref"]),
                         ("SOURCE", self.MICROTOPIC))
        for field in ("aha", "learner_owns", "misconception", "closure"):
            self.assertNotIn(field, row, "the record owns this now")

    def test_a_conceptual_rung_carries_no_relation_and_is_still_admitted(self):
        # The architecture question this rung was authored to answer: every microtopic
        # before it bound an equation, so nothing had shown that a rung making a
        # distinction rather than a calculation could exist at all.
        self.assertEqual(self.microtopic()["relation_refs"], [])

    def test_a_qualitative_exit_says_why_it_asserts_no_number(self):
        # The schema already had the answer -- oracle.no_numeric_claim -- so no field was
        # added for this case. Silence would have been the failure.
        oracle = self.microtopic()["exit_task"]["oracle"]
        self.assertEqual(list(oracle), ["no_numeric_claim"])

    def test_its_capability_asserts_one_thing(self):
        capability = next(c for c in self.package()["capabilities"]
                          if c["id"] == self.CAPABILITY)
        self.assertNotIn(" and ", capability["success_criterion"])
        self.assertEqual(capability["prerequisite_refs"], [], "this is the bottom rung")

    def test_the_explanation_respects_its_own_ceiling(self):
        board = json.loads((REPO / "Physics/matrices/relative-motion.rungs.json")
                           .read_text(encoding="utf-8"))
        row = next(r for r in board["rungs"] if r["rung"] == "R1")
        text = ceiling_audit.explanation(self.microtopic())
        for word in row["ceiling"]:
            with self.subTest(word=word):
                self.assertFalse(ceiling_audit.says(word, text))

    def test_a_diagnostic_can_now_place_a_learner_on_this_ladder(self):
        # Before this rung existed the answer was ENTRY_UNDECIDABLE_FROM_THE_PROFILE: the
        # bottom rung declared no capability, so no observation could say whether a
        # learner was past it.
        caps, mics = author_brief.capability_chain("Physics")
        rows = sorted(resolve_request.ladder("Physics", "BUCKET-RELATIVE-MOTION")["rungs"],
                      key=lambda r: r["ladder_position"])
        entry = resolve_request.entry_from_profile(rows, {"held": {}}, caps, mics)
        self.assertEqual((entry["rung"], entry["capability"]), ("R1", self.CAPABILITY))

    def test_the_whole_ladder_is_product_work_with_no_rung_left_to_author(self):
        report = resolve_request.plan(json.loads(
            (REPO / "Requests/relative-motion-g9.request.json").read_text(encoding="utf-8")))
        segment = next(c for c in report["cores"] if c["core"] == "CORE1A")["segment"]
        self.assertEqual([s["rung"] for s in segment], ["R1", "R3", "R4", "R5"])
        self.assertEqual({s["task"] for s in segment}, {"AUTHOR_THE_PRODUCT"})


class PublicationProvenance(unittest.TestCase):
    """A published page says which library records it came from, or says it came from none.

    Every gate in this repository governs the library. Whether the artifact a learner
    opens has anything to do with that library was, until this check, unasked.
    """

    def scaffold(self, tmp, *, declaration=None, plan="{}"):
        root = Path(tmp)
        (root / "Physics/library").mkdir(parents=True)
        shutil.copy(REPO / "Physics/library/relative-motion.v1.json",
                    root / "Physics/library/relative-motion.v1.json")
        run = root / "Physics/content/probe"
        (run / "publication").mkdir(parents=True)
        (run / "inputs").mkdir(parents=True)
        (run / "publication/manifest.json").write_text("{}", encoding="utf-8")
        (run / "inputs/plan.json").write_text(plan, encoding="utf-8")
        if declaration is not None:
            (run / "provenance.json").write_text(json.dumps(declaration), encoding="utf-8")
        return root, run

    def points(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root, run = self.scaffold(tmp, **kwargs)
            return [f["point"] for f in publication_provenance.findings(run, root)[0]]

    def test_the_committed_run_declares_its_basis(self):
        report = publication_provenance.audit()
        self.assertGreater(report["runs"], 0, "no publication, so this asserts nothing")
        self.assertEqual(report["blocking"], 0,
                         [f for r in report["publications"] for f in r["findings"]])

    def test_a_run_that_says_nothing_is_refused(self):
        self.assertEqual(self.points(), ["PUBLICATION_PROVENANCE_UNDECLARED"])

    def test_authoring_beside_the_library_is_allowed_and_an_unexplained_one_is_not(self):
        # The state has to be expressible or it stops being written down, which is how it
        # went unnoticed in the first place.
        self.assertEqual(self.points(declaration={
            "basis": "AUTHORED_OUTSIDE_THE_LIBRARY", "reason": "engine proof before the "
            "library could feed it"}), [])
        self.assertEqual(self.points(declaration={"basis": "AUTHORED_OUTSIDE_THE_LIBRARY"}),
                         ["PUBLICATION_AUTHORED_OUTSIDE_WITHOUT_A_REASON"])

    def test_a_claimed_library_basis_must_name_records_the_library_holds(self):
        # Staleness fires alongside it -- naming one microtopic leaves the rest uncarried
        # -- so this asserts the dangling reference is among the findings, not that it is
        # the only one.
        self.assertIn(
            "PUBLICATION_RECORD_UNKNOWN",
            self.points(declaration={"basis": "LIBRARY", "records": ["MIC-NOT-REAL"]},
                        plan='{"x": "MIC-SAME-TIME"}'))

    def test_a_library_claim_no_plan_supports_is_refused(self):
        points = self.points(declaration={"basis": "LIBRARY", "records": []}, plan="{}")
        self.assertIn("PUBLICATION_CLAIMS_LIBRARY_BASIS_AND_NAMES_NOTHING", points)

    def test_a_rung_authored_after_the_freeze_is_reported_as_stale(self):
        # The detector this exists to have on the day a run IS library-based: a microtopic
        # the library teaches that the frozen page does not carry. Scoped to the buckets
        # the run publishes, so the run has to name one -- it compared against every
        # microtopic in the subject and reported forty omissions for eleven other
        # subtopics the first time a real run was measured.
        points = self.points(
            declaration={"basis": "LIBRARY",
                         "records": ["BUCKET-RELATIVE-MOTION", "MIC-SAME-TIME"]},
            plan='{"x": "MIC-SAME-TIME"}')
        self.assertIn("PUBLICATION_OMITS_A_MICROTOPIC_THE_LIBRARY_TEACHES", points)

    def test_a_run_is_not_asked_for_teaching_that_belongs_to_another_bucket(self):
        points = self.points(
            declaration={"basis": "LIBRARY", "records": ["MIC-SAME-TIME"]},
            plan='{"x": "MIC-SAME-TIME"}')
        self.assertNotIn("PUBLICATION_OMITS_A_MICROTOPIC_THE_LIBRARY_TEACHES", points)

    def test_the_compilers_own_record_list_is_read_rather_than_the_plans_text(self):
        # Scanning for ids cannot be made correct: loose matching counted
        # CAP-RIGHT-TRIANGLE inside CAP-RIGHT-TRIANGLE-BRIDGE, and whole-token matching
        # then missed MIC-MEASURED-FROM inside the block id CORE1A-MIC-MEASURED-FROM-T.
        run = REPO / "Physics/content/relative-motion-library"
        listed = json.loads((run / "inputs/library_records.json").read_text(encoding="utf-8"))
        self.assertIn("MIC-MEASURED-FROM", listed)
        report = publication_provenance.audit()
        row = next(r for r in report["publications"] if r["run"].endswith("library"))
        self.assertEqual(row["declared"], row["in_plan"])

    def test_staleness_is_reported_and_does_not_fail_the_build(self):
        # Republishing is owner work; failing CI would put the decision in the wrong hands.
        self.assertTrue(publication_provenance.audit()["passed"])

    def test_an_unknown_basis_is_not_silently_accepted(self):
        self.assertEqual(self.points(declaration={"basis": "PROBABLY_FINE"}),
                         ["PUBLICATION_BASIS_UNKNOWN"])
