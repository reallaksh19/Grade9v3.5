# Core2B — supported application and transfer

Read [the shared role invariants](README.md) first.

## Purpose

Assess whether the learner can carry an established capability into a situation that demands a decision they have not been handed — a different model choice, representation translation, novel mapping, or longer reasoning chain.

Core2B is **not Core2A with less support**. Its defining property is a specified changed demand, and the learner decision created by that change must remain protected before the attempt.

For new or materially revised transfer items, that claim is made executable rather than left implicit: the changed decision is a `DECIDE` move in `question.answer.reasoning_route[]`, named by `question.transfer.protected_move_ref`. Existing unstructured transfer items are migration debt; their labels are not upgraded merely because they predate the structured contract.

## What makes a Core2B task

A task belongs here only if it changes a **specified** dimension of demand relative to prior exposure. State which one:

| Dimension | The learner must now |
|---|---|
| `model_choice` | Decide which relation or model applies, rather than being told |
| `representation_translation` | Choose or translate the representation before calculating |
| `novelty` | Map an unfamiliar situation onto a known structure |
| `reasoning_steps` | Chain steps that were previously separated |

**A cover story is not a dimension.** The same question with different numbers, or the same structure with a different object in it, is same-family practice and belongs in Core2A. Declaring it `NEW_TRANSFER` does not make it transfer; the exposure audit exists precisely to dispute that claim, and a flagged pair is resolved by a reviewer, not by the author's own label.

## Required content

- **Graduated pedagogical scaffolds** that support without collapsing the demand. Source/question hints remain custody data; practice support belongs in `question.scaffolds[]`. If `transfer.protected_move_ref` is declared, no pre-attempt scaffold or visual stage may hand over that move.
- **Full answer and rubric**, including what a good justification contains, not only the final result.
- **A repair route** for the predictable failure, pointing back to the specific Core1A/Core1B construction that addresses it.
- **An explicit statement of the changed demand** relative to prior exposure, so the reviewer can check the transfer claim.
- **Exposure lineage**: what the learner has already seen that this builds on. When an adapted transfer has a question parent, that parent belongs in the lineage so the changed demand can be compared pairwise.
- **Established capability continuity**: the transfer may vary the demand, not silently add an untaught capability or model. A capability absent from the prior-exposure/prerequisite closure is upstream teaching work.
- **Pre-attempt protection across channels**: source/question hints remain custody data, but learner-time support shown before an attempt must not disclose the protected decision. METHOD/ANSWER support belongs after commitment unless a reviewer has established that it cannot collapse the changed demand.

## Practice routing

Same inputs as [Core2A](CORE2A.md) — scoped capability evidence or an explicit owner waiver — with the same prohibitions on manufactured diagnosis. Transfer tasks in particular must not be routed to a learner on the assumption that a high aggregate estimate implies the prerequisites are in place.

## What Core2B must not do

- Introduce new scientific content under a transfer label. A task requiring a model the learner was never taught is a coverage gap, not a transfer assessment.
- Depend on a live tutor for closure.
- Treat low measured similarity as evidence of genuine transfer. Similarity is a screening signal; transfer is a claim about demand, and it is established by review.

## What this role requires the library to hold

The prose above is the authority for *meaning*. The block below is the authority for
*presence*: every path in it must resolve to a field the package schema can hold. It
cannot check the reverse — that everything the prose requires appears in the block.

```requires
question.transfer.dimension              state which dimension of demand changes
question.transfer.statement              an explicit statement of the changed demand
question.transfer.builds_on[]            exposure lineage: what the learner has already seen
question.transfer.protected_move_ref      the changed decision that pre-attempt help must not hand over, when authored
question.scaffolds[]                     graduated pedagogical help, separate from source/question hints
question.scaffolds[].reveals             disclosure depth of that help
question.scaffolds[].supports_move_ref   the reasoning move the scaffold targets
question.answer.summary                  full answer
question.answer.rubric[]                 and rubric
question.answer.rubric[].criterion       what a good justification contains
question.answer.rubric[].evidence_of     not only the final result
question.repair_ref                      a repair route pointing back to the Core1A/Core1B construction
question.origin                          a task requiring an untaught model is a coverage gap
```
