from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.contracts import ContractError
from Shared.library import core1_orientation
from Shared.library.compile_inputs import compile_bucket
from Shared.library.resolve import build_index
from Shared.tools import build_core_learning_data, build_core_learning_host
from Shared.tools.core_learning_projection_adapter import (
    _application,
    adapt_compiled_bucket_with_status,
)

REPO = Path(__file__).resolve().parents[1]
MOTION = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
RELATIVE = REPO / "Physics/library/relative-motion.v1.json"
ORIENTATION_REPORT = REPO / "docs/core1-orientation-report.json"
RECONSTRUCTION_REPORT = REPO / "docs/core1b-reconstruction-report.json"
FAMILIAR = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"
TRANSFER = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"
CONCEPT = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"


def physics_packages() -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((REPO / "Physics/library").glob("*.json"))
    ]


def compile_motion(packages: list[dict] | None = None) -> tuple[dict, dict]:
    packages = packages or physics_packages()
    records = build_index(packages)
    compiled = compile_bucket(
        records,
        "BUCKET-PHY-KIN-2D-MOTION",
        topic_id="TEST-CORE-LEARNER-MOTION2D",
        title="Core learner Motion in 2D provider proof",
        subject="Physics",
        practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
    )
    return compiled, records


class CoreLearningProductionAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build_core_learning_data.build()
        cls.rows = cls.payload["core_projections"]
        cls.package = json.loads(MOTION.read_text(encoding="utf-8"))

    def row(self, *, core=None, source=None, concept=None):
        matches = [
            row for row in self.rows
            if (core is None or row["projection"]["core"] == core)
            and (source is None or row["source_ref"] == source)
            and (
                concept is None
                or (row["projection"].get("concept") or {}).get("microtopic_ref") == concept
            )
        ]
        self.assertEqual(len(matches), 1, [row["id"] for row in matches])
        return matches[0]

    def test_public_provider_is_compiler_backed_not_fixture_backed(self):
        self.assertEqual(self.payload["provider_status"], "PRODUCTION_COMPILED_CANONICAL")
        self.assertTrue(self.rows)
        self.assertFalse(any(row["id"].startswith("fixture:") for row in self.rows))
        self.assertEqual(
            self.payload["provider"]["mode"],
            "CANONICAL_LIBRARY_TO_COMPILE_BUCKET_TO_CORE_PROJECTION",
        )

    def test_core1_pair_shares_concept_but_changes_reveal_policy(self):
        a = self.row(core="CORE1A", concept=CONCEPT)
        b = self.row(core="CORE1B", concept=CONCEPT)
        self.assertEqual(a["projection"]["concept"]["microtopic_ref"], CONCEPT)
        self.assertEqual(a["projection"]["concept"]["inferential_jump"], b["projection"]["concept"]["inferential_jump"])
        self.assertFalse(a["projection"]["presentation"]["attempt_before_reveal"])
        self.assertTrue(a["projection"]["presentation"]["show_full_construction"])
        self.assertTrue(b["projection"]["presentation"]["attempt_before_reveal"])
        self.assertFalse(b["projection"]["presentation"]["show_full_construction"])
        self.assertTrue(b["projection"]["concept"]["elicitation"]["predict"]["prompt"])

    def test_every_core1_orientable_bucket_reaches_the_learner_provider(self):
        # The committed audit is an earlier evidence snapshot, not a live
        # compiler allowlist. Compare *all* current canonical orientable
        # buckets against the provider so newly added candidates are not
        # silently dropped merely because an old JSON report predates them.
        live_report = core1_orientation.audit(REPO)
        expected = {
            (row["subject"], row["bucket_ref"])
            for row in live_report["buckets"]
            if row["core1_compilable"]
        }
        delivered = {
            (row["subject"], row["source_ref"])
            for row in self.rows
            if row["projection"]["core"] == "CORE1"
        }
        self.assertTrue(expected)
        self.assertEqual(delivered, expected)

    def test_historical_orientation_snapshot_delta_is_explicit_not_publication(self):
        # Do not regenerate the historical 22-bucket report or let an
        # executable compiler preview masquerade as curriculum/QRT approval.
        historical = json.loads(ORIENTATION_REPORT.read_text(encoding="utf-8"))
        live_report = core1_orientation.audit(REPO)
        old_ids = {
            (row["subject"], row["bucket_ref"])
            for row in historical["buckets"]
        }
        live_ids = {
            (row["subject"], row["bucket_ref"])
            for row in live_report["buckets"]
        }
        preview_delta = {
            ("Mathematics", "BUCKET-MAT-POLYNOMIALS"),
            ("TEST", "BUCKET-TEST-IMO-G9-NS-DIVISIBILITY"),
            ("TEST", "BUCKET-MATH-POLY-STRESS-ISS55"),
        }
        self.assertEqual(len(historical["buckets"]), 22)
        self.assertEqual(live_ids - old_ids, preview_delta)
        self.assertEqual(old_ids - live_ids, set())
        self.assertTrue(all(
            row["core1_compilable"]
            for row in live_report["buckets"]
            if (row["subject"], row["bucket_ref"]) in preview_delta
        ))
        for path in (
            REPO / "Mathematics/library/polynomials.v1.json",
            REPO / "TEST/library/imo-g9-divisibility-core1a.v1.json",
            REPO / "TEST/library/iss55-poly.v1.json",
        ):
            package = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(package["status"], "CANDIDATE", path)
            self.assertTrue(all(b["status"] == "CANDIDATE" for b in package["buckets"]))
        # All emitted data is compiled using an explicitly labelled design
        # preview. No test here grants QRT acceptance or publication rights.
        with patch.object(
            build_core_learning_data, "compile_bucket", wraps=compile_bucket
        ) as compile_call:
            for subject in ("Mathematics", "TEST"):
                build_core_learning_data._subject_rows(subject)
            self.assertTrue(compile_call.call_args_list)
            self.assertTrue(all(
                call.kwargs.get("practice_control") == {
                    "mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"
                }
                for call in compile_call.call_args_list
            ))

    def test_public_and_pages_core_data_are_physically_held_without_grants(self):
        # Exact bytes: no TEST, Mathematics candidate or Physics candidate
        # projection can ride into either public/ or the GitHub Pages docs/.
        public = build_core_learning_data.build_public()
        self.assertEqual(public["provider_status"], "PUBLICATION_HELD")
        self.assertEqual(public["publication_gate"], {
            "status": "HOLD",
            "code": "NO_INDEPENDENT_CORE_PUBLICATION_GRANT",
            "authority": "NOT_GRANTED_BY_ANY_MACHINE_CHECK",
        })
        for field in ("core_projections", "bucket_availability", "findings"):
            self.assertEqual(public[field], [], field)
        expected = build_core_learning_data.render(public).encode("utf-8")
        for relative in ("public/core-learning/data.js", "docs/core-learning/data.js"):
            with self.subTest(relative=relative):
                self.assertEqual((REPO / relative).read_bytes(), expected)

        # Internal compiler preview is not deleted or reclassified as released.
        self.assertTrue(any(row["subject"] == "TEST" for row in self.rows))
        self.assertTrue(any(
            row["subject"] == "Mathematics"
            and row["source_ref"] == "BUCKET-MAT-POLYNOMIALS"
            for row in self.rows
        ))
        self.assertTrue(any(row["subject"] == "Physics" for row in self.rows))
        self.assertEqual(
            build_core_learning_data.rendered_file(),
            {"public/core-learning/data.js": expected},
        )

    def test_public_pages_mirror_contains_release_hold_instead_of_preview_chooser(self):
        public = (REPO / "public/core-learning/index.html").read_bytes()
        pages = (REPO / "docs/core-learning/index.html").read_bytes()
        self.assertEqual(pages, public)
        self.assertIn(b'if (data?.publication_gate?.status === "HOLD")', public)
        self.assertIn(b'No public activities are available.', public)

    def test_every_routed_concept_reaches_both_core1a_and_core1b(self):
        report = json.loads(RECONSTRUCTION_REPORT.read_text(encoding="utf-8"))
        routed = {
            (row["subject"], row["microtopic_ref"])
            for row in report["microtopics"]
            if row["routing_state"] != "UNROUTED"
        }
        for core in ("CORE1A", "CORE1B"):
            delivered = {
                (row["subject"], row["source_ref"])
                for row in self.rows
                if row["projection"]["core"] == core
            }
            self.assertEqual(delivered, routed, core)

    def test_core1_projection_preserves_compiler_orientation_blocks(self):
        compiled, _ = compile_motion()
        product = next(
            row for row in compiled["plan"]["products"]
            if row["core"] == "CORE1"
        )
        learner = self.row(core="CORE1", source="BUCKET-PHY-KIN-2D-MOTION")
        projection = learner["projection"]
        self.assertEqual(projection["orientation"]["bucket_ref"], "BUCKET-PHY-KIN-2D-MOTION")
        self.assertEqual(
            [row["id"] for row in projection["orientation"]["blocks"]],
            [
                block["id"]
                for block in product["units"][0]["blocks"]
                if block["kind"] in {"TEXT", "EQUATION", "FIGURE"}
            ],
        )
        self.assertIsNone(projection["concept"])
        self.assertIsNone(projection["application"])

    def test_relationless_bucket_keeps_core1_delivery(self):
        row = self.row(core="CORE1", source="BUCKET-PHY-ELEC-CURRENT-OHM")
        blocks = row["projection"]["orientation"]["blocks"]
        self.assertTrue(any(block["id"] == "CORE1-DEMAND" for block in blocks))
        self.assertFalse(any(block["kind"] == "EQUATION" for block in blocks))

    def test_core1_family_concept_payload_preserves_canonical_learning_cycle(self):
        source = next(m for m in self.package["microtopics"] if m["id"] == CONCEPT)
        a = self.row(core="CORE1A", concept=CONCEPT)["projection"]["concept"]
        b = self.row(core="CORE1B", concept=CONCEPT)["projection"]["concept"]
        self.assertEqual(a["inferential_jump"], source["inferential_jump"])
        self.assertEqual(a["entry_assumptions"], source["entry_assumptions"])
        self.assertEqual(a["teaching_path"], source["teaching_path"])
        self.assertEqual(a["misconceptions"], source["misconceptions"])
        self.assertEqual(a["representation_refs"], source["representation_refs"])
        self.assertEqual(a["exit_task"], source["exit_task"])
        self.assertEqual(b["elicitation"], source["elicitation"])
        self.assertEqual(b["inferential_jump"], source["inferential_jump"])

    def test_core2a_preserves_reasoning_source_hints_solution_and_scaffolds(self):
        row = self.row(core="CORE2A", source=FAMILIAR)
        source = next(q for q in self.package["questions"] if q["id"] == FAMILIAR)
        app = row["projection"]["application"]
        self.assertEqual(app["reasoning_route"], source["answer"]["reasoning_route"])
        self.assertEqual(app["crux_move_ref"], source["answer"]["crux_move_ref"])
        self.assertEqual(app["hints"], source["hints"])
        self.assertEqual(app["scaffolds"], source["scaffolds"])
        self.assertEqual(app["exposure"], source["exposure"])
        self.assertEqual(app["check"], source["answer"]["check"])
        self.assertEqual(app["solution"]["summary"], source["answer"]["summary"])
        self.assertEqual(app["solution"]["steps"], source["answer"]["reasoning"])
        for field in ("source_refs", "origin", "subparts", "options", "conditions", "figure_refs"):
            self.assertEqual(app[field], source[field])
        self.assertEqual(app["original_number"], source.get("original_identifier"))

    def test_compiled_question_parts_survive_without_rewriting(self):
        block = {
            "source_question_id": "Q-EXAMPLE",
            "family": "F-EXAMPLE",
            "stem": "Choose the valid relation.",
            "source_refs": ["SRC-EXAMPLE"],
            "origin": "ADAPTED",
            "original_number": "7(a)",
            "subparts": ["Find the first value.", "Explain the choice."],
            "options": ["A", "B"],
            "conditions": ["Assume a closed system."],
            "figure_refs": ["FIG-1"],
            "answer": {
                "summary": "B",
                "steps": ["Compare the conditions."],
                "rubric": [{"criterion": "Chooses B.", "evidence_of": "Uses the stated condition."}],
                "reasoning_route": [],
                "check": "Check units.",
            },
            "repair_ref": "STEP-1",
        }
        app = _application(block)
        for field in ("source_refs", "origin", "original_number", "subparts", "options", "conditions", "figure_refs"):
            self.assertEqual(app[field], block[field])
        self.assertEqual(app["solution"]["summary"], "B")
        self.assertEqual(app["solution"]["rubric"], block["answer"]["rubric"])
        self.assertEqual(app["repair"], {"step_ref": "STEP-1"})

    def test_demand_bearing_figure_gets_semantic_learner_payload(self):
        package = json.loads(RELATIVE.read_text(encoding="utf-8"))
        records = build_index([package])
        question = next(q for q in package["questions"] if q["figure_refs"])
        block = {
            "source_question_id": question["id"],
            "family": question["family_ref"],
            "stem": question["stem"],
            "figure_refs": question["figure_refs"],
            "answer": {
                "summary": question["answer"]["summary"],
                "steps": question["answer"]["reasoning"],
                "check": question["answer"]["check"],
            },
        }
        app = _application(block, records)
        self.assertEqual([row["figure_ref"] for row in app["figures"]], question["figure_refs"])
        self.assertTrue(app["figures"][0]["purpose"])
        self.assertTrue(app["figures"][0]["read_order"])

    def test_every_bucket_has_explicit_availability_and_all_provider_findings_are_retained(self):
        availability = self.payload["bucket_availability"]
        self.assertTrue(availability)
        self.assertEqual(len({(row["subject"], row["bucket_ref"]) for row in availability}), len(availability))
        projected_findings = {
            (row["subject"], row["bucket_ref"], finding["code"], finding.get("source_ref"))
            for row in availability
            for finding in row.get("findings", [])
        }
        payload_findings = {
            (row["subject"], row["bucket_ref"], row["code"], row.get("source_ref"))
            for row in self.payload["findings"]
        }
        self.assertEqual(projected_findings, payload_findings)
        for row in availability:
            self.assertIn(row["status"], {"AVAILABLE", "UNSUPPORTED"})
            if row["status"] == "AVAILABLE":
                self.assertTrue(row["projection_refs"])
                self.assertTrue(set(row["projection_refs"]).issubset({record["id"] for record in self.rows}))
            else:
                self.assertTrue(row["code"])
                self.assertEqual(row["projection_refs"], [])

    def test_compiler_error_is_reported_with_named_code(self):
        subject = next(name for name in build_core_learning_data.subjects() if name == "Physics")
        with patch.object(build_core_learning_data, "compile_bucket", side_effect=ContractError("BAD_SOURCE", "example")):
            rows, availability = build_core_learning_data._subject_rows(subject)
        self.assertEqual(rows, [])
        self.assertTrue(availability)
        self.assertTrue(all(row["status"] == "UNSUPPORTED" for row in availability))
        self.assertTrue(all(row["code"] == "BAD_SOURCE" for row in availability))

    def test_core2b_preserves_protected_transfer_with_explicit_pre_attempt_limits(self):
        row = self.row(core="CORE2B", source=TRANSFER)
        source = next(q for q in self.package["questions"] if q["id"] == TRANSFER)
        app = row["projection"]["application"]
        protected = source["transfer"]["protected_move_ref"]
        self.assertEqual(app["transfer"], source["transfer"])
        self.assertEqual(app["crux_move_ref"], protected)
        self.assertEqual(row["projection"]["presentation"]["protected_move_refs"], [protected])
        self.assertFalse(any(s["supports_move_ref"] == protected for s in app["scaffolds"]))
        self.assertTrue(all(
            scaffold["reveals"] == "CONCEPT"
            for scaffold in app["scaffolds"][
                :row["projection"]["presentation"]["pre_attempt_scaffold_limit"]
            ]
        ))
        self.assertEqual(app["solution"]["rubric"], source["answer"]["rubric"])
        self.assertEqual(app["repair"]["step_ref"], source["repair_ref"])

    def test_mature_core2a_does_not_require_core2b_or_interactive_explorer(self):
        compiled, records = compile_motion()
        compiled = copy.deepcopy(compiled)
        compiled["plan"]["products"] = [
            product for product in compiled["plan"]["products"]
            if product["core"] != "CORE2B"
        ]
        records = copy.deepcopy(records)
        for row in records.values():
            if isinstance(row, dict) and row.get("_collection") == "representations":
                row["interactive_resource_refs"] = []
        rows, findings = adapt_compiled_bucket_with_status(compiled, records, subject="Physics")
        familiar = [
            row for row in rows
            if row["projection"]["core"] == "CORE2A" and row["source_ref"] == FAMILIAR
        ]
        self.assertEqual(len(familiar), 1, findings)
        self.assertIsNone(familiar[0]["explorer_locator"])
        self.assertFalse(any(row["projection"]["core"] == "CORE2B" for row in rows))

    def test_adapter_never_promotes_authored_practice_to_core2(self):
        self.assertFalse(any(
            row["projection"]["core"] == "CORE2"
            for row in self.rows
            if row["source_ref"] in {FAMILIAR, TRANSFER}
        ))

    def test_compiler_emitted_core2_can_project_without_teaching_pair(self):
        block = {
            "kind": "QUESTION",
            "source_question_id": "Q-SOURCE-1",
            "family": "F-SOURCE",
            "stem": "Preserved source demand.",
            "source_refs": ["SRC-1"],
            "origin": "ORIGINAL",
            "original_number": "12",
            "subparts": [],
            "options": ["A", "B"],
            "conditions": ["Use the source condition."],
            "figure_refs": [],
            "answer": {
                "summary": "A",
                "steps": ["Source working."],
                "check": "Check against the source key.",
                "rubric": [{"criterion": "Selects A.", "evidence_of": "Matches the source key."}],
            },
            "hints": [{"text": "Source hint.", "reveals": "CONCEPT"}],
            "family": "F-SOURCE",
        }
        compiled = {
            "plan": {"products": [{"core": "CORE2", "units": [{"blocks": [block]}]}]},
            "derived_from": {"microtopics": []},
        }
        rows, findings = adapt_compiled_bucket_with_status(compiled, {}, subject="Physics")
        self.assertEqual(findings, [])
        self.assertEqual(len(rows), 1)
        projection = rows[0]["projection"]
        self.assertEqual(projection["core"], "CORE2")
        self.assertTrue(projection["presentation"]["show_solution_initially"])
        self.assertEqual(projection["application"]["solution"]["summary"], "A")

    def test_public_and_standalone_hosts_share_one_academic_template(self):
        rendered = {
            path: content.decode("utf-8")
            for path, content in build_core_learning_host.render().items()
        }
        public = rendered["public/core-learning/index.html"]
        standalone = rendered["standalone/core-learning/index.html"]
        normalized_public = (
            public
            .replace("./data.js", "__DATA__")
            .replace("../js/core-learning", "__RUNTIME__")
            .replace("../css/site.css", "__SITE_CSS__")
            .replace("../js/display-controls.js", "__DISPLAY__")
            .replace("../js/site-header.js", "__HEADER__")
            .replace('data-site-root="../"', 'data-site-root="__SITE_ROOT__"')
            .replace('data-site-parent="../index.html"', 'data-site-parent="__SITE_PARENT__"')
            .replace('href="../index.html"', 'href="__SITE_ROOT__index.html"')
            .replace('href="../question-bank/index.html"', 'href="__SITE_ROOT__question-bank/index.html"')
            .replace('const siteRoot = "../";', 'const siteRoot = "__SITE_ROOT__";')
            .replace('content="PUBLIC"', 'content="__PACKAGING_MODE__"')
        )
        normalized_standalone = (
            standalone
            .replace("../../public/core-learning/data.js", "__DATA__")
            .replace("../../public/js/core-learning", "__RUNTIME__")
            .replace("../../public/css/site.css", "__SITE_CSS__")
            .replace("../../public/js/display-controls.js", "__DISPLAY__")
            .replace("../../public/js/site-header.js", "__HEADER__")
            .replace('data-site-root="../../public/"', 'data-site-root="__SITE_ROOT__"')
            .replace('data-site-parent="../../public/index.html"', 'data-site-parent="__SITE_PARENT__"')
            .replace('href="../../public/index.html"', 'href="__SITE_ROOT__index.html"')
            .replace('href="../../public/question-bank/index.html"', 'href="__SITE_ROOT__question-bank/index.html"')
            .replace('const siteRoot = "../../public/";', 'const siteRoot = "__SITE_ROOT__";')
            .replace('content="REPOSITORY_ALTERNATE_HOST"', 'content="__PACKAGING_MODE__"')
        )
        self.assertEqual(normalized_public, normalized_standalone)
        self.assertIn("const rows = Array.isArray(data?.core_projections)", public)
        self.assertIn("mountCoreLearningPage", public)
        self.assertIn('data-site-root="../"', public)
        self.assertIn("Legacy iframe · migration only", public)
        self.assertIn("row?.projection?.delivery?.web", public)
        self.assertIn('locator.slice("public/".length)', public)

    def test_learner_hosts_label_previews_and_hold_test_sandbox_at_ui_boundary(self):
        # This protects the ordinary chooser/direct-link mount route, not the
        # underlying bytes of public/core-learning/data.js. A separate data
        # publication policy must close that remaining exposure.
        rendered = build_core_learning_host.render()
        for relative in (
            "public/core-learning/index.html",
            "standalone/core-learning/index.html",
        ):
            html = rendered[relative].decode("utf-8")
            self.assertIn(
                "Compiler design preview only. Curriculum approval, source custody and QRT release remain unverified",
                html,
                relative,
            )
            self.assertIn(
                '.filter(row => row?.subject !== "TEST")',
                html,
                relative,
            )
            self.assertIn(
                'if (!row) throw new Error("CORE_LEARNING_PROJECTION_NOT_PUBLIC_PREVIEW");',
                html,
                relative,
            )

    def test_shared_clock_explorer_remains_available_when_canonical_resource_exists(self):
        row = self.row(core="CORE2A", source=FAMILIAR)
        self.assertEqual(
            row["explorer_locator"],
            "public/physics/motion-2d/explorers/shared-clock/index.html",
        )
        self.assertTrue((REPO / row["explorer_locator"]).is_file())

    def test_shared_tooling_has_no_motion_specific_identifier_switch(self):
        adapter = (REPO / "Shared/tools/core_learning_projection_adapter.py").read_text(encoding="utf-8")
        builder = (REPO / "Shared/tools/build_core_learning_data.py").read_text(encoding="utf-8")
        for forbidden in ("MIC-PHY-", "Q-PHY-", "BUCKET-PHY-", "motion2d", "Physics/library"):
            self.assertNotIn(forbidden, adapter)
            self.assertNotIn(forbidden, builder)


if __name__ == "__main__":
    unittest.main()
