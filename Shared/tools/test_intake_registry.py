"""Fail-closed registry for the existing flat TEST official-source intake.

This is an identity and shape gate, NOT an academic or source-verification gate.
Stronger custody evidence must be reconciled into the same source identities instead
of being published as a second bank. A structured custody bank requires an explicit
versioned projection adapter; the same schema_version must not mean two shapes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "grade9v3-test-source-question-intake-v1"

OFFICIAL_HOSTS = {"NCERT_OFFICIAL": {"ncert.nic.in"},
                  "CBSE_OFFICIAL": {"cbse.gov.in", "cbseacademic.nic.in"}}


def official_source_url(url: object, authority: object) -> bool:
    """Permit only explicit official HTTPS hosts, never lookalikes or active URLs."""
    if not isinstance(url, str) or not isinstance(authority, str):
        return False
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https"
                and parsed.hostname in OFFICIAL_HOSTS.get(authority, set())
                and not parsed.username and not parsed.password
                and parsed.port is None and bool(parsed.path)
                and url.startswith(f"https://{parsed.hostname}/")
                and parsed.path != "/"
                and "//" not in parsed.path
                and not any(part in (".", "..") for part in parsed.path.split("/"))
                and not any(mark in url for mark in ("?", "#", "%", chr(92)))
                and not any(char.isspace() for char in url))
    except ValueError:
        return False



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
        if bank.get("bank_id") != path.stem:
            raise ValueError(f"{path}: bank ID must equal source filename")
        if bank.get("subject") != "Mathematics" or type(bank.get("grade")) is not int or bank["grade"] != 9:
            raise ValueError(f"{path}: unsupported TEST intake subject/grade")
        scope = bank.get("source_scope")
        if not isinstance(scope, list) or not scope or any(x not in OFFICIAL_HOSTS for x in scope):
            raise ValueError(f"{path}: invalid official source scope")

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
            metadata = ("original_identifier", "document_title", "capture_method",
                        "wording_custody", "text_verification_status", "last_checked",
                        "topic_label", "question_type")
            if any(not isinstance(q.get(field), str) or not q[field].strip() for field in metadata):
                raise ValueError(f"{where}: missing required Stage-1 metadata")
            # The flat v1 file is an unverified capture ledger, never a custody
            # or READY receipt. Those decisions come only from the reconciler.
            if q.get("workflow_status") != "EVIDENCE_PENDING":
                raise ValueError(f"{where}: raw capture cannot claim READY or source HOLD")
            if q.get("text_verification_status") != "CAPTURED_UNVERIFIED":
                raise ValueError(f"{where}: raw capture cannot claim independent text verification")
            if "page" in q:
                raise ValueError(f"{where}: ambiguous raw page is prohibited; use unverified_legacy_page")
            legacy_page = q.get("unverified_legacy_page")
            if legacy_page is not None and (type(legacy_page) is not int or legacy_page < 1):
                raise ValueError(f"{where}: invalid unverified legacy page")
            if q.get("subject") != bank["subject"] or type(q.get("grade")) is not int or q["grade"] != bank["grade"]:
                raise ValueError(f"{where}: bank/question subject or grade mismatch")
            if q.get("source_authority") not in scope:
                raise ValueError(f"{where}: source authority outside bank scope")

            fields = ("source_authority", "source_kind", "source_url",
                      "chapter_or_unit", "exercise_or_section", "question_number")
            if any(not isinstance(q.get(field), str) or not q[field].strip() for field in fields):
                raise ValueError(f"{where}: incomplete official source identity/locator")
            if not official_source_url(q["source_url"], q["source_authority"]):
                raise ValueError(f"{where}: unofficial or unsafe source URL")
            if not isinstance(q.get("stem"), str) or not q["stem"].strip():
                raise ValueError(f"{where}: missing source stem")
            digest = q.get("stem_sha256")
            if not isinstance(digest, str) or not digest.startswith("sha256:") or len(digest) != 71:
                raise ValueError(f"{where}: missing or malformed source stem digest")
            computed = "sha256:" + hashlib.sha256(q["stem"].encode("utf-8")).hexdigest()
            if digest != computed:
                raise ValueError(f"{where}: source stem digest does not match wording")

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
