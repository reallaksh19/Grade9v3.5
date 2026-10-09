/** Canonical compiler-bound Core2A familiar → Core2B new-decision progression.
 * Structural evidence only. Neither declared novelty nor HTML navigation is an
 * independent academic judgement or proof a learner has mastered prior material.
 */
const VALID_DIMENSIONS = new Set([
  "model_choice", "representation_translation", "reasoning_steps", "novelty",
]);
const text = (value) => typeof value === "string" && value.trim().length > 0;
const list = (value) => Array.isArray(value) ? value : [];
const role = (row) => row?.projection?.core;
const app = (row) => row?.projection?.application;

function sameGroup(data, id) {
  const rows = list(data?.core_projections);
  const selection = rows.filter((row) => row?.id === id);
  if (selection.length !== 1) return { selected: null, findings: ["SELECTED_PROJECTION_NOT_UNIQUE"] };
  const selected = selection[0];
  if (!["CORE2A", "CORE2B"].includes(role(selected))) {
    return { selected, outside: true, findings: [] };
  }
  const groups = list(data?.bucket_availability).filter((group) =>
    group?.status === "AVAILABLE" && group?.subject === selected.subject
    && list(group.projection_refs).includes(selected.id)
  );
  if (groups.length !== 1) {
    return { selected, findings: ["CANONICAL_PRACTICE_BUCKET_NOT_UNIQUE"] };
  }
  const group = groups[0];
  return {
    selected, group, findings: [],
    rows: rows.filter((row) => row?.subject === selected.subject
      && list(group.projection_refs).includes(row?.id)),
  };
}

function inspectPair(parent, child) {
  const a = app(parent);
  const b = app(child);
  const transfer = b?.transfer;
  const moves = list(b?.reasoning_route);
  const protectedMove = moves.filter((move) =>
    move?.id === transfer?.protected_move_ref
  );
  const whyNew = transfer?.novelty?.why_new;
  const findings = [];
  const fail = (code) => findings.push(code);
  if (role(parent) !== "CORE2A" || role(child) !== "CORE2B"
      || parent?.subject !== child?.subject) {
    fail("EXPOSURE_ROLES_INVALID");
  }
  if (!text(a?.question_ref) || !text(b?.question_ref)
      || parent?.source_ref !== a.question_ref || child?.source_ref !== b.question_ref) {
    fail("CANONICAL_QUESTION_IDENTITY_MISMATCH");
  }
  if (!text(a?.family_ref) || a.family_ref !== b?.family_ref) fail("FAMILY_LINEAGE_MISMATCH");
  if (!list(transfer?.builds_on).includes(a?.question_ref)) fail("CORE2A_PARENT_NOT_IN_TRANSFER_LINEAGE");
  const parentMoves = list(a?.reasoning_route);
  if (!text(a?.crux_move_ref) || !parentMoves.some((move) =>
      move?.id === a.crux_move_ref && text(move.action))
      || !list(a?.solution?.steps).length || !text(a?.check)) {
    fail("CORE2A_FAMILIAR_REASONING_INCOMPLETE");
  }
  if (!VALID_DIMENSIONS.has(transfer?.dimension) || !text(transfer?.statement)
      || !text(transfer?.invariant) || !text(whyNew)) {
    fail("CORE2B_CHANGED_DEMAND_EVIDENCE_INCOMPLETE");
  }
  if (protectedMove.length !== 1 || protectedMove[0]?.kind !== "DECIDE"
      || !text(protectedMove[0]?.action)
      || b?.crux_move_ref !== transfer?.protected_move_ref) {
    fail("CORE2B_PROTECTED_DECISION_NOT_BOUND");
  }
  if (!text(b?.repair?.step_ref)
      || !list(b?.solution?.rubric).length
      || !b.solution.rubric.every((rubric) =>
        text(rubric?.criterion) && text(rubric?.evidence_of))) {
    fail("CORE2B_REPAIR_OR_RUBRIC_INCOMPLETE");
  }
  const pa = parent?.projection?.presentation || {};
  const pb = child?.projection?.presentation || {};
  if (pa.attempt_before_reveal !== false
      || pb.attempt_before_reveal !== true
      || pb.show_solution_initially !== false
      || !list(pb.protected_move_refs).includes(transfer?.protected_move_ref)) {
    fail("CORE2B_ATTEMPT_OR_PROTECTED_W_POLICY_INVALID");
  }
  if (a?.question_ref === b?.question_ref
      || (text(a?.stem) && a.stem === b?.stem)) {
    fail("CORE2B_NO_CHANGED_QUESTION");
  }
  return {
    source: "COMPILER_BOUND_QUESTION_LINEAGE",
    status: findings.length ? "HOLD" : "STRUCTURED_REVIEW_REQUIRED",
    findings, parent_ref: a?.question_ref || null,
    child_ref: b?.question_ref || null,
    family_ref: a?.family_ref || null,
    transfer_dimension: transfer?.dimension || null,
    invariant: transfer?.invariant || null,
    changed_demand_statement: transfer?.statement || null,
    academic_acceptance: "NOT_EVALUATED",
    learner_prerequisite: "NOT_EVALUATED",
    source_custody: "NOT_EVALUATED",
  };
}

export function resolveFamiliarTransfer(data, selectedId) {
  const context = sameGroup(data, selectedId);
  if (context.outside) return {
    status: "OUTSIDE_PRACTICE", pairs: [], findings: [],
  };
  if (context.findings.length) return {
    status: "HOLD", pairs: [], findings: context.findings,
  };
  const { selected, rows } = context;
  const parents = rows.filter((row) => role(row) === "CORE2A");
  const children = rows.filter((row) => role(row) === "CORE2B");
  const selectedRef = app(selected)?.question_ref;
  const pairs = [];
  const findings = [];
  for (const child of children) {
    const transfer = app(child)?.transfer;
    const parentsInLineage = parents.filter((parent) =>
      list(transfer?.builds_on).includes(app(parent)?.question_ref));
    if (role(selected) === "CORE2B" && child.id !== selected.id) continue;
    if (role(selected) === "CORE2A"
        && !parentsInLineage.some((p) => p.id === selected.id)) continue;
    if (parentsInLineage.length !== 1) {
      findings.push(`CORE2B_FAMILIAR_PARENT_NOT_UNIQUE:${child.source_ref}`);
      continue;
    }
    const parent = parentsInLineage[0];
    const checked = inspectPair(parent, child);
    if (checked.findings.length) {
      findings.push(...checked.findings.map((code) => `${code}:${child.source_ref}`));
      continue;
    }
    pairs.push({
      ...checked, subject: selected.subject,
      parent_projection_id: parent.id,
      transfer_projection_id: child.id,
      prior_exposure_required: true,
    });
  }
  if (role(selected) === "CORE2B" && pairs.length !== 1 && !findings.length) {
    findings.push("SELECTED_CORE2B_HAS_NO_COMPILED_FAMILIAR_PARENT");
  }
  return {
    status: findings.length ? (pairs.length ? "PARTIAL" : "HOLD")
      : pairs.length ? "STRUCTURED_REVIEW_REQUIRED" : "NO_TRANSFER_CHILD",
    pairs,
    findings,
    academic_acceptance: "NOT_EVALUATED",
  };
}

/** Resolve a specifically authored Core2B repair to an actual compiled Core1A
 * teaching step. This is a learner-selected assisted route, never a diagnosis
 * or a judgement that the step adequately repairs the claimed misconception.
 */
export function resolveTransferRepair(data, selectedId) {
  const context = sameGroup(data, selectedId);
  if (context.findings.length || context.outside) {
    return { status: "HOLD", paths: [], findings: context.findings.length
      ? context.findings : ["TRANSFER_REPAIR_OUTSIDE_APPLICATION"] };
  }
  const { selected, rows } = context;
  if (role(selected) !== "CORE2B") {
    return { status: "OUTSIDE_TRANSFER", paths: [], findings: [] };
  }
  const repair = app(selected)?.repair;
  if (!text(repair?.step_ref) || !text(repair?.microtopic_ref)) {
    return { status: "HOLD", paths: [], findings: ["SPECIFIC_REPAIR_REFERENCE_MISSING"] };
  }
  const candidates = rows.filter((row) =>
    role(row) === "CORE1A" && row.projection?.concept?.microtopic_ref === repair.microtopic_ref
    && row.source_ref === repair.microtopic_ref
    && list(row.projection?.concept?.teaching_path).filter((step) =>
      step?.id === repair.step_ref && text(step.action)
      && (!text(repair.action) || step.action === repair.action)).length === 1);
  if (candidates.length !== 1) {
    return { status: "HOLD", paths: [], findings: ["REPAIR_TEACHING_STEP_NOT_UNIQUE_IN_CANONICAL_BUCKET"] };
  }
  return {
    status: "CANONICAL_REPAIR_STEP_REVIEW_REQUIRED",
    findings: [],
    paths: [{
      origin_projection_id: selected.id,
      origin_question_ref: app(selected)?.question_ref,
      target_projection_id: candidates[0].id,
      repair_step_ref: repair.step_ref,
      repair_microtopic_ref: repair.microtopic_ref,
      learner_diagnosis: "NOT_ESTABLISHED",
      learner_return_type: "SAME_QUESTION_ASSISTED_RETRY",
      repair_adequacy: "NOT_INDEPENDENTLY_EVALUATED",
    }],
  };
}
