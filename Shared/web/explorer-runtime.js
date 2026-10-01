/* The explorer's page behaviour: the picture, the graph, the sliders and the eleven-step route, driven by one model.

   Shared/tools/explorer_build.py writes the markup (every sentence of the route is already in it) and embeds the spec as JSON;
   this file wires it. Text from the spec is only ever inserted as text, never as markup. The numbers come from
   Shared/web/explorer-model.js, which computes what the build already checked. */
(function () {
  'use strict';
  const GX = window.GXModel;
  const dataNode = document.getElementById('gx-data');
  if (!GX || !dataNode) return;
  const data = JSON.parse(dataNode.textContent);
  const spec = data.spec;
  const compiled = data.compiled;
  const ROUTE = data.route;
  const FADE_LEVELS = data.fade_levels;
  const model = new GX.Model(compiled);
  const decimals = compiled.decimals;
  const q = (selector, root) => (root || document).querySelector(selector);
  const qa = (selector, root) => Array.from((root || document).querySelectorAll(selector));
  const SVG = 'http://www.w3.org/2000/svg';
  const testMode = location.hash === '#gx-test';
  const targetQuantity = spec.target.quantity;
  const freeIds = model.free();
  const allStates = model.states();

  const state = {
    params: model.initial(),
    stage: 0,
    prediction: null,
    imposed: false,
    goals: { MANIPULATE: [], CONTRADICT: [] },
    observe: [],
    dstep: -1,
    asks: {},
    rstep: -1,
    eqSeen: new Set(),
    invSeen: new Set(),
    boundary: [],
    fade: { level: 0, results: [] },
    transfer: { index: 0, results: [] },
    trail: [],
    evidence: [],
    locked: true,
    closed: false,
  };

  /* ------------------------------------------------------------------ small helpers */

  const fmt = (value, digits) => GX.fixed(value, digits);
  const key = (params) => model.ids.map((id) => params[id]).join('|');
  const env = () => model.values(state.params);
  const live = (message) => { const node = q('#gx-live'); if (node) node.textContent = message; };
  const stageId = () => ROUTE[state.stage];
  const stageIndex = (id) => ROUTE.indexOf(id);
  const reached = (id) => state.stage >= stageIndex(id);
  const span = (id) => (spec.parameters.find((p) => p.id === id) || {});
  const emit = (type, detail) => {
    const event = { type, at: new Date().toISOString(), stage: stageId(), detail: detail || {} };
    state.evidence.push(event);
    document.dispatchEvent(new CustomEvent('g9:evidence', { detail: event }));
  };

  function fadeRules() {
    if (stageId() !== 'FADE') return {};
    return FADE_LEVELS[Math.min(state.fade.level, FADE_LEVELS.length - 1)] || {};
  }

  function setText(node, text) { if (node && node.textContent !== text) node.textContent = text; }
  const calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reveal = (node) => { if (node && node.scrollIntoView) node.scrollIntoView({ block: 'nearest', behavior: calm ? 'auto' : 'smooth' }); };

  function nearest(predicate) {
    let best = null;
    let bestDistance = Infinity;
    for (const candidate of allStates) {
      if (!predicate(candidate)) continue;
      let distance = 0;
      for (const id of freeIds) {
        const p = model.byId[id];
        distance += Math.abs(candidate[id] - state.params[id]) / ((p.max - p.min) || 1);
      }
      if (distance < bestDistance) { best = candidate; bestDistance = distance; }
    }
    return best;
  }

  function setParams(next) {
    for (const id of model.ids) if (id in next) state.params[id] = Number(next[id]);
    syncSliders();
    if (!['FADE', 'TRANSFER'].includes(stageId())) trailAdd();
    noteVisit();
    render();
  }

  /* ------------------------------------------------------------------ the picture */

  const scene = spec.scene;
  const world = compiled.world;
  const [VW, VH] = compiled.view_box;
  const scale = VW / (world.x[1] - world.x[0]);
  const X = (x) => (x - world.x[0]) * scale;
  const Y = (y) => (world.y[1] - y) * scale;
  const sceneSvg = q('#gx-scene-svg');
  const sceneNodes = new Map();

  function svg(name, attributes, parent) {
    const node = document.createElementNS(SVG, name);
    for (const [k, v] of Object.entries(attributes || {})) node.setAttribute(k, v);
    if (parent) parent.appendChild(node);
    return node;
  }

  function buildScene() {
    if (!sceneSvg) return;
    const layer = svg('g', { class: 'gx-elements' }, sceneSvg);
    for (const element of compiled.elements) {
      const group = svg('g', { class: `gx-el gx-r-${element.role}`, 'data-gx-el': element.id, 'data-gx-kind': element.kind }, layer);
      const parts = {};
      if (element.kind === 'point') parts.shape = svg('circle', { r: 5.5, class: 'gx-fill' }, group);
      else if (element.kind === 'segment' || element.kind === 'arrow') parts.shape = svg('line', { class: 'gx-stroke' }, group);
      else if (element.kind === 'circle') parts.shape = svg('circle', { class: 'gx-stroke gx-nofill' }, group);
      else if (element.kind === 'arc') parts.shape = svg('path', { class: 'gx-stroke gx-nofill' }, group);
      else if (element.kind === 'polygon') parts.shape = svg('polygon', { class: 'gx-stroke gx-soft' }, group);
      else if (element.kind === 'curve') parts.shape = svg('path', { class: 'gx-stroke gx-nofill' }, group);
      if (element.kind === 'arrow') parts.shape.setAttribute('marker-end', `url(#gx-ah-${element.role})`);
      if (element.label || element.kind === 'text') parts.label = svg('text', { class: 'gx-lab', 'data-rank': element.role === 'helper' ? '2' : element.role === 'wrong' ? '1' : element.kind === 'text' ? '1' : '0' }, group);
      sceneNodes.set(element.id, { element, group, parts });
    }
  }

  function deconstructRevealed() {
    const out = new Set();
    if (reached('DECONSTRUCT')) {
      spec.deconstruct.steps.forEach((step, i) => {
        if (stageIndex('DECONSTRUCT') < state.stage || i <= state.dstep) step.reveals.forEach((id) => out.add(id));
      });
    }
    return out;
  }

  function placeLabel(node, x, y, anchor) {
    node.setAttribute('x', x.toFixed(1));
    node.setAttribute('y', y.toFixed(1));
    node.setAttribute('text-anchor', anchor);
    node.setAttribute('dominant-baseline', 'central');
  }

  function drawElement(entry, values, hidden) {
    const { element, parts, group } = entry;
    const v = element.vars.map((name) => values[name]);
    const rules = fadeRules();
    const showLabels = !rules.labels;
    let label = null;
    const geometry = (() => {
      switch (element.kind) {
        case 'point': return { x: X(v[0]), y: Y(v[1]) };
        case 'text': return { x: X(v[0]), y: Y(v[1]) };
        case 'segment':
        case 'arrow': return { x1: X(v[0]), y1: Y(v[1]), x2: X(v[2]), y2: Y(v[3]) };
        case 'circle': return { cx: X(v[0]), cy: Y(v[1]), r: v[2] * scale };
        case 'arc': return { cx: X(v[0]), cy: Y(v[1]), r: v[2] * scale, a1: v[3], a2: v[4] };
        case 'polygon': { const pts = []; for (let i = 0; i + 1 < v.length; i += 2) pts.push([X(v[i]), Y(v[i + 1])]); return { pts }; }
        default: return {};
      }
    })();
    const finiteAll = Object.values(geometry).every((g) => (Array.isArray(g) ? g.every((p) => p.every(Number.isFinite)) : Number.isFinite(g)));
    if (element.kind !== 'curve' && !finiteAll) { group.style.display = 'none'; return; }

    if (element.kind === 'point') {
      parts.shape.setAttribute('cx', geometry.x.toFixed(1));
      parts.shape.setAttribute('cy', geometry.y.toFixed(1));
      const flip = geometry.x > VW * 0.72;
      label = { x: geometry.x + (flip ? -10 : 10), y: geometry.y - 12, anchor: flip ? 'end' : 'start' };
    } else if (element.kind === 'segment' || element.kind === 'arrow') {
      for (const [k, val] of Object.entries(geometry)) parts.shape.setAttribute(k, val.toFixed(1));
      const dx = geometry.x2 - geometry.x1;
      const dy = geometry.y2 - geometry.y1;
      const length = Math.hypot(dx, dy) || 1;
      const nx = dy / length;
      const ny = -dx / length;
      const mx = (geometry.x1 + geometry.x2) / 2;
      const my = (geometry.y1 + geometry.y2) / 2;
      label = { x: mx + nx * 15, y: my + ny * 15, anchor: Math.abs(nx) < 0.4 ? 'middle' : nx > 0 ? 'start' : 'end' };
      if (element.kind === 'arrow') parts.shape.style.visibility = length < 2 ? 'hidden' : 'visible';
      if (element.role === 'helper' && length < 2) label = null;  // an arrow too short to see is not labelled
    } else if (element.kind === 'circle') {
      for (const [k, val] of Object.entries(geometry)) parts.shape.setAttribute(k, val.toFixed(1));
      label = { x: geometry.cx, y: geometry.cy - geometry.r - 10, anchor: 'middle' };
    } else if (element.kind === 'arc') {
      const at = (deg) => [geometry.cx + geometry.r * Math.cos((deg * Math.PI) / 180), geometry.cy - geometry.r * Math.sin((deg * Math.PI) / 180)];
      const [sx, sy] = at(geometry.a1);
      const [ex, ey] = at(geometry.a2);
      const sweep = geometry.a2 >= geometry.a1 ? 0 : 1;
      const large = Math.abs(geometry.a2 - geometry.a1) > 180 ? 1 : 0;
      parts.shape.setAttribute('d', Math.abs(geometry.a2 - geometry.a1) < 0.05 ? '' : `M${sx.toFixed(1)} ${sy.toFixed(1)}A${geometry.r.toFixed(1)} ${geometry.r.toFixed(1)} 0 ${large} ${sweep} ${ex.toFixed(1)} ${ey.toFixed(1)}`);
      const mid = ((geometry.a1 + geometry.a2) / 2) * (Math.PI / 180);
      label = { x: geometry.cx + (geometry.r + 18) * Math.cos(mid), y: geometry.cy - (geometry.r + 18) * Math.sin(mid), anchor: 'middle' };
    } else if (element.kind === 'polygon') {
      parts.shape.setAttribute('points', geometry.pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' '));
      const cx = geometry.pts.reduce((a, p) => a + p[0], 0) / geometry.pts.length;
      const cy = geometry.pts.reduce((a, p) => a + p[1], 0) / geometry.pts.length;
      label = { x: cx, y: cy, anchor: 'middle' };
    } else if (element.kind === 'curve') {
      const c = element.curve;
      const lo = model.evaluate(c.t_min, state.params);
      const hi = model.evaluate(c.t_max, state.params);
      const parts2 = [];
      let pen = false;
      let mid = null;
      for (let k = 0; k <= c.steps; k += 1) {
        const t = lo + ((hi - lo) * k) / c.steps;
        const local = { ...values, [c.param]: t };
        const px = X(GX.evaluate(model.tree(c.x), local));
        const py = Y(GX.evaluate(model.tree(c.y), local));
        if (Number.isFinite(px) && Number.isFinite(py)) { parts2.push(`${pen ? 'L' : 'M'}${px.toFixed(1)} ${py.toFixed(1)}`); pen = true; if (k === Math.round(c.steps / 2)) mid = [px, py]; } else pen = false;
      }
      parts.shape.setAttribute('d', parts2.join(''));
      if (mid) label = { x: mid[0], y: mid[1] - 14, anchor: 'middle' };
    } else if (element.kind === 'text') {
      label = { x: geometry.x, y: geometry.y, anchor: element.anchor || 'start' };
    }
    if (parts.label && !label) parts.label.textContent = '';
    if (parts.label && label) {
      const template = element.kind === 'text' ? element.text : element.label;
      if (!showLabels && element.kind !== 'text') parts.label.textContent = '';
      else setText(parts.label, GX.format(template, values, decimals, hidden));
      placeLabel(parts.label, label.x, label.y, label.anchor);
    }
  }

  /* Labels that would sit on one another are moved apart, so every label can be read at every position of the sliders.
     `labels` are SVG text elements; the ones that matter most (data-rank 0: given and result) are placed first and stay nearest where they
     belong, each stays inside a width x height box. A label that cannot be placed clear of the others within reach is hidden when it is
     only a helper (data-rank 2 or more): its number is always in the readouts beside the picture. */
  const REACH = (() => {
    const out = [];
    for (let dy = -84; dy <= 84; dy += 14) for (let dx = -120; dx <= 120; dx += 30) out.push([dx, dy, Math.hypot(dx, dy)]);
    return out.sort((a, b) => a[2] - b[2] || Math.abs(a[0]) - Math.abs(b[0]));
  })();

  function nudgeLabels(labels, width, height) {
    const placed = [];
    const rank = (node) => Number(node.getAttribute('data-rank') || 1);
    const ordered = labels.map((node, i) => ({ node, i })).filter((e) => e.node)
      .sort((a, b) => rank(a.node) - rank(b.node) || a.i - b.i).map((e) => e.node);
    for (const label of ordered) {
      label.style.visibility = '';
      if (!label.textContent) continue;
      let box = label.getBBox();
      const x0 = parseFloat(label.getAttribute('x'));
      const y0 = parseFloat(label.getAttribute('y'));
      const clashes = (b) => placed.filter((p) => b.x < p.x + p.w + 3 && p.x < b.x + b.w + 3 && b.y < p.y + p.h + 1 && p.y < b.y + b.h + 1).length;
      const inside = (b) => b.x >= 3 && b.x + b.w <= width - 3 && b.y >= 0 && b.y + b.h <= height;
      // pull a label that hangs over the edge back inside first, so the search starts from a legal place
      const pull = box.x < 3 ? 3 - box.x : box.x + box.width > width - 3 ? width - 3 - (box.x + box.width) : 0;
      let base = { x: box.x + pull, y: box.y, w: box.width, h: box.height };
      let chosen = null;
      let best = null;
      for (const [dx, dy] of REACH) {
        const b = { x: base.x + dx, y: base.y + dy, w: base.w, h: base.h };
        if (!inside(b)) continue;
        const n = clashes(b);
        if (n === 0) { chosen = { dx, dy, b }; break; }
        if (!best || n < best.n) best = { dx, dy, b, n };
      }
      if (!chosen && rank(label) >= 2) { label.style.visibility = 'hidden'; continue; }
      const pick = chosen || best || { dx: 0, dy: 0, b: base };
      label.setAttribute('x', (x0 + pull + pick.dx).toFixed(1));
      label.setAttribute('y', (y0 + pick.dy).toFixed(1));
      placed.push(pick.b);
    }
  }

  const sceneLabels = () => [...sceneNodes.values()].filter((e) => e.group.style.display !== 'none' && e.parts.label).map((e) => e.parts.label);

  function renderScene() {
    if (!sceneSvg) return;
    const values = env();
    const rules = fadeRules();
    const hidden = Boolean(rules.values);
    for (const entry of sceneNodes.values()) {
      const visible = visibleElement(entry.element);
      entry.group.style.display = visible ? '' : 'none';
      if (visible) drawElement(entry, values, hidden);
    }
    nudgeLabels(sceneLabels(), VW, VH);
    const summary = `State: ${model.free().map((id) => `${span(id).label} ${fmt(state.params[id], decimals[id])} ${span(id).unit || ''}`.trim()).join(', ')}.`
      + (reached('MANIPULATE') && !hidden ? ` ${targetLabel()} is ${fmt(values[targetQuantity], decimals[targetQuantity])} ${targetUnit()}.` : '');
    setText(q('#gx-state-summary'), summary);
  }

  const visibleElement = (element) => {
    const rules = fadeRules();
    if (element.reveal === 'start') return !(rules.result && element.role === 'result');
    if (element.reveal === 'manipulate') return reached('MANIPULATE') && !rules.result;
    if (element.reveal === 'contradict') return state.imposed;
    if (element.reveal === 'deconstruct') return deconstructRevealed().has(element.id) && !rules.mechanism;
    return true;
  };

  const quantityRow = (id) => spec.quantities.find((row) => row.id === id) || {};
  const targetLabel = () => quantityRow(targetQuantity).label || targetQuantity;
  const targetUnit = () => quantityRow(targetQuantity).unit || '';

  /* ------------------------------------------------------------------ the graph */

  const view = spec.second_view;
  const graphSvg = q('#gx-graph-svg');
  const GRAPH = { w: 440, h: 330, l: 66, r: 16, t: 18, b: 52 };
  const graphNodes = {};
  const xParam = model.byId[view.x];
  const xTicks = niceTicks(xParam.min, xParam.max, 5);
  const yTicks = niceTicks(compiled.y_range[0], compiled.y_range[1], 5);
  const gx = (x) => GRAPH.l + ((x - xParam.min) / (xParam.max - xParam.min)) * (GRAPH.w - GRAPH.l - GRAPH.r);
  const gy = (y) => GRAPH.t + (1 - (y - compiled.y_range[0]) / (compiled.y_range[1] - compiled.y_range[0])) * (GRAPH.h - GRAPH.t - GRAPH.b);

  function niceTicks(lo, hi, count) {
    const raw = (hi - lo) / count;
    const magnitude = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 5, 10].map((m) => m * magnitude).find((s) => s >= raw) || raw;
    const out = [];
    for (let v = Math.ceil(lo / step - 1e-9) * step; v <= hi + 1e-9; v += step) out.push(Number(v.toFixed(10)));
    return { values: out, step };
  }

  function tickText(value, step) {
    const places = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
    return GX.fixed(value, places);
  }

  function buildGraph() {
    if (!graphSvg) return;
    const axes = svg('g', { class: 'gx-axes' }, graphSvg);
    svg('rect', { x: GRAPH.l, y: GRAPH.t, width: GRAPH.w - GRAPH.l - GRAPH.r, height: GRAPH.h - GRAPH.t - GRAPH.b, class: 'gx-plot' }, axes);
    xTicks.values.forEach((v) => {
      svg('line', { x1: gx(v), x2: gx(v), y1: GRAPH.t, y2: GRAPH.h - GRAPH.b, class: 'gx-grid' }, axes);
      const t = svg('text', { x: gx(v), y: GRAPH.h - GRAPH.b + 20, 'text-anchor': 'middle', class: 'gx-tick' }, axes);
      t.textContent = tickText(v, xTicks.step);
    });
    yTicks.values.forEach((v) => {
      svg('line', { x1: GRAPH.l, x2: GRAPH.w - GRAPH.r, y1: gy(v), y2: gy(v), class: 'gx-grid' }, axes);
      const t = svg('text', { x: GRAPH.l - 8, y: gy(v), 'text-anchor': 'end', 'dominant-baseline': 'central', class: 'gx-tick' }, axes);
      t.textContent = tickText(v, yTicks.step);
    });
    const xl = svg('text', { x: (GRAPH.l + GRAPH.w - GRAPH.r) / 2, y: GRAPH.h - 8, 'text-anchor': 'middle', class: 'gx-axis-label' }, axes);
    xl.textContent = `${xParam.label}${xParam.unit ? ` (${xParam.unit})` : ''}`;
    const yl = svg('text', { transform: `translate(16 ${(GRAPH.t + GRAPH.h - GRAPH.b) / 2}) rotate(-90)`, 'text-anchor': 'middle', class: 'gx-axis-label' }, axes);
    yl.textContent = view.y_label || view.series[0].label;
    graphNodes.guides = (view.guides || []).map((guide) => {
      const g = svg('g', { class: 'gx-guide gx-r-helper' }, graphSvg);
      return { guide, line: svg('line', { class: 'gx-stroke' }, g), label: svg('text', { class: 'gx-lab', 'data-rank': '2' }, g), group: g };
    });
    graphNodes.ghost = view.ghost ? svg('path', { class: 'gx-stroke gx-nofill gx-r-wrong gx-curve' }, graphSvg) : null;
    graphNodes.series = view.series.map((series) => ({ series, path: svg('path', { class: `gx-stroke gx-nofill gx-curve gx-r-${series.role || 'result'}` }, graphSvg),
      marker: svg('circle', { r: 6.5, class: `gx-fill gx-r-${series.role || 'result'}` }, graphSvg),
      drop: svg('line', { class: 'gx-stroke gx-drop' }, graphSvg) }));
    graphNodes.trail = svg('g', { class: 'gx-trail gx-r-result' }, graphSvg);
    graphNodes.ghostLabel = view.ghost ? svg('text', { class: 'gx-lab gx-r-wrong', 'data-rank': '1' }, graphSvg) : null;
    graphNodes.readout = svg('text', { class: 'gx-lab gx-r-result', 'data-rank': '0', 'text-anchor': 'start', 'dominant-baseline': 'central' }, graphSvg);
  }

  function curvePath(quantity, others) {
    let pen = false;
    let d = '';
    for (const [x, y] of model.resolver(others).sweep(quantity, view.x)) {
      if (Number.isFinite(y)) { d += `${pen ? 'L' : 'M'}${gx(x).toFixed(1)} ${gy(y).toFixed(1)}`; pen = true; } else pen = false;
    }
    return d;
  }

  function renderGraph() {
    if (!graphSvg) return;
    const values = env();
    const rules = fadeRules();
    const showCurve = reached('OBSERVE');
    const hidden = Boolean(rules.values);
    graphNodes.series.forEach(({ series, path, marker, drop }) => {
      path.setAttribute('d', showCurve ? curvePath(series.quantity, state.params) : '');
      const y = values[series.quantity];
      const visible = reached('MANIPULATE') && Number.isFinite(y);
      for (const node of [marker, drop]) node.style.display = visible ? '' : 'none';
      if (visible) {
        marker.setAttribute('cx', gx(state.params[view.x]).toFixed(1));
        marker.setAttribute('cy', gy(y).toFixed(1));
        drop.setAttribute('x1', gx(state.params[view.x]).toFixed(1));
        drop.setAttribute('x2', gx(state.params[view.x]).toFixed(1));
        drop.setAttribute('y1', gy(y).toFixed(1));
        drop.setAttribute('y2', (GRAPH.h - GRAPH.b).toFixed(1));
      }
    });
    const first = graphNodes.series[0];
    const y0 = values[first.series.quantity];
    if (reached('MANIPULATE') && Number.isFinite(y0) && !hidden) {
      const flip = gx(state.params[view.x]) > GRAPH.w * 0.62;
      setText(graphNodes.readout, `${fmt(y0, decimals[first.series.quantity])}`);
      graphNodes.readout.setAttribute('x', (gx(state.params[view.x]) + (flip ? -12 : 12)).toFixed(1));
      graphNodes.readout.setAttribute('y', (gy(y0) - 14).toFixed(1));
      graphNodes.readout.setAttribute('text-anchor', flip ? 'end' : 'start');
    } else setText(graphNodes.readout, '');
    if (graphNodes.ghost) {
      graphNodes.ghost.setAttribute('d', state.imposed ? curvePath(view.ghost.quantity, state.params) : '');
      graphNodes.ghostLabel.textContent = state.imposed ? view.ghost.label : '';
      graphNodes.ghostLabel.setAttribute('x', GRAPH.l + 10);
      graphNodes.ghostLabel.setAttribute('y', GRAPH.t + 16);
    }
    graphNodes.guides.forEach(({ guide, line, label, group }) => {
      const value = model.evaluate(guide.expr, state.params);
      const vertical = guide.orient === 'v';
      group.style.display = reached('OBSERVE') && Number.isFinite(value) ? '' : 'none';
      if (!Number.isFinite(value)) return;
      if (vertical) { line.setAttribute('x1', gx(value)); line.setAttribute('x2', gx(value)); line.setAttribute('y1', GRAPH.t); line.setAttribute('y2', GRAPH.h - GRAPH.b); }
      else { line.setAttribute('x1', GRAPH.l); line.setAttribute('x2', GRAPH.w - GRAPH.r); line.setAttribute('y1', gy(value)); line.setAttribute('y2', gy(value)); }
      setText(label, GX.format(guide.label, values, decimals));
      label.setAttribute('x', vertical ? gx(value) + 8 : GRAPH.w - GRAPH.r - 6);
      label.setAttribute('y', vertical ? GRAPH.t + 16 : gy(value) - 12);
      label.setAttribute('text-anchor', vertical ? 'start' : 'end');
    });
    graphNodes.trail.replaceChildren();
    if (!showCurve && reached('MANIPULATE')) {
      state.trail.forEach(([x, y]) => svg('circle', { cx: gx(x).toFixed(1), cy: gy(y).toFixed(1), r: 3.2, class: 'gx-fill' }, graphNodes.trail));
    }
    nudgeLabels([graphNodes.readout, graphNodes.ghostLabel, ...graphNodes.guides.filter((g) => g.group.style.display !== 'none').map((g) => g.label)], GRAPH.w, GRAPH.h);
    const figure = q('[data-gx-view=graph]');
    if (figure) figure.classList.toggle('gx-faded', Boolean(rules.graph));
  }

  /* ------------------------------------------------------------------ sliders, readouts */

  function syncSliders() {
    for (const id of freeIds) {
      const input = q(`#gx-p-${id}`);
      if (input && Number(input.value) !== state.params[id]) input.value = state.params[id];
    }
  }

  function renderControls() {
    const rules = fadeRules();
    const locked = state.locked || ['FADE', 'TRANSFER'].includes(stageId());
    for (const id of freeIds) {
      const input = q(`#gx-p-${id}`);
      if (input) input.disabled = locked;
      setText(q(`[data-gx-out="${id}"]`), fmt(state.params[id], decimals[id]));
    }
    const note = q('[data-gx-lock-note]');
    if (note) {
      note.hidden = !state.locked;
      note.textContent = 'The sliders unlock when you have locked in your prediction.';
    }
    const values = env();
    const hiddenValues = Boolean(rules.values);
    qa('[data-gx-q]').forEach((out) => {
      const id = out.dataset.gxQ;
      const row = out.closest('[data-gx-reveal]');
      const reveal = row ? row.dataset.gxReveal : 'manipulate';
      const shown = reveal === 'start' || (reveal === 'manipulate' && reached('MANIPULATE')) || (reveal === 'contradict' && state.imposed);
      if (row) row.hidden = !shown;
      setText(out, hiddenValues && reveal !== 'start' ? '—' : fmt(values[id], decimals[id]));
    });
    const panel = q('.gx-readouts');
    if (panel) panel.hidden = state.closed;
    const controls = q('.gx-controls');
    if (controls) controls.hidden = state.closed;
    const views = q('.gx-views');
    if (views) views.hidden = state.closed;
    const closed = q('.gx-closed-note');
    if (closed) closed.hidden = !state.closed;
    const sceneFigure = q('[data-gx-view=scene]');
    if (sceneFigure) sceneFigure.hidden = state.closed;
    document.body.classList.toggle('gx-closed', state.closed);
  }

  function bindSliders() {
    for (const id of freeIds) {
      const input = q(`#gx-p-${id}`);
      if (!input) continue;
      input.addEventListener('input', () => {
        state.params[id] = Number(input.value);
        if (!['FADE', 'TRANSFER'].includes(stageId())) trailAdd();
        noteVisit();
        render();
      });
      input.addEventListener('change', () => { live(q('#gx-state-summary') ? q('#gx-state-summary').textContent : ''); });
    }
    const reset = q('[data-gx-reset]');
    if (reset) reset.addEventListener('click', () => { setParams(model.initial()); live('Sliders reset to their starting positions.'); });
  }

  function trailAdd() {
    const y = env()[view.series[0].quantity];
    if (!Number.isFinite(y)) return;
    const x = state.params[view.x];
    if (!state.trail.some(([tx]) => tx === x)) { state.trail.push([x, y]); if (state.trail.length > 90) state.trail.shift(); }
  }

  function noteVisit() {
    const k = key(state.params);
    if (stageId() === 'RECONSTRUCT' && state.rstep >= spec.reconstruct.steps.length - 1) state.eqSeen.add(k);
    if (stageId() === 'INVARIANT') state.invSeen.add(k);
  }

  /* ------------------------------------------------------------------ the route */

  const cards = Object.fromEntries(ROUTE.map((id) => [id, q(`[data-gx-step="${id}"]`)]));
  const stages = {};
  const continueButton = (id) => q('[data-gx-continue]', cards[id]);

  function goto(index, moveFocus = true) {
    state.stage = Math.max(0, Math.min(ROUTE.length, index));
    state.closed = stageId() === 'TRANSFER' && state.stage < ROUTE.length;
    ROUTE.forEach((id, i) => {
      const card = cards[id];
      card.dataset.state = i < state.stage ? 'done' : i === state.stage ? 'current' : 'locked';
      card.hidden = i > state.stage;
      if (i === state.stage) card.removeAttribute('data-open');
    });
    const done = q('#gx-done');
    if (done) done.hidden = state.stage < ROUTE.length;
    if (state.stage >= ROUTE.length) state.closed = false;
    const id = stageId();
    if (id && stages[id] && stages[id].enter) stages[id].enter();
    renderRail();
    render();
    if (moveFocus) {
      const target = state.stage >= ROUTE.length ? q('#gx-done h2') : q('h2', cards[id]);
      if (target) { target.setAttribute('tabindex', '-1'); target.focus({ preventScroll: false }); }
      live(state.stage >= ROUTE.length ? 'You have finished the route.' : `Step ${state.stage + 1} of ${ROUTE.length}: ${q('.gx-t', cards[id]).textContent}.`);
    }
    const route = q('.gx-route');
    if (route) route.scrollTop = 0;
  }

  function advance() {
    const id = stageId();
    if (id && stages[id] && stages[id].leave) stages[id].leave();
    const summary = stages[id] && stages[id].summary ? stages[id].summary() : '';
    setText(q('[data-gx-summary]', cards[id]), summary);
    goto(state.stage + 1);
  }

  function renderRail() {
    qa('[data-gx-rail]').forEach((item) => {
      const i = stageIndex(item.dataset.gxRail);
      item.dataset.state = i < state.stage ? 'done' : i === state.stage ? 'current' : 'todo';
      if (i === state.stage) item.setAttribute('aria-current', 'step'); else item.removeAttribute('aria-current');
      item.setAttribute('aria-label', `Step ${i + 1} of ${ROUTE.length}: ${item.dataset.gxTitle}, ${item.dataset.state === 'done' ? 'done' : item.dataset.state === 'current' ? 'now' : 'to do'}`);
    });
  }

  function render() {
    renderControls();
    renderScene();
    renderGraph();
    const id = stageId();
    if (id && stages[id] && stages[id].update) stages[id].update();
    const button = id ? continueButton(id) : null;
    if (button && stages[id] && stages[id].ready) button.disabled = !stages[id].ready();
  }

  /* --- goals (manipulate and contradict) */
  function goalList(id, goals, hits) {
    const items = qa('[data-gx-goal]', cards[id]);
    goals.forEach((goal, i) => {
      if (!hits[i] && model.holds(goal.goal, state.params) && !state.locked) { hits[i] = true; emit('GOAL_REACHED', { stage: id, goal: i }); live(`Goal reached: ${goal.prompt}`); }
      const item = items[i];
      if (!item) return;
      item.dataset.met = hits[i] ? 'true' : 'false';
      setText(q('.gx-goal-state', item), hits[i] ? 'done' : 'not yet');
      setText(q('.gx-check', item), hits[i] ? '✓' : '');
    });
  }

  function bindGoals(id, goals) {
    qa('[data-gx-goal]', cards[id]).forEach((item, i) => {
      const hint = q('[data-gx-hint]', item);
      const show = q('[data-gx-show]', item);
      if (show) show.disabled = true;
      if (hint) hint.addEventListener('click', () => { const p = q('.gx-hint', item); p.hidden = !p.hidden; hint.setAttribute('aria-expanded', String(!p.hidden)); if (show) show.disabled = false; });
      if (show) show.addEventListener('click', () => {
        const target = nearest((s) => model.holds(goals[i].goal, s));
        if (target) { setParams(target); emit('GOAL_SHOWN', { stage: id, goal: i }); }
      });
    });
  }

  /* --- the stages */

  stages.CONTEXT = { ready: () => true, summary: () => 'Read the question and the situation.' };

  stages.PREDICT = {
    enter() { state.locked = true; },
    ready: () => state.prediction !== null,
    summary: () => (state.prediction === null ? '' : `You predicted: ${spec.predict.options[state.prediction].text}`),
    leave() {
      state.locked = false;
      qa('input[name=gx-predict]', cards.PREDICT).forEach((input) => { input.disabled = true; });
      emit('INITIAL_PREDICTION', { option: state.prediction, correct: state.prediction === spec.predict.correct });
    },
  };

  stages.MANIPULATE = {
    update() { goalList('MANIPULATE', spec.manipulate.goals, state.goals.MANIPULATE); },
    ready: () => spec.manipulate.goals.every((_, i) => state.goals.MANIPULATE[i]),
    summary: () => `${spec.manipulate.goals.length} goals reached.`,
    leave() { emit('MANIPULATION_COMPLETED', { goals: spec.manipulate.goals.length }); },
  };

  const claimCache = new Map();
  function claimTruth(claim) {
    if (!claimCache.has(claim)) {
      let fails = null;
      let holds = null;
      for (const s of allStates) {
        const value = model.evaluate(claim, s);
        if (Number.isNaN(value)) continue;
        if (value !== 0) holds = holds || s; else fails = fails || s;
      }
      claimCache.set(claim, { truth: !fails ? 'always' : !holds ? 'never' : 'sometimes' });
    }
    return claimCache.get(claim);
  }

  stages.OBSERVE = {
    update() {
      qa('[data-gx-statement]', cards.OBSERVE).forEach((item, i) => {
        const saved = state.observe[i];
        qa('.gx-choice button', item).forEach((button) => {
          const mine = button.hasAttribute('data-gx-agree') ? 'agree' : 'disagree';
          button.setAttribute('aria-pressed', String(Boolean(saved) && saved.choice === mine));
          button.disabled = Boolean(saved);
        });
      });
    },
    ready: () => spec.observe.statements.every((_, i) => state.observe[i]),
    summary() {
      const right = state.observe.filter((o) => o && o.correct).length;
      return `${right} of ${spec.observe.statements.length} judged right.`;
    },
    leave() { emit('MISCONCEPTION_SIGNATURE', { prediction: state.prediction, correct: state.prediction === spec.predict.correct, judged: state.observe.map((o) => o && o.correct) }); },
  };

  function bindObserve() {
    qa('[data-gx-statement]', cards.OBSERVE).forEach((item, i) => {
      const statement = spec.observe.statements[i];
      const answer = (choice) => {
        if (state.observe[i]) return;
        const { truth } = claimTruth(statement.claim);
        const correct = (choice === 'agree') === (truth === 'always');
        state.observe[i] = { choice, truth, correct };
        const feedback = q('.gx-feedback', item);
        feedback.hidden = false;
        const verdict = q('[data-gx-verdict]', feedback);
        verdict.textContent = (correct ? 'Right. ' : 'Not quite. ')
          + (truth === 'always' ? 'This holds at every position of the sliders.' : truth === 'never' ? 'This is false at every position of the sliders.' : 'This holds at some positions and fails at others.');
        const witness = q('[data-gx-witness]', feedback);
        if (truth !== 'always') {
          witness.hidden = false;
          witness.onclick = () => { const s = nearest((candidate) => !model.holds(statement.claim, candidate)); if (s) setParams(s); };
        }
        live(verdict.textContent);
        render();
        reveal(feedback);
      };
      q('[data-gx-agree]', item).addEventListener('click', () => answer('agree'));
      q('[data-gx-disagree]', item).addEventListener('click', () => answer('disagree'));
    });
  }

  function renderRecall() {
    const box = q('[data-gx-recall]', cards.OBSERVE);
    if (!box) return;
    const all = spec.observe.statements.every((_, i) => state.observe[i]);
    box.hidden = !all;
    if (!all || state.prediction === null) return;
    const option = spec.predict.options[state.prediction];
    const correct = state.prediction === spec.predict.correct;
    const text = q('[data-gx-recall-text]', box);
    const button = q('[data-gx-recall-show]', box);
    if (correct) { text.textContent = `You predicted: “${option.text}”. The model agrees.`; button.hidden = true; return; }
    const failing = option.tests.find((test) => !model.holds(test.holds, model.withSet(test.set, model.initial())));
    const at = model.withSet(failing.set, model.initial());
    text.textContent = `You predicted: “${option.text}”. ${failing.says ? GX.format(failing.says, model.values(at), decimals) : 'The model says otherwise.'}`;
    button.hidden = false;
    button.onclick = () => setParams(at);
  }

  stages.CONTRADICT = {
    enter() { state.imposed = false; },
    update() {
      goalList('CONTRADICT', [spec.contradict.goal], state.goals.CONTRADICT);
      const toggle = q('[data-gx-impose]', cards.CONTRADICT);
      if (toggle) toggle.setAttribute('aria-pressed', String(state.imposed));
      const why = q('[data-gx-why]', cards.CONTRADICT);
      if (why) why.hidden = !state.goals.CONTRADICT[0];
      const compare = q('[data-gx-wrong-compare]', cards.CONTRADICT);
      if (compare) {
        compare.hidden = !state.imposed;
        const values = env();
        setText(q('[data-gx-wrong]', compare), `${fmt(values[spec.contradict.wrong_model.quantity], decimals[spec.contradict.wrong_model.quantity])} ${quantityRow(spec.contradict.wrong_model.quantity).unit || ''}`.trim());
        setText(q('[data-gx-true]', compare), `${fmt(values[targetQuantity], decimals[targetQuantity])} ${targetUnit()}`.trim());
      }
    },
    ready: () => Boolean(state.goals.CONTRADICT[0]),
    summary: () => `Tested the tempting model: ${spec.contradict.wrong_model.label}.`,
    leave() { emit('CONTRADICTION_UNDERSTOOD', { model: spec.contradict.wrong_model.quantity }); },
  };

  function bindContradict() {
    const toggle = q('[data-gx-impose]', cards.CONTRADICT);
    if (toggle) toggle.addEventListener('click', () => { state.imposed = !state.imposed; if (state.imposed) emit('MODEL_IMPOSED', {}); render(); });
  }

  function askBlock(item, stepIndex, ask) {
    const buttons = qa('[data-gx-ask-opt]', item);
    buttons.forEach((button) => button.addEventListener('click', () => {
      if (state.asks[stepIndex] !== undefined) return;
      const choice = Number(button.dataset.gxAskOpt);
      state.asks[stepIndex] = choice;
      const feedback = q('.gx-feedback', item);
      feedback.hidden = false;
      feedback.textContent = `${choice === ask.correct ? 'Right. ' : 'Not quite. '}${ask.why}`;
      buttons.forEach((b) => { b.disabled = true; b.setAttribute('aria-pressed', String(Number(b.dataset.gxAskOpt) === choice)); });
      live(feedback.textContent);
      render();
      reveal(feedback);
    }));
  }

  stages.DECONSTRUCT = {
    enter() { state.dstep = 0; },
    update() {
      qa('[data-gx-dstep]', cards.DECONSTRUCT).forEach((item, i) => { item.hidden = i > state.dstep; item.classList.toggle('gx-latest', i === state.dstep); });
      const more = q('[data-gx-more]', cards.DECONSTRUCT);
      const steps = spec.deconstruct.steps;
      const pending = steps[state.dstep] && steps[state.dstep].ask && state.asks[state.dstep] === undefined;
      if (more) { more.hidden = state.dstep >= steps.length - 1; more.disabled = Boolean(pending); }
    },
    ready() {
      const steps = spec.deconstruct.steps;
      return state.dstep >= steps.length - 1 && !(steps[state.dstep].ask && state.asks[state.dstep] === undefined);
    },
    summary: () => `${spec.deconstruct.steps.length} causes exposed.`,
    leave() { state.dstep = spec.deconstruct.steps.length - 1; emit('CAUSAL_CHAIN_RECONSTRUCTED', { steps: spec.deconstruct.steps.length }); },
  };

  function bindDeconstruct() {
    spec.deconstruct.steps.forEach((step, i) => { if (step.ask) askBlock(q(`[data-gx-dstep="${i}"]`, cards.DECONSTRUCT), i, step.ask); });
    const more = q('[data-gx-more]', cards.DECONSTRUCT);
    if (more) more.addEventListener('click', () => { state.dstep = Math.min(state.dstep + 1, spec.deconstruct.steps.length - 1); render(); reveal(q(`[data-gx-dstep="${state.dstep}"]`, cards.DECONSTRUCT)); });
  }

  stages.RECONSTRUCT = {
    enter() { state.rstep = 0; state.eqSeen = new Set([key(state.params)]); },
    update() {
      const steps = spec.reconstruct.steps;
      const values = env();
      qa('[data-gx-rstep]', cards.RECONSTRUCT).forEach((item, i) => {
        item.hidden = i > state.rstep;
        const output = q('[data-gx-val]', item);
        if (output) setText(output, fmt(values[steps[i].quantity], decimals[steps[i].quantity]));
      });
      const last = state.rstep >= steps.length - 1;
      const equation = q('[data-gx-equation]', cards.RECONSTRUCT);
      if (equation) {
        equation.hidden = !last;
        if (last) {
          const value = model.evaluate(spec.reconstruct.equation.expr, state.params);
          setText(q('[data-gx-eq-value]', equation), fmt(value, decimals[targetQuantity]));
          setText(q('[data-gx-eq-measured]', equation), fmt(values[targetQuantity], decimals[targetQuantity]));
          setText(q('[data-gx-eq-ok]', equation), GX.equal(value, values[targetQuantity]) ? '✓ equal' : '✗ differ');
          setText(q('[data-gx-eq-count]', equation), String(Math.min(3, state.eqSeen.size) - 1));
        }
      }
      const more = q('[data-gx-more]', cards.RECONSTRUCT);
      if (more) more.hidden = last;
    },
    ready: () => state.rstep >= spec.reconstruct.steps.length - 1 && state.eqSeen.size >= 3,
    summary: () => 'Built the equation from the mechanism and tested it.',
    leave() { emit('EQUATION_TESTED', { states: state.eqSeen.size }); },
  };

  function bindReconstruct() {
    const more = q('[data-gx-more]', cards.RECONSTRUCT);
    if (more) more.addEventListener('click', () => {
      state.rstep = Math.min(state.rstep + 1, spec.reconstruct.steps.length - 1);
      state.eqSeen = new Set([key(state.params)]);
      render();
      reveal(state.rstep >= spec.reconstruct.steps.length - 1 ? q('[data-gx-equation]', cards.RECONSTRUCT) : q(`[data-gx-rstep="${state.rstep}"]`, cards.RECONSTRUCT));
    });
  }

  const INV_NEEDED = 5;
  stages.INVARIANT = {
    enter() { state.invSeen = new Set([key(state.params)]); },
    update() {
      qa('[data-gx-inv]', cards.INVARIANT).forEach((item, i) => {
        const inv = spec.invariants[i];
        const a = model.evaluate(inv.lhs, state.params);
        const b = model.evaluate(inv.rhs, state.params);
        setText(q('[data-gx-inv-lhs]', item), fmt(a, 3));
        setText(q('[data-gx-inv-rhs]', item), fmt(b, 3));
        const ok = inv.rel === '==' ? GX.equal(a, b) : inv.rel === '<=' ? (a <= b || GX.equal(a, b)) : (a >= b || GX.equal(a, b));
        setText(q('[data-gx-inv-ok]', item), ok ? '✓ holds here' : '✗ broken here');
        setText(q('[data-gx-inv-count]', item), String(Math.min(INV_NEEDED, state.invSeen.size)));
      });
    },
    ready: () => state.invSeen.size >= INV_NEEDED,
    summary: () => `${spec.invariants.length} relations tried against ${state.invSeen.size} positions; none broke.`,
    leave() { emit('INVARIANT_RECONSTRUCTED', { relations: spec.invariants.length, states: state.invSeen.size }); },
  };

  stages.BOUNDARY = {
    enter() { state.imposed = true; },
    update() {
      const boundary = spec.boundary;
      qa('[data-gx-case]', cards.BOUNDARY).forEach((item, i) => {
        const saved = state.boundary[i];
        const compare = q('.gx-compare', item);
        const shown = Boolean(item.dataset.visited);
        compare.hidden = !shown;
        const at = model.withSet(boundary.cases[i].set, model.initial());
        const values = model.values(at);
        const a = model.evaluate(boundary.cases[i].shortcut, at);
        setText(q('[data-gx-sc]', item), fmt(a, decimals[targetQuantity] + 1));
        setText(q('[data-gx-true]', item), fmt(values[targetQuantity], decimals[targetQuantity] + 1));
        qa('.gx-choice button', item).forEach((button) => {
          button.disabled = Boolean(saved) || !shown;
          const mine = button.hasAttribute('data-gx-yes') ? 'holds' : 'fails';
          button.setAttribute('aria-pressed', String(Boolean(saved) && saved.choice === mine));
        });
      });
      const take = q('.gx-takeaway', cards.BOUNDARY);
      if (take) take.hidden = !boundary.cases.every((_, i) => state.boundary[i]);
    },
    ready: () => spec.boundary.cases.every((_, i) => state.boundary[i]),
    summary: () => `${state.boundary.filter((b) => b && b.correct).length} of ${spec.boundary.cases.length} cases judged right.`,
    leave() { state.imposed = false; emit('BOUNDARY_TEST_RESULT', { cases: state.boundary.map((b) => b && b.correct) }); },
  };

  function bindBoundary() {
    qa('[data-gx-case]', cards.BOUNDARY).forEach((item, i) => {
      const c = spec.boundary.cases[i];
      q('[data-gx-go]', item).addEventListener('click', () => { setParams(model.withSet(c.set, state.params)); item.dataset.visited = '1'; render(); });
      const answer = (choice) => {
        if (state.boundary[i]) return;
        const at = model.withSet(c.set, model.initial());
        const actual = GX.equal(model.evaluate(c.shortcut, at), model.values(at)[targetQuantity]) ? 'holds' : 'fails';
        const correct = choice === actual;
        state.boundary[i] = { choice, actual, correct };
        const feedback = q('.gx-feedback', item);
        feedback.hidden = false;
        feedback.textContent = `${correct ? 'Right. ' : 'Not quite. '}Here the shortcut ${actual === 'holds' ? 'gives the true value' : 'does not give the true value'}.`;
        live(feedback.textContent);
        render();
        reveal(feedback);
      };
      q('[data-gx-yes]', item).addEventListener('click', () => answer('holds'));
      q('[data-gx-no]', item).addEventListener('click', () => answer('fails'));
    });
  }

  /* --- fade and transfer: numeric tasks */
  function parseAnswer(text) {
    const cleaned = String(text).replace(/−/g, '-').replace(',', '.').trim();
    const match = cleaned.match(/^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)(?:\s*\/\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)))?\s*[^\d\s]{0,12}$/);
    if (!match) return NaN;
    const top = parseFloat(match[1]);
    return match[2] !== undefined ? top / parseFloat(match[2]) : top;
  }

  function taskAt(task) { return model.withSet(task.set, model.initial()); }

  function bindTasks(id, tasks, results, onDone) {
    qa('[data-gx-task]', cards[id]).forEach((item, i) => {
      const input = q('[data-gx-answer]', item);
      const check = q('[data-gx-check]', item);
      const feedback = q('.gx-feedback', item);
      let attempts = 0;
      const finish = (correct, revealed) => {
        results[i] = { correct, attempts, revealed };
        const at = taskAt(tasks[i]);
        const answer = model.evaluate(tasks[i].answer, at);
        const extra = { ...model.values(at), answer };
        const lines = [(tasks[i].worked || []), [tasks[i].why]].flat().map((line) => GX.format(line, extra, { ...decimals, answer: tasks[i].decimals ?? 1 }));
        feedback.replaceChildren();
        const head = document.createElement('p');
        head.textContent = correct ? 'Right.' : `The answer is ${fmt(answer, tasks[i].decimals ?? 1)} ${tasks[i].unit || ''}`.trim() + '.';
        feedback.appendChild(head);
        lines.forEach((line) => { const p = document.createElement('p'); p.textContent = line; feedback.appendChild(p); });
        feedback.hidden = false;
        input.disabled = true;
        check.disabled = true;
        live(head.textContent);
        onDone(i, results[i]);
        render();
        reveal(feedback);
      };
      check.addEventListener('click', () => {
        if (results[i]) return;
        const given = parseAnswer(input.value);
        if (Number.isNaN(given)) { feedback.hidden = false; feedback.textContent = 'Type a number (for example 12.5).'; return; }
        attempts += 1;
        const at = taskAt(tasks[i]);
        const answer = model.evaluate(tasks[i].answer, at);
        if (Math.abs(given - answer) <= tasks[i].tolerance) finish(true, false);
        else if (attempts >= 2) finish(false, true);
        else { feedback.hidden = false; feedback.textContent = 'Not quite. Check your working and try once more.'; live(feedback.textContent); }
      });
      input.addEventListener('keydown', (event) => { if (event.key === 'Enter') check.click(); });
    });
  }

  stages.FADE = {
    enter() { state.fade.level = 0; applyFadeState(); },
    update() {
      const level = state.fade.level;
      qa('[data-gx-task]', cards.FADE).forEach((item, i) => { item.hidden = i > level; });
      const label = q('[data-gx-level]', cards.FADE);
      const rules = FADE_LEVELS[Math.min(level, FADE_LEVELS.length - 1)];
      if (label) setText(label, `Level ${Math.min(level, spec.fade.length - 1) + 1} of ${spec.fade.length}: ${rules.label}`);
    },
    ready: () => spec.fade.every((_, i) => state.fade.results[i]),
    summary: () => `${state.fade.results.filter((r) => r && r.correct).length} of ${spec.fade.length} answered with less help.`,
    leave() { emit('SCAFFOLD_FADE_RESULT', { results: state.fade.results.map((r) => r && r.correct) }); },
  };

  function applyFadeState() {
    const task = spec.fade[Math.min(state.fade.level, spec.fade.length - 1)];
    state.params = model.withSet(task.set, model.initial());
    syncSliders();
  }

  stages.TRANSFER = {
    enter() { state.transfer.index = 0; state.closed = true; },
    update() { qa('[data-gx-task]', cards.TRANSFER).forEach((item, i) => { item.hidden = i > state.transfer.index; }); },
    ready: () => spec.transfer.every((_, i) => state.transfer.results[i]),
    summary: () => `${state.transfer.results.filter((r) => r && r.correct).length} of ${spec.transfer.length} fresh tasks answered right.`,
    leave() { state.closed = false; emit('FRESH_TRANSFER_RESULT', { results: state.transfer.results.map((r) => r && r.correct) }); },
  };

  /* ------------------------------------------------------------------ the end */

  function renderDone() {
    const done = q('#gx-done');
    if (!done) return;
    const parts = [];
    const correct = state.prediction === spec.predict.correct;
    parts.push(`Your prediction: ${state.prediction === null ? 'none' : spec.predict.options[state.prediction].text} (${correct ? 'the model agreed' : 'the model disagreed'}).`);
    parts.push(`Statements judged right: ${state.observe.filter((o) => o && o.correct).length} of ${spec.observe.statements.length}.`);
    parts.push(`Boundary cases judged right: ${state.boundary.filter((b) => b && b.correct).length} of ${spec.boundary.cases.length}.`);
    parts.push(`Answered with less help: ${state.fade.results.filter((r) => r && r.correct).length} of ${spec.fade.length}. Fresh tasks: ${state.transfer.results.filter((r) => r && r.correct).length} of ${spec.transfer.length}.`);
    const list = q('[data-gx-summary-list]', done);
    list.replaceChildren();
    parts.forEach((line) => { const li = document.createElement('li'); li.textContent = line; list.appendChild(li); });
  }

  /* ------------------------------------------------------------------ wiring */

  function bindPredict() {
    qa('input[name=gx-predict]', cards.PREDICT).forEach((input) => input.addEventListener('change', () => { state.prediction = Number(input.value); render(); }));
  }

  function bindContinue() {
    ROUTE.forEach((id) => {
      const button = continueButton(id);
      if (!button) return;
      button.addEventListener('click', () => {
        if (button.disabled) return;
        if (id === 'TRANSFER') { advance(); renderDone(); return; }
        advance();
      });
    });
    qa('.gx-card-head', document).forEach((head) => head.addEventListener('click', () => {
      const card = head.closest('.gx-card');
      if (card.dataset.state === 'done') { if (card.hasAttribute('data-open')) card.removeAttribute('data-open'); else card.setAttribute('data-open', ''); }
    }));
    const restart = q('[data-gx-restart]');
    if (restart) {
      let armed = null;
      restart.addEventListener('click', () => {
        if (armed) { clearTimeout(armed); location.reload(); return; }
        restart.textContent = 'Sure? Tap again';
        armed = setTimeout(() => { armed = null; restart.textContent = 'Start over'; }, 4000);
      });
    }
    const theme = q('[data-gx-theme]');
    if (theme) theme.addEventListener('click', () => {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = next;
      try { localStorage.setItem('g9-theme', next); } catch (e) { /* the choice is only a convenience */ }
      theme.setAttribute('aria-pressed', String(next === 'dark'));
    });
  }

  /* Beside the stage the route is pinned and scrolls inside itself; it is never taller than what is left of the screen below it,
     so the button that goes on is in reach whatever sits above the page (the TEST header, for one). */
  function fitRoute() {
    const route = q('.gx-route');
    if (!route) return;
    if (getComputedStyle(route).position !== 'sticky') { route.style.maxHeight = ''; return; }
    const pinned = parseFloat(getComputedStyle(route).top) || 0;
    const top = Math.max(pinned, route.getBoundingClientRect().top);
    route.style.maxHeight = `${Math.max(240, window.innerHeight - top - 12)}px`;
  }

  function pinViews() {
    let queued = false;
    const fit = () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; fitRoute(); }); } };
    window.addEventListener('scroll', fit, { passive: true });
    window.addEventListener('resize', fit);
    fitRoute();
    const views = q('.gx-views');
    if (!views || typeof ResizeObserver === 'undefined') return;
    const set = () => document.documentElement.style.setProperty('--gx-views-h', `${views.offsetHeight}px`);
    new ResizeObserver(set).observe(views);
    set();
  }

  function start() {
    pinViews();
    try { const saved = localStorage.getItem('g9-theme'); if (saved === 'light' || saved === 'dark') document.documentElement.dataset.theme = saved; } catch (e) { /* none */ }
    buildScene();
    buildGraph();
    bindSliders();
    bindPredict();
    bindObserve();
    bindContradict();
    bindDeconstruct();
    bindReconstruct();
    bindBoundary();
    bindGoals('MANIPULATE', spec.manipulate.goals);
    bindGoals('CONTRADICT', [spec.contradict.goal]);
    bindTasks('FADE', spec.fade, state.fade.results, (i) => {
      if (i < spec.fade.length - 1) { state.fade.level = i + 1; applyFadeState(); }
    });
    bindTasks('TRANSFER', spec.transfer, state.transfer.results, (i) => {
      if (i < spec.transfer.length - 1) state.transfer.index = i + 1;
    });
    bindContinue();
    const baseUpdate = stages.OBSERVE.update;
    stages.OBSERVE.update = () => { baseUpdate(); renderRecall(); };
    document.documentElement.dataset.gxReady = '1';
    goto(0, false);
  }

  window.__gx = {
    spec, model, state,
    values: () => env(),
    stage: () => stageId(),
    set: setParams,
    evidence: () => state.evidence.slice(),
    claims: () => spec.observe.statements.map((s) => claimTruth(s.claim).truth),
    geometry() {
      const values = env();
      const out = {};
      for (const entry of sceneNodes.values()) {
        const { element, parts } = entry;
        if (!parts.shape || entry.group.style.display === 'none') continue;
        const read = (name) => parseFloat(parts.shape.getAttribute(name));
        if (element.kind === 'point') out[element.id] = { x: read('cx'), y: read('cy'), expect: [X(values[element.vars[0]]), Y(values[element.vars[1]])] };
        else if (element.kind === 'segment' || element.kind === 'arrow') out[element.id] = { x1: read('x1'), y1: read('y1'), x2: read('x2'), y2: read('y2'),
          expect: [X(values[element.vars[0]]), Y(values[element.vars[1]]), X(values[element.vars[2]]), Y(values[element.vars[3]])] };
      }
      return out;
    },
    goto(id) { if (testMode) goto(typeof id === 'number' ? id : stageIndex(id)); },
    visible: (id) => { const entry = sceneNodes.get(id); return Boolean(entry) && entry.group.style.display !== 'none'; },
  };

  start();
})();
