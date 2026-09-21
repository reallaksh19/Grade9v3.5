import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import {
  WORKBENCH_API_VERSION,
  WorkbenchRuntime,
  WorkbenchError,
  resolvePlacement,
  validateScene,
} from "../Shared/workbench/runtime.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const fixturePath = resolve(here, "fixtures/workbench/arithmetic-division.json");
const fixture = JSON.parse(await readFile(fixturePath, "utf8"));
const identityFixturePath = resolve(here, "fixtures/workbench/arithmetic-division-semantic-identity.json");
const identityFixture = JSON.parse(await readFile(identityFixturePath, "utf8"));

function divisionAdapter() {
  return {
    evaluateTransfer(request, snapshot) {
      if (request.sourceEntityRef !== "dividend-156" || request.targetRef !== "quotient-first-digit") {
        return { accepted: false, reason: "Choose the partial dividend before deriving this result.", allowedTargets: ["quotient-first-digit"] };
      }
      assert.equal(snapshot.sceneId, fixture.id);
      return {
        accepted: true,
        summary: "The first quotient digit is 1 because 12 fits into 15 once.",
        patch: {
          addEntities: [{
            id: "quotient-digit-1",
            label: "1",
            provenance: { kind: "DERIVED", sourceEntityRefs: ["dividend-156", "divisor-12"] }
          }],
          addProjections: [{
            id: "quotient-digit-1-result",
            entityRef: "quotient-digit-1",
            label: "1",
            representation: "quotient digit",
            placement: { grid: "division-work", row: "result", column: "main" }
          }]
        }
      };
    }
  };
}

function identityLifecycleAdapter(onCall = () => {}) {
  return {
    evaluateTransfer(request, snapshot) {
      onCall(request, snapshot);
      assert.equal(snapshot.sceneId, identityFixture.id);

      if (request.sourceEntityRef === "dividend-156" && request.targetRef === "partial-dividend-first") {
        return {
          accepted: true,
          summary: "The first partial dividend is 15.",
          patch: {
            addEntities: [{
              id: "partial-dividend-15",
              label: "15",
              provenance: { kind: "DERIVED", sourceEntityRefs: ["dividend-156"] }
            }],
            addProjections: [{
              id: "partial-dividend-working",
              entityRef: "partial-dividend-15",
              label: "15",
              representation: "partial dividend",
              placement: { grid: "division-work", row: "working", column: "right" }
            }]
          }
        };
      }

      if (request.sourceEntityRef === "partial-dividend-15" && request.targetRef === "quotient-first-digit") {
        return {
          accepted: true,
          summary: "The first quotient digit is 1 because 12 fits into 15 once.",
          patch: {
            addEntities: [{
              id: "quotient-digit-1",
              label: "1",
              provenance: { kind: "DERIVED", sourceEntityRefs: ["partial-dividend-15", "divisor-12"] }
            }],
            addProjections: [{
              id: "quotient-digit-1-result",
              entityRef: "quotient-digit-1",
              label: "1",
              representation: "quotient digit",
              placement: { grid: "division-work", row: "result", column: "main" }
            }]
          }
        };
      }

      return {
        accepted: false,
        reason: "Use the current semantic intermediate for this target.",
        allowedTargets: snapshot.entities.some((row) => row.id === "partial-dividend-15")
          ? ["quotient-first-digit"]
          : ["partial-dividend-first"]
      };
    }
  };
}

function finalStateFor(channel) {
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter());
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel });
  runtime.dispatch({ type: "PREVIEW_TARGET", targetRef: "quotient-first-digit", channel });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel });
  return runtime.snapshot;
}

test("one semantic entity may have multiple projections and derivation preserves provenance", () => {
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter());
  const sourceProjections = runtime.snapshot.projections.filter((row) => row.entityRef === "dividend-156");
  assert.equal(sourceProjections.length, 2);

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const event = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(event.type, "TRANSFER_ACCEPTED");
  const derived = runtime.snapshot.entities.find((row) => row.id === "quotient-digit-1");
  assert.deepEqual(derived.provenance.sourceEntityRefs, ["dividend-156", "divisor-12"]);
  assert.notEqual(derived.id, "dividend-156");
});

test("partial dividend is a distinct semantic entity with reversible provenance lifecycle", () => {
  let adapterCalls = 0;
  const runtime = new WorkbenchRuntime(identityFixture, identityLifecycleAdapter(() => { adapterCalls += 1; }));

  const originalDividend = runtime.snapshot.entities.find((row) => row.id === "dividend-156");
  assert.ok(originalDividend);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "partial-dividend-15"), false);
  assert.equal(runtime.snapshot.projections.filter((row) => row.entityRef === "dividend-156").length, 2);
  assert.equal(runtime.snapshot.projections.some((row) => row.entityRef === "dividend-156" && row.label === "15"), false);

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const partialEvent = runtime.dispatch({ type: "DROP", targetRef: "partial-dividend-first", channel: "click" });
  assert.equal(partialEvent.type, "TRANSFER_ACCEPTED");

  const partial = runtime.snapshot.entities.find((row) => row.id === "partial-dividend-15");
  assert.ok(partial);
  assert.notEqual(partial.id, originalDividend.id);
  assert.deepEqual(partial.provenance.sourceEntityRefs, ["dividend-156"]);
  const partialProjection = runtime.snapshot.projections.find((row) => row.id === "partial-dividend-working");
  assert.equal(partialProjection.entityRef, "partial-dividend-15");

  const inspection = runtime.dispatch({
    type: "INSPECT",
    entityRef: "partial-dividend-15",
    projectionRef: "partial-dividend-working",
    channel: "keyboard",
  });
  assert.deepEqual(inspection.linkedProjectionRefs, ["partial-dividend-working"]);

  runtime.dispatch({ type: "PICK", entityRef: "partial-dividend-15", channel: "keyboard" });
  const quotientEvent = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "keyboard" });
  assert.equal(quotientEvent.type, "TRANSFER_ACCEPTED");
  const quotient = runtime.snapshot.entities.find((row) => row.id === "quotient-digit-1");
  assert.deepEqual(quotient.provenance.sourceEntityRefs, ["partial-dividend-15", "divisor-12"]);
  assert.equal(adapterCalls, 2);

  runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), false);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "partial-dividend-15"), true);

  runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "partial-dividend-15"), false);
  assert.equal(runtime.snapshot.projections.some((row) => row.id === "partial-dividend-working"), false);

  runtime.dispatch({ type: "REDO", channel: "keyboard" });
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "partial-dividend-15"), true);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), false);

  runtime.dispatch({ type: "REDO", channel: "keyboard" });
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), true);
  assert.equal(adapterCalls, 2);
  assert.equal(runtime.snapshot.revision, 6);
});

test("inspection exposes projection origin and linked representations", () => {
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter());
  const event = runtime.dispatch({
    type: "INSPECT",
    entityRef: "dividend-156",
    projectionRef: "dividend-expression",
    channel: "keyboard",
  });

  assert.equal(event.type, "ENTITY_INSPECTED");
  assert.equal(event.entityRef, "dividend-156");
  assert.equal(event.projectionRef, "dividend-expression");
  assert.deepEqual(event.linkedProjectionRefs, ["dividend-expression", "dividend-place-value"]);
  assert.equal(runtime.snapshot.interaction.inspectedProjectionRef, "dividend-expression");
  assert.doesNotThrow(() => JSON.stringify(event));

  assert.throws(
    () => runtime.dispatch({
      type: "INSPECT",
      entityRef: "dividend-156",
      projectionRef: "divisor-expression",
      channel: "keyboard",
    }),
    (error) => error instanceof WorkbenchError && error.code === "WORKBENCH_PROJECTION_ENTITY_MISMATCH"
  );
});

test("pointer, click, and keyboard intents commit through the same semantic path", () => {
  const pointer = finalStateFor("pointer");
  const click = finalStateFor("click");
  const keyboard = finalStateFor("keyboard");
  assert.deepEqual(pointer, click);
  assert.deepEqual(click, keyboard);
});

test("domain adapter request is input-neutral while transfer events retain channel", () => {
  const requests = [];

  for (const channel of ["pointer", "click", "keyboard", "touch"]) {
    const baseAdapter = divisionAdapter();
    const adapter = {
      evaluateTransfer(request, snapshot) {
        requests.push(structuredClone(request));
        assert.equal("channel" in request, false);
        return baseAdapter.evaluateTransfer(request, snapshot);
      }
    };

    const runtime = new WorkbenchRuntime(fixture, adapter);
    runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel });
    const event = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel });

    assert.equal(event.type, "TRANSFER_ACCEPTED");
    assert.equal(event.request.channel, channel);
  }

  const expected = {
    sourceEntityRef: "dividend-156",
    targetRef: "quotient-first-digit",
    operation: "derive-first-quotient-digit",
  };
  requests.forEach((request) => assert.deepEqual(request, expected));
});

test("invalid domain action is rejected without mutation", () => {
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter());
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
  const before = runtime.snapshot;
  const event = runtime.dispatch({ type: "DROP", targetRef: "remainder-final", channel: "keyboard" });
  assert.equal(event.type, "TRANSFER_REJECTED");
  const after = runtime.snapshot;
  assert.deepEqual(after.entities, before.entities);
  assert.deepEqual(after.projections, before.projections);
  assert.equal(after.revision, before.revision);
});

test("rejection target guidance must reference unique existing targets", () => {
  const validAdapter = {
    evaluateTransfer() {
      return {
        accepted: false,
        reason: "Use the first quotient target.",
        allowedTargets: ["quotient-first-digit"],
      };
    }
  };
  const validRuntime = new WorkbenchRuntime(fixture, validAdapter);
  validRuntime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
  const validEvent = validRuntime.dispatch({ type: "DROP", targetRef: "remainder-final", channel: "keyboard" });
  assert.equal(validEvent.type, "TRANSFER_REJECTED");
  assert.deepEqual(validEvent.allowedTargets, ["quotient-first-digit"]);

  for (const [allowedTargets, expectedCode] of [
    [["missing-target"], "WORKBENCH_ALLOWED_TARGET_UNKNOWN"],
    [["quotient-first-digit", "quotient-first-digit"], "WORKBENCH_ALLOWED_TARGETS_INVALID"],
    ["quotient-first-digit", "WORKBENCH_ALLOWED_TARGETS_INVALID"],
  ]) {
    const runtime = new WorkbenchRuntime(fixture, {
      evaluateTransfer() {
        return { accepted: false, reason: "Rejected.", allowedTargets };
      }
    });
    runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
    const before = runtime.snapshot;
    const event = runtime.dispatch({ type: "DROP", targetRef: "remainder-final", channel: "keyboard" });
    assert.equal(event.type, "TRANSFER_REJECTED");
    assert.equal(event.code, expectedCode);
    assert.deepEqual(event.allowedTargets, []);
    assert.deepEqual(runtime.snapshot.entities, before.entities);
    assert.deepEqual(runtime.snapshot.projections, before.projections);
    assert.equal(runtime.snapshot.revision, before.revision);
  }
});

test("canonical transformation refs validate current targets without forbidding deferred sources", () => {
  assert.doesNotThrow(() => validateScene(identityFixture));

  const unknownTarget = structuredClone(fixture);
  unknownTarget.canonicalTransformations[0].targetRef = "missing-target";
  assert.throws(
    () => validateScene(unknownTarget),
    (error) => error instanceof WorkbenchError
      && error.code === "WORKBENCH_TRANSFORMATION_TARGET_UNKNOWN"
      && error.detail === "choose-first-quotient-digit -> missing-target"
  );

  const malformedSources = structuredClone(fixture);
  malformedSources.canonicalTransformations[0].sourceEntityRefs = "dividend-156";
  assert.throws(
    () => validateScene(malformedSources),
    (error) => error instanceof WorkbenchError
      && error.code === "WORKBENCH_TRANSFORMATION_SOURCES_INVALID"
  );

  const duplicateSources = structuredClone(fixture);
  duplicateSources.canonicalTransformations[0].sourceEntityRefs = ["dividend-156", "dividend-156"];
  assert.throws(
    () => validateScene(duplicateSources),
    (error) => error instanceof WorkbenchError
      && error.code === "WORKBENCH_TRANSFORMATION_SOURCES_INVALID"
  );
});

test("accepted empty patch fails closed without creating a semantic revision", () => {
  let adapterCalls = 0;
  const baseAdapter = divisionAdapter();
  const adapter = {
    evaluateTransfer(request, snapshot) {
      adapterCalls += 1;
      if (adapterCalls === 1) return baseAdapter.evaluateTransfer(request, snapshot);
      return { accepted: true, summary: "Accepted without a semantic delta", patch: {} };
    }
  };
  const runtime = new WorkbenchRuntime(fixture, adapter);

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(runtime.snapshot.revision, 2);
  assert.equal(runtime.canUndo, false);
  assert.equal(runtime.canRedo, true);

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
  const before = runtime.snapshot;
  const event = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "keyboard" });

  assert.equal(event.type, "TRANSFER_REJECTED");
  assert.equal(event.code, "WORKBENCH_PATCH_EMPTY");
  assert.deepEqual(runtime.snapshot.entities, before.entities);
  assert.deepEqual(runtime.snapshot.projections, before.projections);
  assert.equal(runtime.snapshot.revision, before.revision);
  assert.equal(runtime.canUndo, false);
  assert.equal(runtime.canRedo, true);

  const redo = runtime.dispatch({ type: "REDO", channel: "keyboard" });
  assert.equal(redo.type, "REDO_APPLIED");
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), true);
  assert.equal(runtime.snapshot.revision, 3);
  assert.equal(adapterCalls, 2);
});

test("undo restores the exact prior semantic state", () => {
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter());
  const initial = runtime.snapshot;
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  const undo = runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(undo.type, "UNDO_APPLIED");
  const restored = runtime.snapshot;
  assert.deepEqual(restored.entities, initial.entities);
  assert.deepEqual(restored.projections, initial.projections);
  assert.deepEqual(restored.canonicalTransformations, initial.canonicalTransformations);
  assert.equal(restored.interaction.pickedEntityRef, null);
});

test("redo restores an accepted semantic state without replaying adapter validity", () => {
  let adapterCalls = 0;
  const baseAdapter = divisionAdapter();
  const adapter = {
    evaluateTransfer(request, snapshot) {
      adapterCalls += 1;
      return baseAdapter.evaluateTransfer(request, snapshot);
    }
  };
  const runtime = new WorkbenchRuntime(fixture, adapter);
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  const committed = runtime.snapshot;
  assert.equal(adapterCalls, 1);
  assert.equal(committed.revision, 1);

  runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
  runtime.dispatch({ type: "CANCEL", channel: "keyboard" });
  const redo = runtime.dispatch({ type: "REDO", channel: "keyboard" });

  assert.equal(redo.type, "REDO_APPLIED");
  assert.equal(adapterCalls, 1);
  const restored = runtime.snapshot;
  assert.deepEqual(restored.entities, committed.entities);
  assert.deepEqual(restored.projections, committed.projections);
  assert.deepEqual(restored.canonicalTransformations, committed.canonicalTransformations);
  assert.equal(restored.revision, 3);
  assert.equal(restored.interaction.pickedEntityRef, null);
});

test("a new accepted commit after undo invalidates the redo branch", () => {
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter());
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  runtime.dispatch({ type: "UNDO", channel: "keyboard" });

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });

  assert.throws(
    () => runtime.dispatch({ type: "REDO", channel: "keyboard" }),
    (error) => error instanceof WorkbenchError && error.code === "WORKBENCH_NOTHING_TO_REDO"
  );
});

test("initial scene provenance source refs must resolve to scene entities", () => {
  const valid = structuredClone(fixture);
  valid.entities.push({
    id: "initial-derived",
    label: "Derived",
    provenance: { kind: "DERIVED", sourceEntityRefs: ["dividend-156"] }
  });
  assert.doesNotThrow(() => validateScene(valid));

  const dangling = structuredClone(fixture);
  dangling.entities.push({
    id: "initial-orphan",
    label: "Orphan",
    provenance: { kind: "DERIVED", sourceEntityRefs: ["missing-source"] }
  });
  assert.throws(
    () => validateScene(dangling),
    (error) => error instanceof WorkbenchError
      && error.code === "WORKBENCH_PROVENANCE_SOURCE_UNKNOWN"
      && error.detail === "initial-orphan -> missing-source"
  );
});

test("initial scene provenance must be acyclic while valid DAGs remain order-independent", () => {
  const forwardDag = structuredClone(fixture);
  forwardDag.entities.push(
    {
      id: "derived-first-declared",
      label: "Derived first",
      provenance: { kind: "DERIVED", sourceEntityRefs: ["derived-later-declared"] }
    },
    {
      id: "derived-later-declared",
      label: "Derived later",
      provenance: { kind: "DERIVED", sourceEntityRefs: ["dividend-156"] }
    }
  );
  assert.doesNotThrow(() => validateScene(forwardDag));

  const selfCycle = structuredClone(fixture);
  selfCycle.entities.push({
    id: "self-cycle",
    label: "Self cycle",
    provenance: { kind: "DERIVED", sourceEntityRefs: ["self-cycle"] }
  });
  assert.throws(
    () => validateScene(selfCycle),
    (error) => error instanceof WorkbenchError
      && error.code === "WORKBENCH_PROVENANCE_CYCLE"
      && error.detail === "self-cycle -> self-cycle"
  );

  const twoNodeCycle = structuredClone(fixture);
  twoNodeCycle.entities.push(
    {
      id: "cycle-a",
      label: "Cycle A",
      provenance: { kind: "DERIVED", sourceEntityRefs: ["cycle-b"] }
    },
    {
      id: "cycle-b",
      label: "Cycle B",
      provenance: { kind: "DERIVED", sourceEntityRefs: ["cycle-a"] }
    }
  );
  assert.throws(
    () => validateScene(twoNodeCycle),
    (error) => error instanceof WorkbenchError
      && error.code === "WORKBENCH_PROVENANCE_CYCLE"
      && error.detail === "cycle-a -> cycle-b -> cycle-a"
  );
});

test("provenance metadata fails closed when structurally malformed", () => {
  for (const provenance of [
    "not-an-object",
    [],
    { kind: "" },
    { sourceEntityRefs: "dividend-156" },
    { sourceEntityRefs: ["dividend-156", "dividend-156"] },
    { sourceEntityRefs: [42] },
  ]) {
    const badScene = structuredClone(fixture);
    badScene.entities[0].provenance = provenance;
    assert.throws(
      () => validateScene(badScene),
      (error) => error instanceof WorkbenchError
        && error.code === "WORKBENCH_PROVENANCE_INVALID"
    );
  }

  const runtime = new WorkbenchRuntime(fixture, {
    evaluateTransfer() {
      return {
        accepted: true,
        patch: {
          addEntities: [{
            id: "malformed-provenance",
            label: "Malformed provenance",
            provenance: { sourceEntityRefs: ["dividend-156", "dividend-156"] }
          }],
          addProjections: []
        }
      };
    }
  });
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const before = runtime.snapshot;
  const event = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(event.type, "TRANSFER_REJECTED");
  assert.equal(event.code, "WORKBENCH_PROVENANCE_INVALID");
  assert.deepEqual(runtime.snapshot.entities, before.entities);
  assert.equal(runtime.snapshot.revision, before.revision);
});

test("adapter exceptions cannot impersonate Core validation failures", () => {
  const spoofingAdapter = {
    evaluateTransfer() {
      throw new WorkbenchError("WORKBENCH_PATCH_EMPTY", "adapter-spoofed-code");
    }
  };
  const spoofedRuntime = new WorkbenchRuntime(fixture, spoofingAdapter);
  spoofedRuntime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const spoofed = spoofedRuntime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(spoofed.type, "TRANSFER_REJECTED");
  assert.equal(spoofed.code, "WORKBENCH_ADAPTER_FAILURE");
  assert.match(spoofed.reason, /adapter-spoofed-code/);

  const malformedDecisionRuntime = new WorkbenchRuntime(fixture, {
    evaluateTransfer() {
      return { accepted: true, patch: {} };
    }
  });
  malformedDecisionRuntime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const coreRejected = malformedDecisionRuntime.dispatch({
    type: "DROP",
    targetRef: "quotient-first-digit",
    channel: "click",
  });
  assert.equal(coreRejected.type, "TRANSFER_REJECTED");
  assert.equal(coreRejected.code, "WORKBENCH_PATCH_EMPTY");
});

test("named logical placement resolves without authored pixel coordinates", () => {
  const placement = fixture.projections[0].placement;
  assert.deepEqual(resolvePlacement(fixture, placement), { grid: "division-expression", row: 1, column: 1 });
  const bad = structuredClone(fixture);
  bad.projections[0].placement.x = 120;
  assert.throws(() => validateScene(bad), (error) => error instanceof WorkbenchError && error.code === "WORKBENCH_PIXEL_COORDINATE_FORBIDDEN");
});

test("checkpoint injections remain outside canonical transformations", () => {
  const injections = [{
    id: "estimate-checkpoint",
    kind: "checkpoint",
    afterTransformationRef: "choose-first-quotient-digit",
    prompt: "How many 12s fit into 15 without passing it?"
  }];
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter(), { injections });
  assert.deepEqual(runtime.canonicalTransformations, fixture.canonicalTransformations);
  assert.equal(runtime.injections[0].prompt, injections[0].prompt);
  assert.equal("placement" in runtime.injections[0], false);
});

test("observer mutation and exceptions cannot alter semantic dispatch", () => {
  const observed = [];
  const runtime = new WorkbenchRuntime(fixture, divisionAdapter(), {
    eventSink(event) {
      observed.push(structuredClone(event));
      event.type = "HOST_MUTATED_EVENT";
      event.revision = 999;
      throw new Error("host observer failure");
    }
  });

  const picked = runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  assert.equal(picked.type, "ENTITY_PICKED");
  assert.equal(picked.revision, 0);

  const accepted = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(accepted.type, "TRANSFER_ACCEPTED");
  assert.equal(accepted.revision, 1);
  assert.equal(runtime.snapshot.revision, 1);
  assert.equal(runtime.canUndo, true);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), true);

  const undo = runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(undo.type, "UNDO_APPLIED");
  assert.equal(undo.revision, 2);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), false);
  assert.deepEqual(observed.map((event) => event.type), ["ENTITY_PICKED", "TRANSFER_ACCEPTED", "UNDO_APPLIED"]);
});

test("synchronous callbacks cannot reenter semantic dispatch", () => {
  const nestedErrors = [];
  let runtime;
  runtime = new WorkbenchRuntime(fixture, divisionAdapter(), {
    eventSink(event) {
      if (event.type !== "TRANSFER_ACCEPTED") return;
      try {
        runtime.dispatch({ type: "UNDO", channel: "observer" });
      } catch (error) {
        nestedErrors.push(error);
      }
    }
  });

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const accepted = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });

  assert.equal(accepted.type, "TRANSFER_ACCEPTED");
  assert.equal(accepted.revision, 1);
  assert.equal(nestedErrors.length, 1);
  assert.equal(nestedErrors[0] instanceof WorkbenchError, true);
  assert.equal(nestedErrors[0].code, "WORKBENCH_REENTRANT_DISPATCH");
  assert.equal(runtime.snapshot.revision, 1);
  assert.equal(runtime.canUndo, true);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), true);

  const undo = runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(undo.type, "UNDO_APPLIED");
  assert.equal(undo.revision, 2);
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "quotient-digit-1"), false);
});

test("undo branches cannot reassign committed entity or projection IDs", () => {
  let phase = 0;
  const baseAdapter = divisionAdapter();
  const entityReuseAdapter = {
    evaluateTransfer(request, snapshot) {
      phase += 1;
      if (phase === 1) return baseAdapter.evaluateTransfer(request, snapshot);
      return {
        accepted: true,
        summary: "Attempt to rebind abandoned semantic identity.",
        patch: {
          addEntities: [{
            id: "quotient-digit-1",
            label: "Different semantic object",
            provenance: { kind: "DERIVED", sourceEntityRefs: ["divisor-12"] }
          }],
          addProjections: [{
            id: "different-result-view",
            entityRef: "quotient-digit-1",
            label: "Different result",
            representation: "different result",
            placement: { grid: "division-work", row: "result", column: "right" }
          }]
        }
      };
    }
  };

  const runtime = new WorkbenchRuntime(fixture, entityReuseAdapter);
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  runtime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(runtime.canRedo, true);

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
  const beforeReuse = runtime.snapshot;
  const reuse = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "keyboard" });
  assert.equal(reuse.type, "TRANSFER_REJECTED");
  assert.equal(reuse.code, "WORKBENCH_ENTITY_ID_REUSED");
  assert.deepEqual(runtime.snapshot.entities, beforeReuse.entities);
  assert.deepEqual(runtime.snapshot.projections, beforeReuse.projections);
  assert.equal(runtime.snapshot.revision, beforeReuse.revision);
  assert.equal(runtime.canRedo, true);

  const redo = runtime.dispatch({ type: "REDO", channel: "keyboard" });
  assert.equal(redo.type, "REDO_APPLIED");
  assert.equal(runtime.snapshot.entities.find((row) => row.id === "quotient-digit-1").label, "1");

  let projectionPhase = 0;
  const projectionRuntime = new WorkbenchRuntime(fixture, {
    evaluateTransfer() {
      projectionPhase += 1;
      return {
        accepted: true,
        summary: projectionPhase === 1 ? "Add temporary representation." : "Rebind representation ID.",
        patch: {
          addEntities: [],
          addProjections: [{
            id: "temporary-dividend-view",
            entityRef: "dividend-156",
            label: projectionPhase === 1 ? "156 temporary" : "156 rebound",
            representation: projectionPhase === 1 ? "temporary" : "rebound",
            placement: { grid: "division-work", row: "result", column: "left" }
          }]
        }
      };
    }
  });
  projectionRuntime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  projectionRuntime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  projectionRuntime.dispatch({ type: "UNDO", channel: "keyboard" });
  assert.equal(projectionRuntime.canRedo, true);

  projectionRuntime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "keyboard" });
  const projectionReuse = projectionRuntime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "keyboard" });
  assert.equal(projectionReuse.type, "TRANSFER_REJECTED");
  assert.equal(projectionReuse.code, "WORKBENCH_PROJECTION_ID_REUSED");
  assert.equal(projectionRuntime.canRedo, true);
});

test("rejected candidate IDs are not reserved before a successful commit", () => {
  let calls = 0;
  const runtime = new WorkbenchRuntime(fixture, {
    evaluateTransfer() {
      calls += 1;
      if (calls === 1) {
        return {
          accepted: true,
          summary: "Malformed candidate should not reserve its ID.",
          patch: {
            addEntities: [{
              id: "candidate-id",
              label: "Candidate",
              provenance: { kind: "DERIVED", sourceEntityRefs: ["missing-source"] }
            }],
            addProjections: []
          }
        };
      }
      return {
        accepted: true,
        summary: "Valid commit may still use the previously rejected candidate ID.",
        patch: {
          addEntities: [{
            id: "candidate-id",
            label: "Committed candidate",
            provenance: { kind: "DERIVED", sourceEntityRefs: ["dividend-156"] }
          }],
          addProjections: []
        }
      };
    }
  });

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const rejected = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(rejected.type, "TRANSFER_REJECTED");
  assert.equal(rejected.code, "WORKBENCH_PROVENANCE_SOURCE_UNKNOWN");
  assert.equal(runtime.snapshot.entities.some((row) => row.id === "candidate-id"), false);

  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const accepted = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(accepted.type, "TRANSFER_ACCEPTED");
  assert.equal(runtime.snapshot.entities.find((row) => row.id === "candidate-id").label, "Committed candidate");
});

test("runtime instances are isolated", () => {
  const first = new WorkbenchRuntime(fixture, divisionAdapter());
  const second = new WorkbenchRuntime(fixture, divisionAdapter());
  first.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  first.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(first.snapshot.entities.length, second.snapshot.entities.length + 1);
  assert.equal(second.snapshot.revision, 0);
});

test("incompatible scenes and malformed adapter patches fail closed", () => {
  const incompatible = structuredClone(fixture);
  incompatible.apiVersion = "9.9.9";
  assert.throws(() => new WorkbenchRuntime(incompatible, divisionAdapter()), (error) => error.code === "WORKBENCH_API_VERSION_MISMATCH");

  const brokenAdapter = {
    evaluateTransfer() {
      return {
        accepted: true,
        patch: {
          addEntities: [{ id: "derived-bad", label: "bad", provenance: { sourceEntityRefs: ["missing-source"] } }],
          addProjections: []
        }
      };
    }
  };
  const runtime = new WorkbenchRuntime(fixture, brokenAdapter);
  runtime.dispatch({ type: "PICK", entityRef: "dividend-156", channel: "click" });
  const before = runtime.snapshot;
  const event = runtime.dispatch({ type: "DROP", targetRef: "quotient-first-digit", channel: "click" });
  assert.equal(event.type, "TRANSFER_REJECTED");
  assert.deepEqual(runtime.snapshot.entities, before.entities);
  assert.equal(runtime.snapshot.revision, before.revision);
});

test("public component uses Shadow DOM and keeps instance state separate", async () => {
  const registry = new Map();
  globalThis.HTMLElement = class {
    attachShadow() {
      const root = {
        innerHTML: "",
        listeners: [],
        addEventListener(type, handler) { this.listeners.push([type, handler]); }
      };
      this.shadowRoot = root;
      return root;
    }
    dispatchEvent() { return true; }
  };
  globalThis.CustomEvent = class { constructor(type, options) { this.type = type; this.detail = options?.detail; } };
  globalThis.customElements = {
    get(name) { return registry.get(name); },
    define(name, ctor) { registry.set(name, ctor); }
  };

  const module = await import(`../Shared/workbench/semantic-workbench.mjs?test=${Date.now()}`);
  assert.equal(registry.get("semantic-workbench"), module.SemanticWorkbench);
  const a = new module.SemanticWorkbench();
  const b = new module.SemanticWorkbench();
  assert.notEqual(a.shadowRoot, b.shadowRoot);
  assert.deepEqual(a.shadowRoot.listeners.map(([type]) => type).sort(), ["click", "focusin", "keydown", "pointerdown", "pointerover", "pointerup"]);
});

assert.equal(WORKBENCH_API_VERSION, "0.1.0");
