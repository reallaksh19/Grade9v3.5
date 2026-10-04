#!/usr/bin/env node
/*
 * Chromium evidence for an interactive learner page.
 *
 * Usage:
 *   node tools/site-audit/interactive-page-audit.mjs page.html --json receipt.json --enforce
 *
 * A PASS receipt is evidence for the exact HTML bytes only. It does not authorize release.
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const htmlArg = process.argv[2];
if (!htmlArg) throw new Error('interactive HTML path required');
const htmlPath = path.resolve(htmlArg);
const jsonOut = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null;
const enforce = process.argv.includes('--enforce');
if (!fs.existsSync(htmlPath)) throw new Error('interactive HTML not found: ' + htmlPath);

const bytes = fs.readFileSync(htmlPath);
const htmlSha = crypto.createHash('sha256').update(bytes).digest('hex');
const browser = await playwright.chromium.launch();
const page = await browser.newPage();
const pageErrors = [];
const consoleErrors = [];
const externalRequests = [];
page.on('pageerror', error => pageErrors.push(String(error.message || error)));
page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
page.on('request', req => {
  const url = req.url();
  if (/^https?:\/\//i.test(url)) externalRequests.push(url);
});

const viewports = [
  { name: 'tablet-landscape', width: 1366, height: 854 },
  { name: 'tablet-portrait', width: 854, height: 1366 },
];
const measured = {};
let keyboardFocus = false;
for (const vp of viewports) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  await page.goto('file://' + htmlPath);
  await page.waitForLoadState('load');
  await page.keyboard.press('Tab');
  const facts = await page.evaluate(() => {
    const visible = el => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const controls = [...document.querySelectorAll('button,input,select,textarea,a[href],[role="button"],[tabindex]')]
      .filter(visible);
    const small = controls.filter(el => {
      const rect = el.getBoundingClientRect();
      const inlineLink = el.tagName === 'A' && !!el.closest('p,li,td');
      return !inlineLink && Math.min(rect.width, rect.height) < 48;
    });
    const unnamed = controls.filter(el => {
      const label = (el.getAttribute('aria-label') || el.getAttribute('title') || el.textContent || '').trim();
      return !label && !el.getAttribute('aria-labelledby');
    });
    return {
      readyState: document.readyState,
      bodyPresent: !!document.body,
      mainCount: document.querySelectorAll('main').length,
      h1Count: document.querySelectorAll('h1').length,
      interactiveControlCount: controls.filter(el => el.tagName !== 'A').length,
      smallTargets: small.length,
      unnamedControls: unnamed.length,
      horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      activeTag: document.activeElement ? document.activeElement.tagName : null,
      interactiveReady: window.__interactivePageReady === undefined ? null : window.__interactivePageReady === true,
    };
  });
  keyboardFocus = keyboardFocus || (facts.activeTag && facts.activeTag !== 'BODY' && facts.activeTag !== 'HTML');
  measured[vp.name] = facts;
}
await browser.close();

const all = Object.values(measured);
const checks = {
  runtime_smoke: {
    verdict: all.every(x => x.readyState === 'complete' && x.bodyPresent && x.interactiveControlCount > 0
      && (x.interactiveReady === null || x.interactiveReady === true)) ? 'PASS' : 'FAIL',
    evidence: measured,
  },
  page_errors: { verdict: pageErrors.length === 0 ? 'PASS' : 'FAIL', evidence: pageErrors },
  console_errors: { verdict: consoleErrors.length === 0 ? 'PASS' : 'FAIL', evidence: consoleErrors },
  external_requests: { verdict: externalRequests.length === 0 ? 'PASS' : 'FAIL', evidence: externalRequests },
  horizontal_overflow: {
    verdict: all.every(x => x.horizontalOverflowPx <= 1) ? 'PASS' : 'FAIL',
    evidence: Object.fromEntries(Object.entries(measured).map(([key,value]) => [key,value.horizontalOverflowPx])),
  },
  touch_targets: {
    verdict: all.every(x => x.smallTargets === 0) ? 'PASS' : 'FAIL',
    evidence: Object.fromEntries(Object.entries(measured).map(([key,value]) => [key,value.smallTargets])),
  },
  accessibility_baseline: {
    verdict: all.every(x => x.mainCount === 1 && x.h1Count >= 1 && x.unnamedControls === 0) ? 'PASS' : 'FAIL',
    evidence: Object.fromEntries(Object.entries(measured).map(([key,value]) => [key,{main:value.mainCount,h1:value.h1Count,unnamedControls:value.unnamedControls}])),
  },
  keyboard_focus: { verdict: keyboardFocus ? 'PASS' : 'FAIL', evidence: { focus_reached: keyboardFocus } },
};
const status = Object.values(checks).every(row => row.verdict === 'PASS') ? 'PASS' : 'FAIL';
const report = {
  schema: 'interactive-chromium-audit/v1',
  engine: 'chromium',
  html_path: path.relative(process.cwd(), htmlPath).split(path.sep).join('/'),
  html_sha256: 'sha256:' + htmlSha,
  audited_at: new Date().toISOString(),
  viewports,
  checks,
  status,
  note: 'Chromium evidence for these exact HTML bytes; not release approval.',
};
const payload = JSON.stringify(report, null, 2) + '\n';
if (jsonOut) fs.writeFileSync(jsonOut, payload);
else process.stdout.write(payload);
if (enforce && status !== 'PASS') process.exitCode = 1;
