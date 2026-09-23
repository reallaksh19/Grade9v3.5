export const CORE_LEARNING_PAGE_TAG = "core-learning-page";
export const CORE_PROJECTION_CONTRACT_VERSION = "1.0";

const CORE_MODES = new Set(["CORE1A", "CORE1B", "CORE2A", "CORE2B"]);
const SUPPORT_KINDS = new Set(["REPRESENT", "CONNECT", "EXECUTE"]);
const REVEAL_KINDS = new Set(["CONCEPT", "METHOD", "ANSWER"]);
const clone = (value) => value == null ? value : JSON.parse(JSON.stringify(value));

export const CORE_LEARNER_EVENTS = Object.freeze({
  ATTEMPT_COMMITTED: "attempt_committed",
  SUPPORT_REQUESTED: "support_requested",
  REVEAL_CHANGED: "reveal_changed",
  REPRESENTATION_MANIPULATED: "representation_manipulated",
  ACTIVITY_COMPLETED: "activity_completed",
});

export class CoreLearningPageError extends Error {
  constructor(code, detail = "") {
    super(detail ? `${code}: ${detail}` : code);
    this.name = "CoreLearningPageError";
    this.code = code;
    this.detail = detail;
  }
}

function requireCondition(condition, code, detail = "") {
  if (!condition) throw new CoreLearningPageError(code, detail);
}

function requireObject(value, code, detail = "") {
  requireCondition(value && typeof value === "object" && !Array.isArray(value), code, detail);
  return value;
}

function requireString(value, code, detail = "") {
  requireCondition(typeof value === "string" && value.trim().length > 0, code, detail);
  return value;
}

function optionalArray(value, code, detail = "") {
  if (value == null) return [];
  requireCondition(Array.isArray(value), code, detail);
  return value;
}

function optionalStringArray(value, code) {
  const items = optionalArray(value, code);
  for (const item of items) requireString(item, code);
  return items;
}

function validateReasoningRoute(projection) {
  const application = projection.application;
  const route = application?.reasoning_route ?? [];
  const moveIds = new Set();
  for (const move of route) {
    requireObject(move, "CORE_PROJECTION_REASONING_MOVE_INVALID");
    const id = requireString(move.id, "CORE_PROJECTION_REASONING_MOVE_ID_REQUIRED");
    requireCondition(!moveIds.has(id), "CORE_PROJECTION_REASONING_MOVE_ID_DUPLICATE", id);
    moveIds.add(id);
    requireString(move.kind, "CORE_PROJECTION_REASONING_MOVE_KIND_REQUIRED", id);
    requireString(move.action, "CORE_PROJECTION_REASONING_MOVE_ACTION_REQUIRED", id);
  }

  const crux = application?.crux_move_ref;
  if (crux != null) {
    requireString(crux, "CORE_PROJECTION_CRUX_MOVE_REF_INVALID");
    requireCondition(moveIds.has(crux), "CORE_PROJECTION_CRUX_MOVE_REF_UNKNOWN", crux);
  }

  for (const ref of projection.presentation.protected_move_refs) {
    requireString(ref, "CORE_PROJECTION_PROTECTED_MOVE_REF_INVALID");
    requireCondition(moveIds.has(ref), "CORE_PROJECTION_PROTECTED_MOVE_REF_UNKNOWN", ref);
  }

  for (const scaffold of application?.scaffolds ?? []) {
    requireObject(scaffold, "CORE_PROJECTION_SCAFFOLD_INVALID");
    requireString(scaffold.text, "CORE_PROJECTION_SCAFFOLD_TEXT_REQUIRED");
    requireCondition(
      SUPPORT_KINDS.has(scaffold.support_kind),
      "CORE_PROJECTION_SCAFFOLD_KIND_INVALID",
      String(scaffold.support_kind),
    );
    requireCondition(
      REVEAL_KINDS.has(scaffold.reveals),
      "CORE_PROJECTION_SCAFFOLD_REVEAL_INVALID",
      String(scaffold.reveals),
    );
    const moveRef = requireString(
      scaffold.supports_move_ref,
      "CORE_PROJECTION_SCAFFOLD_MOVE_REF_REQUIRED",
    );
    requireCondition(moveIds.has(moveRef), "CORE_PROJECTION_SCAFFOLD_MOVE_REF_UNKNOWN", moveRef);
    const hasVisualRef = scaffold.visual_ref != null;
    const hasVisualStage = scaffold.visual_stage_ref != null;
    requireCondition(
      hasVisualRef === hasVisualStage,
      "CORE_PROJECTION_SCAFFOLD_VISUAL_BINDING_INCOMPLETE",
      moveRef,
    );
    if (hasVisualRef) {
      requireString(scaffold.visual_ref, "CORE_PROJECTION_SCAFFOLD_VISUAL_REF_INVALID", moveRef);
      requireString(
        scaffold.visual_stage_ref,
        "CORE_PROJECTION_SCAFFOLD_VISUAL_STAGE_REF_INVALID",
        moveRef,
      );
    }
  }

  const transfer = application?.transfer;
  if (transfer?.protected_move_ref != null) {
    const ref = requireString(
      transfer.protected_move_ref,
      "CORE_PROJECTION_TRANSFER_PROTECTED_MOVE_REF_INVALID",
    );
    requireCondition(moveIds.has(ref), "CORE_PROJECTION_TRANSFER_PROTECTED_MOVE_REF_UNKNOWN", ref);
    requireCondition(
      projection.presentation.protected_move_refs.includes(ref),
      "CORE_PROJECTION_TRANSFER_PROTECTED_MOVE_NOT_PRESENTED",
      ref,
    );
  }
}

export function validateCoreProjection(input) {
  const projection = clone(input);
  requireObject(projection, "CORE_PROJECTION_REQUIRED");
  requireCondition(
    projection.contract_version === CORE_PROJECTION_CONTRACT_VERSION,
    "CORE_PROJECTION_VERSION_UNSUPPORTED",
    String(projection.contract_version),
  );
  requireCondition(
    CORE_MODES.has(projection.core),
    "CORE_PROJECTION_CORE_UNSUPPORTED",
    String(projection.core),
  );

  projection.concept = projection.concept == null
    ? null
    : requireObject(projection.concept, "CORE_PROJECTION_CONCEPT_INVALID");
  projection.application = projection.application == null
    ? null
    : requireObject(projection.application, "CORE_PROJECTION_APPLICATION_INVALID");
  projection.presentation = requireObject(
    projection.presentation,
    "CORE_PROJECTION_PRESENTATION_REQUIRED",
  );

  if (projection.concept) {
    requireString(projection.concept.microtopic_ref, "CORE_PROJECTION_MICROTOPIC_REF_REQUIRED");
    requireString(projection.concept.inferential_jump, "CORE_PROJECTION_INFERENTIAL_JUMP_REQUIRED");
    projection.concept.teaching_path = optionalArray(
      projection.concept.teaching_path,
      "CORE_PROJECTION_TEACHING_PATH_INVALID",
      projection.concept.microtopic_ref,
    );
    projection.concept.misconceptions = optionalArray(
      projection.concept.misconceptions,
      "CORE_PROJECTION_MISCONCEPTIONS_INVALID",
      projection.concept.microtopic_ref,
    );
    projection.concept.representation_refs = optionalArray(
      projection.concept.representation_refs,
      "CORE_PROJECTION_REPRESENTATION_REFS_INVALID",
      projection.concept.microtopic_ref,
    );
  }

  if (projection.application) {
    requireString(projection.application.question_ref, "CORE_PROJECTION_QUESTION_REF_REQUIRED");
    requireString(projection.application.family_ref, "CORE_PROJECTION_FAMILY_REF_REQUIRED");
    requireString(projection.application.stem, "CORE_PROJECTION_STEM_REQUIRED");
    for (const field of ["source_refs", "subparts", "options", "conditions", "figure_refs"]) {
      projection.application[field] = optionalStringArray(
        projection.application[field],
        `CORE_PROJECTION_${field.toUpperCase()}_INVALID`,
      );
    }
    if (projection.application.origin != null) {
      requireCondition(
        ["ORIGINAL", "ADAPTED", "AUTHORED"].includes(projection.application.origin),
        "CORE_PROJECTION_ORIGIN_INVALID",
      );
    }
    if (projection.application.original_number != null) {
      requireString(projection.application.original_number, "CORE_PROJECTION_ORIGINAL_NUMBER_INVALID");
    }
    if (projection.application.check != null) {
      requireCondition(typeof projection.application.check === "string", "CORE_PROJECTION_CHECK_INVALID");
    }
    projection.application.reasoning_route = optionalArray(
      projection.application.reasoning_route,
      "CORE_PROJECTION_REASONING_ROUTE_INVALID",
    );
    projection.application.hints = optionalArray(
      projection.application.hints,
      "CORE_PROJECTION_HINTS_INVALID",
    );
    projection.application.scaffolds = optionalArray(
      projection.application.scaffolds,
      "CORE_PROJECTION_SCAFFOLDS_INVALID",
    );
  }

  requireCondition(
    typeof projection.presentation.attempt_before_reveal === "boolean",
    "CORE_PROJECTION_ATTEMPT_POLICY_REQUIRED",
  );
  requireCondition(
    typeof projection.presentation.show_full_construction === "boolean",
    "CORE_PROJECTION_CONSTRUCTION_POLICY_REQUIRED",
  );
  projection.presentation.protected_move_refs = optionalArray(
    projection.presentation.protected_move_refs,
    "CORE_PROJECTION_PROTECTED_MOVES_INVALID",
  );

  if (["CORE1A", "CORE1B"].includes(projection.core)) {
    requireCondition(projection.concept != null, "CORE_PROJECTION_CONCEPT_REQUIRED", projection.core);
  }
  if (["CORE2A", "CORE2B"].includes(projection.core)) {
    requireCondition(projection.application != null, "CORE_PROJECTION_APPLICATION_REQUIRED", projection.core);
  }

  validateReasoningRoute(projection);
  return projection;
}

function isConceptReconstruction(projection) {
  return Boolean(
    projection.presentation.attempt_before_reveal
    && !projection.application?.question_ref
    && projection.concept.teaching_path.length,
  );
}

export function deriveCoreLearningState(input) {
  const projection = validateCoreProjection(input);
  let stage = "ORIENTATION";
  if (projection.presentation.attempt_before_reveal) stage = "AWAITING_ATTEMPT";
  else if (projection.presentation.show_full_construction) stage = "CONSTRUCTION_VISIBLE";
  else if (projection.application?.question_ref) stage = "QUESTION_VISIBLE";

  return {
    contractVersion: projection.contract_version,
    core: projection.core,
    stage,
    attempted: false,
    attemptCount: 0,
    reconstructionVisible: stage === "CONSTRUCTION_VISIBLE",
    reasoningVisible: false,
    questionVisible: Boolean(projection.application?.question_ref),
    supportIndex: 0,
    protectedMoveRefs: clone(projection.presentation.protected_move_refs),
    currentVisualRef: projection.presentation.initial_visual_ref ?? null,
    currentVisualStageRef: projection.presentation.initial_visual_stage_ref ?? null,
    completed: false,
  };
}

function validateState(projection, state) {
  requireObject(state, "CORE_LEARNING_STATE_REQUIRED");
  requireCondition(
    state.contractVersion === projection.contract_version,
    "CORE_LEARNING_STATE_CONTRACT_MISMATCH",
  );
  requireCondition(state.core === projection.core, "CORE_LEARNING_STATE_CORE_MISMATCH");
  requireCondition(Number.isInteger(state.attemptCount) && state.attemptCount >= 0, "CORE_LEARNING_STATE_ATTEMPT_COUNT_INVALID");
  requireCondition(Number.isInteger(state.supportIndex) && state.supportIndex >= 0, "CORE_LEARNING_STATE_SUPPORT_INDEX_INVALID");
  requireCondition(
    state.supportIndex <= (projection.application?.scaffolds.length ?? 0),
    "CORE_LEARNING_STATE_SUPPORT_INDEX_OUT_OF_RANGE",
  );
  if (!state.attempted) {
    requireCondition(state.attemptCount === 0, "CORE_LEARNING_STATE_ATTEMPT_FLAG_MISMATCH");
    requireCondition(!state.reasoningVisible, "CORE_LEARNING_STATE_REASONING_PREATTEMPT");
    if (isConceptReconstruction(projection)) {
      requireCondition(!state.reconstructionVisible, "CORE_LEARNING_STATE_RECONSTRUCTION_PREATTEMPT");
    }
  }
  return clone(state);
}

function nextScaffold(projection, state) {
  const scaffold = projection.application?.scaffolds[state.supportIndex] ?? null;
  if (!scaffold) return { scaffold: null, blocked: false };
  const blocked = !state.attempted
    && projection.presentation.protected_move_refs.includes(scaffold.supports_move_ref);
  return { scaffold, blocked };
}

export function transitionCoreLearningState(input, currentState, command) {
  const projection = validateCoreProjection(input);
  const state = validateState(projection, currentState);
  requireObject(command, "CORE_LEARNING_COMMAND_REQUIRED");
  requireString(command.type, "CORE_LEARNING_COMMAND_TYPE_REQUIRED");

  if (command.type === "COMMIT_ATTEMPT") {
    state.attempted = true;
    state.attemptCount += 1;
    if (isConceptReconstruction(projection)) {
      state.reconstructionVisible = true;
      state.stage = "RECONSTRUCTION_VISIBLE";
    } else if (projection.application?.reasoning_route.length) {
      state.reasoningVisible = true;
      state.stage = "REASONING_VISIBLE";
    } else {
      state.stage = "ATTEMPT_COMMITTED";
    }
    return { state, changed: true, reason: "ATTEMPT_COMMITTED" };
  }

  if (command.type === "REQUEST_SUPPORT") {
    const { scaffold, blocked } = nextScaffold(projection, state);
    if (!scaffold) return { state, changed: false, reason: "SUPPORT_EXHAUSTED" };
    if (blocked) return { state, changed: false, reason: "SUPPORT_PROTECTED_PREATTEMPT" };

    state.supportIndex += 1;
    if (scaffold.visual_ref && scaffold.visual_stage_ref) {
      state.currentVisualRef = scaffold.visual_ref;
      state.currentVisualStageRef = scaffold.visual_stage_ref;
    }
    return { state, changed: true, reason: "SUPPORT_REVEALED" };
  }

  if (command.type === "COMPLETE_ACTIVITY") {
    const available = state.reconstructionVisible
      || state.reasoningVisible
      || state.stage === "CONSTRUCTION_VISIBLE";
    requireCondition(available, "CORE_LEARNING_COMPLETION_NOT_AVAILABLE");
    state.completed = true;
    state.stage = "COMPLETE";
    return { state, changed: true, reason: "ACTIVITY_COMPLETED" };
  }

  throw new CoreLearningPageError("CORE_LEARNING_COMMAND_UNSUPPORTED", command.type);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderTeachingPath(path) {
  if (!path.length) return '<p class="empty">No construction steps supplied.</p>';
  return `<ol class="construction">${path.map((step) => {
    const action = escapeHtml(step?.action ?? "");
    const why = step?.why_valid ? `<small>${escapeHtml(step.why_valid)}</small>` : "";
    return `<li><span>${action}</span>${why}</li>`;
  }).join("")}</ol>`;
}

function renderConcept(projection, state) {
  if (!projection.concept) return "";
  const eliciting = isConceptReconstruction(projection) && !state.attempted;
  const text = eliciting
    ? projection.concept.elicitation?.prompt ?? "Reconstruct the connection before revealing it."
    : projection.concept.inferential_jump;
  const label = eliciting ? "Reconstruct" : "Concept target";
  return `<section class="concept" aria-labelledby="core-concept-title">
    <h3 id="core-concept-title">${label}</h3>
    <p>${escapeHtml(text)}</p>
  </section>`;
}

function renderQuestion(projection, state) {
  if (!state.questionVisible) return "";
  const app = projection.application;
  const source = [
    app.origin,
    app.original_number ? `Question ${app.original_number}` : null,
    ...app.source_refs.map((ref) => `Source ${ref}`),
  ].filter(Boolean);
  const list = (label, items) => items.length
    ? `<div class="question-parts"><h4>${label}</h4><ol>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol></div>`
    : "";
  return `<section class="question" aria-labelledby="core-question-title">
    <h3 id="core-question-title">Try</h3>
    <p>${escapeHtml(app.stem)}</p>
    ${source.length ? `<p class="source-identity">${source.map(escapeHtml).join(" · ")}</p>` : ""}
    ${list("Conditions", app.conditions)}
    ${list("Parts", app.subparts)}
    ${list("Options", app.options)}
  </section>`;
}

function renderAttempt(projection, state) {
  const needed = state.questionVisible || isConceptReconstruction(projection);
  if (!needed || state.completed) return "";
  if (state.attempted) {
    return `<section class="attempt-panel" aria-label="Attempt status">
      <p class="attempt-status">Attempt committed.</p>
    </section>`;
  }
  return `<form class="attempt-panel" data-attempt-form>
    <label for="core-attempt">Your response</label>
    <textarea id="core-attempt" data-attempt-input rows="3"></textarea>
    <button type="submit" data-action="commit">Commit attempt</button>
  </form>`;
}

function visibleScaffolds(projection, state) {
  return (projection.application?.scaffolds ?? []).slice(0, state.supportIndex);
}

function renderSupport(projection, state) {
  const visible = visibleScaffolds(projection, state);
  const next = nextScaffold(projection, state);
  if (!visible.length && (!next.scaffold || next.blocked)) return "";

  const rows = visible.length
    ? `<ol class="support-list">${visible.map((item) => `<li data-support-kind="${escapeHtml(item.support_kind)}">
        <span>${escapeHtml(item.text)}</span>
      </li>`).join("")}</ol>`
    : "";

  const button = next.scaffold && !next.blocked
    ? '<button type="button" data-action="support">Show support</button>'
    : "";

  return `<section class="support-panel" aria-labelledby="core-support-title">
    <h3 id="core-support-title">Support</h3>
    ${rows}
    ${button}
  </section>`;
}

function renderReasoningRoute(projection, state) {
  if (!state.reasoningVisible || !projection.application?.reasoning_route.length) return "";
  const crux = projection.application.crux_move_ref;
  return `<section class="reasoning-panel" aria-labelledby="core-reasoning-title">
    <h3 id="core-reasoning-title">Reasoning route</h3>
    <ol class="reasoning-route">${projection.application.reasoning_route.map((move) => {
      const isCrux = move.id === crux;
      const marker = isCrux ? '<strong class="crux-label">Key decision</strong>' : "";
      const why = move.why_valid ? `<small>${escapeHtml(move.why_valid)}</small>` : "";
      return `<li data-move-id="${escapeHtml(move.id)}" data-move-kind="${escapeHtml(move.kind)}"${isCrux ? ' data-crux="true"' : ""}>
        ${marker}<span>${escapeHtml(move.action)}</span>${why}
      </li>`;
    }).join("")}</ol>
  </section>`;
}

function renderIndependentCheck(projection, state) {
  const check = projection.application?.check;
  if (!state.reasoningVisible || !check) return "";
  return `<section class="check-panel" aria-labelledby="core-check-title">
    <h3 id="core-check-title">Independent check</h3>
    <p>${escapeHtml(check)}</p>
  </section>`;
}

function renderConstruction(projection, state) {
  if (!projection.concept || !state.reconstructionVisible) return "";
  return `<section class="construction-panel" data-semantic="reconstruction" aria-labelledby="core-construction-title">
    <h3 id="core-construction-title">Construction</h3>
    ${renderTeachingPath(projection.concept.teaching_path)}
  </section>`;
}

function renderRepresentation(state) {
  const visualRef = state.currentVisualRef ? escapeHtml(state.currentVisualRef) : "";
  const visualStage = state.currentVisualStageRef ? escapeHtml(state.currentVisualStageRef) : "";
  return `<section class="representation-panel" aria-labelledby="core-representation-title"
    data-visual-ref="${visualRef}" data-visual-stage-ref="${visualStage}">
    <h3 id="core-representation-title">Representation</h3>
    <div data-workbench-mount></div>
    <p class="representation-fallback" data-workbench-fallback>
      Interactive representation is supplied by the host when available.
    </p>
  </section>`;
}

function renderCompletion(state) {
  if (state.completed) return '<p class="complete" role="status">Activity complete.</p>';
  const available = state.reconstructionVisible || state.reasoningVisible || state.stage === "CONSTRUCTION_VISIBLE";
  if (!available) return "";
  return '<button type="button" data-action="complete">Complete activity</button>';
}

export function renderCoreLearningProjection(input, stateInput = null) {
  const projection = validateCoreProjection(input);
  const state = stateInput
    ? validateState(projection, stateInput)
    : deriveCoreLearningState(projection);

  return `<style>
    :host { display:block; font:inherit; color:inherit; }
    .shell { display:grid; gap:1rem; max-width:72rem; margin:0 auto; }
    .orientation,.concept,.question,.attempt-panel,.support-panel,.reasoning-panel,.check-panel,.construction-panel,.representation-panel {
      border:1px solid currentColor; border-radius:.75rem; padding:1rem;
    }
    .eyebrow { font-size:.8rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
    h2,h3,p { margin:.25rem 0 .75rem; }
    ol { margin:.5rem 0 0; padding-left:1.25rem; }
    li + li { margin-top:.65rem; }
    small { display:block; margin-top:.2rem; opacity:.8; }
    .source-identity { font-size:.85rem; opacity:.8; }
    .question-parts h4 { margin:.75rem 0 .25rem; }
    label { display:block; font-weight:600; margin-bottom:.35rem; }
    textarea { box-sizing:border-box; width:100%; max-width:48rem; font:inherit; }
    button { font:inherit; min-height:2.75rem; padding:.55rem .8rem; margin-top:.65rem; }
    .status { font-weight:600; }
    [data-crux="true"] { border-inline-start:.3rem solid currentColor; padding-inline-start:.75rem; }
    .crux-label { display:block; margin-bottom:.2rem; }
    .visually-hidden {
      position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden;
      clip:rect(0,0,0,0); white-space:nowrap; border:0;
    }
    @media (max-width: 36rem) {
      .orientation,.concept,.question,.attempt-panel,.support-panel,.reasoning-panel,.check-panel,.construction-panel,.representation-panel { padding:.75rem; }
    }
    @media (prefers-reduced-motion: reduce) {
      *,*::before,*::after { animation-duration:0s !important; transition-duration:0s !important; scroll-behavior:auto !important; }
    }
  </style>
  <article class="shell" data-core="${escapeHtml(projection.core)}" data-stage="${escapeHtml(state.stage)}">
    <header class="orientation">
      <div class="eyebrow">${escapeHtml(projection.core)}</div>
      <h2>Current learning target</h2>
      <p class="status">${escapeHtml(state.stage.replaceAll("_", " ").toLowerCase())}</p>
      <p class="visually-hidden" aria-live="polite" data-live-status></p>
    </header>
    ${renderConcept(projection, state)}
    ${renderQuestion(projection, state)}
    ${renderRepresentation(state)}
    ${renderAttempt(projection, state)}
    ${renderSupport(projection, state)}
    ${renderConstruction(projection, state)}
    ${renderReasoningRoute(projection, state)}
    ${renderIndependentCheck(projection, state)}
    ${renderCompletion(state)}
  </article>`;
}

const HTMLElementBase = globalThis.HTMLElement || class {};

export class CoreLearningPage extends HTMLElementBase {
  constructor() {
    super();
    this._projection = null;
    this._state = null;
    this._scene = null;
    this._adapter = null;
    this._injections = [];
    this._injectionsVersion = 0;
    this._workbenchElement = null;
    this._workbenchInjectionsVersion = -1;
    this._workbenchEventHandler = (event) => this._onWorkbenchEvent(event);
    if (typeof this.attachShadow === "function") this.attachShadow({ mode: "open" });
  }

  configure({
    projection,
    scene = null,
    adapter = null,
    injections = [],
  }) {
    const validated = validateCoreProjection(projection);
    const hasScene = scene != null;
    const hasAdapter = adapter != null;
    requireCondition(
      hasScene === hasAdapter,
      "CORE_LEARNING_WORKBENCH_BINDING_INCOMPLETE",
    );
    requireCondition(
      Array.isArray(injections),
      "CORE_LEARNING_INJECTIONS_INVALID",
    );

    this._projection = validated;
    this._state = deriveCoreLearningState(validated);
    this._scene = scene ?? null;
    this._adapter = adapter ?? null;
    this._injections = [...injections];
    this._injectionsVersion += 1;
    this._render();
    return this.state;
  }

  set projection(value) {
    this.configure({
      projection: value,
      scene: this._scene,
      adapter: this._adapter,
      injections: this._injections,
    });
  }

  get projection() {
    return this._projection ? clone(this._projection) : null;
  }

  get state() {
    return this._state ? clone(this._state) : null;
  }

  set scene(value) {
    this._scene = value ?? null;
    this._render();
  }

  get scene() {
    return this._scene ? clone(this._scene) : null;
  }

  set adapter(value) {
    this._adapter = value ?? null;
    this._render();
  }

  get adapter() {
    return this._adapter;
  }

  set injections(value) {
    this._injections = Array.isArray(value) ? [...value] : [];
    this._injectionsVersion += 1;
    this._render();
  }

  get injections() {
    return clone(this._injections);
  }

  get workbenchTextSummary() {
    return this._workbenchElement?.textSummary ?? "Interactive representation is not configured.";
  }

  connectedCallback() {
    this._render();
  }

  commitAttempt(response = "") {
    this._requireProjection();
    const before = this._state;
    const result = transitionCoreLearningState(
      this._projection,
      this._state,
      { type: "COMMIT_ATTEMPT" },
    );
    this._state = result.state;
    this._render();
    this._emit(CORE_LEARNER_EVENTS.ATTEMPT_COMMITTED, {
      attemptNumber: this._state.attemptCount,
      response: String(response ?? ""),
    });
    if (
      before.reconstructionVisible !== this._state.reconstructionVisible
      || before.reasoningVisible !== this._state.reasoningVisible
    ) {
      this._emit(CORE_LEARNER_EVENTS.REVEAL_CHANGED, {
        kind: this._state.reconstructionVisible ? "reconstruction" : "reasoning",
        stage: this._state.stage,
      });
    }
    this._announce("Attempt committed. New material is available.");
    return this.state;
  }

  requestSupport() {
    this._requireProjection();
    const before = this._state.supportIndex;
    const result = transitionCoreLearningState(
      this._projection,
      this._state,
      { type: "REQUEST_SUPPORT" },
    );
    this._state = result.state;
    this._render();
    this._emit(CORE_LEARNER_EVENTS.SUPPORT_REQUESTED, {
      fromTier: before,
      toTier: this._state.supportIndex,
      revealed: result.changed,
      reason: result.reason,
    });
    if (result.changed) {
      this._emit(CORE_LEARNER_EVENTS.REVEAL_CHANGED, {
        kind: "support",
        supportTier: this._state.supportIndex,
        visualRef: this._state.currentVisualRef,
        visualStageRef: this._state.currentVisualStageRef,
      });
      this._announce("Additional support is available.");
    }
    return this.state;
  }

  completeActivity() {
    this._requireProjection();
    const result = transitionCoreLearningState(
      this._projection,
      this._state,
      { type: "COMPLETE_ACTIVITY" },
    );
    this._state = result.state;
    this._render();
    this._emit(CORE_LEARNER_EVENTS.ACTIVITY_COMPLETED, {
      attemptCount: this._state.attemptCount,
      supportTier: this._state.supportIndex,
    });
    this._announce("Activity complete.");
    return this.state;
  }

  _requireProjection() {
    if (!this._projection || !this._state) {
      throw new CoreLearningPageError("CORE_LEARNING_PAGE_PROJECTION_REQUIRED");
    }
  }

  _emit(type, detail) {
    if (
      typeof this.dispatchEvent === "function"
      && typeof globalThis.CustomEvent === "function"
    ) {
      this.dispatchEvent(new globalThis.CustomEvent(type, {
        detail: clone(detail),
        bubbles: true,
        composed: true,
      }));
    }
  }

  _announce(message) {
    const node = this.shadowRoot?.querySelector?.("[data-live-status]");
    if (node) node.textContent = message;
  }

  _onWorkbenchEvent(event) {
    const detail = event?.detail;
    if (!detail || !["TRANSFER_ACCEPTED", "UNDO_APPLIED", "REDO_APPLIED"].includes(detail.type)) return;
    this._emit(CORE_LEARNER_EVENTS.REPRESENTATION_MANIPULATED, {
      workbenchEventType: detail.type,
      sceneId: detail.sceneId ?? this._scene?.id ?? null,
      revision: detail.revision ?? this._workbenchElement?.snapshot?.revision ?? null,
    });
  }

  _mountWorkbench(preserved = null) {
    if (!this.shadowRoot?.querySelector) return;
    const mount = this.shadowRoot.querySelector("[data-workbench-mount]");
    if (!mount) return;

    let workbench = preserved;
    if (!workbench && globalThis.document?.createElement) {
      workbench = globalThis.document.createElement("semantic-workbench");
      workbench.dataset.workbench = "";
    }
    if (!workbench) return;
    mount.append(workbench);
    this._workbenchElement = workbench;
    workbench.removeEventListener?.("semantic-workbench-event", this._workbenchEventHandler);
    workbench.addEventListener?.("semantic-workbench-event", this._workbenchEventHandler);

    const configured = Boolean(this._scene && this._adapter);
    const fallback = this.shadowRoot.querySelector("[data-workbench-fallback]");
    if (fallback) fallback.hidden = configured;
    if (!configured) return;

    if (workbench.scene !== this._scene) workbench.scene = this._scene;
    if (workbench.adapter !== this._adapter) workbench.adapter = this._adapter;
    if (this._workbenchInjectionsVersion !== this._injectionsVersion) {
      workbench.injections = this._injections;
      this._workbenchInjectionsVersion = this._injectionsVersion;
    }
  }

  _bindActions() {
    if (!this.shadowRoot?.querySelector) return;
    const form = this.shadowRoot.querySelector("[data-attempt-form]");
    form?.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = this.shadowRoot.querySelector("[data-attempt-input]");
      this.commitAttempt(input?.value ?? "");
    });
    this.shadowRoot.querySelector('[data-action="support"]')?.addEventListener("click", () => {
      this.requestSupport();
    });
    this.shadowRoot.querySelector('[data-action="complete"]')?.addEventListener("click", () => {
      this.completeActivity();
    });
  }

  _render() {
    if (!this.shadowRoot) return;
    if (!this._projection) {
      this.shadowRoot.innerHTML = '<p role="status">Core learning page requires a projection.</p>';
      return;
    }
    const preservedWorkbench = this.shadowRoot.querySelector?.("[data-workbench]") ?? null;
    this.shadowRoot.innerHTML = renderCoreLearningProjection(this._projection, this._state);
    this._mountWorkbench(preservedWorkbench);
    this._bindActions();
  }
}

if (globalThis.customElements && !globalThis.customElements.get(CORE_LEARNING_PAGE_TAG)) {
  globalThis.customElements.define(CORE_LEARNING_PAGE_TAG, CoreLearningPage);
}
