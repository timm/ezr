#!/usr/bin/env python3 -B
"""dfe.py: naive bayes whose counts are trained, not just counted.

Ordinary naive bayes adds 1 to a cell for every row that lands in
it.  That fits the data's shape but nobody ever told it to
classify well -- which is why it loses most on the datasets with
the MOST rows, where something better was learnable and it did not
learn it.

Discriminative frequency estimate keeps every structure naive
bayes has and changes only what a row contributes.  Score the row
with the counts so far; if the true class already wins with
probability p, add 1-p instead of 1.  Rows it gets right stop
teaching it, rows it gets wrong teach it loudly.  A few passes.

The model it returns is shaped exactly like `nb.fit`'s, so
`nb.nb` scores it unchanged -- only the numbers inside differ,
and they are floats.

  BINS=17 EPOCHS=3 SEEDS=20 python3 etc/dfe.py diabetes ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import log, exp
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB                           # pylint: disable=C0413

SEEDS  = int(os.environ.get("SEEDS", 20))
EPOCHS = int(os.environ.get("EPOCHS", 3))
LGB    = int(os.environ.get("LGB", 0))
RAW    = int(os.environ.get("RAW", 1))

def post(tbl, by, sp, row) -> dict:
  "The normalised posterior, by the same sums `nb.nb` maximises."
  n, nk, s = sum(v[0] for v in by.values()), len(by), {}
  for k, (cnt, cols) in by.items():
    z = log((cnt + NB.K) / (n + NB.K*nk)) if n else 0.0
    for c in tbl.cols.x:
      v = row[c.at]
      if v == "?": continue
      p = ((cols[c.at].get(NB.bin1(c, v), 0) + NB.M/sp[c.at])
           / (cnt + NB.M))
      z += log(max(p, 1e-300))
    s[k] = z
  hi = max(s.values())
  e  = {k: exp(v - hi) for k, v in s.items()}
  tot = sum(e.values())
  return {k: v/tot for k, v in e.items()}

def fit(tbl, rows) -> tuple:
  """Counts that start at nothing and are taught.  The first pass
  sees a uniform posterior, so it adds a near-constant to every
  cell -- i.e. it lays down ordinary naive bayes, and the passes
  after it only correct what that got wrong."""
  at = tbl.cols.klass.at
  by = {k: [0.0, {c.at: {} for c in tbl.cols.x}]
        for k in {r[at] for r in rows}}
  sp = {c.at: (NB.BINS if type(c) is E.Num else max(1, len(c.has)))
        for c in tbl.cols.x}
  order = list(rows)
  for _ in range(EPOCHS):
    random.shuffle(order)
    for r in order:
      y = r[at]
      w = 1 - post(tbl, by, sp, r)[y]
      by[y][0] += w
      for c in tbl.cols.x:
        v = r[c.at]
        if v == "?": continue
        d = by[y][1][c.at]; b = NB.bin1(c, v)
        d[b] = d.get(b, 0) + w
  return by, sp

def main(names):
  if not RAW:
    print(f"BINS={NB.BINS or 'gauss'} EPOCHS={EPOCHS} M={NB.M:g} "
          f"K={NB.K:g} SEEDS={SEEDS}\n"
          f"{'data':<16}{'k':>3}{'x':>5} |{'nb':>6}{'dfe':>6} |"
          f"{'d':>6}{'':>2} |{'s/nb':>7}{'s/dfe':>8}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    a1, a2, t1, t2 = [], [], 0.0, 0.0
    for s in range(SEEDS):
      random.seed(s)
      t  = E.Tbl(E.csv(f))
      t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at = t.cols.klass.at
      sc = lambda g: 100*sum(str(x) == str(r[at]) for x, r in
                             zip(g, te.rows))/len(te.rows)
      t0 = time.time(); by, sp = NB.fit(tr, tr.rows)
      a1 += [sc([NB.nb(tr, by, sp, r) for r in te.rows])]
      t1 += time.time()-t0
      t0 = time.time(); by, sp = fit(tr, tr.rows)
      a2 += [sc([NB.nb(tr, by, sp, r) for r in te.rows])]
      t2 += time.time()-t0
    if RAW:
      print(f"#raw {dn} 0 0 0 " + ",".join(f"{x:g}" for x in a2),
            flush=True)
      continue
    d = S.median(a2) - S.median(a1)
    sig = "=" if E.same(a1, a2, .35) or d == 0 else ("+" if d > 0 else "-")
    print(f"{dn:<16}{len({r[at] for r in t.rows}):>3}{len(t.cols.x):>5} |"
          f"{S.median(a1):>6.0f}{S.median(a2):>6.0f} |{d:>+6.0f} {sig} |"
          f"{NB.dot(t1/SEEDS):>7}{NB.dot(t2/SEEDS):>8}", flush=True)

if __name__ == "__main__": main(sys.argv[1:])
