# Motion in 1D RCA — 2026-09-20

## Scope

This audit covers the current Motion in One Dimension master suite:

- `public/physics/motion-1d/explorers/motion_in_1d/index.html`
- `public/physics/motion-1d/explorers/motion_in_1d/jee_questions_data.js`

The local question bank contains **18 diagnostic records** selected from a source corpus reported as **123 questions (2002–2026)**. The 18-record bank is therefore a diagnostic subset, not a local copy or full audit of all 123 source questions.

## Primary UI incident

### Symptom

Moving a slider repeatedly caused one or more canvases to grow taller. At larger parameter values, bodies, graph traces, labels, or event markers could also leave the visible canvas.

### Root cause 1 — recursive high-DPI height scaling

The previous `setupCanvas()` read the canvas HTML `height` attribute on every draw and then wrote a DPR-scaled value back to `canvas.height`.

On a device with DPR > 1 this formed a feedback loop:

```
logical height 180
→ backing height 360
→ next slider redraw reads 360 as the logical height
→ backing height 720
→ next redraw reads 720
→ ...
```

Every slider input calls a draw routine, so ordinary slider movement repeatedly amplified the canvas backing height and therefore destabilized layout.

### Repair

The logical CSS height is now captured once in `canvas.dataset.logicalHeight`. Every draw derives a fresh backing-store size from:

- stable logical height;
- current parent content width;
- bounded device-pixel ratio.

The drawing context is reset with `setTransform`, while CSS width remains `100%` and the logical height remains fixed. Repeated slider draws can no longer recursively mutate the logical canvas size.

## Secondary UI defects

### Fixed plotting domains pushed figures off-canvas

Several rigs used hard-coded world-coordinate domains that were smaller than the legal slider domain:

- displacement track used a fixed horizontal plotting scale while allowed `v0`, `a`, and time could produce positions hundreds of metres away;
- the v–t graph used a fixed velocity scale while permitted values could exceed it substantially;
- balloon graphics assumed `maxH = 160 m`, although legal release-height/speed combinations can exceed that;
- relative-pursuit road geometry assumed a fixed 250 m visual domain;
- the relative-gap graph used a fixed 15 s time horizon and an initial-gap-derived vertical scale;
- the sandbox used a fixed approximately ±30 m world view although its numerical integration can travel arbitrarily far.

These were drawing-domain bugs, not physics-domain limits.

### Repair

The displacement, balloon, relative-pursuit and sandbox rigs now derive padded plotting bounds from the actual state/event envelope. Tick spacing is generated from the current span, and velocity/acceleration arrows are visually clamped without modifying the physics state.

The v–x/a–x probe is also clamped when its stopping-displacement slider is reduced, preventing a stale probe coordinate from remaining outside the new domain.

### Event sliders had fixed horizons unrelated to the current physics

The balloon scrubber stopped at 8 s, the paratrooper scrubber at 20 s, and the pursuit scrubber at 15 s. Valid slider combinations can make the relevant physical event occur later than those fixed limits.

### Repair

- Balloon time horizon follows the current stone impact time.
- Paratrooper time horizon follows the current two-phase landing time.
- Relative-pursuit horizon follows the current overtake event with a small viewing margin.

Animation and scrubbing therefore use the same physical horizon as the current parameters.

### Window resize could clear a canvas without repainting it

Changing the backing-store dimensions clears an HTML canvas. The prior resize handlers resized the active canvas but did not consistently redraw it.

### Repair

Resize wrappers now redraw their rig, and window resize is requestAnimationFrame-debounced through one `drawCurrentTab()` path.

## Question-bank audit

The repository already has independent regression calculations for the 18 local Motion1D diagnostics in `tests/test_master_suites_gcdr_audit.py`. This RCA also rechecked the local bank structure and teaching fields.

Current local status:

- **18 / 18** records have a non-empty answer, governing formula, derivation steps, trap, independent teacher check, transfer takeaway, answer audit, source audit and simulator fidelity.
- **18 / 18** carry `answerAudit: PASS`.
- No duplicate answer-option text or known generic placeholder answer pattern was found.
- Takeaways, traps and teacher checks are not duplicated across records.
- Source provenance remains deliberately separate from mathematical answer audit:
  - **4 / 18** are `SOURCE_ITEM_VERIFIED`;
  - **14 / 18** remain `SOURCE_PROVENANCE_PENDING`.

The UI now surfaces those two statuses separately instead of allowing “answer checked” to imply “source provenance verified.”

## Teacher / helper UI

Each local question already contains question-specific helper content. The repair makes that contract more visible and explicit:

1. Governing model
2. Question-specific derivation
3. Final result / answer audit
4. Independent teacher check
5. Trap / misconception diagnosis
6. Transfer takeaway / rule
7. Simulator fidelity

Question cards also surface helper-availability chips and answer/source/fidelity badges before the learner opens the Chalkboard.

## Simulator audit

The 18 local records currently classify as:

- **6 EXACT**
- **1 CONSTRAINT_FAITHFUL**
- **5 CONCEPT_ONLY**
- **6 UNAVAILABLE**

The loader remains fail-closed for `UNAVAILABLE` and does not inject a question state for `CONCEPT_ONLY`.

The exact mappings reviewed in the current local subset are the v–x/a–x rigs, balloon inheritance, timed water drops, two-phase paratrooper descent and same-direction relative pursuit. The other records retain their lower fidelity labels where the current rig cannot reproduce the complete stem.

## Static acceptance checks

After the repair:

- 18 unique bank records parse.
- Required question/teaching/audit fields are present on all 18.
- Static DOM IDs are unique.
- Inline JavaScript parses.
- Inline event-handler names resolve to functions.
- The recursive DPR height feedback pattern is absent.
- The fixed balloon, relative-road and sandbox plot-domain constants identified in this incident are absent.
- Fixed 8 s / 20 s / 15 s animation-stop conditions identified above are absent.
- The bank-integrity gate and visible source-audit badges are present.

## Remaining release gate

A real browser interaction smoke test is still required before calling the UI runtime-verified. In this audit session the browser connector was unavailable, so the slider fix has been verified statically and through repository tests/CI rather than by claiming a browser click-through that did not occur.

The same rule applies to the 123-question source corpus: the local 18-question diagnostic subset has been audited here; this document does **not** claim that all 123 external source questions are embedded or individually source-verified.
