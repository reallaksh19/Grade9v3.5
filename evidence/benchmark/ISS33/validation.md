# ISS33 validation ledger

Current state: **EXACT-RENDER REVIEWED CANDIDATE**.

## Immutable inputs and render
- Source snapshot: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`.
- Candidate artifact commit containing generated records/render evidence: `0af8b1fb4a99e3e75f6b008545e1eb6c4f9f82b5`.
- Whole issue-body SHA-256: `a89df1e2d7f5c7a5ca41b51f670b80f15c326b2ba88f62f870d147f82d6763c8`.
- A/B/C core-prompt SHA-256: `6ba9ba40ea30b486792892de7091f51271f3855c0b39d22da5f7e83f20c52469`.
- Renderer stamp: `render_core/2 11078d7676fe225e`.
- Core1A SHA-256: `8ac3ca400fe9facb661826c3a27892ab9f02b7b03d1adaaf4ed437a51c906f9e`.
- Core2 SHA-256: `1ff7dd5c5c8665863787670fc211dd2d330fc2976f81f3bfe5b641e788d49d55`.

## Same-environment checks
- Focused authoring/blueprint/quality contracts: **PASS**.
- Owner-bank custody check: **PASS**.
- Package JSON Schema validation: **PASS**.
- Governed Core1A + Core2 render: **PASS**; no hand-edited learner HTML.
- Strict `quality_gate.py`: **PASS**, 0 findings; contract 1.8.1.
- Playwright tablet audit: **PASS / exit 0**. Tested landscape 1366, landscape 1440 and portrait 854 profiles; 0 horizontal overflow, 0 undersized targets, 0 staged-SVG violations. Exact report is in `rendered/tablet-audit.json`.

## Exact-render semantic findings
The per-question H1–M3 record is `semantic-review.json`.

- H1/H2/H3: YES for Q1–Q10.
- S1/S2/S3: YES where representation is applicable; Q6 is justified NOT_APPLICABLE.
- P1/P3: YES for Q1–Q10.
- P2: **PARTLY** for Q1–Q10 because concept help lands at the correct microtopic but not the unique construction/repair anchor.
- M1: YES for Q1–Q10.
- M2/M3: **PARTLY** for Q1–Q10 because the reader exposes the wrong route but does not elicit a discriminating diagnostic and does not route directly to item-specific repair.
- Hardest-target interaction: meaningful staged orbital inventory exists; **PARTLY** as an active task because it cannot enforce one-use-only orbital allocation. See `builder-proposal.md`.
- Source honesty: the reader correctly gives no exam identity and says “Owner-supplied question, verbatim”, but the pinned metadata surface cannot additionally express “coordinator/AI-drafted, not personally authored by owner”. This is documented as a contract discrepancy, not silently relabelled.

## Academic/source cross-check
OpenStax Chemistry 2e §7.6/§8.1/§8.2/§8.3 and the current IUPAC Gold Book hybridization entry were checked on 2026-10-04. These support the domain-count, electron-pair-vs-molecular-shape, sp/sp2/sp3 and sigma/pi overlap statements used here. No advanced amide/radical/allene/delocalisation claim was needed.

## NOT_RUN / limitations
- External sandbox cold start: **NOT_RUN — sandbox repository not supplied**.
- Independent academic reviewer: **NOT_RUN**.
- Real learner effectiveness / misconception discrimination: **NOT_RUN**; no learner data exist.
- Golden promotion / publication: **NOT_RUN and not authorized for the producing agent**.

Automated PASS does not erase the semantic PARTLY findings above.
