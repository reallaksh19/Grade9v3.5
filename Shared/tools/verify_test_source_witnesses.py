#!/usr/bin/env python3
"""Authenticate pinned GitHub witness pointers for the bounded #68 pilot.

This verifies comment existence/identity, author and minimum recorded context,
not official PDF wording or independent academic acceptance. Network failure
is an explicit failed gate, never a synthetic source-verification PASS.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_source_custody  # noqa: E402
ROOT = "https://github.com/reallaksh19/Grade9v3.5"


def evidence_refs(repo: Path) -> set[str]:
    """Walk the declared overlays; validate their shape before authentication."""
    test_source_custody.reconcile(repo)
    refs: set[str] = set()

    def collect(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "verification_evidence_ref":
                    refs.add(item)
                else:
                    collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)

    for path in sorted((repo / "TEST/evidence/source-intake").glob("*.custody.v1.json")):
        collect(json.loads(path.read_text(encoding="utf-8")))
    return refs


def verify_payload(ref: str, payload: object) -> None:
    expected = test_source_custody.KNOWN_WITNESSES.get(ref)
    if not expected or not isinstance(payload, dict):
        raise ValueError(f"{ref}: unknown or invalid GitHub witness")
    expected_url = f"{ROOT}/issues/{expected['issue']}#issuecomment-{expected['id']}"
    if (payload.get("id") != expected["id"]
            or payload.get("html_url") != expected_url
            or (payload.get("user") or {}).get("login") != "reallaksh19"):
        raise ValueError(f"{ref}: GitHub witness identity/author mismatch")
    body = payload.get("body")
    if not isinstance(body, str) or any(fragment not in body for fragment in expected["fragments"]):
        raise ValueError(f"{ref}: required witness context absent")
    # An authenticated comment is still a review *claim*, not an official PDF oracle.


def verify(repo: Path = REPO, token: str | None = None) -> int:
    token = token or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN required for authenticated pilot witness check")
    refs = evidence_refs(repo)
    if not refs:
        raise ValueError("no source-custody witnesses: cannot claim pilot attestation")
    for ref in sorted(refs):
        expected = test_source_custody.KNOWN_WITNESSES[ref]
        request = Request(
            f"https://api.github.com/repos/reallaksh19/Grade9v3.5/issues/comments/{expected['id']}",
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "User-Agent": "Grade9v3-SourceWitnessAudit"},
        )
        with urlopen(request, timeout=20) as response:
            verify_payload(ref, json.load(response))
    return len(refs)


if __name__ == "__main__":
    count = verify()
    print(f"authenticated {count} known GitHub witness pointer(s); NCERT PDF content and independent review still require separate verification")
