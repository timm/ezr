#!/usr/bin/env python3 -B
"""
ezr.py: minimal XAI for multi-objective reasoning     
(c) 2026 Tim Menzies <timm@ieee.org> MIT license     
     
Options:     
     
      -P=2             minkowski coefficient     
      -Start=4         acquire: initial random labels     
      -Stop=50         acquire: total labelling budget     
      -Few=128         max train rows     
      -Leaf=4          tree: min rows in any leaf     
      -Check=5         holdout: top picks to label
      -k=1             bayes: rare klass hack
      -m=2             bayes: rare evidence hack
      -K=10            kmeans: clusters
      -N=10            kmeans: iterations
      -budget=1000     optimize: max oracle calls
      -restart=100     ls: retry after this many no-improves
      -Repeats=30      klass: number of train/test splits
      -Seed=1234567891 random number seed
      -Klass=$MOOT/classify/diabetes.csv  classify demo data
      -File=$MOOT/optimize/misc/auto93.csv

"""

# pylint: disable=bad-indentation,invalid-name  
# pylint: disable=missing-function-docstring  
# pylint: disable=multiple-statements,multiple-imports  
# pylint: disable=unnecessary-lambda-assignment  
# pylint: disable=inconsistent-return-statements  
# pylint: disable=dangerous-default-value  
# pylint: disable=broad-exception-caught  
# pylint: disable=unidiomatic-typecheck  
 
import os, random, re, sys, traceback
from math import exp, log, log2, pi, sqrt

# Used everywhere, defined late (see misc and start sections):
# `o` (dicts with attribute access), `say` (pretty printer),
# `the` (settings, parsed from this docstring).

def atom(s,bools={'True': True, 'False': False}):
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError:
      s = s.strip()
      return bools.get(s, s)

def csv(file):
  file = file.replace("$MOOT", os.environ.get("MOOT")
                      or os.path.expanduser("~/gits/moot"), 1)
  with open(file, encoding="utf-8") as f:
    return [tuple(atom(x) for x in line.split(","))
            for line in f if line.strip()]


#-- structs -----------------------------------------------

Num = lambda: (0, 0, 0) # n, mu, m2: all Welford keeps
Sym = dict

type Atom = str | bool | int | float
type Col  = tuple[int, float, float] | dict # Num | Sym
type Row  = tuple[Atom, ...]
type Rows = list[Row]
type Tbl  = o # rows:Rows, cols:{at:Col}, x:[at],
              # y:{at:bool}, names:Row, klass:at|None
type Node = list # [edge, n, mid, ymids, go, left, right]

def sd(col): return 0 if col[0] < 2 else sqrt(col[2]/(col[0]-1))

def add(col, v, inc=1): # new Num, or updated Sym; inc=-1 undoes
  if v == "?": return col
  if type(col) is Sym: col[v] = col.get(v, 0) + inc; return col
  n, mu, m2 = col
  n += inc
  d = v - mu
  mu += inc * d / max(1, n)
  return (n, mu, max(0, m2 + inc * d * (v - mu)))

def adds(lst, it=None): # accumulate a list into it
  if it is None: it = Num()   # NB: "it or Num()" would
  for y in lst: it = add(it, y)  # clobber an empty Sym()
  return it

def size(col):
  return sum(col.values()) if type(col) is Sym else col[0]

def div(col): # Num: sd. Sym: entropy
  if type(col) is not Sym: return sd(col)
  n = sum(col.values())
  return -sum(v/n * log2(v/n) for v in col.values() if v>0)

def addRow(tbl, row=None, inc=1): # inc=-1 pops the last row
  tbl._mids = None
  if inc > 0: tbl.rows.append(row)
  else: row = tbl.rows.pop()
  for at in tbl.cols:
    tbl.cols[at] = add(tbl.cols[at], row[at], inc)
  return row

def Tbl(src):
  tbl = o(rows=[], cols={}, x=[], y={}, names=src[0],
          klass=None, _mids=None)
  for at, s in enumerate(tbl.names):
    if not s.endswith("X"):
      tbl.cols[at] = Num() if s[0].isupper() else Sym()
      if   s[-1] == "!":  tbl.klass = at
      elif s[-1] in "+-": tbl.y[at] = s[-1] == "+"
      else: tbl.x.append(at)
  for row in src[1:]: addRow(tbl, row)
  return tbl

def clone(tbl, rows=[]): return Tbl([tbl.names] + rows)


#-- distance ----------------------------------------------
def norm(col, v):
  z = max(-3, min(3, (v - col[1]) / (1e-32 + sd(col))))
  return 1 / (1 + exp(-1.7 * z))

def mid(col):
  return max(col, key=col.get) if type(col) is Sym else col[1]

def mids(tbl): # x centroid; cached until rows change
  tbl._mids = tbl._mids or {at:mid(tbl.cols[at]) for at in tbl.x}
  return tbl._mids

def ydist(tbl, row):
  return (sum(abs(norm(tbl.cols[at], row[at]) - w) ** the.P
             for at, w in tbl.y.items()) / len(tbl.y))**(1/the.P)

def _dist(col, a, b):
  if a == "?" or b == "?": return 1
  return (a != b if type(col) is Sym
          else abs(norm(col, a) - norm(col, b)))

def xdist(tbl, row, m):
  return (sum(_dist(tbl.cols[at], row[at], m[at]) ** the.P
              for at in tbl.x) / len(tbl.x)) ** (1 / the.P)

def ymu(tbl, rows):
  return sum(ydist(tbl, r) for r in rows) / len(rows)

def ymids(tbl, rows):
  return [sum(r[at] for r in rows)/len(rows) for at in tbl.y]

#-- acquire -----------------------------------------------
def centroid(tbl, best, rest): # near best, far from rest
  return lambda z: (xdist(tbl, z, mids(rest))
                  - xdist(tbl, z, mids(best)))

def label(tbl, best, rest, row): # keep best pool near sqrt
  addRow(best, row)
  best.rows.sort(key=lambda r: ydist(tbl, r))
  b, r = len(best.rows), len(rest.rows)
  if b > sqrt(1 + b + r): addRow(rest, addRow(best, inc=-1))

def acquire(tbl, cap=None, score=centroid): # pop the top scorer
  best, rest = clone(tbl), clone(tbl)
  todo = random.sample(tbl.rows, len(tbl.rows))[:the.Few]
  for _ in range(the.Start): label(tbl, best, rest, todo.pop())
  cap = cap or the.Stop
  while todo and len(best.rows) + len(rest.rows) < cap:
    todo.sort(key=score(tbl, best, rest))
    label(tbl, best, rest, todo.pop())
  return best.rows + rest.rows

#-- tree --------------------------------------------------
# Node = [edge, n, ymu, ymids, go, kid, kid]
def xpect(a, b): # sizes are >= the.Leaf, so no zero guard
  return ((div(a)*size(a) + div(b)*size(b))/(size(a) + size(b)))

def cutNum(xy, acc): # (left, right, x) per value boundary
  xy.sort()
  here, there = acc(), adds((y for _, y in xy), acc())
  for i, (x, y) in enumerate(xy[:-1]):
    here, there = add(here, y), add(there, y, -1)
    if x != xy[i+1][0]: yield here, there, x

def cutSym(xy, acc): # (in, out, sym), one per symbol
  for v in sorted({x for x, _ in xy}):
    yield (adds((y for x, y in xy if x == v), acc()),
           adds((y for x, y in xy if x != v), acc()), v)

def cut(tbl, rows, ys, acc): # best (col, val) split
  best = (1e30, None, None)
  for at in tbl.x:
    xy = [(x, y) for r,y in zip(rows, ys) if (x := r[at]) != "?"]
    what = cutSym if type(tbl.cols[at]) is Sym else cutNum
    for here, there, v in what(xy, acc):
      if the.Leaf <= size(here) <= len(xy) - the.Leaf:
        if (s := xpect(here, there)) < best[0]:
          best = (s, at, v)
  if best[1] is not None: return best[1:]

def routing(tbl, at, v):
  s, c = tbl.names[at], tbl.cols[at]
  if type(c) is not Sym:
    return (f"{s} <= {say(v)}", f"{s} > {say(v)}",
            lambda r: (c[1] if r[at] == "?" else r[at]) <= v)
  return (f"{s} = {v}", f"{s} != {v}",
          lambda r: (mid(c) if r[at] == "?" else r[at]) == v)

def tree(tbl, rows, edge="", y=None):
  y    = y or (lambda r: ydist(tbl, r))
  ys   = [y(r) for r in rows]
  acc  = Sym if isinstance(ys[0],str) else Num
  node = [edge, len(rows), mid(adds(ys,acc())), ymids(tbl,rows)]
  if (len(rows) > the.Leaf and (best := cut(tbl, rows, ys,acc))):
    e1, e2, go = routing(tbl, *best)
    yes, no = [], []
    for r in rows:
      (yes if go(r) else no).append(r)
    if yes and no:
      node += [go, tree(tbl, yes, e1, y), tree(tbl, no, e2, y)]
  return node

def kids(n): return n[5:]

def leaf(tr, row):
  while kids(tr): tr = tr[5] if tr[4](row) else tr[6]
  return tr


#-- report ------------------------------------------------
def leafs(tr):
  return [x for k in kids(tr) for x in leafs(k)] or [tr]

def show(tbl, tr):
  ls = sorted(leafs(tr), key=lambda z: z[2])
  print("  d2h   n" + "".join(f"{tbl.names[at]:>7}"
                              for at in tbl.y))
  def walk(z, pre=None):
    m = "+" if z is ls[0] else "-" if z is ls[-1] else " "
    v = z[2] if type(z[2]) is str else round(100 * z[2])
    print((f"{m} {v:>3} {z[1]:>3}"
           + "".join(f"{round(v):>7}" for v in z[3])
           + "   " + (pre or "") + z[0]).rstrip())
    for k in kids(z): walk(k, "" if pre is None else pre+"|  ")
  walk(tr)


#-- stats -------------------------------------------------
def cohen(xs, ys, d=0.35, eps=0): # gap vs pooled sd, floored
  a, b = adds(xs), adds(ys)
  pool = ((a[0]-1)*sd(a)**2 + (b[0]-1)*sd(b)**2)/(a[0]+b[0]-2)
  return abs(a[1] - b[1]) <= max(eps, d * sqrt(pool))

def cliffs(xs, ys, d=0.197): # sorted in. rank imbalance ok?
  gt = lt = j = k = 0
  for x in xs:
    while j < len(ys) and ys[j] <  x: j += 1; k = j
    while k < len(ys) and ys[k] <= x: k += 1
    gt += j; lt += len(ys) - k
  return abs(gt - lt) / (len(xs) * len(ys)) <= d

def ks(xs, ys, a=1.36): # sorted in. 95% kolmogorov-smirnov
  n, m, i, j, d = len(xs), len(ys), 0, 0, 0
  while i < n and j < m:
    v = min(xs[i], ys[j])
    while i < n and xs[i] <= v: i += 1
    while j < m and ys[j] <= v: j += 1
    d = max(d, abs(i/n - j/m))
  return d <= a * sqrt((n + m) / (n * m))

def same(xs, ys, eps=0): # indistinguishable, by all three
  xs, ys = sorted(xs), sorted(ys)
  return (cliffs(xs,ys) and ks(xs,ys) and cohen(xs,ys,eps=eps))

#-- misc -------------------------------------------------
def say(x, p=2):
  if type(x) is float: x= f"{x:.{p}f}".rstrip("0").rstrip(".")
  elif type(x) in (dict, o): x= "{" + ", ".join(
    f"{k}: {say(x[k], p)}" for k in x if str(k)[0] != "_") + "}"
  elif type(x) in (list,tuple):
    x = "[" + ", ".join(say(v, p) for v in x) + "]"
  return str(x)

class o(dict):
  __repr__ = say
  __getattr__,__setattr__ = dict.__getitem__,dict.__setitem__

#-- tests -------------------------------------------------
def wins(tbl):
  ys = sorted(ydist(tbl, r) for r in tbl.rows)
  lo, b4 = ys[0], sum(ys) / len(ys)
  return lambda r: max(-100, min(100,
    100 * (1 - (ydist(tbl, r) - lo) / (b4 - lo + 1e-32))))

def holdout(tbl):
  rows = random.sample(tbl.rows, len(tbl.rows))
  n = len(rows) // 2
  train, test = rows[:n][:the.Few], rows[n:]
  tr = clone(tbl, train)
  tt = tree(tr, acquire(tr, the.Stop - the.Check))
  top = sorted(test, key=lambda r: leaf(tt,r)[2])[:the.Check]
  return min(top, key=lambda r: ydist(tr, r))


#-- start-up ----------------------------------------------
def test_help():
  "Show usage, settings, demos"
  print(__doc__, "Demos:\n",
        *[f"  --{k[5:]:<10} {f.__doc__}"
          for k, f in globals().items() if k[:5] == "test_"],
        sep="\n")

def test_num():
  "Welford add matches textbook mean and sd"
  c = adds([2, 4, 4, 4, 5, 5, 7, 9])
  assert c[0] == 8 and c[1] == 5 and abs(sd(c)-2.138) < .01
  print(f"mu {say(c[1])} sd {say(sd(c))}")

def test_sym():
  "Syms count; mid is mode; div is entropy"
  c = adds("aabbbc", Sym())
  assert c["b"]==3 and mid(c)=="b" and abs(div(c)-1.459)<.01
  print(f"mode {mid(c)} ent {say(div(c))}")

def test_tbl():
  "Headers route columns to x, y, klass, or nowhere"
  t = Tbl([("Age","job!","SkipX","Weight-"), (2,"a",3,80)])
  assert t.x == [0] and t.y == {3: False} and t.klass == 1
  assert 2 not in t.cols
  print(f"x {t.x} y {t.y} klass {t.klass}")

def test_cuts():
  "cut returns a legal, routable split"
  t = Tbl(csv(the.File))
  rows = t.rows[:64]; ys = [ydist(t, r) for r in rows]
  at, v = cut(t, rows, ys, Num)
  e1, e2, go = routing(t, at, v)
  yes = sum(go(r) for r in rows)
  assert 0 < yes < len(rows)
  print(f"cut: {e1} yes={yes}; {e2} no={len(rows)-yes}")

def test_wins():
  "wins grades the best row 100"
  t = Tbl(csv(the.File))
  w = wins(t)(min(t.rows, key=lambda r: ydist(t, r)))
  assert w == 100; print(f"best row wins {w}")


def test_tree():
  "Acquire, grow and show the.File's tree"
  tbl = Tbl(csv(the.File)); lab = acquire(tbl)
  print(f"{the.File} n={len(tbl.rows)}"
        f" mid={say(ymu(tbl, tbl.rows))}"
        f" ezr={say(ydist(tbl, lab[0]))}")
  show(tbl, tree(tbl, lab))

def test_holdout():
  "Mean win over 20 train/test holdouts"
  tbl = Tbl(csv(the.File))
  win = wins(tbl)
  mu = sum(win(holdout(tbl)) for _ in range(20)) / 20
  print(f"win {round(mu)}")

def test_same():
  "Stats tests tell noise from signal"
  x = [random.gauss(10, 1) for _ in range(40)]
  y = [random.gauss(10, 1) for _ in range(40)]
  z = [random.gauss(11, 1) for _ in range(40)]
  assert same(x, y) and not same(x, z)
  print(f"same {same(x, y)} diff {not same(x, z)}")


# -- start ------------------------------------------------
the = o(_defaults=o())
for k, v in re.findall(r"(\w+)=(\S+)", __doc__ or ""):
  the[k] = the._defaults[k] = atom(v)

def run(f=None): # demos may mutate the; always clean up
  random.seed(the.Seed)
  try:              (f or test_help)()
  except Exception: traceback.print_exc(); return 1
  finally:          the.update(the._defaults)
  return 0

def test_all():
  "Run every demo; exit code counts the crashes"
  sys.exit(sum(print(f"\n# {k[5:]}") or run(f)
               for k, f in list(globals().items())
               if k[:5] == "test_" and f is not test_all))

def cli(d, funs, args, n=0):
  while args:
    s = args.pop(0)
    if   s[:2] == "--" : n += run(funs.get("test_"+s[2:]))
    elif s[1:] in d    : d[s[1:]] = atom(args.pop(0))
    else: print(f"unknown arg: {s}")
  sys.exit(n)

def main(): # pip entry point
  cli(the, globals(), sys.argv[1:] or ["--help"])

if __name__ == "__main__": main()
