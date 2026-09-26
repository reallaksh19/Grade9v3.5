# Research-first learner-product workflow

A job starts from the owner's questions, prompts and any syllabus text. The agent researches the subject and the source material, builds the coverage map, authors the Cores and visuals, and delivers the book, web pages, question bank, atlas links and builder integration. Research is part of the job from the first step — not a response to a hold.

The invariants are data in [`Shared/workflows/research-first.v1.json`](../Shared/workflows/research-first.v1.json):

| Invariant | Rule | Enforced by |
|---|---|---|
| `no_escape_state` | HOLD, FAILED, INCOMPLETE, BLOCKED, WAITING, PENDING, WITHHELD, NOT_ESTABLISHED and UNAVAILABLE are never an outcome or a reason to stop. Each condition that used to produce one is a duty in `escape_state_duties`, carried out in the same job. A gate finding is fixed and the gate re-run. | `research_first_policy.duty_for`; planner product states are `READY` or `RESEARCH_AND_AUTHOR` with a duty; composer `duties`; `escape_state_guard.py` over role contracts, templates, prompts, plans and work orders |
| `no_profile_gate` | No student profile is required. Any missing learner fact takes the default median value (knowledge 50%, full support, `DEFAULT_MEDIAN`), then a short diagnostic adjusts from actual attempts. | intake and planner apply `default_learner_start` / `default_request_values`; gate `diagnostic_missing` |
| `no_hold_output` | A hold is never an output or a passing state. Missing examples, diagrams or explanations become research and authoring tasks. Validation checks the rendered learner product. | intake status is always `RESEARCH_AND_AUTHOR`; gate `learner_text_placeholder`, `hold_as_state`, `teaching_incomplete`, `practice_incomplete`, `research_open` |
| `no_ambiguous_source_claim` | A short label is never an identity. The agent researches each candidate's original text and conditions, selects the match and records the discriminator. If none matches, the question is used as the owner's question with no exam identity claimed. | gate `identity_unresolved`, `identity_text_mismatch`, `identity_condition_mismatch`, `identity_discriminator_missing`, `identity_displayed_without_claim` |
| `full_reconciliation` | Every supplied question and syllabus subtopic is reconciled before building. The final coverage ledger links each one to teaching, practice and its learner-facing location. | intake `reconciliation`; gate `input_not_in_ledger`, `location_unresolved`, `question_not_rendered`, `question_not_in_bank` |

## Former holds and the duty that replaces each

| Former state | Duty | What the agent does |
|---|---|---|
| `IDENTITY_HOLD` | `RESEARCH_SOURCE_IDENTITY` | compare each candidate's original text and conditions, pick the match, record the discriminator |
| `UNMAPPED_HOLD`, `AGENT_PROPOSAL_PENDING_REVIEW` | `RESEARCH_CANONICAL_MAPPING` | map to a canonical capability, or add a `CANDIDATE` capability and map to it; agent mappings are used and labelled |
| `MIXED_SUBTOPIC_HOLD`, owner rung confirmation | `COVER_EVERY_SUBTOPIC` | cover every matrix/rung, keep per-question primaries |
| `WAITING_FOR_LEARNER_ENTRY`, `LEARNER_ELIGIBILITY_HOLD`, `NOT_ESTABLISHED` | `APPLY_DEFAULT_LEARNER` | default median learner, then diagnostic |
| `WAITING_FOR_PURPOSE`, supplement policy | `APPLY_DEFAULT_PURPOSE` | `PRACTICE`, `ALLOW_AUTHORED_CANDIDATES` (owner may override) |
| `BLOCKED_SOURCE_*`, `WAITING_FOR_SOURCE_*`, Core2 `HELD` | `ACQUIRE_SOURCE` | research the original source and record custody; owner-supplied text is custody of class `OWNER_SUPPLIED` |
| `BLOCKED_SOURCE_COVERAGE` | `AUTHOR_PRACTICE` | author `AUTHORED_PRACTICE` inside the taught capability |
| `BLOCKED_PREREQUISITE` | `TEACH_PREREQUISITE_BRIDGE` | author the bridge before the dependent Core |
| untaught capability / extension | `AUTHOR_EXTENSION_TEACHING` | admit a `CANDIDATE` extension microtopic, teach it marked `EXTENSION` |
| `BLOCKED_ASSET`, `VISUAL_HOLD`, `HOLD_WORKED_ANCHOR` | `AUTHOR_ASSET` | author the explanation, example, visual or binding as `AUTHORED_PEDAGOGICAL` |
| Core2B `WITHHELD` for exposure | `SEQUENCE_PRIOR_EXPOSURE` | place and cite the Core1A/1B/2A items that establish exposure |
| no human review yet | `RECORD_REVIEW_STATUS` | deliver; the missing review is a label (`OWNER_REVIEW`), not a stop |

Truthfulness is unchanged: nothing is fabricated to close a duty. Researched material keeps its source provenance, authored material says it is authored, and exam identity is never guessed.

## Pipeline

```sh
# 1. raw input -> intake plan (content-derived ids, reconciliation, research tasks)
python3 Shared/tools/raw_intake.py --input request.json --out intake.json

# 2. research + author -> job bundle {request, content, evidence}  (agent work)

# 3. render the learner product and the delivery manifest
python3 Shared/tools/learner_product_render.py --bundle job.json --out OUT

# 4. final gate on the rendered product (optionally against a reference benchmark)
python3 Shared/tools/delivery_gate.py --manifest OUT/delivery.json \
  --benchmark benchmarks/learner-product-reference/physics-motion-2d.json
```

The public entry is [`public/raw-intake/`](../public/raw-intake/index.html). It computes the same intake as the Python tool (tested for exact equality) and exports the raw request, the intake plan and an agent prompt. The canonical-ref composer remains available for jobs that are already mapped; canonical ids are optional references discovered during research, never prerequisites.

## Reference benchmark

`benchmarks/learner-product-reference/physics-motion-2d.json` records the owner's Physics reference thresholds: a book of at least 35 pages (each with at least 40 words of learner text, so padding does not count) and at least 15 question-bank units that each carry the question, a worked answer and a visual.

## Regression

`tests/test_research_first_workflow.py` runs Physics (Motion in 2D), Mathematics (quadratics) and Chemistry (mole concept) from raw input through the gate, then mutates the rendered output — hold markers, placeholders, dropped inputs, missing worked examples or visuals, answers before attempts, mismatched or ambiguous identities, open research, missing atlas/builder links — and requires each to fail. The PR #288 Motion-in-2D product, which passed its own audit with holds as the learner output, is kept as a fixture and must fail.
