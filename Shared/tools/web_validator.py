#!/usr/bin/env python3
"""Independently validate WebResolutionPlan receipts and their selected page adapters."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import load
from Shared.tools import (
    build_core_learning_data,
    build_explore_page,
    build_interactive_page,
    web_resolver,
)


def _finding(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _semantic_segments(plan: dict) -> list[dict]:
    # Cache receipts may change when this very run persists a projection. They
    # are provenance, not Core authority or a reason to invalidate the page.
    return [
        {key: value for key, value in segment.items()
         if key not in {"remembered_artifact_ref", "remembered_reuse"}}
        for segment in plan.get("experience_segments") or []
    ]


def validate(
    request: dict,
    plan: dict,
    *,
    route_artifact: dict | None = None,
    repo: Path = REPO,
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    fresh = web_resolver.resolve(request, route_artifact=route_artifact, repo=repo)
    compare_keys = (
        "subject", "target", "availability",
        "artifact_buildable", "request_satisfaction", "build_action", "pins",
        "target_route", "fallback_used", "packaging_mode",
    )
    if (
        any(plan.get(key) != fresh.get(key) for key in compare_keys)
        or _semantic_segments(plan) != _semantic_segments(fresh)
    ):
        findings.append(_finding(
            "WEB_RESOLUTION_STALE_OR_DIVERGENT",
            "Independent canonical/Atlas/provider resolution no longer matches the supplied receipt.",
        ))

    adapter = plan.get("build_action")
    if adapter == "CORE_PAGE_ADAPTER":
        core_payload = build_core_learning_data.build()
        by_id = {row["id"]: row for row in core_payload.get("core_projections", [])}
        segments = plan.get("experience_segments") or []
        if len(segments) != 1 or not segments[0].get("projection_ref"):
            findings.append(_finding("WEB_CORE_ADAPTER_INPUT_INVALID", "Core adapter requires one projection ref."))
        else:
            row = by_id.get(segments[0]["projection_ref"])
            if row is None:
                findings.append(_finding("WEB_CORE_PROJECTION_STALE", "Resolved Core projection no longer exists."))
            else:
                try:
                    package = build_interactive_page.compile_page_package(row)
                except Exception as exc:
                    findings.append(_finding("WEB_CORE_PACKAGE_INVALID", str(exc)))
                else:
                    blueprint = package.get("blueprint") or {}
                    if (
                        plan.get("packaging_mode") in {"OFFLINE_DIRECTORY", "SINGLE_FILE"}
                        and (package.get("representation") or {}).get("mount_mode") == "LEGACY_IFRAME"
                    ):
                        findings.append(_finding(
                            "WEB_OFFLINE_LEGACY_IFRAME_FORBIDDEN",
                            "Offline Core delivery cannot depend on a locator iframe.",
                        ))
                    touch = blueprint.get("touch_policy") or {}
                    if touch.get("minimum_target_css_px", 0) < 48:
                        findings.append(_finding(
                            "WEB_TOUCH_TARGET_CONTRACT_WEAK",
                            "Core blueprint minimum touch target is below the shared product minimum.",
                        ))
                    if not blueprint.get("shell_ref"):
                        findings.append(_finding("WEB_SHELL_REF_MISSING", "Core page has no shell ref."))
    elif adapter == "EXPLORE_PAGE_ADAPTER":
        try:
            package = build_explore_page.compile_page_package(plan, repo)
        except Exception as exc:
            findings.append(_finding("WEB_EXPLORE_PACKAGE_INVALID", str(exc)))
        else:
            if package.get("mount_mode") == "LEGACY_IFRAME":
                policy = (package.get("profile") or {}).get("representation_policy") or {}
                if policy.get("legacy_iframe") != "MIGRATION_ONLY":
                    findings.append(_finding(
                        "WEB_EXPLORE_IFRAME_AUTHORITY_INVALID",
                        "Legacy iframe mount is not explicitly migration-only.",
                    ))
    elif adapter == "COMPOSE_SEGMENTS":
        if len(plan.get("experience_segments") or []) < 2:
            findings.append(_finding(
                "WEB_SEGMENT_COMPOSITION_INVALID",
                "Composite build action requires multiple independently resolved segments.",
            ))
        else:
            findings.append(_finding(
                "WEB_SEGMENT_COMPOSITION_NOT_IMPLEMENTED",
                "A composite page adapter must exist before a multi-segment plan can be released.",
            ))
    elif adapter == "HOLD":
        pass
    else:
        findings.append(_finding("WEB_BUILD_ACTION_UNKNOWN", str(adapter)))

    passed = not findings
    return {
        "passed": passed,
        "release_ready": (
            passed
            and plan.get("artifact_buildable") is True
            and plan.get("request_satisfaction") in {"FULL", "DEGRADED_ACCEPTABLE"}
            and plan.get("build_action") != "HOLD"
        ),
        "request_id": plan.get("request_id"),
        "request_satisfaction": plan.get("request_satisfaction"),
        "findings": findings,
        "gates": {
            "authority_integrity": "PASS" if passed else "FAIL",
            "request_satisfaction": plan.get("request_satisfaction"),
            "adapter_integrity": "PASS" if passed else "FAIL",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--route-artifact", type=Path)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = validate(
        load(args.request),
        load(args.plan),
        route_artifact=load(args.route_artifact) if args.route_artifact else None,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["release_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
