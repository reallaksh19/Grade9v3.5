# One method for authoring a learner product

Start with [HOUSE-RULES.md](HOUSE-RULES.md), then [PROTOCOL.md](PROTOCOL.md). The unit author owns the design, records, prototype and revisions; source readers and an independent reviewer contribute evidence and judgement. Nothing in this method authorizes publication. The Owner accepts or rejects one exact rendered digest.

| When | Read or use | Artifact |
|---|---|---|
| Scope and source | [Source-reader role](roles/SOURCE-READER.md), [source-reader prompt](prompts/source-reader.prompt.md) | acquisition, inventory, cards, independent `readback[]` |
| Design and prototype | [Unit-author role](roles/UNIT-AUTHOR.md), [unit-author prompt](prompts/unit-author.prompt.md), [golden candidates](../../golden/INDEX.md) | `UNIT.md`, `DESIGN-NOTE.md`, `SELF-CRITIQUE.md`, `WORKLOG.md` |
| Build observations | `python3 Shared/tools/self_check.py --unit SUBJECT/slug`; `python3 Shared/tools/diff_readback.py --subject SUBJECT --node NODE` | local advisory report and existing readback comparison |
| Independent review | [Reviewer role](roles/REVIEWER.md), [reviewer prompt](prompts/reviewer.prompt.md), [REVIEW-GUIDE.md](REVIEW-GUIDE.md), [anti-pattern cards](../../golden/anti/) | review v2 tied to the exact render digest |
| Owner decision | `Shared/tools/accept_product.py` | acceptance record and exact build copy |

The [techniques](../../golden/TECHNIQUES.md) and [anti-pattern cards](../../golden/anti/) are examples for reasoning, not fields to fill. Both v1 goldens are marked CANDIDATE and rendered through `render_core.py`; no candidate is a published product. Research the unit's teaching choices and factual sources afresh.

Reusable templates: [UNIT](templates/UNIT.md), [DESIGN-NOTE](templates/DESIGN-NOTE.md), [SELF-CRITIQUE](templates/SELF-CRITIQUE.md), [WORKLOG](templates/WORKLOG.md), [OWNER-NOTES](templates/OWNER-NOTES.md). Superseded parallel instructions remain in [archive/](archive/) for historical reconstruction.
