// The generated Question Bank contracts load in a fixed order, from one build, and fail visibly.
// Uses the real committed artifacts and a small script-loading stand-in for the browser.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { pathToFileURL } from 'node:url';

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const data = (name) => fs.readFileSync(path.join(repo, 'public/data', name), 'utf8');
const NAMES = {
  manifest: 'question-bank-manifest.js',
  catalog: 'question-bank-catalog.js',
  questions: 'question-bank-questions.js',
  search: 'question-bank-search.js',
  resources: 'question-bank-resources.js',
};
const GLOBALS = [
  'GRADE9_QUESTION_BANK_MANIFEST', 'GRADE9_QUESTION_BANK_CATALOG', 'GRADE9_QUESTION_BANK_QUESTIONS',
  'GRADE9_QUESTION_BANK_SEARCH', 'GRADE9_QUESTION_BANK_RESOURCES', 'GRADE9_QUESTION_BANK_DETAIL_SHARDS',
];

// Serves scripts to the service the way a page would, and records every request.
function site({ overrides = {}, fail = new Set(), delay = {} } = {}) {
  const requests = [];
  globalThis.window = globalThis;
  for (const key of GLOBALS) delete globalThis[key];
  globalThis.document = {
    currentScript: null,
    createElement() { return { dataset: {}, set src(value) { this._src = value; }, get src() { return this._src; } }; },
    head: {
      append(node) {
        const url = new URL(node.src, 'http://site.test/question-bank/');
        const file = url.pathname.replace(/^\//, '');
        requests.push({ file, search: url.search });
        const respond = () => {
          const source = overrides[file] ?? (fs.existsSync(path.join(repo, 'public', file)) ? fs.readFileSync(path.join(repo, 'public', file), 'utf8') : null);
          if (fail.has(file) || source === null) { node.onerror(); return; }
          new Function(source)();
          node.onload();
        };
        setTimeout(respond, delay[file] ?? 0);
      },
    },
  };
  new Function(data(NAMES.manifest))();
  return requests;
}

let copies = 0;
async function service() {
  await import(pathToFileURL(path.join(repo, 'public/js/question-bank-data-service.js')).href + `?copy=${copies++}`);
  return globalThis.Grade9QuestionBankData;
}

const filesOf = (requests) => requests.map((r) => r.file.replace('data/', ''));

test('bootstrap draws navigation first, then the list and search, then optional resources', async () => {
  const requests = site();
  const qb = await service();
  const stages = [];
  const result = await qb.bootstrap({ onStage: (name, ready) => stages.push([name, { ...ready }]) });
  assert.equal(result.stale, false);
  assert.deepEqual(result.warnings, []);
  assert.deepEqual(stages.map((s) => s[0]), ['CATALOG_READY', 'LIST_READY', 'SEARCH_READY', 'RESOURCES_READY']);
  assert.equal(stages[0][1].CATALOG_READY, true);
  assert.equal(stages[0][1].LIST_READY, false, 'the list is not claimed before it has loaded');
  assert.equal(filesOf(requests)[0], NAMES.catalog, 'the catalog is requested before anything else');
  assert.equal(qb.summaries().length, 77);
  assert.equal(qb.views().length, 1);
  assert.ok(qb.resources().length > 0);
  assert.equal(qb.assertCoherence(), globalThis.GRADE9_QUESTION_BANK_MANIFEST.build_id);
});

test('every artifact is requested under the manifest build id', async () => {
  const requests = site();
  const qb = await service();
  await qb.bootstrap();
  const buildId = globalThis.GRADE9_QUESTION_BANK_MANIFEST.build_id;
  const artifacts = requests.filter((r) => r.file !== NAMES.manifest);
  assert.equal(artifacts.length, 4);
  for (const request of artifacts) assert.equal(request.search, `?b=${encodeURIComponent(buildId)}`, request.file);
});

test('a required artifact that fails rejects with a named code and leaves the rest usable', async () => {
  site({ fail: new Set([`data/${NAMES.questions}`]) });
  const qb = await service();
  await assert.rejects(qb.bootstrap(), (error) => error.code === 'QB_ARTIFACT_FAILED' && /question-bank-questions/.test(error.message));
  const ready = qb.readiness();
  assert.equal(ready.CATALOG_READY, true);
  assert.equal(ready.LIST_READY, false);
});

test('an optional artifact that fails is reported, not fatal', async () => {
  site({ fail: new Set([`data/${NAMES.resources}`]) });
  const qb = await service();
  const result = await qb.bootstrap();
  assert.deepEqual(result.warnings.map((w) => [w.name, w.code]), [['resources', 'QB_ARTIFACT_FAILED']]);
  const ready = qb.readiness();
  assert.equal(ready.LIST_READY && ready.SEARCH_READY, true);
  assert.equal(ready.RESOURCES_READY, false);
  assert.deepEqual(qb.resources(), []);
});

test('an artifact from another build is rejected and removed, never combined', async () => {
  const foreign = data(NAMES.search).replace(/"build_id":"[^"]+"/, '"build_id":"sha256:some-other-build"');
  assert.notEqual(foreign, data(NAMES.search));
  site({ overrides: { [`data/${NAMES.search}`]: foreign } });
  const qb = await service();
  await assert.rejects(qb.bootstrap(), (error) => error.code === 'QB_BUILD_MISMATCH' && /build mismatch for search/.test(error.message));
  assert.equal(globalThis.GRADE9_QUESTION_BANK_SEARCH, undefined, 'the foreign artifact does not stay loaded');
  assert.throws(() => qb.search('anything'), /not loaded/);
});

test('a foreign optional artifact is a warning and is removed', async () => {
  const foreign = data(NAMES.resources).replace(/"build_id":"[^"]+"/, '"build_id":"sha256:other"');
  site({ overrides: { [`data/${NAMES.resources}`]: foreign } });
  const qb = await service();
  const result = await qb.bootstrap();
  assert.equal(result.warnings[0].code, 'QB_BUILD_MISMATCH');
  assert.equal(globalThis.GRADE9_QUESTION_BANK_RESOURCES, undefined);
});

test('a missing manifest or an absolute artifact path is refused', async () => {
  site();
  const qb = await service();
  delete globalThis.GRADE9_QUESTION_BANK_MANIFEST;
  await assert.rejects(qb.bootstrap(), (error) => error.code === 'QB_MANIFEST_MISSING');
  site();
  const other = await service();
  globalThis.GRADE9_QUESTION_BANK_MANIFEST.bootstrap.catalog.path = 'https://elsewhere.test/catalog.js';
  await assert.rejects(other.bootstrap(), (error) => error.code === 'QB_PATH_NOT_SITE_RELATIVE');
});

test('concurrent loads of the same artifact make one request', async () => {
  const requests = site({ delay: { [`data/${NAMES.catalog}`]: 15 } });
  const qb = await service();
  const first = qb.bootstrap();
  const second = qb.bootstrap();
  const [a, b] = await Promise.all([first, second]);
  assert.equal(requests.filter((r) => r.file === `data/${NAMES.catalog}`).length, 1);
  assert.equal(a.stale, true, 'the older bootstrap gives way to the newer one');
  assert.equal(b.stale, false);
  assert.equal(qb.readiness().SEARCH_READY, true);
});

test('concurrent requests for one detail shard make one request', async () => {
  const requests = site();
  const qb = await service();
  await qb.bootstrap();
  const question = qb.summaries()[0];
  const token = qb.beginRequest();
  const [a, b] = await Promise.all([qb.loadQuestion(question.id, token), qb.loadQuestion(question.id, token)]);
  assert.equal(a.question.id, question.id);
  assert.equal(b.question.id, question.id);
  assert.equal(requests.filter((r) => r.file.includes('question-bank-details')).length, 1);
});

test('an older detail response never overwrites a newer selection', async () => {
  const requests = site();
  const qb = await service();
  await qb.bootstrap();
  const [first, second] = [qb.summaries()[0], qb.summaries().find((row) => row.subject_ref !== qb.summaries()[0].subject_ref)];
  const oldToken = qb.beginRequest();
  const older = qb.loadQuestion(first.id, oldToken);
  const newer = await qb.loadQuestion(second.id);
  assert.equal(newer.stale, false);
  assert.equal((await older).stale, true);
  assert.ok(requests.length > 0);
});

test('a failed detail shard is not left behind and can be retried', async () => {
  const failing = new Set();
  site({ fail: failing });
  const qb = await service();
  await qb.bootstrap();
  const id = qb.summaries()[0].id;
  const meta = qb.shardMetaForQuestion(id);
  failing.add(meta.path.startsWith('data/') ? meta.path : `data/${meta.path}`);
  qb.beginRequest();
  await assert.rejects(qb.loadQuestion(id), (error) => error.code === 'QB_ARTIFACT_FAILED');
  failing.clear();
  const loaded = await qb.loadQuestion(id);
  assert.equal(loaded.question.id, id);
});

test('a detail shard from another build is rejected and not left registered, so a retry can succeed', async () => {
  const overrides = {};
  site({ overrides });
  const qb = await service();
  await qb.bootstrap();
  const id = qb.summaries()[0].id;
  const meta = qb.shardMetaForQuestion(id);
  const genuine = fs.readFileSync(path.join(repo, 'public', meta.path), 'utf8');
  overrides[meta.path] = genuine.replace(/"build_id":"[^"]+"/g, '"build_id":"sha256:other"');
  assert.notEqual(overrides[meta.path], genuine);
  qb.beginRequest();
  await assert.rejects(qb.loadQuestion(id), (error) => error.code === 'QB_BUILD_MISMATCH');
  assert.equal(globalThis.GRADE9_QUESTION_BANK_DETAIL_SHARDS[meta.id], undefined);
  delete overrides[meta.path];
  const loaded = await qb.loadQuestion(id);
  assert.equal(loaded.question.id, id);
});

test('reset clears everything loaded and Retry busts caches', async () => {
  const failing = new Set([`data/${NAMES.search}`]);
  const requests = site({ fail: failing });
  const qb = await service();
  await assert.rejects(qb.bootstrap(), (error) => error.code === 'QB_ARTIFACT_FAILED');
  failing.clear();
  qb.reset();
  assert.equal(qb.readiness().CATALOG_READY, false, 'nothing from the failed attempt survives');
  const result = await qb.bootstrap();
  assert.equal(result.stale, false);
  const retried = requests.filter((r) => r.search.includes('&r=1'));
  assert.equal(retried.length, 4, 'every artifact of the retry is requested with a cache-busting attempt number');
  assert.equal(qb.readiness().SEARCH_READY, true);
});

test('search finds documents from the loaded index and honours filters', async () => {
  site();
  const qb = await service();
  await qb.bootstrap();
  const all = qb.search('');
  assert.ok(all.length >= 77);
  const physics = qb.search('', { subject_ref: 'SUBJECT-PHYSICS', kind: 'question' });
  assert.ok(physics.length > 0 && physics.every((doc) => doc.subject_ref === 'SUBJECT-PHYSICS'));
});
