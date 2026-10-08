# SOF IMO Grade 9 official 2026–27 sample — Q5 source figure proof candidate

**Status: independently derived by this AI agent, not independently reviewed by a human.** The prior eight-item organizer sample research ledger still reports Q5 as `FIGURE_GEOMETRY_PENDING`. That was an accurate **historical pilot snapshot**. This new, separate proof candidate documents an agent derivation from the original printed diagram; it does not overwrite the pilot, the P0 case 009 reviewer packet, or any rights/QRT/Core approval flag.

**Controlling original:** [SOF-hosted Class 9 sample 2026–27 PDF](https://sofworld.org/download/file/fid/73719), physical PDF page index 1 (printed page 2), Mathematical Reasoning Q5. Its answer-key panel prints option **C**. The owner compilation stores it as entry Q23 and lists the same answer label but does not retain the source angle incidence.

## Geometry — independent agent proof

The original diagram visibly marks two parallel pairs **l₁ ∥ l₂** and **l₃ ∥ l₄**. At their first crossing, **x** is between a downward ray on l₁ and a down-left ray on l₃. At the corresponding l₂/l₄ crossing, the angle between downward l₂ and down-left l₄ therefore also equals x, by corresponding angles under the two parallelisms.

The up-right ray on l₄ is the **opposite ray** of that down-left l₄ ray. Its angle with downward l₂ is supplementary to the transferred x:

\[
\theta=180^\circ-x.
\]

Crucially, the printed figure shows a third oblique ray dividing this supplementary sector into **two adjacent angles both labelled y**. It therefore supplies the equality **2y = θ**. Consequently

\[
x+2y=180^\circ,\qquad
\boxed{y=90^\circ-\frac{x}{2}}.
\]

This is the relation represented by SOF's printed **option C**. Merely seeing two generic lines would **not** justify halving the supplementary angle: the two marked y labels and their common source vertex are essential.

An independent **unit-vector** crosscheck sets the downward ray to (0,−1) and the upper-right l₄ ray to (sin x,cos x). The dot product is −cos x, yielding included angle 180°−x; its normalized vector bisector divides that sector into equal angles. The concrete probes (x,y)=(30°,75°),(60°,60°),(80°,50°) each satisfy the vector and supplementary representations. They are **mathematical probes**, not angle measurements claimed to be printed on the diagram.

## Held decisions and explicit reviewer tasks

- **Source image custody:** this repository does **not** include the original diagram or a traced reproduction, original question stem/options, or PDF content. The numeric ray model is an independently authored abstract proof, not a reproduced source asset. Copyright, derivative and redistribution rights remain **NOT_REVIEWED**.
- **Human academic gate (P0):** independent geometry reviewer must confirm the exact two y-labelled sectors, x orientation, parallel glyphs and common vertex against the original PDF. Reviewer must derive the same relation without relying on the answer key and sign `SIGNED_ORIGINAL_SAMPLE_Q5_ANGLE_PROOF` with source version/page and date, or reject the candidate with correction evidence.
- **External approval:** zero signed academic answer acceptances, zero source/figure reuse licenses, zero accepted QRT cells and zero Core-ready question positions. The previously merged reviewer queue and discrepancy case remain **P0/PENDING**. The new agent mathematical proof does not replace independent peer review.
- **No automatic answer normalization:** do not silently update the original 66-question seed, earlier pilot or provisional 4×7 matrix. Any accepted learner derivative requires independent academic, legal source-use and QRT/Core admission decisions separately.

## Technical qualification

```sh
python TEST/imo-research/validate_sample_q5_geometry.py
python -m unittest discover -s tests -p 'test_imo_sample_q5_geometry.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

`validate_sample_q5_geometry.py` checks the source ID/printed key, exact original figure facts, symbolic reasoning steps, independent vector model, organizer sample pilot historical hold, P0 human-review packet, original source asset/rights hold, and zero academic/QRT/Core promotion. The dedicated SOF IMO research workflow runs the new check and all `test_imo_*.py` falsifiers.

Tracked by [issue #258](https://github.com/reallaksh19/Grade9v3.5/issues/258); previous source discrepancy issue [#250](https://github.com/reallaksh19/Grade9v3.5/issues/250) and independent review gate [#254](https://github.com/reallaksh19/Grade9v3.5/issues/254).
