# TASK_EVIDENCE — Core2 projection and local packet checks

Code basis: `f8d8a0dd9953f910fd66c2364cf7107eca505f94`. This slice implements the Owner's amended numeric/structural direction. Medium=D2; Hard=D3–D4. Hard SVG exceptions require a reviewer, explanation and current question digest. The existing three-rung support baseline is used. No CI workflow was added.

## Actual artifacts

- [Core2 HTML](rendered/product.html), [learner PDF](rendered/product.pdf), [key PDF](rendered/product.key.pdf).
- [Owner numeric/structural table](review/index.html), [machine findings](review/packet-check.json).
- [Chromium observations](browser/browser.json), tablet screenshots and accessibility snapshots beside it.
- [PDF text evidence](rendered/pdf-text-evidence.json); extracted text and rasterized pages beside the PDFs.
- These use the existing golden candidate, not newly authored library content. Its missing useful Hard-question SVG is **FAIL**. Its upload denominator is **NOT_RUN** because this specimen did not supply an uploaded-source inventory. Neither fact is relabelled PASS.

## Validation

Full local discovery: **FAIL**, 1,532 tests, 28 failures, 17 errors, 4 skips, 438.627 seconds. [Full tracebacks](pr353-packet-full-final.log). The [exact failure-ID comparison](failure-comparison.json) has no new IDs against `fe889b9…`; that prior slice replayed the failures at pre-PR `d60a939…`. Remaining failures include canonical registry/depiction contradictions, nested IDs, publication/runtime drift, corpus/explorer failures and generated manifest drift. They are not all dependency failures.

Focused packet/renderer/quality tests: **PASS**, 54 tests. Subsequent learner-state/golden/packet regression run: **PASS**, 19 tests, including the real Chromium learner-state test.

Actual offline Chromium: **PASS** for 1366×854, 1440×900 and 900×1440; no horizontal overflow, all measured touch targets >=48px, no failed requests or page errors, native MathML, invalid commitment stays locked, valid commitment materializes authored help, later hints work independently from the source ladder, and reasoning reaches the DOM/accessibility tree. Browser script: `tests/core2_packet_browser.mjs`.

PDF text checks: **PASS**, all four options survive both print modes, learner copy excludes authored help/reasoning, key copy includes them. Visual inspection found and fixed the earlier hidden-options defect. Current learner copy has 2 pages; key has 4. The candidate still has verbose generic reasoning and pagination splits; this is not a claim of golden pedagogical or visual acceptance.

GitHub Actions: **NOT_RUN**. Owner product acceptance: **NOT_RUN**. Merge: **NOT_RUN**.

## Step back: SBC-1 through SBC-9

- SBC-1: Intent is reusable learner support and transparent packet completeness, not topic-specific patches.
- SBC-2: Existing source inventory, question scaffolds/routes, representations and sole Core renderer retain ownership.
- SBC-3: Source hints remain distinct; rendered teaching is not misrepresented as source custody.
- SBC-4: Equal-count substitution, duplication, omitted inventory items and stale visual exceptions have negative tests.
- SBC-5: Actual HTML, Chromium, accessibility and PDF bytes were exercised; reports do not substitute for artifacts.
- SBC-6: Wrong-way findings were corrected here: dynamically inserted hint handlers, later-figure initialization and hidden print options. A global Core2 hint quota in rendering was removed; the difficulty-aware local checker owns the requested threshold.
- SBC-7: No second learner renderer, parallel academic package, topic library authoring or publication authority was added.
- SBC-8: Research and draft output remain available. FAIL prevents false completion claims; exact-render Owner acceptance still decides publication.
- SBC-9: This slice is reviewable separately from #356 recovery. Remaining specimen defects are disclosed, and no merge or product acceptance is claimed.

## Task Snapshot

#352 / #353: shared projection and packet checks implemented and locally verified as above; awaiting Owner review. #354 / reverted #356: recovery proceeds on `codex/interaction-recovery`, with normal EXPLORE integration and real-browser evidence; not merged. Parent programme is unchanged (`PARENT_PROGRAMME: none` for #352); no independent programme Handover index is created.
