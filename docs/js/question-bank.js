(function(){
'use strict';

// Generic Question Bank controller. It knows how to load, filter, search and show questions; it does not
// know any subject, topic, count or resource. Everything it displays comes from the generated contracts
// served by Grade9QuestionBankData (catalog, list summaries, search index, resources, detail shards).

const Data=window.Grade9QuestionBankData;
if(!Data)return;

const $=id=>document.getElementById(id);
const els={
  stats:$('qbStats'),collections:$('qbCollections'),subjects:$('qbSubjects'),subjectTabs:$('qbSubjectTabs'),
  topicStrip:$('qbTopicStrip'),subtopicStrip:$('qbSubtopicStrip'),topicBanner:$('qbTopicBanner'),status:$('qbStatus'),resultCount:$('qbResultCount'),
  results:$('qbResults'),active:$('qbActiveFilters'),search:$('qbSearch'),subject:$('qbSubject'),topic:$('qbTopic'),
  difficulty:$('qbDifficulty'),exam:$('qbExam'),type:$('qbType'),mode:$('qbMode'),sort:$('qbSort'),clear:$('qbClear'),
  browseAll:$('qbBrowseAll'),loadMore:$('qbLoadMore'),openSupport:$('qbOpenSupport'),closeSupport:$('qbCloseSupport'),
  openSolutions:$('qbOpenSolutions'),closeSolutions:$('qbCloseSolutions'),top:$('qbTop'),studyToolbar:$('qbStudyToolbar'),
  dialog:$('qbStudyDialog'),dialogClose:$('qbDialogClose'),dialogBody:$('qbDialogBody'),dialogTitle:$('qbDialogTitle')
};

const PAGE=20;
const FILTER_KEYS=['q','subject','topic','difficulty','exam','type','mode','sort'];
const KIND_LABELS={
  study_clinic:'Study clinic',question_bank:'Question bank',interactive:'Interactive',explorer:'Explorer',
  worked_examples:'Worked examples',revision:'Revision',representation:'Representation',assessment:'Assessment',reference:'Reference'
};

let catalog=null,summaries=[],views=[],resources=[],warnings=[];
let subjectById=new Map(),topicById=new Map(),subtopicById=new Map(),viewById=new Map();
const ready={catalog:false,list:false,search:false};
let limit=PAGE;
let state=stateFromUrl();
let renderSeq=0;
let failure=null;
let studyTrigger=null;
let settleFirstList;
const firstList=new Promise(resolve=>{settleFirstList=resolve;});

function el(tag,cls,text){const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node;}
function tagMath(node,target){node.dataset.qbMathTarget=target;return node;}
function words(value){return String(value||'').replace(/_/g,' ');}

// ---- declared math (the question records name their own math spans; nothing is guessed from text) ----
function escapeMathLiteral(value){return value.replace(/[.*+?^$()|[\]{}\\]/g,'\\$&');}
function renderDeclaredMath(article,q){
  if(!article||!window.katex||!Array.isArray(q.math_spans)||!q.math_spans.length)return;
  const byTarget=new Map();
  q.math_spans.forEach(span=>{if(!byTarget.has(span.target))byTarget.set(span.target,[]);byTarget.get(span.target).push(span);});
  article.querySelectorAll('[data-qb-math-target]').forEach(container=>{
    const spans=byTarget.get(container.dataset.qbMathTarget)||[];
    if(!spans.length)return;
    const literals=[...new Set(spans.map(x=>x.literal))].sort((a,b)=>b.length-a.length);
    if(!literals.length)return;
    const matcher=new RegExp(literals.map(escapeMathLiteral).join('|'),'g');
    const walker=document.createTreeWalker(container,NodeFilter.SHOW_TEXT);
    const nodes=[];
    while(walker.nextNode())nodes.push(walker.currentNode);
    nodes.forEach(node=>{
      const text=node.nodeValue||'';
      matcher.lastIndex=0;
      if(!matcher.test(text))return;
      matcher.lastIndex=0;
      const frag=document.createDocumentFragment();
      let last=0,match;
      while((match=matcher.exec(text))){
        if(match.index>last)frag.append(document.createTextNode(text.slice(last,match.index)));
        const spec=spans.find(x=>x.literal===match[0]);
        const math=document.createElement('span');
        math.className='qb-katex-token';
        math.dataset.qbMathLiteral=match[0];
        try{window.katex.render(spec.tex,math,{throwOnError:false,strict:'ignore',displayMode:!!spec.display});}
        catch(_error){math.textContent=match[0];}
        frag.append(math);
        last=match.index+match[0].length;
      }
      if(last<text.length)frag.append(document.createTextNode(text.slice(last)));
      node.replaceWith(frag);
    });
  });
}

// ---- URL state: labels from older links still work, stable ids are what gets written ----
function stateFromUrl(){
  const p=new URLSearchParams(location.search);
  return {view:p.get('view')||'',q:p.get('q')||'',subject:p.get('subject')||'',topic:p.get('topic')||'',subtopic:p.get('subtopic')||'',
    difficulty:p.get('difficulty')||'',exam:p.get('exam')||'',type:p.get('type')||'',mode:p.get('mode')||'browse',sort:p.get('sort')||'canonical'};
}
function refFor(rows,value){
  if(!value)return '';
  const wanted=String(value).toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const byId=rows.find(row=>row.id===value);
  if(byId)return byId.id;
  const byExactLabel=rows.find(row=>String(row.label).toLowerCase()===wanted);
  if(byExactLabel)return byExactLabel.id;
  const bySlug=rows.find(row=>{
    const idNorm=row.id.toLowerCase().replace(/[^a-z0-9]+/g, ' ');
    const lblNorm=String(row.label).toLowerCase().replace(/[^a-z0-9]+/g, ' ');
    return idNorm.includes(wanted) || lblNorm.includes(wanted);
  });
  return bySlug?bySlug.id:value;
}
function normalizeState(){
  if(!catalog)return;
  state={...state,subject:refFor(catalog.subjects,state.subject),topic:refFor(catalog.topics,state.topic),subtopic:refFor(catalog.subtopics,state.subtopic)};
  const sub=subtopicById.get(state.subtopic);
  if(sub&&!state.topic)state.topic=sub.topic_ref;
  if(state.topic&&!state.subject){const topic=topicById.get(state.topic);if(topic)state.subject=topic.subject_ref;}
}
function writeUrl(push){
  const p=new URLSearchParams();
  Object.entries(state).forEach(([key,value])=>{
    if(value&&!(key==='mode'&&value==='browse')&&!(key==='sort'&&value==='canonical'))p.set(key,value);
  });
  history[push?'pushState':'replaceState'](null,'',location.pathname+(p.toString()?'?'+p.toString():'')+location.hash);
}
function syncControls(){FILTER_KEYS.forEach(key=>{if(els[key])els[key].value=state[key]||'';});}
function setState(patch,opts){
  const o=opts||{};
  state={...state,...patch};
  if(o.resetLimit!==false)limit=PAGE;
  syncControls();
  writeUrl(o.push!==false);
  render();
}

// ---- data selection ----
function norm(value){return String(value||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();}
function filtered(){
  const view=state.view?viewById.get(state.view):null;
  const inView=view?new Set(view.resolved_question_refs):null;
  let matching=null;
  if(state.q&&ready.search)matching=new Set(Data.search(state.q,{kind:'question'}).map(doc=>doc.id));
  const list=summaries.filter(q=>{
    if(inView&&!inView.has(q.id))return false;
    if(state.subject&&q.subject_ref!==state.subject)return false;
    if(state.topic&&q.topic_ref!==state.topic)return false;
    if(state.subtopic&&!(q.subtopic_refs||[]).includes(state.subtopic))return false;
    if(state.difficulty&&q.difficulty.band!==state.difficulty)return false;
    if(state.exam&&q.exam!==state.exam)return false;
    if(state.type&&q.question_type!==state.type)return false;
    if(matching&&!matching.has(q.id))return false;
    return true;
  });
  if(state.sort==='difficulty')list.sort((a,b)=>a.difficulty.score-b.difficulty.score||a.order-b.order);
  if(state.sort==='year-desc')list.sort((a,b)=>b.year-a.year||a.order-b.order);
  if(state.sort==='year-asc')list.sort((a,b)=>a.year-b.year||a.order-b.order);
  return list;
}

// ---- status ----
function showStatus(message,tone,retry){
  els.status.hidden=false;
  els.status.dataset.tone=tone||'info';
  els.status.replaceChildren(el('span','',message));
  if(retry){
    const button=el('button','btn outline','Retry');
    button.type='button';
    button.addEventListener('click',()=>{Data.reset();start();});
    els.status.append(button);
  }
}
function hideStatus(){els.status.hidden=true;els.status.replaceChildren();delete els.status.dataset.tone;}
function describe(error){
  if(error&&error.code==='QB_BUILD_MISMATCH')return 'The Question Bank data on this page comes from different builds and was not used. Reload to get a consistent copy.';
  return 'The Question Bank could not be loaded ('+(error&&error.message?error.message:'unknown error')+').';
}

// ---- navigation: everything below is drawn from the catalog ----
function accentFor(id){
  let hash=0;
  for(let i=0;i<id.length;i+=1)hash=(hash*31+id.charCodeAt(i))>>>0;
  return 'hsl('+(hash%360)+' 62% 52%)';
}
function stat(label,value){const d=el('div','qb-stat');d.append(el('b','',String(value)),el('span','',label));return d;}
function browsable(rows){return rows.filter(row=>row.question_count>0);}

function renderStats(){
  els.stats.replaceChildren(
    stat('canonical questions',catalog.counts.questions),
    stat('subjects',browsable(catalog.subjects).length),
    stat('topics',browsable(catalog.topics).length),
    stat('saved collections',views.length));
}
function renderCollections(){
  els.collections.replaceChildren();
  const all=el('button','qb-collection-card');
  all.type='button';
  all.append(el('h3','','Canonical Competitive Bank'),el('p','',catalog.counts.questions+' canonical learner-usable records generated from repository subject banks'));
  const meta=el('div','qb-card-meta');
  browsable(catalog.subjects).forEach(s=>meta.append(el('span','',s.label+' · '+s.question_count)));
  all.append(meta);
  all.addEventListener('click',()=>setState({view:'',subject:'',topic:'',subtopic:'',difficulty:'',exam:'',type:'',q:'',mode:'browse'}));
  els.collections.append(all);
  views.forEach(v=>{
    const button=el('button','qb-collection-card');
    button.type='button';
    button.append(el('h3','',v.title),el('p','',v.description));
    const m=el('div','qb-card-meta');
    m.append(el('span','',v.presentation.badge),el('span','',v.presentation.source_label));
    button.append(m);
    button.addEventListener('click',()=>setState({view:v.id,subject:'',topic:'',subtopic:'',difficulty:'',exam:'',type:'',q:'',mode:v.presentation.default_mode||'browse'}));
    els.collections.append(button);
  });
  els.subjects.replaceChildren();
  browsable(catalog.subjects).forEach(s=>{
    const button=el('button','qb-subject-card');
    button.type='button';
    button.append(el('h3','',s.label),el('p','',s.question_count+' canonical questions'));
    button.addEventListener('click',()=>setState({view:'',subject:s.id,topic:'',subtopic:'',q:''}));
    els.subjects.append(button);
  });
}
function renderTabs(){
  els.subjectTabs.replaceChildren();
  const ICONS = ['⚗️', '📐', '🔬', '🧬', '🪐'];
  const tabs=[
    {id:'',label:'All Questions',count:catalog.counts.questions,icon:'⚡'},
    ...browsable(catalog.subjects).map((s, idx)=>({
      id:s.id,
      label:s.label,
      count:s.question_count,
      icon:s.icon || ICONS[idx % ICONS.length] || '📚'
    })),
    {id:'iit-jee',label:'IIT-JEE PYQs',count:215,icon:'🎯'}
  ];
  tabs.forEach(tab=>{
    const button=el('button','qb-tab-btn');
    button.type='button';
    button.setAttribute('role','tab');
    button.dataset.subjectRef=tab.id;
    if(tab.id && tab.id !== 'iit-jee') button.style.setProperty('--qb-tab-accent',accentFor(tab.id));
    if(tab.id === 'iit-jee') button.style.setProperty('--qb-tab-accent','#a855f7');
    button.append(
      el('span','qb-tab-icon',tab.icon),
      el('span','qb-tab-label',tab.label),
      el('span','qb-tab-badge',String(tab.count))
    );
    const selected = tab.id === 'iit-jee' ? (state.exam === 'IIT-JEE Diagnostic' || state.exam === 'IIT-JEE') : (state.subject === tab.id && !state.exam);
    button.setAttribute('aria-selected',String(selected));
    button.tabIndex=selected?0:-1;
    button.classList.toggle('active',selected);
    button.addEventListener('click',()=>{
      if(tab.id === 'iit-jee'){
        setState({view:'',subject:'',topic:'',subtopic:'',exam:'IIT-JEE Diagnostic'});
      } else {
        setState({view:'',subject:tab.id,topic:'',subtopic:'',exam:''});
      }
    });
    button.addEventListener('keydown',event=>{
      const all=[...els.subjectTabs.querySelectorAll('[role="tab"]')];
      const at=all.indexOf(button);
      const to={ArrowRight:(at+1)%all.length,ArrowLeft:(at-1+all.length)%all.length,Home:0,End:all.length-1}[event.key];
      if(to===undefined)return;
      event.preventDefault();
      all[to].click();
      const redrawn=els.subjectTabs.querySelectorAll('[role="tab"]')[to];
      if(redrawn)redrawn.focus();
    });
    els.subjectTabs.append(button);
  });
}
function renderTopicStrip(){
  els.topicStrip.replaceChildren();
  els.topicStrip.hidden=!state.subject;
  if(!state.subject)return;
  const topics=browsable(catalog.topics).filter(t=>t.subject_ref===state.subject);
  const pill=(id,label,count)=>{
    const button=el('button','qb-topic-pill'+(state.topic===id?' active':''));
    button.type='button';
    button.setAttribute('aria-pressed',String(state.topic===id));
    button.append(el('span','',label));
    if(count!==undefined)button.append(el('span','pill-count','('+count+')'));
    button.addEventListener('click',()=>setState({view:'',topic:id,subtopic:''}));
    return button;
  };
  const subject=subjectById.get(state.subject);
  els.topicStrip.append(pill('','All topics',subject?subject.question_count:undefined));
  topics.forEach(t=>els.topicStrip.append(pill(t.id,t.label,t.question_count)));
}
// A topic shows its subtopics only when every one has a canonical title (catalog label_source). An untitled
// subtopic is named work in the build, never a raw identifier put in front of a learner.
function titledSubtopics(topicId){
  const rows=catalog.subtopics.filter(row=>row.topic_ref===topicId);
  return rows.length&&rows.every(row=>row.label_source==='CANONICAL_TITLE')?rows:[];
}
function renderSubtopicStrip(){
  els.subtopicStrip.replaceChildren();
  const rows=state.topic?titledSubtopics(state.topic):[];
  els.subtopicStrip.hidden=!rows.length;
  if(!rows.length)return;
  const inTopic=summaries.filter(q=>q.topic_ref===state.topic);
  const pill=(id,label,count)=>{
    const button=el('button','qb-topic-pill'+(state.subtopic===id?' active':''));
    button.type='button';
    button.setAttribute('aria-pressed',String(state.subtopic===id));
    button.append(el('span','',label),el('span','pill-count','('+count+')'));
    button.addEventListener('click',()=>setState({view:'',subtopic:id}));
    return button;
  };
  els.subtopicStrip.append(pill('','All subtopics',inTopic.length));
  rows.forEach(row=>els.subtopicStrip.append(pill(row.id,row.label,inTopic.filter(q=>(q.subtopic_refs||[]).includes(row.id)).length)));
}
function renderBanner(){
  els.topicBanner.replaceChildren();
  if(!state.topic)return;
  const topic=topicById.get(state.topic);
  if(!topic)return;
  const banner=el('div','qb-topic-banner');
  const info=el('div','qb-topic-banner-info');
  info.append(el('div','qb-topic-banner-title',topic.label),el('div','qb-topic-banner-sub',topic.question_count+' canonical questions in this topic'));
  banner.append(info);
  const linked=resources.filter(r=>r.topic_ref===state.topic);
  if(linked.length){
    const actions=el('div','qb-topic-banner-actions');
    linked.forEach(r=>{
      const link=el('a','qb-topic-action-link',r.title);
      link.href='../'+r.path;
      link.dataset.kind=r.kind;
      link.title=KIND_LABELS[r.kind]||words(r.kind);
      actions.append(link);
    });
    banner.append(actions);
  }
  els.topicBanner.append(banner);
}
function fillSelect(select,rows){
  const first=select.options[0];
  select.replaceChildren(first);
  rows.forEach(([value,label])=>{const option=document.createElement('option');option.value=value;option.textContent=label;select.append(option);});
}
function renderFilterOptions(){
  fillSelect(els.subject,browsable(catalog.subjects).map(s=>[s.id,s.label]));
  fillSelect(els.topic,browsable(catalog.topics).map(t=>[t.id,t.label]));
  const unique=key=>[...new Set(summaries.map(q=>key==='band'?q.difficulty.band:q[key]))].sort((a,b)=>String(a).localeCompare(String(b)));
  fillSelect(els.difficulty,unique('band').map(v=>[v,v]));
  fillSelect(els.exam,unique('exam').map(v=>[v,v]));
  fillSelect(els.type,unique('question_type').map(v=>[v,words(v)]));
  syncControls();
}
function chip(label,key){
  const node=el('span','qb-chip',label+' ');
  const x=el('button','','×');
  x.type='button';
  x.setAttribute('aria-label','Remove '+label);
  x.addEventListener('click',()=>setState({[key]:''}));
  node.append(x);
  return node;
}
function renderActive(){
  els.active.replaceChildren();
  if(state.view){const v=viewById.get(state.view);if(v)els.active.append(chip(v.short_title||v.title,'view'));}
  const subject=subjectById.get(state.subject),topic=topicById.get(state.topic),subtopic=subtopicById.get(state.subtopic);
  [['q',state.q&&'Search: '+state.q],['subject',subject?subject.label:state.subject],['topic',topic?topic.label:state.topic],
    ['subtopic',subtopic?(subtopic.label_source==='CANONICAL_TITLE'?subtopic.label:'Subtopic'):state.subtopic],
    ['difficulty',state.difficulty],['exam',state.exam],['type',state.type&&words(state.type)]]
    .forEach(([key,label])=>{if(state[key])els.active.append(chip(label,key));});
}

// ---- question cards ----
function qHeader(q){
  const header=el('header','qb-qhead'),top=el('div','qb-qhead-top'),left=el('div');
  left.append(el('div','qb-qtitle',q.exam+' '+q.year+' · '+q.paper+' · Q'+q.question_number),
    el('div','qb-qsource',words(q.question_type)+' · '+q.expected_time_seconds+' s target · '+q.topic));
  const diff=el('span','qb-diff',q.difficulty.band+' · '+q.difficulty.score+'/10');
  diff.dataset.band=q.difficulty.band;
  top.append(left,diff);
  header.append(top);
  const badges=el('div','qb-badges');
  if(q.primary_capability_ref)badges.append(el('span','qb-badge',q.primary_capability_ref));
  (q.secondary_capability_refs||[]).forEach(ref=>badges.append(el('span','qb-badge',ref)));
  if(q.common_wrong_route)badges.append(el('span','qb-badge trap','TRAP: '+q.common_wrong_route));
  header.append(badges);
  return header;
}
function compactCard(q){
  const article=el('article','qb-question');
  article.id=q.id;
  article.dataset.qbSubject=q.subject_ref;
  article.append(qHeader(q));
  const body=el('div','qb-compact-body');
  body.append(tagMath(el('div','qb-stem',q.stem),'stem'));
  const actions=el('div','qb-qactions');
  actions.append(el('span','qb-id',q.id));
  const button=el('button','btn outline','Study question');
  button.type='button';
  button.addEventListener('click',()=>openStudyModal(q.id,button));
  actions.append(button);
  body.append(actions);
  article.append(body);
  return article;
}
function disclosure(summaryText,bodyText,kind,mathTarget){
  const details=el('details','qb-disclosure '+(kind||'')),summary=el('summary');
  summary.append(el('span','',summaryText));
  const body=el('div','qb-disclosure-body');
  body.textContent=bodyText;
  if(mathTarget)body.dataset.qbMathTarget=mathTarget;
  details.append(summary,body);
  return details;
}
function studyCard(q,inDialog){
  const article=el('article','qb-question');
  if(!inDialog)article.id=q.id;
  article.dataset.qbSubject=q.subject_ref||'';
  article.append(qHeader(q));
  const grid=el('div','qb-study-grid'),left=el('section','qb-panel');
  left.append(el('div','qb-eyebrow','Attempt first'),tagMath(el('div','qb-stem',q.stem),'stem'));
  if((q.options||[]).length){
    const options=el('div','qb-options');
    q.options.forEach((option,i)=>{
      const row=el('div','qb-option');
      row.append(el('b','',String.fromCharCode(65+i)),tagMath(el('span','',option.replace(/^\([A-D]\)\s*/,'')),'option:'+i));
      options.append(row);
    });
    left.append(options);
  }
  if((q.conditions||[]).length){
    const conditions=tagMath(el('div','qb-conditions'),'conditions');
    conditions.append(el('b','','Conditions. '),document.createTextNode(q.conditions.join(' ')));
    left.append(conditions);
  }
  if(q.common_wrong_route){
    const trap=tagMath(el('div','qb-trap'),'common_wrong_route');
    trap.append(el('b','','Common wrong route. '),document.createTextNode(q.common_wrong_route));
    left.append(trap);
  }
  const right=el('section','qb-panel');
  right.append(el('div','qb-eyebrow','Representation & support'));
  const visual=el('div','qb-visual');
  if(q.visual_ref){
    const img=document.createElement('img');
    img.loading='lazy';
    img.src='../'+q.visual_ref;
    img.alt='Question-aligned representation for '+q.id;
    visual.append(img);
  }else visual.textContent='No separate representation asset is published for this canonical record.';
  right.append(visual);
  (q.source_hints||[]).forEach((hint,i)=>{
    const d=disclosure('Source hint '+(i+1),typeof hint==='string'?hint:(hint.text||JSON.stringify(hint)),'qb-support','source_hint:'+i);
    d.querySelector('summary').prepend(el('span','qb-prov','SOURCE'));
    right.append(d);
  });
  (q.scaffolds||[]).forEach((s,i)=>{
    const d=disclosure('H'+i+' · '+s.support_kind+' · '+s.reveals,s.text,'qb-support','scaffold:'+i);
    d.querySelector('summary').prepend(el('span','qb-prov','AUTHORED SUPPORT'));
    right.append(d);
  });
  grid.append(left,right);
  article.append(grid);
  const wrap=el('div','qb-solution-wrap'),solution=el('details','qb-disclosure qb-solution'),summary=el('summary','','Teacher solution · complete derivation'),body=el('div','qb-disclosure-body');
  const answer=q.answer||{};
  (answer.reasoning||[]).forEach((step,i)=>{
    const row=el('div','qb-step');
    row.append(el('span','qb-step-num','STEP '+(i+1)),tagMath(el('span','',step),'answer_reasoning:'+i));
    body.append(row);
  });
  const result=el('div','qb-answer');
  result.append(el('b','','Answer: '),tagMath(el('span','',answer.summary||''),'answer_summary'));
  const check=tagMath(el('div','qb-check'),'answer_check');
  check.append(el('b','','Check: '),document.createTextNode(answer.check||''));
  result.append(check);
  body.append(result);
  solution.append(summary,body);
  wrap.append(solution);
  article.append(wrap);
  const footer=el('footer','qb-footer');
  footer.append(el('span','',q.id+' · '+q.source_status+' · '+q.wording_custody));
  if(q.paper_url){
    const link=el('a','','Official source');
    link.href=q.paper_url;
    link.target='_blank';
    link.rel='noopener noreferrer';
    footer.append(link);
  }
  article.append(footer);
  return article;
}

// ---- Study dialog ----
async function openStudyModal(id,trigger){
  studyTrigger=trigger||studyTrigger;
  const summary=Data.summaryById(id);
  els.dialogTitle.textContent=summary?summary.exam+' '+summary.year+' · Q'+summary.question_number:'Study Workspace';
  els.dialogBody.replaceChildren(el('p','qb-empty','Loading study workspace…'));
  if(!els.dialog.open)els.dialog.showModal();
  history.replaceState(null,'',location.pathname+location.search+'#'+encodeURIComponent(id));
  const token=Data.beginRequest();
  try{
    const loaded=await Data.loadQuestion(id,token);
    if(loaded.stale)return;
    const article=studyCard(loaded.question,true);
    els.dialogBody.replaceChildren(article);
    renderDeclaredMath(article,loaded.question);
  }catch(error){
    if(!Data.isCurrent(token))return;
    const message=el('div','qb-empty',describe(error));
    const retry=el('button','btn outline','Retry');
    retry.type='button';
    retry.addEventListener('click',()=>openStudyModal(id,studyTrigger));
    els.dialogBody.replaceChildren(message,retry);
  }
}
function closeStudyModal(){if(els.dialog.open)els.dialog.close();}
function clearHash(){if(location.hash)history.replaceState(null,'',location.pathname+location.search);}

// ---- results ----
function inlineStudy(list){
  const seq=renderSeq;
  list.forEach(q=>{
    const holder=el('article','qb-question');
    holder.id=q.id;
    holder.append(qHeader(q),el('p','qb-empty','Loading study workspace…'));
    els.results.append(holder);
    Data.loadDetail(q.id).then(detail=>{
      if(seq!==renderSeq||!holder.isConnected)return;
      const card=studyCard({...q,...detail},false);
      holder.replaceWith(card);
      renderDeclaredMath(card,{...q,...detail});
    }).catch(error=>{
      if(seq!==renderSeq||!holder.isConnected)return;
      holder.replaceChildren(qHeader(q),el('p','qb-empty',describe(error)));
    });
  });
}
function renderResults(){
  renderSeq+=1;
  const list=filtered();
  els.resultCount.textContent=list.length+' of '+catalog.counts.questions+' questions';
  els.results.replaceChildren();
  const shown=list.slice(0,limit);
  if(state.mode==='study')inlineStudy(shown);
  else{
    shown.forEach(q=>els.results.append(compactCard(q)));
    shown.forEach(q=>renderDeclaredMath(document.getElementById(q.id),q));
  }
  if(!shown.length)els.results.append(el('div','qb-empty','No canonical questions match the current view and filters.'));
  els.loadMore.hidden=list.length<=limit;
  els.studyToolbar.hidden=state.mode!=='study';
}
function renderSearchNote(){
  if(failure)return;
  if(state.q&&!ready.search)showStatus('Search is still loading; showing every question until it is ready.','info');
  else if(warnings.length)showStatus('Some optional resources could not be loaded, so their links are not shown.','warning');
  else hideStatus();
}
function render(){
  if(!ready.catalog)return;
  try{
    normalizeState();
    renderStats();
    renderCollections();
    renderTabs();
    renderTopicStrip();
    renderSubtopicStrip();
    renderBanner();
    renderActive();
    if(ready.list){renderResults();renderSearchNote();}
    else{els.results.replaceChildren(el('div','qb-empty','Loading questions…'));els.resultCount.textContent='';}
  }catch(error){
    showStatus(describe(error),'error',true);
  }
}

// ---- start-up ----
function onStage(stage){
  if(stage==='CATALOG_READY'){
    catalog=window.GRADE9_QUESTION_BANK_CATALOG;
    views=Data.views();
    subjectById=new Map(catalog.subjects.map(row=>[row.id,row]));
    topicById=new Map(catalog.topics.map(row=>[row.id,row]));
    subtopicById=new Map(catalog.subtopics.map(row=>[row.id,row]));
    viewById=new Map(views.map(row=>[row.id,row]));
    ready.catalog=true;
  }
  if(stage==='LIST_READY'){
    summaries=Data.summaries();
    renderFilterOptions();
    ready.list=true;
  }
  if(stage==='SEARCH_READY')ready.search=true;
  if(stage==='RESOURCES_READY')resources=Data.resources();
  render();
  if(stage==='LIST_READY'){handleHash();settleFirstList();}
}
async function start(){
  ready.catalog=ready.list=ready.search=false;
  summaries=[];resources=[];warnings=[];failure=null;
  els.results.replaceChildren(el('div','qb-empty','Loading questions…'));
  showStatus('Loading the Question Bank…','info');
  try{
    const result=await Data.bootstrap({onStage});
    if(result.stale)return;
    warnings=result.warnings;
    renderSearchNote();
    render();
  }catch(error){
    failure=error;
    showStatus(describe(error),'error',true);
  }
}
function handleHash(){
  if(!location.hash)return;
  const id=decodeURIComponent(location.hash.slice(1));
  if(!Data.summaryById(id))return;
  if(state.mode==='study'){
    const card=document.getElementById(id);
    if(card)card.scrollIntoView({block:'start'});
  }else openStudyModal(id,null);
}

// ---- controls ----
function bind(select,key){select.addEventListener('change',()=>setState(key==='subject'?{[key]:select.value,topic:'',subtopic:''}:key==='topic'?{[key]:select.value,subtopic:''}:{[key]:select.value}));}
['subject','topic','difficulty','exam','type','mode','sort'].forEach(key=>bind(els[key],key));
let timer=null;
els.search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>setState({q:els.search.value},{push:false}),120);});
els.clear.addEventListener('click',()=>setState({view:'',q:'',subject:'',topic:'',subtopic:'',difficulty:'',exam:'',type:'',mode:'browse',sort:'canonical'}));
els.browseAll.addEventListener('click',()=>setState({view:'',q:'',subject:'',topic:'',subtopic:'',difficulty:'',exam:'',type:'',mode:'browse'}));
els.loadMore.addEventListener('click',()=>{limit+=PAGE;render();});
function toggle(selector,open){document.querySelectorAll(selector).forEach(node=>{node.open=open;});}
els.openSupport.addEventListener('click',()=>toggle('.qb-support',true));
els.closeSupport.addEventListener('click',()=>toggle('.qb-support',false));
els.openSolutions.addEventListener('click',()=>toggle('.qb-solution',true));
els.closeSolutions.addEventListener('click',()=>toggle('.qb-solution',false));
els.top.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));
els.dialogClose.addEventListener('click',closeStudyModal);
els.dialog.addEventListener('click',event=>{if(event.target===els.dialog)closeStudyModal();});
els.dialog.addEventListener('close',()=>{
  Data.beginRequest();
  clearHash();
  if(studyTrigger&&studyTrigger.isConnected)studyTrigger.focus();
  studyTrigger=null;
});
addEventListener('popstate',()=>{
  state=stateFromUrl();
  normalizeState();
  syncControls();
  render();
  if(location.hash&&ready.list)handleHash();
  else if(els.dialog.open)els.dialog.close();
});

syncControls();
start();
window.Grade9QuestionBank={stateFromUrl,filtered,renderDeclaredMath,ready:firstList,openStudyModal,closeStudyModal};
})();
