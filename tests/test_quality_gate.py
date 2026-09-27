"""Phase 4: the rendered gate fails thin products and passes complete ones.

The positive case is a test fixture, clearly labelled: the Mathematics linear-equations package
with every depth field supplied for one microtopic and its questions, plus a staged number-line
SVG. It exists to prove that complete records render gap-free and pass the gate. It is not a
learner product and is never published.
"""
from __future__ import annotations

import copy
import json
import re
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
    m["elicitation"]["attempt"]["task"] = {
        "prompt": "Decide, without solving, whether x = 5 makes 2x + 1 = 11 true, and whether x = 4 does. Show each substitution.",
        "givens": ["2x + 1 = 11", "candidates x = 5 and x = 4"]}
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
                           "protected_move_ref": None,
                           "novelty": {"checked_against": ["Q-MATH-LINEAR-01", "MIC-MATH-CONSTRAINT:boundary_test"],
                                       "why_new": "The earlier item undoes an addition then a multiplication; here the bracket reverses the undo order, which no earlier item shows."}}})
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
        m = product_manifest.derive("tests/fixtures/render/thin-kin-2d-motion.v1.json",
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

    def test_lineage_to_a_core1a_worked_anchor_links_to_its_microtopic(self):
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        m["selection"]["core2a"] = []                  # the earlier item is shown only as the Core1A worked anchor
        manifest.write_text(json.dumps(m), encoding="utf-8")
        out = self.build(manifest, draft=True)         # no Core2A practice is a gap; only the link matters here
        self.assertIn('href="core1a.html#MIC-MATH-CONSTRAINT"', (out / "core2b.html").read_text(encoding="utf-8"))
        report = quality_gate.gate(out, "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertNotIn("CONT_LINK_UNRESOLVED", {c["code"] for c in report["continuity"]})

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

    def test_withheld_stages_are_absent_from_the_markup_not_hidden(self):
        out = self.build(complete_fixture(self.tmp))
        html = (out / "core2a.html").read_text(encoding="utf-8")
        fig = re.search(r'<figure[^>]*data-g9-stage="PRE_ATTEMPT".*?</figure>', html, re.S).group(0)
        self.assertIn('data-g9-stage-id="VIS-MATH-NL-1"', fig)
        self.assertNotIn('data-g9-stage-id="VIS-MATH-NL-3"', fig)      # the exact point is the result
        self.assertNotIn("<title", fig)
        self.assertIn('aria-label="Number line"', fig)                   # named from the shown stage only
        self.assertIn('data-g9-caption="stages">Number line</figcaption>', fig)   # not the purpose note
        report = quality_gate.gate(out, "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertNotIn("ALL-PRE-ATTEMPT-MARKUP-WITHHELD", {f["rule"] for f in report["findings"]})

    def test_a_pre_attempt_figure_that_only_hides_later_stages_fails(self):
        out = self.build(complete_fixture(self.tmp))
        page = out / "core2a.html"
        html = page.read_text(encoding="utf-8")
        hidden = '<g data-g9-stage-id="VIS-MATH-NL-3" style="display:none"><text>7/3</text></g></svg>'
        start = html.index('data-g9-stage="PRE_ATTEMPT"')
        end = html.index("</svg>", start)
        page.write_text(html[:end] + hidden + html[end + len("</svg>"):], encoding="utf-8")
        report = quality_gate.gate(out, "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertIn("ALL-PRE-ATTEMPT-MARKUP-WITHHELD", {f["rule"] for f in report["findings"]})

    def test_core1b_mounts_its_own_task_figure(self):
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        pkg_path = Path(m["package_refs"][0])
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        rep = copy.deepcopy(next(r for r in pkg["representations"] if r["id"] == "REP-MATH-NUMBER-LINE"))
        rep["id"] = "REP-MATH-TASK-CANDIDATES"
        pkg["representations"].append(rep)
        mic = next(x for x in pkg["microtopics"] if x["id"] == "MIC-MATH-CONSTRAINT")
        mic["elicitation"]["attempt"]["task"]["representation_ref"] = "REP-MATH-TASK-CANDIDATES"
        pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
        html = (self.build(manifest) / "core1b.html").read_text(encoding="utf-8")
        self.assertIn('data-g9-representation="REP-MATH-TASK-CANDIDATES"', html)
        self.assertNotIn('data-g9-representation="REP-MATH-NUMBER-LINE"', html)

    def test_core1_mounts_the_compact_anchor_figure(self):
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        pkg_path = Path(m["package_refs"][0])
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        rep = copy.deepcopy(next(r for r in pkg["representations"] if r["id"] == "REP-MATH-NUMBER-LINE"))
        rep["id"] = "REP-MATH-ANCHOR-X2"
        pkg["representations"].append(rep)
        mic = next(x for x in pkg["microtopics"] if x["id"] == "MIC-MATH-CONSTRAINT")
        mic["compact_anchor"]["representation_ref"] = "REP-MATH-ANCHOR-X2"
        pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
        html = (self.build(manifest) / "core1.html").read_text(encoding="utf-8")
        self.assertIn('data-g9-representation="REP-MATH-ANCHOR-X2"', html)

    def test_a_pre_attempt_figure_captioned_with_its_purpose_fails(self):
        out = self.build(complete_fixture(self.tmp))
        page = out / "core2a.html"
        html = page.read_text(encoding="utf-8")
        start = html.index('data-g9-stage="PRE_ATTEMPT"')
        cap = html.index('data-g9-caption="stages"', start)
        page.write_text(html[:cap] + 'data-g9-caption="purpose"' + html[cap + len('data-g9-caption="stages"'):], encoding="utf-8")
        report = quality_gate.gate(out, "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertIn("ALL-PRE-ATTEMPT-MARKUP-WITHHELD", {f["rule"] for f in report["findings"]})

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

    def test_one_scene_reused_for_different_items_fails(self):
        manifest = complete_fixture(self.tmp)
        m = json.loads(manifest.read_text(encoding="utf-8"))
        pkg_path = Path(m["package_refs"][0])
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        twin = copy.deepcopy(next(x for x in pkg["questions"] if x["id"] == "Q-MATH-LINEAR-01"))
        twin.update(id="Q-MATH-LINEAR-TWIN", stem="Solve 5x + 1 = 12 over the rationals.")
        pkg["questions"].append(twin)
        pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
        m["selection"]["core2a"].append("Q-MATH-LINEAR-TWIN")
        manifest.write_text(json.dumps(m), encoding="utf-8")
        report = quality_gate.gate(self.build(manifest), "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        self.assertIn("ALL-FIGURE-SPECIFIC", {f["rule"] for f in report["findings"]})

    def test_a_report_cannot_claim_pass_with_findings(self):
        report = quality_gate.gate(self.build(complete_fixture(self.tmp)), "Mathematics", "FIXTURE-MATH-LINEAR", static=True)
        report["verdict"] = "PASS"
        report["findings"].append({"rule": "X", "severity": "S1", "where": "w", "detail": "d"})
        self.assertNotEqual(quality_gate.validate(report), [])


if __name__ == "__main__":
    unittest.main()
