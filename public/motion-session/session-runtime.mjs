export const MOTION_SESSION_TRACE_VERSION = "1.0";
export const MOTION_SESSION_STAGES = Object.freeze(["orient", "core1b", "visual", "core2b", "summary"]);

const clone = (value) => value == null ? value : JSON.parse(JSON.stringify(value));

export class MotionSessionError extends Error {
  constructor(code, detail = "") {
    super(detail ? `${code}: ${detail}` : code);
    this.name = "MotionSessionError";
    this.code = code;
    this.detail = detail;
  }
}

function requireCondition(condition, code, detail = "") {
  if (!condition) throw new MotionSessionError(code, detail);
}

function requireObject(value, code, detail = "") {
  requireCondition(value && typeof value === "object" && !Array.isArray(value), code, detail);
  return value;
}

function requireString(value, code, detail = "") {
  requireCondition(typeof value === "string" && value.trim().length > 0, code, detail);
  return value;
}

function one(rows, code, detail = "") {
  requireCondition(Array.isArray(rows) && rows.length === 1, code, detail || String(rows?.length ?? 0));
  return rows[0];
}

function same(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function unlock(state, stage) {
  if (!state.unlockedStages.includes(stage)) state.unlockedStages.push(stage);
}

function canonicalRefs(identity) {
  return {
    matrix_id: identity?.matrixId ?? null,
    rung: identity?.rung ?? null,
    microtopic_ref: identity?.microtopicRef ?? null,
    capability_ref: identity?.capabilityRef ?? null,
    core1b_projection_ref: identity?.core1bProjectionId ?? null,
    representation_ref: identity?.representationRef ?? null,
    activity_ref: identity?.activityRef ?? null,
    portable_package_ref: identity?.portablePackageRef ?? null,
    core2b_projection_ref: identity?.core2bProjectionId ?? null,
  };
}

export function resolveMotionSessionIdentity(webData, coreData, {
  subject,
  matrixId,
  rung = "R1",
  transferProjectionId,
} = {}) {
  requireString(subject, "SESSION_SUBJECT_REQUIRED");
  requireString(matrixId, "SESSION_MATRIX_ID_REQUIRED");
  requireString(rung, "SESSION_RUNG_REQUIRED");
  requireString(transferProjectionId, "SESSION_TRANSFER_PROJECTION_REQUIRED");
  const subjectData = requireObject(webData?.subjects?.[subject], "SESSION_SUBJECT_DATA_UNAVAILABLE", subject);
  const atlasRows = Array.isArray(subjectData.atlas_index) ? subjectData.atlas_index : [];
  const atlas = one(
    atlasRows.filter((row) => row?.matrix_id === matrixId && row?.rung === rung),
    "SESSION_ATLAS_TARGET_NOT_FOUND",
    `${matrixId}/${rung}`,
  );

  for (const field of ["mapping", "core", "representation", "activity", "locator", "portable_package"]) {
    requireCondition(atlas.availability?.[field] === "READY", "SESSION_ATLAS_INPUT_UNAVAILABLE", `${field}:${atlas.availability?.[field] ?? "MISSING"}`);
  }

  const microtopicRef = requireString(atlas.microtopic_ref, "SESSION_MICROTOPIC_REF_UNAVAILABLE");
  const capabilityRef = requireString(atlas.capability_ref, "SESSION_CAPABILITY_REF_UNAVAILABLE");
  const representationRef = requireString(
    one(atlas.representation_refs, "SESSION_REPRESENTATION_AMBIGUOUS") ,
    "SESSION_REPRESENTATION_REF_UNAVAILABLE",
  );
  const activityRef = requireString(
    one(atlas.activity_refs, "SESSION_ACTIVITY_AMBIGUOUS"),
    "SESSION_ACTIVITY_REF_UNAVAILABLE",
  );
  const projectionRefs = Array.isArray(atlas.core_projection_refs) ? atlas.core_projection_refs : [];
  const coreRows = Array.isArray(coreData?.core_projections) ? coreData.core_projections : [];

  const core1b = one(
    coreRows.filter((row) =>
      projectionRefs.includes(row?.id)
      && row?.projection?.core === "CORE1B"
      && row?.source_ref === microtopicRef
    ),
    "SESSION_CORE1B_BINDING_NOT_FOUND",
    microtopicRef,
  );

  requireCondition(
    projectionRefs.includes(transferProjectionId),
    "SESSION_CORE2B_NOT_BOUND_TO_RUNG",
    transferProjectionId,
  );
  const core2b = one(
    coreRows.filter((row) => row?.id === transferProjectionId),
    "SESSION_CORE2B_BINDING_NOT_FOUND",
    transferProjectionId,
  );
  requireCondition(core2b.projection?.core === "CORE2B", "SESSION_CORE2B_MODE_MISMATCH", transferProjectionId);
  requireCondition(
    core2b.projection?.concept?.microtopic_ref === microtopicRef,
    "SESSION_CORE2B_MICROTOPIC_MISMATCH",
    transferProjectionId,
  );

  const target = requireObject(
    subjectData.visual_targets?.[activityRef],
    "SESSION_VISUAL_TARGET_NOT_FOUND",
    activityRef,
  );
  requireCondition(target.resource_ref === activityRef, "SESSION_VISUAL_RESOURCE_MISMATCH", activityRef);
  requireCondition(target.availability?.portable_package === "READY", "SESSION_PORTABLE_PACKAGE_UNAVAILABLE", activityRef);
  requireCondition(
    Array.isArray(target.representation_refs) && target.representation_refs.includes(representationRef),
    "SESSION_VISUAL_REPRESENTATION_MISMATCH",
    representationRef,
  );
  const portablePackageRef = requireString(target.portable_package_ref, "SESSION_PORTABLE_PACKAGE_REF_UNAVAILABLE");

  return {
    subject,
    matrixId,
    rung,
    microtopicRef,
    capabilityRef,
    core1bProjectionId: core1b.id,
    representationRef,
    activityRef,
    portablePackageRef,
    core2bProjectionId: core2b.id,
    atlasContractVersion: subjectData.atlas_index_contract_version ?? null,
  };
}

export function createInitialMotionSessionState() {
  return {
    stage: "orient",
    unlockedStages: ["orient", "core1b"],
    core1b: {
      attemptCount: 0,
      supportRequests: 0,
      supportUsed: 0,
      revealed: false,
      completed: false,
    },
    visual: {
      packageLoading: false,
      ready: false,
      revision: 0,
      acceptedCount: 0,
      rejectedCount: 0,
      seenEventKeys: [],
      failed: false,
    },
    core2b: {
      attemptCount: 0,
      supportRequests: 0,
      supportUsed: 0,
      revealed: false,
      completed: false,
    },
    summaryCreated: false,
    completed: false,
    resetCount: 0,
  };
}

export function sessionInvariantChecks(stateInput) {
  const state = clone(stateInput);
  const checks = [
    {
      id: "STAGE_IS_KNOWN",
      passed: MOTION_SESSION_STAGES.includes(state.stage),
    },
    {
      id: "CURRENT_STAGE_UNLOCKED",
      passed: Array.isArray(state.unlockedStages) && state.unlockedStages.includes(state.stage),
    },
    {
      id: "CORE1B_REVEAL_REQUIRES_ATTEMPT",
      passed: !state.core1b.revealed || state.core1b.attemptCount > 0,
    },
    {
      id: "CORE2B_REVEAL_REQUIRES_ATTEMPT",
      passed: !state.core2b.revealed || state.core2b.attemptCount > 0,
    },
    {
      id: "SUMMARY_REQUIRES_TRANSFER",
      passed: !state.summaryCreated || state.core2b.attemptCount > 0,
    },
    {
      id: "VISUAL_REVISION_NONNEGATIVE",
      passed: Number.isInteger(state.visual.revision) && state.visual.revision >= 0,
    },
  ];
  return checks;
}

function result(state, outcome, reason, changed) {
  const checks = sessionInvariantChecks(state);
  requireCondition(checks.every((check) => check.passed), "SESSION_INVARIANT_FAILED");
  return { state, outcome, reason, changed, invariantChecks: checks };
}

function observed(state, reason = "OBSERVED") {
  return result(state, "OBSERVE", reason, false);
}

export function transitionMotionSessionState(currentStateInput, actionInput) {
  const state = clone(currentStateInput);
  const action = requireObject(actionInput, "SESSION_ACTION_REQUIRED");
  const type = requireString(action.type, "SESSION_ACTION_TYPE_REQUIRED");

  if ([
    "SESSION_START", "IDENTITY_RESOLVED", "TRACE_EXPORTED", "RETRY_REQUESTED",
    "STAGE_EXITED", "STAGE_ENTERED", "CORE_REVEAL_REQUESTED",
    "VISUAL_ACTION_REQUESTED", "RECOVERY_STARTED",
  ].includes(type)) {
    return observed(state, type);
  }

  if (type === "CORE_REVEAL_DENIED") {
    return result(state, "DENY", action.reason || "SESSION_REVEAL_DENIED", false);
  }

  if (type === "NAVIGATION_REQUESTED") {
    const target = requireString(action.stage, "SESSION_TARGET_STAGE_REQUIRED");
    if (!MOTION_SESSION_STAGES.includes(target)) return result(state, "DENY", "SESSION_STAGE_UNKNOWN", false);
    if (!state.unlockedStages.includes(target)) return result(state, "DENY", "SESSION_STAGE_LOCKED", false);
    if (state.stage === target) return result(state, "DENY", "SESSION_STAGE_ALREADY_ACTIVE", false);
    return result(state, "ACCEPT", "SESSION_NAVIGATION_PERMITTED", false);
  }

  if (type === "IDENTITY_RESOLUTION_FAILED" || type === "PACKAGE_LOAD_FAILED") {
    if (type === "PACKAGE_LOAD_FAILED") state.visual.failed = true;
    return result(state, "FAIL", requireString(action.reason, "SESSION_FAILURE_REASON_REQUIRED"), type === "PACKAGE_LOAD_FAILED");
  }

  if (type === "PACKAGE_LOAD_REQUESTED") {
    state.visual.packageLoading = true;
    return result(state, "OBSERVE", "PACKAGE_LOADING", true);
  }

  if (type === "PACKAGE_READY") {
    state.visual.packageLoading = false;
    return result(state, "OBSERVE", "PACKAGE_READY", true);
  }

  if (type === "NAVIGATE") {
    const target = requireString(action.stage, "SESSION_TARGET_STAGE_REQUIRED");
    if (!MOTION_SESSION_STAGES.includes(target)) return result(state, "DENY", "SESSION_STAGE_UNKNOWN", false);
    if (!state.unlockedStages.includes(target)) return result(state, "DENY", "SESSION_STAGE_LOCKED", false);
    if (state.stage === target) return result(state, "DENY", "SESSION_STAGE_ALREADY_ACTIVE", false);
    state.stage = target;
    return result(state, "OBSERVE", "SESSION_STAGE_ENTERED", true);
  }

  if (type === "CORE_ATTEMPT_REJECTED") {
    requireCondition(action.core === "CORE1B" || action.core === "CORE2B", "SESSION_CORE_UNKNOWN");
    return result(state, "DENY", requireString(action.reason, "SESSION_ATTEMPT_REJECTION_REASON_REQUIRED"), false);
  }

  if (type === "CORE_ATTEMPT_ACCEPTED") {
    const core = action.core;
    requireCondition(core === "CORE1B" || core === "CORE2B", "SESSION_CORE_UNKNOWN");
    const key = core === "CORE1B" ? "core1b" : "core2b";
    if (state[key].attemptCount > 0) return result(state, "DENY", "SESSION_DUPLICATE_ATTEMPT", false);
    state[key].attemptCount = 1;
    return result(state, "OBSERVE", "SESSION_ATTEMPT_ACCEPTED", true);
  }

  if (type === "CORE_SUPPORT_REQUESTED") {
    const core = action.core;
    requireCondition(core === "CORE1B" || core === "CORE2B", "SESSION_CORE_UNKNOWN");
    const key = core === "CORE1B" ? "core1b" : "core2b";
    state[key].supportRequests += 1;
    if (action.revealed === true) {
      state[key].supportUsed += 1;
      return result(state, "OBSERVE", action.reason || "SESSION_SUPPORT_GRANTED", true);
    }
    return result(state, "DENY", action.reason || "SESSION_SUPPORT_WITHHELD", true);
  }

  if (type === "CORE_REVEAL_OBSERVED") {
    const core = action.core;
    requireCondition(core === "CORE1B" || core === "CORE2B", "SESSION_CORE_UNKNOWN");
    const key = core === "CORE1B" ? "core1b" : "core2b";
    if (state[key].attemptCount < 1) return result(state, "DENY", "SESSION_REVEAL_BEFORE_ATTEMPT", false);
    if (state[key].revealed) return result(state, "DENY", "SESSION_DUPLICATE_REVEAL", false);
    state[key].revealed = true;
    return result(state, "OBSERVE", "SESSION_REVEAL_OBSERVED", true);
  }

  if (type === "CORE_ACTIVITY_COMPLETED") {
    const core = action.core;
    requireCondition(core === "CORE1B" || core === "CORE2B", "SESSION_CORE_UNKNOWN");
    const key = core === "CORE1B" ? "core1b" : "core2b";
    if (state[key].attemptCount < 1) return result(state, "DENY", "SESSION_COMPLETION_BEFORE_ATTEMPT", false);
    if (state[key].completed) return result(state, "DENY", "SESSION_DUPLICATE_COMPLETION", false);
    state[key].completed = true;
    if (core === "CORE1B") unlock(state, "visual");
    else unlock(state, "summary");
    return result(state, "OBSERVE", "SESSION_CORE_ACTIVITY_COMPLETED", true);
  }

  if (type === "WORKBENCH_READY") {
    const revision = Number(action.revision ?? 0);
    if (state.visual.ready && revision === state.visual.revision) {
      return result(state, "DENY", "SESSION_DUPLICATE_WORKBENCH_READY", false);
    }
    if (revision !== 0) return result(state, "DENY", "SESSION_WORKBENCH_READY_REVISION_INVALID", false);
    state.visual.ready = true;
    state.visual.revision = 0;
    return result(state, "OBSERVE", "SESSION_WORKBENCH_READY", true);
  }

  if (type === "VISUAL_OUTCOME") {
    if (!state.visual.ready) return result(state, "DENY", "SESSION_WORKBENCH_NOT_READY", false);
    const semanticOutcome = action.semanticOutcome;
    requireCondition(semanticOutcome === "ACCEPT" || semanticOutcome === "REJECT", "SESSION_VISUAL_OUTCOME_INVALID");
    const revision = Number(action.revision);
    requireCondition(Number.isInteger(revision) && revision >= 0, "SESSION_VISUAL_REVISION_INVALID");
    const eventKey = requireString(action.eventKey, "SESSION_VISUAL_EVENT_KEY_REQUIRED");
    if (state.visual.seenEventKeys.includes(eventKey)) {
      return result(state, "DENY", "SESSION_DUPLICATE_WORKBENCH_EVENT", false);
    }
    if (semanticOutcome === "ACCEPT" && revision !== state.visual.revision + 1) {
      return result(state, "DENY", "SESSION_WORKBENCH_REVISION_OUT_OF_ORDER", false);
    }
    if (semanticOutcome === "REJECT" && revision !== state.visual.revision) {
      return result(state, "DENY", "SESSION_WORKBENCH_REVISION_OUT_OF_ORDER", false);
    }
    state.visual.seenEventKeys.push(eventKey);
    if (semanticOutcome === "ACCEPT") {
      state.visual.acceptedCount += 1;
      state.visual.revision = revision;
      return result(state, "ACCEPT", action.reason || "SESSION_VISUAL_ACCEPTED", true);
    }
    state.visual.rejectedCount += 1;
    return result(state, "REJECT", action.reason || "SESSION_VISUAL_REJECTED", true);
  }

  if (type === "VISUAL_STAGE_COMPLETED") {
    if (state.visual.acceptedCount < 1 || state.visual.rejectedCount < 1) {
      return result(state, "DENY", "SESSION_VISUAL_BOTH_OUTCOMES_REQUIRED", false);
    }
    unlock(state, "core2b");
    return result(state, "OBSERVE", "SESSION_VISUAL_STAGE_COMPLETED", true);
  }

  if (type === "SUMMARY_CREATED") {
    if (!state.core2b.completed) return result(state, "DENY", "SESSION_SUMMARY_BEFORE_TRANSFER_COMPLETION", false);
    if (state.summaryCreated) return result(state, "DENY", "SESSION_DUPLICATE_SUMMARY", false);
    state.summaryCreated = true;
    state.completed = true;
    return result(state, "OBSERVE", "SESSION_SUMMARY_CREATED", true);
  }

  if (type === "RESET") {
    const reset = createInitialMotionSessionState();
    reset.resetCount = (state.resetCount || 0) + 1;
    return result(reset, "OBSERVE", "SESSION_RESET", true);
  }

  throw new MotionSessionError("SESSION_ACTION_UNSUPPORTED", type);
}

function sanitizeRequestedTransition(actionInput) {
  const action = clone(actionInput);
  for (const forbidden of ["response", "answer", "text", "learnerText", "freeResponse"]) {
    if (Object.prototype.hasOwnProperty.call(action, forbidden)) {
      throw new MotionSessionError("SESSION_TRACE_RESPONSE_TEXT_FORBIDDEN", forbidden);
    }
  }
  return action;
}

export function createMotionSessionTraceRecorder({
  runId,
  hostMode,
  identity,
  initialState = createInitialMotionSessionState(),
} = {}) {
  requireString(runId, "SESSION_TRACE_RUN_ID_REQUIRED");
  requireCondition(
    ["repository", "external/embedded", "offline"].includes(hostMode),
    "SESSION_TRACE_HOST_MODE_INVALID",
    String(hostMode),
  );
  let state = clone(initialState);
  let sequence = 0;
  const events = [];

  return {
    get state() { return clone(state); },
    get events() { return clone(events); },
    record(actionInput, {
      eventType = null,
      producer = "session shell",
      componentBoundary = "session-shell",
      parentSequence = null,
    } = {}) {
      const action = sanitizeRequestedTransition(actionInput);
      const before = clone(state);
      const transition = transitionMotionSessionState(state, action);
      state = clone(transition.state);
      sequence += 1;
      const event = {
        trace_version: MOTION_SESSION_TRACE_VERSION,
        run_id: runId,
        sequence,
        logical_time: sequence,
        host_mode: hostMode,
        stage: before.stage,
        event_type: eventType || action.type,
        canonical_refs: canonicalRefs(identity),
        prior_state: before,
        requested_transition: action,
        resulting_state: clone(state),
        outcome: transition.outcome,
        reason_code: transition.reason,
        invariant_checks: clone(transition.invariantChecks),
        producer,
        component_boundary: componentBoundary,
        parent_sequence: parentSequence,
      };
      events.push(event);
      return clone(event);
    },
  };
}

export function replayMotionSessionTrace(eventsInput) {
  const events = clone(eventsInput);
  if (!Array.isArray(events) || events.length === 0) {
    return { ok: false, code: "TRACE_EMPTY", sequence: null, state: createInitialMotionSessionState() };
  }
  let state = createInitialMotionSessionState();
  const runId = events[0]?.run_id;

  for (let index = 0; index < events.length; index += 1) {
    const event = events[index];
    const expectedSequence = index + 1;
    const fail = (code, expected, observed) => ({
      ok: false,
      code,
      sequence: event?.sequence ?? expectedSequence,
      event_type: event?.event_type ?? null,
      component_boundary: event?.component_boundary ?? null,
      expected,
      observed,
      state: clone(state),
    });

    if (event?.trace_version !== MOTION_SESSION_TRACE_VERSION) {
      return fail("TRACE_VERSION_MISMATCH", MOTION_SESSION_TRACE_VERSION, event?.trace_version);
    }
    if (event?.run_id !== runId) return fail("TRACE_RUN_MISMATCH", runId, event?.run_id);
    if (event?.sequence !== expectedSequence) {
      const code = event?.sequence < expectedSequence ? "TRACE_SEQUENCE_DUPLICATE_OR_REWIND" : "TRACE_SEQUENCE_GAP";
      return fail(code, expectedSequence, event?.sequence);
    }
    if (event.parent_sequence != null) {
      if (
        !Number.isInteger(event.parent_sequence)
        || event.parent_sequence < 1
        || event.parent_sequence >= event.sequence
      ) {
        return fail("TRACE_PARENT_SEQUENCE_INVALID", "earlier sequence in same run", event.parent_sequence);
      }
    }
    if (!same(event.prior_state, state)) return fail("TRACE_PRIOR_STATE_MISMATCH", state, event.prior_state);

    let transition;
    try {
      const requested = sanitizeRequestedTransition(event.requested_transition);
      transition = transitionMotionSessionState(state, requested);
    } catch (error) {
      return fail(error?.code || "TRACE_TRANSITION_IMPOSSIBLE", "valid transition", event.requested_transition);
    }
    if (transition.outcome !== event.outcome) return fail("TRACE_OUTCOME_MISMATCH", transition.outcome, event.outcome);
    if (transition.reason !== event.reason_code) return fail("TRACE_REASON_MISMATCH", transition.reason, event.reason_code);
    if (!same(transition.invariantChecks, event.invariant_checks)) {
      return fail("TRACE_INVARIANT_CHECK_MISMATCH", transition.invariantChecks, event.invariant_checks);
    }
    if (!same(transition.state, event.resulting_state)) {
      return fail("TRACE_RESULT_STATE_MISMATCH", transition.state, event.resulting_state);
    }
    state = clone(transition.state);
  }

  return {
    ok: true,
    code: "TRACE_REPLAY_OK",
    sequence: events.length,
    state,
    summary: summarizeMotionSessionState(state),
  };
}

export function summarizeMotionSessionState(stateInput) {
  const state = clone(stateInput);
  return {
    core1b_attempts: state.core1b.attemptCount,
    core1b_support_used: state.core1b.supportUsed,
    visual_accepts: state.visual.acceptedCount,
    visual_rejects: state.visual.rejectedCount,
    core2b_attempts: state.core2b.attemptCount,
    core2b_support_used: state.core2b.supportUsed,
    completed: Boolean(state.completed),
    observation_only: true,
    mastery_claimed: false,
  };
}
