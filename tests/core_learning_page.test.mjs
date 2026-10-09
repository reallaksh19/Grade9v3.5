import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import {
  CORE_LEARNER_EVENTS,
  CORE_PROJECTION_CONTRACT_VERSION,
  CoreLearningPageError,
  deriveCoreLearningState,
  renderCoreLearningProjection,
  transitionCoreLearningState,
  validateCoreProjection,
} from "../Shared/workbench/core-learning-page.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const fixturePath = resolve(here, "fixtures/workbench/core-learning-projections.json");
const fixtures = JSON.parse(await readFile(fixturePath, "utf8")).projections;
const byId = Object.fromEntries(fixtures.map((row) => [row.id, row]));

test("frozen CoreProjection fixtures derive the contract-defined initial states", () => {
  const expected = {
    core1: ["CORE1", "ORIENTATION", false, false],
    core1a: ["CORE1A", "CONSTRUCTION_VISIBLE", true, false],
    core1b: ["CORE1B", "AWAITING_ATTEMPT", false, false],
    core2a: ["CORE2A", "QUESTION_VISIBLE", false, true],
    core2b: ["CORE2B", "AWAITING_ATTEMPT", false, true],
  };

  for (const [id, [core, stage, reconstructionVisible, questionVisible]] of Object.entries(expected)) {
    const state = deriveCoreLearningState(byId[id]);
    assert.equal(state.contractVersion, CORE_PROJECTION_CONTRACT_VERSION);
    assert.equal(state.core, core);
    assert.match(state.webBlueprintRef, /^BP-/);
    assert.equal(state.shellRef, "G9-TABLET-SHELL-V1");
    assert.ok(state.layoutFamily);
    assert.equal(state.stage, stage);
    assert.equal(state.reconstructionVisible, reconstructionVisible);
    assert.equal(state.reasoningVisible, false);
    assert.equal(state.questionVisible, questionVisible);
    assert.equal(state.attempted, false);
    assert.equal(state.attemptCount, 0);
    assert.equal(state.supportIndex, 0);
    assert.equal(state.hintIndex, 0);
    assert.equal(state.solutionVisible, false);
  }
});

test("CoreProjection fails closed without explicit web blueprint delivery", () => {
  const projection = structuredClone(byId.core2a);
  delete projection.delivery;
  assert.throws(
    () => validateCoreProjection(projection),
    (error) => error instanceof CoreLearningPageError && error.code === "CORE_PROJECTION_DELIVERY_REQUIRED",
  );
});

test("CoreProjection rejects a mismatched blueprint id/version ref", () => {
  const projection = structuredClone(byId.core2a);
  projection.delivery.web.blueprint_ref = "BP-WRONG@1.0.0";
  assert.throws(
    () => validateCoreProjection(projection),
    (error) => error instanceof CoreLearningPageError && error.code === "CORE_PROJECTION_WEB_BLUEPRINT_REF_MISMATCH",
  );
});

test("initial state follows supplied presentation policy rather than subject or identifier text", () => {
  const left = structuredClone(byId.core2a);
  const right = structuredClone(byId.core2a);

  left.concept.microtopic_ref = "MIC-ALPHA";
  left.concept.inferential_jump = "Alpha supplied relation.";
  left.application.question_ref = "Q-ALPHA";

  right.concept.microtopic_ref = "MIC-BETA";
  right.concept.inferential_jump = "Beta supplied relation.";
  right.application.question_ref = "Q-BETA";

  const leftState = deriveCoreLearningState(left);
  const rightState = deriveCoreLearningState(right);
  assert.equal(leftState.stage, "QUESTION_VISIBLE");
  assert.equal(rightState.stage, "QUESTION_VISIBLE");
  assert.equal(leftState.reconstructionVisible, rightState.reconstructionVisible);
  assert.equal(leftState.reasoningVisible, rightState.reasoningVisible);
});

test("Core1-family fixtures keep orientation and concept products outside application practice", () => {
  assert.equal(byId.core1.application, null);
  assert.equal(byId.core1.concept, null);
  assert.equal(byId.core1a.application, null);
  assert.equal(byId.core1b.application, null);
  assert.doesNotThrow(() => validateCoreProjection(byId.core1));
  assert.doesNotThrow(() => validateCoreProjection(byId.core1a));
  assert.doesNotThrow(() => validateCoreProjection(byId.core1b));
});

test("Core1 renders compiler-owned orientation blocks without inventing an attempt", () => {
  const projection = byId.core1;
  const state = deriveCoreLearningState(projection);
  const rendered = renderCoreLearningProjection(projection, state);

  assert.equal(state.stage, "ORIENTATION");
  assert.match(rendered, /Fixture concept map/);
  assert.match(rendered, /Read the declared sign convention/);
  assert.match(rendered, /Velocity is constant/);
  assert.match(rendered, /labelled displacement from the declared origin/i);
  assert.doesNotMatch(rendered, /data-attempt-form/);
  assert.doesNotMatch(rendered, /Completed construction/);
});

test("Core1A learner surface preserves the completed construction and independent closure", () => {
  const rendered = renderCoreLearningProjection(byId.core1a);
  assert.match(rendered, /Completed construction/);
  assert.match(rendered, /Read the supplied representation/);
  assert.match(rendered, /The representation is part of the projection input/);
  assert.match(rendered, /Representation bridge/);
  assert.match(rendered, /marked state/);
  assert.match(rendered, /Worked conceptual anchor/);
  assert.match(rendered, /Use the supplied representation to explain the relation/);
  assert.match(rendered, /Independent closure/);
  assert.match(rendered, /Reverse the relation and recover the supplied state/);
});

test("projection validation fails closed on unsupported, incomplete, or dangling envelopes", () => {
  const badVersion = structuredClone(byId.core1a);
  badVersion.contract_version = "2.0";
  assert.throws(
    () => validateCoreProjection(badVersion),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_PROJECTION_VERSION_UNSUPPORTED",
  );

  const badCore = structuredClone(byId.core1a);
  badCore.core = "CORE3";
  assert.throws(
    () => validateCoreProjection(badCore),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_PROJECTION_CORE_UNSUPPORTED",
  );

  const missingPolicy = structuredClone(byId.core1a);
  delete missingPolicy.presentation.attempt_before_reveal;
  assert.throws(
    () => validateCoreProjection(missingPolicy),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_PROJECTION_ATTEMPT_POLICY_REQUIRED",
  );

  const danglingCrux = structuredClone(byId.core2a);
  danglingCrux.application.crux_move_ref = "R-MISSING";
  assert.throws(
    () => validateCoreProjection(danglingCrux),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_PROJECTION_CRUX_MOVE_REF_UNKNOWN",
  );

  const danglingScaffold = structuredClone(byId.core2a);
  danglingScaffold.application.scaffolds[0].supports_move_ref = "R-MISSING";
  assert.throws(
    () => validateCoreProjection(danglingScaffold),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_PROJECTION_SCAFFOLD_MOVE_REF_UNKNOWN",
  );
});

test("Core1B keeps canonical truth and authored reconstruction closure behind a genuine attempt", () => {
  const projection = byId.core1b;
  const initial = deriveCoreLearningState(projection);
  const before = renderCoreLearningProjection(projection, initial);

  assert.match(before, /Which supplied condition controls the connection/);
  assert.match(before, /A condition choice plus a reason/);
  assert.match(before, /data-attempt-form/);
  assert.doesNotMatch(before, /A supplied relation follows from the supplied representation and conditions/);
  assert.doesNotMatch(before, /What does the marked state represent/);
  assert.doesNotMatch(before, /Defensible answer/);
  assert.doesNotMatch(before, /Boundary test/);
  assert.doesNotMatch(before, /data-semantic="reconstruction"/);

  assert.throws(
    () => transitionCoreLearningState(
      projection,
      initial,
      { type: "COMMIT_ATTEMPT", response: "   " },
    ),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED",
  );

  const committed = transitionCoreLearningState(
    projection,
    initial,
    { type: "COMMIT_ATTEMPT", response: "The stated condition controls it." },
  ).state;
  const after = renderCoreLearningProjection(projection, committed);

  assert.equal(committed.attempted, true);
  assert.equal(committed.attemptCount, 1);
  assert.equal(committed.stage, "RECONSTRUCTION_VISIBLE");
  assert.equal(committed.reconstructionVisible, true);
  assert.match(after, /A supplied relation follows from the supplied representation and conditions/);
  assert.match(after, /What does the marked state represent/);
  assert.match(after, /Which condition connects that state to the relation/);
  assert.match(after, /Defensible answer/);
  assert.match(after, /The relation is valid without checking the condition/);
  assert.match(after, /Model response/);
  assert.match(after, /Boundary test/);
  assert.doesNotMatch(after, /Read the supplied representation.*Connect the supplied condition/s);
  assert.match(after, /data-semantic="reconstruction"/);
});

test("attempt-first products reject blank responses before reveal", () => {
  const projection = byId.core2b;
  const initial = deriveCoreLearningState(projection);
  assert.throws(
    () => transitionCoreLearningState(
      projection,
      initial,
      { type: "COMMIT_ATTEMPT", response: "   " },
    ),
    (error) => error instanceof CoreLearningPageError
      && error.code === "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED",
  );
  assert.equal(initial.reasoningVisible, false);
  assert.equal(initial.solutionVisible, false);
});

test("source hints are a separate ordered channel from pedagogical scaffolds", () => {
  const projection = structuredClone(byId.core2b);
  projection.application.hints = [
    { text: "Inspect the changed givens.", reveals: "CONCEPT" },
    { text: "Choose the controlling model.", reveals: "METHOD" },
  ];
  projection.presentation.pre_attempt_hint_limit = 1;
  projection.presentation.post_attempt_hint_limit = 1;

  const initial = deriveCoreLearningState(projection);
  const first = transitionCoreLearningState(projection, initial, { type: "REQUEST_HINT" });
  assert.equal(first.changed, true);
  assert.equal(first.state.hintIndex, 1);
  const before = renderCoreLearningProjection(projection, first.state);
  assert.match(before, /Source\/question hints/);
  assert.match(before, /Inspect the changed givens/);
  assert.doesNotMatch(before, /Choose the controlling model/);
  assert.match(before, /Support/);

  const blocked = transitionCoreLearningState(projection, first.state, { type: "REQUEST_HINT" });
  assert.equal(blocked.changed, false);
  assert.equal(blocked.reason, "HINT_PROTECTED_AT_THIS_STAGE");

  const attempted = transitionCoreLearningState(
    projection,
    blocked.state,
    { type: "COMMIT_ATTEMPT", response: "I choose based on the changed condition." },
  ).state;
  const stillBlocked = transitionCoreLearningState(projection, attempted, { type: "REQUEST_HINT" });
  assert.equal(stillBlocked.changed, false);
  assert.equal(stillBlocked.reason, "HINT_PROTECTED_AT_THIS_STAGE");
});

test("Core2A support advances supplied scaffolds without changing question identity", () => {
  const projection = byId.core2a;
  const initial = deriveCoreLearningState(projection);

  const first = transitionCoreLearningState(
    projection,
    initial,
    { type: "REQUEST_SUPPORT" },
  );
  assert.equal(first.changed, true);
  assert.equal(first.state.supportIndex, 1);
  assert.equal(first.state.currentVisualRef, "REP-FIXTURE-1");
  assert.equal(first.state.currentVisualStageRef, "V2");
  assert.equal(first.state.questionVisible, true);
  assert.equal(first.state.reasoningVisible, false);

  const second = transitionCoreLearningState(
    projection,
    first.state,
    { type: "REQUEST_SUPPORT" },
  );
  assert.equal(second.changed, true);
  assert.equal(second.state.supportIndex, 2);
  assert.equal(second.state.currentVisualStageRef, "V3");

  const rendered = renderCoreLearningProjection(projection, second.state);
  assert.match(rendered, /Focus on the supplied state before choosing the controlling condition/);
  assert.match(rendered, /Connect the controlling condition to the authored decision before executing/);
  assert.match(rendered, /Use the supplied representation to decide the next valid move/);
  assert.doesNotMatch(rendered, /Reasoning route/);
});

test("reasoning route appears after commit and marks the supplied crux without color-only meaning", () => {
  const projection = byId.core2a;
  const committed = transitionCoreLearningState(
    projection,
    deriveCoreLearningState(projection),
    { type: "COMMIT_ATTEMPT" },
  ).state;
  const rendered = renderCoreLearningProjection(projection, committed);

  assert.equal(committed.stage, "REASONING_VISIBLE");
  assert.equal(committed.reasoningVisible, true);
  assert.match(rendered, /Reasoning route/);
  assert.match(rendered, /data-move-id="R2"/);
  assert.match(rendered, /data-crux="true"/);
  assert.match(rendered, /Key decision/);
  assert.match(rendered, /Choose the condition that controls the next move/);
  assert.match(rendered, /Independent check/);
  assert.match(rendered, /Check against the supplied condition/);
});

test("question parts and source identity survive projection and display without leaking a solution", () => {
  const projection = structuredClone(byId.core2b);
  Object.assign(projection.application, {
    source_refs: ["SRC-EXAMPLE"],
    origin: "ADAPTED",
    original_number: "7(a)",
    subparts: ["Explain the choice.", "State a limit."],
    options: ["Model A", "Model B"],
    conditions: ["Use the stated reference frame."],
    figure_refs: ["FIG-EXAMPLE"],
    figures: [{
      figure_ref: "FIG-EXAMPLE",
      kind: "DIAGRAM",
      caption: "A semantic figure caption required to interpret the question.",
      purpose: "Carry the demand-bearing geometry.",
      read_order: ["Read the labelled condition.", "Compare the two marked states."],
      accessibility: ["Do not rely on colour alone."],
    }],
  });
  const validated = validateCoreProjection(projection);
  assert.deepEqual(validated.application.source_refs, ["SRC-EXAMPLE"]);
  assert.deepEqual(validated.application.figure_refs, ["FIG-EXAMPLE"]);
  const before = renderCoreLearningProjection(projection);
  assert.match(before, /Explain the choice/);
  assert.match(before, /Model B/);
  assert.match(before, /Use the stated reference frame/);
  assert.match(before, /SRC-EXAMPLE/);
  assert.match(before, /Question figure semantics/);
  assert.match(before, /semantic figure caption required to interpret the question/);
  assert.doesNotMatch(before, /Independent check/);
  assert.doesNotMatch(before, /Select the controlling model or condition/);
});

test("Core2B support stops at a protected move before commit and unlocks only after commit", () => {
  const projection = byId.core2b;
  const initial = deriveCoreLearningState(projection);

  const safe = transitionCoreLearningState(
    projection,
    initial,
    { type: "REQUEST_SUPPORT" },
  );
  assert.equal(safe.changed, true);
  assert.equal(safe.state.supportIndex, 1);
  assert.equal(safe.state.currentVisualStageRef, "V2");

  const blocked = transitionCoreLearningState(
    projection,
    safe.state,
    { type: "REQUEST_SUPPORT" },
  );
  assert.equal(blocked.changed, false);
  assert.equal(blocked.reason, "SUPPORT_PROTECTED_PREATTEMPT");
  assert.equal(blocked.state.supportIndex, 1);
  assert.equal(blocked.state.currentVisualStageRef, "V2");

  const before = renderCoreLearningProjection(projection, blocked.state);
  assert.match(before, /Compare the changed state with the familiar state before deciding/);
  assert.doesNotMatch(before, /Use the changed condition to choose the controlling model or condition/);
  assert.doesNotMatch(before, /Select the controlling model or condition/);
  assert.doesNotMatch(before, /Reasoning route/);

  const committed = transitionCoreLearningState(
    projection,
    blocked.state,
    { type: "COMMIT_ATTEMPT", response: "I select the model from the changed condition." },
  ).state;
  const afterCommit = renderCoreLearningProjection(projection, committed);
  assert.match(afterCommit, /Reasoning route/);
  assert.match(afterCommit, /Select the controlling model or condition/);
  assert.match(afterCommit, /Key decision/);

  const unlocked = transitionCoreLearningState(
    projection,
    committed,
    { type: "REQUEST_SUPPORT" },
  );
  assert.equal(unlocked.changed, true);
  assert.equal(unlocked.state.supportIndex, 2);
  assert.equal(unlocked.state.currentVisualStageRef, "V3");
  assert.match(
    renderCoreLearningProjection(projection, unlocked.state),
    /Use the changed condition to choose the controlling model or condition/,
  );
});

test("post-attempt closure renders solution rubric and repair without changing the protected attempt boundary", () => {
  const projection = structuredClone(byId.core2b);
  projection.application.solution = {
    summary: "Use the changed condition to select the bounded model.",
    steps: ["Represent the changed state.", "Choose the valid model."],
    rubric: [
      { criterion: "Names the model condition.", evidence_of: "Justifies the changed decision." },
    ],
  };
  projection.application.repair = {
    step_ref: "STEP-REPAIR-1",
    microtopic_ref: "MIC-FIXTURE-SHARED-IDEA",
    action: "Review the representation-to-condition connection.",
    why_valid: "The repair targets the prerequisite decision path.",
  };

  const before = renderCoreLearningProjection(projection);
  assert.doesNotMatch(before, /Use the changed condition to select the bounded model/);
  assert.doesNotMatch(before, /Repair route/);

  const afterState = transitionCoreLearningState(
    projection,
    deriveCoreLearningState(projection),
    { type: "COMMIT_ATTEMPT", response: "My bounded-model choice." },
  ).state;
  const after = renderCoreLearningProjection(projection, afterState);
  assert.match(after, /Solution/);
  assert.match(after, /Use the changed condition to select the bounded model/);
  assert.match(after, /Rubric/);
  assert.match(after, /Repair route/);
  assert.match(after, /STEP-REPAIR-1/);
});

test("Core2 source custody displays preserved identity hints and answer without inventing practice semantics", () => {
  const projection = {
    contract_version: "1.1",
    core: "CORE2",
    delivery: {"web":{"blueprint_ref":"BP-CORE2-SOURCE-QUESTION@1.0.0","blueprint_id":"BP-CORE2-SOURCE-QUESTION","blueprint_version":"1.0.0","shell_ref":"G9-TABLET-SHELL-V1","layout_family":"QUESTION_READER","required_slots":["identity","attempt","solution"],"slot_order":["identity","attempt","support","solution"],"interaction_policy":{"attempt_before_reveal":"FROM_PROJECTION","progressive_support":true,"solution_policy":"LEARNER_OPENABLE"},"representation_policy":{"preferred_mount_modes":["PORTABLE_SCENE","COMPONENT","STATIC_FIGURE"],"legacy_iframe":"MIGRATION_ONLY"},"responsive_policy":{"compact":"SINGLE_PANE","medium":"STACKED_SUPPORT","expanded":"STAGE_SUPPORT","primary_fraction":0.68,"support_fraction":0.32},"touch_policy":{"minimum_target_css_px":48,"minimum_control_gap_css_px":8},"packaging_modes":["PUBLIC","PAGES","OFFLINE_DIRECTORY","SINGLE_FILE","EMBED"],"forbidden":["PAGE_LOCAL_ACADEMIC_TRUTH","HOVER_ONLY_ESSENTIAL_INFORMATION","AUTHORED_SCAFFOLD_PRESENTED_AS_SOURCE_HINT"]}},
    concept: null,
    application: {
      question_ref: "Q-SOURCE-1",
      family_ref: "F-SOURCE",
      stem: "Preserved source question.",
      source_refs: ["SRC-SOURCE-1"],
      origin: "ORIGINAL",
      original_number: "12",
      subparts: [],
      options: ["A", "B"],
      conditions: ["Use the preserved condition."],
      figure_refs: [],
      figures: [],
      reasoning_route: [],
      crux_move_ref: null,
      hints: [{ text: "Preserved source hint.", reveals: "CONCEPT" }],
      scaffolds: [],
      transfer: null,
      check: "Check the source key.",
      solution: {
        summary: "A",
        steps: ["Preserved source working."],
        rubric: [{ criterion: "Select A.", evidence_of: "Matches the source key." }],
      },
      repair: null,
    },
    presentation: {
      attempt_before_reveal: false,
      show_full_construction: false,
      show_solution_initially: true,
      initial_visual_ref: null,
      initial_visual_stage_ref: null,
      protected_move_refs: [],
      pre_attempt_scaffold_limit: 0,
      pre_attempt_hint_limit: 1,
      post_attempt_hint_limit: 1,
    },
  };
  const state = deriveCoreLearningState(projection);
  assert.equal(state.stage, "SOURCE_CUSTODY_VISIBLE");
  assert.equal(state.solutionVisible, true);
  const rendered = renderCoreLearningProjection(projection, state);
  assert.match(rendered, /Source question/);
  assert.match(rendered, /SRC-SOURCE-1/);
  assert.match(rendered, /Question 12/);
  assert.match(rendered, /Source answer/);
  assert.match(rendered, /Preserved source working/);
  assert.doesNotMatch(rendered, /data-action="support"/);

  const hinted = transitionCoreLearningState(projection, state, { type: "REQUEST_HINT" }).state;
  assert.match(renderCoreLearningProjection(projection, hinted), /Preserved source hint/);
});

test("rendering uses supplied projection text for Core1A and Core2A", () => {
  const core1a = renderCoreLearningProjection(byId.core1a);
  assert.match(core1a, /data-core="CORE1A"/);
  assert.match(core1a, /Read the supplied representation/);

  const core2a = renderCoreLearningProjection(byId.core2a);
  assert.match(core2a, /Use the supplied representation to decide the next valid move/);
  assert.match(core2a, /data-stage="QUESTION_VISIBLE"/);
});

test("blueprint slot order, responsive policy, and touch policy drive rendered anatomy", () => {
  const rendered = renderCoreLearningProjection(byId.core2a);
  const order = ["identity", "attempt", "support", "reasoning"].map(
    (slot) => rendered.indexOf(`data-blueprint-slot="${slot}"`),
  );
  assert.ok(order.every((index) => index >= 0));
  assert.deepEqual([...order].sort((a, b) => a - b), order);
  assert.match(rendered, /data-expanded-layout="STAGE_SUPPORT"/);
  assert.match(rendered, /--g9-primary:0\.68fr/);
  assert.match(rendered, /--g9-support:0\.32fr/);
  assert.match(rendered, /--g9-min-target:48px/);
  assert.match(rendered, /grid-template-columns:minmax\(0,var\(--g9-primary\)\) minmax\(0,var\(--g9-support\)\)/);
});

test("question role renders stem even when a compiled projection also carries concept metadata", () => {
  for (const core of ["core2a", "core2b"]) {
    const projection = structuredClone(byId[core]);
    const sentinel = "PROTECTED_CONCEPT_INFERENCE_NEVER_PREATTEMPT";
    projection.concept.inferential_jump = sentinel;
    const html = renderCoreLearningProjection(projection);
    assert.ok(html.includes(projection.application.stem), "Actual Core2 question stem must be visible");
    assert.doesNotMatch(html, /PROTECTED_CONCEPT_INFERENCE_NEVER_PREATTEMPT/,
      "Concept inferential jump cannot substitute for a protected question stem");
  }
});

test("solution control is absent for a question with no authored solution body", () => {
  const page = renderCoreLearningProjection(byId.core2a);
  assert.doesNotMatch(page, /data-action="solution"/);
});

test("Core2A learner-openable solution is an explicit reveal rather than commit side effect", () => {
  const projection = structuredClone(byId.core2a);
  // The generic fixture has no solution. An openable solution button is only
  // legitimate when canonical solution content is actually supplied.
  projection.application.solution = {
    summary: "The controlling model is established by the supplied condition.",
    steps: ["Reconstruct the valid move from the given representation."],
    rubric: [],
  };
  const initial = deriveCoreLearningState(projection);
  const before = renderCoreLearningProjection(projection, initial);
  assert.match(before, /data-action="solution"/);
  assert.match(before, /Open complete solution/);

  const committed = transitionCoreLearningState(
    projection,
    initial,
    { type: "COMMIT_ATTEMPT", response: "My attempt." },
  ).state;
  assert.equal(committed.reasoningVisible, true);
  assert.equal(committed.solutionVisible, false);
  assert.match(renderCoreLearningProjection(projection, committed), /Reasoning route/);
  assert.doesNotMatch(renderCoreLearningProjection(projection, committed), /Solution<\/h3>/);

  const revealed = transitionCoreLearningState(
    projection,
    committed,
    { type: "REVEAL_SOLUTION" },
  ).state;
  assert.equal(revealed.solutionVisible, true);
  assert.match(renderCoreLearningProjection(projection, revealed), /Solution<\/h3>/);
});

test("Core2A identity renders canonical family and exposure closure", () => {
  const projection = structuredClone(byId.core2a);
  projection.application.exposure = [
    { core: "CORE2A", role: "FAMILIAR_SUPPORTED_APPLICATION" },
  ];
  const rendered = renderCoreLearningProjection(projection);
  assert.match(rendered, new RegExp(projection.application.family_ref));
  assert.match(rendered, /CORE2A · FAMILIAR_SUPPORTED_APPLICATION/);
});

test("generic learner-shell source contains no subject-specific or learner-classification routing vocabulary", async () => {
  const source = await readFile(resolve(here, "../Shared/workbench/core-learning-page.mjs"), "utf8");
  for (const forbidden of [
    /Physics\//i,
    /projectile/i,
    /friction/i,
    /motion[- ]?2d/i,
    /mastery/i,
    /proficien/i,
    /knowledge percentage/i,
  ]) {
    assert.doesNotMatch(source, forbidden);
  }
});

test("custom element emits only page-level semantic events and keeps state instance-local", async () => {
  const oldHTMLElement = globalThis.HTMLElement;
  const oldCustomElements = globalThis.customElements;
  const oldCustomEvent = globalThis.CustomEvent;
  const registry = new Map();

  globalThis.HTMLElement = class {
    constructor() {
      this.events = [];
    }
    attachShadow() {
      const root = { innerHTML: "" };
      this.shadowRoot = root;
      return root;
    }
    dispatchEvent(event) {
      this.events.push(event);
      return true;
    }
  };
  globalThis.CustomEvent = class {
    constructor(type, options = {}) {
      this.type = type;
      this.detail = options.detail;
      this.bubbles = options.bubbles;
      this.composed = options.composed;
    }
  };
  globalThis.customElements = {
    get(name) { return registry.get(name); },
    define(name, ctor) { registry.set(name, ctor); },
  };

  try {
    const module = await import(`../Shared/workbench/core-learning-page.mjs?custom-element=${Date.now()}`);
    assert.equal(registry.get("core-learning-page"), module.CoreLearningPage);

    const first = new module.CoreLearningPage();
    const second = new module.CoreLearningPage();
    first.projection = byId.core2b;
    second.projection = byId.core2a;

    first.requestSupport();
    first.requestSupport();
    first.commitAttempt("learner decision");
    first.requestSupport();
    first.completeActivity();

    assert.equal(first.state.stage, "COMPLETE");
    assert.equal(first.state.supportIndex, 2);
    assert.equal(second.state.stage, "QUESTION_VISIBLE");
    assert.equal(second.state.supportIndex, 0);
    assert.notEqual(first.shadowRoot, second.shadowRoot);

    assert.deepEqual(
      first.events.map((event) => event.type),
      [
        CORE_LEARNER_EVENTS.SUPPORT_REQUESTED,
        CORE_LEARNER_EVENTS.REVEAL_CHANGED,
        CORE_LEARNER_EVENTS.SUPPORT_REQUESTED,
        CORE_LEARNER_EVENTS.ATTEMPT_COMMITTED,
        CORE_LEARNER_EVENTS.REVEAL_CHANGED,
        CORE_LEARNER_EVENTS.SUPPORT_REQUESTED,
        CORE_LEARNER_EVENTS.REVEAL_CHANGED,
        CORE_LEARNER_EVENTS.ACTIVITY_COMPLETED,
      ],
    );
    assert.equal(first.events[2].detail.revealed, false);
    assert.equal(first.events[2].detail.reason, "SUPPORT_PROTECTED_PREATTEMPT");
    assert.equal(first.events[3].detail.response, "learner decision");
    assert.equal(first.events[4].detail.kind, "reasoning");
    assert.equal(first.events[6].detail.kind, "support");
    assert.doesNotMatch(JSON.stringify(first.events), /mastery|proficien|knowledge percentage|correct|score/i);

    const returned = first.projection;
    returned.core = "CORE1A";
    assert.equal(first.projection.core, "CORE2B");
  } finally {
    if (oldHTMLElement === undefined) delete globalThis.HTMLElement;
    else globalThis.HTMLElement = oldHTMLElement;
    if (oldCustomElements === undefined) delete globalThis.customElements;
    else globalThis.customElements = oldCustomElements;
    if (oldCustomEvent === undefined) delete globalThis.CustomEvent;
    else globalThis.CustomEvent = oldCustomEvent;
  }
});
