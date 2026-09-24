import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import { existsSync, statSync } from "node:fs";
import { spawn, spawnSync } from "node:child_process";
import { dirname, extname, join, resolve, sep } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const repo=resolve(dirname(fileURLToPath(import.meta.url)),"..");
function chromePath(){const c=[];if(process.env.CHROMEWEBDRIVER)c.push(process.env.CHROMEWEBDRIVER,join(process.env.CHROMEWEBDRIVER,"chromedriver"));c.push("/usr/local/share/chromedriver-linux64/chromedriver");for(const p of c){try{if(existsSync(p)&&statSync(p).isFile())return p}catch(_){}}const w=spawnSync("which",["chromedriver"],{encoding:"utf8"});return w.status===0?w.stdout.trim():null}
async function port(){const s=createServer();await new Promise((ok,bad)=>{s.once("error",bad);s.listen(0,"127.0.0.1",ok)});const p=s.address().port;await new Promise(ok=>s.close(ok));return p}
async function driver(path){const p=await port(),child=spawn(path,["--port="+p,"--allowed-origins=*"],{stdio:["ignore","pipe","pipe"]}),base="http://127.0.0.1:"+p;for(let i=0;i<100;i+=1){try{if((await fetch(base+"/status")).ok)return{child,base}}catch(_){}await new Promise(r=>setTimeout(r,50))}child.kill("SIGTERM");throw new Error("ChromeDriver unavailable")}
async function server(){const mime=new Map([[".html","text/html"],[".js","text/javascript"],[".mjs","text/javascript"],[".json","application/json"],[".css","text/css"]]);const s=createServer(async(req,res)=>{try{const u=new URL(req.url||"/","http://127.0.0.1"),p=resolve(repo,"."+decodeURIComponent(u.pathname));if(!(p===repo||p.startsWith(repo+sep)))throw new Error();const info=await stat(p);if(!info.isFile())throw new Error();res.setHeader("content-type",mime.get(extname(p))||"application/octet-stream");res.setHeader("cache-control","no-store");res.end(await readFile(p))}catch(_){res.writeHead(404).end("not found")}});await new Promise((ok,bad)=>{s.once("error",bad);s.listen(0,"127.0.0.1",ok)});return{s,origin:"http://127.0.0.1:"+s.address().port}}
class D{constructor(base){this.base=base;this.id=null}async q(m,p,b){const r=await fetch(this.base+p,{method:m,headers:b===undefined?undefined:{"content-type":"application/json"},body:b===undefined?undefined:JSON.stringify(b)}),x=await r.json();if(!r.ok||x.value?.error)throw new Error(JSON.stringify(x.value||x));return x.value}async open(){const v=await this.q("POST","/session",{capabilities:{alwaysMatch:{browserName:"chrome","goog:chromeOptions":{args:["--headless=new","--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files","--window-size=390,820"]}}}});this.id=v.sessionId}async close(){if(this.id)try{await this.q("DELETE","/session/"+this.id)}catch(_){}}async nav(u){await this.q("POST","/session/"+this.id+"/url",{url:u})}async js(s,a=[]){return this.q("POST","/session/"+this.id+"/execute/sync",{script:s,args:a})}async wait(s,a=[],ms=12000){const t=Date.now();while(Date.now()-t<ms){if(await this.js(s,a))return;await new Promise(r=>setTimeout(r,60))}throw new Error("timeout: "+s)}}
const chrome=chromePath();if(!chrome&&process.env.GITHUB_ACTIONS==="true")throw new Error("Issue #259 browser proof requires ChromeDriver.");
async function use(fn){const w=await server(),p=await driver(chrome),d=new D(p.base);try{await d.open();await fn(d,w.origin)}finally{await d.close();p.child.kill("SIGTERM");await new Promise(r=>w.s.close(r))}}
const route=o=>o+"/public/physics/motion-2d/session/index.html";
async function attempt(d,sel,text){await d.js("const e=document.querySelector(arguments[0]),r=e.shadowRoot,i=r.querySelector('[data-attempt-input]');i.value=arguments[1];r.querySelector('[data-attempt-form]').dispatchEvent(new Event('submit',{bubbles:true,cancelable:true,composed:true}));",[sel,text])}
async function visual(d,projection){await d.js("const f=document.querySelector('#portable-frame'),w=f.contentDocument.querySelector('semantic-workbench'),r=w.shadowRoot;r.querySelector('[data-role=\"entity\"][data-projection-ref=\"'+arguments[0]+'\"]').click();r.querySelector('[data-role=\"target\"][data-target-ref=\"shared-clock-plane-state\"]').click();",[projection])}

test("Issue #259 real Chrome session preserves temporal protection, canonical outcomes and diagnostic privacy",{skip:!chrome,timeout:70000},async()=>{await use(async(d,o)=>{
  await d.nav(route(o));await d.wait("return Boolean(window.__motionSession?.identity);");
  const id=await d.js("return window.__motionSession.identity;");
  assert.deepEqual(id,{matrix_id:"MATRIX-PHY-KIN-2D-MOTION",rung:"R1",microtopic_ref:"MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",capability_ref:"CAP-KIN-2D-INDEPENDENT-COMPONENTS",core1b_projection_ref:"physics:mic-phy-kin-2d-independent-components:core1b",representation_ref:"REP-KIN-2D-SHARED-CLOCK",activity_ref:"ACT-KIN-2D-SHARED-CLOCK",portable_package_ref:"portable-motion-shared-clock",core2b_projection_ref:"physics:q-phy-kin-2d-2b-projectile-validity-04:core2b",core2b_source_ref:"Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04",atlas_contract_version:"2.0"});
  assert.equal(await d.js("return Boolean(document.querySelector('#projection-select'));"),false);
  assert.equal(await d.js("return document.querySelector('#core1b-learner').state.reconstructionVisible;"),false);
  assert.equal(await d.js("return document.querySelector('#core2b-learner').state.reasoningVisible;"),false);
  assert.doesNotMatch(await d.js("return document.querySelector('#core2b-learner').shadowRoot.innerHTML;"),/Reject the standard gravity-only projectile specialization/);

  await d.js("window.__motionSession.navigate('CORE1B');");await attempt(d,"#core1b-learner","   ");await d.wait("return window.__motionSession.trace.some(e=>e.event_type==='ATTEMPT_REJECTED');");
  assert.equal(await d.js("return document.querySelector('#core1b-learner').state.attemptCount;"),0);
  const a1="Separate axes, same physical clock.";await attempt(d,"#core1b-learner",a1);await d.wait("return document.querySelector('#core1b-learner').state.reconstructionVisible===true;");
  assert.equal((await d.js("return JSON.stringify(window.__motionSession.exportTraceObject());")).includes(a1),false);
  assert.equal(await d.js("return window.__motionSession.state.unlocked_stage;"),2);

  await d.js("window.__motionSession.__test.setPortableDelay(150);window.__motionSession.navigate('VISUAL');");
  assert.equal(await d.js("return window.__motionSession.trace.some(e=>e.reason_code==='PORTABLE_WAITING_FOR_DELAY');"),true);
  await d.wait("return window.__motionSession.state.visual_ready===true;");
  await visual(d,"shared-clock-mixed-time-candidate-projection");await d.wait("return window.__motionSession.state.visual_reject_count===1;");
  assert.match(await d.js("return document.querySelector('#visual-status').textContent;"),/single physical state/i);
  await visual(d,"shared-clock-same-time-candidate-projection");await d.wait("return window.__motionSession.state.visual_accept_count===1;");
  assert.match(await d.js("return document.querySelector('#visual-status').textContent;"),/shared physical instant|simultaneous/i);
  assert.equal(await d.js("return window.__motionSession.state.unlocked_stage;"),3);

  const mx=await d.js("return Math.max(...window.__motionSession.trace.map(e=>e.diagnostic_facts?.source_sequence||0));");
  await d.js("window.__motionSession.__test.ingestPortableEvent({type:'TRANSFER_REJECTED'},arguments[0]);window.__motionSession.__test.ingestPortableEvent({type:'TRANSFER_REJECTED'},arguments[0]-1);",[mx]);
  const codes=await d.js("return window.__motionSession.trace.filter(e=>e.event_type==='PORTABLE_EVENT_REJECTED').map(e=>e.reason_code);");
  assert.ok(codes.includes("PORTABLE_EVENT_DUPLICATE"));assert.ok(codes.includes("PORTABLE_EVENT_OUT_OF_ORDER"));

  await d.js("window.__motionSession.navigate('CORE2B');window.__motionSession.navigate('VISUAL');window.__motionSession.navigate('CORE2B');");
  assert.equal(await d.js("return document.querySelector('#core2b-learner').state.reasoningVisible;"),false);
  await d.js("const e=document.querySelector('#core2b-learner'),b=e.shadowRoot.querySelector('[data-action=\"support\"]');if(b)b.click();");
  assert.doesNotMatch(await d.js("return document.querySelector('#core2b-learner').shadowRoot.innerHTML;"),/Reject the standard gravity-only projectile specialization/);
  const a2="Check the changed post-release interaction before choosing the familiar model.";await attempt(d,"#core2b-learner",a2);await d.wait("return document.querySelector('#core2b-learner').state.reasoningVisible===true;");
  assert.match(await d.js("return document.querySelector('#core2b-learner').shadowRoot.innerHTML;"),/Reject the standard gravity-only projectile specialization/);
  assert.equal((await d.js("return JSON.stringify(window.__motionSession.exportTraceObject());")).includes(a2),false);

  await d.js("window.__motionSession.navigate('SUMMARY');");await d.wait("return window.__motionSession.state.completed===true;");
  const out=await d.js("return window.__motionSession.exportTraceObject();");assert.equal(out.replay.ok,true);assert.deepEqual(out.privacy,{response_text_recorded:false,pii_recorded:false,network_telemetry:false});
  assert.equal(out.events.every(e=>e.invariant_checks.every(c=>c.pass)),true);
  assert.ok(out.events.some(e=>e.event_type==="VISUAL_ACTION_RESOLVED"&&e.outcome==="ACCEPT"&&e.correlation));
  assert.ok(out.events.some(e=>e.event_type==="VISUAL_ACTION_RESOLVED"&&e.outcome==="REJECT"&&e.correlation));
  assert.match(await d.js("return document.querySelector('#session-summary').textContent;"),/does not claim mastery or readiness/i);

  const n=out.events.length;await d.js("window.__motionSession.retry();");assert.equal(await d.js("return window.__motionSession.state.stage;"),"CORE1B");assert.equal(await d.js("return document.querySelector('#core1b-learner').state.attemptCount;"),0);
  const last=await d.js("return window.__motionSession.trace.slice(-1)[0];");assert.equal(last.event_type,"RECOVERY_STARTED");assert.equal(last.run_id,"run-0002");assert.equal(last.parent_run_id,"run-0001");assert.ok((await d.js("return window.__motionSession.trace.length;"))>n);
  await attempt(d,"#core1b-learner","Clean retry.");await d.wait("return document.querySelector('#core1b-learner').state.reconstructionVisible===true;");await d.js("window.__motionSession.reset();");
  assert.equal(await d.js("return window.__motionSession.state.stage;"),"ORIENT");assert.equal(await d.js("return document.querySelector('#core1b-learner').state.attemptCount;"),0);
})});

test("Issue #259 fails closed for unknown identity and package load failure",{skip:!chrome,timeout:45000},async()=>{await use(async(d,o)=>{
  await d.nav(route(o)+"?case=unknown");await d.wait("return document.querySelector('#session-unavailable')?.hidden===false;");
  assert.match(await d.js("return document.querySelector('#unavailable-code').textContent;"),/SESSION_ATLAS_SELECTION_UNAVAILABLE/);
  await d.nav(route(o));await d.wait("return Boolean(window.__motionSession?.identity);");await d.js("window.__motionSession.navigate('CORE1B');");await attempt(d,"#core1b-learner","One clock remains shared.");await d.wait("return window.__motionSession.state.unlocked_stage>=2;");
  await d.js("window.__motionSession.__test.setPortablePackage('missing-package');window.__motionSession.navigate('VISUAL');");await d.wait("return window.__motionSession.trace.some(e=>e.event_type==='PORTABLE_LOAD_FAILED');");
  assert.match(await d.js("return document.querySelector('#visual-status').textContent;"),/PORTABLE_PACKAGE_LOAD_FAILED/);
})});

test("Issue #259 offline selected-session route completes without network academic lookup",{skip:!chrome,timeout:70000},async()=>{
  const p=await driver(chrome),d=new D(p.base);try{await d.open();await d.nav(pathToFileURL(join(repo,"standalone/motion-shared-clock-session/index.html")).href);await d.wait("return Boolean(window.__motionSession?.identity);",[],15000);
  assert.equal(await d.js("return window.__motionSession.trace[0].host_mode;"),"offline");
  await d.js("window.__motionSession.navigate('CORE1B');");await attempt(d,"#core1b-learner","Both components refer to one instant.");await d.wait("return window.__motionSession.state.unlocked_stage>=2;");
  await d.js("window.__motionSession.navigate('VISUAL');");await d.wait("return window.__motionSession.state.visual_ready===true;",[],15000);
  await visual(d,"shared-clock-mixed-time-candidate-projection");await d.wait("return window.__motionSession.state.visual_reject_count===1;");await visual(d,"shared-clock-same-time-candidate-projection");await d.wait("return window.__motionSession.state.visual_accept_count===1;");
  await d.js("window.__motionSession.navigate('CORE2B');");await attempt(d,"#core2b-learner","Check the changed interaction against the familiar model conditions.");await d.wait("return window.__motionSession.state.unlocked_stage>=4;");await d.js("window.__motionSession.navigate('SUMMARY');");await d.wait("return window.__motionSession.state.completed===true;");
  assert.equal(await d.js("return window.__motionSession.exportTraceObject().replay.ok;"),true);
  const protocols=await d.js("return performance.getEntriesByType('resource').map(e=>{try{return new URL(e.name).protocol}catch(_){return 'unknown:'}});");assert.equal(protocols.some(x=>x==="http:"||x==="https:"),false);
  await d.js("window.__motionSession.retry();");await attempt(d,"#core1b-learner","Offline retry.");await d.wait("return window.__motionSession.state.unlocked_stage>=2;");await d.js("window.__motionSession.__test.setPortablePackage('missing-offline-package');window.__motionSession.navigate('VISUAL');");await d.wait("return window.__motionSession.trace.some(e=>e.event_type==='PORTABLE_LOAD_FAILED'&&e.run_id==='run-0002');");
  assert.match(await d.js("return document.querySelector('#visual-status').textContent;"),/PORTABLE_PACKAGE_LOAD_FAILED/);
  }finally{await d.close();p.child.kill("SIGTERM")}
});
