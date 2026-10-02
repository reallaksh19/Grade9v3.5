"""From evidence to a decision: the rules, in one place, as functions of validated records.

What a product needs is a policy (Shared/assurance/policies): for each kind of subject, which assurance types must hold and how. What exists is
evidence, each record bound to the content it judged. The bundle states the join; the eligibility record is the decision. Both are recomputed
from the evidence by whoever consumes them, and nothing in either is trusted.

The rules, each of which a test breaks if it is removed:

  * A need is a (type, subject) pair for every subject of the policy's kind. Evidence about some other subject satisfies nothing.
  * Evidence counts only if its subject digest is the subject's digest now; evidence of older content is stale and the need stays open.
  * Several records for one need reduce to the worst (FAIL, INCONCLUSIVE, NOT_RUN, PASS, NOT_APPLICABLE); the last one written does not win.
  * required_pass is satisfied only by PASS; required_pass_or_na by PASS or NOT_APPLICABLE; required_pass_or_reviewed by those or by a waiver
    that names the need, gives a reason and says where the approval was given.
  * A policy with no subject of its kind is not satisfied: nothing proved is not everything proved.
  * An evidence file that is unreadable, schema-invalid, edited after it was written, or missing though the bundle cites it breaks the bundle.
  * A bundle whose id, digest or outcomes are not what its evidence gives is broken, and so is a PASS that carries an S0 or S1 finding.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from Shared.assurance import contract
from Shared.assurance.evidence import load_evidence
from Shared.contracts import canonical

ContractViolation_ = contract.ContractViolation

RANK = {"NOT_APPLICABLE": 0, "PASS": 1, "NOT_RUN": 2, "INCONCLUSIVE": 3, "FAIL": 4}
SATISFIES = {"required_pass": {"PASS"}, "required_pass_or_na": {"PASS", "NOT_APPLICABLE"}, "required_pass_or_reviewed": {"PASS", "NOT_APPLICABLE"}}
BUCKETS = tuple(SATISFIES)
SEVERE = ("S0", "S1")
MIN_WAIVER_REASON = 10


@dataclass(frozen=True)
class Subject:
    kind: str
    id: str
    digest: str
    path: str

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.id}"

    def row(self) -> dict:
        return {"kind": self.kind, "id": self.id, "digest": self.digest, "path": self.path}


def cell_key(assurance_type: str, subject: Subject) -> str:
    return f"{assurance_type}@{subject.key}"


def reduce_outcomes(outcomes: Iterable[str]) -> str | None:
    """The worst of `outcomes`, or None if there are none."""
    found = list(outcomes)
    return max(found, key=RANK.__getitem__) if found else None


def required_types(policies: list[dict]) -> list[str]:
    return sorted({t for p in policies for b in BUCKETS for t in p.get(b, [])})


# -- subjects -----------------------------------------------------------------------------------------------------------------------------------

def subject_from(kind: str, subject_id: str, path: str, repo: Path = contract.REPO) -> Subject:
    """A subject as it is now: its digest is taken from the file, or the tree, at `path` (relative to the repository)."""
    target = repo / path
    if target.is_dir():
        digest = contract.digest_tree(target)
        if digest is None:
            raise ValueError(f"{path} holds no files to judge")
    elif target.is_file():
        digest = contract.digest_file(target)
    else:
        raise ValueError(f"{path} does not exist")
    return Subject(kind, subject_id, digest, Path(path).as_posix())


def package_subjects(paths: Iterable[str], repo: Path = contract.REPO) -> list[Subject]:
    """One canonical subject per package file; a directory stands for the `*.json` files directly in it."""
    out: list[Subject] = []
    for raw in paths:
        target = (repo / raw)
        files = sorted(target.glob("*.json")) if target.is_dir() else [target]
        for f in files:
            try:
                package_id = json.loads(f.read_text(encoding="utf-8")).get("package_id") or f.stem
            except (OSError, ValueError, AttributeError):
                package_id = f.stem                         # an unreadable package is still a subject: its verifiers say FAIL
            out.append(subject_from("CANONICAL_RECORD", package_id, f.relative_to(repo).as_posix(), repo))
    return out


def projection_subjects(specs: Iterable[str], repo: Path = contract.REPO) -> list[Subject]:
    """`id=path` for each projection (a directory of pages, or one file)."""
    out: list[Subject] = []
    for spec in specs:
        pid, _, path = spec.partition("=")
        if not pid or not path:
            raise ValueError(f"a projection is ID=PATH, not {spec!r}")
        out.append(subject_from("PROJECTION", pid, path, repo))
    return out


def policies_dir() -> Path:
    return contract.HERE / "policies"


def load_policies(ids: Iterable[str] | None = None, extra: Iterable[Path] = ()) -> list[dict]:
    """The policies named by `ids` (all of them if None), each checked against the policy schema."""
    from Shared.assurance.evidence import load_policy
    found = {}
    for path in sorted([*policies_dir().glob("*.json"), *extra]):
        policy = load_policy(path)
        found[policy["policy_id"]] = policy
    if ids is None:
        return [found[k] for k in sorted(found)]
    missing = [i for i in ids if i not in found]
    if missing:
        raise ContractViolation_("policy", [f"no policy {m!r}" for m in missing])
    return [found[i] for i in sorted(set(ids))]


def snapshot_digest(subjects: Iterable[Subject]) -> str:
    return contract.digest(sorted([s.kind, s.id, s.digest] for s in subjects if s.kind == "CANONICAL_RECORD"))


# -- evidence ------------------------------------------------------------------------------------------------------------------------------------

def collect(evidence_dir: Path, refs: Iterable[str] | None = None) -> tuple[dict[str, dict], list[dict]]:
    """Validated evidence by id, and the problems found: a file that is unreadable, invalid, edited or (when `refs` is given) missing."""
    records: dict[str, dict] = {}
    problems: list[dict] = []
    if refs is None:
        paths = sorted(evidence_dir.rglob("*.json")) if evidence_dir.is_dir() else []
        wanted = None
    else:
        wanted = sorted(set(refs))
        paths = [evidence_dir / f"{ref}.json" for ref in wanted]
    for path in paths:
        if not path.is_file():
            problems.append({"code": "EVIDENCE_MISSING", "message": f"{path.name} is cited and not there"})
            continue
        try:
            record = load_evidence(path)
        except contract.ContractError as exc:
            problems.append({"code": "EVIDENCE_INVALID", "message": f"{path.name}: {exc.detail or exc}"[:300]})
            continue
        if wanted is not None and record["evidence_id"] != path.stem:
            problems.append({"code": "EVIDENCE_MISPLACED", "message": f"{path.name} holds {record['evidence_id']}"})
            continue
        records[record["evidence_id"]] = record
    return records, problems


def load_waivers(path: Path | None) -> dict[str, dict]:
    """Waivers by need (`TYPE@KIND:ID`). Each names the need, gives a reason and says where the approval was given."""
    if path is None:
        return {}
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for row in rows:
        out[f"{row['type']}@{row['subject']}"] = row
    return out


# -- evaluation ----------------------------------------------------------------------------------------------------------------------------------

@dataclass
class Evaluation:
    outcomes: dict[str, str] = field(default_factory=dict)         # need -> reduced outcome, or MISSING / STALE
    missing: list[dict] = field(default_factory=list)              # needs that are not satisfied
    failing: list[str] = field(default_factory=list)               # needs whose evidence says FAIL
    severe: list[dict] = field(default_factory=list)               # S0 / S1 findings anywhere in the evidence considered
    reviewable: list[dict] = field(default_factory=list)           # S2 / S3 findings
    considered: list[str] = field(default_factory=list)            # ids of the evidence about the expected subjects, current
    problems: list[dict] = field(default_factory=list)

    @property
    def hard_integrity(self) -> str:
        return "FAIL" if (self.failing or self.severe or self.problems) else "PASS"

    @property
    def missing_types(self) -> list[str]:
        return sorted({m["type"] for m in self.missing})


def evaluate(subjects: list[Subject], policies: list[dict], records: Mapping[str, dict], waivers: Mapping[str, dict] | None = None) -> Evaluation:
    waivers = waivers or {}
    ev = Evaluation()
    by_subject = {s.key: s for s in subjects}
    for key, waiver in waivers.items():
        reason = str(waiver.get("reason", "")).strip()
        if len(reason) < MIN_WAIVER_REASON or not str(waiver.get("approval_ref", "")).strip():
            ev.problems.append({"code": "WAIVER_INVALID", "message": f"{key}: a waiver gives a reason of at least {MIN_WAIVER_REASON} characters and says where it was approved"})
    valid_waivers = {k for k, w in waivers.items() if len(str(w.get("reason", "")).strip()) >= MIN_WAIVER_REASON and str(w.get("approval_ref", "")).strip()}

    current: dict[tuple[str, str, str], list[dict]] = {}
    stale: dict[tuple[str, str, str], int] = {}
    for record in records.values():
        subject = by_subject.get(f"{record['subject']['kind']}:{record['subject']['id']}")
        if subject is None:
            continue
        cell = (record["assurance_type"], record["subject"]["kind"], record["subject"]["id"])
        if record["subject"]["digest"] == subject.digest:
            current.setdefault(cell, []).append(record)
        else:
            stale[cell] = stale.get(cell, 0) + 1
    seen_findings: set[tuple] = set()
    for group in current.values():
        for record in group:
            ev.considered.append(record["evidence_id"])
            if record["outcome"] == "PASS" and any(f["severity"] in SEVERE for f in record["findings"]):
                ev.problems.append({"code": "PASS_WITH_SEVERE_FINDING", "message": f"{record['evidence_id']} says PASS and carries an S0 or S1 finding"})
            for f in record["findings"]:
                row = {"code": f["code"], "severity": f["severity"], "subject": f["subject"], "message": f["message"]}
                marker = (row["code"], row["severity"], row["subject"], row["message"])
                if marker in seen_findings:
                    continue
                seen_findings.add(marker)
                (ev.severe if f["severity"] in SEVERE else ev.reviewable).append(row)
    ev.considered = sorted(set(ev.considered))

    for policy in policies:
        mine = [s for s in subjects if s.kind == policy["subject_kind"]]
        if not mine:
            for bucket in BUCKETS:
                for t in policy.get(bucket, []):
                    ev.missing.append({"type": t, "subject": f"{policy['subject_kind']}:*", "reason": "NO_SUBJECTS"})
            continue
        for bucket in BUCKETS:
            for t in policy.get(bucket, []):
                for s in mine:
                    cell = (t, s.kind, s.id)
                    group = current.get(cell, [])
                    outcome = reduce_outcomes(r["outcome"] for r in group) or ("STALE" if stale.get(cell) else "MISSING")
                    ev.outcomes[cell_key(t, s)] = outcome
                    waived = bucket == "required_pass_or_reviewed" and cell_key(t, s) in valid_waivers
                    if outcome == "FAIL":
                        ev.failing.append(cell_key(t, s))
                    if outcome not in SATISFIES[bucket] and not waived:
                        ev.missing.append({"type": t, "subject": s.key, "reason": outcome})
    return ev


# -- bundle --------------------------------------------------------------------------------------------------------------------------------------

def _bundle_body(product: str, subjects: list[Subject], policies: list[dict], ev: Evaluation) -> dict:
    return {
        "schema": "assurance-bundle/v1",
        "subject": {"kind": "PRODUCT", "id": product},
        "canonical_snapshot_digest": snapshot_digest(subjects),
        "policies": sorted(p["policy_id"] for p in policies),
        "subjects": [s.row() for s in sorted(subjects, key=lambda s: s.key)],
        "evidence_refs": ev.considered,
        "required_types": required_types(policies),
        "missing_types": ev.missing_types,
        "outcomes": dict(sorted(ev.outcomes.items())),
        "missing": sorted(ev.missing, key=lambda m: (m["type"], m["subject"])),
        "problems": ev.problems,
    }


def build_bundle(product: str, subjects: list[Subject], policies: list[dict], ev: Evaluation) -> dict:
    body = _bundle_body(product, subjects, policies, ev)
    body["bundle_id"] = "AB-" + hashlib.sha256(canonical(body)).hexdigest()[:16]
    body["bundle_digest"] = contract.digest(body)
    body["bundled_at"] = contract.now()
    return contract.require_valid("bundle", body)


def verify_bundle(bundle: dict) -> list[dict]:
    """Problems in a bundle's own id and digest: they are what its content gives, or the bundle was edited."""
    body = {k: v for k, v in bundle.items() if k not in ("bundle_id", "bundle_digest", "bundled_at")}
    problems = []
    if bundle["bundle_id"] != "AB-" + hashlib.sha256(canonical(body)).hexdigest()[:16]:
        problems.append({"code": "BUNDLE_ID_MISMATCH", "message": "bundle_id is not the digest of the bundle's content"})
    if bundle["bundle_digest"] != contract.digest({**body, "bundle_id": bundle["bundle_id"]}):
        problems.append({"code": "BUNDLE_DIGEST_MISMATCH", "message": "bundle_digest is not the digest of the bundle's content"})
    return problems


# -- decision ------------------------------------------------------------------------------------------------------------------------------------

def subjects_of(bundle: dict) -> list[Subject]:
    return [Subject(s["kind"], s["id"], s["digest"], s["path"]) for s in bundle["subjects"]]


def evaluate_release(bundle: dict, evidence_dir: Path, policies: list[dict], waivers: Mapping[str, dict] | None = None,
                     repo: Path = contract.REPO) -> dict:
    """The eligibility record for `bundle`, recomputed from its evidence and from the subjects as they are now.

    Raises ContractViolation if the bundle does not satisfy its schema: a decision is not made on a record that cannot be read.
    """
    contract.require_valid("bundle", bundle)
    problems = verify_bundle(bundle)
    records, collected = collect(evidence_dir, bundle["evidence_refs"])
    problems += collected

    if sorted(p["policy_id"] for p in policies) != bundle["policies"]:
        problems.append({"code": "POLICY_MISMATCH", "message": f"the bundle was built for {bundle['policies']}, not for the policies given"})
    recorded = subjects_of(bundle)
    claimed = evaluate(recorded, policies, records)       # the bundle is facts: waivers are a decision, applied below
    if (dict(sorted(claimed.outcomes.items())) != bundle["outcomes"] or claimed.missing_types != bundle["missing_types"]
            or snapshot_digest(recorded) != bundle["canonical_snapshot_digest"] or required_types(policies) != bundle["required_types"]):
        problems.append({"code": "BUNDLE_MISMATCH", "message": "the bundle's outcomes, snapshot or required types are not what its own evidence and subjects give"})

    now: list[Subject] = []
    for s in recorded:
        try:
            now.append(subject_from(s.kind, s.id, s.path, repo))
        except ValueError as exc:
            problems.append({"code": "SUBJECT_MISSING", "message": f"{s.key}: {exc}"})
            now.append(Subject(s.kind, s.id, "sha256:" + "0" * 64, s.path))
    decided = evaluate(now, policies, records, waivers)
    stale = [s.key for s, n in zip(recorded, now) if s.digest != n.digest]
    problems += decided.problems
    if stale and not any(p["code"] == "SUBJECT_MISSING" for p in problems):
        decided.missing.append({"type": "*", "subject": ", ".join(stale), "reason": "STALE_SNAPSHOT"})

    hard = "FAIL" if (decided.failing or decided.severe or [p for p in problems if p["code"] != "WAIVER_INVALID"]) else "PASS"
    if hard == "FAIL":
        status = "INELIGIBLE"
    elif decided.missing:
        status = "INCOMPLETE"
    else:
        status = "ELIGIBLE"
    projections = {s.id: s.digest for s in now if s.kind == "PROJECTION" and s.id in ("web", "standalone", "pdf", "search")}
    record = {
        "schema": "release-eligibility/v1",
        "product": bundle["subject"]["id"],
        "canonical_snapshot_digest": snapshot_digest(now),
        "assurance_bundle_digest": bundle["bundle_digest"],
        "hard_integrity": hard,
        "reviewable_findings": decided.reviewable + decided.severe,
        "missing": sorted(decided.missing, key=lambda m: (m["type"], m["subject"])),
        "problems": problems,
        "status": status,
        "evaluated_at": contract.now(),
    }
    if projections:
        record["projection_digests"] = projections
    return contract.require_valid("eligibility", record)
