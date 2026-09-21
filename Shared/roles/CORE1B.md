# Core1B — open-ended conceptual reconstruction

Read [the shared role invariants](README.md) first.

## Purpose

Make the learner do the conceptual work that Core1A did for them, then give them everything needed to check and repair their attempt — without a tutor present.

The canonical crux is the same `microtopic.inferential_jump` used by Core1A. Core1B does not own a second version of the concept: it changes **who performs the inference and when it is revealed**.

## Coverage obligation

Core1B carries **the same intrinsic coverage as Core1A** for the bucket. Every concept Core1A constructs, Core1B elicits. It is not a lighter product, an optional extra, or a quiz appended to the lesson. If a concept is too hard to elicit, that is a design problem to solve, not a licence to drop it.

## Required shape

The self-tutor cycle, per microtopic:

1. **Predict** — pose the decision before revealing anything. The prompt must have a defensible answer the learner can commit to.
2. **Attempt** — the learner constructs, draws, discriminates or explains. State what they should produce.
3. **Reconstruct** — the correct construction, reached the way a learner would reach it, not the way an expert would summarise it.
4. **Diagnose** — the plausible wrong answer, named and tested by a specific question that separates it from the right one.
5. **Repair** — what to do having got it wrong, beyond being told the right answer.
6. **Boundary test** — a limiting case, reversal or edge condition that confirms understanding rather than recall.

## Closure without a tutor

Every prompt closes with a model response, a rubric, or explicit criteria for judging an open answer. Open-ended questions often have several valid responses; closure may legitimately be a rubric plus representative accepted and rejected answers, rather than one string.

## What Core1B must not do

- Be Core1A with the nouns changed, or with blanks punched into the worked text. Random deletion is not reconstruction; the omission must be semantically material — the thing the learner must actually decide.
- Defer closure to a human ("ask your teacher", "check with your class"). The product must stand alone.
- Silently reduce coverage relative to Core1A because elicitation is harder to author than exposition.
- Reveal the answer before the attempt is asked for. Attempt-first ordering is part of the product, though for self-study the answer stays accessible rather than locked.

## What this role requires the library to hold

The prose above is the authority for *meaning*. The block below is the authority for
*presence*: every path in it must resolve to a field the package schema can hold. It
cannot check the reverse — that everything the prose requires appears in the block.

Two of the six steps borrow from `misconceptions[]`, which already holds them for
Core1A. Diagnose and repair are the same claim in both products; duplicating them
under `elicitation` would create a second place for one truth, which is the defect
the authority gate exists to close. The other four steps have no home today.

```requires
microtopic.elicitation                          every concept Core1A constructs, Core1B elicits
microtopic.elicitation.predict.prompt           pose the decision before revealing anything
microtopic.elicitation.predict.defensible_answer  a defensible answer the learner can commit to
microtopic.elicitation.attempt.produces         state what they should produce
microtopic.elicitation.attempt.closure [derived] carried as the content it names rather than as the enum value
microtopic.elicitation.attempt.model_response   closure as one string, where one is right
microtopic.elicitation.attempt.rubric[]         closure as a rubric, where several answers are valid
microtopic.elicitation.attempt.accepted[]       representative accepted answers
microtopic.elicitation.attempt.rejected[]       representative rejected answers
microtopic.elicitation.reconstruct.route[]      the correct construction, reached the learner's way
microtopic.elicitation.reconstruct.route[].ask  not the way an expert would summarise it
microtopic.elicitation.reconstruct.route[].why_this_ask  [author] why this question rather than another here
microtopic.elicitation.reconstruct.differs_from_teaching_path  [author] the A/B claim, in a form a reviewer can check
microtopic.elicitation.boundary_test.prompt     a limiting case, reversal or edge condition
microtopic.elicitation.boundary_test.answer     every prompt closes without a tutor
microtopic.elicitation.boundary_test.confirms   confirms understanding rather than recall
microtopic.misconceptions[].wrong_idea          the plausible wrong answer, named
microtopic.misconceptions[].diagnostic_prompt   a specific question separating it from the right one
microtopic.misconceptions[].repair              what to do having got it wrong
```
