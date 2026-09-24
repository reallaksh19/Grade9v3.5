"""Phase-5 Core1-family learner-delivery integrity report.

This layer checks that the semantic progression already established by Phases 1-4
survives compiler-backed projection and the shared learner host. It does not invent
academic truth or reinterpret local construction debt as delivery debt.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from Shared.library import core1_progression
from Shared.tools import build_core_learning_data, build_core_learning_host


def _finding(code: str, detail: str, ref: str | None = None) -> dict:
    row = {"code": code, "detail": detail}
    if ref:
        row["ref"] = ref
    return row


def _forbidden_state_keys(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            lowered = str(key).lower()
            if any(token in lowered for token in ("mastery", "proficiency", "readiness")):
                found.append(child_path)
            found.extend(_forbidden_state_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_forbidden_state_keys(child, f"{path}[{index}]"))
    return found


def _hosts_equivalent() -> bool:
    rendered = {
        path: content.decode("utf-8")
        for path, content in build_core_learning_host.render().items()
    }
    public = rendered["public/core-learning/index.html"]
    standalone = rendered["standalone/core-learning/index.html"]
    normalized_public = (
        public
        .replace("./data.js", "__DATA__")
        .replace("../js/core-learning", "__RUNTIME__")
    )
    normalized_standalone = (
        standalone
        .replace("../../public/core-learning/data.js", "__DATA__")
        .replace("../../public/js/core-learning", "__RUNTIME__")
    )
    return normalized_public == normalized_standalone


def audit(repo: Path) -> dict:
    progression = core1_progression.audit(repo)
    payload = build_core_learning_data.build()
    rows = payload.get("core_projections") or []

    by_key = {
        (row.get("subject"), row.get("projection", {}).get("core"), row.get("source_ref")): row
        for row in rows
        if isinstance(row, dict)
    }
    findings: list[dict] = []

    expected_core1 = {
        (row["subject"], row["bucket_ref"])
        for row in progression["buckets"]
        if row["core1_orientation_available"]
    }
    expected_study = {
        (row["subject"], row["microtopic_ref"])
        for row in progression["microtopics"]
        if row["routing_state"] != "UNROUTED"
    }

    for subject, bucket_ref in sorted(expected_core1):
        row = by_key.get((subject, "CORE1", bucket_ref))
        if row is None:
            findings.append(_finding(
                "CORE1_DELIVERY_MISSING",
                "A Phase-4 orientable bucket has no Core1 learner projection.",
                bucket_ref,
            ))
            continue
        projection = row["projection"]
        if (
            not isinstance(projection.get("orientation"), dict)
            or projection.get("concept") is not None
            or projection.get("application") is not None
            or projection.get("presentation", {}).get("attempt_before_reveal") is not False
        ):
            findings.append(_finding(
                "CORE1_DELIVERY_POLICY_INVALID",
                "Core1 learner delivery is not a pure non-attempt orientation projection.",
                bucket_ref,
            ))

    for subject, microtopic_ref in sorted(expected_study):
        for core in ("CORE1A", "CORE1B"):
            row = by_key.get((subject, core, microtopic_ref))
            if row is None:
                findings.append(_finding(
                    f"{core}_DELIVERY_MISSING",
                    "A routed study concept has no learner projection for this Core.",
                    microtopic_ref,
                ))
                continue
            projection = row["projection"]
            concept = projection.get("concept") or {}
            if concept.get("microtopic_ref") != microtopic_ref:
                findings.append(_finding(
                    f"{core}_CONCEPT_IDENTITY_DRIFT",
                    "The learner projection no longer points at the canonical microtopic.",
                    microtopic_ref,
                ))
            if projection.get("application") is not None:
                findings.append(_finding(
                    f"{core}_APPLICATION_COUPLING",
                    "Concept acquisition delivery must not depend on a practice application.",
                    microtopic_ref,
                ))
            presentation = projection.get("presentation") or {}
            if core == "CORE1A" and (
                presentation.get("attempt_before_reveal") is not False
                or presentation.get("show_full_construction") is not True
            ):
                findings.append(_finding(
                    "CORE1A_REVEAL_POLICY_INVALID",
                    "Core1A must expose the completed construction without an attempt gate.",
                    microtopic_ref,
                ))
            if core == "CORE1B":
                if (
                    presentation.get("attempt_before_reveal") is not True
                    or presentation.get("show_full_construction") is not False
                ):
                    findings.append(_finding(
                        "CORE1B_REVEAL_POLICY_INVALID",
                        "Core1B must require an attempt before reconstruction reveal.",
                        microtopic_ref,
                    ))
                elicitation = concept.get("elicitation")
                if not isinstance(elicitation, dict):
                    findings.append(_finding(
                        "CORE1B_ELICITATION_DROPPED",
                        "The authored self-tutor cycle is absent from learner delivery.",
                        microtopic_ref,
                    ))

    if not _hosts_equivalent():
        findings.append(_finding(
            "STATIC_STANDALONE_ACADEMIC_DIVERGENCE",
            "Public and standalone learner hosts no longer share one academic template.",
        ))

    forbidden = sorted(set(_forbidden_state_keys([
        row.get("projection") for row in rows if isinstance(row, dict)
    ])))
    for path in forbidden:
        findings.append(_finding(
            "LEARNER_MASTERY_STATE_FORBIDDEN",
            "Learner projection introduced mastery/proficiency/readiness state.",
            path,
        ))

    counts: dict[str, int] = {}
    for row in rows:
        core = (row.get("projection") or {}).get("core")
        if isinstance(core, str):
            counts[core] = counts.get(core, 0) + 1

    finding_counts: dict[str, int] = {}
    for finding in findings:
        finding_counts[finding["code"]] = finding_counts.get(finding["code"], 0) + 1

    return {
        "schema_version": "1.0.0",
        "audit": "CORE1_FAMILY_LEARNER_DELIVERY",
        "semantics": {
            "source": "fresh compiler-backed provider build",
            "core1": "orientation map",
            "core1a": "completed conceptual construction",
            "core1b": "attempt-first reconstruction of the same canonical concept",
            "completion_is_mastery": False,
            "local_phase_debt_is_not_delivery_debt": True,
        },
        "summary": {
            "projection_count": len(rows),
            "projection_counts_by_core": dict(sorted(counts.items())),
            "expected_core1_buckets": len(expected_core1),
            "expected_routed_study_microtopics": len(expected_study),
            "delivery_findings": len(findings),
            "finding_counts": dict(sorted(finding_counts.items())),
            "upstream_cross_progression_gap_microtopics": (
                progression["summary"]["cross_progression_gap_microtopics"]
            ),
        },
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--write-report")
    parser.add_argument("--check-report")
    args = parser.parse_args()

    report = audit(Path(args.repo).resolve())
    if args.write_report:
        Path(args.write_report).write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.check_report:
        committed = json.loads(Path(args.check_report).read_text(encoding="utf-8"))
        passed = committed == report and not report["findings"]
        print(json.dumps({
            "passed": passed,
            "report_matches": committed == report,
            "findings": report["findings"],
        }, indent=2))
        return 0 if passed else 1

    if not args.write_report:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
