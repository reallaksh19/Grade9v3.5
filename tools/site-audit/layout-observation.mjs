// Reconcile the measured layout with the selected blueprint; no new acceptance layer.
export function splitLayoutExpectation(policy) {
  if (policy?.expanded !== 'STAGE_SUPPORT' || !policy.support_fraction) return null;
  return {
    primaryFraction: policy.primary_fraction,
    supportFraction: policy.support_fraction,
    minPx: policy.expanded_min_px || 1100,
  };
}

export function matchesBlueprintLayout(policy, legacyColumnsMatch, measurement) {
  if (policy?.expanded !== 'SINGLE_PANE') return legacyColumnsMatch;
  return measurement.articleCount > 0
    && measurement.columnCounts.every(count => count <= 1);
}
