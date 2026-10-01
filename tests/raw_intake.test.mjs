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

test('a question keeps the lines the Owner wrote, in the browser as in Python, and its identity ignores the layout', () => {
  const w = runtime();
  const laid = '2.  A boat points due east at 4 m/s.\n(a)  Find its velocity.\n\n(b) Find the distance in 10 s.';
  const flat = '2. A boat points due east at 4 m/s. (a) Find its velocity. (b) Find the distance in 10 s.';
  const request = { subject: 'Anything', questions: [laid] };
  const tmp = fs.mkdtempSync('/tmp/raw-intake-');
  fs.writeFileSync(`${tmp}/request.json`, JSON.stringify(request));
  const run = spawnSync('python3', ['Shared/tools/raw_intake.py', '--input', `${tmp}/request.json`], { cwd: root, encoding: 'utf8' });
  assert.equal(run.status, 0, run.stderr || run.stdout);
  const python = JSON.parse(run.stdout);
  const browser = plain(w.RAW_INTAKE.intake(request, w.GRADE9V3_RESEARCH_FIRST_WORKFLOW));
  assert.deepEqual(browser, python);
  const kept = browser.inputs.questions[0];
  assert.equal(kept.text, 'A boat points due east at 4 m/s.\n(a) Find its velocity.\n(b) Find the distance in 10 s.');
  assert.equal(kept.label, '2');
  const alone = plain(w.RAW_INTAKE.intake({ subject: 'Anything', questions: [flat] }, w.GRADE9V3_RESEARCH_FIRST_WORKFLOW));
  assert.equal(alone.inputs.questions[0].id, kept.id, 'the same question laid out differently is the same question');
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

test('browser first-stage route equals Python for requested, supplied and syllabus-only jobs', () => {
  const w = runtime();
  const questions = ['Q1. A car goes from 10 m/s to 30 m/s in 8 s. Find its acceleration.'];
  const cases = [
    { subject: 'Physics', questions },
    { subject: 'Physics', questions, requested_cores: ['core1a'] },
    { subject: 'Physics', syllabus: ['Distance and displacement'] },
    { subject: 'Physics', syllabus: ['Vectors'], requested_cores: 'CORE2, core1a' },
    { subject: 'Physics', questions: ['Q5'], requested_cores: ['CORE2'] },
    { subject: 'Physics', questions, requested_cores: ['CORE9'] },
  ];
  for (const request of cases) {
    const tmp = fs.mkdtempSync('/tmp/raw-intake-');
    fs.writeFileSync(`${tmp}/request.json`, JSON.stringify(request));
    const run = spawnSync('python3', ['Shared/tools/raw_intake.py', '--input', `${tmp}/request.json`], { cwd: root, encoding: 'utf8' });
    const python = JSON.parse(run.stdout);
    const browser = plain(w.RAW_INTAKE.intake(request, w.GRADE9V3_RESEARCH_FIRST_WORKFLOW));
    assert.deepEqual(browser, python, JSON.stringify(request));
  }
});

test('the copy-paste agent prompt follows the first-stage route and not the old six-Core script', () => {
  const w = runtime();
  const wf = w.GRADE9V3_RESEARCH_FIRST_WORKFLOW;
  const bank = w.RAW_INTAKE.intake({ subject: 'Physics', questions: ['Q1. Find x if 2x = 6.'] }, wf);
  const prompt = w.RAW_INTAKE.agentPrompt(bank, wf);
  assert.match(prompt, /Route: SUPPLIED_QUESTIONS\. Build and show CORE2 first/);
  assert.match(prompt, /separate key PDF/);
  assert.match(prompt, /docs\/method\/PROTOCOL\.md/);
  assert.doesNotMatch(prompt, /render the six Cores/);
  assert.doesNotMatch(prompt, /promote_verified/);
  const concept = w.RAW_INTAKE.intake({ subject: 'Physics', syllabus: ['Vectors'], requested_cores: ['CORE1A'] }, wf);
  const conceptPrompt = w.RAW_INTAKE.agentPrompt(concept, wf);
  assert.match(conceptPrompt, /Route: REQUESTED_CORES\. Build and show CORE1A first/);
  assert.doesNotMatch(conceptPrompt, /separate key PDF/);
  assert.match(conceptPrompt, /A hold is never an output/);
});

test('the entry form offers a first-Core choice and sends it with the request', () => {
  const page = read('public/raw-intake/index.html');
  assert.match(page, /id="cores"/);
  assert.match(read('public/js/raw-intake.js'), /requested_cores = \[draft\.cores\]/);
});
