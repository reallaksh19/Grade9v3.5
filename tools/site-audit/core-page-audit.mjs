#!/usr/bin/env node
/*
 * Rendered audit of standalone Core pages against their role blueprint's shell, touch,
 * responsive and navigation policies (Audit 3, issue #298). Read-only: it loads each page
 * in Chromium and reports measured facts as JSON. By default it uses file://; pass --http-root
 * to exercise the same files through a local HTTP origin while preserving repository-relative assets.
 *
 *   node tools/site-audit/core-page-audit.mjs <dir-with-core*.html> [--profile tablet-12.7|core1a-spec] [--json out.json]
 *   node tools/site-audit/core-page-audit.mjs <dir-with-core*.html> --profile core1a-spec --http-root <served-root>
 *
 * Slot realization is judged from the page's DOM outline (headings, disclosures, attempt
 * controls, figures) that this script also prints; a data-blueprint-ref attribute alone
 * never counts as realization.
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(execSync('npm root -g').toString().trim() + '/playwright'); }

const dir = path.resolve(process.argv[2] || '.');
const jsonOut = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null;
const profile = process.argv.includes('--profile') ? process.argv[process.argv.indexOf('--profile') + 1] : 'default';
const httpRoot = process.argv.includes('--http-root')
  ? path.resolve(process.argv[process.argv.indexOf('--http-root') + 1])
  : null;
const enforce = process.argv.includes('--enforce');
const blueprints = JSON.parse(fs.readFileSync(new URL('../../Shared/web/interactive-page-blueprints.v1.json', import.meta.url)));
const DEFAULT_VIEWPORTS = [
  { name: 'android-landscape', width: 1280, height: 800 },
  { name: 'android-portrait', width: 800, height: 1280 },
  { name: 'ipad-landscape', width: 1180, height: 820 },
];
const TABLET_12_7_VIEWPORTS = [
  { name: 'tablet-1366-landscape', width: 1366, height: 854 },
  { name: 'tablet-1440-landscape', width: 1440, height: 900 },
  { name: 'tablet-854-portrait', width: 854, height: 1366 },
  { name: 'tablet-900-portrait', width: 900, height: 1440 },
];
const CORE1A_SPEC_VIEWPORTS = [
  { name: 'phone-390x844', width: 390, height: 844 },
  { name: 'portrait-800x1280', width: 800, height: 1280 },
  { name: 'portrait-820x1180', width: 820, height: 1180 },
  { name: 'landscape-1180x820', width: 1180, height: 820 },
  { name: 'landscape-1280x800', width: 1280, height: 800 },
  { name: 'desktop-1440x900', width: 1440, height: 900 },
];
if (!['default', 'tablet-12.7', 'core1a-spec'].includes(profile)) throw new Error(`unknown audit profile: ${profile}`);
const VIEWPORTS = profile === 'tablet-12.7'
  ? TABLET_12_7_VIEWPORTS
  : profile === 'core1a-spec' ? CORE1A_SPEC_VIEWPORTS : DEFAULT_VIEWPORTS;
const files = fs.readdirSync(dir).filter(f => /^core.*\.html$/.test(f)).sort();

let server = null;
let origin = null;
if (httpRoot) {
  const relativeDir = path.relative(httpRoot, dir);
  if (relativeDir.startsWith('..') || path.isAbsolute(relativeDir)) {
    throw new Error(`audit directory must be inside --http-root: ${dir} not under ${httpRoot}`);
  }
  const MIME = {
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
  };
  server = http.createServer((req, res) => {
    try {
      const pathname = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
      const candidate = path.resolve(httpRoot, '.' + pathname);
      const allowed = candidate === httpRoot || candidate.startsWith(httpRoot + path.sep);
      if (!allowed) {
        res.writeHead(403).end('forbidden');
        return;
      }
      let target = candidate;
      if (fs.existsSync(target) && fs.statSync(target).isDirectory()) target = path.join(target, 'index.html');
      if (!fs.existsSync(target) || !fs.statSync(target).isFile()) {
        res.writeHead(404).end('not found');
        return;
      }
      res.writeHead(200, {
        'content-type': MIME[path.extname(target).toLowerCase()] || 'application/octet-stream',
        'cache-control': 'no-store',
      });
      fs.createReadStream(target).pipe(res);
    } catch (error) {
      res.writeHead(500).end(String(error));
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const address = server.address();
  origin = `http://127.0.0.1:${address.port}`;
}

const browser = await playwright.chromium.launch();
const report = {};
for (const file of files) {
  const page = await browser.newPage();
  const errors = [];
  const requests = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', request => {
    const url = request.url();
    if (/^https?:\/\//i.test(url) && (!origin || !url.startsWith(origin + '/'))) requests.push(url);
  });
  await page.addInitScript(() => {
    window.__g9ListenerEvents = [];
    const original = EventTarget.prototype.addEventListener;
    EventTarget.prototype.addEventListener = function (type, ...args) {
      if (this instanceof Element) window.__g9ListenerEvents.push({ target: this, type });
      return original.call(this, type, ...args);
    };
  });
  const out = { viewports: {}, errors };
  for (const vp of VIEWPORTS) {
    requests.length = 0;
    await page.setViewportSize({ width: vp.width, height: vp.height });
    const pageUrl = origin
      ? origin + '/' + path.relative(httpRoot, path.join(dir, file)).split(path.sep).map(encodeURIComponent).join('/')
      : 'file://' + path.join(dir, file);
    await page.goto(pageUrl);
    const bpId = await page.evaluate(() => document.body.dataset.blueprintRef || null);
    const bp = blueprints.blueprints.find(b => `${b.id}@${b.version}` === bpId);
    const minTarget = bp ? bp.touch_policy.minimum_target_css_px : 48;
    // The expanded layout is the blueprint's own: its fractions and the width it starts at.
    const policy = bp ? bp.responsive_policy : null;
    const pct = x => Number((x * 100).toFixed(4));
    const expectedColumns = policy && policy.support_fraction ? { primary: pct(policy.primary_fraction), support: pct(policy.support_fraction) } : null;
    const expectedTablet = policy && policy.tablet_12_7 ? policy.tablet_12_7 : null;
    const r = await page.evaluate(({ minTarget, expectedColumns, expectedTablet }) => {
      const visible = el => { const b = el.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
      const controls = [...document.querySelectorAll('a[href],button,summary,textarea,input,select')].filter(visible);
      // Inline text links inside a paragraph, list item or table cell are exempt (WCAG 2.5.8), as in tablet-audit.mjs.
      const small = controls.filter(el => { const b = el.getBoundingClientRect(); return Math.min(b.width, b.height) < minTarget && el.tagName !== 'TEXTAREA' && !(el.tagName === 'A' && el.closest('p,li,td')); });
      const texts = [...document.querySelectorAll('body *')].filter(el => el.childElementCount === 0 && el.textContent.trim() && visible(el));
      const minFont = Math.min(...texts.map(el => parseFloat(getComputedStyle(el).fontSize)));
      const minFontElements = texts.filter(el => parseFloat(getComputedStyle(el).fontSize) <= minFont + 0.01);
      const wide = [...document.querySelectorAll('svg,table,pre,figure,.math,math')].filter(el => el.getBoundingClientRect().right > document.documentElement.clientWidth + 1).length;
      const homeLinks = [...document.querySelectorAll('a[href]')].filter(a => /(^|\/)(\.\.\/)+index\.html$|^\/$|^\/Grade9V3\/?$/.test(a.getAttribute('href')) || /home/i.test(a.textContent)).map(a => a.getAttribute('href'));
      const nav = document.querySelector('[data-g9-shell-header]') || document.querySelector('nav');
      const navFixed = nav ? ['fixed', 'sticky'].includes(getComputedStyle(nav).position) : false;
      const sheetText = [...document.styleSheets].flatMap(s => { try { return [...s.cssRules].map(r => r.cssText); } catch { return []; } }).join('\n');
      const figs = [...document.querySelectorAll('svg')];
      const listenerEvents = window.__g9ListenerEvents || [];
      const hoverTypes = new Set(['mouseenter', 'mouseover', 'pointerenter', 'pointerover']);
      const activationTypes = new Set(['click', 'pointerdown', 'touchstart', 'keydown']);
      const hoverTargets = new Set(listenerEvents.filter(x => hoverTypes.has(x.type)).map(x => x.target));
      const activationTargets = new Set(listenerEvents.filter(x => activationTypes.has(x.type)).map(x => x.target));
      const hoverOnly = [...document.querySelectorAll('*')].filter(el => {
        const hover = hoverTargets.has(el) || !!(el.onmouseenter || el.onmouseover || el.onpointerenter || el.onpointerover);
        const activate = activationTargets.has(el) || !!(el.onclick || el.onpointerdown || el.ontouchstart || el.onkeydown);
        return hover && !activate && visible(el);
      });
      return {
        blueprint: document.body.dataset.blueprintRef || null,
        slotMarkers: document.querySelectorAll('[data-slot],[data-blueprint-slot]').length,
        controls: controls.length,
        smallTargets: small.length,
        smallTargetSample: small.slice(0, 3).map(el => el.tagName.toLowerCase() + ' ' + Math.round(el.getBoundingClientRect().height) + 'px "' + el.textContent.trim().slice(0, 20) + '"'),
        minFontPx: minFont,
        minFontSample: minFontElements.slice(0, 3).map(el => el.tagName.toLowerCase() + ' ' + (el.textContent || '').trim().slice(0, 30)),
        contentWidthPx: (() => {
          const main = document.querySelector('main');
          return main ? Math.round(main.getBoundingClientRect().width * 10) / 10 : null;
        })(),
        horizontalOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        wideElements: wide,
        hoverOnlyHandlers: hoverOnly.length,
        hoverOnlySample: hoverOnly.slice(0, 3).map(el => el.tagName.toLowerCase() + ' ' + (el.textContent || '').trim().slice(0, 20)),
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
        tablet: !expectedTablet ? null : (() => {
          // What the 12.7-inch tablet blueprint promises: the labels are short, the two columns start together, the figure is legible.
          const top = el => el.getBoundingClientRect().top + window.scrollY;
          const rows = [...document.querySelectorAll('article[data-g9-unit]')].filter(visible).map(article => {
            const identity = article.querySelector(':scope > .slot-identity');
            const primary = article.querySelector('.g9-split:not(.g9-split-support-only) > .g9-col-primary');
            const support = article.querySelector('.g9-split:not(.g9-split-support-only) > .g9-col-support');
            const labels = [...article.querySelectorAll('figure svg text')].filter(x => x.getClientRects().length);
            let smallest = null;
            for (const label of labels) {
              const size = parseFloat(getComputedStyle(label).fontSize), m = label.getScreenCTM();
              if (m && size) { const px = size * Math.hypot(m.a, m.b); if (smallest === null || px < smallest) smallest = px; }
            }
            return {
              unit: article.dataset.g9Unit || article.id,
              identityPx: identity ? Math.round(identity.getBoundingClientRect().height) : null,
              supportOffsetPx: primary && support ? Math.round(Math.abs(top(support) - top(primary))) : null,
              smallestFigureTextPx: smallest === null ? null : Math.round(smallest * 10) / 10,
            };
          });
          const max = key => rows.reduce((m, row) => row[key] === null ? m : Math.max(m, row[key]), 0);
          const min = key => rows.reduce((m, row) => row[key] === null ? m : (m === null ? row[key] : Math.min(m, row[key])), null);
          return { articles: rows.length, identityMaxPx: max('identityPx'), supportOffsetMaxPx: max('supportOffsetPx'),
                   smallestFigureTextPx: min('smallestFigureTextPx'), worstIdentity: rows.sort((a, b) => (b.identityPx || 0) - (a.identityPx || 0))[0] || null };
        })(),
        stageSupportLayout: !!expectedColumns && new RegExp(`grid-template-columns:\\s*minmax\\(0(?:px)?,\\s*${expectedColumns.primary}fr\\)\\s*minmax\\(0(?:px)?,\\s*${expectedColumns.support}fr\\)`).test(sheetText),
        core1aLayout: (() => {
          // One sample per two-column row (a .g9-split with both columns); a band with only one column is not a row of the layout.
          const splits = [...document.querySelectorAll('article.g9-stage-support .g9-split')]
            .filter(split => visible(split) && !split.classList.contains('g9-split-support-only') && !split.classList.contains('g9-split-primary-only'));
          const samples = splits.map(split => {
            const primary = split.querySelector(':scope > .g9-col-primary');
            const support = split.querySelector(':scope > .g9-col-support');
            const style = getComputedStyle(split);
            const primaryBox = primary?.getBoundingClientRect();
            const supportBox = support?.getBoundingClientRect();
            const expanded = style.display === 'grid' && !!primaryBox && !!supportBox;
            const denominator = expanded ? primaryBox.width + supportBox.width : 0;
            return {
              unit: split.closest('article')?.dataset.g9Unit || null,
              display: style.display,
              gridTemplateColumns: style.gridTemplateColumns,
              primaryWidthPx: primaryBox ? Math.round(primaryBox.width * 10) / 10 : null,
              supportWidthPx: supportBox ? Math.round(supportBox.width * 10) / 10 : null,
              supportFraction: denominator ? Math.round((supportBox.width / denominator) * 1000) / 1000 : null,
              supportStacksAfterPrimary: !!primaryBox && !!supportBox && supportBox.top >= primaryBox.bottom - 1,
            };
          });
          return {
            articleCount: samples.length,
            samples,
            expandedCount: samples.filter(sample => sample.display === 'grid').length,
            stackedCount: samples.filter(sample => sample.supportStacksAfterPrimary).length,
          };
        })(),
        tableContainment: (() => {
          const tables = [...document.querySelectorAll('table')].filter(visible);
          const outsideLocalScroller = tables.filter(table => !table.closest('.g9-table-scroll'));
          const localScrollers = [...document.querySelectorAll('.g9-table-scroll')].filter(visible);
          return {
            tables: tables.length,
            tablesOutsideLocalScroller: outsideLocalScroller.length,
            localScrollers: localScrollers.length,
            locallyScrollable: localScrollers.filter(el => el.scrollWidth > el.clientWidth + 1).length,
          };
        })(),
        controlGeometry: (() => {
          const intended = controls.filter(el =>
            el.matches('button,summary,[data-g9-stage-step],header a,.g9-cu-nav a,nav[data-g9-breadcrumb] a')
          );
          const boxes = intended.map(el => ({ el, box: el.getBoundingClientRect() }));
          const gaps = [];
          for (let i = 0; i < boxes.length; i += 1) {
            for (let j = i + 1; j < boxes.length; j += 1) {
              const a = boxes[i].box, b = boxes[j].box;
              const verticalOverlap = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
              const horizontalOverlap = Math.min(a.right, b.right) - Math.max(a.left, b.left);
              if (verticalOverlap > 0) {
                const gap = Math.max(b.left - a.right, a.left - b.right);
                if (gap >= 0) gaps.push(gap);
              } else if (horizontalOverlap > 0) {
                const gap = Math.max(b.top - a.bottom, a.top - b.bottom);
                if (gap >= 0) gaps.push(gap);
              }
            }
          }
          return {
            intendedControls: intended.length,
            minGapPx: gaps.length ? Math.round(Math.min(...gaps) * 10) / 10 : null,
          };
        })(),
        anchorSafety: (() => {
          const shell = document.querySelector('[data-g9-shell-header]');
          const sticky = shell && ['fixed', 'sticky'].includes(getComputedStyle(shell).position);
          const shellHeight = sticky ? shell.getBoundingClientRect().height : 0;
          const anchors = [...document.querySelectorAll('article[id],section[id]')];
          const risky = anchors.filter(el => {
            const margin = parseFloat(getComputedStyle(el).scrollMarginTop) || 0;
            return sticky && margin + 1 < shellHeight;
          });
          return {
            stickyHeaderHeightPx: Math.round(shellHeight * 10) / 10,
            anchors: anchors.length,
            riskyAnchors: risky.length,
            riskyAnchorSample: risky.slice(0, 3).map(el => el.id),
          };
        })(),
        focusProbe: (() => {
          const candidates = controls.filter(el => !el.disabled && el.getAttribute('aria-disabled') !== 'true');
          let failures = 0;
          let visibleFocus = 0;
          for (const el of candidates) {
            el.focus({ preventScroll: true });
            if (document.activeElement !== el) {
              failures += 1;
              continue;
            }
            const style = getComputedStyle(el);
            const outline = parseFloat(style.outlineWidth) || 0;
            const boxShadow = style.boxShadow && style.boxShadow !== 'none';
            if (outline > 0 || boxShadow) visibleFocus += 1;
          }
          return { candidates: candidates.length, focusFailures: failures, visibleFocus };
        })(),
        learningStart: (() => {
          const first = document.querySelector('[data-g9-bucket-orientation],[data-g9-block="inferential_jump"],[data-g9-derivation-bridge],.g9-cu');
          if (!first) return { topPx: null, viewportHeights: null };
          const top = first.getBoundingClientRect().top + window.scrollY;
          return {
            topPx: Math.round(top * 10) / 10,
            viewportHeights: Math.round((top / window.innerHeight) * 1000) / 1000,
          };
        })(),
        constructionStart: (() => {
          const first = document.querySelector('[data-g9-block="inferential_jump"],[data-g9-derivation-bridge],.g9-cu');
          if (!first) return { topPx: null, viewportHeights: null };
          const top = first.getBoundingClientRect().top + window.scrollY;
          return {
            topPx: Math.round(top * 10) / 10,
            viewportHeights: Math.round((top / window.innerHeight) * 1000) / 1000,
          };
        })(),
        metadataMissingUnits: [...document.querySelectorAll('article[data-g9-unit]')].filter(article => {
          const strip = article.querySelector('[data-g9-meta-strip]');
          return !strip || !strip.querySelector('[data-g9-meta-item]');
        }).length,
        searchCorpusMissingUnits: [...document.querySelectorAll('article[data-g9-unit]')].filter(article =>
          !(article.dataset.g9SearchText || '').trim()
        ).length,
        gatedOpenBeforeAttempt: [...document.querySelectorAll('details[data-requires-attempt]')].filter(d => d.open).length,
        protectedSearchMatches: (() => {
          const input = document.querySelector('[data-g9-search-input]');
          if (!input) return 0;
          let leaks = 0;
          for (const article of document.querySelectorAll('article[data-g9-unit]')) {
            const protectedBlock = article.querySelector('details[data-requires-attempt] [data-g9-block]');
            if (!protectedBlock) continue;
            const text = protectedBlock.textContent.replace(/\s+/g, ' ').trim();
            if (text.length < 24) continue;
            const safe = (article.dataset.g9SearchText || '').toLowerCase();
            const candidates = text
              .split(/[.!?;]\s+/)
              .map(part => part.trim())
              .filter(part => part.length >= 24 && !safe.includes(part.toLowerCase()))
              .sort((a, b) => b.length - a.length);
            if (!candidates.length) continue;
            const query = candidates[0].slice(0, Math.min(64, candidates[0].length));
            if (safe.includes(query.toLowerCase())) continue;
            input.value = query;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            if (!article.hidden) leaks += 1;
            input.value = '';
            input.dispatchEvent(new Event('input', { bubbles: true }));
          }
          return leaks;
        })(),
      };
    }, { minTarget, expectedColumns, expectedTablet });
    r.expectedLayout = policy && policy.support_fraction
      ? { supportFraction: policy.support_fraction, minPx: policy.expanded_min_px || 1100 } : null;
    r.externalRequests = [...new Set(requests)];
    if (profile === 'core1a-spec' && file === 'core1a.html') {
      r.interaction = {
        stageKeyboard: { available: false, changed: null },
        sectionKeyboard: { available: false, resolved: null, historyRestored: null },
        reducedMotion: { activeAnimations: null },
        zoom200: { horizontalOverflowPx: null, overflowSample: [] },
      };

      const stageNext = page.locator('[data-g9-stage-step="next"]').first();
      if (await stageNext.count()) {
        r.interaction.stageKeyboard.available = true;
        const label = page.locator('[data-g9-stage-label]').first();
        const before = (await label.textContent()) || '';
        await stageNext.focus();
        await page.keyboard.press('Enter');
        const after = (await label.textContent()) || '';
        r.interaction.stageKeyboard.changed = before !== after;
      }

      const nextSection = page.locator('[data-g9-next-section]').first();
      if (await nextSection.count()) {
        r.interaction.sectionKeyboard.available = true;
        const href = await nextSection.getAttribute('href');
        const beforeUrl = page.url();
        await nextSection.focus();
        await page.keyboard.press('Enter');
        await page.waitForTimeout(25);
        r.interaction.sectionKeyboard.resolved = !!href && new URL(page.url()).hash === href;
        await page.goBack();
        await page.waitForTimeout(25);
        r.interaction.sectionKeyboard.historyRestored = page.url() === beforeUrl;
      }

      await page.emulateMedia({ reducedMotion: 'reduce' });
      r.interaction.reducedMotion.activeAnimations = await page.evaluate(() =>
        document.getAnimations().filter(animation => animation.playState === 'running').length
      );
      await page.emulateMedia({ reducedMotion: 'no-preference' });

      r.interaction.zoom200 = await page.evaluate(async () => {
        const root = document.documentElement;
        const before = root.style.getPropertyValue('--g9-zoom');
        root.style.setProperty('--g9-zoom', '2');
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        const body = document.body;
        const visible = el => {
          const box = el.getBoundingClientRect();
          return box.width > 0 && box.height > 0;
        };
        const visibleElements = [...document.querySelectorAll('body *')].filter(visible);
        const overflowing = visibleElements
          .filter(el => {
            if (el.closest('.g9-table-scroll')) return false;
            const box = el.getBoundingClientRect();
            return box.right > root.clientWidth + 1 || box.left < -1;
          })
          .slice(0, 8)
          .map(el => {
            const box = el.getBoundingClientRect();
            return {
              tag: el.tagName.toLowerCase(),
              id: el.id || null,
              className: typeof el.className === 'string' ? el.className : null,
              text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80),
              left: Math.round(box.left * 10) / 10,
              right: Math.round(box.right * 10) / 10,
              width: Math.round(box.width * 10) / 10,
            };
          });
        const ownOverflowSample = visibleElements
          .filter(el => !el.closest('.g9-table-scroll') && el.scrollWidth > el.clientWidth + 1)
          .slice(0, 8)
          .map(el => ({
            tag: el.tagName.toLowerCase(),
            id: el.id || null,
            className: typeof el.className === 'string' ? el.className : null,
            clientWidth: el.clientWidth,
            scrollWidth: el.scrollWidth,
            delta: el.scrollWidth - el.clientWidth,
            text: (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80),
          }));
        const edges = visibleElements.reduce((acc, el) => {
          if (el.closest('.g9-table-scroll')) return acc;
          const box = el.getBoundingClientRect();
          acc.maxRight = Math.max(acc.maxRight, box.right);
          acc.minLeft = Math.min(acc.minLeft, box.left);
          return acc;
        }, { maxRight: 0, minLeft: 0 });
        const finalRootClientWidth = root.clientWidth;
        const finalRootScrollWidth = root.scrollWidth;
        const finalBodyClientWidth = body.clientWidth;
        const finalBodyScrollWidth = body.scrollWidth;
        const overflow = finalRootScrollWidth - finalRootClientWidth;
        if (before) root.style.setProperty('--g9-zoom', before);
        else root.style.removeProperty('--g9-zoom');
        return {
          horizontalOverflowPx: overflow,
          overflowSample: overflowing,
          ownOverflowSample,
          rootClientWidth: finalRootClientWidth,
          rootScrollWidth: finalRootScrollWidth,
          bodyClientWidth: finalBodyClientWidth,
          bodyScrollWidth: finalBodyScrollWidth,
          maxRight: Math.round(edges.maxRight * 10) / 10,
          minLeft: Math.round(edges.minLeft * 10) / 10,
        };
      });
    }
    out.viewports[vp.name] = r;
  }
  report[file] = out;
  await page.close();
}
await browser.close();
if (server) await new Promise(resolve => server.close(resolve));
if (enforce && profile === 'core1a-spec') {
  const core = report['core1a.html'];
  const failures = [];
  if (!core) failures.push('core1a.html: missing from audit report');
  else {
    if (core.errors.length) failures.push(`core1a.html: page errors: ${core.errors.join(' | ')}`);
    for (const vp of CORE1A_SPEC_VIEWPORTS) {
      const row = core.viewports[vp.name];
      if (!row) {
        failures.push(`core1a.html ${vp.name}: missing viewport result`);
        continue;
      }
      if (row.horizontalOverflowPx !== 0) failures.push(`${vp.name}: page overflow ${row.horizontalOverflowPx}px`);
      if (row.smallTargets !== 0) failures.push(`${vp.name}: ${row.smallTargets} controls below 48px`);
      if (row.controlGeometry.minGapPx != null && row.controlGeometry.minGapPx < 8) {
        failures.push(`${vp.name}: intended control gap ${row.controlGeometry.minGapPx}px < 8px`);
      }
      if (row.tableContainment.tablesOutsideLocalScroller !== 0) {
        failures.push(`${vp.name}: ${row.tableContainment.tablesOutsideLocalScroller} table(s) outside local scroller`);
      }
      if (row.svg !== row.svgAccessible) failures.push(`${vp.name}: accessible SVG ${row.svgAccessible}/${row.svg}`);
      if (row.anchorSafety.riskyAnchors !== 0) failures.push(`${vp.name}: ${row.anchorSafety.riskyAnchors} sticky-obscured anchor(s)`);
      if (row.focusProbe.focusFailures !== 0 || row.focusProbe.visibleFocus !== row.focusProbe.candidates) {
        failures.push(`${vp.name}: focus ${row.focusProbe.visibleFocus}/${row.focusProbe.candidates}, failures=${row.focusProbe.focusFailures}`);
      }
      if (row.externalRequests.length !== 0) failures.push(`${vp.name}: external request(s): ${row.externalRequests.join(', ')}`);
      const layout = row.core1aLayout;
      const want = row.expectedLayout;
      if (!want) failures.push(`${vp.name}: the page's blueprint declares no two-column layout to check against`);
      else if (vp.width >= want.minPx) {
        if (layout.expandedCount !== layout.articleCount) failures.push(`${vp.name}: expanded layout ${layout.expandedCount}/${layout.articleCount}`);
        for (const sample of layout.samples) {
          if (sample.supportFraction == null || Math.abs(sample.supportFraction - want.supportFraction) > 0.03) {
            failures.push(`${vp.name}: support fraction for ${sample.unit} is ${sample.supportFraction}`);
          }
        }
      } else if (layout.stackedCount !== layout.articleCount) {
        failures.push(`${vp.name}: portrait/compact stack ${layout.stackedCount}/${layout.articleCount}`);
      }
      const interaction = row.interaction;
      if (!interaction?.stageKeyboard?.available || interaction.stageKeyboard.changed !== true) {
        failures.push(`${vp.name}: staged representation keyboard control failed`);
      }
      if (!interaction?.sectionKeyboard?.available || interaction.sectionKeyboard.resolved !== true
          || interaction.sectionKeyboard.historyRestored !== true) {
        failures.push(`${vp.name}: section deep-link/history keyboard flow failed`);
      }
      if (interaction?.reducedMotion?.activeAnimations !== 0) {
        failures.push(`${vp.name}: reduced-motion active animations=${interaction?.reducedMotion?.activeAnimations}`);
      }
      if (interaction?.zoom200?.horizontalOverflowPx !== 0) {
        failures.push(`${vp.name}: 200% zoom overflow=${interaction?.zoom200?.horizontalOverflowPx}px`);
      }
    }
  }
  if (failures.length) {
    console.error('core1a-spec enforcement failed:');
    failures.forEach(failure => console.error(' - ' + failure));
    process.exitCode = 1;
  } else {
    console.log('core1a-spec enforcement: PASS');
  }
}

if (enforce && profile === 'tablet-12.7') {
  // The 12.7-inch tablet blueprint's promises, for every page whose blueprint declares them: the identity block is short enough that
  // the first screen shows the work, the two columns start together, nothing overflows, and every control is a touch target.
  const failures = [];
  for (const [file, r] of Object.entries(report)) {
    if (r.errors.length) failures.push(`${file}: page errors: ${r.errors.join(' | ')}`);
    for (const vp of TABLET_12_7_VIEWPORTS) {
      const row = r.viewports[vp.name];
      if (!row) { failures.push(`${file} ${vp.name}: missing viewport result`); continue; }
      if (row.horizontalOverflowPx !== 0) failures.push(`${file} ${vp.name}: page overflow ${row.horizontalOverflowPx}px`);
      if (row.smallTargets !== 0) failures.push(`${file} ${vp.name}: ${row.smallTargets} controls below 48px`);
      if (!row.tablet) continue;
      const bp = blueprints.blueprints.find(b => `${b.id}@${b.version}` === row.blueprint);
      const promise = bp.responsive_policy.tablet_12_7;
      const landscape = vp.width > vp.height;
      if (landscape && row.tablet.identityMaxPx > promise.identity_max_px + 12) {
        failures.push(`${file} ${vp.name}: the identity block is ${row.tablet.identityMaxPx}px tall (${row.tablet.worstIdentity?.unit}); the blueprint allows ${promise.identity_max_px}px`);
      }
      if (vp.width >= bp.responsive_policy.expanded_min_px && row.tablet.supportOffsetMaxPx > 2) {
        failures.push(`${file} ${vp.name}: the support column starts ${row.tablet.supportOffsetMaxPx}px away from the primary column's top`);
      }
    }
  }
  if (failures.length) {
    console.error('tablet-12.7 enforcement failed:');
    failures.forEach(failure => console.error(' - ' + failure));
    process.exitCode = 1;
  } else {
    console.log('tablet-12.7 enforcement: PASS');
  }
}

for (const [file, r] of Object.entries(report)) {
  const a = r.viewports[VIEWPORTS[0].name], p = r.viewports[VIEWPORTS.find(v => v.height > v.width)?.name || VIEWPORTS[1].name];
  console.log(`${file}: bp=${a.blueprint} slots=${a.slotMarkers} home=${JSON.stringify(a.homeLinks)} nav1=${a.navFirstLink} sticky=${a.headerFixedOrSticky} ` +
    `targets<48=${a.smallTargets}/${a.controls} minFont=${a.minFontPx} overflowL=${a.horizontalOverflowPx} overflowP=${p.horizontalOverflowPx} hoverOnly=${a.hoverOnlyHandlers} external=${a.externalRequests.length} ` +
    `svg=${a.svg} (a11y ${a.svgAccessible}) details=${a.disclosures} gated=${a.gatedDisclosures} attempts=${a.attemptFields} focusCSS=${a.focusStyles} print=${a.printStyles} ` +
    `stage68=${a.stageSupportLayout} metaMissing=${a.metadataMissingUnits} searchMissing=${a.searchCorpusMissingUnits} protectedSearch=${a.protectedSearchMatches} gatedOpen=${a.gatedOpenBeforeAttempt} landmarks=${JSON.stringify(a.landmarks)} js=${a.scripts} errors=${r.errors.length}`);
  if (profile === 'tablet-12.7') {
    for (const vp of TABLET_12_7_VIEWPORTS) console.log(`    tablet ${vp.name}: ${JSON.stringify(r.viewports[vp.name]?.tablet)}`);
  }
  if (profile === 'core1a-spec') {
    console.log(`    core1a: contentWidth=${a.contentWidthPx} layout=${JSON.stringify(a.core1aLayout)} tables=${JSON.stringify(a.tableContainment)} controls=${JSON.stringify(a.controlGeometry)} anchors=${JSON.stringify(a.anchorSafety)} focus=${JSON.stringify(a.focusProbe)} learningStart=${JSON.stringify(a.learningStart)} constructionStart=${JSON.stringify(a.constructionStart)} interaction=${JSON.stringify(a.interaction)}`);
  }
  console.log(`    small targets: ${a.smallTargetSample.join(' | ')}`);
}
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(report, null, 2));
