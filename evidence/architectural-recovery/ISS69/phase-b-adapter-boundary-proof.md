# ISS69 PHASE-B — B03 adapter / QRT / authority boundary proof

## B03.1 — canonical QRT namespace

Direct inspection of all subject demand adapters:

| Subject | DemandReview blob | Demand keys | QRT-like identity |
| --- | --- | --- | --- |
| Chemistry | `596b97a8b6941d75428cedba9daa0929d494d00b` | RETRIEVE, EXPLAIN, APPLY, MODEL, REPRESENT, SYNTHESIZE, JUSTIFY | none |
| Mathematics | `6a6891837f2364af01d86299254ca2708b1867a9` | same seven | none |
| Physics | `03ab1f96443e85f86d909b5dc15afcbe77086181` | same seven | none |

No adapter contains `QRT-`.

Regression:
`tests/test_issue69_subject_neutrality.py::Issue69SubjectNeutrality.test_demand_adapters_specialize_the_same_canonical_demands_without_qrt_identity`.

## B03.2 — adapter specialization independence

All three DemandReview adapters share the same contract shape:

Top level:
- `schema`
- `version`
- `subject`
- `vocabulary_ref`
- `basis_refs`
- `demands`

Every demand specializes only:
- `review_focus`
- `representation_kinds`
- `check_types`
- `misconception_patterns`

Each adapter binds only its own:
- `<Subject>/adapter/QualityVocabulary.json`
- `<Subject>/adapter/CoreContracts.json`

No adapter owns:
- `web_blueprint_ref`
- `components`
- `slots`
- `layout_family`
- `qrt_cell`
- `template_id`
- `core_role`

Regression:
`test_demand_adapters_do_not_own_page_or_product_policy`.

## B03.3 — renderer academic subject branch

`Shared/tools/render_core.py` blob inspected: `31441726e429dbe770f417ade0a20a70809cf039`.

AST/structural readback:
- literal-subject equality/inequality academic comparisons: **0**;
- subject-name literals: Physics / Chemistry / Mathematics only in the portal-navigation link tuple.

Regression:
`test_render_core_has_no_academic_subject_literal_comparison`.

This does not claim all Shared tooling is topic-independent. Frozen PHASE-A already reports 1511 topic-independence violations in 368 files. That inherited platform debt remains explicitly non-green.

## B03.4 — source-of-truth/version closure

Current successor chain:

- role-template contract: `1.4`;
- blueprint registry: `1.17.0`;
- Core1A role binding: `BP-CORE1A-CONSTRUCTION@1.8.0`;
- active Core1A registry row: `BP-CORE1A-CONSTRUCTION@1.8.0`;
- Core2 role binding: `BP-CORE2-SOURCE-QUESTION@1.11.0`;
- active Core2 registry row: `BP-CORE2-SOURCE-QUESTION@1.11.0`;
- generated `PAGE-BLUEPRINT-COMPONENTS.md` contains both successor component blueprints.

The Phase-B Core2 binding changed from 1.10.0 to 1.11.0, so the role contract was correctly versioned from 1.3 to 1.4 rather than silently mutating 1.3.

Generated-spec floating formatting was also corrected from a manual JS artifact (`57.99999999999999%`) to the repository generator's `58%`.

## Branch-exact CI result

Exact head: `ecc579e6c68f9750f5044d258b2c828e57852ddb`  
Fast workflow job: `112380169256`

Branch-exact step results:

- Diagnostic evidence contract: **SUCCESS**
- U09 diagnostic caller migration: **SUCCESS**
- Representation instance binding contract: **SUCCESS**
- Issue69 subject-neutrality contract: **SUCCESS**
- Core2 staged support contract: **FAIL**, at the already-classified downstream renderer seam:
  `KeyError: 'CORE2: TRAP not declared in attempt of BP-CORE2-SOURCE-QUESTION'`

The Issue69 step executes `python3 -m unittest tests.test_issue69_subject_neutrality`. At this exact head that file proves:

- all three DemandReview adapters use the same seven demands and own no `QRT-` identity;
- adapters own no page/product-policy keys;
- `render_core.py` has no academic subject-literal comparison;
- role contract 1.4 resolves to the active registry rows (Core1A 1.8.0 / Core2 1.11.0);
- `docs/specs/PAGE-BLUEPRINT-COMPONENTS.md` is byte-equal to `blueprint_spec.render(registry)`.

This is the branch-exact evidence frontier for B03. The later TRAP failure is PHASE-C work and does not invalidate these passed contracts.
