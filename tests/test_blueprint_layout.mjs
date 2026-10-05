import test from 'node:test';
import assert from 'node:assert/strict';
import { matchesBlueprintLayout } from '../tools/site-audit/layout-observation.mjs';

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
