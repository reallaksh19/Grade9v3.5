#!/usr/bin/env python3
"""M1: move each existing product title into its sole library package."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFESTS = REPO / "products"


def check() -> list[str]:
    problems = []
    for manifest_path in sorted(MANIFESTS.glob("*/*.manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if "title" in manifest:
            problems.append(f"{manifest_path}: title still overrides the package")
        for ref in manifest["package_refs"]:
            package = json.loads((REPO / ref).read_text(encoding="utf-8"))
            if not package.get("title") or len(package["title"]) < 3:
                problems.append(f"{ref}: no learner title")
    return problems


def write() -> None:
    for manifest_path in sorted(MANIFESTS.glob("*/*.manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        title = manifest.pop("title")
        if len(manifest["package_refs"]) != 1:
            raise ValueError(f"{manifest_path}: expected one package for M1")
        package_path = REPO / manifest["package_refs"][0]
        raw = package_path.read_text(encoding="utf-8")
        if "title" in json.loads(raw):
            raise ValueError(f"{package_path}: already has a title")
        pattern = r'("package_id":\s*"[^"]+",\r?\n)'
        changed, count = re.subn(pattern, lambda m: m.group(1) + '  "title": '
                                 + json.dumps(title, ensure_ascii=False) + ",\n", raw, count=1)
        if count != 1:
            raise ValueError(f"{package_path}: package_id line not found")
        package_path.write_text(changed, encoding="utf-8", newline="\n")
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        write()
    problems = check()
    if problems:
        print("\n".join(problems))
        return 1
    print("M1: 21 package titles; no manifest title overrides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
