"""No fft, no frugals, no entropy: halve on a pole projection
until leaves hold LEAF rows, then 1-NN inside the leaf.  Poles
come from at most SOME rows, so a split costs the same at the
root as it does near the bottom."""
# pylint: disable=no-member   # `type()` structs confuse pylint
import os, sys, time, random, statistics as S
sys.path.insert(0, os.path.dirname(os.path.dirname(
                   os.path.abspath(__file__))))
import ezr as E
CAP    = 512
SEEDS  = int(os.environ.get("SEEDS", 5))
LEAF = int(os.environ.get("LEAF", 20))
SOME = int(os.environ.get("SOME", 64))

def proj(tbl, a, b, c, r):
  "Where R falls on the A-B line.  Two distances."
  x, y = E.xdist(tbl,r,a), E.xdist(tbl,r,b)
  return (x*x + c*c - y*y) / (2*c)

def halves(tbl, rows):
  "Poles from SOME rows, then everyone projected and split."
  sm = random.sample(rows, min(SOME, len(rows)))
  a  = max(sm, key=lambda r: E.xdist(tbl, r, sm[0]))
  b  = max(sm, key=lambda r: E.xdist(tbl, r, a))
  c  = E.xdist(tbl, a, b) + 1e-32
  ps = sorted(rows, key=lambda r: proj(tbl,a,b,c,r))
  m  = len(ps)//2
  return (a, b, c, proj(tbl,a,b,c,ps[m]), ps[:m], ps[m:])

def fmtree(tbl, rows):
  "A leaf is its rows; a fork is (poles, split, kid, kid)."
  if len(rows) <= LEAF: return rows
  a, b, c, cut, L, R = halves(tbl, rows)
  return (a, b, c, cut, fmtree(tbl,L), fmtree(tbl,R))

def fmleaf(tbl, node, row):
  "Walk ROW down; two distances at each fork."
  while type(node) is tuple:
    a, b, c, cut, L, R = node
    node = L if proj(tbl,a,b,c,row) <= cut else R
  return node

print(f"LEAF={LEAF} SOME={SOME}\n{'data':<12}{'k':>4}{'test':>6} |"
      f"{'exact':>7}{'fmap':>7}{'delta':>7}{'':>2} |{'s/ex':>7}{'s/build':>8}"
      f"{'s/query':>8}{'x':>6}")
for dn in sys.argv[1:]:
  f = os.path.expanduser(f"~/gits/moot/classify/{dn}.csv")
  ex, fm, tex, tb, tq = [], [], 0.0, 0.0, 0.0
  for s in range(SEEDS):
    random.seed(s)
    t  = E.Tbl(E.csv(f))
    t  = E.clone(t, [r for r in t.rows if r[t.cols.klass.at] != "?"])
    rs = random.sample(t.rows, len(t.rows)); m = int(.75*len(rs))
    full, te = E.clone(t, rs[:m]), E.clone(t, rs[m:])
    k  = t.cols.klass.at
    tr = E.clone(full, E.grabs(full, min(CAP, len(full.rows))))
    sc = lambda g: 100*sum(a==str(r[k]) for a,r in
                           zip(g,te.rows))/len(te.rows)
    t0 = time.time()
    ex += [sc([str(min(tr.rows, key=lambda o: E.xdist(tr,o,r))[k])
               for r in te.rows])]
    tex += time.time()-t0
    t0 = time.time(); root = fmtree(tr, tr.rows); tb += time.time()-t0
    t0 = time.time()
    fm += [sc([str(min(fmleaf(tr,root,r),
                       key=lambda o: E.xdist(tr,o,r))[k])
               for r in te.rows])]
    tq += time.time()-t0
  nk  = len({r[k] for r in t.rows})
  d   = S.median(fm) - S.median(ex)
  sig = " =" if E.same(ex, fm, .35) or d == 0 else (
        " +" if d > 0 else " -")
  print(f"{dn:<12}{nk:>4}{len(te.rows):>6} | {S.median(ex):6.1f}"
        f"{S.median(fm):7.1f}{S.median(fm)-S.median(ex):+7.1f}{sig} |"
        f"{tex/SEEDS:7.2f}{tb/SEEDS:8.2f}{tq/SEEDS:8.2f}"
        f"{tex/(tq+1e-9):6.1f}", flush=True)
