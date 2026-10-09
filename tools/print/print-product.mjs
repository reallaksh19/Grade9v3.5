#!/usr/bin/env node
/*
 * PDF = print of the rendered web page (rebuild plan, Phase 3). There is no other PDF path.
 *
 *   node tools/print/print-product.mjs <dir-with-core*.html> [--out <dir>] [--key]
 *
 * The default learner copy does not materialise protected templates. --key materialises
 * every protected body and hint rung, then opens all reveals and figure stages.
 * The two outputs and receipts have distinct names so one cannot silently overwrite the other.
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

const dir = path.resolve(process.argv[2] || '.');
const key = process.argv.includes('--key');
const outArg = process.argv.indexOf('--out');
const out = path.resolve(outArg > 0 ? process.argv[outArg + 1] : dir);
fs.mkdirSync(out, { recursive: true });
const sha = b => 'sha256:' + crypto.createHash('sha256').update(b).digest('hex');
const browser = await playwright.chromium.launch();
const page = await browser.newPage();
const receipt = { tool: 'print-product/2', mode: key ? 'KEY_PDF' : 'LEARNER_PDF', pages: [] };
for (const file of fs.readdirSync(dir).filter(f => /^core.*\.html$|^product\.html$/.test(f)).sort()) {
  const html = fs.readFileSync(path.join(dir, file));
  await page.goto('file://' + path.join(dir, file));
  const figures = await page.evaluate((keyMode) => {
    if (keyMode && window.g9MaterialiseAll) {
      window.g9MaterialiseAll();
      document.querySelectorAll('details').forEach(d => { d.open = true; });
      document.querySelectorAll('[data-g9-stage-id]').forEach(g => { g.style.display = ''; });
    }
    return document.querySelectorAll('figure[data-g9-figure] svg').length;
  }, key);
  await page.emulateMedia({ media: 'print' });
  // The interactive page fitFigure() narrows a staged SVG viewBox to the
  // currently visible teaching step. Print CSS reveals the remaining steps,
  // but they would still be clipped by that narrow viewBox. Restore the union
  // only for TEACHING figures; never expand protected pre-attempt visuals.
  await page.evaluate(() => {
    document.querySelectorAll('figure[data-g9-stage="TEACHING"] svg').forEach(svg => {
      const steps = [...svg.querySelectorAll('g[data-g9-stage-id]')];
      if (steps.length < 2) return;
      steps.forEach(g => g.style.setProperty('display', 'inline', 'important'));
      const roots = [...steps, ...svg.querySelectorAll(':scope > text')];
      const boxes = roots.map(el => el.getBBox()).filter(b => b.width > 0 && b.height > 0);
      if (!boxes.length) return;
      const x = Math.min(...boxes.map(b => b.x)) - 12;
      const y = Math.min(...boxes.map(b => b.y)) - 12;
      const right = Math.max(...boxes.map(b => b.x + b.width)) + 12;
      const bottom = Math.max(...boxes.map(b => b.y + b.height)) + 12;
      svg.setAttribute('viewBox', [x, y, right - x, bottom - y].join(' '));
      svg.style.width = '100%';
      svg.style.maxWidth = 'none';
      svg.style.height = 'auto';
    });
  });
  const pdf = await page.pdf({ width: '280mm', height: '175mm', printBackground: true, margin: { top: '10mm', bottom: '10mm', left: '10mm', right: '10mm' } });
  const name = file.replace(/\.html$/, key ? '.key.pdf' : '.pdf');
  fs.writeFileSync(path.join(out, name), pdf);
  receipt.pages.push({ page: file, page_digest: sha(html), pdf: name, pdf_digest: sha(pdf), figures });
  await page.emulateMedia({ media: 'screen' });
}
await browser.close();
fs.writeFileSync(path.join(out, key ? 'print-key-receipt.json' : 'print-receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(`printed ${receipt.pages.length} page(s) to ${out}`);
