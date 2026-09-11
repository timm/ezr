const {exp, sqrt, log2, abs, max, min} = Math
const Num = () => [0, 0, 0]                // n, mu, m2: all Welford keeps
const isSym = c => c instanceof Map
const rnd = () => (SEED = SEED * 16807 % 2147483647) / 2147483647
const shuffle = a => {                     // Fisher-Yates, in shared rnd order
  a = [...a]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}
const sd = c => c[0] < 2 ? 0 : sqrt(c[2] / (c[0] - 1))
const add = (c, v, inc = 1) => {           // new Num, or updated Sym
  if (v === "?") return c
  if (isSym(c)) { c.set(v, (c.get(v) || 0) + inc); return c }
  let [n, mu, m2] = c
  n += inc
  const d = v - mu
  mu += inc * d / max(1, n)
  return [n, mu, max(0, m2 + inc * d * (v - mu))]
}
const adds = (lst, it = Num()) => lst.reduce((c, y) => add(c, y), it)
const sum = (a, f) => a.reduce((s, x) => s + f(x), 0)
const size = c => isSym(c) ? sum([...c.values()], v => v) : c[0]
const div = c => {                         // Num: sd. Sym: entropy
  if (!isSym(c)) return sd(c)
  const n = size(c)
  return -sum([...c.values()], v => v > 0 ? v / n * log2(v / n) : 0)
}
const addRow = (tbl, row = null, inc = 1) => {   // inc=-1 pops the last row
  tbl._mids = null
  if (inc > 0) tbl.rows.push(row); else row = tbl.rows.pop()
  for (const at in tbl.cols) tbl.cols[at] = add(tbl.cols[at], row[at], inc)
  return row
}
const Tbl = src => {
  const tbl = {rows: [], cols: {}, x: [], y: {}, names: src[0], klass: null}
  src[0].forEach((s, at) => {
    if (s.endsWith("X")) return
    tbl.cols[at] = s[0] === s[0].toUpperCase() ? Num() : new Map()
    if (s.endsWith("!")) tbl.klass = at
    else if ("+-".includes(s.at(-1))) tbl.y[at] = s.endsWith("+") ? 1 : 0
    else tbl.x.push(at)
  })
  src.slice(1).forEach(row => addRow(tbl, row))
  return tbl
}
const clone = (tbl, rows = []) => Tbl([tbl.names, ...rows])
const norm = (col, v) =>
  1 / (1 + exp(-1.7 * max(-3, min(3, (v - col[1]) / (1e-32 + sd(col))))))
const mid = col => isSym(col)
  ? [...col.keys()].reduce((a, b) => col.get(a) >= col.get(b) ? a : b) : col[1]
const mids = tbl => tbl._mids ||=          // x centroid; cached until rows change
  Object.fromEntries(tbl.x.map(at => [at, mid(tbl.cols[at])]))
const mink = gaps => (sum(gaps, g => g ** P) / gaps.length) ** (1 / P)
const ydist = (tbl, row) => mink(Object.keys(tbl.y).map(at =>
  abs(norm(tbl.cols[at], row[at]) - tbl.y[at])))
const _dist = (col, a, b) => a === "?" || b === "?" ? 1
  : isSym(col) ? (a !== b ? 1 : 0) : abs(norm(col, a) - norm(col, b))
const xdist = (tbl, row, m) =>
  mink(tbl.x.map(at => _dist(tbl.cols[at], row[at], m[at])))
const ymu = (tbl, rows) => sum(rows, r => ydist(tbl, r)) / rows.length
const ymids = (tbl, rows) =>
  Object.keys(tbl.y).map(at => sum(rows, r => r[at]) / rows.length)
const centroid = (tbl, best, rest) => z =>  // near best, far from rest
  xdist(tbl, z, mids(rest)) - xdist(tbl, z, mids(best))
const label = (tbl, best, rest, row) => {  // keep best pool near sqrt
  addRow(best, row)
  best.rows.sort((p, q) => ydist(tbl, p) - ydist(tbl, q))
  const b = best.rows.length, r = rest.rows.length
  if (b > sqrt(1 + b + r)) addRow(rest, addRow(best, null, -1))
}
const acquire = (tbl, cap = Stop, score = centroid) => {  // pop the top scorer
  const best = clone(tbl), rest = clone(tbl)
  const todo = shuffle(tbl.rows).slice(0, Few)
  for (let i = 0; i < Start; i++) label(tbl, best, rest, todo.pop())
  while (todo.length && best.rows.length + rest.rows.length < cap) {
    const f = score(tbl, best, rest)
    todo.sort((p, q) => f(p) - f(q))
    label(tbl, best, rest, todo.pop())
  }
  return [...best.rows, ...rest.rows]
}
const cohen = (xs, ys, d = 0.35, eps = 0) => {  // gap vs pooled sd, floored
  const a = adds(xs), b = adds(ys)
  const pool = ((a[0]-1) * sd(a)**2 + (b[0]-1) * sd(b)**2) / (a[0]+b[0]-2)
  return abs(a[1] - b[1]) <= max(eps, d * sqrt(pool))
}
const cliffs = (xs, ys, d = 0.197) => {    // sorted in. rank imbalance ok?
  let gt = 0, lt = 0, j = 0, k = 0
  for (const x of xs) {
    while (j < ys.length && ys[j] <  x) { j++; k = j }
    while (k < ys.length && ys[k] <= x) k++
    gt += j; lt += ys.length - k
  }
  return abs(gt - lt) / (xs.length * ys.length) <= d
}
const ks = (xs, ys, a = 1.36) => {         // sorted in. 95% kolmogorov-smirnov
  const n = xs.length, m = ys.length
  let i = 0, j = 0, d = 0
  while (i < n && j < m) {
    const v = min(xs[i], ys[j])
    while (i < n && xs[i] <= v) i++
    while (j < m && ys[j] <= v) j++
    d = max(d, abs(i / n - j / m))
  }
  return d <= a * sqrt((n + m) / (n * m))
}
const same = (xs, ys, eps = 0) => {        // indistinguishable, by all three
  xs = [...xs].sort((a, b) => a - b); ys = [...ys].sort((a, b) => a - b)
  return cliffs(xs, ys) && ks(xs, ys) && cohen(xs, ys, 0.35, eps)
}
