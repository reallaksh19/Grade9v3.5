# U6 — Independent three-case Core1B learner and accessibility observation

**Class:** REVIEW_PROTOCOL_ONLY / TEST golden fixtures / NOT_AN_ACCEPTANCE_RESULT  
**Applies to:** `tests/fixtures/core1b-goldens/` in Grade9v3.5 draft PR #334. The historical merged authored TEST divisibility case is not approved curriculum; the algebra and motion cases are newly authored demonstrations, not authenticated exam questions.  
**State at authoring:** Grade 9 observation **NOT_RUN**; independent mathematical/pedagogical review **NOT_RUN**; human screen-reader review **NOT_RUN**; curriculum/QRT mapping and publication **NOT_GRANTED**.  
**Owner:** independent academic/accessibility reviewers. Do **not** self-sign as the fixture author or turn synthetic browser output into a real learner result.

## Why this review cannot be replaced by browser automation

The browser test checks whether the **attempt → reconstruct/diagnose → repair → worked explanation → independently committed changed-boundary** flow is operable. It does **not** establish that the student's proof is sound, that the hint repaired their actual misconception, that they understood the explanation, or that they transferred knowledge unassisted. A short attempt such as `33` is a valid **UI commitment only**, not a correct mathematical response. A `paper` checkbox reports an attempted external response but is not evidence of its quality.

The main acceptance question is: **Can a Grade 9 learner reconstruct a warranted explanation and handle a changed case, rather than merely click through answer gates or repeat the key?**

## Before any learner session

1. An independent reviewer verifies the exact `student-practice.v2.html` bytes and three golden JSONs from a pinned PR commit. Note the **reviewed SHA**, not just the moving PR URL. The HTML is **TEST-only** and contains answers in JavaScript source: its UI reveal gates are pedagogical, not cryptographic.
2. Confirm appropriate school/guardian permissions, safeguarding and age-appropriate practice; recruit learners through an authorized educator. Do not place real learner names, contacts, grades, IDs, health/accessibility details or identifying audio/video in GitHub, Actions logs or downloadable exports.
3. Use fresh browser storage (or the page's reset control) for every participant. Note whether the participant already studied the Core1A proof or any of these cases. Prior exposure can make recall look like new reconstruction.
4. Assign one anonymous **session label** that is not linkable to a student. Record the case **order** and device mode; the demonstration opens Case 2 initially, so deliberately navigate to each assigned case. Do not treat an order effect as a demand-band effect.
5. Observers must not give the proof, correct a hint in the moment, or tell a learner which answer to choose. They may repeat only the visible question verbatim. If they provide additional help, record exactly what kind and mark subsequent evidence **AIDED**.
6. An independent subject reviewer checks the mathematical/physics reference and QRT *proposed* cell for each case before rating reasoning. The fixture's prefilled `JUSTIFY-D3`, `REPRESENT-D2`, `MODEL-D2` cells are proposed classifications, **not** owner-admitted QRT resolutions.

## Learner session: observable sequence for **each** case

| Moment | What the facilitator asks the learner to do | Record evidence and falsifier |
| --- | --- | --- |
| Entry / Predict | Read the situation, restate the claim or misconception in their own words | Can they explain the task without the observer paraphrasing? Does “Start with what you think” invite a real idea, or merely prompt random input? |
| Initial attempt | Write/type or work on paper **before** opening any hint; do not demand a minimum response length | Preserve the learner's reasoning steps (anonymously and with permission), not only the committed flag. A number or arbitrary text counts as **attempt recorded**, not sound reasoning |
| Diagnose | Ask which step of the first attempt might be missing; allow the learner to request sequential diagnostics | Record **which prompts were revealed, in order**, and the misconception they actually exposed; flag hint leakage, confusion or an answer given away |
| Repair | Have the learner **rewrite and justify** the solution without seeing the worked reference | Compare original and repaired reasoning. Did the revised proof/model introduce a warranted missing step? A paper checkbox without inspected written work is **NOT_OBSERVED** for learning |
| Find answer | Invite the learner to locate **“Answer N — worked explanation”** after committing repair | Can they find the clear button/jump without help? The answer must not become visible automatically on repair, and the wording must not shame a short/incorrect first idea |
| Changed boundary | Invite a **new decision with justification** before opening its separate boundary answer | Record whether the learner already viewed the main reference. If so, classify transfer as **REFERENCE_EXPOSED**, never unassisted transfer; boundary answer must remain hidden until **its own** commitment |
| Reflect | Ask, “What changed in your reasoning, and how would you check a new example?” | Note student-owned explanation or inability to generalize; a success banner, navigation event or exported JSON does not answer this question |

**Reference-exposure limitation:** The UI can reveal the first worked answer before the boundary response. This is legitimate scaffolding but can confound *independent* boundary transfer. Record explicitly `reference_before_boundary = YES/NO`; only `NO` with genuine student reasoning can be considered a candidate for **UNASSISTED** transfer. Even `NO` is not proof of mastery without a human quality judgement.

## Case-specific independent reasoning warrants (reviewer-only, never prefeed student)

| Golden | Independent repair should show | Changed-boundary evidence | Reject this shortcut |
| --- | --- | --- | --- |
| 01 · Consecutive integers · proposed `JUSTIFY-D3` | Arbitrary integer `t`, guaranteed even factor, complete modulo-3 cases, and why coprime 2 & 3 imply 6 divides the product | Separate assessment of `(t−1)t`, with a valid counterexample (e.g. `t=2` gives 2) | `t=3,4,5` examples asserted to prove **every** case; unsupported claim that `t` itself always contains the factor 3 |
| 02 · Binomial square · proposed `REPRESENT-D2` | Explicitly multiplying `(x+2)(x+2)`; both cross-products leading to `x²+4x+4`; why matching `x=0` is not a universal identity | Characterizing exactly when the incorrect identity holds (`x=0` only) | Purely memorized formula with no explanation of the missing `4x`, or treating one sample as universal |
| 03 · Out-and-back motion · proposed `MODEL-D2` | Total distance 120 m, displacement 0; average speed 3 m/s, average velocity 0 m/s; numerator and direction each justified | For 60 m east then 30 m west in 30 s, speed 3 m/s and velocity 1 m/s **east** | Treating zero displacement as zero distance/speed, or omitting velocity direction |

An independently appointed academic reviewer may disagree with a proposed cell; record their **reason, counterevidence and alternate cell**, do not overwrite the frozen source of record without an authorized review decision.

## Separate human keyboard and screen-reader pass

Use an actual browser + selected supported assistive technology, with a human reviewer. Do **not** substitute programmatic `aria` checks or automated Chromium for this sign-off.

- Keyboard-only: case tab selection and focus; textarea and paper checkbox activation; commit-button disabled state; progressive diagnostics; after-repair focus on the named “Show Answer N” control; after-reveal focus on its heading; new boundary commitment. Verify no focus trap and sane reading/navigation order.
- Screen reader: the initial problem, mathematical notation (especially `(x+2)²`, `t−2`, speed versus velocity units), each announced commitment and revealed section, and distinct boundary answer. Record exact device, browser, assistive-technology version, issue and reproduction step **without student identifiers**.
- Responsive/manual: reflow at 320/390 CSS pixels and 200% text enlargement. Visual no-overflow automation is not a substitute for understanding the content and operating controls.

## Reviewer record — copy once per anonymous case observation

```text
Review artifact commit (immutable SHA):
Anonymous session label (non-identifying):
Independent observer role (academic / accessibility / facilitator):
Case ID / observed order:
Learner prior exposure (YES / NO / UNKNOWN):
Mode (typed / paper / keyboard-only / human screen reader):
Entry prompt comprehension (YES / PARTLY / NO / NOT_OBSERVED):
First attempt evidence — non-identifying reasoning or tightly paraphrased step:
First attempt warranted? (YES / PARTLY / NO / NOT_OBSERVED):
Diagnostic question indexes actually used:
Diagnostic revealed missing idea? (YES / PARTLY / NO / NOT_OBSERVED):
Independent revised reason (non-identifying):
Repair genuinely introduces missing warrant? (YES / PARTLY / NO / NOT_OBSERVED):
Was extra observer help given? (NO / YES + type):
Found the correct numbered answer without help? (YES / NO / NOT_OBSERVED):
Reference opened before boundary? (YES / NO / UNKNOWN):
Boundary response (non-identifying reasoning):
Boundary independently warranted? (YES / PARTLY / NO / NOT_OBSERVED):
Boundary evidence class (UNASSISTED_CANDIDATE / REFERENCE_EXPOSED / OBSERVER_AIDED / NOT_OBSERVED):
Any early worked answer or boundary answer disclosure? (NO / YES + steps):
Student could explain what changed and why? (YES / PARTLY / NO / NOT_OBSERVED):
If accessibility review: AT / browser / version and exact step:
Reviewer evidence location (restricted, NOT public or in PR):
Human assessment (ACCEPT_TEST_EXPERIENCE / REVISE / DEFER):
Reason including actual observed learner behavior:
Reviewer signoff / date (do not include student personal data):
```

**Do not fill this record with fabricated learners, synthetic test clicks or template answers.** Use `NOT_OBSERVED` for any unobserved educational claim, regardless of a successful file export or a working button.

## Decision boundaries and go/no-go

- **Accept the TEST experience only when** an independently authorized reviewer has actually seen honest learner attempts, diagnosed and repaired reasoning, a justified changed-boundary response, and successful findability/keyboard/AT where relevant, with reviewed immutable artifact identity and no decisive unanswered issues. The academic owner must explicitly record any acceptance.
- **Revise** for misleading motivational wording, absent learner-owned repair, confusion between speed and velocity, model answers exposed prematurely, inaccessible controls, answer-navigation dead ends or false claims of correctness.
- **Defer / hold** for absent consent, absent independent assessor, uninspected paper work, unverified screen-reader path, unknown source custody or no actual Grade 9 student observation.
- **Never infer** that three goldens cover all 28 QRT cells, that this TEST HTML is official/licensed curriculum, or that Stage 1 Runner B observations substitute for students or teacher review.
- **Publication and curriculum admission remain separate approvals**. A human observer cannot grant GitHub release or key distribution rights by completing this worksheet.

**Current result:** all review entries **UNFILLED**; no U6 human pass, QRT academic admission, learner mastery or product publication is claimed. Browser/CI status belongs in a separate engineering receipt, not in these human verdict cells.
