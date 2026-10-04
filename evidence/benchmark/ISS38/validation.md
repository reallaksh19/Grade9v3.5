# Validation Ledger — Issue #38 (Independent Candidate B)

- **Issue:** #38 · D4 hybridisation · Q1–Q10 · Independent Agent B
- **Launch commit:** `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`
- **Execution environment:** Local Python 3.12 / PowerShell on Windows
- **Renderer authority:** `Shared/tools/render_core.py`
- **Render receipt digest:** `80020d803ce7d42c`
- **Semantic digest:** `45183d52aec9ab21`

---

## 1. Input Hashes & Intake Verification

| Target | Expected SHA-256 | Actual SHA-256 | Verdict |
|---|---|---|---|
| Whole issue body | `6e05f53a3a8c3958210a69f99a18666d5bc2b46c832aeb550a0bc40093119850` | `6e05f53a3a8c3958210a69f99a18666d5bc2b46c832aeb550a0bc40093119850` | PASS |
| A/B/C core prompt | `52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7` | `52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7` | PASS |
| Stem Q1 | `d44703bf...` | `d44703bfb70cbeec7374a2aa484fa2d884784bdfc9197c312cfeb61e9da74df6` | PASS |
| Stem Q2 | `e77d068e...` | `e77d068e91888e22c92e9e623eb64f7831518f9a2d3fa6e4df9da16ea0dd7cb8` | PASS |
| Stem Q3 | `2ea9cdfb...` | `2ea9cdfb6dafe556f8f553f191b7e6f9872fbddf234bf99d52eb93e03d42e612` | PASS |
| Stem Q4 | `a5bd1762...` | `a5bd17629b3f024765360f06a12555bb0a221f7db9783f98c8c279dd727be082` | PASS |
| Stem Q5 | `7fa193cc...` | `7fa193cc5410915664db803833b7ba8a834924c8b9b8b8d0092c43c16a695b06` | PASS |
| Stem Q6 | `07e8eecc...` | `07e8eecc0364d9522199b5e5df84b80b2d69f0e13eb9e0ef73fa60911762b921` | PASS |
| Stem Q7 | `c695e46f...` | `c695e46f0c7df2559b952f4cfa0d65b7966efbf37c6ae3f3a8b42fc06ee429d2` | PASS |
| Stem Q8 | `706e9521...` | `706e952179b4e72750e2ef64d7df6307399589d9796ff0bcf2e20ffc030c6a8f` | PASS |
| Stem Q9 | `7ef3b550...` | `7ef3b550ffda6d6dd033fe9cfc3eb3bfd06079c65609fffc92eebc69f2130e99` | PASS |
| Stem Q10 | `dfef0e64...` | `dfef0e64860b29841c6f4a86fc01c402179d6756bf0dbd6d9da49301908ddae4` | PASS |

---

## 2. Governed Pipeline Prechecks & Gaps

| Check | Tool / Command | Output / Status | Verdict |
|---|---|---|---|
| Package Schema | `Draft202012Validator(package.schema.json)` | 0 schema validation errors | PASS |
| Owner Bank Schema & Custody | `python Shared/tools/owner_bank.py check` | `evidence/benchmark/ISS38/generated/owner.bank.json: OK` | PASS |
| Product Manifest Resolver | `render_core.py product_manifest.derivable` | All microtopics and core2 questions resolved cleanly | PASS |
| Renderer Gaps | `python Shared/tools/render_core.py gaps` | `0 depth gap(s); 0 subject-authority finding(s)` | PASS |
| Production Render | `python Shared/tools/render_core.py build` | `wrote 3 page(s)` (draft: false) | PASS |

---

## 3. Rendered Deliverable Headroom & File Metrics

| File | Size (bytes) | Headroom / Metrics |
|---|---|---|
| `evidence/benchmark/ISS38/rendered/core1a.html` | `115579` | 3 staged figures, 3 construction units, exit tasks, worked anchors, independent checks |
| `evidence/benchmark/ISS38/rendered/core2.html` | `253348` | 10 full owner questions, 5 scaffolds per question, 4 reasoning moves per question, 10 figures |
| `evidence/benchmark/ISS38/rendered/index.html` | `20929` | Navigation hub linking Core1A and Core2 |
| `evidence/benchmark/ISS38/rendered/render-receipt.json` | `437` | Digest `80020d803ce7d42c`, draft `false`, gaps `[]` |

---

## 4. Academic & Matrix Verification

- **10/10 questions** independently solved with detailed reasoning routes and cross-checks.
- **Difficulty:** 8 D4 + 2 D3. Q6 and Q7 are evaluated at D3 (score 6/10) and preserved honestly without inflation.
- **Cognitive Demands:** Exactly one primary cognitive demand assigned per question:
  - `MODEL`: Q1
  - `REPRESENT`: Q2, Q7
  - `EXPLAIN`: Q3, Q6
  - `SYNTHESIZE`: Q4, Q10
  - `JUSTIFY`: Q5, Q8
  - `APPLY`: Q9
- **Canonical 28-cell QRT Matrix:** Exactly **8 distinct cells** populated with grounded evidence (`MODEL-D4`, `REPRESENT-D4`, `EXPLAIN-D4`, `SYNTHESIZE-D4`, `JUSTIFY-D4`, `EXPLAIN-D3`, `REPRESENT-D3`, `APPLY-D4`).
- **H1–M3 semantic verdicts:** All 10 questions achieve YES on all 12 review facets (H1-H3, S1-S3, P1-P3, M1-M3).

---

## 5. Independence Statement

Matched issue #37 (independent candidate A) and its branch were **NOT inspected** at any point prior to freezing this candidate.
