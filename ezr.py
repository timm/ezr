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
from typing import Any,Iterable,Callable
from types import SimpleNamespace as S

# Naming conventions:
#   i:self  j:iterator  col:Col  data:Data
#   datas:Datas  row:row  rs:rows  v:value  w:weight
#   x:independent  y:dependent  tree:Tree
#   n,m:int  txt:str  xs,ys:lists

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

def mid(col):
  """Central tendency (mean or mode)."""
  return col.mu if Num==type(col) else max(
                   col.has, key=col.has.get)

def spread(col):
  """Variability (sd or entropy)."""
  if Num==type(col): return col.sd
  n = sum(col.has.values())
  return -sum(v/n*log2(v/n)
              for v in col.has.values())

def norm(num, v):
  """Normalize via logistic function."""
  if v == "?": return v
  z = (v - num.mu) / (num.sd+1e-32)
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
    i.all = [Col(txt,j)
             for j,txt in enumerate(names)]
    i.klass = next((col for col in i.all
                     if col.txt[-1]=="!"), None)
    i.xs = [col for col in i.all
             if col.txt[-1] not in "+-!X"]
    i.ys = [col for col in i.all
             if col.txt[-1] in "+-!"]

def clone(data, rows=None):
  """Clone structure, optionally add rows."""
  return adds(rows or [], Data([data.cols.names]))

def sub(it, v):
  """Remove value/row (add with w=-1)."""
  return add(it, v, -1)

def add(it, v, w=1):
  """Add value/row to Data,Cols,Num,Sym."""
  if Data is type(it):
    it._centroid = None
    add(it.cols, v, w)
    (it.rows.append if w > 0 else it.rows.remove)(v)
  elif Cols is type(it):
    [add(col, v[col.at], w) for col in it.all]
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

def mids(data):
  """Centroid of all columns."""
  data._centroid = data._centroid or [
    mid(col) for col in data.cols.all]
  return data._centroid

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

def disty(data, row):
  """Distance to heaven on Y vars."""
  return minkowski(
    abs(norm(col,row[col.at]) - col.heaven)
    for col in data.cols.ys)

def distx(data, r1, r2):
  """Distance between rows on X vars."""
  return minkowski(
    aha(col, r1[col.at], r2[col.at])
    for col in data.cols.xs)

def aha(col, u, v):
  """Distance between two values."""
  if u == v == "?": return 1
  if Sym == type(col): return u != v
  u, v = norm(col, u), norm(col, v)
  u = u if u!="?" else (0 if v>0.5 else 1)
  v = v if v!="?" else (0 if u>0.5 else 1)
  return abs(u - v)

def nearest(data, row, rows=None):
  """Closest row on x-columns."""
  return min(rows or data.rows,
    key=lambda r2: distx(data, row, r2))

# ---- 4. Bayes ----
def like(col, v, prior):
  """How much a column likes a value."""
  if type(col) == Sym:
    return (col.has.get(v,0) +
            the.bayes.k*prior
            ) / (col.n + the.bayes.k)
  sd = col.sd + 1e-32
  return (1/sqrt(2*pi*sd*sd)
          ) * exp(-((v-col.mu)**2)/(2*sd*sd))

def likes(data, row, n_rows, n_klasses):
  """Log likelihood of row given data."""
  prior = (len(data.rows)+the.bayes.m
           ) / (n_rows+the.bayes.m*n_klasses)
  ls = [like(col,v,prior) for col in data.cols.xs
        if (v:=row[col.at])!="?"]
  return log(prior) + sum(log(v)
                          for v in ls if v>0)

def classify(src, wait=10):
  """Test then train: classify before update."""
  src = iter(src)
  h,cf,all = {}, None, Data([next(src)])
  for n, row in enumerate(src):
    want = row[all.cols.klass.at]
    if n >= wait:
      cf = dinc(want, max(h,
        key=lambda kl: likes(
          h[kl],row,len(all.rows),len(h))),cf)
    if want not in h: h[want] = clone(all)
    add(all, add(h[want], row))
  return cf

# ---- 5. Trees ----
class Tree:
  """Decision tree node."""
  def __init__(i, data, rows):
    i.d = clone(data, rows)
    i.ynum = adds(
      (disty(data,row) for row in rows), Num())
    i.col, i.cut = None, 0
    i.left, i.right = None, None

def treeCuts(col, rows):
  """Possible split points for a column."""
  vs = [row[col.at] for row in rows
        if row[col.at]!="?"]
  if not vs: return []
  return (set(vs) if Sym == type(col)
          else [sorted(vs)[len(vs)//2]])

def treeSplit(data, col, cut, rows):
  """Evaluate split on col at cut."""
  l_rows, r_rows = [], []
  l_num, r_num = Num(), Num()
  for row in rows:
    v = row[col.at]
    go = v=="?" or (v==cut if Sym==type(col)
                    else v <= cut)
    (l_rows if go else r_rows).append(row)
    add(l_num if go else r_num,
        disty(data,row))
  return (l_num.n*spread(l_num) +
          r_num.n*spread(r_num),
          col, cut, l_rows, r_rows)

def treeGrow(data, rows):
  """Grow tree to minimize Y-variance."""
  tree = Tree(data, rows)
  if len(rows) >= 2 * the.learn.leaf:
    splits = (treeSplit(data, col, cut, rows)
              for col in tree.d.cols.xs
              for cut in treeCuts(col, rows))
    if valid := [s for s in splits
        if min(len(s[3]),len(s[4]))
           >= the.learn.leaf]:
      _, tree.col, tree.cut, left, right = min(
        valid, key=lambda x: x[0])
      tree.left  = treeGrow(data, left)
      tree.right = treeGrow(data, right)
  return tree

def treeLeaf(tree, row):
  """Find leaf node for row."""
  if not tree.left: return tree
  v = row[tree.col.at]
  go = ((v!="?" and v<=tree.cut)
        if Num == type(tree.col)
        else (v!="?" and v==tree.cut))
  return treeLeaf(
    tree.left if go else tree.right, row)

def treeNodes(tree,lvl=0,col=None,
              op="",cut=None):
  """Yield all nodes (depth-first)."""
  yield tree, lvl, col, op, cut
  if tree.col:
    ops = (("<=",">")
           if Num == type(tree.col)
           else ("==","!="))
    kids = sorted(
      [(tree.left,ops[0]),
       (tree.right,ops[1])],
      key=lambda z: mid(z[0].ynum))
    for k, txt in kids:
      if k: yield from treeNodes(
              k, lvl+1, tree.col,
              txt, tree.cut)

def treeShow(tree):
  """Print tree structure."""
  for t1,lvl,col,op,cut in treeNodes(tree):
    p = f"{col.txt} {op} {o(cut)}" \
        if col else ""
    if lvl > 0: p = "|   "*(lvl-1) + p
    g = {col.txt:mid(col)
         for col in t1.d.cols.ys}
    print(f"{p:<{the.show.show}}"
          f",{o(mid(t1.ynum)):>4}"
          f" ,({t1.ynum.n:3}), {o(g)}")

def treePlan(tree, here):
  """Plans to improve from current leaf."""
  eps = the.stats.eps * spread(tree.ynum)
  for there, _, _, _, _ in treeNodes(tree):
    if there.col is None and \
       (dy := mid(here.ynum) -
              mid(there.ynum)) > eps:
      diff = [f"{col.txt}={o(mid(col))}"
              for col,h in zip(
                there.d.cols.xs,
                here.d.cols.xs)
              if mid(col) != mid(h)]
      if diff:
        yield dy, mid(there.ynum), diff

# ---- 6. Active learning ----
def acquireWithBayes(data, best, rest, row):
  """Score: rest - best likelihood."""
  n = len(best.rows) + len(rest.rows)
  return (likes(rest, row, n, 2) -
          likes(best, row, n, 2))

def acquireWithCentroid(data, best, rest, row):
  """Score: dist(best) - dist(rest)."""
  return (distx(data, row, mids(best)) -
          distx(data, row, mids(rest)))

def warm_start(data, rows, label):
  """Init lab/best/rest from start rows."""
  lab = clone(data, rows[:the.learn.start])
  lab.rows.sort(key=lambda row:
    disty(lab, label(data, row)))
  n = int(sqrt(len(lab.rows)))
  return (lab, clone(data, lab.rows[:n]),
          clone(data, lab.rows[n:]),
          rows[the.learn.start:])

def rebalance(best, rest, lab):
  """Cap best at sqrt(|lab|); evict worst."""
  if len(best.rows) > sqrt(len(lab.rows)):
    best.rows.sort(
      key=lambda row: disty(lab, row))
    add(rest.cols, sub(best.cols,
                       best.rows[-1]))
    rest.rows.append(best.rows.pop())

def acquire(data, score=acquireWithCentroid,
            label=lambda _,row:row):
  """Active learning. Returns labeled Data."""
  rows = data.rows[:]
  shuffle(rows)
  lab, best, rest, unlab = warm_start(
    data, rows[:the.few], label)
  for _ in range(the.learn.budget):
    if not unlab: break
    pick, *unlab = sorted(unlab,
      key=lambda row:
        score(lab,best,rest,row))
    add(lab, add(best, label(data, pick)))
    rebalance(best, rest, lab)
  lab.rows.sort(
    key=lambda row: disty(lab, row))
  return lab

# ---- 7. 1+1 optimization ----
def picks(data, row, n=1):
  """Mutate n random x-columns."""
  s = row[:]
  for col in sample(data.cols.xs,
                    min(n, len(data.cols.xs))):
    s[col.at] = pick(col, s[col.at])
  return s

def oneplus1(data, mutate, accept, oracle,
             budget=1000, restart=0):
  """(1+1) search: mutate, score, accept."""
  h, best, best_e = 0, None, 1E32
  s, e, imp = choice(data.rows)[:], 1E32, 0
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
        s = choice(data.rows)[:]
        e, imp = 1E32, h
        break

def oracleNearest(data, row):
  """Score: copy y-vals from nearest."""
  near = nearest(data, row)
  for col in data.cols.ys:
    row[col.at] = near[col.at]
  return disty(data, row)

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
def dinc(k1, k2, b4=None):
  """Increment nested dict counter."""
  b4 = b4 or {}
  b4[k1] = b4.get(k1) or {}
  b4[k1][k2] = b4[k1].get(k2, 0) + 1
  return b4

def o(x):
  """Recursive format. Sorts dicts."""
  if isa(x,float): 
      return f"{x:.{the.show.decimals}f}"
  if isa(x,dict): 
      return "{"+", ".join(f"{k}={o(v)}"
                   for k,v in sorted(x.items()))+"}"
  if isa(x,list): 
      return "{"+", ".join(map(o, x))+"}"
  if isa(x, S): 
      return "S" + o(x.__dict__)
  if hasattr(x, "__dict__"):
       return x.__class__.__name__+o(x.__dict__)
  return str(x)

def table(lst, w=10):
  """Print list of dicts as aligned table."""
  if not lst: return
  ds = [x if type(x) is dict else x.__dict__ for x in lst]
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

def csv(f, clean=lambda txt:
          txt.partition("#")[0].split(",")):
  """Yield typed rows from a CSV file."""
  with open(f, encoding="utf-8") as file:
    for txt in file:
      row = clean(txt)
      if any(x.strip() for x in row):
        yield [thing(x) for x in row]

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
