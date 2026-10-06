import test from 'node:test';
import assert from 'node:assert/strict';
import { matchesBlueprintLayout, splitLayoutExpectation } from '../tools/site-audit/layout-observation.mjs';

test('a measured single pane satisfies the Core1A policy even without column CSS', () => {
  assert.equal(matchesBlueprintLayout({expanded: 'SINGLE_PANE'}, false,
    {articleCount: 3, columnCounts: [1, 1, 1]}), true);
});
test('an actual two-column article or split violates a single-pane policy', () => {
  assert.equal(matchesBlueprintLayout({expanded: 'SINGLE_PANE'}, true,
    {articleCount: 3, columnCounts: [1, 2, 1]}), false);
});
test('an empty page cannot provide single-pane layout evidence', () => {
  assert.equal(matchesBlueprintLayout({expanded: 'SINGLE_PANE'}, true,
    {articleCount: 0, columnCounts: []}), false);
});
test('roles requiring stage/support columns retain their existing observation', () => {
  assert.equal(matchesBlueprintLayout({expanded: 'STAGE_SUPPORT'}, false, null), false);
  assert.equal(matchesBlueprintLayout({expanded: 'STAGE_SUPPORT'}, true, null), true);
});

test('single-pane policy never creates a split expectation even with retained fractions', () => {
  assert.equal(splitLayoutExpectation({
    expanded: 'SINGLE_PANE',
    primary_fraction: 0.6,
    support_fraction: 0.4,
    expanded_min_px: 1100,
  }), null);
});
test('stage-support policy derives its split expectation from the blueprint', () => {
  assert.deepEqual(splitLayoutExpectation({
    expanded: 'STAGE_SUPPORT',
    primary_fraction: 0.42,
    support_fraction: 0.58,
    expanded_min_px: 980,
  }), {
    primaryFraction: 0.42,
    supportFraction: 0.58,
    minPx: 980,
  });
});
