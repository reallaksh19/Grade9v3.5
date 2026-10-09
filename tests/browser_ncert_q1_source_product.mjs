import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

const root = path.resolve('public/test/products/ncert-u01-q01');
const receipt = JSON.parse(fs.readFileSync(path.join(root, 'deploy-receipt.json'), 'utf8'));
assert.equal(receipt.draft, true);
assert.equal(receipt.accepted, false, 'technical proof cannot publish Q1');
assert.deepEqual(receipt.roles, ['CORE2', 'CORE1A']);
assert.equal(receipt.selection_counts.core2, 1);
const intake = JSON.parse(fs.readFileSync(path.resolve('TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json'), 'utf8'));
const q1 = intake.questions.find(q => q.id === 'ncert-exemplar-g9-math-u01-q01');
assert.ok(q1, 'original NCERT intake Q1 is missing');
assert.equal(q1.options.length, 4, 'source Q1 options must not be truncated');
const printReceipt = JSON.parse(fs.readFileSync(path.join(root, 'print-receipt.json'), 'utf8'));
assert.deepEqual(printReceipt.pages.map(page => page.pdf).sort(), ['core1a.pdf', 'core2.pdf']);
for (const f of ['core1a.pdf', 'core2.pdf']) {
  const bytes = fs.readFileSync(path.join(root, f));
  assert.ok(bytes.length > 1000, 'missing learner PDF ' + f);
  assert.equal(bytes.subarray(0, 5).toString('ascii'), '%PDF-', 'invalid PDF header: ' + f);
  const claim = printReceipt.pages.find(page => page.pdf === f);
  assert.equal('sha256:' + createHash('sha256').update(bytes).digest('hex'), claim.pdf_digest,
    'learner PDF diverged from browser printer receipt: ' + f);
}
assert.ok(!fs.existsSync(path.join(root, 'core2.key.pdf')), 'protected answer key PDF must stay private');
const browser = await chromium.launch({headless: true});
const viewports = [
  {width: 390, height: 844, label: 'mobile portrait'},
  {width: 820, height: 1180, label: 'tablet portrait'},
  {width: 1366, height: 854, label: 'tablet landscape'}
];
const evidence = {source_id: 'ncert-exemplar-g9-math-u01-q01', accepted: false, cases: []};
try {
  for (const vp of viewports) {
    const page = await browser.newPage({viewport: {width: vp.width, height: vp.height}});
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    await page.goto(pathToFileURL(path.join(root, 'core2.html')).href);
    assert.equal(await page.locator('html').getAttribute('data-g9-role'), 'CORE2');
    assert.equal(await page.locator('html').getAttribute('data-g9-test'), 'sandbox-draft');
    const question = page.locator('#ncert-exemplar-g9-math-u01-q01');
    assert.equal(await question.count(), 1);
    const questionText = await question.innerText();
    assert.match(questionText, /Every rational number is/);
    assert.equal((await question.locator('[data-g9-block="stem"]').innerText()).trim(), q1.stem,
      'rendered Q1 stem diverges from official intake');
    assert.match(questionText, /NCERT source custody witnessed \(academic validation separate\)/);
    const options = question.locator('input[data-g9-choice][type=radio]');
    assert.equal(await options.count(), 4, 'original source options must remain present');
    const renderedOptions = (await question.locator('[data-g9-block="options"] label span').allTextContents())
      .map(text => text.trim());
    assert.deepEqual(renderedOptions, q1.options,
      'rendered radio options must exactly match all four original NCERT source options');
    assert.equal(await page.locator('a[data-g9-pdf-link]').getAttribute('href'), 'core2.pdf');
    const commit = question.locator('button[data-g9-commit]');
    assert.equal(await commit.count(), 1);
    await options.nth(2).check();
    await commit.click();
    assert.equal(await question.getAttribute('data-attempted'), '1',
      'valid learner submission must set the attempt-committed state');
    assert.equal(await options.nth(2).isChecked(), true,
      'original selected answer must survive attempt commitment');
    const box = await commit.boundingBox();
    assert.ok(box && box.height >= 40 && box.width >= 48,
      'undersized attempt button in ' + vp.label + ': ' + JSON.stringify(box));
    await page.goto(pathToFileURL(path.join(root, 'core1a.html')).href);
    assert.equal(await page.locator('html').getAttribute('data-g9-role'), 'CORE1A');
    assert.equal(await page.locator('html').getAttribute('data-g9-test'), 'sandbox-draft');
    assert.equal(await page.locator('#CU-TEST-NCERT-U01-RATIONAL-REAL-INCLUSION').count(), 1);
    const math = page.locator('.g9-math math').first();
    assert.ok(await math.count(), 'authored relation needs semantic MathML');
    const mathText = await math.textContent();
    assert.ok(mathText.includes('ℚ') && mathText.includes('⊆') && mathText.includes('ℝ'),
      'the rational/real inclusion direction was changed');
    assert.equal(await page.locator('a[data-g9-pdf-link]').getAttribute('href'), 'core1a.pdf');
    assert.deepEqual(errors, [], 'runtime script errors in ' + vp.label);
    evidence.cases.push({ ...vp, source_options: 4, source_options_exact: true, attempt_committed: true,
      roles: 2, mathml: 'ℚ ⊆ ℝ', js_errors: 0 });
    await page.close();
  }
} finally {
  await browser.close();
}
const output = '/tmp/ncert-q1-browser-evidence.json';
fs.writeFileSync(output, JSON.stringify(evidence, null, 2) + '\n');
console.log('PASS: nonaccepted NCERT Q1 Core2/Core1A browser replay at ' + viewports.length + ' viewports');
