# Research-first learner-product workflow

A job starts from the owner's questions, prompts and any syllabus text. The agent researches the subject and the source material, builds the coverage map, authors the Cores and visuals, and delivers the book, web pages, question bank, atlas links and builder integration. Research is part of the job from the first step — not a response to a hold.

The invariants are data in [`Shared/workflows/research-first.v1.json`](../Shared/workflows/research-first.v1.json):

| Invariant | Rule | Enforced by |
|---|---|---|
| `no_profile_gate` | No student profile is required. Start at the documented default (foundation level, full support), run a short diagnostic, adjust from actual attempts. A missing knowledge percentage cannot block content creation. | intake always sets `learner_start`, `blocking=false`; gate `diagnostic_missing` |
| `no_hold_output` | A hold is never an output or a passing state. Missing examples, diagrams or explanations become research and authoring tasks. Validation checks the rendered learner product. | intake status is always `RESEARCH_AND_AUTHOR`; gate `learner_text_placeholder`, `hold_as_state`, `teaching_incomplete`, `practice_incomplete`, `research_open` |
| `no_ambiguous_source_claim` | A short label is never an identity. An exam identity is shown only when the original source text and the question's stated conditions match; with several candidates a discriminator is recorded. Otherwise no identity is claimed or displayed. | gate `identity_unresolved`, `identity_text_mismatch`, `identity_condition_mismatch`, `identity_discriminator_missing`, `identity_displayed_without_claim` |
| `full_reconciliation` | Every supplied question and syllabus subtopic is reconciled before building. The final coverage ledger links each one to teaching, practice and its learner-facing location. | intake `reconciliation`; gate `input_not_in_ledger`, `location_unresolved`, `question_not_rendered`, `question_not_in_bank` |

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
