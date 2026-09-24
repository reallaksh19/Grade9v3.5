"""Digest-bound review/promotion authority and release falsifiers."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.contracts import digest  # noqa: E402
from Shared.library.resolve import build_index  # noqa: E402
from Shared.tools import academic_readiness, review_authority, source_receipts  # noqa: E402


class ReviewPromotionAuthority(unittest.TestCase):
    RECORD_ID = "Q-AUTHOR-REL-01"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        for path in [
            "Shared/library/review-promotion-request.schema.json",
            "Shared/library/review-promotion-receipt.schema.json",
            "Shared/library/authoring-run-receipt.schema.json",
            "Shared/library/source-inspection-receipt.schema.json",
            "Shared/library/source-question-custody.schema.json",
        ]:
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / path, target)

        # This test isolates review authority, not dependency rollout. Copy the full
        # Physics library so cross-package prerequisites remain real, then give every
        # dependency review-stage status while leaving only the authored target candidate.
        self.package_path = self.repo / "Physics/library/relative-motion.v1.json"
        self.package_path.parent.mkdir(parents=True, exist_ok=True)
        source = None
        for original in sorted((REPO / "Physics/library").glob("*.json")):
            package = json.loads(original.read_text(encoding="utf-8"))
            for value in package.values():
                if isinstance(value, list):
                    for row in value:
                        if isinstance(row, dict) and row.get("status") == "CANDIDATE":
                            row["status"] = "CURATED"
            if original.name == "relative-motion.v1.json":
                source = package
                target = next(q for q in package["questions"] if q["id"] == self.RECORD_ID)
                target["status"] = "CANDIDATE"
            out = self.repo / "Physics/library" / original.name
            out.write_text(
                json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
        if source is None:
            raise AssertionError("relative-motion fixture package not found")
        target = next(q for q in source["questions"] if q["id"] == self.RECORD_ID)
        self.target_package = "Physics/library/relative-motion.v1.json"

        authoring = {
            "run_id": "RUN-REVIEW-FIXTURE",
            "version": "1.0.0",
            "actor_id": "author-agent",
            "run_date": "2026-09-18",
            "packet_id": "PACKET-REVIEW-FIXTURE",
            "packet_digest": "1" * 64,
            "request_id": "REQ-REVIEW-FIXTURE",
            "request_digest": "2" * 64,
            "core": "CORE2A",
            "authoring_action": "AUTHOR_CANDIDATE_QUESTION",
            "work_order_digest": "3" * 64,
            "write_scope": {
                "mode": "CANDIDATE_RECORDS_ONLY",
                "collections": ["questions"],
                "status": "CANDIDATE",
                "origin": "AUTHORED"
            },
            "library_before": {"path": self.target_package, "digest": "4" * 64},
            "library_after": {"path": self.target_package, "digest": digest(source)},
            "changed_records": [{
                "id": self.RECORD_ID,
                "collection": "questions",
                "status": "CANDIDATE",
                "origin": "AUTHORED",
                "sha256": digest(target),
            }],
            "artifacts": [],
            "validation": {
                "state": "VALIDATED",
                "findings": [],
                "note": "Synthetic authoring receipt for review authority tests."
            },
            "acceptance_commands": [],
        }
        self.authoring_path = self.repo / "publication/authoring-runs/RUN-REVIEW-FIXTURE.receipt.json"
        self.authoring_path.parent.mkdir(parents=True, exist_ok=True)
        self.authoring_path.write_text(
            json.dumps(authoring, indent=2) + "\n", encoding="utf-8"
        )
        self.authoring = authoring

    def tearDown(self):
        self.temp.cleanup()

    def package(self):
        return json.loads(self.package_path.read_text(encoding="utf-8"))

    def target(self):
        return next(q for q in self.package()["questions"] if q["id"] == self.RECORD_ID)

    def review_request(self):
        record = self.target()
        return {
            "promotion_id": "PROMO-REVIEW-01",
            "version": "1.0.0",
            "subject": "Physics",
            "target_package": self.target_package,
            "record_id": self.RECORD_ID,
            "record_digest": digest(record),
            "target_stage": "REVIEWED",
            "evidence": {
                "kind": "INDEPENDENT_REVIEW",
                "reviewer_id": "reviewer-agent",
                "reviewed_on": "2026-09-18",
                "scope": "Scientific correctness, provenance, solution and Core exposure.",
                "originals_inspected": True,
                "result": "PASS",
                "observation": "Candidate matches its stated authored provenance and is internally correct.",
                "independence": "Reviewer did not author the candidate."
            },
            "authoring_run_receipt": {
                "path": "publication/authoring-runs/RUN-REVIEW-FIXTURE.receipt.json",
                "digest": digest(self.authoring),
            },
            "prior_promotion_receipt": None,
        }

    def test_candidate_to_reviewed_is_digest_bound_and_receipted(self):
        request = self.review_request()
        report = review_authority.validate_promotion(request, self.repo)
        self.assertTrue(report["passed"], report["findings"])
        receipt = report["receipt"]
        self.assertEqual(receipt["from_stage"], "CANDIDATE")
        self.assertEqual(receipt["to_stage"], "REVIEWED")
        self.assertEqual(receipt["record_digest_before"], request["record_digest"])
        promoted = next(
            q for q in report["merged_package"]["questions"] if q["id"] == self.RECORD_ID
        )
        self.assertEqual(promoted["status"], "REVIEWED")
        self.assertEqual(receipt["record_digest_after"], digest(promoted))

    def test_self_review_is_rejected(self):
        request = self.review_request()
        request["evidence"]["reviewer_id"] = "author-agent"
        report = review_authority.validate_promotion(request, self.repo)
        self.assertIn("SELF_REVIEW_NOT_INDEPENDENT",
                      [row["point"] for row in report["findings"]])

    def test_record_edit_after_authoring_invalidates_review_request(self):
        request = self.review_request()
        package = self.package()
        target = next(q for q in package["questions"] if q["id"] == self.RECORD_ID)
        target["stem"] += " Altered after authoring."
        self.package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
        request["record_digest"] = digest(target)
        report = review_authority.validate_promotion(request, self.repo)
        self.assertIn("REVIEW_AUTHORING_DIGEST_MISMATCH",
                      [row["point"] for row in report["findings"]])

    def test_source_derived_question_cannot_be_reviewed_without_custody_proof(self):
        package = self.package()
        target = next(q for q in package["questions"] if q["id"] == self.RECORD_ID)
        target["origin"] = "ORIGINAL"
        target["origin_ref"] = "SRC-NCERT-PLANE"
        target["source_refs"] = ["SRC-NCERT-PLANE"]
        target["adaptation"] = None
        target["extensions"].pop("source_custody", None)
        self.package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

        authoring = copy.deepcopy(self.authoring)
        authoring["changed_records"][0]["origin"] = "ORIGINAL"
        authoring["changed_records"][0]["sha256"] = digest(target)
        authoring["library_after"]["digest"] = digest(package)
        self.authoring_path.write_text(json.dumps(authoring, indent=2) + "\n", encoding="utf-8")
        self.authoring = authoring

        request = self.review_request()
        report = review_authority.validate_promotion(request, self.repo)
        self.assertIn("SOURCE_CUSTODY_PROOF_MISSING",
                      [row["point"] for row in report["findings"]])

    def test_stage_skip_is_rejected(self):
        request = self.review_request()
        request["target_stage"] = "CURATED"
        request["evidence"] = {
            "kind": "CURATION_ACCEPTANCE",
            "accepted_by": "owner",
            "accepted_on": "2026-09-18",
            "scope": "Final acceptance.",
            "result": "PASS",
            "observation": "Accepted."
        }
        request["authoring_run_receipt"] = None
        report = review_authority.validate_promotion(request, self.repo)
        self.assertIn("REVIEW_PROMOTION_STAGE_INVALID",
                      [row["point"] for row in report["findings"]])

    def _write_review(self):
        report = review_authority.validate_promotion(self.review_request(), self.repo)
        self.assertTrue(report["passed"], report["findings"])
        written = review_authority.write_promotion(report, self.repo)
        return written["receipt"]

    def test_reviewed_status_without_receipt_is_unbacked(self):
        package = self.package()
        target = next(q for q in package["questions"] if q["id"] == self.RECORD_ID)
        target["status"] = "REVIEWED"
        self.package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
        authority = review_authority.authority_for_record(
            "Physics", self.target_package, target, self.repo)
        self.assertFalse(authority["verified"])
        self.assertEqual(authority["state"], "UNBACKED_REVIEWED")

    def test_record_change_after_review_invalidates_authority(self):
        self._write_review()
        package = self.package()
        target = next(q for q in package["questions"] if q["id"] == self.RECORD_ID)
        authority = review_authority.authority_for_record(
            "Physics", self.target_package, target, self.repo)
        self.assertTrue(authority["verified"])
        self.assertEqual(authority["state"], "REVIEWED")

        target["stem"] += " Post-review mutation."
        self.package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
        stale = review_authority.authority_for_record(
            "Physics", self.target_package, target, self.repo)
        self.assertFalse(stale["verified"])
        self.assertEqual(stale["state"], "UNBACKED_REVIEWED")

    def test_reviewed_to_curated_chains_through_prior_receipt(self):
        prior = self._write_review()
        reviewed = self.target()
        request = {
            "promotion_id": "PROMO-CURATE-01",
            "version": "1.0.0",
            "subject": "Physics",
            "target_package": self.target_package,
            "record_id": self.RECORD_ID,
            "record_digest": digest(reviewed),
            "target_stage": "CURATED",
            "evidence": {
                "kind": "CURATION_ACCEPTANCE",
                "accepted_by": "curriculum-owner",
                "accepted_on": "2026-09-18",
                "scope": "Final record acceptance after independent review.",
                "result": "PASS",
                "observation": "Accepted without changing the reviewed substance."
            },
            "authoring_run_receipt": None,
            "prior_promotion_receipt": {
                "path": "Reviews/receipts/PROMO-REVIEW-01.json",
                "digest": digest(prior),
            },
        }
        report = review_authority.validate_promotion(request, self.repo)
        self.assertTrue(report["passed"], report["findings"])
        written = review_authority.write_promotion(report, self.repo)
        curated = self.target()
        authority = review_authority.authority_for_record(
            "Physics", self.target_package, curated, self.repo)
        self.assertTrue(authority["verified"], authority["findings"])
        self.assertEqual(authority["state"], "CURATED")
        self.assertEqual(written["receipt"]["from_stage"], "REVIEWED")

    def test_source_sufficiency_rejects_unbacked_review_status(self):
        package = self.package()
        target = next(q for q in package["questions"] if q["id"] == self.RECORD_ID)
        target["status"] = "REVIEWED"
        self.package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
        records = build_index([package])
        receipt = {
            "receipt_id": "SRCREC-UNBACKED-REVIEW-TEST",
            "version": "1.0.0",
            "subject": "Physics",
            "bucket_id": "BUCKET-RELATIVE-MOTION",
            "source_basis": ["V3B-Relative-Motion-Library-Seed.json"],
            "resource_refs": ["SRC-AUTHOR"],
            "inspection": {
                "inspector_kind": "AGENT",
                "inspector_id": "test",
                "inspected_at": "2026-09-18",
                "access_status": "FULL_ITEM_INSPECTED",
                "sections": ["Q-AUTHOR-REL-01"],
                "content_sha256": "a" * 64,
                "snapshot_ref": "tests/synthetic"
            },
            "basis_assessment": {
                "status": "MATCH",
                "reason": "Synthetic authority falsifier.",
                "replacement_candidates": []
            },
            "coverage": {
                "CORE2": {
                    "status": "INSUFFICIENT",
                    "question_refs": [],
                    "basis": "Not under test."
                },
                "CORE2A": {
                    "status": "SUFFICIENT",
                    "question_refs": [self.RECORD_ID],
                    "basis": "Planted false sufficiency from an unbacked REVIEWED status."
                },
                "CORE2B": {
                    "status": "INSUFFICIENT",
                    "question_refs": [],
                    "basis": "Not under test."
                }
            },
            "notes": ["Synthetic test receipt."]
        }
        report = source_receipts.verify(
            receipt, records_override=records, repo=self.repo)
        self.assertIn("SOURCE_RECEIPT_UNBACKED_REVIEW_CLAIMS_SUFFICIENCY",
                      [row["point"] for row in report["findings"]])


class AcademicReleaseAuthority(unittest.TestCase):
    def test_raw_reviewed_status_does_not_make_release_reviewed(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            source = json.loads(
                (REPO / "Physics/library/relative-motion.v1.json").read_text(encoding="utf-8")
            )
            for row in source["microtopics"]:
                row["status"] = "REVIEWED"
            path = repo / "Physics/library/relative-motion.v1.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(source, indent=2) + "\n", encoding="utf-8")
            for schema in [
                "Shared/library/review-promotion-receipt.schema.json",
                "Shared/library/authoring-run-receipt.schema.json",
            ]:
                target = repo / schema
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / schema, target)

            board = json.loads(
                (REPO / "Physics/matrices/relative-motion.rungs.json").read_text(encoding="utf-8")
            )
            mics = {row["id"]: row for row in source["microtopics"]}
            review = academic_readiness.review_state(board, mics, "Physics", repo)
            self.assertEqual(review["state"], "NOT_REVIEWED")
            self.assertTrue(
                any(state == "UNBACKED_REVIEWED"
                    for state in review["effective_review_states"])
            )


if __name__ == "__main__":
    unittest.main()
