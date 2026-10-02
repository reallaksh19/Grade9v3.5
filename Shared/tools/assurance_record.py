#!/usr/bin/env python3
"""Evidence records: the implementation is Shared/assurance/evidence.py; this module keeps the path the tools import it from."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.assurance.evidence import (  # noqa: E402,F401
    ALIASES, OUTCOMES, SEVERITIES, SUBJECT_KINDS, evidence_id, finding, load_evidence, load_policy, make_evidence, subject_kind,
    validate_evidence, worst, write_evidence,
)
