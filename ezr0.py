#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0.py: one small corner of ezr.py -- buy a few labels, guess the best.
Every name below is ezr.py's, so this is a way in to reading that.
Where ezr.py picks its next label after every label, this spends the
whole budget at random, up front, then splits best from rest.

Options:
   -Budget=50   rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv
"""
import os, random, re, sys
from math import exp, sqrt

class o(dict): # a dict you can poke with a dot.
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__

def atom(s): # '22' -> 22.  'x' -> 'x'.
  try: return int(s)
  except ValueError:
    try: return float(s)
    except ValueError: return s.strip()

def csv(file): # rows of FILE, each cell coerced; -sig drops any BOM
  with open(os.path.expanduser(file), encoding="utf-8-sig") as f:
    return [[atom(s) for s in ln.split(",")] for ln in f if ln.strip()]

the = o(**{k: atom(v) for k, v in re.findall(r"-(\w+)=(\S+)", __doc__)})

#-- columns ----------------------------------------------------
def Col(txt, at): # uppercase name = NUM, else SYM
  return Num(txt, at) if txt[0].isupper() else Sym(txt, at)

def Num(txt, at): # +- marks a goal; 0 = minimise, 1 = maximise
  return o(at=at, txt=txt, n=0, mu=0, m2=0, sd=0,
           goal=0 if txt[-1] == "-" else 1)

def Sym(txt, at): # `has` is what tells a SYM from a NUM
  return o(at=at, txt=txt, n=0, has={})

def add(col, v): # show V to COL.  `?` changes nothing.
  if v != "?":
    col.n += 1
    if "has" in col: col.has[v] = col.has.get(v, 0) + 1
    else:
      d = v - col.mu                          # Welford
      col.mu += d / col.n
      col.m2 += d * (v - col.mu)
      col.sd  = 0 if col.n < 2 else (col.m2 / (col.n - 1))**.5

def mid(col): # middle: the mean, or the most common symbol
  return max(col.has, key=col.has.get) if "has" in col else col.mu

def mids(tbl): # every column's middle, keyed by column index
  return {at: mid(col) for at, col in tbl.cols.items()}

def norm(col, v): # to 0..1, by the logistic curve; syms do not scale
  if "has" in col: return v
  z = max(-3, min(3, (v - col.mu) / (1e-32 + col.sd)))
  return 1 / (1 + exp(-1.7 * z))

#-- tables -----------------------------------------------------
def Tbl(src): # header names the columns: X skip, +-! goal
  src = iter(src)
  tbl = Cols(o(rows=[], cols={}, x=[], y=[], names=next(src)))
  for row in src: addRow(tbl, row)
  return tbl

def Cols(tbl): # create column roles
  for at, s in enumerate(tbl.names):
    if s[-1] == "X": continue             # skip me entirely
    (tbl.y if s[-1] in "+-!" else tbl.x).append(
      tbl.cols.setdefault(at, Col(s, at)))
  return tbl

def addRow(tbl, row): # keep ROW, and show it to my columns
  tbl.rows += [row]
  for at, col in tbl.cols.items(): add(col, row[at])
  return row

def clone(tbl, rows): # an empty copy of TBL, plus ROWS
  return Tbl([tbl.names] + rows)

#-- distance ---------------------------------------------------
def minkowski(vs, n): # root mean square of N gaps
  return sqrt(sum(v*v for v in vs) / n)

def ydist(tbl, row): # how far ROW's goals are from the best they could be
  return minkowski((abs(norm(c,row[c.at])-c.goal) for c in tbl.y),
                   len(tbl.y))

def gap(col, a, b): # distance between two values of one column
  if a == "?" or b == "?": return 1       # unknown = far
  return a != b if "has" in col else abs(norm(col,a) - norm(col,b))

def xdist(tbl, r1, r2): # how far apart two rows are, over the x columns
  return minkowski((gap(c,r1[c.at],r2[c.at]) for c in tbl.x),len(tbl.x))

def holdout(tbl): # train on half, guess on the rest
  random.seed(the.Seed)
  rows = random.sample(tbl.rows, len(tbl.rows))
  half = len(rows)//2                       # 50/50, as in ezr.py
  n    = the.Budget - the.Check             # keep Check in hand
  lab  = clone(tbl, rows[:min(half, n)])    # y stats: labels only
  lab.rows.sort(key=lambda r: ydist(lab, r))
  k    = int(sqrt(len(lab.rows)))           # sqrt best, rest rest
  cb,cr = mids(clone(tbl,lab.rows[:k])), mids(clone(tbl,lab.rows[k:]))
  test = sorted(rows[half:], key=lambda z: xdist(tbl,z,cb)-xdist(tbl,z,cr))
  return min(test[:the.Check],key=lambda z: ydist(lab,z)), lab.rows[0]

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for k, v in zip(sys.argv[1:], sys.argv[2:]):
    if k[1:] in the: the[k[1:]] = atom(v)
  t = Tbl(csv(the.File))
  got, seen = holdout(t)
  print(f"labels={the.Budget}  picked={ydist(t,got):.3f}"
        f"  bestOfBudget={ydist(t,seen):.3f}")
