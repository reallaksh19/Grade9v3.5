#!/usr/bin/env node
/*
 * Focused rendered-browser falsifiers for #319 Core2-v2.
 *
 * This does not replace core-page-audit.mjs. The shared audit owns page-wide
 * shell/touch/overflow/search facts; this file owns only the stateful Core2-v2
 * interaction that requires navigation across Core2 and Core1A.
 *
 * Usage:
 *   node tools/site-audit/core2-v2-browser-audit.mjs \
 *     --base http://127.0.0.1:8765/<pages-product-path>/ \
 *     --single-base http://127.0.0.1:8765/<single-file-product-path>/ \
 *     --witness <selected-core2-question-id> \
 *     --audit-json /tmp/core-page-audit.json
 */
import { createRequire } from 'node:module';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { throw new Error('playwright is required; install it before running the Core2-v2 browser audit'); }

function arg(name, fallback = null) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const base = (arg('--base') || '').replace(/\/?$/, '/');
const singleBase = (arg('--single-base') || '').replace(/\/?$/, '/');
const auditJson = arg('--audit-json');
const WITNESS = arg('--witness');
const isLocal = value => /^https?:\/\/127\.0\.0\.1(?::\d+)?\//.test(value) || /^https?:\/\/localhost(?::\d+)?\//.test(value);
if (!isLocal(base)) throw new Error('--base must be a localhost/127.0.0.1 HTTP URL');
if (!isLocal(singleBase)) throw new Error('--single-base must be a localhost/127.0.0.1 HTTP URL');
if (!WITNESS) throw new Error('--witness must name one selected Core2 question id');
if (!auditJson || !fs.existsSync(auditJson)) throw new Error('--audit-json must point to the shared core-page-audit report');

const TABLET_VIEWPORTS = [
  { name: 'tablet-1366-landscape', width: 1366, height: 854, expanded: true },
  { name: 'tablet-1440-landscape', width: 1440, height: 900, expanded: true },
  { name: 'tablet-854-portrait', width: 854, height: 1366, expanded: false },
  { name: 'tablet-900-portrait', width: 900, height: 1440, expanded: false },
];

// The layout expected is the blueprint's: its fractions, not numbers written here.
const registry = JSON.parse(fs.readFileSync(new URL('../../Shared/web/interactive-page-blueprints.v1.json', import.meta.url), 'utf8'));
const core2Policy = registry.blueprints.find(b => b.core_roles.includes('CORE2')).responsive_policy;

const failures = [];
const notes = [];
const check = (condition, message) => { if (!condition) failures.push(message); };

// Reuse the shared audit as the authority for generic rendered-page facts.
const shared = JSON.parse(fs.readFileSync(auditJson, 'utf8'));
const core2Shared = shared['core2.html'];
check(!!core2Shared, 'shared audit has no core2.html result');
if (core2Shared) {
  check((core2Shared.errors || []).length === 0, `shared Core2 audit page errors: ${(core2Shared.errors || []).join(' | ')}`);
  for (const vp of TABLET_VIEWPORTS) {
    const row = core2Shared.viewports?.[vp.name];
    check(!!row, `shared audit missing ${vp.name}`);
    if (!row) continue;
    check(row.smallTargets === 0, `${vp.name}: ${row.smallTargets} touch target(s) below contract`);
    check(row.horizontalOverflowPx <= 1, `${vp.name}: page horizontal overflow ${row.horizontalOverflowPx}px`);
    check(row.wideElements === 0, `${vp.name}: ${row.wideElements} wide content element(s)`);
    check(row.hoverOnlyHandlers === 0, `${vp.name}: ${row.hoverOnlyHandlers} hover-only handler(s)`);
    check((row.externalRequests || []).length === 0, `${vp.name}: external request(s): ${(row.externalRequests || []).join(', ')}`);
    check(row.focusStyles === true, `${vp.name}: focus-visible styling not observed`);
    check(row.metadataMissingUnits === 0, `${vp.name}: ${row.metadataMissingUnits} unit(s) missing metadata`);
    check(row.searchCorpusMissingUnits === 0, `${vp.name}: ${row.searchCorpusMissingUnits} unit(s) missing safe search corpus`);
    check(row.protectedSearchMatches === 0, `${vp.name}: protected answer/reasoning matched page search`);
    check(row.gatedOpenBeforeAttempt === 0, `${vp.name}: gated disclosure open before attempt`);
    check(row.svgAccessible === row.svg, `${vp.name}: only ${row.svgAccessible}/${row.svg} SVG(s) accessible`);
  }
}

const browser = await playwright.chromium.launch({ headless: true });

async function articleMetrics(page, vp) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  await page.goto(`${base}core2.html#${WITNESS}`, { waitUntil: 'load' });
  const result = await page.locator(`#${WITNESS}`).evaluate((article) => {
    const split = article.querySelector('.g9-split');
    const style = split ? getComputedStyle(split) : getComputedStyle(article);
    const columns = style.gridTemplateColumns;
    const numbers = columns === 'none' ? [] : columns.split(/\s+/).map(v => Number.parseFloat(v)).filter(Number.isFinite);
    const ratio = numbers.length >= 2 ? numbers[0] / (numbers[0] + numbers[1]) : null;
    const support = article.querySelector('.g9-col-support');
    const attempt = article.querySelector('.g9-col-primary');
    const figure = article.querySelector('.slot-representation figure[data-g9-figure]');
    const stem = article.querySelector('[data-g9-block="stem"]');
    return {
      display: style.display,
      columns,
      ratio,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      figures: article.querySelectorAll('figure[data-g9-figure]').length,
      hasSourceFigure: !!figure,
      supportRungsInitial: article.querySelectorAll('.slot-support li[data-g9-rung]').length,
      supportTemplates: article.querySelectorAll('.slot-support template[data-g9-rung-payload]').length,
      supportRightOfAttempt: !!(support && attempt && support.getBoundingClientRect().left > attempt.getBoundingClientRect().left),
      sourceFigureRightOfStem: !!(figure && stem && figure.getBoundingClientRect().left > stem.getBoundingClientRect().left),
    };
  });
  check(result.overflow <= 1, `${vp.name}: focused Core2 overflow ${result.overflow}px`);
  check(result.supportRungsInitial === 0, `${vp.name}: support is materialised before learner request`);
  check(result.supportTemplates >= 1, `${vp.name}: no inert support payloads available for witness`);
  if (vp.expanded) {
    check(result.display === 'grid', `${vp.name}: the Core2 question is not an expanded two-column grid`);
    check(result.ratio !== null && Math.abs(result.ratio - core2Policy.primary_fraction) <= 0.03,
      `${vp.name}: primary/support ratio ${result.ratio} is not the blueprint's ${core2Policy.primary_fraction}/${core2Policy.support_fraction} (${result.columns})`);
    check(result.supportRightOfAttempt, `${vp.name}: support rail is not to the right of learner work`);
    // A source representation is contextual when one exists; source questions are
    // not required to invent a representation merely to occupy the rail.
    if (result.hasSourceFigure) {
      check(result.sourceFigureRightOfStem, `${vp.name}: source representation is not contextual in the support rail`);
    }
  } else {
    check(result.display !== 'grid' || result.columns === 'none', `${vp.name}: portrait retained two-column Core2 grid (${result.columns})`);
  }
  return result;
}

async function makeAttempt(attemptBox) {
  const choices = attemptBox.locator('[data-g9-choice]');
  if (await choices.count()) {
    await choices.first().check();
    return;
  }
  const matches = attemptBox.locator('[data-g9-match]');
  if (await matches.count()) {
    for (let i = 0; i < await matches.count(); i++) await matches.nth(i).selectOption({ index: 1 });
    return;
  }
  const numeric = attemptBox.locator('[data-g9-number]');
  if (await numeric.count()) {
    await numeric.fill('1');
    const unit = attemptBox.locator('[data-g9-unit-input]');
    if (await unit.count()) await unit.fill('m');
    return;
  }
  const parts = attemptBox.locator('[data-g9-part-input]');
  if (await parts.count()) {
    for (let i = 0; i < await parts.count(); i++) await parts.nth(i).fill('1');
    return;
  }
  const field = attemptBox.locator('[data-g9-attempt]').first();
  check(await field.count() === 1, 'witness has no usable learner attempt control');
  if (await field.count()) await field.fill('saved learner attempt');
}

async function controlState(attemptBox) {
  return attemptBox.locator('input,textarea,select').evaluateAll(elements => elements.map(el => ({
    tag: el.tagName,
    type: el.type || '',
    value: el.value,
    checked: !!el.checked,
  })));
}

// Native keyboard path: an Enter key must activate progressive support and the
// exact semantic concept link. Keep this isolated from the persistence witness.
const keyboardContext = await browser.newContext();
const keyboardPage = await keyboardContext.newPage();
const keyboardErrors = [];
keyboardPage.on('pageerror', error => keyboardErrors.push(error.message));
await keyboardPage.setViewportSize({ width: 1366, height: 854 });
await keyboardPage.goto(`${base}core2.html#${WITNESS}`, { waitUntil: 'load' });
const keyboardArticle = keyboardPage.locator(`#${WITNESS}`);
const keyboardSupport = keyboardArticle.locator('[data-g9-next-rung]:not([disabled]):visible').first();
check(await keyboardSupport.count() === 1, 'keyboard witness has no progressive support button');
if (await keyboardSupport.count()) {
  await keyboardSupport.focus();
  check(await keyboardSupport.evaluate(el => document.activeElement === el), 'keyboard support control could not receive focus');
  await keyboardSupport.press('Enter');
  check(await keyboardArticle.locator('.slot-support li[data-g9-rung]').count() >= 1, 'Enter did not activate progressive support');
}
const keyboardConcept = keyboardArticle.locator('[data-g9-concept-link]').first();
check(await keyboardConcept.count() === 1, 'keyboard witness has no exact Core1A concept link');
if (await keyboardConcept.count()) {
  const conceptRef = await keyboardConcept.getAttribute('data-g9-concept-ref');
  await keyboardConcept.focus();
  check(await keyboardConcept.evaluate(el => document.activeElement === el), 'keyboard concept link could not receive focus');
  await Promise.all([
    keyboardPage.waitForURL(url => url.pathname.endsWith('/core1a.html') && url.hash === `#${conceptRef}`),
    keyboardConcept.press('Enter'),
  ]);
  const keyboardUrl = new URL(keyboardPage.url());
  check(keyboardUrl.pathname.endsWith('/core1a.html') && keyboardUrl.hash === `#${conceptRef}`,
    `keyboard concept navigation landed at ${keyboardPage.url()}`);
}
check(keyboardErrors.length === 0, `keyboard runtime leaked page error(s): ${keyboardErrors.join(' | ')}`);
await keyboardContext.close();

const context = await browser.newContext();
const page = await context.newPage();
const pageErrors = [];
page.on('pageerror', error => pageErrors.push(error.message));
for (const vp of TABLET_VIEWPORTS) await articleMetrics(page, vp);

// Exercise one real attempt, optional bounded support disclosure, raw reload,
// and the PAGES Core2 -> Core1A -> exact Core2 question round trip. A nested
// Prompt/Reveal disclosure is only applicable when the canonical witness has a
// paired authored prompt; absence is not a product defect.
await page.setViewportSize({ width: 1366, height: 854 });
await page.goto(`${base}core2.html#${WITNESS}`, { waitUntil: 'load' });
let article = page.locator(`#${WITNESS}`);
let box = article.locator('[data-g9-attempt-box]');
await makeAttempt(box);
await box.locator('[data-g9-commit]').click();
check(await article.getAttribute('data-attempted') === '1', 'witness did not record learner commitment');

const firstSupportButton = article.locator('[data-g9-next-rung]:not([disabled]):visible').first();
check(await firstSupportButton.count() === 1, 'witness has no progressive support button');
if (await firstSupportButton.count()) await firstSupportButton.click();

const authoredSupportButton = article.locator('[data-g9-support-group="AUTHORED_CORE2_PROMPT_REVEAL"] [data-g9-next-rung]:not([disabled]):visible').first();
if (await authoredSupportButton.count()) await authoredSupportButton.click();
const supportReveal = article.locator('details[data-g9-support-reveal]').first();
const hasBoundedDisclosure = await supportReveal.count() === 1;
if (hasBoundedDisclosure) {
  await supportReveal.locator('summary').click();
  await page.waitForTimeout(50);
  check(await supportReveal.evaluate(el => el.open), 'bounded support disclosure did not open');
} else {
  notes.push('bounded authored-support disclosure persistence: NOT_APPLICABLE for selected production witness');
}

const controlStateBefore = await controlState(box);
const rungCountBefore = await article.locator('.slot-support li[data-g9-rung]').count();
check(rungCountBefore >= 1, 'support request did not materialise a rung');

await page.reload({ waitUntil: 'load' });
article = page.locator(`#${WITNESS}`);
box = article.locator('[data-g9-attempt-box]');
check(await article.getAttribute('data-attempted') === '1', 'learner commitment was not restored after raw reload');
check(JSON.stringify(await controlState(box)) === JSON.stringify(controlStateBefore), 'typed/selected learner attempt state changed after raw reload');
check(await article.locator('.slot-support li[data-g9-rung]').count() === rungCountBefore, 'support depth changed after raw reload');
if (hasBoundedDisclosure) {
  const reloadedReveal = article.locator('details[data-g9-support-reveal]').first();
  check(await reloadedReveal.count() === 1 && await reloadedReveal.evaluate(el => el.open), 'bounded support disclosure state was not restored after raw reload');
}

const conceptLink = article.locator('[data-g9-concept-link]').first();
check(await conceptLink.count() === 1, 'witness has no exact Core1A concept link');
let conceptRef = null;
if (await conceptLink.count()) {
  conceptRef = await conceptLink.getAttribute('data-g9-concept-ref');
  await Promise.all([
    page.waitForURL(url => url.pathname.endsWith('/core1a.html') && url.hash === `#${conceptRef}`),
    conceptLink.click(),
  ]);
}

if (conceptRef) {
  const returnLink = page.locator(`[data-g9-practice-link][data-g9-question-ref="${WITNESS}"][data-g9-concept-ref="${conceptRef}"]`);
  check(await returnLink.count() === 1, 'Core1A did not expose the exact reverse practice link');
  if (await returnLink.count()) {
    const hasReturnMarker = await returnLink.evaluate(el => el.hasAttribute('data-g9-return-link'));
    const returnLabel = (await returnLink.textContent()).trim();
    check(hasReturnMarker, 'matching reverse link was not marked as Return to question');
    check(returnLabel.startsWith('Return to question'), `matching reverse link has no Return to question affordance: ${returnLabel}`);
    await Promise.all([
      page.waitForURL(url => url.pathname.endsWith('/core2.html') && url.hash === `#${WITNESS}`),
      returnLink.click(),
    ]);
  }
}

check(page.url().includes(`core2.html#${WITNESS}`), `round trip did not return to exact witness: ${page.url()}`);
const restored = page.locator(`#${WITNESS}`);
check(await restored.getAttribute('data-attempted') === '1', 'learner commitment was not restored after concept detour');
const restoredBox = restored.locator('[data-g9-attempt-box]');
check(JSON.stringify(await controlState(restoredBox)) === JSON.stringify(controlStateBefore), 'typed/selected learner attempt state changed across concept detour');
const rungCountAfter = await restored.locator('.slot-support li[data-g9-rung]').count();
check(rungCountAfter === rungCountBefore, `support depth changed across concept detour (${rungCountBefore} → ${rungCountAfter})`);
check(pageErrors.length === 0, `browser page error(s): ${pageErrors.join(' | ')}`);
await context.close();

// SINGLE_FILE is same-document navigation. The return affordance must therefore
// refresh immediately after the Core2 concept-link click, without relying on a reload.
const singleContext = await browser.newContext();
const singlePage = await singleContext.newPage();
const singleErrors = [];
singlePage.on('pageerror', error => singleErrors.push(error.message));
await singlePage.setViewportSize({ width: 1366, height: 854 });
await singlePage.goto(`${singleBase}product.html#g9-CORE2--${WITNESS}`, { waitUntil: 'load' });
let singleArticle = singlePage.locator(`#g9-CORE2--${WITNESS}`);
let singleBox = singleArticle.locator('[data-g9-attempt-box]');
await makeAttempt(singleBox);
await singleBox.locator('[data-g9-commit]').click();
check(await singleArticle.getAttribute('data-attempted') === '1', 'SINGLE_FILE witness did not record learner commitment');
const singleSupportButton = singleArticle.locator('[data-g9-next-rung]:not([disabled]):visible').first();
check(await singleSupportButton.count() === 1, 'SINGLE_FILE witness has no progressive support button');
if (await singleSupportButton.count()) await singleSupportButton.click();
const singleRungCount = await singleArticle.locator('.slot-support li[data-g9-rung]').count();
const singleControlState = await controlState(singleBox);
const singleConceptLink = singleArticle.locator('[data-g9-concept-link]').first();
check(await singleConceptLink.count() === 1, 'SINGLE_FILE witness has no exact Core1A concept link');
let singleConceptRef = null;
if (await singleConceptLink.count()) {
  singleConceptRef = await singleConceptLink.getAttribute('data-g9-concept-ref');
  await Promise.all([
    singlePage.waitForURL(url => url.pathname.endsWith('/product.html') && url.hash === `#g9-CORE1A--${singleConceptRef}`),
    singleConceptLink.click(),
  ]);
}
if (singleConceptRef) {
  const singleReturnLink = singlePage.locator(`[data-g9-practice-link][data-g9-question-ref="${WITNESS}"][data-g9-concept-ref="${singleConceptRef}"]`);
  check(await singleReturnLink.count() === 1, 'SINGLE_FILE Core1A did not expose the exact reverse practice link');
  if (await singleReturnLink.count()) {
    check(await singleReturnLink.evaluate(el => el.hasAttribute('data-g9-return-link')), 'SINGLE_FILE reverse link was not dynamically marked as Return to question');
    check((await singleReturnLink.textContent()).trim().startsWith('Return to question'), 'SINGLE_FILE reverse link was not dynamically relabelled as Return to question');
    await Promise.all([
      singlePage.waitForURL(url => url.pathname.endsWith('/product.html') && url.hash === `#g9-CORE2--${WITNESS}`),
      singleReturnLink.click(),
    ]);
  }
}
check(singlePage.url().includes(`product.html#g9-CORE2--${WITNESS}`), `SINGLE_FILE round trip did not return to exact witness: ${singlePage.url()}`);
singleArticle = singlePage.locator(`#g9-CORE2--${WITNESS}`);
singleBox = singleArticle.locator('[data-g9-attempt-box]');
check(await singleArticle.getAttribute('data-attempted') === '1', 'SINGLE_FILE learner commitment changed across same-document concept detour');
check(JSON.stringify(await controlState(singleBox)) === JSON.stringify(singleControlState), 'SINGLE_FILE typed/selected attempt state changed across concept detour');
check(await singleArticle.locator('.slot-support li[data-g9-rung]').count() === singleRungCount, 'SINGLE_FILE support depth changed across concept detour');
await singlePage.reload({ waitUntil: 'load' });
singleArticle = singlePage.locator(`#g9-CORE2--${WITNESS}`);
singleBox = singleArticle.locator('[data-g9-attempt-box]');
check(await singleArticle.getAttribute('data-attempted') === '1', 'SINGLE_FILE learner commitment did not restore after reload');
check(JSON.stringify(await controlState(singleBox)) === JSON.stringify(singleControlState), 'SINGLE_FILE typed/selected attempt state did not restore after reload');
check(await singleArticle.locator('.slot-support li[data-g9-rung]').count() === singleRungCount, 'SINGLE_FILE support depth did not restore after reload');
check(singleErrors.length === 0, `SINGLE_FILE runtime leaked page error(s): ${singleErrors.join(' | ')}`);
await singleContext.close();

// Storage failure must preserve exact URL-bound return navigation. localStorage is only
// a compatibility fallback; query-bound g9-return/g9-concept is the primary PAGES contract.
const blockedContext = await browser.newContext();
await blockedContext.addInitScript(() => {
  for (const method of ['getItem', 'setItem', 'removeItem']) {
    Object.defineProperty(Storage.prototype, method, {
      configurable: true,
      value() { throw new Error('storage blocked by audit'); },
    });
  }
});
const blocked = await blockedContext.newPage();
const blockedErrors = [];
blocked.on('pageerror', error => blockedErrors.push(error.message));
await blocked.setViewportSize({ width: 1366, height: 854 });
await blocked.goto(`${base}core2.html#${WITNESS}`, { waitUntil: 'load' });
const blockedConcept = blocked.locator(`#${WITNESS} [data-g9-concept-link]`).first();
check(await blockedConcept.count() === 1, 'storage-blocked page lost static concept navigation');
if (await blockedConcept.count()) {
  const blockedConceptRef = await blockedConcept.getAttribute('data-g9-concept-ref');
  await Promise.all([
    blocked.waitForURL(url => url.pathname.endsWith('/core1a.html') && url.hash === `#${blockedConceptRef}`),
    blockedConcept.click(),
  ]);
  const ordinaryPractice = blocked.locator(`[data-g9-practice-link][data-g9-question-ref="${WITNESS}"][data-g9-concept-ref="${blockedConceptRef}"]`);
  check(await ordinaryPractice.count() === 1, 'storage-blocked Core1A page lost exact practice link');
  if (await ordinaryPractice.count()) {
    const urlBoundReturn = await ordinaryPractice.evaluate(el => el.hasAttribute('data-g9-return-link'));
    const returnLabel = (await ordinaryPractice.textContent()).trim();
    check(urlBoundReturn, 'storage-blocked path lost URL-bound exact return state');
    check(returnLabel.startsWith('Return to question'),
      `storage-blocked exact return link was not relabelled: ${returnLabel}`);
    await Promise.all([
      blocked.waitForURL(url => url.pathname.endsWith('/core2.html') && url.hash === `#${WITNESS}`),
      ordinaryPractice.click(),
    ]);
    check(blocked.url().includes(`core2.html#${WITNESS}`), 'storage-blocked URL-bound return did not reach exact question');
  }
}
check(blockedErrors.length === 0, `storage-blocked runtime leaked page error(s): ${blockedErrors.join(' | ')}`);
await blockedContext.close();
await browser.close();

if (failures.length) {
  console.error(`Core2-v2 browser audit: ${failures.length} failure(s)`);
  for (const failure of failures) console.error(`  - ${failure}`);
  process.exit(1);
}
for (const note of notes) console.log(`Core2-v2 browser audit NOTE: ${note}`);
console.log(`Core2-v2 browser audit PASS: ${TABLET_VIEWPORTS.length} viewport(s), visible keyboard/support controls, reload persistence, PAGES + SINGLE_FILE exact state round trips, URL-bound storage-failure fallback.`);
