#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
ezr1_eg.py: the rig that grades ezr1.py.  Nothing here is part of
the method: the judge reads labels the planner never sees.

Per seed: hold Judge rows out, split the rest 50:50, label a budget
from one half, plan Test rows from the other.  Judge = the nearest
held-out row (ezr0's distance, on raw cells); wins = 100 at the best
row, 0 at an average one.

Options:
   -Judge=64    rows held out for the judge, per seed
   -Test=100    holdout rows planned, per seed
   -Repeats=20  seeds

Usage: ./ezr1_eg.py [-Option value]...
"""
import random, sys
from math import log
import ezr1
from ezr1 import *

the.__dict__.update(vars(Settings(__doc__)))   # ezr1's options, plus mine

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
    nu  = plan(t, m, r)
    raw = [v if nu[at] == r.bins[at] else rebin(t.cols.all[at], nu[at])
           for at, v in enumerate(r.raw)]
    out += [(judge(r.raw), judge(raw), rawdist(t, r.raw, raw),
             sum(r.bins[c.at] != nu[c.at] for c in t.cols.x))]
  return out

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
  the.cli(sys.argv[1:])
  _t, _ss = load(csv(the.File)), []
  _w = wins(_t)
  for _s in range(1, the.Repeats + 1): _ss += one(_t, _w, _s)
  print(f"{the.File}  seeds={the.Repeats}  rows={len(_ss)}")
  report(_ss)
