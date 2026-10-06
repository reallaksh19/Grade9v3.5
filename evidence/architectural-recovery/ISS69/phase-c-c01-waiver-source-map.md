# ISS69 PHASE-C — C01.4A Core1A waiver source mapping

Material basis: `fix/iss69-phase-c-runtime-alignment@d779004d6bc33584720c3098c134bb6a6a2c2f16`

Recovered authority: `BP-CORE1A-CONSTRUCTION@1.8.0`

## Applicable expected repeated components

| Component | Level | Repeat scope | Authored content source | Waiver scope |
| --- | --- | --- | --- | --- |
| `WORKED_EXAMPLE` | EXPECTED | PER_CONSTRUCTION_UNIT | `construction_units[].worked_anchor_ref`, `construction_units[].bank_anchor_ref`, or governed lesson anchor | construction unit |
| `STAGED_VISUAL` | EXPECTED | PER_CONSTRUCTION_UNIT | `construction_units[].representation_ref` + authored representation stages | construction unit |

`TRAP_REPAIR` and `QUICK_CHECK` are OPTIONAL, so they do not need applicability waivers merely because they are absent.

## Canonical waiver key

The existing blueprint/component contract defines:

```text
extensions["grade9v3:component_waivers"] = {
  "COMPONENT_ID": "written reason"
}
```

Blank reasons do not count. REQUIRED components cannot be waived.

## Record hierarchy

The Core1A renderer currently obtains:

```python
microtopic_waivers = waivers_of(microtopic)
unit_waivers = {**microtopic_waivers, **waivers_of(unit)}
```

Therefore:

1. a microtopic-level waiver can act as a broad default;
2. a construction-unit waiver overrides the same component key for that unit;
3. both `WORKED_EXAMPLE` and `STAGED_VISUAL` are passed through `unit_part(..., waivers=unit_waivers)`;
4. the component contract emits a hidden `data-g9-component-waiver` marker only when the EXPECTED component body is absent and a non-blank reason exists.

## Architectural decision

For repeated Core1A applicability, the **construction unit is the authoritative scope**.

A microtopic-level waiver is retained only as backward-compatible/default authoring support. New recovery tests must exercise explicit unit-level waivers so one construction cannot silently waive another.

Expected behavior:

- unit U1 may waive WORKED_EXAMPLE without waiving U2;
- unit U2 may waive STAGED_VISUAL without waiving U1;
- an authored component wins by presence: a waiver is relevant only when the component body is absent;
- the waiver marker is governance evidence, not learner-facing filler;
- the waiver reason must survive in ctx.waived / receipt evidence.

## C01.4B–D implications

C01.4B must prove WORKED_EXAMPLE unit waiver projection.

C01.4C must prove STAGED_VISUAL unit waiver projection.

C01.4D must prove isolation across units, including override behavior.

No production waiver change is justified by C01.4A itself; the current mechanism is structurally compatible with the recovered blueprint and now needs direct semantic tests.
