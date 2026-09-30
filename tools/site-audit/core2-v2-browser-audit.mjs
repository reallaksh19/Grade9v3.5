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
 *     --base http://127.0.0.1:8765/products/physics/phy-kin-2d-motion/ \
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
const auditJson = arg('--audit-json');
if (!/^https?:\/\/127\.0\.0\.1(?::\d+)?\//.test(base) && !/^https?:\/\/localhost(?::\d+)?\//.test(base)) {
  throw new Error('--base must be a localhost/127.0.0.1 HTTP URL');
}
if (!auditJson || !fs.existsSync(auditJson)) throw new Error('--audit-json must point to the shared core-page-audit report');

const WITNESS = 'PYQ-PHY-IITJEE-2011-P2-Q33';
const TABLET_VIEWPORTS = [
  { name: 'tablet-1366-landscape', width: 1366, height: 854, expanded: true },
  { name: 'tablet-1440-landscape', width: 1440, height: 900, expanded: true },
  { name: 'tablet-854-portrait', width: 854, height: 1366, expanded: false },
  { name: 'tablet-900-portrait', width: 900, height: 1440, expanded: false },
];

const failures = [];
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
    const style = getComputedStyle(article);
    const columns = style.gridTemplateColumns;
    const numbers = columns === 'none' ? [] : columns.split(/\s+/).map(v => Number.parseFloat(v)).filter(Number.isFinite);
    const ratio = numbers.length >= 2 ? numbers[0] / (numbers[0] + numbers[1]) : null;
    const support = article.querySelector('.slot-support');
    const attempt = article.querySelector('.slot-attempt');
    const figure = article.querySelector('.slot-attempt figure[data-g9-figure]');
    return {
      display: style.display,
      columns,
      ratio,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      figures: article.querySelectorAll('figure[data-g9-figure]').length,
      supportRungsInitial: article.querySelectorAll('.slot-support li[data-g9-rung]').length,
      supportTemplates: article.querySelectorAll('.slot-support template[data-g9-rung-payload]').length,
      supportRightOfAttempt: !!(support && attempt && support.getBoundingClientRect().left > attempt.getBoundingClientRect().left),
      sourceFigureRightOfStem: !!(figure && article.querySelector('[data-g9-block="stem"]') && figure.getBoundingClientRect().left > article.querySelector('[data-g9-block="stem"]').getBoundingClientRect().left),
    };
  });
  check(result.overflow <= 1, `${vp.name}: focused Core2 overflow ${result.overflow}px`);
  check(result.supportRungsInitial === 0, `${vp.name}: support is materialised before learner request`);
  check(result.supportTemplates >= 1, `${vp.name}: no inert support payloads available for witness`);
  if (vp.expanded) {
    check(result.display === 'grid', `${vp.name}: Core2 article is not an expanded grid`);
    check(result.ratio !== null && result.ratio >= 0.66 && result.ratio <= 0.70,
      `${vp.name}: primary/support ratio ${result.ratio} is not approximately 68/32 (${result.columns})`);
    check(result.supportRightOfAttempt, `${vp.name}: support rail is not to the right of learner work`);
    check(result.sourceFigureRightOfStem, `${vp.name}: source representation is not contextual in the support rail`);
  } else {
    check(result.display !== 'grid' || result.columns === 'none', `${vp.name}: portrait retained two-column Core2 grid (${result.columns})`);
  }
  return result;
}

const context = await browser.newContext();
const page = await context.newPage();
const pageErrors = [];
page.on('pageerror', error => pageErrors.push(error.message));
for (const vp of TABLET_VIEWPORTS) await articleMetrics(page, vp);

// Exercise one real attempt and support state at an expanded tablet viewport.
await page.setViewportSize({ width: 1366, height: 854 });
await page.goto(`${base}core2.html#${WITNESS}`, { waitUntil: 'load' });
const article = page.locator(`#${WITNESS}`);
const box = article.locator('[data-g9-attempt-box]');

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

await makeAttempt(box);
await box.locator('[data-g9-commit]').click();
check(await article.getAttribute('data-attempted') === '1', 'witness did not record learner commitment');

const firstSupportButton = article.locator('[data-g9-next-rung]:not([disabled])').first();
check(await firstSupportButton.count() === 1, 'witness has no progressive support button');
if (await firstSupportButton.count()) await firstSupportButton.click();
const rungCountBefore = await article.locator('.slot-support li[data-g9-rung]').count();
check(rungCountBefore >= 1, 'support request did not materialise a rung');

const controlStateBefore = await box.locator('input,textarea,select').evaluateAll(elements => elements.map(el => ({
  tag: el.tagName,
  type: el.type || '',
  value: el.value,
  checked: !!el.checked,
})));

const conceptLink = article.locator('[data-g9-concept-link]').first();
check(await conceptLink.count() === 1, 'witness has no exact Core1A concept link');
let conceptRef = null;
if (await conceptLink.count()) {
  conceptRef = await conceptLink.getAttribute('data-g9-concept-ref');
  await Promise.all([page.waitForLoadState('load'), conceptLink.click()]);
  check(page.url().includes(`core1a.html#${conceptRef}`), `concept navigation landed at ${page.url()}`);
}

if (conceptRef) {
  const returnLink = page.locator(`[data-g9-practice-link][data-g9-question-ref="${WITNESS}"][data-g9-concept-ref="${conceptRef}"]`);
  check(await returnLink.count() === 1, 'Core1A did not expose the exact reverse practice link');
  if (await returnLink.count()) {
    check(await returnLink.getAttribute('data-g9-return-link') === 'true', 'matching reverse link was not marked as Return to question');
    check((await returnLink.textContent()).trim() === 'Return to question', 'matching reverse link was not relabelled Return to question');
    await Promise.all([page.waitForLoadState('load'), returnLink.click()]);
  }
}

check(page.url().includes(`core2.html#${WITNESS}`), `round trip did not return to exact witness: ${page.url()}`);
const restored = page.locator(`#${WITNESS}`);
check(await restored.getAttribute('data-attempted') === '1', 'learner commitment was not restored after concept detour');
const restoredBox = restored.locator('[data-g9-attempt-box]');
const controlStateAfter = await restoredBox.locator('input,textarea,select').evaluateAll(elements => elements.map(el => ({
  tag: el.tagName,
  type: el.type || '',
  value: el.value,
  checked: !!el.checked,
})));
check(JSON.stringify(controlStateAfter) === JSON.stringify(controlStateBefore), 'typed/selected learner attempt state changed across concept detour');
const rungCountAfter = await restored.locator('.slot-support li[data-g9-rung]').count();
check(rungCountAfter === rungCountBefore, `support depth changed across concept detour (${rungCountBefore} → ${rungCountAfter})`);
check(pageErrors.length === 0, `browser page error(s): ${pageErrors.join(' | ')}`);
await context.close();

// Storage failure must degrade to ordinary exact navigation, not break the product.
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
  await Promise.all([blocked.waitForLoadState('load'), blockedConcept.click()]);
  const ordinaryPractice = blocked.locator(`[data-g9-practice-link][data-g9-question-ref="${WITNESS}"][data-g9-concept-ref="${blockedConceptRef}"]`);
  check(await ordinaryPractice.count() === 1, 'storage-blocked Core1A page lost ordinary exact practice link');
  if (await ordinaryPractice.count()) {
    check(await ordinaryPractice.getAttribute('data-g9-return-link') !== 'true', 'storage-blocked path falsely claims saved return state');
    await Promise.all([blocked.waitForLoadState('load'), ordinaryPractice.click()]);
    check(blocked.url().includes(`core2.html#${WITNESS}`), 'storage-blocked ordinary practice link did not return to exact question');
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
console.log(`Core2-v2 browser audit PASS: ${TABLET_VIEWPORTS.length} viewport(s), exact state round trip, storage-failure fallback.`);
