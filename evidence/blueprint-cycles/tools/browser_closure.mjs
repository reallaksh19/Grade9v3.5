// Actual saved-page review: help, commitment, solution, diagnostic, reload,
// opened references, readable staged figures, and the linked print closure.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(path.resolve(process.env.NODE_PATH,'package.json'));
const {chromium}=require('playwright');
const root=process.cwd(), out=path.join(root,'evidence/blueprint-cycles/closure-20261005');
const issues=[32,31,34,33,36,35,38,37];
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const server=http.createServer((req,res)=>{
  const requested=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!requested.startsWith(root+path.sep)||!fs.existsSync(requested)){res.writeHead(404);res.end();return}
  res.setHeader('Content-Type',requested.endsWith('.html')?'text/html; charset=utf-8':requested.endsWith('.js')?'text/javascript':requested.endsWith('.css')?'text/css':'application/octet-stream');
  res.end(fs.readFileSync(requested));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true});
const results=[];
try {
 for(const issue of issues){
  const directory=path.join(root,`evidence/blueprint-cycles/ISS${issue}`);
  const bank=JSON.parse(fs.readFileSync(path.join(directory,'inputs/owner.bank.json')));
  const binding={};
  for(const file of ['rendered/core1a.html','rendered/core2.html','rendered/css/modern-learner.css','rendered/css/tablet-12-7.css','rendered/js/display-controls.js','rendered/js/site-header.js','inputs/owner.bank.json','inputs/package.v1.json'])binding[file]=hash(path.join(directory,file));
  const failures=[], checks=[];
  const context=await browser.newContext({viewport:{width:390,height:844}});
  const page=await context.newPage();
  page.on('pageerror',e=>failures.push('page error: '+e.message));
  const url=base+`/evidence/blueprint-cycles/ISS${issue}/rendered/core2.html`;
  await page.goto(url);
  for(const q of bank.questions){
   const a=page.locator(`article[data-g9-unit="${q.id}"]`);
   const gate=a.locator('details[data-requires-attempt]').first();
   await gate.locator('summary').click();
   if(await gate.getAttribute('open')!==null)failures.push(q.id+': blank response opened protected solution');
   if(await a.locator('[data-g9-learning-repair]').count())failures.push(q.id+': diagnostic materialized before commitment');
   const hints=a.locator('details[data-g9-secondary="core2-hints"]');
   if(await hints.count())await hints.locator('summary').click();
   const next=a.locator('[data-g9-next-rung]');
   while(await next.count() && await next.isEnabled())await next.click();
   if(await gate.getAttribute('open')!==null)failures.push(q.id+': help opened the solution');
   const field=a.locator('textarea[data-g9-attempt]').first();
   if(await field.count())await field.fill('Browser test commitment; not a learner mastery result.');
   else await a.locator('[data-g9-paper]').check();
   await a.locator('[data-g9-commit]').first().click();
   if(await a.getAttribute('data-attempted')!=='1')failures.push(q.id+': commitment did not unlock the solution');
   await gate.locator('summary').click();
   const diagnostic=a.locator('[data-g9-learning-repair]');
   if(await diagnostic.count()!==1)failures.push(q.id+': missing post-attempt diagnostic');
   else{
    const feedback=diagnostic.locator('[data-g9-probe-feedback]');
    await diagnostic.locator('[data-g9-probe-compare]').click();
    if(await feedback.isVisible())failures.push(q.id+': blank diagnostic response unlocked feedback');
    await diagnostic.locator('[data-g9-probe-response]').fill('Changed-case explanation for browser testing.');
    await diagnostic.locator('[data-g9-probe-compare]').click();
    if(!await feedback.isVisible())failures.push(q.id+': committed diagnostic did not show comparison');
   }
   checks.push({question:q.id,states:['INITIAL_PROTECTED','HELP','COMMITTED','SOLUTION','DIAGNOSTIC'],claim:'Interaction execution, not response grading or learning validation'});
  }
  await page.reload();
  const restored=await page.locator('article[data-attempted="1"]').count();
  if(restored!==bank.questions.length)failures.push('commitment restoration: '+restored+'/'+bank.questions.length);
  await page.goto(base+`/evidence/blueprint-cycles/ISS${issue}/rendered/core1a.html`);
  await page.evaluate(()=>document.querySelectorAll('details.g9-secondary-disclosure').forEach(d=>d.open=true));
  await page.keyboard.press('Tab');
  const opened=await page.evaluate(()=>{
   const failures=[];
   const visible=e=>e.checkVisibility({visibilityProperty:true})&&e.getBoundingClientRect().width>0;
   const controls=[...document.querySelectorAll('a[href],button,summary,textarea,input,select,[tabindex="0"]')].filter(e=>visible(e)&&!e.disabled&&e.getAttribute('aria-disabled')!=='true');
   for(const e of controls){e.focus({preventScroll:true});const style=getComputedStyle(e);if(document.activeElement!==e||(!parseFloat(style.outlineWidth)&&style.boxShadow==='none'))failures.push(e.tagName+' '+e.textContent.trim().slice(0,30));}
   const labels=[...document.querySelectorAll('svg text')].filter(visible);
   const fontSizes=labels.map(t=>{const m=t.getScreenCTM();return parseFloat(getComputedStyle(t).fontSize)*Math.hypot(m.a,m.b)});
   return {focusCandidates:controls.length,focusFailures:failures,pageOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,smallestFigureText:Math.min(...fontSizes)};
  });
  if(opened.focusFailures.length)failures.push('opened reference focus: '+opened.focusFailures.join(', '));
  if(opened.pageOverflow>0)failures.push('opened reference page overflow: '+opened.pageOverflow);
  if(opened.smallestFigureText<13.95)failures.push('opened figure text below floor: '+opened.smallestFigureText);
  // Exact saved pages own these local PDFs; no learner publication is performed.
  await page.setViewportSize({width:1280,height:900});
  for(const role of ['core1a','core2']){
    await page.goto(base+`/evidence/blueprint-cycles/ISS${issue}/rendered/${role}.html`);
    await page.evaluate(()=>{
      for(const a of document.querySelectorAll('article[data-g9-unit]')){
        const paper=a.querySelector('[data-g9-paper]');const field=a.querySelector('[data-g9-attempt]');
        if(paper)paper.checked=true;else if(field)field.value='Print review';
        a.querySelector('[data-g9-commit]')?.click();
        for(const input of a.querySelectorAll('textarea,input[type="text"]'))input.value='';
      }
      document.querySelectorAll('details').forEach(d=>d.open=true);
    });
    await page.pdf({path:path.join(directory,'rendered',role+'.pdf'),format:'A4',printBackground:true,margin:{top:'12mm',bottom:'12mm',left:'10mm',right:'10mm'}});
  }
  for(const [file,expected] of Object.entries(binding))if(hash(path.join(directory,file))!==expected)failures.push('tested source changed: '+file);
  results.push({issue,status:failures.length?'FAIL':'PASS',binding,questionStates:checks,reloadRestored:restored,openedReferences:opened,pdfs:{'core1a.pdf':hash(path.join(directory,'rendered/core1a.pdf')),'core2.pdf':hash(path.join(directory,'rendered/core2.pdf'))},failures});
  await context.close();
  console.log(`ISS${issue}: ${failures.length?'FAIL':'PASS'}; ten interaction traces; opened focus ${opened.focusCandidates}; ${failures.join('; ')}`);
 }
}finally{await browser.close();server.close();}
fs.writeFileSync(path.join(out,'interaction-closure.json'),JSON.stringify({schema:'issue29-browser-closure/v1',observed:'NEW_HTTP_CHROMIUM_EXECUTION',results,claim:'Saved-byte interaction and packaging checks; no independent learner/academic certification.'},null,2)+'\n');
process.exitCode=results.every(r=>r.status==='PASS')?0:1;
