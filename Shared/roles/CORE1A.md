# Core1A — declarative detailed teaching

Read [the shared role invariants](README.md) first.

## Purpose

Construct the bucket's concepts for a learner working alone, with the reasoning completed and visible. Core1A is where a difficult inference gets justified rather than asserted.

The canonical crux is `microtopic.inferential_jump`. Core1A and Core1B share that same conceptual truth: Core1A **reveals the completed construction**, while Core1B **elicits the construction before reconstruction/repair**.

## Required content

- **Declared conventions first.** Whatever the subject adapter says must be fixed before quantities can be read — axes and signs, reference states, domains and excluded values, species and phase — is declared before any of it is used.
- **Constructed concepts, not stated conclusions.** For each microtopic in the bucket: the entry capability assumed, the exact inference being learned, why each step is valid, and the observable exit criterion.
- **Representation bridges.** The same idea carried across picture, words and symbols, with the correspondence made explicit in both directions. A figure that sits beside the working without being bound to it is decoration.
- **Completed worked examples**, with the reasoning shown in full, including the steps a confident author would skip. These are conceptual anchors whose job is to illuminate the inferential jump; practice-family coverage and application-route training belong in Core2A.
- **The plausible wrong path**, named, with a diagnostic that would expose it and the repair that fixes it. A misconception the learner never hears is a misconception they keep.
- **Checks the learner can run alone** — limiting cases, reversals, independent recomputation, conservation or domain tests as the subject provides.

## Depth control

Depth follows the subtopic's **intrinsic badge**, which is an authoring judgement about the concept, not a measurement of any learner:

| Badge | Expectation |
|---|---|
| HARD | Research-informed enrichment required; the difficult transitions get explicit, separate treatment |
| MEDIUM | Research-informed enrichment required; fewer irreducible transitions than HARD |
| EASY | Follows the owner's no-enrichment-search instruction |

Page-count examples circulating in earlier design notes express possible depth; they are neither quotas nor ceilings. Use the length the teaching needs and explain a large deviation.

**Depth is invariant under learner knowledge.** A high knowledge estimate is not permission to delete a HARD bucket's explanation; at most it justifies a navigation pointer past it.

## What Core1A must not do

- Consult a knowledge percentage or waiver to decide what to teach. That is Core2A/Core2B's input, not this one's.
- Leave an embedded prompt unclosed (see the shared closure invariant).
- Present an author's own construction as source-supported without the source binding, or a source's claim as the author's construction.

## What this role requires the library to hold

The prose above is the authority for *meaning*. The block below is the authority for
*presence*: every path in it must resolve to a field the package schema can hold. It
cannot check the reverse — that everything the prose requires appears in the block.

```requires
bucket.conventions[]                     declared before any of it is used
bucket.conventions[].statement           axes and signs, reference states, domains, species and phase
microtopic.entry_assumptions[]           the entry capability assumed
microtopic.inferential_jump              the exact inference being learned
microtopic.teaching_path[]               constructed concepts, not stated conclusions
microtopic.teaching_path[].action        the step itself
microtopic.teaching_path[].why_valid     why each step is valid
microtopic.teaching_path[].source_ref    an author's construction is not source-supported without the binding
microtopic.exit_task.prompt              the observable exit criterion
microtopic.exit_task.answer              no embedded prompt left unclosed
question.answer.reasoning[]              completed worked examples, the reasoning shown in full
question.exposure[].core                 a worked example is a question this product exposes
microtopic.misconceptions[].wrong_idea   the plausible wrong path, named
microtopic.misconceptions[].diagnostic_prompt   a diagnostic that would expose it
microtopic.misconceptions[].repair       and the repair that fixes it
relation.checks[]                        checks the learner can run alone
microtopic.exit_task.answer.check        one the learner runs on their own result
microtopic.intrinsic_badge               depth follows the subtopic's intrinsic badge
microtopic.research_contribution         [author] HARD and MEDIUM require research-informed enrichment
representation.scene_instances[]         the same idea carried across picture, words and symbols
representation.scene_instances[].microtopic_ref  a figure not bound to the working is decoration
representation.correspondence[]          the correspondence made explicit in both directions
representation.correspondence[].symbol   the symbol side of the bridge
representation.correspondence[].element  the picture side of the bridge
representation.correspondence[].in_words the words side of the bridge
```
