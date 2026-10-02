#!/usr/bin/env python3
"""Build the manifest of a projection: what it was built from, by digest, and what it holds.

A projection (pages, a PDF set, a search index) is not canonical. Its manifest names the canonical inputs it was built from (every JSON file under the library directories,
LF-normalised), the digest of the artifact (the pages under the render directory), and the canonical records the pages cite, so that verify_projection_manifest.py can say whether
the projection is still a projection of the library as it is now.

    python3 Shared/tools/build_projection_manifest.py --render-dir standalone --projection-type STANDALONE --canonical-dir Physics/library [--output M.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import contract  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402

GENERATOR = {"name": "build_projection_manifest", "version": "1.1.0"}
ID = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+")


def canonical_ids(roots: list[Path]) -> set[str]:
    """The id of every record in every package under `roots`: the things a page may cite."""
    from Shared.library import resolve
    ids: set[str] = set()
    for root in roots:
        for path in sorted(root.glob("*.json")):
            try:
                package = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise ContractError("PROJECTION_UNREADABLE_LIBRARY", f"{path}: {exc}") from exc
            if isinstance(package, dict):
                ids |= {row["id"] for c in resolve.COLLECTIONS for row in package.get(c, []) if isinstance(row, dict) and isinstance(row.get("id"), str)}
    return ids


def cited(render_dir: Path, ids: set[str]) -> list[str]:
    """The canonical record ids that appear in the pages. (A page named after a record is not a record; a record is cited when its id is in the page.)"""
    found: set[str] = set()
    for page in render_dir.rglob("*.html"):
        found |= {token for token in ID.findall(page.read_text(encoding="utf-8", errors="replace")) if token in ids}
    return sorted(found)


def build(render_dir: Path, projection_type: str, canonical_dirs: list[Path]) -> dict:
    artifact = contract.digest_tree(render_dir, ("*.html",))
    if artifact is None:
        raise ContractError("PROJECTION_EMPTY", f"{render_dir} holds no pages")
    canonical = contract.digest_roots(canonical_dirs)
    manifest = {
        "schema": "projection-manifest/v1",
        "projection_type": projection_type,
        "canonical_snapshot_digest": canonical,
        "generator": GENERATOR,
        "generator_input_digest": contract.digest({"canonical": canonical, "generator": GENERATOR}),
        "record_ids": cited(render_dir, canonical_ids(canonical_dirs)),
        "artifact_digest": artifact,
        "generated_at": contract.now(),
    }
    return contract.require_valid("projection-manifest", manifest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--projection-type", choices=["WEB", "STANDALONE", "PDF", "SEARCH", "BROWSER_DATA"], required=True)
    parser.add_argument("--canonical-dir", required=True, nargs="+")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        manifest = build(Path(args.render_dir), args.projection_type, [Path(d) for d in args.canonical_dir])
    except ContractError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.output:
        contract.write_json(Path(args.output), manifest)
    else:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
