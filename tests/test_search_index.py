#!/usr/bin/env python3
"""Tests for search index tools."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools import build_search_index
from Shared.tools import verify_search_index

class TestSearchIndexTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.lib_dir = Path(self.temp_dir.name) / "library"
        self.lib_dir.mkdir()
        self.out_idx = Path(self.temp_dir.name) / "index.json"
        self.out_mnf = Path(self.temp_dir.name) / "manifest.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_lib_file(self, filename: str, data: dict):
        with open(self.lib_dir / filename, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def test_build_search_index_basic(self):
        # Create minimal package JSON
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [
                {
                    "id": "Q-1",
                    "stem": "Stem 1",
                    "primary_capability_ref": "CAP-1"
                },
                {
                    "id": "Q-2",
                    "stem": "Stem 2",
                    "primary_capability_ref": "CAP-2",
                    "extensions": {
                        "search_visibility": "EXCLUDED"
                    }
                },
                {
                    "id": "Q-3",
                    "stem": "Stem 3",
                    "primary_capability_ref": "CAP-3"
                }
            ]
        })

        test_args = [
            "build_search_index.py",
            "--library-dirs", str(self.lib_dir),
            "--output-index", str(self.out_idx),
            "--output-manifest", str(self.out_mnf)
        ]
        
        with patch.object(sys, 'argv', test_args):
            build_search_index.main()

        self.assertTrue(self.out_idx.exists())
        self.assertTrue(self.out_mnf.exists())

        with open(self.out_idx, "r", encoding="utf-8") as f:
            docs = json.load(f)

        self.assertEqual(len(docs), 2)
        ids = sorted(d["canonical_id"] for d in docs)
        self.assertEqual(ids, ["Q-1", "Q-3"])

        with open(self.out_mnf, "r", encoding="utf-8") as f:
            mnf = json.load(f)
        
        self.assertEqual(mnf["record_count"], 2)
        self.assertEqual(sorted(mnf["canonical_ids"]), ["Q-1", "Q-3"])
        self.assertEqual(mnf["excluded_ids"], ["Q-2"])

    def test_search_membership_pass(self):
        # Build first
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-1"}]
        })
        with patch.object(sys, 'argv', ["build", "--library-dirs", str(self.lib_dir), "--output-index", str(self.out_idx), "--output-manifest", str(self.out_mnf)]):
            build_search_index.main()

        # Run verify
        test_args = [
            "verify_search_index.py",
            "--index", str(self.out_idx),
            "--manifest", str(self.out_mnf),
            "--library-dirs", str(self.lib_dir)
        ]
        with patch.object(sys, 'argv', test_args):
            # Should not raise SystemExit
            verify_search_index.main()
            
        evidence_path = Path("standalone/SEARCH_MEMBERSHIP_evidence.json")
        with open(evidence_path, "r", encoding="utf-8") as f:
            ev = json.load(f)
        self.assertEqual(ev["outcome"], "PASS")

    def test_search_membership_missing(self):
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-1"}]
        })
        with patch.object(sys, 'argv', ["build", "--library-dirs", str(self.lib_dir), "--output-index", str(self.out_idx), "--output-manifest", str(self.out_mnf)]):
            build_search_index.main()
        
        # Now add Q-2 to library but not index
        self.create_lib_file("test2.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-2"}]
        })

        import json
        with open(self.out_mnf, "r") as f: mnf = json.load(f)
        with patch("Shared.tools.verify_search_index.compute_sha256_of_files", return_value=mnf["canonical_snapshot_digest"]):
            test_args = [
                "verify_search_index.py",
                "--index", str(self.out_idx),
                "--manifest", str(self.out_mnf),
                "--library-dirs", str(self.lib_dir),
                "--enforce"
            ]
            with patch.object(sys, 'argv', test_args):
                with self.assertRaises(SystemExit):
                    verify_search_index.main()
                
        evidence_path = Path("standalone/SEARCH_MEMBERSHIP_evidence.json")
        with open(evidence_path, "r", encoding="utf-8") as f:
            ev = json.load(f)
        self.assertEqual(ev["outcome"], "FAIL")
        self.assertTrue(any("missing" in f for f in ev.get("findings", [])))

    def test_search_membership_phantom(self):
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-1"}, {"id": "Q-2"}]
        })
        with patch.object(sys, 'argv', ["build", "--library-dirs", str(self.lib_dir), "--output-index", str(self.out_idx), "--output-manifest", str(self.out_mnf)]):
            build_search_index.main()
        
        # Now remove Q-2 from library
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-1"}]
        })

        import json
        with open(self.out_mnf, "r") as f: mnf = json.load(f)
        with patch("Shared.tools.verify_search_index.compute_sha256_of_files", return_value=mnf["canonical_snapshot_digest"]):
            test_args = [
                "verify_search_index.py",
                "--index", str(self.out_idx),
                "--manifest", str(self.out_mnf),
                "--library-dirs", str(self.lib_dir),
                "--enforce"
            ]
            with patch.object(sys, 'argv', test_args):
                with self.assertRaises(SystemExit):
                    verify_search_index.main()
                
        evidence_path = Path("standalone/SEARCH_MEMBERSHIP_evidence.json")
        with open(evidence_path, "r", encoding="utf-8") as f:
            ev = json.load(f)
        self.assertEqual(ev["outcome"], "FAIL")
        self.assertTrue(any("phantom" in f for f in ev.get("findings", [])))

    def test_index_integrity_pass(self):
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-1"}]
        })
        with patch.object(sys, 'argv', ["build", "--library-dirs", str(self.lib_dir), "--output-index", str(self.out_idx), "--output-manifest", str(self.out_mnf)]):
            build_search_index.main()

        test_args = [
            "verify_search_index.py",
            "--index", str(self.out_idx),
            "--manifest", str(self.out_mnf),
            "--library-dirs", str(self.lib_dir)
        ]
        with patch.object(sys, 'argv', test_args):
            verify_search_index.main()
            
        evidence_path = Path("standalone/SEARCH_RETRIEVABILITY_evidence.json")
        with open(evidence_path, "r", encoding="utf-8") as f:
            ev = json.load(f)
        self.assertEqual(ev["outcome"], "PASS")

    def test_index_integrity_fail(self):
        self.create_lib_file("test.json", {
            "subject": "Physics",
            "questions": [{"id": "Q-1"}]
        })
        with patch.object(sys, 'argv', ["build", "--library-dirs", str(self.lib_dir), "--output-index", str(self.out_idx), "--output-manifest", str(self.out_mnf)]):
            build_search_index.main()

        # Modify index so its digest doesn't match manifest
        with open(self.out_idx, "w", encoding="utf-8") as f:
            f.write("[]")

        test_args = [
            "verify_search_index.py",
            "--index", str(self.out_idx),
            "--manifest", str(self.out_mnf),
            "--library-dirs", str(self.lib_dir),
            "--enforce"
        ]
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                verify_search_index.main()
                
        evidence_path = Path("standalone/SEARCH_RETRIEVABILITY_evidence.json")
        with open(evidence_path, "r", encoding="utf-8") as f:
            ev = json.load(f)
        self.assertEqual(ev["outcome"], "FAIL")

if __name__ == "__main__":
    unittest.main()
