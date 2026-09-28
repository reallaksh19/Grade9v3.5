#!/usr/bin/env python3
"""Render candidate exemplars with the sole learner renderer.

The records and manifest under each golden unit are pinned excerpts. Generated
pages are local study artifacts; a golden's CANDIDATE label never accepts or
publishes a product.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import render_core  # noqa: E402

GOLDEN = REPO / "golden" / "units"


def candidates() -> list[Path]:
    return sorted(GOLDEN.glob("*/manifest.json"))


def build_one(manifest: Path, check: bool = False) -> dict:
    pages, gaps, digest = render_core.build(manifest, mode="PAGES")
    if gaps:
        raise ValueError(f"{manifest.parent.name}: {len(gaps)} renderer gap(s)")
    if not check:
        out = manifest.parent / "rendered"
        render_core.main(["build", "--manifest", str(manifest), "--out", str(out), "--mode", "PAGES"])
        receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
        if receipt["digest"] != digest:
            raise ValueError(f"{manifest.parent.name}: receipt digest changed during build")
    return {"id": manifest.parent.name, "digest": digest, "pages": len(pages), "gaps": len(gaps)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--id", help="render one G-ID; default is every candidate")
    parser.add_argument("--check", action="store_true", help="render in memory and check for gaps")
    args = parser.parse_args(argv)
    manifests = [GOLDEN / args.id / "manifest.json"] if args.id else candidates()
    if not manifests or any(not p.is_file() for p in manifests):
        parser.error("no matching golden manifest")
    for manifest in manifests:
        row = build_one(manifest, args.check)
        print(f"{row['id']}: {row['digest']} · {row['pages']} pages · {row['gaps']} gaps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
