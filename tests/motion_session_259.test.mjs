import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import vm from "node:vm";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const sessionModule = await import(pathToFileURL(resolve(repo, "public/physics/motion-2d/session/session.mjs")).href);
const traceModule = await import(pathToFileURL(resolve(repo, "public/physics/motion-2d/session/session-trace.mjs")).href);

async function generatedGlobal(relative, key) {
  const source = await readFile(resolve(repo, relative), "utf8");
  const sandbox = { window: {} };
  vm.runInNewContext(source, sandbox, { filename: relative });
  return sandbox.window[key];
}

function state(overrides = {}) {
  return {
    stage: "ORIENT", unlocked_stage: 1,
    core1b_attempted: false, core1b_revealed: false, core1b_attempts: 0,
    support_requests: 0,
    visual_ready: false, visual_accept_count: 0, visual_reject_count: 0,
    core2b_attempted: false, core2b_disclosed: false, core2b_attempts: 0,
    completed: false,
    ...overrides,
  };
}

function event(sequence, runId, prior, result, extra = {}) {
  return {
    trace_version: traceModule.TRACE_VERSION,
    run_id: runId,
    parent_run_id: null,
    sequence,
    logical_time: sequence,
    host_mode: "repository",
    stage: result.stage,
    event_type: extra.event_type || "OBSERVE",
    identity: {
      matrix_id: "MATRIX-PHY-KIN-2D-MOTION",
      rung: "R1",
      microtopic_ref: "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
    },
    prior_state: prior,
    requested_transition: extra.requested_transition || null,
    resulting_state: result,
    outcome: extra.outcome || "OBSERVE",
    reason_code: extra.reason_code || "TEST",
    invariant_checks: traceModule.invariantChecks(result),
    producer: extra.producer || "session shell",
    correlation: null,
  };
}

test("Issue #259 resolves the exact Motion R1 production chain from generated data", async () => {
  const atlas = await generatedGlobal("public/data/data.js", "GRADE9V3");
  const core = await generatedGlobal("public/core-learning/data.js", "GRADE9V3_CORE");
  const identity = sessionModule.resolveMotionSessionIdentity(atlas, core);

  assert.deepEqual(identity, {
    matrix_id: "MATRIX-PHY-KIN-2D-MOTION",
    rung: "R1",
    microtopic_ref: "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
    capability_ref: "CAP-KIN-2D-INDEPENDENT-COMPONENTS",
    core1b_projection_ref: "physics:mic-phy-kin-2d-independent-components:core1b",
    representation_ref: "REP-KIN-2D-SHARED-CLOCK",
    activity_ref: "ACT-KIN-2D-SHARED-CLOCK",
    portable_package_ref: "portable-motion-shared-clock",
    core2b_projection_ref: "physics:q-phy-kin-2d-2b-projectile-validity-04:core2b",
    core2b_source_ref: "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04",
    atlas_contract_version: "2.0",
  });
});

test("Issue #259 identity resolution fails closed instead of substituting another case", async () => {
  const atlas = await generatedGlobal("public/data/data.js", "GRADE9V3");
  const core = await generatedGlobal("public/core-learning/data.js", "GRADE9V3_CORE");
  assert.throws(
    () => sessionModule.resolveMotionSessionIdentity(atlas, core, {
      matrixId: "MATRIX-PHY-UNKNOWN-SESSION-CASE",
      rung: "R1",
      transferProjectionId: "physics:q-phy-kin-2d-2b-projectile-validity-04:core2b",
    }),
    (error) => error.code === "SESSION_ATLAS_SELECTION_UNAVAILABLE",
  );
});

test("Issue #259 trace replay reconstructs state without rerunning academic logic", () => {
  const s0 = state();
  const s1 = state({ stage: "CORE1B" });
  const s2 = state({ stage: "CORE1B", core1b_attempted: true, core1b_revealed: true, core1b_attempts: 1, unlocked_stage: 2 });
  const s3 = state({ stage: "VISUAL", core1b_attempted: true, core1b_revealed: true, core1b_attempts: 1, unlocked_stage: 2 });
  const s4 = state({
    stage: "CORE2B", core1b_attempted: true, core1b_revealed: true, core1b_attempts: 1,
    visual_ready: true, visual_accept_count: 1, visual_reject_count: 1, unlocked_stage: 3,
  });
  const s5 = state({
    stage: "SUMMARY", core1b_attempted: true, core1b_revealed: true, core1b_attempts: 1,
    visual_ready: true, visual_accept_count: 1, visual_reject_count: 1,
    core2b_attempted: true, core2b_disclosed: true, core2b_attempts: 1, unlocked_stage: 4, completed: true,
  });

  const events = [
    event(1, "run-0001", s0, s0, { event_type: "SESSION_START" }),
    event(2, "run-0001", s0, s1, { event_type: "STAGE_ENTERED", requested_transition: { to_stage: "CORE1B" } }),
    event(3, "run-0001", s1, s2, { event_type: "REVEAL_GRANTED" }),
    event(4, "run-0001", s2, s3, { event_type: "STAGE_ENTERED", requested_transition: { to_stage: "VISUAL" } }),
    event(5, "run-0001", s3, s4, { event_type: "STAGE_ENTERED", requested_transition: { to_stage: "CORE2B" } }),
    event(6, "run-0001", s4, s5, { event_type: "COMPLETION_RECORDED" }),
  ];
  const replay = traceModule.replayMotionSessionTrace(events);
  assert.equal(replay.ok, true);
  assert.equal(replay.code, "TRACE_REPLAY_OK");
  assert.equal(replay.final_state.completed, true);
  assert.equal(replay.diagnostic_summary.visual_actions.accepted, 1);
  assert.equal(replay.diagnostic_summary.visual_actions.rejected, 1);
  assert.match(replay.diagnostic_summary.statement, /does not claim mastery or readiness/i);
});

test("Issue #259 trace replay names the first causal divergence", () => {
  const s0 = state();
  const s1 = state({ stage: "CORE1B" });
  const base = event(1, "run-0001", s0, s0, { event_type: "SESSION_START" });

  let replay = traceModule.replayMotionSessionTrace([
    base,
    event(3, "run-0001", s0, s1, { event_type: "STAGE_ENTERED", requested_transition: { to_stage: "CORE1B" } }),
  ]);
  assert.equal(replay.code, "TRACE_SEQUENCE_GAP");
  assert.equal(replay.first_divergent_sequence, 3);

  replay = traceModule.replayMotionSessionTrace([base, { ...base }]);
  assert.equal(replay.code, "TRACE_SEQUENCE_DUPLICATE");

  replay = traceModule.replayMotionSessionTrace([
    base,
    event(2, "run-0001", s1, s1, { event_type: "OBSERVE" }),
  ]);
  assert.equal(replay.code, "TRACE_PRIOR_STATE_MISMATCH");

  const locked = state({ stage: "SUMMARY", unlocked_stage: 1 });
  replay = traceModule.replayMotionSessionTrace([
    event(1, "run-0001", s0, locked, { event_type: "STAGE_ENTERED", requested_transition: { to_stage: "SUMMARY" } }),
  ]);
  assert.equal(replay.code, "TRACE_STATE_INVALID");
});

test("Issue #259 diagnostic implementation contains no mastery state or analytics transport", async () => {
  const controller = await readFile(resolve(repo, "public/physics/motion-2d/session/session.mjs"), "utf8");
  const page = await readFile(resolve(repo, "public/physics/motion-2d/session/index.html"), "utf8");
  assert.doesNotMatch(controller, /\bfetch\s*\(/);
  assert.doesNotMatch(controller, /XMLHttpRequest|sendBeacon|WebSocket/);
  assert.doesNotMatch(controller, /state\.mastery|mastery\s*:/);
  assert.match(page, /does not store learner response text/i);
  assert.match(page, /does not claim mastery/i);
});
