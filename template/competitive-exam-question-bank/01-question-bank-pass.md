# PASS 1 — Canonical Competitive-Exam Question Bank

You are building the canonical competitive-exam question bank for Grade9V3.

Repository:
https://github.com/reallaksh19/Grade9V3

Your task is PASS 1 ONLY: create the question bank.
Do not create practice sets/exams yet.

## Scope

Physics:
1. Newton's Laws of Motion / NLM
2. Motion in 2D / Motion in a Plane — linear/projectile motion only; NO circular motion
3. Motion in 1D — relative motion only

Chemistry:
4. Redox Reactions
5. Some Basic Concepts of Chemistry / Mole Concept / Stoichiometry

## Target exam corpus

Prefer genuine previous-paper questions from:
- NEET UG and legacy AIPMT where verified;
- JEE Main and legacy AIEEE where verified;
- JEE Advanced and legacy IIT-JEE where verified.

Preserve the examination's actual historical identity. Do not relabel an IIT-JEE question as JEE Advanced or an AIEEE question as JEE Main merely for consistency.

## Source integrity is the first priority

For every claimed previous-paper question:

1. Locate a source record.
2. Prefer an official exam-organizer paper / answer key / official archive.
3. Secondary websites may be used for discovery but are not sufficient to declare a question VERIFIED when an authoritative source can reasonably be checked.
4. Record:
   - exam;
   - year;
   - date/session/shift where applicable;
   - original question number if available;
   - paper/section;
   - source URL/ref;
   - answer-key URL/ref where available;
   - last checked;
   - verification status.
5. Never invent an exam, year, shift, paper number or question number.
6. Never reconstruct a remembered question and label it original.
7. If exact source identity cannot be verified, do NOT mark ORIGINAL/PYQ VERIFIED.

## Provenance classes

Use only:

### A. PYQ_VERIFIED
Exact previous-paper identity has been independently verified.
This is eligible for genuine Core2 custody.

### B. PYQ_ADAPTED
Derived from a verified PYQ.
Preserve parent_ref and enumerate changed_fields exactly.
It must never display itself as the original exam question.

### C. SOURCE_UNVERIFIED
Candidate donor only.
Do not promote into learner-facing Core2.

Do not create fully AUTHORED questions unless the Owner explicitly authorizes it later.

## Important current-repo warning

Existing Chemistry donor registries such as:
- public/chemistry/redox/explorers/redox_reactions/jee_questions_data.js
- public/chemistry/some-basic-concepts/explorers/mole_concept/jee_questions_data.js

are discovery inputs, not automatic source authority.

The current repository audit explicitly records that some attributed source items/keys have not been independently matched against their claimed source.

Audit, deduplicate and verify them rather than copying their source claims.

## Core2 contract

Read current-main:
- Shared/roles/CORE2.md
- Shared/roles/CORE2A.md
- Shared/roles/CORE2B.md
- Shared/library/package.schema.json

A genuine sourced question must preserve:
- source_refs[];
- original_identifier;
- exact stem/subparts/options/conditions where repository rights/source policy permits;
- figure identity/caption where applicable;
- original hints if the source supplied them;
- source answer/key/rubric where available;
- origin/provenance.

Do not rewrite a source hint into a pedagogical hint.

Pedagogical scaffolds belong separately to Core2A/Core2B.

## Question analysis

For each accepted bank item, independently solve/check it and attach:

- topic;
- concept_bucket;
- family_ref or proposed family;
- primary capability;
- secondary capabilities;
- exam/source badge;
- question type;
- difficulty D1–D4;
- difficulty_score 0–10;
- difficulty_basis;
- expected_time;
- answer verification status;
- common wrong route / trap;
- reasoning_route where appropriate;
- stable crux move;
- independent check.

### Difficulty rubric

Concept/model selection       0–2
Representation translation    0–2
Reasoning-chain length        0–2
Algebra/computational load    0–2
Trap/exception sensitivity    0–2

Map:
- 0–2  -> D1
- 3–5  -> D2
- 6–7  -> D3
- 8–10 -> D4

Do not use the exam label itself as the difficulty score.

## Concept coverage

Use canonical repo capabilities/microtopics where they already exist.

Do not create story-specific capabilities simply because a question has a different surface context.

Create/propose a new family only when the invariant application demand is genuinely different.

For Core2B candidates, distinguish real transfer from same-family variation:
- model_choice;
- representation_translation;
- novelty;
- reasoning_steps.

Changing only numbers or story context is NOT transfer.

## Recommended concept buckets

### Newton's Laws / NLM
- body selection & FBD
- equilibrium / Newton I
- net force / Newton II
- Newton III pairs
- contact forces
- friction direction/state/limiting friction
- inclined planes
- connected bodies/string tension/pulleys
- accelerating-frame/pseudo-force only as JEE extension

### Motion in 2D / Plane
- vector components
- 2D constant acceleration
- shared x/y clock
- horizontal projectile
- oblique projectile
- event conditions/time of flight
- range/height/trajectory
- projectile from unequal heights
- model-validity / force-to-acceleration decisions
- NO circular motion

### Motion in 1D — relative motion only
- signed relative velocity
- same-direction catch/overtake
- opposite-direction meeting
- delayed starts
- finite-length/train problems
- separation/closing speed
- graph/piecewise relative motion

### Redox Reactions
- oxidation number
- structural exceptions
- oxidation/reduction identification
- oxidant/reductant
- reaction-dependent n-factor
- electron equivalence
- balancing
- disproportionation/comproportionation
- equivalent/redox stoichiometry

### Some Basic Concepts in Chemistry
- mole/particle scale
- molar/atomic/molecular mass
- stoichiometric mole ratios
- limiting/excess reagent
- purity/yield
- percentage composition
- empirical/molecular formula
- concentration terms
- mixtures/sequential stoichiometry
- gas stoichiometry where it genuinely belongs to this chapter

## Bank quality

Deduplicate:
- exact duplicates;
- same question repeated across coaching sites;
- trivial number-swapped variants;
- paper-language variants of the same source item.

Maintain a variant cluster / parent relationship.

For each topic produce a coverage matrix:

concept bucket
× exam source
× question type
× D1/D2/D3/D4
× provenance status.

Do not manufacture questions merely to make the matrix rectangular.

## Explicit badges / metadata

Every learner-facing question should be able to expose:
- provenance badge: PYQ VERIFIED / PYQ ADAPTED;
- exam badge: NEET / AIPMT / JEE MAIN / AIEEE / JEE ADVANCED / IIT-JEE;
- exact year/session where verified;
- difficulty badge D1–D4;
- concept bucket;
- question family;
- question type;
- expected time;
- answer verification status.

Internal metadata should additionally hold:
- primary capability;
- secondary capabilities;
- reasoning crux;
- common trap;
- independent check.

Do not expose the reasoning crux before the learner's attempt in strict exam mode.

## Suggested first bank size

Treat these as targets, never as sourcing quotas:

- NLM: ~60
- Motion in 2D: ~50
- 1D relative motion: ~35
- Redox: ~50
- Some Basic Concepts Chemistry: ~55

Total target: ~250 high-quality records.

Priority:
verified PYQ
>
adaptation of verified PYQ
>
leave coverage gap explicit

Never fabricate a citation just to reach a target count.

## Output / repository requirements

1. Put canonical question truth in subject/library data, not page-local JavaScript.
2. Preserve existing public/explorer banks as donor evidence until migrated; do not silently delete them.
3. Use existing schema/extensions where possible before proposing a new global schema field.
4. If badges need temporary storage, use a clearly namespaced exam-bank extension rather than editing Shared schema casually.
5. Add validation/tests for:
   - provenance honesty;
   - source-ref resolution;
   - duplicate IDs;
   - adaptation parent resolution;
   - difficulty metadata;
   - concept/family resolution;
   - answer verification;
   - no fabricated official identity.

Produce:
A. canonical bank changes;
B. source-acquisition ledger;
C. rejected/unverified-source report;
D. coverage matrix;
E. concept-bucket inventory;
F. test results;
G. PR linked to a dedicated question-bank issue.

Do NOT build final question sets in this pass.


## Machine-enforced activity contract

The prose above defines intent. The following files make the activity mechanically checkable:

- Shared/library/competitive-exam-bank.schema.json
- Shared/library/exam-source-verification.schema.json
- Shared/library/question-bank-run.schema.json
- Shared/library/question-bank-publication.schema.json
- Shared/tools/competitive_exam_bank.py
- docs/question-bank/pass1/run-manifest.json

Before claiming PASS, run:

```bash
python Shared/tools/competitive_exam_bank.py
python -m unittest tests.test_competitive_exam_bank_contract tests.test_competitive_exam_question_bank
```

The run is gate-driven. Do not skip directly to local question editing:

1. G0_SCOPE_FROZEN
2. G1_CORPUS_ENUMERATED
3. G2_SOURCE_AUTHORITY_CHECKED
4. G3_SOURCE_DISPOSITIONS_COMPLETE
5. G4_CANONICAL_ITEMS_VALID
6. G5_CONCEPT_REFS_RESOLVED
7. G6_ANSWERS_AND_DIFFICULTY_CHECKED
8. G7_COVERAGE_CLOSED
9. G8_PUBLICATION_CONTRACT_READY

A blocking gate in HOLD or FAIL forbids a PASS claim. Coverage reports and publication views are projections of canonical bank truth; they must not become independent sources of question truth.

```requires
bank.extensions.grade9v3:pass_scope                 PASS 1 scope is explicit
bank.extensions.grade9v3:generated_sets            no practice/final set assembly in PASS 1
question.extensions.grade9v3:provenance_class      accepted provenance is explicit
question.extensions.grade9v3:source_custody        verified parent identity and authority
question.extensions.grade9v3:analysis              difficulty, concept, trap and transfer analysis
question.answer.reasoning_route[]                   structured solution route
question.answer.crux_move_ref                       stable application crux
question.answer.check                               independent learner-runnable check
question.scaffolds[]                                authored support separate from source hints
run.gates[]                                         activity closure is gate-driven
run.publication_contract                            fixture-quality semantics are declared
```
