#!/usr/bin/env python3
"""Verify a projection against its manifest: the artifact is the one the manifest describes, and the canonical state it was built from is the one the library holds now.

Both are PROJECTION_INTEGRITY. The first fails when the pages changed after the manifest was made (edited by hand, or built again without a new manifest); the second when the
canonical content changed after the projection was built (the projection is stale). Evidence about the projection, bound to the digest of its pages now, is written outside the
render directory. With --enforce the exit status is 1 unless both hold.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import contract  # noqa: E402
from Shared.assurance.evidence import finding, make_evidence, write_evidence  # noqa: E402


def verify(manifest: dict, render_dir: Path, canonical_dirs: list[Path]) -> tuple[str, list[dict], str]:
    """(outcome, findings, digest of the pages now)."""
    contract.require_valid("projection-manifest", manifest)
    now = contract.digest_tree(render_dir, ("*.html",))
    found: list[dict] = []
    if now is None:
        found.append(finding("PROJECTION_EMPTY", "S1", str(render_dir), "the render directory holds no pages"))
        now = contract.digest({"empty": str(render_dir)})
    elif now != manifest["artifact_digest"]:
        found.append(finding("ARTIFACT_CHANGED", "S1", str(render_dir), "the pages are not the ones the manifest describes", evidence={"committed": manifest["artifact_digest"], "now": now}))
    if canonical_dirs and contract.digest_roots(canonical_dirs) != manifest["canonical_snapshot_digest"]:
        found.append(finding("STALE_CANONICAL", "S1", str(render_dir), "the library changed after this projection was built: rebuild it"))
    return ("FAIL" if found else "PASS"), found, now


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--canonical-dir", nargs="+", default=[], help="the library directories it was built from; without them staleness is not checked")
    parser.add_argument("--projection-id", default=None, help="the subject id of the evidence (default: the name of the render directory)")
    parser.add_argument("--evidence-dir", default="build/assurance/evidence")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"Error: {manifest_path} not found", file=sys.stderr)
        return 1
    outcome, found, now = verify(json.loads(manifest_path.read_text(encoding="utf-8")), Path(args.render_dir), [Path(d) for d in args.canonical_dir])
    record = make_evidence("PROJECTION_INTEGRITY", "PROJECTION", args.projection_id or Path(args.render_dir).name, outcome, "verify_projection_manifest", "1.1.0",
                           findings=found, subject_digest=now, configuration={"canonical_dirs": sorted(Path(d).as_posix() for d in args.canonical_dir)})
    write_evidence(record, REPO / args.evidence_dir / f"{record['evidence_id']}.json")
    print(f"Outcome: {outcome}")
    for f in found:
        print(f"  {f['code']}: {f['message']}")
    return 1 if (args.enforce and outcome != "PASS") else 0


if __name__ == "__main__":
    raise SystemExit(main())
