# Appendix F — Blueprint 1.9 impact and revised HTML-template implementation plan

**Owner authorization:** update this concept note and start coding the revised Core1A/Core2 templates. Implementation begins on an isolated follow-on branch from PR #21 head `8678645ef2fd5e63401ef5af3621b94e925732a8`. Main remains `9059848c2d2ea757b765a01c66841c8906cd7875`; PR #21 is draft and unmerged. A follow-on draft PR will target its branch so this change is reviewed separately.

## F1. What “Blueprint 1.9” means

`Shared/web/interactive-page-blueprints.v1.json` is the **registry** at version 1.9.0. It currently selects `BP-CORE1A-CONSTRUCTION@1.4.0` and `BP-CORE2-SOURCE-QUESTION@1.5.0`. Registry, blueprint, schema and renderer versions are different authorities. The 4 × 7 matrix reviews the semantic work; it does not define HTML layouts.

Blueprint 1.9 is not just a checklist: its slots, component order, required/expected levels, reference depths, interaction policy and responsive policy are consumed by the renderer and audits. Updating prose alone cannot deliver the new teaching behavior.

## F2. Changes and invariants

| Authority / behavior | Current impact | Required update |
| --- | --- | --- |
| Core1A construction, representation and repair slots | Construction sits in PRIMARY; visual/closure sit in SUPPORT | Make a coherent lesson flow; place the selected visual adjacent to construction inside each unit. Retain component markers and canonical anchors. |
| Core1A KEY_STEP | Crux currently precedes construction | Default direct-teaching migration: construct then summarize; future prediction entry must use an authored neutral prompt and safe initial figure. Never manufacture a prediction from answer-bearing decision text. |
| Worked-example policy | PREDICT_THEN_REVEAL currently wraps every step | Permit coherent visible worked explanation; optional retrieval/completion needs an actual authored decision and feedback. No generic “Predict step N.” |
| Contents and references | Bucket orientation and nested route consume opening space | Collapse Contents / concept route; preserve nested links, unit progress, previous/next and direct anchors. Reference remains requestable. Current assumptions/validity are teaching, not hidden background. |
| Demand-sensitive teaching | Canonical action/why_valid/output projected uniformly | Preserve those fields; present them with task-appropriate labels where the canonical demand is known. Do not infer MODEL just because an animation is present. |
| Core2 reader | Five slots, fourteen components | Preserve this shell; improve timing, provenance labels and exact concept navigation. No new lesson architecture. |
| DIFFICULTY_WHY / TRAP | Closed or hidden content remains reachable pre-attempt | Reuse inert post-attempt payloads for decision-bearing rationale/wrong-route material. Opening a warning does not establish a misconception. |
| HINT_LADDER | Visible ghost-rung stage labels and H0/Guided terminology | Use ordinary hint labels; retain machine provenance/stage/move markers and separate source/authored lanes. Authoring must still verify W protection of each hint. |
| CONCEPT_NAV | Links generally land at concept top | Prefer the unique selected construction unit that names the question; fall back honestly to concept if ambiguous. Preserve origin and return. Explicit pre-attempt study is recorded as assistance. |
| Assistance / result | Navigation state currently lacks complete assistance evidence | Distinguish question help consumed, concept study and solution exposure. Retry is recovery evidence; fresh uncued use can establish independence. No automatic grading or mastery inference. |
| Toughest-unit authoring | Current reference-depth renderer requires the source question as its worked anchor | Accept a valid alternate authored/canonical anchor when the unit builds the target crux. Preserve the requirement to construct the bridge; remove compulsory answer replay. |
| Assurance | Existing tests/audit require generic prediction disclosures | Update behavioral expectations; preserve regression evidence for source custody, exact anchors, staged SVG, touch/focus, overflow and disclosure eligibility. New HTML requires new receipts. |

Keep canonical concept IDs, source text/figures/printed keys, verified corrections, seven demands, four bands, difficulty evidence and question denominator. This revision does not promote new authored questions into authentic Core2.

## F3. Version and compatibility

Advance the registry and affected blueprint versions explicitly; update schema only for a field consumed by production. The resolver selects one active blueprint per role, so a second active Core1A entry would be ambiguous. Preserve manifests and canonical records; historical renders retain their pinned lineage and old receipts do not cover new bytes.

## F4. Coding plan and reviewable outputs

1. Pin live predecessor state, capture baseline failures and start a recoverable work report.
2. Revise Core1A: collapsed navigation; integrated construction/visual; insight after construction; coherent worked example; independent exit; requestable repair/reference. Preserve content, anchors and missing-authoring reports. Do not invent prerequisite tests, completion tasks or response grading.
3. Improve Core2 within its reader: inert post-attempt rationale/warning; ordinary hint labels; exact unique construction anchor; separate source/authored provenance; optional learner-requested study.
4. Preserve attempt/return context and assistance across navigation/reload. Core1A may teach fully; repaired original-question success is recovery evidence.
5. Render the existing mathematics ten-question product with its full coverage record and a chemistry concept specimen through the same renderer. Select the hardest chemistry target from actual reviewed tasks before claiming demand-matched performance.
6. Run focused regressions, the full local suite, static/source readback and exact-byte browser checks where Chromium is available. Report pre-existing failures and NOT_RUN checks honestly. Academic/learner outcomes require separate review.
7. Add authored opening prediction, readiness, completion, revision and transfer operators only when specimens show the need. Improve the interactive builder only after a concrete interaction demonstrates a limitation.

The first code slice delivers usable revised templates, not every conditional operator or educational validation. Preserve this boundary in the draft PR, work report and rendered artifacts. Owner acceptance of the exact render remains the publication decision.

