// What an explorer does with the progress it keeps: it comes back after a reload without telling the host again, "Start over" forgets it,
// a page rebuilt from another spec starts fresh, and a kept list that no longer fits the page is dropped once without a reload loop.
//   node tests/explorer_persist.cjs PAGE_A.html PAGE_B.html   (B has the same path-to-be: it is copied over A to stand for a rebuilt page)
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const [, , fileA, fileB] = process.argv;
  const original = fs.readFileSync(fileA, 'utf8');
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1366, height: 854 } });
  const page = await context.newPage();
  const report = { consoleErrors: [] };
  page.on('console', (m) => { if (m.type() === 'error') report.consoleErrors.push(m.text()); });
  page.on('pageerror', (e) => report.consoleErrors.push(`PAGEERROR: ${e.message}`));
  await page.addInitScript(() => {
    window.__host = [];
    document.addEventListener('g9:evidence', (e) => window.__host.push(e.detail.type));
  });
  const ready = async () => { await page.goto('file://' + fileA); await page.waitForSelector('html[data-gx-ready]'); };
  const reload = async () => { await page.reload(); await page.waitForSelector('html[data-gx-ready]'); };
  const stage = () => page.evaluate(() => window.__gx.stage());
  const kept = () => page.evaluate(() => localStorage.getItem(window.__gx.progress.key));
  const spec = () => page.evaluate(() => window.__gx.spec);

  // a few steps in: the prediction made and locked in, a slider moved, a goal worked on
  const playSome = async () => {
    const sp = await spec();
    await page.locator('[data-gx-step=CONTEXT] [data-gx-continue]').click();
    await page.locator('input[name=gx-predict]').nth(sp.predict.correct).check();
    await page.locator('[data-gx-step=PREDICT] [data-gx-continue]').click();
    await page.evaluate(() => window.__gx.state.params && Object.keys(window.__gx.state.params).length);
    const free = await page.evaluate(() => window.__gx.model.free()[0]);
    const lat = await page.evaluate((id) => window.__gx.model.lattice(id), free);
    await page.$eval(`#gx-p-${free}`, (el, v) => { el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); }, lat[Math.floor(lat.length / 2)]);
    return { free, value: lat[Math.floor(lat.length / 2)] };
  };

  // 1. it comes back, quietly
  await ready();
  const moved = await playSome();
  report.before = { stage: await stage(), host: await page.evaluate(() => window.__host.slice()) };
  await reload();
  report.back = await page.evaluate((free) => ({
    stage: window.__gx.stage(), restored: window.__gx.progress.restored(), host: window.__host.slice(),
    slider: Number(document.querySelector(`#gx-p-${free}`).value), evidence: window.__gx.evidence().map((e) => [e.type, Boolean(e.replayed)]),
    unlocked: [...document.querySelectorAll('input[type=range]')].every((i) => !i.disabled),
  }), moved.free);
  report.back.expectedSlider = Number(moved.value);

  // 2. Start over forgets it
  await page.locator('[data-gx-restart]').click();
  await page.locator('[data-gx-restart]').click();
  await page.waitForSelector('html[data-gx-ready]');
  await page.waitForFunction(() => window.__gx.stage() === 'CONTEXT');
  report.startOver = { stage: await stage(), kept: await kept(), restored: await page.evaluate(() => window.__gx.progress.restored()) };

  // 3. a page rebuilt from another spec starts fresh
  await playSome();
  await page.waitForTimeout(400);
  report.beforeRebuild = { stage: await stage(), kept: Boolean(await kept()) };
  fs.writeFileSync(fileA, fs.readFileSync(fileB, 'utf8'));
  await reload();
  report.rebuilt = { stage: await stage(), restored: await page.evaluate(() => window.__gx.progress.restored()) };
  fs.writeFileSync(fileA, original);

  // 4. a kept list that does not fit this page is dropped, and the page starts from the top: a list that fails at once costs no reload, a list that
  //    fails after part of it was done costs one, and never a loop
  const countLoads = () => { const n = { loads: 0 }; page.on('framenavigated', (f) => { if (f === page.mainFrame()) n.loads += 1; }); return n; };
  await ready();
  await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
  await reload();
  await page.locator('[data-gx-step=CONTEXT] [data-gx-continue]').click();
  await page.waitForTimeout(400);
  const first = JSON.parse(await kept()).log[0];
  const outcome = async (list) => {
    await page.evaluate(([key, value]) => { localStorage.setItem(key, value); sessionStorage.clear(); }, [await page.evaluate(() => window.__gx.progress.key), JSON.stringify({ v: 1, log: list })]);
    const n = countLoads();
    await page.reload();
    await page.waitForSelector('html[data-gx-ready]');
    await page.waitForTimeout(900);
    return { stage: await stage(), restored: await page.evaluate(() => window.__gx.progress.restored()), kept: await kept(), loads: n.loads };
  };
  report.mismatchAtOnce = await outcome([['c', '#nothing-here', null, 1]]);
  report.mismatchAfterSome = await outcome([first, ['c', '#nothing-here', null, 2]]);

  await browser.close();
  process.stdout.write(JSON.stringify(report));
})().catch((e) => { console.error('EXPLORER PERSIST RUN FAILED', e.stack || e.message); process.exit(1); });
