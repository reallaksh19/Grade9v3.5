# ISS33 work report — independent agent A, v2

Status: **CANDIDATE / implementation in progress**  
Branch: `candidate/issue33-agent-a-v2`  
Pinned source snapshot: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`  
Partner-output inspection: **NONE**. Issue #34 has not been fetched or read.

## Mission and protocol
Produce governed Core2 + Core1A learner HTML for the ten owner-supplied hybridisation questions, plus QRT evidence, hardest-target interaction and an evidence-based builder decision. The sole renderer remains `Shared/tools/render_core.py`; generated learner HTML will not be hand-edited. Applicable method: minimal-prompt authoring + Core2 custody + Core1A semantics + Blueprint registry 1.9.0 / active Core1A 1.4.0 and Core2 1.5.0 at the pinned seed.

## Frontier
Academic/QRT analysis is authored. The learner package, staged SVGs and branch-scoped cold-run workflow are next. Exact-render H/S/P/M review and builder decision are deliberately pending.

## Eight-unit denominator
| Unit | Status | Evidence |
| --- | --- | --- |
| U1 Intake/baseline | DONE | owner-core-prompt.md; question-ledger.json; plan comment 5977788909 |
| U2 Academic/task analysis | DONE_PRE_RENDER | qrt-review.v1.json; source-cards.json |
| U3 Hardest-target brief | DONE_PRE_RENDER | qrt-review hardest_target; audit event 5 |
| U4 Canonical records | IN_PROGRESS | build_specimen.py / generated records pending |
| U5 Rendered deliverables | NOT_RUN | governed render pending GitHub Actions |
| U6 Semantic/interaction audit | NOT_RUN | exact bytes/browser evidence required |
| U7 Builder proposal | BLOCKED_BY_RENDER | must inspect exact learner page first |
| U8 Independent handoff | NOT_READY | freeze only after U5–U7 evidence |

## Risks / limitations
No separate sandbox repository was supplied, so no sandbox-copy claim is made. Local container network access is unavailable; the candidate uses a repository-native GitHub Actions cold run for rendering and Chromium audit. Learner state is simulated, not measured. This agent cannot self-certify academic effectiveness, release, or golden promotion.

## Exact next step
Commit canonical Chemistry package generation, staged SVG assets and a branch-scoped cold-run workflow; let that workflow render with the sole renderer, then inspect exact committed HTML and gate outputs before the U7 builder decision.
