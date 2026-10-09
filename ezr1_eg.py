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
seconds (tables loaded once, outside the timing); then FILE.

Options:
   -Judge=64    rows held out for the judge, per seed
   -Test=100    holdout rows planned, per seed
   -Repeats=20  seeds

--budget: that holdout at Stop = 20, 50, 100.  Per Stop, prints the
mean wins (ezr1 ezr0 ezr), a mark each (! = best or tied with it,
by ezr.same over the Repeats seeds), their seconds, then FILE.

--predict: Spearman correlation of guessed and true ydist over Test
held-out rows, for stack, bands, tree (ezr's leaf means), knn1; mean
over Repeats seeds, ! = best or tied by ezr.same; then FILE.

Usage: ./ezr1_eg.py [-Option value]... [--holdout|--budget|--predict]
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

def holdout0(t0, w0, seed): # ezr0's holdout, on the same split
  import ezr0
  ezr0.the.Seed = seed
  return w0(ezr0.holdout(t0))

def holdoutE(tE, wE, seed): # ezr.py's holdout (acquire + tree), same budget
  import ezr as E
  random.seed(seed)
  return wE(E.holdout(tE))

def spearman(xs, ys): # rank correlation; ties get their mean rank
  def rk(v):
    o, r = sorted(range(len(v)), key=v.__getitem__), [0]*len(v)
    i = 0
    while i < len(o):
      j = i
      while j + 1 < len(o) and v[o[j+1]] == v[o[i]]: j += 1
      for q in range(i, j + 1): r[o[q]] = (i + j) / 2
      i = j + 1
    return r
  a, b = rk(xs), rk(ys); n = len(a); ma, mb = sum(a)/n, sum(b)/n
  num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
  den = (sum((p-ma)**2 for p in a) * sum((q-mb)**2 for q in b)) ** .5
  return num / den if den else 0

def preds(t, seed): # spearman(guess, true ydist) per predictor
  import ezr as E
  random.seed(seed)
  rows = random.sample(t.rows, len(t.rows))
  n    = len(rows) // 2
  m    = model(t, rows[:n])
  test = rows[n:][:the.Test]
  lab0 = E.clone(E.Tbl([t.cols.names]), [z.raw for z in m.lab.rows])
  tree = E.ranker(lab0)
  ys   = {id(z): ydist(m.lab, z) for z in m.lab.rows}
  knn  = lambda r: ys[id(min(m.lab.rows, key=lambda z: sum(
           g2(r.bins[c.at], z.bins[c.at]) for c in t.cols.x)))]
  truth = [ydist(t, r) for r in test]
  out   = {}
  for k, f in (("stack", predict(m)), ("bands", bands(m)),
               ("tree", lambda r: tree(r.raw)), ("knn1", knn)):
    out[k] = spearman([f(r) for r in test], truth)
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
  cli(the, sys.argv[1:])
  _t, _ss = load(csv(the.File)), []
  _w = wins(_t)
  if "--holdout" in sys.argv:
    import time, ezr0, ezr as E
    _t0, _tE = ezr0.Tbl(ezr0.csv(the.File)), E.Tbl(E.csv(the.File))
    _w0, _wE = ezr0.wins(_t0), E.wins(_tE)
    _out = []
    for _f in (lambda s: holdout(_t, _w, s), lambda s: holdout0(_t0, _w0, s),
               lambda s: holdoutE(_tE, _wE, s)):
      _clk = time.perf_counter()
      _ws = [_f(s) for s in range(1, the.Repeats + 1)]
      _out += [(sum(_ws) / len(_ws), time.perf_counter() - _clk)]
    print(*[f"{w:.0f}" for w, _ in _out], *[f"{t:.2f}" for _, t in _out],
          os.path.basename(the.File)); sys.exit()
  if "--predict" in sys.argv:       # spearman(guess, truth), Repeats seeds
    import ezr as E
    _r = {}
    for _s in range(1, the.Repeats + 1):
      for _k, _v in preds(_t, _s).items(): _r.setdefault(_k, []).append(_v)
    _mu  = {k: sum(v) / len(v) for k, v in _r.items()}
    _top = max(_mu, key=_mu.get)
    print(*[f"{_mu[k]:.2f}{'!' if k == _top or E.same(_r[k], _r[_top]) else '.'}"
            for k in _r], os.path.basename(the.File)); sys.exit()
  if "--budget" in sys.argv:        # holdout at Stop = 20, 50, 100
    import time, ezr0, ezr as E
    _t0, _tE = ezr0.Tbl(ezr0.csv(the.File)), E.Tbl(E.csv(the.File))
    _w0, _wE = ezr0.wins(_t0), E.wins(_tE)
    for _stop in (20, 50, 100):
      the.Stop = ezr0.the.Stop = E.the.Stop = _stop
      _ws, _secs = [], []
      for _f in (lambda s: holdout(_t, _w, s),
                 lambda s: holdout0(_t0, _w0, s),
                 lambda s: holdoutE(_tE, _wE, s)):
        _clk = time.perf_counter()
        _ws  += [[_f(s) for s in range(1, the.Repeats + 1)]]
        _secs += [time.perf_counter() - _clk]
      _mu  = [sum(w) / len(w) for w in _ws]
      _top = _ws[max(range(3), key=lambda i: _mu[i])]
      _bang = ["!" if w is _top or E.same(w, _top) else "." for w in _ws]
      print(_stop, *[f"{m:.1f}" for m in _mu], "".join(_bang),
            *[f"{x:.2f}" for x in _secs], os.path.basename(the.File))
    sys.exit()
  for _s in range(1, the.Repeats + 1): _ss += one(_t, _w, _s)
  print(f"{the.File}  seeds={the.Repeats}  rows={len(_ss)}")
  report(_ss)
