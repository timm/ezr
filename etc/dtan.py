#!/usr/bin/env python3 -B
"""dtan.py: TAN's structure, DFE's counts.

Two separate wins, stacked.  `tan` fixes WHAT depends on what --
one parent per column, chosen by conditional mutual information.
`dfe` fixes HOW MUCH each row contributes -- a row the model
already gets right teaches it almost nothing.  They touch
different halves of the same model, so they should compose.

The tree is learned once from ordinary counts.  Then the counts
are thrown away and re-learned discriminatively on that fixed
tree, which is the only honest order: you cannot pick a structure
from counts that were trained to suit a structure.

  BINS=17 EPOCHS=3 SEEDS=20 python3 etc/dtan.py diabetes ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import log, exp
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB                           # pylint: disable=C0413
import tan as T                           # pylint: disable=C0413

SEEDS  = int(os.environ.get("SEEDS", 20))
EPOCHS = int(os.environ.get("EPOCHS", 3))
RAW    = int(os.environ.get("RAW", 1))

def scores(tbl, m, row) -> dict:
  "Every class's log score, by TAN's factorisation."
  n1, n2, ny, vs, dad = m
  n, b, s = sum(ny.values()), dict(T.cells(tbl, row)), {}
  for y, cnt in ny.items():
    z = log((cnt + NB.K) / (n + NB.K*len(ny))) if n else 0.0
    for a1, v1 in b.items():
      p = dad.get(a1)
      if p is None or p not in b:
        z += log((n1.get((a1, v1, y), 0) + NB.M/vs[a1]) / (cnt + NB.M))
      else:
        v2 = b[p]
        k  = ((a1, v1, p, v2, y) if a1 < p else (p, v2, a1, v1, y))
        z += log((n2.get(k, 0) + NB.M/vs[a1])
                 / (n1.get((p, v2, y), 0) + NB.M))
    s[y] = z
  return s

def fit(tbl, rows):
  """Learn the tree from plain counts, then re-learn the counts on
  it discriminatively."""
  n1, n2, ny = T.counts(tbl, rows)
  ats = [c.at for c in tbl.cols.x]
  dad = T.tree(ats, T.cmi(ats, n1, n2, ny, max(1, len(rows))))
  vs  = {c.at: (NB.BINS if type(c) is E.Num else max(1, len(c.has)))
         for c in tbl.cols.x}
  at  = tbl.cols.klass.at
  n1, n2 = {}, {}
  ny = {k: 0.0 for k in ny}
  m, order = (n1, n2, ny, vs, dad), list(rows)
  for _ in range(EPOCHS):
    random.shuffle(order)
    for r in order:
      y  = r[at]
      sc = scores(tbl, m, r)
      hi = max(sc.values())
      e  = {k: exp(v - hi) for k, v in sc.items()}
      w  = 1 - e[y]/sum(e.values())
      ny[y] += w
      b = dict(T.cells(tbl, r))
      for a1, v1 in b.items():
        n1[a1, v1, y] = n1.get((a1, v1, y), 0) + w
        p = dad.get(a1)
        if p is not None and p in b:
          v2 = b[p]
          k  = ((a1, v1, p, v2, y) if a1 < p else (p, v2, a1, v1, y))
          n2[k] = n2.get(k, 0) + w
  return m

def main(names):
  if not RAW:
    print(f"BINS={NB.BINS or 'gauss'} EPOCHS={EPOCHS} SEEDS={SEEDS}\n"
          f"{'data':<16}{'k':>3}{'x':>5} |{'nb':>6}{'dtan':>6} |{'d':>6}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    a1, a2 = [], []
    for s in range(SEEDS):
      random.seed(s)
      t  = E.Tbl(E.csv(f))
      t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at = t.cols.klass.at
      sc = lambda g: 100*sum(str(x) == str(r[at]) for x, r in
                             zip(g, te.rows))/len(te.rows)
      by, sp = NB.fit(tr, tr.rows)
      a1 += [sc([NB.nb(tr, by, sp, r) for r in te.rows])]
      mod = fit(tr, tr.rows)
      a2 += [sc([max(scores(tr, mod, r).items(),
                     key=lambda z: z[1])[0] for r in te.rows])]
    if RAW:
      print(f"#raw {dn} 0 0 0 " + ",".join(f"{x:g}" for x in a2),
            flush=True)
      continue
    d = S.median(a2) - S.median(a1)
    print(f"{dn:<16}{len({r[at] for r in t.rows}):>3}{len(t.cols.x):>5} |"
          f"{S.median(a1):>6.0f}{S.median(a2):>6.0f} |{d:>+6.0f}", flush=True)

if __name__ == "__main__": main(sys.argv[1:])
