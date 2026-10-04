# ISS31 work report — independent candidate A

- Issue: #31 — D1 hybridisation, Q1–Q10.
- Work intent: benchmark candidate implementation/review.
- Branch: `agent/iss31-hybridisation-candidate-a-20261004`.
- Pinned source/template seed: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`.
- Protocol: V3_1 ACTIVE.
- Production renderer authority: `Shared/tools/render_core.py`.
- Independence: issue #32 not inspected.
- Owner clarification: initial NONE; round-2 execution clarification accepted from issue comment `5978104772`.
- Publication authority: NOT GRANTED; candidate only.

## U1–U8 status

| Unit | Status | Evidence |
|---|---|---|
| U1 Intake/baseline | PASS | `owner-core-prompt.md`, input hashes, source snapshot, audit log. |
| U2 Academic/task analysis | PASS | `question-ledger.json`, `source-cards.json`. |
| U3 Hardest-target brief | PASS | Q5 · MODEL · D2; learner-relative model-scope target in ledger/QRT. |
| U4 Canonical academic records | PARTIAL | Durable candidate IDs, solutions and QRT evidence complete; owner-bank destination path is repaired, but Chemistry package/bank/manifest are not materialized without an executable checkout. |
| U5 Render/integration | NOT_RUN | Round 2 repaired the TEST-only CLI restriction; this chat still has no executable repository checkout for package/bank materialization, validators, renderer or browser audit. |
| U6 Semantic/interaction audit | PARTIAL | H1–M3 semantic authoring review complete; exact-render leakage/browser evidence NOT_RUN. |
| U7 Builder proposal | NOT_RUN | No actual render to inspect; no speculative builder change proposed. |
| U8 Independent handoff | READY_TO_FREEZE | Evidence branch is ready for a draft candidate PR and issue checkpoint; no paired comparison performed. |

## Key academic decisions

1. Treat electron-domain counting as local to the chosen central atom; multiple bonds are one VSEPR region/direction.
2. Keep electron-domain geometry distinct from molecular geometry when lone pairs are present.
3. Treat wedge/dash as a 3D representation translation, not decorative notation.
4. Select models by explanatory job: VSEPR for overall electron-domain arrangement; orbital-overlap/hybrid descriptions for orbital-level bonding detail.
5. Preserve the introductory hybridisation model boundary rather than presenting it as a complete quantum description.
6. Use internuclear-axis orientation as the defining sigma/pi classification criterion.

## Hardest target

Q5: the learner must choose VSEPR because the requested output is only overall 3D electron-domain arrangement, then state what the model predicts and what detailed orbital-overlap information it does not determine. The authored interaction specification compares two explanatory lenses on the same NH3 anchor.

## Declared weaknesses / limits

- Primary learner-facing HTML is not produced.
- No render digest exists.
- No schema execution, renderer gaps/build, PDF, browser, touch, focus, overflow or protected-source inspection ran.
- No page-derived builder proposal exists.
- Chemistry lacks a package for this slice at the pinned seed.
- The governed owner-bank authoring CLI was TEST-only at the pinned seed; round 2 repaired that inconsistency in `f1621cd…` without changing provenance. The actual Chemistry owner bank is still not materialized because the execution workspace remains unavailable.
- No measured learner fit or learning-effectiveness claim is made.

## Step-back

1. **SBC-1 Learner:** academic support now distinguishes the exact conceptual decisions for all ten items; actual learner page NOT_RUN.
2. **SBC-2 No new gate:** no new completion quota or refusal rule added.
3. **SBC-3 Thinking:** difficulty/demand/QRT were derived independently; D1 cohort mismatches were retained.
4. **SBC-4 One of everything:** no second renderer, bank authority, or HTML path invented.
5. **SBC-5 Construction:** the owner-bank path mismatch is preserved as a finding and repaired in the existing CLI; no alternate schema/renderer or exam-bank workaround was introduced.
6. **SBC-6 Coherence:** evidence is pinned to the issue hashes and template seed; no older page is presented as this candidate.
7. **SBC-7 Honest state:** semantic work PASS/PARTIAL; render/browser/build checks NOT_RUN.
8. **SBC-8 Convergence/cost:** evidence is committed and ready for independent review; spend not measured.
9. **SBC-9 Reusable:** QRT and ledger formats expose the decisions another subject/runtime author must implement without oral context.

Acted on: preserved actual D2 classifications, stopped short of an unauthorised owner-bank path, and recorded exact NOT_RUN consequences.


## Round 2 continuation

Owner comment `5978104772` confirmed the initial diagnosis and authorised a minimal path repair. The original frozen first submission remains `27dd6611b6bf9c824f8e066386a41af22a6ea88c`.

Repair commit `f1621cd167a569f85ea42909ad97db1060028db5` changes only the existing owner-bank path handling, its regressions and documentation. It keeps the TEST path and adds a canonical subject lane at `<Subject>/library/owner-bank/`; it does not alter custody, stem hashes or exam-bank policy.

A second, independent blocker remains: this chat has no checked-out repository runtime. The local shell cannot resolve GitHub and the connector is not an arbitrary Python/browser execution environment. Consequently canonical Chemistry package/bank/manifest materialization and the governed HTML/browser run remain NOT_RUN.
