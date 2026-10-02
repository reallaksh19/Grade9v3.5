"""One contract for the assurance chain: the schemas are the definition, and every producer and every consumer checks against them.

The chain is verifier -> evidence (AE) -> bundle -> eligibility. Each link is a JSON record with a schema in this directory. A record that does
not satisfy its schema is not evidence of anything: a producer refuses to write it, and a consumer refuses to read it. There is no second,
hand-written list of required fields (the first version of this chain had one, and the two drifted).

Digests are over canonical JSON for records and over LF-normalised bytes for files, so the same content digests the same on every checkout
(see `.gitattributes`).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from Shared.contracts import ContractError, canonical

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SCHEMAS = {
    "evidence": "assurance-evidence.schema.json",
    "bundle": "assurance-bundle.schema.json",
    "eligibility": "release-eligibility.schema.json",
    "policy": "policy.schema.json",
    "projection-manifest": "projection-manifest.schema.json",
    "release-fingerprint": "release-fingerprint.schema.json",
}
# Evidence is about a subject; it must not be written into the subject's own tree (that changes the digest it claims, and a Pages mirror is not a
# place for CI output).
PROTECTED_ROOTS = ("standalone", "docs", "public")


class ContractViolation(ContractError):
    """A record does not satisfy the schema it claims."""

    def __init__(self, kind: str, problems: list[str]):
        self.kind = kind
        self.problems = problems
        super().__init__("ASSURANCE_CONTRACT_VIOLATION", f"{kind}: " + "; ".join(problems[:5]) + (f" (+{len(problems) - 5} more)" if len(problems) > 5 else ""))


def _format_checker():
    from jsonschema import FormatChecker
    checker = FormatChecker()

    @checker.checks("date-time", raises=ValueError)
    def _date_time(value: Any) -> bool:       # the stock check needs an optional package, and silently passes without it
        if isinstance(value, str):
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    return checker


@lru_cache(maxsize=None)
def _validator(kind: str):
    from jsonschema import Draft202012Validator
    schema = json.loads((HERE / SCHEMAS[kind]).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=_format_checker())


def schema_problems(kind: str, record: Any) -> list[str]:
    """Every way `record` fails the schema of `kind`, one line each, in a stable order."""
    errors = sorted(_validator(kind).iter_errors(record), key=lambda e: tuple(str(x) for x in e.absolute_path))
    return [f"{'/'.join(str(x) for x in e.absolute_path) or '<root>'}: {e.message}" for e in errors]


def require_valid(kind: str, record: Any) -> Any:
    problems = schema_problems(kind, record)
    if problems:
        raise ContractViolation(kind, problems)
    return record


def digest(value: Any) -> str:
    """`sha256:` plus the digest of the canonical JSON of `value`."""
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def normalise_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(normalise_text(path.read_bytes())).hexdigest()


def digest_tree(root: Path, patterns: Iterable[str] = ("*",)) -> str | None:
    """Digest of the files under `root` that match `patterns`: their relative paths and LF-normalised bytes, in path order. None if there are none."""
    files = sorted({p for pattern in patterns for p in root.rglob(pattern) if p.is_file()}, key=lambda p: p.relative_to(root).as_posix())
    if not files:
        return None
    h = hashlib.sha256()
    for p in files:
        h.update(p.relative_to(root).as_posix().encode("utf-8") + b"\0" + normalise_text(p.read_bytes()) + b"\0")
    return "sha256:" + h.hexdigest()


def digest_roots(roots: Iterable[Path], patterns: Iterable[str] = ("*.json",)) -> str:
    """Digest of the files under several roots: each file named by its root (as the repository names it) and its path in the root, with LF-normalised bytes.

    The canonical inputs of a projection: every JSON file under the library directories it read. The same files give the same digest on every checkout."""
    patterns = tuple(patterns)
    entries = []
    for root in roots:
        root = Path(root)
        try:
            label = root.resolve().relative_to(REPO).as_posix()
        except ValueError:
            label = root.resolve().as_posix()
        for p in {q for pattern in patterns for q in root.rglob(pattern) if q.is_file()}:
            entries.append((f"{label}/{p.relative_to(root).as_posix()}", normalise_text(p.read_bytes())))
    h = hashlib.sha256()
    for name, data in sorted(entries):
        h.update(name.encode("utf-8") + b"\0" + data + b"\0")
    return "sha256:" + h.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def outside_subject_trees(path: Path) -> bool:
    """True when `path` is not under standalone/, docs/ or public/ of this repository."""
    try:
        first = path.resolve().relative_to(REPO).parts[0]
    except (ValueError, IndexError):
        return True
    return first not in PROTECTED_ROOTS


def write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
