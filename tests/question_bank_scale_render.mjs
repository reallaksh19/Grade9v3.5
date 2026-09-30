// Local artifact exercise, not a CI workflow. Requires a real Chromium installation.
//   node tests/question_bank_scale_render.mjs [counts] [out.json]
// Loads the real Question Bank page over local HTTP against a synthetic corpus of N questions and
// measures what the learner waits for: time to a drawn list, and the cost of the interactions that
// redraw it. Timings depend on the machine and are evidence for a sharding decision, not thresholds.
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'playwright')); }

const repo = path.resolve(process.argv[2] === '--repo' ? process.argv[3] : path.dirname(new URL(import.meta.url).pathname) + '/..');
const args = process.argv.filter((a, i) => !(a === '--repo' || process.argv[i - 1] === '--repo')).slice(2);
const counts = (args[0] || '500,2000,5000,10000').split(',').map(Number);
const outFile = args[1] ? path.resolve(args[1]) : null;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf' };
const median = (values) => [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)];

function serve(root) {
  const server = http.createServer((req, res) => {
    const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({ server, base: `http://127.0.0.1:${server.address().port}` })));
}

const GENERATE = `
import json, os, sys
sys.path.insert(0, ${JSON.stringify(repo)})
from Shared.tools import build_question_bank_platform as bqp, question_bank_scale as sc
n, out = int(sys.argv[1]), sys.argv[2]
platform = bqp.build_from_projection({"questions": sc.synthetic_questions(n)})
sizes = {}
for path, data in bqp.artifact_payloads(platform).items():
    if path.suffix == ".js":
        target = out + "/" + path.relative_to("public").as_posix()
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "wb").write(data)
        sizes[path.name] = len(data)
print(json.dumps(sizes))
`;

const browser = await playwright.chromium.launch({ args: ['--enable-precise-memory-info'] });
const results = [];
try {
  for (const n of counts) {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), `qb-render-${n}-`));
    for (const dir of ['css', 'js', 'vendor', 'question-bank']) fs.cpSync(path.join(repo, 'public', dir), path.join(root, dir), { recursive: true });
    fs.copyFileSync(path.join(repo, 'public/index.html'), path.join(root, 'index.html'));
    const sizes = JSON.parse(execFileSync('python3', ['-c', GENERATE, String(n), root]).toString());
    const site = await serve(root);
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(`${site.base}/question-bank/index.html`);
    const timeToList = await page.evaluate(() => window.Grade9QuestionBank.ready.then(() => performance.now()));
    const heap = await page.evaluate(() => performance.memory.usedJSHeapSize);
    const cards = await page.$$eval('#qbResults > article', (nodes) => nodes.length);

    const timed = (script) => page.evaluate(async (source) => {
      const t = performance.now();
      await new Function(`return (async () => { ${source} })()`)();
      return performance.now() - t;
    }, script);
    const samples = { subject_tab: [], search: [], load_more: [], study_open: [], filter_topic: [] };
    for (let i = 0; i < 5; i += 1) {
      samples.subject_tab.push(await timed(`
        const tabs = [...document.querySelectorAll('#qbSubjectTabs [role=tab]')];
        tabs[1 + (${i} % (tabs.length - 1))].click();
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));`));
      samples.filter_topic.push(await timed(`
        const pill = document.querySelectorAll('#qbTopicStrip .qb-topic-pill')[1];
        if (pill) pill.click();
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));`));
      samples.search.push(await timed(`
        const box = document.querySelector('#qbSearch');
        box.value = ['synthetic invariant', 'record 25', 'topic 7', 'family 12', 'evaluate'][${i}];
        box.dispatchEvent(new Event('input', { bubbles: true }));
        await new Promise((r) => setTimeout(r, 160));
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));`) - 160);
      await page.click('#qbClear');
      samples.load_more.push(await timed(`
        const more = document.querySelector('#qbLoadMore');
        if (!more.hidden) more.click();
        await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));`));
      samples.study_open.push(await timed(`
        document.querySelector('#qbResults .qb-qactions button').click();
        while (!document.querySelector('#qbStudyDialog[open] .qb-panel')) await new Promise((r) => setTimeout(r, 5));`));
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => !document.querySelector('#qbStudyDialog').open);
    }
    const summary = Object.fromEntries(Object.entries(samples).map(([k, v]) => [k, { median_ms: +median(v).toFixed(1), worst_ms: +Math.max(...v).toFixed(1) }]));
    results.push({ questions: n, artifact_bytes: sizes, first_page_cards: cards, time_to_list_ms: +timeToList.toFixed(1), js_heap_bytes: heap, interactions: summary, page_errors: errors, timings_are_thresholds: false });
    await context.close();
    site.server.close();
    fs.rmSync(root, { recursive: true, force: true });
  }
} finally {
  await browser.close();
}
const text = JSON.stringify({ tool: 'tests/question_bank_scale_render.mjs', cpus: os.cpus().length, results }, null, 2) + '\n';
if (outFile) fs.writeFileSync(outFile, text); else process.stdout.write(text);
