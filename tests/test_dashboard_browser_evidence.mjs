// Exact TEST dashboard browser evidence.
//   node tests/test_dashboard_browser_evidence.mjs [out-dir]
// Captures desktop/tablet screenshots, measured horizontal overflow and keyboard Tab order.
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'playwright')); }

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const root = path.join(repo, 'public');
const outDir = path.resolve(process.argv[2] || '/tmp/test-dashboard-browser-evidence');
fs.mkdirSync(outDir, { recursive: true });

const TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.png': 'image/png',
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://x');
  const file = path.join(root, decodeURIComponent(url.pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404);
    res.end('not found');
    return;
  }
  res.writeHead(200, {
    'content-type': TYPES[path.extname(file)] || 'application/octet-stream',
    'cache-control': 'no-store',
  });
  fs.createReadStream(file).pipe(res);
});

await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await playwright.chromium.launch({ headless: true });

const profiles = [
  { id: 'desktop-1440x900', width: 1440, height: 900 },
  { id: 'tablet-portrait-854x1366', width: 854, height: 1366 },
  { id: 'tablet-landscape-1366x854', width: 1366, height: 854 },
];

const report = {
  tool: 'tests/test_dashboard_browser_evidence.mjs',
  page: 'test/index.html',
  profiles: [],
  status: 'PASS',
};

const failures = [];

for (const profile of profiles) {
  const context = await browser.newContext({
    viewport: { width: profile.width, height: profile.height },
    hasTouch: true,
  });
  const page = await context.newPage();
  const errors = [];
  const failedRequests = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`);
  });
  page.on('requestfailed', (request) => failedRequests.push(request.url()));

  await page.goto(`${base}/test/index.html`, { waitUntil: 'networkidle' });
  await page.waitForSelector('[data-g9-unit="core-contract"]');
  await page.waitForSelector('[data-g9-unit="fixture-boundary"]');
  await page.waitForSelector('[data-g9-unit="question-intake"]');

  const metrics = await page.evaluate(() => {
    const rect = (selector) => {
      const el = document.querySelector(selector);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return {
        top: Math.round(r.top),
        left: Math.round(r.left),
        width: Math.round(r.width),
        height: Math.round(r.height),
      };
    };
    const banner = document.querySelector('[data-g9-test-banner]');
    return {
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      bannerVisible: !!banner && banner.getBoundingClientRect().height > 0,
      bannerText: banner ? banner.textContent.trim() : '',
      coreCard: rect('[data-g9-unit="core-contract"]'),
      fixtureCard: rect('[data-g9-unit="fixture-boundary"]'),
      intakeRecordCount: document.querySelectorAll('[data-g9-intake-record]').length,
      intakeSearchScope: JSON.parse(document.querySelector('[data-g9-test-search-index]').textContent).scope,
      smallControls: [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [role=button]')]
        .filter((el) => {
          const r = el.getBoundingClientRect();
          const style = getComputedStyle(el);
          return r.width > 0 && r.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
        })
        .filter((el) => {
          const r = el.getBoundingClientRect();
          return Math.min(r.width, r.height) < 47.5;
        })
        .map((el) => {
          const r = el.getBoundingClientRect();
          return {
            tag: el.tagName.toLowerCase(),
            label: (el.getAttribute('aria-label') || el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 100),
            href: el.getAttribute('href'),
            width: Math.round(r.width * 10) / 10,
            height: Math.round(r.height * 10) / 10,
          };
        }),
    };
  });

  const screenshot = path.join(outDir, `${profile.id}.png`);
  await page.screenshot({ path: screenshot, fullPage: true });

  const intakeFilter = await page.evaluate(() => {
    const root = document.querySelector('[data-g9-test-intake]');
    const query = root.querySelector('[data-g9-test-intake-query]');
    const source = root.querySelector('[data-g9-test-intake-source]');
    const records = [...root.querySelectorAll('[data-g9-intake-record]')];
    const shown = () => records.filter((row) => !row.hidden).length;
    query.value = 'irrational';
    query.dispatchEvent(new Event('input', { bubbles: true }));
    const queryShown = shown();
    const queryCountText = root.querySelector('[data-g9-test-intake-count]').textContent.trim();
    query.value = '';
    query.dispatchEvent(new Event('input', { bubbles: true }));
    source.value = 'NCERT_OFFICIAL';
    source.dispatchEvent(new Event('change', { bubbles: true }));
    const sourceShown = shown();
    source.value = '';
    source.dispatchEvent(new Event('change', { bubbles: true }));
    return { queryShown, queryCountText, sourceShown, resetShown: shown() };
  });

  await page.evaluate(() => {
    if (document.activeElement && document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
    window.scrollTo(0, 0);
  });

  const focusOrder = [];
  const seen = new Set();
  for (let i = 0; i < 80; i += 1) {
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body || el === document.documentElement) return null;
      const r = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      const label = (
        el.getAttribute('aria-label') ||
        el.textContent ||
        el.getAttribute('title') ||
        el.getAttribute('href') ||
        ''
      ).trim().replace(/\s+/g, ' ').slice(0, 100);
      const all = [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]')];
      const domIndex = all.indexOf(el);
      return {
        tag: el.tagName.toLowerCase(),
        href: el.getAttribute('href'),
        label,
        domIndex,
        key: `${domIndex}|${el.tagName.toLowerCase()}|${el.getAttribute('href') || ''}|${label}`,
        rect: {
          top: r.top,
          left: r.left,
          right: r.right,
          bottom: r.bottom,
          width: r.width,
          height: r.height,
        },
        display: style.display,
        visibility: style.visibility,
        viewport: { width: innerWidth, height: innerHeight },
      };
    });
    if (!focused) continue;
    if (seen.has(focused.key)) break;
    seen.add(focused.key);
    const inside =
      focused.rect.width > 0 &&
      focused.rect.height > 0 &&
      focused.display !== 'none' &&
      focused.visibility !== 'hidden' &&
      focused.rect.left >= -1 &&
      focused.rect.right <= focused.viewport.width + 1 &&
      focused.rect.top >= -1 &&
      focused.rect.bottom <= focused.viewport.height + 1;
    focusOrder.push({ ...focused, insideViewport: inside });
  }

  const result = {
    ...profile,
    metrics,
    screenshot: path.basename(screenshot),
    intakeFilter,
    focusOrder,
    pageErrors: errors,
    failedRequests,
  };
  report.profiles.push(result);

  if (metrics.overflow > 1) failures.push(`${profile.id}: horizontal overflow ${metrics.overflow}px`);
  if (metrics.smallControls.length) {
    failures.push(`${profile.id}: controls under 48px: ${metrics.smallControls.map((x) => `${x.tag} "${x.label}" ${x.width}x${x.height}`).join('; ')}`);
  }
  if (!metrics.bannerVisible || !/not accepted/.test(metrics.bannerText)) {
    failures.push(`${profile.id}: sandbox draft banner is not visibly present`);
  }
  if (!metrics.coreCard || !metrics.fixtureCard) failures.push(`${profile.id}: dashboard cards missing`);
  if (metrics.intakeRecordCount !== 6) failures.push(`${profile.id}: expected 6 intake records, saw ${metrics.intakeRecordCount}`);
  if (metrics.intakeSearchScope !== 'TEST_ONLY_SANDBOX') failures.push(`${profile.id}: TEST-only intake search scope is not isolated`);
  if (intakeFilter.queryShown !== 3 || intakeFilter.queryCountText !== '3 shown') failures.push(`${profile.id}: intake query filter did not isolate 3 irrational-number records`);
  if (intakeFilter.sourceShown !== 6 || intakeFilter.resetShown !== 6) failures.push(`${profile.id}: intake source/reset filter state is wrong`);
  if (errors.length) failures.push(`${profile.id}: page errors: ${errors.join('; ')}`);
  if (failedRequests.length) failures.push(`${profile.id}: failed requests: ${failedRequests.join(', ')}`);
  if (focusOrder.length < 4) failures.push(`${profile.id}: only ${focusOrder.length} keyboard focus target(s) observed`);
  const outside = focusOrder.filter((item) => !item.insideViewport);
  if (outside.length) failures.push(`${profile.id}: focused controls outside viewport: ${outside.map((x) => x.key).join('; ')}`);
  for (const label of ['Atlas', 'Rungs', 'Deployments']) {
    if (!focusOrder.some((item) => item.label.includes(label))) {
      failures.push(`${profile.id}: keyboard traversal did not reach ${label}`);
    }
  }

  await context.close();
}

await browser.close();
await new Promise((resolve) => server.close(resolve));

if (failures.length) {
  report.status = 'FAIL';
  report.failures = failures;
}
const reportPath = path.join(outDir, 'dashboard-browser-evidence.json');
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');

if (failures.length) {
  console.error(failures.join('\n'));
  console.error(`FAIL: ${failures.length} dashboard browser evidence problem(s)`);
  process.exit(1);
}

console.log(`PASS: TEST dashboard browser evidence captured for ${profiles.length} viewports`);
console.log(reportPath);
