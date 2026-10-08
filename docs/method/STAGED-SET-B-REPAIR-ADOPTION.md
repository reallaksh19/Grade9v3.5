# Staged Set B repair: adoption and scoped guidance

This is the first repair slice under #29, based on the frozen Set B audit and the Owner's confirmation that all four authors used low thinking. It adds no universal author checklist or publishing blocker. The four submitted candidate PRs are not accepted by this slice.

## Adopt the structural changes where the failure exists

**S1: choose the question's scene.** Keep a reusable representation and its concept-teaching asset. Add a `scene_instances[]` entry with the question owner, applicable role, existing datum references and an `asset_ref` for that case. The question's optional `grade9v3:core2_support_plan.visuals[]` selects that instance. Do not overwrite a valid teaching example merely because its coefficients differ from the question. Authentic source snapshots retain their source-custody path and cannot be replaced by this binding.

The consumer checks that the selected scene belongs to the question and role, its datum records exist and its requested stages occur in the asset. It does not infer mathematical truth from an SVG or a datum reference. Check the drawn values and their correspondence to the datum when authoring the affected scene. Production render fingerprints include case asset bytes.

**S2: connect support to protected work.** Identify the relevant existing `answer.reasoning_route[]` move IDs. Record them in `protected_move_refs`; record which protected outputs an authored hint or visual stage completes through `completed_move_refs`. These links differ from `supports_move_ref`: a suggestion can support a move without giving its result. The consumer defers protected completion to the existing attempted solution, while leaving conceptual help available before the attempt.

Example: #55 Q1 asks the learner to determine `k`. A hint naming `p_0(x)` supplies that answer even though its old label says METHOD. The replay records its completion links and defers it. Its wording and source provenance are retained. An initial figure presents the given `p_k(x)` and given factor; the numerical cubic and its complete factorisation return with the solution.

If a reasoning move combines several decisions, split it into meaningful existing reasoning-route records before using it for finer protection. Do not claim a hint completes an entire calculation merely because it gives one input. The first replay protects #56's model/domain moves; it does not claim to protect every sub-decision in the combined discriminating-input move.

The optional plan is typed in the base question schema and allowed by the competitive-bank adapter. Missing plans keep historical behavior. A no-picture question needs no visual binding. Core1A teaching examples keep their existing disclosure policy. Unlisted support retains its existing reveal semantics: adopting this plan does not automatically certify other hints as safe.

**S3: retain the basis of a review.** Canonical pipeline reviews may explicitly use `basis: AUTHOR_ONLY` or `basis: RENDERED`. Author-only assessments are retained but cannot satisfy the existing post-render review requirement. Rendered reviews use the existing artifact identifier, exact-byte hash, head and twelve semantic judgements. Records without a basis retain legacy rendered semantics. This types an existing review contract; it does not introduce a second gate or convert ungrounded YES claims into valid review.

Archived Set B QRT formats remain archived. Use a deliberate adapter when moving them into the canonical pipeline format. Do not silently relabel the #55 `AUTHORED_NOT_RENDER_VERIFIED` assessment as rendered acceptance.

## Tighten existing instructions only at repeated operations

These clarifications are trial guidance for the affected Set B repairs. Their recurrence and examples are recorded in the [staged RCA](https://github.com/reallaksh19/Grade9v3.5/issues/29#issuecomment-5998155562).

| Operation | Clarification | Use existing fields |
|---|---|---|
| Generalising a solution into a theorem or repair | Carry the necessary degree, distinctness, nonzero and domain assumptions into the new claim. Recheck the conclusion when an assumption changes. | conditions, task, answer/check |
| Selecting a proof or check for this learner | Use demonstrated prerequisites. If advanced machinery is necessary, teach and declare that extension rather than assuming it from the difficulty band. | prerequisite references, learner scope |
| Attaching a reference to a mathematical claim | Distinguish a consulted claim-supporting section from a named website or inaccessible publication. Preserve edition/access limitations and avoid invented quotations. | source, edition/section, access status |
| Reporting verification | Preserve the actual exit/status and measured scope. A narrow successful check does not erase failed or unmeasured checks. | existing receipts and report statuses |
| Diagnosing a wrong route | Demonstrate a plausible wrong move, why it fails in this case and a usable repair. Supply changed givens for a transfer probe. | diagnostic repair and task/answer records |

No new compulsory counters, repeated sign-off steps or schema fields are added for these clarifications. Apply each to its affected operation, then judge the repaired output.

## Optional add-ons for the observed low-thinking runs

Use only the relevant add-on. The Owner's low-thinking answer is already recorded; do not ask again. These are not generic rules for all future authors.

| Observed case | Add-on |
|---|---|
| #56 illustrative tangency | Compute the curve's vertex/intersection with the drawn axis. A “tangent” label is not a geometric check. The replay's #54 quadratic uses an exact quadratic Bézier segment rather than a guessed curve. |
| #56 real-root classification task | Restore the degree bound. Without it, `(x²−1)²(x²+1)` is a monic degree-six counterexample with only real zeros ±1 and value 1 at zero. |
| #56 minimum-degree proof | Check the quartic cases with repeated real linear factors as well as the irreducible-quadratic case. For multiplicities 1, 2, 3, the ratios `p(2)/p(0)` are −27, 9, −3. |
| #56 agreement formula | Test a non-1,2,3 agreement triple; the third factor is `(x−x3)`, not a hard-coded `(x−3)`. |
| #55 transfer probes | Replace “apply to a variant” with actual changed givens and a checked expected response. |
| #54 template IDs/components | Select existing registered QRT IDs and repair the existing omission findings. Do not invent a registry or demand a diagram for every task. |
| #55 receipt / #53 PR base | Regenerate the existing receipt from the actual render; use the agreed integration base and inspect the benchmark diff. |

## Pilot results and limits

`python tools/staged_set_b_replay.py --out evidence/staged-repair/ISS29-set-b/rendered` regenerates four partial question contexts from pinned candidate heads. It preserves stems, answers and support wording. `python -m unittest tests.test_staged_support_repair` checks the adopted failures, no-picture/teaching/source-custody controls, negative reference cases and review basis. The existing layout observation has focused Node tests and an actual Core1A browser measurement.

The partial contexts deliberately do not supply full concept lineage or resolve other candidate defects. #55's safe pre-attempt ladder has one rung after four revealing rungs are deferred. The existing two-rung floor still reports that gap. Do not add filler or reinterpret the result as overall PASS. A subsequent candidate repair must address the useful support design and the existing floor's relevance together.

The four pilots do not cover forty-question acceptance, all 28 cells, all subjects, candidate navigation/packaging, Linux phone overflow or learner publication. Those remain separate recorded work.

## Reuse the methodology in another repository

Collect observed failures and their exact inputs/outputs first. Group by the same causal mechanism, not by similar wording. Record what the current data model already supports and whether samples are independent.

1. A shared representation gap: improve the existing schema and its producer/consumer together. Pilot both affected and valid cases.
2. Repeated mistakes despite adequate structure: clarify the relevant instruction at that operation. Reuse current fields.
3. An isolated mistake: establish the run's configuration with its owner. Trial a scoped add-on for a low-thinking run. For a high-thinking recurrence, assess a targeted check against the observed failure and its cost.
4. Promote only what the replay supports. Retain failures and applicability limits. Remove redundant ceremony and retest ordinary successful paths.

With multiple agents, count distinct independent runs and shared inputs explicitly. With one agent, use independently specified cases/runs to assess recurrence; repeated copied output is not independent evidence. One observation establishes a defect, not general prevalence. Thinking level informs the intervention scope; it does not change the accuracy expected of the result.
