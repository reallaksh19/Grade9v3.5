# Core2A — purpose-adjusted practice with complete solutions

Read [the shared role invariants](README.md) first.

## Purpose

Teach the learner to solve a **familiar question-family demand** by making the application reasoning route explicit and supportable. Core2A is supported application: the learner is not expected to get there unaided.

The canonical crux is the question-specific application reasoning move. Where authored, `question.answer.reasoning_route[]` holds the structured route and `question.answer.crux_move_ref` identifies the stable move that unlocks the problem.

## Required content

Per question:

- **Exact source identity** preserved (see [Core2](CORE2.md)) and visible to the learner, including provenance class.
- **Complete solution breakdown**: not the answer and not a summary, but the sequence of reasoning moves and transformations, with the crux move made explicit rather than glossed.
- **Pedagogical scaffolds**, where useful, separate from source/question hints. There is no required scaffold count. Each authored scaffold may declare its cognitive function (`REPRESENT | CONNECT | EXECUTE`), reveal depth, target reasoning move, and optional canonical visual stage.
- **A check** the learner can run on their own result — a limiting case, reversal, independent recomputation, or whatever the subject adapter qualifies.
- **A figure** where the geometry, structure or representation carries meaning, bound to the working rather than placed beside it.
- **Declared family and exposure role**, so that reuse across products is auditable.

## Practice routing

Core2A consults **learner knowledge or an explicit owner waiver** — the only inputs of their kind in the six products, shared with Core2B.

- With scoped capability evidence: compare required capabilities against demonstrated, uncertain and missing ones. Do not infer mastery of a prerequisite from a high aggregate score.
- With an owner waiver and unknown knowledge: follow the owner's requested demand and support. Keep UNKNOWN visible. Make no personalised-readiness claim.
- With neither: personalised acceptance is held. Study products proceed unaffected.

An owner asking for the simplest questions stays effective even when an estimate is high. A high estimate with one missing critical prerequisite triggers a bridge or a scoped hold — never a silent assumption of readiness.

## What Core2A must not do

- Claim measured fit, calibration or mastery from a percentage, a routing decision or a successfully generated book.
- Hide the solution behind a reveal that the self-study learner cannot open.
- Present a same-family variant as new transfer. That belongs to [Core2B](CORE2B.md), and only when the demand genuinely changes.

## What this role requires the library to hold

The prose above is the authority for *meaning*. The block below is the authority for
*presence*: every path in it must resolve to a field the package schema can hold. It
cannot check the reverse — that everything the prose requires appears in the block.

```requires
question.source_refs[]                   exact source identity preserved and visible
question.original_identifier             including the original question number
question.origin                          including provenance class
question.answer.reasoning[]              legacy prose fallback for the sequence of decisions
question.answer.reasoning_route[]        structured sequence of application reasoning moves, when authored
question.answer.crux_move_ref            stable id of the question-specific crux move, when authored
question.answer.difficult_move           legacy fallback index while older records migrate
question.answer.check                    a check the learner can run on their own result
question.scaffolds[]                     pedagogical support, where useful; no required count
question.scaffolds[].support_kind        what cognitive help is provided
question.scaffolds[].supports_move_ref   the reasoning move the scaffold targets
question.figure_refs[]                   a figure where the representation carries meaning
question.family_ref                      declared family, so reuse is auditable
question.exposure[].core                 declared exposure role, so reuse is auditable
question.exposure[].role [derived] mapped to the block's exposure_role, which is the learner-facing name
representation.scene_instances[].question_ref  bound to the working rather than placed beside it
```
