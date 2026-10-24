#!/usr/bin/env python3 -B
"""ens.py: naive bayes, AODE and TAN, voting as probabilities.

The three disagree for different reasons -- NB ignores every
dependence, AODE averages all the pairwise ones, TAN keeps the
single best parent per column -- so the hope is that where one is
confidently wrong the other two outvote it.

Each member is normalised to a posterior (softmax of its own log
score, which keeps a member that is unsure from shouting), then
the posteriors are averaged.  Each member also keeps the bin
width it likes best: AODE's pair tables are quadratic in bins, so
it reads the data at ABINS while the other two read it at BINS.

  BINS=17 ABINS=5 SEEDS=20 python3 etc/ens.py diabetes soybean ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
from math import log, exp
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB, aode as A, tan as T      # pylint: disable=C0413
import a2de as A2                        # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 20))
ABINS = int(os.environ.get("ABINS", 5))   # bins AODE reads at
TWO   = int(os.environ.get("TWO", 0))     # 1 = also vote a2de in
TAN   = int(os.environ.get("TAN", 1))     # 0 = leave TAN out
TBINS = int(os.environ.get("TBINS", 3))   # bins a2de reads at
RAW   = int(os.environ.get("RAW", 1))

def soft(d: dict) -> dict:
  "Log scores to probabilities, the biggest subtracted out first."
  hi = max(d.values())
  z  = {k: exp(v - hi) for k, v in d.items()}
  s  = sum(z.values())
  return {k: v/s for k, v in z.items()}

def nbp(tbl, m, row) -> dict:
  "`nb.nb`, but keeping every class score, not just the best."
  by, sp = m
  n, nk, out = sum(v[0] for v in by.values()), len(by), {}
  for k, (cnt, cols) in by.items():
    s = log((cnt + NB.K) / (n + NB.K*nk))
    for c in tbl.cols.x:
      v = row[c.at]
      if v == "?": continue
      slot = cols[c.at]
      p = (NB.gauss(slot, v, sp[c.at]) if type(slot) is not dict else
           (slot.get(NB.bin1(c, v), 0) + NB.M/sp[c.at]) / (cnt + NB.M))
      s += log(max(p, 1e-300))
    out[k] = s
  return out

def aodep(tbl, m, row) -> dict:
  "`aode.aode`, ditto.  None if no column had the support to lead."
  n1, n2, ny, vs = m
  ks, n = list(ny), sum(ny.values())
  b  = A.cells(tbl, row)
  sp = [(a, v) for a, v in b
        if sum(n1.get((a, v, y), 0) for y in ks) >= A.MINC]
  if not sp: return None
  out = {}
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
    out[y] = hi + log(sum(exp(x - hi) for x in xs))
  return out

def tanp(tbl, m, row) -> dict:
  "`tan.tan`, ditto."
  n1, n2, ny, vs, dad = m
  n, b, out = sum(ny.values()), dict(T.cells(tbl, row)), {}
  for y, cnt in ny.items():
    s = log((cnt + NB.K) / (n + NB.K*len(ny)))
    for a1, v1 in b.items():
      p = dad.get(a1)
      if p is None or p not in b:
        s += log((n1.get((a1, v1, y), 0) + NB.M/vs[a1]) / (cnt + NB.M))
      else:
        v2 = b[p]
        k  = ((a1, v1, p, v2, y) if a1 < p else (p, v2, a1, v1, y))
        s += log((n2.get(k, 0) + NB.M/vs[a1])
                 / (n1.get((p, v2, y), 0) + NB.M))
    out[y] = s
  return out

def a2dep(tbl, m, row) -> dict:
  "`a2de.a2de`, ditto."
  n2, n3, ny, vs = m
  ks, n = list(ny), sum(ny.values())
  b  = A.cells(tbl, row)
  sp = []
  for i, (a1, v1) in enumerate(b):
    for a2, v2 in b[i+1:]:
      c = sum(n2.get((a1, v1, a2, v2, y), 0) for y in ks)
      if c >= A2.MINC: sp += [(c, a1, v1, a2, v2)]
  if not sp: return None
  if A2.MAXSP and len(sp) > A2.MAXSP:
    sp = sorted(sp, reverse=True)[:A2.MAXSP]
  out = {}
  for y in ks:
    xs = []
    for _, a1, v1, a2, v2 in sp:
      c2 = n2.get((a1, v1, a2, v2, y), 0)
      s  = log((c2 + 1/(len(ks)*vs[a1]*vs[a2])) / (n + 1))
      for a3, v3 in b:
        if a3 in (a1, a2): continue
        k = tuple(x for q in sorted([(a1, v1), (a2, v2), (a3, v3)])
                  for x in q) + (y,)
        s += log((n3.get(k, 0) + NB.M/vs[a3]) / (c2 + NB.M))
      xs += [s]
    hi = max(xs)
    out[y] = hi + log(sum(exp(x - hi) for x in xs))
  return out

def main(names):
  if not RAW:
    print(f"BINS={NB.BINS} ABINS={ABINS} SEEDS={SEEDS}\n"
          f"{'data':<16}{'k':>3}{'x':>5} |{'nb':>6}{'ens':>6} |"
          f"{'d':>6}{'':>2} |{'s/nb':>7}{'s/ens':>8}")
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    a1, a2, t1, t2, big = [], [], 0.0, 0.0 ,0
    for s in range(SEEDS):
      random.seed(s)
      t  = E.Tbl(E.csv(f))
      t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at  = t.cols.klass.at
      big = len(t.cols.x) > A.AMAX          # too wide for AODE
      sc  = lambda g: 100*sum(str(x) == str(r[at]) for x, r in
                              zip(g, te.rows))/len(te.rows)
      t0 = time.time(); mnb = NB.fit(tr, tr.rows)
      pnb = [nbp(tr, mnb, r) for r in te.rows]
      a1 += [sc([max(p, key=p.get) for p in pnb])]
      t1 += time.time()-t0
      t0  = time.time()
      mt  = T.fit(tr, tr.rows) if TAN else None
      bins = NB.BINS
      NB.BINS = ABINS
      ma  = None if big else A.fit(tr, tr.rows)
      NB.BINS = TBINS
      m2  = A2.fit(tr, tr.rows) if TWO and len(t.cols.x) <= A2.AMAX else None
      NB.BINS = bins
      out = []
      for r, p0 in zip(te.rows, pnb):
        ps = [soft(p0)] + ([soft(tanp(tr, mt, r))] if mt else [])
        if ma:
          NB.BINS = ABINS
          pa = aodep(tr, ma, r)
          NB.BINS = bins
          if pa: ps += [soft(pa)]
        if m2:
          NB.BINS = TBINS
          p2 = a2dep(tr, m2, r)
          NB.BINS = bins
          if p2: ps += [soft(p2)]
        avg = {y: sum(p.get(y, 0) for p in ps) for y in ps[0]}
        out += [max(avg, key=avg.get)]
      a2 += [sc(out)]; t2 += time.time()-t0
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
