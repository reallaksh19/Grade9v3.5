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

- SBC-1 — Learner: Core2 now exposes distinct source/authored hint ladders, reasoning, offline math and correctly printed options after the appropriate commitment.
- SBC-2 — No new gate: the Owner subsequently authorized local numeric and difficulty-based structural checks. They report FAIL for incomplete support and tally mismatches; they do not prevent research, draft rendering or replace Owner publication. This is an explicit amendment to the original no-count-gate direction, recorded in PLAN_UPDATE.
- SBC-3 — Thinking, not filling: reviewed actual rendered HTML, browser interaction and PDF pages; found and corrected hidden print options and dynamically inserted hint failures. Counts alone cannot establish pedagogical quality.
- SBC-4 — One of everything: existing source inventory, package records, sole Core renderer and exact-render publication authority retain ownership. Packet reports are derived observations, not another academic ledger.
- SBC-5 — Construction over policing: inert payloads prevent premature help exposure; distinct ladder IDs and delegated handlers make inserted hints function; print CSS preserves options. Local tallies catch omissions at the delivery boundary.
- SBC-6 — Coherence: schemas, renderer, method guidance and negative tests reflect Medium=D2 / Hard=D3–D4 and digest-bound reviewed visual exceptions. The mistaken unconditional renderer hint quota was removed within this slice.
- SBC-7 — Honest state: full suite FAIL with unchanged failure IDs; actual browser/PDF checks PASS within stated scope; inventory NOT_RUN and specimen SVG FAIL. No golden-quality or acceptance claim.
- SBC-8 — Convergence and cost: implementation and evidence pushed for review; final full run took 438.627 seconds. Monetary/token cost is unavailable. Remaining review focuses on disclosed content quality and baseline failures.
- SBC-9 — Reusable by others: FIRST-STAGE-REVIEW documents the command and interpretation; HTML/JSON reports retain item IDs and concrete reasons for any subject's uploaded inventory and selected Core2 packet.

## Task Snapshot

#352 / #353: shared projection and packet checks implemented and locally verified as above; awaiting Owner review. #354 / reverted #356: recovery proceeds on `codex/interaction-recovery`, with normal EXPLORE integration and real-browser evidence; not merged. Parent programme is unchanged (`PARENT_PROGRAMME: none` for #352); no independent programme Handover index is created.
