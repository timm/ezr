#!/usr/bin/env python3 -B
"""clas.py: the same question as pick.py, asked of classification.

An ezr tree on a budget of random labels, against LightGBM given
the whole training half.  Score is accuracy on the held-out 20%,
plus the macro pd (mean recall over the classes) -- accuracy alone
flatters anything that learns only the majority class.

Nothing here touches training.  The tree is grown on the budget;
every number comes off the test half.

  ARM=lgbm python3 etc/clas.py FILE     # LightGBM, every train row
  ARM=256  python3 etc/clas.py FILE     # ezr tree, 256 labels
  ARM=50   python3 etc/clas.py FILE     # ezr tree,  50 labels
  ARM=rf   python3 etc/clas.py FILE     # 20 ezr trees, 512 labels
  ARM=zeroR python3 etc/clas.py FILE    # always the majority class
"""
import os, sys, time, random, statistics as S
from collections import Counter
from math import sqrt
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E

SEEDS = 20
ARM   = os.environ.get("ARM", "256")
LEAF  = os.environ.get("LEAF", "auto")

def split(f, seed):
  random.seed(seed)
  t  = E.Tbl(E.csv(f))
  t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
  rs = random.sample(t.rows, len(t.rows)); n = int(.8*len(rs))
  return t, E.clone(t, rs[:n]), E.clone(t, rs[n:])

def ezr(full, te, cap):
  """A tree on CAP random labels; one guess per test row.  `auto`
  aims at eight leaves per class: too few and a class has nowhere
  to live, too many and each leaf is one noisy row."""
  n = min(cap, len(full.rows))
  k = len({r[full.cols.klass.at] for r in full.rows})
  E.the.Leaf = (max(2, n // (8*k)) if LEAF == "auto" else int(LEAF))
  tr   = E.clone(full, E.grabs(full, n))
  root = E.fit(E.tree(tr, tr.rows), *E.target(tr))
  return [E.leaf(root, r).pred for r in te.rows], n

def forest(full, te, cap=512, trees=20):
  """TREES trees on bootstraps of the SAME cap labels -- no extra
  budget, just more model.  Each split sees only sqrt(#x) columns,
  drawn afresh: bagging rows alone leaves every tree rooted on the
  same question, so the votes barely differ."""
  n   = min(cap, len(full.rows))
  k   = len({r[full.cols.klass.at] for r in full.rows})
  lab = E.grabs(full, n)
  E.the.Leaf = max(2, n // (8*k))
  box = int(sqrt(len(full.cols.x))) or 1
  out = []
  for _ in range(trees):
    tr   = E.clone(full, [random.choice(lab) for _ in lab])
    out += [E.fit(E.tree(tr, tr.rows, sub=box), *E.target(tr))]
  return [Counter(E.leaf(t,r).pred for t in out).most_common(1)[0][0]
          for r in te.rows], n

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
  return list(m.predict(X(te.rows))), len(full.rows)

def main(f):
  acc, pd, secs, ns = [], [], 0.0, []
  for s in range(SEEDS):
    t, full, te = split(f, s)
    k  = t.cols.klass.at
    t0 = time.time()
    if   ARM == "lgbm":  g, n = lgbm(full, te)
    elif ARM == "rf":    g, n = forest(full, te)
    elif ARM == "zeroR": g, n = ([E.mid(E.adds(
      (r[k] for r in full.rows), E.Sym()))]*len(te.rows), len(full.rows))
    else:                g, n = ezr(full, te, int(ARM))
    secs += time.time() - t0
    want  = [str(r[k]) for r in te.rows]
    pairs = list(zip([str(x) for x in g], want))
    d     = E.abcd(pairs)
    acc  += [100*sum(a == b for a, b in pairs)/len(pairs)]
    pd   += [S.mean(v["pd"] for v in d.values())]
    ns   += [n]
  pre = [os.path.basename(f)[:-4], str(len(te.rows)),
         str(len(t.cols.x)), str(len({r[k] for r in t.rows})),
         ARM, f"{secs/SEEDS:.5f}", f"{S.median(ns):.0f}"]
  if os.environ.get("RAW"):      # every seed, for a stats test
    for lab, v in (("acc", acc), ("pd", pd)):
      print("\t".join(pre + [lab] + [f"{x:.4f}" for x in v]),
            flush=True)
  else:
    print("\t".join(pre + [f"{S.median(acc):.4f}",
                          f"{S.median(pd):.4f}"]), flush=True)

if __name__ == "__main__":
  for p in sys.argv[1:]:
    try: main(p)
    except Exception as ex:
      print(f"SKIP\t{p}\t{type(ex).__name__}: {ex}", file=sys.stderr)
