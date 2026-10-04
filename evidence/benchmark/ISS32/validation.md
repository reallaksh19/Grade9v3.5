# Validation Ledger — Issue #32 (Agent B)

## 1. Execution Environment & Baseline
- **Launch Snapshot Seed:** `e01c6365acfd6aec84c0a6e94f11b683bd961f6e` (HEAD of `feat/issue29-integrated-core-templates`, based on PR #21 head `8678645ef2fd5e63401ef5af3621b94e925732a8`)
- **Working Branch:** `feat/iss32-d1-hybridisation-agent-b`
- **Whole-body SHA-256:** `fb3e45cdbe8dfb55d0c82146f917dfbc0220bd97beb1689a5d9073f1c1c88037`
- **A/B/C core-prompt SHA-256:** `cd87b3e209617c6170a8d7916a2f66c42706e13de3280bb68d46aaca542233a9`
- **Renderer Version:** `render_core/2` (`digest: 2fd27aae5dedf573`, `semantic_digest: 152fb307951d98d7`)
- **Blueprint Registry:** `Shared/web/interactive-page-blueprints.v1.json` (1.9.0)

---

## 2. Command Checks & Output Log

| Tool / Check | Command | Result / Exit Code | Findings / Observations |
| :--- | :--- | :--- | :--- |
| **Owner Bank Validation** | `python Shared/tools/owner_bank.py check evidence/benchmark/ISS32/generated/owner.bank.json` | **PASS** (Exit 0) | `OK` — All 10 questions strictly satisfy schema, verbatim stems, typing, and custody constraints. |
| **Renderer Gap Preflight** | `python Shared/tools/render_core.py gaps --manifest evidence/benchmark/ISS32/generated/product.manifest.json` | **PASS** (Exit 0) | `0 depth gap(s); 0 subject-authority finding(s)` — Zero missing slots or blueprint shortfalls. |
| **Governed Page Generation** | `python Shared/tools/render_core.py build --manifest evidence/benchmark/ISS32/generated/product.manifest.json --out evidence/benchmark/ISS32/rendered --mode PAGES` | **PASS** (Exit 0) | `wrote 3 page(s)` (`core1a.html`, `core2.html`, `index.html`) with `draft: false`. |
| **Static Quality Gate** | `python Shared/tools/quality_gate.py evidence/benchmark/ISS32/rendered --subject Chemistry --product-id EVIDENCE-CHE-ISSUE32-HYBRID --static` | **PASS** (Exit 0) | `0 finding(s)` across all static validation rules. |
| **Browser Measurement Gate** | `python Shared/tools/quality_gate.py evidence/benchmark/ISS32/rendered --subject Chemistry --product-id EVIDENCE-CHE-ISSUE32-HYBRID` | **PASS** (Exit 0) | `PASS; 0 finding(s)` — Passed full Chromium browser rendering checks (touch targets, contrast, overflow, DOM layout). |
| **Toughest Target Derivation** | `python Shared/tools/toughest_concept.py evidence/benchmark/ISS32/generated/product.manifest.json --json` | **PASS** (Exit 0) | Derived `OWN-ISSUE32-HYBRID-05` (Q5, band D3, conceptual score 3/total 6) as hardest target; runner up `OWN-ISSUE32-HYBRID-09` (Q9). |

---

## 3. Exact Render Evidence & Asset Verification

### Rendered Files
- `evidence/benchmark/ISS32/rendered/core1a.html` (118 KB): Complete interactive construction lesson for:
  - Steric domain inventory (`MIC-CHE-BOND-DOMAIN-COUNTING`)
  - Hybrid orbital conservation (`MIC-CHE-BOND-HYBRID-ORBITAL-MAPPING`)
  - 3D stereochemical representation and VSEPR model boundaries (`MIC-CHE-BOND-3D-REPRESENTATION-MODELS`)
- `evidence/benchmark/ISS32/rendered/core2.html` (236 KB): Verbatim 10-question reader with:
  - Staged SVG reveals
  - Inert commitment controls
  - 3–5 scaffold hint ladders
  - Full structured solution moves and independent checks
  - Direct concept anchors linking to `core1a.html`
- `evidence/benchmark/ISS32/rendered/render-receipt.json`: Immutable audit receipt recording zero gaps.

### Asset Digest Confirmation
- `evidence/benchmark/ISS32/assets/hybrid-tetrahedral-3d.svg`: Valid multi-stage SVG with stages `TET-STAGE-1`, `TET-STAGE-2`, `TET-STAGE-3`.
- `evidence/benchmark/ISS32/assets/sigma-pi-overlap.svg`: Valid multi-stage SVG with stages `SIGMA-PI-1`, `SIGMA-PI-2`, `SIGMA-PI-3`.
- `evidence/benchmark/ISS32/assets/electron-domains-hcho.svg`: Valid multi-stage SVG with stages `DOM-STAGE-1`, `DOM-STAGE-2`, `DOM-STAGE-3`.

---

## 4. Unresolved Findings & Waivers

- **Unresolved Failures:** 0.
- **Waivers Granted:**
  - `TRAP`: Handled via explicit misconception modeling in package microtopics and QRT hint ladders.
  - `CONDITIONS`: Boundary conditions (VBT/VSEPR assumptions) are stated within question stems.
  - `CHECK`: Explicit independent verification procedures are embedded directly in every question record.
