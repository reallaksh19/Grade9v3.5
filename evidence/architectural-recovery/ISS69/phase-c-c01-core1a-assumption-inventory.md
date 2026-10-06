# ISS69 PHASE-C — C01.1 Core1A renderer/audit assumption inventory

Basis: `fix/iss69-phase-c-runtime-alignment`
Recovered authority: `BP-CORE1A-CONSTRUCTION@1.8.0`

## Classification

| Location | Current assumption | Recovered classification | Owning unit |
| --- | --- | --- | --- |
| `Shared/library/core1a_construction.py` | every microtopic without misconceptions gets `MISCONCEPTION_REPAIR_MISSING` | **OPTIONAL** repair; absence is valid | C01.2 |
| same | every microtopic must map a question exposed to CORE1A as worked anchor | **EXPECTED/WAIVABLE**, not universal | C01.2 |
| `render_core.core1a` | missing worked anchor gets manual `AUTHOR_WORKED_ANCHOR` gap before component policy runs | **EXPECTED/WAIVABLE**; component authority must decide absence | C01.3/C01.4 |
| same | missing per-unit `independent_checks` gets `AUTHOR_INDEPENDENT_CHECK` gap | `QUICK_CHECK` is **OPTIONAL**; independent exit evidence remains mandatory through `EXIT_RECALL` | C01.3 |
| `_quick_check()` | title/structure is always “1-2-3 quick check” / triad presentation | optional compact checks may have any useful count/role | C01.3 |
| Core1A unit loop | every construction emits a `g9-cu-support` wrapper | support wrapper should exist only when repair/check content or an explicit governed waiver marker needs projection | C01.3/C01.4 |
| `_toughest_unit_gaps()` | hardest question must itself be the worked example via `bank_anchor_ref` | hardest target must bind to the construction/crux; source question need not become teaching anchor | C01.3 |
| same docstring/messages | D-band determines step/stage depth | forbidden by recovered contract; D-band is not panel/depth count | C01.3 |
| `STAGED_VISUAL` component call | absence flows through component policy | **EXPECTED/WAIVABLE**; basic mechanism is already correct | C01.4 |
| `WORKED_EXAMPLE` component call | component policy can handle expected/waiver, but manual pre-gap bypasses it | remove bypass; preserve invalid-present-anchor errors | C01.3/C01.4 |
| exit task | prompt/model closure remains required | **REQUIRED**; preserve | no change |
| construction steps/key step | authored teaching path/inferential jump required | **REQUIRED**; preserve | no change |
| relation checks | governing relations with no independent check are structural debt | separate from optional per-unit quick-check; preserve unless later evidence says otherwise | no change |

## Important distinction

`QUICK_CHECK` becoming optional does **not** remove independent learner evidence from Core1A. The mandatory exit task remains the independent closure. A per-construction quick check is only an intermediate teaching operator.

Likewise, making `WORKED_EXAMPLE` waivable does not permit an empty construction. The construction route, key inferential step, and exit remain required.

## C01.2 target

Change only the construction audit:
- stop reporting missing misconception repair as debt;
- stop reporting missing worked anchor as debt;
- keep validating misconception rows and worked anchors when present;
- preserve all required construction/representation/exit checks;
- adjust manual-review wording so worked-anchor review is conditional on presence.
