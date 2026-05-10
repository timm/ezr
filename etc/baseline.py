#!/usr/bin/env python3
"""Run acquire pipeline on all moot/optimize CSVs, output mean wins per file."""
import sys, glob, random, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ezr import *
from ezeg import ready, wins

the.learn.budget = 50
the.learn.check = 5
REPS = 20

files = sorted(glob.glob(str(Path.home()/"gits/moot/optimize/*/*.csv")))
print(f"# {len(files)} files, budget={the.learn.budget} check={the.learn.check} reps={REPS}", flush=True)

for f in files:
  try:
    t0 = time.time()
    d0 = Data(csv(f))
    w2 = Num()
    for i in range(REPS):
      random.seed(the.seed + i)
      d, d_train, test_rows = ready(d0)
      lab = acquire(d_train)
      t = treeGrow(d_train, lab.rows)
      win = wins(d0)
      guess = sorted(test_rows, key=lambda r: mid(treeLeaf(t, r).ynum))
      add(w2, win(min(guess[:the.learn.check], key=lambda r: disty(d_train, r))))
    print(f"{Path(f).name}\t{int(mid(w2))}\t{int(spread(w2))}\t{w2.n}\t{time.time()-t0:.1f}s", flush=True)
  except Exception as e:
    print(f"{Path(f).name}\tERR\t{e}", flush=True)
