"""Agent A semantic Atlas packet for Grade-9 connected systems and ideal strings."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.library import practice_inventory  # noqa: E402
from Shared.tools import feedback, resolve_request, session_readiness  # noqa: E402


class Grade9NlmConnectedStringAgentAAtlas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(
            (REPO / "Physics/library/phy-nlm-first-law.v1.json").read_text(encoding="utf-8")
        )
        cls.matrix = json.loads(
            (REPO / "Physics/matrices/phy-nlm-first-law.rungs.json").read_text(encoding="utf-8")
        )
        cls.records = resolve_request.library_records("Physics")
        cls.questions = {row["id"]: row for row in cls.package["questions"]}
        cls.microtopics = {row["id"]: row for row in cls.package["microtopics"]}
        cls.capabilities = {row["id"]: row for row in cls.package["capabilities"]}
        cls.packet_caps = {
            "CAP-NLM-CONNECTED-COMMON-ACCEL",
            "CAP-NLM-IDEAL-STRING-TENSION",
            "CAP-NLM-SINGLE-STRING-CONSTRAINT",
        }

    def test_three_durable_capabilities_are_preserved(self):
        present = {
            cap_id for cap_id in self.capabilities
            if cap_id in self.packet_caps
        }
        self.assertEqual(present, self.packet_caps)
        self.assertIn(
            "does not own equal-string-tension",
            self.capabilities["CAP-NLM-CONNECTED-COMMON-ACCEL"]["extensions"][
                "agent_a:semantic_boundary"
            ],
        )
        self.assertIn(
            "does not own the string-length kinematic constraint",
            self.capabilities["CAP-NLM-IDEAL-STRING-TENSION"]["extensions"][
                "agent_a:semantic_boundary"
            ],
        )
        self.assertIn(
            "does not by itself prove equal tension",
            self.capabilities["CAP-NLM-SINGLE-STRING-CONSTRAINT"]["extensions"][
                "agent_a:semantic_boundary"
            ],
        )

    def test_semantic_leaf_ids_are_stable_and_address_distinct_failures(self):
        expected = {
            "MIC-PHY-NLM-CONNECTED-COMMON-ACCEL":
                ["NLM9-1", "NLM9-2", "NLM9-3", "NLM9-4", "NLM9-5"],
            "MIC-PHY-NLM-IDEAL-STRING-TENSION":
                ["NLM10-1", "NLM10-2", "NLM10-3", "NLM10-4", "NLM10-5"],
            "MIC-PHY-NLM-SINGLE-STRING-CONSTRAINT":
                ["NLM11-1", "NLM11-2", "NLM11-3", "NLM11-4", "NLM11-5"],
        }
        for micro_id, step_ids in expected.items():
            with self.subTest(micro_id=micro_id):
                micro = self.microtopics[micro_id]
                self.assertEqual([row["id"] for row in micro["teaching_path"]], step_ids)
                for row in micro["teaching_path"]:
                    self.assertTrue(row["action"])
                    self.assertTrue(row["why_valid"])
                    self.assertTrue(row["output"])

    def test_misconceptions_cover_constraint_force_and_tension_boundaries(self):
        connected = " ".join(
            row["wrong_idea"]
            for row in self.microtopics["MIC-PHY-NLM-CONNECTED-COMMON-ACCEL"][
                "misconceptions"
            ]
        ).lower()
        tension = " ".join(
            row["wrong_idea"]
            for row in self.microtopics["MIC-PHY-NLM-IDEAL-STRING-TENSION"][
                "misconceptions"
            ]
        ).lower()
        string = " ".join(
            row["wrong_idea"]
            for row in self.microtopics["MIC-PHY-NLM-SINGLE-STRING-CONSTRAINT"][
                "misconceptions"
            ]
        ).lower()

        self.assertIn("automatically have the same acceleration", connected)
        self.assertIn("same net force", connected)
        self.assertIn("always equal to the mass's weight", tension)
        self.assertIn("every rope over every pulley", tension)
        self.assertIn("because the string tension is equal", string)
        self.assertIn("same acceleration ratio", string)

    def test_packet_has_five_core2a_and_five_core2b_primary_items(self):
        rows = [
            row for row in self.package["questions"]
            if row["primary_capability_ref"] in self.packet_caps
        ]
        core2a = [
            row for row in rows
            if any(e["core"] == "CORE2A" for e in row["exposure"])
        ]
        core2b = [
            row for row in rows
            if any(e["core"] == "CORE2B" for e in row["exposure"])
        ]
        self.assertEqual(len(core2a), 5)
        self.assertEqual(len(core2b), 5)

        inventory = practice_inventory.coverage(
            self.records, "BUCKET-PHY-NLM-FIRST-LAW"
        )
        for row in core2a:
            self.assertIn(row["id"], inventory["CORE2A"])
        for row in core2b:
            self.assertIn(row["id"], inventory["CORE2B"])

    def test_packet_questions_are_authored_and_have_specific_repairs(self):
        # Core1A worked anchors (added in the Phase 6 pilot, family *-WORKED-ANCHORS) teach the
        # construction; they are not packet practice.
        rows = [
            row for row in self.package["questions"]
            if row["primary_capability_ref"] in self.packet_caps
            and {e["core"] for e in row["exposure"]} != {"CORE1A"}
        ]
        self.assertEqual(len(rows), 10)
        for row in rows:
            with self.subTest(question=row["id"]):
                self.assertEqual(row["origin"], "AUTHORED")
                self.assertEqual(row["source_refs"], ["SRC-AUTHOR-NLM"])
                self.assertEqual(
                    row["extensions"].get("agent_a:packet"),
                    "NLM_CONNECTED_STRING",
                )
                self.assertTrue(row["original_identifier"].startswith("AUTHOR-NLM-"))
                self.assertTrue(row.get("repair_ref"))

    def test_transfer_set_spans_all_three_existing_adaptation_dimensions(self):
        transfers = [
            row for row in self.package["questions"]
            if row["primary_capability_ref"] in self.packet_caps
            and any(e["core"] == "CORE2B" for e in row["exposure"])
        ]
        self.assertEqual(len(transfers), 5)
        self.assertEqual(
            {row["transfer"]["dimension"] for row in transfers},
            {"model_choice", "reasoning_steps", "representation_translation"},
        )

        packet_steps = {
            step["id"]
            for micro_id in (
                "MIC-PHY-NLM-CONNECTED-COMMON-ACCEL",
                "MIC-PHY-NLM-IDEAL-STRING-TENSION",
                "MIC-PHY-NLM-SINGLE-STRING-CONSTRAINT",
            )
            for step in self.microtopics[micro_id]["teaching_path"]
        }
        for row in transfers:
            with self.subTest(question=row["id"]):
                self.assertIsNotNone(row["adaptation"])
                self.assertIn(row["adaptation"]["parent_ref"], self.questions)
                self.assertIn(
                    row["adaptation"]["parent_ref"],
                    row["transfer"]["builds_on"],
                )
                self.assertIn(row["repair_ref"], packet_steps)
                self.assertTrue(row["answer"].get("rubric"))

    def test_model_choice_hints_do_not_reveal_the_selected_branch(self):
        for row in self.package["questions"]:
            if (
                row["primary_capability_ref"] not in self.packet_caps
                or not row.get("transfer")
                or row["transfer"]["dimension"] != "model_choice"
            ):
                continue
            with self.subTest(question=row["id"]):
                self.assertEqual(
                    {hint["reveals"] for hint in row["hints"]},
                    {"CONCEPT"},
                )
                first = feedback.next_safe_hint(row, [])
                self.assertIsNotNone(first)
                self.assertEqual(first["reveals"], "CONCEPT")

    def test_atwood_practice_separates_tension_from_weight(self):
        q = self.questions["Q-PHY-NLM-2A-ATWOOD-12"]
        self.assertEqual(q["primary_capability_ref"], "CAP-NLM-IDEAL-STRING-TENSION")
        self.assertIn("T>m_A g", q["answer"]["summary"])
        self.assertIn("T<m_B g", q["answer"]["summary"])
        self.assertEqual(q["repair_ref"], "NLM10-5")

    def test_cross_model_transfer_keeps_length_constraint_but_refuses_equal_tension(self):
        q = self.questions["Q-PHY-NLM-2B-CONSTRAINT-VS-TENSION-07"]
        summary = q["answer"]["summary"]
        self.assertIn("a_A+a_B=0", summary)
        self.assertIn("T_A=T_B", summary)
        self.assertIn("no longer guaranteed", summary)
        self.assertEqual(q["repair_ref"], "NLM11-5")
        self.assertEqual(q["hints"][0]["reveals"], "CONCEPT")

    def test_outputs_remain_semantic_actions_not_new_capabilities(self):
        package_text = json.dumps(self.package)
        for token in (
            "CAP-NLM-CONTACT-LOSS",
            "CAP-NLM-SYSTEM-BOUNDARY-CHOICE",
            "CAP-NLM-TENSION-VS-WEIGHT",
            "CAP-NLM-ATWOOD",
            "CAP-NLM-TENSION-CONSTRAINT-SEPARATION",
        ):
            self.assertNotIn(token, package_text)

    def test_matrix_variations_make_boundaries_visible(self):
        by_rung = {row["rung"]: row for row in self.matrix["rungs"]}
        for rung in ("R9", "R10", "R11"):
            self.assertGreaterEqual(len(by_rung[rung]["controlled_variation"]), 3)

        self.assertIn(
            "system boundary",
            " ".join(by_rung["R9"]["must_contain"]).lower(),
        )
        self.assertIn(
            "not automatically equal to weight",
            " ".join(by_rung["R10"]["must_contain"]).lower(),
        )
        self.assertIn(
            "fixed-length acceleration constraint",
            " ".join(by_rung["R11"]["must_contain"]).lower(),
        )

    def test_matrix_remains_session_ready(self):
        report = session_readiness.audit(
            "Physics",
            matrix_id="MATRIX-PHY-NLM-FIRST-LAW",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertIn(
            report["status"],
            {session_readiness.READY, session_readiness.READY_WITH_BRIDGE},
        )


if __name__ == "__main__":
    unittest.main()
