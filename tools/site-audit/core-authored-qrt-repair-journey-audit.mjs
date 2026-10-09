#!/usr/bin/env node
/** Browser-observed attempt → support → reasoning → linked Core1A repair.
 * This tests UI visibility and navigation; raw HTML is not a secure exam vault.
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { chromium } from 'playwright';

if (!process.argv[2]) throw new Error('Pass the generated TEST product directory');
const folder = path.resolve(process.argv[2]);
for (const page of ['core2a.html','core1a.html']) {
  if (!fs.existsSync(path.join(folder,page))) throw new Error('missing actual generated '+page);
}
const evidence = process.env.CORE_JOURNEY_EVIDENCE
  ? path.resolve(process.env.CORE_JOURNEY_EVIDENCE)
  : path.join(folder,'journey-evidence');
fs.mkdirSync(evidence,{recursive:true});
const out={schema:'core-authored-qrt-repair-browser/v1',roles:['CORE2A','CORE1A'],
  widths:[],failures:[],original_exam_core2:false,
  disclosure_is_cryptographic_security:false,
  human_accessibility:'NOT_RUN',learner_comprehension:'NOT_RUN',
  owner_acceptance:false};
const browser=await chromium.launch({headless:true});
try {
  for (const w of [320,390,768,1280]) {
    const ctx=await browser.newContext({viewport:{width:w,height:780}});
    const pg=await ctx.newPage();
    const errors=[];
    pg.on('pageerror',e=>errors.push(e.message));
    await pg.goto(pathToFileURL(path.join(folder,'core2a.html')).href,{waitUntil:'load'});
    const article=pg.locator('article[data-g9-role="CORE2A"]');
    const cnt=await article.count();
    const pre=article.locator('figure[data-g9-stage="PRE_ATTEMPT"]');
    const npre=await pre.count();
    let preBody=npre?await pre.first().innerText():'';
    const preSvg=npre?await pre.first().locator('svg').first().evaluate(e=>e.outerHTML):'';
    const doc=await pg.evaluate(()=>({
      client:document.documentElement.clientWidth,
      scroll:document.documentElement.scrollWidth,
      isTest:document.documentElement.dataset.g9Test==='sandbox-draft'
    }));
    out.widths.push({width:w,article:cnt,pre_fig:npre,client:doc.client,scroll:doc.scroll,
      test:doc.isTest,page_errors:errors});
    if(cnt!==1)out.failures.push(w+': expected one authored Core2A article, found '+cnt);
    if(!doc.isTest)out.failures.push(w+': no TEST-only stamp');
    if(doc.scroll>doc.client)out.failures.push(w+': horizontal overflow '+(doc.scroll-doc.client)+'px');
    if(!npre||!preSvg.includes('PRACTICE-FACTORS-ONLY'))
      out.failures.push(w+': no safe initial factor representation');
    if(/factor of 3|factor of two|coprime|remainder classes|divisible by 6|modulo 3/i.test(preSvg+preBody))
      out.failures.push(w+': pre-attempt figure leaks decisive justification');
    if(errors.length)out.failures.push(w+': JS errors: '+errors.join('; '));
    await pg.screenshot({path:path.join(evidence,'core2a-'+w+'-attempt.png'),fullPage:true});
    if(w===390){
      await pg.addStyleTag({content:'html{font-size:200%!important}'});
      const zoom=await pg.evaluate(()=>({
        client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth
      }));
      out.zoom200=zoom;
      if(zoom.scroll>zoom.client)out.failures.push('200%-text overflow '+(zoom.scroll-zoom.client)+'px');
      await pg.screenshot({path:path.join(evidence,'core2a-390-200pct.png'),fullPage:true});
    }
    if(w===1280){
      const summary=article.locator('summary').filter({hasText:'Reasoning route and full solution'}).first();
      if(await summary.count()!==1){out.failures.push('missing keyboard-accessible full-solution summary');}
      else{
        const initiallyClosed=!(await summary.evaluate(el=>el.parentElement.open));
        const initiallyHidden=!(await summary.isVisible());
        // This is a machine-produced example attempt, NOT real learner assessment.
        const answerField=article.locator('[data-g9-attempt-box] textarea').first();
        if(await answerField.count()!==1)out.failures.push('missing free-response attempt field');
        else{
          await answerField.fill('Synthetic QA attempt: an arbitrary-number proof is required.');
          await article.locator('[data-g9-commit]').first().click();
        }
        const released=await summary.isVisible();
        if(!initiallyHidden||!released)out.failures.push('attempt-gated answer not protected until explicit commitment');
        await summary.focus();await summary.press('Enter');
        const opened=await summary.evaluate(el=>el.parentElement.open);
        const route=article.locator('[data-g9-block="reasoning_route"]');
        const routeText=await route.first().innerText({timeout:2500});
        const link=article.locator('a[data-g9-repair-ref="TC-03"]');
        const href=await link.first().getAttribute('href');
        out.learning={initially_closed:initiallyClosed,pre_commit_hidden:initiallyHidden,
          post_commit_released:released,keyboard_opened:opened,
          route_explains_parity_and_modulo3:/parity/i.test(routeText)&&/modulo 3/i.test(routeText),
          repair_href:href,repair_link_count:await link.count()};
        if(!initiallyClosed||!opened)out.failures.push('solution was exposed initially or did not reveal using Enter');
        if(!out.learning.route_explains_parity_and_modulo3)out.failures.push('reasoning route missing actual warrant');
        if(!href?.startsWith('core1a.html#CU-'))out.failures.push('repair does not link to bound Core1A construction');
        await pg.screenshot({path:path.join(evidence,'core2a-1280-solution.png'),fullPage:true});
        if(await link.count()){
          await Promise.all([pg.waitForURL(/core1a\.html#CU-/),link.first().click()]);
          const dest=await pg.evaluate(()=>({
            file:window.location.pathname.endsWith('core1a.html'),
            target:window.location.hash.slice(1),
            found:!!document.getElementById(decodeURIComponent(window.location.hash.slice(1)))
          }));
          out.learning.repair_destination=dest;
          if(!dest.file||!dest.found)out.failures.push('Core1A repair target did not resolve');
          await pg.screenshot({path:path.join(evidence,'core1a-repair-arrival.png'),fullPage:true});
        }
      }
    }
    await ctx.close();
  }
}finally{await browser.close();}
fs.writeFileSync(path.join(evidence,'journey-browser-report.json'),JSON.stringify(out,null,2)+'\n');
console.log(JSON.stringify(out,null,2));
if(out.failures.length)process.exitCode=1;
