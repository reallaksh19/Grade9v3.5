"""Adversarial research-only checks for Core2 source custody and Core1A concept plans."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0,str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_core_pilot_research import (  # noqa: E402
    validate_census,validate_concept,
)

CENSUS = ROOT/"intake"/"core2-source-custody-eligibility.v1.json"
CONCEPT = ROOT/"intake"/"core1a-number-systems-construction-proposal.v1.json"


class CorePilotResearchTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base=Path(tmp.name)
        self.census=base/"census.json"
        self.concept=base/"concept.json"
        self.census.write_bytes(CENSUS.read_bytes())
        self.concept.write_bytes(CONCEPT.read_bytes())

    def inspect(self):
        return validate_census(self.census),validate_concept(self.concept,self.census)

    def mutate(self,path,fn):
        d=json.loads(path.read_text(encoding="utf-8"))
        fn(d)
        path.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")

    def rejects(self,path,fn):
        self.mutate(path,fn)
        with self.assertRaises(SeedError):
            self.inspect()

    def test_source_denominator_and_no_core(self):
        source,concept=self.inspect()
        self.assertEqual(source["source_positions"],68)
        self.assertEqual(source["owner_seed_positions"],66)
        self.assertEqual(source["additional_sample_positions"],2)
        self.assertEqual(source["source_conflict_cases"],10)
        self.assertEqual(source["affected_positions"],11)
        self.assertEqual((source["core2_eligible"],source["core2_admitted"],
                          source["learner_published"]),(0,0,0))
        self.assertEqual((concept["complete_teaching_steps"],concept["topic_clusters"]),(4,5))
        self.assertEqual((concept["source_backed_core2_anchors"],
                          concept["canonical_microtopics_admitted"]),(0,0))

    def test_one_seed_source_position_cannot_disappear(self):
        self.rejects(self.census,lambda d:d["records"].pop(0))

    def test_two_discovered_sample_positions_are_not_merged(self):
        self.rejects(self.census,lambda d:d["records"].pop(
            next(i for i,r in enumerate(d["records"]) if
                 r["question_id"]=="SOF-IMO-G09-SAMPLE-2026-27-Q001")))

    def test_no_fake_new_source_position(self):
        self.rejects(self.census,lambda d:d["records"][2].update(
            question_id="SOF-IMO-G09-L1-2030-31-A-Q001"))

    def test_original_question_number_preserved(self):
        self.rejects(self.census,lambda d:d["records"][1].update(
            original_printed_position_claim="88"))

    def test_38_split_cannot_be_collapsed(self):
        self.rejects(self.census,lambda d:d["source_census"].update(
            source_seed_positions=65))

    def test_source_host_not_organizer_claimed_for_mirror(self):
        self.rejects(self.census,lambda d:next(
            r for r in d["records"] if r["origin_scope"]==
            "FULLPAPER_OWNER_SEED_POSITION").update(
                source_host_kind="SOF_ORGANIZER_HOSTED_PDF"))

    def test_fabricated_source_pdf_sha_rejected(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            document_retained_sha256="a"*64))

    def test_source_locator_not_inferred_from_question_number(self):
        self.rejects(self.census,lambda d:next(
            r for r in d["records"] if r["source_locator_pdf_page_index"] is None
        ).update(source_locator_pdf_page_index=10))

    def test_no_source_stem_component_certification(self):
        self.rejects(self.census,lambda d:d["records"][0][
            "component_verification"].update(original_stem="VERIFIED"))

    def test_no_source_figure_certificate(self):
        self.rejects(self.census,lambda d:d["records"][-1][
            "component_verification"].update(
                source_figures_and_captions="LICENSED"))

    def test_no_reproduction_license(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            publisher_publication_rights="AUTHORIZED"))

    def test_no_external_reference_without_retained_digest(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            external_reference_custody_authorized=True))

    def test_no_core2_eligibility_by_default(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            core2_eligible=True))

    def test_no_source_core2_promotion(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            core2_admitted=True))

    def test_no_qrts_inferred(self):
        self.rejects(self.census,lambda d:d.update(accepted_qrt_cells=7))

    def test_no_student_release(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            learner_published=True))

    def test_no_erased_discrepancy_case(self):
        self.rejects(self.census,lambda d:next(
            r for r in d["records"] if r["source_discrepancy_case_id"]
        ).update(source_discrepancy_case_id=None))

    def test_source_keys_are_not_mathematical_acceptance(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            official_printed_key_receipt="PUBLISHER_CERTIFIED"))

    def test_no_unlicensed_original_sof_stem_injected(self):
        self.rejects(self.census,lambda d:d["records"][0].update(
            actual_sof_stem="source text not licensed"))

    def test_input_git_blob_pin_cannot_change(self):
        self.rejects(self.census,lambda d:d["inputs"][1].update(
            git_blob_sha="0"*40))

    def test_zero_count_must_not_be_boolean(self):
        self.rejects(self.census,lambda d:d.update(core2_admitted_positions=False))

    def test_core1a_idea_is_not_canonically_accepted(self):
        self.rejects(self.concept,lambda d:d.update(
            canonical_academic_package_ref="TEST/library/fake.json"))

    def test_authored_example_is_not_official_core2(self):
        self.rejects(self.concept,lambda d:d.update(
            dedicated_core2_source_question_ref=
                "IMO-G9-ORIGINAL-PRACTICE-001"))

    def test_core1a_not_admitted(self):
        self.rejects(self.concept,lambda d:d.update(core1a_admitted=True))

    def test_no_unearned_curriculum_owner_approval(self):
        self.rejects(self.concept,lambda d:d.update(
            product_owner_curriculum_acceptance="APPROVED"))

    def test_inferential_jump_cannot_be_removed(self):
        self.rejects(self.concept,lambda d:d["concept_slice"].update(
            inferential_jump="just calculate"))

    def test_misconception_repair_not_dropped(self):
        self.rejects(self.concept,lambda d:d["concept_slice"][
            "misconception_repair"].update(code="NONE"))

    def test_source_anchor_cannot_be_relabelled(self):
        self.rejects(self.concept,lambda d:d["concept_slice"][
            "worked_concept_anchor"].update(
                status="ORIGINAL_SOF_SOURCE"))

    def test_exit_proof_cannot_ignore_eight_factor(self):
        self.rejects(self.concept,lambda d:d["concept_slice"][
            "exit_task"].update(answer=
            "Every number works by checking n equals one and two."))

    def test_four_justified_steps_mandatory(self):
        self.rejects(self.concept,lambda d:d["concept_slice"][
            "completed_teaching_path"].pop())

    def test_grade9_extension_must_remain_visible(self):
        self.rejects(self.concept,lambda d:d["topic_rollout"][4].update(
            role="ACCEPTED_GRADE9_STANDARD"))

    def test_all_seven_original_practice_refs_kept_in_scope(self):
        self.rejects(self.concept,lambda d:d["topic_rollout"][1][
            "original_practice_ids"].pop())


if __name__=="__main__":
    unittest.main()
