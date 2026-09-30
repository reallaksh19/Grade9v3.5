// Local artifact exercise, not a CI workflow. Requires a real Chromium installation.
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(path.join(execSync('npm root -g').toString().trim(), 'playwright')); }
const file = path.resolve(process.argv[2]);
const out = path.resolve(process.argv[3]);
fs.mkdirSync(out, {recursive:true});
const bytes = fs.readFileSync(file);
const evidence = {artifact_sha256:crypto.createHash('sha256').update(bytes).digest('hex'), profiles:[]};
const browser = await playwright.chromium.launch();
try {
  for (const viewport of [{width:1366,height:854},{width:1440,height:900},{width:900,height:1440}]) {
    const context = await browser.newContext({viewport,offline:true,hasTouch:true});
    const page = await context.newPage();
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    const failed = []; page.on('requestfailed', r => failed.push(r.url()));
    await page.goto(pathToFileURL(file).href);
    const before = await page.evaluate(() => ({
      width:document.documentElement.scrollWidth,
      authored:document.querySelectorAll('[data-g9-block="authored_core2_support"] li[data-g9-rung]').length,
      math:document.querySelectorAll('math').length,
      errors:document.querySelectorAll('.katex-error').length,
      touch:[...document.querySelectorAll('button,summary,.g9-answer-option')].filter(e=>e.getBoundingClientRect().width>0)
        .map(e=>({label:e.textContent.trim(),width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))
    }));
    assert.equal(before.authored,0,'authored support is inert until the learner requests it');
    assert.ok(before.math>=3,'declared option math is typeset offline');
    assert.equal(before.errors,0);
    assert.ok(before.width<=viewport.width,'no horizontal overflow');
    assert.ok(before.touch.every(t=>t.width>=48&&t.height>=48),'48px touch targets');
    await page.emulateMedia({media:'print'});
    assert.equal(await page.locator('.g9-answer-option:visible').count(),4,'all options survive learner print');
    assert.equal(await page.locator('[data-g9-choice]:visible').count(),0,'input controls are not printed');
    await page.emulateMedia({media:'screen'});
    await page.locator('[data-g9-commit]').click();
    assert.equal(await page.locator('[data-g9-block="structured_working"]').count(),0,'empty commitment keeps the solution locked');
    // Core2 v2: every support rung is collapsed until requested, in two independent ladders.
    const sourceHints = page.locator('[data-g9-block="source_hints"] [data-g9-rung]');
    assert.equal(await sourceHints.count(),0,'no source hint is live before it is requested');
    await page.getByRole('button',{name:'Show source hint'}).click();
    assert.equal(await sourceHints.count(),1);
    await page.locator('[data-g9-choice]').first().check();
    await page.locator('[data-g9-commit]').click();
    const hints = page.locator('[data-g9-block="authored_core2_support"]');
    assert.equal(await hints.locator('[data-g9-rung]').count(),0);
    for (let n = 1; n <= 3; n++) {
      await hints.getByRole('button',{name:/^Show (guided|next) support$/}).click();
      assert.equal(await hints.locator('[data-g9-rung]').count(),n);
    }
    assert.equal(await hints.locator('[data-g9-rung]').count(),3,'later support buttons work after insertion');
    assert.equal(await sourceHints.count(),1,'source and authored ladders are independent');
    await page.getByText('Answer and working',{exact:true}).click();
    assert.equal(await page.locator('[data-g9-solution-move]').count(),3);
    assert.deepEqual(errors,[]); assert.deepEqual(failed,[]);
    await page.screenshot({path:path.join(out,`${viewport.width}x${viewport.height}.png`),fullPage:true});
    const ax = await page.locator('main').ariaSnapshot();
    fs.writeFileSync(path.join(out,`${viewport.width}x${viewport.height}.aria.txt`),ax);
    evidence.profiles.push({viewport,before,errors,failed,status:'PASS'});
    await context.close();
  }
} finally { await browser.close(); }
fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(evidence,null,2)+'\n');
console.log('PASS: actual offline Chromium, three tablet profiles, typed commitment, independent source/authored ladders and reasoning');
