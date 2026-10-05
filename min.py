#!/usr/bin/env python3 -B
"""
min.py: eat rows, spit guesses.
(c) 2026 Tim Menzies <timm@ieee.org> MIT license.

Options:
   -Budget=50   rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=../src/ezr-lua/data/auto93.csv
"""
import random
from math import exp, sqrt
from types import SimpleNamespace as o

the = o(Budget=50, Check=5, Seed=1,
        File="../src/ezr-lua/data/auto93.csv")

def atom(s): # '22' -> 22.  'x' -> 'x'.
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return s.strip()

#-- 1. eat: rows off disc; mu,n,m2 per num, seen[v]+1 per sym ---
def Col(txt, at): # uppercase name = NUM, else SYM; +- = a goal
  return o(at=at, txt=txt, n=0, mu=0, m2=0, seen={},
           num=txt[0].isupper(), y=txt[-1] in "+-",
           goal=0 if txt[-1] == "-" else 1)

def add(col, v): # show V to COL
  if v != "?":
    col.n += 1
    if not col.num: col.seen[v] = col.seen.get(v, 0) + 1
    else:
      d = v - col.mu                             # Welford
      col.mu += d / col.n
      col.m2 += d * (v - col.mu)
  return v

def eat(file): # row 1 names the columns, the rest are data
  rows, cols = [], None
  for line in open(file):
    if not line.strip(): continue
    row = [atom(s) for s in line.split(",")]
    if cols is None: cols = [Col(s, at) for at, s in enumerate(row)]
    else: rows += [[add(c, row[c.at]) for c in cols]]
  return o(rows=rows, cols=cols, y=[c for c in cols if c.y],
           x=[c for c in cols if not c.y and c.txt[-1] != "X"])

#-- distance ---------------------------------------------------
def norm(col, v): # to 0..1, by the logistic curve; syms do not scale
  if not col.num or v == "?": return v
  sd = sqrt(col.m2 / (col.n - 1)) if col.n > 1 else 0
  return 1 / (1 + exp(-1.7 * max(-3, min(3, (v - col.mu)/(1e-32 + sd)))))

def gap(col, a, b): # one column's two values; unknown = far
  if a == "?" or b == "?": return 1
  return norm(col,a) - norm(col,b) if col.num else a != b

def rms(vs, n): # root mean square of N gaps (so no abs needed above)
  return sqrt(sum(v*v for v in vs) / n)

def ydist(d, row): # how far ROW's goals are from heaven; 0 = best
  return rms((norm(c, row[c.at]) - c.goal for c in d.y), len(d.y))

def xdist(d, r1, r2): # how far apart two rows are, over the x cols
  return rms((gap(c, r1[c.at], r2[c.at]) for c in d.x), len(d.x))

def mid(d, rows): # centroid: each column's mean, or its mode
  out = {}
  for col in d.cols:
    c = Col(col.txt, col.at)
    for row in rows: add(c, row[col.at])
    out[col.at] = c.mu if col.num else max(c.seen, key=c.seen.get)
  return out

#-- 2. spit: budget random labels, then rank what is left ------
def spit(d): # label BUDGET-CHECK rows, split best vs rest, rank the unseen
  random.seed(the.Seed)
  todo = random.sample(d.rows, len(d.rows))
  n    = the.Budget - the.Check                # keep Check in hand
  lab  = sorted(todo[:n], key=lambda r: ydist(d, r))
  todo = todo[n:]
  k    = int(sqrt(len(lab)))                   # sqrt best, rest rest
  b, r = mid(d, lab[:k]), mid(d, lab[k:])
  todo.sort(key=lambda z: xdist(d,z,b) - xdist(d,z,r))
  return min(todo[:the.Check], key=lambda z: ydist(d,z)), lab[0]

if __name__ == "__main__":
  d = eat(the.File)
  got, seen = spit(d)
  print(f"labels={the.Budget}  picked={ydist(d,got):.3f}"
        f"  bestOfBudget={ydist(d,seen):.3f}")
