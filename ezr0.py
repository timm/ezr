#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr0.py: one small corner of ezr.py -- buy a few labels, guess the best.
Every name below is ezr.py's, so this is a way in to reading that.
Where ezr.py picks its next label after every label, this spends the
whole budget at random, up front, then splits best from rest.

Options:
   -Cut=10      plan: ignore gaps under this % of the biggest
   -decimals=2  explain: digits shown after the point
   -Stop=50     rows we may label, all up
   -Check=5     of that budget, saved for the unseen rows
   -Seed=1      random number seed
   -File=~/gits/moot/optimize/misc/auto93.csv
"""
import os, random, re, sys
from math import exp, sqrt

class o(dict): # a dict you can poke with a dot.
  __getattr__, __setattr__ = dict.__getitem__, dict.__setitem__

def atom(s): # '22' -> 22. '3.1' -> 3.1. 'True' -> True. 'x' -> 'x'.
  for fn in (int, float):
    try: return fn(s)
    except ValueError: pass
  s = s.strip()
  return {"True": True, "False": False}.get(s, s)

def csv(file): # rows of FILE, one at a time; -sig drops any BOM
  with open(os.path.expanduser(file), encoding="utf-8-sig") as f:
    for ln in f:
      if ln.strip(): yield [atom(s) for s in ln.split(",")]

the = o(**{k: atom(v) for k, v in re.findall(r"-(\w+)=(\S+)", __doc__)})

#-- columns ----------------------------------------------------
def Col(txt=" ", at=0): # uppercase name = NUM, else SYM
  return Num(txt, at) if txt[0].isupper() else Sym(txt, at)

def Num(txt=" ", at=0): # +- marks a goal; 0 = minimise, 1 = maximise
  return o(at=at, txt=txt, n=0, mu=0, m2=0, sd=0,
           goal=0 if txt[-1] == "-" else 1)

def Sym(txt=" ", at=0): # `has` is what tells a SYM from a NUM
  return o(at=at, txt=txt, n=0, has={})

def add(col, v, inc=1): # show V to COL; INC=-1 takes it away
  if v != "?":
    col.n += inc
    if "has" in col: col.has[v] = col.has.get(v, 0) + inc
    else:
      d = v - col.mu                          # Welford
      col.mu += inc * d / max(1, col.n)
      col.m2  = max(0, col.m2 + inc * d * (v - col.mu))
      col.sd  = 0 if col.n < 2 else (col.m2 / (col.n - 1))**.5

def mid(col): # middle: the mean, or the most common symbol; ? if none
  return (max(col.has, key=col.has.get) if col.has else "?"
          ) if "has" in col else col.mu

def mids(tbl): # every column's middle, cached until the next addRow
  tbl.mids = tbl.mids or {at: mid(c) for at, c in tbl.cols.items()}
  return tbl.mids

def norm(col, v): # to 0..1, by the logistic curve; syms do not scale
  if "has" in col: return v
  z = max(-3, min(3, (v - col.mu) / (1e-32 + col.sd)))
  return 1 / (1 + exp(-1.7 * z))

#-- tables -----------------------------------------------------
def Tbl(src): # header names the columns: X skip, +-! goal
  src = iter(src)
  tbl = Cols(o(rows=[], cols={}, x=[], y=[], mids=None, names=next(src)))
  for row in src: addRow(tbl, row)
  return tbl

def Cols(tbl): # create column roles
  for at, s in enumerate(tbl.names):
    if s[-1] == "X": continue             # skip me entirely
    (tbl.y if s[-1] in "+-!" else tbl.x).append(
      tbl.cols.setdefault(at, Col(s, at)))
  return tbl

def addRow(tbl, row): # keep ROW, and show it to my columns
  tbl.mids = None                 # a new row moves the middles
  tbl.rows += [row]
  for at, col in tbl.cols.items(): add(col, row[at])
  return row

def clone(tbl, rows=None): # an empty copy of TBL, plus ROWS
  return Tbl([tbl.names] + (rows or []))

#-- distance ---------------------------------------------------
def dist(vs, n): return sqrt(sum(v*v for v in vs) / n) # distance

def ydist(tbl, row): # how far ROW's goals are from the best they could be
  return dist((abs(norm(c,row[c.at])-c.goal) for c in tbl.y), len(tbl.y))

def wins(tbl): # grader: 100 at the pool's best row, 0 at an average one.
  ys = sorted(ydist(tbl, r) for r in tbl.rows)   # peeks at every label,
  lo, avg = ys[0], sum(ys) / len(ys)             # so only reports use it
  return lambda row: max(-100, min(100,
                     100 * (1 - (ydist(tbl,row)-lo) / (avg-lo+1e-32))))

def gap(col, a, b): # distance between two values of one column
  if a == "?" or b == "?": return 1       # unknown = far
  return a != b if "has" in col else abs(norm(col,a) - norm(col,b))

def xdist(tbl, r1, r2): # how far apart two rows are, over the x columns
  return dist((gap(c,r1[c.at],r2[c.at]) for c in tbl.x),len(tbl.x))

#-- inference ----------------------------------------------------
def oracle(row): return row # labeller: does nothing if already labelled.

def model(tbl, rows, label=oracle): # return something that can rank rows
  lab = clone(tbl, [label(r) for r in rows[:the.Stop - the.Check]])
  lab.rows.sort(key=lambda r: ydist(lab, r))
  k    = int(sqrt(len(lab.rows)))          # sqrt best, rest rest
  best = clone(tbl, lab.rows[:k])
  rest = clone(tbl, lab.rows[k:])
  return o(key=lambda z: (xdist(tbl, z, mids(best)) -
                          xdist(tbl, z, mids(rest))),
           best=best, rest=rest, lab=lab)

def holdout(tbl, label=oracle): # train on half, guess on the rest
  random.seed(the.Seed)
  rows = random.sample(tbl.rows, len(tbl.rows))
  m    = model(tbl, rows[:len(rows)//2], label)
  test = sorted(rows[len(rows)//2:], key=m.key)
  return min(test[:the.Check], key=lambda z: ydist(m.lab, label(z)))

def say(v): # numbers get `decimals` digits; everything else, as is
  return (f"{round(v, the.decimals):g}"
          if isinstance(v, (int, float)) else str(v))

def explain(tbl, m): # the model is two centroids; show their gap
  print(f"{'power':>6}{'best':>10}{'rest':>10}  attribute")
  cb, cr = mids(m.best), mids(m.rest)
  d = lambda c: gap(c, cb[c.at], cr[c.at])
  for col in sorted(tbl.x, key=lambda c: -d(c)):
    print(f"{int(100*d(col)):>5}{say(cb[col.at]):>10}"
          f"{say(cr[col.at]):>10}  {col.txt}")

#-- plan -------------------------------------------------------
def gaps(tbl, m): # x columns, widest best-to-rest gap first
  cb, cr = mids(m.best), mids(m.rest)
  out = [(gap(c, cb[c.at], cr[c.at]), c.at, cb[c.at]) for c in tbl.x]
  return sorted(out, key=lambda z: -z[0])

def worth(tbl, m): # ... and the stop rule: keep the big gaps only
  out = gaps(tbl, m)
  return [z for z in out if z[0] >= the.Cut/100 * out[0][0]]

def plan(tbl, m, row): # walk ROW toward best; a labelled row witnesses each step
  now, out, sofar, w0 = row[:], [], [], None
  for _, at, v in worth(tbl, m):
    now[at] = v                             # changes ACCUMULATE
    sofar += [f"{tbl.names[at]}:{say(row[at])}->{say(v)}"]
    w = min(m.lab.rows, key=lambda z: xdist(tbl, now, z))
    out += [o(steps=list(sofar), witness=w, dx=xdist(tbl, now, w),
              paid=w is not w0)]            # a new witness costs a label
    w0 = w
  return out

#-- cli, main ----------------------------------------------------
# One line out: what the budget bought.  The rigs that grade it
# live next door, in ezr0_eg.py.
if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):   # _ : no leaks
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  t = Tbl(csv(the.File))
  random.seed(the.Seed)
  rows = random.sample(t.rows, len(t.rows))
  m    = model(t, rows[:len(rows)//2])
  got  = min(sorted(rows[len(rows)//2:], key=m.key)[:the.Check],
             key=lambda z: ydist(m.lab, z))
  w    = wins(t)                              # 100 = best row, 0 = average
  print(f"labels={the.Stop}  picked={ydist(t,got):.{the.decimals}f}"
        f" (win {w(got):.0f})"
        f"  bestOfBudget={ydist(t,m.lab.rows[0]):.{the.decimals}f}"
        f" (win {w(m.lab.rows[0]):.0f})")
