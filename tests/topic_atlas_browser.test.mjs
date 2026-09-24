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
const SPACE = "\uE00D";

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
  await new Promise(ok => server.close(ok));
  return port;
}

async function startDriver(path) {
  const port = await freePort();
  const child = spawn(path, [`--port=${port}`, "--allowed-origins=*"], { stdio: ["ignore", "pipe", "pipe"] });
  let stderr = "";
  child.stderr.on("data", chunk => { stderr += chunk.toString(); });
  const base = `http://127.0.0.1:${port}`;
  for (let i = 0; i < 100; i += 1) {
    try {
      const response = await fetch(`${base}/status`);
      if (response.ok) return { child, base };
    } catch (_) {}
    await new Promise(r => setTimeout(r, 50));
  }
  child.kill("SIGTERM");
  throw new Error("ChromeDriver did not become ready: " + stderr);
}

async function openStaticServer() {
  const mime = new Map([
    [".html", "text/html; charset=utf-8"],
    [".js", "text/javascript; charset=utf-8"],
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
  constructor(base) { this.base = base; this.sessionId = null; }
  async request(method, path, body) {
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
      capabilities: { alwaysMatch: {
        browserName: "chrome",
        "goog:chromeOptions": { args: [
          "--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
          "--allow-file-access-from-files", "--window-size=1280,1000"
        ] }
      } }
    });
    this.sessionId = value.sessionId;
  }
  async close() {
    if (!this.sessionId) return;
    try { await this.request("DELETE", `/session/${this.sessionId}`); } catch (_) {}
  }
  async navigate(url) { await this.request("POST", `/session/${this.sessionId}/url`, { url }); }
  async execute(script, args = []) {
    return this.request("POST", `/session/${this.sessionId}/execute/sync`, { script, args });
  }
  async waitFor(script, args = [], timeoutMs = 7000) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      if (await this.execute(script, args)) return;
      await new Promise(r => setTimeout(r, 60));
    }
    throw new Error("Timed out waiting for: " + script);
  }
  async element(css) {
    const value = await this.request("POST", `/session/${this.sessionId}/element`, {
      using: "css selector", value: css
    });
    return value[W3C_ELEMENT];
  }
  async sendKeys(id, text) {
    await this.request("POST", `/session/${this.sessionId}/element/${id}/value`, { text, value: [...text] });
  }
}

const driverPath = chromeDriverPath();
if (!driverPath && process.env.GITHUB_ACTIONS === "true") {
  throw new Error("GitHub Actions Topic Atlas browser proof requires ChromeDriver.");
}

test("Topic Atlas 2.0 exact browser navigation contract", { skip: !driverPath, timeout: 45000 }, async () => {
  const staticServer = await openStaticServer();
  const proc = await startDriver(driverPath);
  const driver = new Driver(proc.base);
  try {
    await driver.open();

    const motion = `${staticServer.origin}/public/physics/motion-2d/index.html`;
    await driver.navigate(motion);
    await driver.execute("localStorage.clear(); location.reload();");
    await driver.waitFor("return Boolean(window.ATLAS && document.querySelector('.rung-node'));");

    const neutral = await driver.execute(`
      return {
        search: location.search,
        estimate: document.getElementById('estimateStatusText')?.textContent || '',
        buttons: [...document.querySelectorAll('.rung-node')].every(x => x.tagName === 'BUTTON'),
        text: document.getElementById('progressionLaneContainer')?.textContent || ''
      };
    `);
    assert.equal(neutral.search, "");
    assert.match(neutral.estimate, /No estimate supplied/);
    assert.equal(neutral.buttons, true);
    assert.doesNotMatch(neutral.text, /Foundation|Dynamics & Applications|Constraints & Quantitative|Interaction & Closure/);

    const r1 = await driver.element(".rung-node");
    await driver.sendKeys(r1, SPACE);
    await driver.waitFor("return new URLSearchParams(location.search).get('rung') === 'R1';");
    const selected = await driver.execute(`
      const card = document.getElementById('card-R1');
      return {
        matrix: new URLSearchParams(location.search).get('matrix'),
        rung: new URLSearchParams(location.search).get('rung'),
        open: Boolean(card?.open),
        focused: document.activeElement?.tagName,
        canonical: card?.textContent?.includes('Canonical AtlasIndex 2.0'),
        core: card?.querySelectorAll('a[href*="core-learning"][href*="projection="]').length || 0,
        visual: card?.querySelectorAll('a[href*="shared-clock"]').length || 0,
        portable: card?.querySelectorAll('a[href*="portable-workbench"][href*="package=portable-motion-shared-clock"]').length || 0,
        hashFallbacks: card?.querySelectorAll('a[href="#"]').length || 0,
      };
    `);
    assert.equal(selected.matrix, "MATRIX-PHY-KIN-2D-MOTION");
    assert.equal(selected.rung, "R1");
    assert.equal(selected.open, true);
    assert.equal(selected.focused, "SUMMARY");
    assert.equal(selected.canonical, true);
    assert.ok(selected.core >= 1);
    assert.ok(selected.visual >= 1);
    assert.ok(selected.portable >= 1);
    assert.equal(selected.hashFallbacks, 0);

    await driver.execute(`
      [...document.querySelectorAll('.rung-node')].find(x => x.textContent.includes('R2'))?.click();
    `);
    await driver.waitFor("return new URLSearchParams(location.search).get('rung') === 'R2';");
    await driver.execute("history.back();");
    await driver.waitFor("return new URLSearchParams(location.search).get('rung') === 'R1';");

    await driver.navigate(motion + "?matrix=MATRIX-PHY-KIN-2D-MOTION&rung=R999");
    await driver.waitFor("return document.querySelector('.atlas-finding')?.textContent?.includes('ATLAS_TARGET_NOT_FOUND');");
    const invalid = await driver.execute(`
      return {
        finding: document.querySelector('.atlas-finding')?.textContent || '',
        coreActions: document.querySelectorAll('#rungCardsContainer a[href*="core-learning"]').length,
        visualActions: document.querySelectorAll('#rungCardsContainer a[href*="/explorers/"]').length
      };
    `);
    assert.match(invalid.finding, /ATLAS_TARGET_NOT_FOUND/);
    assert.equal(invalid.coreActions, 0);
    assert.equal(invalid.visualActions, 0);

    const math = `${staticServer.origin}/public/mathematics/linear-equations/index.html`;
    await driver.navigate(math + "?matrix=MATRIX-MATH-LINEAR-EQUATIONS&rung=R1");
    await driver.waitFor("return document.getElementById('card-R1')?.open === true;");
    const mathState = await driver.execute(`
      const card = document.getElementById('card-R1');
      return {
        text: card?.textContent || '',
        core: card?.querySelectorAll('a[href*="core-learning"]').length || 0,
        visual: card?.querySelectorAll('a[href*="/explorers/"]').length || 0,
        portable: card?.querySelectorAll('a[href*="portable-workbench"]').length || 0,
        lane: document.getElementById('progressionLaneContainer')?.textContent || ''
      };
    `);
    assert.match(mathState.text, /Representation:\s*READY/);
    assert.match(mathState.text, /Core:\s*READY/);
    assert.equal(mathState.core, 2);
    assert.equal(mathState.visual, 0);
    assert.equal(mathState.portable, 0);
    assert.doesNotMatch(mathState.lane, /Dynamics & Applications|Constraints & Quantitative/);

    const nlm = `${staticServer.origin}/public/physics/nlm/index.html?matrix=MATRIX-PHY-NLM-FIRST-LAW&rung=R4`;
    await driver.navigate(nlm);
    await driver.waitFor("return document.getElementById('card-R4')?.open === true;");
    await driver.execute("window.ATLAS.setKnowledgeInput('100');");
    const r4 = await driver.execute(`
      return {
        rung: new URLSearchParams(location.search).get('rung'),
        open: document.getElementById('card-R4')?.open,
        status: document.getElementById('estimateStatusText')?.textContent || ''
      };
    `);
    assert.equal(r4.rung, "R4");
    assert.equal(r4.open, true);
    assert.match(r4.status, /100%/);

    const fileUrl = pathToFileURL(join(repo, "public/physics/motion-2d/index.html")).href
      + "?matrix=MATRIX-PHY-KIN-2D-MOTION&rung=R1";
    await driver.navigate(fileUrl);
    await driver.waitFor("return Boolean(window.ATLAS && document.getElementById('card-R1')?.open);", [], 10000);
    const fileState = await driver.execute(`
      return {
        protocol: location.protocol,
        matrix: new URLSearchParams(location.search).get('matrix'),
        rung: new URLSearchParams(location.search).get('rung'),
        canonical: document.getElementById('card-R1')?.textContent?.includes('Canonical AtlasIndex 2.0'),
        portable: document.getElementById('card-R1')?.querySelectorAll('a[href*="portable-workbench"][href*="package=portable-motion-shared-clock"]').length || 0
      };
    `);
    assert.equal(fileState.protocol, "file:");
    assert.equal(fileState.matrix, "MATRIX-PHY-KIN-2D-MOTION");
    assert.equal(fileState.rung, "R1");
    assert.equal(fileState.canonical, true);
    assert.ok(fileState.portable >= 1);
  } finally {
    await driver.close();
    proc.child.kill("SIGTERM");
    await new Promise(ok => staticServer.server.close(ok));
  }
});
