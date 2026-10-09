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
    if(w===1280){
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
