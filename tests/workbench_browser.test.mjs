import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { dirname, extname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const W3C_ELEMENT = "element-6066-11e4-a52e-4f735466cecf";
const W3C_SHADOW = "shadow-6066-11e4-a52e-4f735466cecf";
const ENTER = "\uE007";
const SPACE = "\uE00D";
const ESCAPE = "\uE00C";
const CONTROL = "\uE009";

function chromeDriverPath() {
  const env = process.env.CHROMEWEBDRIVER;
  const candidates = [];
  if (env) {
    candidates.push(env);
    candidates.push(join(env, "chromedriver"));
  }
  candidates.push("/usr/local/share/chromedriver-linux64/chromedriver");
  for (const candidate of candidates) {
    try {
      if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
    } catch (_) { /* continue */ }
  }
  const which = spawnSync("which", ["chromedriver"], { encoding: "utf8" });
  return which.status === 0 ? which.stdout.trim() : null;
}

async function openStaticServer() {
  const mime = new Map([
    [".html", "text/html; charset=utf-8"],
    [".js", "text/javascript; charset=utf-8"],
    [".mjs", "text/javascript; charset=utf-8"],
    [".json", "application/json; charset=utf-8"],
    [".css", "text/css; charset=utf-8"],
  ]);
  const server = createServer(async (request, response) => {
    try {
      const url = new URL(request.url || "/", "http://127.0.0.1");
      const requested = url.pathname === "/"
        ? "/tests/fixtures/workbench/browser-host.html"
        : decodeURIComponent(url.pathname);
      const path = resolve(repo, `.${requested}`);
      if (!(path === repo || path.startsWith(repo + sep))) {
        response.writeHead(403).end("forbidden");
        return;
      }
      const info = await stat(path);
      if (!info.isFile()) throw new Error("not a file");
      response.setHeader("content-type", mime.get(extname(path)) || "application/octet-stream");
      response.setHeader("cache-control", "no-store");
      response.end(await readFile(path));
    } catch (_) {
      response.writeHead(404).end("not found");
    }
  });
  await new Promise((resolveListen, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolveListen);
  });
  const { port } = server.address();
  return { server, origin: `http://127.0.0.1:${port}` };
}

async function freePort() {
  const server = createServer();
  await new Promise((resolveListen, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolveListen);
  });
  const port = server.address().port;
  await new Promise((resolveClose) => server.close(resolveClose));
  return port;
}

async function startDriver(path) {
  const port = await freePort();
  const child = spawn(path, [`--port=${port}`, "--allowed-origins=*"], {
    stdio: ["ignore", "pipe", "pipe"],
  });
  let stderr = "";
  child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
  const base = `http://127.0.0.1:${port}`;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (child.exitCode != null) throw new Error(`ChromeDriver exited early: ${stderr}`);
    try {
      const response = await fetch(`${base}/status`);
      if (response.ok) return { child, base };
    } catch (_) { /* not ready */ }
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 50));
  }
  child.kill("SIGTERM");
  throw new Error(`ChromeDriver did not become ready: ${stderr}`);
}

class WebDriver {
  constructor(base) {
    this.base = base;
    this.sessionId = null;
  }

  async request(method, path, body = undefined) {
    const response = await fetch(`${this.base}${path}`, {
      method,
      headers: body === undefined ? undefined : { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok || payload.value?.error) {
      throw new Error(`WebDriver ${method} ${path} failed: ${JSON.stringify(payload.value ?? payload)}`);
    }
    return payload.value;
  }

  async open() {
    const value = await this.request("POST", "/session", {
      capabilities: {
        alwaysMatch: {
          browserName: "chrome",
          "goog:chromeOptions": {
            args: ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1200,900"],
          },
        },
      },
    });
    this.sessionId = value.sessionId;
  }

  async close() {
    if (!this.sessionId) return;
    try { await this.request("DELETE", `/session/${this.sessionId}`); } catch (_) { /* cleanup */ }
    this.sessionId = null;
  }

  async navigate(url) {
    await this.request("POST", `/session/${this.sessionId}/url`, { url });
  }

  async execute(script, args = []) {
    return this.request("POST", `/session/${this.sessionId}/execute/sync`, { script, args });
  }

  async waitFor(script, args = [], timeoutMs = 5000) {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (await this.execute(script, args)) return;
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 50));
    }
    throw new Error(`Timed out waiting for browser condition: ${script}`);
  }

  async element(css) {
    const value = await this.request("POST", `/session/${this.sessionId}/element`, {
      using: "css selector",
      value: css,
    });
    return value[W3C_ELEMENT];
  }

  async shadow(hostElementId) {
    const value = await this.request("GET", `/session/${this.sessionId}/element/${hostElementId}/shadow`);
    return value[W3C_SHADOW];
  }

  async shadowElement(hostCss, innerCss) {
    const host = await this.element(hostCss);
    const shadow = await this.shadow(host);
    const value = await this.request("POST", `/session/${this.sessionId}/shadow/${shadow}/element`, {
      using: "css selector",
      value: innerCss,
    });
    return value[W3C_ELEMENT];
  }

  ref(elementId) {
    return { [W3C_ELEMENT]: elementId };
  }

  async browserClick(elementId) {
    await this.execute("arguments[0].click();", [this.ref(elementId)]);
  }

  async sendKeys(elementId, text) {
    await this.request("POST", `/session/${this.sessionId}/element/${elementId}/value`, { text, value: [...text] });
  }

  async pointerTransfer(pointerType, sourceId, targetId) {
    const source = {
      type: "pointer",
      id: `${pointerType}-semantic-transfer`,
      parameters: { pointerType },
      actions: [
        { type: "pointerMove", duration: 0, origin: this.ref(sourceId), x: 0, y: 0 },
        { type: "pointerDown", button: 0 },
      ],
    };
    await this.request("POST", `/session/${this.sessionId}/actions`, { actions: [source] });
    const target = {
      type: "pointer",
      id: `${pointerType}-semantic-transfer`,
      parameters: { pointerType },
      actions: [
        { type: "pointerMove", duration: 100, origin: this.ref(targetId), x: 0, y: 0 },
        { type: "pointerUp", button: 0 },
      ],
    };
    await this.request("POST", `/session/${this.sessionId}/actions`, { actions: [target] });
    await this.request("DELETE", `/session/${this.sessionId}/actions`);
  }

  async setWindow(width, height) {
    await this.request("POST", `/session/${this.sessionId}/window/rect`, { width, height, x: 0, y: 0 });
  }

  async cdp(command, params) {
    return this.request("POST", `/session/${this.sessionId}/chromium/send_command`, { cmd: command, params });
  }
}

function semanticProjection(snapshot) {
  return {
    revision: snapshot.revision,
    entities: snapshot.entities,
    projections: snapshot.projections,
    canonicalTransformations: snapshot.canonicalTransformations,
    pickedEntityRef: snapshot.interaction.pickedEntityRef,
    preview: snapshot.interaction.preview,
  };
}

const driverPath = chromeDriverPath();
const browserRequired = process.env.GITHUB_ACTIONS === "true";

if (!driverPath && browserRequired) {
  throw new Error("GitHub Actions browser proof requires ChromeDriver, but no CHROMEWEBDRIVER/chromedriver binary was found.");
}

test("real browser semantic interaction contract", { skip: !driverPath, timeout: 30000 }, async () => {
  const staticServer = await openStaticServer();
  const driverProcess = await startDriver(driverPath);
  const driver = new WebDriver(driverProcess.base);
  try {
    await driver.open();
    await driver.navigate(`${staticServer.origin}/tests/fixtures/workbench/browser-host.html`);
    await driver.waitFor("return window.__workbenchReady === true;");

    const initialSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(initialSummary, /No source selected\./);
    assert.match(initialSummary, /156 ÷ 12 \[division expression\]/);
    assert.match(initialSummary, /156 in long-division working form \[working dividend\]/);

    const sourceSelector = '[data-role="entity"][data-projection-ref="dividend-expression"]';
    const linkedSelector = '[data-role="entity"][data-projection-ref="dividend-place-value"]';
    const targetSelector = '[data-role="target"][data-target-ref="quotient-first-digit"]';

    const runFresh = async (id, interaction) => {
      await driver.execute("window.workbenchHarness.reset(arguments[0]);", [id]);
      await driver.waitFor("return window.workbenchHarness.snapshot(arguments[0])?.revision === 0;", [id], 3000);
      await interaction();
      return driver.execute("return window.workbenchHarness.snapshot(arguments[0]);", [id]);
    };

    await driver.execute("window.workbenchHarness.reset('primary');");
    const inspectOrigin = await driver.shadowElement("#primary", sourceSelector);
    await driver.execute("arguments[0].focus();", [driver.ref(inspectOrigin)]);
    const inspectLinked = await driver.shadowElement("#primary", linkedSelector);
    const focusCorrespondence = await driver.execute(`
      const origin = arguments[0];
      const linked = arguments[1];
      const events = window.workbenchHarness.events('primary');
      const inspected = [...events].reverse().find((event) => event.type === 'ENTITY_INSPECTED');
      return {
        originState: origin.dataset.correspondenceState,
        linkedState: linked.dataset.correspondenceState,
        originLabel: origin.querySelector('.entity-state')?.textContent,
        linkedLabel: linked.querySelector('.entity-state')?.textContent,
        inspected,
        serialized: JSON.stringify(inspected),
      };
    `, [driver.ref(inspectOrigin), driver.ref(inspectLinked)]);
    assert.equal(focusCorrespondence.originState, "origin");
    assert.equal(focusCorrespondence.linkedState, "linked");
    assert.equal(focusCorrespondence.originLabel, "Inspected representation");
    assert.equal(focusCorrespondence.linkedLabel, "Linked representation");
    assert.equal(focusCorrespondence.inspected.projectionRef, "dividend-expression");
    assert.deepEqual(focusCorrespondence.inspected.linkedProjectionRefs, ["dividend-expression", "dividend-place-value"]);
    assert.match(focusCorrespondence.serialized, /ENTITY_INSPECTED/);
    const inspectedSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(inspectedSummary, /Inspecting 156 ÷ 12\./);

    await driver.execute(
      "arguments[0].dispatchEvent(new PointerEvent('pointerover', {bubbles:true, composed:true, pointerType:'mouse'}));",
      [driver.ref(inspectLinked)]
    );
    const hoverCorrespondence = await driver.execute(`
      return {
        first: arguments[0].dataset.correspondenceState,
        second: arguments[1].dataset.correspondenceState,
      };
    `, [driver.ref(inspectOrigin), driver.ref(inspectLinked)]);
    assert.equal(hoverCorrespondence.first, "linked");
    assert.equal(hoverCorrespondence.second, "origin");

    const clickState = await runFresh("primary", async () => {
      const source = await driver.shadowElement("#primary", sourceSelector);
      await driver.browserClick(source);
      const target = await driver.shadowElement("#primary", targetSelector);
      await driver.browserClick(target);
    });

    const keyboardState = await runFresh("primary", async () => {
      const source = await driver.shadowElement("#primary", sourceSelector);
      await driver.sendKeys(source, SPACE);
      const target = await driver.shadowElement("#primary", targetSelector);
      await driver.sendKeys(target, ENTER);
    });

    const mouseState = await runFresh("primary", async () => {
      const source = await driver.shadowElement("#primary", sourceSelector);
      await driver.request("POST", `/session/${driver.sessionId}/actions`, { actions: [{
        type: "pointer", id: "mouse-semantic-transfer", parameters: { pointerType: "mouse" }, actions: [
          { type: "pointerMove", duration: 0, origin: driver.ref(source), x: 0, y: 0 },
          { type: "pointerDown", button: 0 },
        ],
      }] });
      const target = await driver.shadowElement("#primary", targetSelector);
      await driver.request("POST", `/session/${driver.sessionId}/actions`, { actions: [{
        type: "pointer", id: "mouse-semantic-transfer", parameters: { pointerType: "mouse" }, actions: [
          { type: "pointerMove", duration: 100, origin: driver.ref(target), x: 0, y: 0 },
          { type: "pointerUp", button: 0 },
        ],
      }] });
      await driver.request("DELETE", `/session/${driver.sessionId}/actions`);
    });

    const touchState = await runFresh("primary", async () => {
      const source = await driver.shadowElement("#primary", sourceSelector);
      await driver.request("POST", `/session/${driver.sessionId}/actions`, { actions: [{
        type: "pointer", id: "touch-source-pick", parameters: { pointerType: "touch" }, actions: [
          { type: "pointerMove", duration: 0, origin: driver.ref(source), x: 0, y: 0 },
          { type: "pointerDown", button: 0 },
          { type: "pointerUp", button: 0 },
        ],
      }] });
      await driver.request("DELETE", `/session/${driver.sessionId}/actions`);

      const target = await driver.shadowElement("#primary", targetSelector);
      await driver.request("POST", `/session/${driver.sessionId}/actions`, { actions: [{
        type: "pointer", id: "touch-target-drop", parameters: { pointerType: "touch" }, actions: [
          { type: "pointerMove", duration: 0, origin: driver.ref(target), x: 0, y: 0 },
          { type: "pointerDown", button: 0 },
          { type: "pointerUp", button: 0 },
        ],
      }] });
      await driver.request("DELETE", `/session/${driver.sessionId}/actions`);
    });

    assert.deepEqual(semanticProjection(clickState), semanticProjection(keyboardState));
    assert.deepEqual(semanticProjection(keyboardState), semanticProjection(mouseState));
    assert.deepEqual(semanticProjection(mouseState), semanticProjection(touchState));
    assert.equal(clickState.entities.some((row) => row.id === "quotient-digit-1"), true);

    await driver.execute("window.workbenchHarness.reset('primary');");
    const sourceForCancel = await driver.shadowElement("#primary", sourceSelector);
    await driver.sendKeys(sourceForCancel, SPACE);
    const picked = await driver.execute("return window.workbenchHarness.snapshot('primary').interaction.pickedEntityRef;");
    assert.equal(picked, "dividend-156");
    const pickedSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(pickedSummary, /Selected source 156\./);
    const sourceForEscape = await driver.shadowElement("#primary", sourceSelector);
    await driver.sendKeys(sourceForEscape, ESCAPE);
    const cancelled = await driver.execute("return window.workbenchHarness.snapshot('primary');");
    assert.equal(cancelled.interaction.pickedEntityRef, null);
    assert.equal(cancelled.revision, 0);

    const sourceForUndo = await driver.shadowElement("#primary", sourceSelector);
    await driver.browserClick(sourceForUndo);
    const targetForUndo = await driver.shadowElement("#primary", targetSelector);
    await driver.browserClick(targetForUndo);
    const committedSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(committedSummary, /Revision 1\./);
    assert.match(committedSummary, /1 \[quotient digit\]/);
    const undoButton = await driver.shadowElement("#primary", '[data-action="undo"]');
    await driver.browserClick(undoButton);
    const undone = await driver.execute("return window.workbenchHarness.snapshot('primary');");
    assert.equal(undone.entities.some((row) => row.id === "quotient-digit-1"), false);
    assert.equal(undone.interaction.pickedEntityRef, null);
    const undoneSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(undoneSummary, /Revision 2\./);
    assert.doesNotMatch(undoneSummary, /\[quotient digit\]/);

    const redoButton = await driver.shadowElement("#primary", '[data-action="redo"]');
    assert.equal(await driver.execute("return arguments[0].disabled;", [driver.ref(redoButton)]), false);
    await driver.browserClick(redoButton);
    const redone = await driver.execute("return window.workbenchHarness.snapshot('primary');");
    assert.equal(redone.entities.some((row) => row.id === "quotient-digit-1"), true);
    assert.equal(redone.revision, 3);
    const redoneSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(redoneSummary, /Revision 3\./);
    assert.match(redoneSummary, /1 \[quotient digit\]/);

    const undoAgain = await driver.shadowElement("#primary", '[data-action="undo"]');
    await driver.browserClick(undoAgain);
    const transientSource = await driver.shadowElement("#primary", sourceSelector);
    await driver.browserClick(transientSource);
    const cancelButton = await driver.shadowElement("#primary", '[data-action="cancel"]');
    await driver.browserClick(cancelButton);
    const redoAfterTransient = await driver.shadowElement("#primary", '[data-action="redo"]');
    assert.equal(await driver.execute("return arguments[0].disabled;", [driver.ref(redoAfterTransient)]), false);

    const branchSource = await driver.shadowElement("#primary", sourceSelector);
    await driver.browserClick(branchSource);
    const branchTarget = await driver.shadowElement("#primary", targetSelector);
    await driver.browserClick(branchTarget);
    const redoAfterBranch = await driver.shadowElement("#primary", '[data-action="redo"]');
    assert.equal(await driver.execute("return arguments[0].disabled;", [driver.ref(redoAfterBranch)]), true);

    await driver.execute("window.workbenchHarness.reset('primary'); window.workbenchHarness.reset('secondary');");
    const isolationSource = await driver.shadowElement("#primary", sourceSelector);
    await driver.browserClick(isolationSource);
    const isolationTarget = await driver.shadowElement("#primary", targetSelector);
    await driver.browserClick(isolationTarget);
    const isolated = await driver.execute("return [window.workbenchHarness.snapshot('primary'), window.workbenchHarness.snapshot('secondary')];");
    assert.equal(isolated[0].revision, 1);
    assert.equal(isolated[1].revision, 0);
    assert.equal(isolated[1].entities.some((row) => row.id === "quotient-digit-1"), false);

    await driver.setWindow(420, 900);
    await driver.execute("window.workbenchHarness.reset('primary'); document.querySelector('#primary').style.width='320px';");
    await new Promise((resolveDelay) => setTimeout(resolveDelay, 100));
    const beforeResponsive = await driver.execute("return window.workbenchHarness.snapshot('primary');");
    const narrow = await driver.execute("return window.workbenchHarness.metrics('primary');");
    assert.deepEqual(narrow.columnCounts, [1, 1]);
    assert.ok(Math.abs(narrow.sourceLeft - narrow.targetLeft) < 2, JSON.stringify(narrow));
    assert.ok(Math.abs(narrow.targetTop - narrow.sourceTop) > 40, JSON.stringify(narrow));
    assert.notEqual(narrow.sourceGrid, narrow.targetGrid);
    const afterResponsive = await driver.execute("return window.workbenchHarness.snapshot('primary');");
    assert.deepEqual(afterResponsive, beforeResponsive);

    await driver.cdp("Emulation.setEmulatedMedia", {
      media: "",
      features: [{ name: "prefers-reduced-motion", value: "reduce" }],
    });
    const reduced = await driver.execute("return window.workbenchHarness.metrics('primary');");
    assert.equal(reduced.reducedMotion, true);
    assert.equal(reduced.transitionDuration, "0s");
    assert.equal(reduced.animationName, "none");

    await driver.execute("window.workbenchHarness.reset('primary');");
    const previewSource = await driver.shadowElement("#primary", sourceSelector);
    await driver.browserClick(previewSource);
    const previewTarget = await driver.shadowElement("#primary", targetSelector);
    await driver.execute("arguments[0].dispatchEvent(new PointerEvent('pointerover', {bubbles:true, composed:true, pointerType:'mouse'}));", [driver.ref(previewTarget)]);
    const previewText = await driver.execute("return arguments[0].querySelector('small')?.textContent;", [driver.ref(await driver.shadowElement("#primary", targetSelector))]);
    assert.equal(previewText, "Available");
    const previewSummary = await driver.execute("return window.workbenchHarness.textSummary('primary');");
    assert.match(previewSummary, /Target First quotient digit: available\./);
  } finally {
    await driver.close();
    driverProcess.child.kill("SIGTERM");
    await new Promise((resolveClose) => staticServer.server.close(resolveClose));
  }
});


test("real browser preserves distinct intermediate semantic identity through undo and redo", { skip: !driverPath, timeout: 30000 }, async () => {
  const staticServer = await openStaticServer();
  const driverProcess = await startDriver(driverPath);
  const driver = new WebDriver(driverProcess.base);
  try {
    await driver.open();
    await driver.navigate(`${staticServer.origin}/tests/fixtures/workbench/browser-semantic-identity-host.html`);
    await driver.waitFor("return window.__identityReady === true;");

    const initial = await driver.execute("return window.identityHarness.snapshot();");
    assert.equal(initial.entities.some((row) => row.id === "partial-dividend-15"), false);
    assert.equal(initial.projections.some((row) => row.entityRef === "dividend-156" && row.label === "15"), false);

    const dividend = await driver.shadowElement("#identity", '[data-role="entity"][data-projection-ref="dividend-expression"]');
    await driver.browserClick(dividend);
    const partialTarget = await driver.shadowElement("#identity", '[data-role="target"][data-target-ref="partial-dividend-first"]');
    await driver.browserClick(partialTarget);
    await driver.waitFor("return window.identityHarness.snapshot().revision === 1;");

    const afterPartial = await driver.execute("return window.identityHarness.snapshot();");
    const partial = afterPartial.entities.find((row) => row.id === "partial-dividend-15");
    assert.ok(partial);
    assert.deepEqual(partial.provenance.sourceEntityRefs, ["dividend-156"]);
    assert.notEqual(partial.id, "dividend-156");
    assert.equal(afterPartial.projections.find((row) => row.id === "partial-dividend-working").entityRef, "partial-dividend-15");

    const partialProjection = await driver.shadowElement("#identity", '[data-role="entity"][data-projection-ref="partial-dividend-working"]');
    await driver.execute("arguments[0].focus();", [driver.ref(partialProjection)]);
    const inspected = await driver.execute(`
      const events = window.identityHarness.events();
      return [...events].reverse().find((event) => event.type === "ENTITY_INSPECTED");
    `);
    assert.equal(inspected.entityRef, "partial-dividend-15");
    assert.equal(inspected.projectionRef, "partial-dividend-working");
    assert.deepEqual(inspected.linkedProjectionRefs, ["partial-dividend-working"]);

    await driver.browserClick(partialProjection);
    const quotientTarget = await driver.shadowElement("#identity", '[data-role="target"][data-target-ref="quotient-first-digit"]');
    await driver.browserClick(quotientTarget);
    await driver.waitFor("return window.identityHarness.snapshot().revision === 2;");

    const afterQuotient = await driver.execute("return window.identityHarness.snapshot();");
    const quotient = afterQuotient.entities.find((row) => row.id === "quotient-digit-1");
    assert.deepEqual(quotient.provenance.sourceEntityRefs, ["partial-dividend-15", "divisor-12"]);
    assert.equal(await driver.execute("return window.identityHarness.adapterCalls();"), 2);

    let undo = await driver.shadowElement("#identity", '[data-action="undo"]');
    await driver.browserClick(undo);
    let state = await driver.execute("return window.identityHarness.snapshot();");
    assert.equal(state.entities.some((row) => row.id === "quotient-digit-1"), false);
    assert.equal(state.entities.some((row) => row.id === "partial-dividend-15"), true);

    undo = await driver.shadowElement("#identity", '[data-action="undo"]');
    await driver.browserClick(undo);
    state = await driver.execute("return window.identityHarness.snapshot();");
    assert.equal(state.entities.some((row) => row.id === "partial-dividend-15"), false);

    let redo = await driver.shadowElement("#identity", '[data-action="redo"]');
    await driver.browserClick(redo);
    state = await driver.execute("return window.identityHarness.snapshot();");
    assert.equal(state.entities.some((row) => row.id === "partial-dividend-15"), true);
    assert.equal(state.entities.some((row) => row.id === "quotient-digit-1"), false);

    redo = await driver.shadowElement("#identity", '[data-action="redo"]');
    await driver.browserClick(redo);
    state = await driver.execute("return window.identityHarness.snapshot();");
    assert.equal(state.entities.some((row) => row.id === "quotient-digit-1"), true);
    assert.equal(state.revision, 6);
    assert.equal(await driver.execute("return window.identityHarness.adapterCalls();"), 2);

    const summary = await driver.execute("return window.identityHarness.textSummary();");
    assert.match(summary, /15 \[partial dividend\]/);
    assert.match(summary, /1 \[quotient digit\]/);
  } finally {
    await driver.close();
    driverProcess.child.kill("SIGTERM");
    await new Promise((resolveClose) => staticServer.server.close(resolveClose));
  }
});
