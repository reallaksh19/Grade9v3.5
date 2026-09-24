export const TRACE_VERSION = "motion-session-trace/1.0";
export const STAGES = Object.freeze(["ORIENT", "CORE1B", "VISUAL", "CORE2B", "SUMMARY"]);

const clone = (v) => v == null ? v : JSON.parse(JSON.stringify(v));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const stageIndex = (s) => STAGES.indexOf(s);

export function validSessionState(s) {
  return Boolean(
    s && STAGES.includes(s.stage)
    && Number.isInteger(s.unlocked_stage) && s.unlocked_stage >= 0 && s.unlocked_stage < STAGES.length
    && stageIndex(s.stage) <= s.unlocked_stage
    && ["core1b_attempts","core2b_attempts","support_requests","visual_accept_count","visual_reject_count"]
      .every((k) => Number.isInteger(s[k]) && s[k] >= 0)
  );
}

export function summarizeMotionSessionState(s) {
  return {
    attempts: { core1b: s.core1b_attempts, core2b: s.core2b_attempts },
    support_used: s.support_requests,
    visual_actions: { accepted: s.visual_accept_count, rejected: s.visual_reject_count },
    completion: Boolean(s.completed),
    statement: "This summary records observations from this local session only. It does not claim mastery or readiness.",
  };
}

function bad(event, code, detail = "") {
  return {
    ok: false,
    code,
    detail,
    first_divergent_sequence: event?.sequence ?? null,
    event_type: event?.event_type ?? null,
    component_boundary: event?.producer ?? "trace",
  };
}

export function replayMotionSessionTrace(input) {
  const events = Array.isArray(input) ? input : (Array.isArray(input?.events) ? input.events : []);
  if (!events.length) return bad(null, "TRACE_EMPTY", "No diagnostic events supplied.");
  let expected = 1;
  let finalState = null;
  const byRun = new Map();

  for (const event of events) {
    if (event?.trace_version !== TRACE_VERSION) return bad(event, "TRACE_VERSION_UNSUPPORTED", String(event?.trace_version));
    if (!Number.isInteger(event.sequence)) return bad(event, "TRACE_SEQUENCE_INVALID", String(event?.sequence));
    if (event.sequence < expected) {
      return bad(event, event.sequence === expected - 1 ? "TRACE_SEQUENCE_DUPLICATE" : "TRACE_SEQUENCE_OUT_OF_ORDER",
        "expected " + expected + ", observed " + event.sequence);
    }
    if (event.sequence > expected) return bad(event, "TRACE_SEQUENCE_GAP", "expected " + expected + ", observed " + event.sequence);
    expected += 1;
    if (!validSessionState(event.prior_state) || !validSessionState(event.resulting_state)) {
      return bad(event, "TRACE_STATE_INVALID", "State shape or stage invariant failed.");
    }
    const prior = byRun.get(event.run_id);
    if (prior && !same(prior, event.prior_state)) {
      return bad(event, "TRACE_PRIOR_STATE_MISMATCH", "prior_state does not match reconstructed state.");
    }
    if (event.event_type === "STAGE_ENTERED") {
      const target = event.requested_transition?.to_stage;
      if (!STAGES.includes(target) || event.resulting_state.stage !== target) {
        return bad(event, "TRACE_STAGE_TRANSITION_INVALID", String(target));
      }
      if (stageIndex(target) > event.resulting_state.unlocked_stage) {
        return bad(event, "TRACE_STAGE_LOCK_VIOLATION", target);
      }
    }
    if (event.event_type === "COMPLETION_RECORDED") {
      const s = event.resulting_state;
      if (!s.core2b_disclosed || s.visual_accept_count < 1 || s.visual_reject_count < 1) {
        return bad(event, "TRACE_COMPLETION_PRECONDITION_FAILED");
      }
    }
    byRun.set(event.run_id, clone(event.resulting_state));
    finalState = clone(event.resulting_state);
  }

  return {
    ok: true,
    code: "TRACE_REPLAY_OK",
    final_state: finalState,
    diagnostic_summary: summarizeMotionSessionState(finalState),
    event_count: events.length,
  };
}

export function invariantChecks(s) {
  return [
    { id: "SESSION_STATE_SHAPE_VALID", pass: validSessionState(s) },
    { id: "NO_MASTERY_STATE", pass: !Object.prototype.hasOwnProperty.call(s, "mastery") },
    { id: "CORE2B_DISCLOSURE_AFTER_ATTEMPT", pass: !s.core2b_disclosed || s.core2b_attempted },
    { id: "SUMMARY_AFTER_REQUIRED_VISUALS", pass: !s.completed || (s.visual_accept_count > 0 && s.visual_reject_count > 0) },
  ];
}
