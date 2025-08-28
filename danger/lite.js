help = `
ezr0.js: lightweight incremental multi-objective optimization   
(c) 2025, Tim Menzies <timm@ieee.org>, MIT license   
   
    -A  Any=4              on init, how many initial guesses?   
    -B  Budget=50          when growing theory, how many labels?   
    -D  Delta=smed         required effect size test for cliff's delta
    -F  Few=128            sample size of data random sampling  
    -K  Ks=0.95            confidence for Kolmogorov–Smirnov test
    -p  p=2                distance co-efficient
    -s  seed=1234567891    random number seed   
    -f  file=../../moot/optimize/misc/auto93.csv  data file 
    -h                     show help   
`
function label(row) { return row }

//--------------------------------------------------------------------
the = {}
big = 1e32
say = console.log
min = Math.min; max = Math.max; sqrt = Math.sqrt
abs = Math.abs; floor = Math.floor; round = Math.round

function atom(s) {
  let n = Number(s)
  if (!isNaN(n)) return n
  s = s.trim(); return {'True':true,'False':false}[s] || s }

for (let [,k,v] of help.matchAll(/(\w+)=(\S+)/g)) the[k] = atom(v)

//--------------------------------------------------------------------
function Num(s = "", i = 0) { 
  return { it: Num, i: i, txt: s, n: 0, 
           mu: 0, m2: 0, sd: 0, hi: -big, lo: big, 
           more: /-$/.test(s) ? 0 : 1 }}

function Sym(s = "", i = 0) { 
  return { it: Sym, i: i, txt: s, n: 0, has: {} }}

function Cols(names) {
  let all = names.map((s, c) => (/^[A-Z]/.test(s) ? Num : Sym)(s, c))
  return { it: Cols, names: names, all: all, 
           x: all.filter(col => !/[X\-+]$/.test(col.txt)), 
           y: all.filter(col =>   /[\-+]$/.test(col.txt))}}

function Data(src) { 
  return adds(src.slice(1), 
             { it: Data, n: 0, mid: null, rows: [], cols: Cols(src[0]) })}

function clone(data, rows = []) { return adds(rows, Data([data.cols.names]))}

function adds(src, obj = null) {
  obj ||= Num(); src.forEach(x => add(obj, x)); return obj }

function sub(i, v, zap = false) { return add(i, v, -1, zap) }

function add(i, v, inc = 1, zap = false) {
  if (v === "?") return v
  if (i.it === Sym) {
    i.has[v] = inc + (i.has[v] || 0)
  } else if (i.it === Num) {
    i.n += inc
    i.lo = min(v, i.lo)
    i.hi = max(v, i.hi)
    if (inc < 0 && i.n < 2) i.sd = i.m2 = i.mu = i.n = 0
    else {
      let d = v - i.mu
      i.mu += inc * (d / i.n)
      i.m2 += inc * (d * (v - i.mu))
      i.sd  = i.n < 2 ? 0 : sqrt(max(0, i.m2) / (i.n - 1))
    }
  } else if (i.it === Data) {
    i.mid = null
    i.n  += inc
    if (inc > 0) i.rows.push(v)
    else if (zap) i.rows.splice(i.rows.indexOf(v), 1)
    i.cols.all.forEach(col => add(col, v[col.i], inc))
  }
  return v }

//--------------------------------------------------------------------
function norm(num, v) { 
  return v === "?" ? v : (v - num.lo) / (num.hi - num.lo + 1e-32) }

function mids(data) { 
  return data.mid ||= data.cols.all.map(col => mid(col)) }

function mid(col) { return col.it === Num ? col.mu : argmax(col.has) }

//--------------------------------------------------------------------
function dist(src) {
  let d = 0, n = 0
  for (let v of src) { n++; d += v**the.p }
  return (d/n) ** (1/the.p) }

function disty(data, row) {
  return dist(data.cols.y.map(c => abs(norm(c, row[c.i]) - c.more))) }

function distysort(data, rows = null) {
  return (rows || data.rows).sort((a,b) => disty(data,a) - disty(data,b))}

function distx(data, row1, row2) {
  function fn(col, a, b) {
    if (a === "?" && b === "?") return 1
    if (col.it === Sym) return a !== b ? 1 : 0
    a = norm(col, a)
    b = norm(col, b)
    a = a !== "?" ? a : (b > 0.5 ? 0 : 1)
    b = b !== "?" ? b : (a > 0.5 ? 0 : 1)
    return abs(a - b) }
  return dist(data.cols.x.map(col => fn(col, row1[col.i], row2[col.i]))) }

//--------------------------------------------------------------------
function likely(data, rows = null) {
  rows = rows || data.rows
  x = clone(data, shuffle(rows.slice()))
  xy = clone(data)
  best = clone(data) 
  rest = clone(data)
  
  // label anything
  for (let i = 0; i < the.Any; i++) add(xy, label( sub(x, x.rows.pop())))
  
  // divide labelled items into best and rest
  xy.rows = distysort(xy)
  n = round(the.Any**0.5)
  adds(xy.rows.slice(0, n), best)
  adds(xy.rows.slice(n), rest)
  
  // loop, labelling the best guess
  while (x.n > 2 && xy.n < the.Budget) {
    add(xy, add(best, sub(x, label(guess(xy, best, rest, x)))))
    if (best.n > xy.n**0.5) {
      best.rows = distysort(xy, best.rows)
      while (best.n > xy.n**0.5) {
        add(rest, sub(best, best.rows.pop())) }}}
  return distysort(xy) }

function guess(xy, best, rest, x) {
  for (let i = 0; i < the.Few; i++) {
    let idx = floor(rand() * x.n)
    let row = x.rows[idx]
    if (distx(xy, mids(best), row) < distx(xy, mids(rest), row)) {
      return x.rows.splice(idx, 1)[0] }}
  return x.rows.pop() }

//--------------------------------------------------------------------
function distKpp(data, rows, k=20) {
  rows = shuffle((rows || data.rows).slice())
  let out = [rows[0]]
  while (out.length < min(k, rows.length)) {
    let tmp = sample(rows, min(the.Few, rows.length))
    let ws  = tmp.map(r =>
      min(...out.map(c => { let d = distx(data, r, c); return d*d })))
    let p = ws.reduce((a,b)=>a+b,0) * rand()
    let j = ws.findIndex(w => (p -= w) <= 0)
    out.push(tmp[j < 0 ? tmp.length - 1 : j]) }
  return out }

//--------------------------------------------------------------------
function fyi(s) { process.stderr.write(s) }

function sample(xs, n) { return shuffle(xs.slice()).slice(0, n) }

function shuffle(arr) { return arr.sort(() => rand() - 0.5) }

function argmax(obj) { 
  return Object.keys(obj).reduce((a,b) => obj[a] > obj[b] ? a : b) }

function csv(file, sep=',', com='%') {
  let txt = require('fs').readFileSync(file,'utf8')
  return txt.split(/\r?\n/)
    .map(l => l.split(com)[0].trim())
    .filter(Boolean)
    .map(l => l.split(sep).map(s => atom(s.trim()))) }

let rngSeed = 1
function srand(s) { rngSeed = s >>> 0 }

function rand() {
  rngSeed = (1664525 * rngSeed + 1013904223) >>> 0
  return rngSeed / 2**32 }

function main(funs) {
  let args = process.argv.slice(2)
  for (let i=0; i<args.length; i++) {
    let arg = args[i]
    let fn  = funs[`eg${arg.replace(/-/g,'_')}`] || funs[arg]
    if (fn) {
      srand(the.seed)   
      fn()
    } else {
      if (arg === '-h') { console.log(help); process.exit(0) }
      for (let key of Object.keys(the)) {
        if (arg === '-' + key[0]) the[key] = atom(args[++i]) }}}}

function statsSame(x,y){
  x = x.slice().sort((a,b)=>a-b)
  y = y.slice().sort((a,b)=>a-b)
  let n=x.length, m=y.length

  // Cliff's delta (|P(x>y)-P(x<y)|)
  let gt=0, lt=0
  for (let a of x) for (let b of y) gt+=a>b, lt+=a<b
  let delta = abs(gt-lt)/(n*m)

  // KS distance (max CDF gap) via merge-walk
  let i=0,j=0,d=0
  while(i<n && j<m){
    x[i] <= y[j] ? i++ : j++
    let fx = i/n, fy = j/m
    d = max(d, abs(fx-fy))
  }
  d = max(d, abs(1 - j/m), abs(i/n - 1))
  let a = +(1-the.Ks).toFixed(2)
  let ksCrit = ({0.1:1.22, 0.05:1.36, 0.01:1.63}[a] ?? 1.36)
  let delCrit = ({small:0.11, smed:0.195, medium:0.28, large:0.43}[the.Delta] ?? 0.11)
  return delta <= delCrit && d <= ksCrit * ((n+m)/(n*m))**0.5 }

function statsTop(rxs, reverse=false, same=statsSame, eps=0.01){
  let sum = a => a.reduce((s,x)=>s+x,0), mean = a => sum(a)/a.length
  let xs = Object.entries(rxs)
    .filter(([,v])=>v && v.length)
    .map(([k,v])=>({k,v,mu:mean(v)}))
    .sort((a,b)=> reverse ? b.mu-a.mu : a.mu-b.mu)

  while(xs.length>1){
    let best=-1, gap=0
    for(let i=1;i<xs.length;i++){
      let L = xs.slice(0,i).flatMap(o=>o.v)
      let R = xs.slice(i).flatMap(o=>o.v)
      let g = abs(mean(L)-mean(R))
      if (g>eps && g>gap) gap=g, best=i 
    }
    if (best<0) break
    let L = xs.slice(0,best).flatMap(o=>o.v)
    let R = xs.slice(best).flatMap(o=>o.v)
    if (same(L,R)) break
    xs = xs.slice(0,best) 
  }
  return new Set(xs.map(o=>o.k)) }

function worker(buds, R=20){
  let d = Data(csv(the.file))
  let base = adds(d.rows.map(r=>disty(d,r)))
  let best = rs => disty(d, distysort(d,rs)[0])
  let gen  = {rand:_=>sample(d.rows,the.Budget),
              kpp :_=>distKpp(d,undefined,the.Budget),
              near:_=>likely(d)}
  let t0 = process.hrtime.bigint()

  let out = Object.fromEntries(buds.flatMap(b => (
    the.Budget=b, fyi(`${b}.`),
    Object.keys(gen).map(k => [`${b}_${k}`, Array.from({length:R}, _ => best(gen[k]()))])
  )))

  let all = Object.values(out).flat()
  let eps = adds(all).sd * 0.35
  let top = [...statsTop(out,false,statsSame,eps)].sort()
  let mu  = adds(top.flatMap(k=>out[k])).mu

  let win = v => Math.trunc(100*(1 - (v - base.lo)/(base.mu - base.lo)))
  let per = Math.trunc(Number(process.hrtime.bigint()-t0)/(R*1e6))
  let name= the.file.replace(/.*\//,'')
  console.log([win(mu), name, per,
               ...[eps, base.mu, base.lo, mu].map(x=>Math.trunc(100*x)),
               ...top].join(', '))
}

eg = {}
eg['10'] = _ => worker([10])
eg['20'] = _ => worker([10,20])
eg['40'] = _ => worker([10,20,30,40])
eg['80'] = _ => worker([10,20,30,40,50,60,70,80])

if (require.main === module) main(eg)
;

`
Write JavaScript in a terse, AWK-like style:

- No semicolons (rely on ASI)
- No const/let keywords when possible (use globals like: the = {}, big = 1e32)
- One-line functions when feasible
- Compact aliases: min,max,sqrt,abs = Math.min,Math.max,Math.sqrt,Math.abs
- Use regex for pattern matching: /^[A-Z]/.test(s), /-$/.test(s)
- Template literals with backticks for multi-line strings
- Simple object literals, no classes
- Functional style: map/filter/reduce over loops  
- Short variable names: i, n, d, col, src
- Compact conditionals: x ||= defaultValue, x = x || defaultValue
- Ternary operators over if/else: return x === "?" ? x : (x - lo) / (hi - lo)
- Direct array methods: .slice(), .pop(), .push(), .splice()
- Inline small helpers inside functions when appropriate
- Use destructuring: let [,k,v] of str.matchAll(/regex/g)
- Pattern: Object.keys(obj).reduce((a,b) => obj[a] > obj[b] ? a : b) for argmax
- Simple for loops: for (let v of src), for (let i = 0; i < n; i++)
- Extract repeated Math functions to short aliases
- Think AWK/shell scripting: direct, imperative, minimal ceremony, maximum readability through compactness
- Avoid verbose JavaScript idioms, prefer concise functional equivalents
`
