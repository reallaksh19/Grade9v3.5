// Focused blocking browser qualification for the TEST-only NCERT Question Bank.
// It intentionally excludes Atlas/rungs so their independent QA debt cannot mask this responsibility.
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
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end(); return;
  }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
  fs.createReadStream(file).pipe(res);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await playwright.chromium.launch();
const failures = [];

for (const width of [320, 390, 768, 1280]) {
  const context = await browser.newContext({ viewport: { width, height: 900 }, hasTouch: true });
  const page = await context.newPage();
  const problems = [];
  page.on('pageerror', error => problems.push(`script error: ${error.message}`));
  page.on('console', message => { if (message.type() === 'error') problems.push(`console error: ${message.text()}`); });
  page.on('request', request => {
    if (!request.url().startsWith(base) && !request.url().startsWith('data:')) problems.push(`external request: ${request.url()}`);
  });
  page.on('response', response => { if (response.status() >= 400) problems.push(`${response.status()} ${response.url()}`); });

  await page.goto(`${base}/test/question-bank/index.html`, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.querySelectorAll('[data-g9-test-question]').length === 210, null, { timeout: 8000 });

  const facts = await page.evaluate(() => {
    const cards = [...document.querySelectorAll('[data-g9-test-question]')];
    const controls = [...document.querySelectorAll('#tqbSearch,#tqbUnit,#tqbType,#tqbReset,.tqb-test-nav a,.tqb-answer summary')];
    const small = controls.filter(el => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0 && rect.height < 47.5;
    }).map(el => `${el.tagName.toLowerCase()} ${Math.round(el.getBoundingClientRect().height)}px`);
    return {
      cards: cards.length,
      unique: new Set(cards.map(card => card.dataset.g9TestQuestion)).size,
      validated: cards.filter(card => card.dataset.g9Validation === 'VALIDATED').length,
      hold: cards.filter(card => card.dataset.g9Validation === 'HOLD').length,
      unvalidated: cards.filter(card => card.dataset.g9Validation === 'UNVALIDATED').length,
      sourceVerified: cards.filter(card => card.dataset.g9SourceVerification === 'SOURCE VERIFIED').length,
      duplicateReview: cards.filter(card => card.dataset.g9Review === 'DUPLICATE_REVIEW').length,
      types: Object.fromEntries(['MULTIPLE_CHOICE','SHORT_ANSWER','TRUE_FALSE'].map(type => [type, cards.filter(card => card.dataset.type === type).length])),
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      banner: (document.querySelector('[data-g9-test-banner]') || {}).textContent || '',
      boundary: document.body.innerText.includes('Production admission is governed separately.'),
      small,
    };
  });

  const where = `TEST Question Bank @${width}`;
  if (facts.cards !== 210 || facts.unique !== 210) failures.push(`${where}: card denominator/uniqueness is ${facts.cards}/${facts.unique}, expected 210/210`);
  if (facts.validated !== 59) failures.push(`${where}: ${facts.validated}/59 VALIDATED`);
  if (facts.hold !== 1) failures.push(`${where}: ${facts.hold}/1 HOLD`);
  if (facts.unvalidated !== 150) failures.push(`${where}: ${facts.unvalidated}/150 UNVALIDATED`);
  if (facts.sourceVerified !== 210) failures.push(`${where}: ${facts.sourceVerified}/210 SOURCE VERIFIED`);
  if (facts.duplicateReview !== 0) failures.push(`${where}: ${facts.duplicateReview} duplicate-review cards, expected 0`);
  if (facts.types.MULTIPLE_CHOICE !== 125 || facts.types.SHORT_ANSWER !== 45 || facts.types.TRUE_FALSE !== 40) {
    failures.push(`${where}: type denominators ${JSON.stringify(facts.types)}`);
  }
  if (facts.overflow > 1) failures.push(`${where}: ${facts.overflow}px horizontal overflow`);
  if (!/not accepted/.test(facts.banner)) failures.push(`${where}: TEST draft banner missing`);
  if (!facts.boundary) failures.push(`${where}: production-isolation statement missing`);
  if (facts.small.length) failures.push(`${where}: controls under 48px: ${facts.small.slice(0,6).join(', ')}`);

  await page.locator('#tqbUnit').selectOption('Unit 2: Polynomials');
  await page.waitForTimeout(50);
  const polynomialCount = await page.locator('[data-g9-test-question]:not([hidden])').count();
  if (polynomialCount !== 30) failures.push(`${where}: Polynomials filter shows ${polynomialCount}, expected 30`);

  await page.locator('#tqbReset').click();
  await page.locator('#tqbSearch').fill('ncert-exemplar-g9-math-u13-q30');
  await page.waitForTimeout(50);
  const idCount = await page.locator('[data-g9-test-question]:not([hidden])').count();
  if (idCount !== 1) failures.push(`${where}: exact-id search shows ${idCount}, expected 1`);

  problems.forEach(problem => failures.push(`${where}: ${problem}`));
  await context.close();
}

await browser.close();
server.close();

if (failures.length) {
  console.log(failures.join('\n'));
  console.log(`FAIL: ${failures.length} TEST Question Bank browser problem(s)`);
  process.exit(1);
}
console.log('PASS: TEST Question Bank renders 210 source-verified questions with 59 VALIDATED / 1 HOLD / 150 UNVALIDATED, correct filters, touch targets and no narrow overflow');
