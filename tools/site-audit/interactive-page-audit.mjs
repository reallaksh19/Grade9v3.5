#!/usr/bin/env node
/*
 * Mandatory Chromium audit for standalone interactive learner pages.
 *
 * Usage:
 *   node tools/site-audit/interactive-page-audit.mjs path/to/page.html \
 *     --profile tablet-12.7 --json path/to/report.json [--head <sha>]
 *
 * The report binds the exact HTML SHA-256 to Playwright Chromium measurements.
 */
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const args = process.argv.slice(2);
const fileArg = args[0];
if (!fileArg) throw new Error('interactive HTML path is required');
const file = path.resolve(fileArg);
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : null;
const profile = args.includes('--profile') ? args[args.indexOf('--profile') + 1] : 'tablet-12.7';
const headSha = args.includes('--head') ? args[args.indexOf('--head') + 1] : null;
if (profile !== 'tablet-12.7') throw new Error(`unsupported interactive audit profile: ${profile}`);
if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw new Error(`interactive HTML not found: ${file}`);

const TABLET_12_7_VIEWPORTS = [
  { name: 'tablet-1366-landscape', width: 1366, height: 854 },
  { name: 'tablet-1440-landscape', width: 1440, height: 900 },
  { name: 'tablet-854-portrait', width: 854, height: 1366 },
  { name: 'tablet-900-portrait', width: 900, height: 1440 },
];

const artifactSha = 'sha256:' + createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const browser = await playwright.chromium.launch();
const page = await browser.newPage();
const pageErrors = [];
const consoleErrors = [];
const externalRequests = [];

page.on('pageerror', error => pageErrors.push(String(error.message || error)));
page.on('console', msg => {
  if (msg.type() === 'error') consoleErrors.push(msg.text());
});
page.on('request', request => {
  const url = request.url();
  if (/^https?:\/\//i.test(url)) externalRequests.push(url);
});

const report = {
  schema: 'interactive-page-audit/v1',
  tool: 'tools/site-audit/interactive-page-audit.mjs',
  engine: 'playwright.chromium',
  profile,
  head_sha: headSha,
  artifact_path: path.relative(process.cwd(), file).split(path.sep).join('/'),
  artifact_sha256: artifactSha,
  viewports: {},
  page_errors: pageErrors,
  console_errors: consoleErrors,
  external_requests: externalRequests,
  status: 'FAIL',
};

for (const vp of TABLET_12_7_VIEWPORTS) {
  await page.setViewportSize({ width: vp.width, height: vp.height });
  await page.goto('file://' + file, { waitUntil: 'load' });

  const measured = await page.evaluate(() => {
    const visible = el => {
      const b = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return b.width > 0 && b.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };
    const controls = [...document.querySelectorAll('a[href],button,summary,input,select,textarea,[role="button"]')].filter(visible);
    const small = controls.filter(el => {
      const b = el.getBoundingClientRect();
      const inlineLink = el.tagName === 'A' && !!el.closest('p,li,td');
      return !inlineLink && Math.min(b.width, b.height) < 48;
    });
    const wide = [...document.querySelectorAll('svg,canvas,table,pre,figure,.interactive,.explorer')]
      .filter(visible)
      .filter(el => el.getBoundingClientRect().right > document.documentElement.clientWidth + 1);

    let focusFailures = 0;
    let focusVisibleFailures = 0;
    for (const el of controls.filter(el => !el.disabled && el.getAttribute('aria-disabled') !== 'true')) {
      el.focus({ preventScroll: true });
      if (document.activeElement !== el) {
        focusFailures += 1;
        continue;
      }
      const style = getComputedStyle(el);
      const outline = parseFloat(style.outlineWidth) || 0;
      const shadow = style.boxShadow && style.boxShadow !== 'none';
      if (!(outline > 0 || shadow)) focusVisibleFailures += 1;
    }

    const svgs = [...document.querySelectorAll('svg')].filter(visible);
    const inaccessibleSvgs = svgs.filter(svg =>
      !svg.querySelector('title') &&
      !svg.getAttribute('aria-label') &&
      !svg.getAttribute('aria-labelledby')
    );

    return {
      controls: controls.length,
      smallTargets: small.length,
      smallTargetSample: small.slice(0, 5).map(el => {
        const b = el.getBoundingClientRect();
        return `${el.tagName.toLowerCase()} ${Math.round(b.width)}x${Math.round(b.height)} "${(el.textContent || '').trim().slice(0, 30)}"`;
      }),
      horizontalOverflowPx: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
      wideElements: wide.length,
      focusFailures,
      focusVisibleFailures,
      svgCount: svgs.length,
      inaccessibleSvgCount: inaccessibleSvgs.length,
      mainCount: document.querySelectorAll('main').length,
      headingCount: document.querySelectorAll('h1,h2,h3').length,
    };
  });

  report.viewports[vp.name] = measured;
}

await browser.close();

const failures = [];
if (pageErrors.length) failures.push(`page errors: ${pageErrors.length}`);
if (consoleErrors.length) failures.push(`console errors: ${consoleErrors.length}`);
if (externalRequests.length) failures.push(`external requests: ${externalRequests.length}`);
for (const [name, row] of Object.entries(report.viewports)) {
  if (row.smallTargets) failures.push(`${name}: small targets ${row.smallTargets}`);
  if (row.horizontalOverflowPx > 1) failures.push(`${name}: horizontal overflow ${row.horizontalOverflowPx}px`);
  if (row.wideElements) failures.push(`${name}: wide elements ${row.wideElements}`);
  if (row.focusFailures) failures.push(`${name}: focus failures ${row.focusFailures}`);
  if (row.focusVisibleFailures) failures.push(`${name}: focus-visible failures ${row.focusVisibleFailures}`);
  if (row.inaccessibleSvgCount) failures.push(`${name}: inaccessible SVGs ${row.inaccessibleSvgCount}`);
  if (row.mainCount !== 1) failures.push(`${name}: expected exactly one main landmark`);
  if (row.headingCount < 1) failures.push(`${name}: no learner heading`);
}
report.failures = failures;
report.status = failures.length ? 'FAIL' : 'PASS';

const json = JSON.stringify(report, null, 2) + '\n';
if (jsonOut) fs.writeFileSync(jsonOut, json);
console.log(json.trim());
process.exitCode = failures.length ? 1 : 0;
