#!/usr/bin/env node
'use strict';
// Real browser check on the canonical renderer's TEST-only, wholly authored Core1A.
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const folder=process.env.IMO_Q26_RENDER_OUT||'/tmp/imo-q26-core-render';
const report={schema:'imo-g9-authored-q26-core1a-render-browser-v1',
  product_status:'TEST_CANDIDATE_NOT_ACCEPTED',
  source_core2_admissions:0,source_pdf_rights_granted:false,
  pdf_owner_accepted:false,screen_reader_manual:'NOT_RUN',
  widths:[],keyboard_disclosure:'NOT_RUN',failures:[]};
const checks=[{name:'mobile-320',width:320,height:640},
  {name:'mobile-390',width:390,height:844},
  {name:'tablet-768',width:768,height:1024},
  {name:'desktop-1280',width:1280,height:800}];
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage({viewport:{width:1280,height:800}});
  const url='file://'+path.join(folder,'core1a.html');
  page.on('pageerror',e=>report.failures.push('page-error: '+e.message));
  for(const view of checks){
    await page.setViewportSize({width:view.width,height:view.height});
    await page.goto(url,{waitUntil:'load'});
    const m=await page.evaluate(()=>{
      const root=document.documentElement,body=document.body;
      const w=root.clientWidth;
      return {width:innerWidth,rootScrollWidth:root.scrollWidth,
        bodyScrollWidth:body.scrollWidth,overflowPx:Math.max(0,root.scrollWidth-w,body.scrollWidth-w),
        headings:[...document.querySelectorAll('h1,h2,h3')].map(h=>h.innerText.trim()).filter(Boolean).slice(0,8),
        offenders:[...document.querySelectorAll('body *')]
          .filter(n=>n.scrollWidth>n.clientWidth+2
            && !/auto|hidden|scroll|clip/.test(getComputedStyle(n).overflowX))
          .slice(0,8).map(n=>({tag:n.tagName,id:n.id,
            className:typeof n.className==='string'?n.className:'',
            scrollWidth:n.scrollWidth,clientWidth:n.clientWidth}))};
    });
    if(m.overflowPx>0)report.failures.push(view.name+': horizontal overflow '
      +m.overflowPx+' '+JSON.stringify(m.offenders));
    if(!m.headings.length)report.failures.push(view.name+': no learner headings');
    report.widths.push({name:view.name,...m,screenshot:view.name+'.png'});
    await page.screenshot({path:path.join(folder,view.name+'.png'),
      fullPage:true,animations:'disabled'});
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto(url,{waitUntil:'load'});
  await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
  const scaled=await page.evaluate(()=>{
    const w=document.documentElement.clientWidth;
    return {extra:Math.max(document.documentElement.scrollWidth,
      document.body.scrollWidth)-w,
      scrollItems:[...document.querySelectorAll('body *')]
        .filter(n=>n.scrollWidth>n.clientWidth+3)
        .slice(0,12).map(n=>({tag:n.tagName,id:n.id,
          clientWidth:n.clientWidth,scrollWidth:n.scrollWidth,
          overflowX:getComputedStyle(n).overflowX}))};
  });
  report.zoom200=scaled;
  if(scaled.extra>0)report.failures.push('200%-text horizontal overflow: '
    +scaled.extra+' '+JSON.stringify(scaled.scrollItems));
  await page.screenshot({path:path.join(folder,'zoom200-mobile.png'),
    fullPage:true,animations:'disabled'});
  await page.setViewportSize({width:1280,height:800});
  await page.goto(url,{waitUntil:'load'});
  const content=await page.locator('body').innerText();
  for(const phrase of ['a common positive quantity','3t=t+162','2^(2y+1)=4^y+64']){
    if(!content.includes(phrase))report.failures.push('learner text missing '+phrase);
  }
  if(content.includes('SOF-IMO-G09')||content.includes('© SOF'))
    report.failures.push('source identification or copyrighted source material leaked');
  const steps=await page.locator('[data-g9-step]').count();
  report.steps=steps;
  if(steps!==5)report.failures.push('expected five authored teaching steps, got '+steps);
  const reveals=await page.locator('[data-g9-reveal],details,button').count();
  report.accessible_controls_count=reveals;
  if(reveals===0)report.failures.push('no keyboard-operable learner controls rendered');
  const focusControls=await page.locator('button,summary,[tabindex="0"]').count();
  if(focusControls===0)report.failures.push('no controls accessible for keyboard focus');
  else{
    await page.keyboard.press('Tab');
    const focused=await page.evaluate(()=>document.activeElement?.tagName);
    report.keyboard_disclosure=focused&&focused!=='BODY'?'FOCUSABLE':'NO_FOCUS';
    if(report.keyboard_disclosure!=='FOCUSABLE')
      report.failures.push('Tab did not reach a focusable control');
  }
  report.browser_exercised=true;
}finally{
  await browser.close();
  fs.writeFileSync(path.join(folder,'q26-browser-review.json'),
    JSON.stringify(report,null,2)+'\n');
}
if(report.failures.length){
  for(const f of report.failures)console.error('BLOCK: '+f);
  process.exitCode=1;
}else console.log('PASS authored Q26 canonical Core1A browser',JSON.stringify({
  viewports:report.widths.length,zoom:report.zoom200?.extra,
  steps:report.steps,keyboard:report.keyboard_disclosure
}));
