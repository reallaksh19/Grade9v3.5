# Cumulative blueprint repair: current R3 review package

The D1 B32 → shared rule → A31 sequence, then D2 B34/A33, D3 B36/A35 and D4 B38/A37, is implemented and measured in the new 5 October repair round. Registry/Core1A/Core2 are 1.12.0/1.6.0/1.7.0. Original submissions remain frozen.

Read [current implementation and evidence](closure-20261005/README.md) and [final-assurance.json](closure-20261005/final-assurance.json) first. All-eight replay, 80 source-question interactions, strict/tablet browser checks, 26 fresh learner PDFs and final focused tests PASS. The clean full suite remains FAIL with no additional failure IDs against seed. Eight matrix candidates are authored and solution-checked; independent 28-cell and 960-facet acceptance remains open. Physics and all six Mathematics roles are exercised, with Mathematics source/gate limitations preserved.

The original ISS*/rendered products are regenerated current outputs. Each ISS*/qrt-repair-ledger.json is a current hash-bound review worksheet, not independent certification. The previous text below is retained as historical checkpoint documentation; its NOT_RUN, PDF and coverage statements are superseded only by the explicitly scoped new measurements.

---

# Blueprint 1.10 correction candidates

Eight frozen submissions informed four cumulative B→blueprint→A cycles. Corrected copies are stored here; original PRs are not rewritten. This is a post-freeze correction round, not a blind trial or golden certification.

Read REPORT.md and each ISS*/cycle-receipt.json. Canonical inputs are under ISS*/inputs; referenced SVGs are under ISS*/assets. The HTML under ISS*/rendered is generated through the production renderer, with local CSS/JS beside it. Open core1a.html and core2.html with a local server for learner review. Linked learner PDFs have not been built.

## Reproduce the published artifact snapshot

The original artifact snapshot remains at `46e91c9ec4285e14ca0db469eda281ff31df596a`. [Fresh recovery](recovery-20261004/README.md) reconciles the interrupted amendment. The latest [compatibility slice](compatibility-20261004/README.md) regenerates all eight packs with unchanged corrected canonical inputs and explicit authority hashes. Replay and the limited tablet profile PASS; full suite and broader Core1A audit FAIL. Missing historical logs are not claimed recovered.

Python 3.12, Node 22, jsonschema 4.17.3 and lxml were used for the recorded checks. Install project dependencies or these explicit Python packages in an isolated environment before running:

```sh
python evidence/blueprint-cycles/tools/replay.py --repo . --out replay-local.json
python evidence/blueprint-cycles/tools/final_cycle_check.py
python evidence/blueprint-cycles/tools/test_learning_repair.py -v
python -m unittest tests.test_core2_v2 tests.test_core2_v2_quality -v
python evidence/blueprint-cycles/tools/quality_static.py --repo .
```

Replay validates schema, custody/reference completeness, selection and repair bindings, then requires all three regenerated pages and the digest to match each stored receipt. It uses the production renderer API with an explicit local JSON Schema resolver; it does not claim eight default-CLI or GitHub Actions cold starts.

The artifact checker parses saved HTML and inert templates. The Node harness checks interaction logic with DOM stubs. Neither measures actual browser layout, accessibility or learning effectiveness.

The static-gate command writes each actual verdict. Zero content findings is compatible with FAIL / RENDERED_RULES_NOT_MEASURED. Do not convert the command's exit status into a quality PASS.

## Pending promotion gates

- Real tablet/browser inspection of initial, hint, committed, solution, diagnostic, repair and return states, including geometry change, focus, keyboard/touch, overflow and search protection.
- Independent answer/warrant/check, ancillary task, source and twelve-facet review on the newly hashed artifacts.
- Difficulty/hardest-target calibration and evidence for the eight uncovered canonical cells.
- A nonchemistry specimen for module generality; learner testing where effectiveness is claimed.
- Publication/PDF closure and owner decision.

The six focus tests, source pins and all eight replay results are evidence of their stated checks only. All ledgers remain AUTHORED_REQUIRES_EXACT_RENDER_REVIEW and golden false. The latest limited tablet audits PASS, with figure legibility and broader phone/focus findings still open. Full repair/return, print and learner-effectiveness review remains pending.

author_repairs.py and visual_repairs.py preserve authored correction data and SVG constructors. The original source branches/materializers remain the provenance for the first submissions. Replay consumes the stored corrected canonical inputs, so it needs no chat-specific scratch directory or hidden authoring state.

Final all-band amendment: distinct lesson anchors now bind the actual target question, its real crux move and construction unit, and cannot bypass the hardest-target gate. The authored D4 model probe is visible on Core1A construction as an optional governed component; Core2 diagnostic feedback remains attempt-gated. A dedicated regression rejects a foreign target despite a matching legacy bank_anchor_ref.
