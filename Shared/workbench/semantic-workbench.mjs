import {
  WorkbenchRuntime,
  WorkbenchError,
  resolvePlacement,
} from "./runtime.mjs";

const TAG_NAME = "semantic-workbench";

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function placementStyle(scene, placement) {
  const resolved = resolvePlacement(scene, placement);
  return `grid-row:${resolved.row};grid-column:${resolved.column};`;
}

export class SemanticWorkbench extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._scene = null;
    this._adapter = null;
    this._injections = [];
    this._runtime = null;
    this._lastStatus = "Workbench not configured.";
    this._suppressNextClick = false;

    this.shadowRoot.addEventListener("pointerover", (event) => this._onPointerOver(event));
    this.shadowRoot.addEventListener("pointerdown", (event) => this._onPointerDown(event));
    this.shadowRoot.addEventListener("pointerup", (event) => this._onPointerUp(event));
    this.shadowRoot.addEventListener("focusin", (event) => this._onFocusIn(event));
    this.shadowRoot.addEventListener("click", (event) => this._onClick(event));
    this.shadowRoot.addEventListener("keydown", (event) => this._onKeyDown(event));
  }

  set scene(value) {
    this._scene = value;
    this._mountRuntime();
  }

  get scene() {
    return this._scene;
  }

  set adapter(value) {
    this._adapter = value;
    this._mountRuntime();
  }

  get adapter() {
    return this._adapter;
  }

  set injections(value) {
    this._injections = Array.isArray(value) ? value : [];
    this._mountRuntime();
  }

  get injections() {
    return [...this._injections];
  }

  get snapshot() {
    return this._runtime ? this._runtime.snapshot : null;
  }

  get textSummary() {
    return this._runtime ? this._summaryText(this._runtime.snapshot) : this._lastStatus;
  }

  connectedCallback() {
    this._render();
  }

  dispatchIntent(intent) {
    if (!this._runtime) throw new WorkbenchError("WORKBENCH_NOT_READY");
    const event = this._runtime.dispatch(intent);
    this._render();
    return event;
  }

  _dispatchWithoutRebuild(intent) {
    if (!this._runtime) throw new WorkbenchError("WORKBENCH_NOT_READY");
    const event = this._runtime.dispatch(intent);
    this._syncInteractionVisuals();
    return event;
  }

  _mountRuntime() {
    if (!this._scene || !this._adapter) {
      this._runtime = null;
      this._lastStatus = "Workbench requires scene data and an adapter.";
      this._render();
      return;
    }
    try {
      this._runtime = new WorkbenchRuntime(this._scene, this._adapter, {
        injections: this._injections,
        eventSink: (event) => this._onRuntimeEvent(event),
      });
      this._lastStatus = "Workbench ready.";
      this._render();
      this.dispatchEvent(new CustomEvent("semantic-workbench-event", {
        detail: { type: "WORKBENCH_READY", sceneId: this._scene.id, revision: 0 },
        bubbles: true,
        composed: true,
      }));
    } catch (error) {
      this._runtime = null;
      this._lastStatus = error instanceof Error ? error.message : String(error);
      this._render();
    }
  }

  _onRuntimeEvent(event) {
    if (event.type === "TRANSFER_REJECTED") this._lastStatus = `Rejected: ${event.reason}`;
    else if (event.type === "TRANSFER_ACCEPTED") this._lastStatus = event.summary || "Transfer accepted.";
    else if (event.type === "TRANSFER_PREVIEW") this._lastStatus = event.accepted ? "Target available." : `Target unavailable: ${event.reason}`;
    else if (event.type === "ENTITY_INSPECTED") this._lastStatus = event.linkedProjectionRefs?.length > 1
      ? `Inspecting ${event.linkedProjectionRefs.length} linked representations.`
      : "Inspecting representation.";
    else if (event.type === "ENTITY_PICKED") this._lastStatus = "Source selected. Choose a target.";
    else if (event.type === "INTERACTION_CANCELLED") this._lastStatus = "Selection cancelled.";
    else if (event.type === "UNDO_APPLIED") this._lastStatus = "Previous transformation restored.";
    else if (event.type === "REDO_APPLIED") this._lastStatus = "Undone transformation restored.";

    this.dispatchEvent(new CustomEvent("semantic-workbench-event", {
      detail: event,
      bubbles: true,
      composed: true,
    }));
  }

  _closestRole(event, role) {
    const target = event.target?.closest?.(`[data-role="${role}"]`);
    return target || null;
  }

  _onPointerOver(event) {
    const entity = this._closestRole(event, "entity");
    if (entity) this._dispatchWithoutRebuild({
      type: "INSPECT",
      entityRef: entity.dataset.entityRef,
      projectionRef: entity.dataset.projectionRef,
      channel: "pointer",
    });
    const target = this._closestRole(event, "target");
    if (target && this._runtime?.snapshot.interaction.pickedEntityRef) {
      this._dispatchWithoutRebuild({ type: "PREVIEW_TARGET", targetRef: target.dataset.targetRef, channel: "pointer" });
    }
  }

  _onPointerDown(event) {
    const entity = this._closestRole(event, "entity");
    if (!entity) return;
    this._suppressNextClick = true;
    this._dispatchWithoutRebuild({ type: "PICK", entityRef: entity.dataset.entityRef, channel: "pointer" });
  }

  _onPointerUp(event) {
    const target = this._closestRole(event, "target");
    if (!target || !this._runtime?.snapshot.interaction.pickedEntityRef) return;
    this._suppressNextClick = true;
    this.dispatchIntent({ type: "DROP", targetRef: target.dataset.targetRef, channel: "pointer" });
  }

  _onFocusIn(event) {
    const entity = this._closestRole(event, "entity");
    if (entity) this._dispatchWithoutRebuild({
      type: "INSPECT",
      entityRef: entity.dataset.entityRef,
      projectionRef: entity.dataset.projectionRef,
      channel: "keyboard",
    });
  }

  _onClick(event) {
    if (this._suppressNextClick) {
      this._suppressNextClick = false;
      return;
    }
    const action = event.target?.closest?.("[data-action]");
    if (action) {
      const type = action.dataset.action === "undo" ? "UNDO" : (action.dataset.action === "redo" ? "REDO" : "CANCEL");
      try { this.dispatchIntent({ type, channel: "click" }); } catch (_) { /* no-op when unavailable */ }
      return;
    }
    const entity = this._closestRole(event, "entity");
    if (entity) {
      this._dispatchWithoutRebuild({ type: "PICK", entityRef: entity.dataset.entityRef, channel: "click" });
      return;
    }
    const target = this._closestRole(event, "target");
    if (target && this._runtime?.snapshot.interaction.pickedEntityRef) {
      this.dispatchIntent({ type: "DROP", targetRef: target.dataset.targetRef, channel: "click" });
    }
  }

  _onKeyDown(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      this.dispatchIntent({ type: "CANCEL", channel: "keyboard" });
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
      event.preventDefault();
      const type = event.shiftKey ? "REDO" : "UNDO";
      try { this.dispatchIntent({ type, channel: "keyboard" }); } catch (_) { /* history action unavailable */ }
      return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "y") {
      event.preventDefault();
      try { this.dispatchIntent({ type: "REDO", channel: "keyboard" }); } catch (_) { /* nothing to redo */ }
      return;
    }
    if (event.key !== "Enter" && event.key !== " ") return;
    const entity = this._closestRole(event, "entity");
    if (entity) {
      event.preventDefault();
      this._dispatchWithoutRebuild({ type: "PICK", entityRef: entity.dataset.entityRef, channel: "keyboard" });
      return;
    }
    const target = this._closestRole(event, "target");
    if (target && this._runtime?.snapshot.interaction.pickedEntityRef) {
      event.preventDefault();
      this.dispatchIntent({ type: "DROP", targetRef: target.dataset.targetRef, channel: "keyboard" });
    }
  }

  _focusToken() {
    const active = this.shadowRoot?.activeElement;
    if (!active) return null;
    if (active.dataset.role === "entity") return { kind: "entity", ref: active.dataset.projectionRef };
    if (active.dataset.role === "target") return { kind: "target", ref: active.dataset.targetRef };
    if (active.dataset.action) return { kind: "action", ref: active.dataset.action };
    return null;
  }

  _restoreFocus(token) {
    if (!token || !this.shadowRoot) return;
    const candidates = [...this.shadowRoot.querySelectorAll("button")];
    const next = candidates.find((button) => {
      if (token.kind === "entity") return button.dataset.role === "entity" && button.dataset.projectionRef === token.ref;
      if (token.kind === "target") return button.dataset.role === "target" && button.dataset.targetRef === token.ref;
      return token.kind === "action" && button.dataset.action === token.ref;
    });
    next?.focus({ preventScroll: true });
  }

  _summaryText(state) {
    const entity = (ref) => state.entities.find((row) => row.id === ref);
    const projection = (ref) => state.projections.find((row) => row.id === ref);
    const target = (ref) => state.targets.find((row) => row.id === ref);
    const label = (row, fallback) => row?.label || fallback;

    let inspectedText = "Nothing inspected.";
    if (state.interaction.inspectedProjectionRef) {
      inspectedText = `Inspecting ${label(projection(state.interaction.inspectedProjectionRef), state.interaction.inspectedProjectionRef)}.`;
    } else if (state.interaction.inspectedEntityRef) {
      inspectedText = `Inspecting ${label(entity(state.interaction.inspectedEntityRef), state.interaction.inspectedEntityRef)}.`;
    }

    const selectedText = state.interaction.pickedEntityRef
      ? `Selected source ${label(entity(state.interaction.pickedEntityRef), state.interaction.pickedEntityRef)}.`
      : "No source selected.";

    let previewText = "No target preview.";
    if (state.interaction.preview) {
      const preview = state.interaction.preview;
      const targetLabel = label(target(preview.targetRef), preview.targetRef);
      const availability = preview.accepted ? "available" : "unavailable";
      const reason = preview.reason ? ` Reason: ${preview.reason}.` : "";
      previewText = `Target ${targetLabel}: ${availability}.${reason}`;
    }

    const representations = state.projections.length
      ? state.projections.map((row) => {
          const kind = row.representation ? ` [${row.representation}]` : "";
          return `${label(row, row.id)}${kind}`;
        }).join("; ")
      : "none";

    return `Scene ${state.sceneId}. Revision ${state.revision}. ${inspectedText} ${selectedText} ${previewText} Representations: ${representations}.`;
  }

  _syncInteractionVisuals() {
    if (!this._runtime || !this.shadowRoot) return;
    const state = this._runtime.snapshot;
    const picked = state.interaction.pickedEntityRef;
    const inspected = state.interaction.inspectedEntityRef;
    const inspectedProjection = state.interaction.inspectedProjectionRef;
    for (const button of this.shadowRoot.querySelectorAll('[data-role="entity"]')) {
      const selected = button.dataset.entityRef === picked;
      const origin = Boolean(inspectedProjection) && button.dataset.projectionRef === inspectedProjection;
      const linked = button.dataset.entityRef === inspected && !origin;
      const active = selected || origin || linked;
      const correspondenceState = origin ? "origin" : (linked ? "linked" : (selected ? "selected" : "none"));
      button.classList.toggle("active", active);
      button.dataset.correspondenceState = correspondenceState;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
      const label = button.querySelector(".entity-state");
      if (label) label.textContent = origin ? "Inspected representation" : (linked ? "Linked representation" : (selected ? "Selected representation" : "Representation"));
    }
    for (const button of this.shadowRoot.querySelectorAll('[data-role="target"]')) {
      const isPreview = state.interaction.preview?.targetRef === button.dataset.targetRef;
      const accepted = isPreview && state.interaction.preview?.accepted === true;
      button.classList.toggle("valid", accepted);
      button.classList.toggle("invalid", isPreview && !accepted);
      const label = button.querySelector("small");
      if (label) label.textContent = isPreview ? (accepted ? "Available" : "Unavailable") : "Target";
    }
    const status = this.shadowRoot.querySelector(".status");
    if (status) status.textContent = this._lastStatus;
    const summary = this.shadowRoot.querySelector(".text-summary p");
    if (summary) summary.textContent = this._summaryText(state);
  }

  _renderGrid(grid, state) {
    const projections = state.projections
      .filter((row) => row.placement.grid === grid.id)
      .map((row) => ({ ...row, role: "entity" }));
    const targets = state.targets
      .filter((row) => row.placement.grid === grid.id)
      .map((row) => ({ ...row, role: "target" }));
    const rows = [...projections, ...targets].sort((a, b) => {
      const pa = resolvePlacement(this._scene, a.placement);
      const pb = resolvePlacement(this._scene, b.placement);
      return pa.row - pb.row || pa.column - pb.column || a.id.localeCompare(b.id);
    });

    const picked = state.interaction.pickedEntityRef;
    const inspected = state.interaction.inspectedEntityRef;
    const inspectedProjection = state.interaction.inspectedProjectionRef;
    const preview = state.interaction.preview;
    const content = rows.map((row) => {
      const style = placementStyle(this._scene, row.placement);
      if (row.role === "entity") {
        const selected = row.entityRef === picked;
        const origin = Boolean(inspectedProjection) && row.id === inspectedProjection;
        const linked = row.entityRef === inspected && !origin;
        const active = selected || origin || linked;
        const correspondenceState = origin ? "origin" : (linked ? "linked" : (selected ? "selected" : "none"));
        const stateLabel = origin ? "Inspected representation" : (linked ? "Linked representation" : (selected ? "Selected representation" : "Representation"));
        return `<button class="slot entity${active ? " active" : ""}" style="${style}" data-role="entity" data-entity-ref="${escapeHtml(row.entityRef)}" data-projection-ref="${escapeHtml(row.id)}" data-correspondence-state="${correspondenceState}" aria-pressed="${selected ? "true" : "false"}"><span>${escapeHtml(row.label)}</span><small class="entity-state">${stateLabel}</small></button>`;
      }
      const isPreview = preview?.targetRef === row.id;
      const stateLabel = isPreview ? (preview.accepted ? "Available" : "Unavailable") : "Target";
      return `<button class="slot target${isPreview ? (preview.accepted ? " valid" : " invalid") : ""}" style="${style}" data-role="target" data-target-ref="${escapeHtml(row.id)}"><span>${escapeHtml(row.label)}</span><small>${stateLabel}</small></button>`;
    }).join("");

    return `<section class="grid-shell"><h3>${escapeHtml(grid.label || grid.id)}</h3><div class="logical-grid" style="--column-count:${grid.columns.length}">${content}</div></section>`;
  }

  _render() {
    if (!this.shadowRoot) return;
    const focusToken = this._focusToken();
    if (!this._runtime) {
      this.shadowRoot.innerHTML = `<style>:host{display:block;font:inherit}.diagnostic{border:1px solid currentColor;padding:.75rem;border-radius:.5rem}</style><div class="diagnostic" role="status">${escapeHtml(this._lastStatus)}</div>`;
      this._restoreFocus(focusToken);
      return;
    }

    const state = this._runtime.snapshot;
    const checkpoints = this._runtime.injections.map((row) => `<aside class="checkpoint"><strong>${escapeHtml(row.kind)}</strong><span>${escapeHtml(row.prompt)}</span></aside>`).join("");
    const grids = state.grids.map((grid) => this._renderGrid(grid, state)).join("");
    const textSummary = this._summaryText(state);

    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;container-type:inline-size;font:inherit;color:var(--workbench-fg,inherit)}
        .frame{border:1px solid var(--workbench-border,#94a3b8);border-radius:.75rem;padding:1rem;background:var(--workbench-bg,#fff)}
        .toolbar{display:flex;gap:.5rem;justify-content:flex-end;margin-bottom:.75rem}
        button{font:inherit}
        .logical-grid{display:grid;grid-template-columns:repeat(var(--column-count),minmax(0,1fr));gap:.6rem;align-items:stretch}
        .slot{min-width:0;min-height:2.75rem;border:1px solid var(--workbench-border,#94a3b8);border-radius:.5rem;padding:.65rem;background:var(--workbench-surface,#f8fafc);color:inherit;text-align:left;touch-action:manipulation}
        .entity{display:flex;flex-direction:column;gap:.15rem}.entity small{font-size:.75em}
        .entity.active{outline:3px solid var(--workbench-focus,#2563eb);outline-offset:2px}
        .target{display:flex;flex-direction:column;gap:.15rem}.target small{font-size:.75em}.target.valid{border-style:double}.target.invalid{border-style:dashed}
        .checkpoint{display:flex;gap:.5rem;align-items:flex-start;margin:.75rem 0;padding:.65rem;border-left:4px solid var(--workbench-checkpoint,#64748b);background:var(--workbench-surface,#f8fafc)}
        .text-summary{margin-top:1rem;padding-top:.75rem;border-top:1px solid var(--workbench-border,#94a3b8)}
        .text-summary h3{margin:.1rem 0 .35rem;font-size:1em}.text-summary p{margin:0}
        .status{margin-top:.75rem;min-height:1.5em}
        @container (max-width:34rem){.logical-grid{grid-template-columns:1fr}.slot{grid-column:1!important;grid-row:auto!important}}
        @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
      </style>
      <section class="frame" aria-label="Semantic transformation workbench">
        <div class="toolbar"><button data-action="undo"${this._runtime.canUndo ? "" : " disabled"}>Undo</button><button data-action="redo"${this._runtime.canRedo ? "" : " disabled"}>Redo</button><button data-action="cancel">Cancel</button></div>
        ${checkpoints}
        ${grids}
        <section class="text-summary" aria-label="Workbench text state"><h3>Text state</h3><p>${escapeHtml(textSummary)}</p></section>
        <div class="status" role="status" aria-live="polite">${escapeHtml(this._lastStatus)}</div>
      </section>`;
    this._restoreFocus(focusToken);
  }
}

if (typeof customElements !== "undefined" && !customElements.get(TAG_NAME)) {
  customElements.define(TAG_NAME, SemanticWorkbench);
}
