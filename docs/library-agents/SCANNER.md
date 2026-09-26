# Scanner (local agent): converting scanned books and question papers

The scanner is a researcher that works on the owner's machine with books and papers the owner
holds on paper or as scans. Its output is the same as the web researcher's: pinned
acquisitions and **evidence cards**. The same checker verifies them, and the same author and
verifier consume them.

Three problems make scans riskier than web sources, and the protocol answers each:

| Problem | Answer |
|---|---|
| OCR misreads text, especially numbers, symbols and equations | Quotes must match the OCR text exactly, so nothing is silently "fixed". Every card whose numbers matter carries an **independent second reading** from the page image, and the checker compares the numbers itself. |
| The book is copyrighted and the repository is public | Scan bytes, OCR text and page images **never leave the owner's machine**. The repository gets the scan's SHA-256 and a **hashed 5-word shingle index** per page: quotes can be proven present, but the text cannot be read back. |
| An agent could ingest anything and call it a source | Only the **owner** registers a source and the exact SHA-256 of each scan file. An unregistered file cannot be ingested or cited. |

## 1. Owner registers the source (once per book or paper)

1. Print the digest of each scan file:
   `python Shared/tools/scan_ingest.py hash --file "D:\scans\hcv-vol1-ch3.pdf"`
2. Add an entry to `local_sources` in `Physics/research/source-allowlist.json`:
   ```json
   {
     "source_id": "SRC-BOOK-EXAMPLE-VOL1",
     "title": "…", "authors": ["…"], "publisher": "…", "edition": "…", "year": 2019, "isbn": "…",
     "kind": "TEXTBOOK",
     "tier": "B",
     "may_support": ["DEFINITION", "RELATION", "CONDITION", "WORKED_EXAMPLE", "MISCONCEPTION", "QUESTION", "ANSWER_KEY"],
     "rights": "COPYRIGHTED_OWNED_COPY",
     "scan_sha256s": ["<digest from step 1>"],
     "registered_by": "owner", "registered_at": "2026-09-26"
   }
   ```
   - `tier` is **A** only for official NCERT, CBSE, NTA or JEE Advanced material, and **B** for
     published reference books and question banks.
   - `may_support` may narrow the tier. Tier-B sources can back questions and answer keys only
     if you list them here, and those questions are labelled with the book, never an exam.
   - `kind` is one of `TEXTBOOK`, `EXEMPLAR`, `QUESTION_BANK`, `EXAM_PAPER`, `ANSWER_KEY` or
     `NOTES`.
   - `rights` is `OFFICIAL_PUBLIC` or `COPYRIGHTED_OWNED_COPY`.

   Commit the allowlist change yourself (owner). The scanner must not edit `local_sources`.

## 2. Scan quality

- 300 dpi, grayscale, one printed page per PDF page (split two-page spreads), deskewed, with
  the printed page number visible.
- Scan the **answer pages** of any exercise or question bank you use. A question without
  its official or book answer key cannot become a QUESTION card.
- One PDF per chapter (or per paper). Images can be combined first, for example with
  `img2pdf *.png -o ch3.pdf`.
- Keep scans outside the repository folder, or in `.source-cache/` (git-ignored).

## 3. OCR and ingest

Preferred engine: **OCRmyPDF + Tesseract**. It is pinned and reproducible, and its version is
recorded automatically.

```powershell
pip install jsonschema pypdf cffi ocrmypdf        # plus Tesseract (UB-Mannheim installer on Windows)
python Shared/tools/scan_ingest.py ingest --subject Physics --source-id SRC-BOOK-EXAMPLE-VOL1 `
  --file "D:\scans\hcv-vol1-ch3.pdf" --node PHY-11-MOTION-IN-A-PLANE --agent local-scanner-1 `
  --ocr ocrmypdf --printed-page-offset 40
```

Other engines are allowed if you record the engine name and version:

- **The PDF already has an OCR text layer:** `--text-layer --ocr-engine "ABBYY FineReader 16"`.
- **Any other OCR:** write `{"pages": ["page 1 text", …]}` and pass
  `--pages-json pages.json --ocr-engine "name version"`.

The tool refuses unregistered files. It writes:

- `Physics/research/acquisitions/<ACQ>.json`: the source id and the scan file's SHA-256;
- `Physics/research/scans/<ACQ>.scan.json`:
  - OCR engine and version;
  - the page map (`printed page = pdf page + offset`);
  - `low_text_pages`;
  - the shingle index.

  This file holds **no text**.

The local OCR text goes into `.source-cache/`.

**`low_text_pages`** are figure pages or OCR failures. Re-scan them, or use them only for
DIAGRAM cards (section 5).

## 4. Writing cards from a scan

Follow [RESEARCHER.md](RESEARCHER.md) with these additions:

1. Read the OCR text with
   `python Shared/tools/scan_ingest.py pages --subject Physics --acq <ACQ> --page N`.
2. `quote` is copied **exactly from that OCR output, noise included** (for example `T ake`,
   `10 –3`). Never correct the quote. The clean version goes into `claim` and, for numeric
   cards, into `scan_check.second_reading`.
3. `locator.page` is the PDF page index. `printed_page` comes from the page map.
4. **Numeric cards need a second reading.** This covers QUESTION, ANSWER_KEY, WORKED_EXAMPLE
   and RELATION cards:
   ```json
   "scan_check": {
     "second_reading": "A stone is thrown horizontally at 15 m/s from a cliff 20 m high.",
     "second_reader": "owner",
     "method": "HUMAN",
     "image_crop_sha256": "<optional: digest of the page crop that was read>"
   }
   ```
   - The second reading is transcribed **from the page image**, not from the OCR text, by
     someone other than the harvester. That can be the owner (`HUMAN`), a separate vision
     model session given only the image crop (`VISION_MODEL`), or a different OCR engine
     (`SECOND_OCR_ENGINE`, e.g. a math OCR).
   - `evidence_check.py` refuses the card if the second reader is the harvester, if the
     numbers differ from the OCR quote's, or if the passages are under 85% alike. On a number
     mismatch, look at the page image and fix whichever reading is wrong. **Never guess**: an
     illegible number means re-scan or pick another question.
   - The author uses `second_reading`, not the OCR quote, as the question stem.
5. QUESTION cards from a book use `question.exam` = the book title and `paper` = the chapter or
   exercise, with the `answer_key_card_ref` pointing at the ANSWER_KEY card from the book's
   answer pages. An exam identity (JEE 2019 …) is claimed only if the book prints it **and** a
   Tier-A card from the official paper confirms it.
6. `python Shared/tools/evidence_check.py check --subject Physics --node <NODE>` must report
   no findings.

## 5. Figures

- Figures are not OCR'd. Describe a figure in a DIAGRAM card: its labelled elements, arrows,
  angles and given values, with a quote of the caption or nearby text.
- Keep page crops local, and record their digest in `image_crop_sha256` when they were read.
- **Never commit crops of a copyrighted figure.** The author redraws the figure as original
  SVG from the description, with provenance `SOURCE_DERIVED`. The verifier compares it with
  the description.

## 6. Rights

- `COPYRIGHTED_OWNED_COPY`: quotes stay as short as the claim allows, one or two sentences at
  most. Questions are stored with custody mode `EXTERNAL_REFERENCE` (book, chapter,
  exercise, number). Whether learner products reproduce them is the owner's decision; authored
  practice can always teach the same demand.
- `OFFICIAL_PUBLIC` (NCERT, CBSE and NTA papers): normal rules.
- Never commit scans, OCR text, page images, or `.source-cache/`.

## 7. Batch quality check (owner)

After each chapter:

- open 5 random cards from the scan and compare them with the page image;
- for one random page, type a paragraph yourself and compare it with the OCR text.

If more than 1 in 5 cards is wrong, re-scan or switch OCR engine for that book before
continuing. These are labels on the batch; the board keeps assigning work either way.

## 8. Git

Commit `acquisitions/`, `scans/` and `evidence/` for one node per commit, and push to
`research/physics-library` (`git pull --rebase` first). The cloud author and verifier, and CI,
verify your quotes from the shingle index without needing your files.

## Forbidden

- Ingesting a file the owner has not registered, or editing `local_sources`.
- Correcting OCR text inside `quote`.
- Filling illegible parts from memory.
- Second-reading your own cards.
- Committing scan bytes, OCR text or figure crops.
- Claiming an exam identity from a book's label alone.
