import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { dirname, extname, join, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const W3C_ELEMENT = "element-6066-11e4-a52e-4f735466cecf";
const W3C_SHADOW = "shadow-6066-11e4-a52e-4f735466cecf";
const SPACE = "\uE00D";
const ENTER = "\uE007";

const MATRIX = "MATRIX-PHY-KIN-2D-MOTION";
const MICROTOPIC = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS";
const CAPABILITY = "CAP-KIN-2D-INDEPENDENT-COMPONENTS";
const CORE1B = "physics:mic-phy-kin-2d-independent-components:core1b";
const CORE2B = "physics:q-phy-kin-2d-2b-projectile-validity-04:core2b";
const CORE2B_SOURCE = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04";
const REPRESENTATION = "REP-KIN-2D-SHARED-CLOCK";
const RESOURCE = "ACT-KIN-2D-SHARED-CLOCK";
const PACKAGE = "portable-motion-shared-clock";

function chromeDriverPath() {
  const candidates = [];
  if (process.env.CHROMEWEBDRIVER) {
    candidates.push(process.env.CHROMEWEBDRIVER);
    candidates.push(join(process.env.CHROMEWEBDRIVER, "chromedriver"));
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
  const child = spawn(path, [`--port=${port}`, "--allowed-origins=*"], {
    stdio: ["ignore", "pipe", "pipe"],
  });
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
    [".html", "text/html; charset=utf-8"],
    [".js", "text/javascript; charset=utf-8"],
    [".mjs", "text/javascript; charset=utf-8"],
    [".json", "application/json; charset=utf-8"],
    [".css", "text/css; charset=utf-8"],
  ]);
  const server = createServer(async (request, response) => {
    try {
      const url = new URL(request.url || "/", "http://127.0.0.1");
      const path = resolve(repo, "." + decodeURIComponent(url.pathname));
      if (!(path === repo || path.startsWith(repo + sep))) {
        response.writeHead(403).end("forbidden");
        return;
      }
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
  constructor(base) {
    this.base = base;
    this.sessionId = null;
  }

  async request(method, path, body = undefined) {
    const response = await fetch(this.base + path, {
      method,
      headers: body === undefined ? undefined : { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok || payload.value?.error) {
      throw new Error(`WebDriver ${method} ${path}: ${JSON.stringify(payload.value ?? payload)}`);
    }
    return payload.value;
  }

  async open() {
    const value = await this.request("POST", "/session", {
      capabilities: {
        alwaysMatch: {
          browserName: "chrome",
          "goog:chromeOptions": {
            args: [
              "--headless=new",
              "--no-sandbox",
              "--disable-dev-shm-usage",
              "--allow-file-access-from-files",
              "--window-size=1280,1000",
            ],
          },
        },
      },
    });
    this.sessionId = value.sessionId;
  }

  async close() {
    if (!this.sessionId) return;
    try {
      await this.request("DELETE", `/session/${this.sessionId}`);
    } catch (_) {}
    this.sessionId = null;
  }

  async navigate(url) {
    await this.request("POST", `/session/${this.sessionId}/url`, { url });
  }

  async execute(script, args = []) {
    return this.request("POST", `/session/${this.sessionId}/execute/sync`, { script, args });
  }

  async waitFor(script, args = [], timeoutMs = 8000) {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (await this.execute(script, args)) return;
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 60));
    }
    throw new Error("Timed out waiting for: " + script);
  }

  async element(css) {
    const value = await this.request("POST", `/session/${this.sessionId}/element`, {
      using: "css selector",
      value: css,
    });
    return value[W3C_ELEMENT];
  }

  async shadowElement(hostCss, innerCss) {
    const host = await this.element(hostCss);
    const shadow = await this.request("GET", `/session/${this.sessionId}/element/${host}/shadow`);
    const value = await this.request(
      "POST",
      `/session/${this.sessionId}/shadow/${shadow[W3C_SHADOW]}/element`,
      { using: "css selector", value: innerCss },
    );
    return value[W3C_ELEMENT];
  }

  ref(elementId) {
    return { [W3C_ELEMENT]: elementId };
  }

  async sendKeys(elementId, text) {
    await this.request("POST", `/session/${this.sessionId}/element/${elementId}/value`, {
      text,
      value: [...text],
    });
  }

  async click(elementId) {
    await this.execute("arguments[0].click();", [this.ref(elementId)]);
  }
}

const driverPath = chromeDriverPath();
if (!driverPath && process.env.GITHUB_ACTIONS === "true") {
  throw new Error("GitHub Actions Issue #215 joined browser proof requires ChromeDriver.");
}

test("Issue #215 carries canonical identity through Atlas, Core and portable hosts", {
  skip: !driverPath,
  timeout: 65000,
}, async () => {
  const staticServer = await openStaticServer();
  const driverProcess = await startDriver(driverPath);
  const driver = new Driver(driverProcess.base);

  try {
    await driver.open();

    // 1. Enter through the Atlas and select R1 by keyboard.
    const motion = `${staticServer.origin}/public/physics/motion-2d/index.html`;
    await driver.navigate(motion);
    await driver.execute("localStorage.clear(); location.reload();");
    await driver.waitFor("return Boolean(window.ATLAS && document.querySelector('.rung-node'));");

    const r1 = await driver.element('button.rung-node[aria-controls="card-R1"]');
    await driver.sendKeys(r1, SPACE);
    await driver.waitFor("return new URLSearchParams(location.search).get('rung') === 'R1';");

    const atlas = await driver.execute(`
      const subject = window.GRADE9V3?.subjects?.Physics;
      const row = subject?.atlas_index?.find(
        (item) => item.matrix_id === "${MATRIX}" && item.rung === "R1"
      );
      const target = subject?.visual_targets?.["${RESOURCE}"];
      const card = document.getElementById("card-R1");
      const coreLinks = [...(card?.querySelectorAll('a[href*="core-learning"][href*="projection="]') || [])]
        .map((anchor) => ({
          href: anchor.href,
          projection: new URL(anchor.href).searchParams.get("projection"),
        }));
      const portable = card?.querySelector('a[data-portable-package="${PACKAGE}"]');
      return {
        contract: subject?.atlas_index_contract_version || null,
        matrix: new URLSearchParams(location.search).get("matrix"),
        rung: new URLSearchParams(location.search).get("rung"),
        focused: document.activeElement?.tagName || null,
        row,
        target,
        coreLinks,
        portableHref: portable?.href || null,
        portablePackage: portable?.dataset?.portablePackage || null,
        hashFallbacks: card?.querySelectorAll('a[href="#"]').length || 0,
      };
    `);

    assert.equal(atlas.contract, "2.0");
    assert.equal(atlas.matrix, MATRIX);
    assert.equal(atlas.rung, "R1");
    assert.equal(atlas.focused, "SUMMARY");
    assert.equal(atlas.hashFallbacks, 0);
    assert.equal(atlas.row.microtopic_ref, MICROTOPIC);
    assert.equal(atlas.row.capability_ref, CAPABILITY);
    assert.deepEqual(atlas.row.representation_refs, [REPRESENTATION]);
    assert.deepEqual(atlas.row.activity_refs, [RESOURCE]);
    assert.ok(atlas.row.core_projection_refs.includes(CORE1B));
    assert.ok(atlas.row.core_projection_refs.includes(CORE2B));
    assert.equal(atlas.row.availability.core, "READY");
    assert.equal(atlas.row.availability.representation, "READY");
    assert.equal(atlas.row.availability.activity, "READY");
    assert.equal(atlas.row.availability.portable_package, "READY");
    assert.equal(atlas.row.availability.standalone, "READY");
    assert.deepEqual(atlas.target.representation_refs, [REPRESENTATION]);
    assert.equal(atlas.target.resource_ref, RESOURCE);
    assert.equal(atlas.target.portable_package_ref, PACKAGE);
    assert.equal(atlas.portablePackage, PACKAGE);

    const coreByProjection = new Map(atlas.coreLinks.map((item) => [item.projection, item.href]));
    assert.ok(coreByProjection.has(CORE1B));
    assert.ok(coreByProjection.has(CORE2B));
    assert.ok(atlas.portableHref);

    // 2. Follow the exact Core1B destination captured at the Atlas boundary.
    await driver.navigate(coreByProjection.get(CORE1B));
    await driver.waitFor("return window.__coreLearningStaticHostReady === true;");
    await driver.waitFor("return document.querySelector('#learner').state?.core === 'CORE1B';");

    const core1Before = await driver.execute(`
      const id = new URLSearchParams(location.search).get("projection");
      const row = window.GRADE9V3_CORE.core_projections.find((item) => item.id === id);
      const learner = document.querySelector("#learner");
      return {
        id,
        selected: document.querySelector("#projection-select").value,
        sourceRef: row?.source_ref || null,
        state: learner.state,
        html: learner.shadowRoot.innerHTML,
      };
    `);
    assert.equal(core1Before.id, CORE1B);
    assert.equal(core1Before.selected, CORE1B);
    assert.equal(core1Before.sourceRef, MICROTOPIC);
    assert.equal(core1Before.state.stage, "AWAITING_ATTEMPT");
    assert.equal(core1Before.state.reconstructionVisible, false);
    assert.equal(core1Before.state.attemptCount, 0);
    assert.doesNotMatch(core1Before.html, /data-semantic="reconstruction"/);

    const core1Input = await driver.shadowElement("#learner", "[data-attempt-input]");
    await driver.sendKeys(core1Input, "Horizontal and vertical components use one elapsed time.");
    const core1Commit = await driver.shadowElement("#learner", '[data-action="commit"]');
    await driver.sendKeys(core1Commit, ENTER);
    await driver.waitFor("return document.querySelector('#learner').state?.reconstructionVisible === true;");

    const core1After = await driver.execute(`
      const learner = document.querySelector("#learner");
      return { state: learner.state, html: learner.shadowRoot.innerHTML };
    `);
    assert.equal(core1After.state.stage, "RECONSTRUCTION_VISIBLE");
    assert.equal(core1After.state.attemptCount, 1);
    assert.equal(core1After.state.reconstructionVisible, true);
    assert.match(core1After.html, /data-semantic="reconstruction"/);

    // 3. Verify the separate Core2B protected decision without conflating it with rung identity.
    await driver.navigate(coreByProjection.get(CORE2B));
    await driver.waitFor("return window.__coreLearningStaticHostReady === true;");
    await driver.waitFor("return document.querySelector('#learner').state?.core === 'CORE2B';");

    const core2Before = await driver.execute(`
      const id = new URLSearchParams(location.search).get("projection");
      const row = window.GRADE9V3_CORE.core_projections.find((item) => item.id === id);
      const learner = document.querySelector("#learner");
      return {
        id,
        selected: document.querySelector("#projection-select").value,
        sourceRef: row?.source_ref || null,
        reasoningVisible: learner.state.reasoningVisible,
        html: learner.shadowRoot.innerHTML,
      };
    `);
    assert.equal(core2Before.id, CORE2B);
    assert.equal(core2Before.selected, CORE2B);
    assert.equal(core2Before.sourceRef, CORE2B_SOURCE);
    assert.equal(core2Before.reasoningVisible, false);
    assert.doesNotMatch(
      core2Before.html,
      /Reject the standard gravity-only projectile specialization/,
    );

    const core2Input = await driver.shadowElement("#learner", "[data-attempt-input]");
    await driver.sendKeys(
      core2Input,
      "The horizontal thrust means the gravity-only projectile specialization no longer applies.",
    );
    const core2Commit = await driver.shadowElement("#learner", '[data-action="commit"]');
    await driver.sendKeys(core2Commit, ENTER);
    await driver.waitFor("return document.querySelector('#learner').state?.reasoningVisible === true;");

    const core2After = await driver.execute(
      "return document.querySelector('#learner').shadowRoot.innerHTML;",
    );
    assert.match(core2After, /Reject the standard gravity-only projectile specialization/);
    assert.match(core2After, /Key decision/);

    // 4. Carry the portable package identity captured from Atlas across all three host forms.
    const packageId = new URL(atlas.portableHref).searchParams.get("package");
    assert.equal(packageId, PACKAGE);
    const hosts = [
      "/public/portable-workbench/index.html",
      "/tests/fixtures/portable-workbench/external-host.html",
      "/standalone/portable-workbench/index.html",
    ];
    const acceptedEvents = [];
    const rejectedEvents = [];

    for (const host of hosts) {
      const url = `${staticServer.origin}${host}?package=${encodeURIComponent(packageId)}`;

      await driver.navigate(url);
      await driver.waitFor("return window.__portableWorkbenchReady === true;");
      assert.equal(await driver.execute("return window.__portablePackageId;"), packageId);

      const sameSource = await driver.shadowElement(
        "semantic-workbench",
        '[data-role="entity"][data-projection-ref="shared-clock-same-time-candidate-projection"]',
      );
      const sameTarget = await driver.shadowElement(
        "semantic-workbench",
        '[data-role="target"][data-target-ref="shared-clock-plane-state"]',
      );
      await driver.click(sameSource);
      await driver.click(sameTarget);
      await driver.waitFor(
        "return window.__portableEvents.some((event) => event.type === 'TRANSFER_ACCEPTED');",
      );
      const accepted = await driver.execute(`
        const wb = document.querySelector("semantic-workbench");
        return {
          event: window.__portableEvents.find((event) => event.type === "TRANSFER_ACCEPTED"),
          revision: wb.snapshot?.revision,
          summary: wb.textSummary,
        };
      `);
      assert.equal(accepted.revision, 1);
      assert.match(accepted.summary, /simultaneous/i);
      acceptedEvents.push(accepted.event);

      await driver.navigate(url);
      await driver.waitFor("return window.__portableWorkbenchReady === true;");
      const mixedSource = await driver.shadowElement(
        "semantic-workbench",
        '[data-role="entity"][data-projection-ref="shared-clock-mixed-time-candidate-projection"]',
      );
      const mixedTarget = await driver.shadowElement(
        "semantic-workbench",
        '[data-role="target"][data-target-ref="shared-clock-plane-state"]',
      );
      await driver.click(mixedSource);
      await driver.click(mixedTarget);
      await driver.waitFor(
        "return window.__portableEvents.some((event) => event.type === 'TRANSFER_REJECTED');",
      );
      const rejected = await driver.execute(`
        const wb = document.querySelector("semantic-workbench");
        return {
          event: window.__portableEvents.find((event) => event.type === "TRANSFER_REJECTED"),
          revision: wb.snapshot?.revision,
          summary: wb.textSummary,
        };
      `);
      assert.equal(rejected.revision, 0);
      assert.match(rejected.event.reason, /single physical state/i);
      assert.match(rejected.summary, /single physical state/i);
      rejectedEvents.push(rejected.event);
    }

    for (const event of acceptedEvents.slice(1)) assert.deepEqual(event, acceptedEvents[0]);
    for (const event of rejectedEvents.slice(1)) assert.deepEqual(event, rejectedEvents[0]);

    // 5. Keyboard interaction, visible active focus treatment, and text meaning.
    await driver.navigate(
      `${staticServer.origin}/public/portable-workbench/index.html?package=${encodeURIComponent(packageId)}`,
    );
    await driver.waitFor("return window.__portableWorkbenchReady === true;");
    const keyboardSource = await driver.shadowElement(
      "semantic-workbench",
      '[data-role="entity"][data-projection-ref="shared-clock-same-time-candidate-projection"]',
    );
    const keyboardTarget = await driver.shadowElement(
      "semantic-workbench",
      '[data-role="target"][data-target-ref="shared-clock-plane-state"]',
    );
    await driver.execute(`
      arguments[0].focus();
      arguments[0].dispatchEvent(new KeyboardEvent("keydown", {
        key: "Enter", bubbles: true, composed: true
      }));
    `, [driver.ref(keyboardSource)]);
    const focusedStyle = await driver.execute(`
      const wb = document.querySelector("semantic-workbench");
      const active = wb.shadowRoot.activeElement;
      return {
        role: active?.dataset?.role || null,
        outlineStyle: getComputedStyle(arguments[0]).outlineStyle,
        outlineWidth: getComputedStyle(arguments[0]).outlineWidth,
      };
    `, [driver.ref(keyboardSource)]);
    assert.equal(focusedStyle.role, "entity");
    assert.notEqual(focusedStyle.outlineStyle, "none");
    assert.notEqual(focusedStyle.outlineWidth, "0px");

    await driver.execute(`
      arguments[0].focus();
      arguments[0].dispatchEvent(new KeyboardEvent("keydown", {
        key: "Enter", bubbles: true, composed: true
      }));
    `, [driver.ref(keyboardTarget)]);
    await driver.waitFor(
      "return window.__portableEvents.some((event) => event.type === 'TRANSFER_ACCEPTED' && event.request?.channel === 'keyboard');",
    );
    const keyboardSummary = await driver.execute(
      'return document.querySelector("semantic-workbench").textSummary;',
    );
    assert.match(keyboardSummary, /simultaneous/i);

    // 6. Direct single-file offline load uses the same captured package and no resource requests.
    const offline = pathToFileURL(join(repo, "standalone/portable-workbench/index.html")).href
      + `?package=${encodeURIComponent(packageId)}`;
    await driver.navigate(offline);
    await driver.waitFor("return window.__portableWorkbenchReady === true;", [], 10000);
    assert.equal(await driver.execute("return location.protocol;"), "file:");
    assert.equal(await driver.execute("return window.__portablePackageId;"), packageId);
    assert.deepEqual(
      await driver.execute('return performance.getEntriesByType("resource").map((entry) => entry.name);'),
      [],
    );

    // 7. Fail closed for an unknown canonical selection.
    await driver.navigate(
      motion + `?matrix=${encodeURIComponent(MATRIX)}&rung=R999`,
    );
    await driver.waitFor(
      "return document.querySelector('.atlas-finding')?.textContent?.includes('ATLAS_TARGET_NOT_FOUND');",
    );
    const invalid = await driver.execute(`
      return {
        finding: document.querySelector(".atlas-finding")?.textContent || "",
        coreActions: document.querySelectorAll('#rungCardsContainer a[href*="core-learning"]').length,
        visualActions: document.querySelectorAll('#rungCardsContainer a[href*="/explorers/"]').length,
        portableActions: document.querySelectorAll('#rungCardsContainer a[href*="portable-workbench"]').length,
      };
    `);
    assert.match(invalid.finding, /ATLAS_TARGET_NOT_FOUND/);
    assert.equal(invalid.coreActions, 0);
    assert.equal(invalid.visualActions, 0);
    assert.equal(invalid.portableActions, 0);

    // 8. Contrasting subject: preserve real representation state without inventing Core/portable availability.
    const math = `${staticServer.origin}/public/mathematics/linear-equations/index.html`
      + "?matrix=MATRIX-MATH-LINEAR-EQUATIONS&rung=R1";
    await driver.navigate(math);
    await driver.waitFor("return document.getElementById('card-R1')?.open === true;");
    const mathState = await driver.execute(`
      const subject = window.GRADE9V3?.subjects?.Mathematics;
      const row = subject?.atlas_index?.find(
        (item) => item.matrix_id === "MATRIX-MATH-LINEAR-EQUATIONS" && item.rung === "R1"
      );
      const card = document.getElementById("card-R1");
      return {
        row,
        coreActions: card?.querySelectorAll('a[href*="core-learning"]').length || 0,
        visualActions: card?.querySelectorAll('a[href*="/explorers/"]').length || 0,
        portableActions: card?.querySelectorAll('a[href*="portable-workbench"]').length || 0,
      };
    `);
    assert.deepEqual(mathState.row.representation_refs, ["REP-MATH-NUMBER-LINE"]);
    assert.equal(mathState.row.availability.representation, "READY");
    assert.equal(mathState.row.availability.core, "UNAVAILABLE");
    assert.equal(mathState.row.availability.activity, "UNAVAILABLE");
    assert.equal(mathState.row.availability.portable_package, "UNAVAILABLE");
    assert.equal(mathState.row.availability.standalone, "UNAVAILABLE");
    assert.equal(mathState.coreActions, 0);
    assert.equal(mathState.visualActions, 0);
    assert.equal(mathState.portableActions, 0);
  } finally {
    await driver.close();
    driverProcess.child.kill("SIGTERM");
    await new Promise((ok) => staticServer.server.close(ok));
  }
});
