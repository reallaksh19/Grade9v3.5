// Real Chromium evidence for R-2 through R-5. Called by test_learner_state.py.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const url = file => pathToFileURL(path.resolve(file)).href;
const browser = await playwright.chromium.launch();
const evidence = {};
try {
  const page = await browser.newPage();
  await page.goto(url(process.argv[2]));
  const article = page.locator('article[data-g9-unit]').first();
  const phrase = 'The printed decimal is rounded.';
  const liveText = () => article.evaluate(node => {
    const clone = node.cloneNode(true);
    clone.querySelectorAll('template').forEach(t => t.remove());
    return clone.textContent;
  });
  const before = await article.innerText();
  const beforeA11y = await article.ariaSnapshot();
  assert(!before.includes(phrase) && !beforeA11y.includes(phrase) && !(await liveText()).includes(phrase));
  evidence.source_protected_before = true;
  await page.locator('[data-g9-action="search"]').click();
  await page.locator('[data-g9-search-input]').fill(phrase);
  assert(!(await article.isVisible()));
  await page.locator('[data-g9-search-input]').fill('');
  evidence.search_excludes_protected = true;

  // Core2 v2 support stays collapsed until requested. Wrong-route content is
  // attempt-gated; genuinely safe source hints may be requested before commitment.
  const wrongRoute = article.locator('details[data-g9-payload-ref$="-wrong-route"]');
  assert.equal(await wrongRoute.count(), 1);
  assert.equal(await article.locator('[data-g9-block="common_wrong_route"]').count(), 0);
  await wrongRoute.locator('summary').click();
  assert.equal(await wrongRoute.evaluate(d => d.open), false);
  assert.equal(await article.getAttribute('data-g9-assisted'), null);

  const ladder = article.locator('.g9-ladder[data-g9-support-group="SOURCE_HINT"]');
  assert.equal(await ladder.locator('li[data-g9-rung]').count(), 0);
  assert(!(await ladder.innerText()).includes('Try an inverse operation.'));
  await ladder.locator('[data-g9-next-rung]').click();
  assert.equal(await ladder.locator('li[data-g9-rung]').count(), 1);
  assert.equal(await article.getAttribute('data-g9-assisted'), '1');
  assert((await article.getAttribute('data-g9-assistance')).split(',').includes('HINT_LADDER'));

  // Assistance provenance is durable for this question and survives a page reload.
  await page.reload();
  assert.equal(await article.getAttribute('data-g9-assisted'), '1');
  assert((await article.getAttribute('data-g9-assistance')).split(',').includes('HINT_LADDER'));
  assert.equal(await ladder.locator('li[data-g9-rung]').count(), 1);
  assert(!(await ladder.innerText()).includes('Remove the added 2 first.'));
  await ladder.locator('[data-g9-next-rung]').click();
  assert.equal(await ladder.locator('li[data-g9-rung]').count(), 2);
  assert(!(await ladder.innerText()).includes('The exact result is 7/3.'));
  // The third source hint reveals the result. Core2 v2 withholds it until the solution stage,
  // so the ladder ends after two rungs and the request control is spent.
  assert(await ladder.locator('[data-g9-next-rung]').isDisabled());
  assert(!(await liveText()).includes('The exact result is 7/3.'));
  evidence.progressive_hints = true;

  const box = article.locator('[data-g9-attempt-box]').first();
  await box.locator('[data-g9-commit]').click();
  assert.equal(await article.getAttribute('data-attempted'), null);
  assert(!(await liveText()).includes(phrase));
  await box.locator('[data-g9-choice]').first().check();
  await box.locator('[data-g9-commit]').click();
  assert.equal(await article.getAttribute('data-attempted'), '1');

  // AFTER_ATTEMPT wrong-route support materialises only after commitment and records
  // assistance provenance without creating diagnosis.
  assert.equal(await article.locator('[data-g9-block="common_wrong_route"]').count(), 1);
  await wrongRoute.locator('summary').click();
  assert.equal(await wrongRoute.evaluate(d => d.open), true);
  assert((await article.getAttribute('data-g9-assistance')).split(',').includes('WRONG_ROUTE'));
  evidence.after_attempt_wrong_route = true;

  await article.locator('details[data-g9-payload-ref$="-solution"] summary').click();
  assert((await article.innerText()).includes(phrase));
  assert((await article.ariaSnapshot()).includes(phrase));
  assert((await liveText()).includes(phrase));
  evidence.source_visible_after = true;

  // Exact concept navigation carries its origin in the URL so standalone file pages
  // do not depend on cross-file localStorage semantics. Returning to the question
  // restores the question's persisted assisted state.
  const originQuestion = await article.getAttribute('data-g9-unit');
  const conceptLink = article.locator('[data-g9-concept-link]').first();
  assert.equal(await conceptLink.count(), 1);
  const conceptHref = await conceptLink.getAttribute('href');
  assert(conceptHref.includes('g9-return=' + originQuestion));
  assert(conceptHref.includes('g9-concept=MIC-MATH-CONSTRAINT'));
  await Promise.all([
    page.waitForURL(/core1a\.html/),
    conceptLink.click(),
  ]);
  const returnLink = page.locator(
    '[data-g9-practice-link][data-g9-question-ref="' + originQuestion + '"][data-g9-return-link]'
  ).first();
  assert.equal(await returnLink.count(), 1);
  assert((await returnLink.innerText()).startsWith('Return to question ·'));
  await Promise.all([
    page.waitForURL(/core2\.html/),
    returnLink.click(),
  ]);
  const returnedArticle = page.locator('article[data-g9-unit="' + originQuestion + '"]');
  assert.equal(await returnedArticle.getAttribute('data-attempted'), '1');
  assert.equal(await returnedArticle.getAttribute('data-g9-assisted'), '1');
  const returnedAssistance = (await returnedArticle.getAttribute('data-g9-assistance')).split(',');
  assert(returnedAssistance.includes('HINT_LADDER'));
  assert(returnedAssistance.includes('WRONG_ROUTE'));
  assert(returnedAssistance.includes('CONCEPT_NAV'));
  evidence.concept_round_trip = true;
  evidence.assistance_persisted = true;

  await page.goto(url(process.argv[3]));
  const practice = page.locator('article[data-g9-unit]').first();
  assert.equal(await practice.locator('figure[data-g9-stage="POST_ATTEMPT"]').count(), 0);
  await practice.locator('textarea[data-g9-attempt]').first().fill('I worked the exact substitution.');
  await practice.locator('[data-g9-commit]').first().click();
  await practice.locator('details[data-requires-attempt] summary').first().click();
  const post = practice.locator('figure[data-g9-stage="POST_ATTEMPT"]').first();
  assert.equal(await post.count(), 1);
  assert.equal(await post.locator('[data-g9-stage-label]').innerText(), 'Stage 1 of 3');
  await post.locator('[data-g9-stage-step="next"]').click();
  assert.equal(await post.locator('[data-g9-stage-label]').innerText(), 'Stage 2 of 3');
  await post.locator('[data-g9-stage-step="next"]').click();
  assert.equal(await post.locator('[data-g9-stage-label]').innerText(), 'Stage 3 of 3');
  evidence.staged_figure = true;

  await page.goto(url(process.argv[4]));
  evidence.typed_controls = [];
  for (const kind of ['single_choice', 'multiple_choice', 'true_false', 'numeric', 'short_text',
                       'free_response', 'multipart', 'match']) {
    const item = page.locator(`article[data-g9-unit="${kind}"]`);
    const commit = item.locator('[data-g9-commit]');
    await item.locator('summary').click();
    await commit.click();
    assert.equal(await item.getAttribute('data-attempted'), null, `${kind} unlocked without a commitment`);
    if (kind === 'single_choice' || kind === 'multiple_choice' || kind === 'true_false') {
      await item.locator('[data-g9-choice]').first().check();
    } else if (kind === 'numeric') {
      await item.locator('[data-g9-number]').fill('nonsense');
      await commit.click();
      assert.equal(await item.getAttribute('data-attempted'), null);
      await item.locator('[data-g9-number]').fill('1e999');
      await commit.click();
      assert.equal(await item.getAttribute('data-attempted'), null);
      await item.locator('[data-g9-number]').fill('7/3');
    } else if (kind === 'short_text') {
      await item.locator('[data-g9-attempt]').fill('a');
    } else if (kind === 'free_response') {
      await item.locator('[data-g9-paper]').check();
    } else if (kind === 'multipart') {
      await item.locator('[data-g9-part-input]').nth(0).fill('2.3');
      await item.locator('[data-g9-part-input]').nth(1).fill('because');
    } else if (kind === 'match') {
      await item.locator('[data-g9-match]').nth(0).selectOption('0');
      await item.locator('[data-g9-match]').nth(1).selectOption('1');
    }
    await commit.click();
    assert.equal(await item.getAttribute('data-attempted'), '1', `${kind} failed valid commitment`);
    assert((await item.evaluate(node => {
      const clone = node.cloneNode(true);
      clone.querySelectorAll('template').forEach(t => t.remove());
      return clone.textContent;
    })).includes('Protected ' + kind));
    evidence.typed_controls.push(kind);
  }
  console.log(JSON.stringify(evidence));
} finally {
  await browser.close();
}
