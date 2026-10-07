#!/usr/bin/env python3
"""Subject-neutral Question Bank growth contracts for catalog, search, dedup and lineage.

Curriculum names and learner-resource routes are input data. This module only defines
stable producer/consumer contracts. It consumes the existing canonical browser projection
and can also normalize package-shaped questions that explicitly opt into Question Bank
publication through ``extensions.grade9v3:question_bank``.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

PLATFORM_SCHEMA = "grade9v3-question-bank-platform-v1"
CATALOG_SCHEMA = "grade9v3-question-bank-catalog-v1"
SUMMARY_SCHEMA = "grade9v3-question-bank-questions-v1"
SEARCH_SCHEMA = "grade9v3-question-bank-search-v1"
RESOURCE_SCHEMA = "grade9v3-question-bank-resources-v1"
DEDUP_SCHEMA = "grade9v3-question-bank-dedup-v1"
LINEAGE_SCHEMA = "grade9v3-question-bank-lineage-v1"
RECEIPT_SCHEMA = "grade9v3-question-bank-build-receipt-v1"
WORKER_CONTRACT_VERSION = "1.0.0"
NEAR_SHINGLE_SIZE = 3
NEAR_MAX_BUCKET = 32
NEAR_MAX_CANDIDATES_PER_RECORD = 24
NEAR_THRESHOLD = 0.82

_TOKEN = re.compile(r"[a-z0-9]+")
_SPACE = re.compile(r"\s+")
_LATEX_DELIMS = re.compile(r"(?:\\\(|\\\)|\\\[|\\\]|\$\$|\$)")
_MATH_SPACING = re.compile(r"\s*([+\-*/=^<>()\[\]{},])\s*")
_TERMINAL_PUNCT = re.compile(r"[.!?]+$")


class ProjectionError(ValueError):
    """Fail-closed error for contradictory identity or malformed opted-in data."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: object) -> str:
    raw = value if isinstance(value, str) else canonical_json(value)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def slug(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return "-".join(_TOKEN.findall(text)) or "unknown"


def subject_ref(label: str, explicit: str | None = None) -> str:
    return explicit or f"SUBJECT-{slug(label).upper()}"


def topic_ref(subject: str, label: str, explicit: str | None = None) -> str:
    return explicit or f"TOPIC-{slug(subject).upper()}-{slug(label).upper()}"


def normalize_content(value: object) -> str:
    """Normalize presentation differences while preserving mathematical operators.

    Operators/signs/grouping are semantic. In particular, ``x + 1`` and ``x - 1`` must
    never collapse to the same exact-content fingerprint.
    """
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    text = _LATEX_DELIMS.sub("", text)
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = _SPACE.sub(" ", text).strip()
    text = _MATH_SPACING.sub(r"\1", text)
    return _TERMINAL_PUNCT.sub("", text).strip()


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
    return digest({
        "stem": normalize_content(question.get("stem")),
        "subparts": [normalize_content(x) for x in question.get("subparts", []) or []],
        "options": [normalize_content(_option_text(x)) for x in question.get("options", []) or []],
        "conditions": [normalize_content(x) for x in question.get("conditions", []) or []],
    })


def structural_fingerprint(question: Mapping[str, object]) -> str:
    return digest({
        "stem": normalize_content(question.get("stem")),
        "question_type": normalize_content(question.get("question_type")),
        "options": [normalize_content(_option_text(x)) for x in question.get("options", []) or []],
        "answer": normalize_content(_answer_summary(question)),
    })


def source_identity(question: Mapping[str, object]) -> tuple[str, ...] | None:
    # Subject participates in source identity so equal paper/question numbers from different
    # subject sections cannot be reconciled as one source item.
    fields = ("subject", "exam", "year", "paper", "question_number")
    values = tuple(str(question.get(key) or "").strip() for key in fields)
    return values if all(values) else None


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def compare_pair(left: Mapping[str, object], right: Mapping[str, object]) -> dict:
    """Classify one pair. This function never mutates, merges or deletes either record."""
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
    if similarity >= NEAR_THRESHOLD:
        return {
            "classification": "NEAR_DUPLICATE",
            "reason": "stem_token_jaccard",
            "score": round(similarity, 6),
        }
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


def _group_evidence(questions: Sequence[Mapping[str, object]]) -> list[dict]:
    """Create compact exact/source/family groups; never materialize every family pair."""
    groups: list[dict] = []
    exact: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    sources: dict[tuple[str, ...], list[Mapping[str, object]]] = defaultdict(list)
    families: dict[str, list[Mapping[str, object]]] = defaultdict(list)

    for question in questions:
        exact[normalized_exact_fingerprint(question)].append(question)
        src = source_identity(question)
        if src:
            sources[src].append(question)
        fam = str(question.get("family_ref") or "")
        if fam:
            families[fam].append(question)

    for fingerprint, members in exact.items():
        if len(members) > 1:
            groups.append({
                "classification": "DUPLICATE",
                "reason": "normalized_exact_content",
                "fingerprint": fingerprint,
                "member_ids": sorted(str(row["id"]) for row in members),
            })

    for identity, members in sources.items():
        if len(members) < 2:
            continue
        structures = {structural_fingerprint(row) for row in members}
        classification = "DUPLICATE" if len(structures) == 1 else "SOURCE_COLLISION"
        groups.append({
            "classification": classification,
            "reason": "same_source_identity_same_structure" if classification == "DUPLICATE" else "same_source_identity_conflict",
            "source_identity": list(identity),
            "member_ids": sorted(str(row["id"]) for row in members),
        })

    for family_ref, members in families.items():
        if len(members) > 1:
            groups.append({
                "classification": "VARIANT",
                "reason": "explicit_family_ref",
                "family_ref": family_ref,
                "member_ids": sorted(str(row["id"]) for row in members),
            })

    groups.sort(key=lambda row: (
        row["classification"],
        str(row.get("family_ref") or row.get("fingerprint") or row.get("source_identity") or ""),
    ))
    return groups


def _shingles(tokens: Sequence[str]) -> set[tuple[str, ...]]:
    if len(tokens) < NEAR_SHINGLE_SIZE:
        return set()
    return {
        tuple(tokens[index:index + NEAR_SHINGLE_SIZE])
        for index in range(len(tokens) - NEAR_SHINGLE_SIZE + 1)
    }


def _near_duplicate_evidence(questions: Sequence[Mapping[str, object]]) -> tuple[list[dict], dict]:
    """Bounded deterministic near-duplicate search within subject/topic partitions.

    Shared 3-token shingles generate candidates. Extremely common shingles are ignored and
    each record compares with at most a fixed number of strongest candidates, preventing
    same-topic corpora from degenerating into all-pairs work as the corpus grows.

    Those bounds mean the search can decline to look. The second value says how often it did, so
    "no near duplicates found" is never confused with "the search skipped most of the corpus".
    """
    partitions: dict[tuple[str, str], list[Mapping[str, object]]] = defaultdict(list)
    for question in questions:
        partitions[(
            str(question.get("subject_ref") or question.get("subject") or ""),
            str(question.get("topic_ref") or question.get("topic") or ""),
        )].append(question)

    relationships: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()
    coverage = {"records": 0, "records_with_shingles": 0, "shingle_buckets": 0,
                "shingle_buckets_skipped_as_too_common": 0, "records_with_truncated_candidates": 0,
                "records_whose_shingles_were_all_skipped": 0}
    for members in partitions.values():
        by_id = {str(row["id"]): row for row in members}
        tokens_by_id = {qid: tokenize(row.get("stem")) for qid, row in by_id.items()}
        inverted: dict[tuple[str, ...], list[str]] = defaultdict(list)
        for qid, tokens in tokens_by_id.items():
            for shingle in _shingles(tokens):
                inverted[shingle].append(qid)

        candidate_scores: dict[str, Counter] = defaultdict(Counter)
        examined_shingles: Counter = Counter()
        skipped_shingles: Counter = Counter()
        for ids in inverted.values():
            unique_ids = sorted(set(ids))
            if len(unique_ids) < 2:
                continue
            coverage["shingle_buckets"] += 1
            if len(unique_ids) > NEAR_MAX_BUCKET:
                coverage["shingle_buckets_skipped_as_too_common"] += 1
                skipped_shingles.update(unique_ids)
                continue
            examined_shingles.update(unique_ids)
            for qid in unique_ids:
                for other in unique_ids:
                    if qid != other:
                        candidate_scores[qid][other] += 1

        for qid in sorted(by_id):
            ranked = sorted(candidate_scores.get(qid, {}).items(), key=lambda row: (-row[1], row[0]))
            coverage["records"] += 1
            if _shingles(tokens_by_id[qid]):
                coverage["records_with_shingles"] += 1
                if qid in skipped_shingles and qid not in examined_shingles:
                    coverage["records_whose_shingles_were_all_skipped"] += 1
            if len(ranked) > NEAR_MAX_CANDIDATES_PER_RECORD:
                coverage["records_with_truncated_candidates"] += 1
            for other, shared_shingles in ranked[:NEAR_MAX_CANDIDATES_PER_RECORD]:
                pair = tuple(sorted((qid, other)))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                result = compare_pair(by_id[qid], by_id[other])
                if result["classification"] != "NEAR_DUPLICATE":
                    continue
                relationships.append({
                    "left_id": pair[0],
                    "right_id": pair[1],
                    "shared_shingles": shared_shingles,
                    **result,
                })

    relationships.sort(key=lambda row: (row["left_id"], row["right_id"]))
    coverage["complete"] = (
        coverage["shingle_buckets_skipped_as_too_common"] == 0
        and coverage["records_with_truncated_candidates"] == 0
    )
    return relationships, coverage


def build_dedup_report(questions: Sequence[Mapping[str, object]]) -> dict:
    validate_unique_ids(questions)
    groups = _group_evidence(questions)
    relationships, coverage = _near_duplicate_evidence(questions)
    counts = Counter(row["classification"] for row in groups)
    counts.update(row["classification"] for row in relationships)
    return {
        "schema_version": DEDUP_SCHEMA,
        "authority": "EVIDENCE_ONLY_NO_SILENT_DELETION",
        "question_count": len(questions),
        "strategy": {
            "exact": "normalized_semantic_preserving_fingerprint",
            "source": "subject_exam_year_paper_question_number",
            "variants": "compact_family_groups",
            "near_duplicate": {
                "partition": "subject_topic",
                "shingle_size": NEAR_SHINGLE_SIZE,
                "max_shingle_bucket": NEAR_MAX_BUCKET,
                "max_candidates_per_record": NEAR_MAX_CANDIDATES_PER_RECORD,
                "jaccard_threshold": NEAR_THRESHOLD,
            },
        },
        "evidence_counts": dict(sorted(counts.items())),
        "evidence_count": len(groups) + len(relationships),
        "near_duplicate_coverage": coverage,
        "groups": groups,
        "relationships": relationships,
    }


def _projection_refs(question: Mapping[str, object]) -> tuple[str, str]:
    subject = str(question.get("subject") or "")
    topic = str(question.get("topic") or "")
    explicit_subject = question.get("subject_ref")
    explicit_topic = question.get("topic_ref")
    return (
        subject_ref(subject, str(explicit_subject) if explicit_subject else None),
        topic_ref(subject, topic, str(explicit_topic) if explicit_topic else None),
    )


def enrich_question_refs(question: Mapping[str, object]) -> dict:
    sref, tref = _projection_refs(question)
    out = dict(question)
    out["subject_ref"] = sref
    out["topic_ref"] = tref
    subtopics = list(question.get("subtopic_refs") or [])
    if not subtopics and question.get("primary_capability_ref"):
        subtopics = [str(question["primary_capability_ref"])] + [
            str(value) for value in question.get("secondary_capability_refs", []) or []
        ]
    out["subtopic_refs"] = list(dict.fromkeys(subtopics))
    return out


def _resource_scope(resource: Mapping[str, object], fallback_subject: str | None = None) -> dict:
    subject = str(resource.get("subject") or fallback_subject or "")
    topic = str(resource.get("topic") or resource.get("topic_label") or "")
    out = dict(resource)
    if subject:
        out["subject"] = subject
        out["subject_ref"] = subject_ref(subject, str(resource.get("subject_ref")) if resource.get("subject_ref") else None)
    if topic:
        out["topic"] = topic
        out["topic_ref"] = topic_ref(subject, topic, str(resource.get("topic_ref")) if resource.get("topic_ref") else None)
    out["subtopic_refs"] = list(resource.get("subtopic_refs") or [])
    out["keywords"] = sorted({
        normalize_content(value)
        for value in resource.get("keywords", []) or []
        if str(value).strip()
    })
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
            if not all(row.get(key) for key in ("id", "kind", "title", "path")):
                raise ProjectionError(f"Malformed resource record in {path.relative_to(repo)}: {row}")
            resources.append(_resource_scope(row, fallback_subject))
        basis.append({
            "path": path.relative_to(repo).as_posix(),
            "digest": digest(doc),
            "resource_count": len(rows),
        })
    return resources, basis


def load_gcdr_suite_resources(repo: Path) -> tuple[list[dict], list[dict]]:
    """Project GCDR suite delivery records generically; no curriculum branch is needed."""
    resources: list[dict] = []
    basis: list[dict] = []
    suites_dir = repo / "docs" / "gcdr-suites"
    if not suites_dir.is_dir():
        return resources, basis

    for path in sorted(suites_dir.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        title = doc.get("title")
        artifacts = doc.get("delivery_artifacts") or []
        bundle = next((
            row for row in artifacts
            if isinstance(row, Mapping) and row.get("profile") == "REPO_BUNDLE" and row.get("locator")
        ), None)
        if not title or not bundle:
            continue
        locator = str(bundle["locator"])
        public_path = locator[7:] if locator.startswith("public/") else locator
        parts = Path(public_path).parts
        if not parts:
            continue
        corpus = doc.get("external_corpus") or {}
        subject = str(corpus.get("subject") or parts[0]).replace("-", " ").title()
        topic = str(corpus.get("topic") or "")
        suite_id = str(doc.get("suite_id") or f"gcdr-suite:{slug(title)}")
        keywords = sorted(set(_TOKEN.findall(normalize_content(
            " ".join([str(title), topic, suite_id, "explorer interactive suite"])
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


def load_topic_links(repo: Path) -> list[dict]:
    """Explicit resource-to-question-topic links, recorded beside the resources they describe.

    A discovered explorer suite names its topic in an external provider's words, which is usually not the
    question topic's. Nothing here guesses the match: a person records it in the subject's registry
    (``topic_links``) with the reason, and the build refuses a link that does not resolve.
    """
    links: list[dict] = []
    for path in sorted(repo.glob("*/question-bank/resources.v1.json")):
        source = path.relative_to(repo).as_posix()
        for row in json.loads(path.read_text(encoding="utf-8")).get("topic_links") or []:
            if not all(str(row.get(key) or "").strip() for key in ("resource_id", "topic_ref", "reason")):
                raise ProjectionError(f"Malformed topic link in {source}: {row} (needs resource_id, topic_ref and reason)")
            links.append({
                "resource_id": str(row["resource_id"]),
                "topic_ref": str(row["topic_ref"]),
                "reason": str(row["reason"]),
                "source": source,
            })
    return links


def apply_topic_links(resources: Sequence[Mapping[str, object]], links: Sequence[Mapping[str, str]]) -> list[dict]:
    by_id = {str(row["id"]): dict(row) for row in resources}
    linked: set[str] = set()
    for link in links:
        rid = link["resource_id"]
        if rid not in by_id:
            raise ProjectionError(f"Topic link in {link['source']} names resource {rid!r}, which no registry or suite defines")
        if rid in linked:
            raise ProjectionError(f"Resource {rid!r} is linked to more than one topic")
        linked.add(rid)
        row = by_id[rid]
        if row.get("topic"):
            row["source_topic"] = row["topic"]
        row["topic_ref"] = link["topic_ref"]
        row["topic_link"] = {"reason": link["reason"], "source": link["source"]}
    return [by_id[str(row["id"])] for row in resources]


def bind_topic_links(resources: Sequence[Mapping[str, object]],
                     questions: Sequence[Mapping[str, object]]) -> list[dict]:
    """Check every explicit link against the question topics and take the topic's own label."""
    topics = {str(q["topic_ref"]): (str(q["subject_ref"]), str(q["topic"])) for q in questions}
    bound: list[dict] = []
    for row in resources:
        row = dict(row)
        link = row.get("topic_link")
        if link:
            target = topics.get(str(row.get("topic_ref")))
            if target is None:
                raise ProjectionError(
                    f"Resource {row['id']!r} is linked to topic {row.get('topic_ref')!r} ({link['source']}), "
                    "which no question has; a link may not create a topic")
            if row.get("subject_ref") and row["subject_ref"] != target[0]:
                raise ProjectionError(
                    f"Resource {row['id']!r} ({row['subject_ref']}) is linked to topic {row['topic_ref']!r}, "
                    f"which belongs to {target[0]}")
            row["topic"] = target[1]
        bound.append(row)
    return bound


def load_resources(repo: Path) -> tuple[list[dict], list[dict]]:
    registry_resources, registry_basis = load_resource_registries(repo)
    suite_resources, suite_basis = load_gcdr_suite_resources(repo)
    rows = registry_resources + suite_resources
    ids = [str(row["id"]) for row in rows]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ProjectionError(f"Question Bank resources contain duplicate ids: {duplicates}")
    rows = apply_topic_links(rows, load_topic_links(repo))
    rows.sort(key=lambda row: (
        str(row.get("subject_ref") or ""),
        str(row.get("topic_ref") or ""),
        str(row.get("order", 0)),
        str(row["id"]),
    ))
    return rows, registry_basis + suite_basis


PACKAGE_GLOB = "*/library/*.json"


def load_subtopic_titles(repo: Path) -> dict[str, dict]:
    """Learner-facing names for capability refs, from canonical records only.

    A capability has no title of its own; the concept that owns it does. A ref is titled when exactly one
    microtopic across the library packages names it as its primary capability. Zero owners or several
    owners is not resolved here (and never guessed from the identifier): the ref stays untitled and the
    catalog says so.
    """
    owners: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(repo.glob(PACKAGE_GLOB)):
        try:
            package = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(package, dict):
            continue
        # TEST is a sandbox authority, never canonical Question Bank naming authority.
        if package.get("subject") == "TEST":
            continue
        for microtopic in package.get("microtopics") or []:
            ref, title = microtopic.get("primary_capability_ref"), microtopic.get("title")
            if isinstance(ref, str) and ref and isinstance(title, str) and title.strip():
                owners[ref].append({"title": title.strip(), "source_ref": str(microtopic.get("id") or "")})
    
    return {
        ref: {"title": rows[0]["title"], "source_ref": rows[0]["source_ref"]}
        for ref, rows in sorted(owners.items()) if len(rows) == 1
    }


_VIEW_FIELDS = ("id", "title", "short_title", "description", "match_mode", "presentation")


def normalize_views(views: Sequence[Mapping[str, object]], question_ids: Iterable[str]) -> list[dict]:
    """Saved collections as membership: each names the questions it contains, none may dangle."""
    known = set(question_ids)
    rows: list[dict] = []
    seen: set[str] = set()
    for view in views or ():
        vid = str(view.get("id") or "")
        if not vid or vid in seen:
            raise ProjectionError(f"saved view id is missing or repeated: {vid!r}")
        seen.add(vid)
        refs = [str(ref) for ref in view.get("resolved_question_refs", []) or []]
        dangling = [ref for ref in refs if ref not in known]
        if dangling:
            raise ProjectionError(f"saved view {vid!r} names unknown questions: {dangling[:3]}")
        row = {key: view[key] for key in _VIEW_FIELDS if key in view}
        row["resolved_question_refs"] = refs
        rows.append(row)
    return sorted(rows, key=lambda row: row["id"])


_SUMMARY_FIELDS = (
    "id", "order", "subject", "subject_ref", "topic", "topic_ref", "subtopic_refs", "exam", "year", "paper",
    "question_number", "question_type", "expected_time_seconds", "difficulty", "primary_capability_ref",
    "secondary_capability_refs", "common_wrong_route", "stem", "source_status",
)


def summarize_question(question: Mapping[str, object]) -> dict:
    """What a result list needs to show and filter one question; everything else is on demand."""
    enriched = enrich_question_refs(question)
    row = {key: enriched[key] for key in _SUMMARY_FIELDS if key in enriched}
    spans = [span for span in enriched.get("math_spans") or [] if isinstance(span, Mapping) and span.get("target") == "stem"]
    if spans:
        row["math_spans"] = spans
    row["has_visual"] = bool(enriched.get("visual_ref"))
    row["option_count"] = len(enriched.get("options") or [])
    row["has_support"] = bool(enriched.get("source_hints") or enriched.get("scaffolds"))
    row["support_count"] = len(enriched.get("source_hints") or []) + len(enriched.get("scaffolds") or [])
    ans = enriched.get("answer") or {}
    row["has_solution"] = bool(ans.get("summary") or ans.get("reasoning")) if isinstance(ans, Mapping) else False
    return row


def build_question_summaries(questions: Sequence[Mapping[str, object]]) -> dict:
    rows = sorted((summarize_question(q) for q in questions), key=lambda row: (row.get("order", 0), str(row["id"])))
    return {"schema_version": SUMMARY_SCHEMA, "question_count": len(rows), "questions": rows}


def build_catalog(questions: Sequence[Mapping[str, object]], resources: Sequence[Mapping[str, object]] = (),
                  views: Sequence[Mapping[str, object]] = (),
                  subtopic_titles: Mapping[str, Mapping[str, str]] | None = None) -> dict:
    enriched = [enrich_question_refs(question) for question in questions]
    subject_rows: dict[str, dict] = {}
    topic_rows: dict[str, dict] = {}
    subtopic_rows: dict[str, dict] = {}

    for question in enriched:
        sref, tref = question["subject_ref"], question["topic_ref"]
        subject_rows.setdefault(sref, {
            "id": sref,
            "label": question["subject"],
            "question_count": 0,
            "resource_count": 0,
        })["question_count"] += 1
        topic_rows.setdefault(tref, {
            "id": tref,
            "subject_ref": sref,
            "label": question["topic"],
            "question_count": 0,
            "resource_count": 0,
            "identity_basis": "EXPLICIT_REF" if tref != topic_ref(question["subject"], question["topic"]) else "LEGACY_LABEL_DERIVED",
        })["question_count"] += 1
        for ref in question.get("subtopic_refs", []):
            titled = (subtopic_titles or {}).get(ref)
            subtopic_rows.setdefault(ref, {
                "id": ref,
                "subject_ref": sref,
                "topic_ref": tref,
                "label": titled["title"] if titled else ref,
                "label_source": "CANONICAL_TITLE" if titled else "REF_ONLY",
                **({"label_source_ref": titled["source_ref"]} if titled else {}),
                "question_count": 0,
            })["question_count"] += 1

    for raw in resources:
        resource = _resource_scope(raw)
        sref, tref = resource.get("subject_ref"), resource.get("topic_ref")
        if sref:
            subject_rows.setdefault(sref, {
                "id": sref,
                "label": resource.get("subject", sref),
                "question_count": 0,
                "resource_count": 0,
            })["resource_count"] += 1
        if tref:
            topic_rows.setdefault(tref, {
                "id": tref,
                "subject_ref": sref,
                "label": resource.get("topic", tref),
                "question_count": 0,
                "resource_count": 0,
                "identity_basis": "EXPLICIT_REF" if raw.get("topic_ref") else "LEGACY_LABEL_DERIVED",
            })["resource_count"] += 1

    subjects = sorted(subject_rows.values(), key=lambda row: (str(row["label"]).casefold(), row["id"]))
    topics = sorted(topic_rows.values(), key=lambda row: (row.get("subject_ref") or "", str(row["label"]).casefold(), row["id"]))
    subtopics = sorted(subtopic_rows.values(), key=lambda row: (row.get("topic_ref") or "", row["id"]))
    saved_views = normalize_views(views, (str(q["id"]) for q in enriched))
    return {
        "schema_version": CATALOG_SCHEMA,
        "counts": {
            "questions": len(enriched),
            "resources": len(resources),
            "subjects": len(subjects),
            "topics": len(topics),
            "subtopics": len(subtopics),
            "subtopics_without_title": sum(1 for row in subtopics if row["label_source"] == "REF_ONLY"),
            "views": len(saved_views),
        },
        "subjects": subjects,
        "topics": topics,
        "subtopics": subtopics,
        "views": saved_views,
    }


def _search_text(parts: Iterable[object]) -> str:
    return " ".join(part for part in (normalize_content(value) for value in parts) if part)


def _difficulty_descriptors(band: object) -> str:
    mapping = {
        "d1": "d1 easy",
        "d2": "d2 medium",
        "d3": "d3 hard",
        "d4": "d4 olympiad",
    }
    return mapping.get(str(band or "").strip().lower(), "")


def _question_aliases(question: Mapping[str, object]) -> str:
    aliases = []
    exam_str = str(question.get("exam") or "").lower()
    qid = str(question.get("id") or "").lower()
    tags = [str(t).lower() for t in question.get("tags") or []]
    if "ncert" in exam_str or "ncert" in qid or any("ncert" in t for t in tags):
        aliases.extend(["ncert", "cbse"])
    if "jee" in exam_str or "iit" in exam_str or "jee" in qid or any("jee" in t for t in tags):
        aliases.extend(["jee", "iit", "pyq"])
    if "core" in qid or "core2" in qid or any("core2" in t for t in tags):
        aliases.append("core2")
    return " ".join(aliases)


def build_search_index(questions: Sequence[Mapping[str, object]], resources: Sequence[Mapping[str, object]] = (),
                       subtopic_titles: Mapping[str, Mapping[str, str]] | None = None) -> dict:
    documents: list[dict] = []
    for raw in questions:
        question = enrich_question_refs(raw)
        sub_titles = [
            (subtopic_titles or {}).get(ref, {}).get("title", "")
            for ref in question.get("subtopic_refs", []) or []
        ]
        diff_band = (question.get("difficulty") or {}).get("band") if isinstance(question.get("difficulty"), Mapping) else question.get("difficulty")
        parts: list[object] = [
            question.get("id"), question.get("subject"), question.get("topic"), question.get("exam"),
            question.get("year"), question.get("paper"), question.get("question_type"), question.get("stem"),
            question.get("primary_capability_ref"), question.get("family_ref"), question.get("stable_crux_move"),
            " ".join(question.get("secondary_capability_refs", []) or []),
            " ".join(t for t in sub_titles if t),
            _difficulty_descriptors(diff_band),
            _question_aliases(question),
        ]
        documents.append({
            "id": question["id"],
            "kind": "question",
            "subject_ref": question["subject_ref"],
            "topic_ref": question["topic_ref"],
            "subtopic_refs": question.get("subtopic_refs", []),
            "label": question.get("stem") or question["id"],
            "difficulty": (question.get("difficulty") or {}).get("band") if isinstance(question.get("difficulty"), Mapping) else None,
            "search_text": _search_text(parts),
        })

    for raw in resources:
        resource = _resource_scope(raw)
        documents.append({
            "id": resource["id"],
            "kind": "resource",
            "subject_ref": resource.get("subject_ref"),
            "topic_ref": resource.get("topic_ref"),
            "subtopic_refs": resource.get("subtopic_refs", []),
            "label": resource["title"],
            "path": resource["path"],
            "resource_kind": resource["kind"],
            "search_text": _search_text([
                resource.get("id"), resource.get("title"), resource.get("kind"),
                resource.get("subject"), resource.get("topic"), resource.get("source_topic"),
                " ".join(resource.get("keywords", [])),
            ]),
        })

    documents.sort(key=lambda row: (row["kind"], str(row["id"])))
    return {"schema_version": SEARCH_SCHEMA, "document_count": len(documents), "documents": documents}


def search(index: Mapping[str, object], query: str, *, kind: str | None = None,
           subject: str | None = None, topic: str | None = None) -> list[dict]:
    terms = tokenize(query)
    output: list[dict] = []
    for document in index.get("documents", []) or []:
        if kind and document.get("kind") != kind:
            continue
        if subject and document.get("subject_ref") != subject:
            continue
        if topic and document.get("topic_ref") != topic:
            continue
        haystack = str(document.get("search_text") or "")
        if terms and not all(term in haystack for term in terms):
            continue
        output.append(dict(document))
    return output


def _package_qbank_config(package: Mapping[str, object], question: Mapping[str, object]) -> Mapping[str, object] | None:
    package_extensions = package.get("extensions") or {}
    question_extensions = question.get("extensions") or {}
    package_config = package_extensions.get("grade9v3:question_bank") if isinstance(package_extensions, Mapping) else None
    question_config = question_extensions.get("grade9v3:question_bank") if isinstance(question_extensions, Mapping) else None
    config: dict = {}
    if isinstance(package_config, Mapping):
        config.update(package_config)
    if isinstance(question_config, Mapping):
        config.update(question_config)
    return config if config.get("include") is True else None


def project_package_question(package: Mapping[str, object], question: Mapping[str, object], order: int = 0) -> dict | None:
    """Normalize one explicitly opted-in Shared package question without subject branches."""
    config = _package_qbank_config(package, question)
    if config is None:
        return None

    extensions = question.get("extensions") or {}
    analysis = extensions.get("grade9v3:analysis") if isinstance(extensions, Mapping) else None
    custody = extensions.get("grade9v3:source_custody") if isinstance(extensions, Mapping) else None
    analysis = analysis if isinstance(analysis, Mapping) else {}
    custody = custody if isinstance(custody, Mapping) else {}
    difficulty = analysis.get("difficulty") or config.get("difficulty")
    question_type = analysis.get("learner_question_type") or config.get("question_type")
    expected_time = analysis.get("expected_time_seconds") or config.get("expected_time_seconds")
    if not isinstance(difficulty, Mapping) or not difficulty.get("band") or question_type is None or expected_time is None:
        raise ProjectionError(f"Opted-in package question {question.get('id')} lacks browser metadata")

    subject = str(package.get("subject") or "")
    package_id = str(package.get("package_id") or "")
    topic_label = str(config.get("topic_label") or package.get("title") or package_id)
    stable_topic_ref = str(config.get("topic_ref") or package_id)
    if not subject or not package_id or not topic_label or not stable_topic_ref:
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
        "topic_ref": stable_topic_ref,
        "subtopic_refs": list(config.get("subtopic_refs") or ([question.get("primary_capability_ref")] if question.get("primary_capability_ref") else [])),
        "version": question.get("version"),
        "status": question.get("status"),
        "question_type": question_type,
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
        "expected_time_seconds": expected_time,
        "common_wrong_route": analysis.get("common_wrong_route") or config.get("common_wrong_route") or "",
        "stable_crux_move": analysis.get("stable_crux_move") or config.get("stable_crux_move") or "",
        "primary_capability_ref": question.get("primary_capability_ref"),
        "secondary_capability_refs": question.get("secondary_capability_refs", []),
        "family_ref": question.get("family_ref"),
        "source_hints": question.get("hints", []),
        "scaffolds": question.get("scaffolds") or [],
        "answer": {
            "summary": answer.get("summary", ""),
            "reasoning": answer.get("reasoning", []),
            "reasoning_route": answer.get("reasoning_route", []),
            "crux_move_ref": answer.get("crux_move_ref"),
            "check": answer.get("check", ""),
            "verification_status": answer.get("verification_status"),
        },
        "visual_ref": config.get("visual_ref"),
        "lineage": {"adapter": "shared_package_question_v1", "package_id": package_id},
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


@dataclass(frozen=True)
class Node:
    """One logical producer in the build graph.

    ``needs`` names the nodes whose results this node reads; ``read`` turns those results into the
    exact value the node consumes (that value is what its receipt digests); ``produce`` is a pure
    function of it. A node never reaches for module state, so any order that respects ``needs``
    yields the same outputs.
    """

    worker_id: str
    needs: tuple[str, ...]
    read: Callable[[Mapping[str, WorkerResult]], object]
    produce: Callable[[object], object]
    receipted: bool = True


def run_nodes(
    nodes: Sequence[Node],
    *,
    order: Callable[[list[str]], list[str]] | None = None,
    parallel: bool = False,
) -> dict[str, WorkerResult]:
    """Run ``nodes`` once each, only after everything they need has finished.

    ``order`` picks the sequence among nodes that are ready at the same time (default: by id) and
    ``parallel`` runs each ready set concurrently. Neither may change any output: that is the
    determinism contract the build tests hold this function to.
    """
    by_id = {node.worker_id: node for node in nodes}
    if len(by_id) != len(nodes):
        raise ProjectionError("duplicate worker id in the build graph")
    for node in nodes:
        for need in node.needs:
            if need not in by_id:
                raise ProjectionError(f"worker {node.worker_id!r} needs unknown worker {need!r}")
    done: dict[str, WorkerResult] = {}
    remaining = set(by_id)
    while remaining:
        ready = sorted(wid for wid in remaining if all(need in done for need in by_id[wid].needs))
        if not ready:
            raise ProjectionError("the build graph has a cycle: " + ", ".join(sorted(remaining)))
        sequence = order(list(ready)) if order else ready
        if sorted(sequence) != ready:
            raise ProjectionError("the order function must return exactly the ready workers")
        snapshot = dict(done)
        if parallel and len(sequence) > 1:
            with ThreadPoolExecutor(max_workers=len(sequence)) as pool:
                results = list(pool.map(
                    lambda wid: run_worker(wid, by_id[wid].read(snapshot), by_id[wid].produce), sequence))
        else:
            results = [run_worker(wid, by_id[wid].read(snapshot), by_id[wid].produce) for wid in sequence]
        for wid, result in zip(sequence, results):
            done[wid] = result
            remaining.discard(wid)
    return done


def build_lineage(questions: Sequence[Mapping[str, object]], search_index: Mapping[str, object], build_id: str) -> dict:
    indexed = {
        str(row["id"])
        for row in search_index.get("documents", []) or []
        if row.get("kind") == "question"
    }
    rows = []
    for raw in questions:
        question = enrich_question_refs(raw)
        lineage = question.get("lineage") or {}
        rows.append({
            "id": question["id"],
            "subject_ref": question["subject_ref"],
            "topic_ref": question["topic_ref"],
            "subtopic_refs": question.get("subtopic_refs", []),
            "source_path": question.get("source_path"),
            "adapter": lineage.get("adapter") if isinstance(lineage, Mapping) else question.get("adapter"),
            "search_indexed": question["id"] in indexed,
            "build_id": build_id,
        })
    rows.sort(key=lambda row: str(row["id"]))
    return {"schema_version": LINEAGE_SCHEMA, "build_id": build_id, "questions": rows}


def platform_nodes(questions: Sequence[Mapping[str, object]], scoped_resources: Sequence[Mapping[str, object]],
                   build_id: str, views: Sequence[Mapping[str, object]] = (),
                   subtopic_titles: Mapping[str, Mapping[str, str]] | None = None) -> tuple[Node, ...]:
    """The build graph: catalog, summaries, search and dedup are independent; lineage reads the search result."""
    shared = {"questions": questions, "resources": scoped_resources}
    with_views = {**shared, "views": list(views), "subtopic_titles": dict(subtopic_titles or {})}
    return (
        Node("catalog", (), lambda done: with_views,
             lambda value: build_catalog(value["questions"], value["resources"], value["views"], value["subtopic_titles"])),
        Node("summaries", (), lambda done: questions, build_question_summaries),
        Node("search", (), lambda done: with_views,
             lambda value: build_search_index(value["questions"], value["resources"], value.get("subtopic_titles"))),
        Node("dedup", (), lambda done: questions, build_dedup_report),
        Node("lineage", ("search",), lambda done: {"search": done["search"].output, "build_id": build_id},
             lambda value: build_lineage(questions, value["search"], value["build_id"]), receipted=False),
    )


def assemble_platform(browser_projection: Mapping[str, object], resources: Sequence[Mapping[str, object]] = (),
                      resource_basis: Sequence[Mapping[str, object]] = (), *,
                      order: Callable[[list[str]], list[str]] | None = None,
                      parallel: bool = False,
                      subtopic_titles: Mapping[str, Mapping[str, str]] | None = None) -> dict:
    """Build deterministic derived contracts from the canonical browser projection.

    ``order`` and ``parallel`` only choose how independent workers are scheduled; the result is
    identical for every schedule.
    """
    questions = [enrich_question_refs(question) for question in browser_projection.get("questions", []) or []]
    validate_unique_ids(questions)
    scoped_resources = bind_topic_links([_resource_scope(resource) for resource in resources], questions)

    identity_basis = {
        "browser_projection_digest": digest(browser_projection),
        "resource_basis": list(resource_basis),
        "subtopic_titles": digest(dict(subtopic_titles or {})),
        "worker_contract_version": WORKER_CONTRACT_VERSION,
    }
    build_id = digest(identity_basis)
    views = browser_projection.get("views", []) or []
    results = run_nodes(platform_nodes(questions, scoped_resources, build_id, views, subtopic_titles),
                        order=order, parallel=parallel)
    catalog_worker, search_worker, dedup_worker = results["catalog"], results["search"], results["dedup"]
    summaries_worker = results["summaries"]
    lineage = results["lineage"].output
    workers = [catalog_worker.receipt, search_worker.receipt, dedup_worker.receipt, summaries_worker.receipt]
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "build_id": build_id,
        "basis": identity_basis,
        "counts": {
            "questions": len(questions),
            "resources": len(scoped_resources),
            "search_documents": search_worker.output["document_count"],
            "dedup_evidence": dedup_worker.output["evidence_count"],
            "near_duplicate_search_complete": dedup_worker.output["near_duplicate_coverage"]["complete"],
        },
        "workers": sorted(workers, key=lambda row: row["worker_id"]),
        "outputs": {
            "catalog": digest(catalog_worker.output),
            "search": digest(search_worker.output),
            "summaries": digest(summaries_worker.output),
            "resources": digest(scoped_resources),
            "dedup": digest(dedup_worker.output),
            "lineage": digest(lineage),
        },
    }
    return {
        "schema_version": PLATFORM_SCHEMA,
        "build_id": build_id,
        "catalog": catalog_worker.output,
        "summaries": summaries_worker.output,
        "search": search_worker.output,
        "resources": {"schema_version": RESOURCE_SCHEMA, "build_id": build_id, "resources": scoped_resources},
        "dedup": {**dedup_worker.output, "build_id": build_id},
        "lineage": lineage,
        "receipt": receipt,
    }


def render_js(global_name: str, value: object) -> str:
    return f"window.{global_name}=" + canonical_json(value) + ";\n"


def explain(platform: Mapping[str, object], record_id: str) -> dict | None:
    for row in platform.get("lineage", {}).get("questions", []) or []:
        if row.get("id") != record_id:
            continue
        search_document = next((
            document
            for document in platform.get("search", {}).get("documents", []) or []
            if document.get("id") == record_id
        ), None)
        return {"lineage": row, "search_document": search_document}
    return None
