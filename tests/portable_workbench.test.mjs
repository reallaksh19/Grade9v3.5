import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { WorkbenchRuntime } from "../Shared/workbench/runtime.mjs";
import { PortablePackageError, createDeclarativeAdapter, resolveCanonicalPortableTarget, validatePortablePackage } from "../Shared/portable/portable-host.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const ids = ["portable-long-division", "portable-redox-electron-equivalence", "portable-integration-riemann"];
async function packageById(id) { return JSON.parse(await readFile(resolve(repo, `public/portable-workbench/packages/${id}.json`), "utf8")); }

test("three packages validate under one portable version seam", async () => {
  const versions = new Set();
  for (const id of ids) {
    const pkg = validatePortablePackage(await packageById(id));
    versions.add([pkg.packageVersion,pkg.componentApiVersion,pkg.transformationIrVersion,pkg.adapterApiVersion,pkg.scenePackageVersion,pkg.adapter.id].join("|"));
  }
  assert.equal(versions.size, 1);
});

test("canonical provenance requires explicit resource and representation refs", async () => {
  const canonical = structuredClone(await packageById(ids[0]));
  canonical.resourceRef = "ACT-TEST-CANONICAL";
  canonical.representationRefs = ["REP-TEST-CANONICAL"];
  canonical.sourceRefs = ["SRC-TEST-CANONICAL"];
  canonical.provenance = {
    authority: "CANONICAL_COMPILED_RESOURCE",
    sourceKind: "CANONICAL_RESOURCE",
    sourceRefs: ["SRC-TEST-CANONICAL"],
    resourceRef: "ACT-TEST-CANONICAL",
    representationRef: "REP-TEST-CANONICAL",
  };
  assert.equal(validatePortablePackage(canonical).resourceRef, "ACT-TEST-CANONICAL");

  const missing = structuredClone(canonical);
  delete missing.provenance.resourceRef;
  assert.throws(
    () => validatePortablePackage(missing),
    (error) => error instanceof PortablePackageError && error.code === "PORTABLE_CANONICAL_RESOURCE_REF_REQUIRED",
  );
});

test("AtlasIndex 2.0 visual target binding is exact-ID and fail-closed", async () => {
  const resourceRef = "ACT-KIN-2D-SHARED-CLOCK";
  const unavailable = {
    resource_ref: resourceRef,
    representation_refs: ["REP-KIN-2D-SHARED-CLOCK"],
    locator: "public/physics/motion-2d/explorers/shared-clock/index.html",
    delivery_kind: "EXISTING_ACTIVITY",
    delivery_profile: "REPO_BUNDLE",
    portable_package_ref: null,
    availability: { resource: "READY", locator: "READY", portable_package: "UNAVAILABLE", standalone: "UNAVAILABLE" },
  };
  assert.throws(
    () => resolveCanonicalPortableTarget(resourceRef, { [resourceRef]: unavailable }, {}),
    (error) => error instanceof PortablePackageError && error.code === "STANDALONE_PACKAGE_UNAVAILABLE",
  );
  assert.throws(
    () => resolveCanonicalPortableTarget("ACT-NOT-HERE", { [resourceRef]: unavailable }, {}),
    (error) => error instanceof PortablePackageError && error.code === "VISUAL_REF_UNAVAILABLE",
  );

  const canonical = structuredClone(await packageById(ids[0]));
  canonical.id = "portable-motion-shared-clock";
  canonical.resourceRef = resourceRef;
  canonical.representationRefs = ["REP-KIN-2D-SHARED-CLOCK"];
  canonical.sourceRefs = ["SRC-AUTHOR-KIN-2D-EXAMSIDE-ADAPTATION"];
  canonical.provenance = {
    authority: "CANONICAL_COMPILED_RESOURCE",
    sourceKind: "CANONICAL_RESOURCE",
    sourceRefs: ["SRC-AUTHOR-KIN-2D-EXAMSIDE-ADAPTATION"],
    resourceRef,
    representationRef: "REP-KIN-2D-SHARED-CLOCK",
  };
  const ready = {
    ...unavailable,
    delivery_kind: "PORTABLE_PACKAGE",
    delivery_profile: "SINGLE_FILE_OFFLINE",
    portable_package_ref: canonical.id,
    availability: { resource: "READY", locator: "READY", portable_package: "READY", standalone: "READY" },
  };
  const binding = resolveCanonicalPortableTarget(resourceRef, { [resourceRef]: ready }, { [canonical.id]: canonical });
  assert.equal(binding.portablePackageRef, canonical.id);
  assert.equal(binding.representationRef, "REP-KIN-2D-SHARED-CLOCK");
});

test("generic declarative adapter executes each proof without Core edits", async () => {
  for (const id of ids) {
    const pkg = validatePortablePackage(await packageById(id));
    const rule = pkg.adapter.rules[0];
    const events = [];
    const runtime = new WorkbenchRuntime(pkg.scene, createDeclarativeAdapter(pkg), { injections: pkg.injections, eventSink: (event) => events.push(event) });
    runtime.dispatch({ type: "PICK", entityRef: rule.sourceEntityRef, channel: "test" });
    const result = runtime.dispatch({ type: "DROP", targetRef: rule.targetRef, channel: "test" });
    assert.equal(result.type, "TRANSFER_ACCEPTED");
    assert.equal(runtime.snapshot.revision, 1);
    assert.equal(JSON.stringify(events).toLowerCase().includes("mastery"), false);
  }
});

test("incompatible and executable packages fail closed", async () => {
  const pkg = await packageById(ids[0]);
  const mismatch = structuredClone(pkg); mismatch.componentApiVersion = "99.0.0";
  assert.throws(() => validatePortablePackage(mismatch), (error) => error instanceof PortablePackageError && error.code === "PORTABLE_COMPONENTAPIVERSION_MISMATCH");
  const executable = structuredClone(pkg); executable.handler = "doThing";
  assert.throws(() => validatePortablePackage(executable), (error) => error instanceof PortablePackageError && error.code === "PORTABLE_EXECUTABLE_FIELD_FORBIDDEN");
});

test("portable host contains no dynamic code execution", async () => {
  const source = await readFile(resolve(repo, "Shared/portable/portable-host.mjs"), "utf8");
  assert.doesNotMatch(source, /\beval\s*\(/);
  assert.doesNotMatch(source, /new\s+Function\b/);
});

import { createServer } from "node:http";
import { existsSync, statSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { extname, join, sep } from "node:path";
import { stat } from "node:fs/promises";

const W3C_ELEMENT = "element-6066-11e4-a52e-4f735466cecf";
const W3C_SHADOW = "shadow-6066-11e4-a52e-4f735466cecf";

function chromeDriverPath() {
  const candidates = [];
  if (process.env.CHROMEWEBDRIVER) {
    candidates.push(process.env.CHROMEWEBDRIVER, join(process.env.CHROMEWEBDRIVER, "chromedriver"));
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
      const path = resolve(repo, `.${decodeURIComponent(url.pathname)}`);
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
  return { server, origin: `http://127.0.0.1:${server.address().port}` };
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
  const child = spawn(path, [`--port=${port}`, "--allowed-origins=*"], { stdio: ["ignore", "pipe", "pipe"] });
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

class PortableWebDriver {
  constructor(base) { this.base = base; this.sessionId = null; }
  async request(method, path, body = undefined) {
    const response = await fetch(`${this.base}${path}`, {
      method,
      headers: body === undefined ? undefined : { "content-type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const payload = await response.json();
    if (!response.ok || payload.value?.error) throw new Error(JSON.stringify(payload.value ?? payload));
    return payload.value;
  }
  async open() {
    const value = await this.request("POST", "/session", { capabilities: { alwaysMatch: {
      browserName: "chrome",
      "goog:chromeOptions": { args: ["--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1200,900"] },
    } } });
    this.sessionId = value.sessionId;
  }
  async close() { if (this.sessionId) { try { await this.request("DELETE", `/session/${this.sessionId}`); } catch (_) {} this.sessionId = null; } }
  async navigate(url) { await this.request("POST", `/session/${this.sessionId}/url`, { url }); }
  async execute(script, args = []) { return this.request("POST", `/session/${this.sessionId}/execute/sync`, { script, args }); }
  async waitFor(script, args = [], timeoutMs = 5000) {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (await this.execute(script, args)) return;
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 50));
    }
    throw new Error(`Timed out: ${script}`);
  }
  async element(css) {
    const value = await this.request("POST", `/session/${this.sessionId}/element`, { using: "css selector", value: css });
    return value[W3C_ELEMENT];
  }
  async shadowElement(hostCss, innerCss) {
    const host = await this.element(hostCss);
    const shadow = await this.request("GET", `/session/${this.sessionId}/element/${host}/shadow`);
    const value = await this.request("POST", `/session/${this.sessionId}/shadow/${shadow[W3C_SHADOW]}/element`, { using: "css selector", value: innerCss });
    return value[W3C_ELEMENT];
  }
  ref(elementId) { return { [W3C_ELEMENT]: elementId }; }
  async click(elementId) { await this.execute("arguments[0].click();", [this.ref(elementId)]); }
  async setWindow(width, height) { await this.request("POST", `/session/${this.sessionId}/window/rect`, { width, height, x: 0, y: 0 }); }
  async cdp(command, params) { return this.request("POST", `/session/${this.sessionId}/chromium/send_command`, { cmd: command, params }); }
}

const driverPath = chromeDriverPath();
if (!driverPath && process.env.GITHUB_ACTIONS === "true") {
  throw new Error("GitHub Actions portability proof requires ChromeDriver");
}

test("portable workbench runs in repository, external and single-file hosts", { skip: !driverPath, timeout: 30000 }, async () => {
  const staticServer = await openStaticServer();
  const driverProcess = await startDriver(driverPath);
  const driver = new PortableWebDriver(driverProcess.base);
  try {
    await driver.open();
    const hosts = [
      "/public/portable-workbench/index.html",
      "/tests/fixtures/portable-workbench/external-host.html",
      "/standalone/portable-workbench/index.html",
    ];
    for (const path of hosts) {
      await driver.navigate(`${staticServer.origin}${path}`);
      await driver.waitFor("return window.__portableWorkbenchReady === true;");
      const mounted = await driver.execute(`
        const wb = document.querySelector("semantic-workbench");
        return {
          packageId: window.__portablePackageId,
          sceneId: wb.snapshot?.sceneId,
          revision: wb.snapshot?.revision,
          error: window.__portableWorkbenchError || null,
        };
      `);
      assert.equal(mounted.packageId, "portable-long-division");
      assert.equal(mounted.sceneId, "division-first-quotient-digit");
      assert.equal(mounted.revision, 0);
      assert.equal(mounted.error, null);
      const source = await driver.shadowElement("semantic-workbench", '[data-role="entity"][data-projection-ref="dividend-expression"]');
      const target = await driver.shadowElement("semantic-workbench", '[data-role="target"][data-target-ref="quotient-first-digit"]');
      await driver.click(source);
      await driver.click(target);
      await driver.waitFor("return document.querySelector('semantic-workbench').snapshot?.revision === 1;");
      const events = await driver.execute("return window.__portableEvents;");
      assert.ok(events.some((event) => event.type === "TRANSFER_ACCEPTED"));
      assert.equal(JSON.stringify(events).toLowerCase().includes("mastery"), false);
    }

    for (const path of [
      "/public/portable-workbench/index.html?package=portable-does-not-exist",
      "/tests/fixtures/portable-workbench/external-host.html?package=portable-does-not-exist",
      "/standalone/portable-workbench/index.html?package=portable-does-not-exist",
    ]) {
      await driver.navigate(`${staticServer.origin}${path}`);
      await driver.waitFor("return Boolean(window.__portableWorkbenchError);");
      const missingPackage = await driver.execute(`return {
        diagnostic: window.__portableWorkbenchError || null,
        packageId: window.__portablePackageId || null,
        ready: window.__portableWorkbenchReady === true,
      };`);
      assert.match(missingPackage.diagnostic, /PORTABLE_PACKAGE_NOT_FOUND/);
      assert.equal(missingPackage.packageId, null);
      assert.equal(missingPackage.ready, false);
    }

    await driver.setWindow(390, 844);
    await driver.cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
    for (const packageId of ["portable-redox-electron-equivalence", "portable-integration-riemann"]) {
      await driver.navigate(`${staticServer.origin}/public/portable-workbench/index.html?package=${packageId}`);
      await driver.waitFor("return window.__portableWorkbenchReady === true;");
      assert.equal(await driver.execute("return window.__portablePackageId;"), packageId);
    }

    await driver.navigate(`${staticServer.origin}/standalone/portable-workbench/index.html`);
    await driver.waitFor("return window.__portableWorkbenchReady === true;");
    assert.deepEqual(await driver.execute('return performance.getEntriesByType("resource").map((entry) => entry.name);'), []);
  } finally {
    await driver.close();
    driverProcess.child.kill("SIGTERM");
    await new Promise((resolveClose) => staticServer.server.close(resolveClose));
  }
});
