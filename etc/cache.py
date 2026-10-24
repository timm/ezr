#!/usr/bin/env python3 -B
"""cache.py: freeze the train/test splits, and LightGBM's answers to them.

Every arm re-reads the same CSVs and re-shuffles them with the same
seeds, which is both wasted work and a standing invitation for two
arms to disagree about what "seed 7" meant.  So write the splits
down once:

    ~/tmp/ezr/<data>/<seed>.tr.csv   and  <seed>.te.csv

and let every arm read them with `-t` and `-T`.  LightGBM then runs
over those same files once, and its PREDICTIONS -- one class per
test row, not a score -- go beside them:

    ~/tmp/ezr/<data>/<seed>.lgbm

Caching predictions, not accuracies, is the point: a new measure
(pd, pf, d2h, anything) is then a few seconds of arithmetic over
the cache instead of another full run of LightGBM.

  OUT=~/tmp/ezr SEEDS=20 python3 etc/cache.py diabetes vowel ...
  LGB=0 ... to write the splits and skip LightGBM.
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB                           # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
LGB   = int(os.environ.get("LGB", 1))
OUT   = os.path.expanduser(os.environ.get("OUT", "~/tmp/ezr"))

def put(f: str, head: list, rows: list):
  "Rows back out as csv, in the column order they came in."
  with open(f, "w") as fp:
    print(",".join(str(x) for x in head), file=fp)
    for r in rows: print(",".join(str(x) for x in r), file=fp)

def main(names):
  for dn in names:
    src  = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    head = next(iter(E.csv(src)))
    t    = E.Tbl(E.csv(src))
    t    = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
    d    = os.path.join(OUT, dn)
    os.makedirs(d, exist_ok=True)
    secs = 0.0
    for s in range(SEEDS):
      random.seed(s)
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      put(f"{d}/{s}.tr.csv", head, tr.rows)
      put(f"{d}/{s}.te.csv", head, te.rows)
      if LGB:
        t0 = time.time()
        g, _ = NB.lgbm(t, tr, te)
        secs += time.time()-t0
        with open(f"{d}/{s}.lgbm", "w") as fp:
          for x in g: print(x, file=fp)
    print(f"{dn:<16} {SEEDS} splits, {len(t.rows):>6} rows"
          + (f", lgbm {secs:6.2f}s" if LGB else ""), flush=True)

if __name__ == "__main__": main(sys.argv[1:])
