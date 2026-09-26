# Stress-test prompt: Motion in 2D six-Core product (research-first, no escape states)

Give everything below the line to a fresh agent with write access to the repository. It
exercises the research-first policy end to end: raw demand questions → research → six Cores
with web pages → Atlas, question bank and Run Builder updated from the created data. The
policy it tests is `Shared/workflows/research-first.v1.json` (`no_escape_state`,
`no_profile_gate`, `no_ambiguous_source_claim`, `full_reconciliation`).

---

You are building a source-grounded Grade 9 Physics six-Core learner product for:

**MOTION IN 2D — PROJECTILE MOTION: STANDARD MODEL AND MODIFIED-DYNAMICS DEMAND**

Repository: https://github.com/reallaksh19/Grade9V3

Produce the complete six-Core learner-product set — Core1, Core2, Core1A, Core1B, Core2A,
Core2B — with their web pages, and feed everything you create back into the Atlas, the
question bank and the Run Builder data. Use the five fixed projectile questions below as the
assessment-demand anchor set.

Do not redesign the Core roles. Do not invent a new academic schema. Do not treat execution
order as authority order.

======================================================================
0. READ THESE FIRST
======================================================================

Policy and contracts (repository contracts override this prompt on any conflict — except that
nothing may reintroduce an escape state; see section 1):

- `Shared/workflows/research-first.v1.json` and `docs/RESEARCH-FIRST-WORKFLOW.md`
- `Shared/roles/README.md`, `Shared/roles/CORE-AUTHORITY-CONTRACT.md`,
  `Shared/roles/LEARNER-PRODUCT-TEMPLATES.md`
- `Shared/roles/CORE1.md`, `CORE2.md`, `CORE1A.md`, `CORE1B.md`, `CORE2A.md`, `CORE2B.md`
- `Shared/library/package.schema.json`
- `Shared/web/interactive-page-blueprints.v1.json`

Canonical Motion-in-2D truth and demand records:

- `Physics/library/phy-kin-2d-motion.v1.json` (bucket `BUCKET-PHY-KIN-2D-MOTION`)
- `Physics/matrices/phy-kin-2d-motion.rungs.json` (`MATRIX-PHY-KIN-2D-MOTION`, rungs R1–R3)
- `Physics/library/exam-bank/competitive-exam-question-bank.v2.json`
- `tests/fixtures/prompt-composer/projectile-stress-set.json` (the owner's question set)
- existing explorers under `public/physics/motion-in-2d/explorers/`

======================================================================
1. OPERATING RULE — THERE IS NO ESCAPE STATE
======================================================================

HOLD, HELD, FAIL/FAILED, INCOMPLETE, BLOCKED, WAITING, PENDING, WITHHELD, NOT_ESTABLISHED,
UNAVAILABLE and DEFERRED are never an outcome of your work, a product state, a validation
result you hand back, or a reason to stop. "Out of scope", "requires owner input", "left for
a follow-up" and "cannot be determined" are the same thing in other words and are equally
forbidden.

Every condition that older instructions resolved with a hold is a duty you complete inside
this job:

| Condition you meet | Duty | What you do |
|---|---|---|
| ambiguous question identity | `RESEARCH_SOURCE_IDENTITY` | read each candidate's original paper, compare text, figure and stated conditions with the demand, choose the match, record the discriminator |
| no canonical mapping | `RESEARCH_CANONICAL_MAPPING` | map to an existing capability, or add a `CANDIDATE` capability through the package schema and map to it |
| missing source custody | `ACQUIRE_SOURCE` | find and record the original (stem, conditions, options, figures, answer, locator); owner-supplied text is custody of class `OWNER_SUPPLIED` |
| source does not cover practice | `AUTHOR_PRACTICE` | author practice inside the taught capability, labelled `AUTHORED_PRACTICE` |
| untaught model or extension | `AUTHOR_EXTENSION_TEACHING` | research it, add a `CANDIDATE` extension microtopic, teach it in Core1A/Core1B marked `EXTENSION`, then practise it |
| missing prerequisite | `TEACH_PREREQUISITE_BRIDGE` | author the bridge before the dependent Core |
| missing worked example, explanation or visual | `AUTHOR_ASSET` | author it with provenance `AUTHORED_PEDAGOGICAL` and bind it to a representation |
| missing learner data | `APPLY_DEFAULT_LEARNER` | default median learner (knowledge 50%, full support), then a short diagnostic |
| transfer needs prior exposure | `SEQUENCE_PRIOR_EXPOSURE` | place and cite the Core1A/Core1B/Core2A items that establish it before each Core2B task |
| a gate or test reports a defect | `FIX_AND_REGATE` | fix the product, re-run the gate; a finding is never your result |
| no human review yet | `RECORD_REVIEW_STATUS` | deliver; state the missing review as a label |

Truthfulness is not relaxed. You never fabricate to close a duty: no invented exam identity,
no authored text presented as source, no guessed question number, no source hints the source
did not give. If research finds no original for a question, the owner's text is the custody,
the question is used, and no exam identity is claimed. That is a completed outcome.

Do not stop to ask the owner. Where a decision is not given, use the defaults in
`default_request_values` and say which defaults you applied.

======================================================================
2. FIXED FIVE-QUESTION DEMAND CORPUS
======================================================================

These owner labels define the demand set. Do not substitute different demands.

| Owner label | Demand | Repository ref |
|---|---|---|
| Q28 | Velocity direction from x(t) and y(t) | `PYQ-PHY-JEEMAIN-2026-04APR-S2-Q29` |
| Q15 | Maximum projectile height after an energy-losing bounce | ambiguous: `PYQ-PHY-JEEADV-2018-P2-Q08` or `PYQ-PHY-JEEADV-2023-P1-Q01` |
| Q21 | Gravity changes after the apex | `PYQ-PHY-JEEADV-2022-P1-Q08` |
| Q26 | Trajectory through a specified point | `PYQ-PHY-JEEADV-2026-P1-Q06` |
| Q23 | Projectile motion with linear drag | `PYQ-PHY-JEEADV-2025-P2-Q15` |

Q15: the short label is not an identity. Resolve it by research — the original papers' text,
figures and conditions against the stated demand — and record the discriminating evidence.
Do not guess, and do not leave it unresolved. The non-selected candidate stays as demand
evidence in the trace with the reason it was not selected.

All five demands must appear in the product and in the traceability file.

======================================================================
3. AUTHORITY GRAPH — NON-NEGOTIABLE
======================================================================

```
CANONICAL ACADEMIC TRUTH           → Core1, Core1A, Core1B
AUTHORIZED SOURCE CUSTODY          → Core2
CANONICAL TRUTH + ELIGIBLE DEMAND or TRUTHFULLY AUTHORED PRACTICE
  (+ optional learner support)     → Core2A
PRIOR EXPOSURE + TAUGHT CAPABILITY + GENUINELY CHANGED DEMAND → Core2B
```

1. Core1/Core1A/Core1B derive from the canonical Motion-in-2D package, never from Core2.
2. Core2 is source custody. Missing custody is researched (section 1), never held, and never
   becomes academic authority while research is in progress.
3. An extension a question needs is admitted explicitly as a `CANDIDATE` extension
   microtopic and then taught; it never silently rewrites the three canonical microtopics.
4. Prompt generation, set planning and owner labels are not academic authorities.

======================================================================
4. EXECUTION ORDER (production control only)
======================================================================

1. Record the starting SHA of `main`.
2. Compose and plan with the repository tools, and read their duties:
   ```sh
   python3 Shared/tools/prompt_composer.py --input tests/fixtures/prompt-composer/projectile-stress-set.json --out-dir OUT/compose
   python3 Shared/tools/plan_request.py --plan OUT/compose/authoring-request.json
   python3 Shared/tools/compile_execution_packet.py --request OUT/compose/authoring-request.json
   ```
   Every `duties` / `agent_actions` / `RESEARCH_AND_AUTHOR` entry is work for this job.
3. Inspect canonical truth; resolve the five question records (Q15 by research).
4. Establish Core2 custody (research).
5. Core1 → Core1A → Core1B from canonical truth (plus admitted extensions, marked).
6. Core2A from canonical truth plus eligible demand or authored practice.
7. Core2B only after the exposure it needs is sequenced and cited.
8. Build web pages, update Atlas / question bank / Run Builder data (section 17).
9. Validate (section 19); fix and re-run until everything passes.

Inspecting Core2 first does not make Core2 the source of Core1-family truth.

======================================================================
5. CANONICAL CONCEPT BOUNDARY
======================================================================

The canonical bucket has three microtopics:

- R1 `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS` — one event, independent x/y components, one clock
- R2 `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION` — constant-acceleration kinematics per component
- R3 `MIC-PHY-KIN-PROJECTILE-MODEL` — choose the gravity-only projectile model before its consequences

Core1/Core1A/Core1B cover exactly these, preserving `microtopic.inferential_jump`, intrinsic
depth, canonical relations, representations, misconceptions, checks and exit criteria.

Classify every demand element as `CANONICAL`, `CANONICAL_CONSEQUENCE`, `BRIDGE` or
`EXTENSION` — nothing else. Candidates for EXTENSION include differentiating x(t), y(t) for
velocity direction; energy loss on impact (coefficient of restitution / kinetic-energy
fraction); a change of gravity after the apex; trajectory-equation manipulation through a
point; linear drag (exponential velocity decay). For each EXTENSION:

1. research the physics from a reliable source and record the reference;
2. add a `CANDIDATE` extension microtopic (and capability/relation/representation as needed)
   through `Shared/library/package.schema.json`, marked as extension, prerequisite-linked to
   the canonical microtopic it extends;
3. teach it in Core1A and Core1B **after** the canonical microtopics, labelled `EXTENSION`;
4. only then use it in Core2A, and in Core2B only as transfer of what was just taught.

The three canonical microtopics are not rewritten, merged or reordered.

======================================================================
6. PER-QUESTION CANONICAL MAPPING
======================================================================

Preserve each question's `question.primary_capability_ref`. Never create or use
`primary_concept_id`. Set labels ("Projectile Motion", "Modified Dynamics", "R3",
"Advanced") are composition context only.

For each of the five record: owner label; resolved ref; other candidate refs and why not
chosen; `primary_capability_ref`; secondary capability refs; microtopic/rung; extension
microtopics it needs; source-custody provenance class; demand-evidence status;
learner-eligibility status; classification; the duties you performed.

======================================================================
7. DEMAND EVIDENCE AND LEARNER ELIGIBILITY
======================================================================

These are separate. The owner fixture marks the JEE Advanced items `EXCLUDED` from the
learner set. For each excluded demand:

- keep the original as demand evidence (Core2 custody, diagnostic trace);
- author an eligible `AUTHORED_PRACTICE` twin inside the taught (canonical or admitted
  extension) capability so the learner still learns and practises that demand. The twin
  never impersonates the source item or claims its exam identity.

Where eligibility is not decided, it is `DEFAULT_ELIGIBLE` (median learner).

======================================================================
8. LEARNER PROFILE
======================================================================

Owner estimate: about 50% familiarity (this is also the default median). The learner
understands basic velocity components and knows the standard projectile equations; chooses
equations inconsistently; confuses position direction, velocity direction and trajectory
tangent; struggles with apex and impact conditions and with changed model assumptions;
benefits from graphical reasoning, worked examples, staged scaffolds, misconception
diagnosis and immediate independent verification.

The percentage is not mastery. It must not shrink or expand Core1A/Core1B, establish
prerequisite mastery or establish transfer readiness. Begin with a diagnostic of at least
three items and route Core2A/Core2B support from actual attempts.

======================================================================
9. CORE1 — compact semantic orientation
======================================================================

From the canonical bucket: scope; named quantities; conventions; canonical representation;
governing relations with meanings and conditions; compact anchor examples; the hard
conceptual transitions; the admitted extensions listed as extensions; pointers into
Core1A/Core1B. Not a derivation book, not a PYQ solution bank, not a shortened Core1A.

======================================================================
10. CORE2 — source custody
======================================================================

For every one of the five questions (and the non-selected Q15 candidate as evidence):
exact source identity (or `OWNER_SUPPLIED` with no exam identity), original identifier,
stem, conditions, options/subparts, figures and captions, source hints only if the source
gave them, source answer/rubric/working, provenance class. Record the source receipt.

`question.hints[]` = source custody. `question.scaffolds[]` = authored support. Never mix.

Core2 is delivered complete. It is never an empty or "held" product.

======================================================================
11. CORE1A — detailed declarative teaching
======================================================================

For each canonical microtopic, then each admitted extension (marked `EXTENSION`): entry
assumptions; frame/convention; the inferential jump; stepwise construction; why each step
is valid; representation bridge; worked anchor; plausible wrong path; diagnostic prompt;
repair; independent checks and limits; exit task; model answer.

A missing worked anchor is authored (`AUTHORED_PEDAGOGICAL`), never left out.

======================================================================
12. CORE1B — self-tutor reconstruction
======================================================================

The same conceptual coverage as Core1A (canonical + extensions). Per concept: PREDICT →
ATTEMPT → RECONSTRUCT → DIAGNOSE → REPAIR → BOUNDARY TEST. A real conceptual decision
precedes every reveal; each prompt closes with a model response, rubric or accepted/rejected
examples. Not Core1A with blanks. Protected material does not appear before the attempt in
the rendered page.

======================================================================
13. CORE2A — supported familiar application
======================================================================

Each item: truthful provenance; capability mapping; stem/conditions; representation;
optional authored scaffold ladder (`question.scaffolds[]`); complete reasoning route
(`question.answer.reasoning_route[]`); crux (`question.answer.crux_move_ref`); full solution;
independent check; failure signal; repair pointer; exposure role. Routes must explain model,
representation and event choice, not only algebra. Include the eligible twins from
section 7.

======================================================================
14. CORE2B — changed-demand transfer
======================================================================

Valid only with explicit prior exposure (cite the Core1A/Core1B/Core2A items placed before
it), already-taught capability, a genuinely changed decision expressed as a DECIDE move
identified by `question.transfer.protected_move_ref`, and no pre-attempt scaffold or visual
that reveals it. Dimensions: model_choice, representation_translation, novelty,
reasoning_steps. Changing numbers or nouns does not count. Drag, energy loss or changed
gravity may appear in Core2B only after their extension teaching exists in this product.

Every item: prior-exposure lineage; changed-demand statement; protected move; safe
pre-attempt support; learner commitment; post-attempt support; full answer; justification
rubric; independent check; repair route to the Core1A/Core1B concept.

======================================================================
15. VISUALS
======================================================================

Visuals are academic content. Use the canonical representations
(`REP-KIN-2D-SHARED-CLOCK`, `REP-KIN-2D-EVENT-CLOCK`, `REP-KIN-2D-PROJECTILE-MODEL`) and the
existing explorers. Where a needed visual has no binding, author it: add a `CANDIDATE`
representation / scene binding in the subject library and render it on the page. For every
visual record: representation ref; purpose; required elements; elements actually present;
correspondence; reveal stage; accessible description; provenance; review label. A spec file
is not a visual — the page must render it. No subject geometry in `Shared/` code.

======================================================================
16. PROVENANCE
======================================================================

Every stem, hint, scaffold, worked example, reasoning route, diagram, shortcut, model answer
and transfer variant is one of: `SOURCE_VERBATIM`, `SOURCE_DERIVED`, `OWNER_SUPPLIED`,
`CANONICAL_DERIVED`, `AUTHORED_PEDAGOGICAL`, `AUTHORED_PRACTICE`. Authored material next to a
PYQ must be visibly distinct from it.

======================================================================
17. INTEGRATION — CREATED DATA UPDATES ATLAS, WEB PAGES, BANK, BUILDER
======================================================================

The product is not finished until what you created flows through the repository's own
pipeline:

1. Write every new record (extension microtopics, capabilities, representations, authored
   questions, source custody) into the Physics library through the package schema, as
   `CANDIDATE`, using the execution-packet work orders
   (`Shared/tools/execute_authoring_run.py`).
2. Regenerate the Core projections: `python3 Shared/tools/build_core_learning_data.py`.
3. Build each Core's web page through its registered blueprint:
   `Shared/tools/web_resolver.py` → `Shared/tools/web_run_bundle.py` /
   `Shared/tools/build_interactive_page.py`.
4. Regenerate the question-bank, Atlas and Run Builder data:
   `python3 Shared/tools/build_question_bank_web.py`, `python3 Shared/tools/build_web_data.py`,
   `python3 Shared/tools/build_manifest.py`, `python3 Shared/tools/build_pages_site.py`.
5. Confirm the Atlas (`public/` topic atlas) links every microtopic — canonical and
   extension — to its Core pages, and the Run Builder lists the bucket.

======================================================================
18. FIVE-QUESTION DEMAND ANALYSIS
======================================================================

For each owner question answer: A. canonical capability exercised; B. the real bottleneck
decision; C. assumed prerequisite; D. canonical part; E. extension/bridge part and the
microtopic that now teaches it; F. source custody obtained and how; G. learner eligibility
and basis; H. its Core2A role; I. its Core2B role, if any, with the exposure that licenses it;
J. the duties you performed and the artifacts that close them.

======================================================================
19. TRACEABILITY AND VALIDATION
======================================================================

Produce a machine-readable trace with, for every artifact: artifact_id; Core; canonical
source ref; owner label; exact ref and other candidates; primary and secondary capability
refs; microtopic (canonical or extension); demand-evidence status; learner-eligibility
status; prerequisites; misconception; representation ref; reveal state; source-hint refs;
authored-scaffold refs; reasoning refs; verification ref; provenance class; transformation
from canonical truth; prior-exposure refs (Core2B); protected move; duties performed; review
labels. Do not expose private chain-of-thought.

Distinguish `STRUCTURALLY_VALIDATED`, `SOURCE_VERIFIED`, `ACADEMICALLY_REVIEWED`,
`PUBLICATION_READY`. You may claim only the first two; the others are labels for human
review, and their absence does not stop delivery.

Run and make pass:

```sh
python3 Shared/tools/escape_state_guard.py
python3 Shared/tools/core_template_contract.py
python3 Shared/tools/core_authority_contract.py
python3 Shared/tools/topic_independence_guard.py
python3 Shared/tools/build_manifest.py --check
python3 Shared/tools/build_pages_site.py --check
python3 -m unittest discover -s tests -p "test_*.py"
```

Also check at minimum: Core1-family authority is canonical; order ≠ derivation; no fabricated
custody; Q15 resolved by recorded evidence; every `primary_capability_ref` preserved; no
`primary_concept_id`; eligibility separate from demand; hints ≠ scaffolds; Core1A and Core1B
coverage identical; attempt before reveal in the rendered pages; extensions admitted and
marked, canonical microtopics unchanged; Core2A routes explain choices; Core2B teaches
nothing new; protected decisions hidden pre-attempt; every visual rendered and bound;
terminology/equations/conditions consistent across the six Cores; everything closes without
a tutor; **no escape state anywhere in the product, the trace or your report.**

======================================================================
20. DELIVERABLES
======================================================================

1–6. The six Core learner products, complete, each with its web page.
7. The five-question demand map (section 18).
8. The cross-Core traceability file.
9. The validation report with the commands above and their results.
10. A duty register: every duty met, what you did, and the artifact that closes it.
11. The updated library records, Atlas, question bank and Run Builder data.
12. A rendered learner preview showing visuals and attempt/reveal behaviour.

A pull request containing all of it.

======================================================================
21. ACCEPTANCE — AND WHAT FAILS THIS STRESS TEST
======================================================================

The work passes only if all five demands are accounted for, all six Cores are delivered
complete with web pages, the Atlas/bank/builder are updated, and every check in section 19
passes.

The stress test is failed by any of:

- an escape state (section 1) or an equivalent phrase used as an outcome, product state,
  trace status or report conclusion;
- stopping to ask the owner, or leaving work "for a follow-up";
- an empty, partial or "held" Core, page or visual;
- Q15 guessed, or left unresolved;
- authored material presented as source, or an invented exam identity or source hint;
- an extension taught without admission, or needed but left untaught;
- Core2B requiring a model not taught earlier in the product;
- the 50% estimate used as mastery or to change Core1A/Core1B coverage;
- created data that never reaches the Atlas, question bank or Run Builder;
- a claim of success based on files existing or tests parsing rather than the rendered product.

======================================================================
22. WORKING METHOD
======================================================================

Inspect `main` and record the SHA; read the contracts; inspect the canonical package and
the five records; publish a short plan (authority sources, canonical coverage, Q15 research
approach, extensions to admit, custody plan, eligibility, files to change, validation). Then
execute without waiting for approval. Where repository truth contradicts this prompt,
preserve repository truth and record the contradiction — then keep going.

The objective is the strongest complete, honest six-Core learning system for Motion in 2D —
researched where the repository was silent, authored where research leaves a gap, and
labelled truthfully throughout.
