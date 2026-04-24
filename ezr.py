#!/usr/bin/env python3 -B
# ezr.py: explainable multi-objective optimization
# (c) 2026 Tim Menzies, timm@ieee.org, MIT license
"""
Options:

    --seed=1             random number seed
    --p=2                distance (1,2=Man,Euclid)
    --learn.leaf=3       examples per leaf
    --learn.budget=50    rows to evaluate
    --learn.check=5      guesses to check
    --learn.start=4      initial labels
    --bayes.m=2          m-estimate for Naive Bayes
    --bayes.k=1          k-estimate (Laplace) for NB
    --few=128            max unlabelled rows
    --stats.cliffs=0.195 Cliff's Delta threshold
    --stats.conf=1.36    KS test confidence
    --stats.eps=0.35     margin of error multiplier
    --show.show=30       tree display width
    --show.decimals=2    decimal places for floats
    --textmine.norm=0    CNB weight normalization
    --textmine.yes=20    positive samples
    --textmine.no=20     negative samples
    --textmine.top=100   top TF-IDF features
    --textmine.valid=20  repeats for stats testing
"""
from __future__ import annotations
from time import perf_counter_ns as now
import os, re, random, sys, bisect, math
from pathlib import Path
from random import random as rand
from random import choices,choice,sample,shuffle
from math import log, log2, exp, sqrt, pi
from typing import Any
from types import SimpleNamespace as S

# Naming conventions:
#   i:self  j:iterator  c:Col  d:Data
#   ds:Datas  r:row  rs:rows  v:value  w:weight
#   x:independent  y:dependent  t:Tree
#   n,m:int  s:str  xs,ys:lists

isa = isinstance

# ---- Types ----
type Qty   = int | float
type Atom  = str | bool | Qty
type Row   = list[Atom]
type Rows  = list[Row]
type Col   = Num | Sym
type Cols  = list[Col]
type Tree  = Any
type Datas = list[Data]

# ---- 1. Columns ----
def Col(txt="", a=0):
  """Num or Sym column based on name case."""
  return (Num if txt[0].isupper()
          else Sym)(txt, a)

class Num:
  """Summarizes a stream of numbers."""
  def __init__(i, txt="", a=0):
    i.txt, i.at, i.n = txt, a, 0
    i.mu, i.m2, i.sd = 0, 0, 0
    i.heaven = txt[-1:] != "-"

class Sym:
  """Summarizes a stream of symbols."""
  def __init__(i, txt="", a=0):
    i.txt, i.at, i.n, i.has = txt, a, 0, {}

def mid(c):
  """Central tendency (mean or mode)."""
  return c.mu if Num==type(c) else max(
                   c.has, key=c.has.get)

def spread(c):
  """Variability (sd or entropy)."""
  if Num==type(c): return c.sd
  n = sum(c.has.values())
  return -sum(v/n*log2(v/n)
              for v in c.has.values())

def norm(c, v):
  """Normalize via logistic function."""
  if v == "?": return v
  z = (v - c.mu) / (c.sd+1e-32)
  z = max(-3, min(3, z))
  return 1/(1 + exp(-1.7*z))

# ---- 2. Data (Tables) ----
class Data:
  """Rows + summarized columns."""
  def __init__(i, src=None):
    src = iter(src or {})
    i.rows = []
    i.cols = Cols(next(src))
    i._centroid = None
    adds(src, i)

class Cols:
  """Organize Num/Sym columns from headers."""
  def __init__(i, names):
    i.names = names
    i.all = [Col(s,j)
             for j,s in enumerate(names)]
    i.klass = next((c for c in i.all
                     if c.txt[-1]=="!"), None)
    i.xs = [c for c in i.all
             if c.txt[-1] not in "+-!X"]
    i.ys = [c for c in i.all
             if c.txt[-1] in "+-!"]

def clone(d, rs=None):
  """Clone structure, optionally add rows."""
  return adds(rs or [], Data([d.cols.names]))

def sub(it, v):
  """Remove value/row (add with w=-1)."""
  return add(it, v, -1)

def add(it, v, w=1):
  """Add value/row to Data,Cols,Num,Sym."""
  if Data is type(it):
    it._centroid = None
    add(it.cols, v, w)
    (it.rows.append if w > 0
     else it.rows.remove)(v)
  elif Cols is type(it):
    [add(c, v[c.at], w) for c in it.all]
  elif v != "?":
    if Sym == type(it):
      it.has[v] = w + it.has.get(v, 0)
    elif w < 0 and it.n <= 2:
      it.n = it.mu = it.m2 = it.sd = 0
    else:
      it.n += w
      delta = v - it.mu
      it.mu += w * delta / it.n
      it.m2 += w * delta * (v - it.mu)
      it.sd = ((max(0, it.m2)/(it.n-1))**.5
               if it.n > 1 else 0)
  return v

def mids(d):
  """Centroid of all columns."""
  d._centroid = d._centroid or [
    mid(c) for c in d.cols.all]
  return d._centroid

def adds(src, it=None):
  """Add multiple items to target."""
  it = it or Num()
  [add(it, v) for v in (src or [])]
  return it

# ---- 3. Distance ----
def minkowski(items):
  """Minkowski distance (param: the.p)."""
  tot, n = 0, 1e-32
  for item in items:
    tot, n = tot + item**the.p, n + 1
  return (tot/n) ** (1/the.p)

def disty(d, r):
  """Distance to heaven on Y vars."""
  return minkowski(
    abs(norm(c,r[c.at]) - c.heaven)
    for c in d.cols.ys)

def distx(d, r1, r2):
  """Distance between rows on X vars."""
  return minkowski(
    aha(c, r1[c.at], r2[c.at])
    for c in d.cols.xs)

def aha(c, u, v):
  """Distance between two values."""
  if u == v == "?": return 1
  if Sym == type(c): return u != v
  u, v = norm(c, u), norm(c, v)
  u = u if u!="?" else (0 if v>0.5 else 1)
  v = v if v!="?" else (0 if u>0.5 else 1)
  return abs(u - v)

def nearest(d, r, rs=None):
  """Closest row on x-columns."""
  return min(rs or d.rows,
    key=lambda r2: distx(d, r, r2))

# ---- 4. Bayes ----
def like(c, v, prior):
  """How much a column likes a value."""
  if type(c) == Sym:
    return (c.has.get(v,0) +
            the.bayes.k*prior
            ) / (c.n + the.bayes.k)
  sd = c.sd + 1e-32
  return (1/sqrt(2*pi*sd*sd)
          ) * exp(-((v-c.mu)**2)/(2*sd*sd))

def likes(d, r, n_rows, n_klasses):
  """Log likelihood of row r given data d."""
  prior = (len(d.rows)+the.bayes.m
           ) / (n_rows+the.bayes.m*n_klasses)
  ls = [like(c,v,prior) for c in d.cols.xs
        if (v:=r[c.at])!="?"]
  return log(prior) + sum(log(v)
                          for v in ls if v>0)

def classify(src, wait=10):
  """Test then train: classify before update."""
  src = iter(src)
  h,cf,all = {}, Confuse(), Data([next(src)])
  for n, r in enumerate(src):
    want = r[all.cols.klass.at]
    if n >= wait:
      confuse(cf, want, max(h,
        key=lambda kl: likes(
          h[kl],r,len(all.rows),len(h))))
    if want not in h: h[want] = clone(all)
    add(all, add(h[want], r))
  return cf

def Confuse():
  """Empty confusion matrix."""
  return {}

def confuse(cf, want, got):
  """Track a prediction."""
  cf[want] = cf.get(want) or {}
  cf[want][got] = cf[want].get(got, 0) + 1
  return got

# ---- 5. Trees ----
class Tree:
  """Decision tree node."""
  def __init__(i, d, rs):
    i.d = clone(d, rs)
    i.ynum = adds(
      (disty(d,r) for r in rs), Num())
    i.col, i.cut = None, 0
    i.left, i.right = None, None

def treeCuts(c, rs):
  """Possible split points for a column."""
  vs = [r[c.at] for r in rs if r[c.at]!="?"]
  if not vs: return []
  return (set(vs) if Sym == type(c)
          else [sorted(vs)[len(vs)//2]])

def treeSplit(d, c, cut, rs):
  """Evaluate split on column c at cut."""
  l_rs, r_rs = [], []
  l_num, r_num = Num(), Num()
  for r in rs:
    v = r[c.at]
    go = v=="?" or (v==cut if Sym==type(c)
                    else v <= cut)
    (l_rs if go else r_rs).append(r)
    add(l_num if go else r_num, disty(d,r))
  return (l_num.n*spread(l_num) +
          r_num.n*spread(r_num),
          c, cut, l_rs, r_rs)

def treeGrow(d, rs):
  """Grow tree to minimize Y-variance."""
  t = Tree(d, rs)
  if len(rs) >= 2 * the.learn.leaf:
    splits = (treeSplit(d, c, cut, rs)
              for c in t.d.cols.xs
              for cut in treeCuts(c, rs))
    if valid := [s for s in splits
        if min(len(s[3]),len(s[4]))
           >= the.learn.leaf]:
      _, t.col, t.cut, left, right = min(
        valid, key=lambda x: x[0])
      t.left  = treeGrow(d, left)
      t.right = treeGrow(d, right)
  return t

def treeLeaf(t, r):
  """Find leaf node for row."""
  if not t.left: return t
  v = r[t.col.at]
  go = ((v!="?" and v<=t.cut)
        if Num == type(t.col)
        else (v!="?" and v==t.cut))
  return treeLeaf(
    t.left if go else t.right, r)

def treeNodes(t,lvl=0,col=None,op="",cut=None):
  """Yield all nodes (depth-first)."""
  yield t, lvl, col, op, cut
  if t.col:
    ops = (("<=",">") if Num == type(t.col)
           else ("==","!="))
    kids = sorted(
      [(t.left,ops[0]), (t.right,ops[1])],
      key=lambda z: mid(z[0].ynum))
    for k, s in kids:
      if k: yield from treeNodes(
              k, lvl+1, t.col, s, t.cut)

def treeShow(t):
  """Print tree structure."""
  for t1,lvl,col,op,cut in treeNodes(t):
    p = f"{col.txt} {op} {o(cut)}" \
        if col else ""
    if lvl > 0: p = "|   "*(lvl-1) + p
    g = {c.txt:mid(c) for c in t1.d.cols.ys}
    print(f"{p:<{the.show.show}}"
          f",{o(mid(t1.ynum)):>4}"
          f" ,({t1.ynum.n:3}), {o(g)}")

def treePlan(t, here):
  """Plans to improve from current leaf."""
  eps = the.stats.eps * spread(t.ynum)
  for there, _, _, _, _ in treeNodes(t):
    if there.col is None and \
       (dy := mid(here.ynum) -
              mid(there.ynum)) > eps:
      diff = [f"{c.txt}={o(mid(c))}"
              for c,h in zip(
                there.d.cols.xs,
                here.d.cols.xs)
              if mid(c) != mid(h)]
      if diff:
        yield dy, mid(there.ynum), diff

# ---- 6. Active learning ----
def acquireWithBayes(d, best, rest, r):
  """Score: rest - best likelihood."""
  n = len(best.rows) + len(rest.rows)
  return (likes(rest, r, n, 2) -
          likes(best, r, n, 2))

def acquireWithCentroid(d, best, rest, r):
  """Score: dist(best) - dist(rest)."""
  return (distx(d, r, mids(best)) -
          distx(d, r, mids(rest)))

def warm_start(d, rows, label):
  """Init lab/best/rest from start rows."""
  lab = clone(d, rows[:the.learn.start])
  lab.rows.sort(key=lambda r:
    disty(lab, label(d, r)))
  n = int(sqrt(len(lab.rows)))
  return (lab, clone(d, lab.rows[:n]),
          clone(d, lab.rows[n:]),
          rows[the.learn.start:])

def rebalance(best, rest, lab):
  """Cap best at sqrt(|lab|); evict worst."""
  if len(best.rows) > sqrt(len(lab.rows)):
    best.rows.sort(
      key=lambda r: disty(lab, r))
    add(rest.cols, sub(best.cols,
          (r := best.rows.pop())))
    rest.rows.append(r)

def acquire(d, score=acquireWithCentroid,
            label=lambda _,r:r):
  """Active learning. Returns labeled Data."""
  rows = d.rows[:]
  shuffle(rows)
  lab, best, rest, unlab = warm_start(
    d, rows[:the.few], label)
  for _ in range(the.learn.budget):
    if not unlab: break
    pick, *unlab = sorted(unlab,
      key=lambda r:score(lab,best,rest,r))
    add(lab, add(best, label(d, pick)))
    rebalance(best, rest, lab)
  lab.rows.sort(key=lambda r: disty(lab, r))
  return lab

# ---- 7. 1+1 optimization ----
def picks(d, r, n=1):
  """Mutate n random x-columns."""
  s = r[:]
  for c in sample(d.cols.xs,
                  min(n, len(d.cols.xs))):
    s[c.at] = pick(c, s[c.at])
  return s

def oneplus1(d, mutate, accept, oracle,
             budget=1000, restart=0):
  """(1+1) search: mutate, score, accept."""
  h, best, best_e = 0, None, 1E32
  s, e, imp = choice(d.rows)[:], 1E32, 0
  while h < budget:
    for sn in mutate(s):
      h += 1
      en = oracle(sn)
      if accept(e, en, h, budget):
        s, e = sn, en
      if en < best_e:
        best, best_e, imp = sn[:], en, h
        yield h, best_e, best
      if restart and h - imp > restart:
        s = choice(d.rows)[:]
        e, imp = 1E32, h
        break

def oracleNearest(d, r):
  """Score: copy y-vals from nearest."""
  near = nearest(d, r)
  for c in d.cols.ys: r[c.at] = near[c.at]
  return disty(d, r)

# ---- 8. Stats ----
def same(xs, ys, eps):
  """Are two lists statistically same?"""
  xs, ys = sorted(xs), sorted(ys)
  n, m = len(xs), len(ys)
  if abs(xs[n//2]-ys[m//2]) <= eps: return True
  gt = sum(bisect.bisect_left(ys,a) for a in xs)
  lt = sum(m - bisect.bisect_right(ys,a)
           for a in xs)
  if abs(gt-lt)/(n*m) > the.stats.cliffs:
    return False
  ks = lambda v: abs(
    bisect.bisect_right(xs,v)/n -
    bisect.bisect_right(ys,v)/m)
  return max(max(map(ks,xs)),max(map(ks,ys))
    ) <= the.stats.conf * ((n+m)/(n*m))**.5

def bestRanks(d):
  """Group treatments tied for best."""
  items = sorted(d.items(), key=lambda kv:
    sorted(kv[1])[len(kv[1])//2])
  k0, lst0 = items[0]
  best = {k0: adds(lst0, Num(k0))}
  for k, lst in items[1:]:
    if same(lst0, lst,
            spread(best[k0])*the.stats.eps):
      best[k] = adds(lst, Num(k))
    else: break
  return best

# ---- 9. Utilities ----
def o(x):
  """Recursive format. Sorts dicts."""
  if isa(x,float):
    return f"{x:.{the.show.decimals}f}"
  if isa(x,dict):
    return "{"+", ".join(f"{k}={o(v)}"
      for k,v in sorted(x.items()))+"}"
  if isa(x,list):
    return "{"+", ".join(map(o, x))+"}"
  if isa(x, S): return "S" + o(x.__dict__)
  if hasattr(x, "__dict__"):
    return x.__class__.__name__+o(x.__dict__)
  return str(x)

def table(lst, w=10):
  """Print list of dicts as aligned table."""
  if not lst: return
  ds = [x if type(x) is dict
        else x.__dict__ for x in lst]
  ks = list(ds[0].keys())
  print("".join(f"{str(k):>{w}}" for k in ks))
  print("-" * (len(ks) * w))
  for d in ds:
    print("".join(
       f"{str(d.get(k,'')):>{w}}" for k in ks))

def thing(txt):
  """Coerce string to number or bool."""
  txt = txt.strip()
  b = lambda s: {"true":1,"false":0}.get(
                   s.lower(), s)
  for f in [int, float, b]:
    try: return f(txt)
    except ValueError: pass

def nest(t, k, v):
  """Set value in nested namespace."""
  for x in (ks := k.split("."))[:-1]:
    t = t.__dict__.setdefault(x, S())
  setattr(t, ks[-1], v)

def csv(f, clean=lambda s:
          s.partition("#")[0].split(",")):
  """Yield typed rows from a CSV file."""
  with open(f, encoding="utf-8") as file:
    for s in file:
      r = clean(s)
      if any(x.strip() for x in r):
        yield [thing(x) for x in r]

def pick(it, v=None):
  """Sample from distribution."""
  if Sym == type(it): return pick(it.has)
  if Num == type(it):
    tmp = (v if v is not None and v!="?"
           else it.mu)
    lo = it.mu - 3*it.sd
    hi = it.mu + 3*it.sd
    new = tmp + it.sd*2*(
            rand()+rand()+rand() - 1.5)
    return lo + (new-lo) % (hi-lo + 1e-32)
  if dict == type(it):
    n = sum(it.values()) * rand()
    for k, v in it.items():
      if (n := n - v) <= 0: return k

# ---- Ready, set, go. ----

the = S()
for k,v in re.findall(r"([\w.]+)=(\S+)",__doc__):
  nest(the, k, thing(v))
