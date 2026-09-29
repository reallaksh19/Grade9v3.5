# Core authority and dependency contract

This document defines **where each Core is allowed to get authority from**.

The six role files define learner-product meaning. The learner-product template contract defines
presentation anatomy and reveal order. This contract defines a different concern: the
authority graph that must remain stable when planners, prompt generators, authoring agents,
renderers and publication tools compose those products.

A requested production sequence is never an authority graph.

For example, an owner may request:

```text
CORE2 → CORE1 / CORE1A / CORE1B → CORE2A / CORE2B
```

That sequence may be useful operationally, but it does **not** mean Core1-family academic
truth is derived from Core2. Academic truth remains owned by canonical subject records.

## Human-readable authority graph

```text
CANONICAL ACADEMIC TRUTH
  ├── CORE1
  ├── CORE1A
  └── CORE1B

AUTHORIZED SOURCE CUSTODY
  └── CORE2

CANONICAL ACADEMIC TRUTH
+ ELIGIBLE REVIEWED DEMAND or EXPLICITLY AUTHORED PRACTICE
+ OPTIONAL LEARNER SUPPORT INPUT
  └── CORE2A

CORE2A / OTHER ESTABLISHED PRIOR EXPOSURE
+ ALREADY-TAUGHT CAPABILITY CLOSURE
+ GENUINELY CHANGED DEMAND
  └── CORE2B
```

Missing Core2 source custody is a research duty: the agent finds and records the original source
(an owner-supplied question text is itself custody of class `OWNER_SUPPLIED`). While that research
is in progress, source material never becomes academic authority, and Core1-family study products
are built from their canonical academic inputs regardless.

## Cross-cutting authority rules

**Execution order is not derivation order.** A workflow may inspect or attempt Core2 first.
That does not make Core2 the source of Core1/Core1A/Core1B concepts.

**Canonical per-question mapping survives set planning.** A set-level topic, matrix or rung
may describe composition scope. It must not rewrite a question's canonical
`question.primary_capability_ref`.

**Demand evidence and learner eligibility are separate.** A question may be useful evidence
about assessment demand while the owner has excluded it from learner use. Where the owner has
not decided, learner eligibility takes the default median learner (`DEFAULT_ELIGIBLE`).

**Source hints and authored scaffolds are different custody classes.**
`question.hints[]` preserves supplied/source question help. `question.scaffolds[]` is
authored pedagogical support. A downstream tool may render both, but may not relabel one as
the other.

**Extensions are admitted explicitly, never silently.** A source question may require an
advanced model, bridge concept or extension. The agent researches it, adds it to the subject
library as a `CANDIDATE` extension microtopic through the package schema, and then teaches it in
Core1A/Core1B marked `EXTENSION`. It never rewrites the existing canonical microtopics, and it is
never left untaught because admission had not happened yet.

**Learner estimates are not mastery evidence.** A percentage or owner estimate may influence
Core2A/Core2B routing/support where their contracts permit. It cannot reduce, expand or
replace Core1A/Core1B intrinsic conceptual scope.

**Continue research with honest gaps.** Missing source custody, learner data, prior exposure,
canonical teaching, examples or visuals identify research and authoring duties (see
`Shared/workflows/research-first.v1.json`, `escape_state_duties`). Continue useful work and
retain unresolved findings with their scope and consequence; a missing dependency is not a
new whole-task refusal or permission requirement. Missing learner data takes the existing
default support route with unknown knowledge kept visible. Closure is never fabricated:
researched material keeps its provenance, authored material is labelled
`AUTHORED_PEDAGOGICAL` or `AUTHORED_PRACTICE`, and missing human review is stated on the
delivered product. These dependency semantics introduce no new blocker or CI gate.

**Planning tools are not academic authorities.** Prompt composers, worksheet maps, run
builders and publication manifests may carry and validate references. They may not create
curriculum truth, source custody, learner mastery or canonical question identity.

## Machine-readable authority contract

The fenced block below is the machine-readable authority for the invariants above. It is not
a new academic schema and it does not replace subject package schemas.

```core-authority
{
  "version": "1.0",
  "authority_classes": {
    "CANONICAL_ACADEMIC_TRUTH": {
      "description": "Canonical subject package records: bucket/microtopic/capability/relation/representation truth.",
      "may_authorize": ["CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"]
    },
    "AUTHORIZED_SOURCE_CUSTODY": {
      "description": "Reviewed source/question custody sufficient for ordinary source-backed Core2.",
      "may_authorize": ["CORE2"]
    },
    "ELIGIBLE_REVIEWED_DEMAND": {
      "description": "Demand evidence explicitly eligible for learner application.",
      "may_authorize": ["CORE2A", "CORE2B"]
    },
    "AUTHORED_PRACTICE": {
      "description": "Truthfully labelled authored application content grounded in canonical capability truth.",
      "may_authorize": ["CORE2A", "CORE2B"]
    },
    "LEARNER_SUPPORT_INPUT": {
      "description": "Scoped learner evidence, owner estimate or waiver used only where role contracts permit routing/support.",
      "may_authorize": ["CORE2A", "CORE2B"]
    },
    "PRIOR_EXPOSURE": {
      "description": "Recorded prior exposure/established route needed before transfer claims.",
      "may_authorize": ["CORE2B"]
    }
  },
  "roles": {
    "CORE1": {
      "required_authority": ["CANONICAL_ACADEMIC_TRUTH"],
      "forbidden_authority_substitution": ["AUTHORIZED_SOURCE_CUSTODY", "LEARNER_SUPPORT_INPUT"]
    },
    "CORE1A": {
      "required_authority": ["CANONICAL_ACADEMIC_TRUTH"],
      "forbidden_authority_substitution": ["AUTHORIZED_SOURCE_CUSTODY", "LEARNER_SUPPORT_INPUT"]
    },
    "CORE1B": {
      "required_authority": ["CANONICAL_ACADEMIC_TRUTH"],
      "forbidden_authority_substitution": ["AUTHORIZED_SOURCE_CUSTODY", "LEARNER_SUPPORT_INPUT"]
    },
    "CORE2": {
      "required_authority": ["AUTHORIZED_SOURCE_CUSTODY"],
      "forbidden_authority_substitution": ["AUTHORED_PRACTICE", "CANONICAL_ACADEMIC_TRUTH"]
    },
    "CORE2A": {
      "required_authority": ["CANONICAL_ACADEMIC_TRUTH"],
      "one_of_authority": ["ELIGIBLE_REVIEWED_DEMAND", "AUTHORED_PRACTICE"],
      "optional_authority": ["LEARNER_SUPPORT_INPUT"],
      "forbidden_authority_substitution": ["LEARNER_SUPPORT_INPUT"]
    },
    "CORE2B": {
      "required_authority": ["CANONICAL_ACADEMIC_TRUTH", "PRIOR_EXPOSURE"],
      "one_of_authority": ["ELIGIBLE_REVIEWED_DEMAND", "AUTHORED_PRACTICE"],
      "optional_authority": ["LEARNER_SUPPORT_INPUT"],
      "forbidden_authority_substitution": ["LEARNER_SUPPORT_INPUT"]
    }
  },
  "invariants": {
    "execution_order_is_not_authority_order": true,
    "core2_custody_gap_does_not_rewrite_academic_authority": true,
    "core2_custody_research_does_not_block_study_roles": true,
    "preserve_question_primary_capability_ref": true,
    "set_scope_must_not_overwrite_question_primary": true,
    "demand_evidence_and_learner_eligibility_are_distinct": true,
    "source_hints_and_authored_scaffolds_are_distinct": true,
    "extensions_require_canonical_admission_before_core1_family": true,
    "learner_estimate_is_not_mastery_evidence": true,
    "learner_estimate_cannot_change_core1_family_intrinsic_scope": true,
    "prompt_and_planning_outputs_are_not_academic_authority": true,
    "unresolved_authority_dependency_becomes_research_duty": true
  },
  "canonical_field_rules": {
    "question_primary": "question.primary_capability_ref",
    "source_hints": "question.hints[]",
    "authored_scaffolds": "question.scaffolds[]",
    "core1_family_crux": "microtopic.inferential_jump"
  },
  "planning_distinctions": {
    "execution_order": "PRODUCTION_CONTROL_ONLY",
    "set_level_scope": "COMPOSITION_CONTEXT_ONLY",
    "demand_evidence": "MAY_EXIST_WITHOUT_LEARNER_ELIGIBILITY",
    "learner_eligibility": "INDEPENDENT_REVIEW_STATE"
  },
  "allowed_dependency_states": ["PASS", "RESEARCH_AND_AUTHOR"]
}
```

## Consumer requirements

Any planner, prompt generator, authoring agent, learner renderer or publisher that emits
instructions about more than one Core must preserve this contract.

At minimum, a generated multi-Core prompt must make these facts recoverable:

1. the requested execution order;
2. the authority source for each requested role;
3. any unresolved authority dependency as a named research or authoring duty;
4. the distinction between set-level scope and per-question canonical primaries;
5. the distinction between demand evidence and learner eligibility;
6. extension demands, and the CANDIDATE extension microtopic that admits each one;
7. learner estimates as support inputs rather than mastery/curriculum authority.

A consumer may use different wording or a machine-readable projection, but it may not collapse
those distinctions.
