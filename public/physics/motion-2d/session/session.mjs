import { TRACE_VERSION, STAGES, invariantChecks, replayMotionSessionTrace, summarizeMotionSessionState } from "./session-trace.mjs";

const CASE = Object.freeze({
  matrixId: "MATRIX-PHY-KIN-2D-MOTION",
  rung: "R1",
  transferProjectionId: "physics:q-phy-kin-2d-2b-projectile-validity-04:core2b",
});
const clone = (v) => v == null ? v : JSON.parse(JSON.stringify(v));
const idx = (stage) => STAGES.indexOf(stage);

class SessionError extends Error {
  constructor(code, detail = "") { super(detail ? code + ": " + detail : code); this.code = code; }
}
const need = (ok, code, detail = "") => { if (!ok) throw new SessionError(code, detail); };
const one = (rows, code, detail = "") => { need(rows.length === 1, code, detail || String(rows.length)); return rows[0]; };

export function resolveMotionSessionIdentity(atlasData, coreData, selector = CASE) {
  const physics = atlasData?.subjects?.Physics;
  need(physics && Array.isArray(physics.atlas_index), "SESSION_ATLAS_INDEX_UNAVAILABLE");
  need(Array.isArray(coreData?.core_projections), "SESSION_CORE_DATA_UNAVAILABLE");
  const atlas = one(
    physics.atlas_index.filter((r) => r?.matrix_id === selector.matrixId && r?.rung === selector.rung),
    "SESSION_ATLAS_SELECTION_UNAVAILABLE", selector.matrixId + "/" + selector.rung
  );
  for (const key of ["mapping","core","representation","activity","portable_package","standalone"]) {
    need(atlas.availability?.[key] === "READY", "SESSION_ATLAS_INPUT_UNAVAILABLE", key);
  }
  need(Array.isArray(atlas.core_projection_refs), "SESSION_CORE_REFS_UNAVAILABLE");
  need(Array.isArray(atlas.representation_refs) && atlas.representation_refs.length === 1, "SESSION_REPRESENTATION_AMBIGUOUS");
  need(Array.isArray(atlas.activity_refs) && atlas.activity_refs.length === 1, "SESSION_ACTIVITY_AMBIGUOUS");

  const core1b = one(coreData.core_projections.filter((r) =>
    atlas.core_projection_refs.includes(r?.id)
    && r?.projection?.core === "CORE1B"
    && r?.source_ref === atlas.microtopic_ref
  ), "SESSION_CORE1B_UNAVAILABLE");
  const core2b = one(coreData.core_projections.filter((r) =>
    r?.id === selector.transferProjectionId
    && atlas.core_projection_refs.includes(r.id)
    && r?.projection?.core === "CORE2B"
  ), "SESSION_CORE2B_UNAVAILABLE", selector.transferProjectionId);

  const activityRef = atlas.activity_refs[0];
  const representationRef = atlas.representation_refs[0];
  const target = physics.visual_targets?.[activityRef];
  need(target?.resource_ref === activityRef, "SESSION_VISUAL_TARGET_UNAVAILABLE", activityRef);
  need(target?.representation_refs?.includes(representationRef), "SESSION_VISUAL_REPRESENTATION_MISMATCH");
  need(target?.availability?.portable_package === "READY" && target?.availability?.standalone === "READY",
    "SESSION_PORTABLE_TARGET_UNAVAILABLE");
  need(typeof target.portable_package_ref === "string" && target.portable_package_ref, "SESSION_PORTABLE_PACKAGE_UNAVAILABLE");

  return {
    matrix_id: atlas.matrix_id,
    rung: atlas.rung,
    microtopic_ref: atlas.microtopic_ref,
    capability_ref: atlas.capability_ref,
    core1b_projection_ref: core1b.id,
    representation_ref: representationRef,
    activity_ref: activityRef,
    portable_package_ref: target.portable_package_ref,
    core2b_projection_ref: core2b.id,
    core2b_source_ref: core2b.source_ref,
    atlas_contract_version: physics.atlas_index_contract_version || null,
  };
}

function fresh(stage = "ORIENT") {
  return {
    stage, unlocked_stage: 1,
    core1b_attempted: false, core1b_revealed: false, core1b_attempts: 0,
    support_requests: 0,
    visual_ready: false, visual_accept_count: 0, visual_reject_count: 0,
    core2b_attempted: false, core2b_disclosed: false, core2b_attempts: 0,
    completed: false,
  };
}

async function bootstrap() {
  const cfg = globalThis.GRADE9V3_MOTION_SESSION_CONFIG;
  if (!cfg || !globalThis.document) return;
  const $ = (q) => document.querySelector(q);
  const status = $("#session-status"), unavailable = $("#session-unavailable");
  const core1b = $("#core1b-learner"), core2b = $("#core2b-learner");
  const frame = $("#portable-frame"), visualStatus = $("#visual-status"), summary = $("#session-summary");
  const traceStatus = $("#trace-status");
  const stages = new Map([...document.querySelectorAll("[data-stage]")].map((n) => [n.dataset.stage, n]));

  let identity = null, state = fresh(), trace = [], capture = true, sequence = 0;
  let runNumber = 1, runId = "run-0001", parentRunId = null;
  let mountCore = null, portableIndex = 0, lastPortableSeq = 0, pendingVisualParent = null;
  let pollTimer = null, portableDelay = 0, portableOverride = null;

  const snap = () => clone(state);
  const idEnvelope = () => clone(identity || { matrix_id: CASE.matrixId, rung: CASE.rung, core2b_projection_ref: CASE.transferProjectionId });

  function record(type, o = {}) {
    if (!capture) return null;
    sequence += 1;
    const prior = clone(o.prior || state), result = clone(o.result || state);
    const event = {
      trace_version: TRACE_VERSION, run_id: runId, parent_run_id: parentRunId,
      sequence, logical_time: sequence, host_mode: cfg.hostMode || "repository",
      stage: result.stage, event_type: type, identity: idEnvelope(),
      prior_state: prior, requested_transition: clone(o.transition || null), resulting_state: result,
      outcome: o.outcome || "OBSERVE", reason_code: o.reason || type,
      invariant_checks: invariantChecks(result), producer: o.producer || "session shell",
      correlation: o.parent ? { parent_sequence: o.parent } : null,
    };
    if (o.facts) event.diagnostic_facts = clone(o.facts);
    trace.push(event);
    return event;
  }

  function render() {
    for (const [name, node] of stages) node.hidden = name !== state.stage;
    for (const b of document.querySelectorAll("[data-stage-target]")) {
      b.disabled = idx(b.dataset.stageTarget) > state.unlocked_stage;
      b.setAttribute("aria-disabled", b.disabled ? "true" : "false");
    }
  }

  function renderSummary() {
    const s = summarizeMotionSessionState(state);
    summary.innerHTML = "";
    const dl = document.createElement("dl");
    for (const [k,v] of [
      ["Core1B attempts",s.attempts.core1b],["Core2B attempts",s.attempts.core2b],
      ["Support requests",s.support_used],["Shared-clock ACCEPT actions",s.visual_actions.accepted],
      ["Shared-clock REJECT actions",s.visual_actions.rejected],["Session completion",s.completion ? "Complete" : "Not complete"]
    ]) {
      const dt=document.createElement("dt"), dd=document.createElement("dd"); dt.textContent=k; dd.textContent=String(v); dl.append(dt,dd);
    }
    const p=document.createElement("p"); p.textContent=s.statement; summary.append(dl,p);
  }

  function failClosed(code, detail) {
    unavailable.hidden = false;
    $("#unavailable-code").textContent = code;
    $("#unavailable-detail").textContent = detail || "Required session input is unavailable.";
    for (const node of stages.values()) node.hidden = true;
    const s=snap(); record("FAIL_CLOSED_UNAVAILABLE",{prior:s,result:s,outcome:"FAIL",reason:code,facts:{detail_present:Boolean(detail)}});
    status.textContent = "Session unavailable: " + code + ".";
  }

  function navigate(target) {
    const prior=snap();
    if (idx(target) < 0 || idx(target) > state.unlocked_stage) {
      record("NAVIGATION_DENIED",{prior,result:prior,outcome:"DENY",reason:"SESSION_STAGE_LOCKED",transition:{from_stage:state.stage,to_stage:target}});
      status.textContent="That stage is not available yet."; return false;
    }
    record("NAVIGATION_PERMITTED",{prior,result:prior,outcome:"ACCEPT",reason:"SESSION_STAGE_AVAILABLE",transition:{from_stage:state.stage,to_stage:target}});
    record("STAGE_EXITED",{prior,result:prior,transition:{from_stage:state.stage,to_stage:target}});
    const before=snap(); state.stage=target; const after=snap();
    record("STAGE_ENTERED",{prior:before,result:after,transition:{from_stage:before.stage,to_stage:target}});
    render(); status.textContent="Stage: "+target+".";
    if (target==="VISUAL" && !state.visual_ready) loadPortable();
    if (target==="SUMMARY" && !state.completed) {
      const p=snap(); state.completed=true; const r=snap();
      record("COMPLETION_RECORDED",{prior:p,result:r,reason:"LOCAL_SESSION_COMPLETE"});
      renderSummary(); record("SUMMARY_CREATED",{prior:r,result:r,reason:"LOCAL_OBSERVATION_SUMMARY"});
    }
    return true;
  }

  function guardAttempt(el, core) {
    el.shadowRoot?.addEventListener("submit",(e)=>{
      const form=e.target?.closest?.("[data-attempt-form]"); if(!form) return;
      const value=el.shadowRoot.querySelector("[data-attempt-input]")?.value || "";
      if(value.trim()) return;
      e.preventDefault(); e.stopPropagation();
      const s=snap(); record("ATTEMPT_REJECTED",{prior:s,result:s,outcome:"DENY",reason:"CORE_LEARNING_GENUINE_ATTEMPT_REQUIRED",
        producer:"Core projection/runtime",facts:{core,response_present:false}});
      status.textContent="Enter a response before committing the attempt.";
    },true);
  }

  function wireCore(el, core) {
    el.addEventListener("attempt_committed",()=>{
      const p=snap();
      if(core==="CORE1B"){state.core1b_attempted=true;state.core1b_attempts+=1;}
      else{state.core2b_attempted=true;state.core2b_attempts+=1;}
      record("ATTEMPT_ACCEPTED",{prior:p,result:snap(),outcome:"ACCEPT",reason:"ATTEMPT_COMMITTED",
        producer:"Core projection/runtime",facts:{core,response_present:true}});
    });
    for (const name of ["support_requested","hint_requested"]) el.addEventListener(name,(e)=>{
      const p=snap(), shown=Boolean(e.detail?.revealed); if(shown) state.support_requests+=1;
      record(name==="support_requested"?"SUPPORT_REQUESTED":"HINT_REQUESTED",{prior:p,result:snap(),outcome:shown?"ACCEPT":"DENY",
        reason:e.detail?.reason || name.toUpperCase(),producer:"Core projection/runtime",facts:{core,revealed:shown}});
    });
    el.addEventListener("reveal_changed",(e)=>{
      const p=snap();
      if(core==="CORE1B" && el.state?.reconstructionVisible){state.core1b_revealed=true;state.unlocked_stage=Math.max(state.unlocked_stage,2);}
      if(core==="CORE2B" && el.state?.reasoningVisible){state.core2b_disclosed=true;state.unlocked_stage=Math.max(state.unlocked_stage,4);}
      record("REVEAL_GRANTED",{prior:p,result:snap(),outcome:"ACCEPT",reason:"CORE_REVEAL_CHANGED",
        producer:"Core projection/runtime",facts:{core,reveal_kind:e.detail?.kind || null}});
      render();
    });
  }

  function configureCores() {
    const regs=globalThis.CORE_LEARNING_REGISTRIES || {};
    mountCore(core1b,globalThis.GRADE9V3_CORE,identity.core1b_projection_ref,regs);
    mountCore(core2b,globalThis.GRADE9V3_CORE,identity.core2b_projection_ref,regs);
    guardAttempt(core1b,"CORE1B"); guardAttempt(core2b,"CORE2B"); wireCore(core1b,"CORE1B"); wireCore(core2b,"CORE2B");
  }

  function resetPortable() {
    if(pollTimer) clearInterval(pollTimer); pollTimer=null; portableIndex=0; lastPortableSeq=0; pendingVisualParent=null;
    state.visual_ready=false; frame.removeAttribute("src"); visualStatus.textContent="The shared-clock activity will load when this stage opens.";
  }

  function portableFail(code,detail) {
    if(pollTimer) clearInterval(pollTimer); pollTimer=null; const s=snap();
    record("PORTABLE_LOAD_FAILED",{prior:s,result:s,outcome:"FAIL",reason:code,producer:"portable workbench",facts:{detail_present:Boolean(detail)}});
    visualStatus.textContent="Shared-clock activity unavailable: "+code+".";
  }

  function ingestPortable(detail, sourceSeq) {
    if(!detail || !Number.isInteger(sourceSeq)) return null;
    if(sourceSeq<=lastPortableSeq){
      const s=snap(), code=sourceSeq===lastPortableSeq?"PORTABLE_EVENT_DUPLICATE":"PORTABLE_EVENT_OUT_OF_ORDER";
      return record("PORTABLE_EVENT_REJECTED",{prior:s,result:s,outcome:"DENY",reason:code,producer:"portable workbench",
        facts:{source_sequence:sourceSeq,event_type:detail.type||null}});
    }
    lastPortableSeq=sourceSeq;
    if(detail.type==="WORKBENCH_READY"){
      if(!state.visual_ready){const p=snap();state.visual_ready=true;record("PORTABLE_READY",{prior:p,result:snap(),reason:"PORTABLE_WORKBENCH_READY",
        producer:"portable workbench",facts:{source_sequence:sourceSeq,scene_id:detail.sceneId||null}});visualStatus.textContent="Shared-clock activity ready.";}
      return null;
    }
    if(detail.type==="ENTITY_PICKED"){
      const s=snap(), ev=record("VISUAL_ACTION_REQUESTED",{prior:s,result:s,reason:"PORTABLE_ENTITY_PICKED",producer:"portable workbench",
        facts:{source_sequence:sourceSeq,entity_ref:detail.entityRef||null}}); pendingVisualParent=ev?.sequence||null; return ev;
    }
    if(detail.type==="TRANSFER_ACCEPTED" || detail.type==="TRANSFER_REJECTED"){
      const p=snap(), accepted=detail.type==="TRANSFER_ACCEPTED";
      if(accepted) state.visual_accept_count+=1; else state.visual_reject_count+=1;
      if(state.visual_accept_count>0 && state.visual_reject_count>0) state.unlocked_stage=Math.max(state.unlocked_stage,3);
      const ev=record("VISUAL_ACTION_RESOLVED",{prior:p,result:snap(),outcome:accepted?"ACCEPT":"REJECT",
        reason:accepted?"PORTABLE_TRANSFER_ACCEPTED":"PORTABLE_TRANSFER_REJECTED",producer:"portable workbench",parent:pendingVisualParent,
        facts:{source_sequence:sourceSeq,workbench_event_type:detail.type,scene_id:detail.sceneId||null,revision:Number.isInteger(detail.revision)?detail.revision:null}});
      pendingVisualParent=null; visualStatus.textContent=accepted?(detail.summary||"Canonical workbench accepted the reconstruction."):(detail.reason||"Canonical workbench rejected the reconstruction.");
      render(); return ev;
    }
    return null;
  }

  function beginPoll() {
    if(pollTimer) clearInterval(pollTimer);
    pollTimer=setInterval(()=>{
      try{
        const w=frame.contentWindow; if(!w) return;
        if(w.__portableWorkbenchError){portableFail("PORTABLE_PACKAGE_LOAD_FAILED",String(w.__portableWorkbenchError));return;}
        const events=Array.isArray(w.__portableEvents)?w.__portableEvents:[];
        while(portableIndex<events.length){ingestPortable(events[portableIndex],portableIndex+1);portableIndex+=1;}
      }catch(e){portableFail("PORTABLE_COMPONENT_ACCESS_FAILED",String(e?.message||e));}
    },80);
  }

  function loadPortable() {
    const s=snap(); record("PORTABLE_LOAD_REQUESTED",{prior:s,result:s,reason:portableDelay>0?"PORTABLE_WAITING_FOR_DELAY":"PORTABLE_LOAD_REQUESTED",
      facts:{delayed:portableDelay>0}}); visualStatus.textContent=portableDelay>0?"Waiting for the shared-clock activity…":"Loading the shared-clock activity…";
    const ref=portableOverride || identity.portable_package_ref;
    setTimeout(()=>{const sep=cfg.portableBase.includes("?")?"&":"?";frame.src=cfg.portableBase+sep+"package="+encodeURIComponent(ref)+"&session_run="+encodeURIComponent(runId);beginPoll();},portableDelay);
  }

  function newRun(kind) {
    const old=runId, oldState=snap();
    record(kind==="retry"?"RETRY_REQUESTED":"RESET_REQUESTED",{prior:oldState,result:oldState,reason:kind==="retry"?"SESSION_RETRY":"SESSION_RESET"});
    runNumber+=1; parentRunId=old; runId="run-"+String(runNumber).padStart(4,"0"); state=fresh(kind==="retry"?"CORE1B":"ORIENT");
    configureCores(); resetPortable(); const s=snap();
    record("RECOVERY_STARTED",{prior:s,result:s,reason:kind==="retry"?"RETRY_NEW_RUN":"RESET_NEW_RUN",facts:{predecessor_run_id:old}});
    render(); renderSummary(); status.textContent=kind==="retry"?"Retry started with a clean learner state.":"Session reset.";
  }

  function exportObject() {
    return { trace_version:TRACE_VERSION, case_identity:idEnvelope(), events:clone(trace), replay:replayMotionSessionTrace(trace),
      privacy:{response_text_recorded:false,pii_recorded:false,network_telemetry:false} };
  }
  function downloadTrace() {
    const blob=new Blob([JSON.stringify(exportObject(),null,2)+"\n"],{type:"application/json"}), url=URL.createObjectURL(blob), a=document.createElement("a");
    a.href=url;a.download="motion-shared-clock-session-trace.json";a.click();URL.revokeObjectURL(url);
    traceStatus.textContent="Trace exported locally. No learner response text is included.";
  }

  for(const b of document.querySelectorAll("[data-stage-target]")) b.addEventListener("click",()=>navigate(b.dataset.stageTarget));
  $("#retry-session")?.addEventListener("click",()=>newRun("retry"));
  $("#reset-session")?.addEventListener("click",()=>newRun("reset"));
  $("#export-trace")?.addEventListener("click",downloadTrace);

  record("SESSION_START",{prior:snap(),result:snap(),reason:"SESSION_STARTED"});
  try{
    const requested=new URL(location.href).searchParams.get("case");
    const selector=requested==="unknown"?{...CASE,matrixId:"MATRIX-PHY-UNKNOWN-SESSION-CASE"}:CASE;
    identity=resolveMotionSessionIdentity(globalThis.GRADE9V3,globalThis.GRADE9V3_CORE,selector);
    const s=snap();record("IDENTITY_RESOLVED",{prior:s,result:s,outcome:"ACCEPT",reason:"SESSION_IDENTITY_RESOLVED"});
    await import(cfg.semanticModule); await import(cfg.corePageModule); mountCore=(await import(cfg.coreHostModule)).mountCoreLearningPage;
    configureCores(); render(); renderSummary();
    status.textContent="Ready. Commit your own reasoning before protected reconstruction or transfer reasoning is shown.";
  }catch(e){failClosed(e?.code||"SESSION_INITIALIZATION_FAILED",String(e?.message||e));}

  globalThis.__motionSession={
    get state(){return snap();}, get identity(){return clone(identity);}, get trace(){return clone(trace);},
    exportTraceObject:exportObject,replayTrace:replayMotionSessionTrace,navigate,retry:()=>newRun("retry"),reset:()=>newRun("reset"),
    setTraceCapture(v){capture=Boolean(v);},
    __test:{
      ingestPortableEvent:ingestPortable,setPortableDelay(ms){portableDelay=Math.max(0,Number(ms)||0);},
      setPortablePackage(ref){portableOverride=ref||null;},forcePortableReload(){resetPortable();loadPortable();}
    }
  };
}

if(globalThis.document && globalThis.GRADE9V3_MOTION_SESSION_CONFIG) bootstrap();
