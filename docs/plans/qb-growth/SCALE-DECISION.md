# Question Bank scale: what was measured and what it decides (#359, STEP-QB-09)

Evidence for two questions #359 left open: does the browser need a Web Worker, and does the search
index need to be sharded? The figures below come from a deterministic synthetic fixture
(`Shared/tools/question_bank_scale.py`) run through the real artifact builder and loaded into real
Chromium (`tests/question_bank_scale_browser.mjs`). Byte and count figures are reproducible; timings
are one 4-CPU container and are evidence, not thresholds.

## Browser cost of the generated artifacts

| Questions | Search index | gzip | Parse and run | JS heap growth | Median query, before | Median query, after | Cold first query |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 500 | 266 KB | 17 KB | 7 ms | 1.3 MB | 0.9 ms | 0.1 ms | 4 ms |
| 2,000 | 1.07 MB | 67 KB | 16 ms | 2.9 MB | 4.7 ms | 0.4 ms | 12 ms |
| 5,000 | 2.68 MB | 167 KB | 49 ms | 6.2 MB | 7.4 ms | 1.0 ms | 23 ms |
| 10,000 | 5.37 MB | 332 KB | 76 ms | 11.7 MB | 19.8 ms | 2.2 ms | 28 ms |
| 20,000 | 10.79 MB | 666 KB | 163 ms | 22.8 MB | 31.5 ms | 4.6 ms | 64 ms |

- The catalog is 32 KB at every scale: it holds counts and membership, not questions.
- The search index grows linearly at about 0.54 KB per question (about 33 bytes gzipped).
- "Before" is the search loop as first written, which re-normalised every document's text on every
  query. "After" normalises each document once (cached per document object) and returns identical
  hits for every measured query. Only the first query pays for it.

## Page render cost (the real page, wired to the generated contracts)

`tests/question_bank_scale_render.mjs` loads the real Question Bank page over local HTTP against N
synthetic questions and times what the learner waits for. Each interaction figure includes two
animation frames (about 33 ms at 60 Hz), so a value near 30 ms means "done within the frame".

| Questions | To a drawn list | JS heap | Subject tab | Topic pill | Search | Load more | Open Study |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 500 | 184 ms | 3.7 MB | 28 ms | 31 ms | 13 ms | 28 ms | 11 ms |
| 2,000 | 172 ms | 7.2 MB | 53 ms | 26 ms | 22 ms | 29 ms | 11 ms |
| 5,000 | 287 ms | 13.9 MB | 48 ms | 31 ms | 17 ms | 30 ms | 13 ms |
| 10,000 | 432 ms | 24.5 MB | 59 ms | 31 ms | 15 ms | 33 ms | 15 ms |

Median of five runs per interaction. Interactions do not grow with the corpus because the page draws
one page of 20 cards whatever N is; only the filter over the summaries grows, and it is small. Time to a
drawn list grows with the artifacts (parse, catalog and list), as the table above predicts.
A tweak that draws the static navigation once per load was tried and showed no difference above the noise,
so it was not kept.

## Decisions

1. **No Web Worker for search.** After the cache a query costs about 1 ms at 5,000 questions and
   under 5 ms at 20,000, so a worker's message-passing overhead would not pay for itself.
2. **No sharding of the search index at the current target (thousands).** At 5,000 questions the
   index is 167 KB over the wire and 49 ms to evaluate. **Revisit** when the index passes about
   5 MB raw (about 10,000 questions) or evaluation passes 100 ms on the slowest supported tablet;
   the per-subject detail shards that already exist are the natural template.
3. **Detail stays sharded and on demand** (already in place); it is not part of the figures above.

## Finding: the near-duplicate search declines to look, silently

Building is linear for the catalog and search index, but the near-duplicate search is bounded on
purpose (`NEAR_MAX_BUCKET`, `NEAR_MAX_CANDIDATES_PER_RECORD`) and used to say nothing when a bound
applied. On the synthetic fixture at 5,000 questions (50 templated stems per topic) every one of the
400 shared-shingle buckets exceeds the bound, so **no record was examined** and the report looked
like "no near duplicates". The report now carries `near_duplicate_coverage`, and the build receipt
carries `counts.near_duplicate_search_complete`.

Not decided here: replacing the per-bucket cap with a per-topic work budget (rarest shingles first)
would search crowded topics without going all-pairs. It changes what the build reports on large
corpora, so it is left for the Owner. The committed corpus (77 questions) is searched completely.

## Not measured

A tablet-class CPU, memory outside the JS heap, network latency, and the heap the per-document search cache
adds after the first query (about the size of the index text again; the first heap column is taken before it).
The 12.7-inch tablet is expected to be several times slower than this container; that ratio has not been measured.

## Re-running

```
node tests/question_bank_scale_render.mjs 500,2000,5000,10000 out.json
node tests/question_bank_scale_browser.mjs 500,2000,5000,10000,20000 out.json
python3 Shared/tools/question_bank_scale.py --questions 5000
```
