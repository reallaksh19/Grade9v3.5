#!/usr/bin/env python3
"""Detect changed governed questions and linked assets; require scoped QRT receipts.

This is a change-scope gate, NOT a second QRT classification or academic approval.
It consumes Git's base...HEAD delta, the existing I1b coverage index, and existing
governed completion checks. Historical unmodified banks are never autoaccepted.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import qrt_coverage_report as coverage

SOURCE_ROOTS = ("Physics/", "Chemistry/", "Mathematics/", "TEST/")
SOURCE_AREAS = ("/library/", "/question-bank/", "/content/", "/research/packages/",
                "TEST/imo-research/", "TEST/question-bank/")
AUTHORITY_GLOBAL = frozenset({
    "Shared/quality/question-demand-matrix.v1.json",
    "Shared/quality/question-demand-templates.v1.json",
    "Shared/vocabularies/cognitive-demand.v1.json",
    "Shared/vocabularies/learner-question-metadata.v1.json",
    "Shared/web/interactive-page-blueprints.v1.json",
    "Shared/tools/render_core.py",
    "Shared/tools/core2_v2.py",
    "Shared/tools/qrt_pipeline_guard.py",
    "Shared/tools/qrt_content_self_audit.py",
    "Shared/tools/question_review_matrix.py",
    "Shared/tools/question_difficulty.py",
    "Shared/web/explorer-runtime.js",
    "Shared/web/explorer-model.js",
    "Shared/web/explorer-profiles.v1.json",
    "Shared/web/explorer-spec.schema.json",
})
RESOURCE_EXTENSIONS = {".html", ".htm", ".svg", ".png", ".jpg", ".jpeg",
                       ".webp", ".gif", ".css", ".js", ".mjs", ".json", ".pdf"}
CSS_URLS = re.compile(r"""url\(\s*['"]?([^'")]+)""", re.IGNORECASE)
CSS_IMPORTS = re.compile(r"""@import\s+['"]([^'"]+)['"]""", re.IGNORECASE)
JS_IMPORTS = re.compile(r"""\b(?:import|export)\s+(?:[^;]*?\s+from\s+)?['"]([^'"]+)['"]""")
MAX_DEPENDENCIES = 1000


def _finding(code: str, where: str, detail: str = "") -> dict[str, str]:
    return {"code": code, "where": where, "detail": detail}


def _json(raw: str, where: str) -> tuple[dict | None, list[dict[str, str]]]:
    if not raw.strip():
        return None, []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [_finding("CHANGED_SOURCE_JSON_INVALID", where, str(exc))]
    if not isinstance(data, dict):
        return None, [_finding("CHANGED_SOURCE_NOT_OBJECT", where)]
    return data, []


def _question_records(data: dict) -> tuple[dict[str, dict], list[dict[str, str]]]:
    """Recognize actual governed questions; do not mistake arbitrary manifest rows for questions."""
    found: dict[str, dict] = {}
    problems: list[dict[str, str]] = []

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            if isinstance(value.get("id"), str) and (
                isinstance(value.get("stem"), str)
                or isinstance(value.get("verbatim_text"), str)
                or (key == "records" and ("source_question" in value or "question" in value))
            ):
                qid = value["id"]
                if qid in found:
                    problems.append(_finding("CHANGED_SOURCE_DUPLICATE_QUESTION_ID", qid))
                found[qid] = value
                return
            for child_key, child in value.items():
                if isinstance(child, dict):
                    visit(child, child_key)
                elif isinstance(child, list) and child_key in {
                    "questions", "records", "microtopics", "topics", "units",
                    "sections", "practice_families", "packages",
                }:
                    for row in child:
                        visit(row, child_key)
        elif isinstance(value, list) and key in {"questions", "records", "microtopics"}:
            for row in value:
                visit(row, key)

    visit(data)
    return found, problems


def question_delta(path: str, before_text: str, after_text: str) -> tuple[list[dict], list[dict]]:
    """Changed/new/deleted IDs and conservative source-envelope invalidation."""
    before, b_err = _json(before_text, path)
    after, a_err = _json(after_text, path)
    problems = b_err + a_err
    old, old_errors = _question_records(before or {})
    new, new_errors = _question_records(after or {})
    problems.extend(old_errors + new_errors)
    for doc in (before, after):
        if doc is not None and isinstance(doc.get("questions"), list) and doc["questions"] and not (
            old if doc is before else new
        ):
            problems.append(_finding("QUESTION_COLLECTION_FORMAT_UNRECOGNIZED", path))
    result: list[dict] = []
    for qid in sorted(set(old) | set(new)):
        if qid not in new:
            result.append({"question_ref": qid, "source_path": path, "reason": "QUESTION_REMOVED"})
        elif qid not in old:
            result.append({"question_ref": qid, "source_path": path, "reason": "QUESTION_ADDED"})
        elif new[qid] != old[qid]:
            result.append({"question_ref": qid, "source_path": path, "reason": "QUESTION_MODIFIED"})
    # A bank resource, provenance, shared figure or metadata edit can change
    # what every included question means even if question rows are untouched.
    if old and new and before != after:
        old_meta = {k: v for k, v in (before or {}).items() if k not in {"questions", "records"}}
        new_meta = {k: v for k, v in (after or {}).items() if k not in {"questions", "records"}}
        if old_meta != new_meta:
            active = {x["question_ref"] for x in result}
            for qid in sorted(set(new) - active):
                result.append({"question_ref": qid, "source_path": path,
                               "reason": "BANK_ENVELOPE_CHANGED"})
    if after is not None and not new and old:
        # A replacement lacking question records must not silently erase all coverage.
        problems.append(_finding("QUESTION_CONTAINER_DISAPPEARED", path))
    return result, problems


def _is_governed_source(path: str) -> bool:
    return (path.endswith((".json", ".jsonl")) and path.startswith(SOURCE_ROOTS)
            and any(area in path for area in SOURCE_AREAS))


class _Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        for name in ("src", "href", "poster", "data", "xlink:href"):
            ref = attributes.get(name)
            if isinstance(ref, str):
                self.refs.add(ref)
        if isinstance(attributes.get("srcset"), str):
            for item in attributes["srcset"].split(","):
                self.refs.add(item.strip().split(" ")[0])


def _resolve_link(repo: Path, origin: Path, raw: str) -> Path | None:
    raw = raw.strip()
    if not raw or raw.startswith(("#", "//")):
        return None
    bits = urlsplit(raw)
    if bits.scheme or bits.netloc or not bits.path:
        return None
    path = unquote(bits.path)
    candidate = ((repo / path.lstrip("/")) if path.startswith("/")
                 else (origin.parent / path)).resolve()
    if not candidate.is_relative_to(repo.resolve()):
        return None
    if candidate.suffix.lower() not in RESOURCE_EXTENSIONS:
        return None
    return candidate


def linked_dependencies(repo: Path, origin: str) -> tuple[set[str], list[dict[str, str]]]:
    """Static graph of local HTML/CSS/JS refs, bounded and deterministic.

    Not runtime JS/network reachability or W safety: the governed full QRT gate
    still owns transitive pre-attempt semantic reachability.
    """
    root, error = coverage._path(repo, origin)
    if error or root is None:
        return set(), [_finding("ARTIFACT_PATH_INVALID", str(origin))]
    pending = [root]
    seen: set[Path] = set()
    findings: list[dict[str, str]] = []
    while pending:
        path = pending.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if len(seen) > MAX_DEPENDENCIES:
            findings.append(_finding("STATIC_RESOURCE_GRAPH_LIMIT", origin))
            break
        if not path.is_file():
            findings.append(_finding("REACHABLE_LOCAL_RESOURCE_MISSING", path.relative_to(repo).as_posix()))
            continue
        if path.suffix.lower() not in {".html", ".htm", ".css", ".js", ".mjs"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            findings.append(_finding("REACHABLE_RESOURCE_NOT_UTF8", path.relative_to(repo).as_posix()))
            continue
        refs: set[str] = set()
        if path.suffix.lower() in {".html", ".htm"}:
            parser = _Refs()
            parser.feed(text)
            refs = parser.refs
        elif path.suffix.lower() == ".css":
            refs = set(CSS_URLS.findall(text)) | set(CSS_IMPORTS.findall(text))
        elif path.suffix.lower() in {".js", ".mjs"}:
            refs = set(JS_IMPORTS.findall(text))
        for raw in sorted(refs):
            target = _resolve_link(repo, path, raw)
            if target is not None and target not in seen and target not in pending:
                pending.append(target)
    return {p.relative_to(repo).as_posix() for p in seen}, findings


def diff_paths(repo: Path, base: str) -> list[str]:
    if not re.fullmatch(r"[0-9a-f]{40}", base):
        raise ValueError("base must be a real forty-character Git SHA")
    query = subprocess.run(["git", "diff", "--name-only", "--no-renames",
                            f"{base}...HEAD", "--"], cwd=repo, text=True,
                           capture_output=True, check=False)
    if query.returncode:
        raise ValueError("git diff failed: " + query.stderr.strip())
    return sorted(set(line for line in query.stdout.splitlines() if line))


def prior_file(repo: Path, base: str, path: str) -> str:
    # Explicit pathspec limits the lookup to a repository file; missing means new.
    p = subprocess.run(["git", "show", f"{base}:{path}"], cwd=repo,
                       capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else ""


def discover(
    repo: Path, *, base: str, head: str, paths: list[str],
    before: Any, index: dict,
) -> dict:
    """Return complete changed scope + missing/broken receipts. No silent empty-index pass."""
    changed = sorted(set(paths))
    impacted: list[dict] = []
    findings: list[dict[str, str]] = []
    global_changes = sorted(set(changed) & AUTHORITY_GLOBAL)
    scope_files: set[str] = set(global_changes)
    for path in changed:
        if not _is_governed_source(path):
            continue
        source, error = coverage._path(repo, path)
        if error:
            findings.append(_finding("CHANGED_PATH_UNSAFE", path))
            continue
        assert source is not None
        try:
            old = before(path)
            fresh = source.read_text(encoding="utf-8") if source.is_file() else ""
        except (OSError, UnicodeError) as exc:
            findings.append(_finding("CHANGED_SOURCE_UNREADABLE", path, str(exc)))
            continue
        if path.endswith(".jsonl"):
            # JSONL inventory is not currently a canonical QRT question schema.
            # Do not claim safety by ignoring a changed, unparsed source.
            findings.append(_finding("CHANGED_QUESTION_JSONL_REQUIRES_ADAPTER", path))
            scope_files.add(path)
            continue
        changes, problems = question_delta(path, old, fresh)
        impacted.extend(changes)
        findings.extend(problems)
        if changes or problems:
            scope_files.add(path)
    items = index.get("items") if isinstance(index, dict) else None
    if not isinstance(items, list):
        items = []
        findings.append(_finding("COVERAGE_INDEX_INVALID", "index"))

    tracked: dict[str, list[dict]] = {}
    for row in items:
        if not isinstance(row, dict):
            findings.append(_finding("COVERAGE_ITEM_INVALID", "index"))
            continue
        qid = str(row.get("question_ref") or "")
        tracked.setdefault(qid, []).append(row)
        dependents = {r.get("path") for r in row.get("tracked_inputs") or []
                      if isinstance(r, dict)}
        run = row.get("run") or {}
        run_path, run_error = coverage._path(repo, run.get("path"))
        if not run_error and run_path is not None and run_path.is_file():
            try:
                data = json.loads(run_path.read_text(encoding="utf-8"))
                for artifact in data.get("rendered_artifacts") or []:
                    if not isinstance(artifact, dict):
                        continue
                    artifact_path = artifact.get("path")
                    if isinstance(artifact_path, str):
                        deps, errors = linked_dependencies(repo, artifact_path)
                        dependents.update(deps)
                        findings.extend(errors)
            except (OSError, ValueError, TypeError):
                findings.append(_finding("INDEXED_RUN_RESOURCE_GRAPH_UNREADABLE", qid))
        hit = sorted(set(changed) & dependents)
        if hit or global_changes:
            reason = "LINKED_DEPENDENCY_CHANGED" if hit else "GLOBAL_QRT_OR_RENDER_AUTHORITY_CHANGED"
            impacted.append({"question_ref": qid, "source_path": row.get("question_source_path"),
                             "reason": reason, "changed_dependencies": hit or global_changes})
            scope_files.update(hit)
    if global_changes and not items:
        findings.append(_finding("GLOBAL_CHANGE_WITHOUT_INDEXED_QRT_SCOPE", ",".join(global_changes)))
    # New published HTML/PDF, product manifolds and images can affect unindexed
    # questions; never silently classify these as routine unrelated edits.
    unindexed_surfaces = [
        path for path in changed
        if path.startswith(SOURCE_ROOTS) and (
            "/publication/" in path and path.endswith((".html", ".svg", ".pdf", "manifest.json"))
            or path.startswith("TEST/products/") and path.endswith(".manifest.json")
            or path.endswith((".svg", ".png", ".webp", ".css", ".js", ".mjs"))
            and ("/library/figures/" in path or "/content/" in path)
        )
    ]
    for path in unindexed_surfaces:
        if not any(path in (row.get("changed_dependencies") or []) for row in impacted):
            findings.append(_finding("PUBLISHED_SURFACE_WITHOUT_QRT_BINDING", path))
        scope_files.add(path)
    deduped: dict[tuple[str, str], dict] = {}
    for row in impacted:
        key = (str(row["question_ref"]), str(row["reason"]))
        deduped[key] = row
    rows: list[dict] = []
    for effect in sorted(deduped.values(), key=lambda x: (str(x["question_ref"]), str(x["reason"]))):
        qid = effect["question_ref"]
        matches = tracked.get(qid, [])
        if len(matches) != 1 or effect["reason"] == "QUESTION_REMOVED":
            findings.append(_finding(
                "CHANGED_QUESTION_REVIEW_REQUIRED" if effect["reason"] != "QUESTION_REMOVED"
                else "QUESTION_REMOVAL_REQUIRES_LINEAGE_REVIEW",
                str(qid), str(effect["reason"]),
            ))
            continue
        if effect.get("source_path") and matches[0].get("question_source_path") != effect["source_path"]:
            findings.append(_finding("INDEXED_SOURCE_IDENTITY_MISMATCH", str(qid),
                                     str(effect["source_path"])))
            continue
        result = coverage.candidate(repo, matches[0], head=head)
        rows.append(result)
        if result["status"] != "REVIEW_EVIDENCE_COMPLETE_NOT_ACCEPTANCE":
            findings.append(_finding("SCOPED_QRT_REVIEW_NOT_CURRENT", str(qid), result["status"]))
        if "changed_dependencies" in effect:
            changed_dep = effect["changed_dependencies"]
            inputs = {r.get("path") for r in matches[0].get("tracked_inputs") or []
                      if isinstance(r, dict)}
            run_ref = (matches[0].get("run") or {}).get("path")
            if isinstance(run_ref, str):
                inputs.add(run_ref)
            for dep in changed_dep:
                if dep not in inputs and dep not in AUTHORITY_GLOBAL:
                    findings.append(_finding("CHANGED_REACHABLE_RESOURCE_NOT_PINNED", str(qid), dep))
    return {
        "schema": "qrt-change-discovery/v1",
        "base_sha": base, "head_sha": head, "changed_path_count": len(changed),
        "scope_changed_paths": sorted(scope_files),
        "impacts": sorted(deduped.values(), key=lambda x: (str(x["question_ref"]), str(x["reason"]))),
        "evaluated_candidates": rows,
        "findings": findings,
        "pass_changed_scope": not findings,
        "no_relevant_changes": not scope_files and not findings,
        "repository_wide_qrt_acceptance": "NOT_EVALUATED",
        "academic_acceptance": "NOT_EVALUATED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="PR base commit SHA, never a moving remote branch")
    parser.add_argument("--index", type=Path, default=REPO / "docs/qrt-coverage-index.v1.json")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--enforce", action="store_true", help="Fail for missing changed-scope receipts")
    args = parser.parse_args(argv)
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                              text=True, capture_output=True, check=True).stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{40}", head):
            raise ValueError("current Git HEAD invalid")
        if not re.fullmatch(r"[0-9a-f]{40}", args.base):
            raise ValueError("base Git SHA invalid")
        index = json.loads(args.index.read_text(encoding="utf-8"))
        delta = diff_paths(REPO, args.base)
        result = discover(
            REPO, base=args.base, head=head, paths=delta,
            before=lambda path: prior_file(REPO, args.base, path),
            index=index,
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"QRT_DISCOVERY_FAILED: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(output, end="")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    return 1 if args.enforce and not result["pass_changed_scope"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
