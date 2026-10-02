"""The ratchet for what was already wrong when a check arrived: a finding that is in the baseline is known, one that is not is new, and only new ones fail a run.

The baseline is written by `assurance_run.py --write-baseline` and never by hand. It names findings, not counts and not "this package fails": a second collision
in a package that already has one is a new finding. It does not make anything pass: the evidence still says FAIL, and a product with a FAIL is not eligible. It
only lets a check that finds old debt be switched on without a flag day, and it can only shrink.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from Shared.assurance import contract

BASELINE = contract.HERE / "baseline.v1.json"
SEVERE = ("S0", "S1")


def key(evidence: dict, found: dict) -> str:
    s = evidence["subject"]
    return f"{evidence['assurance_type']}|{s['kind']}:{s['id']}|{found['code']}|{found['subject']}"


def keys(evidence: Iterable[dict]) -> list[str]:
    """The keys of the severe findings in the FAIL evidence about canonical subjects."""
    return sorted({key(e, f) for e in evidence if e["outcome"] == "FAIL" and e["subject"]["kind"] == "CANONICAL_RECORD"
                   for f in e["findings"] if f["severity"] in SEVERE})


def load(path: Path = BASELINE) -> set[str]:
    if not Path(path).exists():
        return set()
    return set(json.loads(Path(path).read_text(encoding="utf-8"))["findings"])


def write(found: list[str], path: Path = BASELINE) -> None:
    contract.write_json(Path(path), {"schema": "assurance-baseline/v1",
                                     "note": "Written by Shared/tools/assurance_run.py --write-baseline. Findings that were already there when the check arrived. "
                                             "A finding in this list does not fail a run; it is still a FAIL in the evidence, and a product with one is not eligible.",
                                     "findings": found})


def new_findings(evidence: Iterable[dict], baseline: set[str]) -> list[str]:
    return [k for k in keys(evidence) if k not in baseline]


def fixed(evidence: Iterable[dict], baseline: set[str]) -> list[str]:
    """Baseline entries no longer found: the baseline can be tightened."""
    return sorted(baseline - set(keys(evidence)))
