# IMO intake #327 — claim-first V3.2 candidate plan

**Status:** pre-materialization candidate; no child issue/PR binding, no accepted progress,
no protocol cutover, no source Core2 admission and no learner publication. This file
does not override the active Grade9v3.5 V3.1 execution lease.

- Programme root: [#327](https://github.com/reallaksh19/Grade9v3.5/issues/327)
- Proposal: [imo-327-delp-proposal-v2.json](imo-327-delp-proposal-v2.json)
- Requested pinned protocol: [Common@13989969f6b7e432c4f7c1ddfe975449dba53593/skills/engineering-pr-delivery-v3.2](https://github.com/reallaksh19/Common/tree/13989969f6b7e432c4f7c1ddfe975449dba53593/skills/engineering-pr-delivery-v3.2)
- Actual operating protocol selected in Grade9v3.5: `relay/PROTOCOL_SELECTION.yaml` → V3.1, with a checked-in ACTIVE #212 lease and CLOSED GitHub #212. **That disagreement needs governed reconciliation.**

## Required release checks

The focused `test_imo_327_claim_first_proposal.py` uses only Python's standard
library. It proves basic claim coverage, weight conservation, semantic-unit class,
scope, dependency and staged-release guards, including negative mutations.
**This is a PRECHECK, not the official Common V3.2 decomposition validator.**

Once a runner has the exact pinned Common checkout, invoke:

```bash
python /path/to/Common/skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py \
  validate-graph --graph TEST/imo-research/intake/imo-327-delp-proposal-v2.json
python /path/to/Common/skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py \
  decompose-check --graph TEST/imo-research/intake/imo-327-delp-proposal-v2.json --json
```

Publish the actual exact input digest, findings, outcome and `proposal_digest` only after
the official validator is executed. Never fabricate a `released_proposal_digest`,
release child bindings, or set up provider progress projection just because this
structural precheck is green. Any changed graph must repeat the official check.

**Dependency rule:** F04 (homepage) and F06 (role-specific release review)
may qualify a reviewed Core1A-only Stage A without F05 source rights being
satisfied. An authentic Core2 Stage C must separately clear F05 and its own
F06 gate. This separation is not permission to bypass F03 reviews when
author-authored practice is included.

**Material boundaries:** keep #308/#312 academic package edits serialized
on one successor; keep #294 custody and #313 QRT authority separate;
keep shared renderer and public/docs outside this candidate plan PR.
