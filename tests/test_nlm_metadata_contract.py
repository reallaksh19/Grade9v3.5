from __future__ import annotations

import copy
import json
import re
import tempfile
import unittest
from pathlib import Path

from Shared.tools import product_manifest, quality_contract, quality_observe, render_core

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "products/physics/phy-nlm-first-law.manifest.json"
PACKAGE = REPO / "Physics/library/phy-nlm-first-law.v1.json"
BANK = REPO / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"


class NlmSelectionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.bank_questions = cls.bank["questions"]

    def validate(self, manifest: dict) -> dict[str, list[dict]]:
        return product_manifest.validate_selection(
            manifest,
            [self.package],
            self.bank_questions,
        )

    def test_current_nlm_selection_is_exactly_resolved_in_role_authority(self):
        selection = self.manifest["selection"]
        self.assertEqual(
            {key: len(value) for key, value in selection.items()},
            {"microtopics": 11, "core2": 13, "core2a": 22, "core2b": 16},
        )
        self.assertTrue(all(len(values) == len(set(values)) for values in selection.values()))

        resolved = self.validate(self.manifest)
        self.assertEqual(
            {key: len(value) for key, value in resolved.items()},
            {"microtopics": 11, "core2": 13, "core2a": 22, "core2b": 16},
        )

        package_question_ids = {row["id"] for row in self.package["questions"]}
        bank_question_ids = {row["id"] for row in self.bank_questions}
        self.assertTrue(set(selection["core2"]) <= bank_question_ids)
        self.assertTrue(set(selection["core2"]).isdisjoint(package_question_ids))
        self.assertTrue(set(selection["core2a"]) <= package_question_ids)
        self.assertTrue(set(selection["core2b"]) <= package_question_ids)
        self.assertTrue(set(selection["core2a"]).isdisjoint(bank_question_ids))
        self.assertTrue(set(selection["core2b"]).isdisjoint(bank_question_ids))

    def test_selected_authored_assessments_have_explicit_normalized_metadata(self):
        selected = self.manifest["selection"]["core2a"] + self.manifest["selection"]["core2b"]
        package_questions = {q["id"]: q for q in self.package["questions"]}
        self.assertEqual(len(selected), 38)
        rows = [package_questions[record_id] for record_id in selected]
        self.assertEqual({row.get("learner_question_type") for row in rows}, {"constructed_response", "derivation", "experimental_design"})
        self.assertTrue(all(isinstance(row.get("difficulty"), dict) for row in rows))
        self.assertGreaterEqual(len({package_questions[i]["difficulty"]["band"] for i in self.manifest["selection"]["core2a"]}), 3)
        self.assertGreaterEqual(len({package_questions[i]["difficulty"]["band"] for i in self.manifest["selection"]["core2b"]}), 2)
        for row in rows:
            difficulty = row["difficulty"]
            self.assertEqual(difficulty["score"], sum(difficulty["components"].values()))
            self.assertTrue(difficulty["basis"])

    def test_all_six_roles_render_one_metadata_component_contract(self):
        ctx = render_core.context(MANIFEST)
        digest = render_core.render_digest(ctx)
        expected = {
            "CORE1": (11, {"subject", "topic", "concept", "concept-difficulty"}),
            "CORE1A": (11, {"subject", "topic", "concept", "concept-difficulty"}),
            "CORE1B": (11, {"subject", "topic", "concept", "concept-difficulty"}),
            "CORE2": (13, {"subject", "topic", "concept", "concept-difficulty", "question-difficulty", "family", "question-type", "source", "provenance"}),
            "CORE2A": (22, {"subject", "topic", "concept", "concept-difficulty", "question-difficulty", "family", "question-type", "provenance"}),
            "CORE2B": (16, {"subject", "topic", "concept", "concept-difficulty", "question-difficulty", "family", "question-type", "provenance", "transfer-dimension"}),
        }
        for role, (unit_count, kinds) in expected.items():
            with self.subTest(role=role):
                html = render_core.page(ctx, role, "PAGES", digest)
                self.assertEqual(html.count("data-g9-meta-strip"), unit_count)
                for kind in kinds:
                    self.assertEqual(
                        len(re.findall(rf'data-g9-meta-kind="{re.escape(kind)}"', html)),
                        unit_count,
                        kind,
                    )
        self.assertEqual(ctx.gaps, [])

    def test_render_core_observation_and_existing_quality_contract_enforce_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            ctx = render_core.context(MANIFEST)
            digest = render_core.render_digest(ctx)
            for role, filename in render_core.ROLE_FILE.items():
                (folder / filename).write_text(
                    render_core.page(ctx, role, "PAGES", digest),
                    encoding="utf-8",
                )
            obs = quality_observe.observe_render_core(
                folder, "PRODUCT-PHY-NLM-FIRST-LAW", "Physics"
            )
            metadata_rules = {"C1-FAMILY-METADATA", "C2-METADATA", "C2A-METADATA", "C2B-METADATA"}
            result = quality_contract.evaluate(obs)
            self.assertFalse(metadata_rules & {finding["rule"] for finding in result["findings"]})

            core2 = next(page for page in obs["pages"] if page["role"] == "CORE2")
            core2["units"][0]["metadata"] = [
                row for row in core2["units"][0]["metadata"]
                if row["kind"] != "source"
            ]
            broken = quality_contract.evaluate(obs)
            self.assertIn("C2-METADATA", {finding["rule"] for finding in broken["findings"]})

    def test_core2b_difficulty_is_not_a_role_default(self):
        package_questions = {q["id"]: q for q in self.package["questions"]}
        bands = {package_questions[i]["difficulty"]["band"] for i in self.manifest["selection"]["core2b"]}
        self.assertEqual(bands, {"D2", "D3", "D4"})

    def test_render_identity_tracks_every_metadata_authority(self):
        ctx = render_core.context(MANIFEST)
        labels = {label for label, _ in ctx.authority_hashes}
        self.assertTrue({
            "learner-metadata-source",
            "learner-metadata-vocabulary",
            "package-schema",
            "competitive-bank-schema",
            "blueprints",
        } <= labels)

    def test_page_search_uses_explicit_safe_corpus_not_rendered_or_locked_text(self):
        ctx = render_core.context(MANIFEST)
        html = render_core.page(ctx, "CORE2B", "PAGES", render_core.render_digest(ctx))
        self.assertIn("a.dataset.g9SearchText", html)
        self.assertNotIn("a.innerText.toLowerCase()", html)
        self.assertNotIn("a.textContent.toLowerCase()", html)
        self.assertIn("data-g9-search-text=", html)

        question = next(q for q in ctx.selection_rows["core2b"] if q["id"] == "Q-PHY-NLM-2B-FRICTION-STATE-01")
        protected = next(
            move["action"] for move in question["answer"]["reasoning_route"]
            if move["id"] == question["transfer"]["protected_move_ref"]
        )
        search_text = render_core.metadata_search_text(ctx, "CORE2B", question)
        self.assertIn(question["stem"], search_text)
        self.assertIn("Model choice", search_text)
        self.assertNotIn(question["answer"]["summary"], search_text)
        self.assertNotIn(protected, search_text)

    def test_missing_selected_id_fails_closed(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["selection"]["core2"][0] = "Q-DOES-NOT-EXIST"
        with self.assertRaisesRegex(
            product_manifest.ProductSelectionError,
            r"PRODUCT_SELECTION_UNRESOLVED: core2:Q-DOES-NOT-EXIST:expected=BANK",
        ):
            self.validate(manifest)

    def test_duplicate_selected_id_fails_closed(self):
        manifest = copy.deepcopy(self.manifest)
        duplicate = manifest["selection"]["core2"][0]
        manifest["selection"]["core2"].append(duplicate)
        with self.assertRaisesRegex(
            product_manifest.ProductSelectionError,
            rf"PRODUCT_SELECTION_DUPLICATE_ID: core2:{duplicate}",
        ):
            self.validate(manifest)

    def test_wrong_authority_fails_closed(self):
        manifest = copy.deepcopy(self.manifest)
        package_question = manifest["selection"]["core2a"][0]
        manifest["selection"]["core2"][0] = package_question
        with self.assertRaisesRegex(
            product_manifest.ProductSelectionError,
            rf"PRODUCT_SELECTION_WRONG_AUTHORITY: core2:{package_question}:expected=BANK",
        ):
            self.validate(manifest)

    def test_renderer_context_uses_the_same_fail_closed_selection_contract(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["selection"]["core2b"][0] = "Q-DOES-NOT-EXIST"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                product_manifest.ProductSelectionError,
                r"PRODUCT_SELECTION_UNRESOLVED: core2b:Q-DOES-NOT-EXIST:expected=PACKAGE",
            ):
                render_core.context(path)


if __name__ == "__main__":
    unittest.main()
