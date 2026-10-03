# Core 1A Agent Fill-in-the-Blanks Runbook

This guide enables any autonomous agent (or human contributor) to generate a gold-standard **Core 1A: Conceptual Construction** page that strictly adheres to the repository's constitutional specification (`Shared/roles/CORE1A.md` and `BP-CORE1A-CONSTRUCTION@1.4.0`).

---

## 1. The Core 1A Philosophy
* **Never state conclusions**: Always construct the concept in logical steps.
* **Explain why valid**: Every step must articulate *why* it is mathematically or physically valid.
* **Progressive Visuals**: Diagrams must be staged SVGs with step buttons (`data-g9-stages="s1 s2 s3"`), not static pictures.
* **Direct Misconception Attack**: Plausible mistakes must be identified, diagnosed, and repaired.
* **Active Triad Recall**: Every unit concludes with a 1-2-3 Triad (`CHECK`, `APPLY`, `CONNECT`).

---

## 2. Fill-in-the-Blanks Slots (18 Blueprint Components)

| Slot Name | Description & Requirement |
|---|---|
| `topic_title` & `subject_name` | Name of the topic and parent subject (`Mathematics`, `Physics`, `Chemistry`). |
| `core1a_subtitle` | 3-6 word subtitle focusing on the core inferential leap. |
| `conventions` | Declared invariants (rules, reference frames, signs, or domains) required before evaluation. |
| `concept_difficulty` | Intrinsic badge: `EASY`, `MEDIUM`, or `HARD` (depth follows the concept's nature). |
| `cognitive_demand` | One of the 9 canonical demand keys: `CONCEPTUAL_EXPLANATION` (💡), `PROOF_DERIVATION` (📐), `MULTISTEP_REASONING` (⛓️), `REPRESENTATION_TRANSLATION` (📊), `QUANTITATIVE_APPLICATION` (🧮), `MEMORY_RECALL` (🧠), `EXPERIMENTAL_REASONING` (🔬), `ESTIMATION_LIMITS` (⚖️), `CLASSIFICATION_PATTERN` (🗂️). |
| `review_template_ref` | Review rubric ID (e.g. `CRT-PHY-CONSTRUCTION`, `CRT-MAT-CONSTRUCTION`). |
| `demand_scaffolding` | 4 cognitive variables: `x` (target concept), `y` (entry foundation), `z` (inferential jump), `w` (exit verification). |
| `entry_assumptions` | Array of prerequisite capabilities or existing 1D/elementary models required. |
| `inferential_jump` | The precise difficult transition or key theorem being constructed. |
| `steps` | Logical construction steps (`is_crux_step`, `action`, `why_valid`, `state_output`). |
| `governing_equation` | KaTeX equation in standard `\\[ ... \\]` or `$$ ... $$` delimiters with validity conditions. |
| `svg_body` & `stage_ids` | Staged SVG with `<g data-g9-stage-id="s1">`, `<g data-g9-stage-id="s2">`, etc., with prev/next buttons. |
| `worked_problem_stem` | Authentic anchor problem with numbered working steps and verified conclusion. |
| `trap_wrong_idea` | Plausible misconception, with diagnostic question and pedagogical repair. |
| `triad_check` / `apply` / `connect` | 1-2-3 Triad: 1. Check (recall), 2. Apply (minimal case), 3. Connect (forward transfer). |
| `exit_task` | "Try it with less support" observable exit task with attempt-first gating, model answer, and independent check. |
| `core2_practice_links` | Direct navigation links to corresponding practice questions in Core 2. |

---

## 3. Cognitive Demand Scaffolding in Construction ($X, Y, Z, W$)

In Core 1A, the cognitive scaffolding maps directly to the constitutional learning contract:
- **$X$ (Target Concept / Inference)**: The core concept being constructed (`microtopic.title` / target quantity or theorem).
- **$Y$ (Entry Foundation / Assumptions)**: The entry assumptions required (`microtopic.entry_assumptions[]` / declared conventions).
- **$Z$ (Inferential Jump / Crux Deduction)**: The exact inferential jump (`microtopic.inferential_jump` / crux construction step).
- **$W$ (Exit Criterion / Observable Verification)**: The observable exit task and independent self-check (`microtopic.exit_task` & `relation.checks[]`).

---

## 4. Autonomous Generator Script

An agent creates `payload.json` containing the dictionary of fields and runs:
```bash
python template/core1a-construction/generate_core1a.py \
  --payload my-topic.json \
  --output public/mathematics/my-topic/core1a.html
```
*(The compiler outputs to `public/` and mirrors bit-for-bit to `docs/`, passing all 6 CI suites)*.
