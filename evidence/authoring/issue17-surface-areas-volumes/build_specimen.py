#!/usr/bin/env python3
"""Build the Issue #17 cold-run specimen from the validated Issue #10 authoring path.

Issue #10 proved the repository render path. This wrapper deliberately reuses that path while
changing only cold-run identity, owner purpose, evidence location and the academic answer policy
that Issue #17 independently established (exact pi unless an approximation is stated).
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "issue10-surface-areas-volumes" / "build_specimen.py"

source = SOURCE.read_text(encoding="utf-8")
owner_condition_projection = '''row["conditions"] = {
        "Q1": [],
        "Q2": [],
        "Q3": ["The bucket is open at the top.", "Ignore the thickness of the metal sheet."],
        "Q4": ["The base of the tent is open."],
        "Q5": [],
        "Q6": ["The cone and hemisphere have the same radius, 3.5 cm.", "The circular face where the cone and hemisphere join is not exposed."],
        "Q7": ["The vessel is open at the top.", "Paint the entire outer curved surface and the outside of the circular base.", "The inside is not painted."],
        "Q8": ["The tank is filled to 75% of its total capacity."],
        "Q9": ["No metal is lost during melting and recasting."],
        "Q10": ["The cone and cylinder have the same base radius and the same height."],
    }[qid]
    if not row["conditions"]:
        row["extensions"].setdefault("grade9v3:component_waivers", {})["CONDITIONS"] = "The owner question states no separate constraint or assumption beyond its givens and requested quantity."'''
replacements = [
    ("issue10-surface-areas-volumes", "issue17-surface-areas-volumes"),
    ("Issue #10", "Issue #17"),
    ("ISSUE10", "ISSUE17"),
    ('"issue": 10', '"issue": 17'),
    ('"purpose": "REVISION"', '"purpose": "COMPETITION"'),
    ('"depth": ["REVISION"]', '"depth": ["COMPETITION"]'),
    ("revision learner", "competition learner"),
    ('row["conditions"] = ["Use π = 22/7 wherever numerical approximation is required unless the question states otherwise."]', owner_condition_projection),
    ('row["extensions"]["grade9v3:component_waivers"] = {"REPRESENTATION": evidence["representation"]["reason"]}', 'row["extensions"].setdefault("grade9v3:component_waivers", {})["REPRESENTATION"] = evidence["representation"]["reason"]'),
    ("880 cm²", "280π cm²"),
    ("Evaluate with r=7 cm, h=18 cm and π=22/7.", "Evaluate with r=7 cm and h=18 cm; keep π exact unless an approximation is explicitly chosen."),
    ("946 cm²", "301π cm²"),
    ("550 m²", "175π m²"),
    ("693 cm²", "220.5π cm²"),
    ("214.5 cm²", "68.25π cm²"),
    ("πr²=38.5 cm²", "πr²=12.25π cm²"),
    ("1254 cm²", "399π cm²"),
]
for old, new in replacements:
    source = source.replace(old, new)

# Execute the proven builder with this file as __file__, so HERE/OUT resolve to Issue #17.
namespace = {"__name__": "__main__", "__file__": str(Path(__file__).resolve())}
exec(compile(source, str(SOURCE), "exec"), namespace, namespace)
