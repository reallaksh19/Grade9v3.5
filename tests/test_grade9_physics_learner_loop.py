import copy
import json
import unittest
from pathlib import Path

from Shared.library.resolve import build_index
from Shared.library.visual_support import findings as visual_findings

ROOT = Path(__file__).resolve().parents[1]
NLM = ROOT / "Physics/library/phy-nlm-first-law.v1.json"
PHYSICS_LIBRARY = ROOT / "Physics/library"

SMOKE = {
    "Q-PHY-NLM-2A-COV-03",
    "Q-PHY-NLM-2A-FRICTION-STATIC-09",
    "Q-PHY-NLM-2B-FRICTION-STATE-01",
}
REPRESENTATIONS = {
    "REP-NLM-FBD-BODY-OWNERSHIP",
    "REP-NLM-FRICTION-THRESHOLD",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class Grade9PhysicsVisualLearnerLoopTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = [load(path) for path in sorted(PHYSICS_LIBRARY.glob("*.json"))]
        cls.records = build_index(cls.packages)
        cls.nlm = load(NLM)

    def test_invalidated_question_expansion_is_removed(self):
        tagged = [
            q["id"]
            for package in self.packages
            for q in package.get("questions", [])
            if q.get("extensions", {}).get("grade9v3:closure_ep") == "EP-TA-006"
        ]
        self.assertEqual([], tagged)

    def test_nlm_has_canonical_representation_and_explorer_bindings(self):
        reps = {row["id"]: row for row in self.nlm["representations"]}
        self.assertEqual(REPRESENTATIONS, set(reps))

        micro = {row["id"]: row for row in self.nlm["microtopics"]}
        self.assertEqual(
            ["REP-NLM-FBD-BODY-OWNERSHIP"],
            micro["MIC-PHY-NLM-FBD-BODY-OWNERSHIP"]["representation_refs"],
        )
        self.assertEqual(
            ["REP-NLM-FRICTION-THRESHOLD"],
            micro["MIC-PHY-NLM-FRICTION-QUANT"]["representation_refs"],
        )
        self.assertEqual(
            ["ACT-NLM-CONNECTED-BLOCKS-THIRD-LAW"],
            reps["REP-NLM-FBD-BODY-OWNERSHIP"]["interactive_resource_refs"],
        )
        self.assertEqual(
            ["ACT-NLM-FRICTION-THRESHOLD"],
            reps["REP-NLM-FRICTION-THRESHOLD"]["interactive_resource_refs"],
        )
        # FREE_BODY_DIAGRAM remains PROPOSED: canonical truth exists without a fake renderer.
        self.assertEqual([], reps["REP-NLM-FBD-BODY-OWNERSHIP"]["scene_instances"])
        self.assertEqual([], reps["REP-NLM-FRICTION-THRESHOLD"]["scene_instances"])

    def test_support_stage_and_hint_stage_are_separate_and_resolve(self):
        self.assertEqual([], visual_findings(self.records))
        reps = {row["id"]: row for row in self.nlm["representations"]}
        for rep in reps.values():
            mapping = {x["support_level"]: x["visual_stage_ref"] for x in rep["support_stage_map"]}
            self.assertEqual({"low", "medium", "high"}, set(mapping))
            stage_ids = {stage["id"] for stage in rep["reveal_stages"]}
            self.assertTrue(set(mapping.values()).issubset(stage_ids))

        questions = {q["id"]: q for q in self.nlm["questions"]}
        visually_bound = {
            qid for qid, q in questions.items()
            if any(h.get("visual_ref") for h in q.get("hints", []))
        }
        self.assertEqual(SMOKE, visually_bound)
        for qid in SMOKE:
            self.assertTrue(all(
                bool(h.get("visual_ref")) == bool(h.get("visual_stage_ref"))
                for h in questions[qid]["hints"]
            ))

    def test_visual_validator_rejects_foreign_stage_and_non_activity(self):
        records = copy.deepcopy(self.records)
        records["Q-PHY-NLM-2A-COV-03"]["hints"][0]["visual_stage_ref"] = "VIS-NLM-FRICTION-V4"
        records["REP-NLM-FBD-BODY-OWNERSHIP"]["interactive_resource_refs"] = ["SRC-AUTHOR-NLM"]
        codes = {item["code"] for item in visual_findings(records)}
        self.assertIn("HINT_VISUAL_STAGE_FOREIGN", codes)
        self.assertIn("VISUAL_EXPLORER_NOT_ACTIVITY", codes)


if __name__ == "__main__":
    unittest.main()
