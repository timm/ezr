#!/usr/bin/env python3 -B
"""
ezr0.py: multi-objective reasoning, cut to the bone.
(c) 2026 Tim Menzies <timm@ieee.org> MIT license

Options:

      -Start=4         acquire: initial random labels
      -Stop=50         acquire: total labelling budget
      -Few=128         holdout: max training rows
      -Cuts=8          tree: splits to try, per num
      -Leaf=4          tree: min rows in any leaf
      -Check=5         holdout: top picks to label
      -Repeats=20      holdout: how many train/test splits
      -Seed=1234567891 random number seed
      -File=~/gits/moot/optimize/misc/auto93.csv

"""
import os, re, sys, random, traceback
from math import exp, log2, sqrt

#-- misc ---------------------------------------------------

def say(x, p=2):
  "Floats get P decimals; dicts list their keys."
  if type(x) is float: 
    return f"{x:.{p}f}".rstrip("0").rstrip(".")
  if isinstance(x, dict):            # not str(): that would
    return "{" + ", ".join(          # call __repr__ -> say
      f"{k}: {say(v,p)}" for k,v in x.items()) + "}"
  return str(x)

class o(dict):
  "A dict you can poke with a dot."
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__
  __repr__ = say

def atom(s):
  "'22' -> 22.  'x' -> 'x'."
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return s.strip()

def csv(file):
  "Rows of FILE, each cell coerced."
  with open(os.path.expanduser(file), encoding="utf-8") as f:
    for line in f:
      if line.strip(): yield [atom(s) for s in line.split(",")]

#-- columns ------------------------------------------------
# A column is a Num or a Sym.  Sym has `has`; Num does not.

def Num(at=0, txt=" "):
  return o(at=at, txt=txt, n=0, mu=0, m2=0, sd=0,
           goal=0 if txt[-1] == "-" else 1)

def Sym(at=0, txt=" "):
  return o(at=at, txt=txt, n=0, has={})

def add(col, v, inc=1):
  "Show V to COL.  INC=-1 takes it away.  `?` changes nothing."
  if v != "?":
    col.n += inc
    if "has" in col:
      col.has[v] = col.has.get(v, 0) + inc
    else:
      d = v - col.mu                      # Welford, for `div`
      col.mu += inc * d / max(1, col.n)
      col.m2  = max(0, col.m2 + inc * d * (v - col.mu))
      col.sd  = 0 if col.n < 2 else (col.m2/(col.n-1))**.5
  return v

def adds(vs, col=None):
  "Every item of VS into COL."
  col = col if col is not None else Num()
  for v in vs: add(col, v)
  return col

def mid(col):
  "Middle: the mean, or the most common symbol."
  return max(col.has,key=col.has.get) if "has" in col else col.mu

def mids(tbl):
  "Every column's middle, keyed by column index."
  return {at: mid(col) for at, col in tbl.cols.items()}

def div(col):
  "Spread: entropy, or standard deviation."
  return (-sum(v/col.n * log2(v/col.n) for v in col.has.values())
          if "has" in col else col.sd)  # sd kept fresh by `add`

def norm(col, v):
  "To 0..1, by the logistic curve.  Symbols do not scale."
  if "has" in col: return v
  z = max(-3, min(3, (v - col.mu) / (1e-32 + div(col))))
  return 1 / (1 + exp(-1.7 * z))

#-- tables -------------------------------------------------

def Tbl(src):
  "Header names the columns: X skip, +- goal, ! klass."
  src = iter(src)
  tbl = o(rows=[], cols={}, x=[], y=[], names=next(src))
  for at, s in enumerate(tbl.names):
    if s[-1] == "X": continue            # skip me entirely
    tbl.cols[at] = Num(at,s) if s[0].isupper() else Sym(at,s)
    (tbl.y if s[-1] in "+-!" else tbl.x).append(at)
  for row in src: addRow(tbl, row)
  return tbl

def addRow(tbl, row):
  "Keep ROW, and show it to my columns."
  tbl.rows += [row]
  return addCols(tbl, row)

def addCols(tbl, row, inc=1):
  "Show ROW to my columns, without keeping it."
  for at, col in tbl.cols.items(): add(col, row[at], inc)
  return row

def clone(tbl, rows=[]):
  "An empty copy of TBL, plus ROWS."
  return Tbl([tbl.names] + rows)

#-- distance -----------------------------------------------

def minkowski(vs, n):
  "Root mean square of N gaps."
  return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl, row):
  "How far ROW's goals are from the best they could be."
  return minkowski((abs(norm(tbl.cols[at], row[at])
                        - tbl.cols[at].goal) for at in tbl.y),
                   len(tbl.y))

def gap(col, a, b):
  "Distance between two values of one column."
  if a == "?" or b == "?": return 1    # unknown = far
  return a != b if "has" in col else abs(norm(col,a) - norm(col,b))

def xdist(tbl, r1, r2):
  "How far apart two rows are, over the x columns."
  return minkowski((gap(tbl.cols[at], r1[at], r2[at])
                    for at in tbl.x), len(tbl.x))

#-- acquire ------------------------------------------------

def acquire(tbl, cap=None):
  "Label near the best rows, far from the rest.  Best first."
  cap  = cap or the.Stop
  todo = random.sample(tbl.rows, len(tbl.rows))[:the.Few]
  both = clone(tbl, [todo.pop() for _ in range(the.Start)])
  done = sorted(both.rows, key=lambda r: ydist(both, r))
  n    = int(sqrt(len(done)))
  best, rest = clone(tbl, done[:n]), clone(tbl, done[n:])
  while todo and len(both.rows) < cap:
    b, r = mids(best), mids(rest)
    todo.sort(key=lambda z: xdist(tbl,z,r) - xdist(tbl,z,b))
    addRow(best, addRow(both, todo.pop()))
    best.rows.sort(key=lambda z: ydist(both, z))  # no y leak
    if len(best.rows) > sqrt(len(both.rows)): # best stays small
      addRow(rest, addCols(best, best.rows.pop(), -1))
  return sorted(both.rows, key=lambda r: ydist(both, r))

def grabs(tbl, cap=None):
  "The straw man: same budget, taken at random."
  cap = cap or the.Stop
  return random.sample(tbl.rows, min(cap, len(tbl.rows)))

#-- tree ---------------------------------------------------
# A node is o(rows, at, v, go, kids, mu).

def cut(tbl, rows):
  "The (at, v, go) whose two sides have the tightest ys."
  ys = [ydist(tbl, r) for r in rows]
  out, least = None, 1e30
  for at in tbl.x:
    for v, go in candidates(tbl.cols[at], rows, at):
      a, b = Num(), Num()   # one pass, so one `go` per row
      for r,y in zip(rows,ys): add(a if go(r) else b, y)
      if a.n >= the.Leaf and b.n >= the.Leaf:
        s = (div(a)*a.n + div(b)*b.n) / (a.n + b.n)
        if s < least: out, least = (at, v, go), s
  return out

def candidates(col, rows, at):
  "What splits to try: one per symbol, or CUTS per num."
  if "has" in col:
    for v in sorted({r[at] for r in rows if r[at] != "?"}):
      yield v, lambda r,v=v,at=at: r[at] == v
  else:                # by rank, not value: THESE rows are dense
    xs = sorted(r[at] for r in rows if r[at] != "?")
    k  = max(1, len(xs)//the.Cuts)     # cuts, spaced by rank
    for v in xs[k-1:-1:k]:
      yield v, (lambda r,v=v,at=at: r[at] != "?" and r[at] <= v)

def tree(tbl, rows):
  "Split while a split keeps both sides big enough."
  node = o(rows=rows, at=None, v=None, go=None, kids=[],
           mu=sum(ydist(tbl,r) for r in rows)/len(rows))
  if len(rows) > the.Leaf and (found := cut(tbl, rows)):
    at, v, go = found
    yes, no = [], []
    for r in rows: (yes if go(r) else no).append(r)
    node.at, node.v, node.go = at, v, go   # cut kept both sides big
    node.kids = [tree(tbl, yes), tree(tbl, no)]
  return node

def leaf(node, row):
  "Walk ROW down to its leaf."
  while node.kids: node = node.kids[0 if node.go(row) else 1]
  return node

def leafs(node):
  return [x for k in node.kids for x in leafs(k)] or [node]

def show(tbl, node, pre=None, edge=""):
  "Tree on the left; d2h and n on the right."
  ls = sorted(leafs(node), key=lambda z: z.mu)
  def walk(z, pre, edge):
    m = "+" if z is ls[0] else "-" if z is ls[-1] else " "
    print(f"{m} {round(100*z.mu):>4} {len(z.rows):>5}   "
          f"{(pre or '')+edge}".rstrip())
    op = "=" if "has" in tbl.cols[z.at or 0] else "<="
    no = "!=" if op == "=" else ">"
    for k, o2 in zip(z.kids, [op, no]):
      walk(k, "" if pre is None else pre + "|  ",
           f"{tbl.names[z.at]} {o2} {say(z.v)}")
  print(f"  d2h     n")
  walk(node, pre, edge)

#-- holdout ------------------------------------------------

def wins(tbl):
  "100 at the best row, 0 at an average one."
  ys = sorted(ydist(tbl, r) for r in tbl.rows)
  lo, b4 = ys[0], sum(ys)/len(ys)
  return lambda r: max(-100, min(100, 100*(1 - (ydist(tbl,r)-lo)
                                            / (b4-lo+1e-32))))

def holdout(tbl, pick=acquire):
  "Train on half; of CHECK guesses on the rest, pick best."
  rows  = random.sample(tbl.rows, len(tbl.rows))
  n     = len(rows)//2
  tr    = clone(tbl, rows[:n][:the.Few])
  lab   = clone(tbl, pick(tr, the.Stop - the.Check))
  tt    = tree(lab, lab.rows)
  top   = sorted(rows[n:], key=lambda r: leaf(tt,r).mu)
  return min(top[:the.Check], key=lambda r: ydist(lab, r))

#-- stats --------------------------------------------------
def cohen(xs, ys, d=0.35, eps=0):
  "Are the means within D pooled standard deviations?"
  a, b = adds(xs), adds(ys)
  pool = ((a.n-1)*div(a)**2 + (b.n-1)*div(b)**2)/(a.n+b.n-2)
  return abs(a.mu - b.mu) <= max(eps, d * sqrt(pool))

def cliffs(xs, ys, d=0.197):
  "Sorted in.  Is the rank imbalance small enough?"
  gt = lt = j = k = 0
  for x in xs:
    while j < len(ys) and ys[j] <  x: j += 1; k = j
    while k < len(ys) and ys[k] <= x: k += 1
    gt += j; lt += len(ys) - k
  return abs(gt - lt) / (len(xs) * len(ys)) <= d

def ks(xs, ys, a=1.36):
  "Sorted in.  95% Kolmogorov-Smirnov."
  n, m, i, j, d = len(xs), len(ys), 0, 0, 0
  while i < n and j < m:
    v = min(xs[i], ys[j])
    while i < n and xs[i] <= v: i += 1
    while j < m and ys[j] <= v: j += 1
    d = max(d, abs(i/n - j/m))
  return d <= a * sqrt((n + m) / (n * m))

def same(xs, ys, eps=0):
  "Indistinguishable by all three.  One sort, then linear."
  xs, ys = sorted(xs), sorted(ys)
  return cliffs(xs,ys) and ks(xs,ys) and cohen(xs,ys,eps=eps)

#-- demos --------------------------------------------------

def eg_h():
  "Show the options and the demos."
  print(__doc__, "Demos:", *[f"  --{k[3:]:<9} {f.__doc__}"
        for k,f in globals().items() if k[:3]=="eg_"], sep="\n")

def eg_num():
  "Welford matches the textbook mean and sd."
  c = adds([2,4,4,4,5,5,7,9])
  assert c.n==8 and mid(c)==5 and abs(div(c)-2.138) < .01
  print(say(c))                      # also checks __repr__

def eg_sym():
  "Syms count; mid is the mode, div is entropy."
  c = adds("aabbbc", Sym())
  assert c.has["b"]==3 and mid(c)=="b" and abs(div(c)-1.459)<.01
  print(f"mode {mid(c)} ent {say(div(c))}")

def eg_tbl():
  "The header routes each column."
  t = Tbl([["Age","job!","SkipX","Weight-"],[2,"a",3,80]])
  assert t.x == [0] and t.y == [1,3]
  print(f"x {t.x} y {t.y}")

def eg_dist():
  "A row is nearest itself, and ydist orders the data."
  t  = Tbl(csv(the.File))
  r  = t.rows[0]
  assert xdist(t,r,r) == 0
  ys = sorted(ydist(t,r) for r in t.rows)
  print(f"ydist best {say(ys[0])} mid {say(ys[len(ys)//2])}"
        f" worst {say(ys[-1])}")

def eg_tree():
  "Acquire, then grow and show a tree."
  t   = Tbl(csv(the.File))
  lab = clone(t, acquire(t))
  show(lab, tree(lab, lab.rows))

def eg_same():
  "The stats tell noise from signal."
  x = [random.gauss(10,1) for _ in range(40)]
  y = [random.gauss(10,1) for _ in range(40)]
  z = [random.gauss(11,1) for _ in range(40)]
  assert same(x,y) and not same(x,z) and same(x,x)
  print(f"same {same(x,y)} differ {not same(x,z)}")

def eg_holdout():
  "Mean win over REPEATS holdouts."
  t = Tbl(csv(the.File)); w = wins(t)
  ws = sorted(round(w(holdout(t))) for _ in range(the.Repeats))
  print(f"{round(sum(ws)/len(ws)):>4} {os.path.basename(the.File)}")

def eg_vs():
  "Acquire versus random, same budget.  0 if the same."
  t = Tbl(csv(the.File)); w = wins(t)
  a = [w(holdout(t, acquire)) for _ in range(the.Repeats)]
  b = [w(holdout(t, grabs))   for _ in range(the.Repeats)]
  d = 0 if same(a,b) else round(sum(a)/len(a) - sum(b)/len(b))
  print(f"{round(sum(a)/len(a)):>4} {round(sum(b)/len(b)):>4}"
        f" {d:>4} {os.path.basename(the.File)}")

def eg_all():
  "Run every demo; exit code counts the crashes."
  sys.exit(sum(print(f"\n# {k[3:]}") or run(f)
                for k,f in list(globals().items())
                if k[:3]=="eg_" and f is not eg_all))

#-- start --------------------------------------------------

the = o(_defaults=o())
for k, v in re.findall(r"(\w+)=(\S+)", __doc__ or ""):
  the[k] = the._defaults[k] = atom(v)

def run(f=None):
  "Demos may poke `the`, so always put it back."
  random.seed(the.Seed)
  try:              (f or eg_h)()
  except Exception: traceback.print_exc(); return 1
  finally:          the.update(the._defaults)
  return 0

def main(args):
  while args:
    s = args.pop(0)
    if   s[:2] == "--": run(globals().get("eg_" + s[2:]))
    elif s[1:] in the : the[s[1:]] = atom(args.pop(0))
    else: print(f"unknown arg: {s}")

if __name__ == "__main__": main(sys.argv[1:] or ["--h"])
