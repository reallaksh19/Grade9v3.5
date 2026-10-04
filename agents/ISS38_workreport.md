# ISS38 Work Report — Independent Candidate B

- **Issue:** [#38](https://github.com/reallaksh19/Grade9v3.5/issues/38) — D4 hybridisation · Q1–Q10 · Independent Agent B
- **Matched issue:** [#37](https://github.com/reallaksh19/Grade9v3.5/issues/37) (Independent Agent A)
- **Branch:** `candidate/iss38-d4-hybridisation-agent-b-r1`
- **Pinned launch seed:** `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`
- **Renderer authority:** `Shared/tools/render_core.py` (v2)
- **Protocol:** `relay/PROTOCOL_SELECTION.yaml` — `V3_1`, `ACTIVE`
- **Independence status:** Issue #37 and its candidate were **NOT inspected** at any time.
- **Owner clarification:** NONE required; A/B/C core prompt was completely sufficient.

---

## Eight-Unit Delivery Status

| Unit | Status | Evidence Head |
|---|---|---|
| **U1 — Intake & baseline** | PASS | `owner-core-prompt.md` (SHA-256: `52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7`), launch hashes, chronological audit. |
| **U2 — Academic/task analysis** | PASS | `question-ledger.json`, `source-cards.json` (10/10 solved, 8 D4 + 2 D3, 6 demands). |
| **U3 — Hardest-target brief** | PASS | `OWN-ISSUE38-HYB-03` (Q3 · EXPLAIN · D4 · Torsional alignment); X/Y/Z/W defined. |
| **U4 — Canonical records** | PASS | `owner.bank.json` (OK), `package.v1.json` (0 schema errors), `product.manifest.json`. |
| **U5 — Rendered deliverables** | PASS | `rendered/core1a.html` (115579 bytes), `rendered/core2.html` (253348 bytes), `render-receipt.json` (0 gaps, draft: false). |
| **U6 — Semantic/interaction audit** | PASS | `qrt-review.json` (10/10 questions have full H1–M3 YES verdicts), `validation.md`. |
| **U7 — Builder proposal after page** | PASS | `builder-proposal.md` proposing `PARAMETER_SCRUBBER_COMPARATOR` from inspected render. |
| **U8 — Independent handoff** | FROZEN | Draft PR created, `candidate-review.md`, `run-receipt.json`, all receipts reconciled. |

---

## Key Academic Insights & Decisions

1. **Rehybridisation vs Local Counting:** Local 4-domain counting fails in formamide because resonance donation into the carbonyl pi* orbital provides significant stabilization, driving rehybridisation from sp3 to an approximately planar sp2 framework with an unhybridised pz orbital.
2. **Conformational Torsion & Orthogonality:** Twisting the C–N bond toward 90° extinguishes lateral p-orbital overlap purely through geometric orthogonality (\(\langle p_y | p_z \rangle = 0\)), without altering atom connectivity or formal electron counts.
3. **Refuting Nominal Causation:** The loss of donation upon twisting is caused by loss of orbital overlap, not because the 'hybridisation label changed'. Hybridisation is a human descriptive model, not a physical force.
4. **Pathway Continuity:** Intervening saturated –CH2– groups possess four sigma bonds and no unhybridised p orbitals, acting as electronic insulators. Spatial proximity in a folded conformation does not constitute chemical conjugation.
5. **Radical SOMO Occupancy:** Three sigma bonds in planar methyl radical leave a singly occupied pz orbital (SOMO, 1 electron), refuting the false universal generalization that three sigma bonds always leave an empty orbital (conflating radicals with carbocations).
6. **Hardest Target Specification:** Q3 (EXPLAIN · D4) models the torsional overlap boundary, refuting label causation and establishing epistemological distinctions between model assumptions and physical measurements.

---

## Rendered Deliverables

- **Core1A Concept Learning Page:** `evidence/benchmark/ISS38/rendered/core1a.html`
- **Core2 Source Questions Page:** `evidence/benchmark/ISS38/rendered/core2.html`
- **Product Index:** `evidence/benchmark/ISS38/rendered/index.html`

No gaps remain. Production build completed cleanly with `Shared/tools/render_core.py`.
