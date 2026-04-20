#!/usr/bin/env python3 -B
# ezr.py: explainable multi-objective optimization   
# (c) 2026 Tim Menzies, timm@ieee.org, MIT license   
"""
Options:

    --seed=1              set random number seed         
    --p=2                 distance (1=Manhattan, 2=Euclidean)   
    --learn.leaf=3        examples per leaf in a tree         
    --learn.budget=50     number of rows to evaluate         
    --learn.check=5       number of guesses to check         
    --learn.start=4       initial number of labels   
    --bayes.m=2           m-estimate for Naive Bayes   
    --bayes.k=1           k-estimate (Laplace smoothing) for Naive Bayes   
    --few=128             max number of unlabelled rows to evaluate in active learning   
    --stats.cliffs=0.195  threshold for Cliff's Delta         
    --stats.conf=1.36     confidence coefficient for KS test   
    --stats.eps=0.35      margin of error multiplier         
    --show.show=30        display width/padding for trees         
    --show.decimals=2     number of decimals for floats         
    --textmine.norm=0     CNB weight normalization (0/1)
    --textmine.yes=20     positive samples for text mining
    --textmine.no=20      negative samples for text mining
    --textmine.top=100    top TF-IDF features to keep
    --textmine.valid=20   repeats for statistical testing
"""
from __future__ import annotations
from time import perf_counter_ns as now
import os, re, random, sys, bisect, math
from pathlib import Path
from random import random as rand, choices, choice, sample, shuffle
from math import log, log2, exp, sqrt, pi
from typing import Any, Iterable, Callable
from types import SimpleNamespace as S

# Naming conventions:
#   
#     i   : self   
#     j   : iterator variable   
#     c   : any column (Num or Sym)   
#     d   : Data (rows + summarized columns)   
#     ds  : Datas (list of Data objects)   
#     r   : row (a single list of values)   
#     rs  : rows (a list of lists)   
#     x   : an x-column specifically (independent)   
#     y   : a y-column specifically (dependent)   
#     t   : Tree node   
#     txt : string   

# ----  Types ----
type Qty   = int | float
type Atom  = str | bool | Qty
type Row   = list[Atom]
type Rows  = list[Row]
type Col   = Num | Sym
type Cols  = list[Col]
type Tree  = Any  # Type hinting wrapper
type Datas = list[Data]

# ---- 0. Utilities ----
def o(x: Any) -> str:
  """Recursively format objects. Sorts dicts for stable table columns."""
  if isinstance(x, float): return f"{x:.{the.show.decimals}f}"
  if isinstance(x, dict):  
    return "{"+", ".join(f"{k}={o(v)}" for k,v in sorted(x.items()))+"}"
  if isinstance(x, list):  return "{"+", ".join(map(o, x))+"}"
  if isinstance(x, S):     return "S" + o(x.__dict__)
  if hasattr(x, "__dict__"): return x.__class__.__name__ + o(x.__dict__)
  return str(x)
  
def table(lst: list, w: int = 10) -> None:
  """Print a list of dicts or objects as an aligned table."""
  if not lst: return
  ds = [x if type(x) is dict else x.__dict__ for x in lst]
  ks = list(ds[0].keys())
  print("".join(f"{str(k):>{w}}" for k in ks))
  print("-" * (len(ks) * w))
  for d in ds: print("".join(f"{str(d.get(k, '')):>{w}}" for k in ks))

def thing(txt: str) -> Atom:
  """Coerce strings into numbers or booleans."""
  txt = txt.strip()
  b = lambda s: {"true": 1, "false": 0}.get(s.lower(), s)
  for f in [int, float, b]:
    try: return f(txt)
    except ValueError: pass

def nest(t: Any, k: str, v: Any) -> None:
  """Set value in nested namespace (e.g., 'a.b.c')."""
  for x in (ks := k.split("."))[:-1]: t = t.__dict__.setdefault(x, S())
  setattr(t, ks[-1], v)

def csv(f: str, clean: Callable = lambda s: s.partition("#")[0].split(",")) -> Iterable:
  """Yield formatted and typed rows from a CSV file."""
  with open(f, encoding="utf-8") as file:
    for s in file:
      r = clean(s)
      if any(x.strip() for x in r): yield [thing(x) for x in r]

def same(xs: list, ys: list, eps: float) -> bool:
  """Check if two lists of numbers are statistically indistinguishable."""
  xs, ys = sorted(xs), sorted(ys)
  n, m = len(xs), len(ys)
  if abs(xs[n//2] - ys[m//2]) <= eps: return True
  gt = sum(bisect.bisect_left(ys, a) for a in xs)
  lt = sum(m - bisect.bisect_right(ys, a) for a in xs)
  if abs(gt - lt) / (n * m) > the.stats.cliffs: return False
  ks = lambda v: abs(bisect.bisect_right(xs, v)/n - bisect.bisect_right(ys, v)/m)
  return max(max(map(ks, xs)), max(map(ks, ys))) <= the.stats.conf * ((n+m)/(n*m))**.5

def bestRanks(d: dict) -> dict:
  """Group treatments that are statistically tied for best."""
  items = sorted(d.items(), key=lambda kv: sorted(kv[1])[len(kv[1])//2])
  k0, lst0 = items[0]
  best = {k0: adds(lst0, Num(k0))}
  for k, lst in items[1:]:
    if same(lst0, lst, spread(best[k0]) * the.stats.eps): 
        best[k] = adds(lst, Num(k))
    else: break
  return best

# ---- 1. Columns ----
def Col(txt: str = "", a: int = 0) -> Col: 
  """Return a Num or Sym column based on capitalization."""
  return (Num if txt[0].isupper() else Sym)(txt, a) 

class Num:
  """Summarizes a stream of numbers."""
  def __init__(i, txt: str = "", a: int = 0):
    i.txt, i.at, i.n = txt, a, 0
    i.mu, i.m2, i.sd, i.heaven = 0, 0, 0, txt[-1:] != "-"

class Sym:
  """Summarizes a stream of symbols."""
  def __init__(i, txt: str = "", a: int = 0): 
    i.txt, i.at, i.n, i.has = txt, a, 0, {}

def summarize(c: Col, v: Any, w: int = 1) -> Any:
  """Update column statistics incrementally with value `v`, weight `w`."""
  if v == "?": return v
  if Sym == type(c): c.has[v] = w + c.has.get(v, 0)
  elif w < 0 and c.n <= 2: c.n = c.mu = c.m2 = c.sd = 0
  else:
    c.n += w
    delta = v - c.mu
    c.mu += w * delta / c.n
    c.m2 += w * delta * (v - c.mu)
    c.sd = (max(0, c.m2) / (c.n - 1))**.5 if c.n > 1 else 0

def mid(c: Col) -> Atom: 
  """Return central tendency (mean for Num, mode for Sym)."""
  return c.mu if Num==type(c) else max(c.has, key=c.has.get)

def spread(c: Col) -> float:
  """Return variability (standard deviation for Num, entropy for Sym)."""
  if Num==type(c): return c.sd
  n = sum(c.has.values())
  return  -sum(v/n * log2(v/n) for v in c.has.values())

def norm(c: Num, v: Qty) -> float:
  """Normalize numeric values using a logistic function."""
  if v == "?": return v
  z = (v - c.mu) / (c.sd+1e-32)
  z = max(-3, min(3, z))
  return 1/(1 + exp(-1.7*z))

def pick(it: Any, v: Any = None) -> Any:
  """Sample from distribution. If v given, mutate around it."""
  if Sym == type(it): return pick(it.has)
  if Num == type(it):
    center = v if v is not None and v != "?" else it.mu
    lo, hi = it.mu - 3*it.sd, it.mu + 3*it.sd
    new = center + it.sd*2*(rand()+rand()+rand() - 1.5)
    return lo + (new - lo) % (hi - lo + 1e-32)
  if dict == type(it):
    n = sum(it.values()) * rand()
    for k, v in it.items():
      if (n := n - v) <= 0: return k

# ---- 2. Data (Tables) ----
class Data:
  """Stores rows and summarizes them in corresponding columns."""
  def __init__(i, src: Iterable = None):
    src = iter(src or {})
    i.rows, i.cols, i._centroid = [], Cols(next(src)), None
    adds(src, i)

class Cols:
  """Extracts and organizes Num and Sym columns from header strings."""
  def __init__(i, names: list[str]):
    i.names, i.all = names, [Col(txt, j) for j, txt in enumerate(names)]
    i.klass = next((c for c in i.all if c.txt[-1] == "!"), None)
    i.xs    = [c for c in i.all if c.txt[-1] not in "+-!X"]
    i.ys    = [c for c in i.all if c.txt[-1] in "+-!"]

def clone(d: Data, rs: list = None) -> Data: 
  """Create an empty Data object with the same columns, adding optional rows."""
  return adds(rs or [], Data([d.cols.names]))

def sub(it: Any, v: Any) -> Any: 
  """Remove a value or row by adding it with weight -1."""
  return add(it, v, -1)

def add(it: Data|Col, v: Any, w: int = 1) -> Any:
  """Add a value or row, updating nested summaries automatically."""
  if Data is type(it):
    it._centroid = None
    [summarize(c, v[c.at], w) for c in it.cols.all] 
    (it.rows.append if w > 0 else it.rows.remove)(v) 
  else: summarize(it, v, w)
  return v

def mids(d: Data) -> list[Atom]: 
  """Return the centroid (midpoints) of all columns in the data."""
  d._centroid = d._centroid or [mid(c) for c in d.cols.all]
  return d._centroid

def adds(src: Iterable, it: Any = None) -> Data | Col:
  """Add multiple items from an iterable into the target object."""
  it = it or Num(); [add(it, v) for v in (src or [])]; return it

def wins(d: Data) -> Callable:
  """Return a function that scores rows based on distance to heaven."""
  ds = [disty(d, r) for r in d.rows]
  lo, med = min(ds), sorted(ds)[len(ds)//2]
  return lambda r: int(100*(1 - (disty(d,r) - lo) / (med - lo + 1e-32)))

def ready(file: Any) -> tuple[Data, Data, Rows]:
  """Load, safely shuffle, and split data into train/test sets."""
  d = file if Data == type(file) else Data(csv(file))
  random.shuffle(d.rows)
  n = len(d.rows) // 2
  return d, clone(d, d.rows[:n][:the.learn.budget]), d.rows[n:]

# ---- 3, Bayes ----
def like(c: Col, v: Any, prior) -> float:
  """Return how much a column likes a value."""
  if type(c) == Sym:
    return (c.has.get(v,0) + the.bayes.k*prior) / (c.n + the.bayes.k)
  sd = c.sd + 1e-32
  return (1/sqrt(2*pi*sd*sd)) * exp(-((v-c.mu)**2) / (2*sd*sd))

def likes(d: Data, r: Row, n_rows: int, n_klasses: int) -> float:
  """Return log likelihood of row r given data d."""
  prior = (len(d.rows)+the.bayes.m) / (n_rows + the.bayes.m * n_klasses)
  ls    = [like(c,v,prior) for c in d.cols.xs if (v:=r[c.at])!="?"]
  return log(prior) + sum(log(v) for v in ls if v>0)

def classify(src: Iterable, wait: int = 10) -> dict:
  """Test then train: classify row using existing models before updating them."""
  src = iter(src)
  h, cf, all = {}, Confuse(), Data([next(src)])
  for n, r in enumerate(src):
    want = r[all.cols.klass.at]
    if n >= wait:
      confuse(cf, want, max(h, key=lambda kl: likes(h[kl],r,len(all.rows),len(h))))
    if want not in h: h[want] = clone(all)
    add(all, add(h[want], r))
  return cf
   
def Confuse() -> dict: 
  """Initialize an empty dictionary for lazy confusion matrix tracking."""
  return {}

def confuse(cf: dict, want: Any, got: Any) -> Any:
  """Track a prediction. O(1) update time via lazy tracking."""
  cf[want] = cf.get(want) or {}
  cf[want][got] = cf[want].get(got, 0) + 1
  return got

def confused(cf: dict ) -> list[S]:
  """Confusion stats. label on RHS for alignment. All metrics as int %."""
  klasses = sorted(set(cf.keys()).union({g for w in cf.values() for g in w.keys()}))
  total = sum(cf[w][g] for w in cf for g in cf[w])
  p = lambda y, z: int(100 * y / (z or 1e-32)) 
  out = []
  for c in klasses:
    tp = cf.get(c, {}).get(c, 0)
    fn = sum(cf.get(c, {}).values()) - tp
    fp = sum(cf.get(w, {}).get(c, 0) for w in cf if w != c)
    tn = total - tp - fn - fp
    pd, pr, sp = p(tp, tp+fn), p(tp, fp+tp), p(tn, tn+fp)
    out.append(S(tp=tp, fn=fn, fp=fp, tn=tn, pd=pd, pr=pr, 
                 f1=int(2*pd*pr/(pd+pr+1e-32)), 
                 g=int(2*pd*sp/(pd+sp+1e-32)), 
                 acc=p(tp+tn, total), label="  " +c))
  return out

# ---- 4. Distance ----
def minkowski(items: Iterable[Qty]) -> float:
  """Calculate generic Minkowski distance parameterised by `the.p`."""
  tot, n = 0, 1e-32
  for item in items: tot, n = tot + item**the.p, n + 1
  return (tot/n) ** (1/the.p)

def disty(d: Data, r: Row) -> float:
  """Calculate distance to the 'heaven' (perfect) row on dependent (Y) vars."""
  return minkowski(abs(norm(c, r[c.at]) - c.heaven) for c in d.cols.ys)

def distx(d: Data, r1: Row, r2: Row) -> float:
  """Calculate distance between two rows on independent (X) vars."""
  return minkowski(aha(c, r1[c.at], r2[c.at]) for c in d.cols.xs)

def aha(c: Col, u: Any, v: Any) -> float:
  """Calculate distance between two isolated values in a specific column."""
  if u == v == "?": return 1
  if Sym == type(c): return u != v
  u, v = norm(c, u), norm(c, v)
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)

# ---- 5. Trees ----
class Tree:
  """A decision tree node holding data, splits, and children."""
  def __init__(i, d: Data, rs: Rows):
    i.d, i.ynum = clone(d, rs), adds((disty(d, r) for r in rs), Num())
    i.col, i.cut, i.left, i.right = None, 0, None, None

def treeCuts(c: Col, rs: Rows) -> Iterable[Any]:
  """Yield possible split points for a column."""
  vs = [r[c.at] for r in rs if r[c.at] != "?"]
  if not vs: return []
  return set(vs) if Sym == type(c) else [sorted(vs)[len(vs)//2]]

def treeSplit(d: Data, c: Col, cut: Any, rs: Rows) -> tuple:
  """Evaluate splitting rows on a specific column and cut point."""
  l_rs, r_rs, l_num, r_num = [], [], Num(), Num()
  for r in rs:
    v = r[c.at]
    go = v == "?" or (v == cut if Sym == type(c) else v <= cut)
    (l_rs if go else r_rs).append(r)
    add(l_num if go else r_num, disty(d, r))
  return (l_num.n * spread(l_num) + r_num.n * spread(r_num), c, cut, l_rs, r_rs)

def treeGrow(d: Data, rs: Rows) -> Tree:
  """Recursively grow a decision tree to minimize Y-distance variance."""
  t = Tree(d, rs)
  if len(rs) >= 2 * the.learn.leaf:
    splits = (treeSplit(d, c, cut, rs) 
                 for c in t.d.cols.xs for cut in treeCuts(c, rs))
    if valid := [s for s in splits if min(len(s[3]), len(s[4])) >= the.learn.leaf]:
      _, t.col, t.cut, left, right = min(valid, key=lambda x: x[0])
      t.left, t.right = treeGrow(d, left), treeGrow(d, right)
  return t

def treeLeaf(t: Tree, r: Row) -> Tree:
  """Traverse the tree to find the leaf node for a given row."""
  if not t.left: return t
  v = r[t.col.at]
  go = (v != "?" and v <= t.cut) if Num == type(t.col) else (v != "?" and v == t.cut)
  return treeLeaf(t.left if go else t.right, r)

def treeNodes(t: Tree, lvl: int = 0, col: Col = None, op: str = "", 
              cut: Any = None) -> Iterable[tuple]:
  """Yield all nodes in the tree via depth-first search."""
  yield t, lvl, col, op, cut
  if t.col:
    ops = ("<=", ">") if Num == type(t.col) else ("==", "!=")
    kids = sorted([(t.left, ops[0]), (t.right, ops[1])], key=lambda z: mid(z[0].ynum))
    for k, s in kids:
      if k: yield from treeNodes(k, lvl + 1, t.col, s, t.cut)

def treeShow(t: Tree) -> None:
  """Print the full tree structure to standard output."""
  for t1, lvl, col, op, cut in treeNodes(t):
    p = f"{col.txt} {op} {o(cut)}" if col else ""
    if lvl > 0: p = "|   " * (lvl - 1) + p
    g = {c.txt: mid(c) for c in t1.d.cols.ys}
    print(f"{p:<{the.show.show}},{o(mid(t1.ynum)):>4} ,({t1.ynum.n:3}), {o(g)}")

def treePlan(t: Tree, here: Tree) -> Iterable[tuple]:
  """Yield plans (variable changes) to improve outcomes from current leaf."""
  eps = the.stats.eps * spread(t.ynum)
  for there, _, _, _, _ in treeNodes(t):
    if there.col is None and (dy := mid(here.ynum) - mid(there.ynum)) > eps:
      diff = [f"{c.txt}={o(mid(c))}" for c, h in zip(there.d.cols.xs, here.d.cols.xs) 
              if mid(c) != mid(h)]
      if diff: yield dy, mid(there.ynum), diff

# ---- 6. Clustering ----
def kmeans(d: Data, rs: Rows = None, k: int = 10, n: int = 10, 
           cents: Rows = None) -> Datas:
  """Cluster rows into `k` groups using nearest-centroid assignments."""
  rs, out = rs or d.rows, []
  cents = cents or choices(rs, k=k)
  for _ in range(n):
    out = [clone(d) for _ in cents]
    for r in rs: add(out[min(range(len(cents)), key=lambda j: distx(d, cents[j], r))], r)
    cents = [mids(kid) for kid in out if kid.rows]
  return out

def kpp(d: Data, rs: Rows = None, k: int = 10, few: int = 256) -> Rows:
  """Select initial k-means centroids maximizing distances (k-means++)."""
  rs, out = rs or d.rows, [choice(rs or d.rows)]
  while len(out) < k:
    t = sample(rs, min(few, len(rs)))
    ws = {i: min(distx(d, t[i], c)**2 for c in out) for i in range(len(t))}
    out.append(t[pick(ws)])
  return out

def half(d: Data, rs: Rows, few: int = 20) -> tuple:
  """Divide rows into two halves based on distance to two extreme points."""
  t = sample(rs, min(few, len(rs)))
  gap, east, west = max(
    ((distx(d, r1, r2), r1, r2) for r1 in t for r2 in t),
    key=lambda z: z[0]
  )
  proj = lambda r: (distx(d, r, east)**2 + gap**2 - distx(d, r, west)**2) / (2*gap+1e-32)
  rs = sorted(rs, key=proj)
  n = len(rs) // 2
  return rs[:n], rs[n:], east, west, gap, proj(rs[n])
 
def rhalf(d: Data, rs: Rows = None, k: int = 10, stop: int = None, 
          few: int = 20) -> Datas:
  """Recursively halve rows into clusters until hitting a size/depth limit."""
  rs, stop = rs if rs is not None else d.rows, stop or 20
  if len(rs) <= 2 * stop: return [clone(d, rs)]
  l, r, east, west, gap, cut = half(d, rs, few)
  return rhalf(d, l, k, stop, few) + rhalf(d, r, k, stop, few)

def neighbors(d: Data, r1: Row, ds: Datas, near: int = 1, fast: bool = False) -> Rows:
  """Find the `near`-est rows (or nearest cluster centroid if `fast`) to `r1`."""
  c = min(ds, key=lambda c: distx(d, r1, mids(c)))
  return [mids(c)] if fast else sorted(c.rows, key=lambda r2: distx(d, r1, r2))[:near]

def clustering(d0: Data, build: Callable, near: int = 1, fast: bool = False) -> list[str]:
  """Benchmark clustering algorithms, returning timing and error metrics."""
  t_build, t_apply, err, repeats = 0, 0, 0, 10
  for _ in range(repeats):
    d, train, test = ready(d0)
    predict = lambda rs: sum(disty(train, r) for r in rs)/len(rs) if rs else 0
    t_1 = now()
    ds = build(train)
    t_2 = now()
    t_build += t_2 - t_1
    for r in test: 
      near_rs = neighbors(train, r, ds, near=near, fast=fast)
      err += abs(disty(d, r) - predict(near_rs)) / len(test)
    t_apply += now() - t_2
  return [f"{x/repeats:>7.2f}" for x in [t_build/1e6, t_apply/1e6, err]] 

# ----- 7. Active learning -----
def acquireWithBayes(d: Data, best: Data, rest: Data, r: Row) -> float:
  """Negative means more likely best. Sorting ascending = most likely 1st."""
  n = len(best.rows) + len(rest.rows)
  return likes(rest, r, n, 2) - likes(best, r, n, 2)

def acquireWithCentroid(d: Data, best: Data, rest: Data, r: Row) -> float:
  """Negative means closer to best. Sorting ascending = closest first."""
  return distx(d, r, mids(best)) - distx(d, r, mids(rest))

def acquire(d, score=acquireWithBayes, label=lambda _,r:r) -> (Rows,callable):
  """Using rows labelled so far, pick what unlabelled to label next."""
  rows = d.rows[:]
  shuffle(rows)
  lab   = clone(d, rows[:the.learn.start])
  unlab = rows[the.learn.start:][:the.few]
  lab.rows.sort(key=lambda r: disty(lab, label(d,r)))
  n = sqrt(len(lab.rows))
  best,rest = clone(d,lab.rows[:int(n)]), clone(d,lab.rows[int(n):])
  cursor = 0
  fn = lambda r: score(lab, best, rest, r)
  for _ in range(the.learn.budget):
    for j in range(len(unlab)):  # scan at most one full cycle
      idx = (cursor + j) % len(unlab)  # calculate circular offset safely
      if fn(unlab[idx]) < 0:
        add(lab, 
          add(best, 
            label(d,
              unlab.pop(idx))))
        if len(best.rows) > sqrt(len(lab.rows)):
          best.rows.sort(key=lambda r: disty(lab,r))
          add(rest, 
            sub(best, 
              best.rows[-1]))
        cursor = idx  # resume from the shifted position next cycle
        break
    else:
      break  # stop outer for loop if a full pass finds nothing
  lab.rows.sort(key=lambda r: disty(lab,r))
  return lab

# ---- 8. 1+1 optimization ----
def picks(d: Data, r: Row, n: int = 1) -> Row:
  """Copy row, mutate n random x-columns around current vals."""
  s = r[:]
  for c in sample(d.cols.xs, min(n, len(d.cols.xs))):
    s[c.at] = pick(c, s[c.at])
  return s

def nearest(d: Data, r: Row, rs: Rows = None) -> Row:
  """Find row in rs closest to r on x-columns."""
  return min(rs or d.rows, key=lambda r2: distx(d, r, r2))

def last(gen) -> Any:
  """Return final value from a generator."""
  v = None
  for v in gen: pass
  return v

def oneplus1(d: Data, mutate: Callable,
             accept: Callable, oracle: Callable,
             budget: int = 1000, restart: int = 0):
  """(1+1) search: mutate, score via oracle, accept/reject."""
  h, best, best_e = 0, None, 1E32
  s, e, imp = choice(d.rows)[:], 1E32, 0
  while h < budget:
    for sn in mutate(s):
      h += 1
      en = oracle(sn)
      if accept(e, en, h, budget): s, e = sn, en
      if en < best_e:
        best, best_e, imp = sn[:], en, h
        yield h, best_e, best
      if restart and h - imp > restart:
        s, e, imp = choice(d.rows)[:], 1E32, h
        break

def oracleNearest(d: Data, r: Row) -> float:
  """Score row: copy y-vals from nearest, return disty."""
  near = nearest(d, r)
  for c in d.cols.ys: r[c.at] = near[c.at]
  return disty(d, r)

def sa(d: Data, oracle: Callable, restarts: int = 0,
       m: float = 0.5, budget: int = 1000):
  """Simulated annealing: Boltzmann accept, multi-col mutate."""
  n = max(1, int(m * len(d.cols.xs)))
  def accept(e, en, h, b): return en<e or rand()<exp((e-en)/(1-h/b+1E-32))
  def mutate(s): yield picks(d, s, n)
  return oneplus1(d, mutate, accept, oracle, budget, restarts)

def ls(d: Data, oracle: Callable, restarts: int = 100,
       p: float = 0.5, tries: int = 20,
       budget: int = 1000):
  """Local search: greedy accept, single-col neighborhood."""
  def accept(e, en, *_): return en < e
  def mutate(s):
    c = choice(d.cols.xs)
    for _ in range(tries if rand() < p else 1):
      s = s[:]; s[c.at] = pick(c, s[c.at]); yield s
  return oneplus1(d, mutate, accept, oracle, budget, restarts)
 
# ---- Ready,set, go. ----

the = S()
for k, v in re.findall(r"([\w.]+)=(\S+)", __doc__): nest(the, k, thing(v))
