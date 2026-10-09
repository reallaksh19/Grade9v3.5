"""Falsification checks for candidate Core1A teaching preview and PDF custody queue."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "TEST/imo-research"))
from validate_qualification_evidence import git_blob_sha  # noqa: E402
from validate_core1a_test_review import (  # noqa: E402
    PreviewError, validate_preview
)

FILENAMES = {
    "package": REPO/"TEST/library/imo-g9-divisibility-core1a.v1.json",
    "preview": REPO/"public/test/imo-grade9/core1a.html",
    "mirror": REPO/"docs/test/imo-grade9/core1a.html",
    "math_pub": REPO/"public/mathematics/imo-grade9/index.html",
    "math_docs": REPO/"docs/mathematics/imo-grade9/index.html",
    "receipt": REPO/"TEST/imo-research/intake/core1a-test-review-receipt.v1.json",
    "queue": REPO/"TEST/imo-research/intake/core2-source-acquisition-handoff.v1.json",
}


class Core1ATestReviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root=Path(temp.name)
        self.files={}
        for name,original in FILENAMES.items():
            file=root/(name+original.suffix)
            file.write_bytes(original.read_bytes())
            self.files[name]=file

    def validate(self):
        return validate_preview(
            pkg_path=self.files["package"],
            preview=self.files["preview"],
            mirror=self.files["mirror"],
            math_pub=self.files["math_pub"],
            math_docs=self.files["math_docs"],
            receipt_path=self.files["receipt"],
            queue_path=self.files["queue"],
        )

    def edited(self,name,mutate):
        file=self.files[name]
        obj=json.loads(file.read_text(encoding="utf-8"))
        mutate(obj)
        file.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")

    def edit_page(self,before,after,which=("preview","mirror"),repin=True):
        for name in which:
            file=self.files[name]
            content=file.read_text(encoding="utf-8")
            self.assertIn(before,content)
            file.write_text(content.replace(before,after,1),encoding="utf-8")
        if repin:
            self.repin()

    def repin(self):
        receipt=json.loads(self.files["receipt"].read_text(encoding="utf-8"))
        receipt["derived_review_pages"]=[
            {"path":"public/test/imo-grade9/core1a.html",
             "git_blob_sha":git_blob_sha(self.files["preview"])},
            {"path":"docs/test/imo-grade9/core1a.html",
             "git_blob_sha":git_blob_sha(self.files["mirror"])},
        ]
        receipt["mathematics_topic_links"]=[
            {"path":"public/mathematics/imo-grade9/index.html",
             "git_blob_sha":git_blob_sha(self.files["math_pub"])},
            {"path":"docs/mathematics/imo-grade9/index.html",
             "git_blob_sha":git_blob_sha(self.files["math_docs"])},
        ]
        receipt["core2_source_acquisition_handoff"]["git_blob_sha"] = (
            git_blob_sha(self.files["queue"])
        )
        self.files["receipt"].write_text(
            json.dumps(receipt,indent=2)+"\n",encoding="utf-8")

    def reject(self,mutate):
        mutate()
        with self.assertRaises(PreviewError):
            self.validate()

    def test_review_page_is_present_but_not_canonically_accepted(self):
        result=self.validate()
        self.assertEqual(
            (result["teaching_steps"],result["residue_table_cases"],
             result["model_exit_steps"],result["source_pdfs_pending"]),
            (4,3,4,4))
        self.assertEqual(
            (result["source_positions_held"],result["source_core2_admitted"],
             result["canonical_core1a_admitted"],result["qrt_accepted"]),
            (68,0,0,0))

    def test_mirrors_must_stay_exact(self):
        self.reject(lambda:self.edit_page(
            "TEST REVIEW ONLY · CANDIDATE",
            "TEST REVIEW · CANDIDATE",which=("mirror",),repin=True))

    def test_repinning_cannot_pretend_core1a_approval(self):
        self.reject(lambda:self.edit_page(
            'data-g9-role="TEST"','data-g9-role="CORE1A"'))

    def test_study_page_cannot_drop_candidate_disclosure(self):
        self.reject(lambda:self.edit_page(
            "TEST REVIEW ONLY · CANDIDATE", "LEARNER CORE1A READY"))

    def test_no_false_browser_testing_status(self):
        self.reject(lambda:self.edit_page(
            "real device, keyboard, assistive-technology and print inspections are NOT RUN",
            "real device, keyboard, assistive-technology and print inspections PASSED"))

    def test_inferential_jump_never_dropped(self):
        self.reject(lambda:self.edit_page(
            "Convert finite observations into a universal argument",
            "Check a few examples and declare a universal argument"))

    def test_step_two_parity_action_remains(self):
        self.reject(lambda:self.edit_page(
            "Consider n and n+1: one is even",
            "Assume n is even for convenience"))

    def test_each_why_valid_justification_remains(self):
        self.reject(lambda:self.edit_page(
            "Parity alternates in adjacent integers.",
            "The result is obvious."))

    def test_four_step_order_mandatory(self):
        self.reject(lambda:self.edit_page(
            'data-core1a-step-id="TC-04"',
            'data-core1a-step-id="TC-03"'))

    def test_divisible_modulo_three_row_zero_required(self):
        self.reject(lambda:self.edit_page(
            'data-residue="0"','data-residue="8"'))

    def test_modulo_three_row_one_identity_protected(self):
        self.reject(lambda:self.edit_page(
            '<code>n+2</code></td><td>The remainder',
            '<code>n+1</code></td><td>The remainder'))

    def test_modulo_three_row_two_identity_protected(self):
        self.reject(lambda:self.edit_page(
            '<code>n+1</code></td><td>The remainder',
            '<code>n+2</code></td><td>The remainder'))

    def test_exit_disclosure_not_open_by_default(self):
        self.reject(lambda:self.edit_page(
            '<details class="model-proof" id="exit-model-closure">',
            '<details class="model-proof" id="exit-model-closure" open>'))

    def test_model_answer_requires_all_four_reasoning_lines(self):
        self.reject(lambda:self.edit_page(
            "Exactly one of these four has remainder 0 modulo 4",
            "A single even number provides everything"))

    def test_exit_task_must_keep_general_proof_domain(self):
        self.reject(lambda:self.edit_page(
            "Give a general proof, not only examples.",
            "Just check a few examples."))

    def test_misconception_repair_must_remain(self):
        self.reject(lambda:self.edit_page(
            "Use complete residue cases modulo 2 and 3",
            "Just use several numeric examples"))

    def test_no_external_script_or_figure(self):
        self.reject(lambda:self.edit_page(
            '<script src="../../js/site-header.js"',
            '<script src="https://example.invalid/script.js"'))

    def test_no_source_sof_paper_item_added(self):
        self.reject(lambda:self.edit_page(
            "No authentic SOF question stem",
            "SOF-IMO-G09-L1-2025-26-A-Q001 original item"))

    def test_math_hub_must_keep_explicit_review_link(self):
        self.reject(lambda:self.edit_page(
            'data-test-review-link="IMO-G9-CORE1A-CANDIDATE"',
            'data-test-review-link="FULLY_ADMITTED_CORE1A"',
            which=("math_pub","math_docs")))

    def test_source_bytes_cannot_be_invented(self):
        def mutate():
            self.edited("queue",lambda d:d["source_documents_queue"][0].update(
                document_sha256="f"*64))
            self.repin()
        self.reject(mutate)

    def test_pdf_count_cannot_silently_increase(self):
        def mutate():
            self.edited("queue",lambda d:d.update(retained_pdf_documents=1))
            self.repin()
        self.reject(mutate)

    def test_source_host_cannot_be_relabelled_official(self):
        def mutate():
            self.edited("queue",lambda d:d["source_documents_queue"][0].update(
                origin_host_kind="SOF_ORGANIZER_HOSTED_PDF"))
            self.repin()
        self.reject(mutate)

    def test_sample_source_pdf_cannot_be_changed(self):
        def mutate():
            self.edited("queue",lambda d:d["source_documents_queue"][-1].update(
                requested_pdf_url="https://example.invalid/other.pdf"))
            self.repin()
        self.reject(mutate)

    def test_rights_cannot_be_granted_by_fiat(self):
        def mutate():
            self.edited("queue",lambda d:d["source_documents_queue"][0].update(
                publisher_reproduction_permission="GRANTED"))
            self.repin()
        self.reject(mutate)

    def test_public_preview_is_not_canonical_publication(self):
        self.reject(lambda:self.edited("receipt",lambda d:d[
            "content_claims"].update(published_canonical_learner_product=True)))

    def test_assistive_technology_qa_not_claimed(self):
        self.reject(lambda:self.edited("receipt",lambda d:d[
            "review_checks"].update(
                assistive_technology_screen_reader="PASSED")))

    def test_no_fake_authorized_pdf_receipt(self):
        def mutate():
            self.edited("queue",lambda d:d["source_documents_queue"][0].update(
                acquisition_receipt_ref="ACQ-INVENTED"))
            self.repin()
        self.reject(mutate)

    def test_original_candidate_package_cannot_be_silently_changed(self):
        self.reject(lambda:self.edited("package",lambda d:d.update(
            status="CURATED")))


if __name__ == "__main__":
    unittest.main()
