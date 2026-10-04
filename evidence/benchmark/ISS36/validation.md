# Validation Report — Issue #36 Independent Candidate B

## 1. Baseline vs. Candidate Environment
- **Launch Baseline / Seed Commit:** `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`
- **Candidate Branch:** `candidate/iss36-d3-hybridisation-agent-b-r1`
- **Execution Environment:** Windows PowerShell / Python 3.12 / GitHub CLI
- **Delivery Protocol:** V3.1 ACTIVE
- **Paired Blind Submission:** Issue #35 (Candidate A) was NOT inspected prior to candidate freeze.

## 2. Cold-Start Reproduction Command
The entire learner delivery artifact can be reproduced deterministically from repository root:
```powershell
python Shared/tools/render_core.py build --manifest evidence/benchmark/ISS36/generated/product.manifest.json --out evidence/benchmark/ISS36/rendered --draft
```

## 3. Render Execution & Quality Gates
- **Production Renderer:** `Shared/tools/render_core.py` (`render_core/2`)
- **Artifact Render Digest:** `649b50554da6aeb1`
- **Semantic Metadata Digest:** `232b7b3130d7fbed`
- **Gate Results:**
  - Depth gaps: **0**
  - Subject-authority findings: **0**
  - Draft status: `draft: false` (clean production build)
- **Rendered Output Files:**
  - `evidence/benchmark/ISS36/rendered/core1a.html` (126,254 bytes)
  - `evidence/benchmark/ISS36/rendered/core2.html` (235,760 bytes)
  - `evidence/benchmark/ISS36/rendered/index.html` (20,918 bytes)
  - `evidence/benchmark/ISS36/rendered/render-receipt.json` (437 bytes)

## 4. Academic & Custody Integrity Checks
- **Whole-body SHA-256:** `656fec84e565f638f9c605a84fb9e13ddb7ecdf604328dd9314327667c50b5f2` (VERIFIED MATCH)
- **A/B/C Core-prompt SHA-256:** `cc448399f7c44781f8e3ca659aaa96da8b9fde5edc7a66625b45729f728a29d5` (VERIFIED MATCH)
- **Per-Question Stems:** All 10 question stems match their exact intake SHA-256 digests.
- **Custody Authority:** All 10 questions carry `OWNER_SUPPLIED_RAW_INPUT` custody without exam fabrication.
- **W-Protection:** Authored scaffolds in `owner.bank.json` and `qrt-review.json` provide conceptual guidance without revealing the protected work (W).
- **Instructional Assets:**
  - `allene-orthogonal-pi.svg`: Verified valid SVG, accessible title/desc, 3 reveal stages.
  - `nitrate-delocalised-pi.svg`: Verified valid SVG, accessible title/desc, 3 reveal stages.
  - `conjugation-pathway.svg`: Verified valid SVG, accessible title/desc, 2 reveal stages.

## 5. Unresolved Findings and Waivers
- **Unresolved findings:** 0
- **Waivers:** None requested.
