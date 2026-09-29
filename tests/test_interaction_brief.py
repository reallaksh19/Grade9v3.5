from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from Shared.tools import interaction_brief


SUBJECT = "Mathematics"
MICROTOPIC = "MIC-MAT-LEQ-04-TWO-VARIABLES-LINE-OF-SOLUTIONS"
CAPABILITY = "CAP-MAT-LEQ-04-TWO-VARIABLE-SOLUTIONS"
REPRESENTATION = "REP-MAT-LEQ-04-SOLUTION-LINE"


class InteractionBriefTests(unittest.TestCase):
    def test_builds_bounded_brief_from_canonical_interactive_idea(self):
        brief = interaction_brief.build_from_microtopic(SUBJECT, MICROTOPIC)

        self.assertEqual(brief["schema_version"], "1.0.0")
        self.assertEqual(brief["subject"], SUBJECT)
        self.assertEqual(brief["academic_target"]["target_ref"], MICROTOPIC)
        self.assertEqual(brief["academic_target"]["microtopic_refs"], [MICROTOPIC])
        self.assertEqual(brief["academic_target"]["capability_refs"], [CAPABILITY])
        self.assertEqual(brief["academic_target"]["representation_refs"], [REPRESENTATION])
        self.assertEqual(brief["academic_target"]["question_refs"], [])
        self.assertIn("drag", brief["interaction_intent"]["learner_manipulates"].lower())
        self.assertIn("straight line", brief["interaction_intent"]["becomes_visible"].lower())
        self.assertIn("unique solution", brief["interaction_intent"]["misconception_targeted"].lower())

        provenance = brief["provenance"]
        self.assertEqual(provenance["authority"], "DERIVED_INTERACTION_HANDOFF_ONLY")
        self.assertEqual(
            provenance["canonical_record_refs"],
            sorted([MICROTOPIC, CAPABILITY, REPRESENTATION]),
        )
        self.assertRegex(provenance["canonical_input_digest"], r"^sha256:[a-f0-9]{64}$")
        self.assertRegex(brief["brief_id"], r"^IBR-[A-F0-9]{20}$")

        # Study-side priority/difficulty-lot metadata must not become runtime/reuse authority.
        rendered = str(brief)
        self.assertNotIn("interaction_value", rendered)
        self.assertNotIn("LP-H", rendered)
        self.assertNotIn("LP-M", rendered)
        self.assertNotIn("LP-L", rendered)

    def test_current_brief_revalidates_against_live_canonical_records(self):
        brief = interaction_brief.build_from_microtopic(SUBJECT, MICROTOPIC)
        status = interaction_brief.freshness(brief)
        self.assertEqual(status["status"], "CURRENT", status)
        self.assertEqual(status["current_digest"], brief["provenance"]["canonical_input_digest"])

    def test_canonical_change_marks_existing_brief_stale(self):
        records = interaction_brief._subject_records(SUBJECT)
        with patch.object(interaction_brief, "_subject_records", return_value=records):
            brief = interaction_brief.build_from_microtopic(SUBJECT, MICROTOPIC)

        changed = copy.deepcopy(records)
        changed[MICROTOPIC]["inferential_jump"] += " Revised academic basis."
        with patch.object(interaction_brief, "_subject_records", return_value=changed):
            status = interaction_brief.freshness(brief)

        self.assertEqual(status["status"], "STALE")
        self.assertNotEqual(status["current_digest"], status["expected_digest"])

    def test_missing_canonical_ref_is_unresolved_not_silently_current(self):
        records = interaction_brief._subject_records(SUBJECT)
        with patch.object(interaction_brief, "_subject_records", return_value=records):
            brief = interaction_brief.build_from_microtopic(SUBJECT, MICROTOPIC)

        missing = copy.deepcopy(records)
        missing.pop(REPRESENTATION)
        with patch.object(interaction_brief, "_subject_records", return_value=missing):
            status = interaction_brief.freshness(brief)

        self.assertEqual(status["status"], "UNRESOLVED")
        self.assertEqual(status["missing_refs"], [REPRESENTATION])

    def test_brief_id_changes_when_canonical_basis_changes(self):
        records = interaction_brief._subject_records(SUBJECT)
        with patch.object(interaction_brief, "_subject_records", return_value=records):
            first = interaction_brief.build_from_microtopic(SUBJECT, MICROTOPIC)

        changed = copy.deepcopy(records)
        changed[CAPABILITY]["success_criterion"] += " Revised."
        with patch.object(interaction_brief, "_subject_records", return_value=changed):
            second = interaction_brief.build_from_microtopic(SUBJECT, MICROTOPIC)

        self.assertNotEqual(first["brief_id"], second["brief_id"])
        self.assertNotEqual(
            first["provenance"]["canonical_input_digest"],
            second["provenance"]["canonical_input_digest"],
        )


if __name__ == "__main__":
    unittest.main()
