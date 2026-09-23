import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  CoreLearningHostError,
  mountCoreLearningPage,
  resolveCoreLearningInputs,
  resolveCoreLearningRecord,
} from "../Shared/workbench/core-learning-host.mjs";
import { CoreLearningPage } from "../Shared/workbench/core-learning-page.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const projectionFixtures = JSON.parse(
  await readFile(resolve(here, "fixtures/workbench/core-learning-projections.json"), "utf8"),
).projections;
const sceneFixture = JSON.parse(
  await readFile(resolve(here, "fixtures/workbench/arithmetic-division.json"), "utf8"),
);

const byId = Object.fromEntries(projectionFixtures.map((row) => [row.id, row]));

function dataWith(records) {
  return {
    generated_by: "test",
    subjects: {
      Physics: {
        matrices: [{
          id: "MATRIX-RAW-NOT-A-PROJECTION",
          microtopics: [{ id: "MIC-RAW", inferential_jump: "Browser must not compile this." }],
          questions: [{ id: "Q-RAW", stem: "Browser must not synthesize pedagogy from this." }],
        }],
      },
    },
    core_projections: records,
  };
}

test("host resolves an explicitly precompiled Core projection record", () => {
  const record = resolveCoreLearningRecord(dataWith([
    { id: "motion-core1b", source_ref: "MIC-FIXTURE-1", projection: byId.core1b },
  ]), "motion-core1b");

  assert.equal(record.id, "motion-core1b");
  assert.equal(record.projection.core, "CORE1B");
  assert.equal(record.sceneRef, null);
  assert.equal(record.adapterRef, null);
  assert.deepEqual(record.injectionRefs, []);
});

test("host refuses raw Topic Atlas data instead of synthesizing a browser-local projection", () => {
  const rawAtlasOnly = {
    generated_by: "Shared/tools/build_web_data.py",
    subjects: {
      Physics: {
        matrices: [{
          id: "MATRIX-PHY-KIN-2D-MOTION",
          microtopics: [{
            id: "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
            inferential_jump: "Perpendicular components share one physical time.",
            teaching_path: [{ id: "K2D1-1", action: "Declare the frame." }],
          }],
          questions: [{
            id: "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04",
            stem: "Find the time and range.",
            hints: [{ text: "Use the vertical event time." }],
          }],
        }],
      },
    },
  };

  assert.throws(
    () => resolveCoreLearningRecord(rawAtlasOnly, "anything"),
    (error) => error instanceof CoreLearningHostError
      && error.code === "CORE_LEARNING_PROJECTIONS_REQUIRED",
  );
});

test("workbench binding is all-or-nothing and references explicit host registries", () => {
  const incomplete = dataWith([{
    id: "core2a-incomplete",
    source_ref: "Q-FIXTURE-2A",
    projection: byId.core2a,
    scene_ref: "scene-1",
  }]);
  assert.throws(
    () => resolveCoreLearningRecord(incomplete, "core2a-incomplete"),
    (error) => error instanceof CoreLearningHostError
      && error.code === "CORE_LEARNING_WORKBENCH_BINDING_INCOMPLETE",
  );

  const bound = dataWith([{
    id: "core2a-bound",
    source_ref: "Q-FIXTURE-2A",
    projection: byId.core2a,
    scene_ref: "scene-1",
    adapter_ref: "adapter-1",
    injection_refs: ["hint-1"],
  }]);

  assert.throws(
    () => resolveCoreLearningInputs(bound, "core2a-bound"),
    (error) => error instanceof CoreLearningHostError
      && error.code === "CORE_LEARNING_SCENE_NOT_FOUND",
  );

  const adapter = { evaluateTransfer() { return { accepted: false, reason: "fixture" }; } };
  const resolved = resolveCoreLearningInputs(bound, "core2a-bound", {
    scenes: { "scene-1": sceneFixture },
    adapters: { "adapter-1": adapter },
    injections: { "hint-1": { kind: "HINT", prompt: "Inspect the supplied representation." } },
  });

  assert.equal(resolved.projection.core, "CORE2A");
  assert.equal(resolved.scene.id, sceneFixture.id);
  assert.equal(resolved.adapter, adapter);
  assert.deepEqual(resolved.injections, [{
    kind: "HINT",
    prompt: "Inspect the supplied representation.",
  }]);
});

test("host fails with named codes for missing, malformed, or unbound references", () => {
  const bound = {
    id: "bound",
    source_ref: "Q-EXAMPLE",
    projection: byId.core2a,
    scene_ref: "scene-1",
    adapter_ref: "adapter-1",
    injection_refs: ["hint-1"],
  };
  const data = dataWith([bound]);
  assert.equal(resolveCoreLearningRecord(data, "bound").sourceRef, "Q-EXAMPLE");
  const fails = (action, code) => assert.throws(
    action,
    (error) => error instanceof CoreLearningHostError && error.code === code,
  );
  fails(() => resolveCoreLearningRecord(data, "absent"), "CORE_LEARNING_PROJECTION_NOT_FOUND");
  fails(
    () => resolveCoreLearningInputs(data, "bound", { scenes: { "scene-1": sceneFixture } }),
    "CORE_LEARNING_ADAPTER_NOT_FOUND",
  );
  fails(
    () => resolveCoreLearningInputs(data, "bound", {
      scenes: { "scene-1": sceneFixture },
      adapters: { "adapter-1": {} },
    }),
    "CORE_LEARNING_INJECTION_NOT_FOUND",
  );
  fails(
    () => resolveCoreLearningRecord(dataWith([{ ...bound, source_ref: " " }]), "bound"),
    "CORE_LEARNING_SOURCE_REF_INVALID",
  );
  const missingSource = { ...bound };
  delete missingSource.source_ref;
  fails(
    () => resolveCoreLearningRecord(dataWith([missingSource]), "bound"),
    "CORE_LEARNING_SOURCE_REF_INVALID",
  );
  fails(
    () => resolveCoreLearningRecord(dataWith([{ ...bound, injection_refs: [""] }]), "bound"),
    "CORE_LEARNING_INJECTION_REFS_INVALID",
  );
  fails(
    () => resolveCoreLearningRecord(dataWith([{
      ...bound, scene_ref: null, adapter_ref: null,
    }]), "bound"),
    "CORE_LEARNING_INJECTION_BINDING_INCOMPLETE",
  );
});

test("mount configures projection and workbench inputs atomically and clears stale bindings", () => {
  const adapter = { evaluateTransfer() { return { accepted: false, reason: "fixture" }; } };
  const data = dataWith([
    {
      id: "core2b-mounted",
      source_ref: "Q-FIXTURE-2B",
      projection: byId.core2b,
      scene_ref: "scene-division",
      adapter_ref: "adapter-division",
      injection_refs: ["hint-1"],
    },
    {
      id: "core1b-plain",
      source_ref: "MIC-FIXTURE-1",
      projection: byId.core1b,
      scene_ref: null,
      adapter_ref: null,
      injection_refs: [],
    },
  ]);
  const element = new CoreLearningPage();
  element.localName = "core-learning-page";

  const result = mountCoreLearningPage(element, data, "core2b-mounted", {
    scenes: { "scene-division": sceneFixture },
    adapters: { "adapter-division": adapter },
    injections: { "hint-1": { kind: "HINT", prompt: "Use supplied evidence only." } },
  });

  assert.deepEqual(result, { id: "core2b-mounted", workbenchBound: true });
  assert.equal(element.projection.core, "CORE2B");
  assert.equal(element.scene.id, sceneFixture.id);
  assert.equal(element.adapter, adapter);
  assert.deepEqual(element.injections, [{ kind: "HINT", prompt: "Use supplied evidence only." }]);

  const plain = mountCoreLearningPage(element, data, "core1b-plain");
  assert.deepEqual(plain, { id: "core1b-plain", workbenchBound: false });
  assert.equal(element.projection.core, "CORE1B");
  assert.equal(element.scene, null);
  assert.equal(element.adapter, null);
  assert.deepEqual(element.injections, []);
});

test("host source contains no subject-specific compiler fallback or learner classification vocabulary", async () => {
  const source = await readFile(
    resolve(here, "../Shared/workbench/core-learning-host.mjs"),
    "utf8",
  );

  for (const forbidden of [
    /Physics\//i,
    /projectile/i,
    /friction/i,
    /motion[- ]?2d/i,
    /microtopic.*inferential_jump.*teaching_path/s,
    /mastery/i,
    /proficien/i,
    /readiness/i,
    /knowledge percentage/i,
  ]) {
    assert.doesNotMatch(source, forbidden);
  }
});
