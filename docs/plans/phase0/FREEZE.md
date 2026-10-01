# Phase 0 freeze

Part of [LEARNER-PRODUCT-QUALITY-REBUILD.md](../LEARNER-PRODUCT-QUALITY-REBUILD.md). The owner
approved the phase order and this freeze on 2026-09-26.

## What is frozen

1. **No new learner products until Phase 4.** No agent generates new Core pages, PDFs, handouts
   or question-bank pages for any subject or subtopic. Pages that are already online stay online.
2. **No new renderers.** Every code path that renders learner content is listed in
   [renderer-inventory.v1.json](renderer-inventory.v1.json), with a classification:

   | Class | Meaning |
   |---|---|
   | `ENGINE_KEEP` | Becomes part of the single blueprint renderer in Phase 3 |
   | `MIGRATE` | Keeps working; moves onto the renderer or its data in Phase 3 |
   | `RETIRE` | Deleted in Phase 3; never extended |
   | `OUT_OF_SCOPE` | Site chrome or tools, not learner content (the tablet shell work continues) |
   | `FROZEN_SNAPSHOT` | Hand-authored explorers and published snapshots; left byte-identical |

   `python3 Shared/tools/renderer_inventory.py --check` fails when a file that emits HTML or
   PDF, or renders into the DOM, is not in the inventory (tests/test_renderer_inventory.py).
3. **The calibration corpus is fixed.** [benchmarks/quality-calibration/](../../../benchmarks/quality-calibration/README.md)
   holds the negative specimens and pins the owner's references.
   `python3 Shared/tools/calibration_corpus.py --check --refs` fails when a specimen file changes,
   appears or disappears (tests/test_calibration_corpus.py).

## What continues

- Research-library work (researcher, author, verifier, scanner). It produces cited records,
  not learner products, and is the input to Phases 2–3.
- The tablet shell and navigation work (template/site-agents/). It changes site chrome only.
- Fixes to existing pages that are already live, when a page is broken. No new content.

## Owner decisions (2026-09-26)

| # | Decision | Recorded in |
|---|---|---|
| 1 | Phase order and the freeze: approved | this file |
| 2 | Quality references live in the repository; agents search the repository for them | `benchmarks/quality-calibration/manifest.v1.json` (`references`) |
| 3 | The owner reviews calibration (Phase 1) and pilot units (Phase 6) | plan §5 |
| 4 | `cdnbbsr.s3waas.gov.in` is Tier A; Tier C is a corroborated fallback for questions and keys, with ExamSIDE and six other publishers | `Physics/research/source-allowlist.json`, `Shared/tools/evidence_check.py` |
| 5 | Cost ceiling per unit: explained in plan §5; the owner sets the number | plan §5 |

## Calls made on the owner's instruction (2026-10-01)

PR #372 left two calls open and named them the owner's. The owner answered "do it", so they were made, with the reason, and each can be undone in one place.
They are decisions of the implementer on that instruction, not a review by the owner.

| # | Decision | Why | To undo it |
|---|---|---|---|
| 6 | The toughest concept of a question set is the question whose difficulty is most *conceptual* (`concept_model_selection` + `trap_exception_sensitivity`), then the higher total score, then `representation_translation`, then `reasoning_chain_length`, then bank order | The owner's complaint was a page "not for the toughest concept" and a Core1A "not for name sake": a question that is hard because of its algebra is practice, not a concept, so conceptual difficulty must lead. It reads only the author's own difficulty estimates and guesses nothing, so the owner can overrule it by changing them | `derive()` in `Shared/tools/toughest_concept.py` and its pinned test `tests/test_toughest_concept.py`; the rule is quoted in `TEST/README.md` and in the authoring hint of the crux component of `Shared/web/interactive-page-blueprints.v1.json` |
| 7 | `Shared/tools/explorer_build.py` and `Shared/web/explorer-runtime.js` are `ENGINE_KEEP` in the renderer inventory | They render learner content, so rule 2 requires them to be listed, and `OUT_OF_SCOPE` would be untrue. They are not a new hand-written renderer: the page is generated from the blueprint registry (`BP-EXPLORER-GCDR`: route, components, layout, depth) and a checked spec, and Phase 3 merges them into `render_core.py` as the explore adapter. They do not break rule 1: the only deploy path (`deploy_test.py interactive`) writes under `public/test/`, and `explorer_build.py build --out` is a preview | Reclassify or delete the two rows in `renderer-inventory.v1.json` and the two modules; only `deploy_test.py` imports the generator (the other explorer modules, `explorer_expr.py` and `explorer_model.py`, are its checks) |

## Exit gate status

| Gate | Status |
|---|---|
| Renderer inventory committed and checked | done |
| Calibration corpus in place and checked | done: 5 negative specimens (40 files); R2 pinned in the repository; R1 not on any branch, so its grammar is encoded and the closest in-repository file is pinned |
| Audits #296–#298 closed with final matrices | done: [audits/AUDIT-1-FINAL.md](audits/AUDIT-1-FINAL.md) (12 findings), [AUDIT-2-FINAL.md](audits/AUDIT-2-FINAL.md) (root-cause chains, control-gap matrix), [AUDIT-3-FINAL.md](audits/AUDIT-3-FINAL.md) (11 findings, compliance matrix); the S1 specimen's expected findings now list A1-001…012 and A3-001…011 |
