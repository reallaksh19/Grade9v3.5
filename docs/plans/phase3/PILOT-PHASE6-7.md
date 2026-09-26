# Phases 6 and 7: pilot and scale-out (status 2026-09-26)

Part of [LEARNER-PRODUCT-QUALITY-REBUILD.md](../LEARNER-PRODUCT-QUALITY-REBUILD.md).

## Phase 6 pilot: running

| Unit | Package | Work | Session |
|---|---|---|---|
| Physics, Motion in a Plane | `Physics/library/phy-kin-2d-motion.v1.json` + research chapter PHY-11-MOTION-IN-A-PLANE | depth duties (author), staged figures (illustrator), X2/X5 official questions (researcher) | author `session_01PXH5D9TfH4bqHq3pzkHj8L`, illustrator `session_018jiYRhSgrQ1N8jYceS5hLK`, researcher `session_01TSLUhXeAu698KjxmZUC96r` |
| Physics, Laws of Motion (friction, connected bodies) | `Physics/library/phy-nlm-first-law.v1.json` | depth duties, figures | same author and illustrator |
| Mathematics, Linear equations | `Mathematics/library/linear-equations.v1.json` | depth duties, figure | same author and illustrator |
| Chemistry, Mole concept | new research library `Chemistry/research/` (scaffold by the owner's session) | spine expansion, evidence harvest | same researcher |

- **Branches.** Author and illustrator work push to `pilot/phase6-depth`; research to `research/physics-library`. The owner's session merges.
- **Acceptance (unchanged):**
  - `build_products.py build` shows PASS for the unit;
  - Audits #296 and #298, re-run on the output, find no S0 or S1;
  - the owner reviews one unit per subject;
  - cost and time are recorded (`cost_ledger.py`).

**Known limits of the pilot**
- **Core2 source items.** Physics has an exam bank. Mathematics and Chemistry need source questions researched into the evidence pipeline before their Core2 can pass (`ACQUIRE_SOURCE`).
- **Prerequisite bridges.** `TEACH_PREREQUISITE_BRIDGE` (12 today) needs researched capabilities, possibly in another subject.
- **Chemistry is a research-first unit.** It has no library package until its nodes are verified and promoted, so it is the slowest of the four.

## Phase 7 ratchets: in place

- **Product gaps may only go down:** `products/ratchet.v1.json` (713 gaps across 21 products today), `tests/test_products_ratchet.py`, `build_products.py ratchet --write` after an improvement.
- **Site navigation and tablet audits** keep their own baselines (`tests/fixtures/site-audit/baseline.json`, PR #295).
- **Calibration** is strict both ways, so a contract change that stops catching an audited defect, or starts flagging something unreviewed, fails.

**Not started:**
- **Chapter-by-chapter scale-out.** It waits for the pilot's acceptance.
- **Backfill of the legacy site pages.** Each is replaced when its product passes.
- **The monthly owner sampling review.**

## Spend so far

`python3 Shared/tools/library_board.py --subject Physics --budget`: $39.20 recorded over the 14 pilot research units, about $2.80 per unit against the proposed $15 ceiling. This covers the three original sessions and the two fix-up sessions. The pilot sessions' costs are added when they finish.
