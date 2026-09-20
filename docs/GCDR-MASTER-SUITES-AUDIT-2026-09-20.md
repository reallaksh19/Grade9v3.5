# GCDR audit — Motion in One Dimension and 3D Vector Algebra master suites

Date: 2026-09-20

Scope:

- `public/physics/motion-1d/explorers/motion_in_1d/`
- `public/mathematics/vectors/explorers/vector_algebra/`
- 18 local Motion diagnostics
- 13 local Vector diagnostics
- page simulators, question loaders, answers/derivations, helper use, source-count claims and concept coverage

This audit treats the suites as candidate GCDR implementations. It does not promote either
suite to `CERTIFIED` merely because the UI exists.

## Source-corpus reconciliation

The current live ExamSIDE chapter pages observed on 2026-09-20 report:

| Suite | Live corpus | Local diagnostics in suite | Previous page claim | Audit disposition |
| --- | ---: | ---: | ---: | --- |
| Motion in a Straight Line | 123 questions, 2002–2026 | 18 | 124 | corrected |
| Mathematics Vector Algebra | 282 questions, 2002–2026 | 13 | 283 | corrected |

The local 18/13 diagnostics are a curated diagnostic slice. They are not a local copy of the
full external corpus.

## Answer audit

All 31 local diagnostic answers were independently recomputed in
`tests/test_master_suites_gcdr_audit.py`.

Critical defects repaired:

1. `1D-Q01` — the authored derivation computed +400 m forward and -100 m backward but then
   changed the displacement to 200 m without justification. Correct values are distance
   500 m, displacement +300 m, average velocity +7.5 m/s.
2. `1D-Q11` — final 4.20 m result was correct but the drop-clock algebra line was malformed.
   It is now `5 = 125 Δt²`, giving `Δt = 0.20 s`.
3. `VEC-Q09` — the previous vectors belonged to a different JEE question and the determinant
   was algebraically changed mid-solution. The record is replaced by a real symmetric
   coplanarity question with determinant `(μ-1)²(μ+2)=0`.
4. `VEC-Q11` — the derivation itself reached `|r|²=44/9` but then called `|3r|²=45`
   by “rounding”. Correct answer is exactly 44.

Every record now has `answerAudit=PASS`. Source-item verification is tracked separately;
records not individually source-verified remain explicitly `SOURCE_PROVENANCE_PENDING`.

## Question → simulator fidelity audit

The old universal “Load in Simulator” contract was rejected. Active parameter bindings are now explicit per item through `simBindingRefs`; an EXACT or CONSTRAINT_FAITHFUL mapping must name only parameters that the governed loader actually consumes.

A load action now uses one of:

- `EXACT` — every governing state required by the represented problem is actually bound;
- `CONSTRAINT_FAITHFUL` — the mapped constraints are genuine, but the rig does not claim a
  complete reproduction;
- `CONCEPT_ONLY` — opens a relevant mechanism and injects no question-specific defaults;
- `UNAVAILABLE` — no simulator state is changed.

### Motion diagnostics

| Fidelity | Questions |
| --- | --- |
| EXACT | Q06, Q07, Q10, Q11, Q12, Q16 |
| CONSTRAINT_FAITHFUL | Q02 |
| CONCEPT_ONLY | Q01, Q03, Q05, Q13, Q18 |
| UNAVAILABLE | Q04, Q08, Q09, Q14, Q15, Q17 |

### Vector diagnostics

| Fidelity | Questions |
| --- | --- |
| EXACT | Q02 |
| CONSTRAINT_FAITHFUL | Q05, Q12 |
| CONCEPT_ONLY | Q01, Q03, Q04, Q06, Q07, Q08, Q09, Q10, Q11 |
| UNAVAILABLE | Q13 |

A concept-only or unavailable record may no longer silently load convenient values and present
them as the source question state.

## Simulator RCA

### Motion v-x → a-x engine

The original implementation only computed `dv/dx` and `a(x)` for the linear profile.
Selecting either alternative profile left derived acceleration at zero.

Repaired model set:

- linear: `v=v0(1-x/x0)`, so `a=v dv/dx` is a positive-slope linear function;
- constant-acceleration stop: `v²=v0²(1-x/x0)`, so
  `a=-v0²/(2x0)`;
- elliptical quarter-circle: `v²/v0²+x²/x0²=1`, so
  `a=-v0² x/x0²`.

The endpoint is evaluated through the finite acceleration relation even when `dv/dx` becomes
singular.

### Vector area rig

The previous “diagonals” toggle computed the side-vector cross-product magnitude and then
halved it, changing the physical parallelogram area. It now draws the actual diagonals,
uses `|d1×d2|=2|a×b|`, and preserves one physical area in both representations.

### Scalar triple-product renderer

The top vertex previously used `c_z` in its y-coordinate. It now uses the correct
`c_y`, restoring parallelepiped closure.

### Vector triple-product rig

The previous rig drew one hard-coded result vector and only one span plane. It now computes
both parenthesizations from the displayed vectors:

- `a×(b×c)`;
- `(a×b)×c`;

and renders the `span(b,c)` and `span(a,b)` planes separately.

The explanatory statement was also weakened from the false universal claim that the two results
“reside in entirely different spatial planes” to the correct statement that they obey different
span constraints and are generally unequal; special choices may coincide.

### Vector-equation rig

The previous fixed `r_p=[0,2,-1]` was labelled perpendicular to `a=[2,1,1]`, although
`r_p·a=1`.

The repaired illustrative state is:

- `a=[2,1,1]`;
- `b=[2,-2,-2]`;
- `r_p=(a×b)/|a|²=[0,1,-1]`;
- solution line `r=r_p+λa`;
- auxiliary plane `r·[1,1,0]=4`, whose unique intersection is `λ=1`.

The UI now reports both the cross-equation residual and auxiliary-plane residual.

## Helper utilization

The shared inventory is committed at `docs/gcdr-master-suite-helper-registry.json`.

Every diagnostic card now actively uses:

- Teacher's Chalkboard / independent check;
- Trap Alert;
- Transfer Takeaway;
- Exactness/Fidelity badge;
- answer/source audit state.

The registry also records the reusable prediction, wrong-model, invariant, boundary, state,
representation-linking, reset, accessibility and domain-specific helper vocabulary.

Presence in the registry alone does not count as implementation. A helper is only implemented
when it consumes governed state and performs its declared job.

## Concept-coverage and canonical-binding findings

### Motion in One Dimension

The suite directly covers the high-value deconstruction set:

- distance versus displacement;
- moving-platform velocity inheritance;
- `v-x → a-x` calculus;
- equal-interval falling-drop clocks;
- piecewise state continuity;
- signed one-dimensional relative pursuit.

However, the current Grade9V3 Motion-1D canonical spine explicitly keeps general calculus and
velocity-dependent drag outside ordinary Grade-9 depth. The advanced calculus/drag diagnostics
therefore remain JEE-depth extensions until a governed advanced capability is authored.

### Mathematics Vector Algebra

The page now gives usable visual mechanisms for basis/direction cosine, projection/rejection,
cross-product area, scalar triple product, VTP non-associativity and vector-equation solution
families.

The repository currently has no canonical Mathematics Vector Algebra capability spine covering
general dot product, cross product, STP, VTP and vector equations. The existing Physics vector
slice is deliberately narrower.

Therefore this master suite must remain an implementation/audit candidate rather than being
declared GCDR `CERTIFIED` against invented canonical bindings.

The skew-line shortest-distance diagnostic also has no current simulator rig and is explicitly
`UNAVAILABLE`.

## Release status

- Answer audit: **31/31 recomputed**
- Known answer defects: **repaired**
- Question-loader exactness: **fail-closed classifications added**
- Helper layer: **activated at diagnostic-card level**
- Simulator mathematical defects identified above: **repaired**
- Full external source-item provenance: **partial; explicitly tracked**
- Canonical GCDR binding: **partial / blocked for advanced Motion calculus and broad Mathematics
  Vector Algebra**
- Draft sandboxes: remain **Draft**
- GCDR certification: **not claimed**

The correct next governance step is to bind only the already-canonical Motion concepts, then
author/review a separate advanced capability spine before attempting certification of the
calculus/drag and full Mathematics Vector Algebra portions.


## Governance response — GCDR v1.3

The defects found in these two suites are now reflected in the architecture rather than being
left as page-specific lessons.

GCDR v1.3 keeps the existing cognitive route unchanged and adds four boundaries around it:

1. **Explorer contract** — canonical scope, representation invariants, rendered-geometry truth,
   state fidelity and delivery profile.
2. **Diagnostic-item contract** — source provenance, answer/derivation evidence, item-specific
   teaching support and simulator fidelity for every bank item.
3. **Helper activation contract** — registry presence is separated from
   `DECLARED → IMPLEMENTED → AUDITED` activation evidence.
4. **Suite contract** — corpus snapshot, coverage claim, diagnostic source and release artifacts
   are governed as a coherent package.

The corresponding schemas are:

- `Shared/library/explorer_design_contract.schema.json` v1.3;
- `Shared/library/gcdr_diagnostic_item.schema.json`;
- `Shared/library/gcdr_helper_contract.schema.json`;
- `Shared/library/gcdr_suite_contract.schema.json`.

`Shared/tools/gcdr_suite_guard.py` now enforces the Motion-1D and Vector Algebra suite
contracts. It normalizes all 31 local question records through the diagnostic-item schema,
rejects generic/filler final answers, verifies helper contracts, checks corpus embedded counts,
checks declared remote dependencies, and verifies that standalone builds embed the same question
bank as the canonical suite source.

The suite declarations intentionally preserve the audit limitations found above:

- Motion-1D is `PARTIAL` canonical binding at `JEE_EXTENSION` depth;
- Vector Algebra is `UNBOUND_EXTENSION` at `JEE_EXTENSION` depth;
- both external corpora are `CURATED_SLICE_AUDITED`, not full-corpus audits;
- both standalone artifacts are `SINGLE_FILE_ONLINE`, not offline bundles.

This converts the audit's wording corrections into release-testable contracts.
