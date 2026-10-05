// Subject and calibration review through the same saved-page production shell.
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(path.resolve(process.env.NODE_PATH,'package.json'));
const {chromium}=require('playwright');
const root=process.cwd(),baseDir=process.env.G9_REVIEW_DIR||'evidence/blueprint-cycles/closure-20261005';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const server=http.createServer((req,res)=>{
  const file=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));
  if(!file.startsWith(root+path.sep)||!fs.existsSync(file)){res.writeHead(404);res.end();return;}
  res.setHeader('Content-Type',file.endsWith('.html')?'text/html':file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'application/octet-stream');res.end(fs.readFileSync(file));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true}),results=[];
try{
 for(const group of ['subjects/physics','subjects/mathematics','matrix']){
  const dir=path.join(root,baseDir,group,'rendered'),failures=[],pages=[];
  const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage();
  page.on('pageerror',e=>failures.push(e.message));
  const receipt={tool:'issue29-supplement-browser/1',mode:'LEARNER_PDF',pages:[]};
  const binding={};
  for(const file of fs.readdirSync(dir).filter(f=>/^core.*\.html$/.test(f))){
   binding[file]=sha(path.join(dir,file));
   await page.goto(origin+'/'+[baseDir,group,'rendered',file].join('/'));await page.waitForTimeout(200);
   const states=[];
   for(const article of await page.locator('article[data-g9-unit]').all()){
    const gate=article.locator('details[data-requires-attempt]').first();
    if(!await gate.count())continue;
    await gate.locator('summary').click();
    if(await gate.getAttribute('open')!==null)failures.push(file+': blank response opened a protected body');
    const next=article.locator('[data-g9-next-rung]').first();
    if(await next.count() && await next.isVisible() && await next.isEnabled())await next.click();
    const field=article.locator('textarea[data-g9-attempt]').first();
    if(await field.count())await field.fill('Mechanical browser check; no learner result.');
    else if(await article.locator('[data-g9-paper]').count())await article.locator('[data-g9-paper]').first().check();
    else continue;
    await article.locator('[data-g9-commit]').first().click();
    await gate.locator('summary').click();
    if(await gate.getAttribute('open')===null)failures.push(file+': committed response did not permit disclosure');
    states.push({unit:await article.getAttribute('data-g9-unit'),observed:['BLANK_BLOCKED','COMMITTED','DISCLOSED']});
   }
   await page.locator('[data-g9-action="display"]').first().click();
   const widget=await page.locator('#g9-display-popover').evaluate(el=>{
    const controls=[...el.querySelectorAll('button,input')].filter(e=>e.checkVisibility());
    return {visible:el.checkVisibility(),small:controls.filter(e=>Math.min(e.getBoundingClientRect().width,e.getBoundingClientRect().height)<47.95).length,minFont:Math.min(...[...el.querySelectorAll('*')].filter(e=>!e.childElementCount&&e.textContent.trim()&&e.checkVisibility()).map(e=>parseFloat(getComputedStyle(e).fontSize)))};
   });
   if(!widget.visible||widget.small||widget.minFont<13.95)failures.push(file+': display widget geometry/type '+JSON.stringify(widget));
   await page.locator('#g9-btn-close').click();
   const geometry=await page.evaluate(()=>{
    const text=[...document.body.querySelectorAll('*')].filter(e=>!e.closest('svg')&&!e.childElementCount&&e.textContent.trim()&&e.checkVisibility()&&e.getBoundingClientRect().width);
    return {overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,minFont:Math.min(...text.map(e=>parseFloat(getComputedStyle(e).fontSize)))};
   });
   if(geometry.overflow>1||geometry.minFont<13.95)failures.push(file+': visible reading geometry '+JSON.stringify(geometry));
   const probes=page.locator('[data-g9-alignment-probe]');
   if(group==='subjects/physics'&&file==='core1a.html'){
    if(!await probes.count())failures.push('Physics optional model-scope probe missing');
    else{
     const probe=probes.first();
     for(const [selector,value] of [['[data-g9-theta]','60'],['[data-g9-other]','1']])await probe.locator(selector).evaluate((e,v)=>{e.value=v;e.dispatchEvent(new Event('input',{bubbles:true}));},value);
     const output=await probe.locator('[data-g9-alignment-output]').textContent();
     if(!output.includes('0.500')||!output.includes('0.750'))failures.push('Physics model-scope numerical execution: '+output);
     await probe.screenshot({path:path.join(root,baseDir,'physics-model-probe.png')});
    }
   }
   pages.push({file,states,widget,geometry});
  }
  // Print from a distinct storage context, following the learner PDF policy.
  const printContext=await browser.newContext({viewport:{width:1280,height:900}}),printPage=await printContext.newPage();
  for(const row of pages){
   await printPage.goto(origin+'/'+[baseDir,group,'rendered',row.file].join('/'));
   const materialized=await printPage.locator('[data-g9-payload-slot] > *').count();
   if(materialized)failures.push(row.file+': a protected body is present in the fresh learner print');
   const pdf=row.file.replace('.html','.pdf');await printPage.emulateMedia({media:'print'});
   await printPage.pdf({path:path.join(dir,pdf),width:'280mm',height:'175mm',printBackground:true,margin:{top:'10mm',bottom:'10mm',left:'10mm',right:'10mm'}});
   receipt.pages.push({page:row.file,page_digest:'sha256:'+sha(path.join(dir,row.file)),pdf,pdf_digest:'sha256:'+sha(path.join(dir,pdf)),protected_bodies_materialized:materialized});await printPage.emulateMedia({media:'screen'});
  }
  fs.writeFileSync(path.join(dir,'print-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
  const broken=[];
  for(const row of pages){
   await page.goto(origin+'/'+[baseDir,group,'rendered',row.file].join('/'));
   for(const href of await page.locator('a[href],script[src],link[rel="stylesheet"]').evaluateAll(es=>es.map(e=>e.getAttribute('href')||e.getAttribute('src')))){
    if(!href||/^https?:|^mailto:/.test(href))continue;
    const url=new URL(href,page.url()),target=path.join(root,decodeURIComponent(url.pathname));
    if(!fs.existsSync(target))broken.push(row.file+': '+href);
    else if(url.hash&&target.endsWith('.html')){
     const id=decodeURIComponent(url.hash.slice(1));if(!fs.readFileSync(target,'utf8').includes('id="'+id+'"'))broken.push(row.file+': unresolved '+href);
    }
   }
  }
  if(broken.length)failures.push(...broken);
  for(const [file,expected] of Object.entries(binding))if(sha(path.join(dir,file))!==expected)failures.push('tested page changed: '+file);
  results.push({group,status:failures.length?'FAIL':'PASS',binding,pages,pdfs:receipt.pages,failures});
  await printContext.close();await context.close();console.log(group+': '+(failures.length?'FAIL':'PASS')+' '+failures.join('; '));
 }
 // Direct visual inspection artifacts for the first and last difficulty bands.
 const page=await browser.newPage({viewport:{width:820,height:1180}});
 for(const issue of [31,37]){
  await page.goto(origin+`/${baseDir}/../ISS${issue}/rendered/core1a.html`);
  const figure=page.locator('figure[data-g9-figure]').first();
  for(const button of await figure.locator('[data-g9-stage-goto]').all())await button.click();
  await figure.screenshot({path:path.join(root,baseDir,`ISS${issue}-final-figure.png`)});
 }
 await page.close();
}finally{await browser.close();server.close();}
fs.writeFileSync(path.join(root,baseDir,'supplement-browser.json'),JSON.stringify({schema:'issue29-subject-and-matrix-browser/v1',observed:'NEW_HTTP_CHROMIUM_EXECUTION',results,claim:'Mechanical subject/operator/packaging checks, not independent classification or learner validation.'},null,2)+'\n');
process.exitCode=results.every(r=>r.status==='PASS')?0:1;
