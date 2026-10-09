#!/usr/bin/env python3
"""Read-only repo-wide six-Core/QRT readiness inventory.

Combines existing *authoritative* audits, never replaces their rules or issues
academic, source, learner, rights, print, or release approval. Issue #313.
Usage: python Shared/tools/repo_core_readiness.py [--out /tmp/readiness.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.library import core1_progression, core1b_reconstruction, core_progression
from Shared.tools import core2a_inventory, core2b_inventory, question_review_matrix as qrt


def _head(repo: Path) -> str | None:
    process = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True,
        check=False,
    )
    return process.stdout.strip() if process.returncode == 0 else None


def project(
    qrt_templates: list[dict], qrt_problems: list[str],
    c1: dict, c1b: dict, c2: dict, c2a: dict, c2b: dict,
    *, head: str | None,
) -> dict:
    """Project six role denominators without converting counts into approval."""
    s1, sb = c1["summary"], c1b["summary"]
    s2, sa, st = c2["summary"], c2a["summary"], c2b["summary"]
    asks = list(qrt.ASKS)
    ids = [row["template_id"] for row in qrt_templates]
    qrt_integrity = (
        len(qrt_templates) == len(qrt.DEMANDS) * len(qrt.BANDS) == 28
        and len(ids) == len(set(ids)) and not qrt_problems
    )
    return {
        "schema": "repo-six-core-qrt-readiness/v1",
        "head_sha": head,
        "scope": "CURRENT_CANONICAL_LIBRARY_AND_EXISTING_QRT_CONTRACT",
        "authority": "READ_ONLY_COMPOSITION_OF_EXISTING_AUDITS",
        "qrt": {
            "primary_demand_count": len(qrt.DEMANDS),
            "difficulty_band_count": len(qrt.BANDS),
            "base_template_count": len(qrt_templates),
            "semantic_ask_ids": asks,
            "mechanical_contract_valid": qrt_integrity,
            "contract_problems": qrt_problems,
            "accepted_cells": "NOT_EVALUATED",
            "independent_exact_render_reviews": "NOT_EVALUATED",
        },
        "core1_continuity": {
            "buckets": s1["bucket_count"],
            "orientation_buckets": s1["core1_orientable_buckets"],
            "canonical_microtopics": s1["microtopic_count"],
            "cross_progression_coherent": s1["cross_progression_coherent_microtopics"],
            "cross_progression_gap": s1["cross_progression_gap_microtopics"],
            "unrouted": s1["unrouted_microtopics"],
            "core1a_local_construction_debt": s1["phase2_local_debt_microtopics"],
            "core1b_routed": sb["routed_microtopics"],
            "core1b_structurally_complete": sb["structured_routed_microtopics"],
            "core1b_coverage_mismatches": sb["coverage_mismatches"],
            "cross_findings": [
                {"microtopic_ref": row["microtopic_ref"], "codes": row["cross_progression_codes"]}
                for row in c1["microtopics"] if row["cross_progression_codes"]
            ],
            "academic_authorship_or_learner_mastery": "NOT_EVALUATED",
        },
        "core2_progression": {
            "practice_families": s2["practice_families"],
            "source_demand_evidenced_families": s2["source_demand_evidenced_families"],
            "ordinary_core2_custody_anchors": s2["ordinary_core2_anchors"],
            "competitive_bank_evidence_anchors": s2["competitive_bank_accepted_anchors_scanned"],
            "core2a_questions": sa["core2a_questions"],
            "core2a_structured": sa["structured"],
            "core2a_migration_required": sa["migration_required"],
            "core2b_questions": st["core2b_questions"],
            "core2b_structured_protected": st["structured_protected"],
            "core2b_current_debt_items": st["debt_items"],
            "core2b_debt_reasons": st["debt_reasons"],
            "cross_findings": [
                {"point": f["point"], "where": f["where"]}
                for f in c2["findings"]
            ],
            "learner_transfer_validity": "NOT_EVALUATED",
        },
        "release": {
            "integrated_six_role_journey": "NOT_EVALUATED",
            "source_rights": "NOT_EVALUATED",
            "human_accessibility": "NOT_EVALUATED",
            "learner_trial": "NOT_EVALUATED",
            "academic_acceptance": "NOT_EVALUATED",
            "owner_publication_authorization": "NOT_EVALUATED",
        },
        "gate_semantics": {
            "template_count_is_accepted_qrt_coverage": False,
            "core1b_structural_parity_is_student_mastery": False,
            "competitive_bank_evidence_is_ordinary_core2_custody": False,
            "core2b_label_is_proof_of_changed_decision": False,
            "synthetic_browser_test_is_human_accessibility": False,
        },
    }


def snapshot(repo: Path = REPO) -> dict:
    """Recompute the live audit results; do not trust copied historical counts."""
    # QRT's compiler uses the existing authoritative source + vocabulary.
    templates = qrt.generated_payload(qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH))["templates"]
    return project(
        templates, qrt.check_paths(),
        core1_progression.audit(repo), core1b_reconstruction.audit(repo),
        core_progression.audit(repo), core2a_inventory.inventory(repo),
        core2b_inventory.inventory(repo), head=_head(repo),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="Write a read-only JSON snapshot to this destination")
    args = parser.parse_args(argv)
    result = snapshot()
    data = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data, encoding="utf-8")
    print(data, end="")
    # Only existing QRT source/projection corruption is a mechanical failure
    # of this read-only collector. Existing progression debt is reported, not waived.
    return 0 if result["qrt"]["mechanical_contract_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
