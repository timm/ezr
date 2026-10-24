#!/usr/bin/env python3 -B
"""aode.py: averaged one-dependence estimators, against naive bayes.

Naive bayes assumes every column is independent of every other,
given the class.  That is false, and on `moot/classify` it is what
costs it -- its worst losses are on its most stable datasets, so
the error is bias, not variance (which is why bagging it is a
waste of time).

AODE fixes the assumption one column at a time.  Pick a column as
a "superparent" and let every other column depend on it and the
class.  That is still a model you can count in one pass.  Do it
once per column and average the models, and the dependence any
single choice gets wrong is diluted by the rest.

Cost is quadratic in columns, both to count and to score, so a
table wider than AMAX falls back to plain naive bayes and says so.

  BINS=17 AMAX=40 SEEDS=20 python3 etc/aode.py diabetes soybean ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import log, exp
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB                           # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
AMAX  = int(os.environ.get("AMAX", 40))   # wider than this: plain nb
MINC  = int(os.environ.get("MINC", 30))   # rows before a column leads
LGB   = int(os.environ.get("LGB", 1))
RAW   = int(os.environ.get("RAW", 0))

def cells(tbl, row) -> list:
  "The row as (column, bin) pairs, skipping what it does not say."
  return [(c.at, NB.bin1(c, row[c.at])) for c in tbl.cols.x
          if row[c.at] != "?"]

def fit(tbl, rows) -> tuple:
  """One pass.  `n1` tallies a class per column-value, `n2` per
  unordered pair of column-values -- which is all a one-dependence
  model needs.  `vs` is how many values a column can take, so M can
  be spread over them the way `nb` spreads it."""
  at, n1, n2, ny = tbl.cols.klass.at, {}, {}, {}
  for r in rows:
    y = r[at]; ny[y] = ny.get(y, 0) + 1
    b = cells(tbl, r)
    for i, (a1, v1) in enumerate(b):
      n1[a1, v1, y] = n1.get((a1, v1, y), 0) + 1
      for a2, v2 in b[i+1:]:
        k = (a1, v1, a2, v2, y)
        n2[k] = n2.get(k, 0) + 1
  vs = {c.at: (NB.BINS if type(c) is E.Num else max(1, len(c.has)))
        for c in tbl.cols.x}
  return n1, n2, ny, vs

def aode(tbl, m, row):
  """Average the one-dependence models, in logs.  A column only gets
  to lead if the training set saw its value MINC times -- otherwise
  everything hanging off it is estimated from noise."""
  n1, n2, ny, vs = m
  ks, n = list(ny), sum(ny.values())
  b  = cells(tbl, row)
  sp = [(a, v) for a, v in b
        if sum(n1.get((a, v, y), 0) for y in ks) >= MINC]
  if not sp: return None
  best, most = None, -1e30
  for y in ks:
    xs = []
    for a1, v1 in sp:
      c1 = n1.get((a1, v1, y), 0)
      s  = log((c1 + 1/(len(ks)*vs[a1])) / (n + 1))
      for a2, v2 in b:
        if a2 == a1: continue
        k = (a1, v1, a2, v2, y) if a1 < a2 else (a2, v2, a1, v1, y)
        s += log((n2.get(k, 0) + NB.M/vs[a2]) / (c1 + NB.M))
      xs += [s]
    hi = max(xs)
    s  = hi + log(sum(exp(x - hi) for x in xs))
    if s > most: best, most = y, s
  return best

def main(names):
  print(f"BINS={NB.BINS or 'gauss'} AMAX={AMAX} MINC={MINC} "
        f"M={NB.M:g} K={NB.K:g} SEEDS={SEEDS}\n"
        f"{'data':<16}{'k':>3}{'x':>5}{'maj%':>6}{'test':>6} |{'nb':>6}"
        f"{'aode':>6}{'lgbm':>6} |{'a-nb':>6}{'':>2}{'a-lgbm':>7}{'':>2} |"
        f"{'s/nb':>7}{'s/aode':>8}{'s/lgbm':>8}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    a1, a2, a3, t1, t2, t3 = [], [], [], 0.0, 0.0, 0.0
    wide = False
    for s in range(SEEDS):
      random.seed(s)
      t  = E.Tbl(E.csv(f))
      t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at = t.cols.klass.at
      wide = len(t.cols.x) > AMAX
      sc = lambda g: 100*sum(str(x) == str(r[at]) for x, r in
                             zip(g, te.rows))/len(te.rows)
      t0 = time.time(); by, sp = NB.fit(tr, tr.rows)
      nbs = [NB.nb(tr, by, sp, r) for r in te.rows]
      a1 += [sc(nbs)]; t1 += time.time()-t0
      t0 = time.time()
      if wide: a2 += [a1[-1]]
      else:
        mod = fit(tr, tr.rows)
        a2 += [sc([aode(tr, mod, r) or g for g, r in zip(nbs, te.rows)])]
      t2 += time.time()-t0
      if LGB:
        g, dt = NB.lgbm(t, tr, te); a3 += [sc(g)]; t3 += dt
      else: a3 += [0]
    cnt = {}
    for r in t.rows: cnt[r[at]] = cnt.get(r[at], 0) + 1
    if RAW:
      print(f"#raw {dn} {len(cnt)} {len(t.cols.x)} {int(wide)} "
            + " ".join(",".join(f"{x:g}" for x in a)
                       for a in (a1, a2, a3)), flush=True)
      continue
    def mark(x, y):
      d = S.median(x) - S.median(y)
      return (d, " =" if E.same(x, y, .35) or d == 0 else
              (" +" if d > 0 else " -"))
    d1, s1 = mark(a2, a1); d2, s2 = mark(a2, a3)
    print(f"{dn:<16}{len(cnt):>3}{len(t.cols.x):>5}"
          f"{100*max(cnt.values())/len(t.rows):>6.0f}{len(te.rows):>6} |"
          f"{S.median(a1):>6.0f}{S.median(a2):>6.0f}{S.median(a3):>6.0f} |"
          f"{d1:>+6.0f}{s1}{d2:>+7.0f}{s2} |{NB.dot(t1/SEEDS):>7}"
          f"{NB.dot(t2/SEEDS):>8}{NB.dot(t3/SEEDS):>8}"
          + ("   wide: aode skipped" if wide else ""), flush=True)

if __name__ == "__main__": main(sys.argv[1:])
