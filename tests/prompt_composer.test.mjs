import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';
import { TextEncoder } from 'node:util';

const root = new URL('../', import.meta.url);
const dataSource = fs.readFileSync(new URL('../public/data/prompt-composer-data.js', import.meta.url), 'utf8');
const appSource = fs.readFileSync(new URL('../public/js/core-prompt-composer.js', import.meta.url), 'utf8');
const fixture = JSON.parse(fs.readFileSync(new URL('./fixtures/prompt-composer/projectile-stress-set.json', import.meta.url), 'utf8'));
const pyGoldenPath = new URL('./fixtures/prompt-composer/projectile-browser-parity.json', import.meta.url);

function runtime() {
  const window = {};
  const context = vm.createContext({ window, globalThis: window, TextEncoder, console });
  vm.runInContext(dataSource, context);
  vm.runInContext(appSource, context);
  return window;
}

test('browser composition preserves the five-row canonical mapping and owner-confirmed R3 scope', () => {
  const w = runtime();
  const result = w.PROMPT_COMPOSER.composeDocument(fixture, w.GRADE9V3_PROMPT_COMPOSER);
  assert.equal(result.passed, true);
  assert.equal(result.prompt_brief.scope.status, 'OWNER_CONFIRMED_CANONICAL_RUNG');
  assert.deepEqual(
    JSON.parse(JSON.stringify(result.prompt_brief.scope.canonical_primary_rungs)),
    ['R1','R2','R3']
  );
  assert.deepEqual(
    JSON.parse(JSON.stringify(result.prompt_brief.question_rows.map(row => row.primary_location.rung))),
    ['R1','R3','R3','R3','R2']
  );
  assert.equal(result.prompt_brief.learner_entry.owner_estimate.knowledge_percentage, 50);
  assert.equal('source_basis' in result.authoring_request, false);
});

test('browser and Python golden agree on normalized brief/trace/digests', () => {
  const w = runtime();
  const result = w.PROMPT_COMPOSER.composeDocument(fixture, w.GRADE9V3_PROMPT_COMPOSER);
  const golden = JSON.parse(fs.readFileSync(pyGoldenPath, 'utf8'));
  assert.equal(result.prompt_brief.input_digest, golden.input_digest);
  assert.equal(result.prompt_brief.prompt_digest, golden.prompt_digest);
  assert.deepEqual(JSON.parse(JSON.stringify(result.prompt_brief.scope)), golden.scope);
  assert.deepEqual(JSON.parse(JSON.stringify(result.prompt_brief.question_rows)), golden.question_rows);
  assert.deepEqual(JSON.parse(JSON.stringify(result.prompt_brief.keyword_fingerprint)), golden.keyword_fingerprint);
  assert.deepEqual(JSON.parse(JSON.stringify(result.prompt_brief.trace_rows)), golden.trace_rows);
});

test('pasted hostile markup stays plain parsed data and exact 0 is not blank', () => {
  const w = runtime();
  const rows = w.PROMPT_COMPOSER.parseRows('X | Q-MATH-LINEAR-01 | <script>globalThis.pwned=true</script>');
  assert.equal(rows[0].summary, '<script>globalThis.pwned=true</script>');
  const math = {
    repository_basis: fixture.repository_basis,
    subject: 'Mathematics',
    questions: rows,
    owner_confirmed_rung: {matrix_id:'MATRIX-MATH-LINEAR-EQUATIONS',rung:'R2',by:'owner'},
    learner: {owner_estimate:{knowledge_percentage:0,by:'owner',instruction:'Starting coordinate only; not evidence of prerequisite mastery.'}},
    requested_cores:['CORE1A'],
    execution_order:['CORE1A']
  };
  const result=w.PROMPT_COMPOSER.composeDocument(math,w.GRADE9V3_PROMPT_COMPOSER);
  assert.equal(result.prompt_brief.learner_entry.owner_estimate.knowledge_percentage,0);
  assert.equal(result.prompt_brief.question_rows[0].summary,'<script>globalThis.pwned=true</script>');
});
