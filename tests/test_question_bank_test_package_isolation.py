from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import question_bank_platform as qbp


def canonical_question() -> dict:
    return {
        "id": "BIO-Q1",
        "subject": "Biology",
        "topic": "Cell Biology",
        "question_type": "constructed_response",
        "exam": "Fixture",
        "year": 2026,
        "paper": "A",
        "question_number": "1",
        "stem": "State one role of mitochondria.",
        "subparts": [],
        "options": [],
        "conditions": [],
        "difficulty": {"band": "D1", "score": 2},
        "primary_capability_ref": "CAP-BIO-CELL",
        "secondary_capability_refs": [],
        "family_ref": "FAM-BIO-CELL",
        "answer": {"summary": "Energy release"},
    }


def write_package(root: Path, subject: str, name: str, microtopics: list[dict]) -> None:
    library = root / subject / "library"
    library.mkdir(parents=True, exist_ok=True)
    (library / name).write_text(json.dumps({
        "subject": subject,
        "microtopics": microtopics,
    }), encoding="utf-8")


class TestQuestionBankPackageIsolation(unittest.TestCase):
    def test_unrelated_or_conflicting_test_package_does_not_change_canonical_platform_identity(self):
        browser = {"questions": [canonical_question()]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_package(root, "Biology", "canonical.json", [{
                "id": "MIC-BIO-CELL",
                "title": "Cell energy release",
                "primary_capability_ref": "CAP-BIO-CELL",
            }])
            before_titles = qbp.load_subtopic_titles(root, browser["questions"])
            before = qbp.assemble_platform(browser, subtopic_titles=before_titles)

            write_package(root, "TEST", "sandbox.json", [
                {"id": "MIC-TEST-OTHER", "title": "Sandbox only", "primary_capability_ref": "CAP-TEST-OTHER"},
                {"id": "MIC-TEST-HIJACK", "title": "Wrong subject claim", "primary_capability_ref": "CAP-BIO-CELL"},
            ])
            after_titles = qbp.load_subtopic_titles(root, browser["questions"])
            after = qbp.assemble_platform(browser, subtopic_titles=after_titles)

        self.assertEqual(before_titles, {
            "CAP-BIO-CELL": {"title": "Cell energy release", "source_ref": "MIC-BIO-CELL"},
        })
        self.assertEqual(after_titles, before_titles)
        self.assertEqual(after["build_id"], before["build_id"])
        self.assertEqual(after["catalog"], before["catalog"])
        self.assertEqual(after["search"], before["search"])


if __name__ == "__main__":
    unittest.main()
