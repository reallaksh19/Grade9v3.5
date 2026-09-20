# GCDR Quality Audit Checklist v1.1

This checklist is the executable quality gate for the **Graphical Cognitive Deconstruction Route (GCDR)**.

It converts the blueprint's review questions into auditable state carried by
`resource.extensions.topic_atlas.gcdr_contract.quality_audit`.

The checklist does not confer scientific, pedagogical, curriculum, or learner-release authority.
It records whether the implementation has actually been checked against the GCDR contract.

## Audit states

Each check is one of:

- `PASS` — checked with evidence;
- `FAIL` — checked and found non-conformant;
- `PENDING` — not yet checked or evidence is incomplete;
- `NOT_APPLICABLE` — genuinely outside this activity, with a mandatory waiver rationale. Core GCDR checks are non-waivable; this state is reserved for the three external-state mapping checks when `external_state_mapping=NOT_APPLICABLE`.

`quality_audit.audit_status=PASS` is valid only when every check is `PASS` or justified
`NOT_APPLICABLE`, every asserted PASS/FAIL is backed by a matching per-check `audit_receipt`,
`audit_provenance` identifies how the audit was performed, `last_audited` is present, and
`unresolved_findings` is empty.

## Audit 1 — Canonical Truth & Scope

| Check id | Requirement |
|---|---|
| `canonical_binding` | The activity supports the declared capability and semantic leaf; it does not teach a nearby but different claim. |
| `assumptions_and_conventions` | Assumptions, frame, sign convention, system boundary, event definition, and other governing conventions are explicit where relevant. |
| `derivation_or_model_check` | Governing equations, derived relations, and model-selection claims have been independently checked rather than copied from implementation text. |
| `units_constants_parameters` | Units, constants, initial conditions, and declared parameters are internally consistent and preserved across the implementation. |
| `boundary_limit_cases` | Boundary, limiting, and exception cases have been tested so a conditional rule is not presented as universal. |
| `source_claim_fidelity` | Source-derived facts and authored adaptations are distinguished; the activity does not silently strengthen source or curriculum authority. |

## Audit 2 — Graphical Deconstruction & State Fidelity

| Check id | Requirement |
|---|---|
| `single_state_source` | One authoritative state drives the scene, controls, overlays, equations, tables, graphs, and derived readouts. |
| `representation_synchronization` | Coordinated views use the same time/event, frame, sign convention, system boundary, units, and active model. |
| `direct_manipulation_is_causal` | Manipulation changes the governing state/model; controls are not cosmetic mocks that only alter labels or banners. |
| `counterfactual_is_honest` | A wrong-model mode actually computes/renders that wrong model and exposes its contradiction; it is not a scripted warning detached from state. |
| `progressive_disclosure` | Prediction occurs before the answer/invariant is revealed in learner mode. |
| `control_state_mapping` | Every externally loaded or preset parameter maps to the control/state variable that actually governs the simulation. |
| `no_invented_exact_parameters` | Missing or symbolic parameters are never replaced by convenient defaults and then described as an exact load. |
| `interaction_fidelity_disclosed` | The learner can tell whether an external task is represented as `EXACT`, `CONSTRAINT_FAITHFUL`, `CONCEPT_ONLY`, or `UNAVAILABLE`. |

## Audit 3 — Reconstruction, Teaching Support & Transfer

Every GCDR implementation must provide a learner-facing or teacher/debug explanation layer.
The UI label may vary; the required reasoning jobs do not.

| Check id | Requirement |
|---|---|
| `answer_or_disposition_specific` | The final result/disposition is specific to the current task/state, never a family-level placeholder such as “apply the formula”. |
| `derivation_specific` | Worked reasoning follows the actual quantities, constraints, and model of the task rather than a reusable boilerplate derivation. |
| `independent_check` | A second check exists where meaningful: substitution, derivative, vector reconstruction, dimensional check, invariant, limiting case, or equivalent. |
| `misconception_trap_specific` | The trap alert names the concrete tempting wrong model and why it fails here. |
| `transfer_takeaway_specific` | The takeaway is a reusable decision rule for a new problem, not a category slogan or summary filler. |
| `boundary_recognition` | The learner must identify where the invariant/shortcut ceases to apply. |
| `scaffold_fade` | Labels/hints/overlays are withdrawn so success is not dependent on the full explorer. |
| `fresh_transfer` | Exit evidence includes a materially fresh task without the explorer. |

## Audit 4 — Runtime & Release Integrity

| Check id | Requirement |
|---|---|
| `implementation_locator` | The governed implementation locator exists and resolves to the intended artifact. |
| `static_syntax` | Executable code and data parse/compile under the project's supported static checks. |
| `handler_and_control_integrity` | Interactive controls resolve to real handlers/state transitions; no dead or stale control IDs remain. |
| `identifier_integrity` | DOM/component identifiers that must be unique are unique and references resolve deterministically. |
| `no_placeholder_or_undefined_output` | Learner-visible output contains no `undefined`, missing-field leakage, generic placeholder answers, or fake success states. |
| `deterministic_reset` | Reset restores the documented initial state across all representations, not merely slider positions. |
| `runtime_smoke` | The core predict → manipulate → observe → reconstruct path has been executed in a supported runtime, with limitations recorded if it cannot be run. |
| `accessibility_baseline` | Essential controls have labels/focus behavior and the activity remains operable without relying solely on color, hover, or animation. |

## Runtime-audit evidence

`Shared/tools/gcdr_runtime_audit.py` provides an automated Audit-4 falsifier. It checks the
implementation locator, JavaScript syntax, control/handler integrity, identifier uniqueness,
placeholder/`undefined` leakage, deterministic reset, a DOM-lite JavaScript smoke runtime, and
a basic accessible-control-label baseline.

The runtime harness executes inline JavaScript under Node with minimal DOM semantics and mutates
controls to observe causal output/state changes. It is intentionally reported as
`STATIC_PLUS_DOM_LITE_JS_RUNTIME_NOT_VISUAL_BROWSER_PROOF`: passing it does not prove CSS/layout,
canvas geometry, animation timing, pointer hit targets, or full assistive-technology behavior.

Subject-owned property sweeps complement the generic runtime audit. For Motion in 2D,
`Physics/tools/motion2d_gcdr_properties.py` checks the numerical/model invariants used by the
six current explorers without moving projectile physics into shared GCDR governance.

### Per-check receipts and provenance

Every asserted `PASS` or `FAIL` must have a matching `audit_receipt`. A receipt records the
quality-check id, outcome, method (`AUTOMATED`, `HUMAN`, or `HYBRID`), evidence reference,
artifact SHA-256, timestamp, auditor, and a short note. `audit_provenance` summarizes how the
overall activity audit was produced.

A stale receipt whose outcome no longer matches the recorded check status fails the guard.

## State-fidelity contract

Every GCDR contract also carries `state_fidelity_contract`.

`external_state_mapping` declares whether external task injection is not applicable, requires
an exact mapping, permits a constraint-faithful mapping, or permits an explicitly disclosed
concept-only mapping.

The learner-facing fidelity vocabulary is fixed:

- `EXACT` — every governing parameter required by the representation came from the task/state being represented;
- `CONSTRAINT_FAITHFUL` — the task determines only part of the state; only those constraints are loaded and unspecified values remain explicitly unspecified/user-controlled;
- `CONCEPT_ONLY` — the activity demonstrates the relevant principle but does not claim to reproduce the task's full state;
- `UNAVAILABLE` — the task cannot be represented safely by the activity.

The mandatory missing-parameter policy is `NEVER_INVENT_AS_EXACT`.

### Parameter-level state bindings

When `external_state_mapping` is not `NOT_APPLICABLE`, the contract must declare
`external_state_bindings`. Each binding identifies:

- an external `source_pointer`;
- the governed `target_state_path`;
- the corresponding control id when one exists;
- whether the value is required for `EXACT`;
- source and target units;
- an explicit transform;
- and what happens when the source value is absent.

The exactness rule is fixed as `ALL_REQUIRED_BINDINGS_PRESENT`. The shared resolver
`Shared/tools/gcdr_state_binding.py` never fills a missing source with a convenient default.
It yields `EXACT` only when every required binding resolves, `CONSTRAINT_FAITHFUL` when only
a permitted subset resolves, `CONCEPT_ONLY` only under an explicitly concept-capable policy,
and otherwise `UNAVAILABLE`.

`CUSTOM_DECLARED` transforms require a subject-owned adapter; the shared resolver does not
silently execute arbitrary conversion logic.

Only `control_state_mapping`, `no_invented_exact_parameters`, and `interaction_fidelity_disclosed` may be `NOT_APPLICABLE`, and only when the activity declares `external_state_mapping=NOT_APPLICABLE`. A waiver for any other check is a guard failure; stale or unknown waiver keys also fail the guard.

## Certification rule

A GCDR activity may claim `CERTIFIED` only when:

1. every legacy `implementation_evidence` flag is true;
2. `quality_audit.audit_status` is `PASS`;
3. every quality check is `PASS` or justified `NOT_APPLICABLE`;
4. every asserted PASS/FAIL has matching digest-bound audit receipt evidence;
5. audit provenance and the audit date are recorded;
6. there are no unresolved quality-audit findings; and
7. the existing semantic-leaf, capability, sequence, runtime-honesty, and implementation-locator guards pass.

This certification is structural and implementation-audit conformance only. Human scientific
review, pedagogical review, empirical learner evidence, and learner-release authority remain
separate governed decisions.
