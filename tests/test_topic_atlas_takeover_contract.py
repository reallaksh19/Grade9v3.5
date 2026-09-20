#!/usr/bin/env python3
"""Falsifiers for the governed Topic Atlas browser-correctness takeover."""
from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[1]
JS = REPO / "public/js/topic-atlas.js"
AUTHORING_SCHEMA = REPO / "Shared/library/authoring-request.schema.json"
ATLAS_PAGES = [
    REPO / "public/physics/nlm/index.html",
    REPO / "public/physics/motion-2d/index.html",
]


def run_node(body: str):
    if not shutil.which("node"):
        raise unittest.SkipTest("node is required for browser-contract execution")
    harness = f"""
global.window = {{}};
global.document = {{ getElementById: () => null }};
global.localStorage = {{ getItem: () => null, setItem: () => {{}}, removeItem: () => {{}} }};
global.alert = () => {{}};
const fs = require('fs');
const vm = require('vm');
vm.runInThisContext(fs.readFileSync({json.dumps(str(JS))}, 'utf8'), {{ filename: 'topic-atlas.js' }});
const t = window.ATLAS.__test;
{body}
"""
    out = subprocess.check_output(["node", "-e", harness], text=True)
    return json.loads(out)


MATRIX_JS = r"""
const matrix = {
  matrix_id: 'MATRIX-TEST',
  subject: 'Subject',
  topic: 'Topic',
  subtopic: 'Subtopic',
  bucket_id: 'BUCKET-TEST',
  rungs: [
    {
      rung: 'R1', ladder_position: 20, default_entry_eligible: true,
      capability: { id: 'CAP-TEST-A', action: 'do A', success_criterion: 'A succeeds', prerequisite_refs: [] },
      microtopic: {
        id: 'MIC-TEST-A', title: 'A', intrinsic_badge: 'MEDIUM', badge_reason: 'reason',
        teaching_path: [
          { id: 'STEP-A1', role: 'DECLARE', action: 'declare', why_valid: 'valid 1' },
          { id: 'STEP-A2', role: 'TRANSFORM', action: 'transform', why_valid: 'valid 2' }
        ],
        misconceptions: [{ wrong_idea: 'wrong', diagnostic_prompt: 'prompt', repair: 'repair' }]
      },
      questions: [{ id: 'Q1', family_ref: 'F1', repair_ref: 'STEP-A2', stem: 'stem' }]
    },
    {
      rung: 'R3', ladder_position: 90, default_entry_eligible: true,
      capability: { id: 'CAP-TEST-C', action: 'do C', success_criterion: 'C succeeds', prerequisite_refs: [] },
      microtopic: { id: 'MIC-TEST-C', title: 'C', teaching_path: [{ id: 'STEP-C1', role: 'DECLARE', action: 'c', why_valid: 'c valid' }], misconceptions: [] },
      questions: []
    },
    {
      rung: 'R4', ladder_position: 100, default_entry_eligible: false,
      capability: { id: 'CAP-TEST-D', action: 'do D', success_criterion: 'D succeeds', prerequisite_refs: [] },
      microtopic: { id: 'MIC-TEST-D', title: 'D', teaching_path: [{ id: 'STEP-D1', role: 'DECLARE', action: 'd', why_valid: 'd valid' }], misconceptions: [] },
      questions: []
    }
  ]
};
"""


class TopicAtlasTakeoverContractTest(unittest.TestCase):
    def test_only_two_normal_learner_input_channels_remain(self):
        source = JS.read_text(encoding="utf-8")
        self.assertNotIn("leaf_progress", source)
        self.assertNotIn("syncKnowledgeToSkillProgress", source)
        self.assertNotIn("markAllLeaves", source)
        self.assertNotIn("cycleLeafStatus", source)
        for page in ATLAS_PAGES:
            html = page.read_text(encoding="utf-8")
            self.assertNotIn("Sync Knowledge with Leaf Progress", html)
            self.assertNotIn("Master All Leaves", html)
            self.assertNotIn("Skill Matrix Progress", html)

    def test_diagnostic_rows_fail_closed_and_narrow_ref_degrades_only_one_level(self):
        result = run_node(MATRIX_JS + r"""
const valid = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-TEST-A', rung_ref:'R1', repair_ref:'STEP-A2',
  result:'MISSING', error_stage:'CONCEPT', score:20, observed:'wrong direction'
}, 0);
const badCap = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-NO', result:'MISSING', error_stage:'CONCEPT', observed:'x'
}, 1);
const badRung = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-TEST-A', rung_ref:'R4', result:'MISSING', error_stage:'CONCEPT', observed:'x'
}, 2);
const badResult = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-TEST-A', result:'DEMONSTRATED', error_stage:'CONCEPT', observed:'x'
}, 3);
const badStage = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-TEST-A', result:'MISSING', error_stage:'IMPLEMENTATION', observed:'x'
}, 4);
const badScore = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-TEST-A', result:'MISSING', error_stage:'CONCEPT', score:101, observed:'x'
}, 5);
const narrow = t.validateDiagnosticRow(matrix.rungs, {
  capability_ref:'CAP-TEST-A', repair_ref:'NO-SUCH-STEP',
  result:'UNCERTAIN', error_stage:'SETUP', score:50, observed:'setup incomplete'
}, 6);
console.log(JSON.stringify({valid,badCap,badRung,badResult,badStage,badScore,narrow}));
""")
        self.assertEqual(result["valid"]["accepted"]["repair_ref"], "STEP-A2")
        for key in ("badCap", "badRung", "badResult", "badStage", "badScore"):
            self.assertIn("error", result[key], key)
        self.assertIsNone(result["narrow"]["accepted"]["repair_ref"])
        self.assertTrue(result["narrow"]["warning"])

    def test_addresses_and_estimate_routing_preserve_precision_without_mastery(self):
        result = run_node(MATRIX_JS + r"""
const exact = t.deriveAtlasAddress('R5', 1, 'CONCEPT');
const unknownDim = t.deriveAtlasAddress('R5', 1, 'UNKNOWN');
const capOnly = t.deriveAtlasAddress('R5', 99, 'SETUP');
const neutral = t.resolveNeedTargetsFor(matrix, null, []);
const estimate = t.resolveNeedTargetsFor(matrix, 100, []);
const gaps = t.resolveNeedTargetsFor(matrix, 100, [
  {capability_ref:'CAP-TEST-A',repair_ref:'STEP-A2',result:'MISSING',error_stage:'CONCEPT',score:20,observed:'concept'},
  {capability_ref:'CAP-TEST-A',repair_ref:'STEP-A2',result:'UNCERTAIN',error_stage:'SETUP',score:50,observed:'setup'},
  {capability_ref:'CAP-TEST-A',repair_ref:'STEP-A2',result:'UNCERTAIN',error_stage:'UNKNOWN',observed:'unclear'}
]);
const parent = t.resolveNeedTargetsFor(matrix, null, [
  {capability_ref:'CAP-TEST-A',result:'MISSING',error_stage:'SETUP',observed:'parent only'}
]);
console.log(JSON.stringify({exact,unknownDim,capOnly,neutral,estimate,gaps,parent}));
""")
        self.assertEqual(result["exact"], "R5.1.0")
        self.assertEqual(result["unknownDim"], "R5.1.99")
        self.assertEqual(result["capOnly"], "R5.99")
        self.assertEqual(result["neutral"]["targets"], [])
        self.assertIsNone(result["neutral"]["primary_target"])
        self.assertEqual(result["estimate"]["primary_target"]["rung"], "R3")
        self.assertNotEqual(result["estimate"]["primary_target"]["rung"], "R4")
        self.assertEqual(
            [row["address"] for row in result["gaps"]["targets"]],
            ["R1.1.0", "R1.1.1", "R1.1.99"],
        )
        self.assertEqual(result["parent"]["primary_target"]["address"], "R1.99")

    def test_plan_level_request_is_schema_valid_without_fabricated_owner_entry(self):
        docs = run_node(MATRIX_JS + r"""
const noEstimate = t.buildAuthoringRequest(
  matrix,
  {cores:['CORE1B','CORE2A'],core2a_purpose:'PRACTICE',core2b_purpose:null},
  null,
  'REQ-1'
);
const withEstimate = t.buildAuthoringRequest(
  matrix,
  {cores:['CORE1B','CORE2B'],core2a_purpose:'PRACTICE',core2b_purpose:'REVISION'},
  80,
  'REQ-2'
);
console.log(JSON.stringify({noEstimate,withEstimate}));
""")
        schema = json.loads(AUTHORING_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(docs["noEstimate"], schema)
        jsonschema.validate(docs["withEstimate"], schema)
        self.assertNotIn("learner", docs["noEstimate"])
        self.assertNotIn("owner_entry", json.dumps(docs))
        self.assertEqual(
            docs["withEstimate"]["learner"]["owner_estimate"]["knowledge_percentage"], 80
        )
        self.assertNotIn("CORE2A", docs["withEstimate"].get("practice", {}))
        self.assertEqual(docs["withEstimate"]["practice"]["CORE2B"]["purpose"], "REVISION")

    def test_measurement_projection_separates_measurement_from_routing_context(self):
        docs = run_node(MATRIX_JS + r"""
const pack = t.buildMeasurementPack(matrix, '2026-09-20T00:00:00Z');
const envelope = t.buildDiagnosticEnvelope(
  matrix,
  [{capability_ref:'CAP-TEST-A',result:'MISSING',error_stage:'CONCEPT',observed:'x'}],
  '2026-09-20T00:00:00Z',
  'DG-1'
);
console.log(JSON.stringify({pack,envelope}));
""")
        target = docs["pack"]["targets"][0]
        self.assertIn("measurement", target)
        self.assertIn("routing_context", target)
        self.assertNotIn("intrinsic_difficulty", target["measurement"])
        self.assertEqual(
            target["measurement"]["misconceptions"][0]["diagnostic_prompt"], "prompt"
        )
        self.assertNotIn("knowledge_percentage", docs["envelope"])
        self.assertNotIn("leaf_progress", docs["envelope"])
        self.assertEqual(
            docs["pack"]["diagnostic_contract"]["error_stage_values"],
            ["CONCEPT", "SETUP", "EXECUTION", "CARELESS", "UNKNOWN"],
        )

    def test_browser_source_does_not_claim_authoritative_planner_execution(self):
        source = JS.read_text(encoding="utf-8")
        self.assertNotIn("Shared request.schema.json Compliant", source)
        self.assertNotIn("Prerequisite Status:</strong> Cleared", source)
        self.assertIn("Shared/tools/plan_request.py --plan", source)


if __name__ == "__main__":
    unittest.main()
