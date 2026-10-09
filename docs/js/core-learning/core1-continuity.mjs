/** Compiler-bound Core1 → Core1A → Core1B route lookup.
 * Uses only bucket_availability and already compiled CoreProjection records.
 * Does not infer a new academic concept from question text or claim mastery.
 */
const CORES = new Set(["CORE1", "CORE1A", "CORE1B"]);
const validString = (value) => typeof value === "string" && value.trim().length > 0;
const eq = (a, b) => JSON.stringify(a ?? []) === JSON.stringify(b ?? []);

function rowFor(data, id) {
  const rows = Array.isArray(data?.core_projections) ? data.core_projections : [];
  const found = rows.filter((row) => row?.id === id);
  return found.length === 1 ? found[0] : null;
}

function coherent(a, b, conceptId) {
  const left = a?.projection?.concept;
  const right = b?.projection?.concept;
  const pa = a?.projection?.presentation || {};
  const pb = b?.projection?.presentation || {};
  const cycle = right?.elicitation;
  return left?.microtopic_ref === conceptId
    && right?.microtopic_ref === conceptId
    && a?.source_ref === conceptId
    && b?.source_ref === conceptId
    && validString(left.inferential_jump)
    && left.inferential_jump === right.inferential_jump
    && eq(left.representation_refs, right.representation_refs)
    && eq(left.entry_assumptions, right.entry_assumptions)
    && eq(left.teaching_path, right.teaching_path)
    && pa.attempt_before_reveal === false
    && pa.show_full_construction === true
    && pb.attempt_before_reveal === true
    && pb.show_full_construction === false
    && eq(left.misconceptions, right.misconceptions)
    && Array.isArray(left.misconceptions) && left.misconceptions.length > 0
    && left.misconceptions.every((item) => ["wrong_idea", "diagnostic_prompt", "repair"]
      .every((key) => validString(item?.[key])))
    && cycle && ["predict", "attempt", "reconstruct", "boundary_test"]
      .every((field) => cycle[field] && typeof cycle[field] === "object")
    && validString(cycle.predict.prompt)
    && validString(cycle.attempt.produces)
    && Array.isArray(cycle.reconstruct.route) && cycle.reconstruct.route.length > 0
    && validString(cycle.boundary_test.prompt)
    && validString(cycle.boundary_test.answer);
}

/** Never return navigable links to a partial or mismatched study route. */
export function resolveCore1StudyContinuity(data, selectedId) {
  const selected = rowFor(data, selectedId);
  if (!selected) return { status: "HOLD", paths: [], findings: ["SELECTED_PROJECTION_MISSING"] };
  const core = selected?.projection?.core;
  if (!CORES.has(core)) return { status: "OUTSIDE_CORE1_STUDY", paths: [], findings: [] };
  const groups = (Array.isArray(data?.bucket_availability) ? data.bucket_availability : [])
    .filter((group) => group?.status === "AVAILABLE"
      && group?.subject === selected.subject
      && Array.isArray(group.projection_refs)
      && group.projection_refs.includes(selected.id));
  if (groups.length !== 1) {
    return { status: "HOLD", paths: [], findings: ["BUCKET_PROJECTION_MEMBERSHIP_NOT_UNIQUE"] };
  }
  const group = groups[0];
  const projections = (Array.isArray(data?.core_projections) ? data.core_projections : [])
    .filter((row) => group.projection_refs.includes(row?.id)
      && row?.subject === group.subject);
  const one = projections.filter((row) => row?.projection?.core === "CORE1"
    && row?.source_ref === group.bucket_ref
    && row?.projection?.orientation?.bucket_ref === group.bucket_ref);
  if (one.length !== 1) {
    return { status: "HOLD", paths: [], findings: ["CORE1_CANONICAL_BUCKET_ROUTE_MISSING"] };
  }
  const aRows = projections.filter((row) => row?.projection?.core === "CORE1A");
  const bRows = projections.filter((row) => row?.projection?.core === "CORE1B");
  const selectedConcept = core === "CORE1"
    ? null : selected?.projection?.concept?.microtopic_ref;
  const candidates = selectedConcept
    ? [...aRows, ...bRows].filter((row) => row?.source_ref === selectedConcept)
    : [...aRows, ...bRows];
  const refs = [...new Set(candidates.map((row) => row?.source_ref).filter(validString))].sort();
  const findings = [];
  const paths = [];
  for (const conceptRef of refs) {
    const as = aRows.filter((row) => row.source_ref === conceptRef);
    const bs = bRows.filter((row) => row.source_ref === conceptRef);
    if (as.length !== 1 || bs.length !== 1 || !coherent(as[0], bs[0], conceptRef)) {
      findings.push(`CORE1A_CORE1B_IDENTITY_OR_RECONSTRUCTION_HOLD:${conceptRef}`);
      continue;
    }
    const a = as[0], b = bs[0];
    paths.push({
      subject: group.subject, bucket_ref: group.bucket_ref,
      microtopic_ref: conceptRef,
      title: a.projection.concept.title || conceptRef,
      steps: [
        { core: "CORE1", id: one[0].id },
        { core: "CORE1A", id: a.id },
        { core: "CORE1B", id: b.id },
      ],
    });
  }
  if (selectedConcept && !paths.length && !findings.length) {
    findings.push("SELECTED_MICROTOPIC_WITHOUT_A_B_ROUTE");
  }
  if (!selectedConcept && !refs.length) findings.push("BUCKET_WITHOUT_STUDY_MICROTOPICS");
  return {
    status: findings.length ? (paths.length ? "PARTIAL" : "HOLD") : "COMPLETE",
    paths, findings,
  };
}
