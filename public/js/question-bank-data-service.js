(function(){
'use strict';

const script=(typeof document!=='undefined'&&document.currentScript)?document.currentScript:null;
const ROOT=script&&script.dataset.siteRoot!==undefined?script.dataset.siteRoot:'../';
const inflight=new Map();
let generation=0;

function manifest(){return window.GRADE9_QUESTION_BANK_MANIFEST||null;}
function catalog(){return window.GRADE9_QUESTION_BANK_CATALOG||null;}
function index(){return window.GRADE9_QUESTION_BANK_SEARCH||null;}
function resources(){return window.GRADE9_QUESTION_BANK_RESOURCES||null;}
function shardStore(){
  window.GRADE9_QUESTION_BANK_DETAIL_SHARDS=window.GRADE9_QUESTION_BANK_DETAIL_SHARDS||{};
  return window.GRADE9_QUESTION_BANK_DETAIL_SHARDS;
}

function assertBuild(label,value,buildId){
  if(!value)return;
  if(value.build_id!==buildId){
    throw new Error('Question Bank build mismatch for '+label+': expected '+buildId+', got '+String(value.build_id||'missing'));
  }
}

function assertCoherence(){
  const m=manifest();
  if(!m||!m.build_id)throw new Error('Question Bank manifest is not loaded');
  assertBuild('catalog',catalog(),m.build_id);
  assertBuild('search',index(),m.build_id);
  assertBuild('resources',resources(),m.build_id);
  Object.entries(shardStore()).forEach(([id,value])=>assertBuild('detail shard '+id,value,m.build_id));
  return m.build_id;
}

function readiness(){
  const m=manifest();
  const buildId=m&&m.build_id;
  const c=catalog(),s=index(),r=resources();
  return {
    APP_SHELL_READY:true,
    CATALOG_READY:!!(buildId&&c&&c.build_id===buildId),
    SEARCH_READY:!!(buildId&&s&&s.build_id===buildId),
    RESOURCES_READY:!!(buildId&&r&&r.build_id===buildId),
    STUDY_DETAIL_READY:Object.keys(shardStore()).length>0
  };
}

function norm(value){
  return String(value||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
}

function search(query,filters){
  assertCoherence();
  const data=index();
  if(!data)throw new Error('Question Bank search index is not loaded');
  const opts=filters||{};
  const terms=norm(query).split(/\s+/).filter(Boolean);
  return data.documents.filter(doc=>{
    if(opts.kind&&doc.kind!==opts.kind)return false;
    if(opts.subject_ref&&doc.subject_ref!==opts.subject_ref)return false;
    if(opts.topic_ref&&doc.topic_ref!==opts.topic_ref)return false;
    if(opts.difficulty&&doc.difficulty!==opts.difficulty)return false;
    if(!terms.length)return true;
    const hay=norm(doc.search_text);
    return terms.every(term=>hay.includes(term));
  });
}

function documentById(id){
  const data=index();
  if(!data)return null;
  return data.documents.find(doc=>doc.id===id)||null;
}

function shardMetaForQuestion(id){
  const m=manifest();
  const doc=documentById(id);
  if(!m||!doc||doc.kind!=='question')return null;
  return (m.detail_shards||[]).find(row=>row.subject_ref===doc.subject_ref)||null;
}

function loadedShard(meta){
  if(!meta)return null;
  const value=shardStore()[meta.id]||null;
  if(value)assertBuild('detail shard '+meta.id,value,assertCoherence());
  return value;
}

function scriptPath(relative){
  if(/^(?:[a-z]+:)?\/\//i.test(relative)||relative.startsWith('/')){
    throw new Error('Question Bank shard path must remain site-relative');
  }
  return ROOT+relative;
}

function loadShard(meta){
  if(!meta)return Promise.reject(new Error('Question Bank detail shard metadata is missing'));
  const present=loadedShard(meta);
  if(present)return Promise.resolve(present);
  if(inflight.has(meta.path))return inflight.get(meta.path);
  if(typeof document==='undefined')return Promise.reject(new Error('Document API unavailable for Question Bank shard loading'));

  const promise=new Promise((resolve,reject)=>{
    const node=document.createElement('script');
    node.src=scriptPath(meta.path);
    node.async=true;
    node.dataset.qbDetailShard=meta.id;
    node.onload=()=>{
      try{
        const value=shardStore()[meta.id];
        if(!value)throw new Error('Question Bank detail shard did not register: '+meta.id);
        assertBuild('detail shard '+meta.id,value,assertCoherence());
        resolve(value);
      }catch(error){reject(error);}
    };
    node.onerror=()=>reject(new Error('Question Bank detail shard failed to load: '+meta.path));
    document.head.append(node);
  }).finally(()=>inflight.delete(meta.path));
  inflight.set(meta.path,promise);
  return promise;
}

function beginRequest(){generation+=1;return generation;}
function isCurrent(token){return token===generation;}

async function loadQuestion(id,token){
  const requestToken=token===undefined?beginRequest():token;
  assertCoherence();
  const meta=shardMetaForQuestion(id);
  if(!meta)throw new Error('No Question Bank detail shard registered for '+id);
  const shard=await loadShard(meta);
  if(!isCurrent(requestToken))return {stale:true,token:requestToken,question:null};
  const question=(shard.questions||[]).find(row=>row.id===id)||null;
  if(!question)throw new Error('Question Bank detail shard does not contain '+id);
  return {stale:false,token:requestToken,question};
}

window.Grade9QuestionBankData={
  version:'1.0.0',
  assertCoherence,
  readiness,
  search,
  documentById,
  shardMetaForQuestion,
  loadShard,
  loadQuestion,
  beginRequest,
  isCurrent
};
})();
