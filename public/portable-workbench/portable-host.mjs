import {
  WORKBENCH_API_VERSION,
  validateScene,
} from "./runtime.mjs";

export const PORTABLE_PACKAGE_VERSION = "1.0.0";
export const PORTABLE_TRANSFORMATION_IR_VERSION = "0.1.0";
export const PORTABLE_ADAPTER_API_VERSION = "0.1.0";
export const PORTABLE_SCENE_PACKAGE_VERSION = "1.0.0";
export const PORTABLE_ADAPTER_ID = "declarative-transfer-v1";

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
    requirePortable(rule.patch && typeof rule.patch === "object", "PORTABLE_ADAPTER_PATCH_REQUIRED", rule.id);
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
  requirePortable(pkg.provenance?.authority === "NON_CANONICAL_COMPILED_PROOF", "PORTABLE_PROVENANCE_AUTHORITY_INVALID");
  const scene = validateScene(pkg.scene);
  requirePortable(pkg.sceneRefs.length === 1 && pkg.sceneRefs[0] === scene.id, "PORTABLE_SCENE_REFS_MISMATCH");
  validateAdapter(pkg.adapter, scene);
  requirePortable(Array.isArray(pkg.injections), "PORTABLE_INJECTIONS_INVALID");
  return pkg;
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
