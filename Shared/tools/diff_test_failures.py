#!/usr/bin/env python3
"""Differential test baseline comparison."""

import sys
import json
import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-failures", type=str, required=True)
    parser.add_argument("--head-failures", type=str, required=True)
    parser.add_argument("--run-tests", type=str)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    base_path = Path(args.base_failures)
    head_path = Path(args.head_failures)

    base = []
    if base_path.exists():
        with base_path.open("r", encoding="utf-8") as f:
            base = json.load(f)

    head = []
    if head_path.exists():
        with head_path.open("r", encoding="utf-8") as f:
            head = json.load(f)
            
    base_set = set(base)
    head_set = set(head)
    
    new_failures = head_set - base_set
    fixed = base_set - head_set
    
    print(f"New Failures: {list(new_failures)}")
    print(f"Fixed: {list(fixed)}")
    
    if args.enforce and new_failures:
        sys.exit(1)

if __name__ == "__main__":
    main()
