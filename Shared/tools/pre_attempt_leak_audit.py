#!/usr/bin/env python3
"""Audit transitive pre-attempt resources for protected-answer leakage."""
from __future__ import annotations

import argparse
import html
import json
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def _normalize_for_match(value: Any) -> str:
    text = html.unescape(str(value))
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split()).casefold()


def _read_asset_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".svg":
        return raw
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return raw
    visible: list[str] = []
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag in {"title", "desc", "text"}:
            value = " ".join("".join(element.itertext()).split())
            if value:
                visible.append(value)
        aria_label = element.attrib.get("aria-label")
        if aria_label:
            visible.append(aria_label)
    return "\n".join(visible)


def _protected_tokens(question: dict[str, Any]) -> list[str]:
    rows = ((question.get("extensions") or {}).get("grade9v3:calculation_audit") or [])
    tokens: set[str] = set()
    for row in rows:
        if not row.get("protected_result"):
            continue
        value = row.get("expected")
        unit = str(row.get("unit") or "").strip()
        if isinstance(value, (int, float)):
            shown = str(int(value)) if float(value).is_integer() else str(value)
            if unit and "coefficient" not in unit and unit != "ratio":
                tokens.add(f"{shown} {unit}")
            elif abs(float(value)) >= 10:
                tokens.add(shown)
    summary = str((question.get("answer") or {}).get("summary") or "").strip()
    if summary:
        tokens.add(summary)
    return sorted(tokens, key=len, reverse=True)


def audit(bank: dict[str, Any], package: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    questions = {q["id"]: q for q in bank.get("questions") or []}
    representations = {r["id"]: r for r in package.get("representations") or []}
    teaching_steps = {
        step["id"]: step
        for microtopic in package.get("microtopics") or []
        for step in microtopic.get("teaching_path") or []
        if isinstance(step, dict) and step.get("id")
    }

    items = []
    for qid, question in questions.items():
        tokens = _protected_tokens(question)
        resources: list[dict[str, Any]] = []

        for index, hint in enumerate(question.get("scaffolds") or []):
            resources.append({
                "kind": "CORE2_SCAFFOLD",
                "ref": f"{qid}.scaffolds[{index}]",
                "text": json.dumps(hint, ensure_ascii=False),
            })

        analysis = (question.get("extensions") or {}).get("grade9v3:analysis") or {}
        for index, condition in enumerate(question.get("conditions") or []):
            resources.append({
                "kind": "CORE2_CONDITION",
                "ref": f"{qid}.conditions[{index}]",
                "text": str(condition),
            })
        resources.append({
            "kind": "CORE2_DIFFICULTY_WHY",
            "ref": f"{qid}.extensions.grade9v3:analysis.difficulty.basis",
            "text": str((analysis.get("difficulty") or {}).get("basis") or ""),
        })
        resources.append({
            "kind": "CORE2_TRAP",
            "ref": f"{qid}.extensions.grade9v3:analysis.common_wrong_route",
            "text": str(analysis.get("common_wrong_route") or ""),
        })
        resources.append({
            "kind": "CORE2_BOTTLENECK",
            "ref": f"{qid}.extensions.grade9v3:analysis.review_bottleneck",
            "text": str(analysis.get("review_bottleneck") or ""),
        })
        resources.append({
            "kind": "CORE2_ROUTE_TO_CRUX",
            "ref": f"{qid}.extensions.grade9v3:analysis.review_route_to_crux",
            "text": str(analysis.get("review_route_to_crux") or ""),
        })

        for microtopic in package.get("microtopics") or []:
            for unit in microtopic.get("construction_units") or []:
                if qid not in (unit.get("crux_question_refs") or []):
                    continue
                resources.append({
                    "kind": "CORE1A_UNIT_DECISION",
                    "ref": unit["id"],
                    "text": str(unit.get("decision") or ""),
                })
                for step_ref in unit.get("step_refs") or []:
                    step = teaching_steps.get(step_ref)
                    if step:
                        resources.append({
                            "kind": "CORE1A_TEACHING_STEP",
                            "ref": step_ref,
                            "text": json.dumps(step, ensure_ascii=False),
                        })
                rep_ref = unit.get("representation_ref")
                rep = representations.get(rep_ref)
                if rep:
                    resources.append({
                        "kind": "CORE1A_REPRESENTATION_RECORD",
                        "ref": rep_ref,
                        "text": json.dumps(rep, ensure_ascii=False),
                    })
                    for asset_ref in rep.get("rendered_asset_refs") or []:
                        asset = repo_root / asset_ref
                        text = _read_asset_text(asset) if asset.is_file() else ""
                        resources.append({
                            "kind": "CORE1A_ASSET",
                            "ref": asset_ref,
                            "text": text,
                            "missing": not asset.is_file(),
                        })

        findings = []
        for resource in resources:
            if resource.get("missing"):
                findings.append({
                    "code": "PREATTEMPT_RESOURCE_MISSING",
                    "resource_kind": resource["kind"],
                    "resource_ref": resource["ref"],
                })
                continue
            normalized_resource = _normalize_for_match(resource["text"])
            for token in tokens:
                normalized_token = _normalize_for_match(token)
                if normalized_token and normalized_token in normalized_resource:
                    findings.append({
                        "code": "PROTECTED_RESULT_REACHABLE",
                        "resource_kind": resource["kind"],
                        "resource_ref": resource["ref"],
                        "token": token,
                    })
        items.append({
            "question_ref": qid,
            "protected_tokens": tokens,
            "resource_refs": [{"kind": r["kind"], "ref": r["ref"]} for r in resources],
            "findings": findings,
            "verdict": "PASS" if not findings else "FAIL",
        })

    return {
        "schema": "pre-attempt-leak-audit/v1",
        "bank_ref": bank.get("bank_id"),
        "package_ref": package.get("package_id") or package.get("id"),
        "items": items,
        "status": "PASS" if items and all(row["verdict"] == "PASS" for row in items) else "FAIL",
        "note": "Checks transitive pre-attempt reachability only; post-attempt solutions are intentionally outside scope.",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    report = audit(
        json.loads(args.bank.read_text(encoding="utf-8")),
        json.loads(args.package.read_text(encoding="utf-8")),
        args.repo_root,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
