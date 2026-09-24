"""Question-level Core2 source-custody proofs."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402

DEMAND_FIELDS = (
    "source_refs", "origin", "origin_ref", "original_identifier", "stem",
    "subparts", "options", "conditions", "figure_refs", "hints", "answer", "adaptation",
)
ADAPTABLE_FIELDS = ("stem", "subparts", "options", "conditions", "figure_refs", "hints", "answer")
ARRAY_COMPONENT_FIELDS = {
    "subparts": "subparts", "options": "options", "conditions": "conditions",
    "figures": "figure_refs", "hints": "hints",
}
RESOLVED_COMPONENT_STATES = {"PRESERVED", "NOT_PRESENT_IN_SOURCE", "EXTERNAL_REFERENCE_VERIFIED"}


def demand_signature(question: dict) -> str:
    return digest({field: question.get(field) for field in DEMAND_FIELDS})


def proof_for(question: dict) -> dict | None:
    extensions = question.get("extensions")
    if not isinstance(extensions, dict):
        return None
    proof = extensions.get("source_custody")
    return proof if isinstance(proof, dict) else None


def _schema_findings(proof: dict, repo: Path) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    validator = jsonschema.Draft202012Validator(
        load(repo / "Shared/library/source-question-custody.schema.json")
    )
    return [{
        "point": "SOURCE_CUSTODY_PROOF_STRUCTURE",
        "where": "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(proof)]


def validate_question(
    question: dict, *, records: dict | None = None, acquisition: dict | None = None,
    inspected_sections: list[str] | None = None, access_status: str | None = None,
    require_resolved: bool = True, check_adaptation: bool = True, repo: Path = REPO,
) -> list[dict]:
    found: list[dict] = []
    qid = question.get("id", "")

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    proof = proof_for(question)
    if proof is None:
        fail("SOURCE_CUSTODY_PROOF_MISSING", qid,
             "source-derived Core2 question has no typed extensions.source_custody proof")
        return found

    found.extend(_schema_findings(proof, repo))
    if proof.get("demand_signature") != demand_signature(question):
        fail("SOURCE_CUSTODY_DEMAND_SIGNATURE_MISMATCH", qid,
             "current demand-bearing question fields differ from the custody proof")

    resource_ref = proof.get("resource_ref")
    if resource_ref not in (question.get("source_refs") or []):
        fail("SOURCE_CUSTODY_RESOURCE_UNBOUND", qid,
             "custody proof resource_ref is not present in question.source_refs")

    origin = question.get("origin")
    comparison = proof.get("comparison_status")
    if origin == "ORIGINAL":
        if comparison not in {"ORIGINAL_EXACT", "UNRESOLVED"}:
            fail("SOURCE_CUSTODY_ORIGINAL_COMPARISON_INVALID", qid,
                 "ORIGINAL question must use ORIGINAL_EXACT or remain UNRESOLVED")
        if question.get("adaptation") is not None:
            fail("SOURCE_CUSTODY_ORIGINAL_HAS_ADAPTATION", qid,
                 "ORIGINAL question cannot carry adaptation metadata")
        if question.get("origin_ref") != resource_ref:
            fail("SOURCE_CUSTODY_ORIGINAL_ORIGIN_REF_MISMATCH", qid,
                 "ORIGINAL question origin_ref must name the custody resource")
    elif origin == "ADAPTED":
        if comparison not in {"ADAPTED_DECLARED", "UNRESOLVED"}:
            fail("SOURCE_CUSTODY_ADAPTED_COMPARISON_INVALID", qid,
                 "ADAPTED question must use ADAPTED_DECLARED or remain UNRESOLVED")
        if not isinstance(question.get("adaptation"), dict):
            fail("SOURCE_CUSTODY_ADAPTATION_MISSING", qid,
                 "ADAPTED question must carry adaptation parent/change metadata")
    else:
        fail("SOURCE_CUSTODY_ORIGIN_INVALID", qid,
             "question-level source custody is only valid for ORIGINAL or ADAPTED questions")

    if acquisition is not None:
        if proof.get("acquisition_ref") != acquisition.get("acquisition_id"):
            fail("SOURCE_CUSTODY_ACQUISITION_MISMATCH", qid,
                 "custody proof does not name the acquired source bytes")
        if resource_ref != acquisition.get("resource_ref"):
            fail("SOURCE_CUSTODY_ACQUISITION_RESOURCE_MISMATCH", qid,
                 "custody proof resource differs from acquisition.resource_ref")
        if proof.get("source_digest") != acquisition.get("sha256"):
            fail("SOURCE_CUSTODY_SOURCE_DIGEST_MISMATCH", qid,
                 "custody proof digest differs from the acquired source bytes")

    if inspected_sections is not None and proof.get("source_item_locator") not in set(inspected_sections):
        fail("SOURCE_CUSTODY_LOCATOR_NOT_INSPECTED", str(proof.get("source_item_locator") or ""),
             "source item locator is not one of the manifest's explicitly inspected sections/items")

    if access_status is not None and access_status != "FULL_ITEM_INSPECTED":
        fail("SOURCE_CUSTODY_ITEM_NOT_FULLY_INSPECTED", qid,
             "question custody requires FULL_ITEM_INSPECTED source access")

    components = proof.get("components") if isinstance(proof.get("components"), dict) else {}
    if require_resolved:
        if comparison == "UNRESOLVED":
            fail("SOURCE_CUSTODY_COMPARISON_UNRESOLVED", qid,
                 "unresolved source comparison cannot establish Core2 custody")
        for name, state in components.items():
            if state not in RESOLVED_COMPONENT_STATES:
                fail("SOURCE_CUSTODY_COMPONENT_UNRESOLVED", f"{qid}:{name}",
                     "unresolved source component cannot establish Core2 custody")

    for essential in ("original_identifier", "stem"):
        if components.get(essential) == "NOT_PRESENT_IN_SOURCE":
            fail("SOURCE_CUSTODY_ESSENTIAL_COMPONENT_ABSENT", f"{qid}:{essential}",
                 "source identity and stem cannot be absent from a source question")

    for component, field in ARRAY_COMPONENT_FIELDS.items():
        state = components.get(component)
        value = question.get(field) or []
        if state == "PRESERVED" and not value:
            fail("SOURCE_CUSTODY_COMPONENT_PRESERVED_BUT_EMPTY", f"{qid}:{component}",
                 f"{component} is claimed preserved but canonical {field} is empty")
        if state == "NOT_PRESENT_IN_SOURCE" and value:
            fail("SOURCE_CUSTODY_COMPONENT_ABSENT_BUT_CANONICAL_PRESENT", f"{qid}:{component}",
                 f"{component} is claimed absent in source but canonical {field} is populated")

    figure_state = components.get("figures")
    caption_state = components.get("captions")
    figure_refs = question.get("figure_refs") or []
    if figure_state in {"PRESERVED", "EXTERNAL_REFERENCE_VERIFIED"} and not figure_refs:
        fail("SOURCE_CUSTODY_FIGURE_IDENTITY_MISSING", qid,
             "source figure is claimed present but question.figure_refs is empty")
    if figure_state == "NOT_PRESENT_IN_SOURCE" and caption_state not in {
        "NOT_PRESENT_IN_SOURCE", "UNRESOLVED", None
    }:
        fail("SOURCE_CUSTODY_CAPTION_WITHOUT_SOURCE_FIGURE", qid,
             "caption custody cannot be claimed when the source has no figure")

    if proof.get("custody_mode") == "EMBEDDED_VERBATIM":
        for name, state in components.items():
            if state == "EXTERNAL_REFERENCE_VERIFIED":
                fail("SOURCE_CUSTODY_MODE_COMPONENT_MISMATCH", f"{qid}:{name}",
                     "EMBEDDED_VERBATIM custody cannot outsource an individual component")

    if records is not None:
        resource = records.get(resource_ref)
        if not resource or resource.get("_collection") != "resources":
            fail("SOURCE_CUSTODY_RESOURCE_DANGLING", str(resource_ref or ""),
                 "custody proof resource does not resolve to a canonical resource")
        else:
            if resource.get("origin") == "AUTHORED":
                fail("SOURCE_CUSTODY_AUTHORED_RESOURCE", resource_ref,
                     "an authored resource cannot establish external source custody")
            if resource.get("snapshot_digest") != proof.get("source_digest"):
                fail("SOURCE_CUSTODY_RESOURCE_DIGEST_MISMATCH", resource_ref,
                     "canonical resource snapshot digest differs from the custody proof")
            if not resource.get("snapshot_ref"):
                fail("SOURCE_CUSTODY_RESOURCE_SNAPSHOT_MISSING", resource_ref,
                     "Core2 question custody requires retained source bytes")

        if caption_state == "PRESERVED":
            for ref in figure_refs:
                figure = records.get(ref)
                if not figure or figure.get("_collection") != "resources":
                    fail("SOURCE_CUSTODY_FIGURE_REF_INVALID", ref,
                         "preserved source figure must resolve to a resource record")
                elif not str(figure.get("caption", "")).strip():
                    fail("SOURCE_CUSTODY_FIGURE_CAPTION_MISSING", ref,
                         "preserved source figure has no preserved caption")

        if origin == "ADAPTED" and check_adaptation:
            adaptation = question.get("adaptation") or {}
            parent_ref = adaptation.get("parent_ref")
            parent = records.get(parent_ref)
            if not parent or parent.get("_collection") != "questions":
                fail("SOURCE_CUSTODY_ADAPTATION_PARENT_DANGLING", str(parent_ref or ""),
                     "ADAPTED question parent_ref does not resolve to a canonical question")
            else:
                if parent.get("status") not in {"REVIEWED", "CURATED"}:
                    fail("SOURCE_CUSTODY_ADAPTATION_PARENT_UNREVIEWED", parent_ref,
                         "ADAPTED Core2 custody requires a reviewed/curated source parent")
                parent_findings = validate_question(
                    parent, records=records, require_resolved=True,
                    check_adaptation=False, repo=repo,
                )
                if parent_findings:
                    fail("SOURCE_CUSTODY_ADAPTATION_PARENT_INVALID", parent_ref,
                         "adaptation parent does not itself have valid resolved source custody")

                declared = set(adaptation.get("changed_fields") or [])
                unsupported = sorted(declared - set(ADAPTABLE_FIELDS))
                if unsupported:
                    fail("SOURCE_CUSTODY_ADAPTATION_FIELD_INVALID", qid,
                         "changed_fields contains non-demand fields: " + ", ".join(unsupported))
                actual = {field for field in ADAPTABLE_FIELDS
                          if question.get(field) != parent.get(field)}
                missing = sorted(actual - declared)
                false_claims = sorted(declared - actual)
                if missing:
                    fail("SOURCE_CUSTODY_ADAPTATION_CHANGES_UNDECLARED", qid,
                         "material changes missing from changed_fields: " + ", ".join(missing))
                if false_claims:
                    fail("SOURCE_CUSTODY_ADAPTATION_CHANGES_FALSE", qid,
                         "changed_fields claims unchanged fields: " + ", ".join(false_claims))

    return found


def valid_for_core2(question: dict, records: dict, repo: Path = REPO) -> bool:
    return (
        question.get("origin") in {"ORIGINAL", "ADAPTED"}
        and not validate_question(question, records=records, require_resolved=True, repo=repo)
    )
