import {
  WORKBENCH_API_VERSION,
  validateScene,
} from "../workbench/runtime.mjs";

export const PORTABLE_PACKAGE_VERSION = "1.0.0";
export const PORTABLE_TRANSFORMATION_IR_VERSION = "0.1.0";
export const PORTABLE_ADAPTER_API_VERSION = "0.2.0";
export const PORTABLE_SCENE_PACKAGE_VERSION = "1.0.0";
export const PORTABLE_ADAPTER_ID = "declarative-transfer-v1";
export const NON_CANONICAL_PROVENANCE_AUTHORITY = "NON_CANONICAL_COMPILED_PROOF";
export const CANONICAL_PROVENANCE_AUTHORITY = "CANONICAL_COMPILED_RESOURCE";

const executableKeys = new Set([
  "script", "javascript", "eval", "function", "handler",
  "onclick", "onload", "onerror", "sourcecode", "executable",
]);
const pixelKeys = new Set(["x", "y", "left", "top", "width", "height"]);
const portableClone = (value) => JSON.parse(JSON.stringify(value));

export class PortablePackageError extends Error {
  constructor(code, detail = "") {
    super(detail ? `${code}: ${detail}` : code);
    this.name = "PortablePackageError";
    this.code = code;
    this.detail = detail;
  }
}

function requirePortable(condition, code, detail = "") {
  if (!condition) throw new PortablePackageError(code, detail);
}

function nonEmpty(value, code, detail = "") {
  requirePortable(typeof value === "string" && value.trim().length > 0, code, detail);
  return value;
}

function stringList(value, code) {
  requirePortable(Array.isArray(value), code);
  value.forEach((row) => nonEmpty(row, code));
  requirePortable(new Set(value).size === value.length, code);
  return value;
}

function scanData(value, path = "package") {
  requirePortable(typeof value !== "function", "PORTABLE_EXECUTABLE_VALUE_FORBIDDEN", path);
  if (Array.isArray(value)) {
    value.forEach((row, index) => scanData(row, `${path}[${index}]`));
    return;
  }
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    requirePortable(!executableKeys.has(key.toLowerCase()), "PORTABLE_EXECUTABLE_FIELD_FORBIDDEN", `${path}.${key}`);
    if (key === "placement" && child && typeof child === "object") {
      for (const pixel of pixelKeys) {
        requirePortable(!(pixel in child), "PORTABLE_PIXEL_COORDINATE_FORBIDDEN", `${path}.${key}.${pixel}`);
      }
    }
    scanData(child, `${path}.${key}`);
  }
}

function validateAdapter(adapter, scene) {
  requirePortable(adapter && typeof adapter === "object", "PORTABLE_ADAPTER_REQUIRED");
  requirePortable(adapter.id === PORTABLE_ADAPTER_ID, "PORTABLE_ADAPTER_ID_UNSUPPORTED", String(adapter.id));
  requirePortable(adapter.apiVersion === PORTABLE_ADAPTER_API_VERSION, "PORTABLE_ADAPTER_API_VERSION_MISMATCH", String(adapter.apiVersion));
  requirePortable(Array.isArray(adapter.rules) && adapter.rules.length > 0, "PORTABLE_ADAPTER_RULES_REQUIRED");
  const transforms = new Map(scene.canonicalTransformations.map((row) => [row.id, row]));
  const targets = new Map(scene.targets.map((row) => [row.id, row]));
  const ids = new Set();
  for (const rule of adapter.rules) {
    nonEmpty(rule.id, "PORTABLE_ADAPTER_RULE_ID_REQUIRED");
    requirePortable(!ids.has(rule.id), "PORTABLE_ADAPTER_RULE_ID_DUPLICATE", rule.id);
    ids.add(rule.id);
    const transform = transforms.get(rule.transformationRef);
    requirePortable(Boolean(transform), "PORTABLE_ADAPTER_TRANSFORMATION_UNKNOWN", String(rule.transformationRef));
    requirePortable(transform.sourceEntityRefs.includes(rule.sourceEntityRef), "PORTABLE_ADAPTER_SOURCE_MISMATCH", rule.id);
    requirePortable(transform.targetRef === rule.targetRef, "PORTABLE_ADAPTER_TARGET_MISMATCH", rule.id);
    requirePortable(targets.get(rule.targetRef)?.operation === rule.operation, "PORTABLE_ADAPTER_OPERATION_MISMATCH", rule.id);
    const outcome = rule.outcome ?? "ACCEPT";
    requirePortable(["ACCEPT", "REJECT"].includes(outcome), "PORTABLE_ADAPTER_OUTCOME_INVALID", rule.id);
    if (outcome === "REJECT") {
      nonEmpty(rule.reason, "PORTABLE_ADAPTER_REJECTION_REASON_REQUIRED", rule.id);
      requirePortable(!("patch" in rule), "PORTABLE_ADAPTER_REJECTION_PATCH_FORBIDDEN", rule.id);
    } else {
      requirePortable(rule.patch && typeof rule.patch === "object", "PORTABLE_ADAPTER_PATCH_REQUIRED", rule.id);
    }
  }
}

export function validatePortablePackage(input) {
  const pkg = portableClone(input);
  scanData(pkg);
  const expected = {
    schemaVersion: "portable-workbench-package",
    packageVersion: PORTABLE_PACKAGE_VERSION,
    componentApiVersion: WORKBENCH_API_VERSION,
    transformationIrVersion: PORTABLE_TRANSFORMATION_IR_VERSION,
    adapterApiVersion: PORTABLE_ADAPTER_API_VERSION,
    scenePackageVersion: PORTABLE_SCENE_PACKAGE_VERSION,
  };
  for (const [key, value] of Object.entries(expected)) {
    requirePortable(pkg[key] === value, `PORTABLE_${key.toUpperCase()}_MISMATCH`, String(pkg[key]));
  }
  nonEmpty(pkg.id, "PORTABLE_PACKAGE_ID_REQUIRED");
  nonEmpty(pkg.title, "PORTABLE_PACKAGE_TITLE_REQUIRED");
  for (const field of ["sourceRefs", "sceneRefs", "representationRefs", "assetRefs", "accessibilityRefs"]) {
    stringList(pkg[field], `PORTABLE_${field.toUpperCase()}_INVALID`);
  }
  requirePortable(Array.isArray(pkg.questionBindings), "PORTABLE_QUESTION_BINDINGS_INVALID");
  const authority = pkg.provenance?.authority;
  requirePortable(
    [NON_CANONICAL_PROVENANCE_AUTHORITY, CANONICAL_PROVENANCE_AUTHORITY].includes(authority),
    "PORTABLE_PROVENANCE_AUTHORITY_INVALID",
    String(authority),
  );
  if (authority === CANONICAL_PROVENANCE_AUTHORITY) {
    nonEmpty(pkg.resourceRef, "PORTABLE_CANONICAL_RESOURCE_REF_REQUIRED");
    nonEmpty(pkg.provenance?.resourceRef, "PORTABLE_CANONICAL_RESOURCE_REF_REQUIRED");
    requirePortable(
      pkg.provenance.resourceRef === pkg.resourceRef,
      "PORTABLE_CANONICAL_RESOURCE_REF_MISMATCH",
      String(pkg.provenance.resourceRef),
    );
    nonEmpty(pkg.provenance?.representationRef, "PORTABLE_CANONICAL_REPRESENTATION_REF_REQUIRED");
    requirePortable(
      pkg.representationRefs.includes(pkg.provenance.representationRef),
      "PORTABLE_CANONICAL_REPRESENTATION_REF_MISMATCH",
      String(pkg.provenance.representationRef),
    );
    stringList(pkg.provenance?.sourceRefs, "PORTABLE_CANONICAL_SOURCE_REFS_REQUIRED");
    requirePortable(pkg.provenance.sourceRefs.length > 0, "PORTABLE_CANONICAL_SOURCE_REFS_REQUIRED");
    requirePortable(
      JSON.stringify(pkg.provenance.sourceRefs) === JSON.stringify(pkg.sourceRefs),
      "PORTABLE_CANONICAL_SOURCE_REFS_MISMATCH",
    );
  }
  const scene = validateScene(pkg.scene);
  requirePortable(pkg.sceneRefs.length === 1 && pkg.sceneRefs[0] === scene.id, "PORTABLE_SCENE_REFS_MISMATCH");
  validateAdapter(pkg.adapter, scene);
  requirePortable(Array.isArray(pkg.injections), "PORTABLE_INJECTIONS_INVALID");
  return pkg;
}

export function resolveCanonicalPortableTarget(resourceRef, visualTargets, packagesById) {
  nonEmpty(resourceRef, "VISUAL_REF_UNAVAILABLE");
  requirePortable(visualTargets && typeof visualTargets === "object" && !Array.isArray(visualTargets), "VISUAL_TARGET_INDEX_INVALID");
  const target = visualTargets[resourceRef];
  requirePortable(target && typeof target === "object" && !Array.isArray(target), "VISUAL_REF_UNAVAILABLE", resourceRef);
  requirePortable(target.resource_ref === resourceRef, "VISUAL_REF_INVALID", String(target.resource_ref));
  requirePortable(target.availability && typeof target.availability === "object", "VISUAL_TARGET_AVAILABILITY_INVALID", resourceRef);
  if (target.availability.resource === "INVALID") throw new PortablePackageError("VISUAL_REF_INVALID", resourceRef);
  requirePortable(target.availability.resource === "READY", "VISUAL_REF_UNAVAILABLE", resourceRef);

  const packageRef = target.portable_package_ref;
  requirePortable(
    target.availability.portable_package === "READY" && typeof packageRef === "string" && packageRef.trim().length > 0,
    "STANDALONE_PACKAGE_UNAVAILABLE",
    resourceRef,
  );
  requirePortable(packagesById && typeof packagesById === "object" && !Array.isArray(packagesById), "PORTABLE_PACKAGE_CATALOG_INVALID");
  requirePortable(packagesById[packageRef] && typeof packagesById[packageRef] === "object", "PORTABLE_PACKAGE_NOT_FOUND", String(packageRef));
  const pkg = validatePortablePackage(packagesById[packageRef]);
  requirePortable(pkg.id === packageRef, "PORTABLE_PACKAGE_REF_MISMATCH", String(pkg.id));
  requirePortable(pkg.provenance?.authority === CANONICAL_PROVENANCE_AUTHORITY, "PORTABLE_CANONICAL_PROVENANCE_REQUIRED", packageRef);
  requirePortable(pkg.resourceRef === resourceRef, "PORTABLE_RESOURCE_BINDING_MISMATCH", String(pkg.resourceRef));
  requirePortable(Array.isArray(target.representation_refs), "VISUAL_TARGET_REPRESENTATIONS_INVALID", resourceRef);
  const representationRef = pkg.provenance?.representationRef;
  requirePortable(target.representation_refs.includes(representationRef), "PORTABLE_REPRESENTATION_BINDING_MISMATCH", String(representationRef));

  return {
    resourceRef,
    representationRef,
    portablePackageRef: packageRef,
    locator: target.locator ?? null,
    deliveryProfile: target.delivery_profile ?? null,
    standaloneReady: target.availability.standalone === "READY",
    package: portableClone(pkg),
  };
}

export function createDeclarativeAdapter(packageInput) {
  const pkg = validatePortablePackage(packageInput);
  return {
    evaluateTransfer(request) {
      const rule = pkg.adapter.rules.find((row) =>
        row.sourceEntityRef === request.sourceEntityRef
        && row.targetRef === request.targetRef
        && row.operation === request.operation
      );
      if (!rule) {
        const allowedTargets = pkg.adapter.rules
          .filter((row) => row.sourceEntityRef === request.sourceEntityRef)
          .map((row) => row.targetRef);
        return {
          accepted: false,
          reason: "No compiled transformation rule authorizes this transfer.",
          allowedTargets: [...new Set(allowedTargets)],
        };
      }
      if ((rule.outcome ?? "ACCEPT") === "REJECT") {
        return {
          accepted: false,
          reason: rule.reason,
          allowedTargets: [rule.targetRef],
        };
      }
      return {
        accepted: true,
        summary: rule.summary || "Compiled transformation accepted.",
        patch: portableClone(rule.patch),
      };
    },
  };
}

export function mountPortableWorkbench(element, packageInput) {
  requirePortable(element && typeof element === "object", "PORTABLE_HOST_ELEMENT_REQUIRED");
  const pkg = validatePortablePackage(packageInput);
  element.scene = portableClone(pkg.scene);
  element.adapter = createDeclarativeAdapter(pkg);
  element.injections = portableClone(pkg.injections);
  return pkg;
}
