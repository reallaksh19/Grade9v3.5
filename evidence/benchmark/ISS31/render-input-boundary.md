# Issue 31 — production-input boundary

Status: **OPEN / NOT RUN**, not a claim of completion.

The benchmark requires a Chemistry Core2 + Core1A learner product while preserving Q1–Q10 as owner-supplied inputs. At the pinned launch commit `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`, the governed renderer can consume an owner-supplied bank, but the repository's authoring command `Shared/tools/owner_bank.py` explicitly says that owner-supplied banks are currently used only by the TEST sandbox and enforces creation under `TEST/question-bank/`. The Chemistry library at the pinned seed contains an exam bank but no subject package for this hybridisation slice.

I therefore did **not**:
- relabel these questions as official/PYQ;
- put an owner bank into `Chemistry/library/exam-bank/`;
- bypass the documented writer policy by manually inventing a Chemistry owner-bank production location;
- create a second renderer or hand-edit generated HTML;
- treat TEST output as Chemistry output.

What is complete is the academic/custody layer in `evidence/benchmark/ISS31/`: verbatim input, independent solutions, five-component difficulty, demand/QRT classification, learner-relative X/Y/Z/W, misconception diagnostics, source cards, and an interaction specification for the hardest target.

What remains for a governed learner-product render is a repository-authorised Chemistry path for owner-supplied bank custody (or an owner-approved generalisation of the existing owner-bank path), plus an executable repository sandbox/runtime. Once that exists, the intended manifest scope is `output_roles: ["CORE1A","CORE2"]` and rendering must use `Shared/tools/render_core.py` only.
