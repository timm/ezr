#!/usr/bin/env python3 -B
# ezr.py: explainable multi-objective optimization (core)
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
from random import choices, choice, sample, shuffle
from math import log, log2, exp, sqrt, pi
from typing import Any, Iterable, Callable
from types import SimpleNamespace as S

isa = isinstance

#  ___
#   |       ._    _    _
#   |   \/  |_)  (/_  _>
#       /   |

type Qty   = int|float
type Atom  = str|bool|Qty
type Row   = list[Atom]
type Rows  = list[Row]
type Col   = "Num|Sym"
type Cols  = "list[Col]"
type Datas = "list[Data]"

#   _
#  /    _   |       ._ _   ._    _
#  \_  (_)  |  |_|  | | |  | |  _>

def Col(txt="", a=0):
  """Num or Sym column based on name case."""
  return (Num if txt[0].isupper() else Sym)(txt, a)

class Num:
  """Summarizes a stream of numbers."""
  def __init__(i, txt="", a=0):
    i.txt, i.at, i.n = txt, a, 0
    i.mu=i.m2=i.sd=0; i.heaven=txt[-1:]!="-"

class Sym:
  """Summarizes a stream of symbols."""
  def __init__(i, txt="", a=0):
    i.txt, i.at, i.n, i.has = txt, a, 0, {}

def mid(col):
  """Central tendency (mean or mode)."""
  return col.mu if Num==type(col) else mode(col.has)

def mode(dct):
  """Return the key with most value."""
  return max(dct, key=dct.get)

def spread(col):
  """Variability (sd or entropy)."""
  return col.sd if Num==type(col) else entropy(col.has)

def entropy(dct):
  """Return diversity of some symbol counts."""
  n = sum(dct.values())
  return -sum(v/n*log2(v/n) for v in dct.values())

def norm(num, v):
  """Normalize via logistic function."""
  if v == "?": return v
  z = max(-3, min(3, (v - num.mu)/(num.sd + 1e-32)))
  return 1/(1 + exp(-1.7*z))

#   _
#  | \   _.  _|_   _.
#  |_/  (_|   |_  (_|

class Data:
  """Rows + summarized columns."""
  def __init__(i, src=None):
    src = iter(src or [])
    i.rows, i._centroid = [], None
    i.cols = Cols(next(src))
    adds(src, i)

class Cols:
  """Organize Num/Sym columns from headers."""
  def __init__(i, names):
    i.names = names
    i.klass, i.xs, i.ys, i.all = None, [], [], []
    for j, txt in enumerate(names):
      i.all.append(col := Col(txt, j))
      if txt[-1] != "X":
        if txt[-1] == "!": i.klass = col
        role = i.ys if txt[-1] in "+-!" else i.xs
        role.append(col)

def clone(data, rows=None):
  """Clone structure, optionally add rows."""
  return adds(rows or [], Data([data.cols.names]))

def sub(it, v):
  """Remove value/row (add with w=-1)."""
  return add(it, v, w=-1)

def add(it, v, w=1):
  """Add value/row to Data, Cols, Num, Sym."""
  if Data is type(it):
    it._centroid = None
    add(it.cols, v, w)
    if w > 0: it.rows.append(v)
    else    : it.rows.remove(v)
  elif Cols is type(it):
    [add(col, v[col.at], w) for col in it.all]
  elif v != "?":
    if Sym == type(it):
      it.n += w
      it.has[v] = w + it.has.get(v, 0)
    elif w < 0 and it.n <= 2:
      it.n = it.mu = it.m2 = it.sd = 0
    else:
      it.n  += w
      delta  = v - it.mu
      it.mu += w * delta / it.n
      it.m2 += w * delta * (v - it.mu)
      it.sd  = sqrt(max(0, it.m2)/(it.n-1)) if it.n > 1 else 0
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

#   _
#  | \  o   _  _|_   _.  ._    _   _
#  |_/  |  _>   |_  (_|  | |  (_  (/_

def minkowski(items, p=2):
  """Minkowski distance."""
  tot, n = 0, 1e-32
  for item in items: tot, n = tot + item**p, n + 1
  return (tot/n) ** (1/p)

def disty(data, row):
  """Distance to heaven on Y vars."""
  return minkowski((abs(norm(y, row[y.at]) - y.heaven)
                    for y in data.cols.ys), the.p)

def distx(data, r1, r2):
  """Distance between rows on X vars."""
  return minkowski((aha(x, r1[x.at], r2[x.at])
                    for x in data.cols.xs), the.p)

def aha(col, u, v):
  """Distance between two values."""
  if u == v == "?": return 1
  if Sym == type(col): return u != v
  u, v = norm(col, u), norm(col, v)
  u = u if u != "?" else (0 if v > 0.5 else 1)
  v = v if v != "?" else (0 if u > 0.5 else 1)
  return abs(u - v)

def nearest(data, row, rows=None):
  """Closest row on x-columns."""
  return min(rows or data.rows,
             key=lambda r2: distx(data, row, r2))

def wins(data):
  """Score rows by distance to heaven.
  Clamp d2h within lo+0.35*sd to lo."""
  ys = sorted(disty(data, row) for row in data.rows)
  ten = len(ys)//10
  lo, med, sd = ys[0], ys[5*ten], (ys[9*ten] - ys[ten])/2.56
  def f(row):
    x = disty(data, row)
    if x < lo + 0.35*sd: x = lo
    return max(-100, int(100*(1 - (x-lo)/(med-lo + 1e-32))))
  return f

#   _
#  |_)   _.       _    _
#  |_)  (_|  \/  (/_  _>
#            /

def like(col, v, prior):
  """How much a column likes a value."""
  if type(col) == Sym:
    return (col.has.get(v, 0) +
            the.bayes.k * prior) / (col.n + the.bayes.k)
  sd = col.sd + 1e-32; z = 2 * sd * sd
  return exp(-(v - col.mu)**2 / z) / sqrt(pi * z)

def likes(data, row, n_rows, n_klasses):
  """Log likelihood of row given data."""
  prior = (len(data.rows) + the.bayes.m
          ) / (n_rows + the.bayes.m * n_klasses)
  ls = [like(col, v, prior) for col in data.cols.xs
        if (v := row[col.at]) != "?"]
  return log(prior) + sum(log(v) for v in ls if v > 0)

#   _
#  /  ` ._   _   ._  _   ._  _    ._  ._    o ._  _
#  \_, |  | (_)  | | (_) | | (/_  |_) |  o  | | | (_|
#                                  |             _|

def picks(data, row, n=1):
  """Mutate n random x-columns."""
  s = row[:]
  for col in sample(data.cols.xs,
                    min(n, len(data.cols.xs))):
    s[col.at] = pick(col, s[col.at])
  return s

def pick(it, v=None):
  """Sample from distribution."""
  if Sym == type(it): return pick(it.has)
  if Num == type(it):
    tmp = v if v is not None and v != "?" else it.mu
    lo, hi = it.mu - 3*it.sd, it.mu + 3*it.sd
    new = tmp + it.sd * 2 * (rand() + rand() + rand() - 1.5)
    return lo + (new - lo) % (hi - lo + 1e-32)
  if dict == type(it):
    n = sum(it.values()) * rand()
    for k, v in it.items():
      if (n := n - v) <= 0: break
    return k

def extrapolate(cols, a, b, c, F=0.5):
  """DE blend over given cols: new = a + F*(b-c).
  Num: arithmetic clipped to mu+/-4sd. Sym: prob-F pick of b else a. ?: take a."""
  out = a[:]
  for col in cols:
    va, vb, vc = a[col.at], b[col.at], c[col.at]
    if va == "?":
      out[col.at] = "?"
    elif Num == type(col):
      if vb == "?" or vc == "?":
        out[col.at] = va
      else:
        v = va + F * (vb - vc)
        lo, hi = col.mu - 4*col.sd, col.mu + 4*col.sd
        out[col.at] = max(lo, min(hi, v))
    else:
      out[col.at] = vb if (vb != "?" and rand() < F) else va
  return out

#   _
#  |_   ._ _   _.  _|_
#  | |  (_) |  (_|   |_

def o(x):
  """Recursive format. Sorts dicts."""
  if isa(x, float):
    return f"{x:.{the.show.decimals}f}"
  if isa(x, dict):
    return "{" + ", ".join(f"{k}={o(v)}"
                           for k, v in sorted(x.items())) + "}"
  if isa(x, list):
    return "{" + ", ".join(map(o, x)) + "}"
  if isa(x, S): return "S" + o(x.__dict__)
  if hasattr(x, "__dict__"):
    return x.__class__.__name__ + o(x.__dict__)
  return str(x)

def table(lst, w=10):
  """Print list of dicts as aligned table."""
  if not lst: return
  ds = [x if type(x) is dict else x.__dict__ for x in lst]
  ks = list(ds[0].keys())
  print("".join(f"{str(k):>{w}}" for k in ks))
  print("-" * (len(ks) * w))
  for d in ds:
    print("".join(f"{str(d.get(k, '')):>{w}}" for k in ks))

def thing(txt):
  """Coerce string to number or bool."""
  def bool(s): return {"true": 1, "false": 0}.get(s.lower(), s)
  txt = txt.strip()
  for f in [int, float, bool]:
    try: return f(txt)
    except ValueError: pass

def nest(t, k, v):
  """Set value in nested namespace."""
  for x in (ks := k.split("."))[:-1]:
    t = t.__dict__.setdefault(x, S())
  setattr(t, ks[-1], v)

def csv(f, clean=lambda txt: txt.partition("#")[0].split(",")):
  """Yield typed rows from a CSV file."""
  with open(f, encoding="utf-8") as file:
    for txt in file:
      row = clean(txt)
      if any(x.strip() for x in row):
        yield [thing(x) for x in row]

#   _
#  |_)   _    _.   _|
#  | \  (/_  (_|  (_|  \/
#                      /

the = S()
for k, v in re.findall(r"([\w.]+)=(\S+)", __doc__):
  nest(the, k, thing(v))
