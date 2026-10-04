# Compatibility repair slice — 4 October 2026

Checkout base `346accad5f2489d6a082cffd927c84d4295fb6e3`; actual tested authority hashes are in refreshed cycle receipts. The source commit field identifies the checkout base, while those hashes identify the edited renderer/CSS. Full-run tracked diff SHA256 before and after is identical: `3def4d0a696455d690631d9bb04dee3c0b902358803844652caf17dbf9e12f31`.

The generated blueprint specification and production Core-learning projections now use registry 1.10.0 / Core1A 1.5.0 / Core2 1.6.0. Version-sensitive fixtures were refreshed without relaxing their behavior assertions. Header controls now use the shared 48px minimum; small shell fonts and renderer labels respect a 14px CSS floor. Authored SVG label sizes/framing remain separate open work.

All nine additional failure IDs from the initial candidate-versus-seed full-suite comparison are absent after this repair. A focused 23-test slice PASS. All eight regenerated correction packs replay PASS; inputs remain unchanged. All eight existing tablet audits PASS with zero undersized targets and no page errors. This profile does not enforce every typography/focus/learning requirement: measured figure labels remain below 14px, and the broader Core1A audit FAILS on phone overflow and focus. `browser-bindings.json` distinguishes profile success from overall quality, which is not accepted.

The full local suite still FAILS: 2,289 tests, 79 failures, 52 errors, five skipped (726.717 seconds). The frozen seed has 77 failures/52 errors. The two remaining additional IDs assert an empty saved-artifact state; regeneration writes a local ignored derived-artifact index, so the resolver correctly finds DIRECT reuse instead. Temporarily removing only that generated index, preserving and restoring its bytes, makes both tests PASS. See the isolated empty-state logs and the preserved generated index. The full-suite verdict is not relabeled green, and no clean full-suite rerun or CI success is claimed.

The Physics friction reference build remains successful, and its newly rendered standalone conformance has zero FONT_FLOOR findings. Link closure still fails in the isolated staging tree. The Mathematics reference build's invalid PUBLISHED/VERIFIED_CANONICAL values reproduce at the frozen seed; validation and canonical data were not weakened or silently promoted.

The focus triage is explicitly a separate file-origin probe: all 33 unfocused elements are in closed disclosures and no eligible visible/enabled element failed its focus request. This helps explain the existing audit, but does not certify keyboard navigation, focus-ring visibility or opened repair states. Phone overflow is independently real.

Focused D1 B→A semantic triage and actual screenshots are preserved. Findings include conflicting surviving warrants, generic explanation fields, a repeated worked-anchor exit, tiny staged panels and the still-open coherent-teaching migration. This is not a full facet certificate.

U02 remains open: resolve real responsive/link/single-file compatibility, reconcile audit eligibility and the agreed Core1A policy without lowering usability requirements, and repeat exact checks. U03–U11 remain open under the parent plan. Frozen submission heads are unchanged; no merge, golden admission or learner publication.
