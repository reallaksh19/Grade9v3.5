#!/usr/bin/env node
/** #327: real-browser nonpublishing F04 draft Mathematics route audit. */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root = path.resolve(process.argv[2] || 'docs');
const out = path.resolve(process.argv[3] || path.join(os.tmpdir(), 'imo-327-index-laws-home-audit'));
const names = ['mathematics/number-systems/index.html',
               'mathematics/number-systems/index-laws/index.html'];
const expected = {
  CORE1A: 'CANDIDATE_NOT_PUBLISHED',
  CORE2A: 'CANDIDATE_NOT_PUBLISHED',
  CORE2: 'SOURCE_CUSTODY_AND_RIGHTS_HOLD',
};
const failures = [];
const assert = (valid, detail) => { if (!valid) failures.push(detail); };
fs.mkdirSync(out, {recursive: true});
for (const name of names) {
  if (!fs.existsSync(path.join(root, name))) throw new Error('Draft file missing: ' + name);
}
const browser = await chromium.launch({headless: true});
const report = {schema: 'imo-327-index-laws-home-browser/v1',
  authority: 'CANDIDATE_NO_LAUNCH', originalSourceCore2Admitted: false,
  humanScreenReader: 'NOT_RUN', ownerApproval: 'NOT_GRANTED',
  pages: [], parentToChild: {}, failures};
try {
  for (const width of [320, 390, 768, 1280]) {
    const context = await browser.newContext({viewport: {width, height: 900}});
    const page = await context.newPage();
    const jsErrors = [];
    page.on('pageerror', error => jsErrors.push(error.message));
    for (const name of names) {
      await page.goto(pathToFileURL(path.join(root, name)).href, {waitUntil: 'load'});
      const state = await page.evaluate(() => ({
        client: document.documentElement.clientWidth,
        scroll: document.documentElement.scrollWidth,
        main: document.querySelectorAll('main').length,
        h1: [...document.querySelectorAll('main h1')].map(e => e.textContent.trim()),
        stylesheet: [...document.styleSheets].some(s => s.href?.includes('modern-learner.css')),
        mainSize: Number.parseFloat(getComputedStyle(document.querySelector('main')).fontSize),
        roles: [...document.querySelectorAll('article[data-g9-role]')].map(el => ({
          role: el.dataset.g9Role, authority: el.dataset.g9Authority,
          launch: el.dataset.g9LaunchAuthorized,
          linked: el.querySelectorAll('a, button').length
        }))
      }));
      const key = name.includes('index-laws') ? 'Index Laws' : 'Number Systems';
      assert(state.scroll <= state.client, width + 'px ' + key + ': horizontal overflow ' + (state.scroll-state.client));
      assert(state.main === 1 && state.h1.length === 1 && state.h1[0] === key, width + 'px ' + key + ': missing hierarchy/H1');
      assert(state.stylesheet, width + 'px ' + key + ': repository stylesheet missing');
      assert(!jsErrors.length, width + 'px ' + key + ': JS errors ' + jsErrors.join('; '));
      if (key === 'Index Laws') {
        const roles = Object.fromEntries(state.roles.map(z => [z.role, z]));
        assert(state.roles.length === 3, width + 'px: exactly three role cards required');
        for (const [role, authority] of Object.entries(expected)) {
          assert(roles[role]?.authority === authority, width + 'px: false ' + role + ' authority');
          assert(roles[role]?.launch === 'false', width + 'px: attempted ' + role + ' launch');
          assert(roles[role]?.linked === 0, width + 'px: held ' + role + ' card has a clickable action');
        }
        const body = await page.locator('main').innerText();
        assert(body.includes('not an official SOF question'),
          width + 'px: authored Core2A mislabelled as authentic source');
        assert(!body.includes('SOF-IMO-G09-L1-'),
          width + 'px: original source item identity leaked into a learner product');
      }
      report.pages.push({width, name, ...state, errors: jsErrors.slice()});
      if (width === 320 || width === 1280) {
        await page.screenshot({path: path.join(out, key.toLowerCase().replaceAll(' ', '-')+'-'+width+'.png'),
          fullPage: true});
      }
      if (width === 390) {
        await page.addStyleTag({content: 'html { font-size: 200% !important; }'});
        const zoom = await page.evaluate(() => ({
          client: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth
        }));
        assert(zoom.scroll <= zoom.client, width + 'px ' + key + ': 200% text zoom overflow');
        report.pages.at(-1).zoom200 = zoom;
      }
    }
    // This is a real file-backed learner route, not a synthetic URL or a
    // substitute central IMO browser route. Keyboard Enter must reach it.
    await page.goto(pathToFileURL(path.join(root, names[0])).href);
    const link = page.locator('a[href="index-laws/index.html"]');
    assert(await link.count() === 1, width + 'px: Number Systems does not link its subtopic');
    if (await link.count()) {
      await link.focus();
      const focus = await link.evaluate(el => document.activeElement === el);
      await Promise.all([
        page.waitForURL(url => new URL(url).pathname.endsWith('/index-laws/index.html'),
                        {waitUntil: 'load', timeout: 10000}),
        page.keyboard.press('Enter')
      ]);
      const location = new URL(page.url()).pathname;
      const heading = await page.locator('main h1').innerText();
      report.parentToChild[width] = {focus, heading, location};
      assert(focus && heading === 'Index Laws' && location.endsWith('/index-laws/index.html'),
        width + 'px: keyboard parent→child routing broken');
    }
    await context.close();
  }
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report));
if (failures.length) {
  console.error('Index Laws homepage browser failures:\n- ' + failures.join('\n- '));
  process.exitCode = 1;
}
