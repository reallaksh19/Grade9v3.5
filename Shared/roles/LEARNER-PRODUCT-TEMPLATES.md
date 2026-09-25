# Core learner-product templates

Read [the shared role invariants](README.md) and the six role specifications before using this file.

This file standardises **presentation anatomy and reveal order**. It does not redefine
academic meaning. The role files remain authoritative for what each Core means; canonical
subject records remain authoritative for academic truth.

The template contract exists to answer a practical production question:

> Given valid canonical inputs, what does the learner see, in what order, what stays hidden
> until an attempt/reveal, and how does the product close?

It deliberately standardises only the learner-facing grammar that should be stable across
Physics, Mathematics and Chemistry. Subject-specific wording, figures, equations and examples
continue to come from canonical subject data and adapters.

## Shared presentation grammar

All six products may use these primitives when the role needs them:

- **Identity band** — Core role, bucket/microtopic/question identity and truthful status.
- **Scope band** — what is covered, excluded or carried as labelled extension.
- **Representation panel** — a canonical representation or scene, never a decorative
  independently-authored substitute for canonical representation truth.
- **Try block** — an explicit learner action that precedes a reveal where the role requires
  learner commitment.
- **Reasoning block** — one ordered reasoning move, including why it is valid when the role
  requires that explanation.
- **Misconception / repair block** — a named plausible wrong idea, a diagnostic that
  distinguishes it, and the repair route.
- **Check block** — a self-check, limiting case, reversal, independent recomputation or
  subject-qualified equivalent.
- **Provenance block** — source/origin/custody information where the role requires it.
- **Closure block** — model response, rubric, answer, or explicit criteria that let the
  learner close the work without a live tutor.

A primitive is not mandatory merely because it exists. Each role below specifies its own
required order.

## Six-role matrix

| Core | Learner job | Defining reveal rule | Typical closure |
|---|---|---|---|
| Core1 | Orient to the semantic map | No hard inference is taught in full | orientation check |
| Core1A | Receive the completed conceptual construction | Difficult inference is fully revealed and explained | exit task + checked model response |
| Core1B | Reconstruct the same conceptual truth | Predict/attempt precede reconstruction and answer | rubric/model response + boundary test |
| Core2 | Encounter the source assessment demand with custody intact | Source hints/answer retain source order and identity | source answer/rubric |
| Core2A | Learn a familiar application route with support | Familiar crux is teachable and may be revealed | full solution + independent check |
| Core2B | Make a changed transfer decision | Protected decision is not disclosed before commitment | full rubric + changed-demand review + repair |

## Machine-readable presentation contract

The fenced block below is the authority for **template presence and ordering**. It is not a
second academic schema. The referenced canonical paths are inputs already owned by the role
specifications and canonical library.

Each role also carries one versioned `web_blueprint_ref`. That reference is presentation/delivery
authority only: it selects the subject-neutral interactive-page blueprint that must render the
ordered blocks. It does not move scientific, mathematical, chemical, question, source-custody or
learner-evidence truth into the webpage layer. A missing or incompatible blueprint is a build HOLD,
not permission for an agent to invent a page architecture.

```core-templates
{
  "version": "1.1",
  "roles": {
    "CORE1": {
      "learner_job": "Orient to the bucket without replacing detailed teaching.",
      "ordered_blocks": [
        {
          "id": "identity_scope",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "objects_conventions",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "canonical_representation",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "governing_relations",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "compact_anchor",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "hard_transition_map",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "exclusions_extensions",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "orientation_closure",
          "visibility": "IMMEDIATE"
        }
      ],
      "required_inputs": [
        "bucket.title",
        "bucket.conventions[]",
        "bucket.primary_representation_ref",
        "bucket.scope.covers",
        "bucket.scope.excluded[]",
        "bucket.scope.extension_refs[]",
        "relation.expression",
        "relation.meaning",
        "relation.conditions[]",
        "microtopic.intrinsic_badge",
        "microtopic.badge_reason"
      ],
      "withheld_pre_attempt": [],
      "forbidden": [
        "FULL_INFERENTIAL_CONSTRUCTION",
        "FULL_MISCONCEPTION_REPAIR_LESSON",
        "PERSONALISED_PRACTICE_ROUTING"
      ],
      "web_blueprint_ref": "BP-CORE1-ORIENTATION@1.0.0"
    },
    "CORE1A": {
      "learner_job": "Receive a complete declarative construction of the microtopic's inferential truth.",
      "ordered_blocks": [
        {
          "id": "identity_entry_assumptions",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "convention_declaration",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "inferential_jump",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "completed_construction",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "representation_bridge",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "worked_conceptual_anchor",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "plausible_wrong_path",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "diagnose",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "repair",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "independent_checks",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "exit_task_closure",
          "visibility": "IMMEDIATE"
        }
      ],
      "required_inputs": [
        "microtopic.entry_assumptions[]",
        "microtopic.inferential_jump",
        "microtopic.teaching_path[]",
        "microtopic.representation_refs[]",
        "microtopic.misconceptions[]",
        "microtopic.exit_task"
      ],
      "withheld_pre_attempt": [],
      "forbidden": [
        "ATTEMPT_FIRST_AS_PRIMARY_MODE",
        "RANDOM_BLANK_DELETION",
        "UNANSWERED_PROMPT"
      ],
      "web_blueprint_ref": "BP-CORE1A-CONSTRUCTION@1.0.0"
    },
    "CORE1B": {
      "learner_job": "Reconstruct the same inferential truth before seeing the completed route.",
      "ordered_blocks": [
        {
          "id": "identity_concept",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "predict",
          "visibility": "ATTEMPT_FIRST"
        },
        {
          "id": "attempt",
          "visibility": "ATTEMPT_FIRST"
        },
        {
          "id": "reconstruct",
          "visibility": "POST_ATTEMPT"
        },
        {
          "id": "diagnose",
          "visibility": "POST_ATTEMPT"
        },
        {
          "id": "repair",
          "visibility": "POST_ATTEMPT"
        },
        {
          "id": "boundary_test",
          "visibility": "POST_ATTEMPT"
        },
        {
          "id": "model_response_or_rubric",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "rejoin_inferential_jump",
          "visibility": "ON_REVEAL"
        }
      ],
      "required_inputs": [
        "microtopic.inferential_jump",
        "microtopic.elicitation.predict.prompt",
        "microtopic.elicitation.attempt.produces",
        "microtopic.elicitation.reconstruct.route[]",
        "microtopic.misconceptions[]",
        "microtopic.elicitation.boundary_test"
      ],
      "withheld_pre_attempt": [
        "DEFENSIBLE_ANSWER",
        "COMPLETED_RECONSTRUCTION",
        "MODEL_RESPONSE"
      ],
      "forbidden": [
        "CORE1A_WITH_RANDOM_BLANKS",
        "ANSWER_BEFORE_ATTEMPT",
        "COVERAGE_REDUCTION_RELATIVE_TO_CORE1A"
      ],
      "web_blueprint_ref": "BP-CORE1B-RECONSTRUCTION@1.0.0"
    },
    "CORE2": {
      "learner_job": "Preserve and expose the authentic assessment demand with source custody intact.",
      "ordered_blocks": [
        {
          "id": "source_identity_provenance",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "source_question",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "source_figure",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "source_hint_ladder",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "source_answer_rubric",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "custody_status",
          "visibility": "IMMEDIATE"
        }
      ],
      "required_inputs": [
        "question.source_refs[]",
        "question.original_identifier",
        "question.stem",
        "question.subparts[]",
        "question.options[]",
        "question.conditions[]",
        "question.figure_refs[]",
        "question.hints[]",
        "question.answer",
        "question.origin"
      ],
      "withheld_pre_attempt": [
        "SOURCE_ANSWER",
        "ANSWER_REVEALING_SOURCE_HINT"
      ],
      "forbidden": [
        "AUTHORED_SCAFFOLD_PRESENTED_AS_SOURCE_HINT",
        "GENERATED_OFFICIAL_IDENTITY",
        "RECONSTRUCTED_WORDING_PRESENTED_AS_ORIGINAL"
      ],
      "web_blueprint_ref": "BP-CORE2-SOURCE-QUESTION@1.0.0"
    },
    "CORE2A": {
      "learner_job": "Learn a familiar question-family application route with pedagogical support and complete closure.",
      "ordered_blocks": [
        {
          "id": "family_identity_provenance",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "question",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "initial_representation",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "pedagogical_scaffolds",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "reasoning_route",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "application_crux",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "bound_representation",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "complete_solution",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "independent_check",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "failure_signal_repair",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "exposure_family_closure",
          "visibility": "IMMEDIATE"
        }
      ],
      "required_inputs": [
        "question.family_ref",
        "question.source_refs[]",
        "question.answer.reasoning_route[]",
        "question.answer.crux_move_ref",
        "question.scaffolds[]",
        "question.figure_refs[]",
        "question.answer.check",
        "question.exposure[]"
      ],
      "withheld_pre_attempt": [],
      "forbidden": [
        "TRANSFER_CLAIM_FROM_NUMBER_CHANGE_ONLY",
        "SOURCE_HINT_AND_AUTHORED_SCAFFOLD_COLLAPSE",
        "MASTERY_CLAIM_FROM_SUCCESSFUL_GENERATION"
      ],
      "web_blueprint_ref": "BP-CORE2A-SUPPORTED-APPLICATION@1.0.0"
    },
    "CORE2B": {
      "learner_job": "Carry an established capability into a changed demand while protecting the changed learner decision before commitment.",
      "ordered_blocks": [
        {
          "id": "question_prior_exposure",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "safe_initial_representation",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "safe_pre_attempt_support",
          "visibility": "IMMEDIATE"
        },
        {
          "id": "attempt_commitment",
          "visibility": "ATTEMPT_FIRST"
        },
        {
          "id": "post_attempt_support",
          "visibility": "POST_ATTEMPT"
        },
        {
          "id": "full_answer_rubric",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "changed_demand_review",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "repair_route",
          "visibility": "ON_REVEAL"
        },
        {
          "id": "lineage_continuity_check",
          "visibility": "ON_REVEAL"
        }
      ],
      "required_inputs": [
        "question.transfer.dimension",
        "question.transfer.statement",
        "question.transfer.builds_on[]",
        "question.transfer.protected_move_ref",
        "question.scaffolds[]",
        "question.answer.rubric[]",
        "question.repair_ref"
      ],
      "withheld_pre_attempt": [
        "PROTECTED_MOVE",
        "CHANGED_DECISION",
        "METHOD_OR_ANSWER_SUPPORT_THAT_COLLAPSES_TRANSFER"
      ],
      "forbidden": [
        "PROTECTED_MOVE_DISCLOSED_PRE_ATTEMPT",
        "NEW_UNTAUGHT_CAPABILITY_AS_TRANSFER",
        "TRANSFER_CLAIM_FROM_COVER_STORY_ONLY"
      ],
      "web_blueprint_ref": "BP-CORE2B-TRANSFER@1.0.0"
    }
  }
}
```

## Anti-collapse review

A compliant implementation must be able to show these differences directly:

- **Core1 → Core1A:** Core1 points at hard transitions; Core1A constructs them.
- **Core1A → Core1B:** Core1A reveals the route; Core1B asks for the conceptual decision
  before reconstruction.
- **Core2 → Core2A:** Core2 preserves source custody; Core2A may add authored scaffolds and
  an explicit application route, but those must remain distinguishable from source hints.
- **Core2A → Core2B:** Core2A may teach the familiar crux; Core2B must protect the changed
  decision until the learner has committed to an attempt.

Changing headings, colours, story nouns or numbers does not establish these distinctions.

## Rendering guidance

This contract is compatible with interactive and static delivery.

Interactive delivery may progressively reveal `ON_REVEAL` and `POST_ATTEMPT` blocks.
Static/print delivery must still remain semantically complete: withheld material may be
placed after an explicit attempt boundary, on a following page/section, or in a clearly
separated answer/reconstruction section. It may not be omitted.

Representations must consume canonical representation/scene bindings. A page renderer may
choose layout, typography and responsive behaviour; it may not independently redraw a
different academic claim and treat that drawing as equivalent merely because it looks
similar.
