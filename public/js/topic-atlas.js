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
    selected_target: null,       // Focus target (e.g. "R5.1.0")
    request_config: {
      cores: ['CORE1A', 'CORE1B', 'CORE2A'],
      core2a_purpose: 'PRACTICE',
      core2b_purpose: null,      // null = required input if CORE2B selected
      placement_mode: 'AUTO'     // 'AUTO' | 'OWNER_ENTRY' | 'OWNER_ESTIMATE'
    }
  };

  function initAtlas(matrixId) {
    if (!window.GRADE9V3 || !window.GRADE9V3.subjects) {
      console.error("window.GRADE9V3 is not loaded. Ensure public/data/data.js is linked.");
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
      return;
    }

    state.matrix = foundMatrix;
    state.subject = foundSubject;

    // Load LocalStorage state if present, otherwise default to canonical neutral
    loadLocalStorageState();

    // Render all surfaces
    renderHeader();
    renderInputDrawer();
    renderProgressionLane();
    renderMultiResolutionCards();
    renderNeedMap();
    renderCoreBuilder();
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

  // Resolve canonical public/... resource locators from any Topic Atlas page.
  // This keeps the same activity registry usable from file:// and hosted builds.
  function activityHref(locator) {
    if (!locator || !locator.startsWith('public/')) return locator || '#';

    const target = locator.replace(/^public\//, '').split('/').filter(Boolean);
    const current = window.location.pathname.split('/').filter(Boolean);
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

  function activityMatchesStep(activity, stepId) {
    return Boolean(stepId && (activity.teaching_step_refs || []).includes(stepId));
  }

  // --- Need Resolver & Fallback Ladder (GAP-WEB-010) ---
  function resolveNeedTargets() {
    const rungs = state.matrix.rungs;
    const defaultRungs = rungs.filter(r => r.default_entry_eligible);
    const sortedDefault = [...defaultRungs].sort((a, b) => a.ladder_position - b.ladder_position);

    const targets = [];

    // Step 1: Process external diagnostic gap rows
    if (state.diagnostic_rows && state.diagnostic_rows.length > 0) {
      state.diagnostic_rows.forEach(row => {
        // Find matching rung
        const matchedRung = rungs.find(r => 
          (r.capability && r.capability.id === row.capability_ref) ||
          r.rung === row.rung_ref
        );

        if (!matchedRung) return;

        const capId = matchedRung.capability ? matchedRung.capability.id : row.capability_ref;
        const tpath = (matchedRung.microtopic && matchedRung.microtopic.teaching_path) || [];
        
        let stepIdx = 99; // fallback level: capability only
        let matchedStep = null;
        if (row.repair_ref) {
          const sIndex = tpath.findIndex(s => s.id === row.repair_ref);
          if (sIndex !== -1) {
            stepIdx = sIndex;
            matchedStep = tpath[sIndex];
          }
        }

        // Diagnostic Dimension mapping
        const dimMap = {
          'CONCEPT': 0,
          'SETUP': 1,
          'EXECUTION': 2,
          'CARELESS': 3,
          'UNKNOWN': 99
        };
        const stage = row.error_stage || 'UNKNOWN';
        const dimIdx = dimMap[stage] !== undefined ? dimMap[stage] : 99;

        // Derived presentation address (GAP-WEB-008)
        const address = `${matchedRung.rung}.${stepIdx}.${dimIdx}`;

        // Fallback level receipt
        let fallbackLevel = "EXACT_LEAF_DIMENSION";
        if (stepIdx === 99) fallbackLevel = "CAPABILITY_ONLY_FALLBACK";
        else if (dimIdx === 99) fallbackLevel = "LEAF_UNKNOWN_DIMENSION_FALLBACK";

        targets.push({
          address,
          rung: matchedRung.rung,
          rung_obj: matchedRung,
          capability_ref: capId,
          repair_ref: row.repair_ref || (matchedStep ? matchedStep.id : null),
          error_stage: stage,
          score: row.score !== undefined ? row.score : null,
          observed: row.observed || "Diagnostic gap identified from external assessment",
          result: row.result || "MISSING",
          fallback_level: fallbackLevel,
          step_action: matchedStep ? matchedStep.action : null,
          why: `Scanned gap on ${capId}${row.repair_ref ? ' step ' + row.repair_ref : ''} at stage ${stage}`
        });
      });
    }

    // Step 2: If no gap rows, fall back to Knowledge Percentage (GAP-WEB-004)
    let estimateEntryRung = null;
    let quickCheckRungs = [];

    if (targets.length === 0 && state.knowledge_percentage !== null && !isNaN(state.knowledge_percentage)) {
      const pct = state.knowledge_percentage;
      const eligible = sortedDefault.filter(r => r.ladder_position <= pct);
      estimateEntryRung = eligible.length > 0 ? eligible[eligible.length - 1] : sortedDefault[0];
      quickCheckRungs = eligible.map(r => r.rung);

      targets.push({
        address: `${estimateEntryRung.rung}.99.99`,
        rung: estimateEntryRung.rung,
        rung_obj: estimateEntryRung,
        capability_ref: estimateEntryRung.capability ? estimateEntryRung.capability.id : null,
        repair_ref: null,
        error_stage: 'UNKNOWN',
        score: null,
        observed: `Selected via owner knowledge estimate of ${pct}% (Ladder position ${estimateEntryRung.ladder_position})`,
        result: 'UNCERTAIN',
        fallback_level: 'KNOWLEDGE_ESTIMATE_FALLBACK',
        step_action: null,
        why: `Knowledge estimate ${pct}% maps to tentative start coordinate ${estimateEntryRung.rung}`
      });
    }

    // Step 3: If neither present, neutral default canonical route
    if (targets.length === 0) {
      const defaultEntry = sortedDefault[0];
      targets.push({
        address: `${defaultEntry.rung}.0.99`,
        rung: defaultEntry.rung,
        rung_obj: defaultEntry,
        capability_ref: defaultEntry.capability ? defaultEntry.capability.id : null,
        repair_ref: null,
        error_stage: 'UNKNOWN',
        score: null,
        observed: "Canonical baseline: no estimate or gap table supplied",
        result: 'UNCERTAIN',
        fallback_level: 'CANONICAL_DEFAULT_ROUTE',
        step_action: null,
        why: "Default curriculum entry; browsing full canonical atlas"
      });
    }

    return {
      targets,
      primary_target: targets[0],
      estimateEntryRung,
      quickCheckRungs
    };
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
        statusTxt.textContent = "No estimate supplied → neutral/default canonical route";
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

    const rungs = state.matrix.rungs;
    const defaultRungs = rungs.filter(r => r.default_entry_eligible);
    const nonDefaultRungs = rungs.filter(r => !r.default_entry_eligible);

    // Group default rungs into clusters based on position
    const clusters = [
      { title: "1. Foundation", min: 0, max: 70, rungs: [] },
      { title: "2. Dynamics & Applications", min: 71, max: 87, rungs: [] },
      { title: "3. Constraints & Quantitative", min: 88, max: 93, rungs: [] },
      { title: "4. Interaction & Closure", min: 94, max: 99, rungs: [] }
    ];

    defaultRungs.forEach(r => {
      let placed = false;
      for (const c of clusters) {
        if (r.ladder_position <= c.max) {
          c.rungs.push(r);
          placed = true;
          break;
        }
      }
      if (!placed) clusters[clusters.length - 1].rungs.push(r);
    });

    let clustersHtml = clusters.filter(c => c.rungs.length > 0).map(c => `
      <div class="cluster-box">
        <div class="cluster-title">
          <span>${c.title}</span>
          <span>Pos: ${c.rungs[0].ladder_position}–${c.rungs[c.rungs.length - 1].ladder_position}</span>
        </div>
        <div class="rung-flow">
          ${c.rungs.map(r => renderRungNode(r, resolved)).join('')}
        </div>
      </div>
    `).join('');

    let nonDefaultHtml = nonDefaultRungs.map(r => `
      <div class="extension-box">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <div>
            <span class="badge purple" style="margin-bottom: 4px;">Branch Extension</span>
            <h4 style="font-size: 14px; font-weight: 700;">${r.rung} · ${r.microtopic ? r.microtopic.title : r.rung}</h4>
          </div>
          <span class="badge hold">Hard</span>
        </div>
        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">
          <code>${r.capability ? r.capability.id : 'NO_CAP'}</code> (Pos: ${r.ladder_position}) &middot; Explicit Question Demand Only
        </p>
        <button class="btn-sm" style="font-size: 11px; padding: 3px 8px;" onclick="window.ATLAS.openRung('${r.rung}')">
          View Rung Card ↓
        </button>
      </div>
    `).join('');

    laneContainer.innerHTML = `
      <div class="lane-heading default">
        <span>●</span> Default Instructional Route (${defaultRungs.length} Rungs)
      </div>
      <div class="cluster-wrapper">
        ${clustersHtml}
      </div>
      ${nonDefaultRungs.length > 0 ? `
        <div class="lane-heading non-default">
          <span>◆</span> Non-Default Explicit-Demand Extensions (${nonDefaultRungs.length} Rungs)
        </div>
        <div class="non-default-grid">
          ${nonDefaultHtml}
        </div>
      ` : ''}
    `;
  }

  function renderRungNode(rung, resolved) {
    const rId = rung.rung;
    const target = resolved.targets.find(t => t.rung === rId);
    const isQuickCheck = resolved.quickCheckRungs.includes(rId);

    let badgeHtml = '';
    let nodeClass = 'rung-node';

    if (state.overlay_active && target) {
      if (target.result === 'MISSING') {
        nodeClass += ' has-gap';
        badgeHtml = `<span class="badge hold">GAP: ${target.error_stage}</span>`;
      } else if (target.result === 'UNCERTAIN') {
        nodeClass += ' has-uncertain';
        badgeHtml = `<span class="badge warn">UNCERTAIN</span>`;
      } else if (target.result === 'DEMONSTRATED') {
        nodeClass += ' has-demonstrated';
        badgeHtml = `<span class="badge ok">✓ DEMONSTRATED</span>`;
      }
    } else if (state.overlay_active && isQuickCheck) {
      nodeClass += ' is-quick-check';
      badgeHtml = `<span class="badge phy">QUICK CHECK</span>`;
    }

    return `
      <div class="${nodeClass}" onclick="window.ATLAS.openRung('${rId}')">
        <div style="display: flex; align-items: center; gap: 8px; overflow: hidden;">
          <span class="node-id">${rId}</span>
          <span class="node-title">${rung.microtopic ? rung.microtopic.title : rung.rung}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
          <span class="badge neutral">${rung.ladder_position}</span>
          ${badgeHtml}
        </div>
      </div>
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

      // Level 2 & 3: Semantic Leaves & Diagnostic Dimension Cells
      let semanticLeavesHtml = tpath.map((step, idx) => {
        const stepTarget = resolved.targets.find(t => t.rung === r.rung && t.repair_ref === step.id);
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
          return `
            <a href="${activityHref(act.locator)}" class="btn primary-phy"
               style="font-size: 11px; padding: 4px 9px; margin-right: 6px; margin-top: 6px;"
               title="${label} for ${step.id}${status}${audit ? ` · audit ${audit}` : ''}${mapping}">
              🧪 ${label}: ${act.title} ${auditBadge} ↗
            </a>
          `;
        }).join('');
        
        // Level 3 Dimensions
        const dimensions = ['CONCEPT', 'SETUP', 'EXECUTION', 'CARELESS', 'UNKNOWN'];
        const dimCellsHtml = dimensions.map(dim => {
          const isCurrentDim = stepTarget && stepTarget.error_stage === dim;
          let cellStyle = "padding: 3px 6px; border-radius: 4px; font-size: 11px; font-family: var(--font-mono); border: 1px solid var(--border);";
          if (isCurrentDim) {
            cellStyle += " background: var(--chip-hold-bg); border-color: var(--chip-hold-border); color: var(--chip-hold-text); font-weight: 700;";
          } else {
            cellStyle += " background: var(--bg); color: var(--text-muted);";
          }
          const scoreText = isCurrentDim && stepTarget.score !== null ? ` (${stepTarget.score}%)` : '';
          return `<span style="${cellStyle}">${dim}${scoreText}</span>`;
        }).join(' ');

        return `
          <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 10px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; flex-wrap: wrap; gap: 6px;">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge phy" style="font-weight: 700;">Leaf ${r.rung}.${idx}</span>
                <code style="color: var(--accent);">${step.id}</code>
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
              <a href="${activityHref(act.locator)}" class="btn primary-phy" style="font-size: 11px; padding: 4px 10px;">
                Launch Activity ↗
              </a>
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
          ${m.diagnostic ? `<div style="font-size: 12px; color: var(--text-dim); margin: 4px 0 2px 0;"><strong>Diagnostic:</strong> ${m.diagnostic}</div>` : ''}
          <div class="quote-box repair" style="margin-top: 4px;">
            <strong>Repair:</strong> ${m.repair}
          </div>
        </div>
      `).join('');

      return `
        <details class="rung-card ${isDef ? '' : 'non-default'}" id="card-${r.rung}">
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
              <h4 style="font-size: 13px; font-weight: 700; margin-bottom: 8px; color: var(--accent);">
                🌿 Level 2 Semantic Leaves & Level 3 Diagnostic Cells:
              </h4>
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
                    <div style="font-size: 13px; font-weight: 600; margin-bottom: 6px;">${micro.exit_task.task || ''}</div>
                    <div class="quote-box repair" style="font-size: 12px;"><strong>Success:</strong> ${micro.exit_task.success_criterion || ''}</div>
                  </div>
                ` : ''}
                ${activitiesHtml}
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
    needBox.innerHTML = `
      <div class="section-title">
        <span>🎯 Active Need Map & Focus Targets</span>
        <span class="count">${resolved.targets.length} Identified Need(s)</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 24px;">
        ${resolved.targets.map((t, idx) => {
          const exactActivities = ((t.rung_obj && t.rung_obj.activities) || [])
            .filter(act => activityMatchesStep(act, t.repair_ref));
          const exactActivityHtml = exactActivities.map(act => {
            const gcdr = act.support_route && act.support_route.kind === 'GCDR';
            return `
              <a href="${activityHref(act.locator)}" class="btn primary-phy"
                 style="font-size: 11px; padding: 4px 9px; margin-top: 8px; margin-right: 6px;">
                ${gcdr ? 'Open graphical breakdown' : 'Open exact repair'}: ${act.title} ↗
              </a>
            `;
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

  // --- Core Request Builder & Planner Preview (GAP-WEB-013, GAP-WEB-014, GAP-WEB-015, GAP-WEB-016) ---
  function renderCoreBuilder() {
    const builderBox = document.getElementById('coreBuilderContainer');
    if (!builderBox) return;

    const resolved = resolveNeedTargets();
    const primary = resolved.primary_target;

    // Default suggestions based on failure stage (GAP-WEB-014)
    let suggestedEmphasis = "Core1B reconstruction + Core1A concept grounding";
    if (primary && primary.error_stage === 'SETUP') suggestedEmphasis = "Core1B setup reconstruction + scaffolded Core2A";
    else if (primary && primary.error_stage === 'EXECUTION') suggestedEmphasis = "Core2A targeted practice (no broad Core1A reteach)";
    else if (primary && primary.error_stage === 'CARELESS') suggestedEmphasis = "Short Core2A / revision checking loop";
    else if (primary && primary.error_stage === 'UNKNOWN') suggestedEmphasis = "Parent-level diagnostic + Core1B repair";

    const isCore2B = state.request_config.cores.includes('CORE2B');
    const isCore2BPurposeMissing = isCore2B && !state.request_config.core2b_purpose;

    // Planner state preview (GAP-WEB-015)
    const coreStates = {};
    state.request_config.cores.forEach(c => {
      if (c === 'CORE2B') {
        if (state.request_config.core2a_purpose === 'STARTER') {
          coreStates[c] = { state: 'WITHHELD', reason: 'STARTER purpose does not route transfer' };
        } else if (!state.request_config.core2b_purpose) {
          coreStates[c] = { state: 'WAITING', reason: 'WAITING_FOR_PURPOSE' };
        } else {
          coreStates[c] = { state: 'READY', reason: 'Transfer inventory available' };
        }
      } else if (c === 'CORE2A') {
        coreStates[c] = { state: 'READY', reason: `Purpose: ${state.request_config.core2a_purpose}` };
      } else {
        coreStates[c] = { state: 'READY', reason: 'Intrinsic canonical construction' };
      }
    });

    builderBox.innerHTML = `
      <div class="section-title">
        <span>⚡ Authoritative Core Request Builder & Planner Preview</span>
        <span class="badge ok">Shared request.schema.json Compliant</span>
      </div>

      <div style="background: var(--bg-panel); border: 1px solid var(--border); border-radius: 10px; padding: 20px; margin-bottom: 24px;">
        <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);">
          <h4 style="font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 4px;">
            Target Need: <code>${primary.address}</code> (${primary.rung} · ${primary.capability_ref})
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

        <!-- Deterministic Planner Preview (GAP-WEB-015) -->
        <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 16px;">
          <h5 style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">
            Deterministic Planner Preview:
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
            <strong>Entry Rung:</strong> ${primary.rung} &middot; 
            <strong>Prerequisite Status:</strong> Cleared via ${primary.fallback_level} &middot;
            <strong>Targeted Teaching Steps:</strong> ${primary.repair_ref || 'Full rung sequence'}
          </p>
        </div>

        <!-- Action Bar: Export Request & CLI Instructions (GAP-WEB-016) -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button type="button" class="btn primary-phy" onclick="window.ATLAS.exportCoreRequest()">
              💾 Export Core Request JSON
            </button>
            <a href="../../tools/run-builder/index.html" class="btn outline" target="_blank">
              Open Run Builder ↗
            </a>
          </div>
          <div style="font-size: 12px; color: var(--text-dim); font-family: var(--font-mono);">
            CLI: <code>python Shared/tools/resolve_request.py [request.json]</code>
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

        if (doc.knowledge_percentage !== undefined && doc.knowledge_percentage !== null) {
          const num = parseInt(doc.knowledge_percentage, 10);
          if (!isNaN(num) && num >= 0 && num <= 100) {
            state.knowledge_percentage = num;
          }
        }

        const rows = doc.rows || doc.observations || [];
        const rungs = state.matrix.rungs;

        rows.forEach((r, idx) => {
          const capRef = r.capability_ref;
          const matchedRung = rungs.find(rg => (rg.capability && rg.capability.id === capRef) || rg.rung === r.rung_ref);

          if (!matchedRung) {
            rejected.push({ index: idx, raw: r, reason: `Unknown capability ref '${capRef}' in matrix` });
            return;
          }

          // Check repair ref if present
          let validRepair = null;
          if (r.repair_ref) {
            const tpath = (matchedRung.microtopic && matchedRung.microtopic.teaching_path) || [];
            const step = tpath.find(s => s.id === r.repair_ref);
            if (step) {
              validRepair = step.id;
            } else {
              warnings.push(`Row ${idx + 1}: Unrecognized repair_ref '${r.repair_ref}' on ${matchedRung.rung}; fell back to capability-level target.`);
            }
          }

          // Validate error stage
          const validStages = ['CONCEPT', 'SETUP', 'EXECUTION', 'CARELESS', 'UNKNOWN'];
          const stage = (r.error_stage && validStages.includes(r.error_stage.toUpperCase())) ? r.error_stage.toUpperCase() : 'UNKNOWN';

          accepted.push({
            question_ref: r.question_ref || null,
            capability_ref: matchedRung.capability ? matchedRung.capability.id : capRef,
            rung_ref: matchedRung.rung,
            repair_ref: validRepair,
            result: r.result === 'UNCERTAIN' ? 'UNCERTAIN' : 'MISSING',
            error_stage: stage,
            score: r.score !== undefined ? r.score : null,
            observed: r.observed || `Observed gap on ${matchedRung.rung}`
          });
        });

        state.diagnostic_rows = accepted;
        state.validation_report = {
          accepted,
          rejected,
          warnings,
          provenance: "HISTORICAL_IMPORT (PRIOR_DIAGNOSTIC)" // Honest separation (GAP-WEB-006)
        };

        saveLocalStorageState();
        renderInputDrawer();
        renderProgressionLane();
        renderMultiResolutionCards();
        renderNeedMap();
        renderCoreBuilder();
        updateStorageStatusBadge(`📂 Imported: ${accepted.length} accepted, ${rejected.length} isolated`);
      } catch (err) {
        alert("JSON Parse Error: " + err.message);
      }
    };
    reader.readAsText(file);
  }

  // --- Measurement Pack Exporter (GAP-WEB-011) ---
  function exportMeasurementPack() {
    const m = state.matrix;
    const pack = {
      $schema: "https://grade9v3.local/measurement-pack.schema.json",
      generator: "Grade9V3 Topic Atlas",
      matrix_id: m.matrix_id,
      subject: m.subject,
      topic: m.topic,
      subtopic: m.subtopic,
      exported_at: new Date().toISOString(),
      allowed_diagnostic_vocabulary: ["CONCEPT", "SETUP", "EXECUTION", "CARELESS", "UNKNOWN"],
      measurement_obligations: m.rungs.map(r => {
        const cap = r.capability || {};
        const micro = r.microtopic || {};
        const tpath = micro.teaching_path || [];
        return {
          rung: r.rung,
          ladder_position: r.ladder_position,
          default_entry_eligible: r.default_entry_eligible,
          capability_ref: cap.id,
          success_criterion: cap.success_criterion,
          prerequisites: cap.prerequisite_refs || [],
          intrinsic_difficulty: micro.intrinsic_badge,
          difficulty_reason: micro.badge_reason,
          semantic_actions: tpath.map(s => ({
            id: s.id,
            role: s.role,
            action: s.action,
            why_valid: s.why_valid
          })),
          misconceptions: (micro.misconceptions || []).map(misc => ({
            wrong_idea: misc.wrong_idea,
            diagnostic: misc.diagnostic,
            repair: misc.repair
          }))
        };
      })
    };

    downloadJSON(pack, `measurement_pack_${m.matrix_id}.json`);
  }

  // --- Core Request Exporter (GAP-WEB-005, GAP-WEB-013) ---
  function exportCoreRequest() {
    const resolved = resolveNeedTargets();
    const primary = resolved.primary_target;
    const m = state.matrix;

    const requestDoc = {
      $schema: "https://grade9v3.local/request.schema.json",
      request_id: `REQ-${m.matrix_id}-${Date.now()}`,
      subject: m.subject,
      bucket_id: m.bucket_id || `BUCKET-${m.matrix_id}`,
      label: `Topic Atlas Build Request for ${m.subtopic}`,
      cores: state.request_config.cores,
      learner: {
        owner_entry: {
          rung: primary.rung,
          by: "Topic Atlas Need Resolver",
          instruction: `Entry selected via ${primary.fallback_level}: ${primary.why}`
        }
      },
      practice: {
        CORE2A: {
          purpose: state.request_config.core2a_purpose,
          note: `Selected for ${m.subtopic} practice run`
        }
      }
    };

    if (state.request_config.cores.includes('CORE2B') && state.request_config.core2b_purpose) {
      requestDoc.practice.CORE2B = {
        purpose: state.request_config.core2b_purpose,
        note: `Selected for ${m.subtopic} transfer run`
      };
    }

    downloadJSON(requestDoc, `request_${m.matrix_id}.json`);
  }

  // --- Diagnostic Gap Envelope Exporter (GAP-WEB-005) ---
  function exportDiagnosticEnvelope() {
    const m = state.matrix;
    const envelope = {
      matrix_id: m.matrix_id,
      subject: m.subject,
      subtopic: m.subtopic,
      knowledge_percentage: state.knowledge_percentage,
      exported_at: new Date().toISOString(),
      provenance: "HISTORICAL_IMPORT",
      evidence_kind: "PRIOR_DIAGNOSTIC",
      rows: state.diagnostic_rows
    };

    downloadJSON(envelope, `diagnostic_gap_envelope_${m.matrix_id}.json`);
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
    openRung: function(rungId) {
      const el = document.getElementById('card-' + rungId);
      if (el) {
        el.open = true;
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
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
        core2b_purpose: null,
        placement_mode: 'AUTO'
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
    exportDiagnosticEnvelope: exportDiagnosticEnvelope
  };

})();
