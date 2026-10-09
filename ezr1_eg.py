#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr1_eg.py: the rig that grades ezr1.py.  Nothing here is part of
the method: the judge reads labels the planner never sees.

Per seed: hold Judge rows out, split the rest 50:50, label a budget
from one half, plan Test rows from the other.  Judge = the nearest
held-out row (ezr0's distance, on raw cells); wins = 100 at the best
row, 0 at an average one.

--holdout: as ezr0's holdout: train on half, sort the other half by
rank(), label the top Check, keep the best.  Prints the mean win
over Repeats seeds for ezr1, ezr0, ezr (same splits); then their
seconds (ezr0, ezr reload the table each seed); then FILE.

Options:
   -Judge=64    rows held out for the judge, per seed
   -Test=100    holdout rows planned, per seed
   -Repeats=20  seeds

Usage: ./ezr1_eg.py [-Option value]... [--holdout]
"""
import os, random, sys
from math import log
import ezr1
from ezr1 import *

ezr1.the = the = struct("The", **opts(ezr1.__doc__), **opts(__doc__))()

def wins(tbl): # grader: 100 at the pool's best row, 0 at an average one
  ys = sorted(ydist(tbl, r) for r in tbl.rows)
  lo, avg = ys[0], sum(ys) / len(ys)
  return lambda row: max(-100, min(100,
                     100 * (1 - (ydist(tbl,row)-lo) / (avg-lo+1e-32))))

def unbin(col, b): # a bin's centre, back in raw units
  p = (round(b * the.Bins) + .5) / the.Bins
  z = max(-3, min(3, log(p / (1 - p)) / 1.7))
  return col.mu + z * col.sd

def rebin(col, b): # a changed bin, back to a raw cell
  if type(col) is Num: return unbin(col, b)
  return next(k for k in col.has if str(k) == b)

def rawdist(t, a, b): # ezr0's xdist, on raw cells: the judge's ruler
  def g(c, u, v):
    if u == "?" or v == "?": return 1
    return abs(norm(c,u) - norm(c,v)) if type(c) is Num else u != v
  return dist((g(c, a[c.at], b[c.at]) for c in t.cols.x), len(t.cols.x))

def one(t, w, seed): # (win0, win1, dx, k) per planned row
  random.seed(seed)
  rows = random.sample(t.rows, len(t.rows))
  pool, rows = rows[:the.Judge], rows[the.Judge:]
  n     = len(rows) // 2
  m     = model(t, rows[:n])
  judge = lambda raw: w(min(pool, key=lambda z: rawdist(t, raw, z.raw)))
  out   = []
  for r in rows[n:][:the.Test]:
    nu  = plan(m, r)
    raw = [v if nu[at] == r.bins[at] else rebin(t.cols.all[at], nu[at])
           for at, v in enumerate(r.raw)]
    out += [(judge(r.raw), judge(raw), rawdist(t, r.raw, raw),
             sum(r.bins[c.at] != nu[c.at] for c in t.cols.x))]
  return out

def holdout(t, w, seed): # win of the best of Check labels, ranked by rules
  random.seed(seed)
  rows = random.sample(t.rows, len(t.rows))
  m    = model(t, rows[:len(rows)//2])
  test = sorted(rows[len(rows)//2:], key=rank(m))
  return w(min(test[:the.Check], key=lambda z: ydist(m.lab, z)))

def holdout0(f, seed): # ezr0's holdout, on the same split
  import ezr0
  ezr0.the.Seed, ezr0.the.File = seed, f
  t0 = ezr0.Tbl(ezr0.csv(f))
  return ezr0.wins(t0)(ezr0.holdout(t0))

def holdoutE(f, seed): # ezr.py's holdout (acquire + tree), same budget
  import ezr as E
  random.seed(seed)
  t = E.Tbl(E.csv(f))
  return E.wins(t)(E.holdout(t))

def report(ss): # ss: (win0, win1, dx, k) per planned row
  med = lambda xs: sorted(xs)[len(xs)//2]
  w0, w1, dx, k = zip(*ss)
  gain = [b - a for a, b in zip(w0, w1)]
  f   = lambda a: f"{sum(a)/len(a):7.1f}{med(a):6.1f}"
  g   = lambda a: f"{sum(a)/len(a):7.3f}{med(a):6.3f}"
  print(f"{'':6}{'win0':>13}{'win1':>13}{'gain':>13}{'dx':>13}"
        f"{'k':>6}{'gain/k':>8}{'cover':>7}   (mean, median)")
  print(f"{'bins':6}{f(w0)}{f(w1)}{f(gain)}{g(dx)}{sum(k)/len(k):6.2f}"
        f"{sum(gain)/(sum(k)+1e-32):8.1f}{sum(x > 0 for x in k)/len(k):7.0%}")

if __name__ == "__main__":
  if "-h" in sys.argv: print(ezr1.__doc__, __doc__); sys.exit()
  cli(the, sys.argv[1:])
  _t, _ss = load(csv(the.File)), []
  _w = wins(_t)
  if "--holdout" in sys.argv:
    import time
    _out = []
    for _f in (lambda s: holdout(_t, _w, s), lambda s: holdout0(the.File, s),
               lambda s: holdoutE(the.File, s)):
      _t0 = time.perf_counter()
      _ws = [_f(s) for s in range(1, the.Repeats + 1)]
      _out += [(sum(_ws) / len(_ws), time.perf_counter() - _t0)]
    print(*[f"{w:.0f}" for w, _ in _out], *[f"{t:.2f}" for _, t in _out],
          os.path.basename(the.File)); sys.exit()
  for _s in range(1, the.Repeats + 1): _ss += one(_t, _w, _s)
  print(f"{the.File}  seeds={the.Repeats}  rows={len(_ss)}")
  report(_ss)
