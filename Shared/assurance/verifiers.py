"""The verifiers: each reads a subject and says, per assurance type, what it found. The runner turns the verdicts into evidence.

Every check that was written for the blueprint (the question admission points, the page rules) or for the library (intake, the resolver) is run here, once, and
reported in the one vocabulary of the assurance chain: an evidence record per (assurance type, subject), bound to the digest of what was judged. The blueprint
registry says which assurance type each admission point and each page rule feeds (`assurance_type` on the point or rule); nothing here has a second table.

Honesty about coverage: a verdict is PASS only for what was checked. A check that proves part of a type does not report PASS for the type. Static page rules cannot
prove a layout, so they feed PROJECTION_STATIC_CONFORMANCE and leave RESPONSIVE_LAYOUT and ACCESSIBILITY with no evidence (open) until a rendered audit writes
some. Self-containment, answer correctness and dimensional correctness are checked only for questions that declare what they give and how to compute it
(typed.py); a package whose questions declare nothing is INCONCLUSIVE for self-containment, not PASS.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from Shared.assurance import aggregate, contract, typed
from Shared.assurance.aggregate import Subject
from Shared.assurance.evidence import finding, make_evidence, write_evidence
from Shared.contracts import ContractError

PRODUCER = "assurance_run"
VERSION = "1.0.0"
PACKAGE_TYPES = ("STRUCTURAL_VALIDITY", "REFERENCE_INTEGRITY", "CORPUS_SPECIFICITY", "SELF_CONTAINMENT", "ANSWER_CORRECTNESS", "DIMENSIONAL_CORRECTNESS",
                 "REASONING_VALIDITY", "SCOPE_CONFORMANCE", "DISCLOSURE_CONFORMANCE")
PAGE_TYPES = ("NETWORK_POLICY", "LINK_INTEGRITY", "PROJECTION_STATIC_CONFORMANCE")
SUBSTANCE_POINTS = {"DUPLICATED", "TEMPLATED", "SELF_NAMING", "NAMED_WITHOUT_DEMONSTRATING"}   # intake's corpus checks (Shared/library/substance.py)
SEVERITY_OF = {"BLOCK": "S1", "ADVISE": "S3"}
FEW = 8        # how many examples an aggregate finding names


@dataclass
class Verdict:
    outcome: str
    findings: list[dict] = field(default_factory=list)


def _registry() -> dict:
    from Shared.tools import web_blueprint_contract
    return web_blueprint_contract.load_registry()


def point_types() -> dict[str, str]:
    return {p["id"]: p["assurance_type"] for p in _registry()["component_policy"]["admission"]["points"]}


def rule_types() -> dict[str, str]:
    return {r["id"]: r["assurance_type"] for r in _registry()["shell"]["standalone_policy"]["rules"]}


def configuration() -> dict:
    """What the verifiers were configured with: the registry that names the points and rules, the thresholds, the scope policy. Its digest is the producer's."""
    from Shared.library import question_admission as qa
    return {"registry_version": _registry()["registry_version"],
            "admission": {"stem_min_words": qa.STEM_MIN_WORDS, "anchors_min": qa.ANCHORS_MIN, "worked_min_steps": qa.WORKED_MIN_STEPS,
                          "worked_min_chars": qa.WORKED_MIN_CHARS, "summary_max_chars": qa.SUMMARY_MAX_CHARS},
            "scope_policy": contract.digest(json.loads(qa.SCOPE_POLICY.read_text(encoding="utf-8")))}


def _split(detail: str, default: str) -> tuple[str, str]:
    head, sep, rest = detail.partition(": ")
    return (head, rest) if sep and " " not in head else (default, detail)


def _verdict(rows: list[dict]) -> Verdict:
    return Verdict("FAIL" if any(f["severity"] in ("S0", "S1") for f in rows) else "PASS", rows)


# -- canonical packages -----------------------------------------------------------------------------------------------------------------------

def verify_package(subject: Subject, repo: Path) -> dict[str, Verdict]:
    """A verdict for each package-level assurance type except REFERENCE_INTEGRITY (which needs the whole library: verify_references)."""
    import importlib.util
    from Shared.library import intake, question_admission as qa
    if importlib.util.find_spec("jsonschema") is None:             # without it intake reports no schema errors: a check that cannot run is not a pass
        return {t: Verdict("NOT_RUN", [finding("JSONSCHEMA_MISSING", "S3", subject.id, "jsonschema is not installed, so nothing was validated")])
                for t in PACKAGE_TYPES if t != "REFERENCE_INTEGRITY"}
    try:
        package = json.loads((repo / subject.path).read_text(encoding="utf-8"))
        if not isinstance(package, dict):
            raise ValueError("the file is not a JSON object")
    except (OSError, ValueError) as exc:
        out = {t: Verdict("NOT_RUN") for t in PACKAGE_TYPES if t != "REFERENCE_INTEGRITY"}
        out["STRUCTURAL_VALIDITY"] = Verdict("FAIL", [finding("UNPARSEABLE", "S1", subject.id, f"the package cannot be read: {exc}"[:300], location=subject.path)])
        return out
    types = point_types()
    rows: dict[str, list[dict]] = defaultdict(list)

    for message in intake.schema_errors(package):
        rows["STRUCTURAL_VALIDITY"].append(finding("SCHEMA", "S1", subject.id, message[:300], location=subject.path))
    for f in intake.check(package)["findings"]:
        if f["point"] == "STRUCTURE" or f["point"].startswith(("QUESTION_", "ANSWER_")):
            continue                                                  # the schema errors are reported above; the question points below
        kind = "CORPUS_SPECIFICITY" if f["point"] in SUBSTANCE_POINTS else "STRUCTURAL_VALIDITY"
        who, message = _split(f["detail"], subject.id)
        rows[kind].append(finding(f["point"], "S1", who, message[:300]))
    for f in qa.findings(package):
        who, message = _split(f["detail"], subject.id)
        rows[types[f["point"]]].append(finding(f["point"], SEVERITY_OF[f["severity"]], who, message[:300]))

    out = {t: _verdict(rows[t]) for t in ("STRUCTURAL_VALIDITY", "CORPUS_SPECIFICITY", "SCOPE_CONFORMANCE", "DISCLOSURE_CONFORMANCE")}
    questions = [q for q in package.get("questions", []) if isinstance(q, dict)]
    out["REASONING_VALIDITY"] = _reasoning(subject, questions, rows["REASONING_VALIDITY"])
    out["SELF_CONTAINMENT"] = _typed(subject, questions, "SELF_CONTAINMENT", typed.self_containment, rows["SELF_CONTAINMENT"])
    out["ANSWER_CORRECTNESS"] = _typed(subject, questions, "ANSWER_CORRECTNESS", typed.answer_correctness, [])
    out["DIMENSIONAL_CORRECTNESS"] = _typed(subject, questions, "DIMENSIONAL_CORRECTNESS", typed.dimensional_correctness, [])
    return out


def _reasoning(subject: Subject, questions: list[dict], rows: list[dict]) -> Verdict:
    """REASONING_VALIDITY from the status of each key: NOT_RUN or DISPUTED fails, the author's word alone is inconclusive, an independent check passes."""
    if not questions:
        return Verdict("NOT_APPLICABLE")
    if rows:
        return Verdict("FAIL", rows)
    status = Counter((q.get("answer") or {}).get("verification_status") for q in questions)
    if status.get("INDEPENDENTLY_CHECKED", 0) == len(questions):
        return Verdict("PASS")
    authored = [q.get("id", "?") for q in questions if (q.get("answer") or {}).get("verification_status") != "INDEPENDENTLY_CHECKED"]
    return Verdict("INCONCLUSIVE", [finding("AUTHOR_ONLY", "S3", subject.id, f"{len(authored)} of {len(questions)} keys are checked by their author or not at all; none by anyone else",
                                           evidence={"examples": authored[:FEW]})])


def _typed(subject: Subject, questions: list[dict], assurance_type: str, check, extra: list[dict]) -> Verdict:
    """Run a typed check over the questions: FAIL if any declared question fails; PASS only if every question was checked and passed."""
    outcomes: dict[str, str] = {}
    rows = list(extra)
    for q in questions:
        outcome, problems = check(q)
        outcomes[q.get("id", "?")] = outcome
        for p in problems:
            if outcome == "FAIL":
                rows.append(finding(p["code"], "S1", q.get("id", "?"), p["message"][:300]))
    tally = Counter(outcomes.values())
    if tally.get("FAIL"):
        return Verdict("FAIL", rows)
    if not questions or tally.get("NOT_APPLICABLE", 0) == len(questions):
        return Verdict("NOT_APPLICABLE", rows)
    unchecked = [qid for qid, o in outcomes.items() if o in ("INCONCLUSIVE",)]
    if unchecked:
        rows.append(finding("NOT_CHECKED", "S3", subject.id, f"{len(unchecked)} of {len(questions)} questions declare no specification to check",
                            evidence={"examples": unchecked[:FEW]}))
        return Verdict("INCONCLUSIVE", rows)
    return Verdict("PASS", rows)


def verify_references(subjects: list[Subject], repo: Path) -> dict[str, Verdict]:
    """REFERENCE_INTEGRITY, one library at a time: the packages of one directory are one universe (Physics and Mathematics share nested ids, and are not one).

    A package refers to its siblings, so a single package is judged against the whole directory it lives in; only the subjects asked about get a verdict."""
    from Shared.library import resolve
    universes: dict[str, list[Subject]] = defaultdict(list)
    for s in subjects:
        universes[Path(s.path).parent.as_posix()].append(s)
    out: dict[str, Verdict] = {}
    for parent, members in universes.items():
        packages, unreadable = [], set()
        for s in members:
            try:
                package = json.loads((repo / s.path).read_text(encoding="utf-8"))
                if not isinstance(package, dict):
                    raise ValueError
                packages.append(package)
            except (OSError, ValueError):
                unreadable.add(s.key)
        asked = {s.path for s in members}
        for sibling in sorted((repo / parent).glob("*.json")):
            if sibling.relative_to(repo).as_posix() in asked:
                continue
            try:
                package = json.loads(sibling.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue                                    # a sibling that does not parse is the verdict of its own subject, not of this one
            if isinstance(package, dict):
                packages.append(package)
        local: dict[str, list[dict]] = {s.id: [] for s in members}
        shared: list[dict] = []
        try:
            records = resolve.build_index(packages)
        except ContractError as exc:
            shared.append(finding(exc.code, "S1", parent, (exc.detail or str(exc))[:300]))
        else:
            for m in resolve.unresolved(records):
                local.setdefault(records[m["record"]]["_package"], []).append(
                    finding("LIBRARY_UNRESOLVED_REFERENCE", "S1", m["record"], f"{m['field']} -> {m['target']}"))
            for clash in resolve.id_collisions(records):         # one finding each, so that a new collision is not hidden behind an old one
                nested, _, rest = clash.partition(" declared in ")
                second = rest.rpartition(" and again in ")[2]
                owner = records.get(second, {}).get("_package")
                local.setdefault(owner, []).append(finding("LIBRARY_NESTED_ID_COLLISION", "S1", nested, clash[:300]))
            try:
                resolve.validate_library(packages)
            except ContractError as exc:
                if exc.code not in ("LIBRARY_UNRESOLVED_REFERENCE", "LIBRARY_NESTED_ID_COLLISION"):
                    shared.append(finding(exc.code, "S1", parent, (exc.detail or str(exc))[:300]))
        for s in members:
            rows = local.get(s.id, []) + shared
            out[s.key] = Verdict("NOT_RUN") if s.key in unreadable else _verdict(rows)
    return out


# -- projections ------------------------------------------------------------------------------------------------------------------------------

def page_findings(subject: Subject, repo: Path) -> dict[str, dict[tuple[str, str], list[dict]]]:
    """The standalone-policy findings of every page under a projection, by assurance type then (rule, page)."""
    from Shared.tools import standalone_conformance as sc
    shell = sc.policy()
    types = rule_types()
    root = repo / subject.path
    pages = sorted(root.rglob("*.html")) if root.is_dir() else [root]
    base = root if root.is_dir() else root.parent
    cache: dict = {}
    staged = (repo / "publication", repo / "public") if root.is_relative_to(repo / "publication") else None   # a product is judged where it will be served
    out: dict[str, dict[tuple[str, str], list[dict]]] = {t: defaultdict(list) for t in PAGE_TYPES}
    for page in pages:
        rel = (page.relative_to(repo) if page.is_relative_to(repo) else page.relative_to(base)).as_posix()
        for f in sc.check_page(page, root=base, shell=shell, _ids=cache, published=staged):
            out[types[f["rule"]]][(f["rule"], rel)].append(f)
    return out


def verify_projection(subject: Subject, repo: Path) -> dict[str, Verdict]:
    grouped = page_findings(subject, repo)
    out = {}
    for t in PAGE_TYPES:
        rows = []
        for (rule, rel), found in sorted(grouped[t].items()):
            severity = SEVERITY_OF[found[0]["severity"]]
            more = f" (+{len(found) - 1} more on this page)" if len(found) > 1 else ""
            rows.append(finding(rule, severity, rel, found[0]["detail"][:240] + more, location=f"{rel}:{found[0]['line']}",
                                evidence={"count": len(found), "lines": [f["line"] for f in found[:FEW]]}))
        out[t] = _verdict(rows)
    return out


def projection_ratchet(subject: Subject, repo: Path) -> list[str]:
    """Pages worse than the ledger allows (Shared/web/standalone-ledger.v1.json), for a projection under a governed root; [] otherwise."""
    from Shared.tools import standalone_conformance as sc
    shell = sc.policy()
    if not any(Path(subject.path).parts[:1] == (g,) for g in shell["standalone_policy"]["governed_roots"]):
        return [f"{subject.path}: no ledger governs this projection, so every blocking finding counts"]
    counts: dict[str, dict[str, int]] = defaultdict(dict)
    for per_type in page_findings(subject, repo).values():
        for (rule, rel), found in per_type.items():
            blocking = [f for f in found if f["severity"] == "BLOCK"]
            if blocking:
                counts[rel][rule] = len(blocking)
    return sc.ratchet(dict(counts), sc.load_ledger())


# -- the run ----------------------------------------------------------------------------------------------------------------------------------

@dataclass
class Run:
    evidence: list[dict] = field(default_factory=list)
    ratchet_problems: list[str] = field(default_factory=list)

    def by_outcome(self) -> Counter:
        return Counter((e["assurance_type"], e["outcome"]) for e in self.evidence)

    def failing(self) -> list[dict]:
        return [e for e in self.evidence if e["outcome"] == "FAIL"]


def emit(evidence_dir: Path, assurance_type: str, subject: Subject, verdict: Verdict, config: dict) -> dict:
    record = make_evidence(assurance_type, subject.kind, subject.id, verdict.outcome, PRODUCER, VERSION, findings=verdict.findings,
                           subject_digest=subject.digest, configuration=config)
    write_evidence(record, evidence_dir / f"{record['evidence_id']}.json")
    return record


def run(repo: Path, packages: list[str], projections: list[str], evidence_dir: Path, clean: bool = True) -> Run:
    """Verify every package and projection and write the evidence. With `clean`, the evidence directory is emptied first, so it holds exactly this run."""
    if clean and evidence_dir.is_dir():
        for old in evidence_dir.glob("*.json"):
            old.unlink()
    result = Run()
    config = configuration()
    package_subjects = aggregate.package_subjects(packages, repo)
    reference_verdicts = verify_references(package_subjects, repo)
    for s in package_subjects:
        verdicts = verify_package(s, repo)
        verdicts["REFERENCE_INTEGRITY"] = reference_verdicts[s.key]
        for t, v in sorted(verdicts.items()):
            result.evidence.append(emit(evidence_dir, t, s, v, config))
    for s in aggregate.projection_subjects(projections, repo):
        for t, v in sorted(verify_projection(s, repo).items()):
            result.evidence.append(emit(evidence_dir, t, s, v, config))
        if any(e["outcome"] == "FAIL" and e["subject"]["kind"] == "PROJECTION" and e["subject"]["id"] == s.id for e in result.evidence):
            result.ratchet_problems += projection_ratchet(s, repo)
    return result
