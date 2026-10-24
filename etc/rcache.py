#!/usr/bin/env python3 -B
"""rcache.py: freeze the regression splits, and LightGBM's answers.

The classification twin of this is `cache.py`; the rig is the one
`etc/arms.py` scores on -- rows with any missing y dropped, 80:20,
20 seeds.  Each split is written down

    ~/tmp/ezrreg/<data>/<seed>.tr.csv   and  <seed>.te.csv

and LightGBM, which reads every training row, leaves its predicted
y beside them, one per test row:

    ~/tmp/ezrreg/<data>/<seed>.lgbm

Predictions, not errors: a later measure (MAE, Spearman, how good
the top-k of its ranking is) is then arithmetic over the cache
rather than another run of LightGBM.

  OUT=~/tmp/ezrreg SEEDS=20 python3 etc/rcache.py 2dplanes auto93 ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import arms as A                          # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
LGB   = int(os.environ.get("LGB", 1))
OUT   = os.path.expanduser(os.environ.get("OUT", "~/tmp/ezrreg"))

def put(f: str, head: list, rows: list):
  with open(f, "w") as fp:
    print(",".join(str(x) for x in head), file=fp)
    for r in rows: print(",".join(str(x) for x in r), file=fp)

def main(names):
  for dn in names:
    src  = os.path.expanduser(f"~/gits/moot/regression/{dn}.csv")
    head = next(iter(E.csv(src)))
    d    = os.path.join(OUT, dn)
    os.makedirs(d, exist_ok=True)
    secs = 0.0
    for s in range(SEEDS):
      _, tr, te = A.split(src, s)         # the rig arms.py scores on
      put(f"{d}/{s}.tr.csv", head, tr.rows)
      put(f"{d}/{s}.te.csv", head, te.rows)
      if LGB:
        t0 = time.time()
        p  = A.lgbm_pred(tr, te)
        secs += time.time()-t0
        with open(f"{d}/{s}.lgbm", "w") as fp:
          for v in p: print(f"{v:.6f}", file=fp)
    print(f"{dn:<16} {SEEDS} splits, {len(tr.rows)+len(te.rows):>6} rows"
          + (f", lgbm {secs:7.2f}s" if LGB else ""), flush=True)

if __name__ == "__main__": main(sys.argv[1:])
