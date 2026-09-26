"""Phase 4: the rendered gate fails thin products and passes complete ones.

The positive case is a test fixture, clearly labelled: the Mathematics linear-equations package
with every depth field supplied for one microtopic and its questions, plus a staged number-line
SVG. It exists to prove that complete records render gap-free and pass the gate. It is not a
learner product and is never published.
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import product_manifest, quality_gate, render_core  # noqa: E402

MATH = "Mathematics/library/linear-equations.v1.json"
SVG = "tests/fixtures/render/number-line-7-3.svg"
NODE_OK = shutil.which("node") is not None


def complete_fixture(tmp: Path) -> Path:
    pkg = json.loads((REPO / MATH).read_text(encoding="utf-8"))
    rep = next(r for r in pkg["representations"] if r["id"] == "REP-MATH-NUMBER-LINE")
    rep["rendered_asset_refs"] = [SVG]
    rep["reveal_stages"] = [
        {"id": "VIS-MATH-NL-1", "label": "Number line", "purpose": "Show the integers only.", "visible_elements": ["number line 0-4"]},
        {"id": "VIS-MATH-NL-2", "label": "Bracket", "purpose": "Mark the integers either side of the solution.", "visible_elements": ["2", "3"]},
        {"id": "VIS-MATH-NL-3", "label": "Exact point", "purpose": "Place 7/3 between them.", "visible_elements": ["7/3"]}]
    m = next(x for x in pkg["microtopics"] if x["id"] == "MIC-MATH-CONSTRAINT")
    m["compact_anchor"] = {"prompt": "Is x = 2 a solution of 3x + 2 = 9?",
                           "result": "No: 3 × 2 + 2 = 8, and 8 ≠ 9, so the claim is false for x = 2."}
    for u in m["construction_units"]:
        u.pop("migrated_from", None)
        u["worked_anchor_ref"] = "Q-MATH-LINEAR-01"
        u["representation_ref"] = "REP-MATH-NUMBER-LINE"
        u["independent_checks"] = [{"statement": "Substitute the candidate: both sides must give the same number exactly.",
                                    "check_type": "SUBSTITUTION_BACK_CHECK"}]
    q = next(x for x in pkg["questions"] if x["id"] == "Q-MATH-LINEAR-01")
    q["representation_roles"] = {"initial_ref": "REP-MATH-NUMBER-LINE", "safe_ref": None, "bound_ref": None, "stage_refs": []}
    q["failure_signal"] = "Writing x = 2.33: substituting it gives 8.99, not 9, so a rounded decimal is a different claim."
    q["family_exposure"] = {"family_ref": q["family_ref"],
                            "closure": "You solved ax + b = c by undoing operations and kept the exact fraction. Transfer will change which operation comes first."}
    t = copy.deepcopy(q)
    t.update({"id": "Q-MATH-LINEAR-2B-FIXTURE", "stem": "Solve 3(x + 2) = 13 over the rationals and verify the exact solution.",
              "exposure": [{"core": "CORE2B", "role": "TRANSFER", "artifact_ref": None}],
              "hints": [], "scaffolds": [], "hint_ladder": [],
              "representation_roles": {"initial_ref": None, "safe_ref": "REP-MATH-NUMBER-LINE", "bound_ref": None, "stage_refs": []},
              "transfer": {"dimension": "model_choice", "builds_on": ["Q-MATH-LINEAR-01"],
                           "statement": "The addition now sits inside the multiplication, so the undo order reverses: divide by 3 first.",
                           "invariant": "Each step is an equivalent operation on both sides, and the answer stays an exact fraction.",
                           "protected_move_ref": None}})
    t["answer"] = dict(q["answer"], summary="x = 7/3.",
                       reasoning=["Divide both sides by 3: x + 2 = 13/3.", "Subtract 2: x = 13/3 − 6/3 = 7/3.",
                                  "Check: 3(7/3 + 2) = 3 × 13/3 = 13."],
                       check="3(7/3 + 2) = 13 exactly; 2.33 would give 12.99.")
    pkg["questions"].append(t)
    pkg_path = tmp / "linear-equations.fixture.json"
    pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
    bank = {"questions": [dict(copy.deepcopy(q), id="SRC-FIXTURE-LINEAR-01", origin="SOURCE", origin_ref="FIXTURE-SOURCE",
                               exposure=[{"core": "CORE2", "role": "SOURCE", "artifact_ref": None}],
                               extensions={"grade9v3:source_custody": {"exam": "Test fixture", "year": 2026, "paper": "Fixture", "question_number": "1"}})]}
    bank_path = tmp / "bank.fixture.json"
    bank_path.write_text(json.dumps(bank), encoding="utf-8")
    manifest = product_manifest.derive(MATH, [], "FIXTURE-MATH-LINEAR", "Linear equations (fixture)", "../index.html")
    manifest["package_refs"] = [str(pkg_path)]
    manifest["bank_refs"] = [str(bank_path)]
    manifest["selection"] = {"microtopics": ["MIC-MATH-CONSTRAINT"], "core2": ["SRC-FIXTURE-LINEAR-01"],
                             "core2a": ["Q-MATH-LINEAR-01"], "core2b": ["Q-MATH-LINEAR-2B-FIXTURE"]}
    path = tmp / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class Gate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def build(self, manifest: Path, draft=False) -> Path:
        out = self.tmp / "out"
        args = ["build", "--manifest", str(manifest), "--out", str(out)] + (["--draft"] if draft else [])
        self.assertEqual(render_core.main(args), 0)
        return out

    def test_complete_records_render_without_gaps(self):
        _, gaps, _ = render_core.build(complete_fixture(self.tmp))
        self.assertEqual(gaps, [])

    @unittest.skipUnless(NODE_OK, "node/Chromium needed for the rendered measurement")
    def test_complete_product_passes_and_the_report_is_valid(self):
        out = self.build(complete_fixture(self.tmp))
        report = quality_gate.gate(out, "Mathematics", "FIXTURE-MATH-LINEAR")
        self.assertEqual(quality_gate.validate(report), [])
        self.assertEqual(report["verdict"], "PASS", [f for f in report["findings"] if f["severity"] != "S3"] + report["continuity"] + report["fail_reasons"])

    def test_thin_real_product_fails_as_a_draft(self):
        m = product_manifest.derive("Physics/library/phy-kin-2d-motion.v1.json",
                                    ["Physics/library/exam-bank/competitive-exam-question-bank.v2.json"],
                                    "PRODUCT-PHY-KIN-2D", "Motion in a Plane", "../index.html")
        path = self.tmp / "m.json"
        path.write_text(json.dumps(m), encoding="utf-8")
        out = self.build(path, draft=True)
        report = quality_gate.gate(out, "Physics", "PRODUCT-PHY-KIN-2D", static=True)
        self.assertEqual(report["verdict"], "FAIL")
        self.assertTrue({"DRAFT", "BLOCKING_FINDINGS"} <= set(report["fail_reasons"]))
        rules = {f["rule"] for f in report["findings"]}
        self.assertTrue({"C2A-REPRESENTATION", "C2B-SAFE-REPRESENTATION", "C1A-REPRESENTATION-BRIDGE"} <= rules)

    def test_ungated_answer_and_broken_lineage_fail(self):
        out = self.build(complete_fixture(self.tmp))
        page = out / "core2a.html"
        page.write_text(page.read_text(encoding="utf-8").replace(" data-requires-attempt", ""), encoding="utf-8")
        page = out / "core2b.html"
        page.write_text(page.read_text(encoding="utf-8").replace("core2a.html#Q-MATH-LINEAR-01", "core2a.html#Q-GONE"), encoding="utf-8")
        report = quality_gate.gate(out, "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertIn("C2A-REVEAL-GATED", {f["rule"] for f in report["findings"]})
        self.assertIn("CONT_LINK_UNRESOLVED", {c["code"] for c in report["continuity"]})

    def test_pre_attempt_figure_that_shows_the_result_fails(self):
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        pkg_path = Path(m["package_refs"][0])
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        q = next(x for x in pkg["questions"] if x["id"] == "Q-MATH-LINEAR-01")
        q["representation_roles"]["stage_refs"] = ["VIS-MATH-NL-1", "VIS-MATH-NL-2", "VIS-MATH-NL-3"]
        pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
        report = quality_gate.gate(self.build(manifest), "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertIn("ALL-PRE-ATTEMPT-FIGURE-PARTIAL", {f["rule"] for f in report["findings"]})

    def test_every_owner_input_must_resolve_to_a_rendered_unit(self):
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        m["ledger"] = [{"input_id": "q-ok", "kind": "question", "teaching": None, "practice": "Q-MATH-LINEAR-01"},
                       {"input_id": "q-open", "kind": "question", "teaching": None, "practice": None},
                       {"input_id": "s-gone", "kind": "syllabus", "teaching": "MIC-NOT-IN-PRODUCT", "practice": None}]
        manifest.write_text(json.dumps(m), encoding="utf-8")
        report = quality_gate.gate(self.build(manifest), "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        codes = [c["code"] for c in report["continuity"]]
        self.assertEqual(sorted(codes), ["CONT_INPUT_NOT_RENDERED", "CONT_INPUT_UNRESOLVED"])

    def test_a_report_cannot_claim_pass_with_findings(self):
        report = quality_gate.gate(self.build(complete_fixture(self.tmp)), "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        report["verdict"] = "PASS"
        report["findings"].append({"rule": "X", "severity": "S1", "where": "w", "detail": "d"})
        self.assertNotEqual(quality_gate.validate(report), [])


if __name__ == "__main__":
    unittest.main()
