#!/usr/bin/env python3 -B
"""rfrom.py: score a regressor off the frozen splits.

Reads the `~/tmp/ezrreg/<data>/<seed>.{tr,te}.csv` pairs that
`rcache.py` wrote, runs one arm over them, and scores it beside the
LightGBM predictions cached alongside -- so LightGBM never runs
again and both arms are judged on exactly the same rows.

Error is MAE over (mean - min) of the TEST y, which is what
`arms.py` reports, so sets of different scale are comparable.

  ARM=tree CAP=256 python3 etc/rfrom.py auto93 ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random
from math import sqrt
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E

SEEDS = int(os.environ.get("SEEDS", 20))
CAP   = int(os.environ.get("CAP", 256))   # labels the ezr arm may have
ARM   = os.environ.get("ARM", "tree")
OUT   = os.path.expanduser(os.environ.get("OUT", "~/tmp/ezrreg"))

def tree(tr, te):
  "ezr's tree on CAP random labels, about sqrt(n) leaves."
  n = min(CAP, len(tr.rows))
  E.the.Leaf = max(2, int(sqrt(n)))
  lab  = E.clone(tr, E.grabs(tr, n))
  root = E.fit(E.tree(lab, lab.rows), *E.target(lab))
  return [E.leaf(root, r).pred for r in te.rows]

def main(names):
  for dn in names:
    a, b, secs, rows = [], [], 0.0, 0
    for s in range(SEEDS):
      random.seed(s)
      d  = f"{OUT}/{dn}/{s}"
      tr = E.Tbl(E.csv(f"{d}.tr.csv")); te = E.Tbl(E.csv(f"{d}.te.csv"))
      _, Y = E.target(tr)                 # (column, how to read it)
      ys   = [Y(r) for r in te.rows]
      div  = sum(ys)/len(ys) - min(ys) + 1E-32
      t0 = time.time()
      g  = dict(tree=tree)[ARM](tr, te)
      secs += time.time()-t0
      a += [sum(abs(y - v) for y, v in zip(ys, g))/len(ys)/div]
      lg = [float(l) for l in open(f"{d}.lgbm")]
      b += [sum(abs(y - v) for y, v in zip(ys, lg))/len(ys)/div]
      rows = len(tr.rows) + len(te.rows)
    print(f"#raw {dn} {rows} {len(tr.cols.x)} {secs/SEEDS:.4f} "
          + ",".join(f"{x:.6f}" for x in a) + " "
          + ",".join(f"{x:.6f}" for x in b), flush=True)

if __name__ == "__main__": main(sys.argv[1:])
