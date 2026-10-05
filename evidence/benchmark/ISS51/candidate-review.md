# ISS51 candidate review

This is first-run **CANDIDATE** evidence. Quality-gate status is FAIL; the exact inherited layout blocker is preserved rather than waived.

## Hardest target

Q8 is the hardest target: degree-bounded polynomial identity via the difference polynomial and the zero-polynomial exception, primary demand JUSTIFY, band D4. Core1A teaches a changed degree-one case with a four-stage h=f-g construction. The question-specific repair requires a learner to write a changed-case prediction and reason before comparison opens.

## Exact-render finding

The governed render contains all ten Core2 questions in source order and only the requested Core1A/Core2 roles. The Q8 source stem is not reused as the Core1A worked anchor; its changed case, four-stage bridge and return-to-question repair are present.

## Builder improvement proposal after inspection

**BLUEPRINT_DRIVEN_LAYOUT_CONSISTENCY** should make the layout contract single-source and testable. The pinned Core1A blueprint says `expanded: SINGLE_PANE` while also carrying 0.6/0.4 fractions; `render_core.layout_css()` emits split columns only for `STAGE_SUPPORT`; the shared quality rule `PAGE-STAGE-SUPPORT` nevertheless requires a split for Core1A. This three-way disagreement is the sole blocking quality finding.

Resolve the intended Core1A layout in the blueprint first, then derive renderer CSS and audit expectations from that same policy. If Core1A is intentionally single-pane, PAGE-STAGE-SUPPORT/audit must not require split columns. If it is intentionally stage/support, set the blueprint to STAGE_SUPPORT and let the existing renderer emit its declared fractions. Add a contract test covering every role: blueprint expanded mode -> emitted CSS -> browser expectation. This is a shared-authority change; candidate records need no migration.

A polynomial-specific widget is **not required** for this candidate. Existing staged SVG construction plus the shared commit-before-compare repair supports Q8 without exposing the protected source answer.
