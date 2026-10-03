#!/usr/bin/env python3
"""Require a PASS Chromium receipt for an interactive HTML artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED_CHECKS = (
    "runtime_smoke",
    "page_errors",
    "console_errors",
    "external_requests",
    "horizontal_overflow",
    "touch_targets",
    "accessibility_baseline",
    "keyboard_focus",
)


class InteractiveChromiumGateError(ValueError):
    pass


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def validate(html: Path, receipt: dict) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema") != "interactive-chromium-audit/v1":
        errors.append("RECEIPT_SCHEMA_INVALID")
    if receipt.get("engine") != "chromium":
        errors.append("CHROMIUM_REQUIRED")
    if receipt.get("html_sha256") != sha256(html):
        errors.append("HTML_DIGEST_MISMATCH")
    if receipt.get("status") != "PASS":
        errors.append("CHROMIUM_AUDIT_NOT_PASS")
    checks = receipt.get("checks") or {}
    for check in REQUIRED_CHECKS:
        if (checks.get(check) or {}).get("verdict") != "PASS":
            errors.append("CHECK_NOT_PASS:" + check)
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.html.is_file():
        raise SystemExit("interactive HTML missing: " + str(args.html))
    if not args.receipt.is_file():
        raise SystemExit("Chromium receipt missing: " + str(args.receipt))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    errors = validate(args.html, receipt)
    payload = {
        "schema": "interactive-chromium-gate/v1",
        "html": str(args.html),
        "receipt": str(args.receipt),
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
