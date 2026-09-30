from __future__ import annotations

import copy
import unittest

from Shared.tools import quality_contract, quality_observe


class Core2V2QualityContract(unittest.TestCase):
    @staticmethod
    def _unit() -> dict:
        raw = '''
        <article data-g9-unit="Q-QUALITY" data-g9-kind="QUESTION">
          <div data-g9-block="source_identity">Official source</div>
          <div data-g9-block="stem">Question stem</div>
          <div data-g9-attempt-box><textarea></textarea></div>
          <div data-g9-block="source_hints"><h4>Source support</h4>
            <div class="g9-ladder" data-g9-support-group="SOURCE_HINT">
              <ol data-g9-ladder></ol>
              <template data-g9-rung-payload="SOURCE-1">
                <li data-g9-rung="1" data-g9-support-provenance="SOURCE_HINT"
                    data-g9-support-source="hints[0]" data-g9-support-reveals="CONCEPT">Source hint</li>
              </template>
            </div>
          </div>
          <div data-g9-block="authored_core2_support"><h4>Guided support</h4>
            <div class="g9-ladder" data-g9-support-group="AUTHORED_CORE2_PROMPT_REVEAL">
              <ol data-g9-ladder></ol>
              <template data-g9-rung-payload="AUTHORED-1">
                <li data-g9-rung="1" data-g9-support-provenance="AUTHORED_CORE2_PROMPT_REVEAL"
                    data-g9-support-source="scaffolds[0]" data-g9-support-reveals="METHOD">Guided hint</li>
              </template>
            </div>
          </div>
          <details data-g9-reveal data-requires-attempt data-g9-payload-ref="SOLUTION">
            <summary>Answer and working</summary><div data-g9-payload-slot></div>
          </details>
          <template data-g9-payload="SOLUTION">
            <div data-g9-block="answer">Answer</div>
            <div data-g9-block="structured_working">Reasoning route</div>
          </template>
        </article>
        '''
        article = quality_observe.parse(raw).first("article")
        return quality_observe._render_core_unit(article)

    @staticmethod
    def _obs(unit: dict) -> dict:
        return {
            "schema": "learner-observation/v1",
            "product_id": "quality-test",
            "subject": "Physics",
            "observed_by": "render-core-html",
            "provenance": {"render_stamp": "render_core/2 digest", "hand_authored": False},
            "escape_states": [],
            "pages": [{
                "role": "CORE2",
                "path": "core2.html",
                "blueprint_ref": None,
                "shell": None,
                "rendered": None,
                "figures": [],
                "units": [unit],
            }],
        }

    def test_render_observation_extracts_typed_support_provenance_without_materialising_content(self):
        unit = self._unit()
        self.assertEqual(
            unit["support_rows"],
            [
                {
                    "group": "SOURCE_HINT",
                    "provenance": "SOURCE_HINT",
                    "source": "hints[0]",
                    "reveals": "CONCEPT",
                    "block": "source_hints",
                    "label": "Source support",
                    "pre_solution": True,
                },
                {
                    "group": "AUTHORED_CORE2_PROMPT_REVEAL",
                    "provenance": "AUTHORED_CORE2_PROMPT_REVEAL",
                    "source": "scaffolds[0]",
                    "reveals": "METHOD",
                    "block": "authored_core2_support",
                    "label": "Guided support",
                    "pre_solution": True,
                },
            ],
        )
        self.assertEqual(unit["support_levels"], ["Source hint", "Guided hint"])

    def test_valid_source_and_authored_provenance_passes_new_integrity_rule(self):
        obs = self._obs(self._unit())
        self.assertEqual(quality_contract.validate_observation(obs), [])
        self.assertNotIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(obs)["rules_failed"])

    def test_source_custody_cannot_be_relabelled_as_authored_or_guided(self):
        unit = self._unit()
        unit["support_rows"][0]["provenance"] = "AUTHORED_CORE2_PROMPT_REVEAL"
        unit["support_rows"][0]["group"] = "AUTHORED_CORE2_PROMPT_REVEAL"
        unit["support_rows"][0]["label"] = "Guided support"
        self.assertIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(self._obs(unit))["rules_failed"])

    def test_authored_scaffold_cannot_be_presented_as_source_support(self):
        unit = self._unit()
        unit["support_rows"][1]["provenance"] = "SOURCE_HINT"
        unit["support_rows"][1]["group"] = "SOURCE_HINT"
        unit["support_rows"][1]["block"] = "source_hints"
        unit["support_rows"][1]["label"] = "Source support"
        self.assertIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(self._obs(unit))["rules_failed"])

    def _inline(self, provenance: str, block: str, label: str, source: str = "hint_ladder[0]") -> dict:
        unit = self._unit()
        unit["support_rows"][0].update(
            source=source, provenance=provenance, group=provenance, block=block, label=label)
        return unit

    def test_inline_rung_takes_the_provenance_it_declares(self):
        for provenance, block, label in (
            ("SOURCE_HINT", "source_hints", "Source support"),
            ("AUTHORED_CORE2_PROMPT_REVEAL", "authored_core2_support", "Guided support"),
        ):
            unit = self._inline(provenance, block, label)
            self.assertNotIn(
                "C2-SUPPORT-PROVENANCE",
                quality_contract.evaluate(self._obs(unit))["rules_failed"], provenance)

    def test_inline_rung_must_still_be_presented_as_what_it_declares(self):
        unit = self._inline("SOURCE_HINT", "authored_core2_support", "Guided support")
        self.assertIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(self._obs(unit))["rules_failed"])

    def test_inline_rung_with_an_unknown_provenance_is_not_recognised(self):
        unit = self._inline("INVENTED", "source_hints", "Source support")
        self.assertIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(self._obs(unit))["rules_failed"])

    def test_declared_mapping_does_not_let_a_source_hint_be_relabelled(self):
        unit = self._unit()
        unit["support_rows"][0].update(
            provenance="AUTHORED_CORE2_PROMPT_REVEAL", group="AUTHORED_CORE2_PROMPT_REVEAL",
            block="authored_core2_support", label="Guided support")
        self.assertIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(self._obs(unit))["rules_failed"])

    def test_answer_revealing_support_fails_when_observed_pre_solution(self):
        unit = self._unit()
        unit["support_rows"][1]["reveals"] = "ANSWER"
        self.assertIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(self._obs(unit))["rules_failed"])

    def test_structured_working_is_part_of_attempt_gated_solution_contract(self):
        unit = self._unit()
        obs = self._obs(unit)
        self.assertNotIn("C2-ANSWER-ON-REVEAL", quality_contract.evaluate(obs)["rules_failed"])
        broken = copy.deepcopy(obs)
        broken["pages"][0]["units"][0]["reveals"][0]["gated"] = False
        self.assertIn("C2-ANSWER-ON-REVEAL", quality_contract.evaluate(broken)["rules_failed"])

    def test_legacy_observation_without_typed_support_rows_remains_compatible(self):
        unit = self._unit()
        del unit["support_rows"]
        obs = self._obs(unit)
        self.assertEqual(quality_contract.validate_observation(obs), [])
        self.assertNotIn("C2-SUPPORT-PROVENANCE", quality_contract.evaluate(obs)["rules_failed"])


if __name__ == "__main__":
    unittest.main()
