# Core1 — compact basic notes and semantic orientation

Read [the shared role invariants](README.md) first.

## Purpose

Give the learner a short, correct orientation to the bucket: what the objects are, what the governing relations say, what the conditions are, and where the harder work lives. Core1 is the map, not the journey.

## Required content

- The named objects and quantities of the bucket, with the conventions needed to read them (declared axes, sign conventions, reference states, units — whatever the subject adapter specifies).
- The governing relations in their canonical form, each with its meaning in words and the conditions under which it applies.
- The worked anchor values, if the bucket has one, stated compactly.
- Explicit pointers to which transitions are intrinsically hard, so the learner knows where Core1A/Core1B will spend their effort.
- Scope statement: what this bucket covers, and what is deliberately excluded or carried as labelled extension.

## Relationship to upstream material

Where a valid frozen Core1 already exists, Core1 **preserves** it: it is instantiated or referenced, not rewritten. Defects found in frozen material are reported separately rather than silently corrected in place, so that the original and the correction remain distinguishable.

Where no frozen Core1 exists, Core1 may be authored directly from inspected teaching sources and canonical concept records, particularly for the first-stage route when no question bank is available. Record its own source basis, scope, uncertainty and review status; a future Core1A is not a prerequisite for researching or authoring these notes. Later construction work can reveal improvements to the same canonical orientation.

Core1 may also be condensed from the reviewed Core1A content for the same bucket. It then carries Core1A's review status — condensing reviewed teaching does not create independently reviewed notes, and condensing unreviewed teaching certainly does not.

## What Core1 must not do

- Replace teaching. A compact note that asserts a difficult inference without construction is an orientation failure, not a brief lesson.
- Assert curriculum authority it does not have. If the bucket's board/grade mapping is a candidate rather than an established binding, the note says so.
- Accumulate. Core1 grows by the subtopic's genuine conceptual surface, not by absorbing material that belongs in Core1A.

## What this role requires the library to hold

The prose above is the authority for *meaning*. The block below is the authority for
*presence*: every path in it must resolve to a field the package schema can hold, so
that a requirement stated here can never quietly lose its home. It does not, and
cannot, check the reverse — that everything the prose requires appears in the block.
That stays a reviewer's duty.

```requires
bucket.title                             a short, correct orientation to the bucket
bucket.conventions[]                     the conventions needed to read the objects
bucket.conventions[].statement           declared axes, sign conventions, reference states
datum.value                              the worked anchor values, if the bucket has one
datum.symbol                             stated compactly
bucket.primary_representation_ref        [derived] carried as the figure it names, not as the id
bucket.scope.covers                      what this bucket covers
bucket.scope.excluded[]                  what is deliberately excluded
bucket.scope.extension_refs[]            what is carried as labelled extension
bucket.curriculum_mappings[].mapping_status  a candidate rather than an established binding, said so
bucket.status                            it then carries Core1A's review status
datum.meaning                            the named objects and quantities of the bucket
datum.unit                               units -- whatever the subject adapter specifies
relation.expression [derived] typeset as relation.mathml, which is the same expression
relation.meaning                         each with its meaning in words
relation.conditions[]                    the conditions under which it applies
microtopic.intrinsic_badge               which transitions are intrinsically hard
microtopic.badge_reason                  so the learner knows where Core1A/Core1B spend effort
```
