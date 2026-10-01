/* The explorer's model: the expression language and the state it is evaluated over.

   Shared/tools/explorer_expr.py and Shared/tools/explorer_model.py are the other half. They check a spec's numbers when it is
   built; this file computes the same numbers in the learner's browser. tests/test_explorer_parity.py runs both on the same states
   and fails if they differ, so a claim the page makes is a claim somebody computed. No DOM in here: it also runs under Node. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.GXModel = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const TOLERANCE = 1e-9;
  const CONSTANTS = { pi: Math.PI, e: Math.E };
  const KEYWORDS = new Set(['and', 'or', 'not']);
  const AGGREGATES = new Set(['at', 'maxover', 'minover', 'argmax', 'argmin']);
  const SWEEP_CAP = 361;
  const STATE_CAP = 3000;
  const TOKEN = /\s*(?:(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z][A-Za-z0-9_]*)|(<=|>=|==|!=|[-+*\/^(),<>]))/y;
  const RAD = Math.PI / 180;
  const DEG = 180 / Math.PI;

  class ExprError extends Error {}

  const finite = (x) => (Number.isFinite(x) ? x : NaN);
  const guard = (fn) => (...a) => finite(fn(...a));
  const equal = (x, y) => Math.abs(x - y) <= TOLERANCE * Math.max(1, Math.abs(x), Math.abs(y));
  const round = (x, digits = 0) => {
    if (!Number.isFinite(x)) return NaN;
    const scale = Math.pow(10, Math.trunc(digits));
    return Math.floor(x * scale + 0.5) / scale;
  };
  const anyNaN = (xs) => xs.some((x) => Number.isNaN(x));

  /* name -> [arity, function]; arity -1: one or more, -2: one or two; `if` is lazy and handled by the evaluator */
  const FUNCTIONS = {
    sqrt: [1, guard(Math.sqrt)], abs: [1, guard(Math.abs)], exp: [1, guard(Math.exp)], ln: [1, guard(Math.log)], log10: [1, guard(Math.log10)],
    sin: [1, guard(Math.sin)], cos: [1, guard(Math.cos)], tan: [1, guard(Math.tan)],
    asin: [1, guard(Math.asin)], acos: [1, guard(Math.acos)], atan: [1, guard(Math.atan)], atan2: [2, guard(Math.atan2)],
    sind: [1, guard((x) => Math.sin(x * RAD))], cosd: [1, guard((x) => Math.cos(x * RAD))], tand: [1, guard((x) => Math.tan(x * RAD))],
    asind: [1, guard((x) => Math.asin(x) * DEG)], acosd: [1, guard((x) => Math.acos(x) * DEG)], atand: [1, guard((x) => Math.atan(x) * DEG)],
    atan2d: [2, guard((y, x) => Math.atan2(y, x) * DEG)],
    floor: [1, guard(Math.floor)], ceil: [1, guard(Math.ceil)], round: [-2, round],
    hypot: [2, guard(Math.hypot)], pow: [2, guard(Math.pow)],
    sign: [1, guard((x) => (x > 0) - (x < 0))], clamp: [3, guard((x, lo, hi) => Math.min(Math.max(x, lo), hi))],
    min: [-1, (...xs) => (anyNaN(xs) ? NaN : Math.min(...xs))], max: [-1, (...xs) => (anyNaN(xs) ? NaN : Math.max(...xs))],
    deg: [1, guard((x) => x * DEG)], rad: [1, guard((x) => x * RAD)],
    if: [3, null],
  };

  /* ------------------------------------------------------------------ parsing */

  function tokens(source) {
    const text = source.replace(/\s+$/, '');
    const out = [];
    let position = 0;
    while (position < text.length) {
      TOKEN.lastIndex = position;
      const found = TOKEN.exec(text);
      if (!found || TOKEN.lastIndex === position) {
        const rest = text.slice(position);
        const where = position + (rest.length - rest.replace(/^\s+/, '').length);
        throw new ExprError(`unexpected character '${text[where]}' at position ${where + 1}`);
      }
      out.push(found[1] !== undefined ? ['num', found[1]] : found[2] !== undefined ? ['name', found[2]] : ['sym', found[3]]);
      position = TOKEN.lastIndex;
    }
    return out;
  }

  class Parser {
    constructor(text) { this.tokens = tokens(text); this.at = 0; }
    peek() { return this.at < this.tokens.length ? this.tokens[this.at] : null; }
    take() {
      const token = this.peek();
      if (token === null) throw new ExprError('the expression ends where more is expected');
      this.at += 1;
      return token;
    }
    accept(...symbols) {
      const token = this.peek();
      if (token && symbols.includes(token[1]) && (token[0] === 'sym' || KEYWORDS.has(token[1]))) { this.at += 1; return token[1]; }
      return null;
    }
    expect(symbol) {
      if (!this.accept(symbol)) {
        const token = this.peek();
        throw new ExprError(`expected '${symbol}'` + (token ? ` but found '${token[1]}'` : ' at the end'));
      }
    }
    parse() {
      if (!this.tokens.length) throw new ExprError('the expression is empty');
      const node = this.or();
      if (this.peek() !== null) throw new ExprError(`unexpected '${this.peek()[1]}'`);
      return node;
    }
    or() { let node = this.and(); while (this.accept('or')) node = ['or', node, this.and()]; return node; }
    and() { let node = this.not(); while (this.accept('and')) node = ['and', node, this.not()]; return node; }
    not() { return this.accept('not') ? ['not', this.not()] : this.comparison(); }
    comparison() {
      const left = this.sum();
      const op = this.accept('<=', '>=', '==', '!=', '<', '>');
      return op ? ['cmp', op, left, this.sum()] : left;
    }
    sum() {
      let node = this.product();
      for (;;) { const op = this.accept('+', '-'); if (!op) return node; node = ['bin', op, node, this.product()]; }
    }
    product() {
      let node = this.unary();
      for (;;) { const op = this.accept('*', '/'); if (!op) return node; node = ['bin', op, node, this.unary()]; }
    }
    unary() {
      const op = this.accept('-', '+');
      if (op) { const inner = this.unary(); return op === '-' ? ['neg', inner] : inner; }
      return this.power();
    }
    power() {
      const base = this.primary();
      return this.accept('^') ? ['bin', '^', base, this.unary()] : base;
    }
    primary() {
      const [kind, value] = this.take();
      if (kind === 'num') return ['num', parseFloat(value)];
      if (kind === 'name') {
        if (KEYWORDS.has(value)) throw new ExprError(`'${value}' is a keyword, not a value`);
        if (this.accept('(')) {
          const args = [];
          if (!this.accept(')')) {
            args.push(this.or());
            while (this.accept(',')) args.push(this.or());
            this.expect(')');
          }
          return ['call', value, args];
        }
        return ['var', value];
      }
      if (value === '(') { const node = this.or(); this.expect(')'); return node; }
      throw new ExprError(`unexpected '${value}'`);
    }
  }

  const parse = (text) => {
    if (typeof text !== 'string') throw new ExprError('an expression is a string');
    return new Parser(text).parse();
  };

  /* ------------------------------------------------------------------ evaluation */

  function evaluate(source, env, resolver) {
    const node = typeof source === 'string' ? parse(source) : source;
    env = env || {};

    const go = (n) => {
      switch (n[0]) {
        case 'num': return n[1];
        case 'var':
          if (Object.prototype.hasOwnProperty.call(CONSTANTS, n[1])) return CONSTANTS[n[1]];
          if (!Object.prototype.hasOwnProperty.call(env, n[1])) throw new ExprError(`'${n[1]}' has no value`);
          return Number(env[n[1]]);
        case 'neg': return -go(n[1]);
        case 'not': { const v = go(n[1]); return Number.isNaN(v) ? NaN : v !== 0 ? 0 : 1; }
        case 'and': {
          const left = go(n[1]);
          if (Number.isNaN(left)) return NaN;
          if (left === 0) return 0;
          const right = go(n[2]);
          return Number.isNaN(right) ? NaN : right !== 0 ? 1 : 0;
        }
        case 'or': {
          const left = go(n[1]);
          if (Number.isNaN(left)) return NaN;
          if (left !== 0) return 1;
          const right = go(n[2]);
          return Number.isNaN(right) ? NaN : right !== 0 ? 1 : 0;
        }
        case 'cmp': {
          const left = go(n[2]);
          const right = go(n[3]);
          if (Number.isNaN(left) || Number.isNaN(right)) return NaN;
          switch (n[1]) {
            case '<': return +(left < right);
            case '<=': return +(left <= right || equal(left, right));
            case '>': return +(left > right);
            case '>=': return +(left >= right || equal(left, right));
            case '==': return +equal(left, right);
            default: return +!equal(left, right);
          }
        }
        case 'bin': {
          const left = go(n[2]);
          const right = go(n[3]);
          if (Number.isNaN(left) || Number.isNaN(right)) return NaN;
          switch (n[1]) {
            case '+': return finite(left + right);
            case '-': return finite(left - right);
            case '*': return finite(left * right);
            case '/': return finite(left / right);
            default: return finite(Math.pow(left, right));
          }
        }
        case 'call': {
          const name = n[1];
          const args = n[2];
          if (AGGREGATES.has(name)) return aggregate(name, args);
          if (!Object.prototype.hasOwnProperty.call(FUNCTIONS, name)) throw new ExprError(`${name}() is not a function of this language`);
          if (name === 'if') {
            const condition = go(args[0]);
            if (Number.isNaN(condition)) return NaN;
            return condition !== 0 ? go(args[1]) : go(args[2]);
          }
          const values = args.map(go);
          if (anyNaN(values)) return NaN;
          return Number(FUNCTIONS[name][1](...values));
        }
        default: throw new ExprError(`unknown node ${n[0]}`);
      }
    };

    const aggregate = (name, args) => {
      if (!resolver) throw new ExprError(`${name}() reads the model, and there is no model here`);
      const named = name === 'at' ? [args[0], ...args.filter((_, i) => i % 2 === 1)] : args;
      const shapeOk = name === 'at' ? args.length >= 3 && args.length % 2 === 1 : args.length === 2;
      if (!shapeOk || named.some((a) => a[0] !== 'var')) throw new ExprError(`${name}() is not used as ${name === 'at' ? 'at(Q, p, v)' : name + '(Q, p)'}`);
      const quantity = args[0][1];
      if (name === 'at') {
        const overrides = {};
        for (let i = 1; i + 1 < args.length; i += 2) overrides[args[i][1]] = go(args[i + 1]);
        return anyNaN(Object.values(overrides)) ? NaN : Number(resolver.at(quantity, overrides));
      }
      const points = resolver.sweep(quantity, args[1][1]);
      if (!points.length || points.some(([, y]) => Number.isNaN(y))) return NaN;
      let [bestX, bestY] = points[0];
      const wantMax = name === 'maxover' || name === 'argmax';
      for (let i = 1; i < points.length; i += 1) {
        const [x, y] = points[i];
        if ((wantMax ? y > bestY : y < bestY) && !equal(y, bestY)) { bestX = x; bestY = y; }
      }
      return name === 'maxover' || name === 'minover' ? bestY : bestX;
    };

    return go(node);
  }

  const holds = (text, env, resolver) => {
    const value = evaluate(text, env, resolver);
    return !Number.isNaN(value) && value !== 0;
  };

  /* ------------------------------------------------------------------ the model */

  class Model {
    /* `compiled` is what Shared/tools/explorer_model.py compile_page_model writes into the page: parameters and the ordered steps. */
    constructor(compiled) {
      this.parameters = compiled.parameters;
      this.ids = this.parameters.map((p) => p.id);
      this.byId = Object.fromEntries(this.parameters.map((p) => [p.id, p]));
      this.steps = compiled.steps;
      this.trees = new Map();
      this.cache = new Map();
      this.sweeps = new Map();
    }
    initial() { return Object.fromEntries(this.parameters.map((p) => [p.id, Number(p.value)])); }
    free() { return this.parameters.filter((p) => !p.fixed).map((p) => p.id); }
    lattice(id, cap = SWEEP_CAP) {
      const p = this.byId[id];
      if (p.fixed) return [Number(p.value)];
      const low = Number(p.min);
      const high = Number(p.max);
      const step = Number(p.step);
      const count = Math.floor((high - low) / step + 0.5);
      let values = [];
      for (let k = 0; k <= count; k += 1) values.push(low + k * step);
      if (Math.abs(values[values.length - 1] - high) <= 1e-9 * Math.max(1, Math.abs(high))) values[values.length - 1] = high;
      if (values.length > cap) {
        const keep = new Set();
        for (let i = 0; i < cap; i += 1) keep.add(Math.floor((i * (values.length - 1)) / (cap - 1) + 0.5));
        let nearest = 0;
        for (let i = 1; i < values.length; i += 1) if (Math.abs(values[i] - p.value) < Math.abs(values[nearest] - p.value)) nearest = i;
        keep.add(nearest);
        values = [...keep].sort((a, b) => a - b).map((i) => values[i]);
      }
      return values;
    }
    caps(free, cap) {
      const sizes = free.map((id) => this.lattice(id).length);
      const product = () => sizes.reduce((a, b) => a * b, 1);
      while (product() > cap) {
        let index = 0;
        for (let i = 1; i < sizes.length; i += 1) if (sizes[i] > sizes[index]) index = i;
        if (sizes[index] <= 5) break;
        sizes[index] = Math.max(5, Math.min(sizes[index] - 1, Math.floor(sizes[index] * 0.9)));
      }
      return sizes;
    }
    states(cap = STATE_CAP) {
      const free = this.free();
      const sizes = this.caps(free, cap);
      const grids = free.map((id, i) => this.lattice(id, sizes[i]));
      const base = this.initial();
      const out = [{ ...base }];
      const index = grids.map(() => 0);
      if (!grids.every((g) => g.length)) return out;
      for (;;) {
        const state = { ...base };
        free.forEach((id, i) => { state[id] = grids[i][index[i]]; });
        if (free.some((id) => state[id] !== base[id])) out.push(state);
        let k = free.length - 1;
        while (k >= 0 && index[k] === grids[k].length - 1) { index[k] = 0; k -= 1; }
        if (k < 0) break;
        index[k] += 1;
      }
      return out;
    }
    tree(text) {
      let node = this.trees.get(text);
      if (!node) { node = parse(text); this.trees.set(text, node); }
      return node;
    }
    values(state) {
      const key = this.ids.map((id) => state[id]).join('|');
      let env = this.cache.get(key);
      if (!env) {
        env = {};
        for (const id of this.ids) env[id] = Number(state[id]);
        for (const [name, text] of this.steps) env[name] = evaluate(this.tree(text), env);
        if (this.cache.size < 200000) this.cache.set(key, env);
      }
      return env;
    }
    resolver(state) {
      const model = this;
      return {
        at(name, overrides) {
          const env = model.values({ ...state, ...overrides });
          if (!(name in env)) throw new ExprError(`'${name}' is not a parameter or a quantity`);
          return env[name];
        },
        sweep(name, parameter) {
          if (!(parameter in model.byId)) throw new ExprError(`'${parameter}' is not a parameter`);
          const others = model.ids.filter((id) => id !== parameter).map((id) => state[id]).join('|');
          const key = `${name}|${parameter}|${others}`;
          let points = model.sweeps.get(key);
          if (!points) {
            points = model.lattice(parameter).map((value) => {
              const env = model.values({ ...state, [parameter]: value });
              if (!(name in env)) throw new ExprError(`'${name}' is not a parameter or a quantity`);
              return [value, env[name]];
            });
            model.sweeps.set(key, points);
          }
          return points;
        },
      };
    }
    evaluate(text, state, extra) {
      const env = extra ? { ...this.values(state), ...extra } : this.values(state);
      return evaluate(this.tree(text), env, this.resolver(state));
    }
    holds(text, state) {
      const value = this.evaluate(text, state);
      return !Number.isNaN(value) && value !== 0;
    }
    withSet(overrides, state) {
      const out = { ...(state || this.initial()) };
      for (const [k, v] of Object.entries(overrides || {})) out[k] = Number(v);
      return out;
    }
  }

  /* ------------------------------------------------------------------ display */

  const TEMPLATE = /\{([A-Za-z][A-Za-z0-9_]*)(?::(\d+))?\}/g;

  function fixed(value, decimals) {
    if (!Number.isFinite(value)) return '—';
    const text = value.toFixed(decimals);
    return (/^-0(\.0+)?$/.test(text) ? text.slice(1) : text).replace('-', '−');
  }

  /* '{R:1} m' for an env: a value named in the braces, to the decimals after the colon (or the quantity's own). */
  function format(template, env, decimalsOf, hidden) {
    return String(template).replace(TEMPLATE, (_, name, decimals) => {
      if (hidden) return '?';
      const digits = decimals !== undefined ? Number(decimals) : (decimalsOf && decimalsOf[name] !== undefined ? decimalsOf[name] : 2);
      return name in env ? fixed(env[name], digits) : '—';
    });
  }

  return { ExprError, FUNCTIONS, AGGREGATES, parse, evaluate, holds, Model, fixed, format, equal, TEMPLATE, SWEEP_CAP, STATE_CAP };
});
