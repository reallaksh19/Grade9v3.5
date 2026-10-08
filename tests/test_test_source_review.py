"""R4 primary-source visual observations do not grant source READY."""
from __future__ import annotations

import copy
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
