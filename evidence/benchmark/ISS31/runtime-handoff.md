# Issue 31 — executable-runtime handoff

Use this only in a real checkout of `agent/iss31-hybridisation-candidate-a-20261004` at or after repair commit `f1621cd167a569f85ea42909ad97db1060028db5`.

The purpose is to continue the same candidate, not to alter provenance or promote it.

## 1. Validate the path repair first

```bash
python3 -m unittest tests.test_test_area.TestOwnerBankFromIntake -v
```

Do not continue if the new destination/security regression fails.

## 2. Materialize owner custody through the repaired CLI

Prepare an intake projection whose ten question texts are byte-for-byte the stems recorded in `evidence/benchmark/ISS31/question-ledger.json`. Then run:

```bash
python3 Shared/tools/owner_bank.py new \
  --intake evidence/benchmark/ISS31/owner-bank-intake.json \
  --bank-id issue31-hybridisation \
  --out Chemistry/library/owner-bank/issue31-hybridisation.json
```

Populate only authored answer/support/analysis fields from the frozen ledger/QRT evidence. Never edit a stem and never add exam/year/paper/source URL identity.

Then:

```bash
python3 Shared/tools/owner_bank.py check \
  Chemistry/library/owner-bank/issue31-hybridisation.json \
  --intake evidence/benchmark/ISS31/owner-bank-intake.json
```

## 3. Chemistry package + manifest

Create the Chemistry hybridisation package under `Chemistry/library/` using `Shared/library/package.schema.json`, binding the capabilities/microtopics/families used by all ten owner questions. Validate it with the repository resolver/schema checks.

Derive the product manifest with `Shared/tools/product_manifest.py derive`, select all ten owner questions, and set exactly:

```json
"output_roles": ["CORE1A", "CORE2"]
```

## 4. Governed render only

```bash
python3 Shared/tools/render_core.py gaps --manifest <manifest>
python3 Shared/tools/render_core.py build --manifest <manifest> --out /tmp/iss31-hybridisation --mode PAGES
test -f /tmp/iss31-hybridisation/core1a.html
test -f /tmp/iss31-hybridisation/core2.html
```

Run the repository quality/browser audit on those exact bytes. Record render digest, protected-byte/leakage evidence, tablet/touch/focus/overflow results and exact tested commit.

Only after inspecting the actual pages may the Q5 two-lens interaction be translated into a builder-module proposal. No merge, publication or golden promotion is authorised by this handoff.
