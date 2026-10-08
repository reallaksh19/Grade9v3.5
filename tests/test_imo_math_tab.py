"""Adversarial tests for public Maths-tab IMO research-only topic sorting and rights."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT / "TEST" / "imo-research"))
from validate_math_tab_imo_topics import (  # noqa: E402
    TopicBrowserError,validate_directory
)
INDEX=ROOT/"Mathematics"/"research"/"imo-g9-topic-browser.v1.json"
PUBLIC=ROOT/"public"/"mathematics"/"imo-grade9"/"index.html"
DOCS=ROOT/"docs"/"mathematics"/"imo-grade9"/"index.html"
PUBLIC_HUB=ROOT/"public"/"mathematics"/"index.html"
DOCS_HUB=ROOT/"docs"/"mathematics"/"index.html"

class ImoMathTabTests(unittest.TestCase):
    def setUp(self):
        ctx=tempfile.TemporaryDirectory()
        self.addCleanup(ctx.cleanup)
        temp=Path(ctx.name)
        self.paths={}
        for name,source in (("index",INDEX),("public",PUBLIC),("docs",DOCS),
                            ("public_hub",PUBLIC_HUB),("docs_hub",DOCS_HUB)):
            dest=temp/(name+".txt")
            dest.write_bytes(source.read_bytes())
            self.paths[name]=dest

    def check(self):
        return validate_directory(
            index=self.paths["index"],public=self.paths["public"],
            docs=self.paths["docs"],public_hub=self.paths["public_hub"],
            docs_hub=self.paths["docs_hub"]
        )

    def mutate_data(self,fn):
        path=self.paths["index"]
        d=json.loads(path.read_text(encoding="utf-8"))
        fn(d)
        path.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")

    def mutate_html(self,name,old,new):
        path=self.paths[name]
        txt=path.read_text(encoding="utf-8")
        assert old in txt, f"{name}: old fixture absent"
        path.write_text(txt.replace(old,new,1),encoding="utf-8")

    def rejects(self,change):
        change()
        with self.assertRaises(TopicBrowserError):
            self.check()

    def test_exact_count_and_public_research_boundary(self):
        result=self.check()
        self.assertEqual((result["source_linked_question_positions"],
                          result["model_authored_practice_stems_visible"],
                          result["topic_groups"],result["source_conflict_rows"]),
                         (68,7,15,11))
        self.assertEqual((result["source_stems_redistributed"],
                          result["official_source_cores_accepted"],
                          result["qrt_cells_accepted"]),(0,0,0))

    def test_source_question_missing(self):
        self.rejects(lambda:self.mutate_data(lambda d:d["records"].pop(0)))

    def test_duplicate_question_id(self):
        self.rejects(lambda:self.mutate_data(lambda d:d["records"][1].update(
            id=d["records"][0]["id"])))

    def test_topic_label_reassigned(self):
        self.rejects(lambda:self.mutate_data(lambda d:d["records"][0].update(
            topic_id="UNLISTED")))

    def test_source_stem_must_never_be_embedded(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(source_stem="copied protected original SOF question")))

    def test_source_choices_must_never_be_embedded(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(source_options=["A","B","C","D"])))

    def test_source_figures_must_never_be_embedded(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(source_figure="data:image/png;base64,fake")))

    def test_source_custody_cannot_be_claimed(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(source_custody="FULL_VERIFIED")))

    def test_source_rights_cannot_be_claimed(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(rights_status="GRANTED")))

    def test_source_core2_cannot_be_auto_admitted(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(core2_admitted=True)))

    def test_qrt_cannot_be_auto_accepted(self):
        self.rejects(lambda:self.mutate_data(lambda d:d.update(canonical_qrt_accepted=7)))

    def test_published_draft_is_not_learner_core_product(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="AUTHORED_PRACTICE_PREVIEW"
        ).update(learner_core_product_published=True)))

    def test_author_cannot_be_relabelled_official(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="AUTHORED_PRACTICE_PREVIEW"
        ).update(origin="OFFICIAL_SOF_PAPER")))

    def test_author_stem_cannot_be_rewritten(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="AUTHORED_PRACTICE_PREVIEW"
        ).update(stem="This has been rewritten silently.")))

    def test_extension_hold_006_cannot_disappear(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["id"]=="IMO-G9-ORIGINAL-PRACTICE-006"
        ).update(provisional_curriculum_scope="TOPIC_MATCH_ONLY")))

    def test_extension_hold_007_cannot_disappear(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["id"]=="IMO-G9-ORIGINAL-PRACTICE-007"
        ).update(provisional_curriculum_scope="TOPIC_MATCH_ONLY")))

    def test_source_link_cannot_be_repointed(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="SOF_SOURCE_REFERENCE_ONLY"
        ).update(source_pdf_url="https://example.invalid/fake.pdf")))

    def test_sample_q1_cannot_be_folded_back_into_seed(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["id"]=="SOF-IMO-G09-SAMPLE-2026-27-Q001"
        ).update(source_membership="OWNER_SEED_66")))

    def test_q32_q33_split_identity_must_survive(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["id"]=="SOF-IMO-G09-L1-2025-26-A-Q033"
        ).update(original_number_claim="32")))

    def test_wrong_source_git_sha_rejected(self):
        self.rejects(lambda:self.mutate_data(lambda d:d["source_git_blobs"][0].update(
            git_blob_sha="0"*40)))

    def test_mirrored_docs_must_match_public(self):
        self.rejects(lambda:self.mutate_html("docs","68 SOF source-paper references",
                                             "67 SOF source-paper references"))

    def test_math_hub_link_required(self):
        self.rejects(lambda:self.mutate_html("public_hub",'href="imo-grade9/index.html"',
                                             'href="missing.html"'))

    def test_authored_visible_question_text_required(self):
        self.rejects(lambda:self.mutate_html("public",
            "A student claims that multiplying any three consecutive positive integers",
            "Someone claims that multiplying any three consecutive positive integers"))

    def test_html_source_link_keeps_exact_official_source(self):
        self.rejects(lambda:self.mutate_html("public",
            "https://sofworld.org/download/file/fid/73719",
            "https://example.invalid/sample.pdf"))

    def test_html_no_secret_answer_leaks(self):
        self.rejects(lambda:self.mutate_html("public",
            "No answers or solutions appear on this page.",
            "Answers are fully supplied on this page."))

    def test_html_topic_header_cannot_disappear(self):
        self.rejects(lambda:self.mutate_html("public",
            'data-topic="COORD"','data-topic="INVALID"'))

    def test_accessible_filter_must_exist(self):
        self.rejects(lambda:self.mutate_html("public",
            '<label for="imo-topic-select">','<label for="missing">'))

    def test_extra_html_question_id_rejected(self):
        self.rejects(lambda:self.mutate_html("public",
            'id="IMO-G9-ORIGINAL-PRACTICE-001"',
            'id="SOF-IMO-G09-SAMPLE-2026-27-Q099"'))

    def test_public_preview_has_explicit_owner_instruction(self):
        self.rejects(lambda:self.mutate_data(lambda d:next(
            x for x in d["records"] if x["kind"]=="AUTHORED_PRACTICE_PREVIEW"
        ).update(question_display_authorization="AUTOMATIC_CI")))

if __name__=="__main__":
    unittest.main()
