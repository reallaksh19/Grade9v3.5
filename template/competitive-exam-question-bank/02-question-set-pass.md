# PASS 2 — Exam Question Set Builder

You are now performing PASS 2.

PASS 1 canonical exam question bank is the only allowed question source.

Do not research new questions.
Do not invent new questions.
Do not create an adaptation inside a set.

If a required item does not exist in the bank, record BANK_GAP and return that requirement to Pass 1.

## Goal

Create reusable question sets for:

1. Newton's Laws of Motion
2. Motion in 2D / Plane — no circular motion
3. 1D relative motion
4. Redox Reactions
5. Some Basic Concepts of Chemistry

The sets must serve NEET, JEE Main and JEE Advanced preparation while remaining honest about provenance.

## Set types

For each topic create:

### A. CONCEPT DRILL
Grouped by concept bucket.
Visible difficulty and concept badges.

### B. NEET PRACTICE
Primarily verified NEET/AIPMT demand where available.
D1–D3 emphasis.
Do not claim to reproduce the current official exam pattern unless that pattern is separately verified.

### C. JEE MAIN PRACTICE
Verified JEE Main/AIEEE demand where available.
D2–D3 emphasis with selected D4.

### D. JEE ADVANCED PRACTICE
Verified JEE Advanced/IIT-JEE demand where available.
Higher model-selection, representation and multi-step demand.
Include source question types faithfully.

### E. MIXED MASTERY
Deliberately mixes buckets and removes obvious topic-order cues.

Do not force an exam source into a set when the bank lacks verified material.

## Question selection rules

Every set must:
- draw only by question ID from the canonical bank;
- avoid duplicate/near-duplicate variants in the same set;
- cover multiple concept buckets;
- contain an intentional difficulty profile;
- preserve original question type;
- preserve provenance badge;
- preserve source citation;
- preserve answer/key identity;
- declare total expected time.

For browse/drill mode show:
- difficulty;
- concept bucket;
- source/exam;
- provenance.

For exam simulation mode hide before submission:
- reasoning crux;
- capability refs;
- common trap;
- full family explanation;
- solution route.

Concept/difficulty badges may also be hidden in strict mock mode so they do not cue the method.

## Set blueprint

Every set must have a machine-readable blueprint containing:

- set_id
- topic_scope[]
- target_exam
- question_refs[]
- concept_bucket_distribution
- difficulty_distribution
- question_type_distribution
- verified_pyq_count
- adapted_count
- estimated_time
- coverage_gaps[]
- duplicate_check
- answer_key_ref
- solution_pack_ref

## Solutions

After the exam section provide:
- answer key;
- full solution;
- reasoning route;
- visibly marked key decision/crux;
- independent check;
- common trap;
- provenance/citation.

Do not expose these before the attempt in strict exam mode.

For Core2A:
show progressively stronger support around a familiar application reasoning move.

For Core2B:
do not reveal the protected changed decision before the learner commits.

## Quality audit

For every generated set report:

- bucket coverage;
- D1/D2/D3/D4 counts;
- verified PYQ / adapted counts;
- NEET/JEE source distribution;
- question-type distribution;
- repeated-family concentration;
- estimated time;
- missing-bank gaps.

Reject a set when:
- one bucket dominates accidentally;
- the same template appears repeatedly;
- a supposed JEE Advanced set is only numerically harder same-family work;
- a transfer item exposes its model choice;
- an adapted item is displayed as an official PYQ;
- any citation cannot resolve back to Pass 1.

Create the set manifests and tests, then open a separate PR for question-set assembly.

Do not modify source question wording or provenance in Pass 2.
