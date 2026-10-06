from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Shared.tools import question_review_matrix as qrt


REPO = Path(__file__).resolve().parents[1]


class QuestionReviewMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocab = qrt.load(qrt.VOCAB_PATH)
        cls.matrix = qrt.load(qrt.MATRIX_PATH)
        cls.templates = qrt.compile_templates(cls.matrix, cls.vocab)

    def test_vocabulary_has_exactly_seven_subject_neutral_demands(self):
        self.assertEqual(tuple(self.vocab["demands"]), qrt.DEMANDS)
        text = json.dumps(self.vocab)
        self.assertNotIn("Physics", text)
        self.assertNotIn("Chemistry", text)
        self.assertNotIn("Mathematics", text)

    def test_source_contract_is_valid_and_projection_is_current(self):
        self.assertEqual(qrt.validate_contract(self.matrix, self.vocab), [])
        self.assertEqual(qrt.check_paths(), [])

    def test_compiler_emits_exactly_twenty_eight_unique_cells(self):
        self.assertEqual(len(self.templates), 28)
        ids = [row["template_id"] for row in self.templates]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            set(ids),
            {f"QRT-{demand}-{band}" for demand in qrt.DEMANDS for band in qrt.BANDS},
        )

    def test_every_cell_has_twelve_semantic_asks_and_protects_w(self):
        for row in self.templates:
            with self.subTest(row["template_id"]):
                self.assertEqual(tuple(row["review"]), qrt.ASKS)
                self.assertIn("Band protection:", row["slots"]["W"])
                self.assertIn(row["band_policy"]["protected_work"], row["slots"]["W"])
                base_w = row["slots"]["W"].split(". Band protection:", 1)[0]
                self.assertIn(base_w, row["review"]["H3"]["question"])
                self.assertIn(row["band_policy"]["protected_work"], row["review"]["P1"]["question"])

    def test_cells_are_semantically_distinct_without_using_ids_as_the_difference(self):
        signatures = [qrt.normalized_signature(row) for row in self.templates]
        self.assertEqual(len(signatures), len(set(signatures)))

    def test_no_numeric_quality_score_contract_exists(self):
        self.assertEqual(qrt.forbidden_score_keys(self.matrix), [])
        for row in self.templates:
            self.assertEqual(qrt.forbidden_score_keys(row), [], row["template_id"])

    def test_missing_demand_and_scoring_mutations_are_refused(self):
        missing = copy.deepcopy(self.matrix)
        del missing["demands"]["JUSTIFY"]
        self.assertTrue(any("matrix demands" in p for p in qrt.validate_contract(missing, self.vocab)))

        scored = copy.deepcopy(self.matrix)
        scored["band_policies"]["D4"]["weight"] = 4
        self.assertTrue(any("numeric-quality scoring" in p for p in qrt.validate_contract(scored, self.vocab)))

    def test_primary_demand_and_band_are_orthogonal_axes(self):
        by_demand = {d: {row["band"] for row in self.templates if row["demand"] == d} for d in qrt.DEMANDS}
        self.assertTrue(all(bands == set(qrt.BANDS) for bands in by_demand.values()))
        by_band = {b: {row["demand"] for row in self.templates if row["band"] == b} for b in qrt.BANDS}
        self.assertTrue(all(demands == set(qrt.DEMANDS) for demands in by_band.values()))

    def test_generated_projection_is_exact_compiler_output(self):
        committed = json.loads(qrt.GENERATED_PATH.read_text(encoding="utf-8"))
        self.assertEqual(committed, qrt.generated_payload(self.matrix, self.vocab))


    def synthetic_question(self, *, transfer=False):
        question = {
            "id": "Q-TEST-REP-D3",
            "primary_capability_ref": "CAP-A",
            "secondary_capability_refs": ["CAP-B"],
            "difficulty": {
                "band": "D3",
                "score": 6,
                "components": {
                    "concept_model_selection": 1,
                    "representation_translation": 2,
                    "reasoning_chain_length": 2,
                    "algebra_computational_load": 1,
                    "trap_exception_sensitivity": 0,
                },
                "basis": "Representation plus a multi-step bridge.",
            },
            "extensions": {
                "grade9v3:cognitive_demand": {
                    "primary": "REPRESENT",
                    "secondary": ["SYNTHESIZE"],
                    "basis": "The decisive act is preserving meaning while changing representation.",
                },
                "grade9v3:analysis": {
                    "stable_crux_move": "Preserve the signed invariant while translating the diagram into an equation.",
                    "common_wrong_route": "Copy the visible shape and lose the sign convention.",
                },
            },
            "answer": {
                "reasoning_route": [
                    {"id": "MOVE-1", "kind": "DECIDE", "action": "Choose the sign convention.", "why_valid": "It fixes the invariant.", "inputs": [], "output": "signed axes"},
                    {"id": "MOVE-2", "kind": "REPRESENT", "action": "Translate each directed segment into a signed term.", "why_valid": "The representation preserves direction.", "inputs": ["signed axes"], "output": "equation"},
                    {"id": "MOVE-3", "kind": "VERIFY", "action": "Translate back to the diagram.", "why_valid": "Round-trip translation tests invariance.", "inputs": ["equation"], "output": "checked diagram"},
                ],
                "crux_move_ref": "MOVE-2",
            },
        }
        if transfer:
            question["transfer"] = {
                "dimension": "representation_translation",
                "statement": "Choose the invariant under a changed representation.",
                "builds_on": ["Q-OLD"],
                "protected_move_ref": "MOVE-1",
            }
        return question

    def synthetic_profile(self, percentage=50):
        return {
            "profile_id": "PROFILE-TEST",
            "provenance": "SYNTHETIC_TEST",
            "held": {"CAP-A": "UNCERTAIN", "CAP-B": "DEMONSTRATED"},
            "knowledge_percentage": percentage,
            "measured_fit_claim": False,
        }

    def test_resolver_selects_one_cell_and_fills_learner_relative_slots(self):
        result = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(), self.matrix, self.vocab)
        self.assertEqual(result["template_id"], "QRT-REPRESENT-D3")
        self.assertEqual(result["classification"]["demand"]["primary"], "REPRESENT")
        self.assertEqual(result["classification"]["band"], "D3")
        self.assertIn("CAP-A is UNCERTAIN", result["slots"]["X"]["text"])
        self.assertEqual(result["slots"]["Y"]["text"], "CAP-B")
        self.assertEqual(result["slots"]["Z"]["text"], "Translate each directed segment into a signed term.")
        self.assertEqual(result["slots"]["W"]["text"], "Translate each directed segment into a signed term.")
        self.assertIn(result["slots"]["X"]["text"], result["review"]["H1"]["question"])
        self.assertIn(result["slots"]["Y"]["text"], result["review"]["H2"]["question"])

    def test_difficulty_band_is_derived_from_component_evidence(self):
        question = self.synthetic_question()
        result = qrt.resolve_review(question, self.synthetic_profile(), self.matrix, self.vocab)
        self.assertEqual(result["classification"]["band"], "D3")
        self.assertIn("difficulty_metadata", result["basis_digests"])

        question["difficulty"]["score"] = 7
        with self.assertRaisesRegex(qrt.QRTContractError, "QUESTION_DIFFICULTY_SCORE_MISMATCH"):
            qrt.resolve_review(question, self.synthetic_profile(), self.matrix, self.vocab)

        question = self.synthetic_question()
        question["difficulty"]["band"] = "D4"
        with self.assertRaisesRegex(qrt.QRTContractError, "QUESTION_DIFFICULTY_BAND_MISMATCH"):
            qrt.resolve_review(question, self.synthetic_profile(), self.matrix, self.vocab)

    def test_requested_band_is_planning_metadata_not_qr_t_cell_authority(self):
        question = self.synthetic_question()
        question["difficulty"]["requested_band"] = "D4"
        result = qrt.resolve_review(question, self.synthetic_profile(), self.matrix, self.vocab)
        self.assertEqual(result["classification"]["band"], "D3")
        self.assertEqual(result["template_id"], "QRT-REPRESENT-D3")
        self.assertEqual(question["difficulty"]["requested_band"], "D4")

    def test_shared_difficulty_ranges_cover_zero_through_ten_once(self):
        self.assertEqual(
            qrt.question_difficulty.score_band_map(),
            {
                0: "D1", 1: "D1", 2: "D1",
                3: "D2", 4: "D2", 5: "D2",
                6: "D3", 7: "D3",
                8: "D4", 9: "D4", 10: "D4",
            },
        )

    def test_percentage_never_routes_or_changes_slots(self):
        low = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(30), self.matrix, self.vocab)
        high = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(80), self.matrix, self.vocab)
        self.assertEqual(low["template_id"], high["template_id"])
        self.assertEqual(low["slots"], high["slots"])

    def test_core2b_transfer_uses_protected_move_as_w(self):
        result = qrt.resolve_review(self.synthetic_question(transfer=True), self.synthetic_profile(), self.matrix, self.vocab)
        self.assertEqual(result["slots"]["W"]["text"], "Choose the sign convention.")
        self.assertIn("transfer.protected_move_ref", result["slots"]["W"]["basis"])

    def test_resolver_refuses_missing_demand_or_band_instead_of_inferring(self):
        question = self.synthetic_question()
        del question["extensions"]["grade9v3:cognitive_demand"]
        with self.assertRaisesRegex(qrt.QRTContractError, "COGNITIVE_DEMAND_MISSING"):
            qrt.resolve_review(question, self.synthetic_profile(), self.matrix, self.vocab)

        question = self.synthetic_question()
        del question["difficulty"]
        with self.assertRaisesRegex(qrt.QRTContractError, "QUESTION_DIFFICULTY"):
            qrt.resolve_review(question, self.synthetic_profile(), self.matrix, self.vocab)

    def test_resolution_carries_digest_bound_basis(self):
        one = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(), self.matrix, self.vocab)
        changed = self.synthetic_question()
        changed["extensions"]["grade9v3:analysis"]["stable_crux_move"] += " Changed."
        two = qrt.resolve_review(changed, self.synthetic_profile(), self.matrix, self.vocab)
        self.assertNotEqual(one["basis_digests"]["question"], two["basis_digests"]["question"])
        self.assertEqual(one["basis_digests"]["matrix"], two["basis_digests"]["matrix"])


    def test_product_review_projection_emits_only_actionable_findings(self):
        resolution = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(), self.matrix, self.vocab)
        projected = qrt.project_product_review_findings(
            resolution,
            {
                "H1": {"verdict": "YES", "evidence": ["useful line"]},
                "H2": {"verdict": "NO", "evidence": ["no bridge"], "fix": "Connect X to CAP-B.", "page": "core2.html#Q-TEST-REP-D3"},
                "S1": {"verdict": "PARTLY", "evidence": ["figure omits sign"], "severity": "S1", "fix": "Add signed axes.", "page": "core2.html#Q-TEST-REP-D3"},
            },
        )
        self.assertEqual(projected["profile_ref"], "PROFILE-TEST")
        self.assertEqual([f["asks"] for f in projected["findings"]], ["H2", "S1"])
        self.assertEqual(projected["findings"][0]["severity"], "S2")
        self.assertEqual(projected["findings"][1]["severity"], "S1")
        self.assertEqual(projected["findings"][1]["kind"], "figure")
        self.assertIn("H2 NO", projected["findings"][0]["learner_impact"])
        self.assertIn("Connect X to CAP-B.", projected["findings"][0]["suggested_fix"])

    def test_product_review_projection_refuses_unknown_verdicts_and_severities(self):
        resolution = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(), self.matrix, self.vocab)
        with self.assertRaisesRegex(qrt.QRTContractError, "VERDICT_INVALID"):
            qrt.project_product_review_findings(resolution, {"H1": {"verdict": "MAYBE"}})
        with self.assertRaisesRegex(qrt.QRTContractError, "SEVERITY_INVALID"):
            qrt.project_product_review_findings(resolution, {"H1": {"verdict": "NO", "severity": "S9"}})

    def test_product_review_schema_declares_qrt_traceability_without_new_authority(self):
        schema = json.loads((REPO / "Shared" / "quality" / "product-review.schema.json").read_text(encoding="utf-8"))
        self.assertIn("profile_ref", schema["properties"])
        self.assertNotIn("profile_ref", schema["required"])
        asks = schema["properties"]["findings"]["items"]["properties"]["asks"]["enum"]
        self.assertEqual(tuple(asks), qrt.ASKS)


    def test_all_subject_adapters_cover_the_same_seven_demands_and_use_controlled_vocabularies(self):
        for subject in ("Physics", "Chemistry", "Mathematics"):
            with self.subTest(subject):
                adapter = qrt.load(REPO / subject / "adapter" / "DemandReview.json")
                self.assertEqual(tuple(adapter["demands"]), qrt.DEMANDS)
                self.assertEqual(qrt.validate_subject_adapter(adapter), [])

    def test_same_base_cell_receives_subject_specific_guidance_without_changing_identity(self):
        resolution = qrt.resolve_review(self.synthetic_question(), self.synthetic_profile(), self.matrix, self.vocab)
        specialized = []
        for subject in ("Physics", "Chemistry", "Mathematics"):
            adapter = qrt.load(REPO / subject / "adapter" / "DemandReview.json")
            specialized.append(qrt.specialize_resolution(resolution, adapter))
        self.assertEqual({row["template_id"] for row in specialized}, {"QRT-REPRESENT-D3"})
        self.assertEqual({row["subject"] for row in specialized}, {"Physics", "Chemistry", "Mathematics"})
        focuses = {row["subject_adapter"]["guidance"]["review_focus"] for row in specialized}
        self.assertEqual(len(focuses), 3)

    def test_adapter_cannot_smuggle_unknown_representation_or_check_type(self):
        adapter = qrt.load(REPO / "Physics" / "adapter" / "DemandReview.json")
        bad = copy.deepcopy(adapter)
        bad["demands"]["REPRESENT"]["representation_kinds"].append("NOT_A_PHYSICS_REPRESENTATION")
        self.assertTrue(any("representation_kinds" in p for p in qrt.validate_subject_adapter(bad)))
        bad = copy.deepcopy(adapter)
        bad["demands"]["REPRESENT"]["check_types"].append("NOT_A_PHYSICS_CHECK")
        self.assertTrue(any("check_types" in p for p in qrt.validate_subject_adapter(bad)))


    def gate_report(self, *, findings=None, continuity=None, pages=None, verdict="FAIL", stamp="render-a"):
        return {
            "schema": "gate-report/v1",
            "tool": "quality_gate/1",
            "contract_version": "1.0.0",
            "product_id": "PRODUCT-TEST",
            "subject": "Mathematics",
            "render_stamp": stamp,
            "pages": pages or [{"page": "core2.html", "sha256": "a" * 64}],
            "rules_evaluated": ["RULE-1"],
            "rendered_measured": True,
            "not_measured": [],
            "findings": findings or [],
            "continuity": continuity or [],
            "verdict": verdict,
            "fail_reasons": [] if verdict == "PASS" else ["BLOCKING_FINDINGS"],
        }

    def test_gate_delta_uses_tool_written_reports_and_reports_new_closed_and_persisting(self):
        before = self.gate_report(
            findings=[
                {"rule": "A", "severity": "S1", "where": "core2", "detail": "spoiler"},
                {"rule": "B", "severity": "S2", "where": "core2", "detail": "missing check"},
            ],
            continuity=[{"code": "CONT_LINK_UNRESOLVED", "detail": "old broken link"}],
            pages=[{"page": "core2.html", "sha256": "a" * 64}],
        )
        after = self.gate_report(
            findings=[
                {"rule": "B", "severity": "S2", "where": "core2", "detail": "missing check"},
                {"rule": "C", "severity": "S3", "where": "core1a", "detail": "advisory"},
            ],
            continuity=[{"code": "CONT_INPUT_NOT_RENDERED", "detail": "new mapping gap"}],
            pages=[
                {"page": "core2.html", "sha256": "b" * 64},
                {"page": "core1a.html", "sha256": "c" * 64},
            ],
        )
        delta = qrt.compare_quality_gate_reports(before, after)
        self.assertEqual([f["rule"] for f in delta["new_findings"]], ["C"])
        self.assertEqual([f["rule"] for f in delta["closed_findings"]], ["A"])
        self.assertEqual([f["rule"] for f in delta["persisting_findings"]], ["B"])
        self.assertEqual(delta["new_continuity"][0]["code"], "CONT_INPUT_NOT_RENDERED")
        self.assertEqual(delta["closed_continuity"][0]["code"], "CONT_LINK_UNRESOLVED")
        self.assertEqual(
            [(p["page"], p["status"]) for p in delta["changed_pages"]],
            [("core1a.html", "ADDED"), ("core2.html", "CHANGED")],
        )
        self.assertNotEqual(delta["basis_digests"]["before_report"], delta["basis_digests"]["after_report"])

    def test_gate_delta_refuses_non_gate_reports_and_cross_product_comparisons(self):
        with self.assertRaisesRegex(qrt.QRTContractError, "expected tool-written"):
            qrt.compare_quality_gate_reports({"schema": "made-up"}, self.gate_report())
        before = self.gate_report()
        after = self.gate_report()
        after["product_id"] = "OTHER"
        with self.assertRaisesRegex(qrt.QRTContractError, "PRODUCT_MISMATCH"):
            qrt.compare_quality_gate_reports(before, after)

    def test_gate_delta_does_not_reimplement_or_score_gate_rules(self):
        before = self.gate_report(findings=[{"rule": "A", "severity": "S0", "where": "x", "detail": "falsehood"}])
        after = self.gate_report(findings=[{"rule": "A", "severity": "S0", "where": "x", "detail": "falsehood"}])
        delta = qrt.compare_quality_gate_reports(before, after)
        self.assertEqual(delta["new_findings"], [])
        self.assertEqual(delta["closed_findings"], [])
        self.assertEqual(len(delta["persisting_findings"]), 1)
        self.assertNotIn("score", json.dumps(delta).lower())


    def test_pr3_math_pilot_exercises_five_real_source_question_cells(self):
        pilot = json.loads((REPO / "tests" / "fixtures" / "quality" / "qrt-pr3-math-pilot.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(pilot["status"], "PILOT_ONLY_NOT_CANONICAL")
        self.assertEqual(pilot["source"]["pull_request"], 3)
        self.assertEqual(pilot["source"]["observed_blueprint_ref"], "BP-CORE2-SOURCE-QUESTION@1.0.0")
        self.assertEqual(pilot["source"]["active_blueprint_ref"], "BP-CORE2-SOURCE-QUESTION@1.5.0")
        resolved_ids = set()
        for item in pilot["items"]:
            question = item["normalized_pilot_question"]
            difficulty = question["difficulty"]
            self.assertEqual(difficulty["score"], sum(difficulty["components"].values()))
            self.assertEqual(set(difficulty["components"]), {
                "concept_model_selection", "representation_translation", "reasoning_chain_length",
                "algebra_computational_load", "trap_exception_sensitivity",
            })
            result = qrt.resolve_review(question, pilot["learner_profile"], self.matrix, self.vocab)
            self.assertEqual(result["template_id"], item["expected_template_id"])
            resolved_ids.add(result["template_id"])
            self.assertTrue(item["render_observation"]["question_anchor_present"])
            self.assertEqual(tuple(item["review"]), qrt.ASKS)
            for ask in ("S1", "S2", "S3"):
                self.assertTrue(item["review"][ask]["correctly_not_applicable"])
                self.assertTrue(item["review"][ask]["not_applicable_reason"])
        self.assertEqual(resolved_ids, {
            "QRT-RETRIEVE-D1", "QRT-APPLY-D2", "QRT-MODEL-D2",
            "QRT-SYNTHESIZE-D3", "QRT-JUSTIFY-D3",
        })

    def test_pr3_pilot_records_render_normalization_blockers_instead_of_claiming_acceptance(self):
        pilot = json.loads((REPO / "tests" / "fixtures" / "quality" / "qrt-pr3-math-pilot.v1.json").read_text(encoding="utf-8"))
        self.assertNotEqual(pilot["source"]["observed_blueprint_ref"], pilot["source"]["active_blueprint_ref"])
        self.assertIn("no data-blueprint-ref", pilot["blocked_companion_path"]["reason"])
        self.assertIn("not acceptance evidence", pilot["source"]["note"])

if __name__ == "__main__":
    unittest.main()
