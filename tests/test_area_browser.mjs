// Local artifact exercise, not a CI workflow. Requires a real Chromium installation.
//   node tests/test_area_browser.mjs
// Opens the TEST area's own pages in a real browser at phone, tablet and desktop widths and checks what a
// static read cannot: no script error, nothing fetched from another host, no sideways scroll, the draft label
// and the way to the portal are on screen and tappable, the Atlas shows an honest empty state, and once a
// matrix exists under TEST the same Atlas engine renders it. The TEST tab is reached from the portal.
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
const PAGES = ['test/index.html', 'test/atlas/index.html', 'test/rungs/index.html', 'test/deployments/index.html'];
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

async function open(width, page, { injectMatrix = false } = {}) {
  const context = await browser.newContext({ viewport: { width, height: 900 }, hasTouch: true });
  const tab = await context.newPage();
  const problems = [];
  tab.on('pageerror', (error) => problems.push(`script error: ${error.message}`));
  tab.on('console', (message) => { if (message.type() === 'error') problems.push(`console error: ${message.text()}`); });
  tab.on('request', (request) => { if (!request.url().startsWith(base) && !request.url().startsWith('data:')) problems.push(`left the site: ${request.url()}`); });
  tab.on('response', (response) => { if (response.status() >= 400) problems.push(`${response.status()} ${response.url().replace(base, '')}`); });
  if (injectMatrix) {
    // The real data.js, plus one matrix copied under TEST: what build_web_data.py produces once a TEST matrix exists.
    await tab.route('**/data/data.js', async (route) => {
      const original = await (await route.fetch()).text();
      const extra = "\n;(function(){var s=window.GRADE9V3.subjects;var m=JSON.parse(JSON.stringify(s.Mathematics.matrices[0]));"
        + "m.matrix_id='MATRIX-TEST-BROWSER';m.subject='TEST';s.TEST.matrices=[m];})();\n";
      await route.fulfill({ body: original + extra, contentType: 'text/javascript' });
    });
  }
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

// The Atlas with nothing under TEST: an empty state that says what to do, not a broken page.
for (const width of [390, 1280]) {
  const { context, tab, problems } = await open(width, 'test/atlas/index.html');
  const subtitle = (await tab.textContent('#atlasSubtopicSubtitle')).trim();
  const note = await tab.evaluate(() => (document.querySelector('.breadcrumb').nextElementSibling || {}).textContent || '');
  checked += 1;
  if (!/No TEST rung matrix yet/.test(subtitle)) failures.push(`atlas empty @${width}: subtitle is "${subtitle}"`);
  if (!/TEST\/matrices/.test(note) || !/build_web_data/.test(note)) failures.push(`atlas empty @${width}: the note does not say how to add a matrix ("${note.slice(0, 80)}")`);
  for (const problem of problems) failures.push(`atlas empty @${width}: ${problem}`);
  await context.close();
}

// The same page with a matrix under TEST: the real Atlas engine renders it, nothing from another subject appears.
for (const width of [390, 1280]) {
  const { context, tab, problems } = await open(width, 'test/atlas/index.html?matrix=MATRIX-TEST-BROWSER', { injectMatrix: true });
  await tab.waitForFunction(() => /Subtopic:/.test((document.getElementById('atlasSubtopicSubtitle') || {}).textContent || ''), null, { timeout: 8000 })
    .catch(() => failures.push(`atlas with matrix @${width}: the subtitle never showed a subtopic`));
  const facts = await tab.evaluate(() => ({
    subtitle: (document.getElementById('atlasSubtopicSubtitle') || {}).textContent || '',
    rungs: document.querySelectorAll('#rungs .rung-card, #rungs [data-rung], #rungs .card').length,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    text: document.body.innerText,
  }));
  checked += 1;
  if (!/MATRIX-TEST-BROWSER/.test(facts.subtitle)) failures.push(`atlas with matrix @${width}: subtitle is "${facts.subtitle}"`);
  if (facts.overflow > 1) failures.push(`atlas with matrix @${width}: ${facts.overflow}px wider than the screen`);
  if (/Laws of Motion|NLM/.test(facts.text)) failures.push(`atlas with matrix @${width}: the Laws of Motion template shows through`);
  for (const problem of problems) failures.push(`atlas with matrix @${width}: ${problem}`);
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
console.log(`PASS: the TEST pages hold at ${WIDTHS.length} widths, the Atlas shows its empty state and renders a TEST matrix, and the tab is reachable (${checked} checks)`);
