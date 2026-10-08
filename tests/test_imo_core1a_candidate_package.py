"""Adversarial Core1A TEST package tests: no invented Core2, authority or release."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "TEST" / "imo-research"))
from validate_core1a_candidate_package import (  # noqa: E402
    IMOCore1ACandidateError, validate_package
)

SOURCE = REPO / "TEST" / "library" / "imo-g9-divisibility-core1a.v1.json"


class Core1ACandidateTests(unittest.TestCase):
    def setUp(self):
        context=tempfile.TemporaryDirectory()
        self.addCleanup(context.cleanup)
        self.filename=Path(context.name) / "candidate.json"
        self.filename.write_bytes(SOURCE.read_bytes())

    def check(self):
        return validate_package(self.filename)

    def mutate(self,fn):
        obj=json.loads(self.filename.read_text(encoding="utf-8"))
        fn(obj)
        self.filename.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")

    def blocked(self,fn):
        self.mutate(fn)
        with self.assertRaises(IMOCore1ACandidateError):
            self.check()

    def test_candidate_is_nonpublishing_and_canonical_refs_resolve(self):
        result=self.check()
        self.assertEqual(result["complete_teaching_steps"],4)
        self.assertEqual(result["mathematics_exhaustive_residue_checks"],"MOD6_AND_MOD24_PASS")
        self.assertEqual((result["official_source_core2"],result["canonical_acceptance"],
                          result["qrt_acceptance"],result["learner_published"]),(0,0,0,0))

    def test_cannot_change_sandbox_subject(self):
        self.blocked(lambda x:x.update(subject="Mathematics"))

    def test_cannot_promote_package(self):
        self.blocked(lambda x:x.update(status="CURATED"))

    def test_cannot_claim_qrt_acceptance(self):
        self.blocked(lambda x:x["extensions"].update({"grade9v3:qrt_admitted":True}))

    def test_cannot_claim_copyright_approval(self):
        self.blocked(lambda x:x["extensions"].update(source_license="GRANTED"))

    def test_cannot_claim_official_sof_core2(self):
        self.blocked(lambda x:x["extensions"].update({"grade9v3:core2_source_custody_granted":True}))

    def test_cannot_publish_learner(self):
        self.blocked(lambda x:x["extensions"].update({"grade9v3:learner_published":True}))

    def test_author_cannot_pose_as_publisher(self):
        self.blocked(lambda x:x["resources"][0].update(origin="WEB"))

    def test_no_snapshot_digest_manufactured(self):
        self.blocked(lambda x:x["resources"][0].update(snapshot_digest="fake"))

    def test_no_source_derived_questions_in_core1a_pack(self):
        self.blocked(lambda x:x["questions"].append({"id":"FAKE-SOF-IMO-Q001"}))

    def test_no_unearned_curriculum(self):
        self.blocked(lambda x:x["curriculum_mappings"].append({"board":"SOF","grade":9}))

    def test_no_extra_microtopic_without_canonical_map(self):
        self.blocked(lambda x:x["microtopics"].append(x["microtopics"][0].copy()))

    def test_primary_capability_immutable(self):
        self.blocked(lambda x:x["microtopics"][0].update(primary_capability_ref="UNACCEPTED-QRT"))

    def test_entry_conventions_exist(self):
        self.blocked(lambda x:x["buckets"][0].update(conventions=[]))

    def test_inference_cannot_collapse_to_examples(self):
        self.blocked(lambda x:x["microtopics"][0].update(inferential_jump="Check n=1,2,3."))

    def test_four_why_valid_moves_required(self):
        self.blocked(lambda x:x["microtopics"][0]["teaching_path"].pop())

    def test_cannot_erase_reason_for_step(self):
        self.blocked(lambda x:x["microtopics"][0]["teaching_path"][2].update(why_valid="Obviously"))

    def test_example_only_misconception_not_dropped(self):
        self.blocked(lambda x:x["microtopics"][0].update(misconceptions=[]))

    def test_independent_exit_no_fake_certification(self):
        self.blocked(lambda x:x["microtopics"][0]["exit_task"]["answer"].update(
            verification_status="INDEPENDENTLY_CHECKED"))

    def test_exit_no_hiding_eight_factor(self):
        self.blocked(lambda x:x["microtopics"][0]["exit_task"]["answer"].update(
            reasoning=["It works for four integers."]))

    def test_wrong_exit_oracle_reference_not_accepted(self):
        self.blocked(lambda x:x["microtopics"][0]["exit_task"]["oracle"][
            "verification"].update(validator_id="unknown"))

    def test_core2_cannot_be_in_route(self):
        self.blocked(lambda x:x["teaching_routes"][0].update(cores=["CORE1A","CORE2"]))

    def test_family_cannot_claim_source_questions(self):
        self.blocked(lambda x:x["question_families"][0].update(item_refs=["SOF-IMO-G9-Q001"]))

    def test_no_rendered_visual_claim(self):
        self.blocked(lambda x:x["representations"][0].update(rendered_asset_refs=["fake.svg"]))

    def test_constructed_steps_cannot_reference_unknown_move(self):
        self.blocked(lambda x:x["microtopics"][0]["construction_units"][0].update(
            step_refs=["UNKNOWN-STEP"]))

    def test_unreviewed_wrong_source_ref_fails(self):
        self.blocked(lambda x:x["relations"][0].update(source_refs=["OFFICIAL-KEY-NOT-AUTHORITY"]))

    def test_duplicate_package_nodes_not_allowed(self):
        self.blocked(lambda x:x["capabilities"].append(x["capabilities"][0].copy()))

if __name__ == "__main__":
    unittest.main()
