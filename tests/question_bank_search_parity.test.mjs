// The generated search index must find everything the page's original in-browser search found.
// The original algorithm is reproduced here verbatim as the oracle; the index may find more, never less.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
globalThis.window = globalThis;
globalThis.document = { currentScript: null };
for (const name of ['question-bank-data.js', 'question-bank-manifest.js', 'question-bank-catalog.js', 'question-bank-questions.js', 'question-bank-search.js', 'question-bank-resources.js']) {
  new Function(fs.readFileSync(path.join(repo, 'public/data', name), 'utf8'))();
}
new Function(fs.readFileSync(path.join(repo, 'public/js/question-bank-data-service.js'), 'utf8'))();
const Data = globalThis.Grade9QuestionBankData;
const questions = globalThis.GRADE9_QUESTION_BANK.questions;

const norm = (value) => String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const original = (query) => {
  const terms = norm(query).split(/\s+/).filter(Boolean);
  return questions.filter((q) => {
    const haystack = norm([q.id, q.subject, q.topic, q.exam, q.year, q.paper, q.question_type, q.stem,
      q.primary_capability_ref, q.secondary_capability_refs.join(' '), q.stable_crux_move].join(' '));
    return terms.every((term) => haystack.includes(term));
  }).map((q) => q.id);
};
const indexed = (query) => Data.search(query, { kind: 'question' }).map((doc) => doc.id);

const vocabulary = new Set();
questions.forEach((q) => norm([q.subject, q.topic, q.exam, q.question_type, q.primary_capability_ref, q.stable_crux_move, q.stem])
  .split(' ').forEach((word) => { if (word.length > 2) vocabulary.add(word); }));
const QUERIES = [
  '', 'zzzzzz-no-such-term',
  ...questions.map((q) => q.id),
  ...questions.slice(0, 25).map((q) => `${q.exam} ${q.year}`),
  ...questions.slice(0, 25).map((q) => `${q.subject} ${q.question_type}`),
  ...[...vocabulary].sort().filter((_, i) => i % 7 === 0),
];

test('the index finds every question the original search found, for every query', () => {
  assert.ok(QUERIES.length > 150, `expected a broad query set, got ${QUERIES.length}`);
  const lost = [];
  for (const query of QUERIES) {
    const now = new Set(indexed(query));
    const missing = original(query).filter((id) => !now.has(id));
    if (missing.length) lost.push({ query, missing });
  }
  assert.deepEqual(lost, []);
});

test('an empty query lists every question and an unknown term lists none', () => {
  assert.equal(indexed('').length, questions.length);
  assert.equal(indexed('zzzzzz-no-such-term').length, 0);
});

test('extra hits are limited to the few added search fields, not a broader match rule', () => {
  let queriesWithExtras = 0;
  for (const query of QUERIES) {
    const before = new Set(original(query));
    if (indexed(query).some((id) => !before.has(id))) queriesWithExtras += 1;
  }
  assert.ok(queriesWithExtras <= Math.ceil(QUERIES.length * 0.05), `${queriesWithExtras} of ${QUERIES.length} queries gained hits`);
});
