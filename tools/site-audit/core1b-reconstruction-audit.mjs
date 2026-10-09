#!/usr/bin/env node
/** Browser QA of ACTUAL generated Core1B, not a page-local second renderer. */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright';

if (!process.argv[2]) throw Error('Generated TEST product folder required');
const dir=path.resolve(process.argv[2]);
if (!fs.existsSync(path.join(dir,'core1b.html'))) throw Error('No canonical Core1B HTML');
const outdir=path.join(dir,'core1b-evidence');
fs.mkdirSync(outdir,{recursive:true});
const result={schema:'core1b-authored-reconstruction-browser/v1',
 exact_generated_product:true,viewports:[],failures:[],
 independent_learner_trial:'NOT_RUN',screen_reader:'NOT_RUN',academic_acceptance:false,
 authentic_source_core2:false};
const browser=await chromium.launch({headless:true});
try {
 for(const width of [320,390,768,1280]){
  const ctx=await browser.newContext({viewport:{width,height:800}});
  const pg=await ctx.newPage();
  const errors=[];
  pg.on('pageerror',e=>errors.push(e.message));
  await pg.goto(pathToFileURL(path.join(dir,'core1b.html')).href);
  const role=pg.locator('article[data-g9-role="CORE1B"]');
  const metrics=await pg.evaluate(()=>({
   scroll:document.documentElement.scrollWidth,
   client:document.documentElement.clientWidth,
   test:document.documentElement.dataset.g9Test==='sandbox-draft'
  }));
  const figure=role.locator('figure[data-g9-stage="PRE_ATTEMPT"]');
  const svgText=await figure.first().locator('svg').evaluate(e=>e.outerHTML);
  result.viewports.push({width,role_count:await role.count(),...metrics,errors});
  if(await role.count()!==1) result.failures.push(width+': not one canonical Core1B role');
  if(metrics.scroll>metrics.client)result.failures.push(width+': root overflow '+(metrics.scroll-metrics.client));
  if(!metrics.test)result.failures.push(width+': missing TEST stamp');
  if(!svgText.includes('CORE1B-GIVEN-FACTORS')||!/t − 2/.test(svgText)||!/t − 1/.test(svgText))
   result.failures.push(width+': own source-safe factor representation unavailable');
  if(/t mod 3|multiples? of (?:3|three)|even factor|parity|remainder|divisible by 6|coprime/i.test(svgText))
   result.failures.push(width+': preattempt figure reveals proof');
  if(errors.length)result.failures.push(width+': JS '+errors.join('; '));
  await pg.screenshot({path:path.join(outdir,'core1b-'+width+'-attempt.png'),fullPage:true});
  if(width===390){
   await pg.addStyleTag({content:'html{font-size:200%!important}'});
   const zoom=await pg.evaluate(()=>({
     client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth
   }));
   result.zoom200=zoom;
   if(zoom.scroll>zoom.client)result.failures.push('200%-text overflow '+(zoom.scroll-zoom.client));
   await pg.screenshot({path:path.join(outdir,'core1b-390-200pct.png'),fullPage:true});
  }

  if(width===1280){
   const summary=role.locator('summary').filter({hasText:'Reconstruct'}).first();
   const boundarySummary=role.locator('summary').filter({hasText:'Boundary answer'}).first();
   const proofBox=role.locator('[data-g9-attempt-box]:not([data-g9-attempt-stage])');
   const boundaryBox=role.locator('[data-g9-attempt-box][data-g9-attempt-stage="boundary"]');
   if(await summary.count()!==1||await boundarySummary.count()!==1
      ||await proofBox.count()!==1||await boundaryBox.count()!==1){
    result.failures.push('missing one of two distinct attempt/reveal pairs');
   }else{
    const initiallyClosed=!(await summary.evaluate(e=>e.parentElement.open));
    await summary.focus();await summary.press('Enter');
    const precommitBlocked=!(await summary.evaluate(e=>e.parentElement.open));
    const precommitPayloadEmpty=await summary.evaluate(e=>e.parentElement.querySelector('[data-g9-payload-slot]')?.children.length===0);
    await boundarySummary.focus();await boundarySummary.press('Enter');
    const boundaryPrecommitBlocked=!(await boundarySummary.evaluate(e=>e.parentElement.open));
    const boundaryPrecommitPayloadEmpty=await boundarySummary.evaluate(e=>e.parentElement.querySelector('[data-g9-payload-slot]')?.children.length===0);
    await proofBox.locator('textarea').fill('Synthetic browser QA only: an ungraded proof attempt.');
    await proofBox.locator('[data-g9-commit]').click();
    await summary.focus();await summary.press('Enter');
    const postcommitOpened=await summary.evaluate(e=>e.parentElement.open);
    const text=await summary.evaluate(e=>e.parentElement.innerText);
    await boundarySummary.focus();await boundarySummary.press('Enter');
    const boundaryStillBlockedAfterProof=!(await boundarySummary.evaluate(e=>e.parentElement.open));
    const boundaryStillEmptyAfterProof=await boundarySummary.evaluate(e=>e.parentElement.querySelector('[data-g9-payload-slot]')?.children.length===0);
    await boundaryBox.locator('textarea').fill('   ');
    await boundaryBox.locator('[data-g9-commit]').click();
    const boundaryWhitespaceBlocked=!(await boundarySummary.evaluate(e=>e.parentElement.open))
      && await boundarySummary.evaluate(e=>e.parentElement.querySelector('[data-g9-payload-slot]')?.children.length===0);
    await boundaryBox.locator('textarea').fill('At t=2 the product is 2, not divisible by six.');
    await boundaryBox.locator('[data-g9-commit]').click();
    await boundarySummary.focus();await boundarySummary.press('Enter');
    const boundaryAnswerAfterOwnCommit=await boundarySummary.evaluate(e=>e.parentElement.open&&/At t=2/.test(e.parentElement.innerText));
    const reverse=await ctx.newPage();
    await reverse.goto(pathToFileURL(path.join(dir,'core1b.html')).href);
    const reverseRole=reverse.locator('article[data-g9-role="CORE1B"]');
    await reverseRole.locator('[data-g9-attempt-stage="boundary"] [data-g9-paper]').check();
    await reverseRole.locator('[data-g9-attempt-stage="boundary"] [data-g9-commit]').click();
    const reverseProof=reverseRole.locator('summary').filter({hasText:'Reconstruct'}).first();
    await reverseProof.focus();await reverseProof.press('Enter');
    const boundaryOnlyDoesNotOpenProof=!(await reverseProof.evaluate(e=>e.parentElement.open))
      && await reverseProof.evaluate(e=>e.parentElement.querySelector('[data-g9-payload-slot]')?.children.length===0);
    const reverseBoundary=reverseRole.locator('summary').filter({hasText:'Boundary answer'}).first();
    await reverseBoundary.focus();await reverseBoundary.press('Enter');
    const boundaryPaperAttemptPermitted=await reverseBoundary.evaluate(e=>e.parentElement.open&&/At t=2/.test(e.parentElement.innerText));
    await reverse.close();
    result.boundary_independent_attempt='SEPARATE_COMMIT_GATES_BROWSER_VERIFIED_UNGRADED';
    result.reconstruction={
      initially_closed:initiallyClosed,precommit_blocked:precommitBlocked,
      precommit_payload_empty:precommitPayloadEmpty,
      boundary_precommit_blocked:boundaryPrecommitBlocked,
      boundary_precommit_payload_empty:boundaryPrecommitPayloadEmpty,
      postcommit_opened:postcommitOpened,
      boundary_still_blocked_after_proof:boundaryStillBlockedAfterProof,
      boundary_still_empty_after_proof:boundaryStillEmptyAfterProof,
      boundary_whitespace_blocked:boundaryWhitespaceBlocked,
      boundary_answer_after_own_commit:boundaryAnswerAfterOwnCommit,
      boundary_only_does_not_open_proof:boundaryOnlyDoesNotOpenProof,
      boundary_paper_attempt_permitted:boundaryPaperAttemptPermitted,
      has_residue_question:/remainder 0,1 or 2/.test(text),
      has_coprime_question:/gcd\(2,3\)/.test(text),
      prediction_check_visible:/No\. Three checks are instances/.test(text),
      full_rubric_evidence_visible:/Evidence:/.test(text),
      accepted_and_rejected_visible:/Representative answers that satisfy/.test(text)
        && /Answers that do not yet satisfy/.test(text)
        && /I tested t=3,4,5/.test(text),
      has_boundary:await role.locator('[data-g9-block="boundary_test"]').count()>0
    };
    for(const [k,v] of Object.entries(result.reconstruction))
      if(!v)result.failures.push('reconstruction: '+k+' is false');
    await pg.screenshot({path:path.join(outdir,'core1b-1280-reconstruction.png'),fullPage:true});
   }
  }
  await ctx.close();
 }
} finally {await browser.close();}
fs.writeFileSync(path.join(outdir,'core1b-browser-report.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({viewports:result.viewports.length,zoom200:result.zoom200,
 reconstruction:result.reconstruction,failures:result.failures},null,2));
if(result.failures.length)process.exitCode=1;
