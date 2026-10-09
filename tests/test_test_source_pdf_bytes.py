"""R4 NCERT PDF byte preflight is a measurement tool, never READY authority."""
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
from Shared.tools import test_source_pdf_bytes  # noqa: E402


class TestNCERTPDFBytePreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((REPO / test_source_pdf_bytes.MANIFEST).read_text(encoding="utf-8"))

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.repo = Path(folder.name)
        self.pdfs = self.repo / "local-pdfs"
        self.pdfs.mkdir()
        self.manifest_file = self.repo / test_source_pdf_bytes.MANIFEST
        self.manifest_file.parent.mkdir(parents=True)
        self.data = copy.deepcopy(self.manifest)
        self.write()

    def write(self):
        self.manifest_file.write_text(json.dumps(self.data), encoding="utf-8")

    @staticmethod
    def synthetic_envelope():
        # Not an authenticated official NCERT PDF; only header/footer envelope.
        return b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n" + b"PDF-TEST-ONLY\n" * 4 + b"%%EOF\n"

    def create_synthetic_files(self):
        for _, filename, _ in test_source_pdf_bytes.DOCS:
            (self.pdfs / filename).write_bytes(self.synthetic_envelope())

    def test_committed_manifest_unverified_and_zero_authority(self):
        test_source_pdf_bytes.validate_manifest(REPO)
        result = test_source_pdf_bytes.preflight(self.repo)
        self.assertEqual(result["document_count"], 3)
        self.assertEqual(result["measurements"], [])
        self.assertEqual(result["status"], "OFFICIAL_PDF_BYTES_UNAVAILABLE")
        for flag in ("source_custody_granted", "academic_pass_granted", "publication_authorized"):
            self.assertIs(result[flag], False)

    def test_local_synthetic_bytes_are_hash_measured_not_source_authenticated(self):
        self.create_synthetic_files()
        result = test_source_pdf_bytes.preflight(self.repo, self.pdfs)
        self.assertEqual(result["status"], "LOCAL_PDF_BYTES_MEASURED_UNAUTHENTICATED")
        self.assertEqual(len(result["measurements"]), 3)
        self.assertEqual(result["measurements"][0]["local_sha256"], "sha256:" +
                         hashlib.sha256(self.synthetic_envelope()).hexdigest())
        self.assertTrue(all(r["independent_official_origin_authenticated"] is False
                            and r["source_custody_granted"] is False for r in result["measurements"]))
        self.assertFalse(result["source_custody_granted"])
        self.assertFalse(result["academic_pass_granted"])
        self.assertFalse(result["publication_authorized"])

    def test_byte_change_invalidates_local_digest_without_granting_custody(self):
        self.create_synthetic_files()
        original = test_source_pdf_bytes.preflight(self.repo, self.pdfs)
        pdf = self.pdfs / "ieep202.pdf"
        pdf.write_bytes(self.synthetic_envelope().replace(b"PDF-TEST-ONLY", b"PDF-TAMPERED!", 1))
        changed = test_source_pdf_bytes.preflight(self.repo, self.pdfs)
        old_digest = original["measurements"][1]["local_sha256"]
        new_digest = changed["measurements"][1]["local_sha256"]
        self.assertNotEqual(old_digest, new_digest)
        self.assertFalse(changed["source_custody_granted"])
        self.assertFalse(changed["academic_pass_granted"])
        self.assertFalse(changed["publication_authorized"])

    def test_mutated_manifest_identity_and_authority_fail_closed(self):
        changes = (
            ("wrong official URL", lambda x: x["official_document_set"][0].__setitem__("official_url", "https://example.org/fake.pdf")),
            ("wrong PDF name", lambda x: x["official_document_set"][0].__setitem__("local_filename", "../../forged.pdf")),
            ("wrong page", lambda x: x["official_document_set"][0]["observed_pdf_page_indices"].append(999)),
            ("invent digest", lambda x: x["official_document_set"][0].__setitem__("byte_sha256", "sha256:"+"f"*64)),
            ("invent official origin", lambda x: x["official_document_set"][0].__setitem__("official_origin_authenticated", True)),
            ("byte authority", lambda x: x.__setitem__("official_pdf_bytes_obtained", True)),
            ("digest authority", lambda x: x.__setitem__("official_pdf_sha256_authenticated", True)),
            ("official origin authority", lambda x: x.__setitem__("independent_official_origin_authenticated", True)),
            ("reviewer", lambda x: x.__setitem__("independent_reviewer_approved", True)),
            ("READY", lambda x: x.__setitem__("source_custody_granted", True)),
            ("academic", lambda x: x.__setitem__("academic_pass_granted", True)),
            ("publication", lambda x: x.__setitem__("publication_authorized", True)),
            ("extra document", lambda x: x["official_document_set"].append(copy.deepcopy(x["official_document_set"][0]))),
            ("wrong source ID", lambda x: x["source_ids"].__setitem__(0, "ncert-exemplar-g9-math-u01-q01")),
            ("injected field", lambda x: x.__setitem__("official_signature_verified", True)),
            ("lost source reference", lambda x: x["source_observation_refs"].pop()),
        )
        for name, change in changes:
            with self.subTest(name=name):
                self.data = copy.deepcopy(self.manifest)
                change(self.data)
                self.write()
                with self.assertRaisesRegex(ValueError, "NCERT byte preflight"):
                    test_source_pdf_bytes.validate_manifest(self.repo)

    def test_invalid_bytes_and_incomplete_document_set_are_rejected(self):
        self.create_synthetic_files()
        candidates = (
            ("missing PDF", lambda: (self.pdfs / "ieep201.pdf").unlink()),
            ("extra PDF", lambda: (self.pdfs / "untrusted.pdf").write_bytes(self.synthetic_envelope())),
            ("non-PDF", lambda: (self.pdfs / "ieep201.pdf").write_bytes(b"not really PDF" * 10)),
            ("truncated", lambda: (self.pdfs / "ieep201.pdf").write_bytes(self.synthetic_envelope()[:-6])),
            ("empty", lambda: (self.pdfs / "ieep201.pdf").write_bytes(b"")),
        )
        for name, mutate in candidates:
            with self.subTest(name=name):
                for f in self.pdfs.glob("*.pdf"):
                    f.unlink()
                self.create_synthetic_files()
                mutate()
                with self.assertRaisesRegex(ValueError, "NCERT byte preflight"):
                    test_source_pdf_bytes.preflight(self.repo, self.pdfs)

    def test_symlink_pdf_is_rejected(self):
        self.create_synthetic_files()
        filename = self.pdfs / "ieep201.pdf"
        external = self.repo / "external.pdf"
        external.write_bytes(self.synthetic_envelope())
        filename.unlink()
        try:
            filename.symlink_to(external)
        except OSError:
            self.skipTest("symlink operation unavailable on test system")
        with self.assertRaisesRegex(ValueError, "nonsymlink PDF"):
            test_source_pdf_bytes.preflight(self.repo, self.pdfs)


if __name__ == "__main__":
    unittest.main()
