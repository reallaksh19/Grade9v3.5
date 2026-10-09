#!/usr/bin/env node
/** Real Chromium navigation smoke against the generated Core learner host. */
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { chromium } from "playwright";

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const port = 18763;
const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"],
  { cwd: repo, stdio: "ignore" });
let browser;
try {
  let available = false;
  for (let i = 0; i < 45; i += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/public/core-learning/index.html`);
      if (response.ok) { available = true; break; }
    } catch { /* server startup */ }
    await new Promise((done) => setTimeout(done, 150));
  }
  assert.ok(available, "Local Core learner host did not serve");
  browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1024, height: 820 } });
  const failures = [];
  page.on("pageerror", (error) => failures.push(error.message));
  await page.goto(`http://127.0.0.1:${port}/public/core-learning/index.html`);
  await page.waitForFunction(() => window.__coreLearningStaticHostReady === true);
  const b = await page.evaluate(() =>
    window.GRADE9V3_CORE.core_projections.find((row) => row?.projection?.core === "CORE1B")?.id
  );
  assert.ok(b, "No canonical Core1B compiler projection");
  await page.goto(`http://127.0.0.1:${port}/public/core-learning/index.html?projection=${encodeURIComponent(b)}`);
  await page.waitForFunction(() => window.__coreLearningStaticHostReady === true);
  const nav = page.locator("#core1-study-journey");
  assert.equal(await nav.isVisible(), true, "Canonical three-Core navigation absent");
  assert.match(await nav.innerText(), /Core1A.*Learn the construction/s);
  assert.match(await nav.innerText(), /Core1B.*Attempt reconstruction/s);
  const aButton = nav.getByRole("button", { name: /Core1A.*Learn the construction/ });
  await aButton.click();
  assert.match(await page.locator("#projection-status").innerText(), /CORE1A/);
  const bButton = nav.getByRole("button", { name: /Core1B.*Attempt reconstruction/ });
  await bButton.click();
  assert.match(await page.locator("#projection-status").innerText(), /CORE1B/);
  assert.match(await page.locator("#core1-study-note").innerText(), /Session assistance:/);
  assert.match(await page.locator("#core1-study-note").innerText(), /not an uncued mastery result/);
  const reveal = await page.evaluate(() => {
    const selected = document.getElementById("projection-select").value;
    const record = window.GRADE9V3_CORE.core_projections.find((row) => row.id === selected);
    const element = document.querySelector("core-learning-page");
    const markup = element.shadowRoot?.innerHTML ?? element.innerHTML;
    const answer = record?.projection?.concept?.elicitation?.attempt?.model_response;
    return { selected, answer, markup };
  });
  assert.equal(reveal.selected, b);
  assert.ok(reveal.answer && !reveal.markup.includes(reveal.answer),
    "Core1B completed model response was exposed before the learner attempt");
  assert.deepEqual(failures, [], "Browser JS errors during continuity route");
  console.log("PASS: compiler-bound Core1A → Core1B browser path and session assistance disclosure");
} finally {
  if (browser) await browser.close();
  server.kill();
}
