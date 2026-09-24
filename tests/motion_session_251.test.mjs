import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { dirname, extname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

import {
  createInitialMotionSessionState,
  createMotionSessionTraceRecorder,
  replayMotionSessionTrace,
  resolveMotionSessionIdentity,
  transitionMotionSessionState,
} from "../public/motion-session/session-runtime.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const W3C_ELEMENT = "element-6066-11e4-a52e-4f735466cecf";
const W3C_SHADOW = "shadow-6066-11e4-a52e-4f735466cecf";

const MATRIX = "MATRIX-PHY-KIN-2D-MOTION";
const MICROTOPIC = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS";
const CAPABILITY = "CAP-KIN-2D-INDEPENDENT-COMPONENTS";
const CORE1B = "physics:mic-phy-kin-2d-independent-components:core1b";
const CORE2B = "physics:q-phy-kin-2d-2b-projectile-validity-04:core2b";
const REPRESENTATION = "REP-KIN-2D-SHARED-CLOCK";
const RESOURCE = "ACT-KIN-2D-SHARED-CLOCK";
const PACKAGE = "portable-motion-shared-clock";

async function parseWindowAssignment(path) {
  const text = await readFile(path, "utf8");
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  assert.ok(start >= 0 && end > start, `No object assignment found in ${path}`);
  return JSON.parse(text.slice(start, end + 1));
}

test("Issue #251 resolves the exact Motion R1 identity chain from generated data", async () => {
  const web = await parseWindowAssignment(resolve(repo, "public/data/data.js"));
  const core = await parseWindowAssignment(resolve(repo, "public/core-learning/data.js"));
  const identity = resolveMotionSessionIdentity(web, core, {
    subject: "Physics",
    matrixId: MATRIX,
    rung: "R1",
    transferProjectionId: CORE2B,
  });
  assert.deepEqual(identity, {
    subject: "Physics",
    matrixId: MATRIX,
    rung: "R1",
    microtopicRef: MICROTOPIC,
    capabilityRef: CAPABILITY,
    core1bProjectionId: CORE1B,
    representationRef: REPRESENTATION,
    activityRef: RESOURCE,
    portablePackageRef: PACKAGE,
    core2bProjectionId: CORE2B,
    atlasContractVersion: "2.0",
  });
  assert.throws(
    () => resolveMotionSessionIdentity(web, core, {
      subject: "Physics",
      matrixId: "MATRIX-UNKNOWN",
      rung: "R1",
      transferProjectionId: CORE2B,
    }),
    (error) => error?.code === "SESSION_ATLAS_TARGET_NOT_FOUND",
  );
});

function completeTrace(identity) {
  const recorder = createMotionSessionTraceRecorder({
    runId: "unit-run-001",
    hostMode: "repository",
    identity,
  });
  const actions = [
    { type: "SESSION_START" },
    { type: "IDENTITY_RESOLVED" },
    { type: "PACKAGE_LOAD_REQUESTED" },
    { type: "PACKAGE_READY" },
    { type: "WORKBENCH_READY", revision: 0 },
    { type: "NAVIGATE", stage: "core1b" },
    { type: "CORE_ATTEMPT_REJECTED", core: "CORE1B", reason: "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED", responsePresent: false },
    { type: "CORE_ATTEMPT_ACCEPTED", core: "CORE1B", responsePresent: true },
    { type: "CORE_REVEAL_OBSERVED", core: "CORE1B", revealKind: "reconstruction" },
    { type: "CORE_ACTIVITY_COMPLETED", core: "CORE1B" },
    { type: "NAVIGATE", stage: "visual" },
    { type: "VISUAL_OUTCOME", semanticOutcome: "REJECT", revision: 0, eventKey: "reject|0", reason: "TRANSFER_REJECTED" },
    { type: "VISUAL_OUTCOME", semanticOutcome: "ACCEPT", revision: 1, eventKey: "accept|1", reason: "TRANSFER_ACCEPTED" },
    { type: "VISUAL_STAGE_COMPLETED" },
    { type: "NAVIGATE", stage: "core2b" },
    { type: "CORE_ATTEMPT_ACCEPTED", core: "CORE2B", responsePresent: true },
    { type: "CORE_REVEAL_OBSERVED", core: "CORE2B", revealKind: "reasoning" },
    { type: "CORE_ACTIVITY_COMPLETED", core: "CORE2B" },
    { type: "SUMMARY_CREATED" },
    { type: "NAVIGATE", stage: "summary" },
  ];
  for (const action of actions) recorder.record(action);
  return recorder;
}

test("Issue #251 trace replay is deterministic, privacy-safe and observational", () => {
  const identity = {
    matrixId: MATRIX, rung: "R1", microtopicRef: MICROTOPIC, capabilityRef: CAPABILITY,
    core1bProjectionId: CORE1B, representationRef: REPRESENTATION, activityRef: RESOURCE,
    portablePackageRef: PACKAGE, core2bProjectionId: CORE2B,
  };
  const recorder = completeTrace(identity);
  const replay = replayMotionSessionTrace(recorder.events);
  assert.equal(replay.ok, true);
  assert.equal(replay.summary.completed, true);
  assert.equal(replay.summary.mastery_claimed, false);
  assert.equal(replay.summary.observation_only, true);
  assert.equal(replay.summary.visual_accepts, 1);
  assert.equal(replay.summary.visual_rejects, 1);

  const serialized = JSON.stringify(recorder.events);
  assert.doesNotMatch(serialized, /private learner response/i);
  assert.throws(
    () => recorder.record({ type: "SESSION_START", response: "private learner response" }),
    (error) => error?.code === "SESSION_TRACE_RESPONSE_TEXT_FORBIDDEN",
  );

  const gap = structuredClone(recorder.events);
  gap.splice(5, 1);
  const gapReplay = replayMotionSessionTrace(gap);
  assert.equal(gapReplay.ok, false);
  assert.equal(gapReplay.code, "TRACE_SEQUENCE_GAP");
  assert.equal(gapReplay.component_boundary, "session-shell");

  const duplicate = structuredClone(recorder.events);
  duplicate.splice(5, 0, structuredClone(duplicate[4]));
  const duplicateReplay = replayMotionSessionTrace(duplicate);
  assert.equal(duplicateReplay.ok, false);
  assert.equal(duplicateReplay.code, "TRACE_SEQUENCE_DUPLICATE_OR_REWIND");
});

test("Issue #251 stress transitions deny duplicates, out-of-order workbench events and cleanly reset", () => {
  let state = createInitialMotionSessionState();
  const step = (action) => {
    const result = transitionMotionSessionState(state, action);
    state = result.state;
    return result;
  };

  assert.equal(step({ type: "NAVIGATION_REQUESTED", stage: "core1b" }).outcome, "ACCEPT");
  step({ type: "STAGE_EXITED", stage: "orient", nextStage: "core1b" });
  step({ type: "NAVIGATE", stage: "core1b" });
  step({ type: "STAGE_ENTERED", stage: "core1b", previousStage: "orient" });
  assert.equal(step({ type: "CORE_ATTEMPT_REJECTED", core: "CORE1B", reason: "CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED" }).outcome, "DENY");
  assert.equal(state.core1b.attemptCount, 0);
  assert.equal(step({ type: "CORE_ATTEMPT_ACCEPTED", core: "CORE1B", responsePresent: true }).outcome, "OBSERVE");
  assert.equal(step({ type: "CORE_ATTEMPT_ACCEPTED", core: "CORE1B", responsePresent: true }).reason, "SESSION_DUPLICATE_ATTEMPT");
  step({ type: "CORE_REVEAL_OBSERVED", core: "CORE1B" });
  step({ type: "CORE_ACTIVITY_COMPLETED", core: "CORE1B" });
  step({ type: "NAVIGATE", stage: "visual" });
  step({ type: "WORKBENCH_READY", revision: 0 });

  const outOfOrder = step({
    type: "VISUAL_OUTCOME", semanticOutcome: "ACCEPT", revision: 2,
    eventKey: "accepted-too-early", reason: "TRANSFER_ACCEPTED",
  });
  assert.equal(outOfOrder.outcome, "DENY");
  assert.equal(outOfOrder.reason, "SESSION_WORKBENCH_REVISION_OUT_OF_ORDER");

  assert.equal(step({
    type: "VISUAL_OUTCOME", semanticOutcome: "REJECT", revision: 0,
    eventKey: "mixed-0", reason: "TRANSFER_REJECTED",
  }).outcome, "REJECT");
  const duplicate = step({
    type: "VISUAL_OUTCOME", semanticOutcome: "REJECT", revision: 0,
    eventKey: "mixed-0", reason: "TRANSFER_REJECTED",
  });
  assert.equal(duplicate.outcome, "DENY");
  assert.equal(duplicate.reason, "SESSION_DUPLICATE_WORKBENCH_EVENT");

  step({
    type: "VISUAL_OUTCOME", semanticOutcome: "ACCEPT", revision: 1,
    eventKey: "same-1", reason: "TRANSFER_ACCEPTED",
  });
  const reset = step({ type: "RESET" });
  assert.equal(reset.reason, "SESSION_RESET");
  assert.equal(state.stage, "orient");
  assert.equal(state.core1b.attemptCount, 0);
  assert.equal(state.visual.acceptedCount, 0);
  assert.equal(state.visual.rejectedCount, 0);
  assert.equal(state.resetCount, 1);
});

function chromeDriverPath() {
  const candidates = [];
  if (process.env.CHROMEWEBDRIVER) {
    candidates.push(process.env.CHROMEWEBDRIVER);
    candidates.push(resolve(process.env.CHROMEWEBDRIVER, "chromedriver"));
  }
  candidates.push("/usr/local/share/chromedriver-linux64/chromedriver");
  for (const candidate of candidates) {
    try {
      if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
    } catch (_) {}
  }
  const which = spawnSync("which", ["chromedriver"], { encoding: "utf8" });
  return which.status === 0 ? which.stdout.trim() : null;
}

async function freePort() {
  const server = createServer();
  await new Promise((ok, bad) => {
    server.once("error", bad);
    server.listen(0, "127.0.0.1", ok);
  });
  const port = server.address().port;
  await new Promise((ok) => server.close(ok));
  return port;
}

async function startDriver(path) {
  const port = await freePort();
  const child = spawn(path, [`--port=${port}`, "--allowed-origins=*"], { stdio: ["ignore", "pipe", "pipe"] });
  let stderr = "";
  child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
  const base = `http://127.0.0.1:${port}`;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    try {
      const response = await fetch(`${base}/status`);
      if (response.ok) return { child, base };
    } catch (_) {}
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 50));
  }
  child.kill("SIGTERM");
  throw new Error("ChromeDriver did not become ready: " + stderr);
}

async function openStaticServer() {
  const mime = new Map([
    [".html", "text/html; charset=utf-8"], [".js", "text/javascript; charset=utf-8"],
    [".mjs", "text/javascript; charset=utf-8"], [".json", "application/json; charset=utf-8"],
    [".css", "text/css; charset=utf-8"],
  ]);
  const server = createServer(async (request, response) => {
    try {
      const url = new URL(request.url || "/", "http://127.0.0.1");
      const path = resolve(repo, "." + decodeURIComponent(url.pathname));
      if (!(path === repo || path.startsWith(repo + sep))) return response.writeHead(403).end("forbidden");
      const info = await stat(path);
      if (!info.isFile()) throw new Error("not file");
      response.setHeader("content-type", mime.get(extname(path)) || "application/octet-stream");
      response.setHeader("cache-control", "no-store");
      response.end(await readFile(path));
    } catch (_) {
      response.writeHead(404).end("not found");
    }
  });
  await new Promise((ok, bad) => {
    server.once("error", bad);
    server.listen(0, "127.0.0.1", ok);
  });
  return { server, origin: `http://127.0.0.1:${server.address().port}` };
}

class Driver {
  constructor(base) { this.base = base; this.sessionId = null; }
  async request(method, path, body = undefined) {
    const response = await fetch(this.base + path, {
      method,
      headers: body === undefined ? undefined : { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok || payload.value?.error) throw new Error(`WebDriver ${method} ${path}: ${JSON.stringify(payload.value ?? payload)}`);
    return payload.value;
  }
  async open() {
    const value = await this.request("POST", "/session", {
      capabilities: { alwaysMatch: { browserName: "chrome", "goog:chromeOptions": {
        args: ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1280,1000"],
      } } },
    });
    this.sessionId = value.sessionId;
  }
  async close() { if (this.sessionId) { try { await this.request("DELETE", `/session/${this.sessionId}`); } catch (_) {} } this.sessionId = null; }
  async navigate(url) { await this.request("POST", `/session/${this.sessionId}/url`, { url }); }
  async execute(script, args = []) { return this.request("POST", `/session/${this.sessionId}/execute/sync`, { script, args }); }
  async waitFor(script, args = [], timeoutMs = 9000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (await this.execute(script, args)) return;
      await new Promise((r) => setTimeout(r, 60));
    }
    throw new Error("Timed out waiting for: " + script);
  }
  async element(css) {
    const value = await this.request("POST", `/session/${this.sessionId}/element`, { using: "css selector", value: css });
    return value[W3C_ELEMENT];
  }
  async shadowElement(hostCss, innerCss) {
    const host = await this.element(hostCss);
    const shadow = await this.request("GET", `/session/${this.sessionId}/element/${host}/shadow`);
    const value = await this.request("POST", `/session/${this.sessionId}/shadow/${shadow[W3C_SHADOW]}/element`, {
      using: "css selector", value: innerCss,
    });
    return value[W3C_ELEMENT];
  }
  ref(elementId) { return { [W3C_ELEMENT]: elementId }; }
  async sendKeys(elementId, text) {
    await this.request("POST", `/session/${this.sessionId}/element/${elementId}/value`, { text, value: [...text] });
  }
  async click(elementId) { await this.execute("arguments[0].click();", [this.ref(elementId)]); }
  async rect(width, height) { await this.request("POST", `/session/${this.sessionId}/window/rect`, { width, height }); }
}

const driverPath = chromeDriverPath();
if (!driverPath && process.env.GITHUB_ACTIONS === "true") {
  throw new Error("GitHub Actions Issue #251 browser proof requires ChromeDriver.");
}

test("Issue #251 direct learner journey preserves protections, portable semantics and trace privacy", {
  skip: !driverPath,
  timeout: 65000,
}, async () => {
  const staticServer = await openStaticServer();
  const driverProcess = await startDriver(driverPath);
  const driver = new Driver(driverProcess.base);
  try {
    await driver.open();
    const route = `${staticServer.origin}/public/motion-session/index.html`;
    await driver.navigate(route);
    await driver.waitFor("return window.__motionSessionReady === true;");
    const observed = await driver.execute("return window.__motionSessionIdentity;");
    assert.equal(observed.matrixId, MATRIX);
    assert.equal(observed.rung, "R1");
    assert.equal(observed.microtopicRef, MICROTOPIC);
    assert.equal(observed.capabilityRef, CAPABILITY);
    assert.equal(observed.core1bProjectionId, CORE1B);
    assert.equal(observed.representationRef, REPRESENTATION);
    assert.equal(observed.activityRef, RESOURCE);
    assert.equal(observed.portablePackageRef, PACKAGE);
    assert.equal(observed.core2bProjectionId, CORE2B);

    await driver.click(await driver.element("#start-session"));
    await driver.waitFor("return window.__motionSessionState.stage === 'core1b';");
    const navigationTrace = await driver.execute("return window.__motionSessionTrace.slice(-4);");
    assert.deepEqual(navigationTrace.map((e) => e.requested_transition.type), [
      "NAVIGATION_REQUESTED", "STAGE_EXITED", "NAVIGATE", "STAGE_ENTERED",
    ]);
    assert.equal(navigationTrace[0].outcome, "ACCEPT");
    assert.equal(navigationTrace[1].parent_sequence, navigationTrace[0].sequence);
    assert.equal(navigationTrace[2].parent_sequence, navigationTrace[0].sequence);
    assert.equal(navigationTrace[3].parent_sequence, navigationTrace[0].sequence);
    const before = await driver.execute(`
      const learner = document.querySelector("#core1b-learner");
      return { state: learner.state, html: learner.shadowRoot.innerHTML };
    `);
    assert.equal(before.state.reconstructionVisible, false);
    assert.doesNotMatch(before.html, /data-semantic="reconstruction"/);

    const input = await driver.shadowElement("#core1b-learner", "[data-attempt-input]");
    await driver.execute("arguments[0].focus();", [driver.ref(input)]);
    await driver.click(await driver.shadowElement("#core1b-learner", '[data-action="commit"]'));
    await driver.waitFor("return window.__motionSessionTrace.some(e => e.event_type === 'attempt_rejected');");
    assert.equal(await driver.execute("return window.__motionSessionState.core1b.attemptCount;"), 0);
    const deniedReveal = await driver.execute("return window.__motionSessionTrace.find(e => e.requested_transition.type === 'CORE_REVEAL_DENIED' && e.requested_transition.core === 'CORE1B');");
    assert.equal(deniedReveal.outcome, "DENY");
    assert.ok(deniedReveal.parent_sequence);
    assert.equal(await driver.execute("return document.querySelector('#core1b-learner').shadowRoot.activeElement?.dataset?.attemptInput !== undefined;"), true);

    const privateCore1 = "PRIVATE_CORE1_RESPONSE_SENTINEL";
    await driver.sendKeys(input, privateCore1);
    await driver.click(await driver.shadowElement("#core1b-learner", '[data-action="commit"]'));
    await driver.waitFor("return window.__motionSessionState.core1b.revealed === true;");
    assert.equal(await driver.execute("return JSON.stringify(window.__motionSessionTrace).includes('PRIVATE_CORE1_RESPONSE_SENTINEL');"), false);
    const core1Reveal = await driver.execute(`
      const trace = window.__motionSessionTrace;
      const request = trace.find(e => e.requested_transition.type === "CORE_REVEAL_REQUESTED" && e.requested_transition.core === "CORE1B");
      const granted = trace.find(e => e.requested_transition.type === "CORE_REVEAL_OBSERVED" && e.requested_transition.core === "CORE1B");
      return { request, granted };
    `);
    assert.equal(core1Reveal.granted.parent_sequence, core1Reveal.request.sequence);
    await driver.click(await driver.element("#core1b-next"));
    await driver.waitFor("return window.__motionSessionState.stage === 'visual';");

    const mixed = await driver.shadowElement("#shared-clock-workbench", '[data-role="entity"][data-projection-ref="shared-clock-mixed-time-candidate-projection"]');
    const target = await driver.shadowElement("#shared-clock-workbench", '[data-role="target"][data-target-ref="shared-clock-plane-state"]');
    await driver.execute(`
      arguments[0].focus();
      arguments[0].dispatchEvent(new KeyboardEvent("keydown", { key:"Enter", bubbles:true, composed:true }));
    `, [driver.ref(mixed)]);
    await driver.execute(`
      arguments[0].focus();
      arguments[0].dispatchEvent(new KeyboardEvent("keydown", { key:"Enter", bubbles:true, composed:true }));
    `, [driver.ref(target)]);
    await driver.waitFor("return window.__motionSessionState.visual.rejectedCount === 1;");
    assert.match(await driver.execute("return document.querySelector('#shared-clock-workbench').textSummary;"), /single physical state/i);

    const same = await driver.shadowElement("#shared-clock-workbench", '[data-role="entity"][data-projection-ref="shared-clock-same-time-candidate-projection"]');
    const targetAfterReject = await driver.shadowElement("#shared-clock-workbench", '[data-role="target"][data-target-ref="shared-clock-plane-state"]');
    await driver.click(same);
    await driver.click(targetAfterReject);
    await driver.waitFor("return window.__motionSessionState.visual.acceptedCount === 1;");
    assert.match(await driver.execute("return document.querySelector('#shared-clock-workbench').textSummary;"), /simultaneous/i);
    const visualCorrelation = await driver.execute(`
      const trace = window.__motionSessionTrace;
      const requests = trace.filter(e => e.requested_transition.type === "VISUAL_ACTION_REQUESTED");
      const outcomes = trace.filter(e => e.requested_transition.type === "VISUAL_OUTCOME");
      return { requests, outcomes };
    `);
    assert.equal(visualCorrelation.requests.length >= 2, true);
    assert.equal(visualCorrelation.outcomes.length, 2);
    assert.equal(visualCorrelation.outcomes.every(e => visualCorrelation.requests.some(r => r.sequence === e.parent_sequence)), true);
    await driver.click(await driver.element("#visual-next"));
    await driver.waitFor("return window.__motionSessionState.stage === 'core2b';");

    const core2Before = await driver.execute(`
      const learner = document.querySelector("#core2b-learner");
      return { state: learner.state, html: learner.shadowRoot.innerHTML };
    `);
    assert.equal(core2Before.state.reasoningVisible, false);
    assert.doesNotMatch(core2Before.html, /Reject the standard gravity-only projectile specialization/);

    await driver.click(await driver.shadowElement("#core2b-learner", '[data-action="commit"]'));
    await driver.waitFor("return window.__motionSessionTrace.some(e => e.reason_code === 'CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED' && e.requested_transition?.core === 'CORE2B');");
    assert.equal(await driver.execute("return window.__motionSessionState.core2b.attemptCount;"), 0);

    const privateCore2 = "PRIVATE_CORE2_RESPONSE_SENTINEL";
    const input2 = await driver.shadowElement("#core2b-learner", "[data-attempt-input]");
    await driver.sendKeys(input2, privateCore2);
    await driver.click(await driver.shadowElement("#core2b-learner", '[data-action="commit"]'));
    await driver.waitFor("return window.__motionSessionState.core2b.revealed === true;");
    const core2After = await driver.execute("return document.querySelector('#core2b-learner').shadowRoot.innerHTML;");
    assert.match(core2After, /Reject the standard gravity-only projectile specialization/);
    assert.equal(await driver.execute("return JSON.stringify(window.__motionSessionTrace).includes('PRIVATE_CORE2_RESPONSE_SENTINEL');"), false);

    await driver.click(await driver.element("#core2b-next"));
    await driver.waitFor("return window.__motionSessionState.stage === 'summary' && window.__motionSessionState.completed === true;");
    const summaryText = await driver.execute("return document.querySelector('#session-summary').textContent;");
    assert.match(summaryText, /does not infer mastery/i);
    const browserTrace = await driver.execute("return window.__motionSessionTrace;");
    assert.equal(replayMotionSessionTrace(browserTrace).ok, true);
    const packageRequested = browserTrace.find((e) => e.requested_transition.type === "PACKAGE_LOAD_REQUESTED");
    const packageReady = browserTrace.find((e) => e.requested_transition.type === "PACKAGE_READY");
    assert.equal(packageReady.parent_sequence, packageRequested.sequence);

    const oldRun = browserTrace[0].run_id;
    await driver.click(await driver.element("#retry-session"));
    await driver.waitFor("return window.__motionSessionPreviousRuns.length === 1;");
    const retry = await driver.execute("return ({run: window.__motionSessionTrace[0].run_id, previous: window.__motionSessionPreviousRuns[0]});");
    assert.notEqual(retry.run, oldRun);
    assert.equal(retry.previous.replay.ok, true);
    assert.equal(retry.previous.run_id, oldRun);
    const recovery = await driver.execute("return window.__motionSessionTrace.find(e => e.requested_transition.type === 'RECOVERY_STARTED');");
    assert.equal(recovery.requested_transition.previousRunId, oldRun);

    await driver.click(await driver.element("#reset-session"));
    assert.equal(await driver.execute("return window.__motionSessionState.resetCount;"), 1);
    assert.equal(await driver.execute("return window.__motionSessionState.core1b.attemptCount;"), 0);

    await driver.rect(390, 844);
    await driver.waitFor("return window.innerWidth <= 410;");
    assert.equal(await driver.execute("return document.documentElement.scrollWidth <= window.innerWidth + 2;"), true);

    await driver.navigate(`${route}?diagnostic=unknown-identity`);
    await driver.waitFor("return document.querySelector('[data-error-code]')?.textContent === 'SESSION_ATLAS_TARGET_NOT_FOUND';");
    assert.equal(await driver.execute("return document.querySelector('#session-app').hidden;"), true);

    await driver.navigate(`${route}?diagnostic=package-failure`);
    await driver.waitFor("return document.querySelector('[data-error-code]')?.textContent === 'SESSION_PORTABLE_PACKAGE_LOAD_FAILED';");
    assert.equal(await driver.execute("return window.__motionSessionTrace.some(e => e.event_type === 'PACKAGE_LOAD_REQUESTED');"), true);
    assert.equal(await driver.execute("return window.__motionSessionTrace.some(e => e.outcome === 'FAIL');"), true);

    await driver.navigate(`${staticServer.origin}/standalone/motion-session/index.html`);
    await driver.waitFor("return window.__motionSessionReady === true;");
    assert.equal(await driver.execute("return window.__motionSessionTrace[0].host_mode;"), "offline");
    const externalRequests = await driver.execute(`
      return performance.getEntriesByType("resource")
        .map((entry) => new URL(entry.name))
        .filter((url) => url.origin !== location.origin)
        .map((url) => url.href);
    `);
    assert.deepEqual(externalRequests, []);
  } finally {
    await driver.close();
    driverProcess.child.kill("SIGTERM");
    await new Promise((ok) => staticServer.server.close(ok));
  }
});
