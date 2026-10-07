import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const url = process.argv[2];
if (!url) throw new Error('usage: node tests/iss66_support_state_browser.mjs <url>');

const browser = await chromium.launch({headless: true});
try {
  const page = await browser.newPage({viewport: {width: 1280, height: 800}});
  await page.goto(url, {waitUntil: 'networkidle'});

  const article = page.locator('article[data-g9-role="CORE2"]').filter({hasText: 'p_k(x)'}).first();
  assert.equal(await article.count(), 1);

  const after = article.locator('details[data-requires-attempt]').filter({has: page.getByText('More support after your attempt', {exact: true})});
  const solution = article.locator('details[data-requires-attempt]').filter({has: page.getByText('Answer and working', {exact: true})});
  assert.equal(await after.count(), 1);
  assert.equal(await solution.count(), 1);

  // PRE_ATTEMPT: both disclosures are locked and neither payload is visible.
  assert.equal(await after.getAttribute('data-locked'), '');
  assert.equal(await solution.getAttribute('data-locked'), '');
  assert.equal(await after.locator('[data-g9-payload-slot]').innerText(), '');
  assert.equal(await solution.locator('[data-g9-payload-slot]').innerText(), '');

  const attempt = article.locator('[data-g9-attempt]').first();
  await attempt.fill('I committed my route before asking for more help.');
  await article.locator('[data-g9-commit]').first().click();
  assert.equal(await article.getAttribute('data-attempted'), '1');
  assert.equal(await after.getAttribute('data-locked'), null);
  assert.equal(await solution.getAttribute('data-locked'), null);

  // AFTER_ATTEMPT: open only the support disclosure.
  await after.locator('summary').click();
  assert.equal(await after.getAttribute('open'), '');
  assert.equal(await solution.getAttribute('open'), null);
  const moved = after.locator('[data-g9-block="after_attempt_support"] [data-g9-support-source]').first();
  assert.equal(await moved.count(), 1);
  const movedRef = await moved.getAttribute('data-g9-support-source');
  assert.ok(movedRef);
  assert.equal(await moved.isVisible(), true);
  assert.equal(await article.locator('[data-g9-stage-id="WORKED"]').isVisible(), false);

  // POST_SOLUTION: only opening Answer and working exposes the WORKED visual.
  await solution.locator('summary').click();
  assert.equal(await solution.getAttribute('open'), '');
  assert.equal(await article.locator('[data-g9-stage-id="WORKED"]').isVisible(), true);
  assert.equal(
    await solution.locator('[data-g9-block="completed_support"] [data-g9-support-source="' + movedRef + '"]').count(),
    0,
  );

  console.log(JSON.stringify({
    pre_attempt_locked: true,
    after_attempt_support_visible: true,
    solution_closed_during_after_attempt_support: true,
    worked_visual_visible_only_after_solution_open: true,
    moved_support_ref: movedRef,
  }));
} finally {
  await browser.close();
}
