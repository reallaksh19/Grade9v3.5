import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { TextEncoder } from 'node:util';

const rootUrl = new URL('../', import.meta.url);
const rootPath = fileURLToPath(rootUrl);
const siteSource = fs.readFileSync(new URL('../public/data/data.js', import.meta.url), 'utf8');
const dataSource = fs.readFileSync(new URL('../public/data/prompt-composer-data.js', import.meta.url), 'utf8');
const appSource = fs.readFileSync(new URL('../public/js/core-prompt-composer.js', import.meta.url), 'utf8');
const fixturePath = 'tests/fixtures/prompt-composer/projectile-stress-set.json';
const fixture = JSON.parse(fs.readFileSync(new URL('./fixtures/prompt-composer/projectile-stress-set.json', import.meta.url), 'utf8'));

function runtime() {
  const window = {};
  const context = vm.createContext({ window, globalThis: window, TextEncoder, console });
  vm.runInContext(siteSource, context);
  vm.runInContext(dataSource, context);
  vm.runInContext(appSource, context);
  return window;
}

test('browser composition preserves the five-row canonical mapping and owner-confirmed R3 scope', () => {
  const w = runtime();
  const result = w.PROMPT_COMPOSER.composeDocument(fixture, w.GRADE9V3_PROMPT_COMPOSER, w.GRADE9V3);
  assert.equal(result.passed, true);
  assert.equal(result.prompt_brief.scope.status, 'OWNER_CONFIRMED_CANONICAL_RUNG');
  assert.deepEqual(JSON.parse(JSON.stringify(result.prompt_brief.scope.canonical_primary_rungs)), ['R1','R2','R3']);
  assert.deepEqual(JSON.parse(JSON.stringify(result.prompt_brief.question_rows.map(row => row.primary_location.rung))), ['R1','R3','R3','R3','R2']);
  assert.equal(result.prompt_brief.learner_entry.owner_estimate.knowledge_percentage, 50);
  assert.equal('source_basis' in result.authoring_request, false);
});

test('browser and Python agree on mapping semantics and deterministic prompt digests', () => {
  const w = runtime();
  const browser = w.PROMPT_COMPOSER.composeDocument(fixture, w.GRADE9V3_PROMPT_COMPOSER, w.GRADE9V3);
  const run = spawnSync('python3', ['Shared/tools/prompt_composer.py', '--input', fixturePath], {cwd: rootPath, encoding:'utf8'});
  assert.equal(run.status, 0, run.stderr || run.stdout);
  const python = JSON.parse(run.stdout);
  assert.equal(browser.prompt_brief.input_digest, python.prompt_brief.input_digest);
  assert.equal(browser.prompt_brief.prompt_digest, python.prompt_brief.prompt_digest);
  assert.equal(browser.prompt_brief.scope.status, python.prompt_brief.scope.status);
  assert.deepEqual(JSON.parse(JSON.stringify(browser.prompt_brief.scope.canonical_primary_rungs)), python.prompt_brief.scope.canonical_primary_rungs);
  assert.deepEqual(
    JSON.parse(JSON.stringify(browser.prompt_brief.question_rows.map(r => [r.canonical_question_ref,r.primary_capability_ref,r.primary_location.rung,r.mapping_status]))),
    python.prompt_brief.question_rows.map(r => [r.canonical_question_ref,r.primary_capability_ref,r.primary_location.rung,r.mapping_status])
  );
  assert.deepEqual(
    JSON.parse(JSON.stringify(browser.prompt_brief.trace_rows.map(r => [r.question_ids,r.primary_capability_ref,r.matrix_ref,r.rung,r.status]))),
    python.prompt_brief.trace_rows.map(r => [r.question_ids,r.primary_capability_ref,r.matrix_ref,r.rung,r.status])
  );
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
  const result=w.PROMPT_COMPOSER.composeDocument(math,w.GRADE9V3_PROMPT_COMPOSER,w.GRADE9V3);
  assert.equal(result.prompt_brief.learner_entry.owner_estimate.knowledge_percentage,0);
  assert.equal(result.prompt_brief.question_rows[0].summary,'<script>globalThis.pwned=true</script>');
});
