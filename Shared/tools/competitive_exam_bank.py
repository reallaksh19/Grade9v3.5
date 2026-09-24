"""Validate the canonical competitive-exam bank as an activity, not only as records.

JSON Schema owns shape. This module owns cross-record invariants that schema cannot
express: source identity uniqueness, ledger closure, provenance promotion rules,
difficulty arithmetic, reasoning/scaffold references, and run-gate closure.

It deliberately reuses package.schema.json for the learner-facing question/resource
records instead of creating a parallel educational object model.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
BANK_SCHEMA = ROOT / "Shared/library/competitive-exam-bank.schema.json"
PACKAGE_SCHEMA = ROOT / "Shared/library/package.schema.json"
RUN_SCHEMA = ROOT / "Shared/library/question-bank-run.schema.json"
PUBLICATION_SCHEMA = ROOT / "Shared/library/question-bank-publication.schema.json"

DEFAULT_BANKS = (
    ROOT / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json",
    ROOT / "Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json",
)
DEFAULT_LEDGER = ROOT / "docs/question-bank/pass1/source-acquisition-ledger.json"
DEFAULT_RUN = ROOT / "docs/question-bank/pass1/run-manifest.json"
DEFAULT_CONCEPT_INVENTORY = ROOT / "docs/question-bank/pass1/concept-bucket-inventory.md"

DIFFICULTY_BAND = {
    0: "D1", 1: "D1", 2: "D1",
    3: "D2", 4: "D2", 5: "D2",
    6: "D3", 7: "D3",
    8: "D4", 9: "D4", 10: "D4",
}
OFFICIAL_HOSTS = {
    "jeeadv.ac.in",
    "www.jeeadv.ac.in",
    "nta.ac.in",
    "www.nta.ac.in",
    "neet.nta.nic.in",
    "www.neet.nta.nic.in",
    "jeemain.nta.nic.in",
    "www.jeemain.nta.nic.in",
    "cdnbbsr.s3waas.gov.in",
}
EXPECTED_GATES = {
    "G0_SCOPE_FROZEN",
    "G1_CORPUS_ENUMERATED",
    "G2_SOURCE_AUTHORITY_CHECKED",
    "G3_SOURCE_DISPOSITIONS_COMPLETE",
    "G4_CANONICAL_ITEMS_VALID",
    "G5_CONCEPT_REFS_RESOLVED",
    "G6_ANSWERS_AND_DIFFICULTY_CHECKED",
    "G7_COVERAGE_CLOSED",
    "G8_PUBLICATION_CONTRACT_READY",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validator(schema: dict):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ModuleNotFoundError as exc:
        raise RuntimeError("jsonschema is required for competitive exam bank validation") from exc
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _schema_findings(value: dict, schema_path: Path, point: str, where: str) -> list[dict]:
    schema = load(schema_path)
    findings = []
    for error in _schema_validator(schema).iter_errors(value):
        loc = "/".join(str(p) for p in error.path)
        findings.append({
            "point": point,
            "where": f"{where}/{loc}".rstrip("/"),
            "detail": error.message,
        })
    return findings


def _package_record_findings(record: dict, definition: str, where: str) -> list[dict]:
    package = load(PACKAGE_SCHEMA)
    local = {
        "$schema": package.get("$schema", "https://json-schema.org/draft/2020-12/schema"),
        "$defs": package["$defs"],
        "$ref": f"#/$defs/{definition}",
    }
    findings = []
    for error in _schema_validator(local).iter_errors(record):
        loc = "/".join(str(p) for p in error.path)
        findings.append({
            "point": "EXAM_BANK_PACKAGE_RECORD_STRUCTURE",
            "where": f"{where}/{loc}".rstrip("/"),
            "detail": error.message,
        })
    return findings


def _fail(findings: list[dict], point: str, where: str, detail: str) -> None:
    findings.append({"point": point, "where": where, "detail": detail})


def _where(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _canonical_physics_ids() -> tuple[set[str], set[str]]:
    capabilities: set[str] = set()
    families: set[str] = set()
    for path in sorted((ROOT / "Physics/library").glob("*.json")):
        try:
            package = load(path)
        except Exception:
            continue
        for row in package.get("capabilities", []):
            if row.get("id"):
                capabilities.add(row["id"])
        for row in package.get("question_families", []):
            if row.get("id"):
                families.add(row["id"])
    return capabilities, families


def _validate_bank(path: Path, ledger: dict, concept_inventory: str) -> tuple[list[dict], list[dict]]:
    bank = load(path)
    findings = _schema_findings(bank, BANK_SCHEMA, "EXAM_BANK_SCHEMA", _where(path))
    questions = list(bank.get("questions") or [])
    resources = list(bank.get("resources") or [])
    resource_ids = {r.get("id") for r in resources if r.get("id")}

    for resource in resources:
        findings += _package_record_findings(
            resource, "resource", f"{_where(path)}#resource:{resource.get('id', '<missing>')}"
        )
    for question in questions:
        findings += _package_record_findings(
            question, "question", f"{_where(path)}#question:{question.get('id', '<missing>')}"
        )

    ext = bank.get("extensions") or {}
    if ext.get("grade9v3:accepted_question_count") != len(questions):
        _fail(findings, "EXAM_BANK_COUNT_MISMATCH", _where(path),
              "grade9v3:accepted_question_count must equal len(questions)")
    topic_counts = ext.get("grade9v3:topic_counts") or {}
    if sum(topic_counts.values()) != len(questions):
        _fail(findings, "EXAM_BANK_TOPIC_COUNT_MISMATCH", _where(path),
              "sum(grade9v3:topic_counts) must equal len(questions)")

    seen_ids: set[str] = set()
    identities: set[tuple] = set()
    physics_caps, physics_families = _canonical_physics_ids()
    accepted_by_id = {}
    for record in ledger.get("accepted_authoritative_records", []):
        for question_id in record.get("accepted_question_ids", []):
            if question_id in accepted_by_id:
                _fail(findings, "EXAM_BANK_LEDGER_DUPLICATE_ACCEPTANCE", question_id,
                      "question appears in more than one authoritative ledger record")
            accepted_by_id[question_id] = record

    for q in questions:
        qid = q.get("id", "<missing>")
        if qid in seen_ids:
            _fail(findings, "EXAM_BANK_DUPLICATE_ID", qid, "question id is duplicated")
        seen_ids.add(qid)

        qext = q.get("extensions") or {}
        provenance = qext.get("grade9v3:provenance_class")
        custody = qext.get("grade9v3:source_custody") or {}
        analysis = qext.get("grade9v3:analysis") or {}

        if provenance not in {"PYQ_VERIFIED", "PYQ_ADAPTED"}:
            _fail(findings, "EXAM_BANK_UNVERIFIED_PROMOTED", qid,
                  "canonical questions may not use SOURCE_UNVERIFIED provenance")

        if provenance == "PYQ_ADAPTED":
            if q.get("origin") != "ADAPTED":
                _fail(findings, "EXAM_BANK_ADAPTATION_ORIGIN", qid,
                      "PYQ_ADAPTED must have origin=ADAPTED")
            adaptation = q.get("adaptation") or {}
            if adaptation.get("parent_ref") != q.get("original_identifier"):
                _fail(findings, "EXAM_BANK_ADAPTATION_PARENT", qid,
                      "adaptation.parent_ref must equal original_identifier")
            if "stem" not in (adaptation.get("changed_fields") or []):
                _fail(findings, "EXAM_BANK_ADAPTATION_FIELDS", qid,
                      "non-verbatim restatement must declare stem in changed_fields")
            if custody.get("source_status") != "PYQ_VERIFIED_PARENT":
                _fail(findings, "EXAM_BANK_ADAPTATION_SOURCE_STATUS", qid,
                      "PYQ_ADAPTED requires PYQ_VERIFIED_PARENT custody")
            if custody.get("wording_custody") != "FAITHFUL_NON_VERBATIM_RESTATEMENT":
                _fail(findings, "EXAM_BANK_ADAPTATION_WORDING", qid,
                      "PYQ_ADAPTED requires faithful non-verbatim wording custody")
            if custody.get("parent_ref") != q.get("original_identifier"):
                _fail(findings, "EXAM_BANK_CUSTODY_PARENT", qid,
                      "source_custody.parent_ref must equal original_identifier")

        refs = set(q.get("source_refs") or [])
        if not refs or not refs.issubset(resource_ids):
            _fail(findings, "EXAM_BANK_SOURCE_REF_RESOLUTION", qid,
                  "all source_refs must resolve against bank resources[]")
        if q.get("origin_ref") not in resource_ids:
            _fail(findings, "EXAM_BANK_ORIGIN_REF_RESOLUTION", qid,
                  "origin_ref must resolve against bank resources[]")

        identity = (
            custody.get("exam"), custody.get("year"), custody.get("paper"),
            custody.get("section"), custody.get("question_number"),
        )
        if identity in identities:
            _fail(findings, "EXAM_BANK_DUPLICATE_SOURCE_IDENTITY", qid,
                  f"authoritative source identity is duplicated: {identity}")
        identities.add(identity)

        for key in ("paper_url", "archive_url"):
            host = urlparse(custody.get(key) or "").hostname
            if host not in OFFICIAL_HOSTS:
                _fail(findings, "EXAM_BANK_NONOFFICIAL_SOURCE_HOST", qid,
                      f"{key} host {host!r} is not in the organizer allow-list")

        ledger_record = accepted_by_id.get(qid)
        if not ledger_record:
            _fail(findings, "EXAM_BANK_LEDGER_MISSING", qid,
                  "accepted question is missing from accepted_authoritative_records")
        else:
            if ledger_record.get("source_url") != custody.get("paper_url"):
                _fail(findings, "EXAM_BANK_LEDGER_SOURCE_MISMATCH", qid,
                      "ledger source_url must equal source_custody.paper_url")
            if ledger_record.get("exam") != custody.get("exam") or ledger_record.get("year") != custody.get("year"):
                _fail(findings, "EXAM_BANK_LEDGER_IDENTITY_MISMATCH", qid,
                      "ledger exam/year must equal source custody")

        difficulty = analysis.get("difficulty") or {}
        components = difficulty.get("components") or {}
        if components:
            score = sum(components.values())
            if difficulty.get("score") != score:
                _fail(findings, "EXAM_BANK_DIFFICULTY_SCORE", qid,
                      "difficulty.score must equal the five component scores")
            if DIFFICULTY_BAND.get(score) != difficulty.get("band"):
                _fail(findings, "EXAM_BANK_DIFFICULTY_BAND", qid,
                      "difficulty.band must derive from the component sum")
            exam = custody.get("exam")
            if exam and exam.lower() in str(difficulty.get("basis", "")).lower():
                _fail(findings, "EXAM_BANK_DIFFICULTY_PRESTIGE_LEAK", qid,
                      "difficulty basis must not use the exam label as evidence")

        answer = q.get("answer") or {}
        route = answer.get("reasoning_route") or []
        move_ids = {m.get("id") for m in route if m.get("id")}
        if not route or answer.get("crux_move_ref") not in move_ids:
            _fail(findings, "EXAM_BANK_CRUX_RESOLUTION", qid,
                  "answer.crux_move_ref must resolve inside reasoning_route[]")
        if answer.get("verification_status") != "INDEPENDENTLY_CHECKED":
            _fail(findings, "EXAM_BANK_ANSWER_VERIFICATION", qid,
                  "accepted canonical answer must be independently checked")
        if not str(answer.get("check") or "").strip():
            _fail(findings, "EXAM_BANK_INDEPENDENT_CHECK", qid,
                  "answer.check must be present")

        if q.get("hints") != []:
            _fail(findings, "EXAM_BANK_SOURCE_HINT_CONFLATION", qid,
                  "PASS-1 may not invent source hints; authored help belongs in scaffolds[]")
        for scaffold in q.get("scaffolds") or []:
            if scaffold.get("supports_move_ref") not in move_ids:
                _fail(findings, "EXAM_BANK_SCAFFOLD_MOVE", qid,
                      "scaffold.supports_move_ref must resolve inside reasoning_route[]")

        transfer = analysis.get("transfer_profile") or {}
        if transfer.get("core2b_candidate"):
            if transfer.get("classification") != "REAL_TRANSFER_CANDIDATE" or not transfer.get("dimension"):
                _fail(findings, "EXAM_BANK_TRANSFER_CLASSIFICATION", qid,
                      "Core2B candidate requires REAL_TRANSFER_CANDIDATE and a changed-demand dimension")
        elif transfer.get("classification") != "SAME_FAMILY_VARIATION" or transfer.get("dimension") is not None:
            _fail(findings, "EXAM_BANK_TRANSFER_VARIATION", qid,
                  "non-Core2B items must remain SAME_FAMILY_VARIATION with dimension=null")

        scope_text = " ".join([
            str(analysis.get("topic", "")), str(q.get("stem", "")),
            str(analysis.get("stable_crux_move", "")),
        ]).lower()
        if "circular motion" in scope_text or "centripetal" in scope_text:
            _fail(findings, "EXAM_BANK_SCOPE_LEAK_CIRCULAR", qid,
                  "circular-motion content is outside this PASS-1 scope")

        if custody.get("section") == "Physics":
            if q.get("primary_capability_ref") not in physics_caps:
                _fail(findings, "EXAM_BANK_CAPABILITY_UNRESOLVED", qid,
                      f"Physics capability {q.get('primary_capability_ref')!r} does not resolve")
            for ref in q.get("secondary_capability_refs") or []:
                if ref not in physics_caps:
                    _fail(findings, "EXAM_BANK_CAPABILITY_UNRESOLVED", qid,
                          f"Physics capability {ref!r} does not resolve")
            if q.get("family_ref") not in physics_families:
                _fail(findings, "EXAM_BANK_FAMILY_UNRESOLVED", qid,
                      f"Physics family {q.get('family_ref')!r} does not resolve")
        elif custody.get("section") == "Chemistry":
            refs_to_check = [
                q.get("primary_capability_ref"),
                *(q.get("secondary_capability_refs") or []),
                q.get("family_ref"),
            ]
            for ref in refs_to_check:
                if ref and f"`{ref}`" not in concept_inventory:
                    _fail(findings, "EXAM_BANK_CHEMISTRY_LOCAL_REF_UNRESOLVED", qid,
                          f"Chemistry local proposal {ref!r} is absent from concept-bucket-inventory.md")

    return findings, questions


def check(
    banks: tuple[Path, ...] = DEFAULT_BANKS,
    ledger_path: Path = DEFAULT_LEDGER,
    run_path: Path = DEFAULT_RUN,
) -> dict:
    findings: list[dict] = []
    ledger = load(ledger_path)
    concept_inventory = DEFAULT_CONCEPT_INVENTORY.read_text(encoding="utf-8")
    all_questions: list[dict] = []

    for path in banks:
        bank_findings, questions = _validate_bank(path, ledger, concept_inventory)
        findings += bank_findings
        all_questions += questions

    ids = [q.get("id") for q in all_questions]
    if len(ids) != len(set(ids)):
        _fail(findings, "EXAM_BANK_CROSS_SUBJECT_DUPLICATE_ID", "banks",
              "question ids must be unique across all subject banks")

    accepted_ids = {
        qid
        for record in ledger.get("accepted_authoritative_records", [])
        for qid in record.get("accepted_question_ids", [])
    }
    if accepted_ids != set(ids):
        _fail(findings, "EXAM_BANK_LEDGER_CLOSURE", _where(ledger_path),
              "ledger accepted_question_ids must equal the canonical bank question id set")
    if ledger.get("accepted_question_count") != len(ids) or ledger.get("accepted_item_count") != len(ids):
        _fail(findings, "EXAM_BANK_LEDGER_COUNT", _where(ledger_path),
              "ledger accepted counts must equal canonical bank size")

    for donor in ledger.get("donor_candidates", []):
        if donor.get("pass1_provenance_status") != "SOURCE_UNVERIFIED":
            _fail(findings, "EXAM_BANK_DONOR_PROVENANCE", donor.get("candidate_id", "<missing>"),
                  "donor candidates must remain SOURCE_UNVERIFIED until independently promoted")
        if donor.get("promotion_status") != "QUARANTINED_DONOR_ONLY":
            _fail(findings, "EXAM_BANK_DONOR_DISPOSITION", donor.get("candidate_id", "<missing>"),
                  "unverified donor candidates must remain quarantined")

    run = load(run_path)
    findings += _schema_findings(run, RUN_SCHEMA, "EXAM_BANK_RUN_SCHEMA", _where(run_path))
    publication = run.get("publication_contract") or {}
    findings += _schema_findings(
        publication, PUBLICATION_SCHEMA, "EXAM_BANK_PUBLICATION_SCHEMA",
        f"{_where(run_path)}#publication_contract",
    )

    gates = run.get("gates") or []
    gate_ids = [g.get("id") for g in gates]
    if set(gate_ids) != EXPECTED_GATES or len(gate_ids) != len(EXPECTED_GATES):
        _fail(findings, "EXAM_BANK_GATE_SET", _where(run_path),
              "run manifest must contain each G0-G8 gate exactly once")

    completion = run.get("completion") or {}
    if completion.get("status") == "PASS":
        not_pass = [g.get("id") for g in gates if g.get("status") != "PASS"]
        if not_pass:
            _fail(findings, "EXAM_BANK_RUN_FALSE_PASS", _where(run_path),
                  f"completion=PASS but gates are not PASS: {not_pass}")
        if completion.get("accepted_count") != len(ids):
            _fail(findings, "EXAM_BANK_RUN_COUNT", _where(run_path),
                  "completion.accepted_count must equal the canonical question count")
        if completion.get("source_identity_duplicates") != 0 or completion.get("unresolved_accepted_items") != 0:
            _fail(findings, "EXAM_BANK_RUN_UNRESOLVED", _where(run_path),
                  "completion PASS requires zero duplicate source identities and zero unresolved accepted items")

    return {
        "passed": not findings,
        "banks_checked": len(banks),
        "questions_checked": len(all_questions),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    result = check()
    if args.as_json:
        print(json.dumps(result, indent=2))
    elif result["passed"]:
        print(f"PASS: {result['questions_checked']} questions across {result['banks_checked']} banks")
    else:
        print(f"FAIL: {len(result['findings'])} finding(s)")
        for finding in result["findings"]:
            print(f"- {finding['point']} | {finding['where']} | {finding['detail']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
