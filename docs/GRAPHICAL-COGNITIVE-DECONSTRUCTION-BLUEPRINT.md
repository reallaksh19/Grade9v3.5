# Graphical Cognitive Deconstruction Route (GCDR) — Blueprint v1.3

## Status

GCDR is a **parallel support-route contract**, not a second curriculum taxonomy.

Canonical authority remains:

```text
capability → matrix rung → microtopic → teaching_path semantic leaf
                                      │
                                      ├─ normal route
                                      └─ GCDR activity
```

A GCDR activity must return evidence to the same semantic leaf/capability it supports. Version
1.3 keeps the v1.2 cognitive route unchanged; it adds governance around scope, diagnostic items,
helper activation, representation equivalence, rendered geometry and delivery packaging.

## v1.3 contract layers

The architecture is deliberately split instead of expanding one explorer schema into a master
schema for every concern:

- `Shared/library/explorer_design_contract.schema.json` — one GCDR activity/explorer;
- `Shared/library/gcdr_diagnostic_item.schema.json` — one diagnostic item inside a suite;
- `Shared/library/gcdr_helper_contract.schema.json` — one helper activation/evidence contract;
- `Shared/library/gcdr_suite_contract.schema.json` — suite scope, corpus snapshot and delivery artifacts.

The governing path for a master suite is:

```text
Canonical Scope
      ↓
Diagnostic / External Task
      ↓
Source → State Binding
      ↓
GCDR Mechanism
      ↓
Representation Invariants
      ↓
Helpers / Reconstruction
      ↓
Fresh Transfer
      ↓
Audit Evidence
```

The explorer schema remains focused on the activity itself. Question-bank and suite-scale
governance live in companion contracts and are enforced by
`Shared/tools/gcdr_suite_guard.py`.

## When to recommend the route

Recommend a GCDR when the concept itself is intrinsically difficult — counterintuitive,
hidden-mechanism, relational, constraint-based, multi-representation, reference-frame or
system-boundary sensitive — **or** when learner evidence shows very low knowledge, a persistent
misconception, repeated failure, failure after normal repair, or failed reconstruction.

Do not auto-route from one wrong answer. Missing prerequisites divert to prerequisite recovery
first.

## One explorer, one cognitive target

Every explorer declares:

- **target failure** — the learner model being replaced;
- **target operation** — the reasoning operation the learner must acquire;
- **core invariant** — what survives valid variation;
- **boundary** — where the invariant/shortcut stops applying.

Do not combine several hard concepts simply because they share a chapter.

## Mandatory cognitive sequence

Version 1.3 does **not** change the route:

```text
CONTEXT
  ↓
PREDICT
  ↓
MANIPULATE
  ↓
OBSERVE
  ↓
CONTRADICT
  ↓
GRAPHICAL DECONSTRUCTION
  ↓
MATHEMATICAL RECONSTRUCTION
  ↓
INVARIANT DISCOVERY
  ↓
BOUNDARY STRESS
  ↓
SCAFFOLD FADE
  ↓
FRESH TRANSFER
```

The final equation is a compression of the visible mechanism, not the opening move.

## Three graphical depths

### G1 — Phenomenon

Show what physically happens: objects, motion, contacts, geometry, trajectory, reference frame,
or system boundary.

### G2 — Mechanism

Expose what is normally invisible: force/velocity components, relative motion, rope segments,
event markers, constraints, interaction pairs, system boundaries, or causal dependencies.

### G3 — Mathematical structure

Convert the mechanism into signed quantities, equations, a derived relation, and the invariant.

## Coordinated representations and representation invariants

Use multiple views only when they perform different reasoning jobs. A typical ensemble is:

```text
physical scene
    ├─ vector/FBD view
    ├─ graph
    ├─ state table
    └─ equation
```

All views must share one underlying state. A view may not silently use a different time, frame,
sign convention, unit system or system boundary.

Synchronization is necessary but no longer sufficient. A v1.3 explorer also declares
`representation_invariants`: relations that must remain true when the same mathematical object
is shown in more than one form. Examples include:

- physical trajectory point = graph/state at the same clock;
- distance odometer = `∫|v|dt`;
- displacement readout = `∫vdt`;
- projection + rejection = original vector;
- rejection is orthogonal to the projection axis;
- parallelogram area from sides = area from diagonals;
- BAC–CAB algebra = the rendered vector-triple-product result.

Representation invariants require an analytic oracle, property test or explicit state assertion.
A visually plausible second representation is not evidence of equivalence.

## Rendered-geometry truth

Canvas/SVG execution can be syntactically correct while the geometry is mathematically wrong.
The v1.3 `geometry_truth_contract` therefore names the governed geometry and the independent
oracle method.

The check is semantic, not pixel matching:

> geometric positions, vectors, planes, graph curves, event markers and derived shapes must be
> independently checked against the governed mathematical state.

Subject-owned property tests are preferred when the invariant is domain-specific.

## Counterfactual requirement

Where useful, let the learner impose the tempting wrong model and observe the contradiction.

Examples:

- force `T = mg` and see that the predicted acceleration becomes zero;
- force `Δy = 0` and see that it solves a real but wrong event;
- remove ground friction and see that internal horse–cart forces cannot accelerate the combined
  centre of mass.

Feedback must answer both **why the correct model works** and **why the tempting model cannot**.

## Progressive disclosure

Learner mode should not expose the invariant, full derivation, all overlays, and diagnostic
answer before prediction.

Preferred reveal order:

```text
physical scene → prediction → relevant overlay → causal relation
→ equation → invariant → boundary
```

A teacher/debug mode may expose all layers simultaneously.

## Scaffold fading

Full graphical success is not mastery.

```text
full labels/values/hints
  ↓
partial labels
  ↓
learner supplies signs/relations
  ↓
physical scene only
  ↓
fresh task without explorer
```

## Diagnostic-item contract

A large master suite is not considered governed merely because its outer explorer is governed.
Every diagnostic item is normalized against
`Shared/library/gcdr_diagnostic_item.schema.json`.

The item contract separates four concerns:

1. **source provenance** — provider, source label, verification status and snapshot date;
2. **answer contract** — final answer, item-specific derivation, independent check and audit evidence;
3. **teaching contract** — trap, transfer rule, Chalkboard check and declared helpers;
4. **simulation contract** — fidelity, target activity, active binding references and fidelity note.

Generic/filler final answers such as “apply formula”, “evaluate” or “use the equation” are
release-blocking findings. `EXACT` and `CONSTRAINT_FAITHFUL` diagnostic mappings require
explicit active binding references; `CONCEPT_ONLY` and `UNAVAILABLE` carry none.

Answer audit and source audit are separate axes. A mathematically correct item is not thereby
source-verified.

## Helper activation contract

The helper registry is vocabulary, not implementation evidence. A helper activation uses
`Shared/library/gcdr_helper_contract.schema.json` and progresses through:

```text
DECLARED → IMPLEMENTED → AUDITED
```

- `DECLARED` — intended by design;
- `IMPLEMENTED` — consumes governed activity/item content or state and produces its required outputs;
- `AUDITED` — implementation evidence exists for those outputs.

Activation modes distinguish `STATE_DRIVEN`, `ITEM_DRIVEN`, and `STATIC_REFERENCE`.
A static reference may be declared, but it cannot be promoted to implemented/audited helper
evidence.

Only `AUDITED` helpers count toward suite audit claims that helper activation has been checked.

## Canonical scope and instructional depth

Good advanced material must not be discarded merely because it exceeds the current canonical
spine, but it also must not inherit canonical authority accidentally.

The v1.3 `scope_contract` declares:

- `BOUND` — fully bound to the declared canonical capability refs;
- `PARTIAL` — a suite/activity mixes canonical and extension material;
- `UNBOUND_EXTENSION` — useful extension material with no current canonical binding.

Instructional depth is one of `FOUNDATION`, `SCHOOL_CORE`, `ADVANCED`, or
`JEE_EXTENSION`. Certification scope must state what is and is not eligible for canonical
GCDR certification.

## External corpus snapshot provenance

External corpus size is snapshot metadata, not a marketing constant. Suite contracts record:

- provider and topic;
- snapshot date;
- observed live count;
- embedded diagnostic count;
- coverage claim:
  - `FULL_CORPUS_AUDITED`;
  - `CURATED_SLICE_AUDITED`;
  - `DEMAND_RECONNAISSANCE_ONLY`.

A local 18-item or 13-item bank therefore cannot be described as a full 123-item or 282-item
audit merely because the source corpus contains that many questions.

## Delivery profiles

Release artifacts declare one of:

- `REPO_BUNDLE` — repository-local dependencies may remain separate;
- `SINGLE_FILE_ONLINE` — repository-local dependencies are embedded, remote CDN dependencies are declared;
- `SINGLE_FILE_OFFLINE` — one file with no remote runtime dependency.

The declared profile is testable. A single-file artifact with an external local JS data file is
not single-file. A CDN-dependent file is not offline.

## 4-Audit Universal Quality Gate

The authoritative checklist is
[`docs/GCDR-QUALITY-AUDIT-CHECKLIST.md`](GCDR-QUALITY-AUDIT-CHECKLIST.md). Every explorer
`gcdr_contract` carries its current status under `quality_audit`; suite/item/helper contracts
are checked by their companion guard.

### Audit 1 — Canonical Truth, Source & Scope

Verify semantic/capability binding, assumptions and conventions, equations/model claims,
units/constants/parameters, boundary cases, source-claim fidelity, corpus snapshot provenance,
and instructional depth/scope.

No visual or external corpus claim may be more authoritative than the canonical academic record
or the recorded source snapshot.

### Audit 2 — State, Representation & Geometry Fidelity

Verify one authoritative state, synchronization, causal manipulation, honest counterfactuals,
progressive disclosure, source→state mappings, no invented exact parameters, disclosed fidelity,
representation equivalence, and rendered-geometry truth.

External task mappings use only:

- `EXACT`;
- `CONSTRAINT_FAITHFUL`;
- `CONCEPT_ONLY`;
- `UNAVAILABLE`.

The mandatory missing-parameter policy remains `NEVER_INVENT_AS_EXACT`.

**Fail Audit 2** if a paragraph + equation + decorative animation would provide essentially the
same learning experience, if the activity can claim a successful load without proving the
governing state changed, or if two mathematically equivalent views disagree.

### Audit 3 — Reconstruction, Helpers & Transfer

The implementation must provide a learner-facing or teacher/debug explanation layer that can
show the governing model, task-specific derivation, final result/disposition, an independent
check, the concrete misconception trap, the transferable takeaway, the boundary, and the
interaction-fidelity disclosure.

Helper presence does not pass this audit. Required helpers must be activated against governed
state/item content and carry the declared implementation/audit state.

The learner must still demonstrate canonical reconstruction, representation transfer, boundary
recognition, scaffold fade, and fresh transfer without the explorer.

### Audit 4 — Runtime, Packaging & Release Integrity

Before release, verify the implementation locator, executable/data syntax, handler/control
wiring, identifier integrity, absence of placeholder/undefined output, deterministic reset, a
supported-runtime smoke test, an accessibility baseline, and conformance to the declared
delivery profile.

A blocked browser/visual test must remain visible as a limitation. DOM-lite runtime success is
not visual-browser or assistive-technology proof.

## Entry, exit and conformance

Every GCDR activity remains machine-bound through
`resource.extensions.topic_atlas.gcdr_contract`.

Conformance states remain:

- `DESIGN_BOUND` — blueprint metadata exists;
- `IMPLEMENTATION_PARTIAL` — some required interaction behaviours exist, but not all;
- `CERTIFIED` — every implementation-evidence flag is true, the quality audit is `PASS`,
  no unresolved audit findings remain, and CI validates structural/referential integrity.

`CERTIFIED` does **not** imply human scientific or pedagogical approval.

## Minimum Definition of Done for certification

- prediction occurs before answer reveal;
- meaningful direct manipulation exists;
- at least two synchronized representations add distinct reasoning value;
- declared representation invariants pass independent checks;
- rendered geometry is checked against governed mathematical state;
- the wrong model produces an observable contradiction;
- a causal chain is explicit;
- mathematics is reconstructed from the visual mechanism;
- the learner discovers/tests an invariant;
- a boundary case breaks a shortcut;
- required helpers are implemented and audited rather than merely named;
- scaffolds fade;
- fresh transfer succeeds without the explorer;
- canonical scope/depth is explicit;
- external corpus claims are snapshot-bound where applicable;
- the released artifact satisfies its declared delivery profile;
- every quality-audit check is `PASS` or explicitly allowed `NOT_APPLICABLE` with rationale;
- every asserted result has digest-bound per-check receipt evidence;
- runtime smoke and accessibility-baseline checks are recorded rather than assumed;
- the exit rejoins the same semantic leaf.

## Reference implementation lessons

The pulley explorer remains a useful benchmark because it coordinates a physical rig,
manipulable parameters, prediction, rope-geometry accounting, FBDs, dynamic/static comparison,
and diagnostic checks.

The Motion-1D and Vector Algebra audits add four durable lessons: item-level answer/source
governance, helper activation evidence, equivalence checks across alternate representations, and
geometry/packaging truth that cannot be inferred from DOM/handler health alone.

The reusable cognitive principle remains:
**predict → manipulate → reveal mechanism → reconstruct → stress boundary → verify transfer**.
