# Techniques T01–T15

These are design moves, not fields or counts to satisfy. The record location tells an author where a move is expressed; the candidate is a place to inspect it, not a claim of Owner blessing.

| ID | Move and reason | Record location | Candidate | Avoids |
|---|---|---|---|---|
| T01 | Put a decision the learner can make before an explanation. | microtopic elicitation or question stem/response | G-MATH Core1B; G-CORE2-R2 Core2 | AP-004, AP-005 |
| T02 | Make each construction unit practise one inferential decision. | `microtopics[].construction_units[]` | G-MATH Core1A | AP-015 |
| T03 | Show only the figure stage needed for the current decision. | `representations[].reveal_stages[]`, stage refs | G-MATH number line | AP-003, AP-005 |
| T04 | Draw the figure for this item and its current givens. | question `figure_refs`, representation asset | G-MATH question figure | AP-006, AP-007 |
| T05 | Move hints from orientation to representation to the first relation; keep each a question. | `hints[]` or `hint_ladder[]` | G-CORE2-R2 source rungs | AP-010, AP-011 |
| T06 | Name the tempting route and the observation that breaks it. | `failure_signal`, wrong-route notes | G-MATH Core1B | AP-009, AP-011 |
| T07 | Check a result by another route or an exact substitution, including an edge case. | `independent_checks`, answer check | G-MATH exact substitution | AP-013 |
| T08 | Write the family closure after the final transfer task is fixed. | `family_exposure.closure` from DESIGN-NOTE task arc | G-MATH Core2B | AP-008 |
| T09 | State what remains invariant and what decision has changed. | `transfer.invariant`, novelty reasoning | G-MATH Core2B | AP-009, AP-015 |
| T10 | Test a boundary where a memorised route might fail. | `boundary_test` | G-MATH Core1B | AP-012, AP-013 |
| T11 | Give a compact worked anchor its own question-aligned figure. | `compact_anchor`, asset refs | G-MATH Core1A | AP-006 |
| T12 | Reconstruct with changed givens so Core1B asks a new decision. | `elicitation.attempt.task` | G-MATH Core1B | AP-015 |
| T13 | Keep a printed key and an independent result separately named, including disagreement. | source inventory key, `readback[]`, answer relation | G-CORE2-R2's declared readback limit | AP-013 |
| T14 | Bridge only the prerequisite needed for the present inference. | `prerequisite_refs`, Core1 orientation | G-MATH Core1 | AP-015 |
| T15 | Keep source options and response form faithful while making commitment typed. | Core2 bank `options`, source format, `response` | G-CORE2-R2 Core2 | AP-005 |

See [INDEX.md](INDEX.md) for Core roles and [anti/](anti/) for the observed failure mechanisms. A technique is useful only if the actual task and source support it.
