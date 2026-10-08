"""Does a record say something, or does it merely have the right shape?

Intake refuses a record with an empty inferential jump. It could not refuse one whose
inferential jump reads "Governing relation." -- non-empty, correctly typed, schema
valid, and teaching nothing. A library whose stated purpose is to stop plausible
titles concealing missing reasoning has to be able to tell the difference, and
presence checks cannot.

Three defects are detectable without knowing any subject:

  duplicated   the same sentence appears on two records. One of them is wrong: either
               the text was templated across records, or two records are the same
               record. Authored prose about different things does not collide.

  templated    the same sentence with the record's own title substituted in. This is
               what a generator produces, and it defeats a plain duplicate check,
               so the title is stripped before comparing.

  self-naming  a phrase of three words or fewer that contains its own declared type --
               "Governing relation." under a RELATION, "System invariant." under an
               INVARIANT. Restating what a thing is called is not explaining it.

Duplication is only compared between records of the same collection. A microtopic's
teaching path legitimately restates a step of the relation it teaches, and a check
that called that a defect would be ignored within a week.

These are corpus properties, not properties of one record, so the checks take a whole
package or catalogue. They are also purely textual: nothing here reads a subject, a
grade or a topic, which is what lets the same gate stand in front of every subject.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable, Iterator, Mapping

from Shared.contracts import PROSE_MIN_WORDS, SENTENCE_END, is_prose, normalise as _normalise

# Keys whose values are identifiers, enumerations or provenance boilerplate rather
# than authored teaching. Repetition across records is expected and correct there:
# every datum in a package may honestly share one locator.
STRUCTURAL_KEYS = {
    "id", "version", "status", "schema_version", "package_id", "kind", "atom_type",
    "bucket_id", "unit", "symbol", "value", "intrinsic_badge", "depth_overlay",
    "locator", "citation", "origin", "acceptance", "provider", "tier", "track",
    "board", "academic_year", "mapping_status", "scope_class", "verification_status",
    "learner_action", "exposure_role", "role", "viewport", "validator_id", "domain",
    "family_ref", "primary_capability_ref", "source_ref", "comparison", "shape",
    "unit_or_domain", "dimension", "species_role",
}
# Keys that state shared constraints rather than authored explanation. Two relations
# in the same frame really do have the same validity conditions, and two figures of
# the same kind really do have the same accessibility requirements. Demanding that
# those differ would teach authors to paraphrase for the checker's benefit, which is
# worse than the repetition. Explanatory fields are checked by default, so a field
# added to the schema later is discriminative until someone argues it here.
SHARED_CONSTRAINT_KEYS = {"conditions", "accessibility", "rights_status", "edition"}
TITLE_KEYS = ("title", "name", "learner_title")
SELF_NAMING_MAX_WORDS = 3


def prose_fields(record: object, path: str = "") -> Iterator[tuple[str, str]]:
    """Every authored sentence in a record, with the path it sits at."""
    if isinstance(record, Mapping):
        for key, value in record.items():
            # Quality-audit provenance/receipts are machine evidence, not authored
            # teaching prose. Repeated check ids, auditor ids and receipt notes are
            # expected across independently audited records and must not be treated
            # as templated academic content.
            if path.endswith("quality_audit") and key in {"audit_receipts", "audit_provenance"}:
                continue
            if (key.startswith("_") or key in STRUCTURAL_KEYS
                    or key in SHARED_CONSTRAINT_KEYS or key.endswith(("_ref", "_refs"))):
                continue
            yield from prose_fields(value, f"{path}.{key}" if path else key)
    elif isinstance(record, (list, tuple)):
        for index, value in enumerate(record):
            yield from prose_fields(value, f"{path}[{index}]")
    elif isinstance(record, str) and is_prose(record):
        yield path, record


def _titles(record: Mapping) -> list[str]:
    """Strings a generator would interpolate into an otherwise fixed template."""
    found = [record[key] for key in TITLE_KEYS
             if isinstance(record.get(key), str) and record[key].strip()]
    return sorted(found, key=len, reverse=True)


def _skeleton(record: Mapping, path: str, text: str) -> str:
    """The text with the record's own title removed, which is what a generator varies.

    A title field is left alone: substituting a title into itself would collapse every
    title in the package to one string and report the whole package as templated.
    """
    if path not in TITLE_KEYS:
        for title in _titles(record):
            text = text.replace(title, "<TITLE>")
    return _normalise(text)


def _self_naming(text: str, types: Iterable[str]) -> bool:
    """A phrase short enough to be a label, containing the name of its own type.

    Only the declared type counts. An earlier version also drew vocabulary from the
    field path, which flagged "Report the solution exactly." under `solution_structure`
    -- a real instruction that happens to share a word with the field holding it.
    """
    words = _normalise(text).split()
    if not words or len(words) > SELF_NAMING_MAX_WORDS:
        return False
    vocabulary = {word for value in types for word in _normalise(str(value)).split()}
    return bool(vocabulary & set(words))


def _declared_types(record: Mapping) -> list[str]:
    return [str(record[key]) for key in ("kind", "atom_type", "type") if key in record]


def findings(records: Mapping[str, Mapping]) -> list[dict]:
    """Substance defects across a corpus of records, keyed by record id.

    Each record may carry `_collection`; duplication is compared only within one.
    """
    exact: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    skeletons: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    found: list[dict] = []

    for record_id, record in records.items():
        types = _declared_types(record)
        collection = str(record.get("_collection", ""))
        for path, text in prose_fields(record):
            exact[(collection, _normalise(text))].append((record_id, path))
            skeletons[(collection, _skeleton(record, path, text))].append((record_id, path))
            if _self_naming(text, types):
                found.append({"point": "SELF_NAMING", "record": record_id, "field": path,
                              "detail": f"{text.strip()!r} restates what the field is called; "
                                        "naming a thing is not explaining it"})

    # A finding is raised at every site that carries the shared text, not once per
    # group. Attributing a string shared by thirty-one records to only the first of
    # them reported four defective packets out of forty-three, and let the other
    # twenty-seven through as clean.
    #
    # A question stem is different from authored explanatory prose: official banks may
    # legitimately reuse a generic stem while changing the choices/conditions that make
    # it a different learner item. Treat the whole learner-visible context as the
    # discriminant for repeated stems. If stem + options + conditions + subparts are all
    # the same, the duplicate remains a finding; differing context must not force a
    # verbatim source stem to be rewritten merely to satisfy this heuristic.
    def question_context(record_id):
        record = records.get(record_id, {})
        def values(key):
            raw = record.get(key) or []
            return tuple(_normalise(str(value)) for value in raw) if isinstance(raw, (list, tuple)) else ()
        return values("options"), values("conditions"), values("subparts")

    def shared(index, point, describe):
        for (collection, _), original_sites in index.items():
            groups = [original_sites]
            if collection == "questions" and original_sites and all(path == "stem" for _, path in original_sites):
                by_context = defaultdict(list)
                for record_id, path in original_sites:
                    by_context[question_context(record_id)].append((record_id, path))
                groups = list(by_context.values())

            for sites in groups:
                owners = sorted({record_id for record_id, _ in sites})
                if len(owners) < 2:
                    continue
                listed = ", ".join(owners[:4]) + ("..." if len(owners) > 4 else "")
                for record_id, path in sites:
                    yield {"point": point, "record": record_id, "field": path,
                           "detail": describe(len(owners), listed)}

    found += list(shared(exact, "DUPLICATED",
                         lambda n, listed: f"identical text on {n} records ({listed})"))
    already = {(f["record"], f["field"]) for f in found if f["point"] == "DUPLICATED"}
    found += [f for f in shared(skeletons, "TEMPLATED",
                                lambda n, listed: f"same text on {n} records once each record's "
                                                  f"own title is removed ({listed})")
              if (f["record"], f["field"]) not in already]
    return sorted(found, key=lambda f: (f["record"], f["field"], f["point"]))


# A step that changes the mathematical state must show the changed state. Describing
# the outcome instead -- "A verified solution.", "A numerical statement that is simply
# true or false." -- names the operation without performing it, which is the defect
# PR #361 records as MATH_OPERATION_NAMED_BUT_NOT_DEMONSTRATED.
#
# The distinction needs the step's own role to be sound. Applied to every step it
# misfired on roughly a quarter of authored ones, all of them declarations whose
# output is a convention rather than a computation: "x ranges over the rationals."
# is a correct output for a step whose whole job is to fix the domain.
DEMONSTRATION = re.compile(r"[0-9=+\-*/^<>√×]")


def step_findings(records: Mapping[str, Mapping]) -> list[dict]:
    """Steps that claim to transform the state without showing it change.

    "Showing it" is read as arithmetic, which is sound only where the rung has arithmetic
    to show. The rule was written when every microtopic bound a relation; a rung that
    states a distinction rather than a calculation binds none, and demanding an operator
    of its output demands an equation the rung does not have. Measured when the first
    conceptual rungs arrived: 20 TRANSFORM steps in relation-free microtopics, 16 passing
    only because they happened to carry a digit and 4 failing for prose that showed two
    states perfectly well -- "decrease in U matches increase in K" among them.

    So the check applies where a relation is bound. Where none is, the output is NOT
    checked here and that is a gap rather than a pass: what would make a relation-free
    demonstration testable has not been designed, and pretending otherwise would put a
    heuristic in the place of a rule.
    """
    found = []
    for record_id, record in records.items():
        if not record.get("relation_refs"):
            continue
        for index, step in enumerate(record.get("teaching_path", []) or []):
            if not isinstance(step, Mapping) or step.get("role") != "TRANSFORM":
                continue
            output = str(step.get("output", "")).strip()
            if output and not DEMONSTRATION.search(output):
                found.append({"point": "NAMED_WITHOUT_DEMONSTRATING", "record": record_id,
                              "field": f"teaching_path[{index}].output",
                              "detail": f'{step.get("id")} transforms the state but its output, '
                                        f'{output.strip()!r}, describes an outcome rather than '
                                        "showing it"})
    return found
