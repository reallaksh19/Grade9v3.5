# Portable Semantic Workbench integration

Issue #163 adds a packaging and host layer around the delivered Semantic Workbench Core. It does not move academic truth, learner routing, or page composition into the portable layer.

## Version seams

Every generated package declares `packageVersion`, `componentApiVersion`, `transformationIrVersion`, `adapterApiVersion`, and `scenePackageVersion`. The host validates all seams before mounting. A mismatch is a visible failure, never a silent best-effort render.

## Data-only package

A portable package contains an already-compiled semantic scene, a declarative transfer adapter payload, provenance/source references, optional question bindings, and pedagogy injections. Two provenance authorities are accepted:

- `NON_CANONICAL_COMPILED_PROOF` for portability fixtures. These packages prove runtime portability only and never become academic authority.
- `CANONICAL_COMPILED_RESOURCE` for a package compiled from governed canonical inputs. This form must carry an explicit `resourceRef`, one declared canonical representation ref, and source refs that match the package provenance exactly.

Package data cannot contain executable JavaScript fields, and normal scene placement uses named grid/row/column coordinates rather than authored pixels. The portable host uses no `eval` or `new Function`.

## Hosts

`Shared/tools/build_portable_workbench.py` generates from one source path:

- `public/portable-workbench/` — repository static host and built runtime assets;
- `tests/fixtures/portable-workbench/external-host.html` — plain HTML host with no Grade9V3 CSS, learner store, router, or page shell;
- `standalone/portable-workbench/index.html` — one HTML file with engine and package data embedded, requiring no CDN or network dependency after the file is obtained.

Hosts configure `<semantic-workbench>` only through public properties and CSS custom properties. Semantic events remain observations such as transfer accepted/rejected; the portable layer does not interpret mastery.

An explicit `?package=<id>` request is fail-closed in repository, external and standalone hosts. An unknown requested package reports `PORTABLE_PACKAGE_NOT_FOUND`; a networked package fetch that cannot be loaded reports `PORTABLE_PACKAGE_LOAD_FAILED`. Only an omitted package query uses the catalog default.

## Canonical Atlas binding

The portable binding layer consumes the final AtlasIndex 2.0 visual-target contract by exact `resource_ref`. It does not derive package identity from a title, locator URL, nearby rung, source order or semantic similarity.

`Shared/portable/binding.py` and the browser-side `resolveCanonicalPortableTarget` enforce the same sequence:

1. the requested `resource_ref` must exist and have resource availability `READY`;
2. `portable_package` must be `READY` and `portable_package_ref` must be explicitly declared;
3. that exact package must exist and validate under the portable package contract;
4. its provenance must be `CANONICAL_COMPILED_RESOURCE`;
5. package resource and representation identity must match the Atlas visual target.

Stable fail-closed findings include `VISUAL_REF_UNAVAILABLE`, `VISUAL_REF_INVALID`, `STANDALONE_PACKAGE_UNAVAILABLE`, `PORTABLE_PACKAGE_NOT_FOUND`, `PORTABLE_CANONICAL_PROVENANCE_REQUIRED`, `PORTABLE_RESOURCE_BINDING_MISMATCH` and `PORTABLE_REPRESENTATION_BINDING_MISMATCH`.

At the Issue #212 AtlasIndex 2.0 release used by Issue #214, `ACT-KIN-2D-SHARED-CLOCK` has a READY canonical resource/locator but `portable_package: UNAVAILABLE` and `standalone: UNAVAILABLE`. The resolver therefore returns `STANDALONE_PACKAGE_UNAVAILABLE`; it does not promote the existing activity page or a proof fixture into a canonical package. A production Motion package still requires a governed portable-declarative scene/action input and an explicit package declaration.

## Cross-subject proofs

The same component and declarative adapter contract is used by long division, Redox, and integration proof packages. Long division reuses the existing Core witness; the Redox and integration rows are compiled portability proof fixtures, not a replacement subject database.

## Redox migration guidance

`standalone/chemistry-redox-reactions-master-suite.html` remains a reference prototype. Its page behavior is not imported as runtime authority. Migration should move a selected scientific transformation into canonical/compiled scene data, keep question selection outside the workbench, and let the host inject support/hints explicitly. The compiled portable package records provenance but never treats the bespoke page JavaScript as canonical truth.

## Compatibility rule

A consuming app needs only the generated portable runtime assets plus a package JSON, or the generated single-file host. It must not reach into Shadow DOM to configure behavior. If Core later changes an API version, old packages fail closed until deliberately rebuilt.
Generated artifacts are freshness-checked by `python -m Shared.tools.build_portable_workbench --check`; exact-head repository validation remains the release gate.
