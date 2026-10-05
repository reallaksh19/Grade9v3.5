// Independent reviewer attempts exact R4 saved pages using independently derived responses.
// This records rendered-page observations; it does not award source or Owner acceptance.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(path.resolve(process.env.NODE_PATH,'package.json'));
const {chromium}=require('playwright');
const root=process.cwd(), output=path.join(root,'evidence/blueprint-cycles/closure-r5-20261005');
const basis=process.env.G9_REVIEW_BASIS||'evidence/blueprint-cycles/closure-r4-20261005';
const outputName=process.env.G9_REVIEW_OUTPUT_NAME||'review-matrix-subjects.browser.json';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const selectedChoices={'Q-MAT-LEQ-01-EXEMPLAR8-Q6':[2],'Q-MAT-LEQ-02-EXEMPLAR9-4-1-Q16':[1],'PYQ-PHY-IITJEE-2007-P1-Q10':[2],'PYQ-PHY-IITJEE-2008-P2-Q33':[1],'PYQ-PHY-JEEADV-2014-P2-Q19':[3],'PYQ-PHY-INJSO-2011-Q22':[0],'PYQ-PHY-INJSO-2018-Q12':[2],'PYQ-PHY-INJSO-2023-Q24':[1,3]};
const cases=[
 ['matrix','core2a','CAL-ISS29-RETRIEVE-D2','One rational solution: collect to 5x=5, coefficient nonzero.'],
 ['matrix','core2a','CAL-ISS29-RETRIEVE-D3','E1: all rationals at k=-6, none otherwise. E2: all at k=2, one otherwise.'],
 ['matrix','core2a','CAL-ISS29-RETRIEVE-D4','k=2 invalid. k=1 yields x=0, one rational. Otherwise first equation x=1/(k-2), second x=k-1; compatibility roots (3±sqrt5)/2 force irrational x. Hence none for every other real k, never all.'],
 ['matrix','core2a','CAL-ISS29-APPLY-D3','22mm=11/5cm. B=5C-2=9; A=(9-4)/3=5/3; X=2A+1=13/3cm. Forward:13/3,5/3,9,11/5cm.'],
 ['matrix','core2a','CAL-ISS29-MODEL-D1','R1 applies: A nonzero licenses reversible division by A.'],
 ['matrix','core2a','CAL-ISS29-REPRESENT-D1','(2,3): x first, y second.'],
 ['matrix','core2a','CAL-ISS29-SYNTHESIZE-D1','Halve first, then subtract3; the doubled output must first be returned to the undoubled inner value.'],
 ['matrix','core2a','CAL-ISS29-JUSTIFY-D1','2 is nonzero, so division by2 is defined and reverses multiplication by2. Zero has no multiplicative inverse; division byzero is undefined.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-01-EXEMPLAR8-Q6','x=5, option c: both expressions11.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-01-EXEMPLAR8-Q17','x=1: 5x=5; both original sides -1.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-01-EXEMPLAR8-Q20','Blank3: 9(-2)-3=-21.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-02-NCERT8-EX2-1-Q1','x=18; 54=36+18.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-02-NCERT8-EX2-1-Q2','t=-1; -8=-8.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-02-NCERT8-EX2-1-Q3','x=-2; -1=-1.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-02-NCERT8-EX2-1-Q5','x=5, positive; 9=9.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-02-EXEMPLAR9-4-1-Q16','B remains same, since nonzero multiplication/division have inverse operations.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-03-NCERT8-EX2-2-Q7','t=-2; original sides both -15.'],
 ['subjects/mathematics','core2','Q-MAT-LEQ-03-NCERT8-EX2-2-Q9','z=2; -3z+1=32z-69 gives35z=70; original sides both-5.'],
 ['subjects/mathematics','core2a','Q-MATH-LINEAR-01','x=7/3; 3*(7/3)+2=9 exactly.'],
 ['subjects/mathematics','core2b','Q-MATH-LINEAR-2B-01','x=8/3; 3*(8/3-1)=5. Divide outer3 first, then add1; expansion equally valid.'],
 ['subjects/physics','core2','PYQ-PHY-IITJEE-2007-P1-Q10','C: incline stores positive gravitational potential, so less dissipated; same surface coefficient.'],
 ['subjects/physics','core2','PYQ-PHY-IITJEE-2008-P2-Q33','B: both true. Pull reduces perpendicular reaction, push increases it; same mu, second statement does not explain difference.'],
 ['subjects/physics','core2','PYQ-PHY-IITJEE-2011-P1-Q41','(1+mu)=3(1-mu); mu=1/2; requested number N=5. Use R_perp for normal force to avoid N collision.'],
 ['subjects/physics','core2','PYQ-PHY-JEEADV-2014-P2-Q19','D: whole-system demand3g sinθ versus sole-contact capacity0.6g cosθ yields tanθ<=0.2. Static expression2 at5,10degrees; sliding3 at15,20degrees.'],
 ['subjects/physics','core2','PYQ-PHY-JEEADV-2020-P1-Q13','Force/torque balance NL/NR=40/(50-l); first switch NL/NR=mu_s/mu_k=1.25 gives l=18. Then NR/NL=32/(r-50)=1.25, so r-50=25.6cm.'],
 ['subjects/physics','core2','PYQ-PHY-JEEMAIN-2026-06APR-S2-Q46','Same distance from rest gives a_s=4a_r;1=4(1-mu), mu=.75, alpha75.'],
 ['subjects/physics','core2','PYQ-PHY-INJSO-2011-Q22','A: static demand20N below capacity25N; acceleration0, friction20N.'],
 ['subjects/physics','core2','PYQ-PHY-INJSO-2016-Q32A','fP16N,fQ48N; F64N. Table-on-Q (-48,+80)N; magnitude16sqrt34 and angle arctan(80/48) towardP above horizontal.'],
 ['subjects/physics','core2','PYQ-PHY-INJSO-2018-Q12','2F=fk,3F-fk=50, henceF50N,fk100N,mu.1,C.'],
 ['subjects/physics','core2','PYQ-PHY-INJSO-2023-Q24','B andD: ground external horizontal force changes total rider+cycle momentum; tyre/brake contacts internal.']
];
const browser=await chromium.launch({headless:true}), context=await browser.newContext({viewport:{width:820,height:1180}}),page=await context.newPage(),rows=[],visuals=[];
try{
 for(const [group,core,initialId,response] of cases){
  let id=initialId;
  if(group==='matrix'&&initialId==='CAL-ISS29-RETRIEVE-D4'){
   const packageData=JSON.parse(fs.readFileSync(path.join(root,basis,'matrix/package.v1.json'),'utf8'));
   id=packageData.questions.find(q=>q.difficulty.band==='D4').id;
  }
  const file=path.join(root,basis,group,'rendered',core+'.html');
  await page.goto('http://127.0.0.1:8769/'+[basis,group,'rendered',core+'.html'].join('/'));await page.waitForTimeout(100);
  const article=page.locator('article[data-g9-unit="'+id+'"]');
  const before=await article.innerText();
  const hint=article.locator('[data-g9-next-rung]').first();
  let help=false;
  if(await hint.count()&&await hint.isVisible()&&await hint.isEnabled()){await hint.click();help=true;}
  const helpText=await article.innerText();
  const field=article.locator('[data-g9-attempt]').first();
  if(await field.count())await field.fill(core==='core2a'&&group==='subjects/mathematics'?'7/3':core==='core2b'?'8/3':response);
  else if(await article.locator('[data-g9-choice]').count())for(const index of selectedChoices[id])await article.locator('[data-g9-choice]').nth(index).check();
  else await article.locator('[data-g9-paper]').first().check();
  if(await article.locator('[data-g9-unit-input]').count())await article.locator('[data-g9-unit-input]').first().fill('dimensionless');
  await article.locator('[data-g9-commit]').first().click();
  const gate=article.locator('details[data-requires-attempt]').first();
  await gate.locator('summary').click();
  const disclosed=await article.innerText();
  rows.push({id,relative_page:path.relative(root,file).replaceAll('\\','/'),page_sha256:sha(file),reviewer_response:response,help_requested:help,solution_disclosed:await gate.getAttribute('open')!==null,initial_visible_text:before,help_visible_text:helpText,disclosed_text:disclosed});
 }
 if(process.env.G9_CAPTURE_VISUAL==='1'){
  await page.goto('http://127.0.0.1:8769/'+basis+'/matrix/rendered/core2a.html');
  for(const article of await page.locator('article[data-g9-unit]').all()){
   const id=await article.getAttribute('data-g9-unit'),figure=article.locator('figure[data-g9-figure]').first();
   await figure.locator('[data-g9-stage-goto="1"]').click();
   const imageFile=path.join(output,'review-matrix-subjects.visual-'+id+'.png');
   await figure.screenshot({path:imageFile});
   visuals.push({id,stage:'CONSTRUCTION_FRAMEWORK',stage_mode:await figure.getAttribute('data-g9-stage-mode'),image_ref:path.relative(root,imageFile).replaceAll('\\','/'),image_sha256:sha(imageFile)});
  }
  await page.goto('http://127.0.0.1:8769/'+basis+'/subjects/mathematics/rendered/core2b.html');
  const transferArticle=page.locator('article[data-g9-unit="Q-MATH-LINEAR-2B-01"]');
  await transferArticle.locator('[data-g9-attempt]').fill('8/3');
  await transferArticle.locator('[data-g9-unit-input]').fill('dimensionless');
  await transferArticle.locator('[data-g9-commit]').click();
  const gate=transferArticle.locator('details[data-requires-attempt]').first();
  if(await gate.getAttribute('open')===null)await gate.locator('summary').click();
  const figure=gate.locator('figure[data-g9-figure]').first();
  await figure.locator('[data-g9-stage-goto="1"]').click();
  const imageFile=path.join(output,'review-matrix-subjects.visual-MATH-TRANSFER.png');
  await figure.screenshot({path:imageFile});
  visuals.push({id:'Q-MATH-LINEAR-2B-01',stage:'PROTECTED_RESULT',image_ref:path.relative(root,imageFile).replaceAll('\\','/'),image_sha256:sha(imageFile)});
 }
}finally{await browser.close();}
fs.mkdirSync(output,{recursive:true});
fs.writeFileSync(path.join(output,outputName),JSON.stringify({schema:'independent-exact-render-attempt/v1',reviewer:'review_matrix_subjects separate reviewer session',basis_head:basis.includes('closure-r4')?'59cfb081a96b6d15ad9c5a6ded771b2dce00091d':'R5_WORKTREE_EXACT_BYTE_HASHES_IN_ROWS',mode:'NEW_CHROMIUM_SAVED_PAGE_EXECUTION',limitation:'Independent content attempts and disclosure observations, not source custody cross-read, learner trial, correctness marking, Owner acceptance, or whole-suite certification. Captured innerText is an observation log; it is not a claim that every SVG stage text in it is visually displayed.',rows,visuals},null,2)+'\n');
console.log(JSON.stringify({attempts:rows.length,disclosed:rows.filter(r=>r.solution_disclosed).length}));
