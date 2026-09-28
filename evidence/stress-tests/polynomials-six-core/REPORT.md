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

The renderer control demonstrates that the six-role path and learner gating can work on a separately authored candidate. The initial negative controls did **not** establish a source-based Polynomials prototype; the continuation below adds one bounded microtopic. Core2 still requires a separately verified source question. Independent human critique and an Owner decision on an exact future render remain necessary.

## Source-backed continuation: one microtopic, incomplete six-role product

After the negative controls, I authored a bounded [stress package and manifest](prototype/records.json) via [build_records.py](prototype/build_records.py). The academic source is the official [NCERT *Ganita Manjari*, Grade 9 Part I, Chapter 2, “Introduction to Linear Polynomials,” §2.1](https://ncert.nic.in/textbook/pdf/iemh102.pdf), PDF page 3 / printed page 18. Its PDF SHA256 is `dbc30792858fa1858d248e4802977cb794b537c1a49f166e2777ea37baf57b02`, matching existing acquisition `ACQ-DBC30792858FA1858D24`. The download is a local input omitted from git; fetch that exact URL and verify its hash to replay source inspection. The scope is degree of a one-variable polynomial after simplifying like terms, not the whole Polynomials curriculum. [WORKLOG.md](prototype/WORKLOG.md) records the authoring corrections and self-critique.

Prototype commands, all from repository root on the recorded execution basis:

| Command | Exit | Result |
|---|---:|---|
| `python evidence/stress-tests/polynomials-six-core/prototype/build_records.py` | 0 | Writes the candidate JSON package and manifest; package schema validation has 0 errors. |
| `python Shared/tools/render_core.py gaps --manifest evidence/stress-tests/polynomials-six-core/prototype/manifest.json` | 1 | One depth gap: `CORE2 ACQUIRE_SOURCE` on `STRESS-MATH-POLY-DEGREE`; one distinct subject-authority finding: `GATE_RELATION_UNKNOWN` on `REL-MATH-POLY-DEGREE`. |
| `python Shared/tools/render_core.py build --manifest evidence/stress-tests/polynomials-six-core/prototype/manifest.json --out evidence/stress-tests/polynomials-six-core/prototype/rendered --mode PAGES --draft` | 0 | Six role HTML files and index, receipt marked draft with one gap. Five roles contain a learner unit; Core2 is a shell. |
| `python Shared/tools/quality_gate.py evidence/stress-tests/polynomials-six-core/prototype/rendered --subject Mathematics --product-id STRESS-MATH-POLY-DEGREE --report evidence/stress-tests/polynomials-six-core/prototype/quality-browser.json --strict` | 1 | FAIL: 2 S1 findings (Core2 lacks slots; draft render stamp is not accepted), plus draft reason. Browser measurement ran. |
| `node tools/site-audit/core-page-audit.mjs evidence/stress-tests/polynomials-six-core/prototype/rendered --json evidence/stress-tests/polynomials-six-core/prototype/chromium-audit.json` | 0 | Portrait/landscape: no overflow, no undersized targets, no JS errors; one accessible SVG and one unit on each populated role. Core2 has zero slots, SVGs or attempts. |
| `node evidence/stress-tests/polynomials-six-core/browser-interaction.mjs` | 0 | At 800×1280, Core1A has one unit and one locked attempt. A precommit reveal is blocked, typed answer commit unlocks it, and a nonmatching search hides the unit. Accessibility tree is in [browser-interaction.json](browser-interaction.json). |
| `node tools/print/print-product.mjs evidence/stress-tests/polynomials-six-core/prototype/rendered --out evidence/stress-tests/polynomials-six-core/prototype/pdf` | 0 | Six learner PDFs; extracted text counts are 1023, 1488, 612, 103, 632 and 936 characters for CORE1 through CORE2B. Core2 text is heading only. PDF hashes are in inventory. |
| `python evidence/stress-tests/polynomials-six-core/audit_inventory.py --verify` | 0 | Read-only SHA256 verification PASS. It never overwrites inventory. |

The candidate offers a real Core1/1A/1B/2A/2B learning path, but is **not golden-like as a six-Core product**. The golden candidate has a populated Core2 and quality PASS with zero findings; this prototype has an explicit Core2 source gap, unregistered Mathematics relation and draft quality FAIL. A consequential revision removed misleading reused figure coefficients and replaced a transfer outside the inspected source scope; the render digest changed from `b559908ec6103294` to `d7cad4dc11cadf5d`. Human review and Owner acceptance are NOT_RUN. No page was published.
