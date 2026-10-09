#!/usr/bin/env node
/** IMO-R1: real generated TEST Core2A attempt/solution -> exact Core1A repair. */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

if(!process.argv[2])throw new Error('Pass the rendered TEST product directory');
const folder=path.resolve(process.argv[2]),outDir=path.join(folder,'r1-browser-evidence');
fs.mkdirSync(outDir,{recursive:true});
for(const name of ['core1a.html','core2a.html'])
  if(!fs.existsSync(path.join(folder,name)))throw new Error('Renderer omitted '+name);
const report={schema:'imo-r1-authored-core2a-repair-browser/v1',product:'TEST_CANDIDATE',
  source_core2_admitted:false,owner_approved:false,cryptographic_answer_isolation:false,
  screen_reader_manual:'NOT_RUN',independent_learner_comprehension:'NOT_RUN',viewports:[],failures:[]};
const assert=(ok,msg)=>{if(!ok)report.failures.push(msg)};
const browser=await chromium.launch({headless:true});
try{
  for(const w of [320,390,768,1280]){
    const context=await browser.newContext({viewport:{width:w,height:840}});
    const page=await context.newPage();const jsErrors=[];
    page.on('pageerror',e=>jsErrors.push(e.message));
    await page.goto(pathToFileURL(path.join(folder,'core2a.html')).href,{waitUntil:'load'});
    const article=page.locator('article[data-g9-role="CORE2A"]');
    const widths=await page.evaluate(()=>({
      client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,
      test:document.documentElement.dataset.g9Test==='sandbox-draft'
    }));
    const text=await article.innerText();
    assert(await article.count()===1,w+': exactly one authored Core2A article required');
    assert(widths.test,w+': missing TEST banner');
    assert(text.includes('4^(2u+1)')&&text.includes('16^u+192'),w+': given equation missing');
    assert(!/SOF-IMO-G09/.test(text),w+': authentic source label leaked');
    assert(widths.scroll<=widths.client,w+': horizontal page overflow '+(widths.scroll-widths.client));
    assert(!jsErrors.length,w+': page errors '+jsErrors.join(';'));
    // A Core2A question starts with zero visible hints. The first is genuinely
    // optional and its disclosure must count as assisted, not independent.
    const initialHints=await article.locator('[data-g9-ladder] [data-g9-rung]').count();
    const firstButton=article.locator('[data-g9-next-rung]').first();
    const assistanceNotice=article.locator('[data-g9-assistance-status]').first();
    assert(initialHints===0,w+': H1 must not be disclosed before request');
    assert(await firstButton.innerText()==='Show hint 1',w+': first hint is not opt-in');
    assert(await assistanceNotice.isHidden(),w+': unexplained assisted-attempt notice');
    const safeFigures=article.locator('figure[data-g9-stage="PRE_ATTEMPT"]');
    assert(await safeFigures.count()===1,w+': original authored stem needs one attempt-safe figure');
    const leakedFigures=await article.locator('figure[data-g9-stage="PRE_ATTEMPT"]').evaluateAll(
      nodes=>nodes.map(el=>el.outerHTML).filter(html=>/u=3\/2|t=64|4t=t|solution/i.test(html)));
    assert(leakedFigures.length===0,w+': preattempt visual leaks answer or factor relation');
    report.viewports.push({width:w,...widths,errors:jsErrors});
    await page.screenshot({path:path.join(outDir,'attempt-'+w+'.png'),fullPage:true});
    if(w===390){
      await page.addStyleTag({content:'html{font-size:200%!important}'});
      const zoom=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));
      assert(zoom.scroll<=zoom.client,'200% text overflow '+(zoom.scroll-zoom.client));
      report.zoom200=zoom;
      await page.screenshot({path:path.join(outDir,'attempt-390-200pct.png'),fullPage:true});
    }
    if(w===768){
      // A hint requested AFTER a committed attempt is review support. It may
      // not retroactively relabel the initial unassisted attempt.
      const input=article.locator('[data-g9-attempt-box] textarea').first();
      await input.fill('I independently attempted the model before seeing help.');
      await article.locator('[data-g9-commit]').first().click();
      await firstButton.click();
      const postStatus=await article.getAttribute('data-g9-post-attempt-hints');
      const retroactive=await article.getAttribute('data-g9-assisted');
      const wording=await assistanceNotice.innerText();
      assert(postStatus==='1'&&!retroactive&&wording.includes('does not retroactively'),
        'post-commit help retroactively misclassified an independent initial attempt');
      report.postCommitReview={postStatus,retroactive,wording,
        trustedAssessment:false};
    }
    if(w===1280){
      await firstButton.click();
      const didReveal=await article.locator('[data-g9-ladder] [data-g9-rung]').count()===1;
      const assisted=await article.getAttribute('data-g9-assisted');
      const assistedKinds=await article.getAttribute('data-g9-assistance');
      const notice=await assistanceNotice.isVisible();
      assert(didReveal&&assisted==='1'&&assistedKinds?.includes('HINT_LADDER')&&notice,
        'first optional hint did not label this as an assisted attempt');
      report.assistedHint={didReveal,assisted,assistedKinds,notice,
        noIndependentMasteryClaim:true};
      const summary=article.locator('summary').filter({hasText:'Reasoning route and full solution'}).first();
      assert(await summary.count()===1,'missing accessible full-solution control');
      if(await summary.count()){
        const initial=!(await summary.evaluate(el=>el.parentElement.open));
        await summary.focus();await summary.press('Enter');
        const blocked=!(await summary.evaluate(el=>el.parentElement.open));
        const noPayload=await summary.evaluate(el=>el.parentElement.querySelector('[data-g9-payload-slot]')?.children.length===0);
        const attempt=article.locator('[data-g9-attempt-box] textarea').first();
        assert(await attempt.count()===1,'missing real free-response input');
        if(await attempt.count()){
          await attempt.fill('Synthetic QA response: I would rewrite positive-base powers using a shared variable.');
          await article.locator('[data-g9-commit]').first().click();
        }
        const released=await summary.isVisible();
        await summary.focus();await summary.press('Enter');
        const opened=await summary.evaluate(el=>el.parentElement.open);
        const routeText=await article.locator('[data-g9-block="reasoning_route"]').first().innerText({timeout:3000});
        assert(routeText.includes('4t')&&routeText.includes('64')&&routeText.includes('256'),
          'postcommit route loses factor, answer or exact reverse-check');
        const link=article.locator('a[data-g9-repair-ref="TC-02"]').first();
        const href=await link.getAttribute('href');
        assert(href?.startsWith('core1a.html#CU-'),'repair does not target owning Core1A construction');
        assert(initial&&blocked&&noPayload&&released&&opened,'typed commitment must gate then release solution');
        report.attemptGate={initial,blocked,noPayload,released,opened,repairHref:href};
        await page.screenshot({path:path.join(outDir,'post-attempt-1280.png'),fullPage:true});
        if(href){
          await Promise.all([page.waitForURL(/core1a\.html#CU-/),link.click()]);
          const target=await page.evaluate(()=>({onCore1A:location.pathname.endsWith('core1a.html'),
            id:decodeURIComponent(location.hash.slice(1)),
            found:!!document.getElementById(decodeURIComponent(location.hash.slice(1)))}));
          assert(target.onCore1A&&target.found,'repair anchor target missing');
          report.repair=target;
          // This link must lead to a neutral-law gate, not expose the previous
          // question's worked answer as a hint.
          const check=page.locator('article[data-g9-role="CORE1A"] [data-g9-concept-check]').first();
          const guided=page.locator('article[data-g9-role="CORE1A"] [data-g9-concept-target]').first();
          assert(await check.count()===1,'Core1A missing concept-first checkpoint');
          assert(await guided.isHidden(),'guided Core1A worked solution visible before concept check');
          const prompt=await check.innerText();
          assert(prompt.includes('2⁴')&&prompt.includes('5⁽ⁿ⁺¹⁾'),
            'Core1A did not start with unrelated neutral index-law examples');
          await check.locator('[data-g9-concept-option][value="ADD"]').check();
          await check.locator('[data-g9-concept-reason]').fill(
            'An exponent means multiply by another factor of the base.');
          await check.locator('[data-g9-concept-commit]').click();
          const wrongBlocked=await guided.isHidden();
          await check.locator('[data-g9-concept-option][value="FACTOR"]').check();
          await check.locator('[data-g9-concept-reason]').fill('Just because');
          await check.locator('[data-g9-concept-commit]').click();
          const reasonBlocked=await guided.isHidden();
          await check.locator('[data-g9-concept-reason]').fill(
            'An extra exponent multiplies the existing power by a factor equal to its base.');
          await check.locator('[data-g9-concept-commit]').click();
          const guidedVisible=await guided.isVisible();
          const formative=await page.locator('article[data-g9-role="CORE1A"]').first()
            .getAttribute('data-g9-concept-check-completed');
          assert(wrongBlocked&&reasonBlocked&&guidedVisible&&formative==='formative_only',
            'Core1A must check choice+reason before revealing guided teaching');
          report.conceptCheck={wrongBlocked,reasonBlocked,guidedVisible,formative};
          await page.screenshot({path:path.join(outDir,'core1a-repair-1280.png'),fullPage:true});
        }
      }
    }
    await context.close();
  }
}finally{await browser.close();}
fs.writeFileSync(path.join(outDir,'report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
if(report.failures.length)process.exitCode=1;
