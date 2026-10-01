// Reads {compiled, states, cases, lattices, grids} on stdin and writes what the page's model (Shared/web/explorer-model.js) computes
// for them. tests/test_explorer_parity.py runs the same through Shared/tools/explorer_model.py and compares the two.
const fs = require('fs');
const path = require('path');
const GX = require(path.join(__dirname, '..', 'Shared', 'web', 'explorer-model.js'));

const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const model = new GX.Model(input.compiled);
const plain = (value) => (typeof value === 'number' && !Number.isFinite(value) ? (Number.isNaN(value) ? 'NaN' : value > 0 ? 'Inf' : '-Inf') : value);
const out = {
  values: input.states.map((state) => Object.fromEntries(Object.entries(model.values(state)).map(([k, v]) => [k, plain(v)]))),
  cases: input.cases.map(({ text, state }) => {
    try { return plain(model.evaluate(text, state)); } catch (error) { return { error: error.message }; }
  }),
  lattices: input.lattices.map(({ id, cap }) => model.lattice(id, cap)),
  grids: input.grids.map(({ compiled, cap }) => new GX.Model(compiled).states(cap)),
  formats: input.formats.map(([template, env, decimals, hidden]) => GX.format(
    template, Object.fromEntries(Object.entries(env).map(([k, v]) => [k, v === null ? NaN : v])), decimals, hidden)),
};
process.stdout.write(JSON.stringify(out));
