#!/usr/bin/env node
/*
 * Tablet audit for the deployed Grade9V3 site (docs/), run in a real browser.
 *
 * Crawls every page reachable from the portal plus every page in data/site-map.js, at the
 * 10-inch tablet viewports in docs/specs/TABLET-SHELL-AND-NAVIGATION.md, and checks the
 * shell contract of that spec. Prints a report and exits 1 if any BLOCKING check fails.
 *
 *   python -m http.server 8765            (from the repository root, in another terminal)
 *   node tools/site-audit/tablet-audit.mjs [--base http://127.0.0.1:8765/docs/] [--json out.json] [--page physics/index.html]
 *
 * Needs Playwright: `npm i -D playwright` then `npx playwright install chromium`
 * (or set PLAYWRIGHT_BROWSERS_PATH to an existing browser install).
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, all) => {
  if (v.startsWith('--')) acc.push([v.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]);
  return acc;
}, []));
const BASE = (args.base || 'http://127.0.0.1:8765/docs/').replace(/\/?$/, '/');

// 10-inch tablets in CSS pixels: Android 10.1" (1280x800 at DPR 1.5) and iPad 10.9" (1180x820).
const VIEWPORTS = [
  { name: 'android-landscape', width: 1280, height: 800 },
  { name: 'android-portrait', width: 800, height: 1280 },
  { name: 'ipad-landscape', width: 1180, height: 820 },
];
const MIN_TAP = 44;          // px, shortest side of any control
const MIN_TEXT = 14;         // px, smallest rendered text at default settings
const EXPLORER = /\/explorers\//;

const BLOCKING = new Set([
  'HTTP_ERROR', 'JS_ERROR', 'BROKEN_LINK', 'H_OVERFLOW', 'NO_SHELL', 'HEADER_NOT_STICKY',
  'SEARCH_BROKEN', 'DISPLAY_BROKEN', 'THEME_BROKEN', 'ZOOM_BROKEN', 'NO_BREADCRUMB',
  'EXTERNAL_REQUEST', 'TAP_TARGET_SMALL', 'TEXT_TOO_SMALL',
]);

function rel(url) { return url.replace(BASE, '').split('#')[0].split('?')[0] || 'index.html'; }

async function sitemapPages(page) {
  try {
    await page.goto(BASE + 'data/site-map.js');
    const text = await page.evaluate(() => document.body.innerText);
    const json = JSON.parse(text.slice(text.indexOf('{'), text.lastIndexOf('}') + 1));
    return (json.pages || []).map(p => p.path);
  } catch { return []; }
}

async function checkPage(ctx, path) {
  const issues = [];
  const add = (code, detail = '', viewport = '') => issues.push({ code, detail: String(detail).slice(0, 160), viewport });
  const page = await ctx.newPage();
  page.on('pageerror', e => add('JS_ERROR', e.message));
  page.on('console', m => { if (m.type() === 'error' && !/favicon/.test(m.text())) add('JS_ERROR', m.text()); });
  page.on('request', r => { const u = r.url(); if (!u.startsWith(BASE) && !u.startsWith('data:') && !u.startsWith('blob:')) add('EXTERNAL_REQUEST', u); });
  page.on('response', r => { if (r.status() >= 400 && r.url().startsWith(BASE)) add('HTTP_ERROR', `${r.status()} ${rel(r.url())}`); });

  const links = new Set();
  for (const vp of VIEWPORTS) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    try { await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 25000 }); }
    catch (e) { add('HTTP_ERROR', e.message, vp.name); continue; }
    await page.waitForTimeout(300);
    const r = await page.evaluate(({ MIN_TAP, MIN_TEXT }) => {
      const out = {};
      out.links = [...document.querySelectorAll('a[href]')].map(a => a.href);
      out.overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
      out.shell = document.documentElement.hasAttribute('data-g9-shell');
      const visible = el => { const b = el.getBoundingClientRect(); const s = getComputedStyle(el); return b.width > 0 && b.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
      const describe = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '') + ' "' + (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 24) + '"';
      out.smallTargets = [...document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[role=button],summary')]
        .filter(visible).filter(el => { const b = el.getBoundingClientRect(); return Math.min(b.width, b.height) < MIN_TAP && !el.closest('p,li,td'); })
        .slice(0, 400).map(describe);
      out.smallText = [...document.querySelectorAll('body *')].filter(el => el.childElementCount === 0 && el.textContent.trim() && visible(el))
        .filter(el => parseFloat(getComputedStyle(el).fontSize) < MIN_TEXT).slice(0, 400).map(el => describe(el) + ' ' + getComputedStyle(el).fontSize);
      out.breadcrumb = !!document.querySelector('nav[data-g9-breadcrumb] a');
      return out;
    }, { MIN_TAP, MIN_TEXT });
    r.links.forEach(l => links.add(l));
    if (r.overflow > 2) add('H_OVERFLOW', `${r.overflow}px wider than the screen`, vp.name);
    if (r.smallTargets.length) add('TAP_TARGET_SMALL', `${r.smallTargets.length}: ${r.smallTargets.slice(0, 4).join(' | ')}`, vp.name);
    if (r.smallText.length) add('TEXT_TOO_SMALL', `${r.smallText.length}: ${r.smallText.slice(0, 3).join(' | ')}`, vp.name);
    if (!r.shell) { add('NO_SHELL', 'html[data-g9-shell] missing', vp.name); continue; }
    if (path !== 'index.html' && !r.breadcrumb) add('NO_BREADCRUMB', 'nav[data-g9-breadcrumb] has no link', vp.name);

    // Sticky header after scrolling.
    const sticky = await page.evaluate(async () => {
      window.scrollTo(0, 1500); await new Promise(res => setTimeout(res, 150));
      const h = document.querySelector('[data-g9-shell-header]');
      if (!h) return 'missing';
      const b = h.getBoundingClientRect(); window.scrollTo(0, 0);
      return b.top <= 1 && b.bottom > 0 ? 'ok' : `top=${b.top}`;
    });
    if (sticky !== 'ok') add('HEADER_NOT_STICKY', sticky, vp.name);
    if (vp !== VIEWPORTS[0]) continue;   // interaction checks once per page

    // Search opens, finds a known topic, and results are links.
    try {
      await page.click('[data-g9-action="search"]');
      const input = page.locator('[data-g9-search-input]');
      await input.fill('projectile');
      await page.waitForTimeout(400);
      const hits = await page.locator('[data-g9-search-results] a[href]').count();
      if (!hits) add('SEARCH_BROKEN', 'no results for "projectile"');
      await page.keyboard.press('Escape');
    } catch (e) { add('SEARCH_BROKEN', e.message); }

    // Display panel: font size, theme and zoom change and persist.
    try {
      await page.click('[data-g9-action="display"]');
      const before = await page.evaluate(() => parseFloat(getComputedStyle(document.documentElement).fontSize));
      await page.click('[data-g9-font="inc"]');
      const after = await page.evaluate(() => parseFloat(getComputedStyle(document.documentElement).fontSize));
      if (!(after > before)) add('DISPLAY_BROKEN', `font ${before}px -> ${after}px`);
      await page.click('[data-g9-font="reset"]');
      await page.click('[data-g9-theme="light"]');
      const theme = await page.evaluate(() => document.documentElement.dataset.theme);
      if (theme !== 'light') add('THEME_BROKEN', `data-theme=${theme}`);
      await page.click('[data-g9-theme="dark"]');
      await page.click('[data-g9-zoom="inc"]');
      const zoom = await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--g9-zoom').trim());
      if (zoom !== '1.1') add('ZOOM_BROKEN', `--g9-zoom=${zoom} after one step (expected 1.1)`);
      await page.click('[data-g9-zoom="reset"]');
      await page.keyboard.press('Escape');
    } catch (e) { add('DISPLAY_BROKEN', e.message); }
  }
  await page.close();
  return { issues, links: [...links] };
}

const browser = await playwright.chromium.launch();
const ctx = await browser.newContext({ hasTouch: true, deviceScaleFactor: 1.5 });
const probe = await ctx.newPage();
const queue = args.page ? [args.page] : ['index.html', ...(await sitemapPages(probe))];
await probe.close();
const seen = new Set(queue);
const report = { base: BASE, viewports: VIEWPORTS, pages: {} };
while (queue.length) {
  const path = queue.shift();
  const { issues, links } = await checkPage(ctx, path);
  report.pages[path] = issues;
  for (const href of links) {
    if (!href.startsWith(BASE)) continue;
    let target = rel(href);
    if (target.endsWith('/')) target += 'index.html';
    if (!target.endsWith('.html')) continue;
    const probeResp = await ctx.request.get(BASE + target).catch(() => null);
    if (!probeResp || probeResp.status() >= 400) { issues.push({ code: 'BROKEN_LINK', detail: target, viewport: '' }); continue; }
    if (!args.page && !seen.has(target)) { seen.add(target); queue.push(target); }
  }
}
await browser.close();

let blocking = 0;
const lines = [];
for (const [path, issues] of Object.entries(report.pages)) {
  const unique = [...new Map(issues.map(i => [i.code + i.detail + i.viewport, i])).values()];
  report.pages[path] = unique;
  unique.forEach(i => { if (BLOCKING.has(i.code)) blocking++; });
  lines.push(`${unique.length ? '✗' : '✓'} ${path}`);
  unique.slice(0, 12).forEach(i => lines.push(`    ${i.code}${i.viewport ? ' [' + i.viewport + ']' : ''} ${i.detail}`));
}
console.log(lines.join('\n'));
console.log(`\n${Object.keys(report.pages).length} pages, ${blocking} blocking issue(s).`);
if (args.json) fs.writeFileSync(args.json, JSON.stringify(report, null, 2));
process.exit(blocking ? 1 : 0);
