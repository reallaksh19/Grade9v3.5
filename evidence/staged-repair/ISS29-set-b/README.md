# Issue 29 staged repair evidence

This records a **code and consumer pilot**, not acceptance of the four Set B candidates or a learner publication.

Frozen question inputs and original assets are in `tests/fixtures/staged_set_b`. Their candidate heads and original asset paths are recorded in `cases.json`. The replay selects #53 Q1, #54 Q9, #55 Q1 and #56 Q5; other question defects are outside these four partial contexts.

Regenerate both pages and exact-byte/authority hashes with:

```text
python tools/staged_set_b_replay.py --out evidence/staged-repair/ISS29-set-b/rendered
```

`rendered/before.html` preserves the old figure/support selection. `rendered/core2.html` adopts the optional scene and protected-move bindings. `replay-report.json` records preserved stems/answers/support wording, deferred support, asset locations, authority hashes and actual gaps/advisories. Both pages are evidence artifacts with partial concept lineage; candidate navigation/packaging is not accepted here.

Local checks: 111 Python tests and four Node layout tests pass. The raw logs are retained. `legacy-comparison.json` records identical hashes for all four unchanged legacy question fragments against integration base `91719ad8df2bfc06c6a481590d2e24c510c24835`. Whole regenerated-page stamps are not claimed identical under changed renderer authority.

Browser evidence is from the in-app browser at the recorded viewport. `initial-facts.json`/DOM establish four owned given-stage instances and no worked-stage groups in the live DOM. `safe-hint-facts.json`/DOM/screenshot establish one safe requested D3 rung with no parameter answer. `after-attempt-facts.json`/DOM establish four deferred rungs and the correct factorisation after a test attempt. `worked-stage-dom.txt`/screenshot establish the stage control's response. These files refer to the checked-in `rendered/core2.html` bytes.

`core1a-layout-facts.json` is a separate measurement of frozen #55's original Core1A page at 1280×800 against its active single-pane blueprint. It uses positive DOM bounds because `checkVisibility` is unavailable in the in-app evaluation interface; it is not a full CLI audit receipt. The production observation continues to use its original visibility method.

Known gaps are retained: partial context metadata ownership; D2 missing conditions advisory; D3 one safe rung below the existing two-rung floor. No filler or semantic acceptance status is manufactured. Full forty-question acceptance, matrix/subject generality, candidate packaging and previous Linux phone overflow remain open.

See the tracked work report and `docs/method/STAGED-SET-B-REPAIR-ADOPTION.md` for adoption, repeated-error clarifications and optional add-ons. No new universal publishing gate or blocker was added.
