// Reconcile the measured layout with the selected blueprint; no new acceptance layer.
export function splitLayoutExpectation(policy) {
  if (policy?.expanded !== 'STAGE_SUPPORT') return null;
  const primary = Number(policy.primary_fraction);
  const support = Number(policy.support_fraction);
  const minPx = policy.expanded_min_px == null ? 1100 : Number(policy.expanded_min_px);
  if (
    !Number.isFinite(primary) || !Number.isFinite(support) || !Number.isFinite(minPx)
    || primary <= 0 || support <= 0 || minPx <= 0
    || Math.abs((primary + support) - 1) > 1e-6
  ) return null;
  return {
    primaryFraction: primary,
    supportFraction: support,
    minPx,
  };
}

export function matchesBlueprintLayout(policy, legacyColumnsMatch, measurement) {
  if (policy?.expanded !== 'SINGLE_PANE') return legacyColumnsMatch;
  return measurement.articleCount > 0
    && measurement.columnCounts.every(count => count <= 1);
}
