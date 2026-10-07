from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import build_test_site


REPO = Path(__file__).resolve().parents[1]
PILOT = REPO / "TEST/question-bank/intake/ncert-exemplar-g9-number-systems-pilot.v1.json"


class TestTestIntakeDashboard(unittest.TestCase):
    def test_intake_state_projects_only_validated_source_workflow_metadata(self):
        state = build_test_site.intake_state()

        self.assertEqual(state["bank_count"], 1)
        self.assertEqual(state["record_count"], 6)
        self.assertEqual(state["ready_for_blueprint"], 6)
        self.assertEqual(state["hold_count"], 0)
        self.assertEqual(state["by_topic"], {"Number System": 6})
        self.assertEqual(state["by_source"], {"NCERT_OFFICIAL": 6})
        self.assertEqual(state["by_status"], {"READY_FOR_BLUEPRINT": 6})

        self.assertEqual([row["source_locator"]["printed_page"] for row in state["records"]], [2, 3, 3, 3, 3, 3])
        self.assertEqual({row["source"]["url"] for row in state["records"]}, {
            "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf"
        })
        self.assertTrue(all(row["official_answer_available"] for row in state["records"]))

        serialized = json.dumps(state, sort_keys=True)
        for forbidden in (
            '"official_answer":',
            '"answer_key":',
            '"difficulty":',
            '"qrt":',
            '"capability":',
            '"crux":',
            '"accepted":',
            '"worked_solution":',
        ):
            self.assertNotIn(forbidden, serialized)

    def test_sandbox_search_projection_is_deterministic_and_source_only(self):
        state = build_test_site.intake_state()
        first = build_test_site.intake_search_index(state)
        second = build_test_site.intake_search_index(state)

        self.assertEqual(first, second)
        self.assertEqual(first["schema_version"], "grade9v3-test-intake-search-index-v1")
        self.assertEqual(first["scope"], "TEST_ONLY_SANDBOX")
        self.assertEqual(first["document_count"], 6)
        self.assertEqual(len(first["documents"]), 6)
        self.assertEqual(
            [row["id"] for row in first["documents"]],
            sorted(row["id"] for row in first["documents"]),
        )
        self.assertTrue(all(row["href"].startswith("#intake-") for row in first["documents"]))
        self.assertTrue(all("ready_for_blueprint" in row["search_text"] for row in first["documents"]))

        serialized = json.dumps(first, sort_keys=True)
        for forbidden in ("answer_key", "worked_solution", '"accepted"', '"difficulty"', '"qrt"'):
            self.assertNotIn(forbidden, serialized)

    def test_invalid_intake_bank_fails_loudly_instead_of_rendering(self):
        bank = json.loads(PILOT.read_text(encoding="utf-8"))
        bank["questions"][0]["stem"] += " changed"

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.v1.json"
            path.write_text(json.dumps(bank), encoding="utf-8")
            with mock.patch.object(build_test_site, "INTAKE_DIR", Path(tmp)):
                with self.assertRaisesRegex(ValueError, "stem_sha256"):
                    build_test_site.intake_state()

    def test_duplicate_source_instance_across_banks_fails_closed(self):
        bank = json.loads(PILOT.read_text(encoding="utf-8"))
        duplicate = json.loads(PILOT.read_text(encoding="utf-8"))
        duplicate["bank_id"] = "ncert-exemplar-g9-number-systems-pilot-copy"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.v1.json").write_text(json.dumps(bank), encoding="utf-8")
            (root / "b.v1.json").write_text(json.dumps(duplicate), encoding="utf-8")
            with mock.patch.object(build_test_site, "INTAKE_DIR", root):
                with self.assertRaisesRegex(ValueError, "duplicate TEST intake id"):
                    build_test_site.intake_state()

    def test_blueprint_handoff_projection_is_not_reloaded_as_source_authority(self):
        banks = build_test_site.intake_banks()
        self.assertEqual(len(banks), 1)
        self.assertTrue(banks[0][0].name.endswith(".v1.json"))
        self.assertNotIn("blueprint-handoff", banks[0][0].name)


if __name__ == "__main__":
    unittest.main()
