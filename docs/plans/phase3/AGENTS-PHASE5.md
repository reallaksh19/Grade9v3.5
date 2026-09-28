# Phase 5: agents and prompts aligned to the contract

Part of [LEARNER-PRODUCT-QUALITY-REBUILD.md](../LEARNER-PRODUCT-QUALITY-REBUILD.md).

| Change | Where |
|---|---|
| **Depth duties** in the workflow. Each gives the role that does it, the exact fields, what to do, and the contract rules it serves. A test keeps the table and `package_depth.py` identical | `Shared/workflows/research-first.v1.json` → `depth_duties` |
| **Definition of complete:** no depth duty on the records **and** a rendered gate PASS. A label, a report or a COMPLETED status never counts | same file → `definition_of_complete`; author prompt |
| **Illustrator role** (staged SVG figures; clears BUILD_SCENE / STAGE_REPRESENTATION) | `docs/library-agents/ILLUSTRATOR.md`, `template/library-agents/05-illustrator.md` |
| **Author prompt:** completeness is the depth board plus the product gate, with the reference grammar as the model of "deep" | `template/library-agents/02-author.md` |
| **Verifier prompt:** product verification of a sample of rendered units against Audits 1 and 3, with independence from its authors | `template/library-agents/03-verifier.md` |
| **Board stages** beyond research nodes:<br>• `--depth` (record gaps);<br>• `--products` (gate verdict per product);<br>• `--budget` (spend against the ceiling) | `Shared/tools/library_board.py` |
| **Cost ledger and ceiling.** Proposed default: $15 per unit (researcher $5, author $4, verifier $3, illustration/render $3). REVIEW at 100% and ESCALATE at 200%, never a stop. The pilot's three sessions are recorded: $29.54 over 14 units ≈ $2.11 per unit | `Shared/tools/cost_ledger.py`, `Physics/research/work-rules.json` → `cost_ceiling`, `Physics/research/cost-ledger.json` |
| **Stress prompt acceptance** is now the gate report and the commands, not self-declared statuses | `evidence/stress-tests/MOTION-2D-SIX-CORE-RESEARCH-FIRST.md` §19, §21 |

**Exit gate (a thin item is caught and routed back automatically).** The tests show it:
- a thin real product renders only as a draft;
- the gate fails it on the audited rules;
- each gap appears as a named duty for a named role on `library_board.py --depth`
  (`tests/test_render_core.py`, `tests/test_quality_gate.py`, `tests/test_package_depth.py`).

The live dry run is the Phase 6 pilot.
