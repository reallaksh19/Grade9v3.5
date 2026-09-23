# Pass 1 question-bank validation results

Issue: #216  
PR: #217  
Branch: `question-bank/pass1-provenance`  
Last checked: 2026-09-23

## Canonical bank under test

| Topic | Accepted |
| --- | ---: |
| Physics — Newton's Laws of Motion / NLM | 13 |
| Physics — Motion in 2D / Motion in a Plane, linear/projectile only | 15 |
| Physics — Motion in 1D, relative motion only | 3 |
| Chemistry — Redox Reactions | 26 |
| Chemistry — Some Basic Concepts / Mole Concept / Stoichiometry | 20 |
| **Total** | **77** |

No practice set or exam generation is enabled.

## Executed repository-connected validation

**PASS — 4,275 assertions, 0 failures.**

The validation was executed directly against the pushed branch through the repository connector and covered all 77 canonical records.

Validated invariants:

- 77 unique canonical question IDs;
- 77 unique historical source identities;
- 77 canonical questions resolved to exactly one accepted authoritative ledger record;
- exact ledger paper URL / exam / year agreement with per-question source custody;
- official-organizer source hosts and subject-qualified original identifiers;
- honest `PYQ_ADAPTED` origin plus parent and changed-field custody;
- source refs and origin refs resolve;
- source hints remain empty unless actually supplied; authored scaffolds remain separate;
- reasoning route, crux move, independent answer check and rubric resolve;
- component-based D1–D4 scoring recomputes correctly and does not use exam label as difficulty;
- Physics capability/family refs resolve against canonical NLM, 2D kinematics and relative-motion libraries;
- Chemistry capability/family refs resolve against the explicit PASS-1 local-proposal concept inventory;
- donor registries remain present and every donor candidate remains `SOURCE_UNVERIFIED` / quarantined;
- no circular-motion or centripetal leakage;
- five JEE Main 2026 accepted records require first-party paper custody plus the official NTA final key;
- relative-motion coverage is three accepted official-parent items;
- donor claims `1D-Q16` and `REDOX-Q01` remain quarantined because their claimed shift does not match the inspected official paper.

## Committed unit-test contract

`tests/test_competitive_exam_question_bank.py` now enforces:

- canonical counts and topic counts;
- provenance honesty and adaptation-parent resolution;
- source-ref and authoritative-ledger resolution;
- duplicate IDs and duplicate source identities;
- source hint / scaffold separation;
- answer verification and reasoning-route integrity;
- difficulty metadata;
- Core2B transfer-vs-same-family classification;
- concept/capability/family resolution;
- JEE Main 2026 official paper + final-key custody;
- relative-motion minimum custody;
- circular-motion exclusion;
- donor preservation and quarantine.

## Runner / CI status

A local clone-based Python test invocation could not be started because the execution container could not resolve `github.com`; this is an environment/network limitation, not a test failure. GitHub reported no Actions workflow run or commit status attached to the checked PR head at validation time.

The connector-backed invariant execution above is therefore the recorded PASS result for this update. A future CI run, if attached by repository configuration, should execute the committed Python test file without changing PASS-1 scope.
