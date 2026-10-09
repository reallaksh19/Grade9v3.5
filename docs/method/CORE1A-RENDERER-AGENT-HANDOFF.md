# Core1A authoring-to-render handoff — maturity pilot

**Status:** TEST engineering demonstration / not canonically or academically accepted.  
**Coordination:** IMO directions and conceptual objections → [issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294); NCERT status → [issue #68](https://github.com/reallaksh19/Grade9v3.5/issues/68). **Both agents are paused until the Owner explicitly reactivates them.** This guide is not an automatic GO signal.

## One authorized Core1A pipeline (no alternate page engine)

1. **Author one source-safe, canonical package.** Store substantive content in its existing library schema, not hard-coded HTML: declared assumptions, the exact inference in `microtopic.inferential_jump`, a `teaching_path[]` whose steps explain `why_valid`, qualified representations and correct maths. Include a wrong-path diagnostic, repair, fully checked worked anchor, independently attempted exit with verified answer/check and explicit applicability limits. Preserve original-source custody separately.
2. **Select with the existing manifest contract.** An `output_roles: ["CORE1A"]` product still needs the complete `selection` object (`microtopics`, `core2`, `core2a`, `core2b`), an honest `coverage` block, package refs and any source-bank refs. It must **not** fabricate `CORE2` selections to make another role look finished. For the first sandbox example see `TEST/products/core1a-divisibility-render-maturity.manifest.json`.
3. **Run the single canonical renderer** and inspect gaps: `python Shared/tools/render_core.py gaps --manifest TEST/products/core1a-divisibility-render-maturity.manifest.json --reference`. An output whose blueprint REQUIRED/EXPECTED reference components are absent must record those gaps; absence of an SVG is not evidence that a textual description has rendered as a labelled diagram.
4. **Build actual learner HTML/PDF through the shared TEST path**, never hand-edit generated HTML: `python Shared/tools/deploy_test.py product TEST/products/core1a-divisibility-render-maturity.manifest.json --no-mirror`. That calls the sole renderer, stamps every page TEST and prints via the normal browser `tools/print/print-product.mjs` path. The output is under `public/test/products/core1a-divisibility-render-maturity/` when run in an isolated checkout. This path is strictly **not** the manual `public/test/imo-grade9/core1a.html` authored preview.
5. **Inspect what the learner actually sees.** With a pinned Chromium installation run `node tools/site-audit/core1a-render-maturity-audit.mjs public/test/products/core1a-divisibility-render-maturity`. Inspect widths 320/390/768/1280, 200% text scaling, JS exceptions, semantic Core1A article, keyboard/disclosure and mathematical presentation. Record keyboard/screen-reader and independent learner-comprehension statuses separately; automation cannot pass a test that was never performed.
6. **Bind exact version and PDFs to evidence.** The TEST `deploy-receipt.json` carries `inputs_sha256`, `render_digest`, `pages`, `gaps`, `waived`, `pdf` and `accepted: false`; `print-receipt.json` binds the actual page/PDF digests. The [focused nonrelease workflow](../../.github/workflows/core1a-render-maturity.yml) uploads full HTML/PDF/Chromium receipts and screenshots on PR heads. A successful shell command or unit test is not the same as actual browser/print QA.

## What agent independence requires

The agent must independently supply **complete governed content** to this pipeline. Use these checks as a *repeatable authoring protocol*, not as an excuse to introduce a new engine or require that all subjects share the same topic hierarchy.

| Decision | Responsible party | Evidence needed |
| --- | --- | --- |
| Concept and protected inference | Core architect + appropriate academic review | Exact prerequisite, inference, proof/warrant, boundary, independent transfer |
| Authored Core1A package | Producing agent, under accepted academic scope | Schema-valid library content and own reasoning; provenance explicitly AUTHOR_CREATED |
| Source-question Core2 | Source-owning agent | Original question/option/figure/key custody, rights-permitted mode and exact-source reasoning |
| Learner output | Shared renderer and TEST deployment | Actual generated HTML/PDF, responsive/browser and keyboard checks, QA receipts |
| Canonical / public acceptance | Owner and existing governed acceptance route | Exact rendered digest plus independent academic/source/rights decisions; never implied by TEST or CI |

**Rights-safe worked examples:** Original mathematical practice is not SOF/NCERT Core2. Reference-only links are not permission to reproduce printed source problems; source-custody and academic verification are independent axes. An independently authored Core1A can be tested without a licensed original question, but it cannot claim to repair that particular source problem until its protected inference is properly corroborated.

**Academic non-shortcuts:** A shared topic label does not establish a shared inferential jump. A hard construction cannot be replaced by copied answer steps. Visuals must bind actual mathematical data. A changed number or story is not a proved changed-demand transfer. Schema validity and green CI do not prove student comprehension.

## Maturity and reactivation rubric

- **M1 — Verified canonical route:** A versioned, role-scoped TEST manifest **actually renders** with the existing `render_core`; output reproducibility and invalid-selection rejection demonstrated.
- **M2 — Complete reference-depth candidate:** No unresolved REQUIRED/EXPECTED blueprint gaps at the selected slice's justified applicability; any expected component waiver is narrowly documented and inspectable.
- **M3 — Real learner artefacts:** TEST-stamped HTML and corresponding printed learner PDF, actual browser widths/200%-text, keyboard navigation, functioning disclosure, correct math and reproducible hashes. Manual a11y/learner checks clearly marked not run until performed.
- **M4 — Conceptual integrity:** Reviewed inference/construction/diagnosis and independent answer/check, with original examples and honest source-link confidence.
- **M5 — Ownership boundary:** Distinct source custody, academic, engineering, TEST and canonical acceptance decisions; no agent has been tacitly authorized to merge/publish. Independent agents get bounded tasks with explicit exit and stop criteria.

**Current position:** Maturity is NOT assumed from the creation of this document. Read exact-head workflow evidence and its gap count. If any criterion fails, keep both agents held and fix the smallest shared pipeline/content deficiency. Only an explicit Owner decision recorded in #294 or #68 can reactivate an agent; NCERT's separate `PARKED_EVIDENCE_DEPENDENCY` remains even after engineering maturity unless its own evidence blockers change.

## No-repeat rule

Do not add a second canonical renderer, duplicate content bank, independent blueprint, blanket CI gate, fixed pedagogical step quota, or hand-composed rendered HTML. If the existing model cannot express an essential teaching move, report the smallest defective field-to-render projection with a failing test, then repair it in the single owning component. Every future source batch should use one genuine learner vertical slice as its proof of integration.
