"""Fail-closed registry for the existing flat TEST official-source intake.

This is an identity and shape gate, NOT an academic or source-verification gate.
Stronger custody evidence must be reconciled into the same source identities instead
of being published as a second bank. A structured custody bank requires an explicit
versioned projection adapter; the same schema_version must not mean two shapes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "grade9v3-test-source-question-intake-v1"


def load_intake_banks(repo: Path) -> list[dict]:
    root = repo / "TEST" / "question-bank" / "intake"
    if not root.is_dir():
        return []

    banks: list[dict] = []
    ids: dict[str, Path] = {}
    locators: dict[tuple[str, ...], tuple[str, Path]] = {}

    for path in sorted(root.glob("*.json")):
        if path.name.endswith(".blueprint-handoff.json"):
            continue
        try:
            bank = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}: unreadable official-source intake: {exc}") from exc

        if not isinstance(bank, dict) or bank.get("schema_version") != SCHEMA:
            raise ValueError(f"{path}: unsupported TEST intake schema; no silent exclusion")
        if "documents" in bank:
            raise ValueError(
                f"{path}: structured custody uses the flat {SCHEMA} identity; "
                "reconcile it via an explicit versioned adapter, not a second TEST bank"
            )
        if not isinstance(bank.get("questions"), list):
            raise ValueError(f"{path}: questions must be a list")

        for index, q in enumerate(bank["questions"]):
            where = f"{path}: questions[{index}]"
            if not isinstance(q, dict):
                raise ValueError(f"{where}: expected a question object")
            if "source_document_ref" in q or "source_locator" in q:
                raise ValueError(f"{where}: incompatible structured custody requires an adapter")
            qid = q.get("id")
            if not isinstance(qid, str) or not qid.strip():
                raise ValueError(f"{where}: missing stable source question id")
            if qid in ids:
                raise ValueError(f"{where}: duplicate source id {qid!r} (first in {ids[qid]})")

            fields = ("source_authority", "source_kind", "source_url",
                      "chapter_or_unit", "exercise_or_section", "question_number")
            if any(not isinstance(q.get(field), str) or not q[field].strip() for field in fields):
                raise ValueError(f"{where}: incomplete official source identity/locator")
            if not isinstance(q.get("stem"), str) or not q["stem"].strip():
                raise ValueError(f"{where}: missing source stem")
            digest = q.get("stem_sha256")
            if not isinstance(digest, str) or not digest.startswith("sha256:") or len(digest) != 71:
                raise ValueError(f"{where}: missing or malformed source stem digest")

            # The locator, not the stem alone, is the identity. Official Q6/Q7
            # legitimately share a stem and differ in their source position/options.
            locator = tuple(q[field].strip() for field in fields)
            if locator in locators:
                first_id, first_path = locators[locator]
                raise ValueError(
                    f"{where}: duplicate official locator for {qid!r}; "
                    f"first used by {first_id!r} in {first_path}"
                )
            ids[qid] = path
            locators[locator] = (qid, path)
        banks.append(bank)
    return banks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    banks = load_intake_banks(args.repo)
    print(f"TEST intake identity PASS: {sum(len(b['questions']) for b in banks)} unique "
          f"questions in {len(banks)} bank(s); no custody or academic PASS implied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
