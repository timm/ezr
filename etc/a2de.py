#!/usr/bin/env python3 -B
"""a2de.py: AODE, but two superparents at a time.

AODE averages the models that hang every column off one other
column.  A2DE averages the models that hang every column off a
PAIR of others, so a three-way interaction -- the thing that
beats this family on the exact-rule datasets -- is at least
representable.

The price is one more factor of columns in the counting and the
scoring, and one more factor of BINS in how thinly the data is
spread over the tables.  So A2DE wants coarser bins than AODE,
which already wanted coarser bins than naive bayes, and a table
wider than AMAX falls straight back to plain naive bayes.

  BINS=3 AMAX=20 SEEDS=20 python3 etc/a2de.py diabetes car ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import log, exp
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB, aode as A                # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
AMAX  = int(os.environ.get("AMAX", 20))   # wider than this: plain nb
MINC  = int(os.environ.get("MINC", 30))   # rows before a pair leads
MAXSP = int(os.environ.get("MAXSP", 0))   # 0 = every pair leads
RAW   = int(os.environ.get("RAW", 1))

def fit(tbl, rows):
  """`n2` counts value pairs, `n3` value triples -- a pair of
  parents plus one child is three columns, so that is the biggest
  table a 2-dependence model reads."""
  at, n2, n3, ny = tbl.cols.klass.at, {}, {}, {}
  for r in rows:
    y = r[at]; ny[y] = ny.get(y, 0) + 1
    b = A.cells(tbl, r)
    for i, (a1, v1) in enumerate(b):
      for j in range(i+1, len(b)):
        a2, v2 = b[j]
        n2[a1, v1, a2, v2, y] = n2.get((a1, v1, a2, v2, y), 0) + 1
        for a3, v3 in b[j+1:]:
          k = (a1, v1, a2, v2, a3, v3, y)
          n3[k] = n3.get(k, 0) + 1
  vs = {c.at: (NB.BINS if type(c) is E.Num else max(1, len(c.has)))
        for c in tbl.cols.x}
  return n2, n3, ny, vs

def a2de(tbl, m, row):
  "Average, in logs, over every pair of columns with the support to lead."
  n2, n3, ny, vs = m
  ks, n = list(ny), sum(ny.values())
  b  = A.cells(tbl, row)
  sp = []
  for i, (a1, v1) in enumerate(b):
    for a2, v2 in b[i+1:]:
      c = sum(n2.get((a1, v1, a2, v2, y), 0) for y in ks)
      if c >= MINC: sp += [(c, a1, v1, a2, v2)]
  if not sp: return None
  if MAXSP and len(sp) > MAXSP:           # the best supported lead
    sp = sorted(sp, reverse=True)[:MAXSP]
  sp = [x[1:] for x in sp]
  best, most = None, -1e30
  for y in ks:
    xs = []
    for a1, v1, a2, v2 in sp:
      c2 = n2.get((a1, v1, a2, v2, y), 0)
      s  = log((c2 + 1/(len(ks)*vs[a1]*vs[a2])) / (n + 1))
      for a3, v3 in b:
        if a3 in (a1, a2): continue
        k = tuple(x for p in sorted([(a1, v1), (a2, v2), (a3, v3)])
                  for x in p) + (y,)
        s += log((n3.get(k, 0) + NB.M/vs[a3]) / (c2 + NB.M))
      xs += [s]
    hi = max(xs)
    s  = hi + log(sum(exp(x - hi) for x in xs))
    if s > most: best, most = y, s
  return best

def main(names):
  if not RAW:
    print(f"BINS={NB.BINS} AMAX={AMAX} MINC={MINC} SEEDS={SEEDS}\n"
          f"{'data':<16}{'k':>3}{'x':>5} |{'nb':>6}{'a2de':>6} |"
          f"{'d':>6}{'':>2} |{'s/nb':>7}{'s/a2de':>8}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    a1, a2, t1, t2, wide = [], [], 0.0, 0.0, False
    for s in range(SEEDS):
      random.seed(s)
      t  = E.Tbl(E.csv(f))
      t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at   = t.cols.klass.at
      wide = len(t.cols.x) > AMAX
      sc   = lambda g: 100*sum(str(x) == str(r[at]) for x, r in
                               zip(g, te.rows))/len(te.rows)
      t0  = time.time(); by, sp = NB.fit(tr, tr.rows)
      nbs = [NB.nb(tr, by, sp, r) for r in te.rows]
      a1 += [sc(nbs)]; t1 += time.time()-t0
      t0  = time.time()
      if wide: a2 += [a1[-1]]
      else:
        mod = fit(tr, tr.rows)
        a2 += [sc([a2de(tr, mod, r) or g for g, r in zip(nbs, te.rows)])]
      t2 += time.time()-t0
    if RAW:
      print(f"#raw {dn} 0 0 {int(wide)} " + ",".join(f"{x:g}" for x in a2),
            flush=True)
      continue
    d = S.median(a2) - S.median(a1)
    sig = "=" if E.same(a1, a2, .35) or d == 0 else ("+" if d > 0 else "-")
    print(f"{dn:<16}{len({r[at] for r in t.rows}):>3}{len(t.cols.x):>5} |"
          f"{S.median(a1):>6.0f}{S.median(a2):>6.0f} |{d:>+6.0f} {sig} |"
          f"{NB.dot(t1/SEEDS):>7}{NB.dot(t2/SEEDS):>8}"
          + ("   wide: a2de skipped" if wide else ""), flush=True)

if __name__ == "__main__": main(sys.argv[1:])
