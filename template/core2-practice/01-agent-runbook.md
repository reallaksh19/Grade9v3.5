# Core 2 Practice & Question Custody Agent Runbook

This guide enables any autonomous agent to produce a gold-standard **Core 2: Question Custody & Guided Practice** page that strictly adheres to the repository's constitutional specification (`Shared/roles/CORE2.md` and `BP-CORE2-SOURCE-QUESTION@1.5.0`).

---

## 1. The Core 2 Constitutional Philosophy
* **Preserve Source Custody**: Questions are never invented. Use exact textbook/exam wording, numbering, conditions, and diagrams.
* **Hard Attempt-First Gate**: Answers and teacher workings are locked until the learner inputs an answer or confirms "I worked this out on paper".
* **Progressive Hint Ladder**: Guided help is revealed one rung at a time (`H0 Representation`, `H1 Key Concept`, `H2 Crux`). Rungs remain as ghost previews until unlocked.
* **5-Axis Difficulty Disclosure**: Every question explains *why* it has its difficulty band across 5 dimensions (model, representation, reasoning chain, math, traps).
* **Structured Reasoning Route**: Solutions are not monolithic paragraphs. They are numbered moves (Action, Uses, Why Valid, Result, with Crux highlighted).
* **Direct Concept Navigation**: Includes a 1-click bridge back to the matching concept unit in Core 1A.

---

## 2. Fill-in-the-Blanks Slots (16 Blueprint Components)

| Slot | Field Name | Description & Requirement |
|---|---|---|
| **1** | `source_title` & `provenance` | Exact exam citation (e.g. `IIT-JEE · 2007 · Paper I · Q10` or `Check Point 2 · Q10`). |
| **2** | `pdf_url` (optional) | Direct link to official source PDF. |
| **3** | `cognitive_demand` | One of the 9 canonical demand keys: `MEMORY_RECALL` (🧠), `CONCEPTUAL_EXPLANATION` (💡), `QUANTITATIVE_APPLICATION` (🧮), `MULTISTEP_REASONING` (⛓️), `REPRESENTATION_TRANSLATION` (📊), `EXPERIMENTAL_REASONING` (🔬), `ESTIMATION_LIMITS` (⚖️), `PROOF_DERIVATION` (📐), `CLASSIFICATION_PATTERN` (🗂️). |
| **4** | `review_template_ref` | Review rubric ID (e.g. `QRT-PHY-MEMORY`, `QRT-PHY-MULTISTEP`, `QRT-MAT-PROOF`). |
| **5** | `demand_scaffolding` | Scaffolding variables: `x` (target concept/quantity), `y` (related foundation), `z` (crux retrieval path), `w` (final step left to student). |
| **6** | `difficulty_grid` | 5 scores (0–2) for model, representation, chain, math, and traps. Total score determines band $D_1 \dots D_4$. |
| **7** | `stem` | Verbatim problem statement with KaTeX math delimiters (`$...$`). |
| **8** | `conditions` | Explicit list of givens and constraints. |
| **9** | `common_wrong_route` | The tempting mistake or trap path learners take. |
| **10** | `response_type` | `single_choice`, `multiple_choice`, `numeric`, `short_text`, or `free_response`. |
| **11** | `svg_body` | Problem-aligned schematic SVG figure (omit for pure memory recall). |
| **12** | `hint_ladder` | 3 rungs (D1/D2) or 5 rungs (D3/D4) with `label`, `prompt`, and `hint`. H1 clarifies category $X$, H2 correlates $X$ to $Y$, H3 cues retrieval to $Z$ without giving answer. |
| **13** | `core1a_anchor_url` | Direct URL link back to the matching unit in `core1a.html`. |
| **14** | `solution_moves` | 3–4 numbered steps: `stage_label`, `action`, `uses`, `why_valid`, `result`, `is_crux`. |
| **15** | `answer_summary` | Official verified answer in the green highlight box. |
| **16** | `independent_check` | Sanity check, numerical verification, or limiting-case test. |

---

## 3. Cognitive Demand Taxonomy (Bloom & TIMSS Aligned)

Core 2 decouples scalar difficulty ($D_1 \dots D_4$) from qualitative cognitive demand:
- **`MEMORY_RECALL` (🧠 Factual recall)**: Recall of definitions, formulas, units (NCERT Exemplar, foundation questions).
- **`CONCEPTUAL_EXPLANATION` (💡 Conceptual explanation)**: Qualitative understanding of principles without calculations.
- **`QUANTITATIVE_APPLICATION` (🧮 Quantitative calculation)**: Direct algebraic or numerical application of formulas.
- **`MULTISTEP_REASONING` (⛓️ Model & multi-step chain)**: Selecting physical models, chaining kinematics, dynamics, energy.
- **`REPRESENTATION_TRANSLATION` (📊 Representation translation)**: Converting graphs to equations or free-body diagrams.
- **`EXPERIMENTAL_REASONING` (🔬 Experimental & data interpretation)**: Laboratory setups, error bounds, tabular data inference.
- **`ESTIMATION_LIMITS` (⚖️ Estimation & limiting cases)**: Asymptotic behavior ($v \to 0$, $m \to \infty$) and order-of-magnitude tests.
- **`PROOF_DERIVATION` (📐 Proof & formal derivation)**: Rigorous algebraic proofs and formal mathematical derivations.
- **`CLASSIFICATION_PATTERN` (🗂️ Classification & patterns)**: Categorizing motion, reaction mechanisms, or algebraic curves.

---

## 4. Autonomous Generator Script

An agent creates `topic_core2_payload.json` and runs:
```bash
python template/core2-practice/generate_core2.py \
  --payload topic_core2_payload.json \
  --output public/mathematics/my-topic/core2.html
```
*(The compiler outputs to `public/` and mirrors bit-for-bit to `docs/`, passing all 6 CI suites)*.
