#!/usr/bin/env python3 -B
"""pick.py: not "how wrong is the model" but "could you pick with it".

Sort the test rows by their TRUE y and number them 0..100% -- 0% is
the genuinely best row.  Now sort those same rows by what a model
PREDICTS, walk down that order, and after each 1% ask: the best row
I have turned up so far, what was its true percentile?

A perfect model answers 0 immediately.  Picking at random answers
about 100/(k+1) after k rows.  Everything else lands between, and
the gap at small x is the whole question: spend 1% of your labels
on the model's shortlist, how good is the best thing in it?

  ARM=lgbm python3 etc/pick.py FILE     # LightGBM, every train row
  ARM=256  python3 etc/pick.py FILE     # ezr tree,  256 labels
  ARM=50   python3 etc/pick.py FILE     # ezr tree,   50 labels
  ARM=rand python3 etc/pick.py FILE     # no model at all
"""
import os, sys, time, random
from math import sqrt
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E

SEEDS, ARM = 20, os.environ.get("ARM", "256")

def split(f, seed):
  random.seed(seed)
  t  = E.Tbl(E.csv(f))
  t  = E.clone(t, [r for r in t.rows
                   if all(r[c.at] != "?" for c in t.cols.y)])
  rs = random.sample(t.rows, len(t.rows)); n = int(.8*len(rs))
  return E.clone(t, rs[:n]), E.clone(t, rs[n:])

def ezr(full, te, cap):
  "A tree on CAP random labels; score every test row with it."
  n = min(cap, len(full.rows))
  E.the.Leaf = max(2, int(sqrt(n)))
  tr   = E.clone(full, E.grabs(full, n))
  root = E.fit(E.tree(tr, tr.rows), E.ys(tr))
  return [E.leaf(root, r).pred for r in te.rows]

def lgbm(full, te):
  "LightGBM on every training row; score every test row with it."
  import numpy as np, lightgbm as lgb
  xs   = [c.at for c in full.cols.x]
  cats = {at: {v: i for i, v in enumerate(sorted(
                 {r[at] for r in full.rows if type(r[at]) is str
                  and r[at] != "?"}))}
          for at in xs if type(full.cols.all[at]) is E.Sym}
  X = lambda rows: np.array(
    [[cats[at].get(r[at], np.nan) if at in cats else
      (np.nan if r[at] == "?" else r[at]) for at in xs]
     for r in rows], dtype=float)
  Y = E.ys(full)
  m = lgb.LGBMRegressor(verbose=-1, n_estimators=100)
  m.fit(X(full.rows), [Y(r) for r in full.rows],
        categorical_feature=[i for i,at in enumerate(xs) if at in cats])
  return list(m.predict(X(te.rows)))

def curve(truth, guess, most=100):
  """Walk the rows in GUESS order; after each ONE report the true
  percentile of the best row seen so far.  TRUTH is each row's own
  percentile, 0 = the best there is.  X counts ROWS, not a fraction
  of them, so curves from files of different size can be averaged."""
  order = sorted(range(len(truth)), key=lambda i: guess[i])
  out, best = [], 101.0
  for j in range(most):
    if j < len(order): best = min(best, truth[order[j]])
    out += [best]
  return out

def main(f):
  tot, secs = [0.0]*100, 0.0
  for s in range(SEEDS):
    full, te = split(f, s)
    Y  = E.ys(full)
    ys = [Y(r) for r in te.rows]
    rank  = sorted(range(len(ys)), key=lambda i: ys[i])
    truth = [0.0]*len(ys)                  # 0% = the true best row
    for p, i in enumerate(rank): truth[i] = 100.0*p/(len(ys)-1 or 1)
    t0 = time.time()
    g  = (lgbm(full, te) if ARM == "lgbm" else
          [random.random() for _ in ys] if ARM == "rand" else
          ezr(full, te, int(ARM)))
    secs += time.time() - t0
    for i, v in enumerate(curve(truth, g)): tot[i] += v/SEEDS
  print("\t".join([os.path.basename(f)[:-4], str(len(te.rows)), ARM,
                   f"{secs/SEEDS:.5f}"] + [f"{v:.4f}" for v in tot]),
        flush=True)

if __name__ == "__main__":
  for p in sys.argv[1:]:
    try: main(p)
    except Exception as ex:
      print(f"SKIP\t{p}\t{type(ex).__name__}: {ex}", file=sys.stderr)
