#!/usr/bin/env python3
"""Verify the committed search index against the canonical state: current, complete, and unaltered.

  SEARCH_MEMBERSHIP     every canonical question is in the index and nothing else is; and the index was built from the canonical content as it is now
                        (an index of older text is not a projection of this library, even if the ids still match)
  SEARCH_RETRIEVABILITY the index file is the one its manifest describes

Each is written as evidence about the PROJECTION `search`, bound to the digest of the index file, outside the tree it judges. With --enforce the exit status is 1 unless
both PASS: a stale index is not a pass with a caveat.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance import contract  # noqa: E402
from Shared.assurance.evidence import finding, make_evidence, write_evidence  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402
from Shared.tools.build_search_index import read_questions  # noqa: E402

PRODUCER = "verify_search_index"
VERSION = "1.1.0"
EXAMPLES = 20


def verify(index_path: Path, manifest_path: Path, library_dirs: list[Path]) -> dict:
    """The two verdicts, as {SEARCH_MEMBERSHIP: (outcome, findings), SEARCH_RETRIEVABILITY: (outcome, findings), digest, stale}."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_bytes = contract.normalise_text(index_path.read_bytes())
    index_digest = "sha256:" + hashlib.sha256(index_bytes).hexdigest()

    canonical_ids = {q["id"] for _, q in read_questions(library_dirs) if q.get("extensions", {}).get("search_visibility") != "EXCLUDED"}
    indexed = set(manifest.get("canonical_ids", []))
    missing, phantom = sorted(canonical_ids - indexed), sorted(indexed - canonical_ids)
    stale = contract.digest_roots(library_dirs) != manifest.get("canonical_snapshot_digest")

    membership: list[dict] = []
    if missing:
        membership.append(finding("MISSING_FROM_INDEX", "S1", missing[0], f"{len(missing)} canonical question(s) are not in the index", evidence={"ids": missing[:EXAMPLES]}))
    if phantom:
        membership.append(finding("PHANTOM_IN_INDEX", "S1", phantom[0], f"{len(phantom)} indexed id(s) are not canonical questions", evidence={"ids": phantom[:EXAMPLES]}))
    if stale:
        membership.append(finding("STALE_INDEX", "S1", "search", "the index was built from different canonical content than the library holds now; rebuild it with build_search_index.py"))
    retrievability: list[dict] = []
    if index_digest != manifest.get("index_digest"):
        retrievability.append(finding("INDEX_DIGEST_MISMATCH", "S1", "search", "the index file is not the one its manifest describes"))
    return {"SEARCH_MEMBERSHIP": membership, "SEARCH_RETRIEVABILITY": retrievability, "digest": index_digest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--index", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--library-dirs", nargs="+", required=True)
    parser.add_argument("--evidence-dir", default="build/assurance/evidence")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args(argv)

    index_path, manifest_path = Path(args.index), Path(args.manifest)
    if not index_path.is_file() or not manifest_path.is_file():
        print("Missing index or manifest file.")
        return 1 if args.enforce else 0
    try:
        result = verify(index_path, manifest_path, [Path(d) for d in args.library_dirs if Path(d).exists()])
    except ContractError as exc:                          # a library file that does not parse: nothing can be said about membership
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    outcomes = {}
    for assurance_type in ("SEARCH_MEMBERSHIP", "SEARCH_RETRIEVABILITY"):
        found = result[assurance_type]
        outcomes[assurance_type] = "FAIL" if found else "PASS"
        record = make_evidence(assurance_type, "PROJECTION", "search", outcomes[assurance_type], PRODUCER, VERSION, findings=found,
                               subject_digest=result["digest"], configuration={"library_dirs": sorted(Path(d).as_posix() for d in args.library_dirs)})
        write_evidence(record, REPO / args.evidence_dir / f"{record['evidence_id']}.json")      # a relative directory is the repository's; an absolute one is itself
    print("=== Search Index Verification ===")
    for assurance_type, outcome in outcomes.items():
        print(f"{assurance_type}: {outcome}")
        for f in result[assurance_type]:
            print(f"  {f['code']}: {f['message']}")
    return 1 if (args.enforce and "FAIL" in outcomes.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
