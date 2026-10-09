"""Fail-closed nonpromoting 210-row NCERT Exemplar edition-provenance audit."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry, test_source_custody  # noqa: E402

EVIDENCE = "TEST/evidence/source-intake/ncert-exemplar-g9-r4-edition-provenance-review.v1.json"
BANK_REF = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
FROZEN = json.loads(r'''{"schema_version":"grade9v3-test-exemplar-edition-provenance-review-v1","observed_on":"2026-10-09","source_bank_ref":"TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json","provenance_scope":"ALL_210_NCERT_EXEMPLAR_G9_INTAKE_ROWS","observed_raw_edition_label":"2023-24","rows_bearing_raw_label":210,"edition_claim_disposition":"UNVERIFIED_PUBLISHER_EDITION","official_source_index_url":"https://ncert.nic.in/exemplar-problems.php?ln=en","official_rendered_pdf_urls":["https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf","https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf","https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf"],"official_page_layout_date_stamps":["16/04/18"],"official_layout_date_is_publisher_edition":false,"secondary_bibliography":{"url":"https://files.allncert.in/ncertbooks/2018/class9/ieep2ps.pdf","publisher_first_edition_as_claimed_in_unverified_mirror":"September 2008","most_recent_reprint_as_claimed_in_unverified_mirror":"April 2014","independently_authenticated_as_official_ncert_document":false,"may_resolve_2023_24_claim":false},"spot_checked_source_ids":["ncert-exemplar-g9-math-u01-q07","ncert-exemplar-g9-math-u01-q11","ncert-exemplar-g9-math-u01-q12","ncert-exemplar-g9-math-u01-q13","ncert-exemplar-g9-math-u01-q14","ncert-exemplar-g9-math-u02-q07","ncert-exemplar-g9-math-u02-q11","ncert-exemplar-g9-math-u02-q12","ncert-exemplar-g9-math-u02-q13","ncert-exemplar-g9-math-u02-q14"],"directly_compared_spot_check_count":10,"exact_official_pdf_bytes_obtained":false,"official_pdf_sha256":null,"publisher_edition_verified":false,"independent_reviewer_authenticated":false,"reviewer_conflict_disclosed":true,"reviewer_role":"ASSISTANT_CONTRIBUTED_TO_PR_IMPLEMENTATION","source_ready_promoted":false,"academic_validation_granted":false,"canonical_admission_authorized":false,"owner_acceptance_granted":false,"publication_authorized":false,"note":"This is a nonpromoting bibliographic discrepancy review. NCERT currently serves rendered pages with layout stamps 16/04/18, which do not identify the edition. The 2008/2014 imprint history is from a third-party mirror and is NOT independently authenticated. The bank's shared 2023-24 label is a historical capture claim only, not a verified publisher edition. Request original official imprint/edition evidence before any edition-specific certification."}''')


def require(ok: bool, description: str) -> None:
    if not ok:
        raise ValueError("R4 NCERT edition provenance: " + description)


def validate(repo: Path = REPO) -> dict:
    try:
        doc = json.loads((repo / EVIDENCE).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("R4 NCERT edition provenance: missing or invalid evidence") from exc
    require(doc == FROZEN, "frozen scope, bibliographic caveat, or authority flag changed")
    banks = test_intake_registry.load_intake_banks(repo)
    require(len(banks) == 1 and banks[0]["bank_id"] == "ncert-cbse-math-g9-pilot",
            "intake bank identity changed")
    rows = banks[0]["questions"]
    ids = [q["id"] for q in rows]
    require(len(ids) == len(set(ids)) == 210, "all 210 original source IDs must remain unique")
    require(all(q.get("edition_or_year") == FROZEN["observed_raw_edition_label"]
                and q.get("source_authority") == "NCERT_OFFICIAL"
                and q.get("source_kind") == "EXEMPLAR" for q in rows),
            "raw edition claim, source-authority family or scope changed")
    require(set(FROZEN["spot_checked_source_ids"]) <= set(ids)
            and len(FROZEN["spot_checked_source_ids"]) == 10,
            "spot-checked source scope changed")
    require(FROZEN["publisher_edition_verified"] is False
            and FROZEN["exact_official_pdf_bytes_obtained"] is False
            and FROZEN["official_pdf_sha256"] is None
            and FROZEN["secondary_bibliography"]["independently_authenticated_as_official_ncert_document"] is False
            and FROZEN["independent_reviewer_authenticated"] is False
            and FROZEN["reviewer_conflict_disclosed"] is True,
            "unsupported independent book origin/edition claim")
    require(all(FROZEN[name] is False for name in (
        "source_ready_promoted", "academic_validation_granted",
        "canonical_admission_authorized", "owner_acceptance_granted",
        "publication_authorized")), "edition note may not authorize promotion")
    status = test_source_custody.reconcile(repo)
    require(len(set(FROZEN["spot_checked_source_ids"]) & set(status["ready_ids"])) == 0,
            "edition review cannot supply original READY custody evidence")
    return {"question_count": len(rows),
            "raw_edition_label": FROZEN["observed_raw_edition_label"],
            "verified_publisher_edition": False,
            "source_ready_granted": 0,
            "academic_validation_granted": 0,
            "publication_authorized": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args(argv)
    try:
        report = validate(args.repo)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"NCERT edition provenance: {report['question_count']}/210 have "
          f"unverified raw edition label {report['raw_edition_label']}; "
          "0 new READY, academic PASS or publication authorizations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
