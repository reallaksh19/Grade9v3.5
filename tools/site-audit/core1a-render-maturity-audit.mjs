#!/usr/bin/env node
/**
 * Real-browser audit for any TEST Core1A renderer product folder.
 * Read-only QA. This is NOT an alternate renderer, source verifier or release gate.
 * Usage: node tools/site-audit/core1a-render-maturity-audit.mjs public/test/products/SLUG
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const folder = path.resolve(process.argv[2] || '');
if (!process.argv[2] || !fs.existsSync(path.join(folder, 'core1a.html'))) {
  throw new Error('expected a generated core1a.html product folder');
}
const evidenceDir = path.resolve(process.env.CORE_MATURITY_EVIDENCE || path.join(folder, 'qa-evidence'));
fs.mkdirSync(evidenceDir, {recursive: true});
const productUrl = pathToFileURL(path.join(folder, 'core1a.html')).href;
const sizes = [
  ['mobile-320',320,680], ['mobile-390',390,844],
  ['tablet-768',768,1024], ['desktop-1280',1280,800]
];
const report = {schema:'core1a-real-browser-maturity-audit/v1',
  product_url_kind:'EXACT_CHECKOUT_GENERATED_TEST_PRODUCT_FILE', sizes:[],
  failures:[], manual_screen_reader:'NOT_RUN', learner_comprehension:'NOT_RUN',
  publisher_source_custody:'NOT_APPLICABLE_AUTHORED_TEST',
  owner_acceptance:false, canonical_release:false};
const browser = await chromium.launch({headless:true});
try {
  for (const [name,width,height] of sizes) {
    const ctx = await browser.newContext({viewport:{width,height}});
    const page = await ctx.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(productUrl,{waitUntil:'load'});
    const measurements = await page.evaluate(() => ({
      width:document.documentElement.clientWidth,
      scroll:document.documentElement.scrollWidth,
      h1:document.querySelector('h1')?.textContent?.trim()||'',
      units:document.querySelectorAll('article[data-g9-role="CORE1A"]').length,
      test:document.documentElement.dataset.g9Test==='sandbox-draft',
      acceptance:document.documentElement.dataset.g9CanonicalAcceptance||'',
      stages:document.querySelectorAll('figure[data-g9-figure] [data-g9-stage-id]').length,
      authoredFigures:document.querySelectorAll('figure[data-g9-figure] svg[aria-label] title').length
    }));
    await page.screenshot({path:path.join(evidenceDir,name+'.png'),fullPage:true});
    report.sizes.push({name, ...measurements, page_errors:errors});
    if (measurements.scroll>measurements.width)
      report.failures.push(name+': root horizontal overflow '+(measurements.scroll-measurements.width)+'px');
    if (!measurements.test) report.failures.push(name+': missing actual TEST stamp');
    if (measurements.units<1) report.failures.push(name+': missing canonical Core1A article');
    if (errors.length) report.failures.push(name+': browser JS errors: '+errors.join('; '));
    if (measurements.stages<3 || measurements.authoredFigures<1)
      report.failures.push(name+': canonical authored staged SVG missing/inaccessible');
    if (name==='desktop-1280') {
      const summary=page.locator('details:not([data-requires-attempt]) summary').first();
      if (await summary.count()) {
        await summary.focus();
        await summary.press('Enter');
        const opened=await summary.evaluate(el=>el.parentElement.open);
        await summary.press('Enter');
        const closed=!(await summary.evaluate(el=>el.parentElement.open));
        report.keyboard={summary_enter_opens:opened,summary_enter_closes:closed};
        if (!opened || !closed) report.failures.push('keyboard Enter disclosure open/close failed');
      } else { report.failures.push('no keyboard-accessible authored disclosure found'); }
    }
    if (name==='mobile-390') {
      await page.addStyleTag({content:'html {font-size:200%!important}'});
      const zoom=await page.evaluate(()=>({
        client:document.documentElement.clientWidth,
        scroll:document.documentElement.scrollWidth
      }));
      report.zoom200=zoom;
      await page.screenshot({path:path.join(evidenceDir,'mobile-390-200pct.png'),fullPage:true});
      if (zoom.scroll>zoom.client)
        report.failures.push('200% text: horizontal overflow '+(zoom.scroll-zoom.client)+'px');
    }
    await ctx.close();
  }
} finally { await browser.close(); }
fs.writeFileSync(path.join(evidenceDir,'qa-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checked:report.sizes.length,zoom200:report.zoom200,failures:report.failures},null,2));
if (report.failures.length) process.exitCode=1;
