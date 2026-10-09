"""Fail-closed checks for the IMO Index Laws F01 research crosswalk (Issue #327).

No authentic Core2, canonical Core1A, QRT or learner release is asserted here.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "TEST/imo-research/intake/imo-index-laws-subtopic-pilot.v1.json"
BROWSER = ROOT / "Mathematics/research/imo-g9-topic-browser.v1.json"
CUSTODY = ROOT / "TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
SUBTOPICS = ROOT / "TEST/imo-research/taxonomy/sof-class9-subtopics.v1.json"

EXPECTED = {
    "SOF-IMO-G09-L1-2024-25-B-Q026": "COMMON_BASE_SUBSTITUTION_RESEARCH_HYPOTHESIS",
    "SOF-IMO-G09-L1-2025-26-A-Q035": "SEPARATE_FRACTIONAL_NEGATIVE_INDEX_LAW_FAMILY_NOT_SAME_MICROTOPIC",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_pilot(pilot: dict, browser: dict, custody: dict, subtopics: dict) -> None:
    """Require independently held source facts and explicit null learner routes."""
    if pilot.get("schema") != "imo-g9-f01-index-laws-provisional-crosswalk-v1":
        raise ValueError("Unrecognized F01 pilot schema")
    if (pilot.get("governing_issue"), pilot.get("source_custody_governing_issue")) != (327, 294):
        raise ValueError("Issue ownership drift")
    if pilot.get("canonical_authority") != "DERIVED_RESEARCH_ONLY_NOT_PRODUCT_OR_QRT":
        raise ValueError("Research cannot become academic authority")
    scope = pilot["scope"]
    if (scope.get("topic_id"), scope.get("subtopic_id")) != ("NS", "NS-INDEX-LAWS"):
        raise ValueError("Wrong academic topic/subtopic")
    named = {x["id"]: x for x in subtopics["subtopics"]}
    sub = named["NS-INDEX-LAWS"]
    if scope.get("subtopic_status") != sub["academic_status"] or scope.get("provisional_microconcept_ref") != sub["microconcept_ref"]:
        raise ValueError("Unreviewed taxonomy was promoted or incorrectly mapped")
    if any(scope.get(x) != 0 for x in ("source_core2_admitted", "source_custody_eligible", "learner_products_released")):
        raise ValueError("False released or admitted product count")
    if scope.get("launch_authorized") is not False:
        raise ValueError("Unreviewed home may not launch")

    # The pilot may cover only two items, but it must not corrupt the 68-source
    # census, inflate the old 66-entry map, or admit other unverified sources.
    original_refs = [r for r in browser["records"] if r["kind"] == "SOF_SOURCE_REFERENCE_ONLY"]
    authored_previews = [r for r in browser["records"] if r["kind"] == "AUTHORED_PRACTICE_PREVIEW"]
    source_ids = [r["id"] for r in original_refs]
    custody_ids = [r["question_id"] for r in custody["records"]]
    if (len(source_ids) != 68 or len(set(source_ids)) != 68
        or len(custody_ids) != 68 or len(set(custody_ids)) != 68
        or set(source_ids) != set(custody_ids)
        or len(authored_previews) != 7):
        raise ValueError("68 genuine reference identities and seven separate authored previews must be conserved")
    if (sum(r["source_membership"] == "OWNER_SEED_66" for r in original_refs) != 66
        or {r["id"] for r in original_refs
            if r["source_membership"] == "ADDITIONAL_ORGANIZER_SAMPLE_2"} != {
                "SOF-IMO-G09-SAMPLE-2026-27-Q001",
                "SOF-IMO-G09-SAMPLE-2026-27-Q003"}):
        raise ValueError("Historical seed66 versus two new organizer samples conflated")
    if any(r.get("core2_eligible") is not False or r.get("core2_admitted") is not False
           or r.get("learner_published") is not False for r in custody["records"]):
        raise ValueError("Nonadmitted source census was silently promoted")
    if any(r.get("original_source_claim") is not False for r in authored_previews):
        raise ValueError("Authored practice recast as an original SOF source")
    rows = pilot["source_questions"]
    if len(rows) != 2 or {row["question_id"] for row in rows} != set(EXPECTED):
        raise ValueError("Missing, duplicate or extra source identities")
    browsed = {x["id"]: x for x in browser["records"]}
    held = {x["question_id"]: x for x in custody["records"]}
    for row in rows:
        sid = row["question_id"]
        original = browsed[sid]
        source = held[sid]
        if row["conceptual_bridge"] != EXPECTED[sid]:
            raise ValueError("Source mathematics family conflation: " + sid)
        for dst, key in (
            ("browser_kind", "kind"), ("source_id", "source_id"),
            ("printed_position_claim", "original_number_claim"),
            ("source_reference_url", "source_pdf_url"),
            ("provisional_concept_summary", "concept_summary"),
            ("exam_section", "exam_section"),
            ("source_membership", "source_membership"),
            ("discrepancy_case", "discrepancy_case"),
        ):
            if row.get(dst) != original.get(key):
                raise ValueError("Stale research browser identity: " + sid + " " + dst)
        if original.get("kind") != "SOF_SOURCE_REFERENCE_ONLY" or original.get("subtopic_id") != "NS-INDEX-LAWS":
            raise ValueError("Source identity misclassified: " + sid)
        for dst, key in (
            ("source_custody_status", "source_seed_custody_status"),
            ("source_sha256", "document_retained_sha256"),
            ("source_locator_pdf_page_index", "source_locator_pdf_page_index"),
            ("source_question_fidelity", "source_text_fidelity_status"),
            ("rights_status", "publisher_publication_rights"),
            ("source_core2_eligible", "core2_eligible"),
            ("source_core2_admitted", "core2_admitted"),
            ("learner_published", "learner_published"),
            ("next_source_action", "next_source_action"),
        ):
            if row.get(dst) != source.get(key):
                raise ValueError("Stale custody ledger status: " + sid + " " + dst)
        if row.get("provenance") != "OWNER_SEED_SOURCE_REFERENCE_ONLY":
            raise ValueError("Source provenance substituted")
        if (row.get("source_core2_eligible") is not False or
            row.get("source_core2_admitted") is not False or
            row.get("learner_published") is not False or
            row.get("source_sha256") is not None or
            row.get("rights_status") != "NOT_REVIEWED" or
            row.get("disposition") != "SOURCE_CUSTODY_HOLD"):
            raise ValueError("Pilot source not eligible for source-Core2")
    # A visual page locator is a narrow observation, not the official custody ledger.
    # It must never mutate that ledger's unverified locator or imply that the
    # source file bytes, a version-stable digest, rights or question fidelity exist.
    observed = {
        "SOF-IMO-G09-L1-2024-25-B-Q026": (26, "B", "COMMON_BASE_EXPONENT_EQUATION"),
        "SOF-IMO-G09-L1-2025-26-A-Q035": (35, "A", "FRACTIONAL_NEGATIVE_INDICES_WITH_ROOTS"),
    }
    for row in rows:
        question_number, exam_set, family = observed[row["question_id"]]
        obs = row.get("source_locator_visual_observation")
        if not isinstance(obs, dict):
            raise ValueError("Missing remote-PDF visual locator observation")
        expected = {
            "observation_class": "REMOTE_SCHOOL_HOSTED_PDF_PAGE_VISUAL_ONLY",
            "observed_utc_date": "2026-10-09",
            "viewed_pdf_url": row["source_reference_url"],
            "pdf_page_index_zero_based": 4,
            "printed_page_number": 5,
            "question_number_visible": question_number,
            "exam_set_visible": exam_set,
            "math_family_visible": family,
            "file_bytes_retained": False,
            "pdf_sha256": None,
            "source_question_components_fidelity_verified": False,
            "source_rights_granted": False,
            "core2_admission_granted": False,
        }
        if any(obs.get(k) != v or isinstance(obs.get(k), bool) != isinstance(v, bool)
               for k, v in expected.items()):
            raise ValueError("Remote source observation cannot be forged as custody or authority")
        if not isinstance(obs.get("note"), str) or "UNVERIFIED" not in obs["note"]:
            raise ValueError("Missing publication/custody limitation on visual observation")
        if row["source_locator_pdf_page_index"] is not None:
            raise ValueError("Visual observation is not an official source custody receipt")
    authored = pilot["authored_teaching_candidate"]
    if (authored.get("kind") != "AUTHORED_CORE1A_TEST_CANDIDATE_NOT_SOURCE_CORE2"
        or authored.get("provenance") != "MODEL_AUTHORED"
        or authored.get("status") != "CANDIDATE"
        or authored.get("acceptance_status") != "CANDIDATE"
        or authored.get("canonical_mapping_status") != "NOT_ACADEMICALLY_APPROVED"
        or authored.get("source_match_status") != "RESEARCH_FAMILY_HYPOTHESIS_NOT_SOURCE_QUESTION_BINDING"
        or authored.get("provisional_source_family_link") != "SOF-IMO-G09-L1-2024-25-B-Q026"
        or authored.get("basis_pr") != 312 or authored.get("competing_draft_pr") != 308):
        raise ValueError("TEST authored candidate promoted or conflated")
    route = pilot["routing"]
    if any(route.get(k) is not None for k in (
        "core1a_product_url", "core2_source_product_url", "core2a_authored_product_url")):
        raise ValueError("A held pilot cannot leak published learner links")
    if route.get("learner_publication_status") != "HELD_NOT_GENERATED":
        raise ValueError("Unapproved page cannot appear released")
    if (pilot.get("source_rights_boundary") !=
        "REFERENCES_ONLY_NO_ORIGINAL_SOF_STEMS_OPTIONS_FIGURES_KEYS_OR_PDF_BYTES_EMBEDDED"
        or pilot.get("generated_artifact_is_authoritative") is not False):
        raise ValueError("Research product authority or media rights leak")
    forbidden = ("source_stem", "source_options", "source_figure", "source_answer", "official_answer")
    if any(k in row for row in rows for k in forbidden):
        raise ValueError("Source media or answer copied into public-facing crosswalk")


class TestIndexLawsPilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = load_json(PILOT)
        cls.browser = load_json(BROWSER)
        cls.custody = load_json(CUSTODY)
        cls.subtopics = load_json(SUBTOPICS)

    def valid(self, mutate=None):
        pilot = copy.deepcopy(self.pilot)
        if mutate:
            mutate(pilot)
        check_pilot(pilot, self.browser, self.custody, self.subtopics)

    def test_held_source_crosswalk_consistent(self):
        self.valid()

    def test_reject_unverified_source_as_core2(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][0].update(source_core2_eligible=True))

    def test_reject_website_url_before_review(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["routing"].update(core2_source_product_url="/core2/fake.html"))

    def test_reject_source_family_conflation(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][1].update(
                conceptual_bridge="COMMON_BASE_SUBSTITUTION_RESEARCH_HYPOTHESIS"))

    def test_reject_test_core1a_as_academically_accepted(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["authored_teaching_candidate"].update(
                canonical_mapping_status="ACCEPTED"))

    def test_reject_wrong_provisional_subtopic(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["scope"].update(subtopic_id="POLY-DIVISIBILITY"))

    def test_global_denominator_rejects_missing_unrelated_source(self):
        browser = copy.deepcopy(self.browser)
        browser["records"] = [r for r in browser["records"]
                              if r["id"] != "SOF-IMO-G09-SAMPLE-2026-27-Q001"]
        with self.assertRaises(ValueError):
            check_pilot(self.pilot, browser, self.custody, self.subtopics)

    def test_global_denominator_rejects_unrelated_core2_promotion(self):
        census = copy.deepcopy(self.custody)
        item = next(r for r in census["records"]
                    if r["question_id"] == "SOF-IMO-G09-SAMPLE-2026-27-Q003")
        item["core2_admitted"] = True
        with self.assertRaises(ValueError):
            check_pilot(self.pilot, self.browser, census, self.subtopics)

    def test_authored_preview_cannot_claim_original_source(self):
        browser = copy.deepcopy(self.browser)
        item = next(r for r in browser["records"]
                    if r["kind"] == "AUTHORED_PRACTICE_PREVIEW")
        item["original_source_claim"] = True
        with self.assertRaises(ValueError):
            check_pilot(self.pilot, browser, self.custody, self.subtopics)

    def test_visual_source_page_identified_but_custody_held(self):
        self.valid()
        for item in self.pilot["source_questions"]:
            self.assertEqual(item["source_locator_visual_observation"]["pdf_page_index_zero_based"], 4)
            self.assertEqual(item["source_locator_visual_observation"]["printed_page_number"], 5)
            self.assertIsNone(item["source_sha256"])
            self.assertIsNone(item["source_locator_pdf_page_index"])
            self.assertFalse(item["source_locator_visual_observation"]["core2_admission_granted"])

    def test_reject_visual_locator_promoted_into_official_custody(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][0].update(
                source_locator_pdf_page_index=4))

    def test_reject_unhashed_visual_as_immutable_digest(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][0]["source_locator_visual_observation"].update(
                pdf_sha256="sha256:" + "0" * 64))

    def test_reject_visual_scan_as_rights_grant(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][1]["source_locator_visual_observation"].update(
                source_rights_granted=True))

    def test_reject_fractional_index_misidentified_as_common_base(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][1]["source_locator_visual_observation"].update(
                math_family_visible="COMMON_BASE_EXPONENT_EQUATION"))

    def test_reject_unlicensed_source_copy(self):
        with self.assertRaises(ValueError):
            self.valid(lambda p: p["source_questions"][0].update(source_stem="fabricated copied question"))


if __name__ == "__main__":
    unittest.main()
