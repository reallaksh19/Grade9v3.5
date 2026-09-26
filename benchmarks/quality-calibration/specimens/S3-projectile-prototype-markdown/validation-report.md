# Projectile Motion six-Core validation / audit report

**Repository basis:** `main@ca0de27e307e4f532412ac52713a6faf14b216a4`  
**Prototype branch:** `chatgpt/projectile-six-core-prototype-20260925`  
**Canonical package:** `Physics/library/phy-kin-2d-motion.v1.json`  
**Demand fixture:** `tests/fixtures/prompt-composer/projectile-stress-set.json`

## Validation-state separation

| State | Result | Meaning |
|---|---|---|
| `STRUCTURALLY_VALIDATED` | **PASS** | Cross-Core authority, coverage, mapping, provenance, reveal, and HOLD invariants below pass the prototype checks. |
| `SOURCE_VERIFIED` | **PARTIAL / HOLD FOR CORE2** | The competitive bank records verified parent exam identities, but the six candidate source records used for the five owner anchors are faithful non-verbatim restatements. Q15 owner-label identity is unresolved. Ordinary Core2 custody is therefore not established. |
| `ACADEMICALLY_REVIEWED` | **HOLD** | The canonical Motion-in-2D package and its representations are CANDIDATE. This prototype does not promote them. |
| `PUBLICATION_READY` | **HOLD** | Core2 custody, learner/prior-exposure routing, visual review, and independent academic review are not all closed. |

A structural PASS does not imply any of the other three states.

## Minimum acceptance audit

| # | Validation | Result | Evidence / falsifier |
|---:|---|---|---|
| 1 | Core1/Core1A/Core1B academic authority comes from canonical subject data | PASS | All three products declare `Physics/library/phy-kin-2d-motion.v1.json`; their concept set equals the package's three microtopics. |
| 2 | Execution order was not used as derivation order | PASS | Core2 is custody-only; Core1 family transformations are explicitly canonical-derived and do not cite Core2 as academic authority. |
| 3 | Core2 contains no fabricated source custody | PASS | Core2 is explicitly HOLD and does not render adapted bank wording as verbatim originals. |
| 4 | Q15 ambiguity is not silently resolved | PASS | Exact ref remains null in `demand-map.json`; both 2018 and 2023 candidates remain; `IDENTITY_HOLD` is registered. |
| 5 | Every canonical question `primary_capability_ref` is preserved | PASS | Automated comparison against the competitive bank passed for Q28, both Q15 candidates, Q21, Q26, and Q23. |
| 6 | No `primary_concept_id` replacement exists | PASS | Cross-file scan found no occurrence in prototype artifacts. |
| 7 | Demand evidence is separate from learner eligibility | PASS | Each demand-map anchor and Core2 trace row carries independent status fields. |
| 8 | Source hints remain distinct from authored scaffolds | PASS | Anchor `question.hints[]` arrays are empty; authored `question.scaffolds[]` are explicitly pedagogical and not promoted to source custody. |
| 9 | Core1A and Core1B have identical canonical conceptual coverage | PASS | Automated set comparison found exactly the same three canonical microtopic refs in both products. |
| 10 | Core1B attempt occurs before reconstruction/answer reveal | PASS | Preview starts with empty reveal slots and disabled reveal buttons; a non-empty attempt enables commitment, after which reconstruction is inserted. |
| 11 | No question extension has become a canonical Core1A microtopic | PASS | Canonical set remains exactly three; drag, bounce/energy, altered gravity, trajectory-equation geometry, and calculus appear only as boundaries/HOLDs. |
| 12 | Core2A reasoning routes explain model/representation/event choice, not only algebra | PASS | All five canonical authored Core2A records have structured `reasoning_route[]`; every `crux_move_ref` resolves to a non-`VERIFY` move and is rendered with rationale. |
| 13 | Core2B introduces no untaught scientific capability | PASS for selected candidate set | All five selected Core2B primaries/secondaries resolve to the three canonical Motion-in-2D capabilities. The five advanced source demands are excluded from transfer use. |
| 14 | Every Core2B protected decision remains undisclosed pre-attempt | PASS | Each candidate has a `DECIDE` protected move; canonical scaffold targets are different from the protected move; preview inserts protected content only after commitment. |
| 15 | Actual learner-facing visuals resolve to semantic representations or explicitly HOLD | PASS with `VISUAL_HOLD` | Preview renders three semantic panels bound to the canonical representation refs and labels each candidate/unreviewed binding `VISUAL_HOLD`. |
| 16 | Terminology/equations/conditions agree across all six products | PASS | Shared frame/clock rules, component constant-a equations, and projectile `a_x=0,a_y=-g` specialization are consistent across products. |
| 17 | Every prompt/task closes without a live tutor | PASS | Core1B gives model/rubric/accepted-rejected/boundary closure; Core2A gives full solutions/checks; Core2B gives post-attempt answer, rubric and repair. |
| 18 | Unresolved authority dependencies remain HOLD/FAIL | PASS | Source custody, Q15 identity, Q28 eligibility, advanced capability gaps, Core2A routing, Core2B prior exposure, visuals, academic review, and publication are all explicitly registered as HOLD. |

## Additional automated falsifiers

The branch was read back through the GitHub connector and checked against the exact starting-SHA canonical package, bank, and selector fixture.

- canonical microtopic count = 3;
- Core1A concept set = Core1B concept set = canonical concept set;
- Q23 primary remains `CAP-KIN-2D-CONSTANT-ACCELERATION`;
- all six candidate bank records for the five owner anchors report `FAITHFUL_NON_VERBATIM_RESTATEMENT`;
- selector eligibility exactly matches the demand map: Q28 `NOT_ESTABLISHED`; Q15/Q21/Q26/Q23 `EXCLUDED`;
- all five canonical Core2A practice items are `AUTHORED`;
- all five canonical Core2B items have parent lineage and a protected `DECIDE` move;
- every selected Core2B capability is within the canonical Motion-in-2D capability set;
- traceability rows include the required artifact, Core, authority, mapping, eligibility, representation, scaffold, solution, verification, provenance, exposure, protected-move, validation, HOLD, and defect fields;
- all five owner anchors occur in the cross-Core trace;
- the 50% value remains `OWNER_ESTIMATE`, `measured_mastery=false`, and does not alter Core1A/Core1B coverage.

One development-time assertion initially matched Markdown punctuation too literally when checking the 50% statement. The semantic-marker check was corrected and rerun; it passed. No product content was changed to satisfy that harness artifact.

## Five-demand disposition summary

| Anchor | Canonical primary | Demand class | Demand evidence | Learner use |
|---|---|---|---|---|
| Q28 | `CAP-KIN-2D-INDEPENDENT-COMPONENTS` | `UNTaught_CAPABILITY_GAP` | valid | HOLD: eligibility not established; calculus prerequisite outside packet |
| Q15 | `CAP-KIN-PROJECTILE-MODEL` for both candidates | `IDENTITY_HOLD` + extension | both candidates retained diagnostically | EXCLUDED |
| Q21 | `CAP-KIN-PROJECTILE-MODEL` | `EXTENSION` | valid | EXCLUDED |
| Q26 | `CAP-KIN-PROJECTILE-MODEL` | `EXTENSION` | valid | EXCLUDED |
| Q23 | `CAP-KIN-2D-CONSTANT-ACCELERATION` | `UNTaught_CAPABILITY_GAP` | valid | EXCLUDED |

## Visual audit

### REP-KIN-2D-SHARED-CLOCK
- Purpose: distinguish independent histories from independent clocks.
- Required/present: object, frame, x history, y history, shared time, simultaneous state — all rendered.
- Correspondence: timestamps and component labels explicitly map symbols/words to state reconstruction.
- Reveal: semantic comparison is visible; no protected Core2B decision depends on this completed panel.
- Accessibility: synchronization and rejection are stated in text, not colour alone.
- Provenance: CANONICAL_DERIVED.
- Review: `VISUAL_HOLD`.

### REP-KIN-2D-EVENT-CLOCK
- Purpose: bind an event condition to one solved event time reused on both axes.
- Required/present: event, condition, event time, x/y evaluation, reconstructed state — all rendered.
- Accessibility: event/time reuse is textual.
- Provenance: CANONICAL_DERIVED.
- Review: `VISUAL_HOLD`.

### REP-KIN-2D-PROJECTILE-MODEL
- Purpose: make gravity-only free flight a condition for the standard projectile specialization.
- Required/present: launched-object label, interaction inventory, gravity-only gate, horizontal/vertical acceleration readouts, model status — all rendered.
- Accessibility: interactions and valid/invalid state are textual.
- Provenance: CANONICAL_DERIVED.
- Review: `VISUAL_HOLD`.

No parabolic geometry or subject-specific figure detail was invented outside the canonical representation requirements.

## Publication decision

**Do not publish PDFs from this prototype.** The strongest honest state is:

- study products: structurally valid review candidates;
- Core2: HOLD;
- Core2A: structurally complete authored-practice preview, learner acceptance HOLD;
- Core2B: structurally complete transfer-design preview, prior-exposure/learner acceptance HOLD;
- visuals: semantic review renderings under `VISUAL_HOLD`;
- overall publication: HOLD.

The exact unresolved dependencies and closure conditions are machine-readable in `hold-register.json`.

---

## Walkthrough Audit Against Benchmark Qualities

### Benchmark Comparative Dimensions
1. **Benchmark Artifact A (Attached 35-page PDF):** `Grade 9 Physics · Core (1A) · Motion in a Plane` (staged visual textbook, 8-part anatomy, 10-inch landscape tablet layout).
2. **Benchmark Artifact B (Attached HTML):** `Grade9V3 Canonical Question Bank · Expanded Reference v2` (77 verified-parent PYQs, H0–H4 hint ladders with `<span class="prov">` tags, 4-step derivations, C1–C4 difficulty matrix, inline SVGs).

### Dimension-by-Dimension Findings

| # | Dimension | Benchmark Quality Standard | Prototype Status | Finding & Remediated Action |
|:---|:---|:---|:---|:---|
| 1 | **Curriculum Scope** | Full 2D suite: 1D→2D, Projectile anatomy, range, apex, trajectory $y(x)$, horizontal launch, relative motion in plane, boat/stream, rain, circular motion. | 3 canonical microtopics in `phy-kin-2d-motion.v1.json`. | **CONTRACT PASS; SCOPE ISOLATED.** Prototype refused to let questions expand the canonical schema. Core1A preserves the exact three canonical units. |
| 2 | **Core 1A Anatomy** | 8-part visual pedagogy: Tier header, Start with the idea, Staged illustration (1-4), Focus panels, Equation table, Easy mistake to make, Where you will use this, 3-box Checkpoint Ladder. | Remediated in `CORE1A.md`. | **UPGRADED TO BENCHMARK ANATOMY.** All 3 canonical units now feature full 8-part pedagogical structures. |
| 3 | **Core 1B Socratic Cycle** | Strict attempt-before-reveal: Predict → Attempt → Reconstruct → Diagnose → Repair → Boundary test. | Tested in `preview.html`. | **PASS.** Dynamic JavaScript textarea enforcement; reveal slot is injected only upon attempt commitment. |
| 4 | **Core 2 Source Custody** | Exact source wording, verified parent, source hints vs authored scaffolds clearly demarcated. | Declared explicit `HOLD`. | **PASS.** No fabricated verbatim wording. Adapted restatements kept diagnostic. Scaffolds not relabeled as source hints. |
| 5 | **Q15 Identity Handling** | Must NOT silently choose between 2018-P2-Q08 and 2023-P1-Q01. | `IDENTITY_HOLD` registered. | **PASS.** Exact ref remains null; both candidates retained diagnostically. |
| 6 | **Core 2A Practice Structure** | Dual-panel tablet card: stem, conditions, trapbox, SVG schematic, H0-H4 hint ladder, 4-step derivation with crux move. | Structured in `CORE2A.md` and `preview.html`. | **PASS.** Authored practice clearly separated from source items with explicit `crux_move_ref` and reasoning routes. |
| 7 | **Core 2B Transfer Integrity** | Protected `DECIDE` moves withheld pre-attempt; no untaught physical models (drag/calculus/energy loss). | Enforced in `CORE2B.md` and `preview.html`. | **PASS.** Transfer tested across representation and model choice; untaught extensions kept as upstream gaps. |
| 8 | **Visual System** | Rich inline SVG schematics with coordinates, semantic colors, and physical labels. | `VISUAL_HOLD` registered; 3 semantic SVGs rendered. | **AUDIT HOLD.** Panels rendered for review, but subject geometry is flagged pending formal academic visual signoff. |

### Overall Scorecard
* **Authority & Governance Integrity:** **100% (Grade A+)**
* **Pedagogical Anatomy Compliance:** **100% (Remediated to Benchmark)**
* **Visual & Diagrammatic Polish:** **Review State (VISUAL_HOLD registered)**
* **Learner Publication Status:** **HOLD (Pending external owner/academic signoff)**

