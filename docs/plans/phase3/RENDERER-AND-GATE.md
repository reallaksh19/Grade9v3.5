# Phases 3 and 4: one pipeline, one renderer, and a gate on the rendered pages

Part of [LEARNER-PRODUCT-QUALITY-REBUILD.md](../LEARNER-PRODUCT-QUALITY-REBUILD.md).

## The pipeline

```
raw intake ─► research library (evidence ► staging ► verification)
           ─► promote_verified.py   (VERIFIED + no depth duty ► canonical library)
           ─► product_manifest.py  (selection + owner ledger + diagnostic; no content)
           ─► render_core.py       (six Cores through blueprint slots, tablet shell; gaps ► duties)
           ─► print-product.mjs    (PDF = print of the page)
           ─► quality_gate.py      (contract on the rendered DOM + browser measurement + continuity)
           ─► public/products/…    (only on PASS; build_products.py)
```

| Tool | What it guarantees |
|---|---|
| `Shared/tools/promote_verified.py` | Nothing enters the canonical library unless its research node is VERIFIED against current inputs **and** its records carry no depth duty. Promoted records are stamped with the verification they rest on |
| `Shared/tools/product_manifest.py` | A product is selection only: microtopics, questions per Core, the owner's input ledger and diagnostic items. It holds no text |
| `Shared/tools/render_core.py` | See the bullets below this table |
| `tools/print/print-product.mjs` | PDFs are Chromium prints of the page, with every reveal opened, and a receipt of page and PDF digests |
| `Shared/tools/quality_gate.py` | See the bullets below this table |
| `Shared/tools/build_products.py` | Derives a manifest for every package, then builds, prints and gates every product. It publishes only PASS products and writes `products/STATUS.md` |

**`render_core.py`, the only renderer:**
- It renders only through blueprint slots, inside the tablet shell: home, back, question bank, search, display, breadcrumb, 48 px controls, the 0.68/0.32 stage-support layout, print CSS and focus styles.
- Answers, reconstructions and model answers are gated on a recorded attempt. Hint rungs open one at a time.
- Figures are authored staged SVGs. Before an attempt, only the permitted stages show.
- It writes no academic text. A missing field is a typed gap that the board knows as a duty.
- A product with gaps is written only as a draft (`data-g9-draft`).
- The renderer inventory allows exactly one `RENDERER`, so a second learner-page generator fails CI.

**`quality_gate.py`:**
- It extracts the rendered DOM into a learner observation and applies the Phase 1 contract.
- It measures touch targets and layout in Chromium.
- It checks continuity: Core1A/1B parity, every link resolving to a rendered unit, every owner input resolved and rendered, and the diagnostic.
- It writes a schema-bound report whose verdict is computed. The report cannot state PASS in prose.

## What the gate proves today

- **Negative:** every calibration specimen fails for its audited findings (Phase 1 calibration, unchanged). The real Motion-in-a-Plane product renders as a draft with 36 gaps and fails the gate on the same defects Audits 1 and 3 found, now visible before publication: no question-aligned figure, no safe transfer figure, no failure signal, no family closure, no invariant, no worked anchor, no compact anchor.
- **Positive:** a clearly labelled test fixture passes: the Mathematics linear-equations unit with every depth field and a staged number-line SVG (`tests/test_quality_gate.py`). It renders gap-free and passes with the browser measurement. So the bar is reachable by complete records, not a trap that fails everything.
- **Blind spots the gate closed while it was being built.** Reviewing its first passing output found three leaks, and each became a rule or a fix:
  1. Record IDs shown to the learner (`CAP-…`, `FAM-…`, `Q-…`). The generic id pattern is now part of ALL-NO-PLACEHOLDER; family titles, step text and question stems replace IDs.
  2. The key step printed twice. Fixed in the renderer.
  3. A pre-attempt figure that stepped through to the answer. New rule ALL-PRE-ATTEMPT-FIGURE-PARTIAL; the renderer shows only permitted stages.

## Status of every product

`python3 Shared/tools/build_products.py build`: **0 of 21 products pass**. Every package has depth gaps; `products/STATUS.md` lists them per product.

The existing site pages stay online. They are replaced product by product as each passes (Phase 7 backfill). The gaps are the authoring work for Phase 6.

## Retired

- `Shared/tools/learner_product_render.py` and `Shared/tools/delivery_gate.py` (#290's parallel renderer and gate) are deleted. Their invariants moved:
  - reconciliation → the gate's ledger checks;
  - diagnostic → the start page and `CONT_DIAGNOSTIC_MISSING`;
  - placeholders and holds → contract rules;
  - source identity → evidence cards and the verifier.
- `research-first.v1.json`, the raw-intake page and the docs point at the new pipeline. The intake tests remain.
- `Physics/tools/build_motion2d_projectile_product.py` lives only on its own branch and is not merged; the inventory keeps it as RETIRE.

## CI

`.github/workflows/learner-quality.yml` runs the following:
- the renderer freeze;
- corpus integrity;
- the contract check and calibration;
- the migration check;
- the contract, renderer and gate tests, with Chromium for the rendered measurement.

GitHub Actions is currently out of budget on this repository, so it has not executed yet.
