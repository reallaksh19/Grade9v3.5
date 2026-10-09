import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { resolveCore1StudyContinuity } from "../Shared/workbench/core1-continuity.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const fixtures = JSON.parse(await readFile(
  resolve(here, "fixtures/workbench/core-learning-projections.json"), "utf8",
)).projections;
const byCore = Object.fromEntries(fixtures.map((row) => [row.core, row]));
const MICRO = "MIC-FIXTURE-SHARED-IDEA";
const BUCKET = "BUCKET-FIXTURE";

function subjectRow(core, suffix = "") {
  const projection = structuredClone(byCore[core]);
  if (core === "CORE1") projection.orientation.bucket_ref = BUCKET;
  // The standalone Core1A fixture intentionally lacks diagnostic material;
  // canonical provider rows carry the same misconceptions on both A and B.
  if (core === "CORE1A") {
    projection.concept.misconceptions = structuredClone(byCore.CORE1B.concept.misconceptions);
  }
  return { id: core + suffix, subject: "Physics",
    source_ref: core === "CORE1" ? BUCKET : MICRO,
    projection };
}

function goodData() {
  const rows = ["CORE1", "CORE1A", "CORE1B"].map((x) => subjectRow(x));
  return { core_projections: rows, bucket_availability: [{
    subject: "Physics", bucket_ref: BUCKET, status: "AVAILABLE",
    projection_refs: rows.map((x) => x.id),
  }] };
}

test("compiler-backed route exposes map, complete construction, then attempt-first B", () => {
  const data = goodData();
  for (const selected of ["CORE1", "CORE1A", "CORE1B"]) {
    const result = resolveCore1StudyContinuity(data, selected);
    assert.equal(result.status, "COMPLETE", selected);
    assert.equal(result.paths.length, 1);
    assert.deepEqual(result.paths[0].steps.map((step) => [step.core, step.id]), [
      ["CORE1", "CORE1"], ["CORE1A", "CORE1A"], ["CORE1B", "CORE1B"],
    ]);
    assert.equal(result.paths[0].microtopic_ref, MICRO);
  }
});

test("changed canonical inferential jump prevents a false A/B link", () => {
  const data = goodData();
  data.core_projections[2].projection.concept.inferential_jump = "Unrelated changed claim";
  const result = resolveCore1StudyContinuity(data, "CORE1A");
  assert.equal(result.status, "HOLD");
  assert.equal(result.paths.length, 0);
  assert.match(result.findings[0], /CORE1A_CORE1B_IDENTITY/);
});

test("wrong original bucket orientation blocks navigation", () => {
  const data = goodData();
  data.core_projections[0].projection.orientation.bucket_ref = "BUCKET-OTHER";
  const result = resolveCore1StudyContinuity(data, "CORE1B");
  assert.equal(result.status, "HOLD");
  assert.deepEqual(result.findings, ["CORE1_CANONICAL_BUCKET_ROUTE_MISSING"]);
});

test("missing or duplicate B never creates guessed learner steps", () => {
  const data = goodData();
  data.core_projections.splice(2, 1);
  assert.equal(resolveCore1StudyContinuity(data, "CORE1A").status, "HOLD");
  const another = subjectRow("CORE1B", "-DUP");
  data.core_projections.push(subjectRow("CORE1B"), another);
  data.bucket_availability[0].projection_refs.push("CORE1B-DUP");
  assert.equal(resolveCore1StudyContinuity(data, "CORE1A").status, "HOLD");
});

test("incomplete reconstruct/boundary/diagnosis is a route hold", () => {
  const data = goodData();
  data.core_projections[2].projection.concept.elicitation.boundary_test = {};
  assert.equal(resolveCore1StudyContinuity(data, "CORE1B").status, "HOLD");
  data.core_projections[2] = subjectRow("CORE1B");
  data.core_projections[1].projection.concept.misconceptions = [];
  assert.equal(resolveCore1StudyContinuity(data, "CORE1A").status, "HOLD");
});

test("a foreign-subject row cannot enter the same bucket via ID coincidence", () => {
  const data = goodData();
  const other = subjectRow("CORE1B", "-OTHER");
  other.subject = "Chemistry";
  data.core_projections.push(other);
  data.bucket_availability[0].projection_refs.push(other.id);
  const result = resolveCore1StudyContinuity(data, "CORE1A");
  assert.equal(result.status, "COMPLETE");
  assert.equal(result.paths.length, 1);
});

test("Core2A is not secretly converted into a Core1 study route", () => {
  const data = goodData();
  data.core_projections.push(subjectRow("CORE2A"));
  const result = resolveCore1StudyContinuity(data, "CORE2A");
  assert.equal(result.status, "OUTSIDE_CORE1_STUDY");
  assert.deepEqual(result.paths, []);
});

test("the generated learner hosts actually mount continuity navigation and assistance disclosure", async () => {
  const [publicHtml, docsHtml, standaloneHtml, builder] = await Promise.all([
    readFile(resolve(here, "../public/core-learning/index.html"), "utf8"),
    readFile(resolve(here, "../docs/core-learning/index.html"), "utf8"),
    readFile(resolve(here, "../standalone/core-learning/index.html"), "utf8"),
    readFile(resolve(here, "../Shared/tools/build_core_learning_host.py"), "utf8"),
  ]);
  for (const text of [publicHtml, docsHtml, standaloneHtml, builder]) {
    assert.match(text, /id="core1-study-journey"/);
    assert.match(text, /resolveCore1StudyContinuity/);
    assert.match(text, /Core1B · Attempt reconstruction/);
    assert.match(text, /viewedConstruction/);
    assert.match(text, /not an uncued mastery result/);
  }
});

test("compiler-generated learner data has no false complete study path", async () => {
  const raw = await readFile(resolve(here, "../public/core-learning/data.js"), "utf8");
  const prefix = "window.GRADE9V3_CORE = ";
  assert.ok(raw.includes(prefix));
  const content = raw.slice(raw.indexOf(prefix) + prefix.length).trim();
  const data = JSON.parse(content.replace(/;$/, ""));
  const pairRows = data.core_projections.filter((r) => ["CORE1A", "CORE1B"].includes(r.projection?.core));
  assert.ok(pairRows.length > 0);
  const mismatches = [];
  for (const row of pairRows) {
    const result = resolveCore1StudyContinuity(data, row.id);
    if (result.status !== "COMPLETE" || result.paths.length !== 1) {
      mismatches.push({ id: row.id, status: result.status, findings: result.findings });
    }
  }
  assert.deepEqual(mismatches, [], JSON.stringify(mismatches.slice(0, 5)));
});
