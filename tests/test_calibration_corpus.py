import json
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Shared/tools"))
import calibration_corpus  # noqa: E402


class CalibrationCorpusTest(unittest.TestCase):
    def test_committed_corpus_is_intact(self):
        self.assertEqual(calibration_corpus.check(), [])

    def test_edited_or_extra_specimen_file_is_reported(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "qc"
            shutil.copytree(calibration_corpus.ROOT, root)
            manifest = json.loads((root / "manifest.v1.json").read_text(encoding="utf-8"))
            first = next(iter(manifest["specimens"][0]["files"]))
            (root / first).write_text("edited", encoding="utf-8")
            (root / manifest["specimens"][0]["dir"] / "extra.html").write_text("x", encoding="utf-8")
            codes = {f["code"] for f in calibration_corpus.check(root)}
            self.assertEqual(codes, {"SPECIMEN_FILE_CHANGED", "SPECIMEN_FILE_UNLISTED"})

    def test_reference_custody_must_be_decided(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "qc"
            shutil.copytree(calibration_corpus.ROOT, root)
            manifest = json.loads((root / "manifest.v1.json").read_text(encoding="utf-8"))
            manifest["references"][0]["custody"] = "OWNER_DECISION_PENDING"
            (root / "manifest.v1.json").write_text(json.dumps(manifest), encoding="utf-8")
            codes = {f["code"] for f in calibration_corpus.check(root)}
            self.assertEqual(codes, {"REFERENCE_CUSTODY_UNSET"})


if __name__ == "__main__":
    unittest.main()
