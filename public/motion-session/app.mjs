import "../js/core-learning/core-learning-page.mjs";
import { CORE_LEARNER_EVENTS } from "../js/core-learning/core-learning-page.mjs";
import { mountCoreLearningPage } from "../js/core-learning/core-learning-host.mjs";
import "../portable-workbench/semantic-workbench.mjs";
import { mountPortableWorkbench } from "../portable-workbench/portable-host.mjs";
import {
  createInitialMotionSessionState,
  createMotionSessionTraceRecorder,
  replayMotionSessionTrace,
  resolveMotionSessionIdentity,
  summarizeMotionSessionState,
} from "./session-runtime.mjs";

const routeRequest = window.GRADE9V3_SESSION_REQUEST || {};
const SESSION_CASE = Object.freeze({
  subject: routeRequest.subject,
  matrixId: routeRequest.matrix_id,
  rung: routeRequest.rung,
  transferProjectionId: routeRequest.transfer_projection_id,
});

const webData = window.GRADE9V3;
const coreData = window.GRADE9V3_CORE;
const core1b = document.getElementById("core1b-learner");
const core2b = document.getElementById("core2b-learner");
const workbench = document.getElementById("shared-clock-workbench");
const status = document.getElementById("session-status");
const unavailable = document.getElementById("session-unavailable");
const app = document.getElementById("session-app");
const summaryNode = document.getElementById("session-summary");
const visualStatus = document.getElementById("visual-status");
const provenance = document.getElementById("provenance-list");
const navButtons = [...document.querySelectorAll("[data-stage-nav]")];
const stageSections = [...document.querySelectorAll("[data-session-stage]")];
const previousRuns = [];
const diagnosticMode = new URL(location.href).searchParams.get("diagnostic");
let runNumber = 1;
let identity = null;
let packageData = null;
let recorder = null;
let resetting = false;
let packageLoadSequence = null;
let pendingVisualActionSequence = null;
const pendingRevealSequence = { CORE1B: null, CORE2B: null };

function hostMode() {
  if (location.protocol === "file:" || location.pathname.includes("/standalone/")) return "offline";
  if (window.top !== window.self) return "external/embedded";
  return "repository";
}

function runId() {
  return `motion-shared-clock-run-${String(runNumber).padStart(3, "0")}`;
}

function seedIdentity() {
  return {
    matrixId: SESSION_CASE.matrixId,
    rung: SESSION_CASE.rung,
    core2bProjectionId: SESSION_CASE.transferProjectionId,
  };
}

function syncDiagnostics() {
  window.__motionSessionReady = Boolean(
    identity && packageData && recorder && unavailable.hidden && recorder.state.visual.ready
  );
  window.__motionSessionIdentity = identity ? structuredClone(identity) : null;
  window.__motionSessionState = recorder ? recorder.state : null;
  window.__motionSessionTrace = recorder ? recorder.events : [];
  window.__motionSessionPreviousRuns = structuredClone(previousRuns);
}

function record(action, options = {}) {
  const event = recorder.record(action, options);
  syncDiagnostics();
  refresh();
  return event;
}

function setStatus(message) {
  status.textContent = message;
}

function failClosed(error, stage = "SESSION_UNAVAILABLE") {
  const code = error?.code || error?.name || stage;
  unavailable.hidden = false;
  unavailable.querySelector("[data-error-code]").textContent = code;
  unavailable.querySelector("[data-error-detail]").textContent = error?.detail || error?.message || "Required canonical input is unavailable.";
  app.hidden = true;
  setStatus(`Session unavailable: ${code}.`);
  syncDiagnostics();
}

function currentRungRecord() {
  const subject = webData?.subjects?.[identity.subject];
  const matrixMatches = (subject?.matrices || []).filter((row) => row?.matrix_id === identity.matrixId);
  if (matrixMatches.length !== 1) throw Object.assign(new Error("Matrix record unavailable"), { code: "SESSION_MATRIX_RECORD_NOT_FOUND" });
  const rungMatches = (matrixMatches[0]?.rungs || []).filter((row) => row?.rung === identity.rung);
  if (rungMatches.length !== 1) throw Object.assign(new Error("Rung record unavailable"), { code: "SESSION_RUNG_RECORD_NOT_FOUND" });
  return rungMatches[0];
}

function renderCanonicalOrientation() {
  const rung = currentRungRecord();
  document.getElementById("session-topic").textContent = rung.microtopic?.title || "Motion in 2D";
  document.getElementById("orientation-goal").textContent = rung.capability?.action || "";
  document.getElementById("orientation-idea").textContent = rung.microtopic?.inferential_jump || "";
  document.getElementById("visual-title").textContent = packageData?.title || "Shared-clock representation";
  provenance.replaceChildren();
  const refs = [
    ["Atlas", `${identity.matrixId} / ${identity.rung}`],
    ["Microtopic", identity.microtopicRef],
    ["Capability", identity.capabilityRef],
    ["Core1B", identity.core1bProjectionId],
    ["Representation", identity.representationRef],
    ["Activity", identity.activityRef],
    ["Portable package", identity.portablePackageRef],
    ["Core2B transfer", identity.core2bProjectionId],
  ];
  for (const [label, value] of refs) {
    const item = document.createElement("li");
    const strong = document.createElement("strong");
    const code = document.createElement("code");
    strong.textContent = label + ": ";
    code.textContent = value;
    item.append(strong, code);
    provenance.append(item);
  }
}

function stageTitle(stage) {
  return {
    orient: "Session orientation",
    core1b: "Build the shared-clock idea",
    visual: "Test component pairs",
    core2b: "Changed-case transfer",
    summary: "Session summary",
  }[stage] || "Session";
}

function refresh() {
  if (!recorder) return;
  const state = recorder.state;
  for (const section of stageSections) section.hidden = section.dataset.sessionStage !== state.stage;
  for (const button of navButtons) {
    const stage = button.dataset.stageNav;
    button.disabled = !state.unlockedStages.includes(stage);
    button.setAttribute("aria-current", state.stage === stage ? "step" : "false");
  }
  document.getElementById("core1b-next").disabled = state.core1b.attemptCount < 1;
  document.getElementById("visual-next").disabled = state.visual.acceptedCount < 1 || state.visual.rejectedCount < 1;
  document.getElementById("core2b-next").disabled = state.core2b.attemptCount < 1;
  const progress = document.getElementById("session-progress");
  progress.textContent = `${stageTitle(state.stage)}. Stage ${Math.max(1, ["orient","core1b","visual","core2b","summary"].indexOf(state.stage) + 1)} of 5.`;
  visualStatus.textContent = [
    state.visual.ready ? "Representation ready." : "Representation preparing.",
    `Accepted actions observed: ${state.visual.acceptedCount}.`,
    `Rejected actions observed: ${state.visual.rejectedCount}.`,
    workbench?.textSummary || "",
  ].filter(Boolean).join(" ");
  if (state.summaryCreated) renderSummary();
}

function focusStage(stage) {
  queueMicrotask(() => document.querySelector(`[data-session-stage="${stage}"] h2`)?.focus());
}

function navigate(stage, { historyMode = "push" } = {}) {
  const fromStage = recorder.state.stage;
  const request = record(
    { type: "NAVIGATION_REQUESTED", stage },
    { producer: "session shell", componentBoundary: "stage-navigation" },
  );
  if (request.outcome === "DENY") return false;
  record(
    { type: "STAGE_EXITED", stage: fromStage, nextStage: stage },
    { producer: "session shell", componentBoundary: "stage-navigation", parentSequence: request.sequence },
  );
  record(
    { type: "NAVIGATE", stage },
    { producer: "session shell", componentBoundary: "stage-navigation", parentSequence: request.sequence },
  );
  record(
    { type: "STAGE_ENTERED", stage, previousStage: fromStage },
    { producer: "session shell", componentBoundary: "stage-navigation", parentSequence: request.sequence },
  );
  const url = new URL(location.href);
  url.hash = stage;
  const payload = { motionSessionStage: stage };
  if (historyMode === "replace") history.replaceState(payload, "", url);
  else if (historyMode === "push") history.pushState(payload, "", url);
  focusStage(stage);
  return true;
}

function safeCoreEvent(core, type, detail = {}) {
  const boundary = core === "CORE1B" ? "core1b-learner" : "core2b-learner";
  if (type === CORE_LEARNER_EVENTS.ATTEMPT_REJECTED) {
    const attempt = record(
      { type: "CORE_ATTEMPT_REJECTED", core, reason: detail.reason || "CORE_LEARNING_ATTEMPT_REJECTED", responsePresent: Boolean(detail.responsePresent) },
      { eventType: type, producer: "Core learner", componentBoundary: boundary },
    );
    record(
      { type: "CORE_REVEAL_DENIED", core, reason: detail.reason || "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED" },
      { producer: "session shell", componentBoundary: boundary, parentSequence: attempt.sequence },
    );
    return;
  }
  if (type === CORE_LEARNER_EVENTS.ATTEMPT_COMMITTED) {
    const attempt = record(
      { type: "CORE_ATTEMPT_ACCEPTED", core, responsePresent: true },
      { eventType: type, producer: "Core learner", componentBoundary: boundary },
    );
    if (attempt.outcome !== "DENY") {
      const reveal = record(
        { type: "CORE_REVEAL_REQUESTED", core },
        { producer: "session shell", componentBoundary: boundary, parentSequence: attempt.sequence },
      );
      pendingRevealSequence[core] = reveal.sequence;
    }
    return;
  }
  if (type === CORE_LEARNER_EVENTS.SUPPORT_REQUESTED || type === CORE_LEARNER_EVENTS.HINT_REQUESTED) {
    record(
      {
        type: "CORE_SUPPORT_REQUESTED",
        core,
        revealed: detail.revealed === true,
        reason: detail.reason || null,
        supportKind: type === CORE_LEARNER_EVENTS.HINT_REQUESTED ? "hint" : "scaffold",
      },
      { eventType: type, producer: "Core learner", componentBoundary: boundary },
    );
    return;
  }
  if (type === CORE_LEARNER_EVENTS.REVEAL_CHANGED && detail.kind !== "support" && detail.kind !== "hint") {
    record(
      { type: "CORE_REVEAL_OBSERVED", core, revealKind: detail.kind || null },
      {
        eventType: type,
        producer: "Core learner",
        componentBoundary: boundary,
        parentSequence: pendingRevealSequence[core],
      },
    );
    pendingRevealSequence[core] = null;
    return;
  }
  if (type === CORE_LEARNER_EVENTS.ACTIVITY_COMPLETED) {
    record(
      { type: "CORE_ACTIVITY_COMPLETED", core },
      { eventType: type, producer: "Core learner", componentBoundary: boundary },
    );
  }
}

function bindCoreEvents(element, core) {
  for (const type of Object.values(CORE_LEARNER_EVENTS)) {
    element.addEventListener(type, (event) => safeCoreEvent(core, type, event.detail || {}));
  }
}

function workbenchEventKey(detail) {
  const request = detail?.request || {};
  return [
    detail?.type || "UNKNOWN",
    detail?.revision ?? "NA",
    request.sourceEntityRef || "NA",
    request.targetRef || "NA",
    request.operation || "NA",
  ].join("|");
}

function onWorkbenchEvent(event) {
  if (!recorder || resetting) return;
  const detail = event.detail || {};
  if (detail.type === "WORKBENCH_READY") {
    record(
      { type: "WORKBENCH_READY", revision: detail.revision ?? 0 },
      { producer: "semantic workbench", componentBoundary: "shared-clock-workbench" },
    );
    return;
  }
  if (detail.type === "ENTITY_PICKED") {
    const requested = record(
      {
        type: "VISUAL_ACTION_REQUESTED",
        sourceEntityRef: detail.entityRef || detail.request?.sourceEntityRef || null,
        revision: detail.revision ?? workbench.snapshot?.revision ?? 0,
      },
      { producer: "semantic workbench", componentBoundary: "shared-clock-workbench" },
    );
    pendingVisualActionSequence = requested.sequence;
    return;
  }
  if (detail.type === "INTERACTION_CANCELLED") {
    pendingVisualActionSequence = null;
    return;
  }
  if (detail.type === "TRANSFER_ACCEPTED" || detail.type === "TRANSFER_REJECTED") {
    const semanticOutcome = detail.type === "TRANSFER_ACCEPTED" ? "ACCEPT" : "REJECT";
    record(
      {
        type: "VISUAL_OUTCOME",
        semanticOutcome,
        revision: detail.revision,
        eventKey: workbenchEventKey(detail),
        reason: detail.code || detail.type,
      },
      {
        producer: "semantic workbench",
        componentBoundary: "shared-clock-workbench",
        parentSequence: pendingVisualActionSequence,
      },
    );
    pendingVisualActionSequence = null;
  }
}

function configureCore() {
  mountCoreLearningPage(core1b, coreData, identity.core1bProjectionId, window.CORE_LEARNING_REGISTRIES || {});
  mountCoreLearningPage(core2b, coreData, identity.core2bProjectionId, window.CORE_LEARNING_REGISTRIES || {});
}

function mountWorkbench() {
  resetting = true;
  mountPortableWorkbench(workbench, packageData);
  resetting = false;
  const ready = workbench.snapshot != null;
  if (ready) {
    record(
      { type: "WORKBENCH_READY", revision: workbench.snapshot?.revision ?? 0 },
      { producer: "semantic workbench", componentBoundary: "shared-clock-workbench" },
    );
  }
}

function renderSummary() {
  const summary = summarizeMotionSessionState(recorder.state);
  const rows = [
    ["Core1B attempts", summary.core1b_attempts],
    ["Core1B support used", summary.core1b_support_used],
    ["Shared-clock accepted actions", summary.visual_accepts],
    ["Shared-clock rejected actions", summary.visual_rejects],
    ["Core2B attempts", summary.core2b_attempts],
    ["Core2B support used", summary.core2b_support_used],
    ["Session completion", summary.completed ? "complete" : "in progress"],
  ];
  summaryNode.replaceChildren();
  for (const [label, value] of rows) {
    const row = document.createElement("div");
    row.className = "summary-row";
    const dt = document.createElement("strong");
    const dd = document.createElement("span");
    dt.textContent = label;
    dd.textContent = String(value);
    row.append(dt, dd);
    summaryNode.append(row);
  }
  const note = document.createElement("p");
  note.className = "observation-note";
  note.textContent = "This summary reports only actions observed in this session. It does not infer mastery, readiness, ability, or a score.";
  summaryNode.append(note);
}

async function loadPackage() {
  const requested = record(
    { type: "PACKAGE_LOAD_REQUESTED" },
    { producer: "session shell", componentBoundary: "portable-package-loader" },
  );
  packageLoadSequence = requested.sequence;
  if (diagnosticMode === "package-failure") {
    throw Object.assign(new Error("Diagnostic package failure"), { code: "SESSION_PORTABLE_PACKAGE_LOAD_FAILED" });
  }
  const ref = identity.portablePackageRef;
  if (!/^[a-z0-9][a-z0-9-]*$/i.test(ref)) {
    throw Object.assign(new Error("Unsafe portable package reference"), { code: "SESSION_PORTABLE_PACKAGE_REF_INVALID" });
  }
  const url = new URL(`../portable-workbench/packages/${ref}.json`, import.meta.url);
  const response = await fetch(url);
  if (!response.ok) throw Object.assign(new Error(`Package load returned HTTP ${response.status}`), { code: "SESSION_PORTABLE_PACKAGE_LOAD_FAILED" });
  const pkg = await response.json();
  if (pkg.id !== identity.portablePackageRef) throw Object.assign(new Error("Portable package ID mismatch"), { code: "SESSION_PORTABLE_PACKAGE_ID_MISMATCH" });
  if (pkg.resourceRef !== identity.activityRef) throw Object.assign(new Error("Portable resource binding mismatch"), { code: "SESSION_PORTABLE_RESOURCE_MISMATCH" });
  if (pkg.provenance?.representationRef !== identity.representationRef) throw Object.assign(new Error("Portable representation binding mismatch"), { code: "SESSION_PORTABLE_REPRESENTATION_MISMATCH" });
  packageData = pkg;
  record(
    { type: "PACKAGE_READY" },
    {
      producer: "session shell",
      componentBoundary: "portable-package-loader",
      parentSequence: packageLoadSequence,
    },
  );
  packageLoadSequence = null;
}

function resetCurrentRun() {
  record({ type: "RESET" }, { producer: "session shell", componentBoundary: "session-reset" });
  configureCore();
  mountWorkbench();
  history.replaceState({ motionSessionStage: "orient" }, "", new URL(location.href).pathname + "#orient");
  refresh();
  focusStage("orient");
}

function retryNewRun() {
  const previousRunId = runId();
  record({ type: "RETRY_REQUESTED" }, { producer: "session shell", componentBoundary: "session-retry" });
  const replay = replayMotionSessionTrace(recorder.events);
  previousRuns.push({ run_id: previousRunId, trace: recorder.events, replay });
  runNumber += 1;
  recorder = createMotionSessionTraceRecorder({
    runId: runId(),
    hostMode: hostMode(),
    identity,
    initialState: createInitialMotionSessionState(),
  });
  record({ type: "SESSION_START" }, { producer: "session shell", componentBoundary: "session-shell" });
  record(
    { type: "RECOVERY_STARTED", previousRunId },
    { producer: "session shell", componentBoundary: "session-retry" },
  );
  record({ type: "IDENTITY_RESOLVED" }, { producer: "session shell", componentBoundary: "identity-resolver" });
  record({ type: "PACKAGE_READY" }, { producer: "session shell", componentBoundary: "portable-package-loader" });
  configureCore();
  mountWorkbench();
  history.replaceState({ motionSessionStage: "orient" }, "", new URL(location.href).pathname + "#orient");
  refresh();
  focusStage("orient");
}

function exportTrace() {
  record({ type: "TRACE_EXPORTED" }, { producer: "session shell", componentBoundary: "trace-export" });
  const bundle = {
    format: "GRADE9V3_MOTION_SESSION_DIAGNOSTIC_TRACE",
    trace_version: "1.0",
    exported_locally: true,
    privacy: "No learner response text or PII is included.",
    previous_runs: structuredClone(previousRuns),
    current_run: {
      run_id: runId(),
      trace: recorder.events,
      replay: replayMotionSessionTrace(recorder.events),
    },
  };
  const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${runId()}-diagnostic-trace.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function wireActions() {
  document.getElementById("start-session").addEventListener("click", () => navigate("core1b"));
  document.getElementById("core1b-next").addEventListener("click", () => {
    if (!recorder.state.core1b.completed) core1b.completeActivity();
    if (recorder.state.core1b.completed) navigate("visual");
  });
  document.getElementById("visual-next").addEventListener("click", () => {
    const event = record(
      { type: "VISUAL_STAGE_COMPLETED" },
      { producer: "session shell", componentBoundary: "shared-clock-workbench" },
    );
    if (event.outcome !== "DENY") navigate("core2b");
  });
  document.getElementById("core2b-next").addEventListener("click", () => {
    if (!recorder.state.core2b.completed) core2b.completeActivity();
    if (!recorder.state.core2b.completed) return;
    const event = record(
      { type: "SUMMARY_CREATED" },
      { producer: "session shell", componentBoundary: "session-summary" },
    );
    if (event.outcome !== "DENY") navigate("summary");
  });
  document.getElementById("reset-session").addEventListener("click", resetCurrentRun);
  document.getElementById("retry-session").addEventListener("click", retryNewRun);
  document.getElementById("export-trace").addEventListener("click", exportTrace);
  for (const button of navButtons) {
    button.addEventListener("click", () => navigate(button.dataset.stageNav));
  }
  addEventListener("popstate", (event) => {
    const target = event.state?.motionSessionStage;
    if (!target || target === recorder.state.stage) return;
    const moved = navigate(target, { historyMode: "none" });
    if (!moved) history.replaceState({ motionSessionStage: recorder.state.stage }, "", "#" + recorder.state.stage);
  });
}

async function init() {
  const selection = diagnosticMode === "unknown-identity"
    ? { ...SESSION_CASE, rung: "__diagnostic_unknown_rung__" }
    : SESSION_CASE;

  try {
    if (coreData?.publication_gate?.status === "HOLD") {
      throw Object.assign(
        new Error("Public Core learner sessions require independently authorized release grants."),
        { code: "NO_INDEPENDENT_CORE_PUBLICATION_GRANT",
          detail: "This Core activity is an internal compiler preview, not released learner content." },
      );
    }
    identity = resolveMotionSessionIdentity(webData, coreData, selection);
    recorder = createMotionSessionTraceRecorder({
      runId: runId(),
      hostMode: hostMode(),
      identity,
      initialState: createInitialMotionSessionState(),
    });
    record({ type: "SESSION_START" }, { producer: "session shell", componentBoundary: "session-shell" });
    record({ type: "IDENTITY_RESOLVED" }, { producer: "session shell", componentBoundary: "identity-resolver" });
    bindCoreEvents(core1b, "CORE1B");
    bindCoreEvents(core2b, "CORE2B");
    workbench.addEventListener("semantic-workbench-event", onWorkbenchEvent);
    configureCore();
    await loadPackage();
    renderCanonicalOrientation();
    if (diagnosticMode === "workbench-delay") {
      app.hidden = false;
      unavailable.hidden = true;
      record(
        { type: "WORKBENCH_WAITING" },
        { producer: "session shell", componentBoundary: "shared-clock-workbench" },
      );
      setStatus("Shared-clock representation is preparing…");
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 250));
    }
    mountWorkbench();
    wireActions();
    app.hidden = false;
    unavailable.hidden = true;
    history.replaceState({ motionSessionStage: "orient" }, "", "#orient");
    setStatus("Motion in 2D shared-clock session ready.");
    refresh();
    syncDiagnostics();
    window.__motionSessionReady = true;
  } catch (error) {
    if (!recorder) {
      recorder = createMotionSessionTraceRecorder({
        runId: runId(),
        hostMode: hostMode(),
        identity: seedIdentity(),
        initialState: createInitialMotionSessionState(),
      });
      recorder.record({ type: "SESSION_START" }, { producer: "session shell", componentBoundary: "session-shell" });
      recorder.record(
        { type: "IDENTITY_RESOLUTION_FAILED", reason: error?.code || "SESSION_IDENTITY_RESOLUTION_FAILED" },
        { producer: "session shell", componentBoundary: "identity-resolver" },
      );
    } else {
      try {
        recorder.record(
          { type: "PACKAGE_LOAD_FAILED", reason: error?.code || "SESSION_PACKAGE_LOAD_FAILED" },
          {
            producer: "session shell",
            componentBoundary: "portable-package-loader",
            parentSequence: packageLoadSequence,
          },
        );
      } catch (_) {}
    }
    failClosed(error);
  }
}

init();
