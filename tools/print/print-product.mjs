#!/usr/bin/env node
/*
 * PDF = print of the rendered web page (rebuild plan, Phase 3). There is no other PDF path.
 *
 *   node tools/print/print-product.mjs <dir-with-core*.html> [--out <dir>]
 *
 * Opens each Core page in headless Chromium, opens every reveal and every figure stage (a
 * printed study copy shows the complete page), and prints with the page's own @media print
 * stylesheet. Writes <page>.pdf plus print-receipt.json (page digests, PDF digests, figure counts).
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
const outArg = process.argv.indexOf('--out');
const out = path.resolve(outArg > 0 ? process.argv[outArg + 1] : dir);
fs.mkdirSync(out, { recursive: true });
const sha = b => 'sha256:' + crypto.createHash('sha256').update(b).digest('hex');
const browser = await playwright.chromium.launch();
const page = await browser.newPage();
const receipt = { tool: 'print-product/1', pages: [] };
for (const file of fs.readdirSync(dir).filter(f => /^core.*\.html$|^product\.html$/.test(f)).sort()) {
  const html = fs.readFileSync(path.join(dir, file));
  await page.goto('file://' + path.join(dir, file));
  const figures = await page.evaluate(() => {
    document.querySelectorAll('details').forEach(d => { d.open = true; });
    document.querySelectorAll('[data-g9-stage-id]').forEach(g => { g.style.display = ''; });
    return document.querySelectorAll('figure[data-g9-figure] svg').length;
  });
  await page.emulateMedia({ media: 'print' });
  const pdf = await page.pdf({ width: '280mm', height: '175mm', printBackground: true, margin: { top: '10mm', bottom: '10mm', left: '10mm', right: '10mm' } });
  const name = file.replace(/\.html$/, '.pdf');
  fs.writeFileSync(path.join(out, name), pdf);
  receipt.pages.push({ page: file, page_digest: sha(html), pdf: name, pdf_digest: sha(pdf), figures });
  await page.emulateMedia({ media: 'screen' });
}
await browser.close();
fs.writeFileSync(path.join(out, 'print-receipt.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(`printed ${receipt.pages.length} page(s) to ${out}`);
