// Local artifact exercise, not a CI workflow. Requires a real Chromium installation.
//   node tests/site_header_fit_browser.mjs
// The shared site header is position:fixed, so a control pushed past the right edge does not widen the
// page and document.scrollWidth cannot see it. This measures the header's own controls instead: at each
// width every visible control must lie inside the viewport, and the last one must be the element that
// actually receives a tap at its centre (not clipped or covered).
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
const PAGES = ['index.html', 'physics/index.html', 'chemistry/index.html', 'mathematics/index.html', 'question-bank/index.html', 'core-learning/index.html'];
const WIDTHS = [320, 360, 390, 414, 620, 700, 980, 1280];
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
for (const page of PAGES) {
  for (const width of WIDTHS) {
    const context = await browser.newContext({ viewport: { width, height: 800 }, hasTouch: true });
    const tab = await context.newPage();
    await tab.goto(`${base}/${page}`);
    await tab.waitForSelector('header.site-nav-enhanced .site-actions');
    const facts = await tab.evaluate(() => {
      const viewport = document.documentElement.clientWidth;
      const header = document.querySelector('header.site-nav-enhanced');
      const visible = [...header.querySelectorAll('.site-leading, .site-actions, .site-actions > *, .site-leading > *')]
        .filter((node) => getComputedStyle(node).display !== 'none' && node.getBoundingClientRect().width > 0);
      const outside = visible.filter((node) => {
        const box = node.getBoundingClientRect();
        return box.left < -0.5 || box.right > viewport + 0.5;
      }).map((node) => `${node.className || node.tagName}:${Math.round(node.getBoundingClientRect().right)}`);
      const buttons = [...header.querySelectorAll('.site-actions button')].filter((n) => getComputedStyle(n).display !== 'none');
      const last = buttons[buttons.length - 1];
      let reachable = true;
      if (last) {
        const box = last.getBoundingClientRect();
        const hit = document.elementFromPoint(box.left + box.width / 2, box.top + box.height / 2);
        reachable = hit === last || last.contains(hit);
      }
      return { outside, reachable, headerWidth: Math.round(header.getBoundingClientRect().width), viewport };
    });
    checked += 1;
    if (facts.outside.length) failures.push(`${page} @${width}: outside the viewport: ${facts.outside.join(', ')}`);
    if (!facts.reachable) failures.push(`${page} @${width}: the last header control is covered or clipped`);
    await context.close();
  }
}
await browser.close();
server.close();

if (failures.length) {
  console.log(failures.join('\n'));
  console.log(`\nFAIL: ${failures.length} problem(s) in ${checked} page/width combinations`);
  process.exit(1);
}
console.log(`PASS: header controls fit inside the viewport on ${PAGES.length} pages at ${WIDTHS.length} widths (${checked} combinations)`);
