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
    const elicitation = record?.projection?.concept?.elicitation;
    // The production Core1B is RUBRIC-closed, not MODEL_RESPONSE-closed.
    // Protect the actual authored prediction and boundary answers, rather than
    // assuming a nonexistent model_response field.
    const protectedAnswers = [
      elicitation?.predict?.defensible_answer,
      elicitation?.attempt?.model_response,
      elicitation?.boundary_test?.answer,
    ].filter((item) => typeof item === "string" && item.trim().length > 0);
    return {
      selected,
      protectedAnswers,
      text: element.shadowRoot?.textContent ?? element.textContent,
      reconstructionMounted: Boolean(element.shadowRoot?.querySelector(".core1b-reconstruction")),
      attempted: element.state?.attempted,
    };
  });
  assert.equal(reveal.selected, b);
  assert.ok(reveal.protectedAnswers.length > 0,
    "This canonical Core1B projection must have real authored answer-bearing closure");
  assert.equal(reveal.attempted, false);
  assert.equal(reveal.reconstructionMounted, false,
    "Core1B complete reconstruction was mounted before the learner attempt");
  for (const answer of reveal.protectedAnswers) {
    assert.ok(!reveal.text.includes(answer),
      "Core1B authored answer-bearing closure was visible before attempt");
  }
  const postReconstruction = await page.evaluate(() => {
    const element = document.querySelector("core-learning-page");
    element.commitAttempt("My own reconstruction of the shared idea and model boundary.");
    return {
      attempted: element.state?.attempted,
      reconstructionMounted: Boolean(element.shadowRoot?.querySelector(".core1b-reconstruction")),
      text: element.shadowRoot?.textContent ?? element.textContent,
    };
  });
  assert.equal(postReconstruction.attempted, true);
  assert.equal(postReconstruction.reconstructionMounted, true,
    "Committed Core1B response must unlock its actual authored reconstruction");
  assert.ok(reveal.protectedAnswers.some((answer) => postReconstruction.text.includes(answer)),
    "Core1B canonical answer-bearing closure did not appear after commitment");
  // Real familiar-to-transfer route. Visiting B directly must not claim
  // learner prior exposure merely because the package contains a parent.
  const transferId = await page.evaluate(() =>
    window.GRADE9V3_CORE.core_projections.find((record) =>
      record?.source_ref === "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"
      && record?.projection?.core === "CORE2B")?.id
  );
  assert.ok(transferId, "Existing canonical 2B changed-decision witness not compiled");
  await page.goto(`http://127.0.0.1:${port}/public/core-learning/index.html?projection=${encodeURIComponent(transferId)}`);
  await page.waitForFunction(() => window.__coreLearningStaticHostReady === true);
  const transferNav = page.locator("#familiar-transfer");
  assert.equal(await transferNav.isVisible(), true, "Familiar-transfer navigation missing");
  assert.match(await page.locator("#familiar-transfer-note").innerText(), /prior capability is unverified/i);
  await transferNav.getByRole("button", { name: /Core2A.*Familiar worked application/ }).click();
  assert.match(await page.locator("#projection-status").innerText(), /CORE2A/);
  // Opening A alone is not proof its worked explanation was encountered.
  await transferNav.getByRole("button", { name: /Core2B.*Attempt changed decision/ }).click();
  assert.match(await page.locator("#familiar-transfer-note").innerText(), /worked explanation was not observed/i);
  await transferNav.getByRole("button", { name: /Core2A.*Familiar worked application/ }).click();
  await page.evaluate(() => {
    document.querySelector("core-learning-page").commitAttempt("I choose the familiar event condition.");
  });
  // Core2A reasoning becomes visible only after the learner's submitted attempt.
  assert.match(await page.locator("#projection-status").innerText(), /CORE2A/);
  await transferNav.getByRole("button", { name: /Core2B.*Attempt changed decision/ }).click();
  assert.match(await page.locator("#projection-status").innerText(), /CORE2B/);
  assert.match(await page.locator("#familiar-transfer-note").innerText(),
    /assisted by instructional exposure, not certified mastery/i);
  const beforeAttempt = await page.evaluate(() => {
    const item = window.GRADE9V3_CORE.core_projections.find((row) =>
      row.id === document.getElementById("projection-select").value);
    const protectedId = item?.projection?.application?.transfer?.protected_move_ref;
    const protectedStep = item?.projection?.application?.reasoning_route?.find((move) =>
      move.id === protectedId);
    const content = document.querySelector("core-learning-page");
    return {
      protectedKind: protectedStep?.kind,
      protectedAction: protectedStep?.action,
      invariant: item.projection.application.transfer.invariant,
      changedDemandStatement: item.projection.application.transfer.statement,
      navText: document.getElementById("familiar-transfer").innerText,
      markup: content.shadowRoot?.innerHTML ?? content.innerHTML,
    };
  });
  assert.equal(beforeAttempt.protectedKind, "DECIDE");
  assert.ok(beforeAttempt.protectedAction
    && !beforeAttempt.markup.includes(beforeAttempt.protectedAction),
    "Core2B protected DECIDE action leaked into the pre-attempt DOM");
  assert.ok(!beforeAttempt.navText.includes(beforeAttempt.invariant)
    && !beforeAttempt.navText.includes(beforeAttempt.changedDemandStatement),
    "Navigation revealed the Core2B model/invariant before an attempt");
  await page.evaluate(() => {
    document.querySelector("core-learning-page").commitAttempt("I first choose the release model and explain it.");
  });
  const afterAttemptNav = await page.locator("#familiar-transfer").innerText();
  assert.ok(afterAttemptNav.includes(beforeAttempt.invariant)
    && afterAttemptNav.includes(beforeAttempt.changedDemandStatement),
    "Author transfer explanation was not disclosed after the B attempt");
  const repair = page.locator("#repair-return");
  assert.equal(await repair.isVisible(), true, "Question-specific repair route unavailable");
  assert.match(await page.locator("#repair-return-note").innerText(), /no error or misconception has been diagnosed/i);
  await page.locator("#repair-return-action").click();
  assert.match(await page.locator("#projection-status").innerText(), /CORE1A/);
  assert.match(await page.locator("#repair-return-note").innerText(), /K2D3-1/);
  const stepFocus = await page.evaluate(() => {
    const shadow = document.querySelector("core-learning-page").shadowRoot;
    const target = shadow.querySelector('[data-teaching-step="K2D3-1"]');
    return { exists: Boolean(target), focused: shadow.activeElement === target, text: target?.innerText || "" };
  });
  assert.equal(stepFocus.exists, true, "Canonical target step not in constructed lesson");
  assert.equal(stepFocus.focused, true, "Exact repair step did not receive keyboard focus");
  assert.match(stepFocus.text, /free flight after release/i);
  await page.locator("#repair-return-action").click();
  assert.match(await page.locator("#projection-status").innerText(), /CORE2B/);
  assert.match(await page.locator("#repair-return-note").innerText(), /same-question retry is assisted practice/i);
  const assistedReturn = await page.evaluate(() => ({
    attempted: document.querySelector("core-learning-page").state.attempted,
    model: window.GRADE9V3_CORE.core_projections.find((r) =>
      r.id === document.getElementById("projection-select").value
    ).projection.application.transfer.statement,
    nav: document.getElementById("familiar-transfer").innerText,
  }));
  assert.equal(assistedReturn.attempted, false, "Returning to B must reset attempt gate");
  assert.ok(!assistedReturn.nav.includes(assistedReturn.model),
    "Assisted retry must not bypass preattempt W disclosure");
  // Pages actually consumes docs/js mirrors, not public/js; check that host too.
  await page.goto(`http://127.0.0.1:${port}/docs/core-learning/index.html?projection=${encodeURIComponent(transferId)}`);
  await page.waitForFunction(() => window.__coreLearningStaticHostReady === true);
  assert.equal(await page.locator("#familiar-transfer").isVisible(), true);
  assert.match(await page.locator("#repair-return-note").innerText(), /attempt this changed-decision question first/i);
  assert.deepEqual(failures, [], "Browser JS errors during continuity route");
  console.log("PASS: compiler-bound Core1A → Core1B browser path and session assistance disclosure");
} finally {
  if (browser) await browser.close();
  server.kill();
}
