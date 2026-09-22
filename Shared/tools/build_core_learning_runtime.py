#!/usr/bin/env python3
"""Generate the public Core learner runtime from Shared/workbench sources.

The Shared modules remain the implementation authority. Public copies exist only so a
static/offline learner page can import the runtime without shipping the whole repository.
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "Shared" / "workbench"
OUT = REPO / "public" / "js" / "core-learning"

MODULES = (
    "runtime.mjs",
    "semantic-workbench.mjs",
    "core-learning-page.mjs",
    "core-learning-host.mjs",
)


def render() -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    for name in MODULES:
        source = SOURCE / name
        if not source.is_file():
            raise FileNotFoundError(f"missing Core learner runtime source: {source.relative_to(REPO)}")
        rendered[(OUT / name).relative_to(REPO).as_posix()] = source.read_bytes()
    return rendered


def write() -> dict[str, bytes]:
    rendered = render()
    for relative, content in rendered.items():
        path = REPO / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify the public Core learner runtime")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render()
    if args.check:
        stale = [
            relative
            for relative, content in rendered.items()
            if not (REPO / relative).is_file() or (REPO / relative).read_bytes() != content
        ]
        for relative in stale:
            print(f"generated file is stale: {relative}")
        return 1 if stale else 0

    write()
    for relative in sorted(rendered):
        print(f"wrote {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
