import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { TextEncoder } from 'node:util';

const root = fileURLToPath(new URL('../', import.meta.url));
const read = rel => fs.readFileSync(new URL('../' + rel, import.meta.url), 'utf8');
const SUBJECTS = ['physics-motion-2d', 'mathematics-quadratics', 'chemistry-mole-concept'];

function runtime() {
  const window = {};
  const context = vm.createContext({ window, globalThis: window, TextEncoder, console });
  vm.runInContext(read('public/data/research-first-workflow.js'), context);
  vm.runInContext(read('public/js/raw-intake.js'), context);
  return window;
}

const plain = value => JSON.parse(JSON.stringify(value));

test('browser intake equals Python intake for every subject fixture', () => {
  const w = runtime();
  for (const name of SUBJECTS) {
    const request = JSON.parse(read(`tests/fixtures/research-first/${name}.json`)).request;
    const tmp = fs.mkdtempSync('/tmp/raw-intake-');
    fs.writeFileSync(`${tmp}/request.json`, JSON.stringify(request));
    const run = spawnSync('python3', ['Shared/tools/raw_intake.py', '--input', `${tmp}/request.json`], { cwd: root, encoding: 'utf8' });
    assert.equal(run.status, 0, run.stderr || run.stdout);
    const python = JSON.parse(run.stdout);
    const browser = plain(w.RAW_INTAKE.intake(request, w.GRADE9V3_RESEARCH_FIRST_WORKFLOW));
    assert.deepEqual(browser, python, name);
  }
});

test('pasted blocks keep owner labels and source hints as data, not identity', () => {
  const w = runtime();
  const blocks = w.RAW_INTAKE.parseQuestionBlocks(
    'Q15: A ball is thrown at 20 m/s at 30°.\nSource: some paper\n\nQ7\n\n<script>globalThis.pwned=1</script> Find x.');
  assert.equal(blocks.length, 3);
  assert.equal(blocks[0].source_hint, 'some paper');
  const plan = w.RAW_INTAKE.intake({ subject: 'Anything', questions: blocks }, w.GRADE9V3_RESEARCH_FIRST_WORKFLOW);
  assert.equal(plan.status, 'RESEARCH_AND_AUTHOR');
  assert.equal(plan.inputs.questions[0].label, 'Q15');
  assert.equal(plan.inputs.questions[1].text_status, 'LABEL_ONLY');
  assert.match(plan.inputs.questions[2].text, /<script>/);
  assert.equal(globalThis.pwned, undefined);
  assert.equal(plan.learner_start.blocking, false);
  assert.doesNotMatch(JSON.stringify(plan), /HOLD/);
  const prompt = w.RAW_INTAKE.agentPrompt(plan, w.GRADE9V3_RESEARCH_FIRST_WORKFLOW);
  assert.match(prompt, /owner label Q15, not an identity/);
  assert.match(prompt, /A hold is never an output/);
});

test('entry page wires the research-first path and keeps the mapped composer secondary', () => {
  const page = read('public/raw-intake/index.html');
  assert.match(page, /research-first-workflow\.js/);
  assert.match(page, /raw-intake\.js/);
  assert.doesNotMatch(page, /canonical question ref \|/);
  const home = read('public/index.html');
  const primary = home.match(/<a href="([^"]+)" class="[^"]*question-set-cta-action/);
  assert.equal(primary && primary[1], 'raw-intake/index.html');
  assert.match(home, /core-prompt-composer\/index\.html/);
});
