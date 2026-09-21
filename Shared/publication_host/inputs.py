"""Bind authored objects to a separate baseline and exact frozen source files."""

from pathlib import Path

from Shared.contracts import digest, load, require, strings, text, unique, validate_dag, verify_file

KINDS = {"TEXT", "EQUATION", "QUESTION", "FIGURE"}
# Where a block sits in the product a learner reads. TEACHING is read straight through;
# ANSWER is collected into the answer section and names the question it answers;
# ELICITED_REVEAL is rendered closed beside the prompt it answers, for a product whose
# role is to ask before it tells. Enumerated so that a typo is a refusal rather than a
# block silently treated as TEACHING, which is how a reveal would have been published
# open.
PLACEMENTS = {"TEACHING", "ANSWER", "ELICITED_REVEAL"}
# How far a hint goes. Declared rather than inferred, so a hint that hands over
# the answer before the last rung is refusable rather than arguable.
REVEALS = {"CONCEPT", "METHOD", "ANSWER"}
# Read from the shared vocabulary, not copied. The inline set was the second place this
# enum lived, and a fifth value added to one would not have reached the other.
PURPOSES = {p["id"] for p in
            load(Path(__file__).resolve().parents[2] / "Shared/vocabularies/purpose.json")["purposes"]}


def read_inputs(plan: dict, baseline: dict, source_root: Path, adapter) -> dict:
    require(plan.get("schema_version") == baseline.get("schema_version") == "1.0.0",
            "PUBLICATION_SCHEMA_UNSUPPORTED")
    require(plan.get("subject") == adapter.subject, "WRONG_SUBJECT_KIT")
    compiled = adapter.compiled_products
    require(bool(compiled), "SUBJECT_CONTRACT_COMPILES_NO_PRODUCT")
    require(plan.get("baseline_digest") == digest(baseline), "STALE_BASELINE")
    require(plan.get("topic_id") == baseline.get("topic_id"), "TOPIC_BINDING_MISMATCH")
    text(plan.get("title"), "TOPIC_TITLE_REQUIRED")
    sources, atoms, questions = _read_sources(baseline, source_root)
    buckets = unique(baseline["buckets"], "id", "BUCKET_ID_INVALID")
    require(bool(buckets), "BUCKETS_REQUIRED")
    validate_dag(baseline["buckets"], "id", "prerequisites")
    for bucket in buckets.values():
        require(bucket.get("badge") in {"EASY", "MEDIUM", "HARD"}, "INTRINSIC_BADGE_REQUIRED")
    obligations = unique(baseline["obligations"], "id", "OBLIGATION_ID_INVALID")
    require(bool(obligations), "OBLIGATIONS_REQUIRED")
    for row in obligations.values():
        require(row["bucket_id"] in buckets, "OBLIGATION_BUCKET_UNKNOWN")
        require(set(strings(row["source_atom_ids"], "OBLIGATION_ATOMS_REQUIRED")) <= atoms.keys(),
                "OBLIGATION_SOURCE_UNKNOWN")
        require(set(strings(row["required_cores"], "OBLIGATION_CORES_REQUIRED")) <= compiled,
                "CORE_UNSUPPORTED")
        require(set(strings(row["required_kinds"], "OBLIGATION_KINDS_REQUIRED")) <= KINDS,
                "CONTENT_KIND_UNSUPPORTED")
    require(set(atoms) == {a for r in obligations.values() for a in r["source_atom_ids"]},
            "SOURCE_ATOM_UNACCOUNTED")
    context = dict(plan=plan, baseline=baseline, sources=sources, atoms=atoms,
                   questions=questions, buckets=buckets, obligations=obligations, adapter=adapter)
    _validate_products(context)
    return context


def _read_sources(baseline, root):
    sources, atoms, questions = {}, {}, {}
    for ref in baseline["sources"]:
        require(ref["id"] not in sources, "SOURCE_ID_COLLISION")
        path = verify_file(root, ref)
        source = load(path)
        require(source.get("id") == ref["id"], "SOURCE_ID_MISMATCH")
        require(source.get("origin") in {"ORIGINAL", "ADAPTED", "AUTHOR_CREATED"},
                "SOURCE_ORIGIN_REQUIRED")
        text(source.get("citation"), "SOURCE_CITATION_REQUIRED")
        sources[ref["id"]] = {**source, "ref": ref}
        for atom in source["atoms"]:
            require(atom["id"] not in atoms, "ATOM_ID_COLLISION")
            text(atom.get("locator"), "ATOM_LOCATOR_REQUIRED")
            require("value" in atom, "ATOM_VALUE_REQUIRED")
            atoms[atom["id"]] = {**atom, "source_id": ref["id"]}
        for q in source.get("questions", []):
            require(set(q) <= {"id", "original_number", "stem", "subparts", "options", "conditions", "verification"},
                    "SOURCE_QUESTION_FIELDS_UNSUPPORTED", q.get("id", ""))
            key = (ref["id"], q["id"])
            require(key not in questions, "SOURCE_QUESTION_COLLISION")
            text(q.get("original_number"), "ORIGINAL_NUMBER_REQUIRED")
            text(q.get("stem"), "SOURCE_STEM_REQUIRED")
            for field in ("subparts", "options", "conditions"):
                require(isinstance(q.get(field, []), list), "SOURCE_QUESTION_LIST_INVALID")
                for value in q.get(field, []):
                    text(value, "SOURCE_QUESTION_FIELD_EMPTY")
            questions[key] = q
    require(bool(sources) and bool(atoms), "SOURCE_INVENTORY_EMPTY")
    return sources, atoms, questions


def _validate_products(ctx):
    products = unique(ctx["plan"]["products"], "core", "PRODUCT_CORE_COLLISION")
    require(bool(products) and set(products) <= ctx["adapter"].compiled_products,
            "CORE_UNSUPPORTED")
    require(set(products) == set(strings(ctx["baseline"].get("selected_cores"), "BASELINE_CORES_REQUIRED")),
            "REQUESTED_CORE_MISSING_OR_ADDED")
    ctx["learner_fit"] = _learner_fit(ctx["plan"], products)
    ctx["objects"], ctx["coverage"], actual_questions = {}, [], set()
    for core, product in products.items():
        require(bool(product["units"]), "PRODUCT_EMPTY", core)
        unique(product["units"], "id", "UNIT_ID_COLLISION")
        for unit in product["units"]:
            _unit(ctx, core, unit)
            for block in unit["blocks"]:
                if block["kind"] == "QUESTION":
                    actual_questions.add((core, block["source_id"], block["source_question_id"]))
    expected = {(r["core"], r["source_id"], r["question_id"])
                for r in ctx["baseline"]["required_questions"] if r["core"] in products}
    require(expected <= actual_questions, "REQUIRED_QUESTION_MISSING")
    for row in ctx["obligations"].values():
        for core in set(row["required_cores"]) & set(products):
            realized = [r for r in ctx["coverage"] if r["core"] == core and r["obligation_id"] == row["id"]]
            require(set(row["required_kinds"]) <= {r["kind"] for r in realized},
                    "OBLIGATION_CONTENT_MISSING", core + ":" + row["id"])
            referenced_atoms = {a for r in realized for a in ctx["objects"][r["object_id"]]["content"]["source_atom_ids"]}
            require(set(row["source_atom_ids"]) <= referenced_atoms,
                    "SOURCE_ATOM_REALIZATION_MISSING", core + ":" + row["id"])


def _unit(ctx, core, unit):
    text(unit.get("title"), "UNIT_TITLE_REQUIRED")
    require(unit["bucket_id"] in ctx["buckets"], "UNIT_BUCKET_UNKNOWN")
    require(bool(unit["blocks"]), "UNIT_EMPTY")
    for b in unit["blocks"]:
        bid = text(b.get("id"), "CONTENT_ID_REQUIRED")
        require(bid not in ctx["objects"], "CONTENT_ID_COLLISION", bid)
        require(b.get("kind") in KINDS, "CONTENT_KIND_UNSUPPORTED")
        bindings = strings(b.get("obligation_ids"), "CONTENT_OBLIGATIONS_REQUIRED")
        atoms = strings(b.get("source_atom_ids"), "CONTENT_SOURCE_ATOMS_REQUIRED")
        require(set(atoms) <= ctx["atoms"].keys(), "CONTENT_SOURCE_UNKNOWN")
        for oid in bindings:
            require(oid in ctx["obligations"], "OBLIGATION_UNKNOWN", oid)
            ob = ctx["obligations"][oid]
            require(ob["bucket_id"] == unit["bucket_id"], "OBLIGATION_BUCKET_MISMATCH")
            require(set(atoms) & set(ob["source_atom_ids"]), "COVERAGE_SOURCE_MISMATCH")
            ctx["coverage"].append(dict(core=core, obligation_id=oid, object_id=bid, kind=b["kind"]))
        ctx["objects"][bid] = {"core": core, "unit": unit["id"], "content": b}
        if b["kind"] == "TEXT":
            text(b.get("text"), "EXPLANATION_BODY_EMPTY",)
        elif b["kind"] == "EQUATION":
            text(b.get("meaning"), "EQUATION_MEANING_REQUIRED")
            strings(b.get("conditions"), "EQUATION_CONDITIONS_REQUIRED")
            strings(b.get("symbols"), "EQUATION_SYMBOLS_REQUIRED")
        elif b["kind"] == "QUESTION":
            _question(ctx, b)
        require(b.get("placement", "TEACHING") in PLACEMENTS, "CONTENT_PLACEMENT_UNSUPPORTED",
                str(b.get("placement")))
        if b.get("placement", "TEACHING") == "ANSWER":
            text(b.get("question_id"), "ANSWER_FIGURE_QUESTION_REQUIRED")
        if b.get("placement") == "ELICITED_REVEAL":
            text(b.get("reveals_block_id"), "REVEAL_PROMPT_REQUIRED")
    order = {b["id"]: position for position, b in enumerate(unit["blocks"])}
    for position, b in enumerate(unit["blocks"]):
        if b.get("placement") == "ANSWER":
            target = next((q for q in unit["blocks"] if q["id"] == b["question_id"]), None)
            require(target is not None and target["kind"] == "QUESTION", "ANSWER_QUESTION_UNKNOWN")
        if b.get("placement") == "ELICITED_REVEAL":
            # A reveal is rendered closed, which is only honest if the prompt it answers
            # has already been read. A reveal placed first would still be closed and
            # would still have given the answer to a question not yet asked.
            prompt = b["reveals_block_id"]
            require(prompt in order, "REVEAL_PROMPT_UNKNOWN", prompt)
            require(order[prompt] < position, "REVEAL_PRECEDES_PROMPT", prompt)
            require(unit["blocks"][order[prompt]].get("placement", "TEACHING") == "TEACHING",
                    "REVEAL_PROMPT_NOT_READABLE", prompt)


def _question(ctx, block):
    key = (block["source_id"], block["source_question_id"])
    require(key in ctx["questions"], "QUESTION_SOURCE_UNKNOWN")
    original = ctx["questions"][key]
    require(block.get("stem") == original["stem"], "SOURCE_STEM_CHANGED")
    require(block.get("original_number") == original["original_number"], "SOURCE_NUMBER_CHANGED")
    for field in ("subparts", "options", "conditions"):
        require(block.get(field, []) == original.get(field, []), "SOURCE_QUESTION_FIELD_CHANGED", field)
    answer = block["answer"]
    text(answer.get("summary"), "ANSWER_BODY_EMPTY")
    strings(answer.get("steps"), "SOLUTION_STEPS_EMPTY")
    text(answer.get("check"), "ANSWER_CHECK_EMPTY")
    require(len(answer.get("subparts", [])) == len(original.get("subparts", [])), "SUBPART_ANSWER_MISSING")
    for part in answer.get("subparts", []):
        text(part, "SUBPART_ANSWER_EMPTY")
    hints = block.get("hints", [])
    require(isinstance(hints, list), "HINT_BODY_EMPTY")
    for position, hint in enumerate(hints):
        # A bare string is a hint whose reach is undeclared. Accepted because the frozen
        # port inputs predate the field, and they are the regression oracle: rewriting
        # them would change the basis digest recorded before the port and destroy the
        # thing they exist to prove. Everything the library compiles carries the declared
        # shape, and intake refuses anything else, so the undeclared form cannot spread.
        if isinstance(hint, str):
            text(hint, "HINT_BODY_EMPTY")
            continue
        require(isinstance(hint, dict), "HINT_BODY_EMPTY", str(position))
        text(hint.get("text"), "HINT_BODY_EMPTY")
        require(hint.get("reveals") in REVEALS, "HINT_REVEAL_UNDECLARED", str(hint.get("reveals")))
        # A hint that gives the answer leaves every hint after it with nothing to offer.
        # Checked here as well as at intake, because a plan can reach the engine without
        # having come through a library at all.
        require(hint["reveals"] != "ANSWER" or position == len(hints) - 1,
                "HINT_REVEALS_ANSWER_TOO_EARLY", f"{position + 1} of {len(hints)}")
    if "guidance" in block:
        strings(block["guidance"], "GUIDANCE_BODY_EMPTY")
    # A complete explanation/check is the minimum support. Hints and guides
    # supplement it according to task purpose; their count is not a quality proxy.
    text(block.get("family"), "EXAMPLE_FAMILY_REQUIRED")
    text(block.get("learner_action"), "LEARNER_ACTION_REQUIRED")
    # SOURCE_CUSTODY is not a teaching decision like the others. It marks a question
    # held in its original form because the bucket holds it, which is what makes
    # assessment demand enter the system as evidence rather than as an assumption.
    require(block.get("exposure_role") in {"NEW_TRANSFER", "PRACTICE", "RECONSTRUCTION_ANCHOR",
            "WORKED_TO_FADED", "SPACED_RETRIEVAL", "WORKED_EXAMPLE", "SOURCE_CUSTODY"},
            "EXPOSURE_ROLE_REQUIRED")


def _learner_fit(plan, products):
    if not set(products) & {"CORE2A", "CORE2B"}:
        return "NOT_APPLICABLE_STUDY_ONLY"
    control = plan.get("practice_control", {})
    require(control.get("purpose") in PURPOSES, "PRACTICE_PURPOSE_REQUIRED",
            str(control.get("purpose")))
    if control.get("mode") == "DESIGN_PREVIEW":
        return "BLOCKED_NO_PERSONALIZATION"
    if control.get("mode") == "OWNER_WAIVER":
        text(control.get("authorization_ref"), "OWNER_WAIVER_EVIDENCE_REQUIRED")
        text(control.get("support_plan"), "SUPPORT_PLAN_REQUIRED")
        return "OWNER_ROUTED_NOT_KNOWLEDGE_VALIDATED; AUTHORIZATION_REVIEW_PENDING"
    require(control.get("mode") == "KNOWLEDGE", "KNOWLEDGE_OR_WAIVER_REQUIRED")
    score = control.get("percentage")
    require(type(score) in {int, float} and 0 <= score <= 100, "KNOWLEDGE_PERCENTAGE_INVALID")
    for key in ("scope", "evidence_ref", "date", "calibration_policy", "support_plan"):
        text(control.get(key), "KNOWLEDGE_PROVENANCE_REQUIRED")
    return "PREDICTED_FIT_REVIEW_PENDING"
