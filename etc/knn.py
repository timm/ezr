#!/usr/bin/env python3 -B
"""knn.py: nearest neighbours, triangular kernel, bounded reference set.

Every bayes variant tried so far fails the same way on the same
datasets -- the ones whose classes are exact rules over several
columns at once.  Nearest neighbours has no such blind spot: it
does not model the boundary, it remembers the rows.

Two knobs keep it honest.  SOME caps the reference set at a random
sample of the training rows, so the cost per test row is a constant
and does not grow with the table.  The triangular kernel weights
each of the k neighbours by `1 - d/dk` (dk being the distance of
the furthest of them), so a neighbour on the edge of the
neighbourhood counts for nearly nothing and k is less of a cliff.

  KS=1,3,5 SOME=2048 SEEDS=5 python3 etc/knn.py diabetes vowel ...
"""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ezr as E
import nb as NB, d2h as H                 # pylint: disable=C0413

SEEDS = int(os.environ.get("SEEDS", 5))
SOME  = int(os.environ.get("SOME", 2048))  # reference rows kept
KS    = [int(k) for k in os.environ.get("KS", "1,3,5").split(",")]
LGB   = int(os.environ.get("LGB", 1))

def knn(tbl, ref, row, k):
  """The k nearest of REF, each voting `1 - d/dk`.  The bandwidth
  `dk` is the k+1-th neighbour's distance, not the k-th: take the
  k-th and the furthest voter weighs exactly nothing, which quietly
  turns k=3 back into k=1."""
  at = tbl.cols.klass.at
  ds = sorted(((E.xdist(tbl, row, r), r) for r in ref),
              key=lambda z: z[0])[:k+1]  # ties: never compare the rows
  dk = ds[-1][0] or 1e-32
  out = {}
  for d, r in ds[:k]:
    out[r[at]] = out.get(r[at], 0) + (1 - d/dk if k > 1 else 1)
  return max(out, key=out.get)

SUM = {}                                  # arm -> per-dataset scores

def wtl(rs, i, j, less: bool):
  """How often arm I beats arm J, by `same`, and the median gap.
  LESS flips the sign for d2h, where smaller is the better score."""
  w = t = l = 0; gaps = []
  for r in rs:
    a, b = r[i], r[j]
    g = S.median(a) - S.median(b); gaps += [g]
    if E.same(a, b, .35) or g == 0: t += 1
    elif (g < 0) == less: w += 1
    else: l += 1
  return f"{w}/{t}/{l}", S.median(gaps)

def main(names):
  ns = ["nb"] + [f"k{k}" for k in KS] + ["lgbm"]
  print(f"SOME={SOME} SEEDS={SEEDS} BINS={NB.BINS}   "
        f"pd: higher better.  pf, d2h: lower better.\n"
        f"{'data':<14}{'k':>3}{'maj%':>5} |"
        + "".join(f"{'pd '+n:>8}" for n in ns) + " |"
        + "".join(f"{'pf '+n:>8}" for n in ns) + " |"
        + "".join(f"{'d2h '+n:>9}" for n in ns))
  for dn in names:
    f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
    A = {n: [] for n in ["nb", "lgbm"] + KS}       # accuracy
    D = {n: [] for n in ["nb", "lgbm"] + KS}       # d2h
    t1 = t2 = t3 = 0.0
    for s in range(SEEDS):
      random.seed(s)
      t  = E.Tbl(E.csv(f))
      t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
      rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
      tr, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
      at   = t.cols.klass.at
      want = [r[at] for r in te.rows]
      acc  = lambda g: 100*sum(str(x) == str(w) for x, w in
                               zip(g, want))/len(want)
      t0 = time.time(); by, sp = NB.fit(tr, tr.rows)
      g  = [NB.nb(tr, by, sp, r) for r in te.rows]
      t1 += time.time()-t0
      A["nb"] += [acc(g)]; D["nb"] += [H.pdpf(want, g)]
      ref = random.sample(tr.rows, min(SOME, len(tr.rows)))
      for k in KS:
        t0 = time.time()
        g  = [knn(tr, ref, r, k) for r in te.rows]
        t2 += time.time()-t0
        A[k] += [acc(g)]; D[k] += [H.pdpf(want, g)]
      if LGB:
        t0 = time.time(); g = NB.lgbm(t, tr, te)[0]; t3 += time.time()-t0
        A["lgbm"] += [acc(g)]; D["lgbm"] += [H.pdpf(want, g)]
      else: A["lgbm"] += [0]; D["lgbm"] += [(0, 0, 0)]
    cnt = {}
    for r in t.rows: cnt[r[at]] = cnt.get(r[at], 0) + 1
    for n in ["nb"] + KS:
      SUM.setdefault(n, []).append(
        (dn, A[n], A["lgbm"],
         [x[2] for x in D[n]], [x[2] for x in D["lgbm"]],
         [x[0] for x in D[n]], [x[0] for x in D["lgbm"]],
         [x[1] for x in D[n]], [x[1] for x in D["lgbm"]]))
    al = ["nb"] + KS + ["lgbm"]
    med = lambda n, i: NB.dot(S.median([x[i] for x in D[n]]))
    print(f"{dn:<14}{len(cnt):>3}"
          f"{100*max(cnt.values())/len(t.rows):>5.0f} |"
          + "".join(f"{med(n, 0):>8}" for n in al) + " |"
          + "".join(f"{med(n, 1):>8}" for n in al) + " |"
          + "".join(f"{med(n, 2):>9}" for n in al), flush=True)

  print(f"\n{'arm':<6}" + "".join(f"{h:>22}" for h in
        ("accuracy (higher)", "pd (higher)", "pf (lower)", "d2h (lower)")))
  for n in ["nb"] + KS:
    rs, out = SUM[n], ""
    for i, j, less in ((1, 2, False), (5, 6, False),
                       (7, 8, True), (3, 4, True)):
      s, m = wtl(rs, i, j, less)
      out += f"{s + f' ({m:+.2f})':>22}"
    print(f"{str(n):<6}{out}")
  print(f"({len(SUM['nb'])} datasets, {SEEDS} seeds, vs LightGBM, "
        f"+/-/= by same(cliffs, ks, cohen d=.35))")

if __name__ == "__main__": main(sys.argv[1:])
