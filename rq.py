#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
rq.py: research questions for ezr -- how much does a budget buy?
Runs an algorithm's holdout many times; each run draws a random
dataset, Budget, and Check; prints one "budget check win" line
(win: 100 = found the best row, 0 = no better than average).
The draw stream depends only on Seed, never on alg, so runs with
-alg ezr0 and -alg ezr are paired. Fast runs: pypy3.12.
Plots (need matplotlib, so CPython):
  python3 rq.py -plot rq0.txt                  one heat map
  python3 rq.py -plot rq1.txt -diff rq0.txt    difference map

Options:
   -alg=ezr0                    ezr0 or ezr
   -runs=1000                   experiments to run
   -dir=~/gits/moot/optimize    where the csv files live
   -plot=                       file of saved lines to draw
   -diff=                       subtract this file's map
   -png=docs/rq.png              where to draw
"""
import os, sys, glob, random, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ezr0 import the, atom

the.update(alg="ezr0", runs=1000, dir="~/gits/moot/optimize",
           plot="", diff="", png="docs/rq.png")

def wins(mod, tbl): # 100 at the best row, 0 at an average one
  ys = sorted(mod.ydist(tbl, r) for r in tbl.rows)
  lo, avg = ys[0], sum(ys) / len(ys)
  return lambda r: max(-100, min(100,
    100 * (1 - (mod.ydist(tbl, r) - lo) / (avg - lo + 1e-32))))

def rq(): # many random holdouts; one "budget check win" line each
  mod   = importlib.import_module(the.alg)
  files = glob.glob(os.path.expanduser(the.dir) + "/**/*.csv",
                    recursive=True)
  R, tbls = random.Random(the.Seed), {}
  print("budget check win")
  for _ in range(the.runs):
    f = R.choice(files)
    if f not in tbls:
      t = mod.Tbl(mod.csv(f)); tbls[f] = (t, wins(mod, t))
    t, w = tbls[f]
    B, C, s = R.randint(10, 200), R.randint(1, 10), R.getrandbits(30)
    mod.the.Check, mod.the.Seed = C, s
    mod.the["Budget" if "Budget" in mod.the else "Stop"] = B
    random.seed(s)
    got = mod.holdout(t)
    if isinstance(got, tuple): got = got[0]
    print(B, C, round(w(got)), flush=True)

def grid(file): # mean win over (budget, check), gaussian blurred
  import numpy as np
  rows = [ln.split() for ln in open(file) if ln[0].isdigit()]
  b, c, w = zip(*[[float(x) for x in r] for r in rows])
  rng = [[0, 200], [.5, 10.5]]
  S,_,_ = np.histogram2d(b, c, bins=(40,10), range=rng, weights=w)
  N,_,_ = np.histogram2d(b, c, bins=(40,10), range=rng)
  g = np.exp(-(np.arange(-3, 4) ** 2) / 2.0); g /= g.sum()
  for ax in (0, 1):
    S = np.apply_along_axis(lambda v: np.convolve(v,g,"same"), ax, S)
    N = np.apply_along_axis(lambda v: np.convolve(v,g,"same"), ax, N)
  return S / (N + 1e-32)

def plot(): # one map, or (-diff) the gap between two maps
  import matplotlib.pyplot as plt
  H = grid(the.plot)
  if the.diff:
    H = H - grid(the.diff)
    hi = abs(H).max()
    plt.imshow(H.T, origin="lower", aspect="auto", cmap="coolwarm",
               vmin=-hi, vmax=hi, extent=(0, 200, .5, 10.5))
    plt.colorbar(label="ezr win")
  else:
    import numpy as np
    lvls = [40, 60, 70, 75, 80, 85, 90]
    xs = np.linspace(2.5, 197.5, 40)
    ys = np.linspace(1, 10, 10)
    cf = plt.contourf(xs, ys, H.T, levels=lvls, cmap="viridis")
    plt.contour(xs, ys, H.T, levels=lvls, colors="k",
                linewidths=.5)
    plt.colorbar(cf, label="mean win")
  plt.xlabel("Budget"); plt.ylabel("Check")
  plt.savefig(the.png, dpi=120, bbox_inches="tight")
  print(the.png)

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  plot() if the.plot else rq()
