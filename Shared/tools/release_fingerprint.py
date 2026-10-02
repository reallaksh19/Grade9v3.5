#!/usr/bin/env python3
"""The fingerprint of a release: what it was made of, by digest (schema: Shared/assurance/release-fingerprint.schema.json).

The canonical inputs, the sources they cite, the policy, the assurance bundle and each projection, every digest taken over LF-normalised bytes so that it is the same on every
checkout. The assurance digest is the bundle's own `bundle_digest`, after the bundle has been checked against its schema and its content, so that it is the digest the
eligibility record names as well.

    python3 Shared/tools/release_fingerprint.py --product-id P --canonical-dir Physics/library --web-dir public [--standalone-dir standalone] [--search-index I]
        [--assurance-bundle B] [--output F]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import aggregate, contract  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402

RENDERER = "render_core/2"
POLICY_DIRS = (REPO / "Shared" / "policy", REPO / "Shared" / "assurance" / "policies")


def source_refs(value, found: set[str] | None = None) -> set[str]:
    found = set() if found is None else found
    if isinstance(value, dict):
        for k, v in value.items():
            if k == "source_refs" and isinstance(v, list):
                found |= {i for i in v if isinstance(i, str)}
            else:
                source_refs(v, found)
    elif isinstance(value, list):
        for item in value:
            source_refs(item, found)
    return found


def build_fingerprint(product: str, canonical_dirs: list[Path], web_dir: Path | None = None, standalone_dir: Path | None = None,
                      search_index: Path | None = None, assurance_bundle: Path | None = None) -> dict:
    refs: set[str] = set()
    for root in canonical_dirs:
        for path in sorted(root.rglob("*.json")):
            try:
                source_refs(json.loads(path.read_text(encoding="utf-8")), refs)
            except (OSError, ValueError) as exc:
                raise ContractError("FINGERPRINT_UNREADABLE_CANONICAL", f"{path}: {exc}") from exc
    bundle_digest = None
    if assurance_bundle is not None:
        bundle = json.loads(Path(assurance_bundle).read_text(encoding="utf-8"))
        contract.require_valid("bundle", bundle)
        problems = aggregate.verify_bundle(bundle)
        if problems:
            raise ContractError("FINGERPRINT_BUNDLE_BROKEN", "; ".join(p["message"] for p in problems))
        bundle_digest = bundle["bundle_digest"]
    record = {
        "schema": "release-fingerprint/v1",
        "product": product,
        "source_set_digest": contract.digest(sorted(refs)) if refs else None,
        "canonical_snapshot_digest": contract.digest_roots(canonical_dirs),
        "policy_digest": contract.digest_roots([d for d in POLICY_DIRS if d.exists()]),
        "assurance_bundle_digest": bundle_digest,
        "renderer_version": RENDERER,
        "web_projection_digest": contract.digest_tree(web_dir, ("*.html",)) if web_dir and Path(web_dir).is_dir() else None,
        "standalone_projection_digest": contract.digest_tree(standalone_dir, ("*.html",)) if standalone_dir and Path(standalone_dir).is_dir() else None,
        "pdf_projection_digest": None,
        "search_projection_digest": contract.digest_file(Path(search_index)) if search_index and Path(search_index).is_file() else None,
        "fingerprinted_at": contract.now(),
    }
    return contract.require_valid("release-fingerprint", record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--canonical-dir", required=True, nargs="+")
    parser.add_argument("--web-dir")
    parser.add_argument("--standalone-dir")
    parser.add_argument("--search-index")
    parser.add_argument("--assurance-bundle")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        record = build_fingerprint(args.product_id, [Path(d) for d in args.canonical_dir], Path(args.web_dir) if args.web_dir else None,
                                   Path(args.standalone_dir) if args.standalone_dir else None, Path(args.search_index) if args.search_index else None,
                                   Path(args.assurance_bundle) if args.assurance_bundle else None)
    except ContractError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.output:
        contract.write_json(Path(args.output), record)
    else:
        print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
