# ISS69 PHASE-C — C03.1 quality/layout authority reconciliation

Material basis: `fix/iss69-phase-c-runtime-alignment@e4f9e4b6b3fb80ff127460b0019b28eaa8a4e60d`

## Authority chain

1. **Product/presentation policy**
   - `Shared/web/interactive-page-blueprints.v1.json`
   - each active role blueprint owns `responsive_policy`.
   - `STAGE_SUPPORT` may declare `primary_fraction`, `support_fraction`, and `expanded_min_px`.
   - `SINGLE_PANE` explicitly means no expanded split.

2. **Renderer projection**
   - `Shared/tools/render_core.py::layout_css`
   - emits split CSS only when the selected blueprint says `expanded == STAGE_SUPPORT`.
   - it reads the fractions/minimum width from the selected blueprint; it does not own a universal ratio.

3. **Browser observation**
   - `tools/site-audit/core-page-audit.mjs`
   - reads the rendered page's `data-blueprint-ref`;
   - resolves that exact blueprint from the registry;
   - asks `layout-observation.mjs` for the expected split, when any;
   - records whether the measured layout matches the selected blueprint.

4. **Observation compatibility shape**
   - `Shared/quality/learner-observation.schema.json`
   - retains `rendered.stage_support_layout` as a legacy v1 field name.
   - its documented meaning is already: "rendered expanded layout matches selected blueprint responsive policy."
   - therefore `SINGLE_PANE` can legitimately produce `true` without a split.

5. **Quality judgement**
   - `Shared/quality/learner-quality.v1.json`
   - rule id `PAGE-STAGE-SUPPORT` and check field `stage_support_layout` are historical compatibility identifiers.
   - they must judge the observer's blueprint-derived boolean, not restate a universal 0.68/0.32 policy.

## Defect

The active quality rule text still says:

> Expanded tablets use the 0.68/0.32 stage-support layout.

That sentence conflicts with active Core1A `SINGLE_PANE` even though the observer/runtime already implement selected-blueprint semantics.

## Compatibility decision

Retain:
- rule id `PAGE-STAGE-SUPPORT`;
- observation field `stage_support_layout`;
- existing evidence JSON shape.

Change:
- active rule wording to selected-blueprint semantics;
- add direct tests around the layout-observation helper.

Do not:
- rewrite historical evidence files;
- mint a second layout field in v1;
- move responsive policy into the quality contract;
- special-case Core1A in quality code.

This preserves historical machine compatibility while restoring the authority direction:

```text
blueprint -> renderer -> browser measurement -> quality boolean
```

not:

```text
quality ratio -> renderer
```
