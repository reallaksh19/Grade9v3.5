// Reconcile the measured layout with the selected blueprint; no new acceptance layer.
export function matchesBlueprintLayout(policy, legacyColumnsMatch, measurement) {
  if (policy?.expanded !== 'SINGLE_PANE') return legacyColumnsMatch;
  return measurement.articleCount > 0
    && measurement.columnCounts.every(count => count <= 1);
}
