#!/usr/bin/env python3
"""Finalize the Issue #17 specimen through the proven Issue #10 projection logic."""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "issue10-surface-areas-volumes" / "finalize_specimen.py"
source = SOURCE.read_text(encoding="utf-8")
for old, new in [
    ("Issue #10", "Issue #17"),
    ("issue10-surface-areas-volumes", "issue17-surface-areas-volumes"),
    ("revision learner", "competition learner"),
]:
    source = source.replace(old, new)
namespace = {"__name__": "__main__", "__file__": str(Path(__file__).resolve())}
exec(compile(source, str(SOURCE), "exec"), namespace, namespace)
