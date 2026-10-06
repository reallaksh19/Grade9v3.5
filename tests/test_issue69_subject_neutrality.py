from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SUBJECTS = ("Chemistry", "Mathematics", "Physics")
CANONICAL_DEMANDS = {
    "RETRIEVE",
    "EXPLAIN",
    "APPLY",
    "MODEL",
    "REPRESENT",
    "SYNTHESIZE",
    "JUSTIFY",
}
DEMAND_FIELDS = {
    "review_focus",
    "representation_kinds",
    "check_types",
    "misconception_patterns",
}
FORBIDDEN_ADAPTER_POLICY_KEYS = {
    "web_blueprint_ref",
    "components",
    "slots",
    "layout_family",
    "qrt_cell",
    "template_id",
    "core_role",
}


class Issue69SubjectNeutrality(unittest.TestCase):
    @staticmethod
    def adapter(subject: str) -> dict:
        return json.loads(
            (REPO / subject / "adapter" / "DemandReview.json").read_text(encoding="utf-8")
        )

    def test_demand_adapters_specialize_the_same_canonical_demands_without_qrt_identity(self):
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                adapter = self.adapter(subject)
                self.assertEqual(adapter["schema"], "demand-review-adapter/v1")
                self.assertEqual(set(adapter["demands"]), CANONICAL_DEMANDS)
                self.assertNotIn("QRT-", json.dumps(adapter, sort_keys=True))
                for demand, row in adapter["demands"].items():
                    self.assertEqual(set(row), DEMAND_FIELDS, (subject, demand))

    def test_demand_adapters_do_not_own_page_or_product_policy(self):
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                adapter = self.adapter(subject)
                self.assertEqual(
                    adapter["basis_refs"],
                    [
                        f"{subject}/adapter/QualityVocabulary.json",
                        f"{subject}/adapter/CoreContracts.json",
                    ],
                )
                self.assertEqual(
                    adapter["vocabulary_ref"],
                    f"{subject}/adapter/QualityVocabulary.json",
                )
                payload = json.dumps(adapter, sort_keys=True)
                for key in FORBIDDEN_ADAPTER_POLICY_KEYS:
                    self.assertNotIn(f'"{key}"', payload, (subject, key))

    def test_render_core_has_no_academic_subject_literal_comparison(self):
        path = REPO / "Shared" / "tools" / "render_core.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        violations: list[tuple[int, list[str]]] = []
        subject_names = set(SUBJECTS)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            literals = {
                child.value
                for child in ast.walk(node)
                if isinstance(child, ast.Constant)
                and isinstance(child.value, str)
                and child.value in subject_names
            }
            if literals:
                violations.append((node.lineno, sorted(literals)))

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
