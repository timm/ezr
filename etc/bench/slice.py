Num = lambda: (0, 0, 0)                    # n, mu, m2: all Welford keeps
Sym = dict
def rnd():                                 # MINSTD, shared by all ports
  global SEED
  SEED = SEED * 16807 % 2147483647
  return SEED / 2147483647
def shuffle(a):                            # Fisher-Yates, in shared rnd order
  a = list(a)
  for i in range(len(a) - 1, 0, -1):
    j = int(rnd() * (i + 1))
    a[i], a[j] = a[j], a[i]
  return a
def sd(col): return 0 if col[0] < 2 else sqrt(col[2] / (col[0] - 1))
def add(col, v, inc=1):                    # new Num, or updated Sym
  if v == "?": return col
  if type(col) is Sym: col[v] = col.get(v, 0) + inc; return col
  n, mu, m2 = col
  n += inc
  d = v - mu
  mu += inc * d / max(1, n)
  return (n, mu, max(0, m2 + inc * d * (v - mu)))
def adds(lst, it=None):                    # accumulate a list into it
  if it is None: it = Num()
  for y in lst: it = add(it, y)
  return it
def size(col):
  return sum(col.values()) if type(col) is Sym else col[0]
def div(col):                              # Num: sd. Sym: entropy
  if type(col) is not Sym: return sd(col)
  n = sum(col.values())
  return -sum(v/n * log2(v/n) for v in col.values() if v > 0)
def addRow(tbl, row=None, inc=1):          # inc=-1 pops the last row
  tbl["_mids"] = None
  if inc > 0: tbl["rows"].append(row)
  else: row = tbl["rows"].pop()
  for at in tbl["cols"]:
    tbl["cols"][at] = add(tbl["cols"][at], row[at], inc)
  return row
def Tbl(src):
  tbl = dict(rows=[], cols={}, x=[], y={}, names=src[0], klass=None, _mids=None)
  for at, s in enumerate(src[0]):
    if not s.endswith("X"):
      tbl["cols"][at] = Num() if s[0].isupper() else Sym()
      if   s[-1] == "!":  tbl["klass"] = at
      elif s[-1] in "+-": tbl["y"][at] = 1 if s[-1] == "+" else 0
      else: tbl["x"].append(at)
  for row in src[1:]: addRow(tbl, row)
  return tbl
def clone(tbl, rows=[]): return Tbl([tbl["names"]] + rows)
def norm(col, v):
  z = max(-3, min(3, (v - col[1]) / (1e-32 + sd(col))))
  return 1 / (1 + exp(-1.7 * z))
def mid(col):
  return max(col, key=col.get) if type(col) is Sym else col[1]
def mids(tbl):                             # x centroid; cached until rows change
  if not tbl["_mids"]:
    tbl["_mids"] = {at: mid(tbl["cols"][at]) for at in tbl["x"]}
  return tbl["_mids"]
def mink(gaps):
  return (sum(g ** P for g in gaps) / len(gaps)) ** (1 / P)
def ydist(tbl, row):
  return mink([abs(norm(tbl["cols"][at], row[at]) - w)
               for at, w in tbl["y"].items()])
def _dist(col, a, b):
  if a == "?" or b == "?": return 1
  return (1 if a != b else 0) if type(col) is Sym \
         else abs(norm(col, a) - norm(col, b))
def xdist(tbl, row, m):
  return mink([_dist(tbl["cols"][at], row[at], m[at]) for at in tbl["x"]])
def ymu(tbl, rows):
  return sum(ydist(tbl, r) for r in rows) / len(rows)
def ymids(tbl, rows):
  return [sum(r[at] for r in rows) / len(rows) for at in tbl["y"]]
def centroid(tbl, best, rest):             # near best, far from rest
  return lambda z: xdist(tbl, z, mids(rest)) - xdist(tbl, z, mids(best))
def label(tbl, best, rest, row):           # keep best pool near sqrt
  addRow(best, row)
  best["rows"].sort(key=lambda r: ydist(tbl, r))
  b, r = len(best["rows"]), len(rest["rows"])
  if b > sqrt(1 + b + r): addRow(rest, addRow(best, inc=-1))
def acquire(tbl, cap=None, score=None):    # pop the top scorer
  best, rest = clone(tbl), clone(tbl)
  todo = shuffle(tbl["rows"])[:Few]
  for _ in range(Start): label(tbl, best, rest, todo.pop())
  cap = cap or Stop
  score = score or centroid
  while todo and len(best["rows"]) + len(rest["rows"]) < cap:
    todo.sort(key=score(tbl, best, rest))
    label(tbl, best, rest, todo.pop())
  return best["rows"] + rest["rows"]
def cohen(xs, ys, d=0.35, eps=0):          # gap vs pooled sd, floored
  a, b = adds(xs), adds(ys)
  pool = ((a[0]-1) * sd(a)**2 + (b[0]-1) * sd(b)**2) / (a[0]+b[0]-2)
  return abs(a[1] - b[1]) <= max(eps, d * sqrt(pool))
def cliffs(xs, ys, d=0.197):               # sorted in. rank imbalance ok?
  gt = lt = j = k = 0
  for x in xs:
    while j < len(ys) and ys[j] <  x: j += 1; k = j
    while k < len(ys) and ys[k] <= x: k += 1
    gt += j; lt += len(ys) - k
  return abs(gt - lt) / (len(xs) * len(ys)) <= d
def ks(xs, ys, a=1.36):                    # sorted in. 95% kolmogorov-smirnov
  n, m, i, j, d = len(xs), len(ys), 0, 0, 0
  while i < n and j < m:
    v = min(xs[i], ys[j])
    while i < n and xs[i] <= v: i += 1
    while j < m and ys[j] <= v: j += 1
    d = max(d, abs(i/n - j/m))
  return d <= a * sqrt((n + m) / (n * m))
def same(xs, ys, eps=0):                   # indistinguishable, by all three
  xs, ys = sorted(xs), sorted(ys)
  return cliffs(xs, ys) and ks(xs, ys) and cohen(xs, ys, 0.35, eps)
