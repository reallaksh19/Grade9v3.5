# Protocol for one unit

Read [HOUSE-RULES.md](HOUSE-RULES.md), the unit's sources and `golden/INDEX.md` when that index is available. Give one unit author ownership from design to revision. A source reader and an independent reviewer contribute their own evidence; their reports do not become permission slips. Work in a unit branch and one PR. Push after each phase.

Use [first-stage and six-Core guidance](FIRST-STAGE-REVIEW.md): establish the real denominator/source state first; choose Core2 when a usable bank/source-question corpus is supplied, otherwise source-grounded Core1; triage canonical difficulty, why the material is difficult and interaction value; then author/review the hardest worthwhile vertical slice(s) first inside that route before presenting the first-stage packet. Hard-first is authoring priority only: preserve authentic source order and the complete denominator/coverage view. Research, solving, sketches and drafts across all Cores can continue. The dependency map describes learning claims, not execution locks; no new approval token, blocker or CI is introduced.

| Phase | Actor | Work and visible artifact | Decision to use judgment on |
|---|---|---|---|
| P0 Intake | Unit author | Define learners, scope, spine nodes, budget and open unknowns in UNIT.md; start WORKLOG. | Can the purpose and boundary be stated plainly? |
| P1 Source | Source readers A and B | Register acquisitions/scans, inventory each numbered item and key, write evidence cards, independently cross-read in batches of up to 25. Record discrepancies and open items. | Is the claimed source scope honest, including its denominator? |
| P2 Research/design | Unit author | Bind the real denominator, choose the Core2/Core1 first-stage route, research broadly, derive and compare teaching approaches, and record difficulty-first triage plus the dependency/task arc in DESIGN-NOTE. Keep concept difficulty, question difficulty/components, teaching-difficulty explanation, interaction value and learner evidence distinct. | Which learner thinking is genuinely difficult, which vertical slice should be authored first, and where does interactivity materially improve learning? |
| P3 First-stage prototype | Unit author | Build the hardest worthwhile vertical slice(s) first inside the selected Core2/Core1 route. Show actual HTML/PDF, the complete denominator/coverage map, explicit Medium/Low/deferred/omitted/unresolved state, concept/difficulty/Atlas mappings and gaps; for Core2 include the separate key PDF. Compare relevant goldens and write SELF-CRITIQUE. | Is the first-stage experience useful, does the Hard slice address the declared crux, and can the Owner see what remains across the full denominator? No numerical revision quota or all-six-Core completion requirement. |
| P4 Calibration | Owner | Comment on the prototype in OWNER-NOTES.md, particularly the first unit per subject or when asked. | Feedback guides the next revision; it is not a machine or delivery gate. |
| P5 Build | Unit author | After showing the first-stage packet, continue Medium then Low/remaining coverage and expand the remaining requested Cores using shared concepts, concrete exposure and distinct learner decisions. Incorporate available feedback; use `self_check.py` as an advisory map and triage observations in WORKLOG. | Would the author put their name to the learner's experience? Missing feedback or a report result is not an admission condition. |
| P6 Review | Independent reviewer | Read the design and self-critique, attempt the exact rendered pages, derive numeric results, compare with goldens and file a coaching review v2. Author revises. Two rounds are suggested, not a ceiling. | What would improve the learner experience, and what remains open? |
| P7 Acceptance | Owner | Inspect exact digest and findings; use `accept_product.py` for the Owner decision and publication. | The Owner may accept with acknowledged findings or reject the render. |

**One source/unit/product/review/decision.** The acquisition and item inventory say which source and how many items; cards support individual claims; package questions cite both. A unit's one library package is the record authority. `render_core.py` alone renders its six Cores. Review names the exact render digest. Only the Owner acceptance file and copy to public/ publish.

**Difficulty-first scheduling.** `LP-H* / LP-M* / LP-L*` are Worklog/Design Note scheduling labels only, never learner/package/search metadata. Interaction value is authoring rationale only. `authoring priority ≠ source order ≠ learner navigation order`. A bank/Core2 first-stage packet may implement only a bounded Hard learner slice while its coverage/mapping view still exposes every inventoried item and its current state.

**Parallelism.** For a new or uncalibrated instructional pattern, default to one or two coherent Hard slices before broad helper parallelism. For an already-calibrated pattern, bounded helpers may start earlier from the same canonical design. One unit author reconciles academic meaning in both cases; no calibration token is created.

**Task arc.** In DESIGN-NOTE §4, compare each Core's practiced decision with all earlier tasks. Write novelty and family closure after the final tasks exist. A source's options, hint text, figure and printed key must remain faithful to the item; independently verified results can disagree with the key and should explain why. Planned Core2A/Core2B lineage is not actual prior exposure until delivered.

**Time and spend.** Prototype calibration is early so expensive content repairs are found before a full build. The $15 unit guide excludes source readback; past $25, note spend and continue thoughtfully. For a 162-item source, the spec's $35–65 two-reader estimate is unmeasured until the first batch. Never turn cost numbers into delivery refusal.

## Step-back check, P0–P7

At each phase's end, put nine one-line answers with evidence in WORKLOG. For code slices use the PR and TASK_EVIDENCE. No tool reads this as permission.

1. **SBC-1 Learner:** What does the learner now see, do or understand differently?
2. **SBC-2 No new gate:** Did I add a refusal, blocker, content failure or count to satisfy?
3. **SBC-3 Thinking:** Did I research and reason, or fill a field because it was there?
4. **SBC-4 One of everything:** Did I add a second renderer, package, ledger, role or path?
5. **SBC-5 Construction:** Can the format or renderer prevent a defect I am policing afterwards?
6. **SBC-6 Coherence:** Does any text, figure, source, task or document describe an older version?
7. **SBC-7 Honest state:** Are PASS, FAIL and NOT_RUN accurate and weaknesses declared?
8. **SBC-8 Convergence/cost:** Did this help approach Owner acceptance? Is the work pushed and spend noted?
9. **SBC-9 Reusable:** Can another subject or offloaded team follow this without an oral explanation?

Record `Acted on: <change>` or `none`. Correct a wrong-way answer now, or log its reason and consequence; never mistake the record for a quality gate.
