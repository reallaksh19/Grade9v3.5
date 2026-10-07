import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
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
test('missing or malformed split policy fails closed instead of assuming a ratio', () => {
  assert.equal(splitLayoutExpectation(null), null);
  assert.equal(matchesBlueprintLayout(
    null, false, {articleCount: 1, columnCounts: [1]},
  ), false);

  assert.equal(splitLayoutExpectation({
    expanded: 'STAGE_SUPPORT',
    support_fraction: 0.58,
    expanded_min_px: 980,
  }), null);
  assert.equal(splitLayoutExpectation({
    expanded: 'STAGE_SUPPORT',
    primary_fraction: 0.50,
    support_fraction: 0.58,
    expanded_min_px: 980,
  }), null);
  assert.equal(splitLayoutExpectation({
    expanded: 'STAGE_SUPPORT',
    primary_fraction: 0.42,
    support_fraction: 0.58,
    expanded_min_px: -1,
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

test('active Core1A SINGLE_PANE policy accepts measured one-column content', () => {
  const registry = JSON.parse(fs.readFileSync(
    new URL('../Shared/web/interactive-page-blueprints.v1.json', import.meta.url), 'utf8'));
  const blueprint = registry.blueprints.find(row => row.id === 'BP-CORE1A-CONSTRUCTION');
  assert.ok(blueprint);
  assert.equal(blueprint.version, '1.8.0');
  assert.equal(splitLayoutExpectation(blueprint.responsive_policy), null);
  assert.equal(matchesBlueprintLayout(
    blueprint.responsive_policy,
    false,
    {articleCount: 3, columnCounts: [1, 1, 1]},
  ), true);
});

test('active Core2 STAGE_SUPPORT policy retains its declared split contract', () => {
  const registry = JSON.parse(fs.readFileSync(
    new URL('../Shared/web/interactive-page-blueprints.v1.json', import.meta.url), 'utf8'));
  const blueprint = registry.blueprints.find(row => row.id === 'BP-CORE2-SOURCE-QUESTION');
  assert.ok(blueprint);
  assert.equal(blueprint.version, '1.11.0');
  assert.deepEqual(splitLayoutExpectation(blueprint.responsive_policy), {
    primaryFraction: 0.42,
    supportFraction: 0.58,
    minPx: 980,
  });
  assert.equal(matchesBlueprintLayout(blueprint.responsive_policy, true, null), true);
});
