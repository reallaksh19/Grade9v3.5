import {
  CORE_LEARNING_PAGE_TAG,
  validateCoreProjection,
} from "./core-learning-page.mjs";

const clone = (value) => value == null ? value : JSON.parse(JSON.stringify(value));

export class CoreLearningHostError extends Error {
  constructor(code, detail = "") {
    super(detail ? `${code}: ${detail}` : code);
    this.name = "CoreLearningHostError";
    this.code = code;
    this.detail = detail;
  }
}

function requireCondition(condition, code, detail = "") {
  if (!condition) throw new CoreLearningHostError(code, detail);
}

function requireObject(value, code, detail = "") {
  requireCondition(value && typeof value === "object" && !Array.isArray(value), code, detail);
  return value;
}

function requireString(value, code, detail = "") {
  requireCondition(typeof value === "string" && value.trim().length > 0, code, detail);
  return value;
}

function projectionRows(data) {
  requireObject(data, "CORE_LEARNING_DATA_REQUIRED");
  const rows = data.core_projections;
  requireCondition(
    Array.isArray(rows),
    "CORE_LEARNING_PROJECTIONS_REQUIRED",
    "generated data must expose a precompiled core_projections array",
  );
  return rows;
}

export function resolveCoreLearningRecord(data, projectionId) {
  const id = requireString(projectionId, "CORE_LEARNING_PROJECTION_ID_REQUIRED");
  const rows = projectionRows(data);
  const matches = rows.filter((row) => row && row.id === id);
  requireCondition(matches.length === 1, "CORE_LEARNING_PROJECTION_NOT_FOUND", id);

  const record = requireObject(matches[0], "CORE_LEARNING_PROJECTION_RECORD_INVALID", id);
  const sourceRef = requireString(record.source_ref, "CORE_LEARNING_SOURCE_REF_INVALID", id);
  const projection = validateCoreProjection(
    requireObject(record.projection, "CORE_LEARNING_PROJECTION_ENVELOPE_REQUIRED", id),
  );

  const sceneRef = record.scene_ref == null
    ? null
    : requireString(record.scene_ref, "CORE_LEARNING_SCENE_REF_INVALID", id);
  const adapterRef = record.adapter_ref == null
    ? null
    : requireString(record.adapter_ref, "CORE_LEARNING_ADAPTER_REF_INVALID", id);

  requireCondition(
    (sceneRef == null) === (adapterRef == null),
    "CORE_LEARNING_WORKBENCH_BINDING_INCOMPLETE",
    id,
  );

  const injectionRefs = record.injection_refs == null ? [] : record.injection_refs;
  requireCondition(
    Array.isArray(injectionRefs) && injectionRefs.every((ref) => typeof ref === "string" && ref),
    "CORE_LEARNING_INJECTION_REFS_INVALID",
    id,
  );
  requireCondition(
    sceneRef != null || injectionRefs.length === 0,
    "CORE_LEARNING_INJECTION_BINDING_INCOMPLETE",
    id,
  );

  return {
    id,
    sourceRef,
    projection,
    sceneRef,
    adapterRef,
    injectionRefs: [...injectionRefs],
  };
}

function resolveRegistryEntry(registry, ref, code) {
  requireObject(registry, code);
  requireCondition(
    Object.prototype.hasOwnProperty.call(registry, ref),
    code,
    ref,
  );
  return registry[ref];
}

export function resolveCoreLearningInputs(
  data,
  projectionId,
  {
    scenes = {},
    adapters = {},
    injections = {},
  } = {},
) {
  const record = resolveCoreLearningRecord(data, projectionId);
  if (!record.sceneRef) {
    return {
      id: record.id,
      projection: clone(record.projection),
      scene: null,
      adapter: null,
      injections: [],
    };
  }

  const scene = resolveRegistryEntry(
    scenes,
    record.sceneRef,
    "CORE_LEARNING_SCENE_NOT_FOUND",
  );
  const adapter = resolveRegistryEntry(
    adapters,
    record.adapterRef,
    "CORE_LEARNING_ADAPTER_NOT_FOUND",
  );
  const resolvedInjections = record.injectionRefs.map((ref) => resolveRegistryEntry(
    injections,
    ref,
    "CORE_LEARNING_INJECTION_NOT_FOUND",
  ));

  return {
    id: record.id,
    projection: clone(record.projection),
    scene,
    adapter,
    injections: resolvedInjections.map((row) => clone(row)),
  };
}

export function mountCoreLearningPage(
  element,
  data,
  projectionId,
  registries = {},
) {
  requireCondition(
    element && typeof element === "object",
    "CORE_LEARNING_ELEMENT_REQUIRED",
  );
  requireCondition(
    element.localName === CORE_LEARNING_PAGE_TAG
      || element.tagName?.toLowerCase?.() === CORE_LEARNING_PAGE_TAG,
    "CORE_LEARNING_ELEMENT_INVALID",
    element.localName || element.tagName || "",
  );

  const inputs = resolveCoreLearningInputs(data, projectionId, registries);
  requireCondition(
    typeof element.configure === "function",
    "CORE_LEARNING_ELEMENT_CONFIGURE_REQUIRED",
  );
  element.configure({
    projection: inputs.projection,
    scene: inputs.scene,
    adapter: inputs.adapter,
    injections: inputs.injections,
  });

  return {
    id: inputs.id,
    workbenchBound: Boolean(inputs.scene && inputs.adapter),
  };
}
