# Portable Semantic Workbench integration

Issue #163 adds a packaging and host layer around the delivered Semantic Workbench Core. It does not move academic truth, learner routing, or page composition into the portable layer.

## Version seams

Every generated package declares `packageVersion`, `componentApiVersion`, `transformationIrVersion`, `adapterApiVersion`, and `scenePackageVersion`. The host validates all seams before mounting. A mismatch is a visible failure, never a silent best-effort render.

## Data-only package

A portable package contains an already-compiled semantic scene, a declarative transfer adapter payload, provenance/source references, optional question bindings, and pedagogy injections. Package provenance is explicitly `NON_CANONICAL_COMPILED_PROOF`.

Package data cannot contain executable JavaScript fields, and normal scene placement uses named grid/row/column coordinates rather than authored pixels. The portable host uses no `eval` or `new Function`.

## Hosts

`Shared/tools/build_portable_workbench.py` generates from one source path:

- `public/portable-workbench/` — repository static host and built runtime assets;
- `tests/fixtures/portable-workbench/external-host.html` — plain HTML host with no Grade9V3 CSS, learner store, router, or page shell;
- `standalone/portable-workbench/index.html` — one HTML file with engine and package data embedded, requiring no CDN or network dependency after the file is obtained.

Hosts configure `<semantic-workbench>` only through public properties and CSS custom properties. Semantic events remain observations such as transfer accepted/rejected; the portable layer does not interpret mastery.

## Cross-subject proofs

The same component and declarative adapter contract is used by long division, Redox, and integration proof packages. Long division reuses the existing Core witness; the Redox and integration rows are compiled portability proof fixtures, not a replacement subject database.

## Redox migration guidance

`standalone/chemistry-redox-reactions-master-suite.html` remains a reference prototype. Its page behavior is not imported as runtime authority. Migration should move a selected scientific transformation into canonical/compiled scene data, keep question selection outside the workbench, and let the host inject support/hints explicitly. The compiled portable package records provenance but never treats the bespoke page JavaScript as canonical truth.

## Compatibility rule

A consuming app needs only the generated portable runtime assets plus a package JSON, or the generated single-file host. It must not reach into Shadow DOM to configure behavior. If Core later changes an API version, old packages fail closed until deliberately rebuilt.
