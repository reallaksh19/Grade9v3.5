from __future__ import annotations

import hashlib
import unittest

from Shared.tools import qrt_pipeline_guard as guard


def digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


class QRTPipelineGuardTests(unittest.TestCase):
    def base_run(self):
        prompt = "Q1 — Cube\nA wooden cube has edge length 7 cm. Find its total surface area."
        pd = digest(prompt)
        return {
            "schema": "qrt-pipeline-run/v1",
            "run_identity": {
                "repository": "reallaksh19/Grade9v3.5",
                "branch": "feat/test",
                "head_sha": "a" * 40,
            },
            "owner_prompt": {"text": prompt, "sha256": pd, "source_ref": "issue#10"},
            "owner_events": [
                {"id": "PROMPT", "kind": "PROMPT", "source_ref": "issue#10", "text": prompt},
                {"id": "OWNER-1", "kind": "CLARIFICATION_REPLY", "source_ref": "issue#10-comment-1", "text": "REVISION; cube surface area demonstrated"},
            ],
            "learner_profile": {
                "profile_id": "P1",
                "purpose": "REVISION",
                "purpose_owner_event_ref": "OWNER-1",
                "held": {
                    "CAP-CUBE": {"state": "DEMONSTRATED", "owner_event_ref": "OWNER-1"}
                },
            },
            "basis_digests": {
                "matrix": "sha256:" + "1" * 64,
                "adapter": "sha256:" + "2" * 64,
                "profile": "sha256:" + "3" * 64,
                "blueprint_registry": "sha256:" + "4" * 64,
            },
            "questions": [
                {
                    "id": "Q1",
                    "verbatim_text": "A wooden cube has edge length 7 cm. Find its total surface area.",
                    "owner_prompt_sha256": pd,
                    "verified_answer": "294 cm2",
                    "blueprint_ref": "BP-CORE2-SOURCE-QUESTION@1.5.0",
                    "slots": {
                        "X": {"text": "The learner may count only four lateral faces.", "basis": ["analysis.common_wrong_route"]},
                        "Y": {"text": "Area of one square face", "capability_ref": "CAP-CUBE"},
                        "Z": {"text": "Inventory all exposed faces before selecting the relation."},
                        "W": {"text": "Construct and evaluate the total-area expression.", "protected_move_ref": "Q1-MOVE-2"},
                    },
                    "core1a_targets": ["CU-CUBE-SURFACE"],
                }
            ],
            "pre_attempt_graphs": [
                {
                    "question_ref": "Q1",
                    "root": "Q1-PAGE",
                    "nodes": [
                        {"id": "Q1-PAGE", "phase": "PRE_ATTEMPT", "move_refs": [], "links": ["HINTS", "CORE1A-SAFE"]},
                        {"id": "HINTS", "phase": "PRE_ATTEMPT", "move_refs": ["Q1-MOVE-1"], "links": []},
                        {"id": "CORE1A-SAFE", "phase": "PRE_ATTEMPT", "move_refs": [], "links": []},
                    ],
                }
            ],
            "concept_evidence": [
                {
                    "id": "CE-CUBE",
                    "question_refs": ["Q1"],
                    "canonical_truth_refs": ["Mathematics/package/cube-surface"],
                    "publication_intent": "PUBLISH_CORE1A",
                    "core1a_unit_ref": "CU-CUBE-SURFACE",
                }
            ],
            "rendered_artifacts": [],
            "reviews": [],
            "validation": {
                "academic": {"status": "PASS", "evidence_ref": "academic.json"},
                "qrt_semantic": {"status": "NOT_RUN"},
                "static": {"status": "NOT_RUN"},
                "browser": {"status": "NOT_RUN"},
                "print": {"status": "NOT_APPLICABLE"},
            },
        }

    def test_owner_facts_must_bind_to_real_owner_event(self):
        run = self.base_run()
        run["learner_profile"]["purpose_owner_event_ref"] = "FABRICATED"
        self.assertIn("LEARNER_PURPOSE_HAS_NO_OWNER_EVENT", guard.validate_owner_truth(run))

    def test_normalized_question_must_still_be_verbatim_from_owner_prompt(self):
        run = self.base_run()
        run["questions"][0]["verbatim_text"] = "Normalized fixture text not present in prompt"
        self.assertIn("QUESTION_NOT_VERBATIM_FROM_OWNER_PROMPT: Q1", guard.validate_owner_truth(run))

    def test_x_must_not_contain_verified_answer(self):
        run = self.base_run()
        run["questions"][0]["slots"]["X"]["text"] = "The answer is 294 cm2."
        self.assertIn("X_CONTAINS_VERIFIED_ANSWER: Q1", guard.validate_slots(run))

    def test_y_requires_demonstrated_bridge(self):
        run = self.base_run()
        run["learner_profile"]["held"]["CAP-CUBE"]["state"] = "UNCERTAIN"
        self.assertIn("Y_NOT_BACKED_BY_DEMONSTRATED_CAPABILITY: Q1:CAP-CUBE", guard.validate_slots(run))

    def test_z_and_w_cannot_collapse_while_preattempt_scaffolding_exists(self):
        run = self.base_run()
        run["questions"][0]["slots"]["Z"]["text"] = run["questions"][0]["slots"]["W"]["text"]
        self.assertIn("Z_W_COLLAPSE_WITH_SCAFFOLDING: Q1", guard.validate_slots(run))

    def test_transitive_preattempt_link_that_exposes_w_is_a_leak(self):
        run = self.base_run()
        run["pre_attempt_graphs"][0]["nodes"][2]["move_refs"] = ["Q1-MOVE-2"]
        problems = guard.validate_pre_attempt_graphs(run)
        self.assertIn("W_LEAK_PRE_ATTEMPT_REACHABLE: Q1:CORE1A-SAFE:Q1-MOVE-2", problems)

    def test_post_attempt_resource_is_not_a_preattempt_leak(self):
        run = self.base_run()
        run["pre_attempt_graphs"][0]["nodes"][2]["phase"] = "POST_ATTEMPT"
        run["pre_attempt_graphs"][0]["nodes"][2]["move_refs"] = ["Q1-MOVE-2"]
        self.assertNotIn("W_LEAK_PRE_ATTEMPT_REACHABLE", "\n".join(guard.validate_pre_attempt_graphs(run)))

    def test_core1a_publication_requires_canonical_truth(self):
        run = self.base_run()
        run["concept_evidence"][0]["canonical_truth_refs"] = []
        self.assertIn("CORE1A_CANONICAL_TRUTH_MISSING: CE-CUBE", guard.validate_core1a_boundary(run))

    def test_bidirectional_core2_core1a_lineage_is_required(self):
        run = self.base_run()
        run["questions"][0]["core1a_targets"] = []
        self.assertIn("CORE2_TO_CORE1A_LINEAGE_MISSING: Q1->CU-CUBE-SURFACE", guard.validate_core1a_boundary(run))

    def test_invented_blueprint_ref_is_rejected(self):
        run = self.base_run()
        registry = {"blueprints": [{"id": "BP-CORE2-SOURCE-QUESTION", "version": "1.5.0"}]}
        run["questions"][0]["blueprint_ref"] = "BP-CORE1A-CONSTRUCTION-BOOK@1.5.0"
        self.assertIn(
            "BLUEPRINT_REF_NOT_IN_ACTIVE_REGISTRY: Q1:BP-CORE1A-CONSTRUCTION-BOOK@1.5.0",
            guard.validate_blueprints(run, registry),
        )

    def test_validation_layers_cannot_be_collapsed_into_self_certified_overall_pass(self):
        run = self.base_run()
        run["validation"]["overall"] = "PASS"
        self.assertIn("AGGREGATE_SELF_CERTIFICATION_FORBIDDEN", guard.validate_validation_layers(run))

    def test_partly_or_no_review_requires_fix_and_all_12_asks(self):
        run = self.base_run()
        artifact = {"id": "CORE2", "path": "dummy.html", "sha256": "sha256:" + "f" * 64, "head_sha": "a" * 40}
        run["rendered_artifacts"] = [artifact]
        run["reviews"] = [{
            "question_ref": "Q1",
            "artifact_ref": "CORE2",
            "artifact_sha256": artifact["sha256"],
            "judgements": {
                ask: {"verdict": "YES", "evidence": f"evidence for {ask}"} for ask in guard.ASKS
            },
        }]
        run["reviews"][0]["judgements"]["H3"] = {"verdict": "NO", "evidence": "H3 reveals W"}
        # Exercise the judgement-shape portion without requiring a real file path.
        original_repo = guard.REPO
        try:
            from pathlib import Path
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                guard.REPO = Path(tmp)
                (guard.REPO / "dummy.html").write_text("non-empty", encoding="utf-8")
                artifact["sha256"] = guard.sha256_file(guard.REPO / "dummy.html")
                run["reviews"][0]["artifact_sha256"] = artifact["sha256"]
                problems = guard.validate_artifacts_and_reviews(run)
                self.assertIn("QRT_FIX_MISSING: Q1:H3", problems)
        finally:
            guard.REPO = original_repo


if __name__ == "__main__":
    unittest.main()
