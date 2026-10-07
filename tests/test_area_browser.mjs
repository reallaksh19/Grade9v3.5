// Real-browser TEST sandbox audit. Runs in learner-platform-code-tests and can also be run locally:
//   node tests/test_area_browser.mjs
// Opens the TEST area's own pages in a real browser at phone, tablet and desktop widths and checks what a
// static read cannot: no script error, nothing fetched from another host, no sideways scroll, the draft label
// and the way to the portal are on screen and tappable, and the real TEST polynomial matrix renders through
// the shared Atlas engine. The TEST tab is reached from the portal.
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'playwright')); }

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'public');
const PAGES = ['test/index.html', 'test/question-bank/index.html', 'test/atlas/index.html', 'test/rungs/index.html', 'test/deployments/index.html'];
const WIDTHS = [320, 390, 768, 1024, 1280, 1920];
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };

const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
  fs.createReadStream(file).pipe(res);
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await playwright.chromium.launch();

const failures = [];
let checked = 0;

async function open(width, page, { height = 900 } = {}) {
  const context = await browser.newContext({ viewport: { width, height }, hasTouch: true });
  const tab = await context.newPage();
  const problems = [];
  tab.on('pageerror', (error) => problems.push(`script error: ${error.message}`));
  tab.on('console', (message) => { if (message.type() === 'error') problems.push(`console error: ${message.text()}`); });
  tab.on('request', (request) => { if (!request.url().startsWith(base) && !request.url().startsWith('data:')) problems.push(`left the site: ${request.url()}`); });
  tab.on('response', (response) => { if (response.status() >= 400) problems.push(`${response.status()} ${response.url().replace(base, '')}`); });
  await tab.goto(`${base}/${page}`, { waitUntil: 'networkidle' });
  return { context, tab, problems };
}

for (const page of PAGES) {
  for (const width of WIDTHS) {
    const { context, tab, problems } = await open(width, page);
    const facts = await tab.evaluate(() => {
      const bannerNode = document.querySelector('[data-g9-test-banner]');
      const banner = bannerNode && bannerNode.getBoundingClientRect().height > 0 ? bannerNode.textContent : '';
      const links = [...document.querySelectorAll('header[data-g9-test-banner] a')];
      const small = links.filter((a) => Math.min(a.getBoundingClientRect().width, a.getBoundingClientRect().height) < 44);
      return {
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        banner,
        barLinks: links.length,
        small: small.map((a) => a.textContent),
        html: document.documentElement.outerHTML,
        title: document.title,
      };
    });
    checked += 1;
    const where = `${page} @${width}`;
    for (const problem of problems) failures.push(`${where}: ${problem}`);
    if (facts.overflow > 1) failures.push(`${where}: ${facts.overflow}px wider than the screen`);
    if (!/not accepted/.test(facts.banner)) failures.push(`${where}: the draft label is not visible ("${facts.banner.slice(0, 60)}")`);
    if (facts.small.length) failures.push(`${where}: header links under 44px: ${facts.small.join(', ')}`);
    if (!/data-g9-shell/.test(facts.html)) failures.push(`${where}: no shell marker`);
    if (!/TEST/.test(facts.title)) failures.push(`${where}: the title does not say TEST ("${facts.title}")`);
    await context.close();
  }
}

// The NCERT TEST Question Bank must materialize all parked questions without losing its validation boundary.
for (const width of [390, 1280]) {
  const { context, tab, problems } = await open(width, 'test/question-bank/index.html');
  await tab.waitForFunction(() => document.querySelectorAll('[data-g9-test-question]').length === 210, null, { timeout: 8000 })
    .catch(() => failures.push(`question bank @${width}: 210 cards never materialized`));
  const facts = await tab.evaluate(() => ({
    cards: document.querySelectorAll('[data-g9-test-question]').length,
    unvalidated: document.querySelectorAll('[data-g9-validation="UNVALIDATED"]').length,
    sourceVerified: document.querySelectorAll('[data-g9-source-verification="SOURCE VERIFIED"]').length,
    duplicateReview: document.querySelectorAll('[data-g9-review="DUPLICATE_REVIEW"]').length,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  checked += 1;
  if (facts.cards !== 210) failures.push(`question bank @${width}: expected 210 cards, got ${facts.cards}`);
  if (facts.unvalidated !== 210) failures.push(`question bank @${width}: expected 210 UNVALIDATED cards, got ${facts.unvalidated}`);
  if (facts.sourceVerified !== 210) failures.push(`question bank @${width}: expected 210 source-verified cards, got ${facts.sourceVerified}`);
  if (facts.duplicateReview !== 1) failures.push(`question bank @${width}: expected one duplicate-review card, got ${facts.duplicateReview}`);
  if (facts.overflow > 1) failures.push(`question bank @${width}: ${facts.overflow}px wider than the screen`);

  await tab.locator('#tqbUnit').selectOption('Unit 2: Polynomials');
  await tab.waitForTimeout(50);
  const visiblePolynomials = await tab.locator('[data-g9-test-question]:not([hidden])').count();
  if (visiblePolynomials !== 30) failures.push(`question bank @${width}: Unit 2 filter shows ${visiblePolynomials}, expected 30`);
  for (const problem of problems) failures.push(`question bank @${width}: ${problem}`);
  await context.close();
}

// The real TEST matrix: the TEST-local projection feeds the existing Atlas engine.
for (const width of [390, 1280]) {
  const { context, tab, problems } = await open(width, 'test/atlas/index.html?matrix=MATRIX-TEST-ISS55-POLY');
  await tab.waitForFunction(() => /Subtopic:/.test((document.getElementById('atlasSubtopicSubtitle') || {}).textContent || ''), null, { timeout: 8000 })
    .catch(() => failures.push(`atlas real matrix @${width}: the subtitle never showed a subtopic`));
  const facts = await tab.evaluate(() => ({
    subtitle: (document.getElementById('atlasSubtopicSubtitle') || {}).textContent || '',
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    text: document.body.innerText,
    hasLocalData: !!document.querySelector('script[data-g9-test-atlas-data]'),
  }));
  checked += 1;
  if (!/MATRIX-TEST-ISS55-POLY/.test(facts.subtitle)) failures.push(`atlas real matrix @${width}: subtitle is "${facts.subtitle}"`);
  if (!facts.hasLocalData) failures.push(`atlas real matrix @${width}: TEST-local Atlas data script is missing`);
  if (!/Degree-Bounded Polynomial Identity|Interval Sign Charts|Auxiliary Variable Substitution/.test(facts.text)) {
    failures.push(`atlas real matrix @${width}: polynomial rung content did not render`);
  }
  if (facts.overflow > 1) failures.push(`atlas real matrix @${width}: ${facts.overflow}px wider than the screen`);
  if (/Laws of Motion|NLM/.test(facts.text)) failures.push(`atlas real matrix @${width}: the Laws of Motion template shows through`);
  for (const problem of problems) failures.push(`atlas real matrix @${width}: ${problem}`);
  await context.close();
}

// On a 12.7-inch tablet (either way up) the real Atlas has no undersized controls/text and no overflow.
for (const [width, height] of [[1366, 854], [854, 1366]]) {
  const { context, tab, problems } = await open(width, 'test/atlas/index.html?matrix=MATRIX-TEST-ISS55-POLY', { height });
  await tab.waitForFunction(() => /Subtopic:/.test((document.getElementById('atlasSubtopicSubtitle') || {}).textContent || ''), null, { timeout: 8000 }).catch(() => {});
  const facts = await tab.evaluate(() => {
    const shown = (el) => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && !el.closest('[hidden]') && getComputedStyle(el).visibility !== 'hidden'; };
    const small = [...document.querySelectorAll('a[href], button, input, select, summary, [role=button]')].filter((el) => shown(el) && el.getBoundingClientRect().height < 47.5)
      .map((el) => `${el.tagName.toLowerCase()} "${(el.textContent || el.getAttribute('aria-label') || el.type || '').trim().slice(0, 20)}" ${Math.round(el.getBoundingClientRect().height)}px`);
    const tiny = new Set();
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const parent = node.parentElement;
      if (!node.textContent.trim() || !parent || parent.closest('script, style, [hidden]') || !shown(parent)) continue;
      const size = parseFloat(getComputedStyle(parent).fontSize);
      if (size < 14) tiny.add(`${parent.tagName.toLowerCase()}.${String(parent.className).split(' ')[0]} ${size}px`);
    }
    return { small, tiny: [...tiny], overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
  });
  checked += 1;
  const where = `atlas real matrix @${width}x${height}`;
  if (facts.small.length) failures.push(`${where}: controls under 48px: ${facts.small.slice(0, 6).join('; ')}`);
  if (facts.tiny.length) failures.push(`${where}: text under 14px: ${facts.tiny.slice(0, 6).join('; ')}`);
  if (facts.overflow > 1) failures.push(`${where}: ${facts.overflow}px wider than the screen`);
  for (const problem of problems) failures.push(`${where}: ${problem}`);
  await context.close();
}

// The tab: from the portal and from each subject hub, one tap reaches the TEST hub, and the hub reaches the other pages.
for (const from of ['index.html', 'physics/index.html', 'chemistry/index.html', 'mathematics/index.html']) {
  const { context, tab, problems } = await open(390, from);
  const link = tab.locator('a[data-site-test]').first();
  const count = await link.count();
  checked += 1;
  if (!count) failures.push(`${from}: no TEST tab`);
  else {
    // On a phone the shared header folds its tabs behind the "more" button, like every other tab.
    if (!(await link.isVisible())) await tab.locator('.site-more-btn').click();
    await link.click({ timeout: 4000 }).catch((error) => failures.push(`${from}: the TEST tab cannot be tapped: ${error.message.split('\n')[0]}`));
    await tab.waitForLoadState('networkidle');
    if (!/\/test\/index\.html$/.test(tab.url())) failures.push(`${from}: the TEST tab led to ${tab.url().replace(base, '')}`);
    for (const label of ['Atlas', 'Rungs', 'Deployments']) {
      if (!(await tab.locator('nav[data-g9-breadcrumb] a', { hasText: label }).count())) failures.push(`${from}: the TEST hub has no ${label} link`);
    }
  }
  for (const problem of problems) failures.push(`${from}: ${problem}`);
  await context.close();
}

await browser.close();
server.close();

if (failures.length) {
  console.log(failures.join('\n'));
  console.log(`\nFAIL: ${failures.length} problem(s) in ${checked} checks`);
  process.exit(1);
}
console.log(`PASS: the TEST pages hold at ${WIDTHS.length} widths, the 210-question TEST bank preserves its validation boundary, the real polynomial Atlas renders from local data, and the tab is reachable (${checked} checks)`);
