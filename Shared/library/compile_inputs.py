"""Compile publication inputs for one bucket from the library.

This is what makes the library executable rather than stored: the baseline, the
source inventory and the plan skeleton are *derived* from library records, so the
numbers, questions and obligations a product publishes have a governed origin
instead of living in a build script beside the lesson.

What is derived and what is not, stated plainly:

  derived   buckets and their prerequisite edges; obligations from microtopics and
            the teaching routes that claim them; source atoms from the data
            collection; source questions with their answers and any declared
            verification; unit structure and per-core coverage; the teaching text
            the library already holds -- teaching-path steps, misconception repairs
            and exit tasks are authored prose and are carried through verbatim.

  not derived  connecting learner prose beyond what the library holds, and any
            product the library has no content for. These are reported as authoring
            requirements rather than invented. Generating teaching prose from graph
            records would produce exactly the plausible titles concealing missing
            reasoning that the library exists to prevent.

Figures sit on the line between the two. A representation record states what a figure
of its kind must show, which is a requirement, not a figure; a scene instance on that
representation states one actual figure bound to the data it draws, which compiles.
So a representation holding instances yields figure blocks, and one holding none is
reported as figure authoring still outstanding -- per representation, rather than as a
blanket warning on every run.

The compiler never fabricates to fill a gap. A bucket that cannot support a product
is reported unsupported, not padded.
"""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from Shared.contracts import digest, join, load, require, sentence
from Shared.library.resolve import build_index, load_packages, slice_for_bucket
from Shared.library.practice_inventory import bucket_questions
from Shared.library import source_custody

# Core1 and Core2 sit outside the teaching-route mechanism. A route says which product
# teaches a microtopic; these two do not teach it. Core1 is the bucket's map -- its
# objects, its governing relations and where the hard work is -- and Core2 is its
# question custody. Both are determined by what the bucket holds, not by a route.
COMPOSABLE = ("CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
ROUTED = ("CORE1A", "CORE1B")
# Of the routed pair, the one whose role is to elicit the decision before revealing it.
# The other reveals a completed construction, which is why its composition is untouched
# by everything below: the A/B comparison is only meaningful while one side holds still.
ELICITING = "CORE1B"
# A block the engine renders closed, and the suffix that pairs it with the prompt it
# answers. Named once here so the pairing cannot be written two ways in two places.
REVEAL_PLACEMENT = "ELICITED_REVEAL"
REVEAL_SUFFIX = "-REVEAL"
# What an obligation is an obligation *of*. A concept is taught by one
# microtopic; a bucket-level slot -- orientation, custody, practice -- is a place
# in the product. Only the first is coverage in the sense the A/B rule means.
CONCEPT, BUCKET = "CONCEPT", "BUCKET"
PRACTICE = ("CORE2A", "CORE2B")
BADGE = {"EASY": "EASY", "MEDIUM": "MEDIUM", "HARD": "HARD"}


def _routes_by_core(records: dict) -> dict[str, set[str]]:
    """Which microtopics each core is claimed to teach, from the library's teaching routes."""
    claimed: dict[str, set[str]] = {core: set() for core in COMPOSABLE}
    for record in records.values():
        if record["_collection"] != "teaching_routes":
            continue
        for core in record.get("cores", []):
            if core in claimed:
                claimed[core].update(record.get("microtopic_refs", []))
    return claimed


def _atoms_for(records: dict, microtopic_ids: set[str]) -> list[dict]:
    """Data records reachable from this bucket's microtopics, via their relations."""
    relations = set()
    for mid in microtopic_ids:
        relations.update(records[mid].get("relation_refs", []))
    chosen = []
    for record in records.values():
        if record["_collection"] != "data":
            continue
        relation = record.get("relation_ref")
        if relation is None or relation in relations:
            chosen.append(record)
    return sorted(chosen, key=lambda r: r["id"])


VOCABULARY = Path(__file__).resolve().parents[2] / "Shared/vocabularies/purpose.json"


def _purpose(control: dict) -> dict:
    """What this run is for, read from the shared vocabulary.

    The enum was validated in the engine, written free-form on a profile, and consulted
    by nothing. One declaration now, read by both.
    """
    declared = {p["id"]: p for p in load(VOCABULARY)["purposes"]}
    require(control.get("purpose") in declared, "PRACTICE_PURPOSE_UNDECLARED",
            str(control.get("purpose")))
    return declared[control["purpose"]]


def _routes_transfer(control: dict) -> bool:
    return bool(_purpose(control).get("routes_transfer"))


def _withheld_reason(control: dict) -> str:
    row = _purpose(control)
    return (f'purpose {row["id"]} does not route transfer: '
            f'{row.get("reason_when_withheld", "declared not to route it")}')


def compile_bucket(records: dict, bucket_id: str, *, topic_id: str, title: str,
                   subject: str, practice_control: dict) -> dict:
    chosen = slice_for_bucket(records, bucket_id)
    microtopics = [records[m] for m in chosen["microtopic_order"]]
    require(microtopics, "LIBRARY_BUCKET_HAS_NO_MICROTOPICS", bucket_id)
    microtopic_ids = {m["id"] for m in microtopics}
    claimed = _routes_by_core(records)
    requirements: list[dict] = []

    # --- source inventory -------------------------------------------------
    atoms, equations = [], {}
    for record in _atoms_for(records, microtopic_ids):
        if record["kind"] == "EQUATION":
            equations[record["relation_ref"]] = record["id"]
            atoms.append({"id": record["id"], "value": record["value"], "kind": "EQUATION",
                          "locator": f'{record["meaning"]} -- {record["locator"]}'})
        else:
            require(record.get("unit"), "LIBRARY_DATUM_WITHOUT_UNIT", record["id"])
            atoms.append({"id": record["id"], "value": record["value"], "unit": record["unit"],
                          "kind": "DATUM", "locator": f'{record["meaning"]} -- {record["locator"]}'})

    # Practice ownership is local to the bucket's taught capabilities. Prerequisite
    # closure is retrieval context, not ownership: a question reached through a prerequisite
    # must not make the downstream bucket practice-ready.
    questions, question_records = [], []
    for record in bucket_questions(records, bucket_id):
        row = {"id": record["id"], "original_number": record["original_identifier"],
               "stem": record["stem"],
               "subparts": deepcopy(record.get("subparts") or []),
               "options": deepcopy(record.get("options") or []),
               "conditions": deepcopy(record.get("conditions") or []),
               # These custody fields let the publication boundary compare the compiled
               # learner block against an unlossy source projection. Legacy frozen
               # source files may omit them; newly compiled library sources do not.
               "source_refs": list(record.get("source_refs") or []),
               "figure_refs": list(record.get("figure_refs") or []),
               "hints": deepcopy(record.get("hints") or [])}
        if record.get("verification"):
            row["verification"] = record["verification"]
            for atom_id in record["verification"]["bindings"].values():
                require(any(a["id"] == atom_id for a in atoms), "QUESTION_BINDS_UNKNOWN_DATUM",
                        f'{record["id"]} -> {atom_id}')
        questions.append(row)
        question_records.append(record)

    # Core2 is source custody, not a synonym for "all questions this bucket can render".
    # A practice question remains available to Core2A/Core2B regardless of origin, but it
    # can enter Core2 only when it is a reviewed/curated source-derived item carrying a
    # resolved Phase-1 custody proof.
    core2_question_records = [
        record for record in question_records
        if record.get("status") in {"REVIEWED", "CURATED"}
        and source_custody.valid_for_core2(record, records)
    ]

    source = {"id": "LIBRARY", "origin": "AUTHOR_CREATED",
              "citation": f"Compiled from the {subject} library for bucket {bucket_id}. "
                          "Records are author-created candidates; no source measurement or "
                          "official question provenance is claimed.",
              "atoms": atoms, "questions": questions}

    # --- which products the library can actually support -------------------
    supported, unsupported = [], {}
    relation_ids = {r for m in microtopics for r in m.get("relation_refs", [])}
    relations = {rid: records[rid] for rid in relation_ids if rid in records}
    for core in COMPOSABLE:
        covered = claimed[core] & microtopic_ids
        if core == "CORE1":
            if relation_ids:
                supported.append(core)
            else:
                unsupported[core] = ("the bucket declares no governing relation, so there is "
                                     "nothing for a map of it to orient a learner to")
        elif core == "CORE2":
            if core2_question_records:
                supported.append(core)
            else:
                unsupported[core] = (
                    "the bucket has no reviewed/curated source-derived question with "
                    "resolved question-level custody; authored practice does not become Core2"
                )
        elif core in PRACTICE:
            exposed = [q for q in question_records
                       if any(e.get("core") == core for e in q.get("exposure", []))]
            if exposed:
                supported.append(core)
            elif core == "CORE2B" and not _routes_transfer(practice_control):
                # Declared by the purpose, not decided here: a purpose may legitimately
                # say "do not build this product". Reported as unsupported with the
                # vocabulary's own reason rather than silently omitted, because a product
                # withheld on purpose and a product nobody could build must not look
                # alike.
                unsupported[core] = _withheld_reason(practice_control)
            else:
                unsupported[core] = "the library holds no question exposed to this product for this bucket"
        elif covered:
            supported.append(core)
        else:
            unsupported[core] = "no teaching route claims this product for this bucket's microtopics"
    require(supported, "LIBRARY_SUPPORTS_NO_PRODUCT", bucket_id)
    for core, reason in unsupported.items():
        requirements.append({"kind": "PRODUCT_UNSUPPORTED", "core": core, "detail": reason})

    # --- baseline ----------------------------------------------------------
    bucket = records[bucket_id]

    # A prerequisite bucket is carried into the baseline as a declared node even though
    # this publication holds no content for it. Dropping the edge would silently erase a
    # real dependency; keeping it says "required, and published elsewhere".
    def bucket_nodes(start: str) -> list[str]:
        ordered, pending = [], [start]
        while pending:
            current = pending.pop()
            if current in ordered:
                continue
            ordered.append(current)
            pending += [p for p in records[current].get("prerequisite_refs", [])
                        if p in records and records[p]["_collection"] == "buckets"]
        return ordered

    node_ids = bucket_nodes(bucket_id)
    bucket_prerequisites = [p for p in bucket.get("prerequisite_refs", [])
                            if p in records and records[p]["_collection"] == "buckets"]
    obligations = []
    for microtopic in microtopics:
        cores = sorted(core for core in supported
                       if microtopic["id"] in claimed[core] or core in ("CORE2A", "CORE2B"))
        relation_atoms = [a["id"] for a in atoms
                          if records[a["id"]].get("relation_ref") in microtopic.get("relation_refs", [])
                          or records[a["id"]].get("relation_ref") is None]
        if not cores or not relation_atoms:
            requirements.append({"kind": "MICROTOPIC_UNBOUND", "microtopic": microtopic["id"],
                                 "detail": "no supported product or no data bound to its relations"})
            continue
        study = [c for c in cores if c in ROUTED]
        if study:
            obligations.append({"id": f'OB-{microtopic["id"]}', "bucket_id": bucket_id,
                                "scope": CONCEPT, "source_atom_ids": sorted(set(relation_atoms)),
                                "required_cores": study, "required_kinds": ["TEXT"]})
    # Conventions are bucket-scoped and every teaching product needs them before it uses
    # what they declare -- the role specs say "declared before any of it is used". They
    # were authored and then dropped: the first buckets to carry conventions flipped six
    # delivery rows from UNAUTHORED to NOT_DELIVERED, which is the compiler failing to
    # carry a field rather than an author failing to write one.
    conventions_obligation = f"OB-{bucket_id}-CONVENTIONS"
    convention_cores = [c for c in supported if c == "CORE1" or c in ROUTED]
    if bucket.get("conventions") and convention_cores:
        obligations.append({"id": conventions_obligation, "bucket_id": bucket_id,
                            "scope": BUCKET, "source_atom_ids": sorted({a["id"] for a in atoms}),
                            "required_cores": convention_cores, "required_kinds": ["TEXT"]})
    orientation_obligation = f"OB-{bucket_id}-ORIENTATION"
    if "CORE1" in supported:
        obligations.append({"id": orientation_obligation, "bucket_id": bucket_id, "scope": BUCKET,
                            "source_atom_ids": sorted({a["id"] for a in atoms}),
                            "required_cores": ["CORE1"], "required_kinds": ["EQUATION", "TEXT"]})
    custody_obligation = f"OB-{bucket_id}-CUSTODY"
    if "CORE2" in supported:
        obligations.append({"id": custody_obligation, "bucket_id": bucket_id, "scope": BUCKET,
                            "source_atom_ids": sorted({a["id"] for a in atoms}),
                            "required_cores": ["CORE2"], "required_kinds": ["QUESTION"]})
    practice = [c for c in supported if c in PRACTICE]
    practice_obligation = f"OB-{bucket_id}-PRACTICE"
    if practice and questions:
        obligations.append({"id": practice_obligation, "bucket_id": bucket_id, "scope": BUCKET,
                            "source_atom_ids": sorted({a["id"] for a in atoms}),
                            "required_cores": practice, "required_kinds": ["QUESTION"]})
    require(obligations, "LIBRARY_PRODUCED_NO_OBLIGATIONS", bucket_id)

    accounted = {a for o in obligations for a in o["source_atom_ids"]}
    unaccounted = {a["id"] for a in atoms} - accounted
    atoms[:] = [a for a in atoms if a["id"] in accounted]
    source["atoms"] = atoms
    for atom_id in sorted(unaccounted):
        requirements.append({"kind": "DATUM_UNUSED", "datum": atom_id,
                             "detail": "no obligation binds this value; it was omitted rather than forced in"})

    baseline = {"schema_version": "1.0.0", "topic_id": topic_id,
                "baseline_id": f"BASE-{bucket_id}",
                "selected_cores": supported,
                "sources": [{"id": "LIBRARY", "path": "sources/source.json", "sha256": ""}],
                "buckets": [{"id": node, "badge": BADGE[records[node]["intrinsic_badge"]],
                             "prerequisites": [p for p in records[node].get("prerequisite_refs", [])
                                               if p in node_ids]}
                            for node in node_ids],
                "obligations": obligations,
                "required_questions": [{"core": core, "source_id": "LIBRARY", "question_id": q["id"]}
                                       for core in practice for q in questions
                                       if any(e.get("core") == core for e in
                                              next(r for r in question_records if r["id"] == q["id"])
                                              .get("exposure", []))]}

    # --- figures the library actually holds, and those it only requires -----
    representations = sorted(chosen["records"].get("representations", []), key=lambda r: r["id"])
    for representation in representations:
        instances = representation.get("scene_instances", [])
        if not instances:
            requirements.append({"kind": "FIGURE_AUTHORING", "representation": representation["id"],
                                 "detail": "the representation states what a figure of this kind must show "
                                           "but holds no scene instance; a figure must be authored"})
            continue
        for instance in instances:
            for core in sorted(set(instance["cores"]) - set(supported)):
                requirements.append({"kind": "FIGURE_PRODUCT_UNSUPPORTED", "core": core,
                                     "representation": representation["id"],
                                     "detail": f'scene instance {instance["id"]} targets a product this '
                                               "bucket does not support; it was not drawn"})

    # --- plan skeleton, carrying the prose the library actually holds -------
    plan = {"schema_version": "1.0.0", "subject": subject, "topic_id": topic_id, "title": title,
            "baseline_digest": "", "practice_control": practice_control, "products": []}
    for core in supported:
        blocks, unit_id = [], f"U-{core}-{bucket_id}"
        # Where a figure goes when the microtopic it names does not claim this product:
        # with the questions in a practice product, with the map in the compact notes.
        figures = _figure_blocks(core, representations, obligations, atoms,
                                 orientation_obligation if core == "CORE1" else practice_obligation)
        conventions = _conventions_blocks(core, bucket, conventions_obligation,
                                          sorted({a["id"] for a in atoms}))
        if core == "CORE1":
            blocks = conventions + _orientation_blocks(
                records, relation_ids, atoms, microtopics, orientation_obligation,
                equations, bucket)
        elif core == "CORE2":
            # Only questions that prove source custody may appear here. Authored practice
            # stays in Core2A/Core2B and may share a family with source-demand evidence,
            # but that relationship never rewrites provenance.
            blocks = [_question_block(core, record, custody_obligation, atoms)
                      for record in core2_question_records]
        elif core in ROUTED:
            blocks = list(conventions)
            for microtopic in microtopics:
                obligation = f'OB-{microtopic["id"]}'
                if not any(o["id"] == obligation and core in o["required_cores"] for o in obligations):
                    continue
                bound = next(o["source_atom_ids"] for o in obligations if o["id"] == obligation)
                if core == ELICITING and microtopic.get("elicitation"):
                    blocks += _elicitation_blocks(microtopic, core, obligation, bound)
                else:
                    blocks.append({"id": f'{core}-{microtopic["id"]}-T', "kind": "TEXT",
                                   "obligation_ids": [obligation], "source_atom_ids": bound,
                                   "text": _teaching_text(microtopic, core, relations)})
                    if core == ELICITING:
                        # Compiling the declarative text here is what made this product
                        # read as the declarative one. It stays only while a microtopic
                        # has no elicitation, and it is recorded as work owed rather
                        # than passed off as the product the role asks for.
                        requirements.append(
                            {"kind": "ELICITATION_AUTHORING", "core": core,
                             "detail": f'{microtopic["id"]} has no elicitation, so this product '
                                       "falls back to the declarative construction for it"})
                # A figure belongs with the microtopic it was bound to. Appending every
                # figure after every text block put the one that explains a transition
                # after the whole argument had been read in prose.
                blocks += [b for b in figures if b["obligation_ids"] == [obligation]]
            # Completed worked examples, which Core1A's required content names and which
            # reached no page: the mechanism already existed -- a question whose exposure
            # names this product -- and nothing emitted it. A worked example is a
            # question with its reasoning fully visible, not a second kind of record.
            for record in question_records:
                if not any(e.get("core") == core for e in record.get("exposure", [])):
                    continue
                blocks.append(_question_block(core, record, practice_obligation, atoms))
            requirements.append({"kind": "PROSE_AUTHORING", "core": core,
                                 "detail": "blocks carry library-held teaching text; connecting narrative "
                                           "still requires authoring"})
        else:
            for record in question_records:
                if not any(e.get("core") == core for e in record.get("exposure", [])):
                    continue
                blocks.append(_question_block(core, record, practice_obligation, atoms))
        # Whatever was not placed beside a microtopic -- figures carried by the practice
        # obligation -- belongs with the questions, which is where they already sat.
        blocks += [b for b in figures if b not in blocks]
        if blocks:
            plan["products"].append({"core": core, "units": [
                {"id": unit_id, "bucket_id": bucket_id, "title": bucket["title"], "blocks": blocks}]})

    plan["products"] = [p for p in plan["products"] if p["units"][0]["blocks"]]
    plan["products"].sort(key=lambda p: COMPOSABLE.index(p["core"]))
    baseline["selected_cores"] = [p["core"] for p in plan["products"]]

    # "Supported" in this compiler means renderable from the current canonical slice.
    # It is deliberately not a statement that source demand is evidenced, familiar
    # reasoning is mature, transfer is protected, or learner release is authorised.
    product_support = {
        core: {
            "renderable": core in baseline["selected_cores"],
            "renderability_reason": (
                "canonical content compiled into at least one learner block"
                if core in baseline["selected_cores"]
                else unsupported.get(core, "no renderable block")
            ),
            "progression_readiness": "NOT_EVALUATED_BY_COMPILER",
        }
        for core in COMPOSABLE
    }

    return {"baseline": baseline, "source": source, "plan": plan,
            "product_support": product_support,
            # Every library record this compilation actually read, so a later audit never
            # has to infer it from the plan's text.
            "library_records": sorted({row["id"] for rows in chosen["records"].values()
                                       for row in rows if isinstance(row, dict)
                                       and row.get("id")}),
            "authoring_requirements": requirements,
            "derived_from": {"bucket": bucket_id, "microtopics": [m["id"] for m in microtopics],
                             "packages": sorted({records[m]["_package"] for m in microtopic_ids})}}


def _elicitation_blocks(microtopic: dict, core: str, obligation: str,
                        atoms: list[str]) -> list[dict]:
    """The self-tutor cycle as blocks, in the order the role specifies.

    Every reveal names the prompt it answers and is emitted after it, so a reader meets
    the question before the answer exists on the page at all. The engine renders an
    ELICITED_REVEAL closed; the ordering here is what makes that honest rather than
    cosmetic, because a reveal that preceded its prompt would still be closed and would
    still be wrong.

    Diagnose and repair come from misconceptions[], which already holds them for the
    declarative product. They are placed inside the reveal because a learner who has not
    yet committed to an answer has nothing to diagnose.
    """
    elicitation = microtopic["elicitation"]
    base = {"kind": "TEXT", "obligation_ids": [obligation], "source_atom_ids": atoms}
    stem = f'{core}-{microtopic["id"]}'
    predict, attempt = elicitation["predict"], elicitation["attempt"]
    reconstruct, boundary = elicitation["reconstruct"], elicitation["boundary_test"]

    ask = [sentence(microtopic["title"]), "", sentence(predict["prompt"]), "",
           *join("Then produce", attempt["produces"])]

    reveal = [f'Our answer: {sentence(predict["defensible_answer"])}', "",
              "Getting there:"]
    reveal += [f'  {position}. {sentence(step["ask"])}'
               for position, step in enumerate(reconstruct["route"], 1)]
    for item in microtopic.get("misconceptions", []):
        # All three parts, in the role's order. The diagnostic prompt is the question
        # that separates the wrong idea from the right one, and dropping it leaves a
        # wrong idea named and untested, which is a warning rather than a diagnosis.
        reveal += ["", *join("A common wrong idea", item["wrong_idea"]),
                   *join("Tell them apart", item["diagnostic_prompt"]),
                   *join("Instead", item["repair"])]
    reveal += ["", *_closure_lines(attempt)]

    def revealing(prompt: dict, lines: list[str]) -> list[dict]:
        """A prompt and the reveal that answers it, in that order and never apart.

        The reveal's id is the prompt's id plus a suffix, so the pair cannot be built
        with the wrong reveals_block_id and a reveal cannot be emitted without the block
        it names existing beside it.
        """
        return [prompt, {**base, "id": prompt["id"] + REVEAL_SUFFIX, "placement": REVEAL_PLACEMENT,
                         "reveals_block_id": prompt["id"], "text": "\n".join(lines)}]

    return [
        *revealing({**base, "id": f"{stem}-ASK", "text": "\n".join(ask)}, reveal),
        *revealing({**base, "id": f"{stem}-BOUNDARY", "text": sentence(boundary["prompt"])},
                   [sentence(boundary["answer"]), "",
                    *join("What this settles", boundary["confirms"])]),
    ]


def _closure_lines(attempt: dict) -> list[str]:
    """How the attempt closes, in whichever of the three forms it declared.

    The role admits no fourth form and no silence, so there is no else branch: a closure
    value with nothing behind it is refused at intake rather than rendered as a heading
    with no content under it.
    """
    if attempt["closure"] == "MODEL_RESPONSE":
        return join("A full answer reads", attempt["model_response"])
    lines = ["Judge your answer against these:"]
    for row in attempt["rubric"]:
        # Through join(), not an f-string: evidence_of is an authored field and arrives
        # as a fragment in some records and a sentence in others, which is the whole
        # reason join() exists.
        lines.append(f'  - {sentence(row["criterion"])}')
        lines += [f"    {line}" for line in join("It shows", row["evidence_of"])]
    for label, key in (("Accepted", "accepted"), ("Not accepted", "rejected")):
        for value in attempt.get(key, []):
            lines += ["", *join(label, value)]
    return lines


def _teaching_text(microtopic: dict, core: str, relations: dict | None = None) -> str:
    """Carry the library's own authored prose; do not synthesise teaching."""
    relations = relations or {}
    lines = [sentence(microtopic["title"]), "", microtopic["inferential_jump"]]

    # What the learner is assumed to be able to do already. Core1A's required content
    # names it first, and the product carried it nowhere: a learner who cannot do this
    # was reading the wrong page and had no way to find out.
    assumed = microtopic.get("entry_assumptions") or []
    if assumed:
        # "Before this you should be able to: Can evaluate..." -- the lead-in has to fit
        # how the field is actually authored, and entry_assumptions[] are written as
        # statements of a capability rather than as verb phrases.
        lines += ["", "What this assumes you can already do:"]
        lines += [f"- {sentence(item)}" for item in assumed]

    for item in microtopic.get("misconceptions", []):
        # Both products carry the wrong path; they frame it differently, which is the
        # whole A/B distinction. Core1A reveals it as part of a completed construction,
        # Core1B poses it as a prediction before anything is revealed.
        #
        # It was emitted for CORE1B only -- and once Core1B compiled from elicitation
        # instead, that branch survived solely as the fallback, so the misconception
        # reached neither product. Core1A's own spec says what that costs: "A
        # misconception the learner never hears is a misconception they keep."
        lines.append("")
        if core == ELICITING:
            lines.append(f'Predict first: {sentence(item["diagnostic_prompt"])}')
            lines += join("A common wrong idea", item["wrong_idea"])
        else:
            lines += join("A common wrong idea", item["wrong_idea"])
            lines += join("Tell them apart", item["diagnostic_prompt"])
        lines += join("Instead", item["repair"])

    for step in microtopic.get("teaching_path", []):
        stated = f'{sentence(step["action"])} {sentence(step["why_valid"])}'
        lines += join(f"{stated} This gives", step["output"]) if step.get("output") else [stated]
    exit_task = microtopic.get("exit_task") or {}
    if exit_task.get("prompt"):
        answer = exit_task.get("answer", {})
        lines += ["", f'Check yourself: {exit_task["prompt"]}', f'Answer: {answer.get("summary", "")}']
        lines += [f'- {step}' for step in answer.get("reasoning", [])]
        if answer.get("check"):
            lines.append(f'Verify: {answer["check"]}')

    # Checks the learner can run alone, which the relations already declare and which no
    # product carried. Drawn from the bound relations rather than restated per
    # microtopic, so a check cannot say something the mathematics does not.
    checks = [check for ref in microtopic.get("relation_refs", [])
              for check in (relations.get(ref) or {}).get("checks", [])]
    if checks:
        lines += ["", "Checks you can run on your own answer:"]
        lines += [f"- {sentence(check)}" for check in dict.fromkeys(checks)]
    return "\n".join(lines)


def _orientation_blocks(records: dict, relation_ids: set[str], atoms: list[dict],
                        microtopics: list[dict], obligation: str,
                        equations: dict[str, str], bucket: dict) -> list[dict]:
    """Core1: what the objects are, what the relations say, and where the work is.

    Every part is carried from a record that already holds it. The relation text comes
    from the relation, which is itself a bound copy of the gate that owns it, so a map
    of the bucket cannot state the mathematics differently from the engineering.
    """
    bound = sorted({a["id"] for a in atoms})
    blocks = []
    quantities = [a for a in atoms if a["kind"] == "DATUM"]
    if quantities:
        lines = ["The quantities this bucket works with."]
        lines += [f'{records[a["id"]]["symbol"]}: {records[a["id"]]["meaning"]} '
                  f'({records[a["id"]]["value"]} {records[a["id"]]["unit"]})'
                  for a in quantities if records[a["id"]].get("symbol")]
        blocks.append({"id": "CORE1-QUANTITIES", "kind": "TEXT", "obligation_ids": [obligation],
                       "source_atom_ids": bound, "text": "\n".join(lines)})
    for relation_id in sorted(relation_ids):
        relation = records[relation_id]
        equation_atom = equations.get(relation_id)
        if not relation.get("mathml") or equation_atom is None:
            continue
        blocks.append({"id": f"CORE1-{relation_id}", "kind": "EQUATION",
                       "obligation_ids": [obligation], "source_atom_ids": [equation_atom],
                       "mathml": relation["mathml"], "meaning": relation["meaning"],
                       "symbols": [f'{s["symbol"]}: {s["meaning"]}'
                                   for s in relation.get("symbols", [])],
                       "conditions": list(relation.get("conditions", []))})
    primary = bucket.get("primary_representation_ref")
    if primary and primary in records:
        # One figure, declared by the bucket. Core1 is the map, and a map with no picture
        # was the product asking a learner to hold the bucket's geometry in their head
        # before any of it had been taught.
        record = records[primary]
        for instance in record.get("scene_instances", []):
            if "CORE1" not in instance.get("cores", []):
                continue
            blocks.append({"id": f'CORE1-{instance["id"]}', "kind": "FIGURE",
                           "obligation_ids": [obligation],
                           "source_atom_ids": sorted(instance["datum_refs"]),
                           "correspondence": deepcopy(record.get("correspondence") or []),
                           "scene": deepcopy(instance["scene"])})
            break
    hard = [m for m in microtopics if m.get("intrinsic_badge") in ("MEDIUM", "HARD")]
    if hard:
        lines = ["Where the hard work is."]
        lines += [f'{sentence(m["title"])} ({m["intrinsic_badge"]}) {m["badge_reason"]}'
                  for m in hard]
        blocks.append({"id": "CORE1-DEMAND", "kind": "TEXT", "obligation_ids": [obligation],
                       "source_atom_ids": bound, "text": "\n".join(lines)})
    return blocks


def _conventions_blocks(core: str, bucket: dict, obligation: str,
                        bound: list[str]) -> list[dict]:
    """The bucket's conventions, and for the map its scope. Empty when unauthored.

    A bucket that declares none emits nothing, and the delivery gate reports the row
    UNAUTHORED rather than NOT_DELIVERED -- the difference between nobody having written
    it and the compiler having dropped what somebody wrote.
    """
    conventions = bucket.get("conventions") or []
    blocks = []
    if conventions:
        lines = ["Read these before anything that uses them."]
        lines += [sentence(row["statement"]) for row in conventions if row.get("statement")]
        blocks.append({"id": f"{core}-CONVENTIONS", "kind": "TEXT",
                       "obligation_ids": [obligation], "source_atom_ids": bound,
                       "text": "\n".join(lines)})
    scope = bucket.get("scope") or {}
    if core == "CORE1" and (scope.get("covers") or scope.get("excluded")):
        lines = []
        if scope.get("covers"):
            lines.append(sentence(f'This bucket covers {scope["covers"]}'))
        for excluded in scope.get("excluded") or []:
            lines.append(sentence(f"Deliberately excluded: {excluded}"))
        blocks.append({"id": f"{core}-SCOPE", "kind": "TEXT",
                       "obligation_ids": [obligation], "source_atom_ids": bound,
                       "text": "\n".join(lines)})
    return blocks


def _figure_blocks(core: str, representations: list[dict], obligations: list[dict],
                   atoms: list[dict], fallback: str) -> list[dict]:
    """Compile the scene instances the library holds for this product.

    A figure is bound to the obligation of the microtopic it carries, so it counts as
    coverage of that teaching rather than as decoration; in a practice product, where
    the obligation is the bucket's practice one, it is bound there instead. A scene
    instance naming a microtopic that produced no obligation, or data this bucket does
    not carry, is an error in the library and fails here rather than being dropped.
    """
    by_id = {o["id"]: o for o in obligations}
    known = {a["id"] for a in atoms}
    blocks = []
    for representation in representations:
        for instance in representation.get("scene_instances", []):
            if core not in instance["cores"]:
                continue
            wanted = f'OB-{instance["microtopic_ref"]}'
            if wanted not in by_id:
                # The instance belongs to a microtopic this bucket does not teach, so it
                # belongs to another bucket's slice. Falling back to the practice
                # obligation here put a figure about one bucket's mathematics into
                # another bucket's practice section, and the A/B check found it as a
                # coverage asymmetry two products later -- a figure the declarative
                # product carried and the eliciting one did not.
                continue
            obligation = wanted if core in by_id[wanted]["required_cores"] else fallback
            require(obligation in by_id, "FIGURE_OBLIGATION_MISSING",
                    f'{instance["id"]} -> {wanted}')
            missing = [d for d in instance["datum_refs"] if d not in known]
            require(not missing, "FIGURE_BINDS_UNKNOWN_DATUM",
                    f'{instance["id"]} -> {", ".join(missing)}')
            require(set(instance["datum_refs"]) & set(by_id[obligation]["source_atom_ids"]),
                    "FIGURE_DATA_OUTSIDE_OBLIGATION", f'{instance["id"]} -> {obligation}')
            blocks.append({"id": f'{core}-{instance["id"]}', "kind": "FIGURE",
                           "obligation_ids": [obligation],
                           "source_atom_ids": sorted(instance["datum_refs"]),
                           # What in the picture is which symbol, and the same thing in
                           # words. Held on the representation since R1 and rendered
                           # nowhere, which made the figure the decoration the role
                           # specifications name -- correctly drawn, bound to nothing a
                           # learner could follow back into the mathematics.
                           "correspondence": deepcopy(representation.get("correspondence") or []),
                           # One instance can appear in several products. Each block owns
                           # its own copy, so a caller editing one plan block cannot reach
                           # into another product or back into the library record.
                           "scene": deepcopy(instance["scene"])})
    return blocks


def _question_block(core: str, record: dict, obligation_id: str, atoms: list[dict]) -> dict:
    answer = record["answer"]
    # Core2 holds every question in its original form, so it has no exposure entry: it
    # is custody of the source, not a decision about how a question is used in teaching.
    exposure = next((e for e in record.get("exposure", []) if e.get("core") == core), None)
    role = ("SOURCE_CUSTODY" if exposure is None else
            {"PLANNED_WORKED_ANCHOR": "WORKED_EXAMPLE"}.get(
                exposure.get("role"), exposure.get("role")))
    block = {"id": f'{core}-{record["id"]}', "kind": "QUESTION",
             "obligation_ids": [obligation_id],
             "source_atom_ids": sorted({a["id"] for a in atoms}),
             # source_id is the engine's key into the source inventory, not the
             # question's provenance. R1.5 read the constant "LIBRARY" here as the
             # compiler discarding source identity; it is not, and overwriting it broke
             # the inventory lookup. The identity Core2 requires preserved travels
             # beside it instead, as its own field.
             "source_id": "LIBRARY", "source_question_id": record["id"],
             "source_refs": list(record.get("source_refs") or []),
             "origin": record.get("origin"),
             "original_number": record["original_identifier"], "stem": record["stem"],
             "subparts": deepcopy(record.get("subparts") or []),
             "options": deepcopy(record.get("options") or []),
             "conditions": deepcopy(record.get("conditions") or []),
             "figure_refs": list(record.get("figure_refs") or []),
             "answer": {"summary": answer["summary"], "steps": answer["reasoning"],
                        "check": answer["check"],
                        "subparts": deepcopy(answer.get("subpart_answers") or []),
                        **({"reasoning_route": deepcopy(answer["reasoning_route"])}
                           if answer.get("reasoning_route") else {}),
                        **({"crux_move_ref": answer["crux_move_ref"]}
                           if answer.get("crux_move_ref") else {}),
                        **({"difficult_move": answer["difficult_move"]}
                           if answer.get("difficult_move") is not None else {}),
                        **({"numeric": answer["numeric"]} if answer.get("numeric") else {}),
                        **({"rubric": deepcopy(answer["rubric"])}
                           if answer.get("rubric") else {})},
             "hints": [deepcopy(hint) for hint in record.get("hints") or []],
             **({"scaffolds": deepcopy(record["scaffolds"])}
                if record.get("scaffolds") else {}),
             # Core2B's changed-demand claim, exposure lineage and repair route are
             # authored assessment content. Dropping them turns a transfer task into
             # ordinary practice even though the library still appears complete.
             **({"transfer": deepcopy(record["transfer"])}
                if record.get("transfer") else {}),
             **({"repair_ref": record["repair_ref"]}
                if record.get("repair_ref") else {}),
             "family": record["family_ref"],
             "learner_action": "solve", "exposure_role": role}
    return block


def write(compiled: dict, out: Path) -> dict:
    """Write inputs, sealing the source digest and baseline digest the host will check."""
    source_path = out / "sources/source.json"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(json.dumps(compiled["source"], indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    import hashlib
    compiled["baseline"]["sources"][0]["sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
    (out / "baseline.json").write_text(
        json.dumps(compiled["baseline"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    compiled["plan"]["baseline_digest"] = digest(compiled["baseline"])
    (out / "plan.json").write_text(
        json.dumps(compiled["plan"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "authoring_requirements.json").write_text(
        json.dumps(compiled["authoring_requirements"], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    # What this plan was compiled from, stated by the compiler rather than guessed from
    # the plan's text afterwards. A downstream audit was scanning for record ids as
    # substrings: it counted CAP-RIGHT-TRIANGLE wherever CAP-RIGHT-TRIANGLE-BRIDGE
    # appeared, and tightening the match to a whole token then missed MIC-MEASURED-FROM
    # inside the block id CORE1A-MIC-MEASURED-FROM-T. Both readings are wrong and neither
    # can be fixed by a better pattern, because only the compiler knows what it read.
    (out / "library_records.json").write_text(
        json.dumps(sorted(compiled["library_records"]), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    return {"out": str(out), "selected_cores": compiled["baseline"]["selected_cores"],
            "library_records": len(compiled["library_records"]),
            "atoms": len(compiled["source"]["atoms"]),
            "questions": len(compiled["source"]["questions"]),
            "obligations": len(compiled["baseline"]["obligations"]),
            "authoring_requirements": len(compiled["authoring_requirements"])}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Compile publication inputs for one bucket from the library")
    parser.add_argument("packages", nargs="+", type=Path)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--topic-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records = build_index(load_packages(args.packages))
    compiled = compile_bucket(records, args.bucket, topic_id=args.topic_id, title=args.title,
                              subject=args.subject,
                              practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"})
    print(json.dumps(write(compiled, args.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
