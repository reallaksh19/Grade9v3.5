"""Observed Set B failures, compatibility controls and honest review evidence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from Shared.tools import core2_v2, qrt_pipeline_guard as guard, render_core
from tools import staged_set_b_replay as replay

REPO = Path(__file__).resolve().parents[1]


def validator(path, definition):
    schema = json.loads((REPO / path).read_text(encoding="utf-8"))
    return Draft202012Validator({"$schema": schema["$schema"], "$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]})


class StagedSupportRepair(unittest.TestCase):
    def test_corrected_quadratic_curve_matches_the_three_conditions_between_endpoints(self):
        # Verify the graphic's geometry, not its label. Parse the authored Bézier segment.
        svg = (REPO / "tests/fixtures/staged_set_b/ISS54-case.svg").read_text(encoding="utf-8")
        values = re.search(r'M(\d+) (\d+) Q(\d+) (\d+) (\d+) (\d+)', svg).groups()
        x0, y0, xc, yc, x1, y1 = map(float, values)
        for index in range(11):
            t = index / 10
            px = (1-t)**2*x0 + 2*(1-t)*t*xc + t*t*x1
            py = (1-t)**2*y0 + 2*(1-t)*t*yc + t*t*y1
            x, y = (px-280)/60, (150-py)/22
            self.assertAlmostEqual(y, x*x-x-6, places=10)

    def test_competitive_bank_allows_the_optional_binding_without_a_second_definition(self):
        schema = json.loads(render_core.BANK_SCHEMA.read_text(encoding="utf-8"))
        extensions = schema["$defs"]["exam_bank_question"]["properties"]["extensions"]
        self.assertIn(core2_v2.SUPPORT_PLAN_KEY, extensions["properties"])
        # The bank's existing base-question validator owns the complete canonical shape.
        from Shared.tools import competitive_exam_bank
        q, _, _ = replay.adopt(replay.cases()[0])
        findings = competitive_exam_bank._package_record_findings(q, "question", "case")
        self.assertFalse(any(core2_v2.SUPPORT_PLAN_KEY in f["where"] for f in findings), findings)

    def test_replay_receipts_include_the_selected_case_asset_bytes(self):
        ctx = replay.context()
        hashes = dict(ctx.authority_hashes)
        for rep in ctx.packages[0]["representations"]:
            asset = rep["scene_instances"][0]["asset_ref"]
            self.assertIn(asset, hashes)

    def test_optional_structures_validate_against_canonical_definitions(self):
        for case in replay.cases():
            q, rep, datum = replay.adopt(case)
            for name, record in [("core2_support_plan", q["extensions"][core2_v2.SUPPORT_PLAN_KEY]),
                                 ("scene_instance", rep["scene_instances"][0]), ("datum", datum)]:
                with self.subTest(issue=case["issue"], definition=name):
                    errors = list(validator("Shared/library/package.schema.json", name).iter_errors(record))
                    self.assertEqual(errors, [], [e.message for e in errors])

    def test_each_actual_question_selects_its_own_asset_and_only_given_stage(self):
        ctx = replay.context()
        for q in ctx.bank:
            with self.subTest(question=q["id"]):
                output = render_core._core2_question_figures(ctx, q)
                self.assertIn(f'data-g9-case-owner="{q["id"]}"', output)
                self.assertIn('data-g9-stages="GIVENS"', output)
                self.assertNotIn('data-g9-stage-id="WORKED"', output)
                self.assertNotIn("<desc>", output)
        self.assertEqual(ctx.gaps, [])

    def test_two_questions_can_share_a_topic_without_sharing_the_selected_case(self):
        ctx = replay.context()
        q1 = ctx.bank[0]
        q2 = copy.deepcopy(q1)
        q2["id"] = "OTHER-QUESTION"
        rep = ctx.packages[0]["representations"][0]
        other = copy.deepcopy(rep["scene_instances"][0])
        other.update(id="OTHER-CASE", question_ref=q2["id"], asset_ref=rep["rendered_asset_refs"][0])
        rep["scene_instances"].append(other)
        q2["extensions"][core2_v2.SUPPORT_PLAN_KEY]["visuals"][0]["instance_ref"] = "OTHER-CASE"
        # The second asset uses its existing stages; the selected instance is still distinct.
        stages = re.findall(r'data-g9-stage-id="([^"]+)"', (REPO / other["asset_ref"]).read_text(encoding="utf-8"))
        q2["extensions"][core2_v2.SUPPORT_PLAN_KEY]["visuals"][0]["stages"] = [
            {"stage_ref": sid, "completed_move_refs": []} for sid in stages]
        self.assertIn('data-g9-case-instance="ISS53-CASE"', render_core._core2_question_figures(ctx, q1))
        self.assertIn('data-g9-case-instance="OTHER-CASE"', render_core._core2_question_figures(ctx, q2))
        self.assertEqual(ctx.gaps, [])

    def test_wrong_case_owner_or_missing_data_is_diagnosed_on_the_adopted_record(self):
        for defect in ("owner", "datum", "asset", "role"):
            ctx = replay.context()
            case = ctx.packages[0]["representations"][0]["scene_instances"][0]
            case.update({"owner": {"question_ref": "WRONG"}, "datum": {"datum_refs": ["ABSENT"]},
                         "asset": {"asset_ref": "absent.svg"}, "role": {"cores": ["CORE1A"]}}[defect])
            self.assertEqual(render_core._core2_question_figures(ctx, ctx.bank[0]), "")
            self.assertTrue(ctx.gaps, defect)
            self.assertTrue({g["duty"] for g in ctx.gaps} <= {"BUILD_SCENE", "MOUNT_REPRESENTATION"})

    def test_parameter_revealing_hint_is_deferred_without_relabeling_its_words(self):
        original = replay.cases()[2]["question"]
        q, _, _ = replay.adopt(replay.cases()[2])
        legacy = core2_v2.pre_solution_support(original)
        self.assertTrue(any("p_0(x)" in row["text"] for row in legacy))
        safe = core2_v2.pre_solution_support(q)
        self.assertEqual([r["source"] for r in safe], ["scaffolds[0]"])
        self.assertNotIn("p_0(x)", render_core._core2_support(replay.context(), q))
        completed = render_core._core2_completed_support(replay.context(), q)
        self.assertIn("p_0(x)", completed)
        self.assertEqual(q["scaffolds"], original["scaffolds"])

    def test_completed_figures_remain_in_the_existing_attempted_solution_payload(self):
        ctx = replay.context()
        output = render_core.core2(ctx, ctx.bank[2])
        payload = re.search(r'<template data-g9-payload="[^"]+">(.*?)</template>', output, re.S)
        self.assertIsNotNone(payload)
        self.assertIn('data-g9-stage-id="WORKED"', payload.group(1))
        outside = output[:payload.start()] + output[payload.end():]
        self.assertNotIn("p_0(x)", outside)
        self.assertNotIn('data-g9-stage-id="WORKED"', outside)

    def test_a_visual_with_only_protected_stages_is_absent_before_attempt(self):
        ctx = replay.context()
        q = ctx.bank[0]
        plan = q["extensions"][core2_v2.SUPPORT_PLAN_KEY]
        plan["visuals"][0]["stages"] = [{"stage_ref": "WORKED", "completed_move_refs": plan["protected_move_refs"]}]
        self.assertEqual(render_core._core2_question_figures(ctx, q), "")
        self.assertIn('data-g9-stage-id="WORKED"', render_core._core2_completed_support(ctx, q))

    def test_bad_plan_references_and_shapes_produce_projection_errors(self):
        for field, value in [("protected_move_refs", ["UNKNOWN"]), ("protected_move_refs", [{}]),
                             ("support_completions", [None]), ("visuals", "bad"),
                             ("support_completions", [{"support_ref": "scaffolds[99]", "completed_move_refs": []}]),
                             ("visuals", [{"representation_ref": "r", "instance_ref": "i", "stages": [None]}])]:
            q, _, _ = replay.adopt(replay.cases()[0])
            q["extensions"][core2_v2.SUPPORT_PLAN_KEY][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(core2_v2.Core2SupportProjectionError):
                core2_v2.project_support(q)

    def test_a_no_picture_question_needs_no_visual_plan_or_figure(self):
        ctx = replay.context()
        q = ctx.bank[0]
        q["figure_refs"] = []
        del q["extensions"][core2_v2.SUPPORT_PLAN_KEY]["visuals"]
        self.assertEqual(render_core._core2_question_figures(ctx, q), "")
        self.assertEqual(ctx.gaps, [])
        self.assertTrue(core2_v2.pre_solution_support(q))

    def test_legacy_and_teaching_keep_the_topic_asset(self):
        ctx = replay.context(False)
        q = ctx.bank[0]
        rep = ctx.packages[0]["representations"][0]
        legacy = render_core._core2_question_figures(ctx, q)
        self.assertNotIn("data-g9-case-instance", legacy)
        teaching = render_core.figure(ctx, rep["id"], "TEACHING", "CORE1A", "changed-example")
        self.assertIn("5x", teaching)
        self.assertNotIn("data-g9-case-owner", teaching)
        self.assertEqual(render_core._core2_completed_support(ctx, q), "")
        self.assertEqual(ctx.gaps, [])

    def test_source_figure_cannot_be_replaced_by_adopted_authored_case(self):
        ctx = replay.context()
        q = ctx.bank[0]
        rep = ctx.packages[0]["representations"][0]
        rep["kind"] = "SOURCE_FIGURE"
        self.assertEqual(render_core._core2_question_figures(ctx, q), "")
        self.assertEqual(ctx.gaps[0]["duty"], "MOUNT_REPRESENTATION")

    def test_reviewed_authored_replacement_is_selected_after_attempt_too(self):
        ctx = replay.context()
        q = ctx.bank[0]
        original = ctx.packages[0]["representations"][0]
        replacement = copy.deepcopy(original)
        replacement["id"] = "REVIEWED-REPLACEMENT"
        replacement.setdefault("extensions", {})["grade9v3:authored_question_ref"] = q["id"]
        ctx.packages[0]["representations"].append(replacement)
        q["extensions"]["grade9v3:core2_visual_review"] = {
            "question_ref": q["id"], "replaces_authored_figure_refs": q["figure_refs"],
            "authored_figure_refs": [replacement["id"]], "rationale": "Correct the authored question coefficient table."}
        q["extensions"][core2_v2.SUPPORT_PLAN_KEY]["visuals"][0]["representation_ref"] = replacement["id"]
        for stage in ("PRE_ATTEMPT", "POST_ATTEMPT"):
            self.assertIn('data-g9-representation="REVIEWED-REPLACEMENT"', render_core._core2_question_figures(ctx, q, stage))
        self.assertEqual(ctx.gaps, [])


class ReviewBasis(unittest.TestCase):
    def setUp(self):
        self.check = validator("Shared/quality/qrt-pipeline-run.schema.json", "semanticReview")

    def test_author_only_record_is_retained_but_does_not_satisfy_rendered_review(self):
        review = {"question_ref": "Q", "basis": "AUTHOR_ONLY", "judgements": {"S1": {"verdict": "YES", "evidence": "Author claim only."}}}
        self.assertEqual(list(self.check.iter_errors(review)), [])
        errors = guard.validate_artifacts_and_reviews({"questions": [{"id": "Q"}], "reviews": [review]})
        self.assertEqual(errors, ["POST_RENDER_QRT_REVIEW_MISSING: Q"])

    def test_legacy_rendered_reviews_keep_existing_binding_and_verdict_behavior(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(guard, "REPO", Path(folder)):
            path = Path(folder) / "page.html"
            path.write_text("<p>Actual rendered output</p>", encoding="utf-8")
            sha = guard.sha256_file(path)
            artifact = {"id": "A", "path": "page.html", "sha256": sha, "head_sha": "a" * 40}
            review = {"question_ref": "Q", "artifact_ref": "A", "artifact_sha256": sha,
                      "judgements": {ask: {"verdict": "YES", "evidence": "Rendered page location."} for ask in guard.ASKS}}
            self.assertEqual(list(self.check.iter_errors(review)), [])
            run = {"run_identity": {"head_sha": "a" * 40}, "questions": [{"id": "Q"}], "rendered_artifacts": [artifact], "reviews": [review]}
            self.assertEqual(guard.validate_artifacts_and_reviews(run), [])
            review["artifact_sha256"] = "sha256:" + "0" * 64
            self.assertIn("REVIEW_NOT_BOUND_TO_RENDERED_BYTES: Q:A", guard.validate_artifacts_and_reviews(run))

    def test_missing_facet_unknown_verdict_and_evidenceless_yes_are_structural_errors(self):
        review = {"question_ref": "Q", "basis": "RENDERED", "artifact_ref": "A", "artifact_sha256": "sha256:" + "a" * 64,
                  "judgements": {ask: {"verdict": "YES", "evidence": "Actual location"} for ask in guard.ASKS}}
        for alteration in ("missing", "unknown", "empty", "fix"):
            bad = copy.deepcopy(review)
            if alteration == "missing": del bad["judgements"]["S1"]
            if alteration == "unknown": bad["judgements"]["S1"]["verdict"] = "PASS"
            if alteration == "empty": del bad["judgements"]["S1"]["evidence"]
            if alteration == "fix": bad["judgements"]["S1"]["verdict"] = "NO"
            self.assertTrue(list(self.check.iter_errors(bad)), alteration)


if __name__ == "__main__":
    unittest.main()
