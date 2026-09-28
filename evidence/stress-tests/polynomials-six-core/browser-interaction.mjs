// Browser witness for the empty Polynomials control and the Mathematics candidate.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }
const base = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(?=[A-Za-z]:)/, ''));
const browser = await playwright.chromium.launch();
const results = {};
for (const [label, dir] of [['polynomials-empty', 'rendered'], ['golden-control', 'golden-control']]) {
  const page = await browser.newPage({ viewport: { width: 800, height: 1280 } });
  await page.goto('file://' + path.join(base, dir, 'core1a.html'));
  const before = await page.evaluate(() => ({
    units: document.querySelectorAll('[data-g9-unit]').length,
    attempts: document.querySelectorAll('[data-g9-attempt-box]').length,
    locked: document.querySelectorAll('details[data-locked]').length,
    searchCorpus: [...document.querySelectorAll('[data-g9-search-text]')].map(e => e.dataset.g9SearchText),
    visibleMainText: document.querySelector('main')?.innerText,
  }));
  await page.locator('[data-g9-action="search"]').click();
  await page.locator('[data-g9-search-input]').fill('no-matching-query-927');
  const search = await page.evaluate(() => ({ panelHidden: document.querySelector('[data-g9-search-panel]').hidden, visibleUnits: [...document.querySelectorAll('[data-g9-unit]')].filter(e => !e.hidden).length }));
  await page.locator('[data-g9-search-input]').fill('');
  let attempt = { status: 'NOT_APPLICABLE_NO_ATTEMPT' };
  if (before.attempts) {
    await page.locator('details[data-requires-attempt] summary').first().click();
    const blocked = await page.locator('details[data-requires-attempt]').first().evaluate(e => !e.open);
    await page.locator('[data-g9-attempt]').first().fill('my attempt');
    await page.locator('[data-g9-commit]').first().click();
    const unlocked = await page.locator('details[data-requires-attempt]').first().evaluate(e => !e.hasAttribute('data-locked'));
    attempt = { status: 'MEASURED', blockedBeforeCommit: blocked, unlockedAfterCommit: unlocked };
  }
  const accessibility = await page.locator('main').ariaSnapshot();
  results[label] = { viewport: { width: 800, height: 1280 }, before, search, attempt, accessibility };
  await page.close();
}
await browser.close();
fs.writeFileSync(path.join(base, 'browser-interaction.json'), JSON.stringify(results, null, 2) + '\n');
