#!/usr/bin/env python3
"""Project QRT M2/M3 into the attempt-gated Core2 solution payload.

M1 remains the learner-facing pre-attempt Common wrong route.  Diagnosis and repair are
post-attempt because they can name the conceptual failure and replacement rule explicitly.
The transform is deterministic and driven by the machine-readable authoring evidence.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


class MisconceptionProjectionError(ValueError):
    pass


def article_id(qid: str) -> str:
    try:
        n = int(qid.removeprefix("Q"))
    except ValueError as exc:
        raise MisconceptionProjectionError(f"unexpected question id: {qid}") from exc
    return f"OWN-ISSUE17-SAV-{n:02d}"


def project(text: str, evidence: dict) -> tuple[str, int]:
    changed = 0
    for item in evidence.get("items") or []:
        qid = str(item.get("question_id") or "")
        rid = article_id(qid)
        misconception = item.get("misconception") or {}
        diagnostic = str(misconception.get("M2") or "").strip()
        repair = str(misconception.get("M3") or "").strip()
        if not diagnostic or not repair:
            raise MisconceptionProjectionError(f"{qid}: M2/M3 authoring evidence missing")

        article_match = re.search(
            rf'(<article\b[^>]*\bid="{re.escape(rid)}"[^>]*>.*?</article>)', text, re.S
        )
        if not article_match:
            raise MisconceptionProjectionError(f"{qid}: rendered Core2 article not found")
        article = article_match.group(1)
        if "data-g9-post-attempt-misconception" in article:
            continue

        marker = f'<template data-g9-payload="CORE2-{rid}-solution">'
        if article.count(marker) != 1:
            raise MisconceptionProjectionError(f"{qid}: matching solution payload not found exactly once")
        block = (
            '<div class="g9-post-attempt-misconception" data-g9-post-attempt-misconception>'
            '<div class="g9-block" data-g9-block="diagnose"><h4>Diagnose the tempting route</h4><p>'
            + html.escape(diagnostic)
            + '</p></div>'
            '<div class="g9-block" data-g9-block="repair"><h4>Repair the idea</h4><p>'
            + html.escape(repair)
            + '</p></div></div>'
        )
        article = article.replace(marker, marker + block, 1)
        text = text[:article_match.start()] + article + text[article_match.end():]
        changed += 1
    return text, changed


def check(text: str, evidence: dict) -> int:
    checked = 0
    for item in evidence.get("items") or []:
        qid = str(item.get("question_id") or "")
        rid = article_id(qid)
        article_match = re.search(
            rf'<article\b[^>]*\bid="{re.escape(rid)}"[^>]*>(.*?)</article>', text, re.S
        )
        if not article_match:
            raise MisconceptionProjectionError(f"{qid}: rendered article missing during check")
        article = article_match.group(1)
        template_match = re.search(
            rf'<template data-g9-payload="CORE2-{re.escape(rid)}-solution">(.*?)</template>', article, re.S
        )
        if not template_match:
            raise MisconceptionProjectionError(f"{qid}: solution payload missing during check")
        payload = template_match.group(1)
        if "data-g9-post-attempt-misconception" not in payload:
            raise MisconceptionProjectionError(f"{qid}: M2/M3 block is not inside the attempt-gated payload")
        misconception = item.get("misconception") or {}
        for key in ("M2", "M3"):
            expected = html.escape(str(misconception.get(key) or "").strip())
            if expected not in payload:
                raise MisconceptionProjectionError(f"{qid}: rendered {key} text does not match authoring evidence")
        checked += 1
    return checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    text = args.html.read_text(encoding="utf-8")
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if args.write:
        text, changed = project(text, evidence)
        args.html.write_text(text, encoding="utf-8")
        print(f"post-attempt misconception projection: moved {changed} question block(s)")
    count = check(text, evidence)
    print(f"post-attempt misconception projection: PASS ({count} question block(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
