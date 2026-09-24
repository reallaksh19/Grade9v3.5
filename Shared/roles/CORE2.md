# Core2 — source questions, hints, identity and answers

Read [the shared role invariants](README.md) first.

## Purpose

Hold the bucket's question custody: the actual source questions, in their original form, each with its identity, its ladder of hints, and an answer. Core2 is where assessment demand enters the system as evidence rather than as assumption.

## Required content

Per question:

- **Exact original identity**: source identifier, original question number, stem, subparts, options and conditions, preserved verbatim. Figures and their captions survive; an unadapted original figure is held rather than dropped.
- **Ladder hints**, where the source supplies them, in their original ordering. These remain custody data in `question.hints[]`; downstream pedagogical support is authored separately in `question.scaffolds[]` rather than rewriting the source ladder.
- **An answer**, with whatever working or rubric the source provides.
- **Provenance class**: supplied original, adapted (with parent identity and the exact changed fields), or authored.

## The custody rule

Core2 is a preservation product. Its contents are **not** generated. If a bucket has no frozen or authorised question corpus, Core2 is `HELD` and says so plainly, naming what acquisition would close the hold. It is never closed by:

- inventing an official exam, year, paper or question number;
- promoting an author-created review corpus to "frozen" status;
- reconstructing a remembered question and presenting it as sourced.

An author-created review corpus may legitimately exist and may feed Core2A/Core2B practice, with truthful authored provenance throughout. It does not become Core2 by being useful.

## Rights-aware preservation

Core2 preserves the **assessment demand exactly**. When repository rights/source policy permit, source wording and demand-bearing media are stored verbatim. When they do not, the exact source item may remain externally referenced only when custody is pinned to retained source bytes, a precise item locator and an explicit component-by-component verification record. Reconstructed wording is never presented as an original.

For source-derived canonical questions, `question.extensions.source_custody` is the durable question-level proof. It binds the question to the acquisition/resource digest, records the exact source item locus, distinguishes embedded-verbatim from external-reference custody, and records whether identity, stem, subparts, options, conditions, figures/captions, source hints and source answer/rubric were preserved, absent in the source, externally verified, or remain unresolved. An unresolved proof may remain candidate evidence; it cannot establish reviewed Core2 custody.

This proof complements rather than replaces digest-bound review authority: acquisition proves the bytes, question custody proves what was compared, and promotion proves who independently accepted the resulting canonical record.

## Downstream consequence

Core2A and Core2B depend on Core2's custody for any claim about assessment demand, exposure or transfer boundaries. While Core2 is held, those products may still be built from authored candidates, but their acceptance inherits the hold: practice can be produced, and it can be honest, but it cannot claim to reflect the real assessment surface of the bucket.

## What this role requires the library to hold

The prose above is the authority for *meaning*. The block below is the authority for
*presence*: every path in it must resolve to a field the package schema can hold. It
cannot check the reverse — that everything the prose requires appears in the block.

```requires
question.source_refs[]                   source identifier, preserved verbatim
question.original_identifier             original question number, preserved verbatim
question.stem                            stem, preserved verbatim
question.subparts[]                      subparts, preserved verbatim
question.options[]                       options, preserved verbatim
question.conditions[]                    conditions, preserved verbatim
question.figure_refs[]                   figures survive; an unadapted original is held
resource.caption                         and their captions survive
resource.access_status                   [author] held rather than dropped
question.hints[]                         ladder hints, in their original ordering
question.answer.summary                  an answer, for every question held
question.answer.reasoning[]              with whatever working the source provides
question.answer.rubric[]                 or rubric the source provides
question.origin                          supplied original, adapted, or authored
question.adaptation.parent_ref           adapted, with parent identity
question.adaptation.changed_fields[]     and the exact changed fields
issue.classification                     Core2 is HELD and says so plainly
issue.affected_refs[]                    which bucket the hold is on
issue.next_action                        naming what acquisition would close the hold
```
