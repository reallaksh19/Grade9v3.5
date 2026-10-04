#!/usr/bin/env node
/**
 * Chromium audit for staged instructional SVGs.
 *
 * This supplements core-page-audit.mjs. It measures whether each visible stage actually
 * contains usable instructional geometry, rather than merely proving that an SVG element
 * and its labels exist in the DOM.
 *
 * Usage:
 *   node tools/site-audit/staged-svg-audit.mjs page.html [page2.html ...] --json report.json [--screenshots DIR]
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const argv = process.argv.slice(2);
let reportPath = null;
let screenshotsDir = null;
const pages = [];
for (let i = 0; i < argv.length; i += 1) {
  if (argv[i] === '--json') reportPath = argv[++i];
  else if (argv[i] === '--screenshots') screenshotsDir = argv[++i];
  else pages.push(argv[i]);
}
if (!pages.length || !reportPath) {
  console.error('usage: staged-svg-audit.mjs page.html [...] --json report.json [--screenshots DIR]');
  process.exit(2);
}

const VIEWPORTS = [
  { name: 'landscape-1366', width: 1366, height: 854 },
  { name: 'landscape-1440', width: 1440, height: 900 },
  { name: 'portrait-854', width: 854, height: 1366 },
  { name: 'portrait-900', width: 900, height: 1440 },
];
const sha256 = (b) => `sha256:${crypto.createHash('sha256').update(b).digest('hex')}`;
const safe = (s) => String(s).replace(/[^A-Za-z0-9_.-]+/g, '-').replace(/^-+|-+$/g, '');

const browser = await chromium.launch({ headless: true });
const findings = [];
const pageReports = [];
try {
  for (const input of pages) {
    const abs = path.resolve(input);
    const bytes = fs.readFileSync(abs);
    const fileDigest = sha256(bytes);
    const one = { path: input, sha256: fileDigest, viewports: [] };
    for (const vp of VIEWPORTS) {
      const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', e => errors.push(String(e)));
      page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
      await page.goto(pathToFileURL(abs).href, { waitUntil: 'load' });
      const figureCount = await page.locator('figure[data-g9-figure]').count();
      const figures = [];
      for (let fi = 0; fi < figureCount; fi += 1) {
        const figure = page.locator('figure[data-g9-figure]').nth(fi);
        const total = Number(await figure.getAttribute('data-g9-stages-total') || '1');
        if (total < 2) continue;
        const figId = await figure.getAttribute('data-g9-fig') || `figure-${fi + 1}`;
        const chipCount = await figure.locator('[data-g9-stage-goto]').count();
        const stageCount = Math.max(chipCount, total);
        const stages = [];
        let previousSignature = null;
        for (let si = 0; si < stageCount; si += 1) {
          if (chipCount > si) {
            await figure.locator('[data-g9-stage-goto]').nth(si).click();
            await page.waitForTimeout(20);
          }
          const measurement = await figure.evaluate((root) => {
            const svg = root.querySelector('svg');
            if (!svg) return { missingSvg: true };
            const svgRect = svg.getBoundingClientRect();
            const visible = (el) => {
              const cs = getComputedStyle(el);
              if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity || '1') <= 0.05) return false;
              const r = el.getBoundingClientRect();
              if (r.width > 0.5 && r.height > 0.5) return true;
              if (el instanceof SVGGeometryElement) {
                try { return el.getTotalLength() > Math.min(svgRect.width, svgRect.height) * 0.05; } catch (_) {}
              }
              return false;
            };
            const primitiveSelector = '[data-g9-geometry-role="primary"],path,circle,ellipse,rect,polygon,polyline,line';
            const primitives = [...svg.querySelectorAll(primitiveSelector)]
              .filter(el => !el.closest('defs,clipPath,mask,marker,pattern') && visible(el))
              .map(el => {
                const r = el.getBoundingClientRect();
                const cs = getComputedStyle(el);
                let length = 0;
                if (el instanceof SVGGeometryElement) { try { length = el.getTotalLength(); } catch (_) {} }
                const painted = (cs.stroke && cs.stroke !== 'none' && Number(cs.strokeOpacity || '1') > 0.05)
                  || (cs.fill && cs.fill !== 'none' && Number(cs.fillOpacity || '1') > 0.05);
                return { tag: el.tagName, x: r.x, y: r.y, width: r.width, height: r.height, length, painted };
              })
              .filter(x => x.painted && (x.width * x.height >= 25 || x.length >= Math.min(svgRect.width, svgRect.height) * 0.12));
            let union = null;
            for (const g of primitives) {
              const x1 = g.x, y1 = g.y, x2 = g.x + Math.max(g.width, 1), y2 = g.y + Math.max(g.height, 1);
              union = union ? {
                x1: Math.min(union.x1, x1), y1: Math.min(union.y1, y1),
                x2: Math.max(union.x2, x2), y2: Math.max(union.y2, y2),
              } : { x1, y1, x2, y2 };
            }
            const occupancy = union && svgRect.width * svgRect.height > 0
              ? ((union.x2 - union.x1) * (union.y2 - union.y1)) / (svgRect.width * svgRect.height) : 0;
            const labels = [...svg.querySelectorAll('text')].filter(visible).map(el => {
              const r = el.getBoundingClientRect();
              const targetRef = el.getAttribute('data-g9-target-ref');
              const target = targetRef ? svg.querySelector(`#${CSS.escape(targetRef)}`) : null;
              return {
                text: (el.textContent || '').trim(),
                clipped: r.left < svgRect.left - 2 || r.top < svgRect.top - 2 || r.right > svgRect.right + 2 || r.bottom > svgRect.bottom + 2,
                targetRef,
                targetVisible: targetRef ? Boolean(target && visible(target)) : null,
              };
            });
            const stageGroups = [...svg.querySelectorAll('[data-g9-stage-id]')]
              .filter(visible).map(g => g.getAttribute('data-g9-stage-id'));
            const textSignature = labels.map(x => x.text).filter(Boolean).join('|');
            const geometrySignature = primitives.map(x => [x.tag, Math.round(x.x), Math.round(x.y), Math.round(x.width), Math.round(x.height), Math.round(x.length)].join(':')).join('|');
            return {
              missingSvg: false,
              svg: { width: svgRect.width, height: svgRect.height },
              stageGroups,
              primaryGeometryCount: primitives.length,
              occupancy,
              labels,
              signature: `${stageGroups.join(',')}::${geometrySignature}::${textSignature}`,
            };
          });
          const stageRef = await figure.locator('[data-g9-stage-label]').count()
            ? await figure.locator('[data-g9-stage-label]').first().textContent() : `Stage ${si + 1}`;
          const stageFindings = [];
          if (measurement.missingSvg) stageFindings.push('SVG_MISSING');
          else {
            if (measurement.primaryGeometryCount < 1) stageFindings.push('PRIMARY_GEOMETRY_MISSING');
            if (measurement.occupancy < 0.015) stageFindings.push(`PRIMARY_GEOMETRY_OCCUPANCY_LOW:${measurement.occupancy.toFixed(4)}`);
            for (const label of measurement.labels || []) {
              if (label.clipped) stageFindings.push(`LABEL_CLIPPED:${label.text.slice(0, 40)}`);
              if (label.targetRef && !label.targetVisible) stageFindings.push(`LABEL_TARGET_NOT_VISIBLE:${label.targetRef}`);
            }
            if (previousSignature !== null && previousSignature === measurement.signature) stageFindings.push('STAGE_RENDER_STATE_UNCHANGED');
            previousSignature = measurement.signature;
          }
          let screenshot = null;
          if (screenshotsDir) {
            fs.mkdirSync(screenshotsDir, { recursive: true });
            screenshot = path.join(screenshotsDir, `${safe(path.basename(input))}-${safe(figId)}-${safe(vp.name)}-stage-${si + 1}.png`);
            await figure.screenshot({ path: screenshot });
          }
          for (const detail of stageFindings) {
            findings.push({ page: input, viewport: vp.name, figure: figId, stage: si + 1, detail });
          }
          stages.push({ index: si + 1, label: stageRef?.trim(), ...measurement, findings: stageFindings, screenshot });
        }
        figures.push({ id: figId, stages });
      }
      if (errors.length) for (const detail of errors) findings.push({ page: input, viewport: vp.name, detail: `BROWSER_ERROR:${detail}` });
      one.viewports.push({ ...vp, figures, browserErrors: errors });
      await context.close();
    }
    pageReports.push(one);
  }
} finally {
  await browser.close();
}
const report = {
  schema: 'staged-svg-chromium-audit/v1',
  tool: 'tools/site-audit/staged-svg-audit.mjs',
  engine: 'playwright.chromium',
  profile: 'tablet-12.7',
  status: findings.length ? 'FAIL' : 'PASS',
  findings,
  pages: pageReports,
};
fs.mkdirSync(path.dirname(path.resolve(reportPath)), { recursive: true });
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ status: report.status, findings: findings.length, report: reportPath }));
process.exit(findings.length ? 1 : 0);
