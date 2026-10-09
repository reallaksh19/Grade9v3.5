export const CORE_LEARNING_PAGE_TAG = "core-learning-page";
export const CORE_PROJECTION_CONTRACT_VERSION = "1.1";

const CORE_MODES = new Set(["CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B"]);
const WEB_MOUNT_MODES = new Set(["PORTABLE_SCENE", "COMPONENT", "STATIC_FIGURE"]);
const WEB_PACKAGING_MODES = new Set(["PUBLIC", "PAGES", "OFFLINE_DIRECTORY", "SINGLE_FILE", "EMBED"]);
const SUPPORT_KINDS = new Set(["REPRESENT", "CONNECT", "EXECUTE"]);
const REVEAL_KINDS = new Set(["CONCEPT", "METHOD", "ANSWER"]);
const clone = (value) => value == null ? value : JSON.parse(JSON.stringify(value));

export const CORE_LEARNER_EVENTS = Object.freeze({
  ATTEMPT_COMMITTED: "attempt_committed",
  ATTEMPT_REJECTED: "attempt_rejected",
  SUPPORT_REQUESTED: "support_requested",
  HINT_REQUESTED: "hint_requested",
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

  projection.orientation = projection.orientation == null
    ? null
    : requireObject(projection.orientation, "CORE_PROJECTION_ORIENTATION_INVALID");
  projection.concept = projection.concept == null
    ? null
    : requireObject(projection.concept, "CORE_PROJECTION_CONCEPT_INVALID");
  projection.application = projection.application == null
    ? null
    : requireObject(projection.application, "CORE_PROJECTION_APPLICATION_INVALID");

  projection.delivery = requireObject(
    projection.delivery,
    "CORE_PROJECTION_DELIVERY_REQUIRED",
  );
  const web = requireObject(
    projection.delivery.web,
    "CORE_PROJECTION_WEB_DELIVERY_REQUIRED",
  );
  requireString(web.blueprint_ref, "CORE_PROJECTION_WEB_BLUEPRINT_REF_REQUIRED");
  requireString(web.blueprint_id, "CORE_PROJECTION_WEB_BLUEPRINT_ID_REQUIRED");
  requireString(web.blueprint_version, "CORE_PROJECTION_WEB_BLUEPRINT_VERSION_REQUIRED");
  requireCondition(
    web.blueprint_ref === `${web.blueprint_id}@${web.blueprint_version}`,
    "CORE_PROJECTION_WEB_BLUEPRINT_REF_MISMATCH",
    web.blueprint_ref,
  );
  requireString(web.shell_ref, "CORE_PROJECTION_WEB_SHELL_REF_REQUIRED");
  requireString(web.layout_family, "CORE_PROJECTION_WEB_LAYOUT_REQUIRED");
  web.required_slots = optionalStringArray(
    web.required_slots,
    "CORE_PROJECTION_WEB_REQUIRED_SLOTS_INVALID",
  );
  web.slot_order = optionalStringArray(
    web.slot_order,
    "CORE_PROJECTION_WEB_SLOT_ORDER_INVALID",
  );
  requireCondition(
    web.required_slots.every((slot) => web.slot_order.includes(slot)),
    "CORE_PROJECTION_WEB_REQUIRED_SLOT_UNKNOWN",
  );
  const interactionPolicy = requireObject(
    web.interaction_policy,
    "CORE_PROJECTION_WEB_INTERACTION_POLICY_REQUIRED",
  );
  requireCondition(
    ["FROM_PROJECTION", "ALWAYS", "NEVER"].includes(interactionPolicy.attempt_before_reveal),
    "CORE_PROJECTION_WEB_ATTEMPT_POLICY_INVALID",
  );
  requireCondition(
    typeof interactionPolicy.progressive_support === "boolean",
    "CORE_PROJECTION_WEB_PROGRESSIVE_SUPPORT_INVALID",
  );
  requireString(
    interactionPolicy.solution_policy,
    "CORE_PROJECTION_WEB_SOLUTION_POLICY_REQUIRED",
  );
  const representationPolicy = requireObject(
    web.representation_policy,
    "CORE_PROJECTION_WEB_REPRESENTATION_POLICY_REQUIRED",
  );
  representationPolicy.preferred_mount_modes = optionalStringArray(
    representationPolicy.preferred_mount_modes,
    "CORE_PROJECTION_WEB_MOUNT_MODES_INVALID",
  );
  requireCondition(
    representationPolicy.preferred_mount_modes.length > 0
      && representationPolicy.preferred_mount_modes.every((mode) => WEB_MOUNT_MODES.has(mode)),
    "CORE_PROJECTION_WEB_MOUNT_MODES_INVALID",
  );
  requireCondition(
    representationPolicy.legacy_iframe === "MIGRATION_ONLY",
    "CORE_PROJECTION_WEB_LEGACY_IFRAME_POLICY_INVALID",
  );
  const responsivePolicy = requireObject(
    web.responsive_policy,
    "CORE_PROJECTION_WEB_RESPONSIVE_POLICY_REQUIRED",
  );
  for (const field of ["compact", "medium", "expanded"]) {
    requireString(responsivePolicy[field], "CORE_PROJECTION_WEB_RESPONSIVE_MODE_REQUIRED", field);
  }
  requireCondition(
    typeof responsivePolicy.primary_fraction === "number"
      && typeof responsivePolicy.support_fraction === "number"
      && Math.abs(
        responsivePolicy.primary_fraction + responsivePolicy.support_fraction - 1
      ) < 1e-9,
    "CORE_PROJECTION_WEB_RESPONSIVE_FRACTIONS_INVALID",
  );
  const touchPolicy = requireObject(
    web.touch_policy,
    "CORE_PROJECTION_WEB_TOUCH_POLICY_REQUIRED",
  );
  requireCondition(
    Number.isInteger(touchPolicy.minimum_target_css_px)
      && touchPolicy.minimum_target_css_px >= 48,
    "CORE_PROJECTION_WEB_TOUCH_TARGET_INVALID",
  );
  requireCondition(
    Number.isInteger(touchPolicy.minimum_control_gap_css_px)
      && touchPolicy.minimum_control_gap_css_px >= 8,
    "CORE_PROJECTION_WEB_TOUCH_GAP_INVALID",
  );
  web.packaging_modes = optionalStringArray(
    web.packaging_modes,
    "CORE_PROJECTION_WEB_PACKAGING_MODES_INVALID",
  );
  requireCondition(
    WEB_PACKAGING_MODES.size === web.packaging_modes.length
      && web.packaging_modes.every((mode) => WEB_PACKAGING_MODES.has(mode)),
    "CORE_PROJECTION_WEB_PACKAGING_MODES_INVALID",
  );
  web.forbidden = optionalStringArray(
    web.forbidden,
    "CORE_PROJECTION_WEB_FORBIDDEN_INVALID",
  );

  projection.presentation = requireObject(
    projection.presentation,
    "CORE_PROJECTION_PRESENTATION_REQUIRED",
  );
  projection.presentation.learner_metadata = optionalArray(
    projection.presentation.learner_metadata,
    "CORE_PROJECTION_LEARNER_METADATA_INVALID",
  );
  const learnerMetadataKinds = new Set([
    "subject", "topic", "concept", "concept-difficulty", "question-difficulty",
    "family", "question-type", "source", "provenance", "transfer-dimension",
  ]);
  for (const item of projection.presentation.learner_metadata) {
    requireObject(item, "CORE_PROJECTION_LEARNER_METADATA_ITEM_INVALID");
    requireCondition(
      learnerMetadataKinds.has(item.kind),
      "CORE_PROJECTION_LEARNER_METADATA_KIND_INVALID",
      String(item.kind),
    );
    requireString(item.field_label, "CORE_PROJECTION_LEARNER_METADATA_FIELD_LABEL_REQUIRED");
    requireString(item.label, "CORE_PROJECTION_LEARNER_METADATA_LABEL_REQUIRED");
    requireString(item.value, "CORE_PROJECTION_LEARNER_METADATA_VALUE_REQUIRED");
    if (item.ref != null) requireString(item.ref, "CORE_PROJECTION_LEARNER_METADATA_REF_INVALID");
  }

  if (projection.orientation) {
    requireString(projection.orientation.bucket_ref, "CORE_PROJECTION_ORIENTATION_BUCKET_REQUIRED");
    requireString(projection.orientation.title, "CORE_PROJECTION_ORIENTATION_TITLE_REQUIRED");
    projection.orientation.blocks = optionalArray(
      projection.orientation.blocks,
      "CORE_PROJECTION_ORIENTATION_BLOCKS_INVALID",
      projection.orientation.bucket_ref,
    );
    requireCondition(
      projection.orientation.blocks.length > 0,
      "CORE_PROJECTION_ORIENTATION_BLOCKS_REQUIRED",
      projection.orientation.bucket_ref,
    );
    for (const block of projection.orientation.blocks) {
      requireObject(block, "CORE_PROJECTION_ORIENTATION_BLOCK_INVALID");
      requireString(block.id, "CORE_PROJECTION_ORIENTATION_BLOCK_ID_REQUIRED");
      requireCondition(
        ["TEXT", "EQUATION", "FIGURE"].includes(block.kind),
        "CORE_PROJECTION_ORIENTATION_BLOCK_KIND_INVALID",
        String(block.kind),
      );
    }
  }

  if (projection.concept) {
    requireString(projection.concept.microtopic_ref, "CORE_PROJECTION_MICROTOPIC_REF_REQUIRED");
    requireString(projection.concept.inferential_jump, "CORE_PROJECTION_INFERENTIAL_JUMP_REQUIRED");
    projection.concept.entry_assumptions = optionalStringArray(
      projection.concept.entry_assumptions,
      "CORE_PROJECTION_ENTRY_ASSUMPTIONS_INVALID",
    );
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
    projection.concept.representation_refs = optionalStringArray(
      projection.concept.representation_refs,
      "CORE_PROJECTION_REPRESENTATION_REFS_INVALID",
    );
    projection.concept.representations = optionalArray(
      projection.concept.representations,
      "CORE_PROJECTION_REPRESENTATIONS_INVALID",
      projection.concept.microtopic_ref,
    );
    projection.concept.relation_checks = optionalStringArray(
      projection.concept.relation_checks,
      "CORE_PROJECTION_RELATION_CHECKS_INVALID",
    );
    projection.concept.worked_anchors = optionalArray(
      projection.concept.worked_anchors,
      "CORE_PROJECTION_WORKED_ANCHORS_INVALID",
      projection.concept.microtopic_ref,
    );
    projection.concept.exit_task = projection.concept.exit_task == null
      ? {}
      : requireObject(projection.concept.exit_task, "CORE_PROJECTION_EXIT_TASK_INVALID");
    if (projection.concept.elicitation != null) {
      requireObject(projection.concept.elicitation, "CORE_PROJECTION_ELICITATION_INVALID");
    }
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
    projection.application.exposure = optionalArray(
      projection.application.exposure,
      "CORE_PROJECTION_EXPOSURE_INVALID",
    );
    for (const row of projection.application.exposure) {
      requireObject(row, "CORE_PROJECTION_EXPOSURE_ROW_INVALID");
      if (row.core != null) requireString(row.core, "CORE_PROJECTION_EXPOSURE_CORE_INVALID");
      if (row.role != null) requireString(row.role, "CORE_PROJECTION_EXPOSURE_ROLE_INVALID");
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
    projection.application.figures = optionalArray(
      projection.application.figures,
      "CORE_PROJECTION_FIGURES_INVALID",
    );
    for (const figure of projection.application.figures) {
      requireObject(figure, "CORE_PROJECTION_FIGURE_INVALID");
      requireString(figure.figure_ref, "CORE_PROJECTION_FIGURE_REF_REQUIRED");
      figure.read_order = optionalStringArray(
        figure.read_order,
        "CORE_PROJECTION_FIGURE_READ_ORDER_INVALID",
      );
      figure.accessibility = optionalStringArray(
        figure.accessibility,
        "CORE_PROJECTION_FIGURE_ACCESSIBILITY_INVALID",
      );
    }
    const solution = projection.application.solution == null
      ? { summary: "", steps: [], rubric: [] }
      : requireObject(projection.application.solution, "CORE_PROJECTION_SOLUTION_INVALID");
    requireCondition(typeof (solution.summary ?? "") === "string", "CORE_PROJECTION_SOLUTION_SUMMARY_INVALID");
    solution.summary = solution.summary ?? "";
    solution.steps = optionalStringArray(solution.steps, "CORE_PROJECTION_SOLUTION_STEPS_INVALID");
    solution.rubric = optionalArray(solution.rubric, "CORE_PROJECTION_SOLUTION_RUBRIC_INVALID");
    for (const row of solution.rubric) {
      requireObject(row, "CORE_PROJECTION_SOLUTION_RUBRIC_ROW_INVALID");
      requireString(row.criterion, "CORE_PROJECTION_SOLUTION_RUBRIC_CRITERION_REQUIRED");
      requireString(row.evidence_of, "CORE_PROJECTION_SOLUTION_RUBRIC_EVIDENCE_REQUIRED");
    }
    projection.application.solution = solution;
    if (projection.application.repair != null) {
      requireObject(projection.application.repair, "CORE_PROJECTION_REPAIR_INVALID");
      requireString(projection.application.repair.step_ref, "CORE_PROJECTION_REPAIR_STEP_REQUIRED");
    }
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
  if (projection.presentation.show_solution_initially == null) {
    projection.presentation.show_solution_initially = projection.core === "CORE2";
  }
  requireCondition(
    typeof projection.presentation.show_solution_initially === "boolean",
    "CORE_PROJECTION_SOLUTION_POLICY_REQUIRED",
  );
  const scaffoldCount = projection.application?.scaffolds.length ?? 0;
  const hintCount = projection.application?.hints.length ?? 0;
  for (const [field, fallback, max] of [
    ["pre_attempt_scaffold_limit", scaffoldCount, scaffoldCount],
    ["pre_attempt_hint_limit", hintCount, hintCount],
    ["post_attempt_hint_limit", hintCount, hintCount],
  ]) {
    if (projection.presentation[field] == null) projection.presentation[field] = fallback;
    requireCondition(
      Number.isInteger(projection.presentation[field])
        && projection.presentation[field] >= 0
        && projection.presentation[field] <= max,
      "CORE_PROJECTION_PRESENTATION_LIMIT_INVALID",
      field,
    );
  }

  if (projection.core === "CORE1") {
    requireCondition(projection.orientation != null, "CORE_PROJECTION_ORIENTATION_REQUIRED", projection.core);
  }
  if (["CORE1A", "CORE1B"].includes(projection.core)) {
    requireCondition(projection.concept != null, "CORE_PROJECTION_CONCEPT_REQUIRED", projection.core);
  }
  if (["CORE2", "CORE2A", "CORE2B"].includes(projection.core)) {
    requireCondition(projection.application != null, "CORE_PROJECTION_APPLICATION_REQUIRED", projection.core);
  }

  validateReasoningRoute(projection);
  return projection;
}

function isConceptReconstruction(projection) {
  return Boolean(
    projection.core === "CORE1B"
    && projection.presentation.attempt_before_reveal
    && !projection.application?.question_ref
    && projection.concept?.elicitation,
  );
}

export function deriveCoreLearningState(input) {
  const projection = validateCoreProjection(input);
  let stage = "ORIENTATION";
  if (projection.presentation.attempt_before_reveal) stage = "AWAITING_ATTEMPT";
  else if (projection.presentation.show_full_construction) stage = "CONSTRUCTION_VISIBLE";
  else if (projection.presentation.show_solution_initially) stage = "SOURCE_CUSTODY_VISIBLE";
  else if (projection.application?.question_ref) stage = "QUESTION_VISIBLE";

  return {
    contractVersion: projection.contract_version,
    core: projection.core,
    webBlueprintRef: projection.delivery.web.blueprint_ref,
    shellRef: projection.delivery.web.shell_ref,
    layoutFamily: projection.delivery.web.layout_family,
    stage,
    attempted: false,
    attemptCount: 0,
    reconstructionVisible: stage === "CONSTRUCTION_VISIBLE",
    reasoningVisible: false,
    solutionVisible: Boolean(projection.presentation.show_solution_initially),
    questionVisible: Boolean(projection.application?.question_ref),
    supportIndex: 0,
    hintIndex: 0,
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
  requireCondition(Number.isInteger(state.hintIndex) && state.hintIndex >= 0, "CORE_LEARNING_STATE_HINT_INDEX_INVALID");
  requireCondition(
    state.hintIndex <= (projection.application?.hints.length ?? 0),
    "CORE_LEARNING_STATE_HINT_INDEX_OUT_OF_RANGE",
  );
  requireCondition(typeof state.solutionVisible === "boolean", "CORE_LEARNING_STATE_SOLUTION_FLAG_INVALID");
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
  const transferPreAttempt = projection.core === "CORE2B" && !state.attempted;
  const blocked = !state.attempted && (
    state.supportIndex >= projection.presentation.pre_attempt_scaffold_limit
    || projection.presentation.protected_move_refs.includes(scaffold.supports_move_ref)
    || (transferPreAttempt && scaffold.reveals !== "CONCEPT")
  );
  return { scaffold, blocked };
}

function nextHint(projection, state) {
  const hint = projection.application?.hints[state.hintIndex] ?? null;
  if (!hint) return { hint: null, blocked: false };
  const limit = state.attempted
    ? projection.presentation.post_attempt_hint_limit
    : projection.presentation.pre_attempt_hint_limit;
  let blocked = state.hintIndex >= limit;
  if (projection.core === "CORE2B") {
    if (!state.attempted && hint.reveals !== "CONCEPT") blocked = true;
    if (
      state.attempted
      && projection.application?.transfer?.dimension === "model_choice"
      && hint.reveals !== "CONCEPT"
    ) blocked = true;
  }
  if (projection.core !== "CORE2" && !state.attempted && hint.reveals === "ANSWER") blocked = true;
  return { hint, blocked };
}

export function transitionCoreLearningState(input, currentState, command) {
  const projection = validateCoreProjection(input);
  const state = validateState(projection, currentState);
  requireObject(command, "CORE_LEARNING_COMMAND_REQUIRED");
  requireString(command.type, "CORE_LEARNING_COMMAND_TYPE_REQUIRED");

  if (command.type === "COMMIT_ATTEMPT") {
    const response = String(command.response ?? "");
    if (projection.presentation.attempt_before_reveal) {
      requireCondition(response.trim().length > 0, "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED");
    }
    state.attempted = true;
    state.attemptCount += 1;
    const solutionPolicy = projection.delivery.web.interaction_policy.solution_policy;
    if (isConceptReconstruction(projection)) {
      state.reconstructionVisible = true;
      state.stage = "RECONSTRUCTION_VISIBLE";
    } else if (projection.application?.reasoning_route.length) {
      state.reasoningVisible = true;
      if (solutionPolicy !== "LEARNER_OPENABLE") state.solutionVisible = true;
      state.stage = "REASONING_VISIBLE";
    } else if (projection.application?.question_ref) {
      if (solutionPolicy !== "LEARNER_OPENABLE") state.solutionVisible = true;
      state.stage = state.solutionVisible ? "SOLUTION_VISIBLE" : "ATTEMPT_COMMITTED";
    } else {
      state.stage = "ATTEMPT_COMMITTED";
    }
    return { state, changed: true, reason: "ATTEMPT_COMMITTED" };
  }

  if (command.type === "REVEAL_SOLUTION") {
    const solutionPolicy = projection.delivery.web.interaction_policy.solution_policy;
    requireCondition(
      solutionPolicy === "LEARNER_OPENABLE"
        || (solutionPolicy === "POST_ATTEMPT" && state.attempted)
        || projection.presentation.show_solution_initially,
      "CORE_LEARNING_SOLUTION_REVEAL_NOT_ALLOWED",
    );
    if (state.solutionVisible) return { state, changed: false, reason: "SOLUTION_ALREADY_VISIBLE" };
    state.solutionVisible = true;
    state.stage = "SOLUTION_VISIBLE";
    return { state, changed: true, reason: "SOLUTION_REVEALED" };
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

  if (command.type === "REQUEST_HINT") {
    const { hint, blocked } = nextHint(projection, state);
    if (!hint) return { state, changed: false, reason: "HINT_EXHAUSTED" };
    if (blocked) return { state, changed: false, reason: "HINT_PROTECTED_AT_THIS_STAGE" };
    state.hintIndex += 1;
    return { state, changed: true, reason: "HINT_REVEALED" };
  }

  if (command.type === "COMPLETE_ACTIVITY") {
    const available = state.reconstructionVisible
      || state.reasoningVisible
      || state.solutionVisible
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
    const id = escapeHtml(step?.id ?? "");
    return `<li data-teaching-step="${id}" tabindex="-1"><span>${action}</span>${why}</li>`;
  }).join("")}</ol>`;
}

function renderConcept(projection, state) {
  if (!projection.concept) return "";
  const eliciting = isConceptReconstruction(projection) && !state.attempted;
  const predict = projection.concept.elicitation?.predict ?? {};
  const attempt = projection.concept.elicitation?.attempt ?? {};
  const text = eliciting
    ? predict.prompt ?? "Reconstruct the connection before revealing it."
    : projection.concept.inferential_jump;
  const label = eliciting ? "Predict and reconstruct" : "Concept target";
  const production = eliciting && attempt.produces
    ? `<p><strong>Produce:</strong> ${escapeHtml(attempt.produces)}</p>`
    : "";
  const assumptions = !eliciting && projection.concept.entry_assumptions.length
    ? `<div class="entry-assumptions"><h4>What this assumes</h4><ul>${projection.concept.entry_assumptions.map(
        (item) => `<li>${escapeHtml(item)}</li>`,
      ).join("")}</ul></div>`
    : "";
  return `<section class="concept" aria-labelledby="core-concept-title">
    <h3 id="core-concept-title">${label}</h3>
    <p>${escapeHtml(text)}</p>
    ${production}
    ${assumptions}
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
    <h3 id="core-question-title">${projection.core === "CORE2" ? "Source question" : "Try"}</h3>
    <p>${escapeHtml(app.stem)}</p>
    ${source.length ? `<p class="source-identity">${source.map(escapeHtml).join(" · ")}</p>` : ""}
    ${list("Conditions", app.conditions)}
    ${list("Parts", app.subparts)}
    ${list("Options", app.options)}
  </section>`;
}

function renderQuestionFigures(projection, state) {
  if (!state.questionVisible || !projection.application?.figures.length) return "";
  return `<section class="question-figures" aria-labelledby="core-question-figures-title">
    <h3 id="core-question-figures-title">Question figure semantics</h3>
    ${projection.application.figures.map((figure) => {
      const description = figure.caption || figure.purpose || "Semantic description supplied by the canonical figure record.";
      const order = figure.read_order.length
        ? `<ol>${figure.read_order.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`
        : "";
      return `<article data-figure-ref="${escapeHtml(figure.figure_ref)}">
        <h4>${escapeHtml(figure.figure_ref)}</h4>
        <p>${escapeHtml(description)}</p>
        ${order}
      </article>`;
    }).join("")}
  </section>`;
}

function renderAttempt(projection, state) {
  const needed = projection.core !== "CORE2"
    && (state.questionVisible || isConceptReconstruction(projection));
  if (!needed || state.completed) return "";
  if (state.attempted) {
    return `<section class="attempt-panel" aria-label="Attempt status">
      <p class="attempt-status">Attempt committed.</p>
    </section>`;
  }
  const required = projection.presentation.attempt_before_reveal ? " required" : "";
  const note = projection.presentation.attempt_before_reveal
    ? '<p>Enter a genuine response before protected reasoning is revealed.</p>'
    : "";
  return `<form class="attempt-panel" data-attempt-form>
    <label for="core-attempt">Your response</label>
    ${note}
    <textarea id="core-attempt" data-attempt-input rows="3"${required}></textarea>
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

function visibleHints(projection, state) {
  return (projection.application?.hints ?? []).slice(0, state.hintIndex);
}

function renderHints(projection, state) {
  const visible = visibleHints(projection, state);
  const next = nextHint(projection, state);
  if (!visible.length && (!next.hint || next.blocked)) return "";
  const rows = visible.length
    ? `<ol class="hint-list">${visible.map((item) => `<li data-hint-reveals="${escapeHtml(item.reveals)}">
        <span>${escapeHtml(item.text)}</span>
      </li>`).join("")}</ol>`
    : "";
  const button = next.hint && !next.blocked
    ? '<button type="button" data-action="hint">Show source/question hint</button>'
    : "";
  return `<section class="hint-panel" aria-labelledby="core-hint-title">
    <h3 id="core-hint-title">Source/question hints</h3>
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
  if (!(state.reasoningVisible || state.solutionVisible) || !check) return "";
  return `<section class="check-panel" aria-labelledby="core-check-title">
    <h3 id="core-check-title">Independent check</h3>
    <p>${escapeHtml(check)}</p>
  </section>`;
}

function renderSolution(projection, state) {
  if (!state.solutionVisible || !projection.application) return "";
  const solution = projection.application.solution;
  const hasSolution = Boolean(solution.summary || solution.steps.length || solution.rubric.length);
  const repair = projection.application.repair;
  if (!hasSolution && !repair) return "";
  const title = projection.core === "CORE2" ? "Source answer" : "Solution";
  const steps = solution.steps.length
    ? `<ol class="solution-steps">${solution.steps.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol>`
    : "";
  const rubric = solution.rubric.length
    ? `<div class="solution-rubric"><h4>Rubric</h4><ul>${solution.rubric.map((row) =>
        `<li><strong>${escapeHtml(row.criterion)}</strong><span> — ${escapeHtml(row.evidence_of)}</span></li>`
      ).join("")}</ul></div>`
    : "";
  const repairHtml = repair
    ? `<div class="repair-route" data-repair-ref="${escapeHtml(repair.step_ref)}">
        <h4>Repair route</h4>
        <p><strong>${escapeHtml(repair.step_ref)}</strong>${repair.action ? `: ${escapeHtml(repair.action)}` : ""}</p>
        ${repair.why_valid ? `<small>${escapeHtml(repair.why_valid)}</small>` : ""}
        <p>Return to this activity after reviewing the named teaching step.</p>
      </div>`
    : "";
  return `<section class="solution-panel" aria-labelledby="core-solution-title">
    <h3 id="core-solution-title">${title}</h3>
    ${solution.summary ? `<p>${escapeHtml(solution.summary)}</p>` : ""}
    ${steps}
    ${rubric}
    ${repairHtml}
  </section>`;
}

function renderMisconceptions(items) {
  if (!items.length) return "";
  return `<div class="misconception-repair"><h4>Diagnose and repair</h4><ul>${items.map((item) =>
    `<li><strong>Wrong idea:</strong> ${escapeHtml(item.wrong_idea ?? "")}
      <br><strong>Tell them apart:</strong> ${escapeHtml(item.diagnostic_prompt ?? "")}
      <br><strong>Repair:</strong> ${escapeHtml(item.repair ?? "")}</li>`
  ).join("")}</ul></div>`;
}

function renderConceptRepresentations(concept) {
  if (!concept.representations.length) return "";
  return `<div class="concept-representations"><h4>Representation bridge</h4>${concept.representations.map((rep) => {
    const correspondence = (rep.correspondence ?? []).length
      ? `<ul>${rep.correspondence.map((row) =>
          `<li>${escapeHtml(row.element ?? "")} ↔ ${escapeHtml(row.symbol ?? "")}: ${escapeHtml(row.in_words ?? "")}</li>`
        ).join("")}</ul>`
      : '<p class="empty">No explicit correspondence supplied.</p>';
    return `<article data-concept-representation="${escapeHtml(rep.representation_ref ?? "")}">
      <h5>${escapeHtml(rep.representation_ref ?? "Representation")}</h5>
      ${correspondence}
    </article>`;
  }).join("")}</div>`;
}

function renderWorkedAnchors(anchors) {
  if (!anchors.length) return "";
  return `<div class="worked-anchors"><h4>Worked conceptual anchor</h4>${anchors.map((anchor) => {
    const answer = anchor.answer ?? {};
    const reasoning = (answer.reasoning ?? []).length
      ? `<ol>${answer.reasoning.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>`
      : "";
    return `<article data-worked-anchor="${escapeHtml(anchor.question_ref ?? "")}">
      <p>${escapeHtml(anchor.stem ?? "")}</p>
      ${answer.summary ? `<p><strong>Answer:</strong> ${escapeHtml(answer.summary)}</p>` : ""}
      ${reasoning}
      ${answer.check ? `<p><strong>Check:</strong> ${escapeHtml(answer.check)}</p>` : ""}
    </article>`;
  }).join("")}</div>`;
}

function renderExitClosure(concept) {
  const task = concept.exit_task ?? {};
  const answer = task.answer ?? {};
  if (!task.prompt && !concept.relation_checks.length) return "";
  const reasoning = (answer.reasoning ?? []).length
    ? `<ol>${answer.reasoning.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol>`
    : "";
  const relationChecks = concept.relation_checks.length
    ? `<div><h5>Independent checks</h5><ul>${concept.relation_checks.map((item) =>
        `<li>${escapeHtml(item)}</li>`
      ).join("")}</ul></div>`
    : "";
  return `<div class="concept-closure"><h4>Independent closure</h4>
    ${task.prompt ? `<p><strong>Check yourself:</strong> ${escapeHtml(task.prompt)}</p>` : ""}
    ${answer.summary ? `<p><strong>Answer:</strong> ${escapeHtml(answer.summary)}</p>` : ""}
    ${reasoning}
    ${answer.check ? `<p><strong>Verify:</strong> ${escapeHtml(answer.check)}</p>` : ""}
    ${relationChecks}
  </div>`;
}

function renderCore1BReconstruction(concept) {
  const elicitation = concept.elicitation ?? {};
  const predict = elicitation.predict ?? {};
  const attempt = elicitation.attempt ?? {};
  const reconstruct = elicitation.reconstruct ?? {};
  const boundary = elicitation.boundary_test ?? {};
  const route = (reconstruct.route ?? []).length
    ? `<ol>${reconstruct.route.map((step) =>
        `<li>${escapeHtml(step.ask ?? "")}${step.why_this_ask ? `<small>${escapeHtml(step.why_this_ask)}</small>` : ""}</li>`
      ).join("")}</ol>`
    : "";
  let closure = "";
  if (attempt.closure === "MODEL_RESPONSE" && attempt.model_response) {
    closure = `<p><strong>Model response:</strong> ${escapeHtml(attempt.model_response)}</p>`;
  } else if ((attempt.rubric ?? []).length) {
    closure = `<div><h5>Self-check criteria</h5><ul>${attempt.rubric.map((row) =>
      `<li><strong>${escapeHtml(row.criterion ?? "")}</strong> — ${escapeHtml(row.evidence_of ?? "")}</li>`
    ).join("")}</ul></div>`;
  }
  return `<div class="core1b-reconstruction">
    ${predict.defensible_answer ? `<p><strong>Defensible answer:</strong> ${escapeHtml(predict.defensible_answer)}</p>` : ""}
    <h4>Reconstruct the reasoning</h4>
    ${route}
    ${renderMisconceptions(concept.misconceptions)}
    ${closure}
    ${boundary.prompt ? `<div class="boundary-test"><h4>Boundary test</h4>
      <p>${escapeHtml(boundary.prompt)}</p>
      ${boundary.answer ? `<p><strong>Answer:</strong> ${escapeHtml(boundary.answer)}</p>` : ""}
      ${boundary.confirms ? `<small>${escapeHtml(boundary.confirms)}</small>` : ""}
    </div>` : ""}
  </div>`;
}

function renderConstruction(projection, state) {
  if (!projection.concept || !state.reconstructionVisible) return "";
  const body = projection.core === "CORE1B"
    ? renderCore1BReconstruction(projection.concept)
    : `${renderTeachingPath(projection.concept.teaching_path)}
       ${renderConceptRepresentations(projection.concept)}
       ${renderMisconceptions(projection.concept.misconceptions)}
       ${renderWorkedAnchors(projection.concept.worked_anchors)}
       ${renderExitClosure(projection.concept)}`;
  const title = projection.core === "CORE1B" ? "Reconstruction and repair" : "Completed construction";
  return `<section class="construction-panel" data-semantic="reconstruction" aria-labelledby="core-construction-title">
    <h3 id="core-construction-title">${title}</h3>
    ${body}
  </section>`;
}

function renderOrientationMap(projection) {
  if (projection.core !== "CORE1" || !projection.orientation) return "";
  return `<section class="orientation-map" aria-labelledby="core-orientation-map-title">
    <h3 id="core-orientation-map-title">${escapeHtml(projection.orientation.title)}</h3>
    ${projection.orientation.blocks.map((block) => {
      if (block.kind === "TEXT") {
        return `<article data-orientation-block="${escapeHtml(block.id)}">
          <p>${escapeHtml(block.text ?? "").replaceAll("\n", "<br>")}</p>
        </article>`;
      }
      if (block.kind === "EQUATION") {
        const symbols = (block.symbols ?? []).length
          ? `<ul>${block.symbols.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
          : "";
        const conditions = (block.conditions ?? []).length
          ? `<ul>${block.conditions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
          : "";
        return `<article data-orientation-block="${escapeHtml(block.id)}">
          <div class="equation-expression">${block.mathml ?? ""}</div>
          ${block.meaning ? `<p>${escapeHtml(block.meaning)}</p>` : ""}
          ${symbols}
          ${conditions}
        </article>`;
      }
      const correspondence = (block.correspondence ?? []).length
        ? `<ul>${block.correspondence.map((row) =>
            `<li>${escapeHtml(row.element ?? "")} ↔ ${escapeHtml(row.symbol ?? "")}: ${escapeHtml(row.in_words ?? "")}</li>`
          ).join("")}</ul>`
        : "";
      return `<article data-orientation-block="${escapeHtml(block.id)}">
        <p>${escapeHtml(block.scene?.caption ?? "Canonical orientation figure.")}</p>
        ${correspondence}
      </article>`;
    }).join("")}
  </section>`;
}

function renderRepresentation(state) {
  if (!state.currentVisualRef) return "";
  const visualRef = escapeHtml(state.currentVisualRef);
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

function renderIdentity(projection, state) {
  const rows = [];
  if (projection.orientation) {
    rows.push(["Bucket", projection.orientation.bucket_ref]);
  }
  if (projection.concept) {
    rows.push(["Microtopic", projection.concept.microtopic_ref]);
  }
  if (projection.application) {
    rows.push(["Family", projection.application.family_ref]);
    rows.push(["Question", projection.application.question_ref]);
  }
  const exposure = (projection.application?.exposure ?? []).map((row) => {
    const bits = [row.core, row.role, row.status].filter(Boolean);
    return bits.length ? bits.join(" · ") : null;
  }).filter(Boolean);
  const learnerMetadata = projection.presentation.learner_metadata ?? [];
  if (learnerMetadata.length) rows.length = 0;
  const learnerMetadataHtml = learnerMetadata.length
    ? `<div class="learner-metadata" data-g9-meta-strip>${learnerMetadata.map((item) =>
        `<span data-g9-meta-item data-g9-meta-kind="${escapeHtml(item.kind)}" data-g9-meta-value="${escapeHtml(item.value)}"${item.ref ? ` data-g9-meta-ref="${escapeHtml(item.ref)}"` : ""}><strong>${escapeHtml(item.field_label)}:</strong> ${escapeHtml(item.label)}</span>`
      ).join("")}</div>`
    : "";
  return `<section class="identity-panel" aria-labelledby="core-identity-title">
    <div class="eyebrow">${escapeHtml(projection.core)}</div>
    <h2 id="core-identity-title">Current learning target</h2>
    <p class="status">${escapeHtml(state.stage.replaceAll("_", " ").toLowerCase())}</p>
    ${learnerMetadataHtml}
    <dl class="identity-grid">${rows.map(([label, value]) =>
      `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`
    ).join("")}</dl>
    ${exposure.length ? `<div class="exposure-closure"><strong>Exposure</strong><ul>${exposure.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
    <p class="visually-hidden" aria-live="polite" data-live-status></p>
  </section>`;
}

function renderSolutionControl(projection, state) {
  const policy = projection.delivery.web.interaction_policy.solution_policy;
  if (policy !== "LEARNER_OPENABLE" || state.solutionVisible || !projection.application) return "";
  const solution = projection.application.solution ?? {};
  const hasSolution = Boolean(solution.summary || solution.steps?.length || solution.rubric?.length || projection.application.repair);
  if (!hasSolution) return "";
  return `<section class="solution-control" aria-label="Solution controls">
    <button type="button" data-action="solution">Open complete solution</button>
  </section>`;
}

function renderBlueprintSlot(projection, state, slotId) {
  let body = "";
  if (slotId === "identity") body = renderIdentity(projection, state);
  else if (slotId === "orientation") body = `${renderOrientationMap(projection)}${renderRepresentation(state)}`;
  else if (slotId === "attempt") {
    // A question-role projection can carry canonical concept metadata too.
    // Question roles must render their real source/authored problem here, not
    // replace it with the concept inferential jump (which can reveal W).
    const questionRole = ["CORE2", "CORE2A", "CORE2B"].includes(projection.core)
      && Boolean(projection.application?.question_ref);
    body = questionRole
      ? `${renderQuestion(projection, state)}${renderQuestionFigures(projection, state)}${renderRepresentation(state)}${renderAttempt(projection, state)}`
      : `${renderConcept(projection, state)}${renderAttempt(projection, state)}`;
  } else if (slotId === "support") body = `${renderHints(projection, state)}${renderSupport(projection, state)}`;
  else if (slotId === "solution") body = `${renderReasoningRoute(projection, state)}${renderIndependentCheck(projection, state)}${renderSolutionControl(projection, state)}${renderSolution(projection, state)}${renderCompletion(state)}`;
  else if (slotId === "construction") body = `${renderConcept(projection, state)}${renderRepresentation(state)}${renderConstruction(projection, state)}`;
  else if (slotId === "repair_closure") body = renderCompletion(state);
  else if (slotId === "reconstruction") body = `${renderConstruction(projection, state)}${renderCompletion(state)}`;
  else if (slotId === "reasoning") body = `${renderReasoningRoute(projection, state)}${renderIndependentCheck(projection, state)}${renderSolutionControl(projection, state)}${renderSolution(projection, state)}${renderCompletion(state)}`;
  else if (slotId === "post_attempt") body = `${renderHints(projection, state)}${renderSupport(projection, state)}${renderReasoningRoute(projection, state)}${renderIndependentCheck(projection, state)}${renderSolution(projection, state)}${renderCompletion(state)}`;
  const required = projection.delivery.web.required_slots.includes(slotId);
  if (!body && !required) return "";
  return `<section class="blueprint-slot slot-${escapeHtml(slotId)}" data-blueprint-slot="${escapeHtml(slotId)}" data-required="${required ? "true" : "false"}>${body}</section>`;
}

function renderBlueprintSlots(projection, state) {
  return projection.delivery.web.slot_order
    .map((slotId) => renderBlueprintSlot(projection, state, slotId))
    .join("");
}

function renderCompletion(state) {
  if (state.completed) return '<p class="complete" role="status">Activity complete.</p>';
  const available = state.reconstructionVisible || state.reasoningVisible || state.solutionVisible || state.stage === "CONSTRUCTION_VISIBLE";
  if (!available) return "";
  return '<button type="button" data-action="complete">Complete activity</button>';
}

export function renderCoreLearningProjection(input, stateInput = null) {
  const projection = validateCoreProjection(input);
  const state = stateInput
    ? validateState(projection, stateInput)
    : deriveCoreLearningState(projection);
  const web = projection.delivery.web;
  const touch = web.touch_policy;
  const responsive = web.responsive_policy;

  return `<style>
    :host { display:block; font:inherit; color:inherit; }
    .shell {
      --g9-min-target:${touch.minimum_target_css_px}px;
      --g9-control-gap:${touch.minimum_control_gap_css_px}px;
      --g9-primary:${responsive.primary_fraction}fr;
      --g9-support:${responsive.support_fraction}fr;
      display:grid; gap:1rem; max-width:80rem; margin:0 auto;
    }
    .blueprint-grid { display:grid; grid-template-columns:minmax(0,1fr); gap:1rem; align-items:start; }
    .blueprint-slot { min-width:0; display:grid; gap:1rem; align-content:start; }
    .identity-panel,.orientation-map,.concept,.question,.question-figures,.attempt-panel,.hint-panel,.support-panel,.reasoning-panel,.check-panel,.solution-panel,.solution-control,.construction-panel,.representation-panel {
      border:1px solid currentColor; border-radius:.75rem; padding:1rem; background:Canvas;
    }
    .eyebrow { font-size:.8rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
    h2,h3,p { margin:.25rem 0 .75rem; }
    ol { margin:.5rem 0 0; padding-left:1.25rem; }
    li + li { margin-top:.65rem; }
    small { display:block; margin-top:.2rem; opacity:.8; }
    .source-identity { font-size:.85rem; opacity:.8; }
    .learner-metadata { display:flex; flex-wrap:wrap; gap:.5rem; margin:.5rem 0 .75rem; }
    .learner-metadata > span { border:1px solid currentColor; border-radius:999px; padding:.25rem .5rem; font-size:.9rem; }
    .identity-grid { display:flex; flex-wrap:wrap; gap:.5rem 1rem; margin:.5rem 0; }
    .identity-grid div { display:grid; grid-template-columns:auto minmax(0,1fr); gap:.35rem; }
    .identity-grid dt { font-weight:700; }
    .identity-grid dd { margin:0; overflow-wrap:anywhere; }
    .question-parts h4 { margin:.75rem 0 .25rem; }
    label { display:block; font-weight:600; margin-bottom:.35rem; }
    textarea { box-sizing:border-box; width:100%; max-width:48rem; min-height:7rem; font:inherit; }
    button {
      font:inherit; min-height:var(--g9-min-target); min-width:var(--g9-min-target);
      padding:.55rem .8rem; margin-top:var(--g9-control-gap);
    }
    .status { font-weight:600; }
    [data-crux="true"] { border-inline-start:.3rem solid currentColor; padding-inline-start:.75rem; }
    .crux-label { display:block; margin-bottom:.2rem; }
    .visually-hidden {
      position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden;
      clip:rect(0,0,0,0); white-space:nowrap; border:0;
    }
    @media (min-width:64rem) {
      .shell[data-expanded-layout="STAGE_SUPPORT"] .blueprint-grid {
        grid-template-columns:minmax(0,var(--g9-primary)) minmax(0,var(--g9-support));
      }
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-identity { grid-column:1 / -1; }
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-support,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-repair_closure,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-reconstruction,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-post_attempt,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-solution { grid-column:2; }
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-attempt,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-construction,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-reasoning,
      .shell[data-expanded-layout="STAGE_SUPPORT"] .slot-orientation { grid-column:1; }
    }
    @media (max-width:56rem) {
      .blueprint-grid { grid-template-columns:minmax(0,1fr); }
    }
    @media (max-width:36rem) {
      .identity-panel,.orientation-map,.concept,.question,.question-figures,.attempt-panel,.hint-panel,.support-panel,.reasoning-panel,.check-panel,.solution-panel,.solution-control,.construction-panel,.representation-panel { padding:.75rem; }
    }
    @media (prefers-reduced-motion: reduce) {
      *,*::before,*::after { animation-duration:0s !important; transition-duration:0s !important; scroll-behavior:auto !important; }
    }
  </style>
  <article class="shell"
    data-core="${escapeHtml(projection.core)}"
    data-stage="${escapeHtml(state.stage)}"
    data-web-blueprint="${escapeHtml(web.blueprint_ref)}"
    data-layout-family="${escapeHtml(web.layout_family)}"
    data-compact-layout="${escapeHtml(responsive.compact)}"
    data-medium-layout="${escapeHtml(responsive.medium)}"
    data-expanded-layout="${escapeHtml(responsive.expanded)}">
    <div class="blueprint-grid">${renderBlueprintSlots(projection, state)}</div>
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
    let result;
    try {
      result = transitionCoreLearningState(
        this._projection,
        this._state,
        { type: "COMMIT_ATTEMPT", response: String(response ?? "") },
      );
    } catch (error) {
      const reason = error?.code || error?.name || "CORE_LEARNING_ATTEMPT_REJECTED";
      this._emit(CORE_LEARNER_EVENTS.ATTEMPT_REJECTED, {
        reason,
        responsePresent: String(response ?? "").trim().length > 0,
      });
      this._announce("Attempt not accepted. Enter a response before continuing.");
      throw error;
    }
    this._state = result.state;
    this._render();
    this._emit(CORE_LEARNER_EVENTS.ATTEMPT_COMMITTED, {
      attemptNumber: this._state.attemptCount,
      response: String(response ?? ""),
    });
    if (
      before.reconstructionVisible !== this._state.reconstructionVisible
      || before.reasoningVisible !== this._state.reasoningVisible
      || before.solutionVisible !== this._state.solutionVisible
    ) {
      this._emit(CORE_LEARNER_EVENTS.REVEAL_CHANGED, {
        kind: this._state.reconstructionVisible
          ? "reconstruction"
          : this._state.reasoningVisible
            ? "reasoning"
            : "solution",
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

  requestHint() {
    this._requireProjection();
    const before = this._state.hintIndex;
    const result = transitionCoreLearningState(
      this._projection,
      this._state,
      { type: "REQUEST_HINT" },
    );
    this._state = result.state;
    this._render();
    this._emit(CORE_LEARNER_EVENTS.HINT_REQUESTED, {
      fromIndex: before,
      toIndex: this._state.hintIndex,
      revealed: result.changed,
      reason: result.reason,
    });
    if (result.changed) {
      this._emit(CORE_LEARNER_EVENTS.REVEAL_CHANGED, {
        kind: "hint",
        hintIndex: this._state.hintIndex,
      });
      this._announce("Source or question hint revealed.");
    }
    return this.state;
  }

  revealSolution() {
    this._requireProjection();
    const result = transitionCoreLearningState(
      this._projection,
      this._state,
      { type: "REVEAL_SOLUTION" },
    );
    this._state = result.state;
    this._render();
    if (result.changed) {
      this._emit(CORE_LEARNER_EVENTS.REVEAL_CHANGED, {
        kind: "solution",
        stage: this._state.stage,
      });
      this._announce("Complete solution revealed.");
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
    const input = this.shadowRoot.querySelector("[data-attempt-input]");
    input?.addEventListener("invalid", () => {
      this._emit(CORE_LEARNER_EVENTS.ATTEMPT_REJECTED, {
        reason: "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED",
        responsePresent: Boolean(String(input.value ?? "").trim().length),
      });
      this._announce("Attempt not accepted. Enter a response before continuing.");
      queueMicrotask(() => input.focus?.());
    });
    form?.addEventListener("submit", (event) => {
      event.preventDefault();
      try {
        this.commitAttempt(input?.value ?? "");
      } catch (error) {
        if (error?.code !== "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED") throw error;
      }
    });
    this.shadowRoot.querySelector('[data-action="support"]')?.addEventListener("click", () => {
      this.requestSupport();
    });
    this.shadowRoot.querySelector('[data-action="hint"]')?.addEventListener("click", () => {
      this.requestHint();
    });
    this.shadowRoot.querySelector('[data-action="solution"]')?.addEventListener("click", () => {
      this.revealSolution();
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
