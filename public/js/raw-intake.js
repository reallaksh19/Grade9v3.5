/* Research-first intake — browser projection of Shared/tools/raw_intake.py.
 * Starts a job from raw questions, prompts and syllabus text. No canonical ids,
 * matrix, rung or learner profile are required, and the result is never a hold.
 */
(function (global) {
  'use strict';

  const SCHEMA = 'research-first-intake/v1';
  const STATUS = 'RESEARCH_AND_AUTHOR';
  const DRAFT_KEY = 'grade9v3_raw_intake_draft_v1';
  const LABEL_PREFIX = /^\s*([Qq]?[0-9]+[a-z]?)\s*[:.)]\s+([\s\S]+)$/;
  const LABEL_ONLY = /^[A-Za-z]{0,3}\s*[0-9]+[a-z]?$/;
  const STOPWORDS = new Set(('the and for with from that this into its are was were has have had how what when ' +
    'which who why find show state give take using use its their them then than per ' +
    'each after before between about over under two one also can will not all any').split(' '));

  function canonicalize(value) {
    if (Array.isArray(value)) return '[' + value.map(canonicalize).join(',') + ']';
    if (value && typeof value === 'object') {
      return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonicalize(value[k])).join(',') + '}';
    }
    return JSON.stringify(value);
  }

  function sha256(text) {
    const bytes = new TextEncoder().encode(text);
    const words = [];
    for (let i = 0; i < bytes.length; i++) words[i >> 2] |= bytes[i] << (24 - (i % 4) * 8);
    words[bytes.length >> 2] |= 0x80 << (24 - (bytes.length % 4) * 8);
    words[(((bytes.length + 8) >> 6) + 1) * 16 - 1] = bytes.length * 8;
    for (let i = 0; i < words.length; i++) words[i] = words[i] || 0;
    const k = [], h = [];
    const isPrime = n => { for (let i = 2; i * i <= n; i++) if (n % i === 0) return false; return true; };
    const frac = x => ((x - Math.floor(x)) * 0x100000000) >>> 0;
    let n = 2;
    while (k.length < 64) { if (isPrime(n)) { if (h.length < 8) h.push(frac(Math.sqrt(n))); k.push(frac(Math.cbrt(n))); } n++; }
    const rotr = (x, r) => (x >>> r) | (x << (32 - r));
    for (let i = 0; i < words.length; i += 16) {
      const w = words.slice(i, i + 16);
      for (let j = 16; j < 64; j++) {
        const x = w[j - 15] >>> 0, y = w[j - 2] >>> 0;
        const s0 = (rotr(x, 7) ^ rotr(x, 18) ^ (x >>> 3)) >>> 0;
        const s1 = (rotr(y, 17) ^ rotr(y, 19) ^ (y >>> 10)) >>> 0;
        w[j] = (w[j - 16] + s0 + w[j - 7] + s1) >>> 0;
      }
      let [a, b, c, d, e, f, g, hh] = h;
      for (let j = 0; j < 64; j++) {
        const S1 = (rotr(e, 6) ^ rotr(e, 11) ^ rotr(e, 25)) >>> 0;
        const ch = ((e & f) ^ (~e & g)) >>> 0;
        const t1 = (hh + S1 + ch + k[j] + w[j]) >>> 0;
        const S0 = (rotr(a, 2) ^ rotr(a, 13) ^ rotr(a, 22)) >>> 0;
        const maj = ((a & b) ^ (a & c) ^ (b & c)) >>> 0;
        const t2 = (S0 + maj) >>> 0;
        hh = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = b; b = a; a = (t1 + t2) >>> 0;
      }
      h[0] = (h[0] + a) >>> 0; h[1] = (h[1] + b) >>> 0; h[2] = (h[2] + c) >>> 0; h[3] = (h[3] + d) >>> 0;
      h[4] = (h[4] + e) >>> 0; h[5] = (h[5] + f) >>> 0; h[6] = (h[6] + g) >>> 0; h[7] = (h[7] + hh) >>> 0;
    }
    return h.map(x => x.toString(16).padStart(8, '0')).join('');
  }

  const digest = value => 'sha256:' + sha256(typeof value === 'string' ? value : canonicalize(value));
  const clean = text => String(text == null ? '' : text).split(/\s+/).filter(Boolean).join(' ');
  const tokens = text => (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter(t => t.length >= 3 && !STOPWORDS.has(t));
  const itemId = (prefix, text) => prefix + sha256(clean(text).toLowerCase()).slice(0, 10);

  function conditions(text) {
    const seen = [];
    for (const v of text.match(/[0-9]+(?:\.[0-9]+)?/g) || []) if (!seen.includes(v)) seen.push(v);
    return seen;
  }

  function lines(value) {
    if (value == null) return [];
    if (typeof value === 'string') return value.split(/\r\n|\r|\n/).map(clean).filter(Boolean);
    return Array.from(value);
  }

  function question(raw) {
    if (typeof raw === 'string') raw = {text: raw};
    let text = clean(raw.text);
    let label = clean(raw.label) || null;
    const m = LABEL_PREFIX.exec(text);
    if (m && !label) { label = m[1]; text = clean(m[2]); }
    const sourceHint = clean(raw.source_hint) || null;
    if (!text || LABEL_ONLY.test(text)) {
      label = label || text || null;
      return {id: itemId('q', 'label:' + (label || '')), text: '', label, source_hint: sourceHint,
        conditions: [], text_status: 'LABEL_ONLY', identity_claim_requested: true};
    }
    return {id: itemId('q', text), text, label, source_hint: sourceHint, conditions: conditions(text),
      text_status: 'SUPPLIED', identity_claim_requested: Boolean(label || sourceHint)};
  }

  function dedupe(rows) {
    const seen = new Map();
    for (const row of rows) {
      if (seen.has(row.id)) seen.get(row.id).supplied_count += 1;
      else seen.set(row.id, Object.assign({}, row, {supplied_count: 1}));
    }
    return Array.from(seen.values());
  }

  function reconcile(questions, syllabus) {
    const subTokens = new Map(syllabus.map(r => [r.id, new Set(tokens(r.text))]));
    const links = [], outside = [], used = new Set();
    for (const q of questions) {
      const words = new Set(tokens(q.text));
      let best = [], bestScore = 0;
      for (const r of syllabus) {
        let score = 0;
        for (const w of words) if (subTokens.get(r.id).has(w)) score++;
        if (score > bestScore) { best = [r.id]; bestScore = score; }
        else if (score === bestScore && score > 0) best.push(r.id);
      }
      if (bestScore === 0) outside.push(q.id);
      best.forEach(id => used.add(id));
      links.push({question_id: q.id, subtopic_ids: best, basis: 'LEXICAL_PROPOSAL'});
    }
    return {question_to_subtopic: links, questions_outside_syllabus: outside,
      subtopics_without_questions: syllabus.map(r => r.id).filter(id => !used.has(id))};
  }

  function researchTasks(prompts, questions, syllabus, rec) {
    const tasks = [];
    const add = (kind, inputId, needs) => tasks.push({id: kind + ':' + inputId, kind, input_id: inputId, needs});
    prompts.forEach(r => add('interpret_prompt', r.id, ['scope', 'learner_goal']));
    questions.forEach(r => {
      if (r.text_status === 'LABEL_ONLY') add('recover_question_text', r.id, ['original_text', 'source_locator']);
      if (r.identity_claim_requested) add('resolve_source_identity', r.id, ['source_text', 'matching_conditions', 'discriminator']);
      add('solve_and_explain', r.id, ['worked_answer', 'hint', 'visual']);
    });
    const outside = new Set(rec.questions_outside_syllabus);
    questions.forEach(r => { if (outside.has(r.id)) add('place_unmatched_question', r.id, ['owning_subtopic', 'teaching']); });
    syllabus.forEach(r => add('teach_subtopic', r.id, ['explanation', 'worked_example', 'visual', 'misconception', 'reconstruction']));
    rec.subtopics_without_questions.forEach(id => add('author_practice', id, ['practice_question', 'worked_answer']));
    return tasks;
  }

  function intake(request, workflow) {
    const subject = clean(request.subject);
    const prompts = dedupe(lines(request.prompts).map(clean).filter(Boolean).map(t => ({id: itemId('p', t), text: t})));
    const questions = dedupe(lines(request.questions).map(question));
    const syllabus = dedupe(lines(request.syllabus).map(clean).filter(Boolean).map(t => ({id: itemId('s', t), text: t})));
    const errors = [];
    if (!subject) errors.push('subject is required (free text; no canonical id needed)');
    if (!(prompts.length || questions.length || syllabus.length)) errors.push('supply at least one prompt, question or syllabus subtopic');
    const owner = ((request.learner || {}).knowledge_percentage);
    const ownerGiven = typeof owner === 'number' && Number.isFinite(owner);
    const learner = Object.assign({}, workflow.default_learner_start, {
      source: ownerGiven ? 'OWNER_ESTIMATE_AS_START_ONLY' : 'DEFAULT_MEDIAN',
      knowledge_percentage: ownerGiven ? owner : workflow.default_learner_start.knowledge_percentage,
      blocking: false
    });
    const rec = reconcile(questions, syllabus);
    const inputs = {prompts, questions, syllabus};
    const ledger = [];
    [['question', questions], ['syllabus', syllabus]].forEach(([kind, rows]) => rows.forEach(r =>
      ledger.push({input_id: r.id, kind, teaching: null, practice: null, learner_location: null})));
    const grade = clean(request.grade) || null;
    const body = {
      schema: SCHEMA, workflow_digest: digest(workflow), subject, grade, learner_start: learner,
      inputs, reconciliation: rec, research_tasks: researchTasks(prompts, questions, syllabus, rec),
      coverage_ledger_template: ledger, deliverables: workflow.deliverables.slice(),
      invariants: workflow.invariants.map(r => r.id), status: errors.length ? 'INVALID_REQUEST' : STATUS, errors
    };
    body.intake_digest = digest({subject, grade, inputs});
    return body;
  }

  /* Blocks separated by blank lines; an optional line "Source: ..." carries a source hint. */
  function parseQuestionBlocks(text) {
    return String(text || '').split(/\n\s*\n/).map(block => {
      const rows = block.split(/\r\n|\r|\n/);
      const hint = rows.find(r => /^\s*source\s*:/i.test(r));
      const body = rows.filter(r => r !== hint).join(' ');
      const q = {text: clean(body)};
      if (hint) q.source_hint = clean(hint.replace(/^\s*source\s*:/i, ''));
      return q;
    }).filter(q => q.text || q.source_hint);
  }

  function agentPrompt(plan, workflow) {
    const out = [];
    out.push('# Research-first learner-product job', '');
    out.push(`Subject: ${plan.subject}${plan.grade ? ' · Grade ' + plan.grade : ''}`);
    out.push(`Intake digest: ${plan.intake_digest}`, '');
    out.push('## Workflow invariants (Shared/workflows/research-first.v1.json)');
    workflow.invariants.forEach(r => out.push(`- **${r.id}** — ${r.rule}`));
    out.push('', '## Learner start');
    out.push(`Start at the ${plan.learner_start.level} level (knowledge ${plan.learner_start.knowledge_percentage}%, ${plan.learner_start.source}) with ${plan.learner_start.support} support. ${plan.learner_start.diagnostic.rule}`);
    out.push('Missing learner data takes the default median value and never blocks authoring.', '');
    out.push('## No escape state');
    out.push('There is no hold, fail or incomplete outcome. Every gap is a research or authoring duty completed in this job:');
    Object.values(workflow.escape_state_duties).forEach(d => out.push(`- ${d.duty}: ${d.do}`));
    out.push('');
    out.push('## Inputs to reconcile — every one must reach teaching, practice and a learner-facing location');
    plan.inputs.syllabus.forEach(r => out.push(`- [${r.id}] syllabus: ${r.text}`));
    plan.inputs.questions.forEach(r => out.push(`- [${r.id}] question${r.label ? ' (owner label ' + r.label + ', not an identity)' : ''}: ${r.text || '(label only: recover the original text)'}`));
    plan.inputs.prompts.forEach(r => out.push(`- [${r.id}] prompt: ${r.text}`));
    if (plan.reconciliation.questions_outside_syllabus.length) {
      out.push('', 'Questions outside the supplied syllabus (research the owning subtopic and add it): ' + plan.reconciliation.questions_outside_syllabus.join(', '));
    }
    out.push('', '## Research and authoring tasks');
    plan.research_tasks.forEach(t => out.push(`- ${t.id} → ${t.needs.join(', ')}`));
    out.push('', '## Deliver', 'Research and author into the research library, promote verified records',
      '(`python3 Shared/tools/promote_verified.py`), render the six Cores with',
      '`python3 Shared/tools/render_core.py build --manifest product.json --out OUT` and pass',
      '`python3 Shared/tools/quality_gate.py OUT`. A hold is never an output.');
    return out.join('\n') + '\n';
  }

  function mount(doc, workflow) {
    const $ = id => doc.getElementById(id);
    const form = $('intakeForm');
    if (!form) return;
    const fields = ['subject', 'grade', 'prompts', 'questions', 'syllabus', 'knowledge'];
    try {
      const draft = JSON.parse(global.localStorage.getItem(DRAFT_KEY) || '{}');
      fields.forEach(f => { if (draft[f] != null) $(f).value = draft[f]; });
    } catch (e) { /* storage unavailable */ }
    let last = null;
    const download = (name, text) => {
      const a = doc.createElement('a');
      a.href = URL.createObjectURL(new Blob([text], {type: 'application/json'}));
      a.download = name; a.click();
    };
    form.addEventListener('submit', ev => {
      ev.preventDefault();
      const draft = {}; fields.forEach(f => { draft[f] = $(f).value; });
      try { global.localStorage.setItem(DRAFT_KEY, JSON.stringify(draft)); } catch (e) { /* ignore */ }
      const k = draft.knowledge.trim();
      const request = {subject: draft.subject, grade: draft.grade, prompts: draft.prompts,
        questions: parseQuestionBlocks(draft.questions), syllabus: draft.syllabus};
      if (k !== '') request.learner = {knowledge_percentage: Number(k)};
      const plan = intake(request, workflow);
      last = {request, plan, prompt: agentPrompt(plan, workflow)};
      $('state').textContent = plan.status === STATUS ? 'Ready to research and author' : 'Needs input';
      $('errors').hidden = !plan.errors.length;
      $('errors').textContent = plan.errors.join(' ');
      const tbody = $('ledgerBody');
      tbody.textContent = '';
      const rows = plan.inputs.syllabus.map(r => ['syllabus', r.id, r.text, 'teach_subtopic'])
        .concat(plan.inputs.questions.map(r => ['question', r.id, r.text || '(label ' + r.label + ')',
          plan.research_tasks.filter(t => t.input_id === r.id).map(t => t.kind).join(', ')]));
      rows.forEach(cells => {
        const card = doc.createElement('div');
        card.className = 'ledger-card';
        const icon = cells[0] === 'syllabus' ? '📚' : '❓';
        card.innerHTML = '<div class="ledger-card-head"><span class="ledger-kind">' + icon + ' <strong>' + cells[0].toUpperCase() + '</strong></span><code>' + cells[1] + '</code></div><div class="ledger-card-body"><div class="ledger-text">' + cells[2] + '</div><div class="ledger-task">🔍 <strong>Research:</strong> <span>' + cells[3] + '</span></div></div>';
        tbody.appendChild(card);
      });
      $('promptPreview').textContent = last.prompt;
      ['copyPrompt', 'downloadRequest', 'downloadIntake', 'downloadPrompt'].forEach(id => { $(id).disabled = false; });
    });
    $('copyPrompt').addEventListener('click', () => last && global.navigator.clipboard && global.navigator.clipboard.writeText(last.prompt));
    $('downloadRequest').addEventListener('click', () => last && download('raw-request.json', JSON.stringify(last.request, null, 2)));
    $('downloadIntake').addEventListener('click', () => last && download('intake.json', JSON.stringify(last.plan, null, 2)));
    $('downloadPrompt').addEventListener('click', () => last && download('agent-prompt.md', last.prompt));
  }

  global.RAW_INTAKE = {intake, digest, sha256, canonicalize, parseQuestionBlocks, agentPrompt, tokens, conditions};
  if (global.document && global.GRADE9V3_RESEARCH_FIRST_WORKFLOW) {
    global.document.addEventListener('DOMContentLoaded', () => mount(global.document, global.GRADE9V3_RESEARCH_FIRST_WORKFLOW));
  }
})(typeof window !== 'undefined' ? window : globalThis);
