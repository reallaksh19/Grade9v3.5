# Candidate Validation Report: ISS34 D2 Hybridisation (Agent B)

**Date**: 2026-10-04  
**Agent**: Independent Agent B  
**Branch**: `candidate/iss34-d2-hybridisation-agent-b-r1`  
**Base Commit**: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e` (`feat/issue29-integrated-core-templates`)

---

## 1. Automated Machine Checks

| Check | Tool / Validator | Target | Result | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Package Schema** | `Draft202012Validator` | `evidence/benchmark/ISS34/package.json` | **PASS (0 errors)** | Validated against `Shared/library/package.schema.json` |
| **Renderer Build** | `Shared/tools/render_core.py` | `evidence/benchmark/ISS34/manifest.json` | **PASS (0 gaps)** | Full production build (`draft: false`) |
| **Prompt Hash** | SHA-256 Checksum | `evidence/benchmark/ISS34/owner-core-prompt.md` | **PASS (Verified)** | `6ba9ba40ea30b486792892de7091f51271f3855c0b39d22da5f7e83f20c52469` |
| **Question Ledger** | Schema & Sum Check | `evidence/benchmark/ISS34/question-ledger.json` | **PASS (10/10 items)** | Scores: Q1(3), Q2(3), Q3(3), Q4(4), Q5(3), Q6(3), Q7(3), Q8(3), Q9(3), Q10(3) |
| **D2 Score Range** | `Shared/vocabularies/learner-question-metadata.v1.json` | `evidence/benchmark/ISS34/bank.json` | **PASS (3 to 5)** | Strictly complies with vocabulary limits (min 3, max 5) |
| **QRT Review Schema**| JSON Schema Inspection | `evidence/benchmark/ISS34/qrt-review.json` | **PASS** | Evaluated H1–M3 criteria with full PASS verdicts |
| **HTML Page Render**| Headless verification | `core1a.html` (91 KB), `core2.html` (243 KB), `index.html` (21 KB) | **PASS** | All interactive SVGs, questions, and routes embedded |

---

## 2. Matrix Conformance Verification

- **Target Grade / Subject**: Grade 11 Chemistry (Chemical Bonding and Molecular Structure)
- **Target Difficulty Band**: D2 (Connected Reasoning, composite score 3–5)
- **Cognitive Demands Covered**:
  - `EXPLAIN`: Q1, Q10
  - `APPLY`: Q2, Q6, Q7, Q9
  - `REPRESENT`: Q3, Q5
  - `SYNTHESIZE`: Q4 (Hardest Target)
  - `JUSTIFY`: Q8
- **Microtopic Distribution**:
  - `MIC-CHEM-G11-HYBRID-DOMAINS`: Q1, Q5, Q6, Q8, Q10 (5 items)
  - `MIC-CHEM-G11-HYBRID-MULTIPLE-BONDS`: Q2, Q3, Q4, Q7, Q9 (5 items)
- **Question Families**:
  - `FAM-CHEM-HYBRID-DOMAINS`: 5 items linked
  - `FAM-CHEM-HYBRID-MULTIPLE-BONDS`: 5 items linked

---

## 3. Rendered Output Verification

- `render-receipt.json` status:
  - `renderer`: `render_core/2`
  - `draft`: `false`
  - `gaps`: `[]` (zero gaps)
  - `pages`: `["core1a.html", "core2.html", "index.html"]`
  - `output_roles`: `["CORE1A", "CORE2"]`

Rendered artifacts are available locally for interactive inspection:
- `core1a.html`: Concept learning core for hybridisation and spatial geometries
- `core2.html`: Full competition/practice core containing all 10 bank items with full multi-step reasoning routes and SVG figures.
