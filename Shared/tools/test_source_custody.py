#!/usr/bin/env python3
"""Reconcile independent Stage-1 source custody evidence onto existing TEST IDs.

This is source custody only. It never establishes academic validation,
canonical admission, curriculum acceptance, or a publication decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry  # noqa: E402

SCHEMA = "grade9v3-test-source-custody-overlay-v1"

# Frozen, manually inspected pilot pointers, not a substitute for official PDF checking.
# Adding a new pilot witness requires an explicit reviewed code change and hosted
# comment-authentication result; arbitrary plausible GitHub IDs cannot admit READY.
KNOWN_WITNESSES = {
    "github:reallaksh19/Grade9v3.5#129:6028932600": {
        "issue": 129, "id": 6028932600,
        "fragments": ("ieep201.pdf", "ieep2an.pdf", "Q1", "Q6"),
    },
    "github:reallaksh19/Grade9v3.5#129:6029049531": {
        "issue": 129, "id": 6029049531,
        "fragments": ("SHA-256", "sha256:40010d207519d386d5d2a6519c39745ee59de121105642b68c4f398a002cb3f6"),
    },
    "github:reallaksh19/Grade9v3.5#68:6050805060": {
        "issue": 68, "id": 6050805060,
        "fragments": ("ieep202.pdf", "ieep2an.pdf", "u02-q02", "u02-q06", "verbatim"),
    },
    "github:reallaksh19/Grade9v3.5#68:6053770988": {
        "issue": 68, "id": 6053770988,
        "fragments": ("ieep202.pdf", "ieep2an.pdf", "Which one of the following is a polynomial?", "Q1", "(C)"),
    },
}
# A real comment pointer is not fungible source evidence: scope it to the exact
# independently inspected question IDs and captured stem digests. The digest also
# prevents replay if the bank and overlay are modified in lockstep after inspection.
# These are bounded witness claims, not automatic official-PDF verification.
QUESTION_WITNESS_SCOPE = {
    "github:reallaksh19/Grade9v3.5#129:6029049531": {
        "ncert-exemplar-g9-math-u01-q01": "sha256:40010d207519d386d5d2a6519c39745ee59de121105642b68c4f398a002cb3f6",
        "ncert-exemplar-g9-math-u01-q02": "sha256:530fe02b34e00327f20ac7eb891300f78be4a57a1c71a3d78b6daaa800c50859",
        "ncert-exemplar-g9-math-u01-q03": "sha256:4c255eb30fe8e41876eec4a4763b3a8edc9ad76be3e12ab61c25790b7441b7b7",
        "ncert-exemplar-g9-math-u01-q04": "sha256:29b572e11d87ac9ecc63095968127fd290bf8dedd16434537dcc5d0dfdf289be",
        "ncert-exemplar-g9-math-u01-q05": "sha256:9e546d00f0d12851328a795961478eb2e7de09c63623aeed959f6fa7cc590f12",
        "ncert-exemplar-g9-math-u01-q06": "sha256:ca54af54c150e14888774feabed443bc1268dd4ffc24c58935994ef023b17e10",
    },
    "github:reallaksh19/Grade9v3.5#68:6053770988": {
        "ncert-exemplar-g9-math-u02-q01": "sha256:fcc60bc35e78598ae1d95c91c96c9e04a6378d0c31a198742b49dcb3c5509a21",
    },
    "github:reallaksh19/Grade9v3.5#68:6050805060": {
        "ncert-exemplar-g9-math-u02-q02": "sha256:627a863a58c1f737a8ec90567d45497ed6091979977777e9a6b851ad42a9ad03",
        "ncert-exemplar-g9-math-u02-q03": "sha256:acf970e82ea78d3e0962ee2961e90547822df1945cf6a0093512c9373be69bd7",
        "ncert-exemplar-g9-math-u02-q04": "sha256:43f7d6ff7a197201b8c538375778d52ee7e2906cd987cba60eaaa94a07d14416",
        "ncert-exemplar-g9-math-u02-q05": "sha256:10c33f397767b5dd584b33dcbe1571188c09ff872732d69ba97102c2e73cb879",
        "ncert-exemplar-g9-math-u02-q06": "sha256:d1f9ab971075dd4795abafbb0e7a9163deb032e79470daae63d2198ebcef5643",
    },
}
# Fixed observed options/pages for the 12 already-inspected pilot instances.
# This is a replay guard for recorded witness scope, not new NCERT PDF proof.
QUESTION_WITNESS_INSTANCE_SCOPE = {
    "ncert-exemplar-g9-math-u01-q01": {"options": ["(A) a natural number", "(B) an integer", "(C) a real number", "(D) a whole number"], "pages": (2, 1)},
    "ncert-exemplar-g9-math-u01-q02": {"options": ["(A) there is no rational number", "(B) there is exactly one rational number", "(C) there are infinitely many rational numbers", "(D) there are only rational numbers and no irrational numbers"], "pages": (3, 2)},
    "ncert-exemplar-g9-math-u01-q03": {"options": ["(A) terminating", "(B) non-terminating", "(C) non-terminating repeating", "(D) non-terminating non-repeating"], "pages": (3, 2)},
    "ncert-exemplar-g9-math-u01-q04": {"options": ["(A) always an irrational number", "(B) always a rational number", "(C) always an integer", "(D) sometimes rational, sometimes irrational"], "pages": (3, 2)},
    "ncert-exemplar-g9-math-u01-q05": {"options": ["(A) a finite decimal", "(B) 1.41421", "(C) non-terminating recurring", "(D) non-terminating non-recurring"], "pages": (3, 2)},
    "ncert-exemplar-g9-math-u01-q06": {"options": ["(A) √(4/9)", "(B) √12/√3", "(C) √7", "(D) √81"], "pages": (3, 2)},
    "ncert-exemplar-g9-math-u02-q01": {"options": ["(A) x²/2 - 2/x²", "(B) √(2x) - 1", "(C) x² + 3x^(3/2)/√x", "(D) (x - 1)/(x + 1)"], "pages": (14, 1)},
    "ncert-exemplar-g9-math-u02-q02": {"options": ["(A) 2", "(B) 0", "(C) 1", "(D) 1/2"], "pages": (14, 1)},
    "ncert-exemplar-g9-math-u02-q03": {"options": ["(A) 4", "(B) 5", "(C) 3", "(D) 7"], "pages": (14, 1)},
    "ncert-exemplar-g9-math-u02-q04": {"options": ["(A) 0", "(B) 1", "(C) Any natural number", "(D) Not defined"], "pages": (14, 1)},
    "ncert-exemplar-g9-math-u02-q05": {"options": ["(A) 0", "(B) 1", "(C) 4√2", "(D) 8√2 + 1"], "pages": (14, 1)},
    "ncert-exemplar-g9-math-u02-q06": {"options": ["(A) -6", "(B) 6", "(C) 2", "(D) -2"], "pages": (14, 1)},
}

# Frozen original document and answer-key claims for the 12 pilot witnesses.
# Prevent coordinated changes to two mutable JSON files from laundering a
# different official PDF or answer under an older witness. These are replay
# guards, not independent re-verification of NCERT document contents.
QUESTION_WITNESS_DOCUMENT_SCOPE = {
    "github:reallaksh19/Grade9v3.5#129:6029049531": (
        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf",
        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf",
        "github:reallaksh19/Grade9v3.5#129:6028932600",
    ),
    "github:reallaksh19/Grade9v3.5#68:6053770988": (
        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf",
        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf",
        "github:reallaksh19/Grade9v3.5#68:6053770988",
    ),
    "github:reallaksh19/Grade9v3.5#68:6050805060": (
        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf",
        "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf",
        "github:reallaksh19/Grade9v3.5#68:6050805060",
    ),
}
QUESTION_WITNESS_ANSWER_SCOPE = {
    "ncert-exemplar-g9-math-u01-q01": "(C)",
    "ncert-exemplar-g9-math-u01-q02": "(C)",
    "ncert-exemplar-g9-math-u01-q03": "(D)",
    "ncert-exemplar-g9-math-u01-q04": "(D)",
    "ncert-exemplar-g9-math-u01-q05": "(D)",
    "ncert-exemplar-g9-math-u01-q06": "(C)",
    "ncert-exemplar-g9-math-u02-q01": "(C)",
    "ncert-exemplar-g9-math-u02-q02": "(B)",
    "ncert-exemplar-g9-math-u02-q03": "(A)",
    "ncert-exemplar-g9-math-u02-q04": "(D)",
    "ncert-exemplar-g9-math-u02-q05": "(B)",
    "ncert-exemplar-g9-math-u02-q06": "(A)",
}


HOLD_WITNESS_SCOPE = {
    "ncert-exemplar-g9-math-u02-q01": (
        "github:reallaksh19/Grade9v3.5#68:6050805060",
        "sha256:e9cf2f9dd0b4ccdd828e671580c65aed68b09405a1eda4c0f54561b9e24a3175",
        "Which one of the following is a polynomial?",
    ),
}


def _require(condition: bool, where: str, reason: str) -> None:
    if not condition:
        raise ValueError(f"{where}: {reason}")


def _evidence_ref(value: object) -> bool:
    # A durable pointer shape, not proof that GitHub has verified the claim.
    return (isinstance(value, str)
            and value in KNOWN_WITNESSES
            and re.fullmatch(
                r"github:reallaksh19/Grade9v3\.5#[1-9][0-9]*:[1-9][0-9]*", value
            ) is not None)


def reconcile(repo: Path) -> dict:
    """Return a fail-closed, deterministic evidence view; never mutate intake records."""
    banks = test_intake_registry.load_intake_banks(repo)
    by_id = {q["id"]: (bank, q) for bank in banks for q in bank["questions"]}
    reconciled: dict[str, dict] = {}
    source_holds: dict[str, dict] = {}
    evidence_dir = repo / "TEST/evidence/source-intake"
    for path in sorted(evidence_dir.glob("*.custody.v1.json")):
        try:
            overlay = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}: invalid custody evidence: {exc}") from exc
        where = str(path)
        _require(isinstance(overlay, dict) and overlay.get("schema_version") == SCHEMA,
                 where, "unsupported custody evidence schema")
        _require(isinstance(overlay.get("source_bank_ref"), str), where, "missing bank reference")
        _require(isinstance(overlay.get("documents"), list), where, "documents must be a list")
        _require(isinstance(overlay.get("records"), list), where, "records must be a list")
        documents: dict[str, dict] = {}
        for document in overlay["documents"]:
            _require(isinstance(document, dict), where, "invalid document")
            name = document.get("id")
            _require(isinstance(name, str) and name and name not in documents,
                     where, "missing or duplicate document id")
            authority = document.get("authority")
            _require(test_intake_registry.official_source_url(document.get("url"), authority), where, "unofficial document URL")
            _require(document.get("role") in {"QUESTION_SOURCE", "ANSWER_KEY"}, where, "invalid document role")
            _require(_evidence_ref(document.get("verification_evidence_ref")), where, "missing source document witness")
            documents[name] = document
        for record in overlay["records"]:
            _require(isinstance(record, dict), where, "invalid evidence record")
            qid = record.get("id")
            _require(isinstance(qid, str) and qid in by_id, where, f"orphan source identity {qid!r}")
            _require(qid not in reconciled and qid not in source_holds,
                     where, f"duplicate custody evidence or source-text HOLD for {qid}")
            bank, source = by_id[qid]
            _require(overlay["source_bank_ref"] == f"TEST/question-bank/intake/{bank['bank_id']}.json",
                     where, f"bank identity mismatch for {qid}")
            origin = documents.get(record.get("source_document_ref"))
            _require(origin is not None and origin["role"] == "QUESTION_SOURCE",
                     where, f"missing question-source document for {qid}")
            _require(origin["authority"] == source["source_authority"]
                     and origin["kind"] == source["source_kind"]
                     and origin["url"] == source["source_url"],
                     where, f"official source identity mismatch for {qid}")
            digest = "sha256:" + hashlib.sha256(source["stem"].encode("utf-8")).hexdigest()
            _require(record.get("stem_sha256") == source["stem_sha256"] == digest,
                     where, f"stem digest mismatch for {qid}")
            _require(record.get("original_identifier") == source["original_identifier"]
                     and record.get("options") == source.get("options", []),
                     where, f"question identifier/options mismatch for {qid}")
            locator = record.get("source_locator") or {}
            _require(isinstance(locator, dict), where, f"invalid locator for {qid}")
            _require(all(locator.get(key) == source[key] for key in
                         ("chapter_or_unit", "exercise_or_section", "question_number")),
                     where, f"source exercise/number mismatch for {qid}")
            _require(type(locator.get("printed_page")) is int
                     and locator["printed_page"] > 0
                     and type(locator.get("pdf_page_index")) is int
                     and locator["pdf_page_index"] >= 0,
                     where, f"missing independently checked PDF/printed page for {qid}")
            _require(record.get("source_verification_status") == "SOURCE_VERIFIED_OFFICIAL"
                     and record.get("text_verification_status") == "TEXT_VERIFIED_AGAINST_OFFICIAL"
                     and _evidence_ref(record.get("verification_evidence_ref")),
                     where, f"independent source/text evidence missing for {qid}")
            _require(QUESTION_WITNESS_SCOPE.get(record.get("verification_evidence_ref"), {}).get(qid) == digest,
                     where, f"question witness scope or stem digest mismatch for {qid}")
            witness_documents = QUESTION_WITNESS_DOCUMENT_SCOPE.get(record["verification_evidence_ref"])
            _require(witness_documents is not None
                     and origin["url"] == witness_documents[0]
                     and origin["verification_evidence_ref"] == witness_documents[2],
                     where, f"question witness official document mismatch for {qid}")
            # A stem digest alone does not pin option text; two coordinated edits
            # to the bank and overlay must not replay a previous question witness.
            instance = QUESTION_WITNESS_INSTANCE_SCOPE.get(qid)
            _require(instance is not None and record.get("options") == instance["options"],
                     where, f"question witness options scope mismatch for {qid}")
            _require((locator["printed_page"], locator["pdf_page_index"]) == instance["pages"],
                     where, f"question witness page scope mismatch for {qid}")
            _require(record.get("workflow_status") == "READY_FOR_BLUEPRINT",
                     where, f"unsupported READY claim for {qid}")
            # Question-text readiness is independent of answer-key availability.
            # When a key is supplied, verify its separate document witness; otherwise
            # do not infer answer custody from a legacy intake answer label.
            key = record.get("official_answer")
            key_doc = None
            if key is not None:
                _require(isinstance(key, dict) and bool(key),
                         where, f"invalid answer custody for {qid}")
                key_doc = documents.get(key.get("document_ref"))
                _require(key_doc is not None and key_doc["role"] == "ANSWER_KEY"
                         and key_doc["authority"] == origin["authority"]
                         and key_doc["url"] != origin["url"]
                         and _evidence_ref(key.get("verification_evidence_ref")),
                         where, f"missing independent official answer-key witness for {qid}")
                _require(key.get("exercise_or_section") == source["exercise_or_section"]
                         and key.get("question_number") == source["question_number"],
                         where, f"answer-key locator mismatch for {qid}")
                answer_key = key.get("answer_key")
                _require(source.get("official_answer_available") is True
                         and isinstance(answer_key, str) and bool(answer_key.strip())
                         and source.get("official_answer_text", "").startswith(answer_key),
                         where, f"official answer differs from source record for {qid}")
                if source.get("question_type") == "MULTIPLE_CHOICE":
                    _require(bool(re.fullmatch(r"\([A-Za-z]\)", answer_key))
                             and any(isinstance(option, str) and option.startswith(answer_key)
                                     for option in source.get("options", [])),
                             where, f"official answer differs from source record for {qid}")
                _require(key_doc["url"] == witness_documents[1]
                         and key_doc["verification_evidence_ref"] == witness_documents[2]
                         and key.get("verification_evidence_ref") == witness_documents[2]
                         and answer_key == QUESTION_WITNESS_ANSWER_SCOPE.get(qid),
                         where, f"answer witness scope mismatch for {qid}")
            reconciled[qid] = {
                "intake_question_ref": qid,
                "source_identity": {"authority": origin["authority"], "kind": origin["kind"],
                                    "document_url": origin["url"], "document_title": origin["title"]},
                "source_locator": locator,
                "stem": source["stem"],
                "stem_sha256": digest,
                "options": source.get("options", []),
                "subject": source["subject"], "grade": source["grade"],
                "topic_label": source["topic_label"], "subtopic_label": source.get("subtopic_label"),
                "question_type": source["question_type"],
                "official_answer_key_ref": ({"document_url": key_doc["url"],
                                             "exercise_or_section": key["exercise_or_section"],
                                             "question_number": key["question_number"],
                                             "answer_key": key["answer_key"]} if key_doc else None),
                "official_answer_custody": "INDEPENDENTLY_EVIDENCED" if key_doc else "KEY_NOT_EVIDENCED",
                "verification_evidence_ref": record["verification_evidence_ref"],
                "intake_status": "READY_FOR_BLUEPRINT",
            }
        hold_rows = overlay.get("holds", [])
        _require(isinstance(hold_rows, list), where, "source-text holds must be a list")
        for hold in hold_rows:
            _require(isinstance(hold, dict), where, "invalid source-text hold")
            qid = hold.get("id")
            _require(isinstance(qid, str) and qid in by_id, where, f"orphan source-text hold {qid!r}")
            _require(qid not in reconciled and qid not in source_holds, where, f"duplicate or READY source-text hold {qid}")
            bank, source = by_id[qid]
            _require(overlay["source_bank_ref"] == f"TEST/question-bank/intake/{bank['bank_id']}.json",
                     where, f"bank identity mismatch for held {qid}")
            origin = documents.get(hold.get("source_document_ref"))
            _require(origin is not None and origin["role"] == "QUESTION_SOURCE"
                     and origin["authority"] == source["source_authority"]
                     and origin["kind"] == source["source_kind"]
                     and origin["url"] == source["source_url"], where, f"held official source mismatch for {qid}")
            loc = hold.get("source_locator")
            _require(isinstance(loc, dict)
                     and all(loc.get(k) == source[k] for k in
                             ("chapter_or_unit", "exercise_or_section", "question_number"))
                     and type(loc.get("printed_page")) is int and loc["printed_page"] > 0
                     and type(loc.get("pdf_page_index")) is int and loc["pdf_page_index"] >= 0,
                     where, f"invalid held source locator for {qid}")
            _require(hold.get("disposition") == "SOURCE_TEXT_HOLD"
                     and hold.get("reason_code") == "VERBATIM_SOURCE_TEXT_MISMATCH"
                     and hold.get("captured_stem") == source["stem"]
                     and hold.get("captured_stem_sha256") == source["stem_sha256"]
                     and isinstance(hold.get("official_stem"), str)
                     and bool(hold["official_stem"].strip()) and hold["official_stem"] != source["stem"]
                     and _evidence_ref(hold.get("verification_evidence_ref"))
                     and HOLD_WITNESS_SCOPE.get(qid) == (
                         hold.get("verification_evidence_ref"),
                         hold.get("captured_stem_sha256"),
                         hold.get("official_stem")),
                     where, f"invalid disputed official wording for {qid}")
            source_holds[qid] = {"id": qid, "reason": hold["reason_code"],
                                 "official_stem": hold["official_stem"],
                                 "verification_evidence_ref": hold["verification_evidence_ref"]}
    return {
        "schema_version": "grade9v3-test-source-custody-reconciliation-v1",
        "total_intake": len(by_id),
        "ready_for_blueprint": len(reconciled),
        "evidence_pending": len(by_id) - len(reconciled) - len(source_holds),
        "source_text_hold": len(source_holds),
        "ready_ids": sorted(reconciled),
        "hold_ids": sorted(source_holds),
        "held": [source_holds[qid] for qid in sorted(source_holds)],
        "pending_ids": sorted(set(by_id) - set(reconciled) - set(source_holds)),
        "handoff": [reconciled[qid] for qid in sorted(reconciled)],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--handoff", action="store_true", help="print machine-readable verified-only handoff")
    args = parser.parse_args(argv)
    result = reconcile(args.repo)
    if args.handoff:
        print(json.dumps(result["handoff"], sort_keys=True, ensure_ascii=False, indent=2))
    else:
        print(f"Stage-1 custody: {result['ready_for_blueprint']} READY_FOR_BLUEPRINT; "
              f"{result['source_text_hold']} SOURCE_TEXT_HOLD; "
          f"{result['evidence_pending']} EVIDENCE_PENDING; "
              "no academic, production or owner acceptance implied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
