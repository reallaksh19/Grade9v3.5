(function(){
'use strict';

// Loads the generated Question Bank contracts and refuses to mix builds. It knows no subject, topic or
// resource: everything it loads is named by the manifest, and every artifact must carry the manifest's
// build id. Rendering belongs to the caller.

const script=(typeof document!=='undefined'&&document.currentScript)?document.currentScript:null;
const ROOT=script&&script.dataset&&script.dataset.siteRoot!==undefined?script.dataset.siteRoot:'../';
const inflight=new Map();
let generation=0;      // latest-wins for detail requests
let bootGeneration=0;  // latest-wins for bootstrap, independent of detail requests
let attempt=0;

const GLOBALS={
  catalog:'GRADE9_QUESTION_BANK_CATALOG',
  questions:'GRADE9_QUESTION_BANK_QUESTIONS',
  search:'GRADE9_QUESTION_BANK_SEARCH',
  resources:'GRADE9_QUESTION_BANK_RESOURCES'
};

function manifest(){return window.GRADE9_QUESTION_BANK_MANIFEST||null;}
function catalog(){return window.GRADE9_QUESTION_BANK_CATALOG||null;}
function questionList(){return window.GRADE9_QUESTION_BANK_QUESTIONS||null;}
function index(){return window.GRADE9_QUESTION_BANK_SEARCH||null;}
function resources(){return window.GRADE9_QUESTION_BANK_RESOURCES||null;}
function shardStore(){
  window.GRADE9_QUESTION_BANK_DETAIL_SHARDS=window.GRADE9_QUESTION_BANK_DETAIL_SHARDS||{};
  return window.GRADE9_QUESTION_BANK_DETAIL_SHARDS;
}

function failure(code,detail){
  const error=new Error(detail?code+': '+detail:code);
  error.code=code;
  return error;
}

function assertBuild(label,value,buildId){
  if(!value)return;
  if(value.build_id!==buildId){
    throw failure('QB_BUILD_MISMATCH','Question Bank build mismatch for '+label+': expected '+buildId+', got '+String(value.build_id||'missing'));
  }
}

function assertCoherence(){
  const m=manifest();
  if(!m||!m.build_id)throw failure('QB_MANIFEST_MISSING','Question Bank manifest is not loaded');
  assertBuild('catalog',catalog(),m.build_id);
  assertBuild('questions',questionList(),m.build_id);
  assertBuild('search',index(),m.build_id);
  assertBuild('resources',resources(),m.build_id);
  Object.entries(shardStore()).forEach(([id,value])=>assertBuild('detail shard '+id,value,m.build_id));
  return m.build_id;
}

function readiness(){
  const m=manifest();
  const buildId=m&&m.build_id;
  const ready=value=>!!(buildId&&value&&value.build_id===buildId);
  return {
    APP_SHELL_READY:true,
    CATALOG_READY:ready(catalog()),
    LIST_READY:ready(questionList()),
    SEARCH_READY:ready(index()),
    RESOURCES_READY:ready(resources()),
    STUDY_DETAIL_READY:Object.keys(shardStore()).length>0
  };
}

function norm(value){
  return String(value||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
}

// The index text never changes within a build, so normalise each document once, not once per query.
const haystacks=new WeakMap();
function haystack(doc){
  let text=haystacks.get(doc);
  if(text===undefined){text=norm(doc.search_text);haystacks.set(doc,text);}
  return text;
}

function search(query,filters){
  assertCoherence();
  const data=index();
  if(!data)throw failure('QB_SEARCH_NOT_LOADED','Question Bank search index is not loaded');
  const opts=filters||{};
  const terms=norm(query).split(/\s+/).filter(Boolean);
  return data.documents.filter(doc=>{
    if(opts.kind&&doc.kind!==opts.kind)return false;
    if(opts.subject_ref&&doc.subject_ref!==opts.subject_ref)return false;
    if(opts.topic_ref&&doc.topic_ref!==opts.topic_ref)return false;
    if(opts.difficulty&&doc.difficulty!==opts.difficulty)return false;
    if(!terms.length)return true;
    const hay=haystack(doc);
    return terms.every(term=>hay.includes(term));
  });
}

function documentById(id){
  const data=index();
  if(!data)return null;
  return data.documents.find(doc=>doc.id===id)||null;
}

function scriptPath(relative){
  if(/^(?:[a-z]+:)?\/\//i.test(relative)||relative.startsWith('/')){
    throw failure('QB_PATH_NOT_SITE_RELATIVE','Question Bank artifact path must remain site-relative');
  }
  return ROOT+relative;
}

// One script per path at a time. The build id in the URL keeps a cached artifact of another build from
// answering; attempt>0 also busts caches after a failure so Retry cannot replay the same bad response.
function loadScript(relative,buildId){
  if(inflight.has(relative))return inflight.get(relative);
  if(typeof document==='undefined')return Promise.reject(failure('QB_NO_DOCUMENT','Document API unavailable for Question Bank loading'));
  const query='?b='+encodeURIComponent(buildId)+(attempt?'&r='+attempt:'');
  const promise=new Promise((resolve,reject)=>{
    const node=document.createElement('script');
    node.src=scriptPath(relative)+query;
    node.async=true;
    node.dataset.qbArtifact=relative;
    node.onload=()=>resolve();
    node.onerror=()=>reject(failure('QB_ARTIFACT_FAILED','Question Bank artifact failed to load: '+relative));
    document.head.append(node);
  }).finally(()=>inflight.delete(relative));
  inflight.set(relative,promise);
  return promise;
}

let summaryIndex=null,summaryIndexOf=null;
function summaryById(id){
  const list=questionList();
  if(!list)return null;
  if(summaryIndexOf!==list){
    summaryIndex=new Map(list.questions.map(row=>[row.id,row]));
    summaryIndexOf=list;
  }
  return summaryIndex.get(id)||null;
}

// The list carries each question's subject, so Study does not wait for the search index.
function shardMetaForQuestion(id){
  const m=manifest();
  if(!m)return null;
  const row=summaryById(id);
  const doc=row?null:documentById(id);
  const subjectRef=row?row.subject_ref:(doc&&doc.kind==='question'?doc.subject_ref:null);
  if(!subjectRef)return null;
  return (m.detail_shards||[]).find(entry=>entry.subject_ref===subjectRef)||null;
}

function loadedShard(meta){
  if(!meta)return null;
  const value=shardStore()[meta.id]||null;
  if(value)assertBuild('detail shard '+meta.id,value,assertCoherence());
  return value;
}

function loadShard(meta){
  if(!meta)return Promise.reject(failure('QB_SHARD_UNKNOWN','Question Bank detail shard metadata is missing'));
  const present=loadedShard(meta);
  if(present)return Promise.resolve(present);
  const buildId=manifest()&&manifest().build_id;
  return loadScript(meta.path,buildId).then(()=>{
    const value=shardStore()[meta.id];
    if(!value)throw failure('QB_SHARD_UNREGISTERED','Question Bank detail shard did not register: '+meta.id);
    assertBuild('detail shard '+meta.id,value,assertCoherence());
    return value;
  }).catch(error=>{
    delete shardStore()[meta.id];
    throw error;
  });
}

function beginRequest(){generation+=1;return generation;}
function isCurrent(token){return token===generation;}

// Full detail for one question, from its subject's shard. Callers that show one thing at a time
// use loadQuestion (latest wins); callers that fill many placeholders use loadDetail.
async function loadDetail(id){
  assertCoherence();
  const meta=shardMetaForQuestion(id);
  if(!meta)throw failure('QB_NO_SHARD','No Question Bank detail shard registered for '+id);
  const shard=await loadShard(meta);
  const question=(shard.questions||[]).find(row=>row.id===id)||null;
  if(!question)throw failure('QB_SHARD_MISSING_QUESTION','Question Bank detail shard does not contain '+id);
  return question;
}

async function loadQuestion(id,token){
  const requestToken=token===undefined?beginRequest():token;
  const question=await loadDetail(id);
  if(!isCurrent(requestToken))return {stale:true,token:requestToken,question:null};
  return {stale:false,token:requestToken,question};
}

// Load one manifest-declared artifact and prove it belongs to the manifest's build.
async function loadArtifact(name){
  const m=manifest();
  const entry=m&&m.bootstrap&&m.bootstrap[name];
  const required=!entry||entry.required!==false;
  const outcome={name,required,ok:false,error:null};
  try{
    if(!entry)throw failure('QB_ARTIFACT_UNDECLARED','The manifest does not declare '+name);
    const key=GLOBALS[name];
    if(window[key]&&window[key].build_id!==m.build_id)delete window[key];
    if(!window[key])await loadScript(entry.path,m.build_id);
    const value=window[key];
    if(!value)throw failure('QB_ARTIFACT_MISSING',name+' did not register '+key);
    if(value.build_id!==m.build_id){
      delete window[key];
      throw failure('QB_BUILD_MISMATCH','Question Bank build mismatch for '+name+': expected '+m.build_id+', got '+String(value.build_id||'missing'));
    }
    outcome.ok=true;
  }catch(error){
    outcome.error=error;
  }
  return outcome;
}

// Catalog first, so navigation and counts can draw at once; then the list and search in parallel;
// resources are optional and never block the rest. A required failure rejects with a named code.
async function bootstrap(options){
  const opts=options||{};
  bootGeneration+=1;
  const token=bootGeneration;
  const current=()=>token===bootGeneration;
  const stage=name=>{if(typeof opts.onStage==='function'&&current())opts.onStage(name,readiness());};
  const m=manifest();
  if(!m||!m.build_id)throw failure('QB_MANIFEST_MISSING','Question Bank manifest is not loaded');
  const warnings=[];
  const settle=outcome=>{
    if(outcome.ok)return;
    if(outcome.required)throw outcome.error;
    warnings.push({name:outcome.name,code:outcome.error&&outcome.error.code,message:outcome.error&&outcome.error.message});
  };

  settle(await loadArtifact('catalog'));
  if(!current())return {stale:true,token,warnings};
  stage('CATALOG_READY');

  const [questionsResult,searchResult,resourcesResult]=await Promise.all([
    loadArtifact('questions'),loadArtifact('search'),loadArtifact('resources')
  ]);
  if(!current())return {stale:true,token,warnings};
  settle(questionsResult);
  stage('LIST_READY');
  settle(searchResult);
  stage('SEARCH_READY');
  settle(resourcesResult);
  if(resourcesResult.ok)stage('RESOURCES_READY');
  assertCoherence();
  return {stale:false,token,warnings,build_id:m.build_id};
}

// Retry after a failure: clear what is loaded so nothing from a bad attempt survives, and bust caches.
function reset(){
  attempt+=1;
  bootGeneration+=1;
  Object.values(GLOBALS).forEach(key=>{delete window[key];});
  window.GRADE9_QUESTION_BANK_DETAIL_SHARDS={};
}

window.Grade9QuestionBankData={
  version:'2.0.0',
  assertCoherence,
  readiness,
  bootstrap,
  reset,
  catalog,
  summaries:()=>{const value=questionList();return value?value.questions:[];},
  views:()=>{const value=catalog();return value&&value.views?value.views:[];},
  resources:()=>{const value=resources();return value?value.resources:[];},
  search,
  documentById,
  shardMetaForQuestion,
  summaryById,
  loadShard,
  loadDetail,
  loadQuestion,
  beginRequest,
  isCurrent
};
})();
