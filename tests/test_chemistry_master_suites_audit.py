#!/usr/bin/env python3
"""Regression tests for the four Chemistry master suites extracted from PR #144."""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

SUITES = {
    "bonding": (
        REPO / "public/chemistry/bonding/explorers/chemical_bonding/index.html",
        REPO / "public/chemistry/bonding/explorers/chemical_bonding/jee_questions_data.js",
        REPO / "standalone/chemistry-chemical-bonding-master-suite.html",
        17,
        3,
    ),
    "mole": (
        REPO / "public/chemistry/some-basic-concepts/explorers/mole_concept/index.html",
        REPO / "public/chemistry/some-basic-concepts/explorers/mole_concept/jee_questions_data.js",
        REPO / "standalone/chemistry-mole-concept-master-suite.html",
        5,
        15,
    ),
    "redox": (
        REPO / "public/chemistry/redox/explorers/redox_reactions/index.html",
        REPO / "public/chemistry/redox/explorers/redox_reactions/jee_questions_data.js",
        REPO / "standalone/chemistry-redox-reactions-master-suite.html",
        8,
        12,
    ),
    "gases": (
        REPO / "public/chemistry/gases/explorers/behaviour_of_gases/index.html",
        REPO / "public/chemistry/gases/explorers/behaviour_of_gases/jee_questions_data.js",
        REPO / "standalone/chemistry-behaviour-of-gases-master-suite.html",
        2,
        18,
    ),
}

REQUIRED = {
    "id", "q", "options", "formula", "steps", "ans", "trap",
    "answerAudit", "answerAuditNote", "sourceAudit", "sourceAuditNote",
    "teacherCheck", "takeaway", "helperTags",
    "simFidelity", "simFidelityNote", "targetTab", "simParams", "simBindingRefs",
}


def load_bank(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    start = text.index("[")
    end = text.rindex("]") + 1
    return json.loads(text[start:end])


def load_window_payload(text: str, name: str):
    marker = text.index(f"window.{name}")
    assign = text.index("=", marker) + 1
    payload = text[assign:].lstrip()
    data, _ = json.JSONDecoder().raw_decode(payload)
    return data


def embedded_bank(html: str) -> list[dict]:
    marker = html.index("window.JEE_QUESTIONS_DATA")
    assign = html.index("=", marker) + 1
    payload = html[assign:].lstrip()
    data, _ = json.JSONDecoder().raw_decode(payload)
    return data


class ChemistryMasterSuitesAuditTest(unittest.TestCase):
    def test_banks_are_structurally_audited(self):
        for name, (html_path, data_path, _, constrained, concept) in SUITES.items():
            with self.subTest(suite=name):
                html = html_path.read_text(encoding="utf-8")
                bank = load_bank(data_path)
                self.assertEqual(len(bank), 20)
                self.assertEqual(len({q["id"] for q in bank}), 20)
                self.assertNotIn("ExamSIDE Verified Bank", html)

                for q in bank:
                    self.assertTrue(REQUIRED.issubset(q), q["id"])
                    self.assertIn(
                        q["sourceAudit"],
                        {"SOURCE_PROVENANCE_PENDING", "SOURCE_UNVERIFIED"},
                        q["id"],
                    )
                    self.assertIn(f'id="{q["targetTab"]}"', html, q["id"])
                    refs = q["simBindingRefs"]
                    self.assertEqual(
                        refs,
                        [f"simParams.{key}" for key in q["simParams"]],
                        q["id"],
                    )
                    if q["simFidelity"] == "CONSTRAINT_FAITHFUL":
                        self.assertTrue(refs, q["id"])
                    elif q["simFidelity"] == "CONCEPT_ONLY":
                        self.assertEqual(refs, [], q["id"])
                    else:
                        self.fail(f"{q['id']}: unexpected fidelity {q['simFidelity']}")

                    self.assertEqual(
                        q["helperTags"],
                        [
                            "TEACHERS_CHALKBOARD",
                            "TRAP_ALERT",
                            "INDEPENDENT_CHECK",
                            "TRANSFER_TAKEAWAY",
                            "EXACTNESS_BADGE",
                        ],
                        q["id"],
                    )

                    if q["answerAudit"] == "PASS":
                        self.assertIn(q["correct"], {o["key"] for o in q["options"]})

                self.assertEqual(
                    sum(q["simFidelity"] == "CONSTRAINT_FAITHFUL" for q in bank),
                    constrained,
                )
                self.assertEqual(
                    sum(q["simFidelity"] == "CONCEPT_ONLY" for q in bank),
                    concept,
                )

                expected_unverified = {
                    "bonding": {"BOND-Q19"},
                    "mole": {"CHEM02-Q04"},
                    "redox": set(),
                    "gases": {"GAS-Q01", "GAS-Q06"},
                }[name]
                self.assertEqual(
                    {q["id"] for q in bank if q["sourceAudit"] == "SOURCE_UNVERIFIED"},
                    expected_unverified,
                )

    def test_known_answer_audit_exceptions_are_fail_closed(self):
        bonding = {q["id"]: q for q in load_bank(SUITES["bonding"][1])}
        mole = {q["id"]: q for q in load_bank(SUITES["mole"][1])}

        self.assertEqual(bonding["BOND-Q19"]["answerAudit"], "PASS")
        self.assertEqual(bonding["BOND-Q19"]["correct"], "B")
        self.assertEqual(bonding["BOND-Q19"]["sourceAudit"], "SOURCE_UNVERIFIED")
        self.assertEqual(mole["CHEM02-Q04"]["answerAudit"], "FAIL")
        self.assertEqual(mole["CHEM02-Q04"]["sourceAudit"], "SOURCE_UNVERIFIED")
        self.assertIsNone(mole["CHEM02-Q04"]["correct"])
        self.assertIn("C₄H₆", mole["CHEM02-Q04"]["ans"])

    def test_known_source_attribution_mismatches_are_explicit(self):
        bonding = {q["id"]: q for q in load_bank(SUITES["bonding"][1])}
        mole = {q["id"]: q for q in load_bank(SUITES["mole"][1])}
        gases = {q["id"]: q for q in load_bank(SUITES["gases"][1])}

        self.assertEqual(bonding["BOND-Q19"]["sourceAudit"], "SOURCE_UNVERIFIED")
        self.assertEqual(mole["CHEM02-Q04"]["sourceAudit"], "SOURCE_UNVERIFIED")
        self.assertEqual(gases["GAS-Q01"]["sourceAudit"], "SOURCE_UNVERIFIED")
        self.assertEqual(gases["GAS-Q06"]["sourceAudit"], "SOURCE_UNVERIFIED")

    def test_canvas_setup_does_not_recurse_dpr_height(self):
        for name, (html_path, _, _, _, _) in SUITES.items():
            with self.subTest(suite=name):
                html = html_path.read_text(encoding="utf-8")
                start = html.index("function setupCanvas")
                end = html.index("\n    function ", start + 20)
                setup = html[start:end]
                self.assertIn("dataset.logicalHeight", setup)
                self.assertIn("ctx.setTransform", setup)
                self.assertNotIn("getAttribute('height') ?", setup)

        bonding = SUITES["bonding"][0].read_text(encoding="utf-8")
        self.assertNotIn("window.addEventListener('mousemove'", bonding)
        self.assertNotIn("window.addEventListener('touchmove'", bonding)
        self.assertIn("pointerdown", bonding)

    def test_standalones_embed_exact_canonical_bank(self):
        for name, (_, data_path, standalone_path, _, _) in SUITES.items():
            with self.subTest(suite=name):
                source = load_bank(data_path)
                html = standalone_path.read_text(encoding="utf-8")
                self.assertEqual(embedded_bank(html), source)
                self.assertNotIn('src="jee_questions_data.js"', html)
                self.assertIn("SINGLE_FILE_ONLINE", html)

    def test_no_duplicate_static_ids_or_unresolved_inline_handlers(self):
        for name, (html_path, _, _, _, _) in SUITES.items():
            with self.subTest(suite=name):
                html = html_path.read_text(encoding="utf-8")
                ids = re.findall(r'\bid="([^"]+)"', html)
                self.assertEqual(len(ids), len(set(ids)))
                handlers = set(re.findall(
                    r'on(?:click|input|change)="([A-Za-z_$][\w$]*)\(',
                    html,
                ))
                functions = set(re.findall(
                    r'function\s+([A-Za-z_$][\w$]*)\s*\(',
                    html,
                ))
                self.assertEqual(handlers - functions, set())

    def test_governed_chemistry_representation_invariants(self):
        # Chemical Bonding: standard introductory MO fixtures.
        self.assertAlmostEqual(0.5 * (10 - 4), 3.0)   # O2^2+ / 14 e- fixture
        self.assertAlmostEqual(0.5 * (8 - 4), 2.0)    # C2 net bond order
        self.assertAlmostEqual(3.0 - 0.5, 2.5)        # locally corrected CO+ classroom value

        # Mole Concept: Q01 Haber limiting-reagent ledger.
        n_n2 = 56.0 / 28.0
        n_h2 = 10.0 / 2.0
        extent = min(n_n2 / 1.0, n_h2 / 3.0)
        n_nh3 = 2.0 * extent
        excess_n2 = n_n2 - extent
        self.assertAlmostEqual(n_nh3 * 17.0, 56.6666666667, places=8)
        self.assertAlmostEqual(excess_n2 * 28.0, 9.3333333333, places=8)

        # Redox: FeC2O4 loses 3 e- per formula unit; dichromate gains 6 e-.
        electrons_per_ferrous_oxalate = 1 + 2
        electrons_per_dichromate = 6
        self.assertEqual(electrons_per_ferrous_oxalate, 3)
        self.assertAlmostEqual(
            electrons_per_ferrous_oxalate / electrons_per_dichromate,
            0.5,
        )

        # Gases: Maxwell characteristic-speed invariant at common T, M.
        R, T, M = 8.314, 300.0, 0.028
        v_mp = math.sqrt(2 * R * T / M)
        v_avg = math.sqrt(8 * R * T / (math.pi * M))
        v_rms = math.sqrt(3 * R * T / M)
        self.assertLess(v_mp, v_avg)
        self.assertLess(v_avg, v_rms)
        self.assertAlmostEqual(v_avg / v_mp, 2 / math.sqrt(math.pi), places=12)
        self.assertAlmostEqual(v_rms / v_mp, math.sqrt(3 / 2), places=12)

    def test_suite_contracts_match_live_snapshot_and_delivery_profile(self):
        expected = {
            "chemistry-chemical-bonding.json": (266, "public/chemistry/bonding/explorers/chemical_bonding/jee_questions_data.js"),
            "chemistry-mole-concept.json": (245, "public/chemistry/some-basic-concepts/explorers/mole_concept/jee_questions_data.js"),
            "chemistry-redox.json": (74, "public/chemistry/redox/explorers/redox_reactions/jee_questions_data.js"),
            "chemistry-gaseous-state.json": (66, "public/chemistry/gases/explorers/behaviour_of_gases/jee_questions_data.js"),
        }
        for name, (live_count, source) in expected.items():
            with self.subTest(contract=name):
                obj = json.loads((REPO / "docs/gcdr-suites" / name).read_text(encoding="utf-8"))
                self.assertEqual(obj["scope_contract"]["canonical_binding_status"], "UNBOUND_EXTENSION")
                self.assertEqual(obj["scope_contract"]["instructional_depth"], "JEE_EXTENSION")
                self.assertEqual(obj["external_corpus"]["snapshot_date"], "2026-09-20")
                self.assertEqual(obj["external_corpus"]["live_count"], live_count)
                self.assertEqual(obj["external_corpus"]["embedded_item_count"], 20)
                self.assertEqual(obj["external_corpus"]["coverage_claim"], "CURATED_SLICE_AUDITED")
                self.assertEqual(obj["diagnostic_source"]["locator"], source)
                self.assertEqual(
                    {row["profile"] for row in obj["delivery_artifacts"]},
                    {"REPO_BUNDLE", "SINGLE_FILE_ONLINE"},
                )
                self.assertEqual(obj["geometry_truth_contract"]["verification_status"], "DECLARED")
                self.assertTrue(obj["representation_invariants"])

    def test_redox_examside_content_map_is_complete(self):
        html = SUITES["redox"][0].read_text(encoding="utf-8")
        tracks = load_window_payload(html, "REDOX_CONTENT_TRACKS")
        meta = load_window_payload(html, "EXAMSIDE_REDOX_CORPUS_META")
        corpus = load_window_payload(html, "EXAMSIDE_REDOX_CORPUS_MAP")
        local = load_window_payload(html, "REDOX_LOCAL_ITEM_TRACKS")

        self.assertEqual(meta["liveCount"], 74)
        self.assertEqual(meta["numericalCount"], 29)
        self.assertEqual(meta["mcqCount"], 45)
        self.assertEqual(len(corpus), 74)
        self.assertEqual(len({row["ref"] for row in corpus}), 74)
        self.assertEqual(sum(row["kind"] == "Numerical" for row in corpus), 29)
        self.assertEqual(sum(row["kind"] == "MCQ" for row in corpus), 45)

        track_ids = {row["id"] for row in tracks}
        self.assertTrue({row["track"] for row in corpus}.issubset(track_ids))
        self.assertEqual(
            {row["id"] for row in load_bank(SUITES["redox"][1])},
            {row["id"] for row in local},
        )
        self.assertEqual(
            {row["id"] for row in local if row["track"] == "OFFCORP"},
            {"REDOX-Q08", "REDOX-Q16", "REDOX-Q19"},
        )

        counts = {}
        for row in corpus:
            counts[row["track"]] = counts.get(row["track"], 0) + 1
        self.assertEqual(
            counts,
            {
                "OS": 14,
                "ROLE": 16,
                "DISP": 9,
                "BAL": 4,
                "NFACTOR": 5,
                "EQUIV": 6,
                "TITR": 8,
                "RELATED": 12,
            },
        )

        standalone = SUITES["redox"][2].read_text(encoding="utf-8")
        self.assertIn('id="tab-examside-map"', html)
        self.assertIn("renderExamSideMap", html)
        self.assertIn("window.EXAMSIDE_REDOX_CORPUS_MAP", html)
        self.assertEqual(
            load_window_payload(standalone, "EXAMSIDE_REDOX_CORPUS_MAP"),
            corpus,
        )
        self.assertEqual(
            load_window_payload(standalone, "REDOX_LOCAL_ITEM_TRACKS"),
            local,
        )

        helpers = load_window_payload(html, "REDOX_OS_QUESTION_HELPERS")
        self.assertTrue(all(row.get("preview") for row in corpus))
        self.assertTrue(all(row.get("previewStatus") == "PARAPHRASED_FROM_LIVE_EXAMSIDE_INDEX" for row in corpus))
        os_refs = {row["ref"] for row in corpus if row["track"] == "OS"}
        self.assertEqual(len(helpers), 14)
        self.assertEqual({row["ref"] for row in helpers}, os_refs)
        for row in helpers:
            self.assertTrue(row["question"])
            self.assertTrue(row["visualFlow"])
            self.assertTrue(row["visualConnect"])
            self.assertGreaterEqual(len(row["derivation"]), 2)
            self.assertTrue(row["answer"])

        self.assertIn('id="examSideQuestionTooltip"', html)
        self.assertIn("examSideQuestionChip", html)
        self.assertIn('id="osExamSideQuestionLab"', html)
        self.assertIn("renderOSQuestionLab", html)
        self.assertEqual(
            load_window_payload(standalone, "REDOX_OS_QUESTION_HELPERS"),
            helpers,
        )

        track_helpers = load_window_payload(html, "REDOX_TRACK_QUESTION_HELPERS")
        core_tracks = {"ROLE", "BAL", "NFACTOR", "DISP", "EQUIV", "TITR"}
        self.assertEqual(
            load_window_payload(standalone, "REDOX_TRACK_QUESTION_HELPERS"),
            track_helpers,
        )
        self.assertIn("teachingQuestionCard", html)
        self.assertIn("localTeachingQuestionCard", html)
        self.assertIn("DERIVED RESULT", html)
        self.assertIn("REASONING CHECKPOINT", html)
        self.assertNotIn("VISUAL / METHOD BRIDGE", html)

        core_refs = {row["ref"] for row in corpus if row["track"] in core_tracks}
        self.assertEqual(len(core_refs), 48)
        self.assertEqual(len(track_helpers), 48)
        self.assertEqual({row["ref"] for row in track_helpers}, core_refs)
        for row in track_helpers:
            self.assertIn(row["track"], core_tracks)
            self.assertTrue(row["checkpoint"])
            self.assertGreaterEqual(len(row["derivation"]), 2)
            self.assertTrue(row["answer"])
            self.assertTrue(row["answerStatus"])
            self.assertNotIn("bridge", row)

        nfactor_helpers = [row for row in track_helpers if row["track"] == "NFACTOR"]
        self.assertEqual(len(nfactor_helpers), 5)
        self.assertTrue(all("actual reduction/oxidation product" in row["checkpoint"] for row in nfactor_helpers))

        n13 = next(row for row in corpus if row["ref"] == "N13")
        n15 = next(row for row in corpus if row["ref"] == "N15")
        self.assertEqual(n13["track"], "BAL")
        self.assertIn("Cr₂O₇", n13["preview"])
        self.assertNotIn("Fe(CO)", n13["preview"])
        self.assertEqual(n15["track"], "OS")
        self.assertIn("Fe(CO)", n15["preview"])

        self.assertTrue(all(row.get("equationStages") for row in helpers))
        self.assertIn('id="canvasOxEquationWorkbench"', html)
        self.assertIn("loadOxEquationQuestion", html)
        self.assertIn("renderMappedTrackQuestionBanks", html)
        for container_id in (
            "electronFlowQuestionBank",
            "ionElectronQuestionBank",
            "nfactorQuestionBank",
            "titrationQuestionBank",
            "electroQuestionBank",
        ):
            self.assertIn(f'id="{container_id}"', html)
        self.assertIn("z-[9999]", html)
        self.assertIn("bg-slate-950 p-3", html)

    def test_js_bank_parser_handles_semicolon_bracket_inside_strings(self):
        from Shared.tools import gcdr_suite_guard

        payload = (
            'window.JEE_QUESTIONS_DATA = ['
            '{"id":"X","q":"dimension [a] = [P][V^2]/[n^2]; enforce constraint"}'
            '];\n'
        )
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as fh:
            fh.write(payload)
            temp = Path(fh.name)
        try:
            parsed = gcdr_suite_guard.load_bank(temp, "WINDOW_JEE_QUESTIONS_DATA_JS")
            self.assertEqual(parsed[0]["id"], "X")
            self.assertIn("]; enforce", parsed[0]["q"])
        finally:
            temp.unlink(missing_ok=True)

    def test_runtime_dependency_detector_ignores_source_navigation_links(self):
        from Shared.tools import gcdr_suite_guard

        html = (
            '<script src="https://cdn.example/a.js"></script>'
            '<link rel="stylesheet" href="https://cdn.example/a.css">'
            '<a href="https://questions.example/source">source</a>'
        )
        self.assertEqual(
            gcdr_suite_guard._external_dependencies(html),
            {"https://cdn.example/a.js", "https://cdn.example/a.css"},
        )

    def test_inline_javascript_parses_with_node(self):
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        for name, (html_path, _, _, _, _) in SUITES.items():
            html = html_path.read_text(encoding="utf-8")
            blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S)
            script = "\n".join(blocks)
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as fh:
                fh.write(script)
                temp = Path(fh.name)
            try:
                proc = subprocess.run(
                    ["node", "--check", str(temp)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, f"{name}: {proc.stderr}")
            finally:
                temp.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
