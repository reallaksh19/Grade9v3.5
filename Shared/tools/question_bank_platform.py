#!/usr/bin/env python3
"""Subject-neutral Question Bank growth contracts for catalog, search, dedup and lineage.

This module deliberately owns no curriculum names. Subject/topic variation is input data.
It consumes the existing canonical browser projection contract and can also normalize
package-shaped questions when a canonical package explicitly opts into Question Bank
publication through ``extensions.grade9v3:question_bank``.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

PLATFORM_SCHEMA = "grade9v3-question-bank-platform-v1"
CATALOG_SCHEMA = "grade9v3-question-bank-catalog-v1"
SEARCH_SCHEMA = "grade9v3-question-bank-search-v1"
RESOURCE_SCHEMA = "grade9v3-question-bank-resources-v1"
DEDUP_SCHEMA = "grade9v3-question-bank-dedup-v1"
LINEAGE_SCHEMA = "grade9v3-question-bank-lineage-v1"
RECEIPT_SCHEMA = "grade9v3-question-bank-build-receipt-v1"
WORKER_CONTRACT_VERSION = "1.0.0"

_TOKEN = re.compile(r"[a-z0-9]+")
_SPACE = re.compile(r"\s+")
_LATEX_DELIMS = re.compile(r"(?:\\\(|\\\)|\\\[|\\\]|\$\$|\$)")
_PUNCT = re.compile(r"[^a-z0-9]+")


class ProjectionError(ValueError):
    """Fail-closed error for contradictory machine identity or malformed opt-in data."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: object) -> str:
    raw = value if isinstance(value, str) else canonical_json(value)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def slug(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    parts = _TOKEN.findall(text)
    return "-".join(parts) or "unknown"


def subject_ref(label: str, explicit: str | None = None) -> str:
    return explicit or f"SUBJECT-{slug(label).upper()}"


def topic_ref(subject: str, label: str, explicit: str | None = None) -> str:
    return explicit or f"TOPIC-{slug(subject).upper()}-{slug(label).upper()}"


def normalize_content(value: object) -> str:
    """Deterministic presentation-insensitive text normalization for duplicate evidence."""
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = _LATEX_DELIMS.sub(" ", text)
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = _PUNCT.sub(" ", text)
    return _SPACE.sub(" ", text).strip()


def tokenize(value: object) -> tuple[str, ...]:
    return tuple(_TOKEN.findall(normalize_content(value)))


def _option_text(option: object) -> str:
    if isinstance(option, Mapping):
        return str(option.get("text") or option.get("label") or option.get("id") or "")
    return str(option or "")


def _answer_summary(question: Mapping[str, object]) -> str:
    answer = question.get("answer") or {}
    return str(answer.get("summary") or "") if isinstance(answer, Mapping) else ""


def normalized_exact_fingerprint(question: Mapping[str, object]) -> str:
    payload = {
        "stem": normalize_content(question.get("stem")),
        "subparts": [normalize_content(x) for x in question.get("subparts", []) or []],
        "options": [normalize_content(_option_text(x)) for x in question.get("options", []) or []],
        "conditions": [normalize_content(x) for x in question.get("conditions", []) or []],
    }
    return digest(payload)


def structural_fingerprint(question: Mapping[str, object]) -> str:
    payload = {
        "stem": normalize_content(question.get("stem")),
        "question_type": normalize_content(question.get("question_type")),
        "options": [normalize_content(_option_text(x)) for x in question.get("options", []) or []],
        "answer": normalize_content(_answer_summary(question)),
    }
    return digest(payload)


def source_identity(question: Mapping[str, object]) -> tuple[str, ...] | None:
    fields = ("exam", "year", "paper", "question_number")
    values = tuple(str(question.get(k) or "").strip() for k in fields)
    return values if all(values) else None


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def compare_pair(left: Mapping[str, object], right: Mapping[str, object]) -> dict:
    """Classify one pair without deleting or merging either record."""
    lid, rid = str(left.get("id")), str(right.get("id"))
    if lid == rid:
        same = structural_fingerprint(left) == structural_fingerprint(right)
        return {
            "classification": "DUPLICATE" if same else "SOURCE_COLLISION",
            "reason": "same_canonical_id_same_structure" if same else "same_canonical_id_conflict",
            "score": 1.0,
        }

    lsrc, rsrc = source_identity(left), source_identity(right)
    if lsrc and lsrc == rsrc:
        same = structural_fingerprint(left) == structural_fingerprint(right)
        return {
            "classification": "DUPLICATE" if same else "SOURCE_COLLISION",
            "reason": "same_source_identity_same_structure" if same else "same_source_identity_conflict",
            "score": 1.0,
        }

    if normalized_exact_fingerprint(left) == normalized_exact_fingerprint(right):
        return {"classification": "DUPLICATE", "reason": "normalized_exact_content", "score": 1.0}

    lfam, rfam = left.get("family_ref"), right.get("family_ref")
    if lfam and lfam == rfam:
        return {"classification": "VARIANT", "reason": "explicit_family_ref", "score": 1.0}

    similarity = _jaccard(tokenize(left.get("stem")), tokenize(right.get("stem")))
    if similarity >= 0.82:
        return {"classification": "NEAR_DUPLICATE", "reason": "stem_token_jaccard", "score": round(similarity, 6)}

    return {"classification": "DISTINCT", "reason": "no_duplicate_signal", "score": round(similarity, 6)}


def validate_unique_ids(questions: Sequence[Mapping[str, object]]) -> None:
    by_id: dict[str, Mapping[str, object]] = {}
    for question in questions:
        qid = str(question.get("id") or "")
        if not qid:
            raise ProjectionError("Question Bank projection contains a record without canonical id")
        previous = by_id.get(qid)
        if previous is not None:
            result = compare_pair(previous, question)
            raise ProjectionError(
                f"Question Bank projection contains duplicate canonical id {qid}: "
                f"{result['classification']} ({result['reason']})"
            )
        by_id[qid] = question


def build_dedup_report(questions: Sequence[Mapping[str, object]]) -> dict:
    validate_unique_ids(questions)
    relationships: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    def emit(left: Mapping[str, object], right: Mapping[str, object], result: dict) -> None:
        key = tuple(sorted((str(left["id"]), str(right["id"]))))
        if key in seen_pairs or result["classification"] == "DISTINCT":
            return
        seen_pairs.add(key)
        relationships.append({
            "left_id": key[0],
            "right_id": key[1],
            **result,
        })

    exact: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    sources: dict[tuple[str, ...], list[Mapping[str, object]]] = defaultdict(list)
    families: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    topical: dict[tuple[str, str], list[Mapping[str, object]]] = defaultdict(list)

    for question in questions:
        exact[normalized_exact_fingerprint(question)].append(question)
        src = source_identity(question)
        if src:
            sources[src].append(question)
        fam = str(question.get("family_ref") or "")
        if fam:
            families[fam].append(question)
        topical[(str(question.get("subject_ref") or question.get("subject") or ""),
                 str(question.get("topic_ref") or question.get("topic") or ""))].append(question)

    for groups in (exact.values(), sources.values(), families.values()):
        for group in groups:
            for i, left in enumerate(group):
                for right in group[i + 1:]:
                    emit(left, right, compare_pair(left, right))

    for group in topical.values():
        ordered = sorted(group, key=lambda q: str(q["id"]))
        for i, left in enumerate(ordered):
            ltokens = tokenize(left.get("stem"))
            for right in ordered[i + 1:]:
                rtokens = tokenize(right.get("stem"))
                if max(len(ltokens), len(rtokens), 1) > 2 * max(min(len(ltokens), len(rtokens)), 1):
                    continue
                emit(left, right, compare_pair(left, right))

    relationships.sort(key=lambda row: (row["left_id"], row["right_id"], row["classification"]))
    counts = dict(sorted(Counter(row["classification"] for row in relationships).items()))
    return {
        "schema_version": DEDUP_SCHEMA,
        "authority": "EVIDENCE_ONLY_NO_SILENT_DELETION",
        "question_count": len(questions),
        "relationship_counts": counts,
        "relationships": relationships,
    }


def _projection_refs(question: Mapping[str, object]) -> tuple[str, str]:
    subject = str(question.get("subject") or "")
    topic = str(question.get("topic") or "")
    explicit_subject = question.get("subject_ref")
    explicit_topic = question.get("topic_ref")
    return subject_ref(subject, str(explicit_subject) if explicit_subject else None), topic_ref(
        subject, topic, str(explicit_topic) if explicit_topic else None
    )


def enrich_question_refs(question: Mapping[str, object]) -> dict:
    sref, tref = _projection_refs(question)
    out = dict(question)
    out["subject_ref"] = sref
    out["topic_ref"] = tref
    subtopics = list(question.get("subtopic_refs") or [])
    if not subtopics and question.get("primary_capability_ref"):
        subtopics = [str(question["primary_capability_ref"])] + [
            str(x) for x in question.get("secondary_capability_refs", []) or []
        ]
    out["subtopic_refs"] = list(dict.fromkeys(subtopics))
    return out


def _resource_scope(resource: Mapping[str, object], fallback_subject: str | None = None) -> dict:
    subject = str(resource.get("subject") or fallback_subject or "")
    topic = str(resource.get("topic") or resource.get("topic_label") or "")
    explicit_subject = resource.get("subject_ref")
    explicit_topic = resource.get("topic_ref")
    out = dict(resource)
    if subject:
        out["subject"] = subject
        out["subject_ref"] = subject_ref(subject, str(explicit_subject) if explicit_subject else None)
    if topic:
        out["topic"] = topic
        out["topic_ref"] = topic_ref(subject, topic, str(explicit_topic) if explicit_topic else None)
    out["subtopic_refs"] = list(resource.get("subtopic_refs") or [])
    out["keywords"] = sorted({slug(x).replace("-", " ") for x in resource.get("keywords", []) or [] if str(x).strip()})
    return out


def load_resource_registries(repo: Path) -> tuple[list[dict], list[dict]]:
    resources: list[dict] = []
    basis: list[dict] = []
    for path in sorted(repo.glob("*/question-bank/resources.v1.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("schema_version") != RESOURCE_SCHEMA:
            raise ProjectionError(f"Unsupported resource registry schema in {path.relative_to(repo)}")
        fallback_subject = path.relative_to(repo).parts[0]
        rows = doc.get("resources") or []
        for row in rows:
            if not all(row.get(k) for k in ("id", "kind", "title", "path")):
                raise ProjectionError(f"Malformed resource record in {path.relative_to(repo)}: {row}")
            resources.append(_resource_scope(row, fallback_subject))
        basis.append({
            "path": path.relative_to(repo).as_posix(),
            "digest": digest(doc),
            "resource_count": len(rows),
        })
    ids = [str(row["id"]) for row in resources]
    if len(ids) != len(set(ids)):
        raise ProjectionError("Question Bank resource registries contain duplicate resource ids")
    return sorted(resources, key=lambda row: (str(row.get("order", 0)), str(row["id"]))), basis


def load_gcdr_suite_resources(repo: Path) -> tuple[list[dict], list[dict]]:
    """Project GCDR suite delivery records as searchable resources without topic branches."""
    resources: list[dict] = []
    basis: list[dict] = []
    suites_dir = repo / "docs" / "gcdr-suites"
    if not suites_dir.is_dir():
        return resources, basis
    for path in sorted(suites_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        title = doc.get("title")
        artifacts = doc.get("delivery_artifacts") or []
        bundle = next(
            (row for row in artifacts if isinstance(row, Mapping) and row.get("profile") == "REPO_BUNDLE" and row.get("locator")),
            None,
        )
        if not title or not bundle:
            continue
        locator = str(bundle["locator"])
        public_path = locator[7:] if locator.startswith("public/") else locator
        path_parts = Path(public_path).parts
        if not path_parts:
            continue
        subject = str((doc.get("external_corpus") or {}).get("subject") or path_parts[0]).replace("-", " ").title()
        topic = str((doc.get("external_corpus") or {}).get("topic") or "")
        suite_id = str(doc.get("suite_id") or f"RES-GCDR-{slug(title).upper()}")
        keywords = sorted(set(_TOKEN.findall(normalize_content(
            " ".join([title, topic, suite_id, "explorer interactive suite"])
        ))))
        resources.append(_resource_scope({
            "id": suite_id,
            "kind": "explorer",
            "title": title,
            "subject": subject,
            "topic": topic,
            "path": public_path,
            "keywords": keywords,
            "source_record": path.relative_to(repo).as_posix(),
        }))
        basis.append({
            "path": path.relative_to(repo).as_posix(),
            "digest": digest(doc),
            "resource_count": 1,
        })
    return resources, basis


def load_resources(repo: Path) -> tuple[list[dict], list[dict]]:
    registry_resources, registry_basis = load_resource_registries(repo)
    suite_resources, suite_basis = load_gcdr_suite_resources(repo)
    rows = registry_resources + suite_resources
    ids = [str(row["id"]) for row in rows]
    if len(ids) != len(set(ids)):
        duplicates = sorted(k for k, count in Counter(ids).items() if count > 1)
        raise ProjectionError(f"Question Bank resources contain duplicate ids: {duplicates}")
    rows.sort(key=lambda row: (str(row.get("subject_ref") or ""), str(row.get("topic_ref") or ""), str(row.get("order", 0)), str(row["id"])))
    return rows, registry_basis + suite_basis


def build_catalog(questions: Sequence[Mapping[str, object]], resources: Sequence[Mapping[str, object]] = ()) -> dict:
    enriched = [enrich_question_refs(q) for q in questions]
    subject_rows: dict[str, dict] = {}
    topic_rows: dict[str, dict] = {}
    subtopic_rows: dict[str, dict] = {}

    for q in enriched:
        sref, tref = q["subject_ref"], q["topic_ref"]
        subject_rows.setdefault(sref, {"id": sref, "label": q["subject"], "question_count": 0, "resource_count": 0})
        subject_rows[sref]["question_count"] += 1
        topic_rows.setdefault(tref, {
            "id": tref,
            "subject_ref": sref,
            "label": q["topic"],
            "question_count": 0,
            "resource_count": 0,
            "identity_basis": "EXPLICIT_REF" if q.get("topic_ref") and q.get("topic_ref") != topic_ref(q["subject"], q["topic"]) else "LEGACY_LABEL_DERIVED",
        })
        topic_rows[tref]["question_count"] += 1
        for ref in q.get("subtopic_refs", []):
            subtopic_rows.setdefault(ref, {
                "id": ref,
                "subject_ref": sref,
                "topic_ref": tref,
                "label": ref,
                "question_count": 0,
            })
            subtopic_rows[ref]["question_count"] += 1

    for raw in resources:
        r = _resource_scope(raw)
        sref, tref = r.get("subject_ref"), r.get("topic_ref")
        if sref:
            subject_rows.setdefault(sref, {"id": sref, "label": r.get("subject", sref), "question_count": 0, "resource_count": 0})
            subject_rows[sref]["resource_count"] += 1
        if tref:
            topic_rows.setdefault(tref, {
                "id": tref,
                "subject_ref": sref,
                "label": r.get("topic", tref),
                "question_count": 0,
                "resource_count": 0,
                "identity_basis": "EXPLICIT_REF" if raw.get("topic_ref") else "LEGACY_LABEL_DERIVED",
            })
            topic_rows[tref]["resource_count"] += 1

    subjects = sorted(subject_rows.values(), key=lambda row: (str(row["label"]).casefold(), row["id"]))
    topics = sorted(topic_rows.values(), key=lambda row: (row.get("subject_ref") or "", str(row["label"]).casefold(), row["id"]))
    subtopics = sorted(subtopic_rows.values(), key=lambda row: (row.get("topic_ref") or "", row["id"]))
    return {
        "schema_version": CATALOG_SCHEMA,
        "counts": {
            "questions": len(enriched),
            "resources": len(resources),
            "subjects": len(subjects),
            "topics": len(topics),
            "subtopics": len(subtopics),
        },
        "subjects": subjects,
        "topics": topics,
        "subtopics": subtopics,
    }


def _search_text(parts: Iterable[object]) -> str:
    return " ".join(x for x in (normalize_content(part) for part in parts) if x)


def build_search_index(questions: Sequence[Mapping[str, object]], resources: Sequence[Mapping[str, object]] = ()) -> dict:
    documents: list[dict] = []
    for raw in questions:
        q = enrich_question_refs(raw)
        parts: list[object] = [
            q.get("id"), q.get("subject"), q.get("topic"), q.get("exam"), q.get("year"), q.get("paper"),
            q.get("question_type"), q.get("stem"), q.get("primary_capability_ref"), q.get("family_ref"),
            q.get("stable_crux_move"), " ".join(q.get("secondary_capability_refs", []) or []),
        ]
        documents.append({
            "id": q["id"],
            "kind": "question",
            "subject_ref": q["subject_ref"],
            "topic_ref": q["topic_ref"],
            "subtopic_refs": q.get("subtopic_refs", []),
            "label": q.get("stem") or q["id"],
            "difficulty": (q.get("difficulty") or {}).get("band") if isinstance(q.get("difficulty"), Mapping) else None,
            "search_text": _search_text(parts),
        })
    for raw in resources:
        r = _resource_scope(raw)
        parts = [r.get("id"), r.get("title"), r.get("kind"), r.get("subject"), r.get("topic"), " ".join(r.get("keywords", []))]
        documents.append({
            "id": r["id"],
            "kind": "resource",
            "subject_ref": r.get("subject_ref"),
            "topic_ref": r.get("topic_ref"),
            "subtopic_refs": r.get("subtopic_refs", []),
            "label": r["title"],
            "path": r["path"],
            "resource_kind": r["kind"],
            "search_text": _search_text(parts),
        })
    documents.sort(key=lambda row: (row["kind"], str(row["id"])))
    return {"schema_version": SEARCH_SCHEMA, "document_count": len(documents), "documents": documents}


def search(index: Mapping[str, object], query: str, *, kind: str | None = None,
           subject: str | None = None, topic: str | None = None) -> list[dict]:
    terms = tokenize(query)
    out: list[dict] = []
    for doc in index.get("documents", []) or []:
        if kind and doc.get("kind") != kind:
            continue
        if subject and doc.get("subject_ref") != subject:
            continue
        if topic and doc.get("topic_ref") != topic:
            continue
        hay = str(doc.get("search_text") or "")
        if terms and not all(term in hay for term in terms):
            continue
        out.append(dict(doc))
    return out


def _package_qbank_config(package: Mapping[str, object], question: Mapping[str, object]) -> Mapping[str, object] | None:
    pext = package.get("extensions") or {}
    qext = question.get("extensions") or {}
    pcfg = pext.get("grade9v3:question_bank") if isinstance(pext, Mapping) else None
    qcfg = qext.get("grade9v3:question_bank") if isinstance(qext, Mapping) else None
    config: dict = {}
    if isinstance(pcfg, Mapping):
        config.update(pcfg)
    if isinstance(qcfg, Mapping):
        config.update(qcfg)
    return config if config.get("include") is True else None


def project_package_question(package: Mapping[str, object], question: Mapping[str, object], order: int = 0) -> dict | None:
    """Normalize one explicitly opted-in Shared package question without subject branching."""
    config = _package_qbank_config(package, question)
    if config is None:
        return None
    extensions = question.get("extensions") or {}
    analysis = extensions.get("grade9v3:analysis") if isinstance(extensions, Mapping) else None
    custody = extensions.get("grade9v3:source_custody") if isinstance(extensions, Mapping) else None
    analysis = analysis if isinstance(analysis, Mapping) else {}
    custody = custody if isinstance(custody, Mapping) else {}
    difficulty = analysis.get("difficulty") or config.get("difficulty")
    qtype = analysis.get("learner_question_type") or config.get("question_type")
    expected = analysis.get("expected_time_seconds") or config.get("expected_time_seconds")
    if not isinstance(difficulty, Mapping) or not difficulty.get("band") or qtype is None or expected is None:
        raise ProjectionError(f"Opted-in package question {question.get('id')} lacks browser metadata")

    subject = str(package.get("subject") or "")
    package_id = str(package.get("package_id") or "")
    topic_label = str(config.get("topic_label") or package.get("title") or package_id)
    tref = str(config.get("topic_ref") or package_id)
    if not subject or not package_id or not topic_label or not tref:
        raise ProjectionError(f"Opted-in package question {question.get('id')} lacks stable package/topic identity")
    answer = question.get("answer") or {}
    if not isinstance(answer, Mapping):
        raise ProjectionError(f"Opted-in package question {question.get('id')} has malformed answer")
    return {
        "id": question["id"],
        "order": order,
        "subject": subject,
        "subject_ref": str(config.get("subject_ref") or subject_ref(subject)),
        "topic": topic_label,
        "topic_ref": tref,
        "subtopic_refs": list(config.get("subtopic_refs") or ([question.get("primary_capability_ref")] if question.get("primary_capability_ref") else [])),
        "version": question.get("version"),
        "status": question.get("status"),
        "question_type": qtype,
        "exam": custody.get("exam") or config.get("exam") or "",
        "year": custody.get("year") or config.get("year") or "",
        "paper": custody.get("paper") or config.get("paper") or "",
        "question_number": custody.get("question_number") or config.get("question_number") or str(order + 1),
        "source_status": custody.get("source_status") or config.get("source_status") or "PACKAGE_CANONICAL",
        "authority_class": custody.get("authority_class") or config.get("authority_class") or "PACKAGE_DECLARED",
        "wording_custody": custody.get("wording_custody") or config.get("wording_custody") or "PACKAGE_DECLARED",
        "paper_url": custody.get("paper_url") or config.get("paper_url"),
        "answer_key_url": custody.get("answer_key_url") or config.get("answer_key_url"),
        "last_checked": custody.get("last_checked") or config.get("last_checked"),
        "origin": question.get("origin"),
        "provenance_class": extensions.get("grade9v3:provenance_class"),
        "math_spans": extensions.get("grade9v3:math_spans", []),
        "stem": question.get("stem", ""),
        "subparts": question.get("subparts", []),
        "options": question.get("options", []),
        "conditions": question.get("conditions", []),
        "difficulty": dict(difficulty),
        "expected_time_seconds": expected,
        "common_wrong_route": analysis.get("common_wrong_route") or config.get("common_wrong_route") or "",
        "stable_crux_move": analysis.get("stable_crux_move") or config.get("stable_crux_move") or "",
        "primary_capability_ref": question.get("primary_capability_ref"),
        "secondary_capability_refs": question.get("secondary_capability_refs", []),
        "family_ref": question.get("family_ref"),
        "source_hints": question.get("hints", []),
        "scaffolds": question.get("scaffolds", []),
        "answer": {
            "summary": answer.get("summary", ""),
            "reasoning": answer.get("reasoning", []),
            "reasoning_route": answer.get("reasoning_route", []),
            "crux_move_ref": answer.get("crux_move_ref"),
            "check": answer.get("check", ""),
            "verification_status": answer.get("verification_status"),
        },
        "visual_ref": config.get("visual_ref"),
        "lineage": {
            "adapter": "shared_package_question_v1",
            "package_id": package_id,
        },
    }


@dataclass(frozen=True)
class WorkerResult:
    worker_id: str
    output: object
    receipt: dict


def run_worker(worker_id: str, input_value: object, producer) -> WorkerResult:
    output = producer(input_value)
    return WorkerResult(
        worker_id=worker_id,
        output=output,
        receipt={
            "worker_id": worker_id,
            "contract_version": WORKER_CONTRACT_VERSION,
            "input_digest": digest(input_value),
            "output_digest": digest(output),
        },
    )


def build_lineage(questions: Sequence[Mapping[str, object]], search_index: Mapping[str, object], build_id: str) -> dict:
    indexed = {str(row["id"]) for row in search_index.get("documents", []) or [] if row.get("kind") == "question"}
    rows = []
    for raw in questions:
        q = enrich_question_refs(raw)
        rows.append({
            "id": q["id"],
            "subject_ref": q["subject_ref"],
            "topic_ref": q["topic_ref"],
            "subtopic_refs": q.get("subtopic_refs", []),
            "source_path": q.get("source_path"),
            "adapter": (q.get("lineage") or {}).get("adapter") if isinstance(q.get("lineage"), Mapping) else q.get("adapter"),
            "search_indexed": q["id"] in indexed,
            "build_id": build_id,
        })
    rows.sort(key=lambda row: str(row["id"]))
    return {"schema_version": LINEAGE_SCHEMA, "build_id": build_id, "questions": rows}


def assemble_platform(browser_projection: Mapping[str, object], resources: Sequence[Mapping[str, object]] = (),
                      resource_basis: Sequence[Mapping[str, object]] = ()) -> dict:
    """Build deterministic derived contracts from the existing canonical browser projection."""
    questions = [enrich_question_refs(q) for q in browser_projection.get("questions", []) or []]
    validate_unique_ids(questions)
    resources = [_resource_scope(r) for r in resources]

    catalog_worker = run_worker("catalog", {"questions": questions, "resources": resources},
                                lambda x: build_catalog(x["questions"], x["resources"]))
    search_worker = run_worker("search", {"questions": questions, "resources": resources},
                               lambda x: build_search_index(x["questions"], x["resources"]))
    dedup_worker = run_worker("dedup", questions, build_dedup_report)

    identity_basis = {
        "browser_projection_digest": digest(browser_projection),
        "resource_basis": list(resource_basis),
        "worker_contract_version": WORKER_CONTRACT_VERSION,
    }
    build_id = digest(identity_basis)
    lineage = build_lineage(questions, search_worker.output, build_id)
    workers = [catalog_worker.receipt, search_worker.receipt, dedup_worker.receipt]
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "build_id": build_id,
        "basis": identity_basis,
        "counts": {
            "questions": len(questions),
            "resources": len(resources),
            "search_documents": search_worker.output["document_count"],
            "dedup_relationships": len(dedup_worker.output["relationships"]),
        },
        "workers": sorted(workers, key=lambda row: row["worker_id"]),
        "outputs": {
            "catalog": digest(catalog_worker.output),
            "search": digest(search_worker.output),
            "resources": digest(resources),
            "dedup": digest(dedup_worker.output),
            "lineage": digest(lineage),
        },
    }
    return {
        "schema_version": PLATFORM_SCHEMA,
        "build_id": build_id,
        "catalog": catalog_worker.output,
        "search": search_worker.output,
        "resources": {"schema_version": RESOURCE_SCHEMA, "build_id": build_id, "resources": resources},
        "dedup": {**dedup_worker.output, "build_id": build_id},
        "lineage": lineage,
        "receipt": receipt,
    }


def render_js(global_name: str, value: object) -> str:
    return f"window.{global_name}=" + canonical_json(value) + ";\n"


def explain(platform: Mapping[str, object], record_id: str) -> dict | None:
    for row in platform.get("lineage", {}).get("questions", []) or []:
        if row.get("id") == record_id:
            search_doc = next(
                (doc for doc in platform.get("search", {}).get("documents", []) or [] if doc.get("id") == record_id),
                None,
            )
            return {"lineage": row, "search_document": search_doc}
    return None
