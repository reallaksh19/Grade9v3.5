// Local artifact exercise, not a CI workflow. Requires a real Chromium installation.
// Measures what the browser pays for the generated Question Bank contracts at synthetic scale.
// Byte and count fields are deterministic. Timings depend on the machine and are evidence for a
// sharding / Web Worker decision, never a pass/fail threshold. Loading a script runs synchronously on the
// main thread, so load_ms is the blocking cost; the PerformanceObserver 'longtask' feed was tried and
// reported nothing for a 160 ms script evaluation, so it is deliberately not used.
import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import zlib from 'node:zlib';
const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require(path.join(execFileSync('npm', ['root', '-g']).toString().trim(), 'playwright')); }

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const scales = (process.argv[2] || '500,2000,5000').split(',').map(Number);
const outFile = process.argv[3] ? path.resolve(process.argv[3]) : null;

const GENERATE = `
import json, sys
sys.path.insert(0, ${JSON.stringify(repo)})
from Shared.tools import build_question_bank_platform as bqp, question_bank_platform as qbp, question_bank_scale as sc
n, out = int(sys.argv[1]), sys.argv[2]
platform = qbp.assemble_platform({"questions": sc.synthetic_questions(n)})
sizes = {}
for path, data in bqp.artifact_payloads(platform).items():
    if path.suffix == ".js":
        open(out + "/" + path.name, "wb").write(data)
        sizes[path.name] = len(data)
print(json.dumps(sizes))
`;

const QUERIES = [
  ['synthetic invariant', {}],
  ['record 250', {}],
  ['topic 7', {}],
  ['family 12', {}],
  ['invariant', { subject_ref: 'fixture:subject:2' }],
  ['no such phrase anywhere', {}],
];

const median = (values) => [...values].sort((a, b) => a - b)[Math.floor(values.length / 2)];
const browser = await playwright.chromium.launch({ args: ['--enable-precise-memory-info'] });
const results = [];
try {
  for (const n of scales) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), `qb-scale-${n}-`));
    const sizes = JSON.parse(execFileSync('python3', ['-c', GENERATE, String(n), dir]).toString());
    const gzip = Object.fromEntries(Object.keys(sizes).map((name) => [
      name, zlib.gzipSync(fs.readFileSync(path.join(dir, name)), { level: 6 }).length]));
    fs.writeFileSync(path.join(dir, 'index.html'), '<!doctype html><meta charset="utf-8"><title>scale</title><body></body>');
    const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (e) => errors.push(e.message));
    await page.goto(pathToFileURL(path.join(dir, 'index.html')).href);
    const load = async (name) => page.evaluate(async (src) => {
      const t = performance.now();
      await new Promise((resolve, reject) => {
        const s = document.createElement('script');
        s.src = src; s.onload = resolve; s.onerror = () => reject(new Error(src));
        document.head.append(s);
      });
      return performance.now() - t;
    }, pathToFileURL(path.join(dir, name)).href);
    const heapBefore = await page.evaluate(() => performance.memory.usedJSHeapSize);
    const loadMs = {};
    for (const name of ['manifest', 'catalog', 'search', 'resources']) loadMs[name] = await load(`question-bank-${name}.js`);
    await page.addScriptTag({ path: path.join(repo, 'public/js/question-bank-data-service.js') });
    const heapAfter = await page.evaluate(() => performance.memory.usedJSHeapSize);
    const search = await page.evaluate(({ queries, reps }) => {
      const out = [];
      for (const [query, filters] of queries) {
        const times = [];
        let hits = 0;
        for (let i = 0; i < reps; i += 1) {
          const t = performance.now();
          hits = window.Grade9QuestionBankData.search(query, filters).length;
          times.push(performance.now() - t);
        }
        out.push({ query, filters, hits, times });
      }
      return out;
    }, { queries: QUERIES, reps: 7 });
    const perQuery = search.map((row) => ({ query: row.query, hits: row.hits, median_ms: median(row.times), worst_ms: Math.max(...row.times) }));
    results.push({
      questions: n,
      bytes: Object.fromEntries(Object.entries(sizes).map(([k, v]) => [k.replace(/^question-bank-|\.js$/g, ''), v])),
      gzip_bytes: Object.fromEntries(Object.entries(gzip).map(([k, v]) => [k.replace(/^question-bank-|\.js$/g, ''), v])),
      timings_are_thresholds: false,
      load_ms: loadMs,
      heap_growth_bytes: heapAfter - heapBefore,
      search: perQuery,
      search_median_ms: median(perQuery.map((row) => row.median_ms)),
      search_worst_ms: Math.max(...perQuery.map((row) => row.worst_ms)),
      page_errors: errors,
    });
    await context.close();
    fs.rmSync(dir, { recursive: true, force: true });
  }
} finally {
  await browser.close();
}
const text = JSON.stringify({ tool: 'tests/question_bank_scale_browser.mjs', cpus: os.cpus().length, results }, null, 2) + '\n';
if (outFile) fs.writeFileSync(outFile, text); else process.stdout.write(text);
