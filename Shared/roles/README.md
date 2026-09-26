# The six Core roles

Six learner products per subtopic bucket. These specifications are **subject-neutral**: Physics, Mathematics and Chemistry all realise the same six roles. Concrete vocabulary — what counts as a relation, a representation, a model choice, a valid check — is supplied by the subject adapter (`<Subject>/adapter/CoreContracts.json`), never by these documents and never by engine code.

| Role | One-line purpose |
|---|---|
| [Core1](CORE1.md) | Compact basic notes and semantic orientation |
| [Core2](CORE2.md) | Source questions with ladder hints, source identity and answers |
| [Core1A](CORE1A.md) | Declarative detailed teaching, by intrinsic subtopic difficulty |
| [Core1B](CORE1B.md) | Open-ended conceptual reconstruction (self-tutor) |
| [Core2A](CORE2A.md) | Purpose-adjusted practice with complete solution breakdowns |
| [Core2B](CORE2B.md) | Supported application and transfer |

## Invariants that apply to every role

**Closure.** Every question, embedded prompt, diagram-completion task and "think about this" aside needs a model answer, rubric, or an explicit statement of how to judge a response. "Discuss with your teacher" is not closure. A product that poses work it cannot close is incomplete, regardless of how much prose it contains.

**Source honesty.** Supplied originals, adapted items and authored items are visibly distinguished. Original identity — question number, wording, figures, conditions — survives into the product unchanged. An authored item carries truthful authored provenance and a local identifier; it never borrows an official exam, year or question number it does not have.

**Depth is intrinsic, not personal.** Core1A/Core1B depth is set by the subtopic's intrinsic badge (EASY / MEDIUM / HARD) and does not shrink because a learner is estimated to know more. Only Core2A/Core2B consult learner knowledge or an owner waiver, and only for practice routing.

**No manufactured knowledge.** A knowledge percentage is an estimate with a scope and a provenance, not a diagnosis. Absent evidence and absent waiver, practice routing uses the default median learner (`DEFAULT_MEDIAN`, knowledge 50%, full support) and a short diagnostic, then adjusts from actual attempts. Seeing a worked solution is not evidence of independent mastery.

**No escape state.** HOLD, FAILED, INCOMPLETE, BLOCKED and WAITING are never an outcome of an agent's work. Every gap — source custody, question identity, mapping, prerequisite, extension, worked example, visual, learner data — is a research or authoring duty completed in the same job, with truthful provenance. See `Shared/workflows/research-first.v1.json`.

**Engineering detail is not a learner product.** Technical gates, routing infrastructure and owner boards specify and audit the work; they are not a seventh book. Learner navigation stays simple; engineering detail belongs in the owner view.

## The A/B differentiation rule

Core1A/Core1B and Core2A/Core2B share scientific truth and may share a declared anchor, but must demand **different learner work**:

| | A product | B product |
|---|---|---|
| Core1 layer | Reveal and explain a completed construction | Elicit the conceptual decision, then supply reconstruction help and misconception repair |
| Core2 layer | Teach a supported application with the full solution visible | Assess a specified change in model choice, representation, context or demand |

Changing numbers alone produces practice **within a family**, not a new transfer capability. A legitimate shared anchor may recur across products, but its new learner action and its help/reveal state must be visible. Repeated equations and definitions need not be paraphrased to defeat a similarity check — necessary repetition is legitimate, and similarity scores are review triggers, not verdicts.

Turning B into A with the nouns changed, or into A with random blanks punched into it, fails this rule.

## Authority and dependency graph

The six role specifications describe learner-product meaning, but they do not make requested
production order into academic authority. [Core authority and dependency contract](CORE-AUTHORITY-CONTRACT.md)
defines the cross-role authority graph used by planners, prompt generators, authoring agents,
renderers and publishers.

Its central rules are:

- canonical academic truth owns Core1/Core1A/Core1B content;
- authorized source custody owns ordinary Core2;
- Core2A combines canonical truth with eligible reviewed demand or truthfully authored
  practice, with learner support only as optional routing/support input;
- Core2B additionally requires established prior exposure and a genuinely changed decision
  inside already taught capability closure;
- execution order is production control only and never changes those ownership boundaries;
- per-question `question.primary_capability_ref` survives set-level topic/rung planning;
- demand evidence and learner eligibility remain separate states;
- unresolved authority dependencies become named research or authoring duties, completed with
  truthful provenance rather than fabricated to satisfy a requested product count.

The machine-readable fenced block is validated by
`Shared/tools/core_authority_contract.py`.

## Learner-facing production templates

The role files define **what each Core means**. [Core learner-product templates](LEARNER-PRODUCT-TEMPLATES.md)
define the stable presentation anatomy and reveal order used to turn those semantics into
learner-facing products.

The template contract is intentionally narrower than the role specifications:

- it does not own subject truth;
- it does not create a seventh Core;
- it does not set page-count quotas;
- it does not replace canonical representation or source-custody records;
- it does define ordered learner-facing blocks, reveal/withhold boundaries and structural
  anti-collapse rules for all six roles.

The machine-readable fenced block in `LEARNER-PRODUCT-TEMPLATES.md` is validated by
`Shared/tools/core_template_contract.py`.

## Cross-lane Core projection and web-delivery contracts

The role files above remain authoritative for learner-product meaning. The durable cross-lane
presentation authority is the machine-readable contract in
[Core learner-product templates](LEARNER-PRODUCT-TEMPLATES.md), validated by
`Shared/tools/core_template_contract.py`.

That contract now binds each of the six Core roles to one exact versioned
`web_blueprint_ref`. The referenced subject-neutral page blueprints live in
`Shared/web/interactive-page-blueprints.v1.json` and are validated by
`Shared/tools/web_blueprint_contract.py`.

The production Core projection boundary is implemented by
`Shared/tools/core_learning_projection_adapter.py`: it consumes compiled canonical records,
preserves the existing Core semantics, and copies the resolved web blueprint into explicit
projection delivery metadata. Browser/runtime code consumes that metadata; it does not infer
page architecture from subject names, question wording, learner percentages, or existing HTML.

These contracts preserve the established boundaries:

- Core1A/Core1B share the same conceptual truth; Core1A reveals the completed inference and
  Core1B elicits it before reconstruction/repair.
- Core2A/Core2B share capability truth; Core2A scaffolds a familiar reasoning route and Core2B
  protects the changed decision required for transfer.
- `microtopic.inferential_jump` is the Core1A/Core1B conceptual crux.
- `answer.reasoning_route[]` + `answer.crux_move_ref` are the structured Core2A/Core2B
  application route when authored.
- `question.hints[]` preserves the question/source hint ladder; `question.scaffolds[]` holds
  optional Core2A/Core2B pedagogical support.
- canonical representations remain academic truth; webpages consume representation bindings and
  reveal stages rather than inventing them.
- webpage blueprints own shell/layout/reveal mechanics only; they are not curriculum, source,
  question, learner-evidence, or mastery authority.

The historical #176 Core Projection Contract was interface-freeze evidence for the earlier
parallel implementation. It is not restored as a second current authority.
