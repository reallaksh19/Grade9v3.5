# Learner Product Audit & Promotion Protocol (LPAP-v1)

Status: **PROPOSED**  
Date: 2026-10-01  
Scope: learner-facing Core products and interactive learning webpages entering Grade9V3 from an existing draft PR, an uploaded artifact, or a TEST-page intake.

Protocol machine identity:

- `protocol_id: LPAP`
- `protocol_revision: 1`
- `protocol_spec: LPAP-v1`
- `protocol_digest`: SHA-256 of the exact normative specification bytes used by an audit run.

Stable profile identities for this revision are:

- `LPAP.COMMON@1`
- `LPAP.CORE2@1`
- `LPAP.CORE1A@1`
- `LPAP.INTERACTIVE@1`
- `LPAP.CORE1@1`
- `LPAP.CORE1B@1`
- `LPAP.CORE2A@1`
- `LPAP.CORE2B@1`

Content/runtime modules and automated rules MUST likewise use stable machine IDs with explicit revisions, for example `LPAP.C2.HINT.PROVENANCE@1`. A future semantic change to a rule MUST change its revision or digest rather than silently reusing evidence produced under different logic.

## 1. Purpose

LPAP-v1 defines how a candidate learner product is independently audited, reconciled with repository authority, corrected, integrated into learner navigation, and presented for Owner acceptance.

It is intentionally not a second authoring method, curriculum store, renderer, Question Bank, publication store, or approval system.

Existing authority remains:

- Relay V3.1 records and reconstructs engineering work.
- `docs/method/PROTOCOL.md` governs one unit's authoring/review method.
- canonical subject/library records remain academic data authority;
- `Shared/tools/render_core.py` remains the governed Core renderer where applicable;
- `Shared/tools/accept_product.py` remains the publication entry point for governed rendered products;
- the Owner alone accepts or rejects one exact rendered digest.

LPAP adds one missing layer: a common path for independently auditing externally produced or draft learner artifacts before they are promoted into the main learner experience.

## 2. Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

A machine PASS proves only the property that the machine actually checked. It MUST NOT be described as independent academic review.

A reviewer recommendation, severity label, or automated result MUST NOT grant publication authority. The Owner decides publication on an exact version.

## 3. Governing model

Every candidate is audited through:

```text
COMMON AUDIT KERNEL
+ PRODUCT ROLE PROFILE
+ CONTENT/RUNTIME MODULES
+ ESCALATION RULES
```

The product role answers:

> What learner job is this product supposed to perform?

The content/runtime modules answer:

> What claims and mechanisms inside the artifact require independent verification?

This separation is mandatory. A mathematically correct page can still violate its Core role; a pedagogically coherent page can still contain a wrong equation.

## 4. Canonical intake invariant

Regardless of origin, every promotion effort MUST normalize to one **promotion set** on one draft PR.

A promotion set MAY contain one or more auditable learner products. Each product keeps its own logical identity, complete artifact/bundle digest, role profile, findings and product-level result. The PR also carries one aggregate audit packet so a legitimate multi-product unit does not fragment into unnecessary PRs.

```text
one promotion set
→ one draft PR
→ one exact head SHA
→ N declared product candidates
→ per-product exact artifact/bundle identity
→ one deduplication/lineage reconciliation
→ one composed audit plan
→ per-product evidence + one aggregate audit packet
→ corrections on the same PR
→ one Owner decision that names every exact accepted product/render/bundle digest
```

In LPAP, **candidate** means one product candidate inside a promotion set unless the text explicitly says promotion set. This remains compatible with the repository's one-unit/one-PR method.

Uploads and TEST-page submissions are intake adapters only. They MUST NOT create separate downstream audit protocols.

### 4.1 Existing draft PR

A draft or open PR targeting `main` may become an LPAP candidate when:

- it contains an explicit LPAP intake manifest; or
- it is explicitly labelled/requested for learner-product promotion; or
- candidate discovery finds learner-facing artifacts and reports that promotion review is appropriate.

Discovery MUST be cheap and informational for unrelated engineering PRs.

### 4.2 Uploaded artifact

An uploaded HTML, PDF, ZIP, SVG, or supporting source bundle MUST first be recorded with:

- original filename;
- SHA-256;
- media type;
- supplied source/reference files;
- claimed subject;
- claimed Core/product role;
- claimed topic/subtopic if supplied;
- upload provenance;
- requested publication intent.

The upload path SHOULD create a temporary branch and draft PR. From that point the standard PR route applies.

### 4.3 TEST page

A TEST page is a preview/intake surface, not a publisher.

It MAY:

- accept candidate files;
- render sandboxed previews;
- calculate digests;
- perform local structural checks;
- collect subject/product/source metadata;
- show responsive previews;
- construct an LPAP intake manifest.

A static public page MUST NOT contain a repository write token or deployment credential.

If one-click draft-PR creation is required, it MUST use an authenticated least-privilege GitHub App or trusted backend. That service SHOULD be restricted to candidate branch/file/PR creation and MUST NOT merge to `main` or deploy production Pages.

## 5. Exact-version rule

Every audit packet MUST distinguish **audit provenance** from the **semantic/content basis** that the evidence actually proves.

It MUST bind to:

- candidate PR number or intake identity;
- `audit_basis_head`: the exact PR head SHA at which the audit evidence was produced;
- `candidate_content_basis`: per-product exact artifact/render/bundle identity plus any candidate metadata that affects product identity, role, semantics, runtime, or learner context;
- exact raw-upload digest when an upload/ZIP supplied the bytes;
- selected profile IDs and rule revisions/digests;
- `protocol_digest`;
- `authority_basis_digest`: the canonical/source/denominator/lineage state used by the audit;
- context identity where evidence is role-, route-, or placement-sensitive.

The PR head SHA is therefore a provenance pointer, not by itself the semantic reuse key. A later commit does not force a full re-audit merely because the SHA changed; the workflow MUST first determine whether the candidate/content basis, authority basis, governing audit logic, or relevant context changed.

### 5.1 Multi-file and interactive bundle identity

For an HTML directory, ZIP, interactive webpage, or any product whose behavior depends on multiple files, publication identity MUST cover the entire deployable closure, not only the entry HTML.

Construct a deterministic bundle manifest from every deployable local file. Each entry MUST contain at least:

- normalized POSIX relative path;
- byte length;
- SHA-256 of the exact bytes.

Entries MUST be sorted deterministically by normalized path. The `bundle_digest` is SHA-256 over a canonical serialization of that complete manifest.

The bundle builder MUST reject or explicitly resolve:

- absolute paths;
- `..` traversal;
- duplicate normalized paths;
- unsafe or escaping symlinks;
- case-colliding paths where the deployment target could collapse them.

The original ZIP/upload bytes, when present, retain their own `raw_upload_sha256`; unpacking/repackaging does not erase upload provenance.

Remote assets are not silently part of a local bundle. An external runtime dependency MUST either be pinned by an independently verifiable immutable identity and declared in the audit basis, vendored into the deployable closure, or recorded as an unresolved runtime/publication dependency.

A normalized/semantic digest is never publication identity. Owner acceptance of a multi-file product MUST name the complete `bundle_digest` or a governed render digest that transitively and verifiably binds the complete deployable closure.

### 5.2 Authority conflict semantics

LPAP MUST preserve disagreement between authoritative evidence rather than silently choosing whichever source matches the candidate.

For each material claim, distinguish applicable evidence such as:

- canonical repository academic records;
- source-custody/original-source evidence;
- admitted extension records;
- Owner-supplied benchmark/reference material;
- Core role/specification contracts;
- candidate artifact content.

When material authorities disagree, create an explicit `AUTHORITY_CONFLICT` or `SOURCE_CONFLICT` finding that records:

- the affected claim/item;
- each disagreeing authority and exact basis;
- the practical learner/product consequence;
- the reconciliation needed or Owner/repository decision required.

The affected claim MUST NOT be described as `PASS` while the disagreement remains unresolved.

This is evidence preservation, not a new permission gate: the Owner may still accept an exact product with acknowledged findings under the existing acceptance method.

### 5.3 Acceptance projection versus audit basis

Owner acceptance deliberately creates publication-projection changes and therefore may move the PR head after semantic review. LPAP MUST NOT create an `audit → accept → commit → invalidate → audit again` loop.

Record separately:

- `audit_basis_head` — the head at which semantic/mechanical evidence was produced;
- `candidate_content_basis` — the exact per-product content/render/bundle identity that was reviewed;
- `authority_basis_digest` — the exact source/canonical/denominator/lineage basis used;
- `projection_commit` — a later commit that records Owner acceptance and its deterministic publication consequences.

A commit qualifies as a **projection-only commit** only when it changes no candidate/content basis and no authority/source/denominator inputs. It may contain only the Owner acceptance record, accepted `public/` projection, generated `docs/` mirror, generated search/navigation/manifests, and other deterministic publication outputs derived from the already accepted basis.

For a valid projection-only commit, prior semantic evidence MAY remain current when all applicable reuse keys still match. The projection commit receives targeted re-verification instead of a full semantic re-audit.

Targeted projection re-verification MUST prove:

- every published product still has the exact accepted render/bundle digest;
- the acceptance record names that exact digest;
- copied `public/` bytes equal the accepted projection;
- generated `docs/` equals the current `public/` projection as required by the Pages builder;
- generated search/navigation/manifests are current;
- no candidate, canonical, source, denominator, role, topic/capability, or dedup basis changed in the same commit.

If any of those bases changed, the commit is not projection-only and the dependency-aware rewind rules in §16.2 apply.

Evidence tied to an older head remains historical provenance; it may be reused only when its complete semantic reuse key still matches.

## 6. Deduplication and lineage reconciliation

Deduplication happens before substantive promotion review.

LPAP uses two separate dimensions and MUST NOT replace a stronger existing subsystem vocabulary.

### Identity relation

Where the Question Bank dedup engine applies, preserve its existing relation exactly:

- `DUPLICATE`
- `SOURCE_COLLISION`
- `VARIANT`
- `NEAR_DUPLICATE`
- `DISTINCT`

LPAP may additionally use `RELATED` for a non-QB relationship such as shared capability/family/concept when identity is known to be distinct.

`SOURCE_COLLISION` and `NEAR_DUPLICATE` MUST NOT be collapsed into a generic unresolved/related state.

### Promotion action

Separately record what promotion should do with that identity evidence:

- `REUSE_CANONICAL`
- `ADMIT_VARIANT`
- `ADMIT_NEW`
- `HOLD_UNRESOLVED`

`HOLD_UNRESOLVED` means only that identity is not safe to mutate/admit automatically; it is not a publication veto and does not create a general work-stop state.

String similarity alone MUST NOT collapse records.

### 6.1 Identity-first resolution

Incoming content MUST first be reconciled against existing canonical IDs, source locators, product identities, and lineage records.

Existing canonical identity outranks filename similarity.

### 6.2 Exact byte deduplication

Every incoming file and significant embedded asset SHOULD have a SHA-256.

Exact digest matches can establish byte identity, but byte difference alone does not establish semantic novelty.

### 6.3 Normalized-content comparison

HTML, SVG, or text MAY also receive a normalized digest for duplicate-candidate evidence, but normalization MUST be media-type and semantics aware.

Only transformations whose semantic irrelevance is explicitly defined and tested for that media type may be used. Generic whitespace removal or generated-ID removal is unsafe for some HTML, SVG, scripts, styles, data files, and accessibility relationships and MUST NOT be assumed harmless.

Both raw provenance digest and normalized digest MUST be retained. A normalized digest is only deduplication/reconciliation evidence; it MUST NOT replace source custody, raw byte identity, bundle identity, executable identity, or Owner publication identity.

### 6.4 Academic identity comparison

Questions and concepts MUST be compared using structured meaning where available.

For questions, relevant evidence may include:

- source locator;
- canonical question ID;
- stem/subpart structure;
- givens;
- requested quantity;
- answer/options;
- figure identity;
- adaptation parent;
- capability/family refs.

A numerical variant can belong to the same question family without being the same question record.

### 6.5 Product identity

A learner product SHOULD have one logical product identity such as:

`subject + topic/subtopic + Core role + product slug`

Revisions SHOULD update the product instead of creating filename-level pseudo-versions such as `final-v2-new.html`.

Exact renders remain separately identifiable by digest.

### 6.6 Audit finding deduplication

A repeated defect mechanism SHOULD be grouped into one finding listing affected records.

A stable finding identity MUST bind a stable rule ID/revision, not a prose heading. Conceptually:

```text
rule_id@revision
+ canonical item/ref
+ affected field/surface
+ defect mechanism
+ context identity where the rule is role-sensitive
```

Example rule ID: `LPAP.C2.HINT.PROVENANCE@1`.

Finding disposition across renders is recorded through the existing review history model where possible. LPAP MUST NOT invent a conflicting per-finding status field inside `product-review/v2`.

### 6.7 Audit-run reuse

An audit run or individual evidence item may be reused only when every relevant semantic key matches, including:

```text
candidate_content_basis
+ authority_basis_digest
+ protocol_digest
+ selected profile_id@revision
+ applicable rule_id@revision or rule digest
+ context identity for role-sensitive evidence
```

`audit_basis_head` MUST be retained as provenance, but a head-SHA change alone does not invalidate semantic evidence when the new delta is proven projection-only under §5.3.

Any semantic change to the candidate/content basis, authority basis, governing rule/profile, or relevant context invalidates the dependent evidence unless an explicit compatibility mapping exists.

### 6.8 Intrinsic versus contextual evidence

Intrinsic evidence MAY be reused by content digest.

Example: an SVG has no clipping at a given viewport.

Context-sensitive conclusions MUST include role/location context.

Example: the same SVG may be appropriate in Core1A but reveal the deciding construction too early in Core2.

### 6.9 Deduplication output

Before deep audit, produce a reconciliation table:

| Incoming item | Existing match | Identity relation | Basis | Promotion action |
|---|---|---|---|---|
| item/ref | canonical ref or NONE | DUPLICATE / SOURCE_COLLISION / VARIANT / NEAR_DUPLICATE / RELATED / DISTINCT | evidence | REUSE_CANONICAL / ADMIT_VARIANT / ADMIT_NEW / HOLD_UNRESOLVED |

LPAP MUST NOT create a second curriculum database, question catalog, source ledger, or product registry merely to track promotion.

## 7. Audit-plan selector

Each candidate MUST receive a deterministic audit plan.

The declared/established learner-product role selects the base role profile. Detected features, source claims, cross-Core claims, and runtime behavior may only **add or escalate** audit modules; they MUST NOT de-escalate or remove the base role audit.

If role identity is missing or ambiguous, record an identity/scope finding and run at least the Common Kernel plus every content/runtime module detected from the artifact. Do not silently choose the lightest profile.

The selector uses:

1. declared product role;
2. detected content/features;
3. source-custody claims;
4. cross-Core claims;
5. runtime/interactive behavior.

Example:

```text
CORE2 + equations + instructional SVG + source custody
→ Common Kernel
→ Core2 Deep Profile
→ Equation Module
→ SVG/Diagram Module
→ Source-Custody Module
→ Cross-Core Module if mappings are present
```

Example:

```text
CORE1B + reconstruction prompts only
→ Common Kernel
→ Core1B Role Profile
```

Example:

```text
CORE2B + executable graph
→ Common Kernel
→ Core2B Role Profile
→ Interactive Deep Profile
→ Equation Module where applicable
→ SVG/Diagram Module
→ Cross-Core Module
```

The selected plan MUST be written into the audit packet.

## 8. Common Audit Kernel

Every learner-facing candidate receives the Common Audit Kernel.

### K1. Identity and scope

Confirm:

- subject;
- grade;
- topic;
- subtopic;
- Core/product role;
- logical product identity;
- source or authoring basis;
- intended learner;
- claimed scope;
- declared denominator where applicable.

The visible product MUST NOT imply broader coverage than the evidence supports.

### K2. Academic correctness

Verify applicable:

- definitions;
- scientific statements;
- mathematical relationships;
- notation;
- units;
- conventions;
- assumptions;
- boundary conditions;
- terminology.

Substantive equations MUST be independently checked.

### K3. Completeness

Compare against an external/canonical denominator rather than the candidate's own navigation count.

Classify content as:

- `PRESENT_CORRECT`
- `PRESENT_INCOMPLETE`
- `PRESENT_WRONG`
- `MISSING`
- `EXTRA_SUPPORTED`
- `EXTRA_UNSUPPORTED`

### K4. Internal consistency

Check consistency among:

- prose;
- equations;
- diagrams;
- examples;
- answers;
- hints;
- labels;
- source identifiers;
- navigation.

### K5. Learner-role fidelity

Verify that the product actually requires the kind of learner thinking assigned to its role.

Useful content is not automatically role-conformant content.

### K6. Pedagogical coherence

Inspect:

- sequencing;
- prerequisite use;
- cognitive jumps;
- examples;
- checks;
- feedback;
- scaffolding;
- transfer.

Presence of cards/headings is not evidence of pedagogy.

### K7. Representation integrity

Audit meaning-bearing:

- SVGs;
- diagrams;
- graphs;
- tables;
- equation layouts;
- animations;
- coordinate plots;
- vector figures;
- geometric constructions.

Academic/semantic correctness matters independently of rendering quality.

### K8. Typography and hierarchy

Inspect:

- readable type;
- heading hierarchy;
- mathematical legibility;
- line length;
- information density;
- contrast;
- spacing;
- grouping;
- alignment;
- emphasis.

### K9. Responsive layout

Inspect representative:

- tablet landscape;
- tablet portrait;
- compact/mobile widths.

Verify:

- no accidental page-level horizontal overflow;
- readable equations/diagrams;
- stable navigation;
- meaningful stacking;
- no hidden instructional content.

### K10. Accessibility and input

Inspect:

- semantic structure;
- keyboard navigation;
- visible focus;
- touch targets;
- text alternatives;
- SVG accessibility;
- colour dependence;
- contrast;
- reduced motion;
- form/control labels;
- textarea/input usability.

Grade9V3's existing 48px tablet touch-target convention remains the local target where applicable.

### K11. Navigation and escape routes

Every promoted learner product SHOULD provide appropriate routes to:

- Home;
- subject;
- topic/subtopic;
- related Core where justified;
- Question Bank where relevant.

Learner-facing pages MUST NOT become accidental dead ends.

### K12. Deployability and runtime integrity

Verify:

- intended production path;
- Pages reachability;
- asset existence;
- relative URL correctness;
- offline/runtime claims;
- local state/version behavior;
- no accidental repository-only links.

## 9. Deep Audit Profile: Core2

### 9.1 Role

Core2 preserves authentic assessment/question demand:

```text
question
→ learner attempt
→ optional staged support
→ continued work
→ full solution/check
```

Core2 MUST NOT become a tutorial that exposes the deciding method before the learner has a chance to attempt the task.

### 9.2 Source fidelity

Where source custody is claimed, verify every applicable:

- source identity;
- stem;
- subpart;
- option;
- numerical value;
- unit;
- figure;
- source hint;
- printed key/answer.

Distinguish original, adapted, authored, and independently verified material.

### 9.3 Independent solving

Do not validate a question by comparing its solution with its own displayed answer.

Independently solve mechanically feasible questions and manually inspect coverage across every substantive question family.

Check:

- model;
- variable definitions;
- signs;
- algebra;
- units;
- boundary conditions;
- final result;
- option selection;
- interpretation.

A correct final option reached through invalid reasoning is a defect.

### 9.4 Hint ladder

Audit cognitive progression, not hint count.

A useful ladder commonly progresses through:

1. **Notice / Key idea** — identify relevant structure without solving.
2. **Model / Representation** — construct the needed physical/mathematical representation.
3. **Start / First executable move** — provide a valid start while leaving meaningful learner work.

Flag:

- `TOO_REVEALING`
- `DUPLICATIVE`
- `GENERIC_FILLER`
- `WRONG_MODEL`
- `WRONG_FIRST_MOVE`
- `PROVENANCE_ERROR`
- `CONTRADICTS_SOLUTION`

Do not invent missing rungs merely to satisfy a visual pattern.

### 9.5 Solution integrity

A complete solution SHOULD make visible, where meaningful:

- setup;
- governing principle;
- representation;
- calculation;
- answer;
- check/interpretation.

### 9.6 Coverage

For large banks, combine:

- mechanical verification of all feasible calculations; and
- stratified deep review across topic, difficulty, equation family, diagram family, special case, and reasoning-route family.

The audit packet MUST state what was exhaustively checked and what was sampled.

### 9.7 Core1A join

Where canonical concept/capability mappings exist, verify:

`Core2 question → required concept(s) → Core1A construction`

Do not infer exact joins from keyword similarity.

## 10. Deep Audit Profile: Core1A

### 10.1 Role

Core1A is the Concept Book.

Its learner job is to construct the model deeply enough that equations, assumptions, representations, and boundaries make sense.

It MUST NOT collapse into a formula sheet or a bank of worked answers.

### 10.2 Conceptual construction

For each substantive concept, inspect whether the experience provides a coherent route such as:

```text
orientation
→ physical/conceptual model
→ representation
→ formal mathematical bridge
→ conditions/boundaries
→ misconception diagnosis/repair
→ worked anchor
→ reduced-support check
→ transfer
```

The page does not need one fixed card shape. The conceptual progression matters.

### 10.3 Prerequisite integrity

Check:

- prerequisite concepts;
- notation;
- assumed mathematics;
- earlier physical models;
- frame/sign conventions.

Major prerequisites MUST NOT be silently assumed without support or navigation.

### 10.4 Equation audit

For every important relation verify applicable:

- derivation or meaningful bridge;
- variable meaning;
- units;
- assumptions;
- validity;
- special/limiting cases.

A relation valid only under constrained conditions MUST NOT be presented as universal.

### 10.5 Representation audit

Figures MUST correspond to the chosen model and conventions.

Examples include:

- vector decomposition against declared axes;
- trajectory and velocity geometry;
- acceleration direction;
- graph slope/area semantics;
- geometric construction.

### 10.6 Misconception quality

Useful misconception treatment SHOULD include:

```text
diagnosis
→ why the idea fails
→ repair
→ check
```

Generic warnings without a concrete failure mechanism do not satisfy this role.

### 10.7 Worked anchor

A worked anchor MUST be mathematically/academically correct and SHOULD illuminate the concept just constructed.

It SHOULD NOT silently introduce a major new conceptual dependency.

### 10.8 Transfer readiness

Where Core2 exists, map important Core2 demand families to Core1A preparation:

- `PREPARED`
- `PARTIALLY_PREPARED`
- `MISSING_PREPARATION`
- `MAPPING_UNCERTAIN`

## 11. Deep Audit Profile: Interactive Webpage

### 11.1 Role

An interactive webpage must make interaction cognitively meaningful.

Controls moving graphics is not sufficient.

For every major interaction establish:

`learner action → model change → visible consequence → intended inference`

### 11.2 Model correctness

Test the executable model against:

- initial conditions;
- zeros;
- negative values where valid;
- extremes;
- limits;
- symmetric cases;
- known special cases.

Use property/numerical falsifiers where practical.

### 11.3 Visual-semantic correctness

Across the operating range inspect:

- vector direction;
- path geometry;
- graph axes/scales;
- labels;
- intersections;
- event order;
- constraints;
- physical/geometric meaning.

### 11.4 Causal integrity

When one parameter changes, every dependent representation MUST update consistently.

A stale representation that contradicts the new state is an academic defect, not only a UI defect.

### 11.5 State integrity

Check:

- reset;
- defaults;
- mode/example switching;
- localStorage/session state;
- refresh;
- orientation changes.

State MUST NOT leak across incompatible scenarios.

### 11.6 Interaction accessibility

Check:

- keyboard operation;
- touch operation;
- focus;
- labels;
- reduced motion;
- status/feedback exposure where needed.

### 11.7 Responsive interaction

Test the interaction itself at representative viewports:

- SVG/canvas scaling;
- control reachability;
- label collisions;
- graph legibility;
- portrait behavior;
- compact behavior;
- virtual keyboard interactions.

### 11.8 Runtime robustness

Check:

- console/runtime errors;
- missing dependencies;
- event listeners;
- NaN/Infinity propagation;
- invalid input;
- repeated control use;
- reset/re-entry;
- meaningful offline behavior when claimed.

## 12. Lightweight role profiles

Core1, Core1B, Core2A, and Core2B use the Common Audit Kernel plus these role-specific checks.

They automatically escalate to deeper modules based on actual content.

### 12.1 Core1 — semantic orientation

Check:

- correct definitions;
- notation;
- prerequisites;
- governing relations;
- meaning of quantities;
- scope/boundaries;
- useful representative diagram;
- common confusion;
- navigation to deeper teaching.

Core1 SHOULD remain compact.

If it contains substantial derivations, interactive graphics, or detailed conceptual construction, add the applicable Core1A/Equation/Interactive modules.

### 12.2 Core1B — reconstruction/self-tutor

Check:

- learner must generate/reconstruct rather than reread;
- protected answer is not exposed too early;
- graduated support;
- cycle can close without a tutor;
- feedback repairs conceptual errors;
- claimed coverage matches relevant conceptual construction;
- learner action requires reasoning, not click-through.

Core1B MUST NOT be Core1A prose split into accordions.

Add Question, Equation, SVG, or Interactive modules when those features occur.

### 12.3 Core2A — familiar application

Check:

- claimed concept has prior exposure;
- task remains learner work;
- reasoning route is correct;
- stable crux/first meaningful move is valid;
- scaffolding does not become transcription;
- solution is independently correct;
- lineage to prior learning is honest.

When questions contain substantial quantitative reasoning or source adaptation, apply the Core2 independent-solution/source checks.

### 12.4 Core2B — transfer

For each item establish:

`prior exposure → changed demand → new learner decision → required adaptation → repair path`

Check:

- changed demand is real;
- difference is not cosmetic;
- prior exposure exists;
- lineage/adaptation is honest;
- learner must adapt rather than repeat;
- solution/rubric explains the transfer;
- repair targets the failed decision.

Use Core2 source/fidelity checks for source-derived tasks and the Interactive profile for executable transfer experiences.

## 13. Content-triggered audit modules

### 13.1 Equation Module

Trigger when substantive equations or calculations occur.

Verify:

- independent derivation/recomputation;
- dimensions/units;
- assumptions;
- conditions;
- sign/frame conventions;
- special cases;
- numerical consistency.

### 13.2 Question Module

Trigger when the artifact contains answerable quantitative/conceptual tasks.

Verify:

- independent answer;
- reasoning;
- answer/options;
- support/hints;
- checks.

### 13.3 SVG/Diagram Module

Trigger for instructional diagrams/SVGs.

Verify:

- axes/origin;
- vector/force/velocity/acceleration directions;
- component decomposition;
- angle location;
- labels;
- trajectory/geometry;
- event order;
- staged-state semantics;
- accessible meaning;
- clipping/legibility.

A polished but physically misleading diagram is a content defect.

### 13.4 Interactive Module

Trigger whenever learner controls mutate model state or representations.

Apply the Interactive Deep Profile.

### 13.5 Source-Custody Module

Trigger whenever the product claims reproduction/adaptation of a source, benchmark, PYQ, or other governed question set.

Perform component-level source comparison and preserve provenance distinctions.

### 13.6 Cross-Core Module

Trigger whenever prerequisite, repair, transfer, or exact-return links across Core roles are claimed.

Validate mappings using canonical references where available.

## 14. Audit depth

### Level 1 — Role conformance

Typical for simple Core1/Core1B resources.

Includes:

- Common Kernel;
- role profile;
- applicable low-cost content modules.

### Level 2 — Independent content review

Typical for Core2A/Core2B or equation/question-heavy resources.

Adds:

- independent solving;
- detailed lineage/source review;
- deeper representation checks.

### Level 3 — Deep product audit

Default for:

- Core2;
- Core1A;
- Interactive Webpages.

Also applies to any artifact whose detected content justifies the same depth.

Includes:

- full Common Kernel;
- deep role profile;
- all applicable content modules;
- browser/runtime evidence;
- explicit denominator reconciliation.

## 15. Audit ledger and review-schema compatibility

LPAP-v1 does not redefine `product-review/v2`.

The existing independent review remains the authoritative coaching review for a governed exact render:

- finding severity is only `S0`, `S1`, `S2`, or `S3`;
- `PASS` is an audit evidence/result state, never a severity;
- current `previous_findings.status` remains `FIXED`, `OPEN`, or `WONT_FIX`;
- LPAP MUST NOT write `REGRESSED` or `PASS` into fields whose current schema does not permit them.

LPAP may produce an **audit packet sidecar** that references one or more `product-review/v2` documents and contains additional machine evidence not represented by that schema, such as:

| Field | Meaning |
|---|---|
| product | logical learner product |
| area / rule_id | audit dimension and stable rule identity |
| item/ref | exact record, section, question, SVG, control, or route |
| authority | canonical/source basis |
| observation | evidence-based result |
| learner impact | consequence for learner where a defect exists |
| evidence_result | PASS / FINDING / NOT_APPLICABLE / NOT_RUN |
| review_finding_id | linked `product-review/v2` finding when applicable |
| reviewed digest | exact artifact/render/bundle basis |

A regression is represented by reopening/creating the applicable current-render finding while preserving prior finding history, unless a future review-schema version explicitly adds a regression state.

If future automation needs first-class LPAP fields inside the review schema, that requires a separately reviewed schema version; #374 does not change `product-review/v2`.

## 16. Promotion audit sequence

The normal sequence is:

```text
INTAKE
→ EXACT-VERSION CAPTURE
→ SOURCE / AUTHORITY BASIS CAPTURE
→ DEDUPLICATION / LINEAGE RECONCILIATION
→ FULL SOURCE / DENOMINATOR RECONSTRUCTION
→ AUDIT-PLAN SELECTION
→ MECHANICAL AUDIT
→ INDEPENDENT ACADEMIC / PRODUCT AUDIT
→ CORRECTION ON SAME PR
→ REWIND TO EARLIEST AFFECTED STAGE
→ INTEGRATION / NAVIGATION RESOLUTION
→ PRODUCTION DRY-RUN
→ OWNER REVIEW
→ PER-PRODUCT OWNER DISPOSITION
→ TRUSTED ACCEPTANCE/PUBLICATION PROJECTION FOR ACCEPTED PRODUCTS
→ COMMIT + TARGETED REVERIFY OF THE EXACT ACCEPTED PROJECTION
→ MERGE TO MAIN
→ TRUSTED DEFAULT-BRANCH PAGES DEPLOYMENT
→ POST-PUBLICATION VERIFICATION
```

The sequence is evidence flow, not a new numerical quality gate.

### 16.1 Source / authority basis capture

Before identity classification, capture the minimum stable source/authority facts needed to interpret deduplication and lineage safely.

This cheap pre-dedup capture SHOULD include, where applicable:

- supplied source locators and source files;
- claimed canonical IDs;
- source-custody identity fields;
- explicit adaptation/family/parent refs;
- current canonical record identity and digest;
- admitted extension/benchmark identity;
- declared product role and subject/topic context.

This stage does not need to reconstruct the full denominator. Its purpose is to ensure LPAP never attempts to distinguish `SOURCE_COLLISION` from `VARIANT` before the relevant source identity is known.

After deduplication/lineage reconciliation, perform full source/denominator reconstruction for completeness, correctness, authority conflict, and audit-plan selection.

### 16.2 Dependency-aware correction and rewind

A correction does not automatically mean “rerun only the changed page.” The workflow MUST determine the earliest audit stage whose inputs changed and recompute from there.

Examples:

| Correction/change | Minimum rewind |
|---|---|
| presentation-only CSS/layout change with unchanged product/source/identity basis | exact-version capture + affected browser/UX/accessibility evidence |
| candidate academic content, question, hint, SVG, equation, runtime model, or bundle content | exact-version capture + every identity/dedup/audit module whose inputs changed |
| source locator/custody, canonical identity, lineage, family/adaptation relation, or dedup input | source/authority basis capture → dedup/lineage → denominator → plan/audit as affected |
| canonical academic record, denominator, topic/capability mapping, or role identity | source/authority basis capture → affected identity/denominator reconstruction → audit-plan selection → dependent audits |
| protocol/profile/rule semantics | audit-plan selection and invalidation of all evidence governed by the changed profile/rule |

The table states minimum rewind, not permission to skip a dependency that actually changed.

Canonical/source/denominator truth MUST NOT be edited merely to make the candidate pass or to erase a finding.

A legitimate correction to canonical/source/denominator authority MUST:

- have evidence independent of the candidate's desire to pass;
- record why the prior authority was wrong/incomplete;
- preserve the prior basis/history;
- produce a new `authority_basis_digest`;
- re-run every dependent reconciliation/audit stage against that new basis.

If an authority change resolves a prior `AUTHORITY_CONFLICT` or `SOURCE_CONFLICT`, the reconciliation record must show both the prior disagreement and the new authoritative basis rather than rewriting history.

### 16.3 Current publication interface versus generic resources

For governed Core products, current repository reality is normative: `Shared/tools/accept_product.py` is the publication entry point. During Owner acceptance it verifies the exact governed render, records the decision, copies the exact accepted pages into `public/`, and rebuilds/checks the Pages mirror. Those publication-projection changes are then committed/reverified on the candidate branch before merge; deployment from `main` follows separately.

LPAP MUST NOT describe merge as occurring before that current acceptance/publication projection.

A generic interactive webpage/ZIP that is not representable by the governed Core manifest/render path may still reach `AUDIT_COMPLETE`, but it MUST NOT be labelled `PUBLISHABLE_UNDER_LPAP` until it enters a repository-governed acceptance interface that can bind the Owner's decision to the complete deployable `bundle_digest` and publish exactly those bytes.

LPAP-v1 recognizes two valid ways to satisfy that requirement:

1. adapt the product into an existing governed representation accepted by the current publisher; or
2. introduce, in a separate reviewed implementation/schema PR, a resource acceptance adapter that:
   - records product/resource identity and complete bundle digest;
   - records the Owner's exact decision/reference;
   - copies only the accepted bundle into the authoritative `public/` destination;
   - regenerates/checks `docs/`;
   - preserves source/resource/search lineage;
   - does not create a second curriculum or publication authority.

#374 specifies this boundary but does not implement the generic resource acceptance adapter.

## 17. Integration resolver

Only after academic/product review should the candidate be mapped into learner navigation.

Resolve:

`Subject → Topic → Subtopic → Product role/resource type`

Typical Core1A route:

`Home → Subject → Topic/Subtopic → Core1A → bucket/section`

Typical Core2 route:

`Question Bank → Subject → Topic → Subtopic → question/study`

A topic-specific Core2 study product may also be surfaced from the relevant subject/topic resource area without forking global Question Bank taxonomy.

Generic browser/runtime code MUST NOT gain topic-specific branches solely to expose one candidate.

## 18. Root landing-page policy

Being published and being featured on the root Home page are separate decisions.

Every accepted learner product SHOULD be reachable from Home through the appropriate hierarchy.

A direct root-home feature SHOULD be added only when:

- explicitly requested by the Owner; or
- current homepage policy classifies the product as featured.

The audit/integration packet SHOULD record:

- `reachable_from_home: true|false`
- `root_home_featured: true|false`

This prevents Home from becoming a flat catalog.

## 19. Search indexing and discoverability

Promotion MUST update search through canonical producers, never by hand-editing generated search artifacts.

Grade9V3 currently has two learner search projections that must remain coherent:

1. the Question Bank platform search, generated as `public/data/question-bank-search.js`; and
2. the site-header/global search projection, generated as `public/data/question-bank-data.js`.

The global site header currently reads the older monolithic projection, while the Question Bank page reads the newer generated platform contracts. Until those consumers converge, LPAP promotion MUST verify both.

### 19.1 Core2 questions

A promoted Core2 question becomes searchable only by entering the existing canonical Question Bank projection path:

- canonical exam-bank question; or
- package-shaped canonical question explicitly opted into Question Bank publication.

LPAP MUST NOT copy question text into a separate search registry.

After canonical integration, the Question Bank generators produce the search documents from the same records.

### 19.2 Core1A, interactive pages, and other learner resources

A learner resource that should be searchable SHOULD be represented through the existing subject resource/discovery authority rather than inserted directly into generated JavaScript.

For ordinary resources, use the applicable `<Subject>/question-bank/resources.v1.json` record with:

- stable resource id;
- kind;
- title;
- deployable path relative to `public/`;
- useful search keywords;
- subject/topic metadata as supported.

Governed explorer suites already discovered from existing suite records SHOULD continue to use that discovery path rather than being duplicated in the resource registry unless an explicit topic link or additional governed resource relationship is required.

When a resource belongs to an existing Question Bank topic, use the existing explicit `topic_ref` / `topic_links` mechanism where appropriate. The generator MUST NOT infer a canonical topic association from similar names.

### 19.3 Search deduplication

Search documents are projections, not identities.

LPAP MUST resolve duplicate/variant/new product identity before indexing.

The search layer MUST NOT create a second result merely because the same logical product is reachable through several navigation surfaces.

Where one canonical resource has multiple contextual links, prefer one searchable resource identity whose destination is canonical.

Questions that are variants remain separate search documents only when they remain separate canonical question records.

### 19.4 Regeneration

After promotion integration, regenerate through the existing producers rather than editing outputs:

```text
python3 Shared/tools/build_question_bank_web.py
python3 Shared/tools/build_question_bank_platform.py --write
python3 Shared/tools/build_pages_site.py
python3 Shared/tools/build_manifest.py
```

Then run the corresponding `--check` modes supported by those generators.

Generated artifacts such as these MUST NOT be manually authored:

- `public/data/question-bank-data.js`
- `public/data/question-bank-search.js`
- `public/data/question-bank-catalog.js`
- `public/data/question-bank-resources.js`
- `docs/data/question-bank-*.js`

### 19.5 Search acceptance evidence

The **promotion packet itself MUST contain search/discoverability evidence** for every product in the promotion set. A successful generator run without the corresponding packet evidence is insufficient.

For each product, the promotion packet MUST verify and record:

- `searchable_intent`: whether the product is intended to be searchable;
- `canonical_search_identity`: the canonical question/resource/product identity that owns the search result;
- `search_projection`: which generated projection(s) are expected to contain it;
- `generated_search_id`: the generated search document/resource id, or `NOT_APPLICABLE` with reason;
- `expected_queries[]`: representative deterministic search terms, including at least one learner-natural query rather than only an exact ID;
- `expected_destination`: the canonical deployed destination URL/path;
- `actual_destination`: the generated search result destination observed in the dry-run;
- `duplicate_result_count`: unintended duplicate results for the same canonical identity, expected to be zero;
- `question_bank_search_visibility`: `PASS / NOT_APPLICABLE / FINDING`;
- `global_header_search_visibility`: `PASS / NOT_APPLICABLE / FINDING`;
- `public_projection_current`: whether generated `public/` search artifacts match the current canonical inputs;
- `docs_projection_current`: whether generated `docs/` search artifacts match the `public/` projection;
- `search_basis_digest`: the relevant Question Bank/resource/search build identity or digest so the witness is tied to exact generated bytes.

At least one deterministic search witness MUST be recorded for each newly searchable resource and for each newly introduced question family or search identity. If several questions share the same family, one family-level natural-language witness MAY supplement—but MUST NOT replace—identity-level checks that prove each canonical question is indexed exactly once.

Example evidence:

```text
product: PHY-MOTION2D-CORE1A
searchable_intent: true
canonical_search_identity: RESOURCE-PHY-MOTION2D-CORE1A
search_projection:
  - question-bank-search
  - global-header-search
query: "projectile motion concept book"
expected destination: physics/.../core1a.html
actual destination: physics/.../core1a.html
duplicate result count: 0
question_bank_search_visibility: PASS
global_header_search_visibility: PASS
public_projection_current: true
docs_projection_current: true
search_basis_digest: <exact build/digest>
```

A product that is intentionally not searchable MUST still appear in the promotion packet with `searchable_intent: false` and a reason; omission is not equivalent to `NOT_APPLICABLE`.

Searchability does not imply root-home featuring. A product may be searchable and hierarchically reachable without receiving a root-home card.

## 20. Publication dry-run

Before acceptance, construct the intended production tree without production deployment.

Verify:

- proposed `public/...` destination;
- generated `docs/...` destination;
- Home/subject/topic routes;
- Question Bank/resource linkage where applicable;
- no broken or escaping links;
- no orphan learner page;
- asset completeness;
- runtime/offline behavior;
- exact generated/output digest.

Generated `docs/` MUST NOT be hand-edited.

## 21. Automatic triggering

LPAP automation uses four trigger layers. They MUST remain distinct so ordinary engineering PR activity does not accidentally become an expensive academic audit or a publication action.

```text
INTAKE TRIGGER
→ CHEAP CANDIDATE DISCOVERY
→ EXPLICIT AUDIT ACTIVATION
→ ROLE + CONTENT MODULE SELECTION
→ DELTA-BASED RE-AUDIT / REWIND
```

Automatic triggering never grants publication authority.

### 21.1 Intake triggers

LPAP intake may begin from any of these routes:

1. **Existing PR** — a PR targeting `main` contains or is declared to contain learner-facing promotion candidates.
2. **Upload** — HTML, ZIP, PDF, SVG, or supporting files are submitted to an authenticated intake adapter, which creates/updates a candidate branch and draft PR before LPAP audit begins.
3. **TEST page** — the learner-product TEST/intake surface prepares the bundle, digests, metadata, and intake manifest; an authenticated least-privilege service MAY create the draft PR. The TEST page itself MUST NOT publish.
4. **Manual replay** — an authorized `workflow_dispatch` or equivalent MAY request re-evaluation of an existing promotion set without changing publication authority.

All routes normalize to the same draft-PR promotion-set model in §4.

### 21.2 PR discovery events

Cheap candidate discovery SHOULD run on relevant `pull_request` activity, including:

- `opened`;
- `synchronize`;
- `reopened`;
- `labeled` or equivalent explicit promotion request;
- `ready_for_review`;
- `converted_to_draft` where useful for pausing/refreshing state.

Discovery SHOULD classify the PR as either:

- `NOT_A_LEARNER_PROMOTION`; or
- `LEARNER_PROMOTION_CANDIDATE`.

Discovery MUST remain lightweight. Merely touching HTML, CSS, JavaScript, SVG, or `public/` does not by itself authorize the expensive LPAP audit.

### 21.3 Audit activation

The expensive LPAP audit SHOULD activate only when promotion intent is explicit. Valid activation signals include:

- a valid LPAP intake manifest;
- a `learner-promotion` label/request or its future repository equivalent;
- recognized learner-product paths plus explicit confirmed promotion intent;
- an authorized manual replay for an already registered promotion set.

A discovered learner-facing file without promotion intent MAY be reported as a candidate but MUST NOT silently become a full promotion audit.

Activation starts audit/evidence generation only. It MUST NOT merge, publish, create an Owner acceptance record, or expose production navigation/search entries.

### 21.4 Role/profile and content-module triggers

Once activated, the declared/established learner role selects the mandatory base profile:

| Product role | Base audit |
|---|---|
| Core2 | Common Kernel + `LPAP.CORE2@1` |
| Core1A | Common Kernel + `LPAP.CORE1A@1` |
| Interactive webpage/product | Common Kernel + `LPAP.INTERACTIVE@1` |
| Core1 | Common Kernel + `LPAP.CORE1@1` |
| Core1B | Common Kernel + `LPAP.CORE1B@1` |
| Core2A | Common Kernel + `LPAP.CORE2A@1` |
| Core2B | Common Kernel + `LPAP.CORE2B@1` |

Detected content may only add/escalate audit coverage:

- substantive equations/calculations → Equation Module;
- answerable quantitative/conceptual questions → Question Module;
- instructional SVG/diagram/graph → SVG/Diagram Module;
- learner controls that mutate model state/representation → Interactive Module / deep interactive profile;
- PYQ/source/benchmark/source-custody claims → Source-Custody Module;
- prerequisite/repair/transfer/exact-return claims across Cores → Cross-Core Module.

Missing metadata MUST NOT be used to obtain a cheaper audit. Ambiguous role follows the escalation rule in §7.

### 21.5 Change and re-audit triggers

Every new candidate-branch commit triggers **delta classification**, not an unconditional full audit.

The orchestrator compares the new head against:

- `candidate_content_basis`;
- `authority_basis_digest`;
- selected profile/rule revisions;
- source/dedup/denominator inputs;
- relevant placement/runtime context.

Then:

- presentation-only changes rerun the affected browser/UX/accessibility evidence;
- candidate academic/runtime/bundle changes rerun the dependent semantic/mechanical modules;
- source, custody, canonical, denominator, lineage, role, topic/capability, or dedup-input changes rewind according to §16.2;
- a proven projection-only acceptance commit under §5.3 keeps valid semantic evidence and runs targeted publication/search/Pages re-verification;
- an unclassifiable delta makes affected evidence stale rather than assuming reuse.

### 21.6 Reusable workflow architecture

The heavy audit SHOULD be implemented as one reusable workflow or equivalent shared runner rather than copied into Core-specific workflows.

Existing product-specific workflows MAY contribute evidence to the LPAP packet, but they MUST NOT independently redefine LPAP activation, Owner authority, or publication semantics.

A useful implementation split is:

```text
candidate-discovery
→ LPAP dispatcher
→ reusable audit runner
→ per-product evidence aggregation
→ promotion packet
```

### 21.7 Security separation

Candidate PR code is untrusted.

PR audit jobs SHOULD:

- use read-only repository permission;
- receive no publication secrets;
- avoid production deploy credentials;
- avoid mutation of `main`;
- avoid privileged execution of untrusted PR code.

Deep interactive/browser auditing necessarily executes candidate JavaScript. That execution MUST occur in a secret-free, credential-free isolated environment with:

- no privileged repository token exposed to the page/process;
- no trusted browser profile, cookies, saved sessions, or personal credentials;
- no mounted sensitive local files or host credentials;
- no access to cloud metadata endpoints or sensitive internal/local network services;
- external network denied by default, or explicitly allowlisted and recorded when network behavior itself is under audit;
- disposable browser/runtime state.

A privileged workflow MUST NOT check out and execute untrusted candidate code merely to gain write permissions.

Repair automation, when authorized, SHOULD write only to the candidate branch.

Production publication/deployment remains a separate trusted path after Owner acceptance and merge.

## 22. Mechanical versus independent evidence

Automation is appropriate for:

- candidate discovery;
- digesting;
- deduplication hints;
- schema/structure checks;
- source inventory comparison;
- link/asset checking;
- mathematical recomputation where deterministic;
- browser geometry;
- viewport testing;
- runtime/property checks;
- Pages dry-run;
- report generation.

Independent semantic review remains necessary for:

- conceptual correctness;
- pedagogical sequencing;
- validity of derivations;
- misleading diagrams;
- hint quality;
- source interpretation;
- transfer validity;
- whether an interaction teaches the intended inference.

No automated label such as `PASS` may imply human/independent academic review unless that review actually occurred and is recorded.

## 23. Owner review packet

Before publication, present the Owner with:

- current PR/head SHA and the `audit_basis_head`;
- per-product `candidate_content_basis` and exact artifact/render/bundle digest;
- `authority_basis_digest` and source/denominator summary;
- declared product role;
- deduplication/lineage reconciliation;
- selected audit plan;
- independent review and unresolved findings;
- representative browser/render evidence;
- Core1A↔Core2 coverage when applicable;
- proposed navigation;
- search/discoverability evidence required by §19.5;
- proposed public/deployed paths;
- validation/test results.

### 23.1 Per-product Owner disposition

A promotion set is not all-or-nothing.

Before merge, every in-scope product MUST have an explicit Owner disposition in the promotion packet:

- `ACCEPTED` — the exact named render/bundle digest may enter the governed publication projection;
- `DEFERRED` — no publication projection is created for this product in the current promotion;
- `REJECTED` — no publication projection is created for this product in the current promotion.

Only `ACCEPTED` products may receive acceptance records, production navigation/search exposure, or published `public/` bytes through LPAP.

A `DEFERRED` or `REJECTED` candidate MAY remain in the merged repository only when repository policy otherwise permits it and it is unmistakably non-published/non-authoritative. At minimum it MUST:

- remain outside the deployed `public/` and generated `docs/` learner tree;
- have no production acceptance record;
- have no production navigation/search/resource-registry exposure;
- not masquerade as canonical academic/source authority;
- remain clearly identified as draft/test/source material where its location is otherwise ambiguous.

If those conditions cannot be met, remove the deferred/rejected product changes from the promotion set or split them to another PR before merge.

Per-product disposition does not waive validation of shared files. If accepted and non-accepted products share runtime, canonical, source, or generated inputs, the shared changes must still be justified and validated independently.

The Owner's decision is always tied to the exact product digest/basis named in the packet.

## 24. Publication

For governed Core products, use the existing `Shared/tools/accept_product.py` acceptance/publication path exactly as described in §16.3.

LPAP MUST NOT introduce a second publisher.

If an imported candidate cannot be represented by an existing governed acceptance interface, it may be audited and integrated in draft form but is not yet `PUBLISHABLE_UNDER_LPAP`. It must first be adapted to an existing governed representation or wait for the separately reviewed generic resource acceptance adapter described in §16.3.

For the current governed Core path, after the per-product Owner dispositions are recorded:

- run the trusted acceptance/publication projection only for products marked `ACCEPTED`;
- create no production acceptance/search/navigation/public projection for `DEFERRED` or `REJECTED` products;
- commit the acceptance records plus exact accepted `public/` bytes and deterministic generated `docs/`/search/navigation/manifests;
- record that commit as `projection_commit`;
- run the targeted projection re-verification required by §5.3;
- confirm every in-scope product has an explicit disposition and any non-accepted bytes satisfy §23.1;
- merge the approved promotion set;
- deploy from trusted/default-branch state;
- verify resulting learner routes.

Do not hand-edit generated Pages output.

## 25. Post-publication verification

After `main` changes, verify:

- Pages mirror freshness;
- intended Home/subject/topic route;
- production URL reachability;
- Question Bank/resource links;
- asset availability;
- no broken internal links;
- accepted render/output identity where applicable.

## 26. Non-goals

LPAP-v1 does not:

- replace V3.1;
- replace `docs/method/PROTOCOL.md`;
- grant curriculum authority;
- create a second Question Bank taxonomy;
- require all six Cores to exist;
- define learner mastery from page visits;
- make automated checks publication authority;
- force one visual layout across Core roles;
- collapse duplicate, variant, and related records into one;
- require root-home featuring for every accepted product.

## 27. Acceptance principle

A candidate is not ready merely because it:

- renders;
- looks polished;
- passes CSS/layout tests;
- contains the expected number of cards/questions;
- has answers;
- has hints;
- is linked from Home.

The promotion packet should establish, to the depth appropriate for the selected profile, that:

- academic claims are correct;
- equations and solutions are independently supported;
- source fidelity is honest;
- completeness is reconciled against a real denominator;
- hints/scaffolding preserve the intended learner work;
- SVGs/diagrams represent the academic model correctly;
- interactions are causally and academically correct;
- the product fulfils its Core role;
- duplicate/variant/new identity is reconciled;
- layout/accessibility/runtime behavior is usable;
- navigation and deployment are coherent;
- the exact version presented to the Owner is the version proposed for publication.
