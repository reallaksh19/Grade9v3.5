export const WORKBENCH_API_VERSION = "0.1.0";

export class WorkbenchError extends Error {
  constructor(code, detail = "") {
    super(detail ? `${code}: ${detail}` : code);
    this.name = "WorkbenchError";
    this.code = code;
    this.detail = detail;
  }
}

const clone = (value) => JSON.parse(JSON.stringify(value));

function requireCondition(condition, code, detail = "") {
  if (!condition) throw new WorkbenchError(code, detail);
}

function nonEmptyString(value, code, detail = "") {
  requireCondition(typeof value === "string" && value.trim().length > 0, code, detail);
  return value;
}

function uniqueStrings(values, code, detail) {
  requireCondition(Array.isArray(values) && values.length > 0, code, detail);
  values.forEach((value) => nonEmptyString(value, code, detail));
  requireCondition(new Set(values).size === values.length, code, detail);
}

function uniqueIds(rows, code) {
  const ids = rows.map((row) => nonEmptyString(row?.id, code));
  requireCondition(new Set(ids).size === ids.length, code);
}

function validateStringRefs(values, code, detail = "") {
  requireCondition(Array.isArray(values), code, detail);
  values.forEach((value) => nonEmptyString(value, code, detail));
  requireCondition(new Set(values).size === values.length, code, detail);
  return values;
}

function validateProvenanceMetadata(provenance, owner) {
  if (provenance == null) return [];
  requireCondition(
    typeof provenance === "object" && !Array.isArray(provenance),
    "WORKBENCH_PROVENANCE_INVALID",
    owner,
  );
  if (Object.prototype.hasOwnProperty.call(provenance, "kind")) {
    nonEmptyString(provenance.kind, "WORKBENCH_PROVENANCE_INVALID", owner);
  }
  if (!Object.prototype.hasOwnProperty.call(provenance, "sourceEntityRefs")) return [];
  return validateStringRefs(
    provenance.sourceEntityRefs,
    "WORKBENCH_PROVENANCE_INVALID",
    owner,
  );
}

function indexById(rows) {
  return Object.fromEntries(rows.map((row) => [row.id, row]));
}

function validateProvenanceAcyclic(entities) {
  const byId = indexById(entities);
  const visiting = new Set();
  const visited = new Set();

  function visit(entityId, path) {
    if (visited.has(entityId)) return;
    if (visiting.has(entityId)) {
      const start = path.indexOf(entityId);
      const cycle = [...path.slice(start), entityId];
      throw new WorkbenchError("WORKBENCH_PROVENANCE_CYCLE", cycle.join(" -> "));
    }

    visiting.add(entityId);
    path.push(entityId);
    const sources = byId[entityId]?.provenance?.sourceEntityRefs || [];
    for (const source of sources) visit(source, path);
    path.pop();
    visiting.delete(entityId);
    visited.add(entityId);
  }

  for (const entity of entities) visit(entity.id, []);
}

function validatePlacement(scene, placement, owner) {
  requireCondition(placement && typeof placement === "object" && !Array.isArray(placement),
    "WORKBENCH_PLACEMENT_REQUIRED", owner);
  for (const forbidden of ["x", "y", "left", "top", "width", "height"]) {
    requireCondition(!(forbidden in placement), "WORKBENCH_PIXEL_COORDINATE_FORBIDDEN", `${owner}.${forbidden}`);
  }
  const allowed = new Set(["grid", "row", "column"]);
  for (const key of Object.keys(placement)) {
    requireCondition(allowed.has(key), "WORKBENCH_PLACEMENT_FIELD_UNSUPPORTED", `${owner}.${key}`);
  }

  const gridId = nonEmptyString(placement.grid, "WORKBENCH_GRID_REF_REQUIRED", owner);
  const rowId = nonEmptyString(placement.row, "WORKBENCH_ROW_REF_REQUIRED", owner);
  const columnId = nonEmptyString(placement.column, "WORKBENCH_COLUMN_REF_REQUIRED", owner);
  const grid = scene.grids.find((row) => row.id === gridId);
  requireCondition(grid, "WORKBENCH_GRID_UNKNOWN", `${owner} -> ${gridId}`);
  requireCondition(grid.rows.includes(rowId), "WORKBENCH_ROW_UNKNOWN", `${owner} -> ${rowId}`);
  requireCondition(grid.columns.includes(columnId), "WORKBENCH_COLUMN_UNKNOWN", `${owner} -> ${columnId}`);
}

export function validateScene(input) {
  const scene = clone(input);
  requireCondition(scene && typeof scene === "object" && !Array.isArray(scene),
    "WORKBENCH_SCENE_REQUIRED");
  requireCondition(scene.apiVersion === WORKBENCH_API_VERSION,
    "WORKBENCH_API_VERSION_MISMATCH", String(scene.apiVersion));
  nonEmptyString(scene.sceneVersion, "WORKBENCH_SCENE_VERSION_REQUIRED");
  nonEmptyString(scene.id, "WORKBENCH_SCENE_ID_REQUIRED");

  requireCondition(Array.isArray(scene.grids) && scene.grids.length > 0,
    "WORKBENCH_GRIDS_REQUIRED", scene.id);
  uniqueIds(scene.grids, "WORKBENCH_GRID_ID_INVALID");
  for (const grid of scene.grids) {
    uniqueStrings(grid.rows, "WORKBENCH_GRID_ROWS_INVALID", grid.id);
    uniqueStrings(grid.columns, "WORKBENCH_GRID_COLUMNS_INVALID", grid.id);
  }

  scene.entities = scene.entities || [];
  scene.projections = scene.projections || [];
  scene.targets = scene.targets || [];
  scene.canonicalTransformations = scene.canonicalTransformations || [];
  requireCondition(Array.isArray(scene.entities), "WORKBENCH_ENTITIES_INVALID");
  requireCondition(Array.isArray(scene.projections), "WORKBENCH_PROJECTIONS_INVALID");
  requireCondition(Array.isArray(scene.targets), "WORKBENCH_TARGETS_INVALID");
  requireCondition(Array.isArray(scene.canonicalTransformations), "WORKBENCH_TRANSFORMATIONS_INVALID");
  uniqueIds(scene.entities, "WORKBENCH_ENTITY_ID_INVALID");
  uniqueIds(scene.projections, "WORKBENCH_PROJECTION_ID_INVALID");
  uniqueIds(scene.targets, "WORKBENCH_TARGET_ID_INVALID");
  uniqueIds(scene.canonicalTransformations, "WORKBENCH_TRANSFORMATION_ID_INVALID");

  const entityIds = new Set(scene.entities.map((row) => row.id));
  for (const entity of scene.entities) {
    nonEmptyString(entity.label, "WORKBENCH_ENTITY_LABEL_REQUIRED", entity.id);
    const sources = validateProvenanceMetadata(entity.provenance, entity.id);
    for (const source of sources) {
      requireCondition(entityIds.has(source),
        "WORKBENCH_PROVENANCE_SOURCE_UNKNOWN", `${entity.id} -> ${source}`);
    }
  }
  validateProvenanceAcyclic(scene.entities);
  for (const projection of scene.projections) {
    nonEmptyString(projection.entityRef, "WORKBENCH_PROJECTION_ENTITY_REQUIRED", projection.id);
    requireCondition(entityIds.has(projection.entityRef), "WORKBENCH_PROJECTION_ENTITY_UNKNOWN", projection.id);
    nonEmptyString(projection.label, "WORKBENCH_PROJECTION_LABEL_REQUIRED", projection.id);
    validatePlacement(scene, projection.placement, projection.id);
  }
  for (const target of scene.targets) {
    nonEmptyString(target.label, "WORKBENCH_TARGET_LABEL_REQUIRED", target.id);
    nonEmptyString(target.operation, "WORKBENCH_TARGET_OPERATION_REQUIRED", target.id);
    validatePlacement(scene, target.placement, target.id);
  }

  const targetIds = new Set(scene.targets.map((row) => row.id));
  for (const transformation of scene.canonicalTransformations) {
    validateStringRefs(
      transformation.sourceEntityRefs,
      "WORKBENCH_TRANSFORMATION_SOURCES_INVALID",
      transformation.id,
    );
    const targetRef = nonEmptyString(
      transformation.targetRef,
      "WORKBENCH_TRANSFORMATION_TARGET_REQUIRED",
      transformation.id,
    );
    requireCondition(
      targetIds.has(targetRef),
      "WORKBENCH_TRANSFORMATION_TARGET_UNKNOWN",
      `${transformation.id} -> ${targetRef}`,
    );
  }

  return scene;
}

export function resolvePlacement(sceneInput, placement) {
  const scene = validateScene(sceneInput);
  validatePlacement(scene, placement, "placement");
  const grid = scene.grids.find((row) => row.id === placement.grid);
  return {
    grid: grid.id,
    row: grid.rows.indexOf(placement.row) + 1,
    column: grid.columns.indexOf(placement.column) + 1,
  };
}

export function validateInjections(injections, sceneInput) {
  const scene = validateScene(sceneInput);
  const rows = clone(injections || []);
  requireCondition(Array.isArray(rows), "WORKBENCH_INJECTIONS_INVALID");
  uniqueIds(rows, "WORKBENCH_INJECTION_ID_INVALID");
  const transformations = new Set(scene.canonicalTransformations.map((row) => row.id));
  for (const row of rows) {
    nonEmptyString(row.kind, "WORKBENCH_INJECTION_KIND_REQUIRED", row.id);
    nonEmptyString(row.prompt, "WORKBENCH_INJECTION_PROMPT_REQUIRED", row.id);
    if (row.afterTransformationRef != null) {
      requireCondition(transformations.has(row.afterTransformationRef),
        "WORKBENCH_INJECTION_TRANSFORMATION_UNKNOWN", row.id);
    }
  }
  return rows;
}

function requestForAdapter(request) {
  return clone({
    sourceEntityRef: request.sourceEntityRef,
    targetRef: request.targetRef,
    operation: request.operation,
  });
}

function snapshotForAdapter(state) {
  return clone({
    sceneId: state.sceneId,
    sceneVersion: state.sceneVersion,
    revision: state.revision,
    grids: state.grids,
    entities: state.entities,
    projections: state.projections,
    targets: state.targets,
    canonicalTransformations: state.canonicalTransformations,
  });
}

function validateAllowedTargets(state, allowedTargetsInput) {
  if (allowedTargetsInput == null) return [];
  const allowedTargets = clone(allowedTargetsInput);
  validateStringRefs(allowedTargets, "WORKBENCH_ALLOWED_TARGETS_INVALID", "allowedTargets");
  const targetIds = new Set(state.targets.map((row) => row.id));
  for (const targetRef of allowedTargets) {
    requireCondition(
      targetIds.has(targetRef),
      "WORKBENCH_ALLOWED_TARGET_UNKNOWN",
      targetRef,
    );
  }
  return allowedTargets;
}

function validatePatch(currentState, patchInput, usedEntityIds, usedProjectionIds) {
  const patch = clone(patchInput || {});
  const allowedKeys = new Set(["addEntities", "addProjections"]);
  for (const key of Object.keys(patch)) {
    requireCondition(allowedKeys.has(key), "WORKBENCH_PATCH_FIELD_UNSUPPORTED", key);
  }
  patch.addEntities = patch.addEntities || [];
  patch.addProjections = patch.addProjections || [];
  requireCondition(Array.isArray(patch.addEntities), "WORKBENCH_PATCH_ENTITIES_INVALID");
  requireCondition(Array.isArray(patch.addProjections), "WORKBENCH_PATCH_PROJECTIONS_INVALID");
  requireCondition(patch.addEntities.length > 0 || patch.addProjections.length > 0,
    "WORKBENCH_PATCH_EMPTY");
  uniqueIds(patch.addEntities, "WORKBENCH_PATCH_ENTITY_ID_INVALID");
  uniqueIds(patch.addProjections, "WORKBENCH_PATCH_PROJECTION_ID_INVALID");

  const existingEntityIds = new Set(currentState.entities.map((row) => row.id));
  const nextEntityIds = new Set(existingEntityIds);
  for (const entity of patch.addEntities) {
    nonEmptyString(entity.label, "WORKBENCH_ENTITY_LABEL_REQUIRED", entity.id);
    requireCondition(!nextEntityIds.has(entity.id), "WORKBENCH_PATCH_ENTITY_EXISTS", entity.id);
    requireCondition(!usedEntityIds.has(entity.id), "WORKBENCH_ENTITY_ID_REUSED", entity.id);
    const sources = validateProvenanceMetadata(entity.provenance, entity.id);
    for (const source of sources) {
      requireCondition(existingEntityIds.has(source), "WORKBENCH_PROVENANCE_SOURCE_UNKNOWN", `${entity.id} -> ${source}`);
    }
    nextEntityIds.add(entity.id);
  }

  const existingProjectionIds = new Set(currentState.projections.map((row) => row.id));
  const sceneLike = {
    apiVersion: WORKBENCH_API_VERSION,
    sceneVersion: currentState.sceneVersion,
    id: currentState.sceneId,
    grids: currentState.grids,
    entities: [...currentState.entities, ...patch.addEntities],
    projections: [],
    targets: [],
    canonicalTransformations: [],
  };
  for (const projection of patch.addProjections) {
    nonEmptyString(projection.entityRef, "WORKBENCH_PROJECTION_ENTITY_REQUIRED", projection.id);
    requireCondition(nextEntityIds.has(projection.entityRef), "WORKBENCH_PROJECTION_ENTITY_UNKNOWN", projection.id);
    requireCondition(!existingProjectionIds.has(projection.id), "WORKBENCH_PATCH_PROJECTION_EXISTS", projection.id);
    requireCondition(!usedProjectionIds.has(projection.id), "WORKBENCH_PROJECTION_ID_REUSED", projection.id);
    nonEmptyString(projection.label, "WORKBENCH_PROJECTION_LABEL_REQUIRED", projection.id);
    validatePlacement(sceneLike, projection.placement, projection.id);
    existingProjectionIds.add(projection.id);
  }
  return patch;
}

export class WorkbenchRuntime {
  constructor(sceneInput, adapter, { injections = [], eventSink = null } = {}) {
    requireCondition(adapter && typeof adapter.evaluateTransfer === "function",
      "WORKBENCH_ADAPTER_REQUIRED");
    const scene = validateScene(sceneInput);
    this._adapter = adapter;
    this._eventSink = typeof eventSink === "function" ? eventSink : null;
    this._injections = validateInjections(injections, scene);
    this._state = {
      sceneId: scene.id,
      sceneVersion: scene.sceneVersion,
      revision: 0,
      grids: clone(scene.grids),
      entities: clone(scene.entities),
      projections: clone(scene.projections),
      targets: clone(scene.targets),
      canonicalTransformations: clone(scene.canonicalTransformations),
      interaction: {
        inspectedEntityRef: null,
        inspectedProjectionRef: null,
        pickedEntityRef: null,
        preview: null,
      },
    };
    this._history = [];
    this._future = [];
    this._usedEntityIds = new Set(scene.entities.map((row) => row.id));
    this._usedProjectionIds = new Set(scene.projections.map((row) => row.id));
    this._dispatching = false;
  }

  get snapshot() {
    return clone(this._state);
  }

  get injections() {
    return clone(this._injections);
  }

  get canonicalTransformations() {
    return clone(this._state.canonicalTransformations);
  }

  get canUndo() {
    return this._history.length > 0;
  }

  get canRedo() {
    return this._future.length > 0;
  }

  _emit(type, detail = {}) {
    const event = clone({
      type,
      sceneId: this._state.sceneId,
      revision: this._state.revision,
      ...detail,
    });
    if (this._eventSink) {
      try {
        this._eventSink(clone(event));
      } catch {
        // Observers are downstream of semantic state; host failures cannot alter dispatch.
      }
    }
    return event;
  }

  _entity(entityRef) {
    return this._state.entities.find((row) => row.id === entityRef) || null;
  }

  _projection(projectionRef) {
    return this._state.projections.find((row) => row.id === projectionRef) || null;
  }

  _linkedProjectionRefs(entityRef) {
    return this._state.projections
      .filter((row) => row.entityRef === entityRef)
      .map((row) => row.id);
  }

  _target(targetRef) {
    return this._state.targets.find((row) => row.id === targetRef) || null;
  }

  _request(targetRef, channel) {
    const sourceEntityRef = this._state.interaction.pickedEntityRef;
    requireCondition(sourceEntityRef, "WORKBENCH_SOURCE_NOT_PICKED");
    const target = this._target(targetRef);
    requireCondition(target, "WORKBENCH_TARGET_UNKNOWN", targetRef);
    return {
      sourceEntityRef,
      targetRef,
      operation: target.operation,
      channel: channel || "unknown",
    };
  }

  _decision(request) {
    let raw;
    try {
      raw = this._adapter.evaluateTransfer(
        requestForAdapter(request),
        snapshotForAdapter(this._state),
      );
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error);
      return {
        accepted: false,
        reason,
        code: "WORKBENCH_ADAPTER_FAILURE",
        allowedTargets: [],
      };
    }

    try {
      requireCondition(raw && typeof raw === "object", "WORKBENCH_ADAPTER_DECISION_INVALID");
      requireCondition(typeof raw.accepted === "boolean", "WORKBENCH_ADAPTER_DECISION_INVALID");
      if (!raw.accepted) {
        return {
          accepted: false,
          reason: nonEmptyString(raw.reason, "WORKBENCH_REJECTION_REASON_REQUIRED"),
          allowedTargets: validateAllowedTargets(this._state, raw.allowedTargets),
        };
      }
      return {
        accepted: true,
        summary: typeof raw.summary === "string" ? raw.summary : "Accepted",
        patch: validatePatch(this._state, raw.patch, this._usedEntityIds, this._usedProjectionIds),
      };
    } catch (error) {
      const code = error instanceof WorkbenchError ? error.code : "WORKBENCH_ADAPTER_DECISION_INVALID";
      const reason = error instanceof Error ? error.message : String(error);
      return { accepted: false, reason, code, allowedTargets: [] };
    }
  }

  _commit(decision, request) {
    const before = clone(this._state);
    const next = clone(this._state);
    next.entities.push(...decision.patch.addEntities);
    next.projections.push(...decision.patch.addProjections);
    next.revision += 1;
    next.interaction.pickedEntityRef = null;
    next.interaction.preview = null;
    this._history.push(before);
    this._future = [];
    for (const entity of decision.patch.addEntities) this._usedEntityIds.add(entity.id);
    for (const projection of decision.patch.addProjections) this._usedProjectionIds.add(projection.id);
    this._state = next;
    return this._emit("TRANSFER_ACCEPTED", {
      request,
      summary: decision.summary,
      addedEntityRefs: decision.patch.addEntities.map((row) => row.id),
      addedProjectionRefs: decision.patch.addProjections.map((row) => row.id),
    });
  }

  dispatch(intentInput) {
    requireCondition(!this._dispatching, "WORKBENCH_REENTRANT_DISPATCH");
    this._dispatching = true;
    try {
      const intent = clone(intentInput || {});
    const type = nonEmptyString(intent.type, "WORKBENCH_INTENT_TYPE_REQUIRED");
    const channel = intent.channel || "unknown";

    if (type === "INSPECT") {
      requireCondition(this._entity(intent.entityRef), "WORKBENCH_ENTITY_UNKNOWN", String(intent.entityRef));
      let projectionRef = null;
      if (intent.projectionRef != null) {
        const projection = this._projection(intent.projectionRef);
        requireCondition(projection, "WORKBENCH_PROJECTION_UNKNOWN", String(intent.projectionRef));
        requireCondition(projection.entityRef === intent.entityRef,
          "WORKBENCH_PROJECTION_ENTITY_MISMATCH",
          `${intent.projectionRef} -> ${intent.entityRef}`);
        projectionRef = projection.id;
      }
      const linkedProjectionRefs = this._linkedProjectionRefs(intent.entityRef);
      this._state.interaction.inspectedEntityRef = intent.entityRef;
      this._state.interaction.inspectedProjectionRef = projectionRef;
      return this._emit("ENTITY_INSPECTED", {
        entityRef: intent.entityRef,
        projectionRef,
        linkedProjectionRefs,
        channel,
      });
    }

    if (type === "PICK") {
      requireCondition(this._entity(intent.entityRef), "WORKBENCH_ENTITY_UNKNOWN", String(intent.entityRef));
      this._state.interaction.pickedEntityRef = intent.entityRef;
      this._state.interaction.preview = null;
      return this._emit("ENTITY_PICKED", { entityRef: intent.entityRef, channel });
    }

    if (type === "PREVIEW_TARGET") {
      const request = this._request(intent.targetRef, channel);
      const decision = this._decision(request);
      this._state.interaction.preview = {
        targetRef: intent.targetRef,
        accepted: decision.accepted,
        reason: decision.reason || null,
      };
      return this._emit("TRANSFER_PREVIEW", {
        request,
        accepted: decision.accepted,
        reason: decision.reason || null,
        allowedTargets: decision.allowedTargets || [],
      });
    }

    if (type === "DROP") {
      const request = this._request(intent.targetRef, channel);
      const decision = this._decision(request);
      if (!decision.accepted) {
        this._state.interaction.preview = {
          targetRef: intent.targetRef,
          accepted: false,
          reason: decision.reason,
        };
        return this._emit("TRANSFER_REJECTED", {
          request,
          reason: decision.reason,
          code: decision.code || null,
          allowedTargets: decision.allowedTargets || [],
        });
      }
      return this._commit(decision, request);
    }

    if (type === "CANCEL") {
      this._state.interaction.pickedEntityRef = null;
      this._state.interaction.preview = null;
      return this._emit("INTERACTION_CANCELLED", { channel });
    }

    if (type === "UNDO") {
      requireCondition(this._history.length > 0, "WORKBENCH_NOTHING_TO_UNDO");
      const previous = this._history.pop();
      const current = clone(this._state);
      const nextRevision = this._state.revision + 1;
      this._future.push(current);
      this._state = previous;
      this._state.revision = nextRevision;
      this._state.interaction.pickedEntityRef = null;
      this._state.interaction.preview = null;
      return this._emit("UNDO_APPLIED", { channel });
    }

    if (type === "REDO") {
      requireCondition(this._future.length > 0, "WORKBENCH_NOTHING_TO_REDO");
      const next = this._future.pop();
      const current = clone(this._state);
      const nextRevision = this._state.revision + 1;
      this._history.push(current);
      this._state = next;
      this._state.revision = nextRevision;
      this._state.interaction.pickedEntityRef = null;
      this._state.interaction.preview = null;
      return this._emit("REDO_APPLIED", { channel });
    }

      throw new WorkbenchError("WORKBENCH_INTENT_UNSUPPORTED", type);
    } finally {
      this._dispatching = false;
    }
  }
}
