# GCDR Quality Audit Checklist v1.2

This checklist is the executable quality gate for **GCDR Blueprint v1.3**. It records whether
the implementation has actually been checked; it does not confer scientific, pedagogical,
curriculum or learner-release authority.

Explorer audit state is carried by
`resource.extensions.topic_atlas.gcdr_contract.quality_audit`. Master-suite item/helper/delivery
governance is validated through the v1.3 companion schemas and
`Shared/tools/gcdr_suite_guard.py`.

## Audit states

Each explorer check is one of:

- `PASS` — checked with evidence;
- `FAIL` — checked and found non-conformant;
- `PENDING` — not yet checked or evidence is incomplete;
- `NOT_APPLICABLE` — genuinely outside the activity, with mandatory waiver rationale.

Only the three external-state checks — `control_state_mapping`,
`no_invented_exact_parameters`, and `interaction_fidelity_disclosed` — may be
`NOT_APPLICABLE`, and only when `external_state_mapping=NOT_APPLICABLE`.

`quality_audit.audit_status=PASS` requires every check to be `PASS` or valid
`NOT_APPLICABLE`, matching per-check receipts for asserted PASS/FAIL states, audit provenance,
an audit date, and no unresolved findings.

## Audit 1 — Canonical Truth, Source & Scope

| Check id | Requirement |
|---|---|
| `canonical_binding` | The activity supports the declared capability and semantic leaf; it does not teach a nearby but different claim. |
| `assumptions_and_conventions` | Frame, sign convention, system boundary, event definition and governing assumptions are explicit where relevant. |
| `derivation_or_model_check` | Equations, derived relations and model-selection claims have been independently checked. |
| `units_constants_parameters` | Units, constants, initial conditions and parameters are consistent across the implementation. |
| `boundary_limit_cases` | Boundary, limiting and exception cases have been tested so conditional rules are not presented as universal. |
| `source_claim_fidelity` | Source-derived facts and authored adaptations are distinguished; source/curriculum authority is not silently strengthened. |
| `corpus_snapshot_provenance` | External corpus provider/topic, snapshot date, live count, embedded count and coverage claim are explicit where a corpus is cited. |
| `instructional_depth_scope` | Canonical binding status and instructional depth distinguish school-core material from advanced/unbound extensions. |

## Audit 2 — State, Representation & Geometry Fidelity

| Check id | Requirement |
|---|---|
| `single_state_source` | One authoritative state drives the scene, controls, overlays, equations, tables, graphs and derived readouts. |
| `representation_synchronization` | Coordinated views use the same time/event, frame, sign convention, system boundary, units and active model. |
| `direct_manipulation_is_causal` | Manipulation changes governing state/model rather than cosmetic labels. |
| `counterfactual_is_honest` | Wrong-model mode computes/renders the wrong model and exposes its contradiction. |
| `progressive_disclosure` | Prediction occurs before answer/invariant reveal in learner mode. |
| `control_state_mapping` | Every external/preset parameter maps to the state variable that actually governs the simulation. |
| `no_invented_exact_parameters` | Missing/symbolic parameters are never replaced by convenient defaults and described as exact. |
| `interaction_fidelity_disclosed` | External tasks visibly distinguish `EXACT`, `CONSTRAINT_FAITHFUL`, `CONCEPT_ONLY`, and `UNAVAILABLE`. |
| `representation_equivalence` | Alternate views of the same mathematical object satisfy declared representation invariants within their tolerance. |
| `rendered_geometry_truth` | Rendered points, vectors, planes, curves, event markers and derived geometry agree with an independent state/math oracle. |

Representation equivalence and geometry truth are semantic checks. Passing JavaScript execution
or a screenshot smoke test does not establish either one.

## Audit 3 — Reconstruction, Helpers & Transfer

| Check id | Requirement |
|---|---|
| `answer_or_disposition_specific` | Final result/disposition is task-specific, never generic filler such as “apply formula”. |
| `derivation_specific` | Worked reasoning follows the actual quantities, constraints and model. |
| `independent_check` | A second check exists where meaningful: substitution, derivative, reconstruction, dimension, invariant, limiting case or equivalent. |
| `misconception_trap_specific` | Trap alert names the concrete tempting wrong model and why it fails here. |
| `transfer_takeaway_specific` | Takeaway is a reusable decision rule for a fresh problem, not a category slogan. |
| `boundary_recognition` | The learner identifies where the invariant/shortcut ceases to apply. |
| `scaffold_fade` | Labels/hints/overlays are withdrawn so success is not explorer-dependent. |
| `fresh_transfer` | Exit evidence includes a materially fresh task without the explorer. |
| `helper_activation` | Required helpers are not merely present by name; their governed state/item inputs, required outputs, activation status and audit evidence are explicit. |

Helper lifecycle is `DECLARED → IMPLEMENTED → AUDITED`. Only `AUDITED` helpers count toward
a claim that helper activation has passed audit.

## Audit 4 — Runtime, Packaging & Release Integrity

| Check id | Requirement |
|---|---|
| `implementation_locator` | The governed implementation locator resolves to the intended artifact. |
| `static_syntax` | Executable code/data parse under supported static checks. |
| `handler_and_control_integrity` | Interactive controls resolve to real handlers/state transitions. |
| `identifier_integrity` | Required-unique DOM/component IDs are unique and references resolve. |
| `no_placeholder_or_undefined_output` | Learner-visible output contains no undefined/missing-field leakage, filler answers or fake success. |
| `deterministic_reset` | Reset restores documented initial state across all representations. |
| `runtime_smoke` | Core interaction path has been executed in a supported runtime; limitations remain explicit. |
| `accessibility_baseline` | Essential controls are labelled/focusable and not dependent solely on color/hover/animation. |
| `delivery_profile_integrity` | The released artifact satisfies its declared `REPO_BUNDLE`, `SINGLE_FILE_ONLINE`, or `SINGLE_FILE_OFFLINE` profile. |

## Diagnostic-item gate

`gcdr_diagnostic_item.schema.json` governs each normalized item. A release fails when an item
lacks source status, final answer, item-specific derivation, independent check, trap, transfer
rule, helper declarations or simulator fidelity.

Generic final-answer text is a release blocker.

For simulation fidelity:

- `EXACT` — every active governing binding is represented and at least one binding ref exists;
- `CONSTRAINT_FAITHFUL` — genuine partial constraints are represented and binding refs identify them;
- `CONCEPT_ONLY` — relevant mechanism only; no question-specific binding refs;
- `UNAVAILABLE` — no simulator state claim; no binding refs.

The missing-parameter rule remains `NEVER_INVENT_AS_EXACT`.

## Corpus and scope gate

External corpus claims use snapshot metadata and one coverage label:

- `FULL_CORPUS_AUDITED`;
- `CURATED_SLICE_AUDITED`;
- `DEMAND_RECONNAISSANCE_ONLY`.

Scope status is independent of content quality:

- `BOUND`;
- `PARTIAL`;
- `UNBOUND_EXTENSION`.

Advanced material may remain useful while being ineligible for canonical certification.

## Delivery-profile gate

- `REPO_BUNDLE`: repository-local dependencies may be separate.
- `SINGLE_FILE_ONLINE`: repository-local runtime/data dependencies are embedded; declared remote dependencies may remain.
- `SINGLE_FILE_OFFLINE`: no local companion runtime/data file and no remote runtime dependency.

The suite guard compares declared remote dependencies with the actual artifact and checks that
single-file builds do not retain local script/stylesheet dependencies. It also verifies that the
embedded standalone question bank matches the canonical diagnostic source.

## Runtime and geometry evidence

`Shared/tools/gcdr_runtime_audit.py` remains the generic Audit-4 static/DOM-lite falsifier for
governed explorers. It intentionally reports
`STATIC_PLUS_DOM_LITE_JS_RUNTIME_NOT_VISUAL_BROWSER_PROOF`.

Subject-owned property sweeps provide mathematical/geometry evidence. For Motion in 2D,
`Physics/tools/motion2d_gcdr_properties.py` remains separate from shared GCDR governance.

## Per-check receipts and provenance

Every asserted explorer `PASS` or `FAIL` requires a matching `audit_receipt` containing
check id, outcome, method, evidence reference, artifact digest, timestamp, auditor and note.
Stale outcome or runtime-digest evidence fails the explorer guard.

## Certification rule

A GCDR activity may claim `CERTIFIED` only when:

1. every implementation-evidence flag is true;
2. `quality_audit.audit_status=PASS`;
3. every quality check is `PASS` or valid `NOT_APPLICABLE`;
4. asserted PASS/FAIL states have matching digest-bound receipts;
5. provenance and audit date are recorded;
6. no unresolved quality findings remain;
7. scope, representation-invariant, geometry-truth and delivery-profile hooks are valid; and
8. semantic-leaf, capability, sequence, runtime-honesty and implementation-locator guards pass.

For master suites, item/helper/suite contracts must additionally pass
`Shared/tools/gcdr_suite_guard.py --enforce`.

Certification remains structural and implementation-audit conformance only. Scientific,
pedagogical, empirical learner and learner-release authority remain separate governed decisions.
