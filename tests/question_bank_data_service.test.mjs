import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

const buildId='sha256:fixture-build';
globalThis.window=globalThis;
globalThis.GRADE9_QUESTION_BANK_MANIFEST={
  build_id:buildId,
  detail_shards:[{
    id:'details:fixture:subject:1',
    subject_ref:'fixture:subject:1',
    path:'data/question-bank-details/fixture.js',
    question_count:1
  }]
};
globalThis.GRADE9_QUESTION_BANK_CATALOG={build_id:buildId,subjects:[],topics:[],subtopics:[]};
globalThis.GRADE9_QUESTION_BANK_RESOURCES={build_id:buildId,resources:[]};
globalThis.GRADE9_QUESTION_BANK_SEARCH={
  build_id:buildId,
  documents:[{
    id:'fixture:question:1',
    kind:'question',
    subject_ref:'fixture:subject:1',
    topic_ref:'fixture:topic:1',
    subtopic_refs:[],
    label:'Mitochondria release usable energy',
    difficulty:'D1',
    search_text:'mitochondria release usable energy cell respiration'
  }]
};
globalThis.GRADE9_QUESTION_BANK_DETAIL_SHARDS={
  'details:fixture:subject:1':{
    build_id:buildId,
    shard_id:'details:fixture:subject:1',
    subject_ref:'fixture:subject:1',
    questions:[{id:'fixture:question:1',stem:'Mitochondria release usable energy'}]
  }
};

await import(new URL('../public/js/question-bank-data-service.js', import.meta.url).href + '?test=' + Date.now());
const service=globalThis.Grade9QuestionBankData;
assert.ok(service);
assert.equal(service.assertCoherence(),buildId);
assert.equal(service.readiness().SEARCH_READY,true);
assert.equal(service.search('mitochondria').length,1);
assert.equal(service.search('mitochondria',{subject_ref:'fixture:subject:1'}).length,1);
assert.equal(service.search('mitochondria',{subject_ref:'fixture:subject:2'}).length,0);

// The normalised text is cached per document object: repeated queries agree, and a document from a
// newer index (a new object with different text) is never answered from an older document's cache.
assert.deepEqual(service.search('usable energy').map(d=>d.id),service.search('usable energy').map(d=>d.id));
const currentIndex=globalThis.GRADE9_QUESTION_BANK_SEARCH;
globalThis.GRADE9_QUESTION_BANK_SEARCH={
  ...currentIndex,
  documents:[{...currentIndex.documents[0],search_text:'chloroplast light reactions'}]
};
assert.equal(service.search('mitochondria').length,0);
assert.equal(service.search('chloroplast').length,1);
globalThis.GRADE9_QUESTION_BANK_SEARCH=currentIndex;
assert.equal(service.search('mitochondria').length,1);

const token=service.beginRequest();
const loaded=await service.loadQuestion('fixture:question:1',token);
assert.equal(loaded.stale,false);
assert.equal(loaded.question.id,'fixture:question:1');

const staleToken=service.beginRequest();
service.beginRequest();
const stale=await service.loadQuestion('fixture:question:1',staleToken);
assert.equal(stale.stale,true);
assert.equal(stale.question,null);

const originalSearch=globalThis.GRADE9_QUESTION_BANK_SEARCH;
globalThis.GRADE9_QUESTION_BANK_SEARCH={...originalSearch,build_id:'sha256:wrong-build'};
assert.throws(()=>service.assertCoherence(),/build mismatch/);
globalThis.GRADE9_QUESTION_BANK_SEARCH=originalSearch;

console.log('question_bank_data_service: PASS');
