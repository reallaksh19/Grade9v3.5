# Graphical Cognitive Deconstruction Route (GCDR) — Blueprint v1.2

## Status

This is a **parallel support-route contract**, not a second curriculum taxonomy.

Canonical authority remains:

```text
capability → matrix rung → microtopic → teaching_path semantic leaf
                                      │
                                      ├─ normal route
                                      └─ GCDR activity
```

A GCDR activity must return evidence to the same semantic leaf/capability it supports.

## When to recommend the route

Recommend a GCDR when the concept itself is intrinsically difficult — counterintuitive, hidden-mechanism, relational, constraint-based, multi-representation, reference-frame/system-boundary sensitive — **or** when learner evidence shows very low knowledge, a persistent misconception, repeated failure, failure after normal repair, or failed reconstruction.

Do not auto-route from one wrong answer. Missing prerequisites divert to prerequisite recovery first.

## One explorer, one cognitive target

Every explorer declares:

- **target failure** — the learner model being replaced;
- **target operation** — the reasoning operation the learner must acquire;
- **core invariant** — what survives valid variation;
- **boundary** — where the invariant/shortcut stops applying.

Do not combine several hard concepts simply because they share a chapter.

## Mandatory cognitive sequence

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
Show what physically happens: objects, motion, contacts, geometry, trajectory, reference frame, or system boundary.

### G2 — Mechanism
Expose what is normally invisible: force/velocity components, relative motion, rope segments, event markers, constraints, interaction pairs, system boundaries, or causal dependencies.

### G3 — Mathematical structure
Convert the mechanism into signed quantities, equations, a derived relation, and the invariant.

## Coordinated representations

Use multiple views only when they perform different reasoning jobs. A typical ensemble is:

```text
physical scene
    ├─ vector/FBD view
    ├─ graph
    ├─ state table
    └─ equation
```

All views must share one underlying state. A view may not silently use a different time, frame, sign convention, or system boundary.

## Counterfactual requirement

Where useful, let the learner impose the tempting wrong model and observe the contradiction.

Examples:

- force `T = mg` and see that the predicted acceleration becomes zero;
- force `Δy = 0` and see that it solves a real but wrong event;
- remove ground friction and see that internal horse–cart forces cannot accelerate the combined centre of mass.

Feedback must answer both **why the correct model works** and **why the tempting model cannot**.

## Progressive disclosure

Learner mode should not expose the invariant, full derivation, all overlays, and diagnostic answer before prediction.

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

## 4-Audit Universal Quality Gate

The quality gate is now both a design checklist and a machine-bound audit record.

The authoritative checklist is
[`docs/GCDR-QUALITY-AUDIT-CHECKLIST.md`](GCDR-QUALITY-AUDIT-CHECKLIST.md), and every
`gcdr_contract` carries its current status under `quality_audit`.

### Audit 1 — Canonical Truth & Scope

Verify the semantic/capability binding, assumptions and conventions, equations/model claims,
units/constants/parameters, boundary cases, and source-claim fidelity.

No visual may be more authoritative than the canonical academic records.

### Audit 2 — Graphical Deconstruction & State Fidelity

Verify that one authoritative state drives every view; all representations stay synchronized;
manipulation changes real state rather than cosmetic labels; counterfactuals compute/render the
wrong model honestly; progressive disclosure is preserved; externally loaded controls map to
the variables that actually govern the model; and missing parameters are never invented and
presented as an exact task load.

External task mappings use only these learner-visible fidelity classes:

- `EXACT`;
- `CONSTRAINT_FAITHFUL`;
- `CONCEPT_ONLY`;
- `UNAVAILABLE`.

The mandatory policy is `NEVER_INVENT_AS_EXACT`. Any activity that accepts an external task must declare parameter-level source→state bindings. `EXACT` is permitted only when every binding marked required-for-exact resolves; partial mappings remain explicitly `CONSTRAINT_FAITHFUL` or lower.

**Fail Audit 2** if a paragraph + equation + decorative animation would provide essentially
the same learning experience, or if the activity can claim a successful load without proving
that the governing state changed.

### Audit 3 — Reconstruction, Teaching Support & Transfer

The implementation must provide a learner-facing or teacher/debug explanation layer that can
show the governing model, task-specific derivation, final result/disposition, an independent
check, the concrete misconception trap, the transferable takeaway, the boundary, and the
interaction-fidelity disclosure.

The learner must still demonstrate canonical reconstruction, representation transfer, boundary
recognition, scaffold fade, and fresh transfer without the explorer. A multiple-choice score
alone is insufficient exit evidence.

### Audit 4 — Runtime & Release Integrity

Before release, verify the implementation locator, executable/data syntax, handler/control
wiring, identifier integrity, absence of placeholder/`undefined` output, deterministic reset,
a supported-runtime smoke test, and an accessibility baseline.

A blocked runtime smoke test must remain visible as a limitation; static checks may not be
silently promoted to runtime proof. The shared DOM-lite runtime auditor may establish executable
control/reset evidence, but it explicitly does not claim visual-browser or assistive-technology
proof. Subject-owned numerical/property sweeps remain separate from the generic GCDR layer.

## Entry and exit contracts

Every GCDR activity is machine-bound through `resource.extensions.topic_atlas.gcdr_contract`.

The contract declares route triggers, cognitive target, interaction sequence, graphical mechanism, parameter-level state-fidelity bindings, boundary stress, exit evidence, implementation evidence, per-check audit receipts/provenance, and the quality-audit record.

Conformance states:

- `DESIGN_BOUND` — blueprint metadata exists;
- `IMPLEMENTATION_PARTIAL` — some required interaction behaviours exist, but not all;
- `CERTIFIED` — every implementation-evidence flag is true, the quality audit is `PASS`, no unresolved audit findings remain, and CI validates structural/referential integrity.

`CERTIFIED` does **not** imply human scientific or pedagogical approval; those remain separate review authorities.

## Minimum Definition of Done for certification

- prediction occurs before answer reveal;
- meaningful direct manipulation exists;
- at least two synchronized representations add distinct reasoning value;
- the wrong model produces an observable contradiction;
- a causal chain is explicit;
- mathematics is reconstructed from the visual mechanism;
- the learner discovers/tests an invariant;
- a boundary case breaks a shortcut;
- scaffolds fade;
- fresh transfer succeeds without the explorer;
- every quality-audit check is `PASS` or explicitly waived as `NOT_APPLICABLE` with rationale;
- every asserted audit result has digest-bound per-check receipt evidence, audit provenance is recorded, and no unresolved audit finding remains;
- runtime smoke and accessibility-baseline checks are recorded rather than assumed;
- the exit rejoins the same semantic leaf.

## Reference implementation lessons

The pulley explorer is a useful benchmark because it coordinates a physical rig, manipulable parameters, prediction, rope-geometry accounting, FBDs, dynamic/static comparison, and diagnostic checks. The reusable principle is not its exact layout; it is the sequence **predict → manipulate → reveal mechanism → reconstruct → stress boundary → verify transfer**.

The blueprint deliberately improves on reference-dashboard behaviour by preventing answer leakage before prediction and by requiring scaffold fade plus fresh transfer before certification.
