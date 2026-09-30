// Local artifact exercise, not a CI workflow. Requires a real Chromium installation.
//   node tests/question_bank_runtime_browser.mjs [out.json]
// Drives the real Question Bank page over local HTTP: a 6-viewport matrix, learner paths, and the
// failure modes of the generated contracts (stale response, build mismatch, optional and required
// failure). A synthetic Biology subject is then added by the ordinary build and shown without any
// change to the runtime. Results are printed as PASS/FAIL per check; nothing is skipped silently.
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

const repo = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outFile = process.argv[2] ? path.resolve(process.argv[2]) : null;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.png': 'image/png' };

function serve(root) {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://x');
    const file = path.join(root, decodeURIComponent(url.pathname));
    if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end('not found'); return; }
    res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream', 'cache-control': 'no-store' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({ server, base: `http://127.0.0.1:${server.address().port}` })));
}

const results = [];
async function check(name, fn) {
  if (process.env.QB_ONLY && !name.includes(process.env.QB_ONLY)) return;
  try { await fn(); results.push({ name, status: 'PASS' }); console.log('PASS', name); }
  catch (error) { results.push({ name, status: 'FAIL', detail: String(error.message).split('\n')[0] }); console.log('FAIL', name, '-', String(error.message).split('\n')[0]); }
}
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const equal = (actual, expected, message) => assert(actual === expected, `${message}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);

const readGlobal = (file) => {
  const text = fs.readFileSync(file, 'utf8');
  return JSON.parse(text.slice(text.indexOf('=') + 1).trim().replace(/;$/, ''));
};
const catalog = readGlobal(path.join(repo, 'public/data/question-bank-catalog.js'));
const summaries = readGlobal(path.join(repo, 'public/data/question-bank-questions.js')).questions;
const physics = catalog.subjects.find((s) => s.label === 'Physics');
const chemistry = catalog.subjects.find((s) => s.label === 'Chemistry');

const titledTopic = catalog.topics.find((t) => {
  const rows = catalog.subtopics.filter((s) => s.topic_ref === t.id);
  return rows.length > 1 && rows.every((s) => s.label_source === 'CANONICAL_TITLE');
});

const browser = await playwright.chromium.launch();
const live = await serve(path.join(repo, 'public'));

async function open(base, query = '', viewport = { width: 1280, height: 800 }, setup) {
  const context = await browser.newContext({ viewport, hasTouch: true });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  if (setup) await setup(page);
  await page.goto(`${base}/question-bank/index.html${query}`);
  return { page, context, errors };
}
const listed = (page) => page.evaluate(() => window.Grade9QuestionBank.ready);
const visibleIds = (page) => page.$$eval('#qbResults > article', (nodes) => nodes.map((n) => n.id));

// ---------------------------------------------------------------- viewport matrix
const VIEWPORTS = [[390, 844], [800, 1280], [820, 1180], [1180, 820], [1280, 800], [1440, 900]];
for (const [width, height] of VIEWPORTS) {
  await check(`matrix ${width}x${height}: renders from the generated contracts, no overflow, touch targets, no errors`, async () => {
    // Open the strips too: the topic and subtopic pills are primary navigation and must meet the floor.
    const { page, context, errors } = await open(live.base, `?topic=${encodeURIComponent(titledTopic.id)}`, { width, height });
    await listed(page);
    const failed = [];
    page.on('requestfailed', (r) => failed.push(r.url()));
    const facts = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      stats: [...document.querySelectorAll('#qbStats .qb-stat b')].map((n) => n.textContent),
      tabs: [...document.querySelectorAll('#qbSubjectTabs [role=tab]')].map((n) => n.textContent),
      small: [...document.querySelectorAll('#qbSubjectTabs button, #qbTopicStrip button, #qbSubtopicStrip button, #qbActiveFilters button, #qbResults button, #qbCollections button, #qbSubjects button, .qb-filter-panel select, .qb-filter-panel button')]
        .filter((n) => n.getBoundingClientRect().width > 0)
        .map((n) => ({ w: n.getBoundingClientRect().width, h: n.getBoundingClientRect().height, label: n.textContent.trim().slice(0, 30) }))
        .filter((n) => n.h < 44 || n.w < 44),
      shown: document.querySelectorAll('#qbResults > article').length,
      stripPills: document.querySelectorAll('#qbTopicStrip button, #qbSubtopicStrip button').length,
    }));
    assert(errors.length === 0, `page errors: ${errors.join('; ')}`);
    assert(facts.scrollWidth <= facts.clientWidth, `horizontal overflow ${facts.scrollWidth} > ${facts.clientWidth}`);
    equal(facts.stats[0], String(catalog.counts.questions), 'question stat comes from the catalog');
    equal(facts.tabs[0], `All Subjects${catalog.counts.questions}`, 'first tab');
    assert(facts.shown > 0, 'results are drawn');
    assert(facts.stripPills > 2, 'the topic and subtopic strips are open while measuring');
    assert(facts.small.length === 0, `touch targets under 44px: ${JSON.stringify(facts.small.slice(0, 3))}`);
    assert(failed.length === 0, `failed requests: ${failed.join(', ')}`);
    await context.close();
  });
}

// ---------------------------------------------------------------- learner paths
await check('subject tab, topic pill and the resource banner come from catalog and resources', async () => {
  const { page, context } = await open(live.base);
  await listed(page);
  await page.click(`#qbSubjectTabs [data-subject-ref="${physics.id}"]`);
  equal(await page.textContent('#qbResultCount'), `${physics.question_count} of ${catalog.counts.questions} questions`, 'count for the subject');
  const pills = await page.$$eval('#qbTopicStrip .qb-topic-pill', (n) => n.map((x) => x.textContent));
  assert(pills.length > 1, 'the topic strip lists the subject topics');
  const topic = catalog.topics.find((t) => t.subject_ref === physics.id && t.question_count > 0 && t.resource_count > 0);
  await page.click(`#qbTopicStrip .qb-topic-pill:has-text("${topic.label}")`);
  const links = await page.$$eval('#qbTopicBanner a.qb-topic-action-link', (n) => n.map((a) => ({ href: a.getAttribute('href'), kind: a.dataset.kind })));
  assert(links.length > 0, 'the banner links the topic resources');
  for (const link of links) {
    const response = await page.request.get(new URL(link.href, `${live.base}/question-bank/`).href);
    equal(response.status(), 200, `resource link ${link.href}`);
  }
  assert(new URL(page.url()).searchParams.get('topic') === topic.id, 'the URL carries the stable topic id');
  await context.close();
});

const untitledTopic = catalog.topics.find((t) => catalog.subtopics.some((s) => s.topic_ref === t.id && s.label_source !== 'CANONICAL_TITLE') && t.question_count > 0);

await check('subtopics: a fully titled topic offers them, filtering matches membership, URL and chip follow', async () => {
  assert(titledTopic, 'the live corpus has a topic whose subtopics are all canonically titled');
  const { page, context } = await open(live.base, `?topic=${encodeURIComponent(titledTopic.id)}`);
  await listed(page);
  const rows = catalog.subtopics.filter((s) => s.topic_ref === titledTopic.id);
  const labels = await page.$$eval('#qbSubtopicStrip .qb-topic-pill > span:first-child', (n) => n.map((x) => x.textContent));
  equal(labels.join('|'), ['All subtopics', ...rows.map((r) => r.label)].join('|'), 'pills are the canonical titles');
  const pick = rows[0];
  await page.click(`#qbSubtopicStrip .qb-topic-pill:has-text("${pick.label.replace(/"/g, '\\"')}")`);
  const expected = summaries.filter((q) => q.topic_ref === titledTopic.id && (q.subtopic_refs || []).includes(pick.id)).length;
  equal((await page.textContent('#qbResultCount')).split(' ')[0], String(expected), 'count equals membership');
  equal(new URL(page.url()).searchParams.get('subtopic'), pick.id, 'stable ref in the URL');
  assert((await page.textContent('#qbActiveFilters')).includes(pick.label), 'the active filter names the subtopic');
  await page.click('#qbTopicStrip .qb-topic-pill:has-text("All topics")');
  equal(await page.$$eval('#qbSubtopicStrip .qb-topic-pill', (n) => n.length), 0, 'leaving the topic drops its subtopics');
  await context.close();
});

await check('subtopics: a topic with an untitled subtopic shows no raw identifiers and says nothing false', async () => {
  assert(untitledTopic, 'the live corpus has a topic with an untitled subtopic');
  const { page, context } = await open(live.base, `?topic=${encodeURIComponent(untitledTopic.id)}`);
  await listed(page);
  equal(await page.$$eval('#qbSubtopicStrip .qb-topic-pill', (n) => n.length), 0, 'no subtopic strip');
  const navigation = await page.$$eval('#qbSubjectTabs, #qbTopicStrip, #qbSubtopicStrip, #qbActiveFilters, #qbTopicBanner', (n) => n.map((x) => x.textContent).join(' '));
  assert(!navigation.includes('CAP-'), 'no capability identifier appears in the navigation strips');
  await context.close();
});

await check('a subtopic in the URL selects its topic and subject', async () => {
  const sub = catalog.subtopics.find((s) => s.label_source === 'CANONICAL_TITLE');
  const { page, context } = await open(live.base, `?subtopic=${encodeURIComponent(sub.id)}`);
  await listed(page);
  const params = await page.evaluate(() => Object.fromEntries(new URLSearchParams(location.search)));
  equal((await page.$$eval('#qbSubjectTabs [aria-selected=true]', (n) => n.length)), 1, 'a subject tab is selected');
  assert(await page.locator('#qbTopicStrip .qb-topic-pill.active').count() === 1, 'the owning topic is selected');
  await context.close();
});

await check('text search agrees with the generated search index and can be cleared', async () => {
  const { page, context } = await open(live.base);
  await listed(page);
  await page.fill('#qbSearch', 'projectile');
  await page.waitForFunction(() => document.querySelector('#qbResultCount').textContent.startsWith(''));
  await page.waitForTimeout(300);
  const expected = await page.evaluate(() => window.Grade9QuestionBankData.search('projectile', { kind: 'question' }).length);
  assert(expected > 0, 'the fixture query finds questions');
  equal((await page.textContent('#qbResultCount')).split(' ')[0], String(expected), 'result count equals search hits');
  await page.click('#qbClear');
  equal((await page.textContent('#qbResultCount')).split(' ')[0], String(catalog.counts.questions), 'cleared');
  await context.close();
});

await check('Study dialog: opens with detail, traps focus, closes on Escape and returns focus', async () => {
  const { page, context, errors } = await open(live.base);
  await listed(page);
  const button = page.locator('#qbResults .qb-qactions button').first();
  await button.click();
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  assert((await page.textContent('#qbDialogTitle')).includes('Q'), 'title names the question');
  const onScreen = await page.evaluate(() => { const r = document.querySelector('#qbStudyDialog').getBoundingClientRect(); const c = document.querySelector('#qbDialogClose').getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight && r.left >= 0 && r.right <= innerWidth && c.top >= 0 && c.bottom <= innerHeight; });
  assert(onScreen, 'the dialog and its close button are fully inside the viewport');
  for (let i = 0; i < 8; i += 1) await page.keyboard.press('Tab');
  assert(await page.evaluate(() => document.querySelector('#qbStudyDialog').contains(document.activeElement)), 'focus stays inside the dialog');
  assert((await page.evaluate(() => location.hash)).length > 1, 'the question id is in the URL hash');
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => !document.querySelector('#qbStudyDialog').open);
  await page.waitForFunction(() => location.hash === '');
  assert(await button.evaluate((n) => n === document.activeElement), 'focus returns to the Study button');
  assert(errors.length === 0, `page errors: ${errors.join('; ')}`);
  await context.close();
});

await check('Study dialog closes on backdrop click and via its close button', async () => {
  const { page, context } = await open(live.base);
  await listed(page);
  await page.locator('#qbResults .qb-qactions button').first().click();
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  await page.mouse.click(4, 4);
  await page.waitForFunction(() => !document.querySelector('#qbStudyDialog').open);
  await page.locator('#qbResults .qb-qactions button').first().click();
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  await page.click('#qbDialogClose');
  await page.waitForFunction(() => !document.querySelector('#qbStudyDialog').open);
  await context.close();
});

await check('deep link: a question id in the hash opens Study on load', async () => {
  const target = summaries.find((q) => q.subject_ref === physics.id);
  const { page, context } = await open(live.base, `#${target.id}`);
  await listed(page);
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  assert((await page.textContent('#qbDialogBody')).includes(target.id), 'the dialog shows the deep-linked question');
  await context.close();
});

await check('legacy label URLs still work and the stable id is written back', async () => {
  const { page, context } = await open(live.base, `?subject=${encodeURIComponent('Physics')}`);
  await listed(page);
  equal(await page.textContent('#qbResultCount'), `${physics.question_count} of ${catalog.counts.questions} questions`, 'label resolved');
  await page.click(`#qbSubjectTabs [data-subject-ref=""]`);
  await page.click(`#qbSubjectTabs [data-subject-ref="${chemistry.id}"]`);
  assert(new URL(page.url()).searchParams.get('subject') === chemistry.id, 'stable ref in URL');
  await context.close();
});

await check('a saved view opens in study mode with every question loaded from its shard', async () => {
  const view = catalog.views[0];
  const { page, context } = await open(live.base, `?view=${view.id}&mode=study`);
  await listed(page);
  await page.waitForFunction((n) => document.querySelectorAll('#qbResults > article .qb-study-grid').length === n, view.resolved_question_refs.length);
  const shown = await visibleIds(page);
  equal([...shown].sort().join(), [...view.resolved_question_refs].sort().join(), 'exactly the view members are listed');
  equal(shown.join(), summaries.filter((q) => view.resolved_question_refs.includes(q.id)).map((q) => q.id).join(), 'in canonical order, as before');
  await context.close();
});

await check('history: Back restores the previous subject', async () => {
  const { page, context } = await open(live.base);
  await listed(page);
  await page.click(`#qbSubjectTabs [data-subject-ref="${physics.id}"]`);
  await page.click(`#qbSubjectTabs [data-subject-ref="${chemistry.id}"]`);
  await page.goBack();
  await page.waitForFunction((n) => document.querySelector('#qbResultCount').textContent.startsWith(String(n)), physics.question_count);
  await context.close();
});

await check('Load more extends the list by one page', async () => {
  const { page, context } = await open(live.base);
  await listed(page);
  await page.click('#qbLoadMore');
  equal((await visibleIds(page)).length, 40, 'two pages');
  await context.close();
});

await check('keyboard: arrow keys move between subject tabs', async () => {
  const { page, context } = await open(live.base);
  await listed(page);
  await page.focus('#qbSubjectTabs [role=tab][aria-selected=true]');
  await page.keyboard.press('ArrowRight');
  const label = await page.evaluate(() => document.activeElement.textContent);
  assert(label.startsWith(catalog.subjects.filter((s) => s.question_count > 0)[0].label), `focus moved to the first subject tab, got ${label}`);
  equal(await page.evaluate(() => document.activeElement.getAttribute('aria-selected')), 'true', 'and it is selected');
  await context.close();
});

await check('declared math is typeset in result cards and in Study, with no KaTeX errors', async () => {
  const withMath = summaries.find((q) => (q.math_spans || []).length > 0);
  assert(withMath, 'the live corpus has a question with declared stem math');
  const { page, context, errors } = await open(live.base, `?q=${encodeURIComponent(withMath.id)}`);
  await listed(page);
  await page.waitForSelector(`[id="${withMath.id}"] .qb-katex-token .katex`);
  assert((await page.$$eval(`[id="${withMath.id}"] .qb-katex-token`, (n) => n.length)) >= 1, 'the card typesets its declared spans');
  await page.locator(`[id="${withMath.id}"] .qb-qactions button`).click();
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  await page.waitForSelector('#qbDialogBody .qb-katex-token .katex');
  equal(await page.$$eval('.katex-error', (n) => n.length), 0, 'no KaTeX errors');
  assert(errors.length === 0, `page errors: ${errors.join('; ')}`);
  await context.close();
});

await check('math and figures stay inside the dialog at phone width', async () => {
  const withMath = summaries.find((q) => (q.math_spans || []).length > 0) || summaries[0];
  const { page, context } = await open(live.base, `#${withMath.id}`, { width: 390, height: 844 });
  await listed(page);
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  const overflow = await page.evaluate(() => {
    const body = document.querySelector('#qbDialogBody');
    return { scroll: body.scrollWidth, client: body.clientWidth, page: document.documentElement.scrollWidth <= document.documentElement.clientWidth };
  });
  assert(overflow.scroll <= overflow.client + 1 && overflow.page, `dialog content overflows: ${JSON.stringify(overflow)}`);
  await context.close();
});

// ---------------------------------------------------------------- failure modes
await check('stale response: an older Study request never overwrites a newer one', async () => {
  const first = summaries.find((q) => q.subject_ref === physics.id);
  const second = summaries.find((q) => q.subject_ref === chemistry.id);
  const { page, context } = await open(live.base, '', { width: 1280, height: 800 }, async (p) => {
    await p.route('**/data/question-bank-details/*physics*', async (route) => { await new Promise((r) => setTimeout(r, 700)); await route.continue(); });
  });
  await listed(page);
  await page.evaluate(([a, b]) => { window.Grade9QuestionBank.openStudyModal(a); setTimeout(() => window.Grade9QuestionBank.openStudyModal(b), 50); }, [first.id, second.id]);
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  await page.waitForTimeout(1200);
  const shown = await page.textContent('#qbDialogBody');
  assert(shown.includes(second.id) && !shown.includes(first.id), 'the newer question is the one displayed');
  await context.close();
});

await check('required artifact failure is visible and Retry recovers', async () => {
  let block = true;
  const { page, context } = await open(live.base, '', { width: 1280, height: 800 }, async (p) => {
    await p.route('**/data/question-bank-questions.js*', (route) => (block ? route.abort() : route.continue()));
  });
  await page.waitForSelector('#qbStatus[data-tone=error]');
  assert((await page.textContent('#qbStatus')).includes('could not be loaded'), 'the failure is described');
  block = false;
  await page.click('#qbStatus button');
  await listed(page);
  await page.waitForFunction(() => document.querySelector('#qbStatus').hidden);
  equal((await visibleIds(page)).length, 20, 'the list draws after Retry');
  await context.close();
});

await check('optional resource failure leaves the bank usable and says so', async () => {
  const { page, context } = await open(live.base, '', { width: 1280, height: 800 }, async (p) => {
    await p.route('**/data/question-bank-resources.js*', (route) => route.abort());
  });
  await listed(page);
  await page.waitForSelector('#qbStatus[data-tone=warning]');
  equal((await visibleIds(page)).length, 20, 'questions still listed');
  const topic = catalog.topics.find((t) => t.question_count > 0 && t.resource_count > 0);
  await page.click(`#qbSubjectTabs [data-subject-ref="${topic.subject_ref}"]`);
  await page.click(`#qbTopicStrip .qb-topic-pill:has-text("${topic.label}")`);
  equal(await page.$$eval('#qbTopicBanner a', (n) => n.length), 0, 'no resource links without the resource artifact');
  assert(await page.locator('#qbStatus[data-tone=warning]').isVisible(), 'the warning stays visible');
  await context.close();
});

await check('an artifact from another build is refused, not mixed in', async () => {
  const { page, context } = await open(live.base, '', { width: 1280, height: 800 }, async (p) => {
    await p.route('**/data/question-bank-search.js*', async (route) => {
      const response = await route.fetch();
      const body = (await response.text()).replace(/"build_id":"[^"]+"/, '"build_id":"sha256:another-build"');
      await route.fulfill({ response, body });
    });
  });
  await page.waitForSelector('#qbStatus[data-tone=error]');
  assert((await page.textContent('#qbStatus')).includes('different builds'), 'says the builds differ');
  equal(await page.evaluate(() => typeof window.GRADE9_QUESTION_BANK_SEARCH), 'undefined', 'the foreign artifact is not kept');
  await context.close();
});

// ---------------------------------------------------------------- growth falsifier: a new subject, no runtime change
const fixtureRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'qb-biology-'));
for (const dir of ['css', 'js', 'vendor', 'question-bank', 'data']) fs.mkdirSync(path.join(fixtureRoot, dir), { recursive: true });
for (const dir of ['css', 'js', 'vendor', 'question-bank']) fs.cpSync(path.join(repo, 'public', dir), path.join(fixtureRoot, dir), { recursive: true });
fs.copyFileSync(path.join(repo, 'public/index.html'), path.join(fixtureRoot, 'index.html'));
const GENERATE = `
import json, sys
sys.path.insert(0, ${JSON.stringify(repo)})
from Shared.tools import build_question_bank_platform as bqp
out = sys.argv[1]
def q(i, sub, stem, ans):
    return {"id": f"BIO-Q{i:02d}", "order": i, "subject": "Biology", "topic": "Cell Biology", "topic_ref": "TOPIC-BIO-CELL",
            "subtopic_refs": [sub], "question_type": "constructed_response", "exam": "Synthetic Board", "year": 2026,
            "paper": "A", "question_number": str(i), "stem": stem, "subparts": [], "options": [], "conditions": [], "difficulty": {"band": "D1", "score": 2},
            "expected_time_seconds": 90, "common_wrong_route": "", "stable_crux_move": "", "primary_capability_ref": "CAP-BIO-CELL",
            "secondary_capability_refs": [], "family_ref": None, "source_status": "SYNTHETIC_FIXTURE", "wording_custody": "TEST_ONLY",
            "source_hints": [], "scaffolds": [], "math_spans": [], "visual_ref": None, "paper_url": None,
            "answer": {"summary": ans, "reasoning": [f"Step for question {i}"], "check": "Recheck the definition."},
            "lineage": {"adapter": "synthetic_fixture_v1", "package_id": "FIXTURE-BIOLOGY"}}
questions = [q(i, "SUB-BIO-MITOCHONDRIA" if i % 3 == 0 else "SUB-BIO-NUCLEUS", f"Question {i}: which organelle {'releases usable energy (mitochondria)' if i % 3 == 0 else 'stores genetic material'}?", "Mitochondria" if i % 3 == 0 else "Nucleus") for i in range(1, 16)]
titles = {"SUB-BIO-MITOCHONDRIA": {"title": "Mitochondria", "source_ref": "MIC-BIO-MITOCHONDRIA"}, "SUB-BIO-NUCLEUS": {"title": "Nucleus", "source_ref": "MIC-BIO-NUCLEUS"}}
resources = [
  {"id": "BIO-CLINIC-CELL", "kind": "study_clinic", "title": "Cell Biology Study Clinic", "subject": "Biology", "topic": "Cell Biology", "topic_ref": "TOPIC-BIO-CELL", "path": "biology/cell-biology/core2.html", "keywords": ["cell"]},
  {"id": "BIO-EXPLORER-CELL", "kind": "interactive", "title": "Mitochondria explorer", "subject": "Biology", "topic": "Cell Biology", "topic_ref": "TOPIC-BIO-CELL", "path": "biology/cell-biology/explorer.html", "keywords": ["mitochondria"]},
]
views = [{"id": "bio-energy", "title": "Energy questions", "short_title": "Energy", "description": "Questions about usable energy.", "match_mode": "EXACT_POLICY_SET",
          "presentation": {"badge": "5 questions", "source_label": "Fixture", "default_mode": "browse"}, "resolved_question_refs": [f"BIO-Q{i:02d}" for i in (3, 6, 9, 12, 15)]}]
platform = bqp.build_from_projection({"questions": questions, "views": views}, resources, [], titles)
for path, data in bqp.artifact_payloads(platform).items():
    if path.suffix == ".js":
        target = out + "/" + path.relative_to("public").as_posix()
        import os; os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "wb").write(data)
print(platform["build_id"])
`;
execFileSync('python3', ['-c', GENERATE, fixtureRoot]);
const bio = await serve(fixtureRoot);

await check('growth falsifier: a new subject, topic and subtopics appear everywhere with no change to the runtime', async () => {
  const runtime = fs.readFileSync(path.join(repo, 'public/js/question-bank.js'), 'utf8') + fs.readFileSync(path.join(repo, 'public/js/question-bank-data-service.js'), 'utf8');
  for (const word of ['Biology', 'Cell Biology', 'Mitochondria', 'Physics', 'Chemistry', 'Mathematics']) assert(!runtime.includes(word), `the runtime names "${word}"`);
  assert(!/style="[^"]*Biology/.test(fs.readFileSync(path.join(repo, 'public/css/question-bank.css'), 'utf8')) && !/data-subject="/.test(fs.readFileSync(path.join(repo, 'public/css/question-bank.css'), 'utf8')), 'the stylesheet has no per-subject rules');
  const { page, context, errors } = await open(bio.base);
  await listed(page);
  equal(await page.$$eval('#qbSubjectTabs [role=tab]', (n) => n.map((x) => x.textContent).join('|')), 'All Subjects15|Biology15', 'tabs');
  equal((await page.textContent('#qbStats')).replace(/\s+/g, ' ').includes('15'), true, 'stats show 15');
  await page.click('#qbSubjectTabs [data-subject-ref="SUBJECT-BIOLOGY"]');
  equal(await page.$$eval('#qbTopicStrip .qb-topic-pill', (n) => n.map((x) => x.textContent).join('|')), 'All topics(15)|Cell Biology(15)', 'topic strip');
  await page.click('#qbTopicStrip .qb-topic-pill:has-text("Cell Biology")');
  equal(await page.$$eval('#qbTopicBanner a', (n) => n.map((a) => a.dataset.kind).sort().join()), 'interactive,study_clinic', 'resource actions');
  equal((await visibleIds(page)).length, 15, 'all 15 questions listed');
  equal(await page.$$eval('#qbSubtopicStrip .qb-topic-pill', (n) => n.map((x) => x.textContent).join('|')), 'All subtopics(15)|Mitochondria(5)|Nucleus(10)', 'subtopics with canonical titles');
  await page.click('#qbSubtopicStrip .qb-topic-pill:has-text("Mitochondria")');
  equal(await page.textContent('#qbResultCount'), '5 of 15 questions', 'the Mitochondria subtopic');
  await page.click('#qbSubtopicStrip .qb-topic-pill:has-text("All subtopics")');
  await page.fill('#qbSearch', 'mitochondria');
  await page.waitForTimeout(300);
  equal(await page.textContent('#qbResultCount'), '5 of 15 questions', 'search finds the five energy questions');
  await page.click('#qbClear');
  await page.click('.qb-collection-card:has-text("Energy questions")');
  equal(await page.textContent('#qbResultCount'), '5 of 15 questions', 'saved view');
  await page.locator('#qbResults .qb-qactions button').first().click();
  await page.waitForSelector('#qbStudyDialog[open] .qb-panel');
  assert((await page.textContent('#qbDialogBody')).includes('Step for question 3'), 'Study loads the Biology detail shard');
  assert(errors.length === 0, `page errors: ${errors.join('; ')}`);
  await context.close();
});

await browser.close();
live.server.close();
bio.server.close();
fs.rmSync(fixtureRoot, { recursive: true, force: true });

const failed = results.filter((r) => r.status === 'FAIL');
console.log(`\n${results.length - failed.length} PASS, ${failed.length} FAIL of ${results.length}`);
const report = JSON.stringify({ tool: 'tests/question_bank_runtime_browser.mjs', chromium: true, results }, null, 2) + '\n';
if (outFile) fs.writeFileSync(outFile, report);
process.exit(failed.length ? 1 : 0);
