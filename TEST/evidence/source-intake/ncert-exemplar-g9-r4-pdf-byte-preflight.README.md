# R4 NCERT Exemplar PDF byte preflight — not custody approval

This is a non-authoritative acquisition checklist for parent issue #68, not an accepted source-custody receipt, academic validation, or release handoff. The corresponding [manifest](ncert-exemplar-g9-r4-pdf-byte-preflight.v1.json) deliberately pins **null** official PDF digests and **false** for every authority/promotion flag.

## Inputs (independently retrieved official documents)

In an environment permitted to retrieve official files, save these original response bytes **without transformation** in a separate local directory:

| Local filename | Official NCERT URL | Observed zero-based PDF page indices |
| --- | --- | --- |
| `ieep201.pdf` | https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf | 2 (Unit 1 Q7), 3 (Unit 1 Q11–Q12) |
| `ieep202.pdf` | https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf | 2 (Unit 2 Q11–Q12) |
| `ieep2an.pdf` | https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf | 0 (Unit 1 answers), 3 (Unit 2 answers) |

Do not copy files from an untrusted mirror and relabel them as NCERT-issued. The official source edition and retrieval provenance must be verified independently from the presence of an NCERT URL in this checklist.

From the repository root:

```sh
python3 -m unittest tests.test_test_source_pdf_bytes -v
python3 Shared/tools/test_source_pdf_bytes.py
python3 Shared/tools/test_source_pdf_bytes.py --pdf-dir /trusted/local/ncert-exemplar
```

Without a `--pdf-dir` argument, the tool reports `OFFICIAL_PDF_BYTES_UNAVAILABLE` and **zero** digests. With all three files supplied, it computes local byte counts and SHA-256 digests, performs only a coarse PDF header/footer probe, and reports `LOCAL_PDF_BYTES_MEASURED_UNAUTHENTICATED`. It does not validate rendered content, origin, transport, edition, reviewer identity, official signatures, or academic correctness. Never turn the local digest output into a `*.custody.v1.json` overlay by itself.

## Additional evidence required before any source-custody review

An independently authorized reviewer must authenticate the origin and exact edition of all three official PDFs, record their immutable bytes/sha256 and retrieval provenance, confirm the relevant printed and PDF-index locators, and compare exact original stem, **every option/subpart**, the official answer-key locator and key, and the stable source ID/Unicode mathematical notation. Existing Q7 and Q11–Q12 rendered-page observations provide context, not that independent authentication. Version a separate per-ID evidence record with verifiable reviewer provenance, then run the existing source-custody witness/overlay checks and request the governed acceptance decision. In all cases, academic receipt validity, canonical admission, Owner approval and publication remain distinct gates.

The current manifest represents **five pending source IDs** (Unit 1 Q7, Q11, Q12; Unit 2 Q11, Q12). Other pending items in the 210-question bank are **out of scope** for this byte-preflight, and none becomes READY through this checklist.
