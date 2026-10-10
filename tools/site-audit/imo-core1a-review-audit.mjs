#!/usr/bin/env node
'use strict';
/** Browser-only TEST Core1A review QA. No admissions, remote fetches or page publishing. */
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const OUT = process.env.IMO_BROWSER_OUT || '/tmp/imo-core1a-browser';
const URL = process.env.IMO_BROWSER_URL || 'http://127.0.0.1:8769/test/imo-grade9/core1a.html';
const MAT_URL = process.env.IMO_MATH_URL || 'http://127.0.0.1:8769/mathematics/imo-grade9/index.html';
const VIEWS = [
  {name:'mobile-320',width:320,height:640},
  {name:'mobile-390',width:390,height:844},
  {name:'tablet-768',width:768,height:1024},
  {name:'desktop-1280',width:1280,height:800}
];

function demand(test,message){if(!test)throw new Error(message)}
(async()=>{
  fs.mkdirSync(OUT,{recursive:true});
  const browser=await chromium.launch({headless:true});
  const report={
    schema:'imo-g9-core1a-chromium-qa-v1',
    page:URL,source_kind:'EXACT_BRANCH_LOCAL_HTTP_STATIC_TEST_PAGE',
    browser:'playwright-chromium-1.56.1',widths:[],
    browser_exercised:true,
    screen_reader_manual:'NOT_RUN',independent_learner_comprehension:'NOT_RUN',
    core_academic_accepted:false,sof_source_material_reproduced:false,
    generated_pdf:'TEST_CANDIDATE_PRINT_REVIEW_ONLY',
    checks:{},failures:[]
  };
  const assert=(test,msg)=>{if(!test)report.failures.push(msg)};
  try{
    const context=await browser.newContext({viewport:{width:1280,height:800},deviceScaleFactor:1,javaScriptEnabled:true});
    const page=await context.newPage();
    page.on('pageerror',e=>report.failures.push('PAGE_ERROR: '+e.message));
    const response=await page.goto(URL,{waitUntil:'networkidle',timeout:30000});
    assert(response && response.status()===200,'review page HTTP status is not 200');
    const body=await page.locator('body').innerText();
    assert(body.includes('TEST REVIEW ONLY · CANDIDATE'),'TEST candidate banner missing');
    assert(body.includes('not an academically accepted Core 1A product'),'non-admission statement missing');
    assert(body.includes('real device, keyboard, assistive-technology and print inspections are NOT RUN'),'historical QA disclosure altered');
    assert(await page.locator('html[data-g9-role="TEST"][data-g9-canonical-acceptance="false"]').count()===1,'not in TEST candidate mode');
    const steps=await page.locator('[data-core1a-step-id]').evaluateAll(nodes=>nodes.map(el=>el.getAttribute('data-core1a-step-id')));
    assert(JSON.stringify(steps)===JSON.stringify(['TC-01','TC-02','TC-03','TC-04']),'wrong Core1A teaching step sequence');
    const table=page.getByRole('table',{name:'Exhaustive modulo-3 cases for three successive integers'});
    assert(await table.count()===1,'semantic residue table inaccessible by caption');
    assert(await table.getByRole('columnheader').count()===3,'residue table must have three named column headers');
    assert(await table.getByRole('rowheader').count()===3,'residue table must have three row headers');
    const mapping=await page.locator('[data-residue]').evaluateAll(rows=>rows.map(tr=>({
      r:tr.getAttribute('data-residue'),term:tr.querySelector('td code')?.textContent.trim()
    })));
    assert(JSON.stringify(mapping)===JSON.stringify([{r:'0',term:'n'},{r:'1',term:'n+2'},{r:'2',term:'n+1'}]),'residue-to-factor mapping incorrect');
    const exit=page.locator('#exit-model-closure');
    assert(!(await exit.evaluate(el=>el.open)),'model answer disclosure must start closed');
    const textarea=page.getByRole('textbox',{name:'Your reasoning (optional)'});
    assert(await textarea.count()===1,'missing accessible unsubmitted response field');
    await textarea.fill('I will show factors 8 and 3 for arbitrary n.');
    assert((await textarea.inputValue()).includes('arbitrary n'),'typed notes not accepted');
    await page.reload({waitUntil:'domcontentloaded'});
    assert(await textarea.inputValue()==='','typed notes must not be stored or sent');
    const heading=page.getByRole('heading',{name:'Independent exit · Transfer to four factors'});
    assert(await heading.count()===1,'exit landmark not accessible');
    const summary=page.locator('#exit-model-closure > summary');
    await summary.focus();
    assert(await summary.evaluate(el=>el===document.activeElement),'summary cannot receive keyboard focus');
    await page.keyboard.press('Enter');
    assert(await exit.evaluate(el=>el.open),'keyboard Enter did not reveal native model answer');
    assert(await page.getByText('The product of four consecutive positive integers is divisible by 24.',{exact:true}).isVisible(),
      'model answer not visible after keyboard reveal');
    await page.keyboard.press('Enter');
    assert(!(await exit.evaluate(el=>el.open)),'keyboard Enter did not close disclosure');
    report.checks.keyboard_disclosure_open_close=true;
    report.checks.user_notes_not_stored_after_reload=true;
    report.checks.complete_proof_and_residue_table=true;

    for(const view of VIEWS){
      await page.setViewportSize({width:view.width,height:view.height});
      await page.goto(URL,{waitUntil:'networkidle',timeout:30000});
      const measurements=await page.evaluate(()=>{
        const html=document.documentElement,body=document.body;
        const el=document.querySelector('.table-wrap');
        const table=el?.querySelector('table');
        const rects=Array.from(document.querySelectorAll('.lesson-nav a, .model-proof summary, a[href]'))
          .filter(x=>x.getClientRects().length).map(x=>({w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height}));
        return {
          viewportWidth:innerWidth,
          overflowPx:Math.max(0,html.scrollWidth-html.clientWidth,body.scrollWidth-html.clientWidth),
          tableOverflowLocal:!!(el && table && table.scrollWidth>el.clientWidth),
          tableScrollerWidth:el?.clientWidth??0,
          tableWidth:table?.scrollWidth??0,
          smallControlCount:rects.filter(r=>r.h<28).length,
          missingH1:document.querySelectorAll('main h1').length!==1,
          loadedCSS:!!Array.from(document.styleSheets).find(x=>x.href?.includes('/css/modern-learner.css')),
          overflowCandidates:Array.from(document.querySelectorAll('body *'))
            .map(node=>({node,rect:node.getBoundingClientRect()}))
            .filter(({rect})=>rect.right>innerWidth+1 || rect.left < -1)
            .slice(0,12).map(({node,rect})=>({
              tag:node.tagName.toLowerCase(),id:node.id||null,
              className:typeof node.className==='string'?node.className.slice(0,80):'',
              left:Math.round(rect.left),right:Math.round(rect.right),
              scrollWidth:node.scrollWidth,clientWidth:node.clientWidth
            }))
        };
      });
      assert(measurements.overflowPx===0,`${view.name}: page horizontal overflow ${measurements.overflowPx}px; offending: ${JSON.stringify(measurements.overflowCandidates)}`);
      assert(!measurements.missingH1,`${view.name}: missing single h1`);
      assert(measurements.loadedCSS,`${view.name}: CSS not loaded`);
      await page.screenshot({path:path.join(OUT,view.name+'.png'),fullPage:true,animations:'disabled'});
      report.widths.push({name:view.name,...measurements,screenshot:view.name+'.png'});
    }

    // True 200%-text test: force large root font while maintaining 390px viewport.
    await page.setViewportSize({width:390,height:844});
    await page.goto(URL,{waitUntil:'networkidle'});
    await page.evaluate(()=>{document.documentElement.style.fontSize='200%'});
    const scaled=await page.evaluate(()=>{
      const overflowCandidates=Array.from(document.querySelectorAll('body *'))
        .filter(node=>{
          const rect=node.getBoundingClientRect();
          if(rect.right<=innerWidth+1 && rect.left>=-1)return false;
          let parent=node.parentElement;
          while(parent && parent!==document.body){
            const style=getComputedStyle(parent), box=parent.getBoundingClientRect();
            if(/auto|hidden|scroll|clip/.test(style.overflowX)
              && box.left>=-1 && box.right<=innerWidth+1)return false;
            parent=parent.parentElement;
          }
          return true;
        })
        .slice(0,18).map(node=>{
          const box=node.getBoundingClientRect();
          return {tag:node.tagName.toLowerCase(),id:node.id||null,
            className:typeof node.className==='string'?node.className.slice(0,90):'',
            left:Math.round(box.left),right:Math.round(box.right),
            width:Math.round(box.width),scrollWidth:node.scrollWidth,
            clientWidth:node.clientWidth,overflowX:getComputedStyle(node).overflowX};
        });
      const scrollCandidates=Array.from(document.querySelectorAll('html, body, body *'))
        .filter(node=>node.scrollWidth>node.clientWidth+4)
        .map(node=>({
          tag:node.tagName.toLowerCase(),id:node.id||null,
          className:typeof node.className==='string'?node.className.slice(0,80):'',
          scrollWidth:node.scrollWidth,clientWidth:node.clientWidth,
          overflowX:getComputedStyle(node).overflowX,
          left:Math.round(node.getBoundingClientRect().left),
          right:Math.round(node.getBoundingClientRect().right)
        }))
        .sort((a,b)=>(b.scrollWidth-b.clientWidth)-(a.scrollWidth-a.clientWidth))
        .slice(0,28);
      return {w:innerWidth,
        extra:Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)
          -document.documentElement.clientWidth,
        root:{clientWidth:document.documentElement.clientWidth,
              scrollWidth:document.documentElement.scrollWidth,
              bodyClientWidth:document.body.clientWidth,
              bodyScrollWidth:document.body.scrollWidth},
        overflowCandidates,scrollCandidates};
    });
    report.checks.zoom200=scaled;
    assert(scaled.extra<=0,'200% text scaling introduces horizontal page overflow: '
      +scaled.extra+'; offenders: '+JSON.stringify(scaled.overflowCandidates)+'; scroll: '+JSON.stringify(scaled.scrollCandidates));
    await page.screenshot({path:path.join(OUT,'zoom200-mobile.png'),fullPage:true,animations:'disabled'});

    // Printed TEST review includes the authored model, not an official SOF key.
    await page.setViewportSize({width:1280,height:800});
    await page.goto(URL,{waitUntil:'networkidle'});
    await page.locator('#exit-model-closure').evaluate(el=>el.open=true);
    await page.emulateMedia({media:'print'});
    const pdf=path.join(OUT,'imo-test-core1a-review-print.pdf');
    await page.pdf({path:pdf,format:'A4',printBackground:true,margin:{top:'14mm',bottom:'14mm',left:'12mm',right:'12mm'}});
    const pdfBytes=fs.statSync(pdf).size;
    assert(pdfBytes>2000,'Chromium print PDF too small/empty');
    report.checks.chromium_print_pdf={path:path.basename(pdf),bytes:pdfBytes,status:'GENERATED_UNREVIEWED'};
    // Mathematics tab link lives under local HTTP; no live host claim.
    const math=await page.goto(MAT_URL,{waitUntil:'domcontentloaded',timeout:30000});
    assert(math && math.status()===200,'Maths linked topic page not loadable');
    const reviewLink=page.locator('a[href="../../test/imo-grade9/core1a.html"]');
    assert(await reviewLink.count()===1,'Maths tab cannot find candidate TEST page');
    await reviewLink.click();
    assert(page.url().endsWith('/test/imo-grade9/core1a.html'),'Maths topic link navigates to wrong page');
    assert(await page.getByRole('heading',{level:1}).innerText()!=='','candidate navigation has no visible heading');
    report.checks.math_tab_navigation=true;
    await context.close();
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(OUT,'browser-evidence.json'),JSON.stringify(report,null,2)+'\n');
  }
  if(report.failures.length){
    for(const problem of report.failures)console.error('BLOCK: '+problem);
    process.exitCode=1;
  }else console.log('PASS Chromium TEST Core1A QA:',JSON.stringify({
    viewportCount:report.widths.length,
    pdfBytes:report.checks.chromium_print_pdf?.bytes,
    keyboardDisclosure:report.checks.keyboard_disclosure_open_close,
    zoom200:report.checks.zoom200,
    failures:report.failures.length
  }));
})().catch(e=>{console.error('BLOCK: '+e.stack);process.exit(1)});
