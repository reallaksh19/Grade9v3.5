/* Core Prompt Composer — deterministic offline browser projection for Issue #272. */
(function (global) {
  'use strict';

  const ALL_CORES = ['CORE1','CORE2','CORE1A','CORE1B','CORE2A','CORE2B'];
  const HANDOFF_KEY = 'grade9v3_prompt_composer_handoff_v1';

  function canonicalize(value) {
    if (Array.isArray(value)) return '[' + value.map(canonicalize).join(',') + ']';
    if (value && typeof value === 'object') {
      return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonicalize(value[k])).join(',') + '}';
    }
    return JSON.stringify(value);
  }

  function sha256(text) {
    const bytes = new TextEncoder().encode(text);
    const words = [];
    for (let i=0;i<bytes.length;i++) words[i>>2] |= bytes[i] << (24-(i%4)*8);
    words[bytes.length>>2] |= 0x80 << (24-(bytes.length%4)*8);
    words[(((bytes.length+8)>>6)+1)*16-1] = bytes.length*8;
    // Sparse array holes must be explicit zero words before message expansion.
    for (let i=0;i<words.length;i++) words[i] = words[i] || 0;
    const k = [], h = [];
    const isPrime = n => { for(let i=2;i*i<=n;i++) if(n%i===0) return false; return true; };
    const frac = (x,p) => ((x-Math.floor(x))*0x100000000)>>>0;
    let n=2;
    while(k.length<64){ if(isPrime(n)){ if(h.length<8) h.push(frac(Math.sqrt(n))); k.push(frac(Math.cbrt(n))); } n++; }
    const rotr=(x,n)=>(x>>>n)|(x<<(32-n));
    for(let i=0;i<words.length;i+=16){
      const w=words.slice(i,i+16);
      for(let j=16;j<64;j++){
        const x=w[j-15]>>>0,y=w[j-2]>>>0;
        const s0=(rotr(x,7)^rotr(x,18)^(x>>>3))>>>0;
        const s1=(rotr(y,17)^rotr(y,19)^(y>>>10))>>>0;
        w[j]=(w[j-16]+s0+w[j-7]+s1)>>>0;
      }
      let [a,b,c,d,e,f,g,hh]=h;
      for(let j=0;j<64;j++){
        const S1=(rotr(e,6)^rotr(e,11)^rotr(e,25))>>>0;
        const ch=((e&f)^(~e&g))>>>0;
        const t1=(hh+S1+ch+k[j]+w[j])>>>0;
        const S0=(rotr(a,2)^rotr(a,13)^rotr(a,22))>>>0;
        const maj=((a&b)^(a&c)^(b&c))>>>0;
        const t2=(S0+maj)>>>0;
        hh=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
      }
      h[0]=(h[0]+a)>>>0;h[1]=(h[1]+b)>>>0;h[2]=(h[2]+c)>>>0;h[3]=(h[3]+d)>>>0;
      h[4]=(h[4]+e)>>>0;h[5]=(h[5]+f)>>>0;h[6]=(h[6]+g)>>>0;h[7]=(h[7]+hh)>>>0;
    }
    return h.map(x=>x.toString(16).padStart(8,'0')).join('');
  }

  const digest = value => 'sha256:' + sha256(typeof value === 'string' ? value : canonicalize(value));

  function browserSubjectData(data, siteData, subject) {
    const site = ((siteData || {}).subjects || {})[subject] || {};
    const supplement = ((data.subjects || {})[subject] || {}).nested_questions || {};
    const questions = Object.assign({}, supplement);
    const capabilities = {};
    const locations = {};
    const matrices = Array.isArray(site.matrices) ? site.matrices : [];

    matrices.forEach(board => {
      (board.rungs || []).forEach(rung => {
        const cap = rung.capability || {};
        if (cap.id) {
          capabilities[cap.id] = {
            id: cap.id,
            action: cap.action || null,
            success_criterion: cap.success_criterion || null
          };
          if (!locations[cap.id]) locations[cap.id] = [];
          locations[cap.id].push({
            matrix_id: board.matrix_id,
            bucket_id: board.bucket_id,
            topic: board.topic,
            subtopic: board.subtopic,
            rung: rung.rung,
            ladder_position: rung.ladder_position,
            default_entry_eligible: rung.default_entry_eligible !== false,
            microtopic_ref: rung.microtopic_ref
          });
        }
        (rung.questions || []).forEach(q => {
          if (!questions[q.id] && cap.id) {
            questions[q.id] = {
              id: q.id,
              status: null,
              primary_capability_ref: cap.id,
              secondary_capability_refs: [],
              analysis: null,
              source_custody: null
            };
          }
        });
      });
    });
    Object.values(locations).forEach(rows => rows.sort((a,b) =>
      String(a.matrix_id || '').localeCompare(String(b.matrix_id || '')) ||
      Number(a.ladder_position || 0) - Number(b.ladder_position || 0) ||
      String(a.rung || '').localeCompare(String(b.rung || ''))
    ));
    return {questions, capabilities, locations, matrices};
  }

  function boardMap(subjectData) {
    return new Map((subjectData.matrices || []).map(row => [row.matrix_id, row]));
  }

  function primaryLocation(subjectData, capabilityRef) {
    const rows = (subjectData.locations || {})[capabilityRef] || [];
    if (rows.length === 1) return {location: rows[0], finding: null};
    if (!rows.length) return {location: null, finding: capabilityRef + ' has no canonical teaching location'};
    return {location: null, finding: capabilityRef + ' has ' + rows.length + ' canonical teaching locations; scope is ambiguous'};
  }

  function resolveRow(raw, subjectData, ownerScope) {
    const ownerId = String(raw.question_id || '').trim();
    const summary = String(raw.summary || '').trim();
    const ref = raw.canonical_question_ref || null;
    const candidates = [...new Set(raw.candidate_question_refs || [])];
    const canonical = ref ? subjectData.questions[ref] : null;
    const holds = [];
    const allowedEligibility = new Set(['ELIGIBLE','EXCLUDED','HOLD','NOT_ESTABLISHED']);
    let learnerEligibility = String(raw.learner_eligibility || 'NOT_ESTABLISHED').trim().toUpperCase();
    if(!allowedEligibility.has(learnerEligibility)){
      holds.push({status:'UNMAPPED_HOLD',point:'LEARNER_ELIGIBILITY_INVALID',detail:ownerId+': learner_eligibility '+JSON.stringify(learnerEligibility)+' is not recognized'});
      learnerEligibility='NOT_ESTABLISHED';
    }
    const learnerEligibilityBasis = raw.learner_eligibility_basis || null;

    if(!ref && candidates.length){
      const valid=candidates.filter(x=>subjectData.questions[x]);
      const unknown=candidates.filter(x=>!subjectData.questions[x]);
      let detail=ownerId+': multiple candidate question identities require explicit exact-ref confirmation: '+(valid.length?valid:candidates).join(', ');
      if(unknown.length) detail+='; unknown candidate refs: '+unknown.join(', ');
      holds.push({status:'IDENTITY_HOLD',point:'QUESTION_IDENTITY_AMBIGUOUS',detail});
      return {row:{
        owner_question_id:ownerId,summary,canonical_question_ref:null,candidate_question_refs:candidates,
        identity_status:'IDENTITY_HOLD',demand_evidence_refs:valid,learner_eligibility:learnerEligibility,
        learner_eligibility_basis:learnerEligibilityBasis,mapping_basis:'UNMAPPED',mapping_status:'IDENTITY_HOLD',
        primary_capability_ref:null,secondary_capability_refs:[],primary_location:null,record_status:null,
        source_custody:null,analysis:null,finding:detail
      },holds};
    }
    if (ref && canonical) {
      const primary = canonical.primary_capability_ref;
      const secondary = canonical.secondary_capability_refs || [];
      const found = primaryLocation(subjectData, primary);
      if (found.finding) holds.push({status:'UNMAPPED_HOLD',point:'PRIMARY_LOCATION_UNRESOLVED',detail:ownerId + ': ' + found.finding});
      return {row:{
        owner_question_id:ownerId,summary,canonical_question_ref:ref,candidate_question_refs:candidates,
        identity_status:'EXACT_CONFIRMED',demand_evidence_refs:[ref],learner_eligibility:learnerEligibility,
        learner_eligibility_basis:learnerEligibilityBasis,mapping_basis:'CANONICAL_QUESTION',
        mapping_status:found.location?'CANONICAL_MATCH':'UNMAPPED_HOLD',primary_capability_ref:primary,
        secondary_capability_refs:[...secondary],primary_location:found.location,record_status:canonical.status || null,
        source_custody:canonical.source_custody || null,analysis:canonical.analysis || null,finding:found.finding
      },holds};
    }
    if (ref && !canonical) {
      const detail=ownerId + ': exact canonical_question_ref ' + ref + ' is not present; short labels or summaries are not source identity';
      return {row:{owner_question_id:ownerId,summary,canonical_question_ref:ref,candidate_question_refs:candidates,
        identity_status:'UNMAPPED',demand_evidence_refs:[],learner_eligibility:learnerEligibility,
        learner_eligibility_basis:learnerEligibilityBasis,mapping_basis:'UNMAPPED',mapping_status:'UNMAPPED_HOLD',
        primary_capability_ref:null,secondary_capability_refs:[],primary_location:null,record_status:null,
        source_custody:null,analysis:null,finding:detail},holds:[{status:'UNMAPPED_HOLD',point:'CANONICAL_QUESTION_UNKNOWN',detail}]};
    }
    const primary=raw.primary_capability_ref || null, secondary=[...(raw.secondary_capability_refs || [])];
    const found=primary ? primaryLocation(subjectData,primary) : {location:null,finding:'primary capability is not supplied'};
    const shared={owner_question_id:ownerId,summary,canonical_question_ref:null,candidate_question_refs:candidates,
      identity_status:'UNMAPPED',demand_evidence_refs:[],learner_eligibility:learnerEligibility,
      learner_eligibility_basis:learnerEligibilityBasis,primary_capability_ref:primary,
      secondary_capability_refs:secondary,primary_location:found.location,record_status:null,source_custody:null,analysis:null};
    if(raw.mapping_basis==='AGENT_PROPOSAL'){
      const detail=ownerId + ': proposed mapping requires owner review before it can constrain a Core prompt';
      return {row:{...shared,mapping_basis:'AGENT_PROPOSAL',mapping_status:'AGENT_PROPOSAL_PENDING_REVIEW',finding:detail},holds:[{status:'AGENT_PROPOSAL_PENDING_REVIEW',point:'AGENT_MAPPING_REVIEW_REQUIRED',detail}]};
    }
    if(raw.mapping_basis==='MANUAL' && primary && found.location && ownerScope){
      return {row:{...shared,mapping_basis:'MANUAL',mapping_status:'OWNER_CONFIRMED_CANONICAL_RUNG',finding:null},holds:[]};
    }
    let detail=ownerId + ': no exact canonical question mapping or owner-confirmed manual canonical mapping is available';
    if(found.finding) detail+=' ('+found.finding+')';
    return {row:{...shared,mapping_basis:'UNMAPPED',mapping_status:'UNMAPPED_HOLD',finding:detail},holds:[{status:'UNMAPPED_HOLD',point:'QUESTION_MAPPING_UNRESOLVED',detail}]};
  }

  function resolveScope(rows, ownerScope, subjectData) {
    const locations=rows.map(r=>r.primary_location).filter(Boolean);
    const matrices=[...new Set(locations.map(x=>x.matrix_id))].sort();
    if(!matrices.length) return {scope:{status:'UNMAPPED_HOLD',matrix_ref:null,bucket_ref:null,topic:null,subtopic:null,canonical_primary_rungs:[],owner_confirmed_rung:ownerScope||null},holds:[{status:'UNMAPPED_HOLD',point:'COMPOSITION_SCOPE_UNMAPPED',detail:'No unique canonical primary teaching matrix can be established from the question rows.'}]};
    if(matrices.length>1) return {scope:{status:'MIXED_SUBTOPIC_HOLD',matrix_ref:null,bucket_ref:null,topic:null,subtopic:null,canonical_primary_rungs:[...new Set(locations.map(x=>x.rung).filter(Boolean))].sort(),owner_confirmed_rung:ownerScope||null},holds:[{status:'MIXED_SUBTOPIC_HOLD',point:'MIXED_PRIMARY_MATRICES',detail:'Primary question mappings span multiple matrices: '+matrices.join(', ')}]};
    const matrixId=matrices[0], board=boardMap(subjectData).get(matrixId);
    if(!board) return {scope:{status:'UNMAPPED_HOLD',matrix_ref:matrixId,bucket_ref:null,topic:null,subtopic:null,canonical_primary_rungs:[],owner_confirmed_rung:ownerScope||null},holds:[{status:'UNMAPPED_HOLD',point:'MATRIX_RECORD_MISSING',detail:matrixId+' is referenced by capability locations but its matrix record is unavailable.'}]};
    const rungs=[...new Set(locations.map(x=>x.rung).filter(Boolean))].sort();
    const holds=[]; let status='CANONICAL_MATCH';
    const ownerValid=ownerScope && ownerScope.matrix_id===matrixId && (board.rungs||[]).some(r=>r.rung===ownerScope.rung);
    if(rungs.length>1){
      if(!ownerScope){holds.push({status:'UNMAPPED_HOLD',point:'OWNER_RUNG_CONFIRMATION_REQUIRED',detail:'Question primaries span canonical rungs '+rungs.join(', ')+'; confirm one composition rung without rewriting per-question mappings.'});status='UNMAPPED_HOLD';}
      else if(!ownerValid){holds.push({status:'UNMAPPED_HOLD',point:'OWNER_RUNG_CONFIRMATION_INVALID',detail:"The owner-confirmed composition rung does not resolve inside the question set's canonical matrix."});status='UNMAPPED_HOLD';}
      else status='OWNER_CONFIRMED_CANONICAL_RUNG';
    } else if(ownerScope){
      if(!ownerValid){holds.push({status:'UNMAPPED_HOLD',point:'OWNER_RUNG_CONFIRMATION_INVALID',detail:'The owner-confirmed composition rung does not resolve inside the canonical matrix.'});status='UNMAPPED_HOLD';}
      else status='OWNER_CONFIRMED_CANONICAL_RUNG';
    }
    return {scope:{status,matrix_ref:matrixId,bucket_ref:board.bucket_id||null,topic:board.topic||null,subtopic:board.subtopic||null,canonical_primary_rungs:rungs,owner_confirmed_rung:ownerScope||null},holds};
  }

  function fingerprint(rows,scope,subjectData){
    const items=[],seen=new Set();
    const add=(phrase,kind,evidence)=>{
      const text=String(phrase||'').replace(/\s+/g,' ').trim(), key=text.toLowerCase();
      if(!text||seen.has(key)) return; seen.add(key);
      items.push({keyword_id:'KW-'+String(items.length+1).padStart(2,'0'),phrase:text,kind,evidence_refs:[...new Set(evidence)].sort()});
    };
    rows.forEach(row=>{
      const a=row.analysis||{}, ref=row.canonical_question_ref;
      add(a.stable_crux_move,'QUESTION_CRUX',[ref||row.owner_question_id]);
      if(!a.stable_crux_move){
        const cap=(subjectData.capabilities||{})[row.primary_capability_ref]||{};
        add(cap.action,'CAPABILITY_ACTION',[row.primary_capability_ref||row.owner_question_id]);
      }
    });
    if(scope.matrix_ref){
      const board=boardMap(subjectData).get(scope.matrix_ref)||{}, family=board.family||{};
      add(family.invariant_demand,'MATRIX_INVARIANT',[scope.matrix_ref]);
      add(family.difficult_move,'MATRIX_DIFFICULT_MOVE',[scope.matrix_ref]);
    }
    if(!items.length) add('No trustworthy concept fingerprint can be emitted until the question mapping is resolved.','CAPABILITY_ACTION',['COMPOSER_HOLD']);
    return items;
  }

  function coreOrderHolds(requested,order){
    const holds=[],unknown=[...new Set(requested.concat(order).filter(x=>!ALL_CORES.includes(x)))].sort();
    if(unknown.length) holds.push({status:'UNMAPPED_HOLD',point:'UNKNOWN_CORE',detail:'Unknown Core role(s): '+unknown.join(', ')});
    if(new Set(requested).size!==requested.length) holds.push({status:'UNMAPPED_HOLD',point:'DUPLICATE_REQUESTED_CORE',detail:'requested_cores must not contain duplicates.'});
    if(new Set(order).size!==order.length || order.length!==requested.length || requested.some(x=>!order.includes(x))) holds.push({status:'UNMAPPED_HOLD',point:'CORE_ORDER_INVALID',detail:'execution_order must contain every requested Core exactly once and no others.'});
    return holds;
  }

  function sourceBasisHolds(sourceBasis,rows){
    const refs=new Set(rows.map(r=>r.canonical_question_ref).filter(Boolean));
    const invalid=sourceBasis.filter(x=>refs.has(x));
    return invalid.length?[{status:'UNMAPPED_HOLD',point:'SOURCE_BASIS_QUESTION_ID_INVALID',detail:'authoring-request source_basis is a source locator/receipt basis, not canonical question IDs: '+invalid.join(', ')}]:[];
  }

  function difficulty(rows){
    const bands=[]; rows.forEach(r=>{const b=r.analysis&&r.analysis.difficulty&&r.analysis.difficulty.band;if(b&&!bands.includes(b))bands.push(b);});
    return bands.sort((a,b)=>{const ai=/^D\d+$/.test(a)?Number(a.slice(1)):999,bi=/^D\d+$/.test(b)?Number(b.slice(1)):999;return ai-bi||a.localeCompare(b);});
  }

  function traceRows(rows,fp){
    const byRef={}; fp.forEach(item=>item.evidence_refs.forEach(ref=>{if(!(ref in byRef))byRef[ref]=item.phrase;}));
    return rows.map((row,i)=>{
      const loc=row.primary_location||{}, key=row.canonical_question_ref||row.owner_question_id;
      return {trace_id:'trace-q-'+String(i+1).padStart(2,'0'),question_ids:[row.owner_question_id],input_or_owner_decision:row.summary||row.owner_question_id,canonical_ref:row.canonical_question_ref||null,candidate_question_refs:row.candidate_question_refs||[],demand_evidence_refs:row.demand_evidence_refs||[],learner_eligibility:row.learner_eligibility||'NOT_ESTABLISHED',primary_capability_ref:row.primary_capability_ref||null,secondary_capability_refs:row.secondary_capability_refs||[],matrix_ref:loc.matrix_id||null,rung:loc.rung||null,keyword:byRef[key]||null,prompt_clause:'FIXED_SOURCE_QUESTIONS;KEYWORD_FINGERPRINT',mapping_basis:row.mapping_basis,provenance:[row.canonical_question_ref,loc.matrix_path,row.primary_capability_ref].filter(Boolean),status:row.mapping_status,finding:row.finding||null};
    });
  }

  function renderPrompt(brief,template){
    const rows=brief.question_rows,fp=brief.keyword_fingerprint,scope=brief.scope;
    const fixed=rows.map(row=>'- '+row.owner_question_id+': '+(row.summary||'(no summary supplied)')+(row.canonical_question_ref?' [canonical: '+row.canonical_question_ref+']':'')+((row.candidate_question_refs||[]).length?' [candidates: '+row.candidate_question_refs.join(', ')+']':'')+' [mapping: '+row.mapping_status+'] [learner eligibility: '+(row.learner_eligibility||'NOT_ESTABLISHED')+']').join('\n');
    const learner=brief.learner_entry?canonicalize(brief.learner_entry):'No learner input supplied.';
    const boundary='Subject: '+brief.subject+'. Matrix: '+(scope.matrix_ref||'UNRESOLVED')+'. Bucket: '+(scope.bucket_ref||'UNRESOLVED')+'. Canonical primary rungs represented: '+((scope.canonical_primary_rungs||[]).join(', ')||'none')+'. Composition scope status: '+scope.status+'.';
    const coreLines=brief.requested_cores.map(core=>'- '+core+': '+template.role_guardrails[core]+' Contract: '+template.role_contract_refs[core]).join('\n');
    const authority=brief.__authority_contract;
    const authorityLines=brief.requested_cores.map(core=>{
      const rule=authority.roles[core]||{}, required=(rule.required_authority||[]).join(', ')||'none';
      let line='- '+core+': required authority = '+required;
      if((rule.one_of_authority||[]).length) line+='; one of = '+rule.one_of_authority.join(', ');
      if((rule.optional_authority||[]).length) line+='; optional support = '+rule.optional_authority.join(', ');
      return line;
    }).join('\n');
    const authorityText=authorityLines+'\nExecution order is production control only; it is not derivation or authority order.\nA Core2 HOLD does not become academic authority and does not automatically block valid Core1-family study products.\nPreserve question.primary_capability_ref; set-level topic/rung scope is composition context only.\nDemand evidence and learner eligibility are independent states.\nSource question.hints[] and authored question.scaffolds[] remain separate custody classes.\nExtension demands do not become Core1/Core1A/Core1B microtopics unless canonical academic authority admits them.';
    const diff=(brief.validation.difficulty_bands||[]).join(' → ')||'Use the canonical/intrinsic difficulty information available in the referenced records; do not infer it from learner percentage.';
    const kws=fp.map(item=>'- '+item.phrase+' ('+item.kind+'; evidence: '+item.evidence_refs.join(', ')+')').join('\n');
    const trace=brief.trace_rows.map(row=>'- '+row.trace_id+': '+row.question_ids.join(', ')+' → '+(row.primary_capability_ref||'UNMAPPED')+' → '+(row.matrix_ref||'UNMAPPED')+'/'+(row.rung||'UNMAPPED')+'; status='+row.status).join('\n');
    const hold=brief.holds.length?brief.holds.map(h=>'- '+h.status+' / '+h.point+': '+h.detail).join('\n'):'- No composer-level HOLD. Downstream planner holds still apply.';
    const content={
      GOAL_OUTCOME:'Produce the requested six-Core authoring outputs from this fixed planning bundle without changing canonical curriculum, question identity, role semantics, or planner authority.',
      FIXED_SOURCE_QUESTIONS:fixed,
      LEARNER_PROFILE:learner+'\nA percentage is a starting coordinate only; it is not evidence of prerequisite mastery.',
      EXECUTION_ORDER:brief.execution_order.join(' → ')+'\nTreat this as production control only. It does not override readiness, HOLD decisions, or the authority graph.',
      AUTHORITY_GRAPH:authorityText,
      TOPIC_BOUNDARY:boundary,
      CORE_OBLIGATIONS:coreLines,
      DIFFICULTY_PROGRESSION:diff+'\nPreserve intrinsic Core1A/Core1B depth regardless of the learner estimate.',
      KEYWORD_FINGERPRINT:kws,
      PROVENANCE_TRACE:trace+'\nUse only the cited repository/owner inputs. Do not expose or invent private reasoning traces.',
      ACCEPTANCE:'Keep every fixed question traceable to its mapping finding; preserve per-question primary_capability_ref independently from set-level scope; keep demand evidence separate from learner eligibility; preserve the requested Core set/order without treating order as authority; distinguish source hints from authored scaffolds and source/adapted/authored material; do not promote extension demand into Core1-family teaching without canonical admission; and hand the unchanged authoring request to the existing planner.',
      NON_GOALS:'Do not select a new canonical question set, create a seventh Core, infer mastery, fabricate source receipts, duplicate plan_request.py, or author/publish PDFs in this task.',
      HOLD_FAIL:hold+'\nIf a composer HOLD is present, do not silently resolve it. If the planner requests source basis, prerequisites or owner input, preserve that HOLD.',
      DOWNSTREAM_DELIVERABLE:'The intended downstream publication is one role-specific PDF for each valid/publishable requested Core. Do not render PDFs here; #273 owns PDF publication after validated learner products exist.'
    };
    const sections=['# Core-agent authoring prompt\n\nPrompt brief: '+brief.prompt_brief_id+'\nRepository basis: '+brief.repository_basis];
    template.sections.forEach(spec=>sections.push('## ['+spec.id+'] '+spec.title+'\n\n'+content[spec.id]));
    return sections.join('\n\n').trim()+'\n';
  }

  function composeDocument(doc,data,siteData){
    const subject=String(doc.subject||'').trim();
    const sitePayload=siteData || global.GRADE9V3 || {subjects:{}};
    const subjectData=browserSubjectData(data, sitePayload, subject);
    const requested=[...(doc.requested_cores||[])], order=[...(doc.execution_order||requested)], ownerScope=doc.owner_confirmed_rung||null;
    const inputDigest=digest(JSON.parse(canonicalize(doc))), briefId='PB-'+inputDigest.split(':')[1].slice(0,16).toUpperCase();
    let holds=[];
    if(!subject)holds.push({status:'UNMAPPED_HOLD',point:'SUBJECT_REQUIRED',detail:'subject is required'});
    if(!(doc.questions||[]).length)holds.push({status:'UNMAPPED_HOLD',point:'QUESTION_SET_REQUIRED',detail:'at least one question row is required'});
    if(subject && !(((sitePayload || {}).subjects || {})[subject]))holds.push({status:'UNMAPPED_HOLD',point:'SUBJECT_UNKNOWN',detail:subject+' has no canonical subject library'});
    const rows=(doc.questions||[]).map(raw=>{const r=resolveRow(raw,subjectData,ownerScope);holds=holds.concat(r.holds);return r.row;});
    const scoped=resolveScope(rows,ownerScope,subjectData);holds=holds.concat(scoped.holds,coreOrderHolds(requested,order),sourceBasisHolds(doc.source_basis||[],rows));
    const seen=new Set();holds=holds.filter(h=>{const k=h.status+'|'+h.point+'|'+h.detail;if(seen.has(k))return false;seen.add(k);return true;});
    const fp=fingerprint(rows,scoped.scope,subjectData), trace=traceRows(rows,fp);
    const brief={
      prompt_brief_id:briefId,template:{id:data.template.template_id,version:data.template.version,path:'template/core-prompt-composer/core-agent-prompt.v1.json'},
      repository_basis:doc.repository_basis||data.repository_basis,authority_contract:{version:data.authority_contract.version,path:'Shared/roles/CORE-AUTHORITY-CONTRACT.md',digest:digest(data.authority_contract)},input_digest:inputDigest,prompt_digest:'sha256:'+'0'.repeat(64),subject,
      scope:scoped.scope,question_rows:rows,keyword_fingerprint:fp,learner_entry:doc.learner||null,requested_cores:requested,execution_order:order,
      source_authoring_policy:{question_identity_rule:'Exact canonical_question_ref may adopt stored mapping metadata without promoting record lifecycle status.',source_basis_rule:'authoring-request source_basis accepts source locator/receipt basis only; canonical question IDs remain in this brief/worksheet map.',source_receipt_rule:'The composer never creates or upgrades source receipts and never claims source-product readiness.',supplemental_question_policy:doc.supplemental_question_policy||null},
      scope_boundaries:['Canonical subject/question records remain authority.','Existing six Core role contracts remain authority; no seventh Core is created.','Learner percentage is a routing coordinate only and cannot shrink CORE1A/CORE1B intrinsic depth.','plan_request.py remains authoritative for readiness, prerequisite bridges, source receipts and product holds.','Reusable question-set selection and strict exam mode remain outside this composer.','PDF publication remains downstream under issue #273.'],
      validation:{composer_state:holds.length?'HOLD':'PASS',difficulty_bands:difficulty(rows),question_count:rows.length,mapped_question_count:rows.filter(r=>r.primary_capability_ref).length,core_order_exact:!holds.some(h=>h.point==='CORE_ORDER_INVALID'),source_basis_contains_question_ids:holds.some(h=>h.point==='SOURCE_BASIS_QUESTION_ID_INVALID')},
      trace_rows:trace,holds,planner_handoff:{state:holds.length?'COMPOSER_HOLD':'READY_FOR_PLANNER',authoring_request_schema:'Shared/library/authoring-request.schema.json',planner_command:'python3 Shared/tools/plan_request.py --plan <authoring-request.json>',run_builder:'tools/run-builder/index.html',note:'Composer PASS means only that the prompt bundle is structurally/mapping-ready for the existing planner; it does not mean any Core product is ready.'}
    };
    Object.defineProperty(brief,'__authority_contract',{value:data.authority_contract,enumerable:false});
    const prompt=renderPrompt(brief,data.template);brief.prompt_digest=digest(prompt);
    const worksheet={worksheet_id:doc.worksheet_id||('WS-'+digest(doc).slice(7,19).toUpperCase()),subject,source_note:'Owner-supplied question set mapped by Core Prompt Composer; mapping is planning demand, not curriculum or source authority.',questions:rows.filter(r=>r.primary_capability_ref&&r.mapping_basis!=='UNMAPPED').map(r=>{const q={question_id:r.owner_question_id,primary_capability_ref:r.primary_capability_ref,secondary_capability_refs:r.secondary_capability_refs,mapping_basis:r.mapping_basis};if(r.mapping_basis==='CANONICAL_QUESTION'&&r.canonical_question_ref)q.canonical_question_ref=r.canonical_question_ref;if(r.summary)q.note=r.summary;return q;})};
    const request={request_id:doc.request_id||('REQ-'+briefId.slice(3)),subject,requested_cores:requested};
    if(scoped.scope.bucket_ref)request.bucket_id=scoped.scope.bucket_ref;else if(scoped.scope.subtopic)request.subtopic=scoped.scope.subtopic;
    if(doc.learner)request.learner=doc.learner;if(doc.practice)request.practice=doc.practice;if(doc.supplemental_question_policy)request.supplemental_question_policy=doc.supplemental_question_policy;
    if((doc.source_basis||[]).length&&!holds.some(h=>h.point==='SOURCE_BASIS_QUESTION_ID_INVALID'))request.source_basis=[...doc.source_basis];
    return {prompt_brief:brief,agent_prompt:prompt,worksheet_map:worksheet,authoring_request:request,passed:!holds.length};
  }

  function parseRows(text){
    return String(text||'').split(/\r?\n/).map(x=>x.trim()).filter(Boolean).map((line,i)=>{
      const parts=line.split('|').map(x=>x.trim());
      if(parts.length>=3)return {question_id:parts[0]||('Q'+(i+1)),canonical_question_ref:parts[1]||undefined,summary:parts.slice(2).join(' | ')};
      if(parts.length===2)return {question_id:parts[0]||('Q'+(i+1)),summary:parts[1]};
      return {question_id:'Q'+(i+1),summary:parts[0]};
    });
  }

  function download(name,text,type){
    const blob=new Blob([text],{type:type||'text/plain'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=name;a.click();URL.revokeObjectURL(url);
  }

  function initUi(){
    const data=global.GRADE9V3_PROMPT_COMPOSER, siteData=global.GRADE9V3;if(!data||!siteData)return;
    const $=id=>document.getElementById(id), subject=$('subjectSelect'), matrix=$('matrixSelect'), rung=$('rungSelect');
    Object.keys(siteData.subjects || {}).sort().forEach(name=>{const o=document.createElement('option');o.value=name;o.textContent=name;subject.appendChild(o);});
    ALL_CORES.forEach(core=>{const label=document.createElement('label'),input=document.createElement('input'),span=document.createElement('span');input.type='checkbox';input.value=core;input.checked=true;span.textContent=core;label.append(input,span);$('coreChoices').appendChild(label);});
    function refreshMatrices(){
      matrix.replaceChildren(new Option('No owner-confirmed matrix',''));rung.replaceChildren(new Option('No owner-confirmed rung',''));
      const d=siteData.subjects[subject.value];(d?d.matrices:[]).forEach(row=>matrix.appendChild(new Option((row.topic||row.matrix_id)+' · '+row.matrix_id,row.matrix_id)));
    }
    function refreshRungs(){
      rung.replaceChildren(new Option('No owner-confirmed rung',''));const d=siteData.subjects[subject.value],b=d&&(d.matrices||[]).find(x=>x.matrix_id===matrix.value);
      (b?b.rungs:[]).forEach(row=>rung.appendChild(new Option(row.rung+' · '+row.microtopic_ref,row.rung)));
    }
    subject.addEventListener('change',refreshMatrices);matrix.addEventListener('change',refreshRungs);refreshMatrices();

    let current=null;
    try{
      const raw=sessionStorage.getItem(HANDOFF_KEY);
      if(raw){sessionStorage.removeItem(HANDOFF_KEY);const h=JSON.parse(raw);if(h.subject&&siteData.subjects[h.subject]){subject.value=h.subject;refreshMatrices();}if(h.matrix_id){matrix.value=h.matrix_id;refreshRungs();}if(h.rung)rung.value=h.rung;if(typeof h.knowledge_percentage==='number')$('knowledgePercentage').value=String(h.knowledge_percentage);if(Array.isArray(h.requested_cores)){document.querySelectorAll('#coreChoices input').forEach(el=>el.checked=h.requested_cores.includes(el.value));}$('handoffStatus').textContent='Loaded one-shot Topic Atlas context. Question rows were not inferred; paste them above.';}
    }catch(err){$('handoffStatus').textContent='Topic Atlas handoff could not be read; no data was retained.';}

    function buildDoc(){
      const k=$('knowledgePercentage').value;
      const scope=matrix.value&&rung.value?{matrix_id:matrix.value,rung:rung.value,by:'owner/browser'}:undefined;
      const learner=k===''?undefined:{owner_estimate:{knowledge_percentage:Math.max(0,Math.min(100,Math.round(Number(k)))),by:'owner/browser',instruction:'Starting coordinate only; not evidence of prerequisite mastery.'}};
      return {repository_basis:data.repository_basis,subject:subject.value,questions:parseRows($('questionRows').value),...(scope?{owner_confirmed_rung:scope}:{}),...(learner?{learner}:{}),requested_cores:[...document.querySelectorAll('#coreChoices input:checked')].map(el=>el.value),execution_order:$('executionOrder').value.split(',').map(x=>x.trim()).filter(Boolean),source_basis:$('sourceBasis').value.split(/\r?\n/).map(x=>x.trim()).filter(Boolean)};
    }

    function render(result){
      current=result;const b=result.prompt_brief;
      $('bundleState').textContent=b.validation.composer_state;$('bundleState').dataset.state=b.validation.composer_state;
      $('composerErrors').hidden=!b.holds.length;$('composerErrors').textContent=b.holds.map(h=>h.status+' / '+h.point+': '+h.detail).join('\n');
      $('fingerprintList').replaceChildren(...b.keyword_fingerprint.map(item=>{const li=document.createElement('li');li.textContent=item.phrase+' — '+item.kind+' — '+item.evidence_refs.join(', ');return li;}));
      $('traceBody').replaceChildren(...b.trace_rows.map(row=>{const tr=document.createElement('tr');[row.question_ids.join(', '),row.canonical_ref||'—',row.primary_capability_ref||'—',(row.matrix_ref||'—')+' / '+(row.rung||'—'),row.status].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.appendChild(td);});return tr;}));
      $('promptPreview').textContent=result.agent_prompt;
      ['copyPrompt','downloadBrief','downloadPrompt','downloadWorksheet','downloadRequest'].forEach(id=>$(id).disabled=false);
      if(b.holds.length){$('composerErrors').focus();}
    }
    $('composerForm').addEventListener('submit',e=>{e.preventDefault();render(composeDocument(buildDoc(),data,siteData));});
    $('resetComposer').addEventListener('click',()=>{location.reload();});
    $('copyPrompt').addEventListener('click',()=>{if(current&&navigator.clipboard)navigator.clipboard.writeText(current.agent_prompt);});
    $('downloadBrief').addEventListener('click',()=>current&&download('prompt-brief.json',JSON.stringify(current.prompt_brief,null,2)+'\n','application/json'));
    $('downloadPrompt').addEventListener('click',()=>current&&download('agent-prompt.md',current.agent_prompt,'text/markdown'));
    $('downloadWorksheet').addEventListener('click',()=>current&&download('worksheet-map.json',JSON.stringify(current.worksheet_map,null,2)+'\n','application/json'));
    $('downloadRequest').addEventListener('click',()=>current&&download('authoring-request.json',JSON.stringify(current.authoring_request,null,2)+'\n','application/json'));
  }

  global.PROMPT_COMPOSER={composeDocument,canonicalize,digest,sha256,parseRows,HANDOFF_KEY,__test:{browserSubjectData,resolveRow,resolveScope,fingerprint,traceRows,renderPrompt}};
  if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',initUi);
})(typeof window!=='undefined'?window:globalThis);
