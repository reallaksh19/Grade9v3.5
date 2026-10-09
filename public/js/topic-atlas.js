/**
 * Topic Atlas Generic Engine (Issue #118 Data-Driven Architecture)
 * 
 * ZERO FAKE DATA POLICY: All curriculum facts, rungs, teaching-path steps,
 * capabilities, and activities are projected directly from window.GRADE9V3.
 * 
 * Works 100% offline via file:// and local web servers.
 */

(function() {
  'use strict';

  // State Management
  const state = {
    matrix: null,
    subject: null,
    knowledge_percentage: null, // null = unsupplied, NOT 0%
    diagnostic_rows: [],         // Validated external scanned gap rows
    validation_report: null,     // Import audit report
    overlay_active: true,
    selected_target: null,       // Diagnostic focus target (e.g. "R5.1.0")
    selected_rung_key: null,      // Explicit Atlas interaction identity { matrix_id, rung }
    atlas_finding: null,          // Visible browser/contract integrity finding
    history_bound: false,
    request_config: {
      cores: ['CORE1A', 'CORE1B', 'CORE2A'],
      core2a_purpose: 'PRACTICE',
      core2b_purpose: null       // null = planner may request purpose if CORE2B selected
    }
  };



  const ATLAS_INDEX_CONTRACT_VERSION = '2.0';

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function currentSubjectPayload() {
    if (!window.GRADE9V3 || !window.GRADE9V3.subjects || !state.subject) return null;
    return window.GRADE9V3.subjects[state.subject] || null;
  }

  function resolveAtlasComposite(subjectPayload, matrixId, rungId) {
    if (!subjectPayload || subjectPayload.atlas_index_contract_version !== ATLAS_INDEX_CONTRACT_VERSION) {
      return {
        status: 'INVALID',
        code: 'ATLAS_INDEX_VERSION_UNSUPPORTED',
        message: 'AtlasIndex 2.0 is required for canonical browser navigation.',
        row: null
      };
    }
    const rows = Array.isArray(subjectPayload.atlas_index) ? subjectPayload.atlas_index : [];
    const matches = rows.filter(row => row.matrix_id === matrixId && row.rung === rungId);
    if (matches.length === 0) {
      return {
        status: 'INVALID',
        code: 'ATLAS_TARGET_NOT_FOUND',
        message: 'No canonical AtlasIndex row exists for ' + matrixId + ' / ' + rungId + '.',
        row: null
      };
    }
    if (matches.length !== 1) {
      return {
        status: 'INVALID',
        code: 'ATLAS_DUPLICATE_KEY',
        message: 'Canonical AtlasIndex identity is not unique for ' + matrixId + ' / ' + rungId + '.',
        row: null
      };
    }
    const row = matches[0];
    const mapping = ((row.availability || {}).mapping || 'INVALID').toUpperCase();
    if (mapping === 'INVALID') {
      return {
        status: 'INVALID',
        code: 'ATLAS_MAPPING_INVALID',
        message: 'The canonical AtlasIndex row is present but its mapping is INVALID.',
        row
      };
    }
    if (mapping !== 'READY') {
      return {
        status: 'UNAVAILABLE',
        code: 'ATLAS_MAPPING_UNAVAILABLE',
        message: 'The canonical AtlasIndex row is present but its mapping is not available.',
        row
      };
    }
    return { status: 'READY', code: null, message: null, row };
  }

  function resolveCoreDestinationsFor(row, corePayload) {
    const availability = ((row || {}).availability || {}).core || 'UNAVAILABLE';
    const refs = Array.isArray((row || {}).core_projection_refs) ? row.core_projection_refs : [];
    // A structurally READY Atlas mapping cannot override the separately
    // governed publication gate. Never link a withheld Core projection.
    if (corePayload?.publication_gate?.status === 'HOLD') {
      return {
        status: 'HOLD',
        code: 'NO_INDEPENDENT_CORE_PUBLICATION_GRANT',
        refs,
        ready: [],
        unresolved: refs
      };
    }
    if (availability !== 'READY') {
      return { status: availability, refs, ready: [], unresolved: [] };
    }
    const projections = corePayload && Array.isArray(corePayload.core_projections)
      ? corePayload.core_projections
      : [];
    const byId = new Map(projections.map(item => [item.id, item]));
    const ready = refs.filter(ref => byId.has(ref));
    const unresolved = refs.filter(ref => !byId.has(ref));
    return { status: unresolved.length ? 'INVALID' : 'READY', refs, ready, unresolved };
  }

  function resolveVisualDestinationsFor(subjectPayload, row) {
    const rowAvailability = (row || {}).availability || {};
    const refs = Array.isArray((row || {}).activity_refs) ? row.activity_refs : [];
    if (rowAvailability.activity !== 'READY' || rowAvailability.locator !== 'READY') {
      return {
        status: rowAvailability.locator === 'INVALID' || rowAvailability.activity === 'INVALID' ? 'INVALID' : 'UNAVAILABLE',
        refs,
        ready: [],
        unresolved: refs
      };
    }
    const targets = (subjectPayload && subjectPayload.visual_targets) || {};
    const ready = [];
    const unresolved = [];
    refs.forEach(ref => {
      const target = targets[ref];
      const locatorState = target && target.availability ? target.availability.locator : null;
      if (target && locatorState === 'READY' && typeof target.locator === 'string' && target.locator.trim()) {
        ready.push({ ref, target });
      } else {
        unresolved.push(ref);
      }
    });
    return { status: unresolved.length ? 'INVALID' : 'READY', refs, ready, unresolved };
  }

  function resolvePortableDestinationsFor(subjectPayload, row) {
    const rowAvailability = (row || {}).availability || {};
    const refs = Array.isArray((row || {}).activity_refs) ? row.activity_refs : [];
    if (rowAvailability.portable_package !== 'READY') {
      return { status: rowAvailability.portable_package || 'UNAVAILABLE', refs, ready: [], unresolved: refs };
    }
    const targets = (subjectPayload && subjectPayload.visual_targets) || {};
    const ready = [];
    const unresolved = [];
    refs.forEach(ref => {
      const target = targets[ref];
      const availability = (target && target.availability) || {};
      const packageRef = target && target.portable_package_ref;
      if (
        availability.portable_package === 'READY'
        && typeof packageRef === 'string'
        && packageRef.trim()
      ) {
        ready.push({
          ref,
          package_ref: packageRef,
          standalone: availability.standalone === 'READY'
        });
      } else {
        unresolved.push(ref);
      }
    });
    return {
      status: ready.length ? 'READY' : 'INVALID',
      refs,
      ready,
      unresolved
    };
  }

  function setAtlasFinding(code, message) {
    state.atlas_finding = { code, message };
  }

  function clearAtlasFinding() {
    state.atlas_finding = null;
  }

  function renderAtlasFatalFinding(code, message) {
    const html = `
      <div class="atlas-finding" role="alert" tabindex="-1"
           style="border:1px solid var(--chip-hold-border);background:var(--chip-hold-bg);color:var(--chip-hold-text);padding:12px;border-radius:8px;margin:12px 0;">
        <strong>${escapeHtml(code)}</strong> · ${escapeHtml(message)}
      </div>
    `;
    ['progressionLaneContainer', 'rungCardsContainer', 'needMapContainer'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = html;
    });
    const first = document.querySelector ? document.querySelector('.atlas-finding') : null;
    if (first && typeof first.focus === 'function') first.focus();
  }

  function atlasFindingHtml() {
    if (!state.atlas_finding) return '';
    return `
      <div class="atlas-finding" role="status"
           style="border:1px solid var(--chip-hold-border);background:var(--chip-hold-bg);color:var(--chip-hold-text);padding:10px 12px;border-radius:8px;margin-bottom:12px;">
        <strong>${escapeHtml(state.atlas_finding.code)}</strong> · ${escapeHtml(state.atlas_finding.message)}
      </div>
    `;
  }

  function activityHref(locator) {
    if (!locator) return null;
    if (!locator.startsWith('public/')) return locator;

    const target = locator.replace(/^public\//, '').split('/').filter(Boolean);
    const pathname = window.location && typeof window.location.pathname === 'string'
      ? window.location.pathname
      : '';
    const current = pathname.split('/').filter(Boolean);
    const publicIdx = current.lastIndexOf('public');
    if (publicIdx === -1) return '../../' + target.join('/');

    const currentDir = current.slice(publicIdx + 1, -1);
    let common = 0;
    while (common < currentDir.length && common < target.length && currentDir[common] === target[common]) {
      common += 1;
    }
    const up = Array(Math.max(0, currentDir.length - common)).fill('..');
    return [...up, ...target.slice(common)].join('/') || './';
  }

  function coreProjectionHref(projectionId) {
    const base = activityHref('public/core-learning/index.html');
    if (!base) return null;
    return base + (base.includes('?') ? '&' : '?') + 'projection=' + encodeURIComponent(projectionId);
  }

  function portablePackageHref(packageRef) {
    const base = activityHref('public/portable-workbench/index.html');
    if (!base || !packageRef) return null;
    return base + (base.includes('?') ? '&' : '?') + 'package=' + encodeURIComponent(packageRef);
  }

  function canonicalNavigationBlocked() {
    return Boolean(
      state.atlas_finding
      && ['ATLAS_INDEX_VERSION_UNSUPPORTED', 'ATLAS_TARGET_INCOMPLETE', 'ATLAS_TARGET_NOT_FOUND', 'ATLAS_DUPLICATE_KEY']
        .includes(state.atlas_finding.code)
    );
  }

  function renderActivityAction(rungId, activity, label) {
    if (canonicalNavigationBlocked()) {
      return '<span class="badge hold">' + escapeHtml(label) + ': navigation disabled</span>';
    }
    const subjectPayload = currentSubjectPayload();
    const resolved = resolveAtlasComposite(subjectPayload, state.matrix.matrix_id, rungId);
    if (!resolved.row || resolved.status !== 'READY') {
      return '<span class="badge neutral">' + escapeHtml(label) + ': unavailable</span>';
    }
    const visual = resolveVisualDestinationsFor(subjectPayload, resolved.row);
    const match = visual.ready.find(item => item.ref === activity.id);
    if (!match) {
      return '<span class="badge neutral">' + escapeHtml(label) + ': ' + escapeHtml(activity.id) + ' unavailable</span>';
    }
    const href = activityHref(match.target.locator);
    if (!href) {
      return '<span class="badge hold">' + escapeHtml(label) + ': locator invalid</span>';
    }
    return `
      <a href="${escapeHtml(href)}" class="btn primary-phy"
         style="font-size:11px;padding:4px 9px;margin-right:6px;margin-top:6px;">
        ${escapeHtml(label)}: ${escapeHtml(activity.title || activity.id)} ↗
      </a>
    `;
  }

  function renderCanonicalAtlasDetails(resolution) {
    if (!resolution || !resolution.row) return '';
    const row = resolution.row;
    const availability = row.availability || {};
    const subjectPayload = currentSubjectPayload();
    const core = resolveCoreDestinationsFor(row, window.GRADE9V3_CORE || null);
    const visual = resolveVisualDestinationsFor(subjectPayload, row);
    const portable = resolvePortableDestinationsFor(subjectPayload, row);

    let coreActions = '';
    if (canonicalNavigationBlocked()) {
      coreActions = '<span class="badge hold">Canonical navigation disabled by Atlas finding</span>';
    } else if (availability.core === 'READY' && core.status === 'READY' && core.ready.length) {
      coreActions = core.ready.map(ref => {
        const href = coreProjectionHref(ref);
        return href
          ? `<a href="${escapeHtml(href)}" class="btn outline" style="font-size:11px;padding:4px 9px;margin:4px 6px 0 0;">Core · ${escapeHtml(ref)} ↗</a>`
          : '';
      }).join('');
    } else if (core.status === 'HOLD') {
      coreActions = '<span class="badge hold">Core publication held: NO_INDEPENDENT_CORE_PUBLICATION_GRANT</span>';
    } else if (availability.core === 'READY' && core.status !== 'READY') {
      coreActions = '<span class="badge hold">CORE_PROJECTION_RUNTIME_UNRESOLVED</span>';
    } else {
      coreActions = '<span class="badge neutral">Core ' + escapeHtml(availability.core || 'UNAVAILABLE') + '</span>';
    }

    let visualActions = '';
    if (canonicalNavigationBlocked()) {
      visualActions = '<span class="badge hold">Visual navigation disabled by Atlas finding</span>';
    } else if (visual.status === 'READY' && visual.ready.length) {
      visualActions = visual.ready.map(item => {
        const href = activityHref(item.target.locator);
        return href
          ? `<a href="${escapeHtml(href)}" class="btn primary-phy" style="font-size:11px;padding:4px 9px;margin:4px 6px 0 0;">Visual · ${escapeHtml(item.ref)} ↗</a>`
          : '';
      }).join('');
    } else {
      visualActions = '<span class="badge neutral">Visual ' + escapeHtml(visual.status || 'UNAVAILABLE') + '</span>';
    }

    let portableActions = '';
    if (canonicalNavigationBlocked()) {
      portableActions = '<span class="badge hold">Portable navigation disabled by Atlas finding</span>';
    } else if (portable.status === 'READY' && portable.ready.length) {
      portableActions = portable.ready.map(item => {
        const href = portablePackageHref(item.package_ref);
        const mode = item.standalone ? 'portable + standalone' : 'portable';
        return href
          ? `<a href="${escapeHtml(href)}" data-portable-package="${escapeHtml(item.package_ref)}" class="btn outline" style="font-size:11px;padding:4px 9px;margin:4px 6px 0 0;">Prototype · ${escapeHtml(item.package_ref)} (${mode}) ↗</a>`
          : '';
      }).join('');
    } else {
      portableActions = '<span class="badge neutral">Portable ' + escapeHtml(portable.status || 'UNAVAILABLE') + '</span>';
    }

    const findingRows = Array.isArray(row.findings) ? row.findings : [];
    const findings = findingRows.length
      ? '<div style="margin-top:8px;font-size:11px;color:var(--text-muted);"><strong>Canonical findings:</strong> ' +
        findingRows.map(item => escapeHtml(item.code || String(item))).join(', ') + '</div>'
      : '';

    const microPrereqs = Array.isArray(row.microtopic_prerequisite_refs) ? row.microtopic_prerequisite_refs : [];
    const capPrereqs = Array.isArray(row.capability_prerequisite_refs) ? row.capability_prerequisite_refs : [];

    return `
      <div class="block-subcard" style="margin:12px 0;border-color:var(--accent);">
        <div class="subcard-heading">Canonical AtlasIndex 2.0</div>
        <div style="font-size:12px;line-height:1.6;color:var(--text-secondary);">
          <div><strong>Identity:</strong> <code>${escapeHtml(row.matrix_id)} / ${escapeHtml(row.rung)}</code></div>
          <div><strong>Mapping:</strong> ${escapeHtml(availability.mapping || 'INVALID')} · <strong>Core:</strong> ${escapeHtml(availability.core || 'UNAVAILABLE')} · <strong>Representation:</strong> ${escapeHtml(availability.representation || 'UNAVAILABLE')} · <strong>Activity:</strong> ${escapeHtml(availability.activity || 'UNAVAILABLE')} · <strong>Locator:</strong> ${escapeHtml(availability.locator || 'UNAVAILABLE')} · <strong>Portable:</strong> ${escapeHtml(availability.portable_package || 'UNAVAILABLE')} · <strong>Standalone:</strong> ${escapeHtml(availability.standalone || 'UNAVAILABLE')}</div>
          <div><strong>Microtopic prerequisites:</strong> ${escapeHtml(microPrereqs.join(', ') || 'None')}</div>
          <div><strong>Capability prerequisites:</strong> ${escapeHtml(capPrereqs.join(', ') || 'None')}</div>
          <div><strong>Representations:</strong> ${escapeHtml((row.representation_refs || []).join(', ') || 'None')}</div>
          <div><strong>Activities:</strong> ${escapeHtml((row.activity_refs || []).join(', ') || 'None')}</div>
        </div>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">${coreActions}${visualActions}${portableActions}</div>
        ${findings}
      </div>
    `;
  }

  function focusSelectedRung() {
    if (!state.selected_rung_key) return;
    const details = document.getElementById('card-' + state.selected_rung_key.rung);
    if (!details) return;
    details.open = true;
    const summary = details.querySelector ? details.querySelector('summary') : null;
    if (summary && typeof summary.focus === 'function') summary.focus({ preventScroll: true });
    if (typeof details.scrollIntoView === 'function') details.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function readSelectionFromLocation(matrixId) {
    if (!window.location || typeof URLSearchParams === 'undefined') return;
    const params = new URLSearchParams(window.location.search || '');
    const queryMatrix = params.get('matrix');
    const queryRung = params.get('rung');

    if (!queryMatrix && !queryRung) {
      state.selected_rung_key = null;
      clearAtlasFinding();
      return;
    }
    if (!queryMatrix || !queryRung) {
      state.selected_rung_key = null;
      setAtlasFinding('ATLAS_TARGET_INCOMPLETE', 'Deep links require both matrix and rung.');
      return;
    }
    if (queryMatrix !== matrixId) {
      state.selected_rung_key = null;
      setAtlasFinding('ATLAS_TARGET_NOT_FOUND', 'Deep-link matrix does not match this Atlas host: ' + queryMatrix + '.');
      return;
    }

    const resolution = resolveAtlasComposite(currentSubjectPayload(), queryMatrix, queryRung);
    state.selected_rung_key = resolution.row ? { matrix_id: queryMatrix, rung: queryRung } : null;
    if (resolution.status === 'READY') clearAtlasFinding();
    else setAtlasFinding(resolution.code, resolution.message);
  }

  function bindHistory(matrixId) {
    if (state.history_bound || !window.addEventListener) return;
    window.addEventListener('popstate', function() {
      readSelectionFromLocation(matrixId);
      renderProgressionLane();
      renderMultiResolutionCards();
      focusSelectedRung();
    });
    state.history_bound = true;
  }

  function selectRung(rungId, options) {
    const opts = Object.assign({ pushHistory: true, focus: true }, options || {});
    if (!state.matrix) return;
    const resolution = resolveAtlasComposite(currentSubjectPayload(), state.matrix.matrix_id, rungId);
    if (!resolution.row) {
      state.selected_rung_key = null;
      setAtlasFinding(resolution.code, resolution.message);
      renderProgressionLane();
      renderMultiResolutionCards();
      return;
    }

    state.selected_rung_key = { matrix_id: state.matrix.matrix_id, rung: rungId };
    if (resolution.status === 'READY') clearAtlasFinding();
    else setAtlasFinding(resolution.code, resolution.message);

    if (opts.pushHistory && window.history && window.location) {
      const url = new URL(window.location.href);
      url.searchParams.set('matrix', state.matrix.matrix_id);
      url.searchParams.set('rung', rungId);
      window.history.pushState({ atlas: state.selected_rung_key }, '', url.href);
    }

    renderProgressionLane();
    renderMultiResolutionCards();
    if (opts.focus) focusSelectedRung();
  }

  function initAtlas(matrixId) {
    if (!window.GRADE9V3 || !window.GRADE9V3.subjects) {
      console.error("window.GRADE9V3 is not loaded. Ensure public/data/data.js is linked.");
      renderAtlasFatalFinding('ATLAS_DATA_UNAVAILABLE', 'Canonical generated Atlas data is not loaded.');
      return;
    }

    // Locate matrix in GRADE9V3
    let foundMatrix = null;
    let foundSubject = null;
    for (const [subjName, subj] of Object.entries(window.GRADE9V3.subjects)) {
      if (subj.matrices) {
        for (const m of subj.matrices) {
          if (m.matrix_id === matrixId) {
            foundMatrix = m;
            foundSubject = subjName;
            break;
          }
        }
      }
      if (foundMatrix) break;
    }

    if (!foundMatrix) {
      console.error("Matrix not found in canonical records:", matrixId);
      renderAtlasFatalFinding('ATLAS_TARGET_NOT_FOUND', 'Matrix not found in canonical records: ' + matrixId);
      return;
    }

    state.matrix = foundMatrix;
    state.subject = foundSubject;

    const subjectPayload = currentSubjectPayload();
    if (!subjectPayload || subjectPayload.atlas_index_contract_version !== ATLAS_INDEX_CONTRACT_VERSION) {
      setAtlasFinding(
        'ATLAS_INDEX_VERSION_UNSUPPORTED',
        'Expected AtlasIndex 2.0 for ' + foundSubject + '; canonical navigation is disabled.'
      );
    }

    // Learner evidence state remains independent from explicit Atlas inspection state.
    loadLocalStorageState();
    bindHistory(matrixId);
    readSelectionFromLocation(matrixId);

    // Render all surfaces
    renderHeader();
    renderInputDrawer();
    renderProgressionLane();
    renderMultiResolutionCards();
    renderNeedMap();
    renderCoreBuilder();
    focusSelectedRung();
  }

  // --- Storage & State Persistence ---
  function getStorageKey() {
    return `grade9v3_atlas_${state.matrix ? state.matrix.matrix_id : 'default'}`;
  }

  function loadLocalStorageState() {
    try {
      const raw = localStorage.getItem(getStorageKey());
      if (raw) {
        const parsed = JSON.parse(raw);
        state.knowledge_percentage = parsed.knowledge_percentage !== undefined ? parsed.knowledge_percentage : null;
        state.diagnostic_rows = Array.isArray(parsed.diagnostic_rows) ? parsed.diagnostic_rows : [];
        state.overlay_active = parsed.overlay_active !== undefined ? parsed.overlay_active : true;
        if (parsed.request_config) {
          state.request_config = Object.assign(state.request_config, parsed.request_config);
        }
      }
    } catch (e) {
      console.warn("Could not read localStorage:", e);
    }
  }

  function saveLocalStorageState() {
    try {
      const payload = {
        knowledge_percentage: state.knowledge_percentage,
        diagnostic_rows: state.diagnostic_rows,
        overlay_active: state.overlay_active,
        request_config: state.request_config
      };
      localStorage.setItem(getStorageKey(), JSON.stringify(payload));
      updateStorageStatusBadge("💾 LocalStorage Synced");
    } catch (e) {
      console.warn("Could not write localStorage:", e);
    }
  }

  function updateStorageStatusBadge(text) {
    const badge = document.getElementById('storageStatusBadge');
    if (badge) {
      badge.textContent = text;
      badge.className = "badge ok";
    }
  }

  function activityMatchesStep(activity, stepId) {
    return Boolean(stepId && (activity.teaching_step_refs || []).includes(stepId));
  }

  const DIAGNOSTIC_STAGES = ['CONCEPT', 'SETUP', 'EXECUTION', 'CARELESS', 'UNKNOWN'];
  const GAP_RESULTS = ['MISSING', 'UNCERTAIN'];

  function diagnosticDimensionIndex(stage) {
    const map = { CONCEPT: 0, SETUP: 1, EXECUTION: 2, CARELESS: 3, UNKNOWN: 99 };
    return Object.prototype.hasOwnProperty.call(map, stage) ? map[stage] : 99;
  }

  function deriveAtlasAddress(rungId, stepIdx, stage) {
    const dimIdx = diagnosticDimensionIndex(stage);
    if (stepIdx === 99) return rungId + '.99';
    if (dimIdx === 99) return rungId + '.' + stepIdx + '.99';
    return rungId + '.' + stepIdx + '.' + dimIdx;
  }

  function validateDiagnosticRow(rungs, row, index) {
    const raw = row || {};
    const capRef = raw.capability_ref;
    if (!capRef) return { error: 'capability_ref is required; no fuzzy mapping is allowed' };

    const matchedRung = rungs.find(rg => rg.capability && rg.capability.id === capRef);
    if (!matchedRung) return { error: "Unknown capability ref '" + capRef + "' in matrix" };

    if (raw.rung_ref && raw.rung_ref !== matchedRung.rung) {
      return { error: "rung_ref '" + raw.rung_ref + "' conflicts with capability_ref '" + capRef + "' (" + matchedRung.rung + ')' };
    }

    if (!GAP_RESULTS.includes(raw.result)) {
      return { error: 'result must be MISSING or UNCERTAIN for a diagnostic gap row' };
    }

    const stage = raw.error_stage ? String(raw.error_stage).toUpperCase() : 'UNKNOWN';
    if (!DIAGNOSTIC_STAGES.includes(stage)) {
      return { error: "error_stage '" + raw.error_stage + "' is not in the diagnostic vocabulary" };
    }

    let score = null;
    if (raw.score !== undefined && raw.score !== null) {
      if (typeof raw.score !== 'number' || !Number.isFinite(raw.score) || raw.score < 0 || raw.score > 100) {
        return { error: 'score, when supplied, must be a numeric value from 0 to 100' };
      }
      score = raw.score;
    }

    if (typeof raw.observed !== 'string' || !raw.observed.trim()) {
      return { error: 'observed is required and must contain the answer-sheet evidence used for this gap' };
    }

    const tpath = (matchedRung.microtopic && matchedRung.microtopic.teaching_path) || [];
    let repairRef = null;
    let warning = null;
    if (raw.repair_ref) {
      const step = tpath.find(s => s.id === raw.repair_ref);
      if (step) repairRef = step.id;
      else warning = 'Row ' + (index + 1) + ": Unrecognized repair_ref '" + raw.repair_ref + "' on " + matchedRung.rung + '; kept the capability-level gap and discarded only the unsupported narrow target.';
    }

    return {
      accepted: {
        question_ref: raw.question_ref || null,
        capability_ref: capRef,
        rung_ref: matchedRung.rung,
        repair_ref: repairRef,
        result: raw.result,
        error_stage: stage,
        score,
        observed: raw.observed.trim()
      },
      warning
    };
  }

  function resolveNeedTargetsFor(matrix, knowledgePercentage, diagnosticRows) {
    const rungs = (matrix && matrix.rungs) || [];
    const defaultRungs = rungs.filter(r => r.default_entry_eligible);
    const sortedDefault = [...defaultRungs].sort((a, b) => a.ladder_position - b.ladder_position);
    const targets = [];

    (diagnosticRows || []).forEach((row, index) => {
      const checked = validateDiagnosticRow(rungs, row, index);
      if (checked.error) return;
      const clean = checked.accepted;
      const matchedRung = rungs.find(r => r.capability && r.capability.id === clean.capability_ref);
      if (!matchedRung) return;

      const tpath = (matchedRung.microtopic && matchedRung.microtopic.teaching_path) || [];
      const rawStepIdx = clean.repair_ref ? tpath.findIndex(s => s.id === clean.repair_ref) : -1;
      const stepIdx = rawStepIdx >= 0 ? rawStepIdx : 99;
      const matchedStep = rawStepIdx >= 0 ? tpath[rawStepIdx] : null;
      let fallbackLevel = 'EXACT_LEAF_DIMENSION';
      if (stepIdx === 99) fallbackLevel = 'CAPABILITY_ONLY_FALLBACK';
      else if (clean.error_stage === 'UNKNOWN') fallbackLevel = 'LEAF_UNKNOWN_DIMENSION_FALLBACK';

      targets.push({
        address: deriveAtlasAddress(matchedRung.rung, stepIdx, clean.error_stage),
        rung: matchedRung.rung,
        rung_obj: matchedRung,
        capability_ref: clean.capability_ref,
        repair_ref: clean.repair_ref,
        error_stage: clean.error_stage,
        score: clean.score,
        observed: clean.observed,
        result: clean.result,
        fallback_level: fallbackLevel,
        step_action: matchedStep ? matchedStep.action : null,
        why: 'Scanned gap on ' + clean.capability_ref + (clean.repair_ref ? ' step ' + clean.repair_ref : '') + ' at stage ' + clean.error_stage
      });
    });

    let estimateEntryRung = null;
    let quickCheckRungs = [];
    if (typeof knowledgePercentage === 'number' && Number.isFinite(knowledgePercentage) && sortedDefault.length > 0) {
      const pct = Math.max(0, Math.min(100, knowledgePercentage));
      const eligible = sortedDefault.filter(r => r.ladder_position <= pct);
      estimateEntryRung = eligible.length > 0 ? eligible[eligible.length - 1] : sortedDefault[0];
      quickCheckRungs = eligible.filter(r => r.rung !== estimateEntryRung.rung).map(r => r.rung);

      if (targets.length === 0) {
        targets.push({
          address: estimateEntryRung.rung,
          rung: estimateEntryRung.rung,
          rung_obj: estimateEntryRung,
          capability_ref: estimateEntryRung.capability ? estimateEntryRung.capability.id : null,
          repair_ref: null,
          error_stage: 'UNKNOWN',
          score: null,
          observed: 'Owner supplied rough knowledge estimate: ' + pct + '%',
          result: 'UNCERTAIN',
          fallback_level: 'KNOWLEDGE_ESTIMATE_COORDINATE',
          step_action: null,
          why: 'Knowledge estimate ' + pct + '% selects tentative start coordinate ' + estimateEntryRung.rung + '; it does not prove prior rungs mastered.'
        });
      }
    }

    return {
      targets,
      primary_target: targets[0] || null,
      estimateEntryRung,
      quickCheckRungs,
      canonicalDefaultEntry: sortedDefault[0] || null
    };
  }

  function resolveNeedTargets() {
    return resolveNeedTargetsFor(state.matrix, state.knowledge_percentage, state.diagnostic_rows);
  }

  // --- Header Renderer ---
  function renderHeader() {
    const m = state.matrix;
    const titleEl = document.getElementById('atlasTopicTitle');
    if (titleEl) titleEl.textContent = m.topic || m.subtopic;
    const subEl = document.getElementById('atlasSubtopicSubtitle');
    if (subEl) subEl.textContent = `Subtopic: ${m.subtopic} · ${m.matrix_id}`;

    // Update Summary Strip
    const rungs = m.rungs || [];
    const defCount = rungs.filter(r => r.default_entry_eligible).length;
    const nonDefCount = rungs.length - defCount;

    const rungsStat = document.getElementById('statRungCount');
    if (rungsStat) {
      rungsStat.innerHTML = `${rungs.length} Rungs <span class="badge ok">${defCount} Default</span>` +
        (nonDefCount > 0 ? ` <span class="badge purple">${nonDefCount} Non-Default</span>` : '');
    }

    const diffStat = document.getElementById('statDiffMix');
    if (diffStat) {
      let hard = 0, med = 0;
      rungs.forEach(r => {
        const b = r.microtopic ? r.microtopic.intrinsic_badge : 'MEDIUM';
        if (b === 'HARD') hard++; else med++;
      });
      diffStat.innerHTML = `<span class="badge hold">${hard} Hard</span> <span class="badge warn">${med} Medium</span>`;
    }

    const qCount = rungs.reduce((acc, r) => acc + (r.questions ? r.questions.length : 0), 0);
    const qStat = document.getElementById('statQuestionCount');
    if (qStat) qStat.textContent = `${qCount} Canonical Items`;

  }

  // --- Input Drawer Renderer (GAP-WEB-002, GAP-WEB-003, GAP-WEB-004) ---
  function renderInputDrawer() {
    const slider = document.getElementById('knowledgeSlider');
    const input = document.getElementById('knowledgeInput');
    const toggle = document.getElementById('overlayToggle');
    const statusTxt = document.getElementById('estimateStatusText');

    if (slider) slider.value = state.knowledge_percentage !== null ? state.knowledge_percentage : 50;
    if (input) input.value = state.knowledge_percentage !== null ? state.knowledge_percentage : '';
    if (toggle) toggle.checked = state.overlay_active;

    if (statusTxt) {
      if (state.knowledge_percentage === null) {
        statusTxt.textContent = "No estimate supplied → canonical browse mode (no learner placement)";
        statusTxt.style.color = "var(--text-muted)";
      } else {
        statusTxt.textContent = `Active estimate: ${state.knowledge_percentage}% (Ladder coordinate, not mastery)`;
        statusTxt.style.color = "var(--accent)";
      }
    }

    // Render Validation Report if available
    renderValidationReport();
  }

  function renderValidationReport() {
    const reportBox = document.getElementById('importValidationReport');
    if (!reportBox) return;

    if (!state.validation_report) {
      reportBox.style.display = 'none';
      return;
    }

    reportBox.style.display = 'block';
    const rep = state.validation_report;
    reportBox.innerHTML = `
      ${rep.fatal_error ? `<div style="font-size:12px;font-weight:700;color:var(--chip-hold-text);margin-bottom:8px;">${escapeHtml(rep.fatal_error)}</div>` : ''}
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <strong style="font-size: 13px; color: ${rep.rejected.length === 0 ? 'var(--chip-ok-text)' : 'var(--chip-warn-text)'};">
          📋 Diagnostic Validation Report: Accepted ${rep.accepted.length} / Rejected ${rep.rejected.length}
        </strong>
        <span class="badge neutral">${rep.provenance}</span>
      </div>
      ${rep.rejected.length > 0 ? `
        <div style="font-size: 12px; color: var(--chip-hold-text); margin-bottom: 6px;">
          <strong>Isolated Rows:</strong>
          <ul style="padding-left: 18px; margin-top: 4px;">
            ${rep.rejected.map(r => `<li>${r.reason}: <code>${JSON.stringify(r.raw)}</code></li>`).join('')}
          </ul>
        </div>
      ` : ''}
      ${rep.warnings.length > 0 ? `
        <div style="font-size: 12px; color: var(--chip-warn-text); margin-bottom: 6px;">
          <strong>Fallbacks Applied:</strong>
          <ul style="padding-left: 18px; margin-top: 4px;">
            ${rep.warnings.map(w => `<li>${w}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
    `;
  }

  // --- Progression Lane Renderer ---
  function renderProgressionLane() {
    const resolved = resolveNeedTargets();
    const laneContainer = document.getElementById('progressionLaneContainer');
    if (!laneContainer) return;

    const rungs = state.matrix.rungs || [];
    const defaultRungs = rungs.filter(r => r.default_entry_eligible);
    const nonDefaultRungs = rungs.filter(r => !r.default_entry_eligible);
    const subjectPayload = currentSubjectPayload();
    const contractReady = Boolean(
      subjectPayload && subjectPayload.atlas_index_contract_version === ATLAS_INDEX_CONTRACT_VERSION
    );

    const defaultHtml = defaultRungs.map(r => renderRungNode(r, resolved, contractReady)).join('');
    const nonDefaultHtml = nonDefaultRungs.map(r => {
      const selected = state.selected_rung_key
        && state.selected_rung_key.matrix_id === state.matrix.matrix_id
        && state.selected_rung_key.rung === r.rung;
      return `
        <div class="extension-box">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
            <div>
              <span class="badge purple" style="margin-bottom:4px;">Non-Default · Explicit Demand</span>
              <h4 style="font-size:14px;font-weight:700;">${escapeHtml(r.rung)} · ${escapeHtml(r.microtopic ? r.microtopic.title : r.rung)}</h4>
            </div>
            <span class="badge ${(r.microtopic || {}).intrinsic_badge === 'HARD' ? 'hold' : 'warn'}">${escapeHtml((r.microtopic || {}).intrinsic_badge || 'MEDIUM')}</span>
          </div>
          <p style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">
            <code>${escapeHtml(r.capability ? r.capability.id : 'NO_CAP')}</code> · Authored position ${escapeHtml(r.ladder_position)}
          </p>
          <button type="button" class="btn-sm" style="font-size:11px;padding:3px 8px;"
                  aria-controls="card-${escapeHtml(r.rung)}" aria-pressed="${selected ? 'true' : 'false'}"
                  ${contractReady ? '' : 'disabled'}
                  onclick="window.ATLAS.openRung('${escapeHtml(r.rung)}')">
            Inspect canonical rung ↓
          </button>
        </div>
      `;
    }).join('');

    laneContainer.innerHTML = `
      ${atlasFindingHtml()}
      <div class="lane-heading default">
        <span>●</span> Authored Default Route (${defaultRungs.length} Rungs)
      </div>
      <div class="cluster-wrapper">
        <div class="cluster-box">
          <div class="cluster-title">
            <span>Canonical authored order</span>
            <span>Positions are labels, not browser-created curriculum phases</span>
          </div>
          <div class="rung-flow">
            ${defaultHtml}
          </div>
        </div>
      </div>
      ${nonDefaultRungs.length > 0 ? `
        <div class="lane-heading non-default">
          <span>◆</span> Non-Default Explicit-Demand Extensions (${nonDefaultRungs.length} Rungs)
        </div>
        <div class="non-default-grid">${nonDefaultHtml}</div>
      ` : ''}
    `;
  }

  function renderRungNode(rung, resolved, contractReady) {
    const rId = rung.rung;
    const target = resolved.targets.find(t => t.rung === rId);
    const isQuickCheck = resolved.quickCheckRungs.includes(rId);
    const selected = state.selected_rung_key
      && state.selected_rung_key.matrix_id === state.matrix.matrix_id
      && state.selected_rung_key.rung === rId;

    let badgeHtml = '';
    let nodeClass = 'rung-node';
    if (selected) nodeClass += ' is-selected';

    if (state.overlay_active && target) {
      if (target.result === 'MISSING') {
        nodeClass += ' has-gap';
        badgeHtml = `<span class="badge hold">GAP: ${escapeHtml(target.error_stage)}</span>`;
      } else if (target.result === 'UNCERTAIN') {
        nodeClass += ' has-uncertain';
        badgeHtml = '<span class="badge warn">UNCERTAIN</span>';
      }
    } else if (state.overlay_active && isQuickCheck) {
      nodeClass += ' is-quick-check';
      badgeHtml = '<span class="badge phy">QUICK CHECK</span>';
    }

    return `
      <button type="button" class="${nodeClass}" style="width:100%;text-align:left;font:inherit;color:inherit;"
              aria-controls="card-${escapeHtml(rId)}" aria-pressed="${selected ? 'true' : 'false'}"
              ${contractReady ? '' : 'disabled'}
              onclick="window.ATLAS.openRung('${escapeHtml(rId)}')">
        <span style="display:flex;align-items:center;gap:8px;overflow:hidden;">
          <span class="node-id">${escapeHtml(rId)}</span>
          <span class="node-title">${escapeHtml(rung.microtopic ? rung.microtopic.title : rung.rung)}</span>
        </span>
        <span style="display:flex;align-items:center;gap:6px;">
          <span class="badge neutral">${escapeHtml(rung.ladder_position)}</span>
          ${badgeHtml}
        </span>
      </button>
    `;
  }

  // --- Multi-Resolution Cards Renderer (Level 1, 2, 3) (GAP-WEB-008) ---
  function renderMultiResolutionCards() {
    const container = document.getElementById('rungCardsContainer');
    if (!container) return;

    const resolved = resolveNeedTargets();
    const rungs = state.matrix.rungs;

    container.innerHTML = rungs.map(r => {
      const isDef = r.default_entry_eligible;
      const target = resolved.targets.find(t => t.rung === r.rung);
      const cap = r.capability || {};
      const micro = r.microtopic || {};
      const tpath = micro.teaching_path || [];
      const atlasResolution = resolveAtlasComposite(currentSubjectPayload(), state.matrix.matrix_id, r.rung);
      const isSelected = Boolean(
        state.selected_rung_key
        && state.selected_rung_key.matrix_id === state.matrix.matrix_id
        && state.selected_rung_key.rung === r.rung
      );
      const canonicalAtlasHtml = renderCanonicalAtlasDetails(atlasResolution);


      // Level 2 & 3: Semantic Leaves & Diagnostic Dimension Cells
      let semanticLeavesHtml = tpath.map((step, idx) => {
        const stepTargets = resolved.targets.filter(t => t.rung === r.rung && t.repair_ref === step.id);
        const stepActivities = (r.activities || []).filter(act => activityMatchesStep(act, step.id));
        const stepActivitiesHtml = stepActivities.map(act => {
          const gcdr = act.support_route && act.support_route.kind === 'GCDR';
          const label = gcdr ? 'Graphical breakdown' : 'Exact repair';
          const status = gcdr && act.support_route.conformance_status
            ? ` · ${act.support_route.conformance_status}`
            : '';
          const audit = gcdr ? act.support_route.quality_audit_status : null;
          const counts = gcdr ? (act.support_route.quality_check_counts || {}) : {};
          const pending = counts.PENDING || 0;
          const failed = counts.FAIL || 0;
          const openFindings = gcdr ? (act.support_route.unresolved_findings_count || 0) : 0;
          const auditClass = audit === 'PASS'
            ? 'ok'
            : (failed || openFindings ? 'hold' : 'warn');
          const auditBadge = audit
            ? `<span class="badge ${auditClass}" style="font-size:9px;margin-left:4px;">
                 Audit ${audit}${pending ? ` · ${pending} pending` : ''}${failed ? ` · ${failed} fail` : ''}
               </span>`
            : '';
          const mapping = gcdr && act.support_route.external_state_mapping
            ? ` · mapping ${act.support_route.external_state_mapping}`
            : '';
          return renderActivityAction(
            r.rung,
            act,
            (gcdr ? 'Graphical breakdown' : 'Exact repair') + (audit ? ' · audit ' + audit : '')
          );
        }).join('');
        
        // Level 3 dimensions remain independent; never average them into a rung score.
        const dimensions = [...DIAGNOSTIC_STAGES];
        const dimCellsHtml = dimensions.map(dim => {
          const dimTargets = stepTargets.filter(t => t.error_stage === dim);
          const isCurrentDim = dimTargets.length > 0;
          let cellStyle = "padding: 3px 8px; border-radius: 4px; font-size: 11px; font-family: var(--font-mono); border: 1px solid var(--border);";
          if (isCurrentDim) {
            cellStyle += " background: var(--chip-hold-bg); border-color: var(--chip-hold-border); color: var(--chip-hold-text); font-weight: 700;";
          } else {
            cellStyle += " background: var(--bg); color: var(--text-muted);";
          }
          const scores = dimTargets.filter(t => t.score !== null).map(t => t.score + '%');
          const scoreText = scores.length ? ' (' + scores.join(', ') + ')' : '';
          return '<span style="' + cellStyle + '">' + dim + scoreText + '</span>';
        }).join(' ');

        return `
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 10px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge phy" style="font-weight: 700;">Leaf ${r.rung}.${idx}</span>
                <code style="color: var(--accent); font-weight: 600;">${step.id}</code>
                <span style="font-size: 12px; font-weight: 600;">${step.action}</span>
              </div>
              <span class="badge neutral">${step.role || 'TRANSFORM'}</span>
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px; line-height: 1.5;">
              <strong>Validity Rationale:</strong> ${step.why_valid}
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <span style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; font-weight: 600;">Diagnostic Dimensions:</span>
              ${dimCellsHtml}
            </div>
            ${stepActivitiesHtml ? `
              <div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--border);">
                <span style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; font-weight: 600;">
                  Exact Repair Surface:
                </span>
                <div>${stepActivitiesHtml}</div>
              </div>
            ` : ''}
          </div>
        `;
      }).join('');

      // Activities linked to this rung
      let activitiesHtml = '';
      if (r.activities && r.activities.length > 0) {
        activitiesHtml = r.activities.map(act => {
          const leafText = (act.teaching_step_refs || []).length
            ? ` · Leaves: ${act.teaching_step_refs.join(', ')}`
            : '';
          return `
            <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 6px; padding: 12px; margin-top: 12px;">
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                <span class="badge phy">Governed Activity Resource</span>
                ${act.activity_kind ? `<span class="badge neutral">${act.activity_kind}</span>` : ''}
                ${act.support_route ? `<span class="badge neutral">${act.support_route.conformance_status || 'GCDR'}</span>` : ''}
                <strong style="color: #fff; font-size: 13px;">${act.title}</strong>
              </div>
              <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
                ${act.section || 'Interactive explorer canonically registered in library records.'}${leafText}
              </p>
              ${act.support_route ? `
                <p style="font-size: 11px; color: var(--text-dim); margin-bottom: 8px;">
                  Parallel graphical support route · recommended for:
                  ${(act.support_route.recommended_when || []).join(', ')}
                </p>
              ` : ''}
              ${renderActivityAction(r.rung, act, 'Launch Activity')}
            </div>
          `;
        }).join('');
      }

      // Controlled variation
      let variationHtml = (r.controlled_variation || []).map(v => `
        <div class="variation-step">
          <div><span class="variation-label">Phase ${v.phase}:</span> Vary <em>${v.vary}</em> while holding <em>${v.hold}</em>.</div>
          <div style="color: var(--text-muted); margin-top: 2px;">→ Notice: <strong>${v.notice}</strong></div>
        </div>
      `).join('');

      // Misconceptions
      let misHtml = (micro.misconceptions || []).map(m => `
        <div style="margin-bottom: 8px;">
          <div class="quote-box misconception">
            <strong>Wrong Idea:</strong> "${m.wrong_idea}"
          </div>
          ${m.diagnostic_prompt ? `<div style="font-size: 12px; color: var(--text-dim); margin: 4px 0 2px 0;"><strong>Diagnostic:</strong> ${m.diagnostic_prompt}</div>` : ''}
          <div class="quote-box repair" style="margin-top: 4px;">
            <strong>Repair:</strong> ${m.repair}
          </div>
        </div>
      `).join('');

      return `
        <details class="rung-card ${isDef ? '' : 'non-default'}" id="card-${r.rung}" ${isSelected ? 'open' : ''}>
          <summary class="rung-summary">
            <div class="summary-left">
              <span class="rung-num-pill">${r.rung}</span>
              <div>
                <div class="summary-title-text">${micro.title || r.rung}</div>
                <div style="font-size: 12px; color: var(--text-dim); font-family: var(--font-mono);">
                  ${micro.id || ''} &middot; ${cap.id || ''}
                </div>
              </div>
            </div>
            <div class="summary-right">
              ${target && state.overlay_active ? `<span class="badge ${target.result === 'MISSING' ? 'hold' : 'warn'}">${target.address} ${target.result}</span>` : ''}
              <span class="badge ${isDef ? 'ok' : 'purple'}">${isDef ? 'Default Lane' : 'Branch Extension'}</span>
              <span class="badge ${micro.intrinsic_badge === 'HARD' ? 'hold' : 'warn'}">${micro.intrinsic_badge || 'MEDIUM'}</span>
              <span style="color: var(--text-dim); font-size: 12px;">Pos: ${r.ladder_position}</span>
            </div>
          </summary>

          <div class="card-body">
            ${canonicalAtlasHtml}
            <!-- Capability Metadata Row -->
            <div class="card-meta-row">
              <div class="meta-item">
                <span class="meta-item-label">Primary Capability</span>
                <span class="meta-item-val">${cap.id || 'None'}</span>
              </div>
              <div class="meta-item">
                <span class="meta-item-label">Capability Action</span>
                <span class="meta-item-val" style="font-family: var(--font-sans);">${cap.action || 'None'}</span>
              </div>
              <div class="meta-item">
                <span class="meta-item-label">Prerequisites</span>
                <span class="meta-item-val">${(cap.prerequisite_refs || []).join(', ') || 'None'}</span>
              </div>
              <div class="meta-item">
                <span class="meta-item-label">Success Criterion</span>
                <span class="meta-item-val" style="font-family: var(--font-sans); color: var(--text-muted);">${cap.success_criterion || 'None'}</span>
              </div>
            </div>

            <!-- Level 2 & 3: Semantic Leaves & Diagnostic Matrix -->
            <div style="margin: 12px 0;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <h4 style="font-size: 13px; font-weight: 700; color: var(--accent); margin: 0;">
                  🌿 Level 2 Semantic Leaves &amp; Level 3 Diagnostic Cells:
                </h4>
                <span style="font-size: 11px; color: var(--text-dim);">
                  Diagnostic cells are read-only projections of imported answer-sheet evidence.
                </span>
              </div>
              ${semanticLeavesHtml || '<p style="font-size: 12px; color: var(--text-muted);">No distinct teaching-path steps recorded.</p>'}
            </div>

            <!-- Controlled Variation & Misconceptions -->
            <div class="card-grid">
              <div style="display: flex; flex-direction: column; gap: 14px;">
                <div class="block-subcard">
                  <div class="subcard-heading">🎯 Inferential Jump</div>
                  <div class="quote-box">${micro.inferential_jump || 'Canonical jump not declared.'}</div>
                </div>
                ${variationHtml ? `
                  <div class="block-subcard">
                    <div class="subcard-heading">⚖️ Controlled Variation</div>
                    <div>${variationHtml}</div>
                  </div>
                ` : ''}
                ${misHtml ? `
                  <div class="block-subcard">
                    <div class="subcard-heading">⚠️ Misconceptions & Repair</div>
                    <div>${misHtml}</div>
                  </div>
                ` : ''}
              </div>

              <div style="display: flex; flex-direction: column; gap: 14px;">
                ${micro.exit_task ? `
                  <div class="block-subcard">
                    <div class="subcard-heading">🏁 Exit Task & Criterion</div>
                    ${(micro.exit_task.task || micro.exit_task.prompt) ? `<div style="font-size: 13px; font-weight: 600; margin-bottom: 6px; line-height: 1.5;">${micro.exit_task.task || micro.exit_task.prompt}</div>` : ''}
                    <div class="quote-box repair" style="font-size: 12px; line-height: 1.5;">
                      <strong>Success:</strong> ${
                        micro.exit_task.success_criterion ||
                        (micro.exit_task.answer && (micro.exit_task.answer.summary || (typeof micro.exit_task.answer === 'string' ? micro.exit_task.answer : ''))) ||
                        cap.success_criterion ||
                        'Complete task demonstrating criterion.'
                      }
                    </div>
                  </div>
                ` : ''}
                ${activitiesHtml}
                <div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border);">
                  ${(r.questions && r.questions.length > 0) ? `
                    <div class="block-subcard" style="margin-bottom: 8px;">
                      <div class="subcard-heading">📝 Canonical Practice Questions (${r.questions.length})</div>
                      ${r.questions.map(q => `
                        <div style="margin-bottom:6px;padding:6px 8px;background:var(--bg);border:1px solid var(--border);border-radius:4px;">
                          <div style="display:flex;justify-content:space-between;align-items:center;">
                            <strong style="font-size:11px;font-family:var(--font-mono);color:var(--accent);">${escapeHtml(q.id)}</strong>
                            <a href="../../question-bank/index.html?q=${encodeURIComponent(q.id)}#${encodeURIComponent(q.id)}" style="font-size:11px;color:var(--accent);text-decoration:none;" target="_blank">Open in Question Bank &nearr;</a>
                          </div>
                          ${q.stem ? `<div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${escapeHtml(q.stem)}</div>` : ''}
                        </div>
                      `).join('')}
                    </div>
                  ` : ''}
                  <a href="../../question-bank/index.html?subject=${encodeURIComponent(state.matrix.subject || '')}&mode=study" class="btn outline" style="display:inline-block;font-size:11px;padding:4px 8px;color:var(--accent);border:1px solid var(--border);border-radius:4px;text-decoration:none;">
                    🎯 Practice Topic in Question Bank &rarr;
                  </a>
                </div>
              </div>
            </div>
          </div>
        </details>
      `;
    }).join('');

  }

  // --- Need Map Renderer (GAP-WEB-010) ---
  function renderNeedMap() {
    const needBox = document.getElementById('needMapContainer');
    if (!needBox) return;

    const resolved = resolveNeedTargets();
    if (resolved.targets.length === 0) {
      needBox.innerHTML = `
        <div class="section-title">
          <span>🎯 Active Need Map & Focus Targets</span>
          <span class="count">Canonical Browse Mode</span>
        </div>
        <div style="background: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-bottom: 24px;">
          <strong>No learner focus supplied.</strong>
          <p style="font-size: 12px; color: var(--text-muted); margin: 6px 0 0 0;">
            The Atlas remains a canonical map. No rung is claimed as learner placement,
            no prerequisite is claimed held, and absence from a gap table is not DEMONSTRATED.
          </p>
        </div>
      `;
      return;
    }
    needBox.innerHTML = `
      <div class="section-title">
        <span>🎯 Active Need Map & Focus Targets</span>
        <span class="count">${resolved.targets.length} Identified Need(s)</span>
      </div>
      ${resolved.estimateEntryRung ? `
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 10px;">
          Broad owner-estimate route: <strong>${resolved.estimateEntryRung.rung}</strong>.
          This is a routing prior only; imported answer-sheet gaps remain the local focus.
        </div>
      ` : ''}
      <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 24px;">
        ${resolved.targets.map((t, idx) => {
          const exactActivities = ((t.rung_obj && t.rung_obj.activities) || [])
            .filter(act => activityMatchesStep(act, t.repair_ref));
          const exactActivityHtml = exactActivities.map(act => {
            const gcdr = act.support_route && act.support_route.kind === 'GCDR';
            return renderActivityAction(
              t.rung,
              act,
              gcdr ? 'Open graphical breakdown' : 'Open exact repair'
            );
          }).join('');
          return `
          <div style="background: var(--bg-panel); border: 1px solid ${idx === 0 ? 'var(--accent)' : 'var(--border)'}; border-radius: 8px; padding: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 8px;">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span class="badge ${t.result === 'MISSING' ? 'hold' : 'warn'}" style="font-size: 12px;">${t.address}</span>
                <strong style="color: #fff;">${t.rung} · ${t.capability_ref}</strong>
              </div>
              <span class="badge neutral">${t.fallback_level}</span>
            </div>
            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px;">
              <strong>Observation:</strong> ${t.observed}
            </p>
            <div style="font-size: 12px; color: var(--text-dim); display: flex; gap: 14px; flex-wrap: wrap;">
              <span><strong>Why Focused:</strong> ${t.why}</span>
              ${t.repair_ref ? `<span><strong>Repair Target:</strong> <code>${t.repair_ref}</code></span>` : ''}
              ${t.error_stage ? `<span><strong>Failure Stage:</strong> <code>${t.error_stage}</code></span>` : ''}
            </div>
            ${exactActivityHtml ? `<div>${exactActivityHtml}</div>` : ''}
          </div>
        `;
        }).join('')}
      </div>
    `;
  }

  function buildAuthoringRequest(matrix, requestConfig, knowledgePercentage, requestId) {
    const cores = Array.isArray(requestConfig.cores) ? [...requestConfig.cores] : [];
    if (cores.length === 0) return null;

    const requestDoc = {
      request_id: requestId,
      subject: matrix.subject,
      subtopic: matrix.subtopic,
      bucket_id: matrix.bucket_id,
      requested_cores: cores
    };

    if (typeof knowledgePercentage === 'number' && Number.isFinite(knowledgePercentage)) {
      requestDoc.learner = {
        owner_estimate: {
          knowledge_percentage: Math.max(0, Math.min(100, Math.round(knowledgePercentage))),
          by: 'Topic Atlas owner input',
          instruction: 'Rough starting coordinate only; not evidence of prerequisite mastery'
        }
      };
    }

    const practice = {};
    if (cores.includes('CORE2A')) practice.CORE2A = { purpose: requestConfig.core2a_purpose };
    if (cores.includes('CORE2B') && requestConfig.core2b_purpose) {
      practice.CORE2B = { purpose: requestConfig.core2b_purpose };
    }
    if (Object.keys(practice).length > 0) requestDoc.practice = practice;
    return requestDoc;
  }

  // --- Core Request Builder & Planner Preview (GAP-WEB-013, GAP-WEB-014, GAP-WEB-015, GAP-WEB-016) ---
  function renderCoreBuilder() {
    const builderBox = document.getElementById('coreBuilderContainer');
    if (!builderBox) return;

    const resolved = resolveNeedTargets();
    const primary = resolved.primary_target;

    // Default suggestions based on failure stage (GAP-WEB-014)
    let suggestedEmphasis = primary ? "Core1B reconstruction + Core1A concept grounding" : "No learner-specific emphasis until optional learner input is supplied";
    if (primary && primary.error_stage === 'SETUP') suggestedEmphasis = "Core1B setup reconstruction + scaffolded Core2A";
    else if (primary && primary.error_stage === 'EXECUTION') suggestedEmphasis = "Core2A targeted practice (no broad Core1A reteach)";
    else if (primary && primary.error_stage === 'CARELESS') suggestedEmphasis = "Short Core2A / revision checking loop";
    else if (primary && primary.error_stage === 'UNKNOWN') suggestedEmphasis = "Parent-level diagnostic + Core1B repair";

    const isCore2B = state.request_config.cores.includes('CORE2B');
    const isCore2BPurposeMissing = isCore2B && !state.request_config.core2b_purpose;

    // Local selection preview only. Shared planning remains authoritative for readiness,
    // prerequisite closure, bridges, source custody and transfer legality.
    const coreStates = {};
    state.request_config.cores.forEach(c => {
      if (c === 'CORE2B') {
        if (!state.request_config.core2b_purpose) {
          coreStates[c] = { state: 'WAITING', reason: 'purpose required for planning' };
        } else if (state.request_config.core2b_purpose === 'NONE') {
          coreStates[c] = { state: 'WITHHELD', reason: 'owner selected NONE' };
        } else {
          coreStates[c] = { state: 'SELECTED', reason: 'purpose: ' + state.request_config.core2b_purpose };
        }
      } else if (c === 'CORE2A') {
        coreStates[c] = { state: 'SELECTED', reason: 'purpose: ' + state.request_config.core2a_purpose };
      } else {
        coreStates[c] = { state: 'SELECTED', reason: 'send to planner for readiness' };
      }
    });

    builderBox.innerHTML = `
      <div class="section-title">
        <span>⚡ Core Request Builder · Local Selection Preview</span>
        <span class="badge warn">Authoritative planner not executed in browser</span>
      </div>

      <div style="background: var(--bg-panel); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 24px;">
        <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);">
          <h4 style="font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 4px;">
            Target Need: ${primary ? `<code>${primary.address}</code> (${primary.rung} · ${primary.capability_ref})` : 'No learner focus supplied — canonical browse mode'}
          </h4>
          <p style="font-size: 13px; color: var(--text-muted); margin: 0;">
            Suggested Routing Emphasis: <strong style="color: var(--accent);">${suggestedEmphasis}</strong>
          </p>
        </div>

        <!-- Request Controls -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 18px;">
          <div>
            <label style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-dim); display: block; margin-bottom: 6px;">
              Requested Products (Cores):
            </label>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              ${['CORE1A', 'CORE1B', 'CORE2A', 'CORE2B', 'CORE1', 'CORE2'].map(c => `
                <label style="font-size: 12px; display: inline-flex; align-items: center; gap: 4px; background: var(--bg-card); padding: 4px 8px; border-radius: 4px; border: 1px solid var(--border); cursor: pointer;">
                  <input type="checkbox" ${state.request_config.cores.includes(c) ? 'checked' : ''} onchange="window.ATLAS.toggleCore('${c}', this.checked)">
                  <span>${c}</span>
                </label>
              `).join('')}
            </div>
          </div>

          <div>
            <label style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-dim); display: block; margin-bottom: 6px;">
              CORE2A Practice Purpose:
            </label>
            <select onchange="window.ATLAS.setCore2APurpose(this.value)" style="background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 6px 10px; border-radius: 4px; font-size: 12px; width: 100%;">
              ${['STARTER', 'PRACTICE', 'REVISION', 'COMPETITION'].map(p => `
                <option value="${p}" ${state.request_config.core2a_purpose === p ? 'selected' : ''}>${p}</option>
              `).join('')}
            </select>
          </div>

          ${isCore2B ? `
            <div>
              <label style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-dim); display: block; margin-bottom: 6px;">
                CORE2B Transfer Purpose:
              </label>
              <select onchange="window.ATLAS.setCore2BPurpose(this.value)" style="background: var(--bg); border: 1px solid ${isCore2BPurposeMissing ? 'var(--chip-hold-border)' : 'var(--border)'}; color: var(--text); padding: 6px 10px; border-radius: 4px; font-size: 12px; width: 100%;">
                <option value="">-- SELECT PURPOSE (REQUIRED) --</option>
                ${['PRACTICE', 'REVISION', 'COMPETITION', 'NONE'].map(p => `
                  <option value="${p}" ${state.request_config.core2b_purpose === p ? 'selected' : ''}>${p}</option>
                `).join('')}
              </select>
              ${isCore2BPurposeMissing ? `<span style="color: var(--chip-hold-text); font-size: 11px;">Purpose required when CORE2B is requested.</span>` : ''}
            </div>
          ` : ''}
        </div>

        <!-- Local selection preview; authoritative planning runs outside the browser. -->
        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 16px;">
          <h5 style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">
            Local Selection Preview:
          </h5>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
            ${state.request_config.cores.map(c => {
              const info = coreStates[c];
              let badgeColor = 'ok';
              if (info.state === 'WITHHELD') badgeColor = 'warn';
              if (info.state === 'WAITING' || info.state === 'BLOCKED') badgeColor = 'hold';
              return `<span class="badge ${badgeColor}">${c}: ${info.state} (${info.reason})</span>`;
            }).join('')}
          </div>
          <p style="font-size: 12px; color: var(--text-secondary); margin: 0;">
            <strong>Entry Basis:</strong> ${primary ? primary.fallback_level : 'NOT SUPPLIED'} &middot;
            <strong>Prerequisite Evidence:</strong> NOT ESTABLISHED BY ATLAS INPUT &middot;
            <strong>Targeted Teaching Steps:</strong> ${primary ? (primary.repair_ref || 'Capability / parent-level focus') : 'None'}
          </p>
          <p style="font-size: 11px; color: var(--text-dim); margin: 6px 0 0 0;">
            Product readiness, prerequisite closure and source/transfer holds are computed only after this request is handed to the repository planner.
          </p>
        </div>

        <!-- Action Bar: Export Request & CLI Instructions (GAP-WEB-016) -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button type="button" class="btn primary-phy" onclick="window.ATLAS.exportCoreRequest()">
              💾 Export Authoring Request JSON
            </button>
            <button type="button" class="btn outline" onclick="window.ATLAS.openPromptComposer()">
              Build from a question set ↗
            </button>
            <a href="../../../tools/run-builder/index.html" class="btn outline" target="_blank">
              Open Run Builder ↗
            </a>
          </div>
          <div style="font-size: 12px; color: var(--text-dim); font-family: var(--font-mono);">
            CLI: <code>python3 Shared/tools/plan_request.py --plan &lt;authoring-request.json&gt;</code>
          </div>
        </div>
      </div>
    `;
  }

  // --- External Diagnostic Import & Audit Engine (GAP-WEB-012) ---
  function handleDiagnosticImport(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      try {
        const doc = JSON.parse(e.target.result);
        const accepted = [];
        const rejected = [];
        const warnings = [];
        const rows = Array.isArray(doc.rows)
          ? doc.rows
          : (Array.isArray(doc.observations) ? doc.observations : null);
        if (!rows) throw new Error('Diagnostic document must contain rows[] or observations[].');

        const rungs = state.matrix.rungs || [];
        rows.forEach((row, idx) => {
          const checked = validateDiagnosticRow(rungs, row, idx);
          if (checked.error) {
            rejected.push({ index: idx, raw: row, reason: checked.error });
            return;
          }
          accepted.push(checked.accepted);
          if (checked.warning) warnings.push(checked.warning);
        });

        state.diagnostic_rows = accepted;
        state.validation_report = {
          accepted,
          rejected,
          warnings,
          provenance: 'HISTORICAL_IMPORT (PRIOR_DIAGNOSTIC)'
        };

        saveLocalStorageState();
        renderInputDrawer();
        renderProgressionLane();
        renderMultiResolutionCards();
        renderNeedMap();
        renderCoreBuilder();
        updateStorageStatusBadge('📂 Imported: ' + accepted.length + ' accepted, ' + rejected.length + ' isolated');
      } catch (err) {
        state.validation_report = {
          accepted: [...state.diagnostic_rows],
          rejected: [{ index: null, raw: null, reason: err.message }],
          warnings: [],
          provenance: 'IMPORT_ERROR',
          fatal_error: 'Diagnostic Import Error: ' + err.message
        };
        renderInputDrawer();
        const reportBox = document.getElementById('importValidationReport');
        if (reportBox) {
          reportBox.setAttribute('role', 'alert');
          reportBox.setAttribute('tabindex', '-1');
          reportBox.focus();
        }
      }
    };
    reader.readAsText(file);
  }

  function buildMeasurementPack(matrix, exportedAt) {
    return {
      format: 'GRADE9V3_TOPIC_ATLAS_MEASUREMENT_PROJECTION',
      version: '0.1.0',
      authority_note: 'Transient browser projection from canonical web data; scanner must use only supplied canonical targets.',
      generator: 'Grade9V3 Topic Atlas',
      matrix_id: matrix.matrix_id,
      subject: matrix.subject,
      topic: matrix.topic,
      subtopic: matrix.subtopic,
      exported_at: exportedAt,
      diagnostic_contract: {
        result_values: [...GAP_RESULTS],
        error_stage_values: [...DIAGNOSTIC_STAGES],
        score: {
          optional: true,
          minimum: 0,
          maximum: 100,
          rule: 'Display-only exact-target score; no automatic mastery threshold or averaging is applied.'
        },
        rules: [
          'Report only what the written answer-sheet evidence supports.',
          'Absence from the gap list is not DEMONSTRATED.',
          'Do not recalculate canonical difficulty or prerequisites.',
          'Do not invent a repair_ref that is not present in this pack.'
        ]
      },
      targets: (matrix.rungs || []).map(r => {
        const cap = r.capability || {};
        const micro = r.microtopic || {};
        const tpath = micro.teaching_path || [];
        return {
          measurement: {
            capability_ref: cap.id,
            capability_action: cap.action,
            success_criterion: cap.success_criterion,
            microtopic_ref: micro.id,
            microtopic_title: micro.title,
            semantic_actions: tpath.map(s => ({
              id: s.id,
              role: s.role,
              action: s.action,
              why_valid: s.why_valid
            })),
            misconceptions: (micro.misconceptions || []).map(misc => ({
              wrong_idea: misc.wrong_idea,
              diagnostic_prompt: misc.diagnostic_prompt,
              repair: misc.repair
            })),
            questions: (r.questions || []).map(q => ({
              id: q.id,
              family_ref: q.family_ref || null,
              repair_ref: q.repair_ref || null,
              stem: q.stem || null
            }))
          },
          routing_context: {
            rung: r.rung,
            ladder_position: r.ladder_position,
            default_entry_eligible: r.default_entry_eligible,
            prerequisites: cap.prerequisite_refs || [],
            intrinsic_difficulty: micro.intrinsic_badge,
            difficulty_reason: micro.badge_reason
          }
        };
      })
    };
  }

  function buildDiagnosticEnvelope(matrix, diagnosticRows, when, diagnosticId) {
    return {
      format: 'GRADE9V3_EXTERNAL_DIAGNOSTIC_GAP_ENVELOPE',
      version: '0.1.0',
      diagnostic_id: diagnosticId,
      matrix_id: matrix.matrix_id,
      subject: matrix.subject,
      subtopic: matrix.subtopic,
      when,
      provenance: 'HISTORICAL_IMPORT',
      evidence_kind: 'PRIOR_DIAGNOSTIC',
      rows: diagnosticRows || []
    };
  }

  // --- Measurement Pack Exporter (GAP-WEB-011) ---
  function exportMeasurementPack() {
    const m = state.matrix;
    downloadJSON(buildMeasurementPack(m, new Date().toISOString()), 'measurement_pack_' + m.matrix_id + '.json');
  }

  // --- Core Request Exporter (GAP-WEB-005, GAP-WEB-013) ---
  function exportCoreRequest() {
    const m = state.matrix;
    const requestDoc = buildAuthoringRequest(
      m,
      state.request_config,
      state.knowledge_percentage,
      'REQ-' + m.matrix_id + '-' + Date.now()
    );
    if (!requestDoc) {
      alert('Select at least one Core before exporting an authoring request.');
      return;
    }

    // Diagnostic focus remains a separate envelope until the Shared resolver consumes it.
    // Do not rewrite diagnostic-derived focus as owner_entry.
    downloadJSON(requestDoc, 'authoring_request_' + m.matrix_id + '.json');
  }

  function openPromptComposer() {
    const m = state.matrix;
    if (!m) return;
    const requested = Array.isArray(state.request_config.cores) ? [...state.request_config.cores] : [];
    const preferredOrder = ['CORE2', 'CORE1', 'CORE1A', 'CORE1B', 'CORE2A', 'CORE2B'];
    const payload = {
      version: 1,
      subject: m.subject,
      matrix_id: m.matrix_id,
      rung: state.selected_rung_key && state.selected_rung_key.matrix_id === m.matrix_id
        ? state.selected_rung_key.rung
        : null,
      knowledge_percentage: state.knowledge_percentage,
      requested_cores: requested,
      execution_order: preferredOrder.filter(core => requested.includes(core))
    };
    try {
      sessionStorage.setItem('grade9v3_prompt_composer_handoff_v1', JSON.stringify(payload));
    } catch (err) {
      // Handoff remains optional. The composer can still be opened without stored context.
    }
    window.location.href = '../../core-prompt-composer/index.html';
  }

  // --- Diagnostic Gap Envelope Exporter (GAP-WEB-005) ---
  function exportDiagnosticEnvelope() {
    const m = state.matrix;
    const now = new Date().toISOString();
    const envelope = buildDiagnosticEnvelope(
      m,
      state.diagnostic_rows,
      now,
      'DG-' + m.matrix_id + '-' + Date.now()
    );
    downloadJSON(envelope, 'diagnostic_gap_envelope_' + m.matrix_id + '.json');
  }

  function downloadJSON(obj, filename) {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  // --- Global Window Bridge ---
  window.ATLAS = {
    init: initAtlas,
    __test: {
      validateDiagnosticRow,
      deriveAtlasAddress,
      resolveNeedTargetsFor,
      resolveAtlasComposite,
      resolveCoreDestinationsFor,
      resolveVisualDestinationsFor,
      resolvePortableDestinationsFor,
      portablePackageHref,
      buildAuthoringRequest,
      buildMeasurementPack,
      buildDiagnosticEnvelope
    },
    openRung: function(rungId) {
      selectRung(rungId, { pushHistory: true, focus: true });
    },
    setKnowledgeSlider: function(val) {
      const num = parseInt(val, 10);
      state.knowledge_percentage = isNaN(num) ? null : num;
      const inp = document.getElementById('knowledgeInput');
      if (inp) inp.value = state.knowledge_percentage !== null ? state.knowledge_percentage : '';
      saveLocalStorageState();
      renderInputDrawer();
      renderProgressionLane();
      renderMultiResolutionCards();
      renderNeedMap();
      renderCoreBuilder();
    },
    setKnowledgeInput: function(val) {
      if (val === '' || val === null || val === undefined) {
        state.knowledge_percentage = null;
      } else {
        let num = parseInt(val, 10);
        if (isNaN(num)) num = null;
        else num = Math.max(0, Math.min(100, num));
        state.knowledge_percentage = num;
      }
      const sld = document.getElementById('knowledgeSlider');
      if (sld && state.knowledge_percentage !== null) sld.value = state.knowledge_percentage;
      saveLocalStorageState();
      renderInputDrawer();
      renderProgressionLane();
      renderMultiResolutionCards();
      renderNeedMap();
      renderCoreBuilder();
    },
    toggleOverlay: function(checked) {
      state.overlay_active = checked;
      saveLocalStorageState();
      renderProgressionLane();
      renderMultiResolutionCards();
    },
    toggleCore: function(core, checked) {
      if (checked && !state.request_config.cores.includes(core)) {
        state.request_config.cores.push(core);
      } else if (!checked) {
        state.request_config.cores = state.request_config.cores.filter(c => c !== core);
      }
      saveLocalStorageState();
      renderCoreBuilder();
    },
    setCore2APurpose: function(p) {
      state.request_config.core2a_purpose = p;
      saveLocalStorageState();
      renderCoreBuilder();
    },
    setCore2BPurpose: function(p) {
      state.request_config.core2b_purpose = p || null;
      saveLocalStorageState();
      renderCoreBuilder();
    },
    handleFileImport: function(evt) {
      const file = evt.target.files[0];
      if (file) handleDiagnosticImport(file);
    },
    loadDemoPreset: function() {
      // Demo preset loaded ONLY on explicit user action (GAP-WEB-002).
      // Build it from the currently loaded canonical matrix so the generic
      // Atlas engine never carries subject/topic identifiers of its own.
      state.knowledge_percentage = 45;
      const eligible = (state.matrix.rungs || [])
        .filter(r => r.capability && r.microtopic && (r.microtopic.teaching_path || []).length)
        .slice(0, 3);
      state.diagnostic_rows = eligible.map((rung, idx) => ({
        question_ref: (rung.questions && rung.questions[0]) ? rung.questions[0].id : null,
        capability_ref: rung.capability.id,
        repair_ref: rung.microtopic.teaching_path[0].id,
        result: "MISSING",
        error_stage: idx === 2 ? "SETUP" : "CONCEPT",
        score: [25, 20, 40][idx] || 30,
        observed: "Demo gap generated from the active matrix for Topic Atlas routing validation."
      }));
      state.validation_report = {
        accepted: state.diagnostic_rows,
        rejected: [],
        warnings: [],
        provenance: "DEMO_SCENARIO (matrix-derived)"
      };
      saveLocalStorageState();
      renderInputDrawer();
      renderProgressionLane();
      renderMultiResolutionCards();
      renderNeedMap();
      renderCoreBuilder();
      updateStorageStatusBadge("📥 Loaded matrix-derived gap demo");
    },
    resetCanonical: function() {
      localStorage.removeItem(getStorageKey());
      state.knowledge_percentage = null;
      state.diagnostic_rows = [];
      state.validation_report = null;
      state.overlay_active = true;
      state.request_config = {
        cores: ['CORE1A', 'CORE1B', 'CORE2A'],
        core2a_purpose: 'PRACTICE',
        core2b_purpose: null
      };
      renderInputDrawer();
      renderProgressionLane();
      renderMultiResolutionCards();
      renderNeedMap();
      renderCoreBuilder();
      updateStorageStatusBadge("↺ Reset to Canonical Neutral");
    },
    exportMeasurementPack: exportMeasurementPack,
    exportCoreRequest: exportCoreRequest,
    openPromptComposer: openPromptComposer,
    exportDiagnosticEnvelope: exportDiagnosticEnvelope
  };

})();