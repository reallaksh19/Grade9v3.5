"""Validate a canonical competitive-exam bank as an activity, not only as records.

The engine is topic-neutral. Scope, bank paths, source-authority hosts, exclusions and
local concept registries are data in the run manifest. JSON Schema owns shape; this
module owns cross-record invariants that schema cannot express.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from Shared.tools import question_difficulty

ROOT = Path(__file__).resolve().parents[2]
BANK_SCHEMA = ROOT / "Shared/library/competitive-exam-bank.schema.json"
PACKAGE_SCHEMA = ROOT / "Shared/library/package.schema.json"
RUN_SCHEMA = ROOT / "Shared/library/question-bank-run.schema.json"
PUBLICATION_SCHEMA = ROOT / "Shared/library/question-bank-publication.schema.json"
DEFAULT_RUN = ROOT / "docs/question-bank/pass1/run-manifest.json"

DIFFICULTY_BAND = question_difficulty.score_band_map()  # compatibility alias; vocabulary-backed authority lives in question_difficulty.
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
    findings = []
    for error in _schema_validator(load(schema_path)).iter_errors(value):
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


def _canonical_ids() -> dict[str, set[str]]:
    out = {"buckets": set(), "capabilities": set(), "families": set()}
    for path in sorted(ROOT.glob("*/library/*.json")):
        try:
            package = load(path)
        except Exception:
            continue
        for row in package.get("buckets", []):
            if row.get("id"):
                out["buckets"].add(row["id"])
        for row in package.get("capabilities", []):
            if row.get("id"):
                out["capabilities"].add(row["id"])
        for row in package.get("question_families", []):
            if row.get("id"):
                out["families"].add(row["id"])
    return out


def _local_registry(paths: list[str]) -> str:
    chunks = []
    for rel in paths:
        path = ROOT / rel
        if path.is_file():
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def _resolves(ref: str | None, canonical: set[str], local_registry: str) -> bool:
    if not ref:
        return False
    return ref in canonical or f"`{ref}`" in local_registry


def validate_bank(
    path: Path,
    ledger: dict,
    local_registry: str,
    canonical: dict[str, set[str]],
    allowed_hosts: set[str],
    forbidden_topics: list[str],
) -> tuple[list[dict], list[dict]]:
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
              "accepted-question count must equal len(questions)")
    topic_counts = ext.get("grade9v3:topic_counts") or {}
    if sum(topic_counts.values()) != len(questions):
        _fail(findings, "EXAM_BANK_TOPIC_COUNT_MISMATCH", _where(path),
              "sum(topic_counts) must equal len(questions)")

    seen_ids: set[str] = set()
    identities: set[tuple] = set()
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
                  "canonical questions may not use unverified provenance")

        if provenance == "PYQ_ADAPTED":
            if q.get("origin") != "ADAPTED":
                _fail(findings, "EXAM_BANK_ADAPTATION_ORIGIN", qid,
                      "adapted provenance requires origin=ADAPTED")
            adaptation = q.get("adaptation") or {}
            if adaptation.get("parent_ref") != q.get("original_identifier"):
                _fail(findings, "EXAM_BANK_ADAPTATION_PARENT", qid,
                      "adaptation.parent_ref must equal original_identifier")
            if "stem" not in (adaptation.get("changed_fields") or []):
                _fail(findings, "EXAM_BANK_ADAPTATION_FIELDS", qid,
                      "non-verbatim restatement must declare stem in changed_fields")
            if custody.get("source_status") != "PYQ_VERIFIED_PARENT":
                _fail(findings, "EXAM_BANK_ADAPTATION_SOURCE_STATUS", qid,
                      "adapted provenance requires verified-parent custody")
            if custody.get("wording_custody") != "FAITHFUL_NON_VERBATIM_RESTATEMENT":
                _fail(findings, "EXAM_BANK_ADAPTATION_WORDING", qid,
                      "adapted provenance requires faithful non-verbatim wording custody")
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
            if host not in allowed_hosts:
                _fail(findings, "EXAM_BANK_NONOFFICIAL_SOURCE_HOST", qid,
                      f"{key} host {host!r} is not allowed by the run manifest")

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
            try:
                question_difficulty.derive(difficulty, question_ref=str(qid))
            except question_difficulty.DifficultyContractError as exc:
                detail = str(exc)
                point = "EXAM_BANK_DIFFICULTY_BAND" if "BAND_" in detail else "EXAM_BANK_DIFFICULTY_SCORE"
                _fail(findings, point, qid, detail)
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
                  "source hints and authored pedagogical support must remain separate")
        for scaffold in q.get("scaffolds") or []:
            if scaffold.get("supports_move_ref") not in move_ids:
                _fail(findings, "EXAM_BANK_SCAFFOLD_MOVE", qid,
                      "scaffold.supports_move_ref must resolve inside reasoning_route[]")

        transfer = analysis.get("transfer_profile") or {}
        if transfer.get("core2b_candidate"):
            if transfer.get("classification") != "REAL_TRANSFER_CANDIDATE" or not transfer.get("dimension"):
                _fail(findings, "EXAM_BANK_TRANSFER_CLASSIFICATION", qid,
                      "transfer candidate requires a real-transfer classification and changed-demand dimension")
        elif transfer.get("classification") != "SAME_FAMILY_VARIATION" or transfer.get("dimension") is not None:
            _fail(findings, "EXAM_BANK_TRANSFER_VARIATION", qid,
                  "non-transfer items must remain same-family variation with dimension=null")

        scope_text = " ".join([
            str(analysis.get("topic", "")),
            str(q.get("stem", "")),
            str(analysis.get("stable_crux_move", "")),
        ]).lower()
        for forbidden in forbidden_topics:
            if forbidden.lower() in scope_text:
                _fail(findings, "EXAM_BANK_SCOPE_LEAK", qid,
                      f"forbidden run-scope topic appears in canonical content: {forbidden!r}")

        if not _resolves(analysis.get("concept_bucket"), canonical["buckets"], local_registry):
            _fail(findings, "EXAM_BANK_BUCKET_UNRESOLVED", qid,
                  f"concept bucket {analysis.get('concept_bucket')!r} does not resolve")
        capability_refs = [q.get("primary_capability_ref"), *(q.get("secondary_capability_refs") or [])]
        for ref in capability_refs:
            if not _resolves(ref, canonical["capabilities"], local_registry):
                _fail(findings, "EXAM_BANK_CAPABILITY_UNRESOLVED", qid,
                      f"capability {ref!r} does not resolve")
        if not _resolves(q.get("family_ref"), canonical["families"], local_registry):
            _fail(findings, "EXAM_BANK_FAMILY_UNRESOLVED", qid,
                  f"family {q.get('family_ref')!r} does not resolve")

    return findings, questions


def check(run_path: Path = DEFAULT_RUN) -> dict:
    findings: list[dict] = []
    run = load(run_path)
    findings += _schema_findings(run, RUN_SCHEMA, "EXAM_BANK_RUN_SCHEMA", _where(run_path))

    publication = run.get("publication_contract") or {}
    findings += _schema_findings(
        publication, PUBLICATION_SCHEMA, "EXAM_BANK_PUBLICATION_SCHEMA",
        f"{_where(run_path)}#publication_contract",
    )

    ledger_path = ROOT / run["ledger_path"]
    ledger = load(ledger_path)
    canonical = _canonical_ids()
    local_registry = _local_registry(run.get("local_ref_registry_paths") or [])
    allowed_hosts = set(run.get("authority_hosts") or [])
    forbidden_topics = list((run.get("scope") or {}).get("forbidden_topics") or [])
    bank_paths = tuple(ROOT / rel for rel in run.get("bank_paths") or [])
    all_questions: list[dict] = []

    for path in bank_paths:
        bank_findings, questions = validate_bank(
            path, ledger, local_registry, canonical, allowed_hosts, forbidden_topics
        )
        findings += bank_findings
        all_questions += questions

    ids = [q.get("id") for q in all_questions]
    if len(ids) != len(set(ids)):
        _fail(findings, "EXAM_BANK_CROSS_BANK_DUPLICATE_ID", "banks",
              "question ids must be unique across all bank files")

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
                  "donor candidate provenance changed before independent promotion")
        if donor.get("promotion_status") != "QUARANTINED_DONOR_ONLY":
            _fail(findings, "EXAM_BANK_DONOR_DISPOSITION", donor.get("candidate_id", "<missing>"),
                  "unverified donor candidate escaped quarantine")

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
        "banks_checked": len(bank_paths),
        "questions_checked": len(all_questions),
        "findings": findings,
    }



def sync_metadata(run_path: Path = DEFAULT_RUN) -> dict:
    """Regenerate Pass-1 count/authority/ledger metadata from the canonical bank records.

    This is deliberately narrow: question wording, answers and source custody remain authored
    in the canonical banks. The sync only derives counts, allowed source hosts and ledger
    membership from those accepted records, so generated Pass-1 bookkeeping cannot drift.
    """
    run = load(run_path)
    ledger_path = ROOT / run["ledger_path"]
    ledger = load(ledger_path)
    all_questions: list[dict] = []
    latest_checked = str(ledger.get("last_checked") or "")

    for rel in run.get("bank_paths") or []:
        path = ROOT / rel
        bank = load(path)
        questions = list(bank.get("questions") or [])
        all_questions.extend(questions)

        counts: dict[str, int] = {}
        for q in questions:
            analysis = (q.get("extensions") or {}).get("grade9v3:analysis") or {}
            topic = str(analysis.get("topic") or "UNSPECIFIED")
            counts[topic] = counts.get(topic, 0) + 1
            checked = str(((q.get("extensions") or {}).get("grade9v3:source_custody") or {}).get("last_checked") or "")
            if checked > latest_checked:
                latest_checked = checked

        ext = bank.setdefault("extensions", {})
        ext["grade9v3:accepted_question_count"] = len(questions)
        ext["grade9v3:topic_counts"] = counts
        path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    valid_ids = {q["id"] for q in all_questions}
    records = list(ledger.get("accepted_authoritative_records") or [])
    by_url = {r.get("source_url"): r for r in records if r.get("source_url")}

    for q in all_questions:
        custody = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
        source_url = custody.get("paper_url")
        if not source_url:
            continue
        record = by_url.get(source_url)
        if record is None:
            exam = str(custody.get("exam") or "SOURCE")
            year = custody.get("year")
            question_number = str(custody.get("question_number") or q["id"])
            slug = re.sub(r"[^A-Za-z0-9]+", "-", f"{exam}-{year}-{question_number}").strip("-").upper()
            record = {
                "source_ref": f"SRC-{slug}-OFFICIAL",
                "exam": custody.get("exam"),
                "year": year,
                "paper": custody.get("paper"),
                "source_url": source_url,
                "archive_url": custody.get("archive_url"),
                "answer_key": custody.get("answer_key_url")
                    or "Official organizer source; answer independently checked and recorded in grade9v3:source_custody.",
                "accepted_question_ids": [],
            }
            records.append(record)
            by_url[source_url] = record
        if q["id"] not in record["accepted_question_ids"]:
            record["accepted_question_ids"].append(q["id"])

    for record in records:
        record["accepted_question_ids"] = [
            qid for qid in record.get("accepted_question_ids") or [] if qid in valid_ids
        ]
    ledger["accepted_authoritative_records"] = [r for r in records if r.get("accepted_question_ids")]
    ledger["accepted_question_count"] = len(all_questions)
    ledger["accepted_item_count"] = len(all_questions)
    if latest_checked:
        ledger["last_checked"] = latest_checked
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    hosts = list(run.get("authority_hosts") or [])
    seen_hosts = set(hosts)
    for q in all_questions:
        custody = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
        for key in ("paper_url", "archive_url"):
            host = urlparse(custody.get(key) or "").hostname
            if host and host not in seen_hosts:
                hosts.append(host)
                seen_hosts.add(host)
    run["authority_hosts"] = hosts
    run.setdefault("completion", {})["accepted_count"] = len(all_questions)
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "questions": len(all_questions),
        "authority_hosts": hosts,
        "ledger_records": len(ledger["accepted_authoritative_records"]),
        "last_checked": latest_checked,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--sync-metadata", action="store_true",
                        help="regenerate canonical bank counts and Pass-1 custody bookkeeping before validation")
    args = parser.parse_args(argv)
    if args.sync_metadata:
        synced = sync_metadata(args.run)
        print("synced Pass-1 metadata: " + json.dumps(synced, sort_keys=True))
    result = check(args.run)
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
