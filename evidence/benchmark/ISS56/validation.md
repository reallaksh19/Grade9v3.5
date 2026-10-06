# Validation Ledger — Issue #56 (Independent Candidate B)

- **Issue:** #56 · Polynomial stress test v1 · D4 · Q1–Q10 · Independent Agent B
- **Launch Commit:** `91719ad8df2bfc06c6a481590d2e24c510c24835`
- **Execution Environment:** Windows PowerShell / Python 3.12.14
- **Renderer Authority:** `Shared/tools/render_core.py` (v2)
- **Render Receipt Digest:** `7909c2addb49b09e`
- **Semantic Digest:** `8bbf32b94e60240a`
- **Status:** CANDIDATE

---

## 1. Input Hashes & Intake Verification

| Target | Expected SHA-256 | Actual SHA-256 | Verdict |
|---|---|---|---|
| A/B/C Core Prompt | `46058f7ade3862a6f5707fa0f49c5e284d74b6de56100312d6f1a840d65392b9` | `46058f7ade3862a6f5707fa0f49c5e284d74b6de56100312d6f1a840d65392b9` | PASS |
| Stem Q1 | `e02e5c653b6dcfb9d18d947aa1822cc7b2283c9d2eaf506212c9b42ad0308ba7` | `e02e5c653b6dcfb9d18d947aa1822cc7b2283c9d2eaf506212c9b42ad0308ba7` | PASS |
| Stem Q2 | `39d0b46d0a99c1abf2bc23dd3341168a57f3266a80708505ae6157f365bf8db3` | `39d0b46d0a99c1abf2bc23dd3341168a57f3266a80708505ae6157f365bf8db3` | PASS |
| Stem Q3 | `dc8957c7bdb5e6011083beee02230b04220fac10a7a4160f7569a9fbf6922fe3` | `dc8957c7bdb5e6011083beee02230b04220fac10a7a4160f7569a9fbf6922fe3` | PASS |
| Stem Q4 | `d28d5a24aa86299fc4568717767bd5410f1ba0dd963a758e835322005d644e0b` | `d28d5a24aa86299fc4568717767bd5410f1ba0dd963a758e835322005d644e0b` | PASS |
| Stem Q5 | `9524918a2550cfdbd9ac49e0667b45e5b4428c9ab629c35fb92f9e16b8b4ec77` | `9524918a2550cfdbd9ac49e0667b45e5b4428c9ab629c35fb92f9e16b8b4ec77` | PASS |
| Stem Q6 | `419740a92840120d38694742de086b1252a859def86f8210b661e7628c576bf8` | `419740a92840120d38694742de086b1252a859def86f8210b661e7628c576bf8` | PASS |
| Stem Q7 | `7179b2bb8a15301a553bd1f99c95c924a49f9debf9b9e5ecf0c4fb303fa9094a` | `7179b2bb8a15301a553bd1f99c95c924a49f9debf9b9e5ecf0c4fb303fa9094a` | PASS |
| Stem Q8 | `0618c1769d3974b8366495cfdb2d55b9f40098922efe4d6bd6cf608ce501a500` | `0618c1769d3974b8366495cfdb2d55b9f40098922efe4d6bd6cf608ce501a500` | PASS |
| Stem Q9 | `6217d10f7b4a7a1bc454f160878027bbd35060f1b4c580eedda5400d7c6354f2` | `6217d10f7b4a7a1bc454f160878027bbd35060f1b4c580eedda5400d7c6354f2` | PASS |
| Stem Q10 | `c8e877db99b662cb2ca901cb9ff6acde0ad99db5b2bc06900347d1c7d6671831` | `c8e877db99b662cb2ca901cb9ff6acde0ad99db5b2bc06900347d1c7d6671831` | PASS |

---

## 2. Governed Pipeline Prechecks & Gaps

| Check | Tool / Command | Output / Status | Verdict |
|---|---|---|---|
| Package Schema | `Draft202012Validator(package.schema.json)` | 0 schema validation errors | PASS |
| Owner Bank Schema & Custody | `python -m Shared.tools.owner_bank check` | `Problems found in owner.bank.json: 0` | PASS |
| Product Manifest Resolver | `Shared.tools.render_core.py` manifest loader | 3 microtopics, 10 Core2 questions, 0 Core2a/b resolved | PASS |
| Renderer Gaps | `python Shared/tools/render_core.py gaps` | `0 depth gap(s); 4 subject-authority finding(s)` | PASS |
| Production Render | `python Shared/tools/render_core.py build` | `wrote 3 page(s)` (draft: false) | PASS |

> [!NOTE]
> The 4 subject-authority findings are informational advisory warnings from `Shared/library/authority.py` reflecting that the benchmark package introduces new relations (`REL-MATH-POLY-IDENTITY`, `REL-MATH-ROOT-PARITY`, `REL-MATH-PARAM-DISCRIMINANT`, `REL-MATH-BOX-VOLUME`) which are not yet registered in `Mathematics/gates/` (which baseline currently confines to linear equations). They produce 0 depth gaps and do not impede production rendering.

---

## 3. Rendered Deliverable Headroom & File Metrics

| File | Size (bytes) | SHA-256 Digest | Headroom / Metrics |
|---|---|---|---|
| `rendered/core1a.html` | `116405` | `ad0eda94168d9ef3fac817c2831118c5aadc6964ec2ef2477e2f126232fb9819` | 3 microtopics, 4 staged SVG figures, 3 construction units, exit tasks, worked anchors, independent checks |
| `rendered/core2.html` | `253466` | `5258654f2d5be4ad97b279137a62841c4cec59ec1cd2b2318c3ca636fac9fffd` | 10 full owner questions, 5 scaffolds per question, 4 reasoning moves per question, 10 figures |
| `rendered/index.html` | `22995` | `1321112f3410b75d80bc5ded1afcd371f4754f5ff3760ebf2033ddbca5889682` | Navigation portal linking Core1A and Core2 |
| `rendered/render-receipt.json` | `437` | `d1ca756248b44643dab82760e129d5039597a48e7757f065142cb3c23aa466b8` | Digest `7909c2addb49b09e`, draft `false`, gaps `[]` |

---

## 4. Academic & Matrix Verification

- **10/10 questions** independently solved with detailed reasoning routes and cross-checks.
- **Difficulty:** 7 D4 + 3 D3. Q5 (modeling box volume), Q6 (rational domain), and Q8 (difference uniqueness) are evaluated at D3 (score 7/10) and preserved honestly without artificial inflation.
- **Cognitive Demands:** Exactly one primary cognitive demand assigned per question:
  - `JUSTIFY`: Q1, Q3, Q7, Q10
  - `SYNTHESIZE`: Q2, Q9
  - `EXPLAIN`: Q4, Q6
  - `MODEL`: Q5
  - `APPLY`: Q8
- **Hardest-Target Deep Brief:** Q3 (`OWN-ISSUE56-POLY-03`, `JUSTIFY · D4`, Score 9). Eliminates degrees 1–3 via IVT sign trapping at $x=1$; eliminates degree 4 via irreducible quadratic constant sign property; constructs verified minimal degree 5 specimen $p(x) = \frac{1}{12}(x-1)^2(x+1)(3x^2-10x+12)$ with $\Delta = -44 < 0$.
- **H1–M3 semantic verdicts:** All 10 questions achieve YES on all 12 review facets (H1–H3, S1–S3, P1–P3, M1–M3).
- **W-Leakage Check:** 10/10 PASS (zero pre-commitment answer disclosure across all questions).

---

## 5. Independence Statement

Matched Issue #52 (independent candidate A) and its branch were **NOT inspected** at any point prior to freezing this candidate deliverable.
