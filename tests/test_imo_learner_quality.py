"""Fail-closed learner-quality research proposal tests; no live accessibility assertions."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_learner_quality import validate_quality  # noqa: E402

SOURCE = ROOT / "original-practice" / "learner-quality-proposals.v1.json"


class LearnerQualityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name) / "quality.json"
        self.data.write_bytes(SOURCE.read_bytes())

    def check(self):
        return validate_quality(self.data)

    def mutate(self, fn):
        obj = json.loads(self.data.read_text(encoding="utf-8"))
        fn(obj)
        self.data.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    def rejects(self, fn):
        self.mutate(fn)
        with self.assertRaises(SeedError):
            self.check()

    def test_seven_design_packets_no_admission(self):
        result = self.check()
        self.assertEqual(result["candidate_packets"], 7)
        self.assertEqual(result["draft_feedback_revisions"], 7)
        self.assertEqual(result["possible_grade9_extension_holds"], 2)
        self.assertEqual((result["screen_reader_tests_performed"],
                          result["learner_tests_performed"],
                          result["qrt_accepted"], result["core_ready"],
                          result["learner_published"]), (0, 0, 0, 0, 0))

    def test_no_false_screenreader_test(self):
        self.rejects(lambda d: d["records"][1].update(actual_screen_reader_audit="PASS"))

    def test_no_false_learner_comprehension(self):
        self.rejects(lambda d: d["records"][2].update(learner_comprehension_test="COMPLETE"))

    def test_no_fake_curriculum_review(self):
        self.rejects(lambda d: d["records"][0].update(independent_curriculum_review="APPROVED"))

    def test_no_false_software_release(self):
        self.rejects(lambda d: d["records"][3].update(learner_published=True))

    def test_no_core_promotion(self):
        self.rejects(lambda d: d["records"][4].update(core_2_ready=True))

    def test_no_qrt_acceptance(self):
        self.rejects(lambda d: d["records"][5].update(accepted_qrt_cell="QRT-MODEL-D3"))

    def test_no_ci_inferred_product_owner_approval(self):
        self.rejects(lambda d: d["records"][6].update(owner_product_approval="CI_SUCCESS"))

    def test_no_claimed_sof_reproduction_license(self):
        self.rejects(lambda d: d.update(third_party_sof_exam_stems_options_figures_copied=True))

    def test_no_prohibited_embedded_source_text(self):
        self.rejects(lambda d: d["records"][0].update(sof_original_stem="source text"))

    def test_no_source_id_collision(self):
        self.rejects(lambda d: d["records"][0].update(candidate_id="SOF-IMO-G09-SAMPLE-2026-27-Q001"))

    def test_no_drop_seventh_candidate(self):
        self.rejects(lambda d: d["records"].pop())

    def test_no_grade_topic_invention(self):
        self.rejects(lambda d: d["records"][2].update(proposed_syllabus_topic_id="UNLISTED_TOPIC"))

    def test_no_section1_as_official_topic(self):
        self.rejects(lambda d: d["records"][1].update(proposed_syllabus_topic_id="LOGIC"))

    def test_no_false_curriculum_acceptance(self):
        self.rejects(lambda d: d.update(official_sof_syllabus_topic_crosswalk_is_only_provisional=False))

    def test_no_graduate_two_equation_skill_without_review(self):
        self.rejects(lambda d: d["records"][5].update(topic_alignment="TOPIC_MATCH_NOT_GRADE_ATTAINMENT"))

    def test_no_hide_simultaneous_equation_scope(self):
        self.rejects(lambda d: d["records"][5].update(scope_review_note="A curriculum comparison is not independently complete."))

    def test_no_hide_determinant_scope(self):
        self.rejects(lambda d: d["records"][6].update(scope_review_note="A curriculum comparison is not independently complete."))

    def test_no_erase_prior_quality_hold(self):
        self.rejects(lambda d: d["records"][2].update(inherited_hold_code="RESOLVED"))

    def test_no_unlinked_misconception_code(self):
        self.rejects(lambda d: d["records"][1].update(targeted_misconception_code="NEW_UNKNOWN_CODE"))

    def test_feedback_must_not_be_unchanged(self):
        hint = ("Review the order of the axes: write east-west displacement first "
                "and north-south displacement second.")
        self.rejects(lambda d: d["records"][1].update(non_answer_leading_feedback_draft=hint))

    def test_feedback_cannot_be_empty(self):
        self.rejects(lambda d: d["records"][4].update(non_answer_leading_feedback_draft="Try again"))

    def test_spoken_math_cannot_claim_accessibility_approved(self):
        self.rejects(lambda d: d["records"][3].update(
            spoken_math_text_draft="APPROVED " + d["records"][3]["spoken_math_text_draft"]))

    def test_response_capture_must_have_detail(self):
        self.rejects(lambda d: d["records"][4].update(accessible_response_capture_spec="Input y"))

    def test_pin_cannot_be_repointed(self):
        self.rejects(lambda d: d["provenance"][1].update(git_blob_sha="0"*40))

    def test_historical_census_must_not_change(self):
        self.rejects(lambda d: d.update(agent_audited_attachment_fullpaper_positions_unchanged=60))

    def test_no_boolean_zero_counter(self):
        self.rejects(lambda d: d.update(product_approved=False))

    def test_human_review_waiver_must_not_be_erased(self):
        self.rejects(lambda d: d["records"][0].update(
            academic_human_signoff_requirement="PEER_SIGNATURE_REQUIRED"))

    def test_source_question_not_modified_by_overlay(self):
        self.rejects(lambda d: d["records"][3].update(authoring_change_to_source_question=True))

    def test_no_unearned_source_independence_review(self):
        self.rejects(lambda d: d["records"][1].update(source_independence_review="CERTIFIED"))

    def test_unexpected_top_level_payload_rejected(self):
        self.rejects(lambda d: d.update(publisher_license="GRANTED"))


if __name__ == "__main__":
    unittest.main()
