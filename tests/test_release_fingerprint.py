import unittest
import tempfile
import os
import json
from pathlib import Path

# Adjust path to import Shared
import sys
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.release_fingerprint import _hash_files, build_fingerprint

class DummyArgs:
    def __init__(self, product_id="test", canonical_dir="", web_dir="", standalone_dir="", search_index="", search_manifest="", assurance_bundle=""):
        self.product_id = product_id
        self.canonical_dir = canonical_dir
        self.web_dir = web_dir
        self.standalone_dir = standalone_dir
        self.search_index = search_index
        self.search_manifest = search_manifest
        self.assurance_bundle = assurance_bundle

class TestReleaseFingerprint(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fingerprint_canonical_digest(self):
        d = self.temp_path / "canonical"
        d.mkdir()
        (d / "a.json").write_text('{"id":"a"}', encoding="utf-8")
        (d / "b.json").write_text('{"id":"b"}', encoding="utf-8")
        
        args = DummyArgs(canonical_dir=str(d), web_dir=str(self.temp_path))
        f1 = build_fingerprint(args)
        f2 = build_fingerprint(args)
        self.assertEqual(f1["canonical_snapshot_digest"], f2["canonical_snapshot_digest"])
        self.assertTrue(f1["canonical_snapshot_digest"].startswith("sha256:"))

    def test_fingerprint_web_digest(self):
        d = self.temp_path / "web"
        d.mkdir()
        (d / "index.html").write_text('<html>1</html>', encoding="utf-8")
        (d / "about.html").write_text('<html>2</html>', encoding="utf-8")
        
        args = DummyArgs(canonical_dir=str(self.temp_path), web_dir=str(d))
        f1 = build_fingerprint(args)
        f2 = build_fingerprint(args)
        self.assertEqual(f1["web_projection_digest"], f2["web_projection_digest"])
        self.assertTrue(f1["web_projection_digest"].startswith("sha256:"))

    def test_fingerprint_changes_on_content_change(self):
        d = self.temp_path / "canonical"
        d.mkdir()
        f = d / "a.json"
        f.write_text('{"id":"a"}', encoding="utf-8")
        
        args = DummyArgs(canonical_dir=str(d), web_dir=str(self.temp_path))
        f1 = build_fingerprint(args)
        
        f.write_text('{"id":"b"}', encoding="utf-8")
        f2 = build_fingerprint(args)
        
        self.assertNotEqual(f1["canonical_snapshot_digest"], f2["canonical_snapshot_digest"])

class TestDriftDetector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_drift(self, accepted, current_args):
        # We simulate the drift detector logic here
        current = build_fingerprint(current_args)
        
        drifts = {}
        if current.get("canonical_snapshot_digest") != accepted.get("canonical_snapshot_digest"):
            drifts["canonical_snapshot"] = "REQUIRES_REBUILD"
        else:
            drifts["canonical_snapshot"] = "CURRENT"
            
        for proj in ["web_projection", "standalone_projection", "search_projection"]:
            acc_dig = accepted.get(f"{proj}_digest")
            cur_dig = current.get(f"{proj}_digest")
            if not acc_dig:
                drifts[proj] = "CURRENT"
            elif cur_dig != acc_dig:
                drifts[proj] = "REQUIRES_REBUILD"
            else:
                drifts[proj] = "CURRENT"
                
        canonical_current = drifts["canonical_snapshot"] == "CURRENT"
        for proj in ["web_projection", "standalone_projection", "search_projection"]:
            if drifts[proj] == "REQUIRES_REBUILD" and canonical_current:
                drifts[proj] = "UNAUTHORIZED"
                
        return drifts

    def test_drift_canonical_current(self):
        d = self.temp_path / "canonical"
        d.mkdir()
        (d / "a.json").write_text('{}', encoding="utf-8")
        
        args = DummyArgs(canonical_dir=str(d), web_dir=str(self.temp_path))
        accepted = build_fingerprint(args)
        
        drifts = self.run_drift(accepted, args)
        self.assertEqual(drifts["canonical_snapshot"], "CURRENT")

    def test_drift_canonical_changed(self):
        d = self.temp_path / "canonical"
        d.mkdir()
        f = d / "a.json"
        f.write_text('{}', encoding="utf-8")
        
        args = DummyArgs(canonical_dir=str(d), web_dir=str(self.temp_path))
        accepted = build_fingerprint(args)
        
        f.write_text('{"changed": true}', encoding="utf-8")
        drifts = self.run_drift(accepted, args)
        self.assertEqual(drifts["canonical_snapshot"], "REQUIRES_REBUILD")

    def test_drift_unauthorized(self):
        c = self.temp_path / "canonical"
        c.mkdir()
        (c / "a.json").write_text('{}', encoding="utf-8")
        
        w = self.temp_path / "web"
        w.mkdir()
        wf = w / "index.html"
        wf.write_text('<html></html>', encoding="utf-8")
        
        args = DummyArgs(canonical_dir=str(c), web_dir=str(w))
        accepted = build_fingerprint(args)
        
        wf.write_text('<html>changed</html>', encoding="utf-8")
        drifts = self.run_drift(accepted, args)
        
        self.assertEqual(drifts["canonical_snapshot"], "CURRENT")
        self.assertEqual(drifts["web_projection"], "UNAUTHORIZED")

if __name__ == "__main__":
    unittest.main()
