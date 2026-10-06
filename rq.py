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
           plot="", diff="", png="docs/rq.png", rq0=0,
           repeats=20, sd=0)

def wins(mod, tbl): # 100 at the best row, 0 at an average one
  ys = sorted(mod.ydist(tbl, r) for r in tbl.rows)
  lo, avg = ys[0], sum(ys) / len(ys)
  return lambda r: max(-100, min(100,
    100 * (1 - (mod.ydist(tbl, r) - lo) / (avg - lo + 1e-32))))

def rq0(): # per dataset: mean win of 20 repeats' picks.
  # read with:  | sort -n | fmt -60
  mod = importlib.import_module(the.alg)
  d = os.path.expanduser(the.dir)
  for f in ([d] if d.endswith(".csv") else
            sorted(glob.glob(d + "/**/*.csv", recursive=True))):
    t, w, ws = mod.Tbl(mod.csv(f)), None, []
    w = wins(mod, t)
    for i in range(the.repeats):
      mod.the.Seed = i; random.seed(i)
      ws += [w(mod.holdout(t))]
    print(f"{round(sum(ws)/len(ws))}:{os.path.basename(f)[:-4]}",
          flush=True)

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
    mod.the.Stop = B
    random.seed(s)
    got = mod.holdout(t)
    print(B, C, round(w(got)), flush=True)

def grid(file): # win mean and sd per (budget, check) cell, blurred
  import numpy as np
  rows = [ln.split() for ln in open(file) if ln[0].isdigit()]
  b, c, w = zip(*[[float(x) for x in r] for r in rows])
  rng = [[0, 200], [.5, 10.5]]
  hist = lambda ws: np.histogram2d(b, c, bins=(40,10), range=rng,
                                   weights=ws)[0]
  S, Q, N = hist(w), hist([x*x for x in w]), hist(None)
  g = np.exp(-(np.arange(-3, 4) ** 2) / 2.0); g /= g.sum()
  blur = lambda H: np.apply_along_axis(
    lambda v: np.convolve(v, g, "same"), 1,
    np.apply_along_axis(lambda v: np.convolve(v,g,"same"), 0, H))
  S, Q, N = blur(S), blur(Q), blur(N)
  mu = S / (N + 1e-32)
  return mu, np.sqrt(np.maximum(0, Q/(N+1e-32) - mu*mu)), N

def plot(): # one map, or (-diff) the gap between two maps
  import matplotlib.pyplot as plt
  from numpy import sqrt as np_sqrt
  mu, sd, n = grid(the.plot)
  H = {0: mu, 1: sd, 2: sd/np_sqrt(n)}[the.sd]
  if the.diff:
    mu, sd, n = grid(the.diff)
    H = H - {0: mu, 1: sd, 2: sd/np_sqrt(n)}[the.sd]
    hi = abs(H).max()
    plt.imshow(H.T, origin="lower", aspect="auto", cmap="coolwarm",
               vmin=-hi, vmax=hi, extent=(0, 200, .5, 10.5))
    plt.colorbar(label="ezr win")
  else:
    import numpy as np
    lvls = ([0,1,2,3,4,5,8,12] if the.sd==2 else
            [10,20,25,30,35,40,45,50] if the.sd else
            [40, 60, 70, 75, 80, 85, 90])
    xs = np.linspace(2.5, 197.5, 40)
    ys = np.linspace(1, 10, 10)
    cf = plt.contourf(xs, ys, H.T, levels=lvls, cmap="viridis")
    plt.contour(xs, ys, H.T, levels=lvls, colors="k",
                linewidths=.5)
    plt.colorbar(cf, label={0:"mean win",1:"sd win",2:"se win"}[the.sd])
  plt.xlabel("Budget"); plt.ylabel("Check")
  plt.savefig(the.png, dpi=120, bbox_inches="tight")
  print(the.png)

if __name__ == "__main__":
  if "-h" in sys.argv: print(__doc__); sys.exit()
  for _k, _v in zip(sys.argv[1:], sys.argv[2:]):
    if _k[1:] in the: the[_k[1:]] = atom(_v)
  plot() if the.plot else rq0() if the.rq0 else rq()
