"""#132: deterministic, zero-write Q1 handoff and fail-closed source boundaries."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from TEST.promotion import q1_dry_run

REPO = Path(__file__).resolve().parents[1]
OVERLAYS = [
    "TEST/evidence/source-intake/ncert-exemplar-g9-number-systems-q1-q6.custody.v1.json",
    "TEST/evidence/source-intake/ncert-exemplar-g9-polynomials-q01.custody.v1.json",
    "TEST/evidence/source-intake/ncert-exemplar-g9-polynomials-q02-q06.custody.v1.json",
]
FILES = [q1_dry_run.BANK, q1_dry_run.RECEIPT, q1_dry_run.PACKAGE, *OVERLAYS]


class Q1CanonicalDryRunTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        for name in FILES:
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPO / name).read_bytes())

    def change(self, path: str, mutate) -> None:
        file = self.repo / path
        payload = json.loads(file.read_text(encoding="utf-8"))
        mutate(payload)
        file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def test_current_q1_is_deferred_with_distinct_source_and_academic_version(self):
        out = q1_dry_run.assess(self.repo)
        self.assertEqual(out["disposition"], "DEFERRED")
        self.assertEqual(out["schema_version"], q1_dry_run.SCHEMA)
        self.assertEqual(out["source"]["source_readiness"], "READY_FOR_BLUEPRINT")
        self.assertTrue(out["source"]["source_digest"].startswith("sha256:fcc60bc"))
        self.assertIsNone(out["source"]["academic_receipt_for_current_digest"])
        self.assertEqual(out["historical_canonical"]["stem_sha256"],
                         out["historical_canonical"]["historical_receipt_digest"])
        self.assertNotEqual(out["source"]["source_digest"],
                            out["historical_canonical"]["stem_sha256"])
        self.assertEqual(out["candidate"]["canonical_question_id"], q1_dry_run.CANONICAL_ID)
        self.assertEqual(out["candidate"]["stem"], "Which one of the following is a polynomial?")
        self.assertEqual(out["candidate"]["official_answer_summary"],
                         "(C) x² + 3x^(3/2)/√x")
        self.assertEqual(out["regeneration"]["mode"], "PLAN_ONLY_NOT_EXECUTED")
        self.assertEqual(out["regeneration"]["producer_sequence"],
                         list(q1_dry_run.PRODUCER_SEQUENCE))
        self.assertFalse(out["regeneration"]["canonical_writes"])
        self.assertEqual(out["effects"], {"files_written": [], "published": False, "accepted": False})
        self.assertEqual(out["authority"]["independent_academic_review_for_candidate"], "MISSING")
        self.assertEqual(out["authority"]["owner_promotion_authorization"], "ABSENT")
        self.assertNotIn("ACCEPTED", json.dumps(out))

    def test_runs_without_any_test_html_and_never_modifies_a_source_file(self):
        """Deletion independence: the mapping uses authority records, not copied TEST pages."""
        self.assertFalse((self.repo / "public").exists())
        self.assertFalse((self.repo / "docs").exists())
        before = {name: (self.repo / name).read_bytes() for name in FILES}
        first = q1_dry_run.assess(self.repo)
        second = q1_dry_run.assess(self.repo)
        self.assertEqual(first, second)
        self.assertEqual({name: (self.repo / name).read_bytes() for name in FILES}, before)
        self.assertFalse((self.repo / "publication").exists())
        self.assertFalse((self.repo / "artifacts").exists())
        self.assertNotIn("public/test", json.dumps(first["candidate"]))
        self.assertNotIn("docs/test", json.dumps(first["candidate"]))
        self.assertNotIn("ncert-exemplar-g9-math-u02-q01",
                         first["candidate"]["canonical_question_id"])

    def test_fingerprint_covers_actual_canonical_candidate_bytes(self):
        result = q1_dry_run.assess(self.repo)
        self.assertEqual(result["candidate_digest"],
                         q1_dry_run._candidate_digest(result["candidate"]))
        modified = copy.deepcopy(result["candidate"])
        modified["stem"] += " changed"
        self.assertNotEqual(result["candidate_digest"], q1_dry_run._candidate_digest(modified))

    def test_duplicate_stable_source_identity_is_never_mapped(self):
        def duplicate(payload):
            original = next(q for q in payload["questions"] if q["id"] == q1_dry_run.SOURCE_ID)
            payload["questions"].append(copy.deepcopy(original))
        self.change(q1_dry_run.BANK, duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate source id"):
            q1_dry_run.assess(self.repo)

    def test_duplicate_canonical_id_is_rejected(self):
        def duplicate(payload):
            original = next(q for q in payload["questions"] if q["id"] == q1_dry_run.CANONICAL_ID)
            payload["questions"].append(copy.deepcopy(original))
        self.change(q1_dry_run.PACKAGE, duplicate)
        with self.assertRaisesRegex(ValueError, "expected exactly one"):
            q1_dry_run.assess(self.repo)

    def test_coordinated_stem_rehash_cannot_replay_old_source_witness(self):
        def alter_bank(payload):
            row = next(q for q in payload["questions"] if q["id"] == q1_dry_run.SOURCE_ID)
            row["stem"] = "Forged revised question"
            row["stem_sha256"] = q1_dry_run._text_digest(row["stem"])
        def alter_overlay(payload):
            payload["records"][0]["stem_sha256"] = q1_dry_run._text_digest("Forged revised question")
        self.change(q1_dry_run.BANK, alter_bank)
        self.change(OVERLAYS[1], alter_overlay)
        with self.assertRaisesRegex(ValueError, "question witness scope"):
            q1_dry_run.assess(self.repo)

    def test_answer_custody_forgery_is_rejected(self):
        self.change(OVERLAYS[1], lambda payload: payload["records"][0]["official_answer"].update(
            {"answer_key": "(A)"}))
        with self.assertRaisesRegex(ValueError, "official answer differs"):
            q1_dry_run.assess(self.repo)

    def test_rebound_academic_pass_without_revalidating_canonical_is_rejected(self):
        def mutate(payload):
            row = next(q for q in payload["records"] if q["source_id"] == q1_dry_run.SOURCE_ID)
            row["stem_sha256"] = q1_dry_run._text_digest("Which one of the following is a polynomial?")
        self.change(q1_dry_run.RECEIPT, mutate)
        with self.assertRaisesRegex(ValueError, "historical canonical/academic lineage"):
            q1_dry_run.assess(self.repo)

    def test_mutated_canonical_source_version_is_rejected(self):
        def mutate(payload):
            row = next(q for q in payload["questions"] if q["id"] == q1_dry_run.CANONICAL_ID)
            row["stem"] = "Changed canonical Q1"
        self.change(q1_dry_run.PACKAGE, mutate)
        with self.assertRaisesRegex(ValueError, "historical canonical/academic lineage"):
            q1_dry_run.assess(self.repo)

    def test_bad_source_locator_or_provenance_is_rejected(self):
        self.change(OVERLAYS[1], lambda payload: payload["records"][0]["source_locator"].update(
            {"printed_page": 99}))
        with self.assertRaisesRegex(ValueError, "Q1 official source, locator"):
            q1_dry_run.assess(self.repo)

    def test_cli_emits_explicit_rejected_nonzero_and_never_accepts_approval_flag(self):
        self.change(q1_dry_run.PACKAGE, lambda payload: payload["questions"].clear())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = q1_dry_run.main(["--repo", str(self.repo)])
        self.assertEqual(rc, 1)
        decision = json.loads(out.getvalue())
        self.assertEqual(decision["disposition"], "REJECTED")
        self.assertEqual(decision["effects"], {"files_written": [], "published": False, "accepted": False})
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
            q1_dry_run.main(["--repo", str(self.repo), "--approve"])
        self.assertEqual(exc.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
