# SOF IMO Grade 9 — independent-review and source-rights handoff

**Purpose:** enable external qualified reviewers and a publishing/rights owner to make **evidenced** decisions on the ten source-versus-compilation discrepancy cases in [the existing custody register](../adjudication/README.md). This is a research work queue, **not** a self-certified academic review, automatic legal clearance, publisher key, or learner-content export.

The question inventory remains the original owner compilation of 66 source candidates. The B01–B04 researcher-computed audit covers **58/58 attachment-selected full-paper source positions**, not the complete 150 printed slots of three Level 1 exams. The SOF-hosted 2026–27 sample has 10 observed positions (eight original seed and two separately discovered). The discrepancy register covers 10 cases / 11 source positions.

## Review order

| Priority | Cases | Distinct external decision needed |
|---|---|---|
| **P0** | 006 (printed identity versus owner inverse), 007 (angle figure and answer C/D), 009 (sample Q5 parallel-line diagram still unsolved), 010 (sample Q9 radical/index rewrite) | Source editorial/math adjudication and independent diagram/notation proof; source content remains held |
| **P1** | 001 (fourth predecessor digit 5/B, owner 4/C), 002 (changed distractor), 003 (correct choice reordering), 004 (original pie-chart custody) | Independent option arithmetic and source-fidelity reviewer; original figure rights separately required |
| **P2** | 005 (2024 printed Q44 section is Everyday Mathematics), 008 (2025 Q32 and Q33 split into separate items sharing one chart) | Source locator and figure-identity sign-off; source observation alone is not learner approval |

The machine-readable `independent-review-queue.v1.json` contains one packet per case: immutable source ID/PDF page/case ID, exact reviewer **role** needed, a targeted question, the minimal signed evidence receipt sought, and the task the reviewer must perform. No personal reviewer has been assigned. `review_packet_status=PREPARED_UNASSIGNED` throughout.

**Not yet obtained:** a qualified independent peer-academic calculation/signature, checked figure-based proof for source sample Q5, publisher's source Q28 erratum/key decision, exact source sample Q9 notation sign-off, or peer-accepted academic answers. An AI-worked answer, a publicly viewable PDF and a passing automated test are **not substitutes** for these receipts.

## Copyright and figure/option rights

The queue has **four distinct document-level license checks**: the three school-hosted full papers and the organizer-hosted sample. A school's publication of a paper does **not** establish that the school owns SOF's copyright or can grant a third-party text/figure/option reproduction license. Likewise, SOF hosting its sample does not automatically license replication in this project's learner-facing bank.

For each document `publisher_rights_holder_identity=NOT_ESTABLISHED`, `permission_request_status=NOT_SENT`, `rights_review_decision=NOT_GRANTED_OR_EVIDENCED`, `figure_and_text_reuse_authorized=false`. No outreach is claimed to have been sent; no signed grant or license document is present.

Before any original-item publication, an authorized reviewer must obtain a written source-specific permission or applicable license, confirm permitted education/redistribution/derivative/figure uses, store the authority and evidence digest via a separately reviewed rights process, and decide what is actually reproducible. If no rights are obtained, use **independently authored analogues** rather than copying exam stems, choices or diagrams and mislabeling them as authentic.

## Academic and QRT acceptance contract

This queue does not contain any positive acceptance pathway executable by tests. A later separately reviewed decision must identify the academic expert, the exact source position and source version, original figure/notation crosscheck, signed mathematical rationale and decision timestamp. Original-source fidelity and legal reuse must also be approved as their **own** gates. Only then should a QRT classification be assessed with the historical seven demands and current five-factor difficulty policy, followed by explicit Core admission approval.

The exact statuses are zero here: **0 signed academic reviews; 0 evidenced source reuse grants; 0 independently accepted 4×7 QRT cells out of 28; 0 Core-ready questions.** Retaining `QRT-NOT-APPROVED` does not imply a provisional classification does not exist elsewhere; the separate sample proposal remains unaccepted.

## Validate

```sh
python TEST/imo-research/validate_review_gates.py
python -m unittest discover -s tests -p 'test_imo_review_gates.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The fail-closed validator first checks the merged discrepancy register against seed, B01/B02 and sample proof metadata. It then checks all 10 reviewer packets, 11 exact source IDs, 4 source-document rights holds, four P0 priorities, expected reviewer receipt types and all no-approval fields. Eighteen focused positive/negative regression tests reject forged peer signatures, organizer errata, publisher permission, missing case IDs or premature QRT/Core eligibility. The dedicated IMO research workflow exercises these tests.

**Limits:** passing the workflow is only evidence of **review-queue data integrity**; it is not evidence of an academic reviewer, real outreach, source license, official full-paper answer key, source-figure consent or learner-ready question. No original exam stem, complete choices or figure images are redistributed in this artifact.

Responsibility: [issue #254](https://github.com/reallaksh19/Grade9v3.5/issues/254); upstream source case ledger: [issue #250](https://github.com/reallaksh19/Grade9v3.5/issues/250).
