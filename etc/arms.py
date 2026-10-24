#!/usr/bin/env python3 -B
"""arms.py: one arm of the comparison, so each picks its own python.

LightGBM is a C extension and will not import on pypy, so the three
arms cannot share a process.  They share a SEED instead: CPython and
pypy both run the Mersenne Twister, so random.seed(s) deals the same
rows to both, and the two ezr columns can be checked against each
other -- if the errors do not match, the pairing is broken.

That LightGBM cannot be moved to another runtime, while ezr needs no
porting at all, is a result and not an inconvenience.

  ARM=ezr  python3 etc/arms.py FILE     # ezr, CPython
  ARM=ezr  pypy3   etc/arms.py FILE     # ezr, pypy
  ARM=lgbm python3 etc/arms.py FILE     # LightGBM, CPython only
"""
import os, sys, time, random
from math import sqrt
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E

SEEDS, CAP = 20, 256
ARM = os.environ.get("ARM", "ezr")
WHO = ARM if ARM == "lgbm" else (
      "ezr-pypy" if hasattr(sys, "pypy_version_info") else "ezr-cpy")

def split(f, seed):
  "The one split every arm is judged on."
  random.seed(seed)
  t  = E.Tbl(E.csv(f))
  t  = E.clone(t, [r for r in t.rows          # a row with no target
                   if all(r[c.at] != "?" for c in t.cols.y)])
  rs = random.sample(t.rows, len(t.rows))     # cannot score anyone
  n  = int(.8 * len(rs))
  return t, E.clone(t, rs[:n]), E.clone(t, rs[n:])

def scale(tr, rows):
  "Test y, and what to divide its errors by.  Train's columns."
  _, Y = E.target(tr); vs = [Y(r) for r in rows]
  return Y, sum(vs)/len(vs) - min(vs) + 1E-32

def ezr(full, te):
  "n=min(CAP,|train|) random rows, a tree of about sqrt(n) leaves."
  n = min(CAP, len(full.rows))
  t0 = time.time()
  E.the.Leaf = max(2, int(sqrt(n)))
  tr   = E.clone(full, E.grabs(full, n))
  root = E.fit(E.tree(tr, tr.rows), *E.target(tr))
  secs = time.time() - t0
  Y, d = scale(full, te.rows)
  return (sum(abs(Y(r) - E.leaf(root,r).pred)
              for r in te.rows)/len(te.rows)/d, secs, n)

def lgbm_pred(full, te):
  "What LightGBM predicts for each test row, and what it cost."
  import numpy as np, lightgbm as lgb     # pylint: disable=C0415
  xs   = [c.at for c in full.cols.x]
  cats = {at: {v: i for i, v in enumerate(sorted(
                 {r[at] for r in full.rows if type(r[at]) is str
                  and r[at] != "?"}))}
          for at in xs if type(full.cols.all[at]) is E.Sym}
  X = lambda rows: np.array(
    [[cats[at].get(r[at], np.nan) if at in cats else
      (np.nan if r[at] == "?" else r[at]) for at in xs]
     for r in rows], dtype=float)
  _, Ytr = E.target(full)
  m  = lgb.LGBMRegressor(verbose=-1, n_estimators=100)
  m.fit(X(full.rows), [Ytr(r) for r in full.rows],
        categorical_feature=[i for i,at in enumerate(xs) if at in cats])
  return m.predict(X(te.rows))

def lgbm(full, te):
  "Every training row, LightGBM's defaults."
  t0 = time.time(); p = lgbm_pred(full, te); secs = time.time()-t0
  Y, d = scale(full, te.rows)
  return (sum(abs(Y(r) - v) for r, v in zip(te.rows, p))
          /len(te.rows)/d, secs, len(full.rows))

def main(f):
  es, ss, ns = [], [], []
  for s in range(SEEDS):
    t, full, te = split(f, s)
    e, sec, n = (lgbm if ARM == "lgbm" else ezr)(full, te)
    es += [e]; ss += [sec]; ns += [n]
  pre = [os.path.basename(f)[:-4], str(len(t.rows)), str(len(te.rows)),
         str(len(t.cols.x)), str(len(t.cols.y)), WHO]
  for k, v in (("err", es), ("secs", ss), ("n", ns)):
    print("\t".join(pre + [k] + [f"{x:.6f}" for x in v]), flush=True)

if __name__ == "__main__":
  for path in sys.argv[1:]:
    try: main(path)
    except Exception as ex:                  # a file nothing can read
      print(f"SKIP\t{path}\t{type(ex).__name__}: {ex}", file=sys.stderr)
