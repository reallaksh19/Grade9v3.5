const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve('public');

const explorerConfigs = [
  {
    path: 'chemistry/bonding/explorers/chemical_bonding/jee_questions_data.js',
    subject: 'Chemistry',
    topic: 'Chemical Bonding',
    topic_ref: 'chem.bonding'
  },
  {
    path: 'chemistry/gases/explorers/behaviour_of_gases/jee_questions_data.js',
    subject: 'Chemistry',
    topic: 'Behaviour of Gases',
    topic_ref: 'chem.gases'
  },
  {
    path: 'chemistry/redox/explorers/redox_reactions/jee_questions_data.js',
    subject: 'Chemistry',
    topic: 'Redox Reactions',
    topic_ref: 'chem.redox'
  },
  {
    path: 'chemistry/some-basic-concepts/explorers/mole_concept/jee_questions_data.js',
    subject: 'Chemistry',
    topic: 'Mole Concept',
    topic_ref: 'chem.mole'
  },
  {
    path: 'mathematics/vectors/explorers/vector_algebra/jee_questions_data.js',
    subject: 'Mathematics',
    topic: 'Vector Algebra',
    topic_ref: 'math.vectors'
  },
  {
    path: 'physics/motion-1d/explorers/motion_in_1d/jee_questions_data.js',
    subject: 'Physics',
    topic: 'Motion in 1D',
    topic_ref: 'phy.motion-1d'
  },
  {
    path: 'physics/motion-in-2d/explorers/motions_in_2d/jee_questions_data.js',
    subject: 'Physics',
    topic: 'Motion in 2D',
    topic_ref: 'phy.motion-2d'
  }
];

let allQuestions = [];

for (const cfg of explorerConfigs) {
  const fullPath = path.join(root, cfg.path);
  if (!fs.existsSync(fullPath)) {
    console.error('Missing file:', fullPath);
    continue;
  }
  const code = fs.readFileSync(fullPath, 'utf8');
  const sandbox = { window: {}, console: console };
  vm.createContext(sandbox);
  try {
    vm.runInContext(code, sandbox);
  } catch (err) {
    console.error('Error running:', cfg.path, err.message);
    continue;
  }

  const list = sandbox.window.JEE_QUESTIONS_DATA || [];
  console.log(`Loaded ${list.length} questions from ${cfg.path} (${cfg.subject} - ${cfg.topic})`);
  
  for (const item of list) {
    // Normalize into canonical QB question format
    const qid = item.id || `IIT-JEE-${cfg.topic_ref}-${allQuestions.length + 1}`;
    const cleanStem = (item.q || item.stem || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    
    // Parse options if available
    let opts = [];
    if (Array.isArray(item.options)) {
      opts = item.options.map(o => String(o).trim());
    }

    allQuestions.push({
      id: qid,
      stem: cleanStem,
      raw_stem: item.q || item.stem || '',
      subject: cfg.subject,
      topic: cfg.topic,
      topic_ref: cfg.topic_ref,
      source_tag: 'IIT-JEE',
      exam: item.source || item.exam || 'IIT-JEE Main',
      year: item.year || null,
      difficulty: item.difficulty || 'Medium',
      options: opts,
      correct: item.correct || item.ans || null,
      formula: item.formula || null,
      steps: item.steps || [],
      trap: item.trap || null,
      teacher_check: item.teacherCheck || null,
      subtab_name: item.subtabName || item.subtab || null,
      sim_fidelity: item.simFidelity || 'EXACT',
      explorer_entrypoint: cfg.path.replace('/jee_questions_data.js', '/index.html')
    });
  }
}

console.log(`\nTotal IIT-JEE questions extracted: ${allQuestions.length}`);

// Write JSON
const outPath = path.join(root, 'data', 'iit-jee-hub-questions.v1.json');
fs.writeFileSync(outPath, JSON.stringify(allQuestions, null, 2), 'utf8');
console.log(`Wrote normalized questions to ${outPath}`);

// Also copy to docs
const docsOut = path.resolve('docs/data/iit-jee-hub-questions.v1.json');
fs.mkdirSync(path.dirname(docsOut), { recursive: true });
fs.writeFileSync(docsOut, JSON.stringify(allQuestions, null, 2), 'utf8');
console.log(`Synced to ${docsOut}`);
