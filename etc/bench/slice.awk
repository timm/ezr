# Rows live once in the global ROWS[idx][at]; tables hold indices.
function rnd() {                         # MINSTD, shared by all ports
  SEED = (SEED * 16807) % 2147483647
  return SEED / 2147483647 }
function shuffle(src, n, dst,   i, j, t) {   # Fisher-Yates, shared order
  for (i = 1; i <= n; i++) dst[i] = src[i]
  for (i = n; i > 1; i--) {
    j = int(rnd() * i) + 1
    t = dst[i]; dst[i] = dst[j]; dst[j] = t } }
function sd(c) { return c["n"] < 2 ? 0 : sqrt(c["m2"] / (c["n"] - 1)) }
function add(c, v, inc,   d, i) {        # inc=-1 undoes
  if (v == "?") return
  if (c["sym"]) {
    for (i = 1; i <= c["k"]; i++)
      if (c["v"][i] == v) { c["c"][i] += inc; return }
    c["k"]++; c["v"][c["k"]] = v; c["c"][c["k"]] = inc; return }
  c["n"] += inc
  d = v - c["mu"]
  c["mu"] += inc * d / (c["n"] > 1 ? c["n"] : 1)
  c["m2"] += inc * d * (v - c["mu"])
  if (c["m2"] < 0) c["m2"] = 0 }
function size(c,   i, s) {
  if (!c["sym"]) return c["n"]
  for (i = 1; i <= c["k"]; i++) s += c["c"][i]
  return s }
function div(c,   i, n, s) {             # Num: sd. Sym: entropy
  if (!c["sym"]) return sd(c)
  n = size(c)
  for (i = 1; i <= c["k"]; i++)
    if (c["c"][i] > 0) s += c["c"][i]/n * log(c["c"][i]/n)/log(2)
  return -s }
function addRow(tid, idx, inc,   at, n) {    # inc=-1 pops the last row
  delete TB[tid]["mids"]
  n = TB[tid]["n"]
  if (inc >= 0) { n++; TB[tid]["rows"][n] = idx; TB[tid]["n"] = n; inc = 1 }
  else { idx = TB[tid]["rows"][n]; delete TB[tid]["rows"][n]
         TB[tid]["n"] = n - 1 }
  for (at = 0; at < NCOL; at++)
    if (USED[at]) add(TB[tid]["cols"][at], ROWS[idx][at], inc)
  return idx }
function Tbl(tid,   at, s, last) {
  delete TB[tid]
  TB[tid]["n"] = 0; TB[tid]["nx"] = 0; TB[tid]["ny"] = 0
  for (at = 0; at < NCOL; at++) {
    s = NAMES[at]; last = substr(s, length(s), 1)
    if (last == "X") continue
    USED[at] = 1
    TB[tid]["cols"][at]["sym"] = (substr(s,1,1) ~ /[A-Z]/) ? 0 : 1
    TB[tid]["cols"][at]["n"] = 0; TB[tid]["cols"][at]["mu"] = 0
    TB[tid]["cols"][at]["m2"] = 0; TB[tid]["cols"][at]["k"] = 0
    if (last == "!") TB[tid]["klass"] = at
    else if (last == "+" || last == "-") {
      TB[tid]["ny"]++; TB[tid]["yat"][TB[tid]["ny"]] = at
      TB[tid]["yw"][TB[tid]["ny"]] = (last == "+") ? 1 : 0 }
    else { TB[tid]["nx"]++; TB[tid]["xat"][TB[tid]["nx"]] = at } } }
function norm(c, v,   z) {
  z = (v - c["mu"]) / (1e-32 + sd(c))
  if (z < -3) z = -3
  if (z >  3) z =  3
  return 1 / (1 + exp(-1.7 * z)) }
function mid(c,   i, bi) {
  if (!c["sym"]) return c["mu"]
  bi = 1
  for (i = 1; i <= c["k"]; i++) if (c["c"][i] > c["c"][bi]) bi = i
  return c["v"][bi] }
function mids(tid,   i, at) {            # x centroid; cached until rows change
  if ("mids" in TB[tid]) return
  for (i = 1; i <= TB[tid]["nx"]; i++) {
    at = TB[tid]["xat"][i]
    TB[tid]["mids"][at] = mid(TB[tid]["cols"][at]) } }
function mink(g, n,   i, s) {
  for (i = 1; i <= n; i++) s += g[i] ^ P
  return (s / n) ^ (1 / P) }
function ydist(tid, idx,   i, at, g) {
  for (i = 1; i <= TB[tid]["ny"]; i++) {
    at = TB[tid]["yat"][i]
    g[i] = norm(TB[tid]["cols"][at], ROWS[idx][at]) - TB[tid]["yw"][i]
    if (g[i] < 0) g[i] = -g[i] }
  return mink(g, TB[tid]["ny"]) }
function dist1(c, a, b,   z) {
  if (a == "?" || b == "?") return 1
  if (c["sym"]) return (a != b) ? 1 : 0
  z = norm(c, a) - norm(c, b)
  return z < 0 ? -z : z }
function xdist(tid, idx, m,   i, at, g) {    # m: a mids array or a row
  for (i = 1; i <= TB[tid]["nx"]; i++) {
    at = TB[tid]["xat"][i]
    g[i] = dist1(TB[tid]["cols"][at], ROWS[idx][at], m[at]) }
  return mink(g, TB[tid]["nx"]) }
function ymu(tid, n,   i, s) {
  for (i = 1; i <= n; i++) s += ydist(tid, TB[tid]["rows"][i])
  return s / n }
function centroid(idx) {                 # near best, far from rest
  mids("rest"); mids("best")
  return xdist("main", idx, TB["rest"]["mids"]) \
       - xdist("main", idx, TB["best"]["mids"]) }
function sortIdx(a, n, keys,   i, pack, srt, bits) {   # stable sort by keys[]
  for (i = 1; i <= n; i++) pack[i] = sprintf("%020.10f %06d", keys[a[i]], i)
  asort(pack, srt, "@val_str_asc")
  for (i = 1; i <= n; i++) { split(srt[i], bits, " "); pack[i] = a[bits[2]+0] }
  for (i = 1; i <= n; i++) a[i] = pack[i] }
function label(idx,   b, r, i, keys) {   # keep best pool near sqrt
  addRow("best", idx, 1)
  for (i = 1; i <= TB["best"]["n"]; i++)
    keys[TB["best"]["rows"][i]] = ydist("main", TB["best"]["rows"][i])
  sortIdx(TB["best"]["rows"], TB["best"]["n"], keys)
  b = TB["best"]["n"]; r = TB["rest"]["n"]
  if (b > sqrt(1 + b + r)) addRow("rest", addRow("best", 0, -1), 1) }
function acquire(cap,   i, nt, todo, keys) {   # pop the top scorer
  Tbl("best"); Tbl("rest")
  shuffle(TB["main"]["rows"], TB["main"]["n"], todo)
  nt = FEW
  for (i = 1; i <= START; i++) { label(todo[nt]); delete todo[nt]; nt-- }
  if (!cap) cap = STOP
  while (nt > 0 && TB["best"]["n"] + TB["rest"]["n"] < cap) {
    delete keys
    for (i = 1; i <= nt; i++) keys[todo[i]] = centroid(todo[i]) + 1000
    sortIdx(todo, nt, keys)
    label(todo[nt]); delete todo[nt]; nt-- } }
function adds(a, n, c,   i) {
  c["n"] = 0; c["mu"] = 0; c["m2"] = 0; c["sym"] = 0
  for (i = 1; i <= n; i++) add(c, a[i], 1) }
function cohen(xs, nx, ys, ny, eps,   a, b, pool, t, g) {   # gap vs pooled sd
  adds(xs, nx, a); adds(ys, ny, b)
  pool = ((a["n"]-1)*sd(a)^2 + (b["n"]-1)*sd(b)^2)/(a["n"]+b["n"]-2)
  t = 0.35 * sqrt(pool)
  if (eps > t) t = eps
  g = a["mu"] - b["mu"]
  return (g < 0 ? -g : g) <= t }
function cliffs(xs, nx, ys, ny,   i, gt, lt, j, k, z) {    # rank imbalance ok?
  gt = 0; lt = 0; j = 0; k = 0
  for (i = 1; i <= nx; i++) {
    while (j < ny && ys[j+1] <  xs[i]) { j++; k = j }
    while (k < ny && ys[k+1] <= xs[i]) k++
    gt += j; lt += ny - k }
  z = gt - lt
  return (z < 0 ? -z : z) / (nx * ny) <= 0.197 }
function ks(xs, nx, ys, ny,   i, j, d, v, g) {             # 95% K-S
  i = 0; j = 0; d = 0
  while (i < nx && j < ny) {
    v = (xs[i+1] < ys[j+1]) ? xs[i+1] : ys[j+1]
    while (i < nx && xs[i+1] <= v) i++
    while (j < ny && ys[j+1] <= v) j++
    g = i/nx - j/ny
    if (g < 0) g = -g
    if (g > d) d = g }
  return d <= 1.36 * sqrt((nx + ny) / (nx * ny)) }
function same(xs, nx, ys, ny, eps,   a, b, na, nb) {       # by all three
  na = asort(xs, a, "@val_num_asc"); nb = asort(ys, b, "@val_num_asc")
  return cliffs(a, na, b, nb) && ks(a, na, b, nb) && cohen(a, na, b, nb, eps) }
