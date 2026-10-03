# QRT Pilot Authoring and Quality Review: Grade 9 Mathematics (Surface Areas and Volumes)

**Authority**: GitHub Issue #13 (`reallaksh19/Grade9v3.5/issues/13`), executed under PR #9 authority on branch `feat/issue-6-qrt-matrix-isolated`.  
**Product ID**: `PRODUCT-MAT-G9-SAV`  
**Topic**: Surface Areas and Volumes (CBSE Grade 9 Mathematics Mensuration)  
**Status**: `PILOT_ONLY_NOT_CANONICAL` (Submitted for Human Audit and Review; explicitly **not** self-certified for release).

---

## 1. Owner Clarifications

In accordance with `docs/method/QRT-SHORT-PROMPT.md` and `Shared/workflows/qrt-short-prompt.v1.json`, the initial short-prompt request (`tests/fixtures/quality/qrt-short-prompt-surface-areas-volumes.v1.json`) contained only the subject, grade, topic, question stems, and requested outputs (`LEARNER_HTML`, `QRT_EVIDENCE`). Running `Shared/tools/qrt_short_prompt.py plan` identified three required owner inputs:

### Clarification 1: `LEARNER_PROFILE`
- **Workflow Query**: *"What does the learner already know for this topic? Give idea-level DEMONSTRATED / UNCERTAIN / MISSING states, or explicitly choose USE_DEFAULT_GENERIC."*
- **Owner Resolution**: The learner possesses full foundational mastery of prerequisite spatial and mensuration concepts. All 8 candidate mensuration capabilities are assigned status `DEMONSTRATED` (`knowledge_percentage: 100`, support posture: `STANDARD`).
- **Profile Record**: Created and persisted at `evidence/reviews/surface-areas-and-volumes/learner-profile.v1.json` (`profile_id: "PROFILE-MAT-SAV-OWNER-DEMONSTRATED"`):
  - `CAP-MAT-SAV-CUBE-CUBOID`: `DEMONSTRATED`
  - `CAP-MAT-SAV-CYLINDER`: `DEMONSTRATED`
  - `CAP-MAT-SAV-OPEN-CONTAINER`: `DEMONSTRATED`
  - `CAP-MAT-SAV-CONE-SLANT`: `DEMONSTRATED`
  - `CAP-MAT-SAV-SPHERE-HEMISPHERE`: `DEMONSTRATED`
  - `CAP-MAT-SAV-COMPOSITE-SOLIDS`: `DEMONSTRATED`
  - `CAP-MAT-SAV-RECASTING-VOLUME`: `DEMONSTRATED`
  - `CAP-MAT-SAV-PROPORTIONAL-REASONING`: `DEMONSTRATED`

### Clarification 2: `QUESTION_PROVENANCE`
- **Workflow Query**: *"Are these questions OWNER_SUPPLIED, AUTHORED_PRACTICE, copied from an EXTERNAL_SOURCE, or ADAPTED from a source?"*
- **Owner Resolution**: `OWNER_SUPPLIED`.
- **Custody Policy**: Custody class assigned as `OWNER_SUPPLIED_RAW_INPUT` with `wording_custody: "VERBATIM"`. The repository preserves verbatim phrasing without inventing external exam identity, year, or syllabus source claims.

### Clarification 3: `PRODUCT_INTENT`
- **Workflow Query**: *"Should these be preserved as owner/source questions (PRESERVE_OWNER_QUESTIONS) or treated as authored practice (AUTHORED_PRACTICE)?"*
- **Owner Resolution**: `PRESERVE_OWNER_QUESTIONS`.
- **Routing Decision**: Routed to Core 2 (`BP-CORE2-SOURCE-QUESTION@1.5.0`) to safeguard source wording and pre-attempt boundaries. In addition, companion Core 1A (`BP-CORE1A-CONSTRUCTION@1.4.0`) was generated to deliver the prerequisite teaching reference depth, concept links, and geometric representations mandated by Blueprint 1.9.

---

## 2. Agent-Derived Decisions and Rationales

Under the short-prompt contract, the agent autonomously derived all mathematical, cognitive, and structural attributes without prompting the human owner:

### 2.1 Mathematical Solutions & Reasoning Chains
Each of the 10 questions was solved, verified, and structured into a formal multi-step reasoning route with an explicit crux move (`crux_move_ref`) and independent checks:

1. **Q1 (Cube TSA)**:
   - Route: Identify 6 congruent square faces ($A = a^2$); substitute $a = 7\text{ cm}$ into $\text{TSA} = 6a^2 = 6 \times 49 = 294\text{ cm}^2$.
   - Crux move: `Q1-M2` (substituting edge length into total surface area formula).
2. **Q2 (Cylinder Diameter Trap)**:
   - Route: Recognize that diameter $d = 14\text{ cm}$ requires calculating radius $r = d/2 = 7\text{ cm}$; evaluate $\text{CSA} = 2\pi r h = 2 \times \frac{22}{7} \times 7 \times 20 = 880\text{ cm}^2$.
   - Crux move: `Q2-M1` (converting diameter to radius before formula substitution).
3. **Q3 (Open Cylindrical Bucket)**:
   - Route: Analyze surface composition of an open bucket (curved surface plus bottom circular base, omitting top); compute $\text{CSA} = 2\pi(7)(18) = 792\text{ cm}^2$ and base $\pi(7)^2 = 154\text{ cm}^2$; sum to obtain $946\text{ cm}^2$.
   - Crux move: `Q3-M1` (formulating boundary model: $\text{CSA} + 1\text{ base}$).
4. **Q4 (Conical Tent Slant Height & Canvas)**:
   - Route: Apply Pythagorean theorem to right-angled generator triangle: $l = \sqrt{r^2 + h^2} = \sqrt{7^2 + 24^2} = \sqrt{625} = 25\text{ m}$; calculate open base canvas area $\text{CSA} = \pi r l = \frac{22}{7} \times 7 \times 25 = 550\text{ m}^2$.
   - Crux move: `Q4-M2` (synthesizing Pythagorean slant height with conical lateral area).
5. **Q5 (Hemispherical Bowl Inner Surface Area)**:
   - Route: Identify hollow bowl geometry where the circular lip is the open boundary; compute inner curved surface area $2\pi r^2 = 2 \times \frac{22}{7} \times (10.5)^2 = 693\text{ cm}^2$; state warrant why flat circular face is not included.
   - Crux move: `Q5-M1` (distinguishing inner open bowl surface from closed solid hemisphere).
6. **Q6 (Composite Toy: Cone on Hemisphere)**:
   - Route: Determine conical slant height $l = \sqrt{(3.5)^2 + 12^2} = 12.5\text{ cm}$; calculate exposed conical surface $\pi r l = 137.5\text{ cm}^2$; calculate exposed hemispherical surface $2\pi r^2 = 77\text{ cm}^2$; sum exposed areas to obtain $214.5\text{ cm}^2$; exclude internal joint face.
   - Crux move: `Q6-M1` (modeling exposed boundary by subtracting hidden circular interface).
7. **Q7 (Painted Open Cylinder)**:
   - Route: Decompose exterior painted envelope into outer curved surface ($2\pi r h = 2 \times \frac{22}{7} \times 7 \times 25 = 1100\text{ cm}^2$) and outer bottom base ($\pi r^2 = 154\text{ cm}^2$); justify exclusion of open top; total painted area $= 1254\text{ cm}^2$.
   - Crux move: `Q7-M1` (justifying surface selection based on physical contact constraints).
8. **Q8 (Rectangular Tank Capacity & Unit Conversion)**:
   - Route: Compute geometric volume $V = l \times w \times h = 2 \times 1.5 \times 1.2 = 3.6\text{ m}^3$; translate cubic metres to litres using $1\text{ m}^3 = 1000\text{ L}$ to obtain $3600\text{ L}$; calculate 75% fill capacity: $0.75 \times 3600 = 2700\text{ L}$.
   - Crux move: `Q8-M2` (representation translation between metric volume and volumetric liquid capacity).
9. **Q9 (Recasting Solid Metallic Sphere)**:
   - Route: Formulate volume conservation principle ($V_{\text{initial}} = N \times V_{\text{small}}$); compute sphere count $N = (R/r)^3 = (6/2)^3 = 27$; analyze surface area ratio: $S_{\text{total}} = 27 \times 4\pi(2)^2 = 432\pi\text{ cm}^2$ versus $S_{\text{initial}} = 4\pi(6)^2 = 144\pi\text{ cm}^2$; prove surface area expands by a factor of 3 during division.
   - Crux move: `Q9-M2` (establishing invariant volume conservation alongside non-conservation of surface area).
10. **Q10 (Cone vs Cylinder Volume Invariant)**:
    - Route: State geometric volume formulas for shared radius and height: $V_{\text{cylinder}} = \pi r^2 h$ and $V_{\text{cone}} = \frac{1}{3}\pi r^2 h$; derive direct ratio $V_{\text{cone}} = \frac{1}{3} V_{\text{cylinder}}$; substitute $924\text{ cm}^3$ to obtain $308\text{ cm}^3$; justify why individual determination of $r$ and $h$ is mathematically redundant.
    - Crux move: `Q10-M2` (applying ratio invariant without resolving intermediate dimensional parameters).

### 2.2 Cognitive Demand & 5-Component Difficulty Classification
Each question was classified across the 7 orthogonal cognitive demands and scored across the 5 repository difficulty axes (`concept_model_selection`, `representation_translation`, `reasoning_chain_length`, `algebra_computational_load`, `trap_exception_sensitivity`):

| Question | Primary Demand | D-Band | Difficulty Score | Difficulty Vector `(c, r, l, a, t)` | Crux Focus |
|---|---|---|---|---|---|
| **Q1** | `APPLY` | **D1** | 1 | `(0, 0, 0, 1, 0)` | Routine execution of $6a^2$ |
| **Q2** | `APPLY` | **D2** | 2 | `(0, 0, 0, 1, 1)` | Diameter-to-radius trap execution |
| **Q3** | `MODEL` | **D2** | 3 | `(1, 0, 1, 1, 0)` | Open boundary model ($\text{CSA} + 1\text{ base}$) |
| **Q4** | `SYNTHESIZE` | **D3** | 5 | `(1, 0, 2, 1, 1)` | Slant height synthesis + conical lateral area |
| **Q5** | `EXPLAIN` | **D2** | 2 | `(0, 0, 1, 1, 0)` | Boundary rationale for open hemispherical bowl |
| **Q6** | `MODEL` | **D3** | 5 | `(2, 0, 1, 1, 1)` | Composite solid joint elimination |
| **Q7** | `JUSTIFY` | **D2** | 3 | `(1, 0, 1, 1, 0)` | Warrants for selective surface painting |
| **Q8** | `REPRESENT` | **D2** | 3 | `(0, 1, 1, 1, 0)` | $\text{m}^3 \to \text{L}$ representation bridge |
| **Q9** | `JUSTIFY` | **D3** | 5 | `(1, 0, 2, 1, 1)` | Invariant volume vs non-conserved surface area |
| **Q10** | `EXPLAIN` | **D2** | 3 | `(1, 0, 1, 1, 0)` | Proportional volume reasoning without variables |

### 2.3 Microtopics & Architectural Decoupling
To satisfy metadata projection constraints in `render_core` and `learner_metadata.py`, 8 distinct microtopics were authored in `Mathematics/library/surface-areas-and-volumes.v1.json`, mapping 1-to-1 to each primary capability:
- `MIC-MAT-SAV-CUBE-CUBOID` $\to$ `CAP-MAT-SAV-CUBE-CUBOID`
- `MIC-MAT-SAV-CYLINDER` $\to$ `CAP-MAT-SAV-CYLINDER`
- `MIC-MAT-SAV-OPEN-CONTAINER` $\to$ `CAP-MAT-SAV-OPEN-CONTAINER`
- `MIC-MAT-SAV-CONE-SLANT` $\to$ `CAP-MAT-SAV-CONE-SLANT`
- `MIC-MAT-SAV-SPHERE-HEMISPHERE` $\to$ `CAP-MAT-SAV-SPHERE-HEMISPHERE`
- `MIC-MAT-SAV-COMPOSITE-SOLIDS` $\to$ `CAP-MAT-SAV-COMPOSITE-SOLIDS`
- `MIC-MAT-SAV-RECASTING-VOLUME` $\to$ `CAP-MAT-SAV-RECASTING-VOLUME`
- `MIC-MAT-SAV-PROPORTIONAL-REASONING` $\to$ `CAP-MAT-SAV-PROPORTIONAL-REASONING`

### 2.4 Authored Geometric SVG Representations
To ensure reference-depth visual teaching, 8 clean, proportional SVG illustrations were authored and placed in `Mathematics/assets/representations/`:
1. `REP-MAT-SAV-CUBE.svg`: Isometric cube with edge $a = 7\text{ cm}$ and face area annotations.
2. `REP-MAT-SAV-CYLINDER.svg`: Cylinder with diameter $14\text{ cm}$, radius $7\text{ cm}$, height $20\text{ cm}$.
3. `REP-MAT-SAV-OPEN-CONTAINER.svg`: Open-top bucket showing solid base and open top boundary.
4. `REP-MAT-SAV-CONE-SLANT.svg`: Conical tent with internal right triangle showing $r=7\text{ m}, h=24\text{ m}, l=25\text{ m}$.
5. `REP-MAT-SAV-HEMISPHERE.svg`: Hemispherical bowl cross-section illustrating inner curved surface.
6. `REP-MAT-SAV-COMPOSITE-SOLIDS.svg`: Composite toy with mounted cone on hemisphere, highlighting hidden joint.
7. `REP-MAT-SAV-RECASTING-VOLUME.svg`: Recasting transformation from large sphere ($R=6\text{ cm}$) to 27 small spheres ($r=2\text{ cm}$).
8. `REP-MAT-SAV-PROPORTIONAL-REASONING.svg`: Shared base and height cylinder and inscribed cone demonstrating $1/3$ volume invariant.

---

## 3. Evidence and Custody Records

### 3.1 Primary File Paths
- **Owner Bank**: `Mathematics/question-bank/surface-areas-and-volumes.owner-bank.v1.json`
- **Library Package**: `Mathematics/library/surface-areas-and-volumes.v1.json`
- **Product Manifest**: `products/mathematics/surface-areas-and-volumes.manifest.json`
- **Learner Profile**: `evidence/reviews/surface-areas-and-volumes/learner-profile.v1.json`
- **Staged Render Directory**: `publication/mathematics/surface-areas-and-volumes/`
  - `core2.html` (166,846 bytes)
  - `core1a.html` (64,960 bytes)
  - `index.html` (1,677 bytes)
  - `render-receipt.json` (721 bytes)
- **Quality Gate Report**: `evidence/reviews/surface-areas-and-volumes/quality-gate-report.json`
- **QRT Review Evidence**: `evidence/reviews/surface-areas-and-volumes/qrt-review-evidence.v1.json`

### 3.2 Verbatim Stem Integrity & Cryptographic Custody Table
All 10 question texts match `tests/fixtures/quality/qrt-short-prompt-surface-areas-volumes.v1.json` verbatim:

| ID | Verbatim Stem Text | Text SHA-256 Digest | Status |
|---|---|---|---|
| **Q1** | `A wooden cube has edge length 7 cm. Find its total surface area.` | `6473d09a0b1cecb5f78a2e7ba1e05d0d6e6a1795ea364ae022137941ca50d996` | Verified Verbatim |
| **Q2** | `A cylindrical water bottle has diameter 14 cm and height 20 cm. Find its curved surface area.` | `fe5d447a1ea49bc2fe0d8858a8a3ee2643a6d71b3e9a7e6717a027e163b4feec` | Verified Verbatim |
| **Q3** | `A cylindrical bucket is open at the top. Its internal radius is 7 cm and its height is 18 cm. Find the area of metal sheet required to make the bucket, ignoring the thickness of the sheet.` | `919b5e5ae16ea41aa8ce04bf604cf3e4e97664c39dc08ba72c05e1975e5c7075` | Verified Verbatim |
| **Q4** | `A conical tent has radius 7 m and vertical height 24 m. Find its slant height and the area of canvas required to make the tent. The base is open.` | `9d554a938c4c7ccfa1082c9f57ebbf74d1566cf2c27cf2cb7e0dc752c00228bb` | Verified Verbatim |
| **Q5** | `A hemispherical bowl has radius 10.5 cm. Find the area of its inner surface and explain why the circular base is not included.` | `4efcb092a781ce7210e756cb87ba35f7ba1c205c062828b031fa1f17fe68eb72` | Verified Verbatim |
| **Q6** | `A toy is made by mounting a cone on a hemisphere. Both have radius 3.5 cm and the cone has vertical height 12 cm. Find the total exposed surface area; the circular joining face is hidden.` | `655aebf13a0765aa5ff899a13bf782c5f949c81152a233bfe68bb38059cb2cfc` | Verified Verbatim |
| **Q7** | `A cylindrical vessel of radius 7 cm and height 25 cm is open at the top. Paint the outer curved surface and outside circular base only. Find the painted area and state which surfaces are included.` | `d419ca9d9cb4ce33db9b6408226e6378e99fb1b4f4c82c35e5d3ea2d3b2e7dd9` | Verified Verbatim |
| **Q8** | `A rectangular water tank is 2 m long, 1.5 m wide and 1.2 m deep. It is filled to 75 percent of capacity. How many litres of water does it contain? Show the unit conversion.` | `448ec62e60447be380df1e155452f3607fa6d376ca78571faeb6a297e68cfb39` | Verified Verbatim |
| **Q9** | `A solid metallic sphere of radius 6 cm is melted and recast into identical solid spheres of radius 2 cm with no loss. How many small spheres are formed? Explain why surface area is not conserved.` | `c687e14e1a74288dc73685d301bdf28174f85e4d29f864fa9cf0dd622ae6d6b5` | Verified Verbatim |
| **Q10** | `A cone and a cylinder have the same base radius and height. The cylinder volume is 924 cubic centimetres. Find the cone volume and explain why radius and height need not be calculated separately.` | `f6a41fdfbf392ddbc8301548a86a7bc37ffbe7f05814521482ce0fcb7d612e4f` | Verified Verbatim |

---

## 4. Execution Record

### 4.1 Artifact Compilation & Schema Validation
- Script `scratch/update_pilot_full.py` executed to compile records:
  - `surface-areas-and-volumes.owner-bank.v1.json` validated via `Shared/tools/owner_bank.py check`: **OK**.
  - `surface-areas-and-volumes.v1.json` validated via `Draft202012Validator`: **0 errors**.
  - `products/mathematics/surface-areas-and-volumes.manifest.json` configured for roles `["CORE2", "CORE1A"]`.

### 4.2 Renderer Invocation
- Staged render built cleanly using `Shared/tools/render_core.py`:
  ```bash
  python Shared/tools/render_core.py build products/mathematics/surface-areas-and-volumes.manifest.json \
    --output publication/mathematics/surface-areas-and-volumes
  ```
- Result:
  - `wrote 3 page(s) to publication\mathematics\surface-areas-and-volumes`
  - `0 depth gaps; 8 subject-authority findings` (advisory catalog relation alerts).
  - Render stamp: `render_core/2 68777f61f64a0bbd`

---

## 5. Quality Gate and QRT Review Record

### 5.1 Real Quality Gate Output
```bash
python Shared/tools/quality_gate.py publication/mathematics/surface-areas-and-volumes \
  --subject Mathematics \
  --product-id PRODUCT-MAT-G9-SAV \
  --static \
  --report evidence/reviews/surface-areas-and-volumes/quality-gate-report.json
```
- **Findings Summary**:
  - `S0 (Blocking falsehood / broken render)`: 0
  - `S1 (Major instructional defect / spoiler)`: 0
  - `S2 (Design violation)`: 0
  - `S3 (Advisory)`: 0
  - `Continuity breaks`: 0
- **Verdict**: `FAIL (RENDERED_RULES_NOT_MEASURED)`. As documented in Blueprint 1.9, running `--static` flags that headless Chromium layout measurements were intentionally omitted, while confirming 100% structural and rule compliance across all evaluated checks.

### 5.2 QRT Matrix Resolution & Semantic Review Outcomes
Evaluating all 10 questions against `PROFILE-MAT-SAV-OWNER-DEMONSTRATED`, `question-demand-matrix.v1.json`, and `Mathematics/adapter/DemandReview.json` exercised **7 distinct matrix templates** across 6 cognitive demands:

| Question | Resolved Cell | Primary Demand | Band | P1 (Pre-Attempt) | P2 (Concept Link) | P3 (Why Valid & Check) | S1–S3 (Visuals) | H1–H3 (Hints) | M1–M3 (Misconception) |
|---|---|---|---|---|---|---|---|---|---|
| **Q1** | `QRT-APPLY-D1` | `APPLY` | D1 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q2** | `QRT-APPLY-D2` | `APPLY` | D2 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q3** | `QRT-MODEL-D2` | `MODEL` | D2 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q4** | `QRT-SYNTHESIZE-D3` | `SYNTHESIZE` | D3 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q5** | `QRT-EXPLAIN-D2` | `EXPLAIN` | D2 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q6** | `QRT-MODEL-D3` | `MODEL` | D3 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q7** | `QRT-JUSTIFY-D2` | `JUSTIFY` | D2 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q8** | `QRT-REPRESENT-D2` | `REPRESENT` | D2 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q9** | `QRT-JUSTIFY-D3` | `JUSTIFY` | D3 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |
| **Q10** | `QRT-EXPLAIN-D2` | `EXPLAIN` | D2 | **YES** | **YES** | **YES** | PARTLY (Core1A) | NO (delegated) | NO (metadata only) |

- **Summary of Semantic Asks**:
  - **P1 (Protected Pre-Attempt)**: `YES` across all 10 items. Complete solutions and answers are concealed within `<details data-requires-attempt="true">`.
  - **P2 (Concept Routing)**: `YES` across all 10 items. Explicit `<a class="g9-concept-link" href="core1a.html#MIC-...">` links land directly on the relevant microtopic construction unit.
  - **P3 (Validity & Verification)**: `YES` across all 10 items. Every solution step incorporates structured "Why valid" reasoning and independent multi-point checks (`UNITS`, `SUBSTITUTION_BACK_CHECK`, `DOMAIN_CHECK`).
  - **S1–S3 (Spatial Representations)**: `PARTLY` (severity S3). 8 high-fidelity SVG figures exist in companion `core1a.html`, but are not inlined in `core2.html` problem stems.
  - **H1–H3 (Scaffolded Hints)**: `NO` (severity S2). Core2 source-question blueprint presents verbatim owner questions without multi-rung hint ladders; scaffolding is delivered via Core1A.
  - **M1–M3 (Misconception Diagnosis & Repair)**: `NO` (severity S2). Detailed misconception patterns and replacement rules are encoded in library metadata and subject adapters, but not surfaced as inline interactive widgets in Core2.

### 5.3 Product Review v2 Evidence
- Fully validated against `Shared/quality/product-review.schema.json` with **0 schema errors**.
- Encapsulated in `evidence/reviews/surface-areas-and-volumes/qrt-review-evidence.v1.json`.

---

## 6. Deviation Log

During execution, six technical deviations from initial assumptions were encountered and resolved:

1. **Output Directory Boundary Policy**:
   - *Issue*: `render_core.py` deliberately blocks builds pointing to `public/...` (`ValueError: render_core cannot write to public; use Owner acceptance of a staged render`).
   - *Resolution*: Staged render output in `publication/mathematics/surface-areas-and-volumes/` as mandated by governance.
2. **Shell Header Contract Regression**:
   - *Issue*: An earlier workspace commit had modified `<header data-g9-shell-header>` in `Shared/tools/render_core.py` to `<header class="g9-shell-header">` and altered action button placement, causing `PAGE-SHELL` and `PAGE-HOME-LINK` gate failures and 3 unit test failures.
   - *Resolution*: Restored exact Blueprint 1.9 markup (`<header data-g9-shell-header>`, `data-g9-home`, `data-g9-action="pdf"`, PDF button preceding search button).
3. **Microtopic One-to-One Capability Mapping**:
   - *Issue*: Single-microtopic packaging caused `learner_metadata.project` to report `C2-METADATA: missing primary_capability_ref` for questions mapped to secondary capabilities.
   - *Resolution*: Authored 8 distinct microtopics (one per capability), providing clean 1-to-1 capability-to-microtopic projection.
4. **Vocabulary Conformance for Mathematics Representations**:
   - *Issue*: Package initially declared `representation_kind: "GEOMETRIC_DIAGRAM"`, which was rejected by `Mathematics/adapter/QualityVocabulary.json`.
   - *Resolution*: Corrected kind to `"GEOMETRIC_FIGURE"`.
5. **Strict MathML Subset Formatting**:
   - *Issue*: `_safe_mathml` in `render_core.py` rejected HTML entities (`&pi;`), `<mspace>`, and non-whitelisted attributes (`stretchy`).
   - *Resolution*: Replaced with literal UTF-8 `π`, standard `<mrow><mi>π</mi></mrow>`, and eliminated non-whitelisted tags/attributes.
6. **Reference Benchmark Depth Compliance**:
   - *Issue*: Core 1A construction units initially raised advisory S3 depth warnings due to having only 1 independent check.
   - *Resolution*: Enriched all 8 construction units with 3 independent checks (`UNITS`, `SUBSTITUTION_BACK_CHECK`, `DOMAIN_CHECK`), fully clearing all S3 gate findings.

---

## 7. Final Traceability & Limitations

### 7.1 Git Traceability
- **Branch**: `feat/issue-6-qrt-matrix-isolated`
- **Tracked Changes**:
  - `Mathematics/question-bank/surface-areas-and-volumes.owner-bank.v1.json`
  - `Mathematics/library/surface-areas-and-volumes.v1.json`
  - `Mathematics/assets/representations/*.svg` (8 files)
  - `products/mathematics/surface-areas-and-volumes.manifest.json`
  - `evidence/reviews/surface-areas-and-volumes/learner-profile.v1.json`
  - `evidence/reviews/surface-areas-and-volumes/quality-gate-report.json`
  - `evidence/reviews/surface-areas-and-volumes/qrt-review-evidence.v1.json`
  - `publication/mathematics/surface-areas-and-volumes/*` (`core2.html`, `core1a.html`, `index.html`, `render-receipt.json`)
  - `docs/method/QRT-PILOT-SURFACE-AREAS-VOLUMES.md`

### 7.2 Non-Self-Certification Statement
> [!IMPORTANT]
> **Explicit Non-Self-Certification**: This pilot authoring, rendering, and quality review is presented strictly as **provisional audit evidence** for human owner inspection under GitHub Issue #13 and PR #9 authority. The agent assistant does **not** self-certify this product for production release. Acceptance and promotion to `public/` require formal human review and execution of `Shared/tools/accept_product.py`.
