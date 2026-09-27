# Vendored browser runtimes

## Tailwind CSS Play CDN 3.4.17

- Local runtime: `vendor/tailwind/3.4.17/tailwind-play.js`
- SHA-256: `20fda8a2158e83d6f78aa7e614ec1f7183ac10423cf956ded061cbe664c87bef`
- Size: 407279 bytes
- Runtime family: Tailwind CSS Play CDN v3; the bundle contains the `3.4.17` version marker.
- Snapshot source: `satoshikawato/gbdraw@main:gbdraw/web/vendor/tailwindcss/tailwindcss-play.js`, whose notices identify it as a vendored snapshot of `https://cdn.tailwindcss.com`.
- Upstream license: Tailwind Labs MIT, copied beside the runtime as `vendor/tailwind/3.4.17/LICENSE`.

The Pages builder rewrites the repository's legacy Tailwind CDN script URLs to this local snapshot. New unapproved external runtime dependencies fail closed in the publication transform rather than silently entering `docs/`.