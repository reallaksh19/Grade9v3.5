// Drives a generated explorer page through its whole route in a real browser and measures what the blueprint promises.
//   node tests/explorer_browser.cjs PAGE.html WIDTH HEIGHT [SHOTS_DIR]   -> one JSON report on stdout
// It needs only the page's own test hook (window.__gx), so it works on any explorer built by Shared/tools/explorer_build.py.
const { chromium } = require('playwright');

(async () => {
  const [, , file, w, h, shots] = process.argv;
  const width = Number(w), height = Number(h);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height } });
  const report = { viewport: { width, height }, consoleErrors: [], steps: [] };
  page.on('console', (m) => { if (m.type() === 'error') report.consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => report.consoleErrors.push(`PAGEERROR: ${e.message}`));
  await page.goto('file://' + file);
  await page.waitForSelector('html[data-gx-ready]');
  const shot = async (name) => { if (shots) await page.screenshot({ path: `${shots}/${name}.png` }); };

  const hook = (fn, arg) => page.evaluate(fn, arg);
  const stage = () => hook(() => window.__gx.stage());
  const slide = (id, value) => page.$eval(`#gx-p-${id}`, (el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); }, value);
  const spec = await hook(() => window.__gx.spec);
  const free = await hook(() => window.__gx.model.free());
  const main = free[0];
  const lat = await hook((id) => window.__gx.model.lattice(id), main);
  const pick = (k) => lat[Math.min(lat.length - 1, Math.max(0, Math.round(k * (lat.length - 1))))];

  // --- measurements that hold at every step
  const measure = async (label) => page.evaluate(([label, minText]) => {
    const out = { label };
    out.overflow = document.documentElement.scrollWidth - window.innerWidth;
    let smallest = Infinity;
    for (const svg of document.querySelectorAll('svg.gx-svg')) {
      const box = svg.getBoundingClientRect();
      if (!box.width || svg.closest('[hidden]')) continue;
      const vb = svg.viewBox.baseVal;
      const scale = box.width / vb.width;
      for (const t of svg.querySelectorAll('text')) {
        if (!t.textContent.trim() || t.closest('[style*="display: none"]')) continue;
        smallest = Math.min(smallest, parseFloat(getComputedStyle(t).fontSize) * scale);
      }
    }
    out.smallestText = smallest === Infinity ? null : smallest;
    let worst = Infinity, what = '';
    for (const el of document.querySelectorAll('button, a[href], input[type=range], label.gx-option, input[type=text]')) {
      const box = el.getBoundingClientRect();
      if (!box.width || !box.height || el.closest('[hidden]') || getComputedStyle(el).visibility === 'hidden') continue;
      if (box.height < worst) { worst = box.height; what = (el.dataset && Object.keys(el.dataset)[0]) || el.tagName; }
    }
    out.smallestTarget = worst === Infinity ? null : worst;
    out.smallestTargetIs = what;
    return out;
  }, [label, 14]);
  const note = async (label) => {
    const row = await measure(label);
    row.continueVisible = await page.evaluate(() => {
      const button = document.querySelector('[data-gx-step][data-state=current] [data-gx-continue]');
      if (!button) return null;
      const box = button.getBoundingClientRect();
      return box.top >= -1 && box.bottom <= window.innerHeight + 1;
    });
    report.steps.push(row);
  };

  // --- before the prediction: nothing to play with
  report.before = await page.evaluate(() => ({
    slidersDisabled: [...document.querySelectorAll('input[type=range]')].every((i) => i.disabled),
    lockNote: !document.querySelector('[data-gx-lock-note]').hidden,
    manipulateElementsShown: window.__gx.spec.scene.elements.filter((e) => e.reveal === 'manipulate' && window.__gx.visible(e.id)).length,
    contradictElementsShown: window.__gx.spec.scene.elements.filter((e) => e.reveal === 'contradict' && window.__gx.visible(e.id)).length,
    deconstructElementsShown: window.__gx.spec.scene.elements.filter((e) => e.reveal === 'deconstruct' && window.__gx.visible(e.id)).length,
    readoutsShown: [...document.querySelectorAll('.gx-ro')].filter((r) => !r.hidden).length,
    curveDrawn: [...document.querySelectorAll('#gx-graph-svg path.gx-curve')].some((p) => (p.getAttribute('d') || '').length > 0),
    stage: window.__gx.stage(),
    routeCardsShown: [...document.querySelectorAll('[data-gx-step]')].filter((c) => !c.hidden).length,
  }));
  await shot('01-context');
  await note('context');

  const cont = async (id) => {
    const button = page.locator(`[data-gx-step="${id}"] [data-gx-continue]`);
    if (await button.isDisabled()) throw new Error(`the continue button of ${id} is disabled`);
    await button.click();
  };
  const disabled = (id) => page.locator(`[data-gx-step="${id}"] [data-gx-continue]`).isDisabled();

  await cont('CONTEXT');
  report.gates = { predictNeedsAChoice: await disabled('PREDICT') };
  await page.locator('input[name=gx-predict]').nth(spec.predict.correct).check();
  report.gates.predictAfterChoice = !(await disabled('PREDICT'));
  await shot('02-predict');
  await note('predict');
  await cont('PREDICT');
  report.after = await page.evaluate(() => ({
    slidersEnabled: [...document.querySelectorAll('input[type=range]')].every((i) => !i.disabled),
    manipulateElementsShown: window.__gx.spec.scene.elements.filter((e) => e.reveal === 'manipulate' && window.__gx.visible(e.id)).length,
    readoutsShown: [...document.querySelectorAll('.gx-ro')].filter((r) => !r.hidden).length,
    curveDrawn: [...document.querySelectorAll('#gx-graph-svg path.gx-curve')].some((p) => (p.getAttribute('d') || '').length > 0),
  }));

  // --- manipulate: the goals gate the way on; the hint comes before the answer
  report.gates.manipulateNeedsGoals = await disabled('MANIPULATE');
  report.gates.showMeNeedsTheHint = await page.locator('[data-gx-step=MANIPULATE] [data-gx-goal="0"] [data-gx-show]').isDisabled();
  await page.locator('[data-gx-step=MANIPULATE] [data-gx-goal="0"] [data-gx-hint]').click();
  report.gates.showMeAfterHint = !(await page.locator('[data-gx-step=MANIPULATE] [data-gx-goal="0"] [data-gx-show]').isDisabled());
  const goals = spec.manipulate.goals;
  for (let i = 0; i < goals.length; i += 1) {
    const item = page.locator(`[data-gx-step=MANIPULATE] [data-gx-goal="${i}"]`);
    if ((await item.getAttribute('data-met')) !== 'true') {
      await item.locator('[data-gx-hint]').click().catch(() => {});
      await item.locator('[data-gx-show]').click();
    }
  }
  await note('manipulate');
  await shot('03-manipulate');
  report.after.trailDots = await page.evaluate(() => document.querySelectorAll('#gx-graph-svg .gx-trail circle').length);

  // --- the drawing is the model: every element sits where the numbers put it, at every position tried
  let worstGeometry = 0;
  let worstOracle = 0;
  for (const k of [0, 0.25, 0.5, 0.75, 1]) {
    await slide(main, pick(k));
    const r = await page.evaluate(() => {
      const g = window.__gx.geometry();
      let worst = 0;
      for (const item of Object.values(g)) {
        const got = item.x !== undefined ? [item.x, item.y] : [item.x1, item.y1, item.x2, item.y2];
        const want = item.expect;
        got.forEach((v, i) => { worst = Math.max(worst, Math.abs(v - want[i])); });
      }
      const env = window.__gx.values();
      let oracle = 0;
      for (const o of window.__gx.spec.oracles) {
        const a = window.GXModel.evaluate(o.left, env, window.__gx.model.resolver(window.__gx.state.params));
        const b = window.GXModel.evaluate(o.right, env, window.__gx.model.resolver(window.__gx.state.params));
        oracle = Math.max(oracle, Math.abs(a - b) / Math.max(1, Math.abs(a), Math.abs(b)));
      }
      return { worst, oracle };
    });
    worstGeometry = Math.max(worstGeometry, r.worst);
    worstOracle = Math.max(worstOracle, r.oracle);
  }
  report.geometry = { worstPixelError: worstGeometry, worstOracleError: worstOracle };
  await cont('MANIPULATE');

  // --- observe: judge each statement by the model's own verdict
  const truths = await hook(() => window.__gx.claims());
  const statements = page.locator('[data-gx-statement]');
  for (let i = 0; i < truths.length; i += 1) await statements.nth(i).locator(truths[i] === 'always' ? '[data-gx-agree]' : '[data-gx-disagree]').click();
  report.recall = await page.locator('[data-gx-recall]').isVisible();
  await shot('04-observe');
  await note('observe');
  // narrower than the breakpoint the pictures and the sliders are pinned while the route scrolls
  report.pinned = await page.evaluate(async () => {
    window.scrollTo(0, 700);
    await new Promise((r) => setTimeout(r, 120));
    const views = document.querySelector('.gx-views').getBoundingClientRect();
    const controls = document.querySelector('.gx-controls').getBoundingClientRect();
    const out = { scrolled: window.scrollY, viewsTop: views.top, viewsBottom: views.bottom, controlsTop: controls.top, controlsBottom: controls.bottom };
    window.scrollTo(0, 0);
    return out;
  });
  await cont('OBSERVE');

  // --- contradict: the tempting model appears only when imposed
  report.contradict = { shownBefore: await hook(() => window.__gx.spec.scene.elements.some((e) => e.reveal === 'contradict' && window.__gx.visible(e.id))) };
  await page.locator('[data-gx-impose]').click();
  report.contradict.shownAfter = await hook(() => window.__gx.spec.scene.elements.some((e) => e.reveal === 'contradict' && window.__gx.visible(e.id)));
  report.contradict.ghostDrawn = await page.evaluate(() => (document.querySelector('#gx-graph-svg path.gx-r-wrong')?.getAttribute('d') || '').length > 0);
  await page.locator('[data-gx-step=CONTRADICT] [data-gx-goal="0"] [data-gx-hint]').click();
  await page.locator('[data-gx-step=CONTRADICT] [data-gx-goal="0"] [data-gx-show]').click();
  report.gates.contradictNeedsTheGoal = false;
  await shot('05-contradict');
  await note('contradict');
  await cont('CONTRADICT');

  // --- deconstruct: one cause at a time, in the order written
  const steps = spec.deconstruct.steps;
  const seen = [];
  for (let i = 0; i < steps.length; i += 1) {
    if (i > 0) await page.locator('[data-gx-step=DECONSTRUCT] [data-gx-more]').click();
    if (steps[i].ask) {
      // the next cause is not offered until the question about this one is answered
      const waits = i < steps.length - 1 ? await page.locator('[data-gx-step=DECONSTRUCT] [data-gx-more]').isDisabled() : true;
      report.gates.deconstructWaitsForTheQuestion = (report.gates.deconstructWaitsForTheQuestion ?? true) && waits;
      await page.locator(`[data-gx-dstep="${i}"] [data-gx-ask-opt="${steps[i].ask.correct}"]`).click();
    }
    seen.push(await hook(() => window.__gx.spec.scene.elements.filter((e) => e.reveal === 'deconstruct' && window.__gx.visible(e.id)).map((e) => e.id)));
  }
  report.deconstruct = { revealedAfterEachStep: seen };
  await shot('06-deconstruct');
  await note('deconstruct');
  await cont('DECONSTRUCT');

  // --- reconstruct: the equation is tested at positions the learner chooses
  const rsteps = spec.reconstruct.steps.length;
  for (let i = 1; i < rsteps; i += 1) await page.locator('[data-gx-step=RECONSTRUCT] [data-gx-more]').click();
  report.gates.reconstructNeedsTesting = await disabled('RECONSTRUCT');
  await slide(main, pick(0.2));
  await slide(main, pick(0.7));
  report.reconstruct = { equationShown: await page.locator('[data-gx-equation]').isVisible(), verdict: await page.locator('[data-gx-eq-ok]').textContent() };
  await shot('07-reconstruct');
  await note('reconstruct');
  await cont('RECONSTRUCT');

  // --- invariant: five different positions
  for (const k of [0.1, 0.3, 0.5, 0.7, 0.9]) await slide(main, pick(k));
  report.invariant = { verdicts: await page.locator('[data-gx-inv-ok]').allTextContents() };
  await shot('08-invariant');
  await note('invariant');
  await cont('INVARIANT');

  // --- boundary: go to each case, judge it by the model
  const cases = spec.boundary.cases;
  for (let i = 0; i < cases.length; i += 1) {
    const item = page.locator(`[data-gx-case="${i}"]`);
    await item.locator('[data-gx-go]').click();
    await item.locator(cases[i].expect === 'holds' ? '[data-gx-yes]' : '[data-gx-no]').click();
  }
  report.boundary = { takeaway: await page.locator('.gx-takeaway').isVisible() };
  await shot('09-boundary');
  await note('boundary');
  await cont('BOUNDARY');

  // --- fade: three levels, less each time
  const answerOf = (task) => page.evaluate((t) => window.__gx.model.evaluate(t.answer, window.__gx.model.withSet(t.set, window.__gx.model.initial())), task);
  report.fade = { levels: [] };
  for (let i = 0; i < spec.fade.length; i += 1) {
    const item = page.locator(`[data-gx-step=FADE] [data-gx-task="${i}"]`);
    const level = await page.evaluate(() => ({
      graphHidden: document.querySelector('[data-gx-view=graph]').classList.contains('gx-faded'),
      mechanismShown: window.__gx.spec.scene.elements.filter((e) => e.reveal === 'deconstruct' && window.__gx.visible(e.id)).length,
      resultShown: window.__gx.spec.scene.elements.filter((e) => e.role === 'result' && window.__gx.visible(e.id)).length,
      numbersHidden: [...document.querySelectorAll('.gx-ro[data-gx-reveal=manipulate] output')].every((o) => o.textContent === '—'),
      labelsShown: [...document.querySelectorAll('#gx-scene-svg .gx-lab')].filter((t) => t.textContent && t.closest('.gx-el').style.display !== 'none').length,
      slidersDisabled: [...document.querySelectorAll('input[type=range]')].every((x) => x.disabled),
    }));
    report.fade.levels.push(level);
    if (i === 0) {
      await item.locator('[data-gx-answer]').fill('not a number');
      await item.locator('[data-gx-check]').click();
      report.fade.asksForANumber = await item.locator('.gx-feedback').textContent();
    }
    await item.locator('[data-gx-answer]').fill(String(await answerOf(spec.fade[i])));
    await item.locator('[data-gx-check]').click();
    await shot(`10-fade-${i}`);
  }
  await note('fade');
  await cont('FADE');

  // --- transfer: the explorer is closed; a wrong answer twice reveals the answer
  report.transfer = { stageHidden: !(await page.locator('.gx-stage').isVisible()) };
  const tasks = page.locator('[data-gx-step=TRANSFER] [data-gx-task]');
  for (let i = 0; i < spec.transfer.length; i += 1) {
    const item = tasks.nth(i);
    if (i === 0) {
      for (let attempt = 0; attempt < 2; attempt += 1) {
        await item.locator('[data-gx-answer]').fill('0.001');
        await item.locator('[data-gx-check]').click();
      }
      report.transfer.revealedAfterTwoWrong = (await item.locator('.gx-feedback').textContent()).includes('The answer is');
    } else {
      await item.locator('[data-gx-answer]').fill(String(await answerOf(spec.transfer[i])));
      await item.locator('[data-gx-check]').click();
    }
  }
  await shot('11-transfer');
  await note('transfer');
  await cont('TRANSFER');
  report.done = { visible: await page.locator('#gx-done').isVisible(), stageBack: await page.locator('.gx-stage').isVisible(),
                  summary: await page.locator('[data-gx-summary-list] li').allTextContents() };
  await shot('12-done');
  await note('done');
  report.evidence = await hook(() => window.__gx.evidence().map((e) => e.type));
  report.fadeResults = await hook(() => window.__gx.state.fade.results.map((r) => r.correct));
  report.transferResults = await hook(() => window.__gx.state.transfer.results.map((r) => r.correct));

  // --- every control and picture has a name a reader who cannot see it can use
  report.a11y = await page.evaluate(() => {
    const name = (el) => (el.getAttribute('aria-label') || (el.labels && el.labels[0] && el.labels[0].textContent) || el.textContent || el.getAttribute('title') || '').trim();
    const unnamed = [...document.querySelectorAll('button, a[href], input, select, textarea')].filter((el) => !name(el)).map((el) => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}`);
    const pictures = [...document.querySelectorAll('svg.gx-svg')].map((svg) => ({ role: svg.getAttribute('role'), named: Boolean(svg.getAttribute('aria-labelledby') && document.getElementById(svg.getAttribute('aria-labelledby').split(' ')[0])), described: Boolean(svg.querySelector('desc')) }));
    const liveOutputs = [...document.querySelectorAll('output')].filter((o) => o.getAttribute('aria-live') !== 'off').length;
    return { unnamed, pictures, liveOutputs, lang: document.documentElement.lang, landmarks: ['header', 'main', 'aside'].map((t) => document.querySelectorAll(t).length), headings: document.querySelectorAll('h1').length };
  });

  // --- layout at the end of the route and the head block
  report.layout = await page.evaluate(() => {
    const head = document.querySelector('.gx-head').getBoundingClientRect();
    const route = document.querySelector('.gx-route');
    const style = getComputedStyle(route);
    return { headHeight: head.height, routePosition: style.position, routeOverflowY: style.overflowY, mainDisplay: getComputedStyle(document.querySelector('.gx-main')).display };
  });
  await browser.close();
  process.stdout.write(JSON.stringify(report));
})().catch((e) => { console.error('EXPLORER BROWSER RUN FAILED', e.stack || e.message); process.exit(1); });
