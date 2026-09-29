# Protocol for one unit

Read [HOUSE-RULES.md](HOUSE-RULES.md), the unit's sources and `golden/INDEX.md` when that index is available. Give one unit author ownership from design to revision. A source reader and an independent reviewer contribute their own evidence; their reports do not become permission slips. Work in a unit branch and one PR. Push after each phase.

Use [first-stage and six-Core guidance](FIRST-STAGE-REVIEW.md): show Core2 first when a bank is supplied, otherwise Core1, with actual HTML/PDF, mappings and open findings before generating the remaining Cores. Research, solving, sketches and drafts across all Cores can continue. The dependency map describes learning claims, not execution locks; no new approval token, blocker or CI is introduced.

| Phase | Actor | Work and visible artifact | Decision to use judgment on |
|---|---|---|---|
| P0 Intake | Unit author | Define learners, scope, spine nodes, budget and open unknowns in UNIT.md; start WORKLOG. | Can the purpose and boundary be stated plainly? |
| P1 Source | Source readers A and B | Register acquisitions/scans, inventory each numbered item and key, write evidence cards, independently cross-read in batches of up to 25. Record discrepancies and open items. | Is the claimed source scope honest, including its denominator? |
| P2 Research/design | Unit author | Research broadly, derive and compare teaching approaches; record meaningful reasoning and the dependency/task arc in DESIGN-NOTE. Fit understood ideas into records and retain schema gaps explicitly. | Does each Core ask a distinct learner decision and does transfer change a real demand? |
| P3 First-stage prototype | Unit author | Build Core2 from the supplied bank, or source-grounded Core1 when no bank is available. Show actual HTML/PDF, scope, concept/difficulty/Atlas mappings and gaps; for Core2 include the separate key PDF. Compare relevant goldens and write SELF-CRITIQUE. | Is this first-stage experience useful and are its weaknesses visible? No numerical revision quota or all-six-Core completion requirement. |
| P4 Calibration | Owner | Comment on the prototype in OWNER-NOTES.md, particularly the first unit per subject or when asked. | Feedback guides the next revision; it is not a machine or delivery gate. |
| P5 Build | Unit author | After showing the first-stage packet, expand the remaining Cores using shared concepts, concrete exposure and distinct learner decisions. Incorporate available feedback; use `self_check.py` as an advisory map and triage observations in WORKLOG. | Would the author put their name to the learner's experience? Missing feedback or a report result is not an admission condition. |
| P6 Review | Independent reviewer | Read the design and self-critique, attempt the exact rendered pages, derive numeric results, compare with goldens and file a coaching review v2. Author revises. Two rounds are suggested, not a ceiling. | What would improve the learner experience, and what remains open? |
| P7 Acceptance | Owner | Inspect exact digest and findings; use `accept_product.py` for the Owner decision and publication. | The Owner may accept with acknowledged findings or reject the render. |

**One source/unit/product/review/decision.** The acquisition and item inventory say which source and how many items; cards support individual claims; package questions cite both. A unit's one library package is the record authority. `render_core.py` alone renders its six Cores. Review names the exact render digest. Only the Owner acceptance file and copy to public/ publish.

**Task arc.** In DESIGN-NOTE §4, compare each Core's practiced decision with all earlier tasks. Write novelty and family closure after the final tasks exist. A source's options, hint text, figure and printed key must remain faithful to the item; independently verified results can disagree with the key and should explain why.

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
