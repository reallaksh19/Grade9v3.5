"""WP4 inventory, readback, source presentation, and migration observations."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from Shared.tools import evidence_check, library_board, render_core, unit_status  # noqa: E402
from Shared.library import resolve  # noqa: E402


class InventoryReadback(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        research = self.repo / "Physics/research"
        for folder in ("acquisitions", "inventories", "verification", "evidence"):
            (research / folder).mkdir(parents=True)
        (self.repo / "Physics/library").mkdir(parents=True)
        self.acq = research / "acquisitions/SRC.json"
        self.acq.write_text(json.dumps({"sha256": "a" * 64}), encoding="utf-8")
        self.item = {"item_id": "Q1", "locator": {"acquisition_ref": "SRC", "page": 4, "label": "1"},
                     "format": "MULTIPLE_CORRECT", "question_card": "QC", "key": {"state": "PRESENT", "card": "KC"}}
        self.inventory = {"schema": "source-inventory/v1", "inventory_id": "INV", "subject": "Physics",
                          "members": [{"acquisition_ref": "SRC", "sha256": "a" * 64, "pages": "4"}],
                          "declared_scope": "PAGE_RANGE", "completeness_unit": "all numbered questions on page 4",
                          "items": [self.item], "counts": {"items": 1, "key_present": 1,
                                                           "key_absent": 0, "key_ambiguous": 0},
                          "digest": evidence_check.inventory_digest([self.item]), "supersedes": None}
        self.invpath = research / "inventories/INV.json"
        self.write_inventory()
        self.cards = {"QC": {"card_id": "QC", "kind": "QUESTION"},
                      "KC": {"card_id": "KC", "kind": "ANSWER_KEY"}}
        self.question = {"id": "Q", "answer": {"summary": "42"},
                         "extensions": {"grade9v3:inventory_item": "INV#Q1",
                                        "grade9v3:research_node": "N",
                                        "grade9v3:authored_by": "author",
                                        "grade9v3:citations": {"stem": "QC", "answer": "KC"}}}
        self.pkgpath = self.repo / "Physics/library/x.v1.json"
        self.pkgpath.write_text(json.dumps({"questions": [self.question]}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write_inventory(self):
        self.invpath.write_text(json.dumps(self.inventory), encoding="utf-8")

    def test_inventory_denominator_links_and_member_digest(self):
        self.assertEqual(evidence_check.inventory_findings("Physics", self.cards, self.repo), [])
        self.inventory["counts"]["items"] = 2
        self.inventory["members"][0]["sha256"] = "b" * 64
        self.write_inventory()
        codes = {row["code"] for row in evidence_check.inventory_findings("Physics", self.cards, self.repo)}
        self.assertIn("INVENTORY_COUNTS", codes)
        self.assertIn("INVENTORY_MEMBER_DIGEST", codes)
        self.question["extensions"]["grade9v3:citations"] = {"stem": "QC"}
        self.pkgpath.write_text(json.dumps({"questions": [self.question]}), encoding="utf-8")
        codes = {row["code"] for row in evidence_check.inventory_findings("Physics", self.cards, self.repo)}
        self.assertIn("INVENTORY_CITATIONS", codes)

    def test_source_item_without_printed_key_is_valid(self):
        self.item["key"] = {"state": "ABSENT"}
        self.inventory["counts"] = {"items": 1, "key_present": 0, "key_absent": 1, "key_ambiguous": 0}
        self.inventory["digest"] = evidence_check.inventory_digest([self.item])
        self.write_inventory()
        self.question["extensions"]["grade9v3:citations"] = {"stem": "QC"}
        self.pkgpath.write_text(json.dumps({"questions": [self.question]}), encoding="utf-8")
        self.assertEqual(evidence_check.inventory_findings("Physics", {"QC": self.cards["QC"]}, self.repo), [])

    def test_readback_and_inventory_changes_stale_existing_digest(self):
        records = [self.question]
        initial = library_board.inputs_digest("Physics", "N", records, self.repo,
                                              readback_refs=["INV#Q1", "QC", "KC"])
        self.item["format"] = "NUMERIC"
        self.inventory["digest"] = evidence_check.inventory_digest([self.item])
        self.write_inventory()
        changed = library_board.inputs_digest("Physics", "N", records, self.repo,
                                              readback_refs=["INV#Q1", "QC", "KC"])
        self.assertNotEqual(initial, changed)

    def test_core2_projects_format_and_independent_key_conflict(self):
        ctx = render_core.Ctx({"product_id": "P"}, [], [], {},
                              source_items={"INV#Q1": self.item},
                              source_checks={"QC": {"official_answer": "41", "independent_answer": "43", "agrees": False}})
        projected = render_core.source_projection(ctx, self.question)
        self.assertEqual(render_core.response_for(projected)["type"], "multiple_choice")
        self.assertEqual(projected["answer"]["source_key"]["value"], "41")
        self.assertEqual(projected["answer"]["key_relation"], "CONFLICTS_WITH_KEY")
        self.assertIn("Printed book key", render_core._source_solution(projected["answer"]))
        self.assertIn("Mathematically verified result", render_core._source_solution(projected["answer"]))
        self.assertIn("43", render_core._source_solution(projected["answer"]))
        self.question["answer"]["key_relation"] = "MATCHES_KEY"
        ctx.source_checks.clear()
        unchecked = render_core.source_projection(ctx, self.question)
        self.assertNotIn("key_relation", unchecked["answer"])
        self.assertIn("awaits independent readback", render_core._source_solution(unchecked["answer"]))
        self.item["key"] = {"state": "ABSENT"}
        no_key = render_core.source_projection(ctx, self.question)
        self.assertEqual(no_key["answer"]["key_relation"], "NO_KEY")
        self.assertNotIn("value", no_key["answer"]["source_key"])

    def test_unit_front_matter_is_honest_without_design_claim(self):
        path = REPO / "Mathematics/units/linear-equations/UNIT.md"
        data = unit_status.front_matter(path)
        self.assertEqual(data["owner_agent"], "UNASSIGNED")
        self.assertEqual(data["inventories"], [])
        self.assertEqual(len(data["spine_nodes"]), 4)
        self.assertFalse((path.parent / "DESIGN-NOTE.md").exists())

    def test_acquisition_links_leave_the_library_index(self):
        record = {"id": "SRC-TEST", "snapshot_ref": "ACQ-TEST", "evidence_refs": ["EV-TEST"],
                  "extensions": {"grade9v3:acquisition_ref": "ACQ-TEST"}}
        self.assertEqual(resolve.references(record), [])

    def test_advisory_status_requires_an_owner_acceptance_record(self):
        unit = self.repo / "Physics/units/x"
        unit.mkdir(parents=True)
        (unit / "UNIT.md").write_text('---\npackage: "Physics/library/x.v1.json"\nmicrotopics: []\n---\n', encoding="utf-8")
        acceptance = self.repo / "products/acceptance/x.json"
        acceptance.parent.mkdir(parents=True)
        record = {"schema": "product-acceptance/v1", "product": "x", "render_digest": "abc", "accepted_by": "agent"}
        acceptance.write_text(json.dumps(record), encoding="utf-8")
        report = unit_status.status("Physics", "x", self.repo, render=([], "abc"))
        self.assertFalse(report["states"]["ACCEPTED"])
        self.assertEqual(report["inventory_formats"], {"MULTIPLE_CORRECT": 1})
        record["accepted_by"] = "owner"
        acceptance.write_text(json.dumps(record), encoding="utf-8")
        report = unit_status.status("Physics", "x", self.repo, render=([], "abc"))
        self.assertTrue(report["states"]["ACCEPTED"])


if __name__ == "__main__":
    unittest.main()
