# NLM first-law trial packet

Status: **READY FOR OFFLOADED CONTENT TRIAL; TRIAL NOT RUN**. This packet prepares STEP-07 / WP7 for `Physics/phy-nlm-first-law`. It changes no academic library record, review verdict, acceptance file or published product.

## Exact baseline

- Source stack head: `ae0c377a8c02f4cd4b579bf170bfbed76809f40e` (draft PR-E #339, containing draft PR-A through PR-D). Trial work should begin from the Owner-approved integrated head when available, then re-render before editing.
- Manifest: `products/physics/phy-nlm-first-law.manifest.json`; renderer: sole `Shared/tools/render_core.py` (`render_core/2`); mode: `PAGES`.
- Baseline render digest: `15499c9f7bbdd871`, seven pages, zero renderer gaps. [RENDER-BASIS.json](RENDER-BASIS.json) records the SHA-256 of all seven page strings and all 86 file authorities the renderer fingerprints. Recompute after any change; never reuse this digest for a changed render.
- The round-four NLM review at [commit `cb84133a`](https://github.com/reallaksh19/Grade9V3/commit/cb84133a) names digest `f985270070b83ef9`. It is **stale** for the baseline above. The current review file retains that historical digest; it is not a current clearance.
- Owner acceptance: **none** for this baseline. No product is published by this packet.

## Execute in the one method

1. Assign one unit author on `unit/physics/phy-nlm-first-law` from an Owner-approved integrated base. Give them [AUTHOR-PROMPT.md](AUTHOR-PROMPT.md) and [ROUND-FOUR-FINDINGS.md](ROUND-FOUR-FINDINGS.md). A separate source reader supplies any needed independent source readback; the unit author keeps the task arc coherent.
2. The author revisits the findings against the **new** render, researches the teaching choices, and writes or updates `Physics/units/phy-nlm-first-law/{UNIT,DESIGN-NOTE,SELF-CRITIQUE,WORKLOG}.md` as needed. They own any content revision in a separate unit PR. A prompt is not permission to patch a record solely to clear a count.
3. At P3/P4, show the Owner a prototype and record notes. At P5, use `self_check.py --unit Physics/phy-nlm-first-law` as an advisory map, render on the 12.7-inch tablet profiles, and record the exact candidate digest, open source/readback items, spend and weaknesses. Push each phase.
4. Assign an **independent** reviewer using [REVIEWER-PROMPT.md](REVIEWER-PROMPT.md). They review the new exact digest in real raw HTML, browser DOM/accessibility/search/interaction and learner/key PDFs where relevant; they derive the physics independently and file review v2 with strengths, grouped findings and prior-finding dispositions.
5. The Owner decides whether to accept that exact candidate digest through `accept_product.py`. The reviewer and tools do not publish. Record the outcome and costs in [RETROSPECTIVE.md](RETROSPECTIVE.md). Nominate a G-PHY golden only after a genuinely accepted trial and Owner judgement.

The user-facing 12.7-inch shell audit in draft PR-D #338 used the current baseline digest; the Owner HTML reference for visual fidelity remains unavailable, so that comparison is **NOT_RUN**. General site repair belongs to #337, not this unit trial.
