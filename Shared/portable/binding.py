"""Fail-closed AtlasIndex 2.0 -> portable package binding."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .package import (
    CANONICAL_PROVENANCE_AUTHORITY,
    PortablePackageError,
    validate_package,
)


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise PortablePackageError(code, detail)


def _text(value: Any, code: str, detail: str = "") -> str:
    _require(isinstance(value, str) and value.strip(), code, detail)
    return value


def resolve_portable_target(
    resource_ref: str,
    visual_targets: dict[str, dict[str, Any]],
    packages_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Resolve one canonical Atlas visual target to a validated portable package.

    The function consumes explicit AtlasIndex 2.0 IDs only. It never infers a
    package from title, locator, source order, or semantic similarity.
    """
    resource_ref = _text(resource_ref, "VISUAL_REF_UNAVAILABLE")
    _require(isinstance(visual_targets, dict), "VISUAL_TARGET_INDEX_INVALID")
    target = visual_targets.get(resource_ref)
    _require(isinstance(target, dict), "VISUAL_REF_UNAVAILABLE", resource_ref)
    _require(
        target.get("resource_ref") == resource_ref,
        "VISUAL_REF_INVALID",
        str(target.get("resource_ref")),
    )

    availability = target.get("availability")
    _require(isinstance(availability, dict), "VISUAL_TARGET_AVAILABILITY_INVALID", resource_ref)
    resource_status = availability.get("resource")
    if resource_status == "INVALID":
        raise PortablePackageError("VISUAL_REF_INVALID", resource_ref)
    _require(resource_status == "READY", "VISUAL_REF_UNAVAILABLE", resource_ref)

    package_ref = target.get("portable_package_ref")
    _require(
        availability.get("portable_package") == "READY"
        and isinstance(package_ref, str)
        and package_ref.strip(),
        "STANDALONE_PACKAGE_UNAVAILABLE",
        resource_ref,
    )

    _require(isinstance(packages_by_id, dict), "PORTABLE_PACKAGE_CATALOG_INVALID")
    package = packages_by_id.get(package_ref)
    _require(isinstance(package, dict), "PORTABLE_PACKAGE_NOT_FOUND", str(package_ref))
    package = validate_package(package)

    _require(package.get("id") == package_ref, "PORTABLE_PACKAGE_REF_MISMATCH", str(package.get("id")))
    _require(
        package.get("provenance", {}).get("authority") == CANONICAL_PROVENANCE_AUTHORITY,
        "PORTABLE_CANONICAL_PROVENANCE_REQUIRED",
        str(package_ref),
    )
    _require(
        package.get("resourceRef") == resource_ref,
        "PORTABLE_RESOURCE_BINDING_MISMATCH",
        str(package.get("resourceRef")),
    )

    representation_ref = package.get("provenance", {}).get("representationRef")
    representation_refs = target.get("representation_refs")
    _require(isinstance(representation_refs, list), "VISUAL_TARGET_REPRESENTATIONS_INVALID", resource_ref)
    _require(
        representation_ref in representation_refs,
        "PORTABLE_REPRESENTATION_BINDING_MISMATCH",
        str(representation_ref),
    )

    return {
        "resource_ref": resource_ref,
        "representation_ref": representation_ref,
        "portable_package_ref": package_ref,
        "locator": target.get("locator"),
        "delivery_profile": target.get("delivery_profile"),
        "standalone_ready": availability.get("standalone") == "READY",
        "package": deepcopy(package),
    }
