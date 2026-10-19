#!/usr/bin/env python3 -B
"""fft.py: Chen et al.'s fast-and-frugal trees, asked of N classes.

One tree0, grown on a budget of random labels by entropy.  Then
every frugal collapse of it is scored on the TRAINING rows -- by
lookup, never by walking -- and the best one goes to test.  No
ensemble, no vote: Chen picks one tree and ships it.

Score is d2h: how far a model sits from (pd=100, pf=0), with pd
and pf weighted by class frequency.  Accuracy is reported too,
but it is not what chooses the tree.

  ARM=fft   python3 etc/fft.py FILE   # best collapse of tree0
  ARM=tree0 python3 etc/fft.py FILE   # the whole tree, no collapse
  ARM=lgbm  python3 etc/fft.py FILE   # LightGBM, every train row
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E

SEEDS = int(os.environ.get("SEEDS", 20))
ARM   = os.environ.get("ARM", "fft")
CAP   = int(os.environ.get("CAP", 512))
DEPTH = int(os.environ.get("DEPTH", 4))

def split(f, seed):
  "Train on 75%, test on the rest.  Rows with no class are out."
  random.seed(seed)
  t  = E.Tbl(E.csv(f))
  t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
  rs = random.sample(t.rows, len(t.rows)); n = int(.75*len(rs))
  return t, E.clone(t, rs[:n]), E.clone(t, rs[n:])

def grow(full):
  "tree0, on CAP random labels, with ~8 leaves per class in mind."
  n = min(CAP, len(full.rows))
  k = len({r[full.cols.klass.at] for r in full.rows})
  E.the.Leaf = max(2, n // (8*k))
  tr = E.clone(full, E.grabs(full, n))
  return E.fit(E.tree(tr, tr.rows, DEPTH), *E.target(tr)), n

def fft(full, te):
  """Of every collapse of tree0, the one the training rows like
  best.  `counts` reads each variant off the Y that `fit` left at
  the nodes, so shopping costs no row walks at all."""
  root, n = grow(full)
  best, least = None, 1e30
  for path in E.frugals(root, 2, DEPTH):
    if (d := E.d2h(E.tally(*E.counts(path)))) < least:
      best, least = path[:], d
  return ([E.fleaf(best, r).pred for r in te.rows], n,
          len(list(E.exits(best))))

def tree0(full, te):
  "The whole tree, nothing collapsed: what fft has to beat."
  root, n = grow(full)
  return ([E.leaf(root, r).pred for r in te.rows], n,
          len(E.leafs(root)))

def lgbm(full, te):
  "LightGBM on every training row."
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
  k = full.cols.klass.at
  m = lgb.LGBMClassifier(verbose=-1, n_estimators=100)
  m.fit(X(full.rows), [str(r[k]) for r in full.rows])
  return list(m.predict(X(te.rows))), len(full.rows), 0

def main(f):
  acc, d2h, secs, ns, ls = [], [], 0.0, [], []
  for s in range(SEEDS):
    t, full, te = split(f, s)
    k  = t.cols.klass.at
    t0 = time.time()
    g, n, nleaf = dict(fft=fft, tree0=tree0, lgbm=lgbm)[ARM](full, te)
    secs += time.time() - t0
    pairs = [(str(a), str(r[k])) for a, r in zip(g, te.rows)]
    acc  += [100*sum(a == b for a, b in pairs)/len(pairs)]
    d2h  += [E.d2h(E.abcd(pairs))]
    ns   += [n]; ls += [nleaf]
  out = [os.path.basename(f)[:-4], str(len(te.rows)),
         str(len(t.cols.x)), str(len({r[k] for r in t.rows})),
         ARM, f"{secs/SEEDS:.5f}", f"{S.median(ns):.0f}",
         f"{S.median(ls):.0f}"]
  if os.environ.get("RAW"):          # every seed, for a stats test
    for lab, v in (("acc", acc), ("d2h", d2h)):
      print("\t".join(out + [lab] + [f"{x:.4f}" for x in v]),
            flush=True)
  else:
    print("\t".join(out + [f"{S.median(acc):.4f}",
                           f"{S.median(d2h):.4f}"]), flush=True)

if __name__ == "__main__":
  for p in sys.argv[1:]:
    try: main(p)
    except Exception as ex:
      print(f"SKIP\t{p}\t{type(ex).__name__}: {ex}", file=sys.stderr)
