#!/usr/bin/env node
/*
 * Rendered audit of standalone Core pages against their role blueprint's shell, touch,
 * responsive and navigation policies (Audit 3, issue #298). Read-only: it loads each page
 * from disk in Chromium at the 10-inch tablet viewports and reports measured facts as JSON.
 *
 *   node tools/site-audit/core-page-audit.mjs <dir-with-core*.html> [--json out.json]
 *
 * Slot realization is judged from the page's DOM outline (headings, disclosures, attempt
 * controls, figures) that this script also prints; a data-blueprint-ref attribute alone
 * never counts as realization.
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const dir = path.resolve(process.argv[2] || '.');
const jsonOut = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null;
const blueprints = JSON.parse(fs.readFileSync(new URL('../../Shared/web/interactive-page-blueprints.v1.json', import.meta.url)));
const VIEWPORTS = [
  { name: 'android-landscape', width: 1280, height: 800 },
  { name: 'android-portrait', width: 800, height: 1280 },
  { name: 'ipad-landscape', width: 1180, height: 820 },
];
const files = fs.readdirSync(dir).filter(f => /^core.*\.html$/.test(f)).sort();
const browser = await playwright.chromium.launch();
const report = {};
for (const file of files) {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  const out = { viewports: {}, errors };
  for (const vp of VIEWPORTS) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.goto('file://' + path.join(dir, file));
    const bpId = await page.evaluate(() => document.body.dataset.blueprintRef || null);
    const bp = blueprints.blueprints.find(b => b.id === bpId);
    const minTarget = bp ? bp.touch_policy.minimum_target_css_px : 48;
    const r = await page.evaluate((minTarget) => {
      const visible = el => { const b = el.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
      const controls = [...document.querySelectorAll('a[href],button,summary,textarea,input,select')].filter(visible);
      const small = controls.filter(el => { const b = el.getBoundingClientRect(); return Math.min(b.width, b.height) < minTarget && el.tagName !== 'TEXTAREA'; });
      const texts = [...document.querySelectorAll('body *')].filter(el => el.childElementCount === 0 && el.textContent.trim() && visible(el));
      const minFont = Math.min(...texts.map(el => parseFloat(getComputedStyle(el).fontSize)));
      const wide = [...document.querySelectorAll('svg,table,pre,figure,.math,math')].filter(el => el.getBoundingClientRect().right > document.documentElement.clientWidth + 1).length;
      const homeLinks = [...document.querySelectorAll('a[href]')].filter(a => /(^|\/)(\.\.\/)+index\.html$|^\/$|^\/Grade9V3\/?$/.test(a.getAttribute('href')) || /home/i.test(a.textContent)).map(a => a.getAttribute('href'));
      const nav = document.querySelector('nav');
      const navFixed = nav ? ['fixed', 'sticky'].includes(getComputedStyle(nav).position) : false;
      const sheetText = [...document.styleSheets].flatMap(s => { try { return [...s.cssRules].map(r => r.cssText); } catch { return []; } }).join('\n');
      const figs = [...document.querySelectorAll('svg')];
      return {
        blueprint: document.body.dataset.blueprintRef || null,
        slotMarkers: document.querySelectorAll('[data-slot],[data-blueprint-slot]').length,
        controls: controls.length,
        smallTargets: small.length,
        smallTargetSample: small.slice(0, 3).map(el => el.tagName.toLowerCase() + ' ' + Math.round(el.getBoundingClientRect().height) + 'px "' + el.textContent.trim().slice(0, 20) + '"'),
        minFontPx: minFont,
        horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        wideElements: wide,
        homeLinks,
        navFirstLink: nav && nav.querySelector('a') ? nav.querySelector('a').getAttribute('href') + ' "' + nav.querySelector('a').textContent.trim() + '"' : null,
        headerFixedOrSticky: navFixed,
        focusStyles: /:focus/.test(sheetText),
        printStyles: /@media print/.test(sheetText),
        landmarks: { main: document.querySelectorAll('main').length, nav: document.querySelectorAll('nav').length, header: document.querySelectorAll('header').length, footer: document.querySelectorAll('footer').length },
        svg: figs.length,
        svgAccessible: figs.filter(s => s.querySelector('title') || s.getAttribute('aria-label') || s.getAttribute('aria-labelledby')).length,
        disclosures: document.querySelectorAll('details').length,
        attemptFields: document.querySelectorAll('textarea').length,
        gatedDisclosures: [...document.querySelectorAll('details')].filter(d => d.hasAttribute('data-requires-attempt') || d.querySelector('summary[aria-disabled="true"]')).length,
        scripts: document.scripts.length,
        stageSupportLayout: /grid-template-columns:[^;]*(68|0?\.68|2fr)/.test(sheetText),
      };
    }, minTarget);
    out.viewports[vp.name] = r;
  }
  report[file] = out;
  await page.close();
}
await browser.close();
for (const [file, r] of Object.entries(report)) {
  const a = r.viewports['android-landscape'], p = r.viewports['android-portrait'];
  console.log(`${file}: bp=${a.blueprint} slots=${a.slotMarkers} home=${JSON.stringify(a.homeLinks)} nav1=${a.navFirstLink} sticky=${a.headerFixedOrSticky} ` +
    `targets<48=${a.smallTargets}/${a.controls} minFont=${a.minFontPx} overflowL=${a.horizontalOverflowPx} overflowP=${p.horizontalOverflowPx} ` +
    `svg=${a.svg} (a11y ${a.svgAccessible}) details=${a.disclosures} gated=${a.gatedDisclosures} attempts=${a.attemptFields} focusCSS=${a.focusStyles} print=${a.printStyles} ` +
    `stage68=${a.stageSupportLayout} landmarks=${JSON.stringify(a.landmarks)} js=${a.scripts} errors=${r.errors.length}`);
  console.log(`    small targets: ${a.smallTargetSample.join(' | ')}`);
}
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 2));
