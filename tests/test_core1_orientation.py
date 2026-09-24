from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from Shared.library import core1_orientation


def package_fixture() -> dict:
    return {
        "subject": "Test",
        "buckets": [{
            "id": "BUCKET-TEST",
            "title": "Test bucket",
            "intrinsic_badge": "MEDIUM",
            "badge_reason": "The transition requires a real conceptual decision.",
            "curriculum_mappings": [{
                "board": "TEST",
                "grade": 9,
                "mapping_status": "CANDIDATE",
            }],
            "conventions": [{
                "id": "CONV-TEST",
                "statement": "Declare +x before reading signed values.",
            }],
            "scope": {
                "covers": "One bounded test concept.",
                "excluded": ["Everything outside the bounded concept."],
                "extension_refs": [],
            },
            "primary_representation_ref": "REP-TEST",
        }],
        "microtopics": [{
            "id": "MIC-TEST",
            "title": "Test inference",
            "bucket_id": "BUCKET-TEST",
            "intrinsic_badge": "MEDIUM",
            "badge_reason": "Learners must distinguish two cases.",
            "inferential_jump": "One test inference.",
            "teaching_path": [{
                "id": "STEP-1",
                "action": "Construct the inference.",
                "why_valid": "The fixture needs a complete teaching route.",
            }],
            "relation_refs": ["REL-TEST"],
        }],
        "relations": [{
            "id": "REL-TEST",
            "meaning": "A canonical test relation.",
            "conditions": ["The declared condition holds."],
        }],
        "representations": [{
            "id": "REP-TEST",
            "scene_instances": [{
                "id": "SCENE-TEST",
                "cores": ["CORE1"],
                "scene": {"caption": "Test scene."},
            }],
        }],
    }


class Core1OrientationAudit(unittest.TestCase):
    def row(self, package: dict) -> dict:
        return core1_orientation.audit_bucket(
            "Test",
            "Test/library/test.v1.json",
            package,
            package["buckets"][0],
        )

    def test_complete_structural_fixture_has_no_structural_findings(self):
        row = self.row(package_fixture())
        self.assertEqual(row["finding_codes"], [])
        self.assertTrue(row["core1_compilable"])
        self.assertEqual(row["scope_state"], "AUTHORED")
        self.assertEqual(row["primary_representation_state"], "RESOLVED")
        self.assertIn(
            "CORE1_IS_MAP_NOT_TEACHING_CONSTRUCTION",
            row["manual_review_obligations"],
        )

    def test_relation_meaning_and_conditions_are_falsifiable(self):
        package = package_fixture()
        package["relations"][0]["meaning"] = ""
        package["relations"][0]["conditions"] = []
        row = self.row(package)
        self.assertIn("RELATION_MEANING_MISSING", row["finding_codes"])
        self.assertIn("RELATION_CONDITIONS_MISSING", row["finding_codes"])

    def test_authored_convention_must_have_a_statement(self):
        package = package_fixture()
        package["buckets"][0]["conventions"][0]["statement"] = ""
        row = self.row(package)
        self.assertIn("CONVENTION_STATEMENT_MISSING", row["finding_codes"])

    def test_medium_or_hard_transition_must_explain_why_it_is_hard(self):
        package = package_fixture()
        package["microtopics"][0]["badge_reason"] = ""
        row = self.row(package)
        self.assertIn("HARD_TRANSITION_BADGE_REASON_MISSING", row["finding_codes"])

    def test_curriculum_mapping_must_declare_authority_status(self):
        package = package_fixture()
        del package["buckets"][0]["curriculum_mappings"][0]["mapping_status"]
        row = self.row(package)
        self.assertIn("CURRICULUM_MAPPING_STATUS_MISSING", row["finding_codes"])

    def test_primary_representation_requires_a_core1_scene_when_declared(self):
        package = package_fixture()
        package["representations"][0]["scene_instances"][0]["cores"] = ["CORE1A"]
        row = self.row(package)
        self.assertIn("PRIMARY_REPRESENTATION_CORE1_SCENE_MISSING", row["finding_codes"])

    def test_relationless_bucket_is_reported_as_not_compilable_without_inventing_debt(self):
        package = package_fixture()
        package["microtopics"][0]["relation_refs"] = []
        row = self.row(package)
        self.assertFalse(row["core1_compilable"])
        self.assertEqual(row["core1_compilability_reason"], "NO_GOVERNING_RELATION_REF")
        self.assertNotIn("RELATION_CONDITIONS_MISSING", row["finding_codes"])

    def test_auditor_does_not_score_prose_or_compare_core1_against_teaching_path(self):
        package = package_fixture()
        package["microtopics"][0]["inferential_jump"] = "same words"
        package["microtopics"][0]["teaching_path"][0]["action"] = "same words"
        row = self.row(package)
        self.assertEqual(row["finding_codes"], [])
        self.assertIn(
            "CORE1_IS_MAP_NOT_TEACHING_CONSTRUCTION",
            row["manual_review_obligations"],
        )

    def test_forward_gate_allows_committed_legacy_debt_but_blocks_new_debt(self):
        clean = self.row(package_fixture())
        report = {"audit": "CORE1_SEMANTIC_ORIENTATION", "buckets": [clean]}
        base = core1_orientation.baseline(report)
        self.assertEqual(core1_orientation.forward_findings(report, base), [])

        damaged = copy.deepcopy(clean)
        damaged["finding_codes"] = ["RELATION_CONDITIONS_MISSING"]
        damaged_report = {"buckets": [damaged]}
        findings = core1_orientation.forward_findings(damaged_report, base)
        self.assertEqual(
            findings,
            [{
                "bucket_ref": "BUCKET-TEST",
                "subject": "Test",
                "code": "RELATION_CONDITIONS_MISSING",
                "detail": "new structural Core1 orientation debt relative to the committed baseline",
            }],
        )

    def test_repo_scan_ignores_nested_exam_bank_and_reads_ordinary_library_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "Physics" / "library"
            library.mkdir(parents=True)
            (library / "ordinary.json").write_text(
                __import__("json").dumps(package_fixture()),
                encoding="utf-8",
            )
            exam_bank = library / "exam-bank"
            exam_bank.mkdir()
            (exam_bank / "bank.json").write_text(
                __import__("json").dumps(package_fixture()),
                encoding="utf-8",
            )
            rows = list(core1_orientation.subject_packages(root))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1].name, "ordinary.json")


if __name__ == "__main__":
    unittest.main()
