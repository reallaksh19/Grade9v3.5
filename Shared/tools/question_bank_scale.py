#!/usr/bin/env python3
"""Measure Question Bank platform behavior on a deterministic synthetic scale fixture.

The observation is engineering evidence, not content authority. Wall-clock and memory values
are intentionally excluded from deterministic build identity and are not pass/fail thresholds.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import tracemalloc
from pathlib import Path

try:
    from .question_bank_platform import assemble_platform, canonical_json, search
except ImportError:  # direct execution
    from question_bank_platform import assemble_platform, canonical_json, search

SCHEMA = "grade9v3-question-bank-scale-observation-v1"
FIXTURE_VERSION = "1.0.0"


def synthetic_questions(count: int) -> list[dict]:
    rows: list[dict] = []
    for index in range(count):
        subject_index = index % 5
        topic_index = (index // 5) % 20
        family_index = (index // 100) % 250
        subject = f"Synthetic Subject {subject_index + 1}"
        topic = f"Synthetic Topic {topic_index + 1}"
        value = index + 2
        rows.append({
            "id": f"fixture:question:{index:06d}",
            "order": index,
            "subject": subject,
            "subject_ref": f"fixture:subject:{subject_index + 1}",
            "topic": topic,
            "topic_ref": f"fixture:topic:{subject_index + 1}:{topic_index + 1}",
            "question_type": "constructed_response",
            "exam": "Synthetic Scale Fixture",
            "year": 2026,
            "paper": f"Fixture {subject_index + 1}",
            "question_number": str(index + 1),
            "stem": f"For synthetic record {index}, evaluate {value} + {topic_index} and explain the invariant.",
            "subparts": [],
            "options": [],
            "conditions": [f"value={value}"],
            "difficulty": {"band": f"D{index % 4 + 1}", "score": index % 10 + 1},
            "expected_time_seconds": 60,
            "common_wrong_route": "",
            "stable_crux_move": f"Apply invariant family {family_index}",
            "primary_capability_ref": f"fixture:capability:{subject_index + 1}:{topic_index + 1}",
            "secondary_capability_refs": [],
            "family_ref": f"fixture:family:{family_index:03d}",
            "answer": {"summary": str(value + topic_index)},
        })
    return rows


def observe(question_count: int) -> dict:
    questions = synthetic_questions(question_count)
    browser_projection = {
        "schema_version": "synthetic-scale-fixture-v1",
        "questions": questions,
    }

    tracemalloc.start()
    started = time.perf_counter()
    platform_data = assemble_platform(browser_projection)
    build_seconds = time.perf_counter() - started
    _current, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    queries = ["synthetic invariant", "record 250", "topic 7", "family 12"]
    search_started = time.perf_counter()
    query_results = []
    for query in queries:
        hits = search(platform_data["search"], query)
        query_results.append({"query": query, "hit_count": len(hits)})
    search_seconds = time.perf_counter() - search_started

    payload_sizes = {
        "catalog_bytes": len(canonical_json(platform_data["catalog"]).encode("utf-8")),
        "search_index_bytes": len(canonical_json(platform_data["search"]).encode("utf-8")),
        "dedup_report_bytes": len(canonical_json(platform_data["dedup"]).encode("utf-8")),
        "lineage_bytes": len(canonical_json(platform_data["lineage"]).encode("utf-8")),
        "receipt_bytes": len(canonical_json(platform_data["receipt"]).encode("utf-8")),
    }
    return {
        "schema_version": SCHEMA,
        "fixture": {
            "version": FIXTURE_VERSION,
            "question_count": question_count,
            "subject_count": 5,
            "topic_count": 100,
            "generator": "Shared/tools/question_bank_scale.py",
        },
        "environment": {
            "python": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "observations": {
            "build_seconds": build_seconds,
            "peak_traced_bytes": peak_bytes,
            "search_batch_seconds": search_seconds,
            "search_queries": query_results,
            **payload_sizes,
            "dedup_evidence_count": platform_data["dedup"]["evidence_count"],
            "search_document_count": platform_data["search"]["document_count"],
        },
        "interpretation": {
            "timings_are_thresholds": False,
            "runtime_metadata_in_build_identity": False,
            "purpose": "Expose monolithic indexing/dedup regressions before choosing sharding or Web Worker architecture.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=int, default=5000)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.questions < 1:
        parser.error("--questions must be positive")
    result = observe(args.questions)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.out:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
