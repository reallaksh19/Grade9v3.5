#!/usr/bin/env node
/** Offline Playwright falsifiers for the three noncanonical Core1B golden journeys. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

const ROOT=process.cwd();
const dir=path.join(ROOT,'tests','fixtures','core1b-goldens');
const html=path.join(dir,'student-practice.v2.html');
const filenames=['01-consecutive.json','02-algebra.json','03-motion.json'];
const fixtures=filenames.map(n=>JSON.parse(fs.readFileSync(path.join(dir,n),'utf8')));
const fail=[];
const check=(ok,message)=>{if(!ok)fail.push(message)};
const norm=s=>String(s).replace(/[“”]/g,'"').replace(/[’]/g,"'").replace(/[^\p{L}\p{N}]+/gu,' ').trim().toLowerCase();
const browser=await chromium.launch({headless:true});
const checked=[];
try {
 for(let i=0;i<fixtures.length;i++){
  const golden=fixtures[i];
  for(const width of [320,390,768,1280]){
   const ctx=await browser.newContext({viewport:{width,height:800}});
   const page=await ctx.newPage();
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(pathToFileURL(html).href);
   await page.locator('#tab-'+i).click();
   const live=await page.evaluate(index=>{
     const c=lessons[index];
     return {id:c.id,title:c.title,situation:c.situation,question:c.question,
       diagnostics:c.diagnostics,reference:c.reference,warrants:c.warrants,
       boundary:c.boundary,boundaryAnswer:c.boundaryAnswer};
   },i);
   const expected=golden.learner;
   check(live.id===golden.id,`${golden.id}@${width}: case ID mismatch`);
   check(live.title===golden.title,`${golden.id}@${width}: title mismatch`);
   for(const [shown,ref] of [['situation','situation'],['question','question']]){
    check(norm(live[shown])===norm(expected[ref]),`${golden.id}@${width}: ${shown} differs from golden`);
   }
   for(const [shown,ref] of [['diagnostics','diagnostics'],['reference','reference'],
     ['warrants','warrants'],['boundary','boundary_question'],['boundaryAnswer','boundary_answer']]){
    check(JSON.stringify(live[shown])===JSON.stringify(expected[ref]),
      `${golden.id}@${width}: protected ${shown} differs from golden`);
   }
   check(!(await page.locator('#repairStage').isVisible()),`${golden.id}@${width}: preattempt diagnosis visible`);
   check(!(await page.locator('#mainReferenceArea').isVisible()),`${golden.id}@${width}: early reference visible`);
   check(!(await page.locator('#boundaryStage').isVisible()),`${golden.id}@${width}: early boundary visible`);
   await page.locator('#firstResponse').fill('  ');
   check(await page.locator('#commitFirst').isDisabled(),`${golden.id}@${width}: whitespace committed`);
   await page.locator('#firstResponse').fill('33');
   check(await page.locator('#commitFirst').isEnabled(),`${golden.id}@${width}: short answer blocked`);
   await page.locator('#commitFirst').click();
   check(await page.locator('#repairStage').isVisible(),`${golden.id}@${width}: diagnosis not opened`);
   check(!(await page.locator('#mainReferenceArea').isVisible()),`${golden.id}@${width}: reference leaked after first attempt`);
   check(!(await page.locator('#boundaryStage').isVisible()),`${golden.id}@${width}: independent boundary leaked before repair`);
   check((await page.locator('#hints li').count())===0,`${golden.id}@${width}: hint prematurely shown`);
   await page.locator('#nextHint').click();
   check((await page.locator('#hints li').count())===1,`${golden.id}@${width}: first hint not progressive`);
   await page.locator('#repairResponse').fill('The initial justification missed an important warrant.');
   await page.locator('#commitRepair').click();
   check(await page.locator('#showReference').isVisible(),`${golden.id}@${width}: Answer ${i+1} not discoverable`);
   check(!(await page.locator('#mainReferenceArea').isVisible()),`${golden.id}@${width}: reference auto-opened before action`);
   check(!(await page.locator('#boundaryReferenceArea').isVisible()),`${golden.id}@${width}: boundary answer leaked by repair`);
   await page.locator('#showReference').click();
   check(await page.locator('#mainReferenceArea').isVisible(),`${golden.id}@${width}: Answer ${i+1} did not open`);
   check((await page.locator('#answerTitle').innerText()).includes(`Answer ${i+1}`),`${golden.id}@${width}: answer label missing`);
   check(!(await page.locator('#boundaryReferenceArea').isVisible()),`${golden.id}@${width}: reference opened boundary`);
   await page.locator('#boundaryResponse').fill('   ');
   check(await page.locator('#commitBoundary').isDisabled(),`${golden.id}@${width}: blank boundary accepted`);
   await page.locator('#boundaryResponse').fill('My new attempt');
   await page.locator('#commitBoundary').click();
   check(await page.locator('#boundaryReferenceArea').isVisible(),`${golden.id}@${width}: boundary still hidden after own attempt`);
   if(width===390){
    await page.addStyleTag({content:'html{font-size:200%!important}'});
   }
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth);
   check(!overflow,`${golden.id}@${width}: responsive/200pct horizontal overflow`);
   check(errors.length===0,`${golden.id}@${width}: JS errors ${errors.join('; ')}`);
   await ctx.close();
   checked.push(`${golden.id}@${width}`);
  }
  // A paper-only first attempt must be accepted without synthetic text or a fake grade.
  const ctx=await browser.newContext({viewport:{width:390,height:800}});
  const page=await ctx.newPage();
  await page.goto(pathToFileURL(html).href);
  await page.locator('#tab-'+i).click();
  await page.locator('#paperFirst').check();
  check(await page.locator('#commitFirst').isEnabled(),`${golden.id}: paper-only attempt rejected`);
  await page.locator('#commitFirst').click();
  check(await page.locator('#repairStage').isVisible(),`${golden.id}: paper-only diagnosis not opened`);
  check(!(await page.locator('#mainReferenceArea').isVisible()),`${golden.id}: paper-only leaked worked answer`);
  await ctx.close();
 }
} finally {await browser.close();}
console.log(JSON.stringify({schema:'core1b-three-case-golden-browser/v1',fixture_count:fixtures.length,
 tested_viewports:checked,variant_paper_cases:fixtures.length,
 human_learner_trial:'NOT_RUN',qrt_owner_acceptance:'NOT_GRANTED',failures:fail},null,2));
if(fail.length)process.exit(1);
