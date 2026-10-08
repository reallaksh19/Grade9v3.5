"""R4 primary-source visual observations do not grant source READY."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import test_source_review, test_source_custody  # noqa: E402

BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
REVIEW = "TEST/evidence/source-intake/ncert-exemplar-g9-r4-u01-u02-q07-q10.review.v1.json"


class TestOfficialSourceReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((REPO / BANK).read_text(encoding="utf-8"))
        cls.review = json.loads((REPO / REVIEW).read_text(encoding="utf-8"))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.source = self.repo / BANK
        self.review_file = self.repo / REVIEW
        self.source.parent.mkdir(parents=True)
        self.review_file.parent.mkdir(parents=True)
        self.source.write_text(json.dumps(self.bank, ensure_ascii=False), encoding="utf-8")
        self.data = copy.deepcopy(self.review)
        self.write()

    def write(self):
        self.review_file.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")

    def test_current_source_review_is_an_eight_id_two_topic_observation(self):
        result = test_source_review.validate(self.repo)
        self.assertEqual(result["reviewed"], 8)
        self.assertEqual(result["custody_promotions"], 0)
        self.assertEqual(result["notation_discrepancies"],
                         ["ncert-exemplar-g9-math-u01-q07"])
        self.assertEqual({r["source_id"] for r in self.data["records"]},
                         {f"ncert-exemplar-g9-math-u{unit:02d}-q{i:02d}"
                          for unit in (1, 2) for i in range(7, 11)})
        self.assertEqual(test_source_custody.reconcile(self.repo)["ready_for_blueprint"], 0)
        current = test_source_custody.reconcile(REPO)
        self.assertEqual((current["ready_for_blueprint"], current["evidence_pending"]),
                         (12, 198))
        self.assertFalse(set(result["review_ids"]) & set(current["ready_ids"]))

    def test_coordinated_raw_and_review_rewrite_cannot_reuse_observation(self):
        """Matching mutable bank+review copies are not an independent PDF witness."""
        for variant in ("stem", "options", "identifier", "source_url"):
            with self.subTest(variant=variant):
                self.data = copy.deepcopy(self.review)
                bank = copy.deepcopy(self.bank)
                record = self.data["records"][4]  # Unit 2 Q7, notation normalised.
                source = next(q for q in bank["questions"] if q["id"] == record["source_id"])
                if variant == "stem":
                    source["stem"] += " altered"
                    source["stem_sha256"] = "sha256:" + hashlib.sha256(
                        source["stem"].encode("utf-8")).hexdigest()
                    record["captured_stem"] = source["stem"]
                    record["stem_sha256"] = source["stem_sha256"]
                elif variant == "options":
                    source["options"][0] = "(A) 99"
                    record["captured_options"] = copy.deepcopy(source["options"])
                elif variant == "identifier":
                    source["original_identifier"] = "Unit 2 Ex 2.1 Q77"
                    record["original_identifier"] = source["original_identifier"]
                else:
                    source["source_url"] = (
                        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep203.pdf"
                    )
                    record["official_question_document_url"] = source["source_url"]
                    self.data["question_documents"].append(source["source_url"])
                self.source.write_text(json.dumps(bank, ensure_ascii=False), encoding="utf-8")
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen primary-source observation scope"):
                    test_source_review.validate(self.repo)

    def test_numeric_locator_rewrite_does_not_reuse_primary_source_observation(self):
        """Well-shaped printed/PDF indices are not authenticated simply by being numbers."""
        alterations = (
            ("question printed page", "source_locator", "printed_page", 99),
            ("question PDF index", "source_locator", "pdf_page_index", 98),
            ("answer PDF index", None, "official_answer_pdf_page_index", 17),
            ("downgraded notation disclosure", None, "comparison_status", "VISUAL_MATCH"),
        )
        for label, parent, key, replacement in alterations:
            with self.subTest(label=label):
                self.data = copy.deepcopy(self.review)
                # U02 Q7 is normalised; an unreviewed downgrade must be detected.
                q = self.data["records"][4]
                target = q[parent] if parent else q
                target[key] = replacement
                self.write()
                with self.assertRaisesRegex(ValueError, "frozen primary-source observation scope"):
                    test_source_review.validate(self.repo)

    def test_review_cannot_be_replayed_or_promote_a_question(self):
        changes = (
            ("unknown", lambda d: d["records"][0].__setitem__("source_id", "other"),
             "unknown or duplicate"),
            ("duplicate", lambda d: d["records"].append(copy.deepcopy(d["records"][0])),
             "unknown or duplicate"),
            ("different stem", lambda d: d["records"][0].__setitem__("stem_sha256", "sha256:" + "0" * 64),
             "stem digest"),
            ("rewritten option", lambda d: d["records"][0]["captured_options"].append("(E) rewrite"),
             "identifier/options"),
            ("redirected source", lambda d: d["records"][0].__setitem__(
                "official_question_document_url", "https://ncert.nic.in/other.pdf"), "source document"),
            ("fabricated page", lambda d: d["records"][0]["source_locator"].__setitem__(
                "printed_page", "unverified"), "review locator"),
            ("fabricated answer", lambda d: d["records"][0].__setitem__("official_answer_key", "(A)"),
             "review answer"),
            ("suppressed mismatch", lambda d: d["records"][0].__setitem__(
                "comparison_status", "VISUAL_MATCH"), "cannot be silently cleared"),
            ("false READY", lambda d: d["records"][0].__setitem__("projection_disposition",
                                                                  "READY_FOR_BLUEPRINT"), "cannot grant"),
            ("false promotion", lambda d: d["records"][0].__setitem__("source_custody_promoted", True),
             "cannot grant"),
        )
        for label, change, reason in changes:
            with self.subTest(label=label):
                self.data = copy.deepcopy(self.review)
                change(self.data)
                self.write()
                with self.assertRaisesRegex(ValueError, reason):
                    test_source_review.validate(self.repo)


if __name__ == "__main__":
    unittest.main()
