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
    core1a: ["CORE1A", "CONSTRUCTION_VISIBLE", true, false],
    core1b: ["CORE1B", "AWAITING_ATTEMPT", false, false],
    core2a: ["CORE2A", "QUESTION_VISIBLE", false, true],
    core2b: ["CORE2B", "AWAITING_ATTEMPT", false, true],
  };

  for (const [id, [core, stage, reconstructionVisible, questionVisible]] of Object.entries(expected)) {
    const state = deriveCoreLearningState(byId[id]);
    assert.equal(state.contractVersion, CORE_PROJECTION_CONTRACT_VERSION);
    assert.equal(state.core, core);
    assert.equal(state.stage, stage);
    assert.equal(state.reconstructionVisible, reconstructionVisible);
    assert.equal(state.reasoningVisible, false);
    assert.equal(state.questionVisible, questionVisible);
    assert.equal(state.attempted, false);
    assert.equal(state.attemptCount, 0);
    assert.equal(state.supportIndex, 0);
  }
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

test("Core1 fixtures use the frozen nullable application boundary", () => {
  assert.equal(byId.core1a.application, null);
  assert.equal(byId.core1b.application, null);
  assert.doesNotThrow(() => validateCoreProjection(byId.core1a));
  assert.doesNotThrow(() => validateCoreProjection(byId.core1b));
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

test("Core1B keeps the inferential jump and reconstruction absent until commit", () => {
  const projection = byId.core1b;
  const initial = deriveCoreLearningState(projection);
  const before = renderCoreLearningProjection(projection, initial);

  assert.match(before, /Reconstruct the connection before revealing the authored path/);
  assert.match(before, /data-attempt-form/);
  assert.doesNotMatch(before, /A supplied relation follows from the supplied representation and conditions/);
  assert.doesNotMatch(before, /Read the supplied representation/);
  assert.doesNotMatch(before, /data-semantic="reconstruction"/);

  const committed = transitionCoreLearningState(
    projection,
    initial,
    { type: "COMMIT_ATTEMPT" },
  ).state;
  const after = renderCoreLearningProjection(projection, committed);

  assert.equal(committed.attempted, true);
  assert.equal(committed.attemptCount, 1);
  assert.equal(committed.stage, "RECONSTRUCTION_VISIBLE");
  assert.equal(committed.reconstructionVisible, true);
  assert.match(after, /A supplied relation follows from the supplied representation and conditions/);
  assert.match(after, /Read the supplied representation/);
  assert.match(after, /data-semantic="reconstruction"/);
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
    { type: "COMMIT_ATTEMPT" },
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

test("rendering uses supplied projection text for Core1A and Core2A", () => {
  const core1a = renderCoreLearningProjection(byId.core1a);
  assert.match(core1a, /data-core="CORE1A"/);
  assert.match(core1a, /Read the supplied representation/);

  const core2a = renderCoreLearningProjection(byId.core2a);
  assert.match(core2a, /Use the supplied representation to decide the next valid move/);
  assert.match(core2a, /data-stage="QUESTION_VISIBLE"/);
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
