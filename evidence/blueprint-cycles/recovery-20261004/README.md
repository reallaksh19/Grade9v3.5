# Fresh recovery execution — 4 October 2026

Plan: https://github.com/reallaksh19/Grade9v3.5/issues/29#issuecomment-5982233572.
Candidate authority: `97c18d846b1efc14c4e1dc7028ef5dcb861f3cc9`; frozen seed: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`.
Protocol: `reallaksh19/Common@149770a21ca073df49717a96e2106c967adddc2d:skills/engineering-pr-delivery-v3.2`.

These are new observations, not recovered predecessor logs. Historical artifacts at `46e91c9ec4285e14ca0db469eda281ff31df596a` replay PASS for all eight packs. Current-authority replay initially failed all eight stale receipts, then passed all eight after production-API regeneration. Canonical corrected inputs remained byte-for-byte unchanged. Render receipts record current authority and canonical input SHA256s; historical source digest fields are retained with their limited meaning.

The pending 63-file inventory has 25 exact matches, 37 different files and one missing historical compatibility report. Twenty-four regenerated HTML files match the predecessor's expected hashes. Enhanced new receipts and fresh logs are deliberately different. The missing old report is not fabricated. The earlier 66-test claim remains historical; six focused tests pass again here, and the full candidate suite ran separately.

Full local suites: seed 2,289 tests, 77 failures, 52 errors, five skipped; candidate 2,289 tests, 80 failures, 58 errors, five skipped. Nine additional failure IDs are in `full-suite-comparison.json`. Both suites FAIL. The candidate's generated evidence changed while the suite ran; production authority stayed unchanged. This comparison guides isolated reproduction and does not by itself adjudicate origins. Raw command logs and summaries are included.

Actual Chromium audits ran on all eight refreshed packs at four tablet viewports. All eight FAIL, including text/figure legibility, 38px header targets and reported focus problems. `browser-bindings.json` pins the measured pages and saved shell assets. The audit reports zero initial protected-search matches and zero horizontal overflow at these viewports, but this is not full interaction, keyboard, print, academic or learner-effectiveness acceptance. Inspect the raw measurements before attributing focus failures; hidden or disabled controls can require separate interpretation.

Hosted CI at candidate authority has completed: learner-platform-code-tests and v31-relay pass; friction-core-browser, core1a-tablet-browser, guardrails and canonical-assurance fail. See `hosted-ci.json`. Original eight submission PR heads were rechecked unchanged. No original source question, workflow tolerance, merge, golden status or learner publication was changed.

Reproduce generation with `python evidence/blueprint-cycles/tools/refresh.py --repo . --write --out refresh-local.json`, then replay with `python evidence/blueprint-cycles/tools/replay.py --repo . --out replay-local.json`. Regeneration resets browser evidence because it requires new measurement. Historical recovery observations remain bound to the recorded hashes even after later changes.

Next: reconcile projections/specification and version-sensitive integration contracts; reproduce the quality observation's stale-reference failure; fix actual font/control defects; investigate link closure; repeat affected checks. The 28-cell coverage, cross-subject evidence and independent twelve-facet adjudication remain open.
