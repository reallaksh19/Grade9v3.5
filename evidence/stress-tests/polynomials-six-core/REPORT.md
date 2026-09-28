# Polynomials six-Core stress witness — 2026-09-29

## Basis and decision

Executed in isolated worktree `C:\CodeA\Grade9V3\_polynomials_stress`, branch `codex/polynomials-six-core-stress`, at `68559ac4cb17eeb5f2d87aebecebf652b9a34efd` (verified `origin/main`). Renderer is `render_core/2`. This is an audit, not academic acceptance or publication. No `public/` files were written by this run. [inventory.json](inventory.json) lists SHA256 and byte length of every renderer/schema/blueprint/fixture input and each output. Regenerate it with `python evidence/stress-tests/polynomials-six-core/audit_inventory.py` from repository root.

**Finding:** Current main has no `Mathematics/library/polynomials.v1.json`, Polynomials bank, or Polynomials product manifest. The one-microtopic P3 Polynomials prototype cannot be honestly completed from canonical content. The positive Mathematics golden candidate renders all six roles; the Polynomials empty scaffold only proves the renderer can emit six empty draft shells. The prior local Polynomials records cannot pass current schema. None is golden-like or accepted.

## Reproduction and command status

Run from repository root; the output directory is this evidence folder. Commands below were executed against the recorded head.

| Command | Exit | Observed result |
|---|---:|---|
| `python Shared/tools/render_core.py gaps --manifest evidence/stress-tests/polynomials-six-core/untrusted-fixture/replay-manifest.json` | 1 | `PRODUCT_STRUCTURE_INVALID`: package root requires `relations` (first schema error). |
| Same renderer `build` with that manifest, `--out evidence/stress-tests/polynomials-six-core/untrusted-fixture/rendered --mode PAGES --draft` | 1 | Same error; no role HTML written. |
| `python Shared/tools/render_core.py gaps --manifest evidence/stress-tests/polynomials-six-core/empty.manifest.json` | 1 | Two gaps: `CORE2 ACQUIRE_SOURCE` and `CORE2A AUTHOR_PRACTICE`, both on `STRESS-MATH-POLYNOMIALS-EMPTY`. |
| Same renderer `build` with empty manifest, `--out evidence/stress-tests/polynomials-six-core/rendered --mode PAGES --draft` | 0 | Six role pages plus index, all marked draft; receipt digest `418e07f1a995a41a`. |
| `python Shared/tools/quality_gate.py evidence/stress-tests/polynomials-six-core/rendered --subject Mathematics --product-id STRESS-MATH-POLYNOMIALS-EMPTY --report evidence/stress-tests/polynomials-six-core/quality-browser.json --strict` | 1 | FAIL: 8 findings, including absent figure, all six page slots absent, and no recognized governed render stamp; reasons `BLOCKING_FINDINGS,DRAFT`. Chromium measurement ran. |
| Same quality command with `--static --report evidence/stress-tests/polynomials-six-core/quality-static.json` | 1 | FAIL; adds `RENDERED_RULES_NOT_MEASURED`. |
| `python Shared/tools/render_core.py build --manifest golden/units/G-MATH-LINEAR-CONSTRAINT/manifest.json --out evidence/stress-tests/polynomials-six-core/golden-control --mode PAGES` | 0 | Six non-draft roles plus index. |
| Quality command for `golden-control`, `--subject Mathematics --product-id FIXTURE-MATH-LINEAR --report .../golden-control-quality.json --strict` | 0 | PASS, zero findings. This is a candidate comparator, not an accepted standard. |
| `node tools/site-audit/core-page-audit.mjs <render-directory> --json <audit.json>` on each control | 0 each | [empty Chromium audit](chromium-audit.json), [candidate Chromium audit](golden-chromium-audit.json). Android portrait/landscape measurements are preserved there. |
| `node evidence/stress-tests/polynomials-six-core/browser-interaction.mjs` | 0 | [Browser interaction](browser-interaction.json) at 800×1280: empty Core1A has zero units, attempts, search corpus and only a heading in accessibility; candidate has one unit, one locked attempt, search filters, precommit reveal blocked and postcommit unlocked. |
| `node tools/print/print-product.mjs evidence/stress-tests/polynomials-six-core/rendered --out evidence/stress-tests/polynomials-six-core/pdf` | 0 | Six learner PDFs. `pypdf` extracts only title/subject strings (83–93 chars each); full text and PDF hashes are in inventory. |

The untrusted snapshot consists of byte-for-byte copies of `C:\CodeA\G9_I329\Mathematics\library\polynomials.v1.json`, `polynomials-bank.v1.json`, and its original manifest. Only `replay-manifest.json` changes relative paths to the snapshot in this worktree. That checkout was read only. [inventory.json](inventory.json) records all 65 package and 29 bank schema errors; missing root fields include `relations`, `representations`, `evidence`, and source custody fields. The first renderer error is sufficient to stop, even with `--draft`.

## Learner and source assessment

| Requirement | Polynomials status | Evidence |
|---|---|---|
| One canonical microtopic across CORE1/1A/1B | FAIL | Main has no Polynomials package; empty control has zero `data-g9-unit` on every role. The untrusted package cannot load. |
| Core2 real source item and custody | FAIL | Main has no Polynomials bank; empty control has `ACQUIRE_SOURCE`. Untrusted bank has 29 schema errors, including required custody fields absent. No official PYQ status is inferred. |
| Core2A supported practice | FAIL | Empty control has `AUTHOR_PRACTICE`; untrusted questions have missing structural fields and answer verification. |
| Core2B transfer and lineage | NOT_RUN | No valid parent practice or canonical transfer record available. The empty renderer produces a shell but no unit. |
| Figure, attempt, hint, search and accessibility | FAIL / NOT_APPLICABLE | Empty Core1A accessibility tree has only the heading; zero attempts or gated disclosures. Candidate interaction succeeds as a renderer control. |
| Quality | FAIL | Empty control: 8 findings and draft. Untrusted fixture cannot reach quality on generated pages. Candidate: PASS, zero findings. |
| PDF text | FAIL | Six blank-content PDFs carry headings only. PDF generation is no proof of instructional content. |
| Human review and Owner acceptance | NOT_RUN | No authentic Polynomials prototype exists to review. No publication. |

The earlier pasted transcript at `C:\Users\reall\.codex\attachments\f31f368e-9103-4414-9e43-c05fd505c82e\Pasted text.txt` shows wrong-way steps: placeholder capability/action, `inferential_jump`/`entry_assumptions` filled with placeholders, removal of `elicitation.attempt.task`, insertion of a generic `h1` hint, and an unverified bank item called “authentic.” It then wrote draft HTML and PDFs into `public/`. These are falsifiers for source truth, learner decision quality and publication state; an exit-zero render would not cure them. The old output is not used as authority here.

## Judgment and next academic inputs

The renderer control demonstrates the current six-role path and learner gating can work on a separately authored candidate. The Polynomials evidence does **not** establish a coherent, source-based six-Core prototype. Before another P3 run, author one actual Polynomials microtopic with a cited, accessible source and source custody; complete schema-valid capability, relations, representation/figure stages, elicitation and exit tasks, Core2A practice with checked answer/hints, and a genuinely changed Core2B transfer. Core2 requires a separately verified source question; do not represent authored practice as a PYQ. Compare the resulting learner choices, reveals and search against the candidate, then get independent human critique and Owner decision on the exact render digest.
