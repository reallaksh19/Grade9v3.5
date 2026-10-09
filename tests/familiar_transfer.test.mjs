import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { resolveFamiliarTransfer } from "../Shared/workbench/familiar-transfer.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const fixture = JSON.parse(await readFile(
  resolve(here, "fixtures/workbench/core-learning-projections.json"), "utf8",
)).projections;
const core2a = fixture.find((x) => x.core === "CORE2A");
const core2b = fixture.find((x) => x.core === "CORE2B");
const FAMILY = core2a.application.family_ref;

function dataWith({ unrelated = false } = {}) {
  const a = structuredClone(core2a);
  const b = structuredClone(core2b);
  a.application.check = "Substitute the input and check the original condition.";
  a.application.solution.steps = ["Reconstruct the familiar relation."];
  b.application.transfer.builds_on = [a.application.question_ref];
  b.application.transfer.invariant = "The model condition still controls the relation.";
  b.application.transfer.novelty = {
    why_new: "This time the learner must select the model instead of applying the provided route.",
  };
  b.application.repair = { step_ref: "K-REPAIR-1" };
  b.application.solution.rubric = [{
    criterion: "Selects the changed model.",
    evidence_of: "Explains why the original model condition no longer controls the case.",
  }];
  b.presentation.show_solution_initially = false;
  b.presentation.protected_move_refs = [b.application.transfer.protected_move_ref];
  const rows = [
    { id: "physics:a", source_ref: a.application.question_ref, subject: "Physics", projection: a },
    { id: "physics:b", source_ref: b.application.question_ref, subject: "Physics", projection: b },
  ];
  if (unrelated) rows.push({
    id: "chem:b", source_ref: b.application.question_ref, subject: "Chemistry", projection: b,
  });
  return {
    core_projections: rows,
    bucket_availability: [{
      subject: "Physics", bucket_ref: "BUCKET-2D", status: "AVAILABLE",
      projection_refs: rows.filter((x) => x.subject === "Physics").map((x) => x.id),
    }],
  };
}

test("familiar authored Core2A and genuinely protected Core2B have one bound path", () => {
  const data = dataWith();
  for (const selected of ["physics:a", "physics:b"]) {
    const output = resolveFamiliarTransfer(data, selected);
    assert.equal(output.status, "STRUCTURED_REVIEW_REQUIRED");
    assert.equal(output.pairs.length, 1);
    assert.deepEqual([
      output.pairs[0].parent_projection_id,
      output.pairs[0].transfer_projection_id,
    ], ["physics:a", "physics:b"]);
    assert.equal(output.pairs[0].transfer_dimension, "model_choice");
    assert.equal(output.pairs[0].family_ref, FAMILY);
    assert.equal(output.pairs[0].academic_acceptance, "NOT_EVALUATED");
    assert.equal(output.pairs[0].learner_prerequisite, "NOT_EVALUATED");
    assert.equal(output.pairs[0].source_custody, "NOT_EVALUATED");
  }
});

test("missing Core2A parent or wrong family never generates a guess", () => {
  const data = dataWith();
  data.core_projections = data.core_projections.filter((x) => x.id !== "physics:a");
  assert.equal(resolveFamiliarTransfer(data, "physics:b").status, "HOLD");
  const replaced = dataWith();
  replaced.core_projections[0].projection.application.family_ref = "NOT-SAME-FAMILY";
  const failed = resolveFamiliarTransfer(replaced, "physics:b");
  assert.equal(failed.status, "HOLD");
  assert.match(failed.findings[0], /FAMILY_LINEAGE_MISMATCH/);
});

test("same-family unrelated child is not enough without builds_on exact question ID", () => {
  const data = dataWith();
  data.core_projections[1].projection.application.transfer.builds_on = ["MIC-UNRELATED"];
  const result = resolveFamiliarTransfer(data, "physics:b");
  assert.equal(result.status, "HOLD");
  assert.match(result.findings[0], /FAMILIAR_PARENT_NOT_UNIQUE/);
});

test("changed label without a new protected DECIDE move is a hold", () => {
  const data = dataWith();
  const child = data.core_projections[1].projection.application;
  child.reasoning_route.find((move) => move.id === "R-PROTECTED").kind = "CONNECT";
  const result = resolveFamiliarTransfer(data, "physics:b");
  assert.equal(result.status, "HOLD");
  assert.ok(result.findings.some((x) => x.includes("PROTECTED_DECISION_NOT_BOUND")));
});

test("a missing novelty explanation or unchanged question is not changed-demand evidence", () => {
  const missing = dataWith();
  missing.core_projections[1].projection.application.transfer.novelty = {};
  assert.ok(resolveFamiliarTransfer(missing, "physics:b").findings.some((x) =>
    x.includes("CHANGED_DEMAND_EVIDENCE_INCOMPLETE")));
  const clone = dataWith();
  clone.core_projections[1].projection.application.stem =
    clone.core_projections[0].projection.application.stem;
  assert.ok(resolveFamiliarTransfer(clone, "physics:b").findings.some((x) =>
    x.includes("NO_CHANGED_QUESTION")));
});

test("no rubric/repair or W attempt protection cannot pass as transfer", () => {
  const variants = [
    (data) => { data.core_projections[1].projection.application.repair = null; },
    (data) => { data.core_projections[1].projection.application.solution.rubric = []; },
    (data) => { data.core_projections[1].projection.presentation.attempt_before_reveal = false; },
    (data) => { data.core_projections[1].projection.presentation.protected_move_refs = []; },
  ];
  for (const mutate of variants) {
    const data = dataWith();
    mutate(data);
    assert.equal(resolveFamiliarTransfer(data, "physics:b").status, "HOLD");
  }
});

test("foreign-subject parent and duplicate parents cannot become established exposure", () => {
  const data = dataWith({ unrelated: true });
  assert.equal(resolveFamiliarTransfer(data, "physics:b").status, "STRUCTURED_REVIEW_REQUIRED");
  const dup = dataWith();
  const copy = structuredClone(dup.core_projections[0]);
  copy.id = "physics:a-duplicate";
  dup.core_projections.push(copy);
  dup.bucket_availability[0].projection_refs.push(copy.id);
  assert.equal(resolveFamiliarTransfer(dup, "physics:b").status, "HOLD");
});

test("no Core2B child is a legitimate explicit gap rather than fabricated transfer", () => {
  const data = dataWith();
  data.core_projections.pop();
  assert.equal(resolveFamiliarTransfer(data, "physics:a").status, "NO_TRANSFER_CHILD");
});

test("existing canonical production 2A/2B changed-model witness is structurally routed", async () => {
  const raw = await readFile(resolve(here, "../public/core-learning/data.js"), "utf8");
  const prefix = "window.GRADE9V3_CORE = ";
  assert.ok(raw.includes(prefix));
  const data = JSON.parse(raw.slice(raw.indexOf(prefix) + prefix.length).trim().replace(/;$/, ""));
  const witness = data.core_projections.find((row) =>
    row?.source_ref === "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"
      && row?.projection?.core === "CORE2B");
  assert.ok(witness, "Canonical Core2B motion witness absent from provider");
  const result = resolveFamiliarTransfer(data, witness.id);
  assert.equal(result.status, "STRUCTURED_REVIEW_REQUIRED", JSON.stringify(result.findings));
  assert.equal(result.pairs.length, 1);
  assert.equal(result.pairs[0].parent_ref, "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04");
  assert.equal(result.pairs[0].transfer_dimension, "model_choice");
});

test("both generated learner hosts wire the guided transfer and disclose exposure", async () => {
  const pages = await Promise.all([
    "../public/core-learning/index.html",
    "../standalone/core-learning/index.html",
    "../Shared/tools/build_core_learning_host.py",
  ].map((path) => readFile(resolve(here, path), "utf8")));
  for(const s of pages) {
    assert.match(s, /id="familiar-transfer"/);
    assert.match(s, /resolveFamiliarTransfer/);
    assert.match(s, /visitedFamiliar/);
    assert.match(s, /prior capability is unverified/i);
    assert.match(s, /not certified mastery/i);
  }
});
