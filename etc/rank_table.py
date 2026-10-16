#!/usr/bin/env python3 -B
# vim: set et sw=2 ts=2 sts=2 cc=75 :
"""
rank_table.py: how close can a shortlist get?  Team A labels K rows
once; team B reuses that work and labels C more to pick a winner.  We
report where that winner really sits among the held-out rows (0 = the
very best), against team B working alone: label C at random, keep the
best.  Same 20 MOOT files as gawk4ai/slides/rank.py.

Every run is cached under its own knobs, so -cache alone redraws
any table we have already paid for, and -cache with knobs that are
not in there says so rather than quietly running for ten minutes.

Usage: pypy3 rank_table.py [-k K] [-c C] [-any N] [-seeds N] [-cache]
"""
import os, sys, json, statistics as st
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + "/..")
import min as m
import random

MOOT  = os.path.expanduser("~/gits/moot/optimize")
CACHE = f"{HERE}/rank_table.json"
DATA = """misc/auto93 process/nasa93dem process/coc1000 process/pom3a
  process/pom3d process/xomo_flight config/SS-A config/SS-D config/SS-K
  config/SS-M config/Apache_AllMeasurements config/HSMGP_num
  config/SQL_AllMeasurements systems/7z systems/BDBC systems/HSQLDB
  rl/A2C_CartPole sales_data/socks misc/Wine_quality test/dataset120""".split()

def one(job):                         # one file: both arms, all seeds
  f, K, C, Any, seeds = job
  src = f"{MOOT}/{f}.csv"
  n = sum(1 for _ in open(src)) - 1
  mod, rnd = [], []
  for s in range(1, seeds + 1):
    for arm, out in ((0, mod), (C, rnd)):
      random.seed(s)
      m.the.Any, m.the.Stop, m.the.Check, m.the.Rand = Any, K + C, C, arm
      t = m.Tbl(m.some(src, Any) if Any else m.csv(src))
      rows = t.rows[:]; random.shuffle(rows)
      todo, train = rows[K:], m.clone(t, rows[:K])
      look = (random.sample(todo, arm) if arm else
              sorted(todo, key=lambda r: m.ydist(train, m.near(train, r)))[:C])
      pick = min(look, key=lambda r: m.ydist(t, r))
      ys = sorted(m.ydist(t, r) for r in todo)
      out += [int(100 * ys.index(m.ydist(t, pick)) / len(ys))]
  return f.split("/")[-1], n, mod, rnd

def qs(v):                            # median, and the quartiles round it
  v = sorted(v)
  q = lambda p: v[min(len(v) - 1, int(len(v) * p))]
  return q(.5), q(.25), q(.75)

def cache(key, out=None):             # read, or write and pass through
  d = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
  if out is None: return d.get(key), sorted(d)
  d[key] = out
  json.dump(d, open(CACHE, "w"), indent=1)
  return out, None

def main(K, C, Any, seeds, redraw):
  key = f"K{K}.C{C}.any{Any}.seeds{seeds}"
  out, have = cache(key) if redraw else (None, None)
  if redraw and not out:
    sys.exit(f"not cached: {key}\ncached: " + " ".join(have))
  if not out:
    out = cache(key, Pool(10).map(one, [(f,K,C,Any,seeds) for f in DATA]))[0]
  out = sorted(out, key=lambda r: qs(r[2])[0])
  print(f"where the pick really sits among the held-out rows, % "
        f"(0 = we found the best one):\n{len(DATA)} MOOT files x {seeds}"
        f" shuffles, K={K} then C={C}, sampled to {Any} rows\n")
  print(f'{"data":<26}{"rows":>7}{"med":>6}{"q25-q75":>11}{"rand "+str(C):>9}')
  for name, n, mod, rnd in out:
    md, lo, hi = qs(mod)
    print(f"{name[:24]:<26}{n:>7}{md:>6}{f'{lo}-{hi}':>11}{qs(rnd)[0]:>9}")
  a = [x for _, _, mo, _ in out for x in mo]
  b = [x for _, _, _, rn in out for x in rn]
  print(f'{"median, all "+str(len(out)):<26}{"":>7}{st.median(a):>6.0f}'
        f'{"":>11}{st.median(b):>9.0f}')

if __name__ == "__main__":
  g = lambda f, d: (int(sys.argv[sys.argv.index(f) + 1])
                    if f in sys.argv else d)
  main(g("-k", 45), g("-c", 5), g("-any", 2048), g("-seeds", 20),
       "-cache" in sys.argv)
