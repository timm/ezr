#!/usr/bin/env python3 -B
"""tan.py: tree-augmented naive bayes.

AODE lets every column be a parent and averages the lot, which
costs n^2 pair tables -- and those tables are quadratic in BINS,
so resolution that helps naive bayes starves them.  TAN picks ONE
parent per column instead: build a maximum spanning tree over the
columns, weighted by how much each pair tells you about the class
that you did not already know (conditional mutual information),
and let each column depend on its one tree parent.

That is n-1 pair tables, not n^2/2, so it survives both wide
tables and fine bins -- the two places AODE could not go.

  BINS=17 SEEDS=20 python3 etc/tan.py diabetes soybean ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import log
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB                           # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
LGB   = int(os.environ.get("LGB", 0))
RAW   = int(os.environ.get("RAW", 1))

def cells(tbl, row):
  "The row as (column, bin) pairs, skipping what it does not say."
  return [(c.at, NB.bin1(c, row[c.at])) for c in tbl.cols.x
          if row[c.at] != "?"]

def counts(tbl, rows):
  "Class tallies per value and per pair of values, in one pass."
  at, n1, n2, ny = tbl.cols.klass.at, {}, {}, {}
  for r in rows:
    y = r[at]; ny[y] = ny.get(y, 0) + 1
    b = cells(tbl, r)
    for i, (a1, v1) in enumerate(b):
      n1[a1, v1, y] = n1.get((a1, v1, y), 0) + 1
      for a2, v2 in b[i+1:]:
        k = (a1, v1, a2, v2, y)
        n2[k] = n2.get(k, 0) + 1
  return n1, n2, ny

def cmi(ats, n1, n2, ny, n):
  """Conditional mutual information for every column pair: how much
  knowing one says about the other, once the class is known."""
  w = {}
  for k in n2:
    a1, v1, a2, v2, y = k
    p12 = n2[k]/n
    p1  = n1.get((a1, v1, y), 0)/n
    p2  = n1.get((a2, v2, y), 0)/n
    py  = ny[y]/n
    if p12 > 0 and p1 > 0 and p2 > 0:
      w[a1, a2] = w.get((a1, a2), 0) + p12*log(p12*py/(p1*p2))
  return w

def tree(ats, w):
  """Prim's, on the heaviest edges: every column gets one parent,
  and the root gets none."""
  if not ats: return {}
  seen, dad = {ats[0]}, {}
  while len(seen) < len(ats):
    best, edge = -1e30, None
    for a in seen:
      for b in ats:
        if b in seen: continue
        z = w.get((a, b), w.get((b, a), 0))
        if z > best: best, edge = z, (a, b)
    if edge is None: break
    dad[edge[1]] = edge[0]; seen.add(edge[1])
  return dad

def fit(tbl, rows):
  "Counts, the tree they imply, and how many values a column has."
  n1, n2, ny = counts(tbl, rows)
  ats = [c.at for c in tbl.cols.x]
  dad = tree(ats, cmi(ats, n1, n2, ny, max(1, len(rows))))
  vs  = {c.at: (NB.BINS if type(c) is E.Num else max(1, len(c.has)))
         for c in tbl.cols.x}
  return n1, n2, ny, vs, dad

def tan(tbl, m, row):
  "Each column scored against its one parent, or alone if it is root."
  n1, n2, ny, vs, dad = m
  n, b = sum(ny.values()), dict(cells(tbl, row))
  best, most = None, -1e30
  for y, cnt in ny.items():
    s = log((cnt + NB.K) / (n + NB.K*len(ny)))
    for a1, v1 in b.items():
      p = dad.get(a1)
      if p is None or p not in b:
        s += log((n1.get((a1, v1, y), 0) + NB.M/vs[a1]) / (cnt + NB.M))
      else:
        v2 = b[p]
        k  = ((a1, v1, p, v2, y) if a1 < p else (p, v2, a1, v1, y))
        up = n1.get((p, v2, y), 0)
        s += log((n2.get(k, 0) + NB.M/vs[a1]) / (up + NB.M))
    if s > most: best, most = y, s
  return best

def main(names):
  if not RAW:
    print(f"BINS={NB.BINS or 'gauss'} M={NB.M:g} K={NB.K:g} SEEDS={SEEDS}\n"
          f"{'data':<16}{'k':>3}{'x':>5} |{'nb':>6}{'tan':>6} |"
          f"{'d':>6}{'':>2} |{'s/nb':>7}{'s/tan':>8}")
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
      t0 = time.time(); mod = fit(tr, tr.rows)
      a2 += [sc([tan(tr, mod, r) for r in te.rows])]
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
