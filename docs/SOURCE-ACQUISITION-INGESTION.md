# Source acquisition and custody ingestion

This layer closes the gap between a source URL and a verified source receipt.

It deliberately separates **acquisition** from **custody transcription**. Downloading a PDF
does not prove that a particular question was preserved correctly, and a parser/OCR pass is
not allowed to silently become source authority.

## Stage 1 — acquire bytes

Use `Shared/tools/source_pipeline.py acquire`.

The acquisition record stores:

- requested and resolved locator;
- subject, bucket and intended resource id;
- acquisition date;
- media type and byte length;
- SHA-256 of the acquired bytes;
- optional retained snapshot path.

The bytes are content-addressed evidence. A later digest mismatch invalidates the acquisition.

Examples:

```text
python3 Shared/tools/source_pipeline.py acquire \
  --url https://example.org/source.pdf \
  --subject Physics \
  --bucket BUCKET-RELATIVE-MOTION \
  --resource-ref SRC-EXAMPLE \
  --locator https://example.org/source.pdf \
  --acquired-at 2026-09-18 \
  --snapshot-output /tmp/source.pdf \
  --output /tmp/source-acquisition.json
```

For a local file, use `--file` instead of `--url`. CI never depends on external network
availability; network acquisition is a runtime action, while tests use pinned local bytes.

## Stage 2 — explicit custody manifest

A custody manifest conforms to
`Shared/library/source-custody-manifest.schema.json`.

It names:

- the acquisition;
- the target canonical package;
- the inspector and inspected sections;
- one complete canonical resource record;
- zero or more complete canonical question records.

The manifest is explicit because exact source custody cannot be inferred safely from lossy
text extraction.

Every source-derived question in the manifest also carries a typed
`extensions.source_custody` proof validated against
`Shared/library/source-question-custody.schema.json`. The proof binds the question to the
acquisition/resource digest, names the precise source item locus, records embedded-verbatim
versus external-reference custody, and records the inspection state of each demand-bearing
component. Candidate records may remain unresolved; unresolved custody cannot be promoted or
used to establish Core2 sufficiency.

The pipeline refuses:

- resource ids that do not match the acquisition;
- authored resources presented as external sources;
- resource snapshot digests that differ from the acquired bytes;
- non-CANDIDATE resources/questions;
- questions marked AUTHORED;
- questions that do not cite the acquired resource;
- question custody proofs whose acquisition/resource/digest or inspected item locus does not match;
- internally inconsistent component claims such as a preserved figure with no figure identity;
- unequal canonical id collisions;
- any merged package that fails the package schema.

## Stage 3 — candidate ingestion

Use:

```text
python3 Shared/tools/source_pipeline.py ingest \
  --acquisition /tmp/source-acquisition.json \
  --manifest /tmp/source-custody-manifest.json
```

Without `--write`, this is a dry-run and does not mutate the package.

With `--write`, the tool updates the target package and writes a generated source receipt.
New source transcriptions remain `CANDIDATE`.

Automated ingestion never promotes a question to `REVIEWED` or `CURATED`.

## Receipt generation

The receipt is derived from the post-ingestion canonical state.

`SUFFICIENT` source coverage is stricter than “at least one question exists.” For each
Core, every capability owned by the bucket must be represented by an eligible
`REVIEWED`/`CURATED` source-bound question.

Therefore a newly ingested CANDIDATE transcription produces an `INSUFFICIENT` receipt even
when the transcription is structurally complete. Review/promotion is a separate lifecycle
step.

Core2 has the additional custody rule that only `ORIGINAL` or `ADAPTED` source-bound
questions count.

## Why extraction is not automatic authority

A PDF parser or OCR system can assist an agent in preparing a custody manifest, but its
output is not accepted as canonical merely because extraction succeeded.

The manifest must explicitly state the canonical question record. The pipeline pins that
record to the acquired source bytes and enters it as a candidate. Separate review decides
whether the transcription is accurate enough to promote.

This keeps three facts distinct:

```text
download succeeded
!=
transcription is exact
!=
source custody is reviewed
```

## Deterministic fixture

`tests/fixtures/source_ingest/` contains a small local source, its acquisition record and
its custody manifest.

The fixture proves the complete path without using a network connection:

```text
raw bytes
  -> digest-verified acquisition
  -> candidate resource/question merge
  -> package-schema validation
  -> automatically derived receipt
  -> receipt remains INSUFFICIENT until review
```

The executable falsifiers live in `tests/test_source_pipeline.py`.
