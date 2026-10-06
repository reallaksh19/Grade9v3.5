# Core Implementation Plan — Worksheet → Study Route → Learner Feedback

> Scope: Shared/core work only.
> Base architecture: PR #18, architecture/final-release-authority.
> Companion subject-content work: Issue #19.
> Concept architecture: docs/REVISED-SELF-STUDY-CONCEPT-MAP.md.
> Goal: implement the smallest practical core needed for worksheet-driven self-study for one learner.

## 0. Design constraint

Do not build a generalized learning platform.

Target workflow:

~~~text
worksheet / question set
        ↓
question → canonical capabilities
        ↓
prerequisite closure
        ↓
matrix/rung lookup + cross-matrix study order
        ↓
optional learner evidence
        ↓
study route
        ↓
attempt → targeted feedback → fresh retry
        ↓
observation → later review
~~~

The existing six Cores remain the learner-content products.

The new code is orchestration around existing content, not a seventh Core and not a second curriculum model.

---

# 1. Existing contracts to reuse

## 1.1 Canonical academic records

Shared/library/package.schema.json already provides capabilities, prerequisite_refs, success criteria, microtopics, primary_capability_ref, misconceptions, exit tasks, questions, primary/secondary capability refs, hints, transfer and repair metadata.

Do not duplicate these in the new worksheet/study-map schema.

## 1.2 Matrices

Shared/library/matrix.schema.json provides matrix/bucket identity, rungs, microtopic_ref, local ladder_position, support ladder and transfer rows.

Rule: ladder_position stays local to one matrix.

## 1.3 Capability topology

Shared/tools/capability_graph.py already provides subject_graph(), prerequisite_closure(), ladder_capabilities(), resolve_entry(), and topology validation.

Extend/reuse this rather than introducing another graph implementation.

## 1.4 Learner evidence

Existing contracts:

- Shared/library/learner-profile.schema.json
- Shared/library/observation.schema.json
- Shared/tools/learner_evidence.py

Keep the existing evidence/waiver distinction.

A parent estimate remains an owner routing input, not demonstrated mastery.

## 1.5 Existing authoring/release lifecycle

PR #10–#18 own planning, owner decisions, execution packets, source custody, authoring receipts, review authority and final release authority.

This implementation MUST NOT create a parallel lifecycle.

---

# 2. Work packages and merge order

Implement as small PRs in this order:

~~~text
C0  Baseline + fixtures
 ↓
C1  Worksheet mapping contract and resolver
 ↓
C2  Cross-matrix study-route planner + scope audit
 ↓
C3  Practical learner evidence/routing
 ↓
C4  Feedback/retry runtime
 ↓
C5  Minimal review scheduling
 ↓
C6  Pilot fixes only
~~~

Issue #19 may progress in parallel after C1 freezes the mapping contract.

---

# 3. C0 — Baseline and golden fixtures

## Purpose

Prove the post-PR18 tree before adding behavior and create realistic fixtures that every later phase must satisfy.

## Files

Create:

~~~text
tests/fixtures/study_route/
    physics-cross-matrix.worksheet.json
    mathematics-cross-matrix.worksheet.json
    prior-study-map.json
~~~

Fixture content must use canonical capability IDs that exist on the implementation branch.

If Issue #19 content is not yet available, use currently existing Mathematics/Physics capabilities and keep the fixture minimal.

## Required baseline checks

Run unchanged:

~~~text
python3 Shared/tools/learner_evidence.py --enforce
python3 Shared/tools/matrix_conformance.py --enforce
python3 Shared/tools/resolve_request.py --enforce
python3 Shared/tools/plan_request.py --audit --enforce
python3 Shared/tools/release_authority.py --audit --enforce
python3 -m unittest discover -s tests -p "test_*.py" -v
~~~

## Acceptance

- existing guardrails green;
- fixtures are transient worksheet/session data, not canonical questions;
- no academic content invented merely for tests.

---

# 4. C1 — Worksheet mapping contract and resolver

## Purpose

Represent the common real input: a worksheet/question set that needs to be mapped onto existing capabilities.

## 4.1 New schema

Create Shared/library/worksheet-map.schema.json.

This is a transient planning artifact, not a canonical academic package.

### Proposed minimum shape

~~~json
{
  "worksheet_id": "PT-2",
  "subject": "Mathematics",
  "source_note": "optional human-readable origin",
  "questions": [
    {
      "question_id": "Q13",
      "primary_capability_ref": "CAP-...",
      "secondary_capability_refs": ["CAP-..."],
      "mapping_basis": "MANUAL",
      "note": "optional short explanation"
    }
  ]
}
~~~

mapping_basis enum:

~~~text
MANUAL
AGENT_PROPOSAL
CANONICAL_QUESTION
~~~

### Constraints

- no learner weakness/strength;
- no knowledge percentage;
- no matrix/rung duplication;
- no copied prerequisite closure;
- no source-authority claim;
- arbitrary worksheet questions need not enter the canonical library.

## 4.2 New resolver

Create Shared/tools/study_map.py.

Initial functions:

~~~python
subject_index(subject, repo=REPO)
capability_locations(subject, repo=REPO)
validate_mapping(mapping, repo=REPO)
resolve_question(question_row, index)
resolve(mapping, repo=REPO)
readable(report)
~~~

subject_index() builds one subject-wide index:

~~~text
capability id
    → capability record
    → teaching microtopic(s)
    → matrix/rung location(s)
~~~

capability_locations() returns deterministic locations.

validate_mapping() reports at least:

~~~text
WORKSHEET_CAPABILITY_UNKNOWN
WORKSHEET_PRIMARY_CAPABILITY_MISSING
WORKSHEET_CAPABILITY_HAS_NO_TEACHING_LOCATION
WORKSHEET_CAPABILITY_AMBIGUOUS_LOCATION
~~~

Do not invent a mapping.

resolve() returns per question:

- primary capability;
- secondary capabilities;
- existing teaching locations;
- missing/unresolved refs;
- mapping basis.

## 4.3 Tests

Create tests/test_study_map.py.

Mandatory falsifiers:

1. unknown capability is reported;
2. known capability resolves to matrix/rung;
3. one question supports one primary + multiple secondary capabilities;
4. secondary capability is not treated as a prerequisite automatically;
5. worksheet question does not need to exist in the canonical question library;
6. local ladder positions are returned but never used globally.

## C1 acceptance

A fixture worksheet resolves deterministically:

~~~text
Q1 → CAP-A → Matrix X / R1
Q2 → CAP-B + CAP-C → Matrix Y / R2 and Matrix X / R3
~~~

with explicit gaps rather than guesses.

---

# 5. C2 — Cross-matrix study-route planner and coverage audit

## Purpose

Turn question capability demand into a logically ordered study route.

## 5.1 Reuse capability graph

Extend Shared/tools/capability_graph.py only where generic graph helpers are missing.

Preferred additions:

~~~python
prerequisite_closure_many(capabilities, caps)
topological_subset(capabilities, caps)
unknown_prerequisites(capabilities, caps)
~~~

Required behavior:

1. compute transitive prerequisite closure;
2. identify unknown prerequisite refs;
3. topologically order capabilities by prerequisite dependency;
4. preserve deterministic ordering among unrelated nodes;
5. never compare ladder_position across matrices;
6. explicitly report a cycle in the requested subset.

## 5.2 Study-route output

Create Shared/tools/study_route.py if keeping sequencing separate makes study_map.py simpler.

Output per capability:

~~~json
{
  "capability_ref": "CAP-X",
  "reason": "QUESTION_DEMAND",
  "required_by_questions": ["Q5", "Q10"],
  "locations": [],
  "depends_on": ["CAP-A"],
  "state": "RESOLVED"
}
~~~

Allowed reason values:

~~~text
QUESTION_DEMAND
PREREQUISITE
SYLLABUS_REQUIREMENT
DECLARED_EXTENSION
~~~

## 5.3 Optional syllabus overlay

Do not create a syllabus ontology.

Allow a simple optional list of canonical capability refs plus optional source_ref.

Output scope classes:

~~~text
QUESTION_AND_SYLLABUS
QUESTION_ONLY
SYLLABUS_ONLY
PREREQUISITE
DECLARED_EXTENSION
~~~

Do not claim question-derived scope is the complete syllabus.

## 5.4 Coverage audit

Create Shared/tools/study_scope_audit.py.

Forward check: every question-required capability must resolve to a canonical teaching location, explicit bridge/provider, or named unresolved gap.

Reverse check: every capability in a proposed study route must be justified by question demand, prerequisite, syllabus requirement or declared extension.

## 5.5 Tests

Create:

- tests/test_study_route.py
- tests/test_study_scope_audit.py

Falsifiers:

- prerequisite in another matrix orders before dependant;
- ladder position in another matrix does not affect order;
- diamond prerequisites appear once;
- unknown prerequisite remains explicit;
- cycle is reported;
- syllabus-only capability is labelled correctly;
- unrelated teaching is flagged as unjustified.

## C2 acceptance

A multi-matrix worksheet produces a human-readable route such as:

~~~text
Study first
  CAP-A — required upstream by Q5, Q10, Q14

Then
  CAP-B — Q3
  CAP-C — Q7

Then
  CAP-D — Q10
  CAP-E — Q14
~~~

with every capability linked to existing teaching locations.

---

# 6. C3 — Practical learner evidence and routing

## Purpose

Make initial parent estimates useful while allowing real evidence to supersede them.

## 6.1 Observation schema — minimal extension only

Update Shared/library/observation.schema.json.

Add optional fields:

~~~text
question_ref
session_ref
help
error_stage
~~~

Suggested help enum:

~~~text
NONE
HINT
WORKED_EXAMPLE
SOLUTION
UNKNOWN
~~~

Suggested error_stage enum:

~~~text
CONCEPT
SETUP
EXECUTION
CARELESS
UNKNOWN
~~~

Do not add mastery probability, confidence score, forgetting strength or difficulty vector.

## 6.2 Learner evidence resolver

Extend Shared/tools/learner_evidence.py with narrowly scoped helpers:

~~~python
load_observations(repo=REPO)
evidence_for_capability(profile, capability_ref, repo=REPO)
effective_state(profile, capability_ref, repo=REPO)
~~~

Practical evidence precedence:

~~~text
newer direct observation
    >
older diagnostic / study-map observation
    >
owner estimate
    >
unknown
~~~

Important: an owner estimate must never be converted into DEMONSTRATED.

## 6.3 Fix percentage routing

Current resolve_request.entry_from_position() rejects estimates that sit between exact ladder coordinates.

Change semantics for owner estimates only.

Recommended conservative rule:

~~~text
choose greatest existing ladder_position <= estimate
if estimate is below first rung, choose first rung
~~~

Example:

~~~text
ladder: 20, 55, 70, 85

10 → 20
40 → 20
60 → 55
75 → 70
95 → 85
~~~

Result provenance should make the nature of the decision explicit, e.g.:

~~~text
OWNER_ESTIMATE_CONSERVATIVE_FLOOR
~~~

It must not imply the selected rung is demonstrated.

Review both Shared/tools/resolve_request.py and Shared/tools/plan_request.py because planning reuses the entry logic.

## 6.4 Prior study-map import

Only if useful after the observation extension, create Shared/tools/import_study_observations.py.

Input rows such as:

~~~text
Q13 → CAP-X → "delta-y / delta-x roles unstable"
~~~

become normal observation JSON.

Do not create a parallel learner-state store.

## 6.5 Tests

Required cases:

- owner estimate between rungs routes conservatively;
- percentage never creates DEMONSTRATED state;
- direct observation supersedes owner estimate for routing;
- worked-solution exposure does not establish independent mastery;
- prior study-map row can become a normal observation.

## C3 acceptance

The learner may begin with only an approximate percentage, while subsequent routing naturally relies on actual capability observations.

---

# 7. C4 — Feedback and retry runtime

## Purpose

Provide useful self-study feedback without immediately revealing the solution.

## 7.1 New module

Create Shared/tools/feedback.py.

Response history stays outside canonical questions/microtopics.

### Proposed request

~~~json
{
  "question_ref": "Q-...",
  "response": "...",
  "reasoning": ["optional learner steps"],
  "attempt_number": 1,
  "previous_help": []
}
~~~

For arbitrary non-canonical worksheet questions, allow the caller to supply the resolved capability mapping and an evaluation result/rubric separately.

## 7.2 Evaluation boundary

First version supports:

1. deterministic/objective evaluation where existing answer structure permits;
2. canonical rubric criteria;
3. caller-supplied evaluated outcome for free-form cases requiring human/LLM judgement.

The feedback engine orchestrates what to reveal next. It does not pretend every proof/free-form answer can be graded deterministically.

## 7.3 Failure representation

Return at least:

~~~json
{
  "result": "INCORRECT",
  "failed_capability_ref": null,
  "error_stage": "UNKNOWN",
  "misconception_index": null,
  "diagnostic_evidence": null,
  "next_action": "HINT"
}
~~~

Never invent failed_capability_ref when evidence cannot distinguish among several required capabilities.

A misconception index is only a hypothesis selector. Misconception-specific repair requires
the canonical diagnostic prompt plus an observed response, an explicit
`CONFIRMED | REFUTED | INDETERMINATE` evaluator conclusion, and a non-empty basis.
Only `CONFIRMED` may enter the misconception-specific repair path.

## 7.4 Feedback escalation

Small state machine:

~~~text
ATTEMPT_1
  wrong
    → HINT_1 directional
      → RETRY

wrong again
    → HINT_2 structural
      → RETRY

wrong again
    → DIAGNOSE with canonical probe
      → INDETERMINATE / REFUTED: stay in DIAGNOSE
      → CONFIRMED with recorded response + basis
        → REPAIR
      → Core1B/Core1A
      → FRESH_VERIFY
~~~

Reuse existing:

- question.hints[];
- hint.reveals;
- microtopic misconceptions;
- diagnostic_prompt;
- repair;
- Core2B repair_ref;
- microtopic exit_task.

### Anti-spoiler rule

Do not emit an ANSWER-revealing hint before final escalation.

For transfer questions, do not reveal the exact model choice defining the transfer task unless intentionally moving into repair mode.

## 7.5 Fresh verification

Initial selection order:

1. another canonical question with the same primary capability and not previously attempted;
2. suitable microtopic exit task;
3. return VERIFICATION_ITEM_REQUIRED.

Do not fabricate a question merely to keep the state machine moving.

## 7.6 Observation output

After a meaningful attempt, produce an observation payload using the C3 schema.

Writing can remain an explicit caller action initially; avoid hidden file mutation.

## 7.7 Tests

Create tests/test_feedback.py.

Falsifiers:

- first wrong answer does not reveal full solution;
- second-stage hint is more informative than first;
- ANSWER hint is not emitted prematurely;
- transfer model choice is protected;
- misconception repair routes to canonical content;
- ambiguous failure remains UNKNOWN;
- independent fresh verification can produce DEMONSTRATED;
- solution-viewed success cannot produce independent DEMONSTRATED.

## C4 acceptance

One canonical topic can run:

~~~text
attempt
→ wrong
→ targeted hint
→ retry
→ repair if needed
→ fresh check
→ observation
~~~

without a live tutor selecting each step.

---

# 8. C5 — Minimal review scheduling

## Purpose

Add delayed retrieval with a tiny deterministic policy.

Create Shared/tools/review_schedule.py.

Pure function first:

~~~python
next_review(outcome, when) -> date
~~~

Initial policy:

~~~text
INCORRECT             +1 day
CORRECT_WITH_HINT     +3 days
CORRECT_INDEPENDENT   +7 days
TRANSFER_INDEPENDENT  +14 days
~~~

Use fixed intervals initially for deterministic behavior.

Scheduling must not change academic mastery/evidence by itself.

Persistence under Learners/review/ should be added only if actual workflow needs it.

## Tests

Create tests/test_review_schedule.py.

Check deterministic dates and reset after failed delayed retrieval.

---

# 9. C6 — Real worksheet pilot

## Mathematics pilot

Use one real worksheet spanning more than one matrix and resembling the existing question → study map example.

Verify:

- question mapping;
- prerequisite route;
- prior learner evidence;
- sensible starting emphasis;
- no learner-specific state in matrices.

## Physics pilot

Use one worksheet spanning at least two existing Physics matrices.

Verify:

- canonical capability reuse;
- cross-matrix prerequisites;
- hints/misconceptions/repair routing.

## Change rule after pilot

Every architecture change proposed after pilot must carry:

~~~text
observed failure
→ smallest fix
→ falsifier test
~~~

No speculative platform expansion.

---

# 10. CI integration

Add guardrails incrementally.

After C1/C2 are stable, add:

~~~text
python3 Shared/tools/study_scope_audit.py --enforce
~~~

C3 should preferably extend the existing learner evidence gate rather than add overlapping global gates.

Feedback and scheduling should primarily be unit-tested initially.

Regenerate docs/architecture-manifest.json whenever new Shared components are committed.

---

# 11. Expected file changes

## New

~~~text
Shared/library/worksheet-map.schema.json
Shared/tools/study_map.py
Shared/tools/study_route.py
Shared/tools/study_scope_audit.py
Shared/tools/feedback.py
Shared/tools/review_schedule.py

tests/test_study_map.py
tests/test_study_route.py
tests/test_study_scope_audit.py
tests/test_feedback.py
tests/test_review_schedule.py
~~~

Only if proven useful:

~~~text
Shared/tools/import_study_observations.py
Shared/library/review-schedule.schema.json
~~~

## Modified

~~~text
Shared/library/observation.schema.json
Shared/tools/capability_graph.py
Shared/tools/learner_evidence.py
Shared/tools/resolve_request.py
Shared/tools/plan_request.py
.github/workflows/guardrails.yml
docs/architecture-manifest.json
~~~

Avoid changing these unless a concrete falsifier proves they cannot support the workflow:

~~~text
Shared/library/package.schema.json
Shared/library/matrix.schema.json
Shared/roles/*
~~~

---

# 12. Core/content integration contract

Issue #19's content agent may rely on these facts after C1:

1. worksheet mapping names canonical capability IDs;
2. a question may have one primary + several secondary capabilities;
3. prerequisite closure is derived from capability records;
4. matrices remain durable and learner-independent;
5. arbitrary worksheets do not need to become canonical questions.

The content agent must not need C3/C4 to finish matrices.

---

# 13. PR slicing

Prefer small reviewable PRs.

### Core PR A

~~~text
C0 + C1
worksheet fixtures
worksheet mapping schema
study_map resolver
tests
~~~

### Core PR B

~~~text
C2
cross-matrix route
scope audit
tests
~~~

### Core PR C

~~~text
C3
learner evidence extensions
practical percentage routing
tests
~~~

### Core PR D

~~~text
C4
feedback/retry runtime
tests
~~~

### Core PR E

~~~text
C5 + pilot support
minimal review scheduler
pilot fixtures/fixes
~~~

Do not build another long 200-commit mixed branch.

---

# 14. Definition of done

Core implementation is sufficient for real use when a caller can:

1. submit a worksheet map;
2. see each question's capability mapping;
3. see unresolved mappings explicitly;
4. obtain prerequisite closure across matrices;
5. receive a deterministic study order;
6. optionally provide a rough estimate or prior observations;
7. receive a conservative starting route;
8. submit an attempt;
9. receive non-spoiling progressive feedback;
10. route to an existing repair;
11. verify on a fresh available task;
12. produce a new learner observation;
13. receive a deterministic later review date.

Anything beyond this requires evidence from actual use.

---

# 15. First implementation action

The first code PR implements only C0 + C1.

Do not begin learner-evidence or feedback code until worksheet → capability → matrix resolution works against at least one realistic fixture.

Dependency order:

~~~text
first know WHAT the question demands
then decide WHERE to study it
then personalize HOW the learner studies it
then improve feedback
~~~
