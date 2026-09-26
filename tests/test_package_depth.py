"""Schema 0.2.0: every package migrated, every package loads, every depth gap is a named duty."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import package_depth, package_migrate  # noqa: E402

SCHEMA = json.loads((REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))


def validator():
    import jsonschema  # noqa: PLC0415
    return jsonschema.Draft202012Validator(SCHEMA)


class Migration(unittest.TestCase):
    def test_every_package_is_at_0_2_0_and_the_migration_is_idempotent(self):
        limit = package_migrate.max_decisions()
        for path in package_migrate.package_paths():
            with self.subTest(package=path.name):
                pkg = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(pkg["schema_version"], "0.2.0")
                self.assertEqual(package_migrate.migrate_package(pkg, limit), pkg)

    def test_every_package_loads_against_the_schema(self):
        v = validator()
        for path in package_migrate.package_paths():
            with self.subTest(package=path.name):
                errors = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(json.loads(path.read_text(encoding="utf-8")))]
                self.assertEqual(errors, [])

    def test_migration_restructures_but_never_invents(self):
        pkg = json.loads(next(p for p in package_migrate.package_paths() if p.name == "phy-kin-2d-motion.v1.json").read_text(encoding="utf-8"))
        for m in pkg["microtopics"]:
            for u in m.get("construction_units", []):
                self.assertEqual(u["decision_from"], "inferential_jump")
                self.assertNotIn("decision", u)                   # a pointer, not a copy
                self.assertEqual(u["step_refs"], [s["id"] for s in m["teaching_path"]])
                self.assertEqual(u["independent_checks"], [])     # never filled in by migration
        for q in pkg["questions"]:
            sources = {f"hints[{i}]" for i in range(len(q.get("hints", [])))} | {f"scaffolds[{i}]" for i in range(len(q.get("scaffolds", [])))}
            self.assertEqual({r["from"] for r in q["hint_ladder"]}, sources)
            self.assertTrue(all("text" not in r for r in q["hint_ladder"]))   # no copied text to drift
            self.assertNotIn("independent_check", q)                          # answer.check stays the source
            self.assertIsNone(q["failure_signal"])
            self.assertIsNone((q.get("family_exposure") or {}).get("closure"))

    def test_long_construction_gets_no_unit(self):
        pkg = {"schema_version": "0.1.0", "representations": [], "questions": [], "microtopics": [{
            "id": "MIC-X", "primary_capability_ref": "CAP-X", "inferential_jump": "j", "representation_refs": [],
            "misconceptions": [], "teaching_path": [{"id": f"S{i}"} for i in range(7)]}]}
        out = package_migrate.migrate_package(pkg, 4)
        self.assertNotIn("construction_units", out["microtopics"][0])


class Duties(unittest.TestCase):
    def setUp(self):
        path = next(p for p in package_migrate.package_paths() if p.name == "phy-kin-2d-motion.v1.json")
        self.pkg = json.loads(path.read_text(encoding="utf-8"))
        self.taught = package_depth.taught_capabilities()

    def duties(self, pkg):
        return package_depth.package_duties(pkg, "x", self.taught, 4)

    def test_every_duty_names_a_role_and_contract_rules_that_exist(self):
        rules = {r["id"] for r in json.loads((REPO / "Shared/quality/learner-quality.v1.json").read_text(encoding="utf-8"))["rules"]}
        duties = package_depth.all_duties()
        self.assertGreater(len(duties), 0)
        for d in duties:
            self.assertIn(d["role"], {"RESEARCHER", "AUTHOR", "RENDERER"})
            self.assertTrue(set(d["contract_rules"]) <= rules, d)

    def test_supplying_a_field_removes_exactly_its_duty(self):
        q = next(q for q in self.pkg["questions"] if any(e["core"] == "CORE2A" for e in q["exposure"]))
        before = {(d["duty"], d["record"]) for d in self.duties(self.pkg)}
        self.assertIn(("AUTHOR_FAILURE_SIGNAL", q["id"]), before)
        fixed = copy.deepcopy(self.pkg)
        next(x for x in fixed["questions"] if x["id"] == q["id"])["failure_signal"] = "Pairs x(2 s) with y(3 s)."
        after = {(d["duty"], d["record"]) for d in self.duties(fixed)}
        self.assertEqual(before - after, {("AUTHOR_FAILURE_SIGNAL", q["id"])})

    def test_cross_subject_prerequisite_resolves_or_becomes_a_bridge_duty(self):
        pkg = copy.deepcopy(self.pkg)
        m = pkg["microtopics"][0]
        m["prerequisite_refs"] = ["Mathematics:CAP-MATH-NOT-TAUGHT-ANYWHERE"]
        self.assertIn(("TEACH_PREREQUISITE_BRIDGE", m["id"]), {(d["duty"], d["record"]) for d in self.duties(pkg)})
        math_cap = next(c for c in self.taught if c.startswith("Mathematics:"))
        m["prerequisite_refs"] = [math_cap]
        self.assertNotIn(("TEACH_PREREQUISITE_BRIDGE", m["id"]), {(d["duty"], d["record"]) for d in self.duties(pkg)})


if __name__ == "__main__":
    unittest.main()
