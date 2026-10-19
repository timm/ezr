#!/usr/bin/env python3 -B
"""pick.py: not "how wrong is the model" but "could you pick with it".

Rank the TEST rows by ezr's own ydist: 0% is the genuinely best row,
100% the worst.  ydist carries the goal direction, so a `!` or `+`
column counts big as good and a `-` column counts small as good --
and the model is read in that same direction.  Now sort those rows
by what a model PREDICTS, walk down that order ONE row at a time,
and after x rows ask: the best row I have turned up so far, what
was its true percentile?

A perfect model answers 0 after one row.  Picking at random answers
about 100/(x+1).  Everything else lands between, and small x is the
whole question: look at x rows off the model's shortlist, how good
is the best thing in them?

Nothing here touches training.  The model is fitted on the 80% train
half; the ranking, the truth and the curve are all the 20% test.

Set RAWY=1 to make a one-y tree split on the column itself instead
of on its ydist -- the experiment that asks whether regression
really needs the multi-objective machinery.

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
LEAF = os.environ.get("LEAF", "8")  # min rows in a leaf.  sqrt(n)
                                    # left only 12 distinct scores
                                    # for 190 test rows: the top of
                                    # the ranking was one big tie
TRUE_YDIST = E.ydist           # keep a handle: RAWY rebinds the name

if os.environ.get("RAWY"):     # EXPERIMENT: split a one-y tree on
  def _raw(tbl, row):          # the column itself, not on its ydist
    c = tbl.cols.y
    return row[c[0].at] if len(c) == 1 else TRUE_YDIST(tbl, row)
  E.ydist = _raw

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
  E.the.Leaf = max(2, int(sqrt(n)) if LEAF == "sqrt" else int(LEAF))
  tr   = E.clone(full, E.grabs(full, n))
  root = E.fit(E.tree(tr, tr.rows), *E.target(tr))
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
  _, Y = E.target(full)
  m = lgb.LGBMRegressor(verbose=-1, n_estimators=100)
  m.fit(X(full.rows), [Y(r) for r in full.rows],
        categorical_feature=[i for i,at in enumerate(xs) if at in cats])
  return list(m.predict(X(te.rows)))

def order(full, guess):
  """Best-first, in the goal's direction.  One y column that wants
  to be big is read descending; anything else ascending, since a
  ydist is already small-is-good."""
  c    = full.cols.y
  flip = len(c) == 1 and c[0].goal == 1
  return sorted(range(len(guess)),
                key=lambda i: -guess[i] if flip else guess[i])

def curve(truth, guess, most=100):
  """Walk the rows in GUESS order; after each ONE report the true
  percentile of the best row seen so far.  TRUTH is each row's own
  percentile, 0 = the best there is.  X counts ROWS, not a fraction
  of them, so curves from files of different size can be averaged."""
  out, best = [], 101.0
  for j in range(most):
    if j < len(guess): best = min(best, truth[guess[j]])
    out += [best]
  return out

def main(f):
  tot, secs = [0.0]*100, 0.0
  for s in range(SEEDS):
    full, te = split(f, s)
    bad   = [TRUE_YDIST(full, r) for r in te.rows]   # 0 = the best
    rank  = sorted(range(len(bad)), key=lambda i: bad[i])
    truth = [0.0]*len(bad)                 # 0% = the true best row
    for p, i in enumerate(rank): truth[i] = 100.0*p/(len(bad)-1 or 1)
    t0 = time.time()
    g  = (lgbm(full, te) if ARM == "lgbm" else
          [random.random() for _ in te.rows] if ARM == "rand" else
          ezr(full, te, int(ARM)))
    secs += time.time() - t0
    for i, v in enumerate(curve(truth, order(full, g))):
      tot[i] += v/SEEDS
  print("\t".join([os.path.basename(f)[:-4], str(len(te.rows)), ARM,
                   f"{secs/SEEDS:.5f}"] + [f"{v:.4f}" for v in tot]),
        flush=True)

if __name__ == "__main__":
  for p in sys.argv[1:]:
    try: main(p)
    except Exception as ex:
      print(f"SKIP\t{p}\t{type(ex).__name__}: {ex}", file=sys.stderr)
