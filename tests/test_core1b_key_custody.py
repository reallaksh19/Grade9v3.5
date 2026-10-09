"""Negative and positive custody tests for the Core1B CI artifact allowlist."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfWriter

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "core1b_custody_stage", ROOT / "tools/site-audit/core1b-custody-evidence.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def build_fixtures(root: Path):
    source = root / "public" / "core1b-authored-reconstruction-journey"
    keydir = root / "private" / "offline-key"
    stage = root / "review" / "safe-upload"
    source.mkdir(parents=True)
    keydir.mkdir(parents=True)
    (source / "core1b-evidence").mkdir()
    keys, learners = [], []
    for role in ("core1a", "core1b", "core2a"):
        file = role + ".pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=280, height=175)
        with (source / file).open("wb") as f:
            writer.write(f)
        writer2 = PdfWriter()
        writer2.add_blank_page(width=280, height=175)
        with (keydir / (role + ".key.pdf")).open("wb") as f:
            writer2.write(f)
        dig = "sha256:synthetic-source-page"
        learners.append({"page":role+".html","page_digest":dig,"pdf":file,
                         "pdf_digest":MODULE.digest(source/file),"figures":1})
        keys.append({"page":role+".html","page_digest":dig,"pdf":role+".key.pdf",
                     "pdf_digest":MODULE.digest(keydir/(role+".key.pdf")),"figures":2})
    (source / "print-receipt.json").write_text(json.dumps({"mode":"LEARNER_PDF","pages":learners}))
    (keydir / "print-key-receipt.json").write_text(json.dumps({"mode":"KEY_PDF","pages":keys}))
    (source / "deploy-receipt.json").write_text(json.dumps({"subject":"TEST","draft":True}))
    (source / "core1b-evidence/qualification.json").write_text(
        json.dumps({"QRT_cells":28,"canonical_publication":False}))
    (source / "core1b-evidence/core1b-browser-report.json").write_text(
        json.dumps({"failures":[],
                    "boundary_independent_attempt":"SEPARATE_COMMIT_GATES_BROWSER_VERIFIED_UNGRADED"}))
    (source / "core1b.html").write_text(
        "<template data-g9-payload>DO NOT PUBLISH SOLUTION TEMPLATE</template>")
    (source / "core1b-evidence/reconstruction.png").write_bytes(b"secret postcommit bitmap")
    return source,keydir,stage


class Core1BKeyCustodyTests(unittest.TestCase):
    def test_evidence_allowlist_omits_all_three_key_pdfs_html_and_screenshots(self):
        with tempfile.TemporaryDirectory() as td:
            source, keys, stage = build_fixtures(Path(td))
            manifest = MODULE.stage(source,keys,stage,"TEST-EXACT-HEAD")
            self.assertEqual(manifest["key_distribution_owner_approval"],"NOT_GRANTED")
            self.assertTrue(manifest["html_source_templates_still_contain_answers"])
            self.assertEqual({p.relative_to(stage).as_posix()
                              for p in stage.rglob("*") if p.is_file()},
                             set(MODULE.ARTIFACT_FILES))
            self.assertFalse(list(stage.rglob("*.key.pdf")))
            self.assertFalse(list(stage.rglob("*.html")))
            self.assertFalse(list(stage.rglob("*.png")))
            digest_only = json.loads((stage/"key-digests-only.json").read_text())
            self.assertEqual(len(digest_only["roles"]),3)
            self.assertFalse(digest_only["release_authorized"])
            self.assertEqual(len(list(keys.glob("*.key.pdf"))),3)

    def test_fail_closed_if_a_key_enters_public_or_a_receipt_has_wrong_digest(self):
        with tempfile.TemporaryDirectory() as td:
            source, keys, stage = build_fixtures(Path(td))
            (source/"core1b.key.pdf").write_bytes(b"should never be in public")
            with self.assertRaisesRegex(ValueError,"unexpectedly present"):
                MODULE.stage(source,keys,stage,"HEAD")
            (source/"core1b.key.pdf").unlink()
            (keys/"core1b.key.pdf").write_bytes(b"corrupted")
            with self.assertRaisesRegex(ValueError,"digest mismatch"):
                MODULE.stage(source,keys,stage,"HEAD")

    def test_output_cannot_overlap_public_or_private_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            source, keys, _ = build_fixtures(Path(td))
            for unsafe in (source/"artifact", keys/"artifact", source.parent):
                with self.assertRaisesRegex(ValueError,"must not overlap"):
                    MODULE.stage(source,keys,unsafe,"HEAD")


if __name__ == "__main__":
    unittest.main()
